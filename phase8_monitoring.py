from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_activation import ActivationSurfaceProfile
from phase8_deployment import DeploymentRollbackGate
from phase8_rollout import DeploymentRolloutControlEngine, RolloutProfile


@dataclass
class MonitoringProfile:
    surface_id: str
    monitoring_mode: str
    min_health_score: float
    max_anomaly_score: float
    rollback_triggers: List[str]
    monitoring_lineage_domain: str
    monitoring_observability_domain: str


class MerchantServiceMonitoringSurface:
    @staticmethod
    def build_profile() -> MonitoringProfile:
        return MonitoringProfile(
            surface_id="merchant_ops_monitor",
            monitoring_mode="enhanced",
            min_health_score=0.8,
            max_anomaly_score=0.3,
            rollback_triggers=["health_breach", "anomaly_breach"],
            monitoring_lineage_domain="merchant",
            monitoring_observability_domain="merchant",
        )


class OperatorCardMonitoringSurface:
    @staticmethod
    def build_profile() -> MonitoringProfile:
        return MonitoringProfile(
            surface_id="operator_card_ops_monitor",
            monitoring_mode="full",
            min_health_score=0.75,
            max_anomaly_score=0.4,
            rollback_triggers=["anomaly_breach"],
            monitoring_lineage_domain="operator",
            monitoring_observability_domain="operator",
        )


class MixedDomainMonitoringSurface:
    @staticmethod
    def build_profile() -> MonitoringProfile:
        return MonitoringProfile(
            surface_id="mixed_domain_ops_monitor",
            monitoring_mode="full",
            min_health_score=0.75,
            max_anomaly_score=0.4,
            rollback_triggers=["health_breach", "anomaly_breach"],
            monitoring_lineage_domain="mixed_domain",
            monitoring_observability_domain="mixed_domain",
        )


class DeploymentMonitoringControlEngine:
    MONITORING_SIGNATURE = "deployment_monitoring:v1"

    def __init__(self) -> None:
        self.rollout_engine = DeploymentRolloutControlEngine()

    def _lineage(self, profile: MonitoringProfile, status: str, reason: str, gate: str, domain: str) -> Dict[str, Any]:
        return {
            "signature": self.MONITORING_SIGNATURE,
            "scope": "phase8_monitoring",
            "surface_id": profile.surface_id,
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "lineage_domain": profile.monitoring_lineage_domain,
        }

    def _observability(
        self,
        profile: MonitoringProfile,
        status: str,
        gate: str,
        domain: str,
        metrics: Dict[str, Any],
        rollback_triggered: bool,
        rollout_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "monitoring": {
                "signature": self.MONITORING_SIGNATURE,
                "surface_id": profile.surface_id,
                "status": status,
                "gate": gate,
                "domain": domain,
                "mode": profile.monitoring_mode,
                "health_score": float(metrics.get("health_score", 1.0)),
                "anomaly_score": float(metrics.get("anomaly_score", 0.0)),
                "rollback_triggered": rollback_triggered,
                "observability_domain": profile.monitoring_observability_domain,
            },
            "rollout": dict((rollout_result.get("observability") or {}).get("rollout", {})),
        }

    def execute_monitoring(
        self,
        *,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        policy_profile: DestinationGovernanceProfile,
        activation_profile: ActivationSurfaceProfile,
        rollout_profile: RolloutProfile,
        monitoring_profile: MonitoringProfile,
        destinations: List[str],
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())
        rollout_result = self.rollout_engine.execute_rollout(
            transport_executor=transport_executor,
            unified_result=unified_result,
            gate=gate,
            envelope=envelope,
            policy_profile=policy_profile,
            activation_profile=activation_profile,
            rollout_profile=rollout_profile,
            destinations=destinations,
            auth_posture=auth_posture,
            risk_score=risk_score,
            rollback_gate=rollback_gate,
        )
        if rollout_result.get("status") != "executed":
            reason = str(rollout_result.get("reason", "rollout_blocked"))
            gate_name = str(rollout_result.get("gate", "monitoring_rollout"))
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "lineage": self._lineage(monitoring_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(monitoring_profile, "blocked", gate_name, domain, metrics, False, rollout_result),
                "replay": dict(unified_result.get("replay", {})),
                "rollout_result": rollout_result,
            }

        health_score = float(metrics.get("health_score", 1.0))
        anomaly_score = float(metrics.get("anomaly_score", 0.0))
        rollback_triggered = False
        status = "executed"
        reason = "ok"
        gate_name = "none"

        if health_score < monitoring_profile.min_health_score and "health_breach" in set(monitoring_profile.rollback_triggers):
            rollback_triggered = True
            status = "rollback_triggered"
            reason = "health_threshold_breached"
            gate_name = "monitoring_health"
        elif anomaly_score > monitoring_profile.max_anomaly_score and "anomaly_breach" in set(monitoring_profile.rollback_triggers):
            rollback_triggered = True
            status = "rollback_triggered"
            reason = "anomaly_threshold_breached"
            gate_name = "monitoring_anomaly"

        return {
            "status": status,
            "reason": reason,
            "gate": gate_name,
            "lineage": self._lineage(monitoring_profile, status, reason, gate_name, domain),
            "observability": self._observability(monitoring_profile, status, gate_name, domain, metrics, rollback_triggered, rollout_result),
            "replay": dict(unified_result.get("replay", {})),
            "rollout_result": rollout_result,
        }

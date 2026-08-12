from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_activation import ActivationSurfaceProfile
from phase8_deployment import DeploymentRollbackGate
from phase8_monitoring import DeploymentMonitoringControlEngine, MonitoringProfile
from phase8_rollout import RolloutProfile


@dataclass
class InterventionProfile:
    surface_id: str
    intervention_mode: str
    intervention_supervision_level: str
    intervention_risk_threshold: float
    intervention_rollback_strategy: str
    intervention_replay_strategy: str
    intervention_lineage_domain: str
    intervention_observability_domain: str


class MerchantServiceInterventionSurface:
    @staticmethod
    def build_pause_profile() -> InterventionProfile:
        return InterventionProfile("merchant_ops_intervention", "pause", "strict", 0.9, "required", "strict", "merchant", "merchant")

    @staticmethod
    def build_drain_profile() -> InterventionProfile:
        return InterventionProfile("merchant_ops_intervention", "drain", "strict", 0.9, "required", "strict", "merchant", "merchant")


class OperatorCardInterventionSurface:
    @staticmethod
    def build_rollback_profile() -> InterventionProfile:
        return InterventionProfile("operator_card_ops_intervention", "rollback", "strict", 0.8, "required", "strict", "operator", "operator")

    @staticmethod
    def build_recovery_profile() -> InterventionProfile:
        return InterventionProfile("operator_card_ops_intervention", "recover", "strict", 0.8, "required", "strict", "operator", "operator")


class MixedDomainInterventionSurface:
    @staticmethod
    def build_pause_profile() -> InterventionProfile:
        return InterventionProfile("mixed_domain_ops_intervention", "pause", "strict", 0.9, "required", "strict", "mixed_domain", "mixed_domain")


class DeploymentInterventionControlEngine:
    INTERVENTION_SIGNATURE = "deployment_intervention:v1"

    def __init__(self) -> None:
        self.monitoring_engine = DeploymentMonitoringControlEngine()

    def _lineage(self, profile: InterventionProfile, status: str, reason: str, gate: str, domain: str) -> Dict[str, Any]:
        return {
            "signature": self.INTERVENTION_SIGNATURE,
            "scope": "phase8_intervention",
            "surface_id": profile.surface_id,
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "lineage_domain": profile.intervention_lineage_domain,
        }

    def _observability(
        self,
        profile: InterventionProfile,
        status: str,
        gate: str,
        domain: str,
        monitoring_result: Dict[str, Any],
        intervention: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "intervention": {
                "signature": self.INTERVENTION_SIGNATURE,
                "surface_id": profile.surface_id,
                "status": status,
                "gate": gate,
                "domain": domain,
                "mode": profile.intervention_mode,
                "state": intervention.get("state", "unknown"),
                "observability_domain": profile.intervention_observability_domain,
            },
            "monitoring": dict((monitoring_result.get("observability") or {}).get("monitoring", {})),
        }

    def _perform_intervention(self, profile: InterventionProfile, monitoring_result: Dict[str, Any], domain: str) -> Dict[str, Any]:
        mode = profile.intervention_mode
        if mode == "pause":
            return {"action": "pause", "state": "paused", "allow_new_executions": False, "complete_in_flight": False, "domain": domain}
        if mode == "drain":
            return {"action": "drain", "state": "draining", "allow_new_executions": False, "complete_in_flight": True, "domain": domain}
        if mode == "rollback":
            return {"action": "rollback", "state": "rolled_back", "restored": True, "domain": domain}
        return {"action": "recover", "state": "recovered", "source_status": monitoring_result.get("status", "unknown"), "domain": domain}

    def execute_intervention(
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
        intervention_profile: InterventionProfile,
        destinations: List[str],
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())
        lineage_sig = str(((unified_result.get("lineage") or {}).get("signature") or "").strip())
        if lineage_sig != "unifiedflow_decision:v1":
            reason = "invalid_unifiedflow_lineage"
            gate_name = "intervention_lineage"
            intervention = {"state": "blocked", "domain": domain}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "intervention": intervention,
                "lineage": self._lineage(intervention_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(intervention_profile, "blocked", gate_name, domain, {}, intervention),
                "replay": dict(unified_result.get("replay", {})),
                "monitoring_result": {},
            }

        if gate.supervision.supervision_mode != intervention_profile.intervention_supervision_level:
            reason = "intervention_supervision_mismatch"
            gate_name = "intervention_supervision"
            intervention = {"state": "blocked", "domain": domain}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "intervention": intervention,
                "lineage": self._lineage(intervention_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(intervention_profile, "blocked", gate_name, domain, {}, intervention),
                "replay": dict(unified_result.get("replay", {})),
                "monitoring_result": {},
            }

        if risk_score > intervention_profile.intervention_risk_threshold:
            reason = "intervention_risk_threshold_exceeded"
            gate_name = "intervention_risk"
            intervention = {"state": "blocked", "domain": domain}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "intervention": intervention,
                "lineage": self._lineage(intervention_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(intervention_profile, "blocked", gate_name, domain, {}, intervention),
                "replay": dict(unified_result.get("replay", {})),
                "monitoring_result": {},
            }

        if intervention_profile.intervention_rollback_strategy == "required" and (not rollback_gate.enabled or rollback_gate.mode != "safe"):
            reason = "intervention_rollback_required"
            gate_name = "intervention_rollback"
            intervention = {"state": "blocked", "domain": domain}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "intervention": intervention,
                "lineage": self._lineage(intervention_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(intervention_profile, "blocked", gate_name, domain, {}, intervention),
                "replay": dict(unified_result.get("replay", {})),
                "monitoring_result": {},
            }

        monitoring_result = self.monitoring_engine.execute_monitoring(
            transport_executor=transport_executor,
            unified_result=unified_result,
            gate=gate,
            envelope=envelope,
            policy_profile=policy_profile,
            activation_profile=activation_profile,
            rollout_profile=rollout_profile,
            monitoring_profile=monitoring_profile,
            destinations=destinations,
            auth_posture=auth_posture,
            risk_score=risk_score,
            rollback_gate=rollback_gate,
            metrics=metrics,
        )
        if monitoring_result.get("status") == "blocked":
            reason = str(monitoring_result.get("reason", "monitoring_blocked"))
            gate_name = str(monitoring_result.get("gate", "intervention_monitoring"))
            intervention = {"state": "blocked", "domain": domain}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "intervention": intervention,
                "lineage": self._lineage(intervention_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(intervention_profile, "blocked", gate_name, domain, monitoring_result, intervention),
                "replay": dict(unified_result.get("replay", {})),
                "monitoring_result": monitoring_result,
            }

        intervention = self._perform_intervention(intervention_profile, monitoring_result, domain)
        return {
            "status": "intervened",
            "reason": intervention_profile.intervention_mode,
            "gate": "none",
            "intervention": intervention,
            "lineage": self._lineage(intervention_profile, "intervened", intervention_profile.intervention_mode, "none", domain),
            "observability": self._observability(intervention_profile, "intervened", "none", domain, monitoring_result, intervention),
            "replay": dict(unified_result.get("replay", {})),
            "monitoring_result": monitoring_result,
        }

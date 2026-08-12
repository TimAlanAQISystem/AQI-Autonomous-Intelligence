from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_deployment import DeploymentRollbackGate, DeploymentSurfaceEngine


@dataclass
class ActivationSurfaceProfile:
    surface_id: str
    activation_mode: str
    activation_allowlist: List[str]
    activation_supervision_level: str
    activation_rollback_strategy: str
    activation_replay_strategy: str
    activation_lineage_domain: str
    activation_observability_domain: str


class MerchantServiceActivationSurface:
    @staticmethod
    def build_profile() -> ActivationSurfaceProfile:
        return ActivationSurfaceProfile(
            surface_id="merchant_ops_active",
            activation_mode="controlled",
            activation_allowlist=["merchant_gateway_prod"],
            activation_supervision_level="strict",
            activation_rollback_strategy="required",
            activation_replay_strategy="strict",
            activation_lineage_domain="merchant",
            activation_observability_domain="merchant",
        )


class OperatorCardActivationSurface:
    @staticmethod
    def build_profile() -> ActivationSurfaceProfile:
        return ActivationSurfaceProfile(
            surface_id="operator_card_ops_active",
            activation_mode="controlled",
            activation_allowlist=["operator_gateway_prod"],
            activation_supervision_level="strict",
            activation_rollback_strategy="required",
            activation_replay_strategy="strict",
            activation_lineage_domain="operator",
            activation_observability_domain="operator",
        )


class MixedDomainActivationSurface:
    @staticmethod
    def build_profile() -> ActivationSurfaceProfile:
        return ActivationSurfaceProfile(
            surface_id="mixed_domain_ops_active",
            activation_mode="controlled",
            activation_allowlist=["mixed_gateway_prod"],
            activation_supervision_level="strict",
            activation_rollback_strategy="required",
            activation_replay_strategy="strict",
            activation_lineage_domain="mixed_domain",
            activation_observability_domain="mixed_domain",
        )


class DeploymentActivationEngine:
    ACTIVATION_SIGNATURE = "deployment_activation:v1"

    def __init__(self) -> None:
        self.deployment_engine = DeploymentSurfaceEngine()

    def _lineage(
        self,
        profile: ActivationSurfaceProfile,
        status: str,
        reason: str,
        gate: str,
        domain: str,
        destination: str,
    ) -> Dict[str, Any]:
        return {
            "signature": self.ACTIVATION_SIGNATURE,
            "scope": "phase8_activation",
            "surface_id": profile.surface_id,
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "destination": destination,
            "lineage_domain": profile.activation_lineage_domain,
        }

    def _observability(
        self,
        profile: ActivationSurfaceProfile,
        status: str,
        gate: str,
        domain: str,
        deployment_result: Dict[str, Any],
        rollback_gate: DeploymentRollbackGate,
    ) -> Dict[str, Any]:
        return {
            "activation": {
                "signature": self.ACTIVATION_SIGNATURE,
                "surface_id": profile.surface_id,
                "status": status,
                "gate": gate,
                "domain": domain,
                "activation_mode": profile.activation_mode,
                "supervision_level": profile.activation_supervision_level,
                "rollback_strategy": profile.activation_rollback_strategy,
                "rollback_enabled": rollback_gate.enabled,
                "replay_strategy": profile.activation_replay_strategy,
                "observability_domain": profile.activation_observability_domain,
            },
            "deployment": dict((deployment_result.get("observability") or {}).get("deployment", {})),
            "policy": dict((deployment_result.get("observability") or {}).get("policy", {})),
            "risk": dict((deployment_result.get("observability") or {}).get("risk", {})),
            "transport": dict((deployment_result.get("observability") or {}).get("transport", {})),
        }

    def activate_surface(
        self,
        *,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        policy_profile: DestinationGovernanceProfile,
        activation_profile: ActivationSurfaceProfile,
        destination: str,
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
    ) -> Dict[str, Any]:
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())

        lineage_sig = str(((unified_result.get("lineage") or {}).get("signature") or "").strip())
        if lineage_sig != "unifiedflow_decision:v1":
            reason = "invalid_unifiedflow_lineage"
            gate_name = "activation_lineage"
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "lineage": self._lineage(activation_profile, "blocked", reason, gate_name, domain, destination),
                "observability": self._observability(activation_profile, "blocked", gate_name, domain, {}, rollback_gate),
                "replay": dict(unified_result.get("replay", {})),
                "deployment_result": {},
                "transport_result": {},
            }

        if destination not in set(activation_profile.activation_allowlist):
            reason = "activation_destination_not_allowlisted"
            gate_name = "activation_allowlist"
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "lineage": self._lineage(activation_profile, "blocked", reason, gate_name, domain, destination),
                "observability": self._observability(activation_profile, "blocked", gate_name, domain, {}, rollback_gate),
                "replay": dict(unified_result.get("replay", {})),
                "deployment_result": {},
                "transport_result": {},
            }

        if gate.supervision.supervision_mode != activation_profile.activation_supervision_level:
            reason = "activation_supervision_mismatch"
            gate_name = "activation_supervision"
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "lineage": self._lineage(activation_profile, "blocked", reason, gate_name, domain, destination),
                "observability": self._observability(activation_profile, "blocked", gate_name, domain, {}, rollback_gate),
                "replay": dict(unified_result.get("replay", {})),
                "deployment_result": {},
                "transport_result": {},
            }

        if activation_profile.activation_rollback_strategy == "required" and (not rollback_gate.enabled or rollback_gate.mode != "safe"):
            reason = "activation_rollback_required"
            gate_name = "activation_rollback"
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "lineage": self._lineage(activation_profile, "blocked", reason, gate_name, domain, destination),
                "observability": self._observability(activation_profile, "blocked", gate_name, domain, {}, rollback_gate),
                "replay": dict(unified_result.get("replay", {})),
                "deployment_result": {},
                "transport_result": {},
            }

        deployment_result = self.deployment_engine.execute_deployment(
            transport_executor=transport_executor,
            unified_result=unified_result,
            gate=gate,
            envelope=envelope,
            policy_profile=policy_profile,
            deployment_profile=self._to_deployment_profile(activation_profile),
            destination=destination,
            auth_posture=auth_posture,
            risk_score=risk_score,
            rollback_gate=rollback_gate,
        )
        status = "executed" if deployment_result.get("status") == "executed" else "blocked"
        reason = "ok" if status == "executed" else str(deployment_result.get("reason", "deployment_blocked"))
        gate_name = "none" if status == "executed" else str(deployment_result.get("gate", "activation_deployment"))
        return {
            "status": status,
            "reason": reason,
            "gate": gate_name,
            "lineage": self._lineage(activation_profile, status, reason, gate_name, domain, destination),
            "observability": self._observability(activation_profile, status, gate_name, domain, deployment_result, rollback_gate),
            "replay": dict(unified_result.get("replay", {})),
            "deployment_result": deployment_result,
            "transport_result": dict(deployment_result.get("transport_result", {})),
        }

    def _to_deployment_profile(self, activation_profile: ActivationSurfaceProfile) -> Any:
        from phase8_deployment import DeploymentSurfaceProfile

        return DeploymentSurfaceProfile(
            surface_id=activation_profile.surface_id,
            deployment_allowlist=list(activation_profile.activation_allowlist),
            deployment_risk_threshold=1.0,
            deployment_lineage_domain=activation_profile.activation_lineage_domain,
            deployment_observability_domain=activation_profile.activation_observability_domain,
            supervision_mode=activation_profile.activation_supervision_level,
            rollback_mode=activation_profile.activation_rollback_strategy,
            replay_mode=activation_profile.activation_replay_strategy,
        )

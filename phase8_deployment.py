from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile, ExternalPolicyRiskEngine
from phase7_transport import GovernedTransportEnvelope


@dataclass
class DeploymentSurfaceProfile:
    surface_id: str
    deployment_allowlist: List[str]
    deployment_risk_threshold: float
    deployment_lineage_domain: str
    deployment_observability_domain: str
    supervision_mode: str
    rollback_mode: str
    replay_mode: str


@dataclass
class DeploymentRollbackGate:
    enabled: bool
    mode: str


@dataclass
class DeploymentSurfaceResult:
    status: str
    reason: str
    gate: str
    lineage: Dict[str, Any]
    observability: Dict[str, Any]
    replay: Dict[str, Any]
    transport_result: Dict[str, Any]
    policy_result: Dict[str, Any]


class MerchantServiceDeploymentSurface:
    @staticmethod
    def build_profile() -> DeploymentSurfaceProfile:
        return DeploymentSurfaceProfile(
            surface_id="merchant_ops",
            deployment_allowlist=["merchant_gateway_prod"],
            deployment_risk_threshold=0.8,
            deployment_lineage_domain="merchant",
            deployment_observability_domain="merchant",
            supervision_mode="strict",
            rollback_mode="required",
            replay_mode="strict",
        )


class OperatorCardDeploymentSurface:
    @staticmethod
    def build_profile() -> DeploymentSurfaceProfile:
        return DeploymentSurfaceProfile(
            surface_id="operator_card_ops",
            deployment_allowlist=["operator_gateway_prod"],
            deployment_risk_threshold=0.7,
            deployment_lineage_domain="operator",
            deployment_observability_domain="operator",
            supervision_mode="strict",
            rollback_mode="required",
            replay_mode="strict",
        )


class MixedDomainDeploymentSurface:
    @staticmethod
    def build_profile() -> DeploymentSurfaceProfile:
        return DeploymentSurfaceProfile(
            surface_id="mixed_domain_ops",
            deployment_allowlist=["mixed_gateway_prod"],
            deployment_risk_threshold=0.9,
            deployment_lineage_domain="mixed_domain",
            deployment_observability_domain="mixed_domain",
            supervision_mode="strict",
            rollback_mode="required",
            replay_mode="strict",
        )


class DeploymentSurfaceEngine:
    DEPLOYMENT_SIGNATURE = "deployment_surface:v1"

    def __init__(self) -> None:
        self.policy_engine = ExternalPolicyRiskEngine()

    def replay_from_lineage(self, deployment_result: Dict[str, Any]) -> Dict[str, Any]:
        lineage = deployment_result.get("lineage") or {}
        policy_lineage = (deployment_result.get("policy_result") or {}).get("policy_lineage") or {}
        risk_lineage = (deployment_result.get("policy_result") or {}).get("risk_lineage") or {}
        replay = dict(deployment_result.get("replay") or {})
        replay["deployment_signature"] = lineage.get("signature", self.DEPLOYMENT_SIGNATURE)
        replay["policy_signature"] = policy_lineage.get("signature", "external_policy:v1")
        replay["risk_signature"] = risk_lineage.get("signature", "external_risk:v1")
        return replay

    def _lineage(self, profile: DeploymentSurfaceProfile, status: str, reason: str, gate: str, domain: str, destination: str) -> Dict[str, Any]:
        return {
            "signature": self.DEPLOYMENT_SIGNATURE,
            "scope": "phase8_deployment",
            "surface_id": profile.surface_id,
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "destination": destination,
            "lineage_domain": profile.deployment_lineage_domain,
        }

    def _observability(
        self,
        profile: DeploymentSurfaceProfile,
        status: str,
        gate: str,
        domain: str,
        policy_result: Dict[str, Any],
        rollback_gate: DeploymentRollbackGate,
    ) -> Dict[str, Any]:
        return {
            "deployment": {
                "signature": self.DEPLOYMENT_SIGNATURE,
                "surface_id": profile.surface_id,
                "status": status,
                "gate": gate,
                "domain": domain,
                "observability_domain": profile.deployment_observability_domain,
                "rollback_mode": profile.rollback_mode,
                "rollback_enabled": rollback_gate.enabled,
                "rollback_gate_mode": rollback_gate.mode,
                "supervision_mode": profile.supervision_mode,
                "replay_mode": profile.replay_mode,
            },
            "policy": dict((policy_result.get("observability") or {}).get("policy", {})),
            "risk": dict((policy_result.get("observability") or {}).get("risk", {})),
            "transport": dict((policy_result.get("observability") or {}).get("transport", {})),
        }

    def execute_deployment(
        self,
        *,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        policy_profile: DestinationGovernanceProfile,
        deployment_profile: DeploymentSurfaceProfile,
        destination: str,
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
    ) -> Dict[str, Any]:
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())

        lineage_sig = str(((unified_result.get("lineage") or {}).get("signature") or "").strip())
        if lineage_sig != "unifiedflow_decision:v1":
            reason = "invalid_unifiedflow_lineage"
            gate_name = "deployment_lineage"
            lineage = self._lineage(deployment_profile, "blocked", reason, gate_name, domain, destination)
            policy_result = {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "observability": {},
            }
            return asdict(
                DeploymentSurfaceResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    lineage=lineage,
                    observability=self._observability(deployment_profile, "blocked", gate_name, domain, policy_result, rollback_gate),
                    replay=dict(unified_result.get("replay", {})),
                    transport_result={},
                    policy_result=policy_result,
                )
            )

        if destination not in set(deployment_profile.deployment_allowlist):
            reason = "deployment_destination_not_allowlisted"
            gate_name = "deployment_allowlist"
            lineage = self._lineage(deployment_profile, "blocked", reason, gate_name, domain, destination)
            policy_result = {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "observability": {},
            }
            return asdict(
                DeploymentSurfaceResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    lineage=lineage,
                    observability=self._observability(deployment_profile, "blocked", gate_name, domain, policy_result, rollback_gate),
                    replay=dict(unified_result.get("replay", {})),
                    transport_result={},
                    policy_result=policy_result,
                )
            )

        if risk_score > float(deployment_profile.deployment_risk_threshold):
            reason = "deployment_risk_threshold_exceeded"
            gate_name = "deployment_risk"
            lineage = self._lineage(deployment_profile, "blocked", reason, gate_name, domain, destination)
            policy_result = {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "observability": {},
            }
            return asdict(
                DeploymentSurfaceResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    lineage=lineage,
                    observability=self._observability(deployment_profile, "blocked", gate_name, domain, policy_result, rollback_gate),
                    replay=dict(unified_result.get("replay", {})),
                    transport_result={},
                    policy_result=policy_result,
                )
            )

        if gate.supervision.supervision_mode != deployment_profile.supervision_mode:
            reason = "supervision_mode_mismatch"
            gate_name = "deployment_supervision"
            lineage = self._lineage(deployment_profile, "blocked", reason, gate_name, domain, destination)
            policy_result = {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "observability": {},
            }
            return asdict(
                DeploymentSurfaceResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    lineage=lineage,
                    observability=self._observability(deployment_profile, "blocked", gate_name, domain, policy_result, rollback_gate),
                    replay=dict(unified_result.get("replay", {})),
                    transport_result={},
                    policy_result=policy_result,
                )
            )

        if deployment_profile.rollback_mode == "required" and (not rollback_gate.enabled or rollback_gate.mode != "safe"):
            reason = "rollback_required"
            gate_name = "deployment_rollback"
            lineage = self._lineage(deployment_profile, "blocked", reason, gate_name, domain, destination)
            policy_result = {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "observability": {},
            }
            return asdict(
                DeploymentSurfaceResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    lineage=lineage,
                    observability=self._observability(deployment_profile, "blocked", gate_name, domain, policy_result, rollback_gate),
                    replay=dict(unified_result.get("replay", {})),
                    transport_result={},
                    policy_result=policy_result,
                )
            )

        policy_result = self.policy_engine.execute_policy(
            transport_executor=transport_executor,
            unified_result=unified_result,
            gate=gate,
            envelope=envelope,
            profile=policy_profile,
            destination=destination,
            auth_posture=auth_posture,
            risk_score=risk_score,
        )

        status = "executed" if policy_result.get("status") == "executed" else "blocked"
        reason = "ok" if status == "executed" else str(policy_result.get("reason", "policy_blocked"))
        gate_name = "none" if status == "executed" else str(policy_result.get("gate", "deployment_policy"))
        lineage = self._lineage(deployment_profile, status, reason, gate_name, domain, destination)
        replay = dict(unified_result.get("replay", {}))

        return asdict(
            DeploymentSurfaceResult(
                status=status,
                reason=reason,
                gate=gate_name,
                lineage=lineage,
                observability=self._observability(deployment_profile, status, gate_name, domain, policy_result, rollback_gate),
                replay=replay,
                transport_result=dict(policy_result.get("transport_result", {})),
                policy_result=policy_result,
            )
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_activation import ActivationSurfaceProfile, DeploymentActivationEngine
from phase8_deployment import DeploymentRollbackGate


@dataclass
class RolloutProfile:
    surface_id: str
    rollout_mode: str
    rollout_supervision_level: str
    rollout_risk_threshold: float
    rollout_rollback_strategy: str
    rollout_replay_strategy: str
    rollout_lineage_domain: str
    rollout_observability_domain: str
    staged_percentage: int = 100
    canary_destinations: List[str] | None = None


class MerchantServiceRolloutSurface:
    @staticmethod
    def build_profile() -> RolloutProfile:
        return RolloutProfile(
            surface_id="merchant_ops_rollout",
            rollout_mode="staged",
            rollout_supervision_level="strict",
            rollout_risk_threshold=0.9,
            rollout_rollback_strategy="required",
            rollout_replay_strategy="strict",
            rollout_lineage_domain="merchant",
            rollout_observability_domain="merchant",
            staged_percentage=50,
            canary_destinations=[],
        )


class OperatorCardRolloutSurface:
    @staticmethod
    def build_profile() -> RolloutProfile:
        return RolloutProfile(
            surface_id="operator_card_ops_rollout",
            rollout_mode="canary",
            rollout_supervision_level="strict",
            rollout_risk_threshold=0.8,
            rollout_rollback_strategy="required",
            rollout_replay_strategy="strict",
            rollout_lineage_domain="operator",
            rollout_observability_domain="operator",
            staged_percentage=100,
            canary_destinations=["operator_gateway_prod_a"],
        )


class MixedDomainRolloutSurface:
    @staticmethod
    def build_profile() -> RolloutProfile:
        return RolloutProfile(
            surface_id="mixed_domain_ops_rollout",
            rollout_mode="full",
            rollout_supervision_level="strict",
            rollout_risk_threshold=0.9,
            rollout_rollback_strategy="required",
            rollout_replay_strategy="strict",
            rollout_lineage_domain="mixed_domain",
            rollout_observability_domain="mixed_domain",
            staged_percentage=100,
            canary_destinations=[],
        )


class DeploymentRolloutControlEngine:
    ROLLOUT_SIGNATURE = "deployment_rollout:v1"

    def __init__(self) -> None:
        self.activation_engine = DeploymentActivationEngine()

    def _lineage(self, profile: RolloutProfile, status: str, reason: str, gate: str, domain: str) -> Dict[str, Any]:
        return {
            "signature": self.ROLLOUT_SIGNATURE,
            "scope": "phase8_rollout",
            "surface_id": profile.surface_id,
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "lineage_domain": profile.rollout_lineage_domain,
        }

    def _observability(
        self,
        profile: RolloutProfile,
        status: str,
        gate: str,
        domain: str,
        selection: Dict[str, Any],
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "rollout": {
                "signature": self.ROLLOUT_SIGNATURE,
                "surface_id": profile.surface_id,
                "status": status,
                "gate": gate,
                "domain": domain,
                "mode": selection.get("mode", profile.rollout_mode),
                "selected_count": len(selection.get("selected_destinations", [])),
                "observability_domain": profile.rollout_observability_domain,
            },
            "results": [
                {
                    "status": item.get("status", "unknown"),
                    "gate": item.get("gate", "none"),
                    "destination": item.get("destination", "unknown"),
                }
                for item in results
            ],
        }

    def _select_destinations(self, profile: RolloutProfile, destinations: List[str]) -> Dict[str, Any]:
        unique = [str(item) for item in destinations]
        if profile.rollout_mode == "canary":
            allowed = set(profile.canary_destinations or [])
            selected = [item for item in unique if item in allowed]
            return {"mode": "canary", "selected_destinations": selected}
        if profile.rollout_mode == "staged":
            count = max(1, int(len(unique) * max(0, min(profile.staged_percentage, 100)) / 100)) if unique else 0
            selected = unique[:count]
            return {"mode": "staged", "selected_destinations": selected}
        return {"mode": "full", "selected_destinations": unique}

    def execute_rollout(
        self,
        *,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        policy_profile: DestinationGovernanceProfile,
        activation_profile: ActivationSurfaceProfile,
        rollout_profile: RolloutProfile,
        destinations: List[str],
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
    ) -> Dict[str, Any]:
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())
        lineage_sig = str(((unified_result.get("lineage") or {}).get("signature") or "").strip())
        if lineage_sig != "unifiedflow_decision:v1":
            gate_name = "rollout_lineage"
            reason = "invalid_unifiedflow_lineage"
            selection = {"mode": rollout_profile.rollout_mode, "selected_destinations": []}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "selection": selection,
                "results": [],
                "lineage": self._lineage(rollout_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(rollout_profile, "blocked", gate_name, domain, selection, []),
                "replay": dict(unified_result.get("replay", {})),
            }

        if gate.supervision.supervision_mode != rollout_profile.rollout_supervision_level:
            gate_name = "rollout_supervision"
            reason = "rollout_supervision_mismatch"
            selection = {"mode": rollout_profile.rollout_mode, "selected_destinations": []}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "selection": selection,
                "results": [],
                "lineage": self._lineage(rollout_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(rollout_profile, "blocked", gate_name, domain, selection, []),
                "replay": dict(unified_result.get("replay", {})),
            }

        if risk_score > rollout_profile.rollout_risk_threshold:
            gate_name = "rollout_risk"
            reason = "rollout_risk_threshold_exceeded"
            selection = {"mode": rollout_profile.rollout_mode, "selected_destinations": []}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "selection": selection,
                "results": [],
                "lineage": self._lineage(rollout_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(rollout_profile, "blocked", gate_name, domain, selection, []),
                "replay": dict(unified_result.get("replay", {})),
            }

        if rollout_profile.rollout_rollback_strategy == "required" and (not rollback_gate.enabled or rollback_gate.mode != "safe"):
            gate_name = "rollout_rollback"
            reason = "rollout_rollback_required"
            selection = {"mode": rollout_profile.rollout_mode, "selected_destinations": []}
            return {
                "status": "blocked",
                "reason": reason,
                "gate": gate_name,
                "selection": selection,
                "results": [],
                "lineage": self._lineage(rollout_profile, "blocked", reason, gate_name, domain),
                "observability": self._observability(rollout_profile, "blocked", gate_name, domain, selection, []),
                "replay": dict(unified_result.get("replay", {})),
            }

        selection = self._select_destinations(rollout_profile, destinations)
        scoped_activation_profile = ActivationSurfaceProfile(
            surface_id=activation_profile.surface_id,
            activation_mode=activation_profile.activation_mode,
            activation_allowlist=list(selection.get("selected_destinations", [])),
            activation_supervision_level=activation_profile.activation_supervision_level,
            activation_rollback_strategy=activation_profile.activation_rollback_strategy,
            activation_replay_strategy=activation_profile.activation_replay_strategy,
            activation_lineage_domain=activation_profile.activation_lineage_domain,
            activation_observability_domain=activation_profile.activation_observability_domain,
        )
        results: List[Dict[str, Any]] = []
        final_status = "executed"
        final_reason = "ok"
        final_gate = "none"

        for idx, destination in enumerate(selection.get("selected_destinations", [])):
            scoped_envelope = GovernedTransportEnvelope(
                timeout_s=envelope.timeout_s,
                max_retries=envelope.max_retries,
                idempotency_key=f"{envelope.idempotency_key}:{idx}",
                correlation_id=f"{envelope.correlation_id}:{idx}",
                max_payload_bytes=envelope.max_payload_bytes,
                max_response_bytes=envelope.max_response_bytes,
                headers=dict(envelope.headers),
            )
            activation_result = self.activation_engine.activate_surface(
                transport_executor=transport_executor,
                unified_result=unified_result,
                gate=gate,
                envelope=scoped_envelope,
                policy_profile=policy_profile,
                activation_profile=scoped_activation_profile,
                destination=destination,
                auth_posture=auth_posture,
                risk_score=risk_score,
                rollback_gate=rollback_gate,
            )
            result_payload = dict(activation_result)
            result_payload["destination"] = destination
            results.append(result_payload)
            if activation_result.get("status") != "executed":
                final_status = "blocked"
                final_reason = str(activation_result.get("reason", "activation_blocked"))
                final_gate = str(activation_result.get("gate", "rollout_activation"))
                break

        return {
            "status": final_status,
            "reason": final_reason,
            "gate": final_gate,
            "selection": selection,
            "results": results,
            "lineage": self._lineage(rollout_profile, final_status, final_reason, final_gate, domain),
            "observability": self._observability(rollout_profile, final_status, final_gate, domain, selection, results),
            "replay": dict(unified_result.get("replay", {})),
        }

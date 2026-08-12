from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_activation import ActivationSurfaceProfile, MerchantServiceActivationSurface, MixedDomainActivationSurface, OperatorCardActivationSurface
from phase8_deployment import DeploymentRollbackGate
from phase8_intervention import (
    DeploymentInterventionControlEngine,
    MerchantServiceInterventionSurface,
    MixedDomainInterventionSurface,
    OperatorCardInterventionSurface,
)
from phase8_monitoring import MerchantServiceMonitoringSurface, MixedDomainMonitoringSurface, MonitoringProfile, OperatorCardMonitoringSurface
from phase8_rollout import MerchantServiceRolloutSurface, MixedDomainRolloutSurface, OperatorCardRolloutSurface, RolloutProfile


@dataclass
class CommandSurfaceProfile:
    surface_id: str
    allowed_commands: List[str]
    required_supervision_level: str
    allowed_domains: List[str]
    allowed_destinations: List[str]
    rollback_authority: bool
    recovery_authority: bool
    replay_visibility: str
    observability_scope: str


class MerchantServiceCommandSurface:
    @staticmethod
    def build_profile() -> CommandSurfaceProfile:
        return CommandSurfaceProfile(
            surface_id="merchant_command_surface",
            allowed_commands=["start", "pause", "resume", "drain", "rollback", "recover", "inspect", "replay", "status"],
            required_supervision_level="strict",
            allowed_domains=["merchant_services"],
            allowed_destinations=["merchant_gateway_prod_a"],
            rollback_authority=True,
            recovery_authority=True,
            replay_visibility="full",
            observability_scope="full",
        )


class OperatorCardCommandSurface:
    @staticmethod
    def build_profile() -> CommandSurfaceProfile:
        return CommandSurfaceProfile(
            surface_id="operator_card_command_surface",
            allowed_commands=["start", "pause", "resume", "drain", "rollback", "recover", "inspect", "replay", "status"],
            required_supervision_level="strict",
            allowed_domains=["operator_card_services"],
            allowed_destinations=["operator_gateway_prod_a"],
            rollback_authority=True,
            recovery_authority=True,
            replay_visibility="full",
            observability_scope="full",
        )


class MixedDomainCommandSurface:
    @staticmethod
    def build_profile() -> CommandSurfaceProfile:
        return CommandSurfaceProfile(
            surface_id="mixed_domain_command_surface",
            allowed_commands=["start", "pause", "resume", "drain", "rollback", "recover", "inspect", "replay", "status"],
            required_supervision_level="strict",
            allowed_domains=["merchant_services", "operator_card_services"],
            allowed_destinations=["mixed_gateway_prod_a"],
            rollback_authority=True,
            recovery_authority=True,
            replay_visibility="full",
            observability_scope="full",
        )


class OperatorCommandEngine:
    COMMAND_SIGNATURE = "operator_command:v1"

    def __init__(self) -> None:
        self.intervention_engine = DeploymentInterventionControlEngine()

    def _lineage(self, profile: CommandSurfaceProfile, command: str, status: str, reason: str, domain: str) -> Dict[str, Any]:
        return {
            "signature": self.COMMAND_SIGNATURE,
            "scope": "phase9_command",
            "surface_id": profile.surface_id,
            "command": command,
            "status": status,
            "reason": reason,
            "domain": domain,
        }

    def _observability(self, profile: CommandSurfaceProfile, command: str, status: str, domain: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "command": {
                "signature": self.COMMAND_SIGNATURE,
                "surface_id": profile.surface_id,
                "command": command,
                "status": status,
                "domain": domain,
                "observability_scope": profile.observability_scope,
            },
            "result": dict(result.get("observability", {})) if isinstance(result, dict) else {},
        }

    def _domain(self, unified_result: Dict[str, Any]) -> str:
        return str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())

    def _profiles_for_domain(self, domain: str) -> tuple[ActivationSurfaceProfile, RolloutProfile, MonitoringProfile, Any]:
        if domain == "merchant_services":
            return (
                MerchantServiceActivationSurface.build_profile(),
                MerchantServiceRolloutSurface.build_profile(),
                MerchantServiceMonitoringSurface.build_profile(),
                MerchantServiceInterventionSurface,
            )
        if domain == "operator_card_services":
            return (
                OperatorCardActivationSurface.build_profile(),
                OperatorCardRolloutSurface.build_profile(),
                OperatorCardMonitoringSurface.build_profile(),
                OperatorCardInterventionSurface,
            )
        return (
            MixedDomainActivationSurface.build_profile(),
            MixedDomainRolloutSurface.build_profile(),
            MixedDomainMonitoringSurface.build_profile(),
            MixedDomainInterventionSurface,
        )

    def execute_command(
        self,
        *,
        command: str,
        command_profile: CommandSurfaceProfile,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        policy_profile: DestinationGovernanceProfile,
        destination: str,
        auth_posture: str,
        risk_score: float,
        rollback_gate: DeploymentRollbackGate,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        domain = self._domain(unified_result)
        scoped_envelope = GovernedTransportEnvelope(
            timeout_s=envelope.timeout_s,
            max_retries=envelope.max_retries,
            idempotency_key=f"{envelope.idempotency_key}:{command}",
            correlation_id=f"{envelope.correlation_id}:{command}",
            max_payload_bytes=envelope.max_payload_bytes,
            max_response_bytes=envelope.max_response_bytes,
            headers=dict(envelope.headers),
        )
        lineage_sig = str(((unified_result.get("lineage") or {}).get("signature") or "").strip())
        if lineage_sig != "unifiedflow_decision:v1":
            reason = "lineage_continuity_broken"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command not in set(command_profile.allowed_commands):
            reason = "command_not_allowed"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if gate.supervision.supervision_mode != command_profile.required_supervision_level:
            reason = "command_supervision_mismatch"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if domain not in set(command_profile.allowed_domains) or destination not in set(command_profile.allowed_destinations):
            reason = "command_surface_outside_policy"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "rollback" and not command_profile.rollback_authority:
            reason = "rollback_authority_required"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "recover" and not command_profile.recovery_authority:
            reason = "recovery_authority_required"
            return {
                "status": "blocked",
                "reason": reason,
                "lineage": self._lineage(command_profile, command, "blocked", reason, domain),
                "observability": self._observability(command_profile, command, "blocked", domain, {}),
                "replay": dict(unified_result.get("replay", {})),
            }

        activation_profile, rollout_profile, monitoring_profile, intervention_surface = self._profiles_for_domain(domain)

        if command in {"pause", "drain", "rollback", "recover"}:
            if command == "pause":
                intervention_profile = intervention_surface.build_pause_profile()
            elif command == "drain":
                intervention_profile = intervention_surface.build_drain_profile()
            elif command == "rollback":
                intervention_profile = intervention_surface.build_rollback_profile()
            else:
                intervention_profile = intervention_surface.build_recovery_profile()

            result = self.intervention_engine.execute_intervention(
                transport_executor=transport_executor,
                unified_result=unified_result,
                gate=gate,
                envelope=scoped_envelope,
                policy_profile=policy_profile,
                activation_profile=activation_profile,
                rollout_profile=rollout_profile,
                monitoring_profile=monitoring_profile,
                intervention_profile=intervention_profile,
                destinations=[destination],
                auth_posture=auth_posture,
                risk_score=risk_score,
                rollback_gate=rollback_gate,
                metrics=metrics,
            )
            return {
                "status": "executed" if result.get("status") == "intervened" else result.get("status", "blocked"),
                "reason": command,
                "command_result": result,
                "lineage": self._lineage(command_profile, command, "executed", command, domain),
                "observability": self._observability(command_profile, command, "executed", domain, result),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "resume":
            result = {"command_state": "resumed", "domain": domain}
            return {
                "status": "executed",
                "reason": "resume",
                "command_result": result,
                "lineage": self._lineage(command_profile, command, "executed", "resume", domain),
                "observability": self._observability(command_profile, command, "executed", domain, {"observability": result}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "status":
            result = {"command_state": "status_reported", "domain": domain, "surface": dict(unified_result.get("surface", {}))}
            return {
                "status": "executed",
                "reason": "status",
                "command_result": result,
                "lineage": self._lineage(command_profile, command, "executed", "status", domain),
                "observability": self._observability(command_profile, command, "executed", domain, {"observability": result}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "inspect":
            result = {"command_state": "inspection_ready", "domain": domain, "lineage": dict(unified_result.get("lineage", {}))}
            return {
                "status": "executed",
                "reason": "inspect",
                "command_result": result,
                "lineage": self._lineage(command_profile, command, "executed", "inspect", domain),
                "observability": self._observability(command_profile, command, "executed", domain, {"observability": result}),
                "replay": dict(unified_result.get("replay", {})),
            }

        if command == "replay":
            result = {"command_state": "replay_ready", "domain": domain}
            return {
                "status": "executed",
                "reason": "replay",
                "command_result": result,
                "lineage": self._lineage(command_profile, command, "executed", "replay", domain),
                "observability": self._observability(command_profile, command, "executed", domain, {"observability": result}),
                "replay": dict(unified_result.get("replay", {})),
            }

        result = {"command_state": "started", "domain": domain}
        return {
            "status": "executed",
            "reason": "start",
            "command_result": result,
            "lineage": self._lineage(command_profile, command, "executed", "start", domain),
            "observability": self._observability(command_profile, command, "executed", domain, {"observability": result}),
            "replay": dict(unified_result.get("replay", {})),
        }

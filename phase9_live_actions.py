from __future__ import annotations

from typing import Any, Dict

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_deployment import DeploymentRollbackGate
from phase9_commands import CommandSurfaceProfile, OperatorCommandEngine


class LiveControlActionEngine:
    ACTION_SIGNATURE = "operator_command:v1"

    _ACTION_ROUTES = {
        "start": "activation_control",
        "pause": "intervention_control",
        "resume": "activation_control",
        "drain": "intervention_control",
        "rollback": "intervention_control",
        "recover": "intervention_control",
        "inspect": "monitoring_view",
        "replay": "lineage_replay",
        "status": "monitoring_view",
    }

    def __init__(self) -> None:
        self.command_engine = OperatorCommandEngine()

    def _lineage(self, profile: CommandSurfaceProfile, action: str, status: str, reason: str, domain: str) -> Dict[str, Any]:
        return {
            "signature": self.ACTION_SIGNATURE,
            "scope": "phase9_live_actions",
            "surface_id": profile.surface_id,
            "command": action,
            "status": status,
            "reason": reason,
            "domain": domain,
            "route": self._ACTION_ROUTES.get(action, "activation_control"),
        }

    def _observability(
        self,
        profile: CommandSurfaceProfile,
        action: str,
        status: str,
        domain: str,
        reason: str,
        deployment_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "command": {
                "signature": self.ACTION_SIGNATURE,
                "surface_id": profile.surface_id,
                "command": action,
                "status": status,
                "reason": reason,
                "domain": domain,
                "route": self._ACTION_ROUTES.get(action, "activation_control"),
                "observability_scope": profile.observability_scope,
            },
            "deployment_state": dict(deployment_state),
        }

    def _domain(self, unified_result: Dict[str, Any]) -> str:
        return str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())

    def _validate_deployment_state(self, deployment_state: Dict[str, Any]) -> Dict[str, Any]:
        required = ("activation", "rollout", "monitoring", "intervention")
        missing = [key for key in required if str(deployment_state.get(key, "")).strip() == ""]
        if missing:
            return {"ok": False, "reason": "deployment_state_incomplete", "missing": missing}
        return {"ok": True, "reason": "deployment_state_valid", "missing": []}

    def execute_live_action(
        self,
        *,
        action: str,
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
        deployment_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        domain = self._domain(unified_result)
        route = self._ACTION_ROUTES.get(action, "activation_control")

        deployment_check = self._validate_deployment_state(deployment_state)
        if not deployment_check["ok"]:
            reason = str(deployment_check["reason"])
            return {
                "action": action,
                "route": route,
                "status": "blocked",
                "reason": reason,
                "command_result": {
                    "missing_deployment_state": deployment_check["missing"],
                    "domain": domain,
                },
                "lineage": self._lineage(command_profile, action, "blocked", reason, domain),
                "observability": self._observability(
                    command_profile,
                    action,
                    "blocked",
                    domain,
                    reason,
                    deployment_state,
                ),
                "replay": dict(unified_result.get("replay", {})),
            }

        command_result = self.command_engine.execute_command(
            command=action,
            command_profile=command_profile,
            transport_executor=transport_executor,
            unified_result=unified_result,
            gate=gate,
            envelope=envelope,
            policy_profile=policy_profile,
            destination=destination,
            auth_posture=auth_posture,
            risk_score=risk_score,
            rollback_gate=rollback_gate,
            metrics=metrics,
        )
        status = str(command_result.get("status", "blocked"))
        reason = str(command_result.get("reason", "blocked"))

        normalized = {
            "action": action,
            "route": route,
            "status": status,
            "reason": reason,
            "command_result": dict(command_result.get("command_result", {})),
            "lineage": dict(command_result.get("lineage", {})),
            "observability": dict(command_result.get("observability", {})),
            "replay": dict(command_result.get("replay", {})),
        }
        if isinstance(normalized["lineage"], dict):
            normalized["lineage"]["scope"] = "phase9_live_actions"
            normalized["lineage"]["route"] = route
        if isinstance(normalized["observability"], dict):
            normalized["observability"]["deployment_state"] = dict(deployment_state)
            command_obs = normalized["observability"].get("command")
            if isinstance(command_obs, dict):
                command_obs["route"] = route
                normalized["observability"]["command"] = command_obs

        return normalized

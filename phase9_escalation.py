from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import GovernedTransportEnvelope
from phase8_deployment import DeploymentRollbackGate
from phase9_commands import CommandSurfaceProfile
from phase9_live_actions import LiveControlActionEngine


@dataclass
class OperatorAuthorityProfile:
    operator_id: str
    supervision_level: str
    allowed_commands: list[str]
    rollback_authority: bool
    recovery_authority: bool
    escalation_tier: str
    arbitration_priority: int


@dataclass
class OperatorEscalationRules:
    command_tiers: Dict[str, str] = field(
        default_factory=lambda: {
            "start": "none",
            "pause": "single",
            "resume": "single",
            "drain": "single",
            "rollback": "quorum",
            "recover": "dual",
            "inspect": "none",
            "replay": "none",
            "status": "none",
        }
    )

    def required_tier(self, action: str) -> str:
        return str(self.command_tiers.get(action, "single")).strip() or "single"

    def satisfies(self, action: str, escalation_chain: list[str]) -> tuple[bool, str]:
        tier = self.required_tier(action)
        approvals = len({item for item in escalation_chain if str(item).strip()})
        required = 0
        if tier == "single":
            required = 1
        elif tier == "dual":
            required = 2
        elif tier == "quorum":
            required = 2

        if approvals < required:
            return False, f"escalation_{tier}_required"
        return True, "escalation_ok"


@dataclass
class OperatorArbitrationRules:
    conflicts: Dict[str, Set[str]] = field(
        default_factory=lambda: {
            "pause": {"resume", "start"},
            "resume": {"pause", "drain"},
            "rollback": {"start", "resume", "recover"},
            "recover": {"rollback"},
            "drain": {"resume", "start"},
        }
    )

    def is_conflict(self, action: str, other_action: str) -> bool:
        action_conflicts = self.conflicts.get(action, set())
        reverse_conflicts = self.conflicts.get(other_action, set())
        return other_action in action_conflicts or action in reverse_conflicts


class OperatorAuthorityValidator:
    def validate(
        self,
        *,
        action: str,
        operator: OperatorAuthorityProfile,
        command_profile: CommandSurfaceProfile,
    ) -> tuple[bool, str]:
        if action not in set(operator.allowed_commands):
            return False, "operator_command_not_allowed"
        if operator.supervision_level != command_profile.required_supervision_level:
            return False, "operator_supervision_mismatch"
        if action == "rollback" and not operator.rollback_authority:
            return False, "operator_lacks_rollback_authority"
        if action == "recover" and not operator.recovery_authority:
            return False, "operator_lacks_recovery_authority"
        return True, "authority_ok"


class OperatorArbitrationEngine:
    _SUPERVISION_WEIGHT = {
        "strict": 3,
        "standard": 2,
        "lenient": 1,
    }

    def resolve(
        self,
        *,
        action: str,
        operator: OperatorAuthorityProfile,
        escalation_chain: list[str],
        conflicting_command: Optional[Dict[str, Any]],
        arbitration_rules: OperatorArbitrationRules,
    ) -> Dict[str, Any]:
        if not conflicting_command:
            return {
                "status": "no_conflict",
                "winner_operator_id": operator.operator_id,
                "loser_operator_id": "none",
                "winner_action": action,
            }

        other_action = str(conflicting_command.get("action", "")).strip()
        other_operator = conflicting_command.get("operator")
        if not isinstance(other_operator, OperatorAuthorityProfile):
            return {
                "status": "invalid_conflict_context",
                "winner_operator_id": operator.operator_id,
                "loser_operator_id": "none",
                "winner_action": action,
            }

        if not arbitration_rules.is_conflict(action, other_action):
            return {
                "status": "no_conflict",
                "winner_operator_id": operator.operator_id,
                "loser_operator_id": other_operator.operator_id,
                "winner_action": action,
            }

        my_score = self._score(operator, len(escalation_chain))
        other_score = self._score(other_operator, 1)

        if my_score >= other_score:
            return {
                "status": "resolved",
                "winner_operator_id": operator.operator_id,
                "loser_operator_id": other_operator.operator_id,
                "winner_action": action,
            }
        return {
            "status": "resolved",
            "winner_operator_id": other_operator.operator_id,
            "loser_operator_id": operator.operator_id,
            "winner_action": other_action,
        }

    def _score(self, profile: OperatorAuthorityProfile, escalation_count: int) -> tuple[int, int, int, int]:
        return (
            self._SUPERVISION_WEIGHT.get(profile.supervision_level, 0),
            int(profile.arbitration_priority),
            int(escalation_count),
            1 if profile.rollback_authority else 0,
        )


class OperatorCommandLineageV2:
    SIGNATURE = "operator_command:v2"

    def build(
        self,
        *,
        action: str,
        operator: OperatorAuthorityProfile,
        escalation_chain: list[str],
        arbitration: Dict[str, Any],
        status: str,
        reason: str,
        domain: str,
    ) -> Dict[str, Any]:
        return {
            "signature": self.SIGNATURE,
            "scope": "phase9_escalation",
            "command": action,
            "status": status,
            "reason": reason,
            "domain": domain,
            "operator_id": operator.operator_id,
            "supervision_level": operator.supervision_level,
            "escalation_chain": list(escalation_chain),
            "arbitration_result": dict(arbitration),
            "authority_signature": f"authority:{operator.operator_id}:{operator.supervision_level}",
        }


class OperatorEscalationEngine:
    def __init__(
        self,
        *,
        escalation_rules: OperatorEscalationRules,
        arbitration_rules: OperatorArbitrationRules,
        arbitration_engine: OperatorArbitrationEngine,
    ) -> None:
        self.escalation_rules = escalation_rules
        self.arbitration_rules = arbitration_rules
        self.arbitration_engine = arbitration_engine
        self.authority_validator = OperatorAuthorityValidator()
        self.lineage_v2 = OperatorCommandLineageV2()
        self.live_action_engine = LiveControlActionEngine()

    def execute_operator_command(
        self,
        *,
        action: str,
        operator: OperatorAuthorityProfile,
        escalation_chain: list[str],
        conflicting_command: Optional[Dict[str, Any]],
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
        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())

        authority_ok, authority_reason = self.authority_validator.validate(
            action=action,
            operator=operator,
            command_profile=command_profile,
        )
        arbitration = self.arbitration_engine.resolve(
            action=action,
            operator=operator,
            escalation_chain=escalation_chain,
            conflicting_command=conflicting_command,
            arbitration_rules=self.arbitration_rules,
        )

        if not authority_ok:
            return self._blocked_result(
                action=action,
                operator=operator,
                reason=authority_reason,
                domain=domain,
                escalation_chain=escalation_chain,
                arbitration=arbitration,
                unified_result=unified_result,
            )

        escalation_ok, escalation_reason = self.escalation_rules.satisfies(action, escalation_chain)
        if not escalation_ok:
            return self._blocked_result(
                action=action,
                operator=operator,
                reason=escalation_reason,
                domain=domain,
                escalation_chain=escalation_chain,
                arbitration=arbitration,
                unified_result=unified_result,
            )

        if arbitration.get("winner_operator_id") != operator.operator_id:
            return self._blocked_result(
                action=action,
                operator=operator,
                reason="arbitration_lost",
                domain=domain,
                escalation_chain=escalation_chain,
                arbitration=arbitration,
                unified_result=unified_result,
            )

        result = self.live_action_engine.execute_live_action(
            action=action,
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
            deployment_state=deployment_state,
        )
        status = str(result.get("status", "blocked"))
        reason = str(result.get("reason", "blocked"))

        lineage = self.lineage_v2.build(
            action=action,
            operator=operator,
            escalation_chain=escalation_chain,
            arbitration=arbitration,
            status=status,
            reason=reason,
            domain=domain,
        )

        return {
            "action": action,
            "route": result.get("route", "activation_control"),
            "status": status,
            "reason": reason,
            "arbitration": arbitration,
            "command_result": dict(result.get("command_result", {})),
            "lineage": lineage,
            "observability": {
                "command": {
                    "signature": OperatorCommandLineageV2.SIGNATURE,
                    "operator_id": operator.operator_id,
                    "supervision_level": operator.supervision_level,
                    "route": result.get("route", "activation_control"),
                    "status": status,
                },
                "arbitration": dict(arbitration),
                "escalation_chain": list(escalation_chain),
            },
            "replay": dict(result.get("replay", {})),
        }

    def _blocked_result(
        self,
        *,
        action: str,
        operator: OperatorAuthorityProfile,
        reason: str,
        domain: str,
        escalation_chain: list[str],
        arbitration: Dict[str, Any],
        unified_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        lineage = self.lineage_v2.build(
            action=action,
            operator=operator,
            escalation_chain=escalation_chain,
            arbitration=arbitration,
            status="blocked",
            reason=reason,
            domain=domain,
        )
        return {
            "action": action,
            "route": "governance_gate",
            "status": "blocked",
            "reason": reason,
            "arbitration": arbitration,
            "command_result": {"domain": domain},
            "lineage": lineage,
            "observability": {
                "command": {
                    "signature": OperatorCommandLineageV2.SIGNATURE,
                    "operator_id": operator.operator_id,
                    "supervision_level": operator.supervision_level,
                    "status": "blocked",
                    "reason": reason,
                },
                "arbitration": dict(arbitration),
                "escalation_chain": list(escalation_chain),
            },
            "replay": dict(unified_result.get("replay", {})),
        }

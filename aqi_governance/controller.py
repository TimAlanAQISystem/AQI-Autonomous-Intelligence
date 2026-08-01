from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from . import rules
from .state import (
    DEFAULT_STATE_PATH,
    GovernanceState,
    load_state,
    save_state,
    update_from_conversation_metrics,
    update_from_mission_result,
)
from .telemetry import DEFAULT_TELEMETRY_DIR, append_history_entry, record_event, record_state_snapshot


@dataclass
class GovernanceDecision:
    allowed: bool
    decision: str
    requires_operator_review: bool
    reason: str
    rule_ids: list[str]
    risk_level: str


class GlobalGovernanceController:
    def __init__(
        self,
        *,
        state_path: str | Path = DEFAULT_STATE_PATH,
        telemetry_dir: str | Path = DEFAULT_TELEMETRY_DIR,
        rrg_path: str | Path = "RRG-I.md",
    ):
        self.state_path = Path(state_path)
        self.telemetry_dir = Path(telemetry_dir)
        self.rrg_path = Path(rrg_path)

    def _utc_now(self) -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    def _as_decision(self, result: rules.RuleResult) -> GovernanceDecision:
        return GovernanceDecision(
            allowed=result.allowed,
            decision=result.decision,
            requires_operator_review=result.requires_operator_review,
            reason=result.reason,
            rule_ids=list(result.rule_ids),
            risk_level=result.risk_level,
        )

    def _append_rrg_line(self, *, event_type: str, details: str) -> None:
        if not self.rrg_path.exists():
            return

        line = f"\n- {self._utc_now()} | global_governance | event={event_type} | {details}\n"
        with self.rrg_path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def can_start_mission(self, mission_type: str, context: Dict[str, Any]) -> GovernanceDecision:
        state = load_state(self.state_path)
        result = rules.evaluate_mission_start(mission_type, state, context)
        decision = self._as_decision(result)

        record_event(
            {
                "event": "can_start_mission",
                "mission_type": mission_type,
                "context": context,
                "decision": asdict(decision),
            },
            telemetry_dir=self.telemetry_dir,
        )

        dry_run = bool(context.get("dry_run", False))
        if decision.allowed and (not dry_run):
            state.total_missions_started += 1
            state.active_mission = {
                "mission_type": mission_type,
                "started_at_utc": self._utc_now(),
                "context": context,
            }
            state.operator_review_required = state.operator_review_required or decision.requires_operator_review
            save_state(state, self.state_path)
            record_state_snapshot(state, telemetry_dir=self.telemetry_dir)

        append_history_entry(
            {
                "event": "mission_gate_decision",
                "mission_type": mission_type,
                "decision": asdict(decision),
            },
            telemetry_dir=self.telemetry_dir,
        )

        if decision.decision in {"deny", "escalate"}:
            self._append_rrg_line(
                event_type="mission_gating",
                details=(
                    f"mission_type={mission_type} decision={decision.decision} "
                    f"rules={','.join(decision.rule_ids)} risk={decision.risk_level}"
                ),
            )

        return decision

    def register_mission_result(self, mission_type: str, result: Dict[str, Any], metrics: Dict[str, Any]) -> None:
        state = load_state(self.state_path)
        update_from_mission_result(state, mission_type=mission_type, result=result, metrics=metrics)
        save_state(state, self.state_path)
        rollup = state.last_mission_result or {}

        record_event(
            {
                "event": "register_mission_result",
                "mission_type": mission_type,
                "result": result,
                "metrics": metrics,
            },
            telemetry_dir=self.telemetry_dir,
        )
        record_state_snapshot(state, telemetry_dir=self.telemetry_dir)
        append_history_entry(
            {
                "event": "mission_result",
                "mission_type": mission_type,
                "status": rollup.get("status", result.get("status", "unknown")),
                "summary_type": rollup.get("summary_type", str(result.get("status", "unknown")).lower()),
                "failure_reason": rollup.get("failure_reason", ""),
                "failure_class": rollup.get("failure_class", ""),
                "failure_stage": rollup.get("failure_stage", ""),
                "artifact_integrity": rollup.get("artifact_integrity", {}),
                "stability_preview": rollup.get("stability_preview", {}),
                "mission_completed": bool(rollup.get("passed", False)),
                "global_stability_score": state.global_stability_score,
                "risk_level": state.risk_level,
            },
            telemetry_dir=self.telemetry_dir,
        )

    def evaluate_conversation_turn(self, turn_context: Dict[str, Any]) -> GovernanceDecision:
        state = load_state(self.state_path)
        result = rules.evaluate_conversation(turn_context, state)
        decision = self._as_decision(result)

        stability_score = float(turn_context.get("stability_score", state.global_stability_score))
        escalation_rate = float(turn_context.get("escalation_rate", state.global_escalation_rate))
        unauthorized = 1 if decision.decision == "deny" and "COMMITMENT" in " ".join(decision.rule_ids) else 0

        update_from_conversation_metrics(
            state,
            stability_score=stability_score,
            escalation_rate=escalation_rate,
            unauthorized_commitment_blocks=unauthorized,
        )
        state.operator_review_required = state.operator_review_required or decision.requires_operator_review
        save_state(state, self.state_path)

        record_event(
            {
                "event": "evaluate_conversation_turn",
                "turn_context": turn_context,
                "decision": asdict(decision),
            },
            telemetry_dir=self.telemetry_dir,
        )
        record_state_snapshot(state, telemetry_dir=self.telemetry_dir)

        if decision.decision in {"deny", "escalate"}:
            self._append_rrg_line(
                event_type="conversation_governance",
                details=(
                    f"decision={decision.decision} rules={','.join(decision.rule_ids)} "
                    f"risk={decision.risk_level} stability={state.global_stability_score:.4f}"
                ),
            )

        return decision

    def update_global_risk(self, metrics: Dict[str, Any]) -> GovernanceState:
        state = load_state(self.state_path)
        risk_score = float(metrics.get("risk_score", 0.0))

        if risk_score >= 0.8:
            state.risk_level = "red"
            state.operator_review_required = True
        elif risk_score >= 0.45:
            state.risk_level = "yellow"
        else:
            state.risk_level = "green"

        save_state(state, self.state_path)

        record_event(
            {
                "event": "update_global_risk",
                "metrics": metrics,
                "risk_level": state.risk_level,
            },
            telemetry_dir=self.telemetry_dir,
        )
        record_state_snapshot(state, telemetry_dir=self.telemetry_dir)
        return state

    def evaluate_qpc_decision(self, context: Dict[str, Any], decision: Dict[str, Any]) -> GovernanceDecision:
        state = load_state(self.state_path)
        result = rules.evaluate_qpc_decision(decision, state, context)
        governance = self._as_decision(result)

        record_event(
            {
                "event": "evaluate_qpc_decision",
                "context": context,
                "qpc_decision": decision,
                "decision": asdict(governance),
            },
            telemetry_dir=self.telemetry_dir,
        )
        append_history_entry(
            {
                "event": "qpc_governance_decision",
                "context": context,
                "qpc_action": decision.get("action", "unknown"),
                "decision": asdict(governance),
            },
            telemetry_dir=self.telemetry_dir,
        )

        if governance.decision in {"deny", "escalate"}:
            self._append_rrg_line(
                event_type="qpc_governance",
                details=(
                    f"decision={governance.decision} rules={','.join(governance.rule_ids)} "
                    f"risk={governance.risk_level}"
                ),
            )

        return governance

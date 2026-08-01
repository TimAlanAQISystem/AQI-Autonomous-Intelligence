from __future__ import annotations

import importlib.util
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    from aqi_agents.orchestrator import MultiAgentOrchestrator
    from aqi_governance.controller import GlobalGovernanceController
    from qpc.context import from_conversation_turn as build_qpc_context_from_turn
    from qpc.core import run_qpc_analysis, run_qpc_decision, run_qpc_plan
    from qpc.telemetry import record_qpc_error, record_qpc_trace
    from .closing import apply as apply_closing
    from .governance import ConversationGovernance, GovernanceDecision
    from .intent_router import IntentResult, IntentRouter
    from .negotiation import apply as apply_negotiation
    from .persona import PersonaSpec, default_persona, render_response
except ImportError:
    try:
        from qpc.context import from_conversation_turn as build_qpc_context_from_turn
        from qpc.core import run_qpc_analysis, run_qpc_decision, run_qpc_plan
        from qpc.telemetry import record_qpc_error, record_qpc_trace
    except ImportError:
        build_qpc_context_from_turn = None  # type: ignore
        run_qpc_analysis = None  # type: ignore
        run_qpc_decision = None  # type: ignore
        run_qpc_plan = None  # type: ignore
        record_qpc_error = None  # type: ignore
        record_qpc_trace = None  # type: ignore
    try:
        from aqi_agents.orchestrator import MultiAgentOrchestrator
    except ImportError:
        MultiAgentOrchestrator = None  # type: ignore
    try:
        from aqi_governance.controller import GlobalGovernanceController
    except ImportError:
        GlobalGovernanceController = None  # type: ignore
    from closing import apply as apply_closing
    from governance import ConversationGovernance, GovernanceDecision
    from intent_router import IntentResult, IntentRouter
    from negotiation import apply as apply_negotiation
    from persona import PersonaSpec, default_persona, render_response


@dataclass
class EngineConfig:
    session_id: str
    operator_name: str = "Tim"
    enable_qpc_reasoning: bool = True
    enable_qpc: bool = True
    allow_mission_triggers: bool = True
    enable_multi_agent: bool = True


@dataclass
class ConversationTurn:
    turn_index: int
    user_message: str
    intent: IntentResult
    governance: GovernanceDecision
    response_text: str
    mission_actions: List[Dict[str, Any]] = field(default_factory=list)
    negotiation_actions: List[Dict[str, Any]] = field(default_factory=list)
    close_actions: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_note: str = ""
    timestamp_utc: str = ""


@dataclass
class ConversationState:
    session_id: str
    started_at_utc: str
    turns: List[ConversationTurn] = field(default_factory=list)
    stage: str = "conversation_start"


@dataclass
class EngineResponse:
    response_text: str
    intent_label: str
    confidence: float
    checkpoint_id: str
    stage: str
    needs_operator_review: bool
    mission_actions: List[Dict[str, Any]]
    negotiation_actions: List[Dict[str, Any]]
    close_actions: List[Dict[str, Any]]
    telemetry: Dict[str, Any]


class ConversationEngine:
    """Alan Conversational Operator Layer (Slice 1) engine scaffold."""

    def __init__(self, config: EngineConfig, persona: PersonaSpec | None = None):
        self.config = config
        self.persona = persona or default_persona()
        self.intent_router = IntentRouter()
        self.governance = ConversationGovernance()
        self.state = ConversationState(
            session_id=config.session_id,
            started_at_utc=self._utc_now(),
        )
        if GlobalGovernanceController is not None:
            session_key = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in config.session_id)
            state_path = Path("reports") / "aqi_governance" / "conversation_sessions" / f"{session_key}.json"
            telemetry_dir = Path("reports") / "aqi_governance" / "conversation_sessions" / session_key
            self.global_governance = GlobalGovernanceController(
                state_path=state_path,
                telemetry_dir=telemetry_dir,
            )
        else:
            self.global_governance = None

        if config.enable_multi_agent and MultiAgentOrchestrator is not None:
            self.multi_agent_orchestrator = MultiAgentOrchestrator(governance_controller=self.global_governance)
        else:
            self.multi_agent_orchestrator = None

    def handle_turn(self, user_message: str) -> EngineResponse:
        turn_index = len(self.state.turns)
        pre_governance_decision = None
        if self.global_governance is not None:
            pre_governance_decision = self.global_governance.evaluate_conversation_turn(
                {
                    "message": user_message,
                    "turn_index": turn_index,
                    "intent_label": "pre_intent",
                    "stability_score": self._stability_signal_preview(),
                    "escalation_rate": self._escalation_rate_preview(),
                    "risk_score": self._risk_signal_from_message(user_message),
                }
            )

        if pre_governance_decision is not None and (not pre_governance_decision.allowed):
            intent = IntentResult(
                label="escalation",
                confidence=0.99,
                signals=["global_governance_deny"],
                mission_trigger="",
            )
        else:
            intent = self.intent_router.detect(user_message)

        governance = self.governance.evaluate(intent.label, user_message, turn_index)

        post_governance_decision = None
        if self.global_governance is not None:
            post_governance_decision = self.global_governance.evaluate_conversation_turn(
                {
                    "message": user_message,
                    "turn_index": turn_index,
                    "intent_label": intent.label,
                    "stability_score": self._stability_signal_preview(),
                    "escalation_rate": self._escalation_rate_preview(),
                    "risk_score": self._risk_signal_from_intent(intent.label, user_message),
                }
            )
            if post_governance_decision.decision == "deny":
                governance = GovernanceDecision(
                    checkpoint_id="OP-CONVO-ESCALATE",
                    stage="conversation_escalate",
                    allowed=False,
                    needs_operator_review=True,
                    reason=post_governance_decision.reason,
                )
                intent = IntentResult(
                    label="escalation",
                    confidence=max(intent.confidence, 0.95),
                    signals=[*intent.signals, "global_governance_deny"],
                    mission_trigger="",
                )
            elif post_governance_decision.requires_operator_review and governance.allowed:
                governance = GovernanceDecision(
                    checkpoint_id=governance.checkpoint_id,
                    stage=governance.stage,
                    allowed=governance.allowed,
                    needs_operator_review=True,
                    reason=f"{governance.reason} Global governance: {post_governance_decision.reason}",
                )

        qpc_payload = self._run_qpc_intelligence(intent, user_message)
        reasoning_note = self._reason_about_turn(intent, user_message)
        if qpc_payload.get("applied"):
            reasoning_note = f"{reasoning_note}; {qpc_payload.get('rationale', '')}".strip()
        mission_actions = self._mission_actions(intent, governance)
        if qpc_payload.get("applied") and qpc_payload.get("annotations"):
            mission_actions.append(
                {
                    "type": "qpc_annotation",
                    "session_id": self.state.session_id,
                    "qpc": qpc_payload.get("annotations"),
                }
            )
        negotiation_actions: List[Dict[str, Any]] = []
        close_actions: List[Dict[str, Any]] = []
        agent_coordination = self._coordinate_internal_agents(intent, user_message)

        coordination_status = str((agent_coordination or {}).get("status", "")).lower()
        if coordination_status in {"blocked", "failed", "error"} and governance.allowed:
            coordination_reason = str((agent_coordination or {}).get("reason", "agent coordination degraded"))
            governance = GovernanceDecision(
                checkpoint_id=governance.checkpoint_id,
                stage=governance.stage,
                allowed=True,
                needs_operator_review=True,
                reason=f"{governance.reason} Agent coordination: {coordination_reason}",
            )

        if not governance.allowed:
            response_text = (
                f"{self.persona.name}: I need to escalate this before making any commitment. "
                f"{governance.reason}"
            )
        elif intent.label == "negotiation":
            negotiation_result = apply_negotiation(
                message=user_message,
                reasoning_note=reasoning_note,
                operator_review_required=governance.needs_operator_review,
            )
            response_text = negotiation_result.response_text
            negotiation_actions = [dict(item) for item in negotiation_result.negotiation_actions]
        elif intent.label == "closing_signal":
            mission_hint = next((item.get("mission_id", "") for item in mission_actions if "mission_id" in item), "")
            closing_result = apply_closing(
                reasoning_note=reasoning_note,
                operator_review_required=governance.needs_operator_review,
                mission_hint=mission_hint,
            )
            response_text = closing_result.response_text
            close_actions = [dict(item) for item in closing_result.close_actions]
        else:
            mission_hint = next((item.get("mission_id", "") for item in mission_actions if "mission_id" in item), "")
            response_text = render_response(
                persona=self.persona,
                intent_label=intent.label,
                user_message=user_message,
                reasoning_note=reasoning_note,
                mission_hint=mission_hint,
            )

        turn = ConversationTurn(
            turn_index=turn_index,
            user_message=user_message,
            intent=intent,
            governance=governance,
            response_text=response_text,
            mission_actions=mission_actions,
            negotiation_actions=negotiation_actions,
            close_actions=close_actions,
            reasoning_note=reasoning_note,
            timestamp_utc=self._utc_now(),
        )
        self.state.turns.append(turn)
        self.state.stage = governance.stage

        telemetry = {
            "session_id": self.state.session_id,
            "turn_index": turn_index,
            "intent": asdict(intent),
            "governance": asdict(governance),
            "global_governance_pre": asdict(pre_governance_decision) if pre_governance_decision is not None else None,
            "global_governance_post": asdict(post_governance_decision) if post_governance_decision is not None else None,
            "mission_actions": mission_actions,
            "negotiation_actions": negotiation_actions,
            "close_actions": close_actions,
            "agent_coordination": agent_coordination,
            "qpc": qpc_payload,
            "stage": self.state.stage,
            "timestamp_utc": turn.timestamp_utc,
        }

        return EngineResponse(
            response_text=response_text,
            intent_label=intent.label,
            confidence=intent.confidence,
            checkpoint_id=governance.checkpoint_id,
            stage=governance.stage,
            needs_operator_review=governance.needs_operator_review,
            mission_actions=mission_actions,
            negotiation_actions=negotiation_actions,
            close_actions=close_actions,
            telemetry=telemetry,
        )

    def _run_qpc_intelligence(self, intent: IntentResult, user_message: str) -> Dict[str, Any]:
        if not self.config.enable_qpc:
            return {"enabled": False, "applied": False, "reason": "qpc_disabled"}

        if build_qpc_context_from_turn is None or run_qpc_decision is None:
            return {"enabled": False, "applied": False, "reason": "qpc_unavailable"}

        context = build_qpc_context_from_turn(
            session_id=self.state.session_id,
            role="operator_agent",
            intent_label=intent.label,
            user_message=user_message,
            mission_type=intent.mission_trigger,
            metrics={
                "stability_score": self._stability_signal_preview(),
                "risk_score": self._risk_signal_from_intent(intent.label, user_message),
                "escalation_rate": self._escalation_rate_preview(),
            },
        )

        try:
            decision = run_qpc_decision(context)
            analysis = run_qpc_analysis(context) if run_qpc_analysis is not None else None
            plan = run_qpc_plan(context) if run_qpc_plan is not None else None

            governance_outcome = None
            if self.global_governance is not None:
                governance_outcome = self.global_governance.evaluate_qpc_decision(context.to_dict(), decision.to_dict())
                if (not governance_outcome.allowed) or (governance_outcome.decision == "deny"):
                    payload = {
                        "enabled": True,
                        "applied": False,
                        "governance": asdict(governance_outcome),
                        "decision": decision.to_dict(),
                    }
                    if record_qpc_trace is not None:
                        record_qpc_trace(
                            context,
                            {"decision": decision.to_dict(), "analysis": analysis.to_dict() if analysis else {}, "plan": plan.to_dict() if plan else {}},
                            governance_outcome=asdict(governance_outcome),
                        )
                    return payload
                if "QPC_LOW_CONFIDENCE_DOWNGRADE" in governance_outcome.rule_ids:
                    payload = {
                        "enabled": True,
                        "applied": False,
                        "governance": asdict(governance_outcome),
                        "decision": decision.to_dict(),
                        "reason": "qpc_downgraded_low_confidence",
                    }
                    if record_qpc_trace is not None:
                        record_qpc_trace(
                            context,
                            {"decision": decision.to_dict(), "analysis": analysis.to_dict() if analysis else {}, "plan": plan.to_dict() if plan else {}},
                            governance_outcome=asdict(governance_outcome),
                        )
                    return payload

            result = {
                "enabled": True,
                "applied": True,
                "rationale": decision.rationale,
                "annotations": {
                    "action": decision.action,
                    "confidence": decision.confidence,
                    "risk": decision.risk,
                    "surplus_score": decision.surplus_score,
                },
                "decision": decision.to_dict(),
                "analysis": analysis.to_dict() if analysis is not None else {},
                "plan": plan.to_dict() if plan is not None else {},
                "governance": asdict(governance_outcome) if governance_outcome is not None else None,
            }
            if record_qpc_trace is not None:
                record_qpc_trace(
                    context,
                    {
                        "decision": result["decision"],
                        "analysis": result["analysis"],
                        "plan": result["plan"],
                    },
                    governance_outcome=result.get("governance") or {},
                )
            return result
        except Exception as exc:  # pragma: no cover - defensive fallback.
            if record_qpc_error is not None:
                record_qpc_error(context, str(exc))
            return {
                "enabled": True,
                "applied": False,
                "reason": "qpc_error",
                "error": str(exc),
            }

    def _coordinate_internal_agents(self, intent: IntentResult, user_message: str) -> Dict[str, Any] | None:
        if self.multi_agent_orchestrator is None:
            return None

        try:
            return self.multi_agent_orchestrator.coordinate_turn(
                session_id=self.state.session_id,
                intent_label=intent.label,
                user_message=user_message,
                profile="conversation",
                script="default",
            )
        except Exception as exc:  # pragma: no cover - defensive fallback.
            return {
                "status": "error",
                "reason": str(exc),
            }

    def state_snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.state.session_id,
            "started_at_utc": self.state.started_at_utc,
            "stage": self.state.stage,
            "turn_count": len(self.state.turns),
            "turns": [
                {
                    "turn_index": t.turn_index,
                    "user_message": t.user_message,
                    "intent": asdict(t.intent),
                    "governance": asdict(t.governance),
                    "response_text": t.response_text,
                    "mission_actions": t.mission_actions,
                    "negotiation_actions": t.negotiation_actions,
                    "close_actions": t.close_actions,
                    "reasoning_note": t.reasoning_note,
                    "timestamp_utc": t.timestamp_utc,
                }
                for t in self.state.turns
            ],
        }

    def _reason_about_turn(self, intent: IntentResult, user_message: str) -> str:
        if not self.config.enable_qpc_reasoning:
            return "Reasoning path: deterministic heuristic mode"

        qpc_available = importlib.util.find_spec("qpc2_engine") is not None or importlib.util.find_spec("qpc_kernel") is not None
        if qpc_available:
            return (
                "Reasoning path: QPC-aware bounded reasoning; "
                f"intent={intent.label}, confidence={intent.confidence:.2f}"
            )

        return (
            "Reasoning path: fallback bounded reasoning; "
            f"intent={intent.label}, message_length={len(user_message)}"
        )

    def _mission_actions(self, intent: IntentResult, governance: GovernanceDecision) -> List[Dict[str, Any]]:
        if not self.config.allow_mission_triggers:
            return []

        actions: List[Dict[str, Any]] = []

        if intent.mission_trigger == "merchant_daily_snapshot":
            actions.append(self._build_mission_action("merchant_daily_snapshot", "Conversation indicates daily operational snapshot need."))

        if intent.mission_trigger == "merchant_weekly_report":
            actions.append(self._build_mission_action("merchant_weekly_report", "Conversation indicates weekly strategic report need."))

        if intent.label in {"negotiation", "closing_signal"} and self._stability_acceptable(governance):
            actions.append(
                self._build_mission_action(
                    "dealflow_conversation",
                    "Negotiation/close stage reached with acceptable conversation stability.",
                    stage=governance.stage,
                )
            )

        return actions

    def _build_mission_action(self, mission_id: str, reason: str, stage: str = "") -> Dict[str, Any]:
        action: Dict[str, Any] = {
            "mission_id": mission_id,
            "action": "recommend_run",
            "reason": reason,
        }

        if stage:
            action["stage"] = stage
        action["session_id"] = self.state.session_id

        if self.global_governance is None:
            return action

        decision = self.global_governance.can_start_mission(
            mission_id,
            {
                "source": "conversation_engine",
                "session_id": self.state.session_id,
                "stability_score": self._stability_signal_preview(),
                "risk_score": self._risk_signal_from_intent(mission_id, reason),
                "dry_run": True,
            },
        )

        action["global_governance_decision"] = asdict(decision)
        if not decision.allowed:
            action["action"] = "requires_operator_review"
            action["blocked"] = True
            action["reason"] = f"{reason} Global governance block: {decision.reason}"
        elif decision.requires_operator_review:
            action["requires_operator_review"] = True

        return action

    def _stability_signal_preview(self) -> float:
        if not self.state.turns:
            return 1.0

        governed_turns = sum(1 for turn in self.state.turns if turn.governance.allowed)
        escalation_count = sum(1 for turn in self.state.turns if turn.governance.checkpoint_id == "OP-CONVO-ESCALATE")
        base = governed_turns / max(1, len(self.state.turns))
        penalty = min(0.4, escalation_count * 0.1)
        return max(0.0, min(1.0, base - penalty))

    def _escalation_rate_preview(self) -> float:
        if not self.state.turns:
            return 0.0
        escalation_count = sum(1 for turn in self.state.turns if turn.governance.checkpoint_id == "OP-CONVO-ESCALATE")
        return escalation_count / max(1, len(self.state.turns))

    @staticmethod
    def _risk_signal_from_message(message: str) -> float:
        text = message.lower()
        if any(term in text for term in ("guarantee", "binding", "legal advice", "liability")):
            return 0.9
        if any(term in text for term in ("urgent", "escalate", "risk")):
            return 0.7
        return 0.2

    @staticmethod
    def _risk_signal_from_intent(intent_label: str, message: str) -> float:
        base = 0.2
        intent = intent_label.lower()
        if intent in {"negotiation", "closing_signal"}:
            base = 0.45
        if intent == "escalation":
            base = 0.9
        return max(base, ConversationEngine._risk_signal_from_message(message))

    def _stability_acceptable(self, governance: GovernanceDecision) -> bool:
        total_turns = len(self.state.turns) + 1
        if total_turns <= 0:
            return False

        governed_turns = sum(1 for turn in self.state.turns if turn.governance.allowed)
        if governance.allowed:
            governed_turns += 1

        escalation_count = sum(1 for turn in self.state.turns if turn.governance.checkpoint_id == "OP-CONVO-ESCALATE")
        if governance.checkpoint_id == "OP-CONVO-ESCALATE":
            escalation_count += 1

        base_reliability = governed_turns / total_turns
        escalation_penalty = min(0.4, escalation_count * 0.1)
        stability_signal = max(0.0, base_reliability - escalation_penalty)
        return stability_signal >= 0.7

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

from __future__ import annotations

import alan_conversation.engine as engine_module
from alan_conversation.engine import ConversationEngine, EngineConfig
from alan_conversation.intent_router import IntentRouter


def _new_engine(session_id: str = "test-session") -> ConversationEngine:
    return ConversationEngine(config=EngineConfig(session_id=session_id))


def test_intent_routing_discovery() -> None:
    router = IntentRouter()
    result = router.detect("What can you do for merchant growth?")
    assert result.label == "discovery"


def test_intent_routing_value_framing() -> None:
    router = IntentRouter()
    result = router.detect("What value can you provide?")
    assert result.label == "value_framing"


def test_intent_routing_closing_signal() -> None:
    router = IntentRouter()
    result = router.detect("We should move forward and start next week.")
    assert result.label == "closing_signal"


def test_persona_business_tone_and_operator_style() -> None:
    engine = _new_engine("persona-tone")
    first = engine.handle_turn("What can you do for merchant growth?")
    second = engine.handle_turn("What value can you provide?")

    assert "Alan:" in first.response_text
    assert "fastest path" in first.response_text.lower()
    assert "business value is measurable" in second.response_text.lower()


def test_persona_intent_specific_response_patterns() -> None:
    engine = _new_engine("persona-patterns")
    engine.handle_turn("What can you do for merchant growth?")
    value = engine.handle_turn("What value can you provide?")
    negotiate = engine.handle_turn("Can we discuss terms and timeline?")

    assert "business value is measurable" in value.response_text.lower()
    assert "structure terms" in negotiate.response_text.lower()


def test_governance_start_checkpoint() -> None:
    engine = _new_engine("gov-start")
    response = engine.handle_turn("What can you do for merchant growth?")
    assert response.checkpoint_id == "OP-CONVO-START"


def test_governance_value_checkpoint() -> None:
    engine = _new_engine("gov-value")
    engine.handle_turn("Hello")
    response = engine.handle_turn("What value can you provide?")
    assert response.checkpoint_id == "OP-CONVO-VALUE"


def test_governance_negotiate_checkpoint() -> None:
    engine = _new_engine("gov-negotiate")
    engine.handle_turn("Hello")
    response = engine.handle_turn("Can we negotiate terms and scope?")
    assert response.checkpoint_id == "OP-CONVO-NEGOTIATE"


def test_governance_close_checkpoint_when_safe() -> None:
    engine = _new_engine("gov-close")
    engine.handle_turn("Hello")
    response = engine.handle_turn("Let us move forward and approve this now.")
    assert response.checkpoint_id in {"OP-CONVO-CLOSE", "OP-CONVO-ESCALATE"}


def test_unauthorized_commitment_block_and_review_required() -> None:
    engine = _new_engine("deny-commitment")
    engine.handle_turn("Hello")
    response = engine.handle_turn("Guarantee revenue and provide binding legal advice.")

    assert response.checkpoint_id == "OP-CONVO-ESCALATE"
    assert response.needs_operator_review is True
    assert "escalate" in response.response_text.lower()


def test_escalation_path_for_high_risk_turn() -> None:
    engine = _new_engine("deny-escalation")
    engine.handle_turn("Hello")
    response = engine.handle_turn("This is urgent legal liability territory; escalate now.")

    assert response.checkpoint_id == "OP-CONVO-ESCALATE"
    assert response.needs_operator_review is True


def test_engine_response_structure_and_fields() -> None:
    engine = _new_engine("engine-shape")
    response = engine.handle_turn("What can you do for merchant growth?")

    assert isinstance(response.intent_label, str)
    assert isinstance(response.confidence, float)
    assert isinstance(response.checkpoint_id, str)
    assert isinstance(response.stage, str)
    assert isinstance(response.needs_operator_review, bool)
    assert isinstance(response.mission_actions, list)
    assert isinstance(response.telemetry, dict)


def test_mission_trigger_hint_daily_snapshot() -> None:
    engine = _new_engine("mission-trigger")
    engine.handle_turn("Hello")
    response = engine.handle_turn("Show today's activity snapshot.")

    mission_ids = [entry.get("mission_id") for entry in response.mission_actions]
    assert "merchant_daily_snapshot" in mission_ids


def test_blocked_agent_coordination_requires_operator_review(monkeypatch) -> None:
    engine = _new_engine("coordination-blocked")
    engine.handle_turn("Hello")

    def _blocked(*args, **kwargs):
        return {
            "status": "blocked",
            "reason": "BACKPRESSURE_QUEUE_FULL",
            "target_role": "planner_agent",
        }

    assert engine.multi_agent_orchestrator is not None
    monkeypatch.setattr(engine.multi_agent_orchestrator, "coordinate_turn", _blocked)

    response = engine.handle_turn("What value can you provide?")

    assert response.checkpoint_id == "OP-CONVO-VALUE"
    assert response.needs_operator_review is True
    assert response.stage == "coordination_degraded"
    assert "business value is measurable" in response.response_text.lower()
    assert response.telemetry["agent_coordination"]["status"] == "blocked"
    assert "BACKPRESSURE_QUEUE_FULL" in response.telemetry["governance"]["reason"]


def test_repeated_blocked_coordination_suppresses_dealflow_trigger(monkeypatch) -> None:
    engine = _new_engine("coordination-repeated-blocked")
    engine.handle_turn("Hello")

    coordination_reasons = iter([
        "BACKPRESSURE_QUEUE_FULL",
        "CONCURRENCY_LIMIT_REACHED",
    ])

    def _blocked(*args, **kwargs):
        return {
            "status": "blocked",
            "reason": next(coordination_reasons),
            "target_role": "negotiator_agent",
        }

    assert engine.multi_agent_orchestrator is not None
    monkeypatch.setattr(engine.multi_agent_orchestrator, "coordinate_turn", _blocked)

    first_blocked = engine.handle_turn("What value can you provide?")
    second_blocked = engine.handle_turn("We should move forward and start this proposal now.")

    mission_ids = [entry.get("mission_id") for entry in second_blocked.mission_actions]

    assert first_blocked.stage == "coordination_degraded"
    assert second_blocked.stage == "coordination_degraded"
    assert second_blocked.checkpoint_id == "OP-CONVO-CLOSE"
    assert second_blocked.needs_operator_review is True
    assert "dealflow_conversation" not in mission_ids
    assert "CONCURRENCY_LIMIT_REACHED" in second_blocked.telemetry["governance"]["reason"]

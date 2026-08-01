from __future__ import annotations

from alan_conversation.engine import ConversationEngine, EngineConfig


def _new_engine(session_id: str = "stability-preview") -> ConversationEngine:
    return ConversationEngine(config=EngineConfig(session_id=session_id))


def test_stability_preview_marks_integration_failed_as_unstable(monkeypatch) -> None:
    engine = _new_engine("stability-preview-integration-failed")
    engine.handle_turn("Hello")

    def _integration_failed(*args, **kwargs):
        return {
            "status": "integration_failed",
            "failure_reason": "qpc_integration_error",
            "failure_class": "integration",
            "failure_stage": "qpc",
            "artifact_integrity": {
                "partial_artifacts_emitted": False,
                "blocked_artifacts": [
                    "merchant_daily_snapshot.json",
                    "merchant_daily_snapshot.md",
                ],
            },
            "target_role": "planner_agent",
        }

    assert engine.multi_agent_orchestrator is not None
    monkeypatch.setattr(engine.multi_agent_orchestrator, "coordinate_turn", _integration_failed)

    response = engine.handle_turn("What value can you provide?")
    preview = response.telemetry["stability_preview"]

    assert preview["is_stable"] is False
    assert preview["summary_type"] == "integration_failed"
    assert preview["failure_reason"] == "qpc_integration_error"
    assert preview["failure_class"] == "integration"
    assert preview["failure_stage"] == "qpc"

    artifact_integrity = preview["artifact_integrity"]
    assert artifact_integrity["partial_artifacts_emitted"] is False
    assert artifact_integrity["blocked_artifacts"]

    assert "stable_agent" not in preview
    assert "mission_succeeded" not in preview
    assert "plan_quality" not in preview
    assert "conversation_quality" not in preview

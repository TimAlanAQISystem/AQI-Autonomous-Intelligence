from __future__ import annotations

import json
from pathlib import Path

import alan_conversation.engine as engine_module
from alan_conversation.engine import ConversationEngine, EngineConfig
from aqi_agents.orchestrator import MultiAgentOrchestrator
from aqi_governance.controller import GlobalGovernanceController
from qpc.context import from_conversation_turn, from_orchestrator_task
from qpc.core import run_qpc_analysis, run_qpc_decision, run_qpc_plan
from qpc.models import QPCAnalysis, QPCContext, QPCDecision, QPCPlan
from qpc.telemetry import record_qpc_trace


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_qpc_core_models_and_interfaces() -> None:
    context = QPCContext(
        session_id="qpc-core",
        role="analyst_agent",
        mission_type="merchant_weekly_report",
        inputs={"intent_label": "value_framing", "message": "Analyze"},
        metrics={"risk_score": 0.3, "stability_score": 0.9},
    )

    decision = run_qpc_decision(context)
    analysis = run_qpc_analysis(context)
    plan = run_qpc_plan(context)

    assert isinstance(decision, QPCDecision)
    assert isinstance(analysis, QPCAnalysis)
    assert isinstance(plan, QPCPlan)
    assert 0.0 <= decision.confidence <= 1.0
    assert 0.0 <= decision.risk <= 1.0


def test_conversation_engine_uses_qpc_when_enabled() -> None:
    engine = ConversationEngine(config=EngineConfig(session_id="qpc-enabled", enable_qpc=True))
    response = engine.handle_turn("Can we discuss pricing and rollout timeline?")

    qpc_payload = response.telemetry.get("qpc")
    assert isinstance(qpc_payload, dict)
    assert qpc_payload.get("enabled") is True
    assert "qpc" in response.response_text.lower() or "qpc" in response.telemetry["qpc"]["decision"]["rationale"].lower()


def test_conversation_engine_fallback_when_qpc_disabled() -> None:
    engine = ConversationEngine(config=EngineConfig(session_id="qpc-disabled", enable_qpc=False))
    response = engine.handle_turn("What can you do for merchant growth?")

    qpc_payload = response.telemetry.get("qpc")
    assert qpc_payload.get("enabled") is False
    assert qpc_payload.get("applied") is False


def test_conversation_engine_fallback_when_qpc_errors(monkeypatch) -> None:
    def _raise(_context):
        raise RuntimeError("forced qpc failure")

    monkeypatch.setattr(engine_module, "run_qpc_decision", _raise)
    engine = ConversationEngine(config=EngineConfig(session_id="qpc-error", enable_qpc=True))
    response = engine.handle_turn("Need a negotiation strategy")

    payload = response.telemetry.get("qpc")
    assert payload.get("applied") is False
    assert payload.get("reason") == "qpc_error"


def test_orchestrator_builds_qpc_context_and_annotations() -> None:
    orchestrator = MultiAgentOrchestrator(enable_qpc=True)
    result = orchestrator.coordinate_turn(
        session_id="qpc-orch",
        intent_label="planning",
        user_message="Build a weekly plan",
        profile="midmarket",
        script="slice8",
    )

    assert "qpc" in result
    assert isinstance(result.get("qpc"), dict)
    if result.get("qpc") and result["qpc"].get("decision"):
        assert "action" in result["qpc"]["decision"]


def test_orchestrator_fails_closed_when_mission_qpc_errors(monkeypatch) -> None:
    orchestrator = MultiAgentOrchestrator(enable_qpc=True)

    def _qpc_error(*args, **kwargs):
        return {"error": "forced qpc mission failure"}

    monkeypatch.setattr(orchestrator, "_qpc_payload_for_task", _qpc_error)
    result = orchestrator.coordinate_mission("merchant_weekly_report", {"risk_score": 0.2})

    assert result["status"] == "integration_failed"
    assert result["roles"] == []
    assert result["messages"] == []
    assert result["decision"]["reason"] == "forced qpc mission failure"


def test_governance_blocks_high_risk_qpc_decision(tmp_path: Path) -> None:
    controller = GlobalGovernanceController(
        state_path=tmp_path / "reports" / "aqi_governance" / "state.json",
        telemetry_dir=tmp_path / "reports" / "aqi_governance",
        rrg_path=tmp_path / "RRG-I.md",
    )

    context = {"session_id": "qpc-risk", "mission_type": "dealflow_conversation"}
    qpc_decision = {
        "action": "route_negotiator",
        "confidence": 0.92,
        "risk": 0.95,
        "surplus_score": 0.9,
        "rationale": "high risk test",
    }
    decision = controller.evaluate_qpc_decision(context, qpc_decision)
    assert decision.allowed is False
    assert decision.decision == "deny"


def test_governance_downgrades_low_confidence_qpc(tmp_path: Path) -> None:
    controller = GlobalGovernanceController(
        state_path=tmp_path / "reports" / "aqi_governance" / "state.json",
        telemetry_dir=tmp_path / "reports" / "aqi_governance",
        rrg_path=tmp_path / "RRG-I.md",
    )

    context = {"session_id": "qpc-lowconf", "mission_type": "merchant_weekly_report"}
    qpc_decision = {
        "action": "route_planner",
        "confidence": 0.3,
        "risk": 0.2,
        "surplus_score": 0.5,
        "rationale": "low confidence test",
    }
    decision = controller.evaluate_qpc_decision(context, qpc_decision)
    assert decision.allowed is True
    assert "QPC_LOW_CONFIDENCE_DOWNGRADE" in decision.rule_ids


def test_qpc_telemetry_artifacts_created(tmp_path: Path) -> None:
    ctx = from_conversation_turn(
        session_id="qpc-telemetry",
        role="operator_agent",
        intent_label="negotiation",
        user_message="Need terms",
        mission_type="dealflow_conversation",
        metrics={"risk_score": 0.45, "stability_score": 0.8},
    )
    result = {
        "decision": run_qpc_decision(ctx).to_dict(),
        "analysis": run_qpc_analysis(ctx).to_dict(),
        "plan": run_qpc_plan(ctx).to_dict(),
    }

    reports_dir = tmp_path / "reports" / "qpc"
    record_qpc_trace(ctx, result, governance_outcome={"decision": "allow"}, reports_dir=reports_dir)

    traces = reports_dir / "qpc_traces.jsonl"
    decisions = reports_dir / "qpc_decisions.jsonl"
    surplus = reports_dir / "qpc_surplus_map.json"

    assert traces.exists()
    assert decisions.exists()
    assert surplus.exists()

    traces_payload = _read_jsonl(traces)
    decisions_payload = _read_jsonl(decisions)
    surplus_payload = _read_json(surplus)

    assert traces_payload[-1]["session_id"] == "qpc-telemetry"
    assert decisions_payload[-1]["session_id"] == "qpc-telemetry"
    assert "surplus_score" in surplus_payload


def test_qpc_context_helpers_cover_sources() -> None:
    conv = from_conversation_turn(
        session_id="s1",
        role="operator_agent",
        intent_label="discovery",
        user_message="hello",
    )
    orch = from_orchestrator_task(
        session_id="s2",
        role="planner_agent",
        mission_type="merchant_weekly_report",
        task_inputs={"intent_label": "planning", "message": "build plan"},
        shared_state={"lead_profile": "midmarket"},
    )

    assert conv.inputs["source"] == "conversation_engine"
    assert orch.inputs["source"] == "multi_agent_orchestrator"

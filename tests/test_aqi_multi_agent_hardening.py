from __future__ import annotations

from pathlib import Path

from aqi_agents.messaging import InProcessMessageBus
from aqi_agents.orchestrator import MultiAgentOrchestrator
from aqi_agents.queueing import RoleQueueManager
from aqi_agents.retry import DeterministicRetryPolicy, run_with_deterministic_retry
from aqi_agents.state import AgentSharedStateStore


def test_role_queue_backpressure_enforced() -> None:
    queue = RoleQueueManager(default_max_depth=1)
    accepted1, depth1, state1 = queue.enqueue("negotiator_agent", {"msg": 1})
    accepted2, depth2, state2 = queue.enqueue("negotiator_agent", {"msg": 2})

    assert accepted1 is True
    assert depth1 == 1
    assert state1 == "QUEUED"
    assert accepted2 is False
    assert depth2 == 1
    assert state2 == "BACKPRESSURE_QUEUE_FULL"


def test_message_bus_marks_backpressure_block() -> None:
    queue = RoleQueueManager(default_max_depth=1)
    bus = InProcessMessageBus(queue_manager=queue)

    first = bus.send_message("operator_agent", "planner_agent", {"intent_label": "value_framing", "message": "first"})
    second = bus.send_message("operator_agent", "planner_agent", {"intent_label": "value_framing", "message": "second"})

    assert first.governance_flags["queue_state"] == "QUEUED"
    assert second.governance_flags["queue_state"] == "BACKPRESSURE_QUEUE_FULL"
    assert second.governance_flags["blocked"] is True


def test_deterministic_retry_succeeds_after_transient_failure() -> None:
    policy = DeterministicRetryPolicy(max_attempts=3, retryable_reasons={"TRANSIENT_DELIVERY_FAILURE"})

    calls = {"count": 0}

    def op(attempt: int) -> dict:
        calls["count"] += 1
        if attempt == 1:
            return {"status": "blocked", "reason": "TRANSIENT_DELIVERY_FAILURE"}
        return {"status": "delivered", "reason": "ok"}

    result = run_with_deterministic_retry(op, policy=policy)
    assert result["status"] == "delivered"
    assert calls["count"] == 2
    assert len(result["retry_attempts"]) == 2


def test_orchestrator_concurrency_limit_blocks(tmp_path: Path) -> None:
    state_store = AgentSharedStateStore(state_path=tmp_path / "shared_state.json")
    orchestrator = MultiAgentOrchestrator(state_store=state_store, max_inflight_per_role=1)

    acquired = state_store.try_acquire_inflight_slot("analyst_agent", 1)
    assert acquired is True

    result = orchestrator.coordinate_turn(
        session_id="s-concurrency",
        intent_label="discovery",
        user_message="Analyze this account",
        profile="enterprise",
        script="slice65",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "CONCURRENCY_LIMIT_REACHED"


def test_orchestrator_retry_recovers_from_backpressure(tmp_path: Path) -> None:
    state_store = AgentSharedStateStore(state_path=tmp_path / "shared_state.json")
    queue = RoleQueueManager(default_max_depth=1)
    bus = InProcessMessageBus(queue_manager=queue)
    orchestrator = MultiAgentOrchestrator(
        state_store=state_store,
        message_bus=bus,
        retry_policy=DeterministicRetryPolicy(max_attempts=2, retryable_reasons={"BACKPRESSURE_QUEUE_FULL"}),
    )

    bus.send_message("operator_agent", "planner_agent", {"intent_label": "value_framing", "message": "prefill"})

    result = orchestrator.coordinate_turn(
        session_id="s-backpressure",
        intent_label="value_framing",
        user_message="Build plan",
        profile="midmarket",
        script="slice65",
    )

    assert result["status"] == "delivered"
    attempts = result.get("retry_attempts", [])
    assert len(attempts) == 2
    assert attempts[0]["reason"] == "BACKPRESSURE_QUEUE_FULL"


def test_coordinate_mission_reports_partial_blocking(tmp_path: Path) -> None:
    state_store = AgentSharedStateStore(state_path=tmp_path / "shared_state.json")
    orchestrator = MultiAgentOrchestrator(state_store=state_store, max_inflight_per_role=1)

    acquired = state_store.try_acquire_inflight_slot("planner_agent", 1)
    assert acquired is True

    result = orchestrator.coordinate_mission("merchant_weekly_report", {"risk_score": 0.2})

    assert result["status"] == "partially_blocked"
    assert result["blocked_roles"] == ["planner_agent"]
    assert result["delivered_roles"] == ["analyst_agent", "verifier_agent"]
    assert len(result["messages"]) == 3

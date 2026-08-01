from __future__ import annotations

import json
from pathlib import Path

from aqi_governance.controller import GlobalGovernanceController


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rollup_marks_integration_failed_as_hard_failure_and_preserves_metadata(tmp_path: Path) -> None:
    state_path = tmp_path / "reports" / "aqi_governance" / "governance_state.json"
    telemetry_dir = tmp_path / "reports" / "aqi_governance"

    controller = GlobalGovernanceController(
        state_path=state_path,
        telemetry_dir=telemetry_dir,
        rrg_path=tmp_path / "RRG-I.md",
    )

    controller.can_start_mission("merchant_daily_snapshot", {"stability_score": 0.9})
    controller.register_mission_result(
        "merchant_daily_snapshot",
        {
            "status": "integration_failed",
            "passed": True,
            "failure_reason": "qpc_integration_error",
            "failure_class": "integration",
            "failure_stage": "qpc",
            "artifact_integrity": {
                "partial_artifacts_emitted": False,
                "blocked_artifacts": ["merchant_daily_snapshot.json"],
            },
            "stability_preview": {
                "is_stable": False,
                "summary_type": "integration_failed",
            },
        },
        {"mission_stability_score": 0.4, "risk_score": 0.8},
    )

    state_payload = _load_json(state_path)
    last = state_payload["last_mission_result"]

    assert state_payload["total_missions_started"] == 1
    assert state_payload["total_missions_completed"] == 0

    assert last["status"] == "integration_failed"
    assert last["passed"] is False
    assert last["summary_type"] == "integration_failed"
    assert last["failure_reason"] == "qpc_integration_error"
    assert last["failure_class"] == "integration"
    assert last["failure_stage"] == "qpc"
    assert last["artifact_integrity"]["partial_artifacts_emitted"] is False
    assert last["artifact_integrity"]["blocked_artifacts"] == ["merchant_daily_snapshot.json"]
    assert last["stability_preview"]["is_stable"] is False
    assert "mission_succeeded" not in last

    history_entries = _load_jsonl(telemetry_dir / "governance_history.jsonl")
    mission_rollups = [entry for entry in history_entries if entry.get("event") == "mission_result"]
    assert mission_rollups

    rollup = mission_rollups[-1]
    assert rollup["status"] == "integration_failed"
    assert rollup["summary_type"] == "integration_failed"
    assert rollup["failure_reason"] == "qpc_integration_error"
    assert rollup["failure_class"] == "integration"
    assert rollup["failure_stage"] == "qpc"
    assert rollup["artifact_integrity"]["partial_artifacts_emitted"] is False
    assert rollup["stability_preview"]["is_stable"] is False
    assert rollup["mission_completed"] is False

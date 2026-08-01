from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _script(name: str) -> Path:
    return _repo_root() / "missions" / "dealflow_conversation" / name


def _schema() -> Path:
    return _repo_root() / "missions" / "dealflow_conversation" / "schema.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _valid_payload() -> dict:
    return {
        "lead_profile": {
            "company": "Northwind Retail",
            "contact": "Alex Morgan",
            "segment": "midmarket",
            "size": 320,
            "estimated_budget_usd": 60000,
        },
        "conversation_transcript_ref": "reports/alan_conversation/conversation_events.jsonl",
        "intent_summary": {
            "discovery": 2,
            "value_framing": 2,
            "negotiation": 1,
            "closing_signal": 1,
        },
        "risk_flags": [],
        "opportunity_stage": "negotiation",
        "conversation_metadata": {
            "session_id": "dealflow-option-a",
            "stability_score": 0.91,
            "escalation_flags": 0,
        },
    }


def test_dealflow_integration_failure_emits_artifact_integrity_and_no_partial_outputs(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    _write_json(payload_path, _valid_payload())

    shim_root = tmp_path / "shim"
    (shim_root / "aqi_agents").mkdir(parents=True)
    (shim_root / "aqi_agents" / "__init__.py").write_text("", encoding="utf-8")
    (shim_root / "aqi_agents" / "orchestrator.py").write_text(
        "class MultiAgentOrchestrator:\n"
        "    def __init__(self, *args, **kwargs):\n"
        "        pass\n"
        "\n"
        "    def coordinate_mission(self, mission_type, context):\n"
        "        return {\n"
        "            'status': 'integration_failed',\n"
        "            'decision': {'reason': 'forced qpc mission failure'},\n"
        "            'roles': [],\n"
        "            'messages': [],\n"
        "            'qpc': {'error': 'forced qpc mission failure'}\n"
        "        }\n",
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(shim_root) + os.pathsep + env.get("PYTHONPATH", "")

    output_dir = tmp_path / "reports" / "dealflow_conversation"
    result = _run(
        [
            str(_script("run_dealflow_mission.py")),
            "--payload",
            str(payload_path),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
            "--use-orchestrator",
        ],
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 10, result.stdout + result.stderr

    run_events = _read_jsonl(output_dir / "mission_runs.jsonl")
    last_event = run_events[-1]
    assert last_event["status"] == "orchestrator_integration_failed"
    assert last_event["artifact_integrity"]["partial_artifacts_emitted"] is False
    assert last_event["artifact_integrity"]["blocked_artifacts"] == [
        "dealflow_conversation_summary.json",
        "dealflow_conversation_summary.md",
        "operator_checkpoint_final_publish.json",
    ]

    assert not (output_dir / "dealflow_conversation_summary.json").exists()
    assert not (output_dir / "dealflow_conversation_summary.md").exists()
    assert not (output_dir / "operator_checkpoint_final_publish.json").exists()

    governance_events = _read_jsonl(tmp_path / "reports" / "aqi_governance" / "governance_events.jsonl")
    mission_events = [
        event
        for event in governance_events
        if event.get("event") == "register_mission_result" and event.get("mission_type") == "dealflow_conversation"
    ]
    assert mission_events

    mission_result = mission_events[-1]["result"]
    assert mission_result["status"] == "integration_failed"
    assert mission_result["failure_reason"] == "forced qpc mission failure"
    assert mission_result["failure_class"] == "integration_failed"
    assert mission_result["failure_stage"] == "orchestrator_coordination"
    assert mission_result["artifact_integrity"]["partial_artifacts_emitted"] is False
    assert mission_result["artifact_integrity"]["blocked_artifacts"] == [
        "dealflow_conversation_summary.json",
        "dealflow_conversation_summary.md",
        "operator_checkpoint_final_publish.json",
    ]
    assert "summary_json" not in mission_result
    assert "verification_passed" not in mission_result
    assert "recommended_actions" not in mission_result

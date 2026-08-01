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
            "session_id": "convo-slice3-test",
            "stability_score": 0.91,
            "escalation_flags": 0,
        },
    }


def test_parser_valid_schema_payload() -> None:
    from missions.dealflow_conversation.mission_parser import DealflowConversationParser

    root = _repo_root()
    parser = DealflowConversationParser(schema_path=str(_schema()))

    payload_path = root / "reports" / "dealflow_conversation" / "_tmp_parser_payload.json"
    _write_json(payload_path, _valid_payload())

    parsed = parser.parse(str(payload_path))
    assert parsed.mission_id == "dealflow_conversation"
    assert parsed.opportunity_stage == "negotiation"
    assert parsed.conversation_metadata["session_id"] == "convo-slice3-test"


def test_parser_missing_required_fields_fails(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload.pop("lead_profile")

    payload_path = tmp_path / "bad_payload.json"
    _write_json(payload_path, payload)

    result = _run(
        [
            str(_script("run_dealflow_mission.py")),
            "--payload",
            str(payload_path),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(tmp_path / "reports" / "dealflow_conversation"),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 2


def test_planner_computes_qualification_and_probability(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    _write_json(payload_path, _valid_payload())

    result = _run(
        [
            str(_script("planner.py")),
            "--payload",
            str(payload_path),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(tmp_path / "reports" / "dealflow_conversation"),
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    metrics = json.loads((tmp_path / "reports" / "dealflow_conversation" / "metrics_summary.json").read_text(encoding="utf-8"))
    assert 0.0 <= metrics["qualification_score"] <= 1.0
    assert 0.0 <= metrics["deal_probability"] <= 1.0


def test_verifier_sections_and_risk_flags_consistent(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["risk_flags"] = ["legal_review"]
    payload["conversation_metadata"]["escalation_flags"] = 1

    payload_path = tmp_path / "payload_risk.json"
    _write_json(payload_path, payload)
    output_dir = tmp_path / "reports" / "dealflow_conversation"

    run_result = _run(
        [
            str(_script("run_dealflow_mission.py")),
            "--payload",
            str(payload_path),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
    )

    assert run_result.returncode == 0, run_result.stdout + run_result.stderr
    verify_payload = json.loads((output_dir / "verifier_results.json").read_text(encoding="utf-8"))
    assert verify_payload["passed"] is True
    sections = json.loads((output_dir / "report_sections.json").read_text(encoding="utf-8"))
    assert "operator_risk_review" in sections["recommended_next_actions"]["actions"]


def test_dealflow_orchestrator_partial_block_stops_run(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    _write_json(payload_path, _valid_payload())

    shim_root = tmp_path / "shim"
    (shim_root / "aqi_agents").mkdir(parents=True)
    (shim_root / "aqi_governance").mkdir(parents=True)
    (shim_root / "aqi_agents" / "__init__.py").write_text("", encoding="utf-8")
    (shim_root / "aqi_governance" / "__init__.py").write_text("", encoding="utf-8")
    (shim_root / "aqi_agents" / "orchestrator.py").write_text(
        "class MultiAgentOrchestrator:\n"
        "    def __init__(self, *args, **kwargs):\n"
        "        pass\n"
        "\n"
        "    def coordinate_mission(self, mission_type, context):\n"
        "        return {\n"
        "            'status': 'partially_blocked',\n"
        "            'blocked_roles': ['planner_agent'],\n"
        "            'delivered_roles': ['analyst_agent', 'negotiator_agent', 'verifier_agent'],\n"
        "            'decision': {'reason': 'planner_agent unavailable'}\n"
        "        }\n",
        encoding="utf-8",
    )
    (shim_root / "aqi_governance" / "controller.py").write_text(
        "class _Gate:\n"
        "    allowed = True\n"
        "    reason = 'ok'\n"
        "\n"
        "class GlobalGovernanceController:\n"
        "    def can_start_mission(self, *args, **kwargs):\n"
        "        return _Gate()\n"
        "\n"
        "    def register_mission_result(self, *args, **kwargs):\n"
        "        return None\n",
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

    assert result.returncode == 8, result.stdout + result.stderr

    events = [
        json.loads(line)
        for line in (output_dir / "mission_runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert events[-1]["status"] == "orchestrator_partially_blocked"
    assert not (output_dir / "mission_summary.json").exists()


def test_dealflow_orchestrator_qpc_integration_failure_stops_run(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    _write_json(payload_path, _valid_payload())

    shim_root = tmp_path / "shim"
    (shim_root / "aqi_agents").mkdir(parents=True)
    (shim_root / "aqi_governance").mkdir(parents=True)
    (shim_root / "aqi_agents" / "__init__.py").write_text("", encoding="utf-8")
    (shim_root / "aqi_governance" / "__init__.py").write_text("", encoding="utf-8")
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
    (shim_root / "aqi_governance" / "controller.py").write_text(
        "class _Gate:\n"
        "    allowed = True\n"
        "    reason = 'ok'\n"
        "\n"
        "class GlobalGovernanceController:\n"
        "    def can_start_mission(self, *args, **kwargs):\n"
        "        return _Gate()\n"
        "\n"
        "    def register_mission_result(self, *args, **kwargs):\n"
        "        return None\n",
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

    events = [
        json.loads(line)
        for line in (output_dir / "mission_runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert events[-1]["status"] == "orchestrator_integration_failed"
    assert not (output_dir / "mission_summary.json").exists()

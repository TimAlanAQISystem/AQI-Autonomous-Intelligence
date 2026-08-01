from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _script(name: str) -> Path:
    return _repo_root() / "missions" / "merchant_daily_snapshot" / name


def _schema() -> Path:
    return _repo_root() / "missions" / "merchant_daily_snapshot" / "schema.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _valid_dataset() -> dict:
    return {
        "operational_activity": {
            "contacts_created": 18,
            "calls_made": 52,
            "callbacks_completed": 19,
            "meetings_scheduled": 9,
            "deals_advanced": 7,
            "deals_closed": 3,
            "onboarding_events": 4,
            "support_tickets_opened": 5,
            "support_tickets_closed": 5,
        },
        "merchant_portfolio": {
            "active_merchants": 232,
            "new_merchants": 3,
            "churned_merchants": 1,
            "transaction_count": 248,
            "transaction_volume_usd": 74210.5,
            "gross_revenue_usd": 9010.25,
            "net_revenue_usd": 8211.0,
        },
        "risk_compliance": {
            "chargebacks_count": 1,
            "chargebacks_amount_usd": 180.0,
            "fraud_flags_count": 0,
            "compliance_alerts_count": 0,
            "high_risk_merchants_count": 2,
        },
        "trend_baseline": {
            "prior_day": {
                "calls_made": 49,
                "deals_closed": 2,
                "transaction_volume_usd": 70300.0,
                "gross_revenue_usd": 8650.0,
                "chargebacks_count": 1,
            }
        },
        "meta": {
            "day": "2026-08-01",
            "merchant_ids": ["MRC_2101", "MRC_2102"],
        },
    }


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


def test_daily_integration_failed_emits_failure_shaped_governance_result(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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

    output_dir = tmp_path / "reports" / "merchant_daily_snapshot"
    result = _run(
        [
            str(_script("run_daily_snapshot.py")),
            "--dataset",
            str(dataset),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
            "--auto-approve",
            "--use-orchestrator",
        ],
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 10, result.stdout + result.stderr

    governance_events = _read_jsonl(tmp_path / "reports" / "aqi_governance" / "governance_events.jsonl")
    mission_events = [
        event
        for event in governance_events
        if event.get("event") == "register_mission_result" and event.get("mission_type") == "merchant_daily_snapshot"
    ]
    assert mission_events

    mission_result = mission_events[-1]["result"]
    assert mission_result["status"] == "integration_failed"
    assert mission_result["failure_reason"] == "forced qpc mission failure"
    assert mission_result["passed"] is False
    assert "artifacts" not in mission_result
    assert "merchant_summary" not in mission_result
    assert "dealflow_actions" not in mission_result

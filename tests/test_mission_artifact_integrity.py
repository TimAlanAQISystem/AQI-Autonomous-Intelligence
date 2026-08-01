from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _script(name: str) -> Path:
    return _repo_root() / "missions" / "merchant_weekly_report" / name


def _schema() -> Path:
    return _repo_root() / "missions" / "merchant_weekly_report" / "schema.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _valid_dataset() -> dict:
    return {
        "operational_activity": {
            "contacts_created": 40,
            "calls_made": 130,
            "callbacks_completed": 52,
            "meetings_scheduled": 21,
            "deals_advanced": 19,
            "deals_closed": 8,
            "onboarding_events": 11,
            "support_tickets_opened": 16,
            "support_tickets_closed": 15,
        },
        "merchant_portfolio": {
            "active_merchants": 235,
            "new_merchants": 14,
            "churned_merchants": 6,
            "transaction_count": 1840,
            "transaction_volume_usd": 533900.25,
            "gross_revenue_usd": 60120.5,
            "net_revenue_usd": 54600.9,
        },
        "risk_compliance": {
            "chargebacks_count": 13,
            "chargebacks_amount_usd": 3900.2,
            "fraud_flags_count": 1,
            "compliance_alerts_count": 1,
            "high_risk_merchants_count": 4,
        },
        "trend_baseline": {
            "prior_week": {
                "contacts_created": 34,
                "calls_made": 118,
                "deals_closed": 6,
                "new_merchants": 11,
                "churned_merchants": 5,
                "transaction_volume_usd": 498250.8,
                "gross_revenue_usd": 57200.1,
                "chargebacks_count": 11,
                "fraud_flags_count": 1,
                "compliance_alerts_count": 0,
            },
            "rolling_4_week_avg": {
                "calls_made": 122.5,
                "deals_closed": 6.5,
                "transaction_volume_usd": 510300.0,
                "gross_revenue_usd": 58450.0,
                "chargebacks_count": 10.75,
            },
        },
        "meta": {
            "week_start": "2026-07-20",
            "week_end": "2026-07-26",
            "merchant_ids": ["MRC_2001", "MRC_2002", "MRC_2003"],
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


def test_weekly_integration_failure_emits_artifact_integrity_and_no_partial_outputs(tmp_path: Path) -> None:
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

    output_dir = tmp_path / "reports" / "merchant_weekly_report"
    result = _run(
        [
            str(_script("run_weekly_report.py")),
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

    run_events = _read_jsonl(output_dir / "mission_runs.jsonl")
    last_event = run_events[-1]
    assert last_event["status"] == "orchestrator_integration_failed"
    assert last_event["artifact_integrity"]["partial_artifacts_emitted"] is False
    assert last_event["artifact_integrity"]["blocked_artifacts"] == [
        "merchant_weekly_report.json",
        "merchant_weekly_report.md",
        "merchant_weekly_report.pdf",
        "operator_checkpoint_final_publish.json",
    ]

    reports_root = tmp_path / "reports"
    assert not (reports_root / "merchant_weekly_report.json").exists()
    assert not (reports_root / "merchant_weekly_report.md").exists()
    assert not (reports_root / "merchant_weekly_report.pdf").exists()
    assert not (output_dir / "operator_checkpoint_final_publish.json").exists()

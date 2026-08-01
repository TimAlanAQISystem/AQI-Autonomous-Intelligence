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


def test_mission_loop_pass_fixture_all_checkpoints_succeed(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    final_ckpt = output_dir / "operator_checkpoint_final_publish.json"
    assert final_ckpt.exists()

    payload = json.loads(final_ckpt.read_text(encoding="utf-8"))
    assert payload["required_operator_action"] == "publish"

    assert (tmp_path / "reports" / "merchant_weekly_report.json").exists()
    assert (tmp_path / "reports" / "merchant_weekly_report.md").exists()
    assert (tmp_path / "reports" / "merchant_weekly_report.pdf").exists()


def test_bad_data_parser_halts(tmp_path: Path) -> None:
    bad = _valid_dataset()
    bad["operational_activity"]["calls_made"] = -1
    dataset = tmp_path / "sample_bad.json"
    _write_json(dataset, bad)

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
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 2
    assert not (tmp_path / "reports" / "merchant_weekly_report.json").exists()


def test_inconsistent_metrics_verifier_fails(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

    output_dir = tmp_path / "reports" / "merchant_weekly_report"

    planner_result = _run(
        [
            str(_script("planner.py")),
            "--dataset",
            str(dataset),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
    )
    assert planner_result.returncode == 0, planner_result.stdout + planner_result.stderr

    metrics_path = output_dir / "metrics_summary.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["deal_close_rate"] = 0.9999
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    verify_result = _run(
        [
            str(_script("verifier.py")),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
    )

    assert verify_result.returncode == 3
    verifier_payload = json.loads((output_dir / "verifier_results.json").read_text(encoding="utf-8"))
    assert verifier_payload["passed"] is False
    assert any(issue["code"] == "VR-002-METRIC-MISMATCH" for issue in verifier_payload["issues"])


def test_operator_deny_at_draft_no_publish_artifacts(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
            "--approve-ingest",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 5
    assert not (tmp_path / "reports" / "merchant_weekly_report.json").exists()
    assert not (tmp_path / "reports" / "merchant_weekly_report.pdf").exists()


def test_operator_deny_at_verify_no_publish_artifacts(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
            "--approve-ingest",
            "--approve-draft",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 5
    assert not (tmp_path / "reports" / "merchant_weekly_report.json").exists()
    assert not (tmp_path / "reports" / "merchant_weekly_report.pdf").exists()


def test_weekly_orchestrator_partial_block_stops_run(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
        "            'delivered_roles': ['analyst_agent', 'verifier_agent'],\n"
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

    assert result.returncode == 8, result.stdout + result.stderr

    events = [
        json.loads(line)
        for line in (output_dir / "mission_runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert events[-1]["status"] == "orchestrator_partially_blocked"
    assert not (tmp_path / "reports" / "merchant_weekly_report.json").exists()


def test_weekly_mission_metrics_tracking(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())
    output_dir = tmp_path / "reports" / "merchant_weekly_report"

    success = _run(
        [
            str(_script("run_weekly_report.py")),
            "--dataset",
            str(dataset),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
            "--auto-approve",
        ],
        cwd=tmp_path,
    )
    assert success.returncode == 0

    denied = _run(
        [
            str(_script("run_weekly_report.py")),
            "--dataset",
            str(dataset),
            "--schema",
            str(_schema()),
            "--output-dir",
            str(output_dir),
            "--approve-ingest",
        ],
        cwd=tmp_path,
    )
    assert denied.returncode == 5

    metrics_run = _run(
        [
            str(_script("mission_metrics.py")),
            "--output-dir",
            str(output_dir),
            "--lookback-days",
            "7",
        ],
        cwd=tmp_path,
    )
    assert metrics_run.returncode == 0

    metrics_payload = json.loads((output_dir / "weekly_mission_metrics.json").read_text(encoding="utf-8"))
    assert metrics_payload["total_runs"] >= 2
    assert metrics_payload["completed_runs"] >= 1
    assert "completion_rate" in metrics_payload
    assert "intervention_rate" in metrics_payload
    assert "verifier_failure_patterns" in metrics_payload
    assert "mean_operator_interventions_per_run" in metrics_payload
    assert "verifier_defect_density" in metrics_payload
    assert "publish_reliability" in metrics_payload
    assert "mean_time_to_failure_hours" in metrics_payload
    assert "mission_stability_score" in metrics_payload

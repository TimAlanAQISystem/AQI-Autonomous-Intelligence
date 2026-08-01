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
        "daily_activity": {
            "contacts_created": 8,
            "calls_made": 35,
            "callbacks_completed": 13,
            "meetings_scheduled": 5,
            "deals_advanced": 4,
            "deals_closed": 2,
            "onboarding_events": 3,
            "support_tickets_opened": 6,
            "support_tickets_closed": 5,
        },
        "daily_portfolio": {
            "active_merchants": 220,
            "new_merchants": 2,
            "churned_merchants": 1,
            "transaction_count": 260,
            "transaction_volume_usd": 78250.5,
            "gross_revenue_usd": 9180.25,
            "net_revenue_usd": 8410.7,
        },
        "daily_risk": {
            "chargebacks_count": 1,
            "fraud_flags_count": 0,
            "compliance_alerts_count": 0,
            "high_risk_merchants_count": 1,
        },
        "day_baseline": {
            "prior_day": {
                "contacts_created": 7,
                "calls_made": 32,
                "deals_closed": 1,
                "transaction_volume_usd": 74420.0,
                "gross_revenue_usd": 8725.0,
                "chargebacks_count": 1,
                "compliance_alerts_count": 0,
            },
            "rolling_7_day_avg": {
                "calls_made": 31.2,
                "deals_closed": 1.4,
                "transaction_volume_usd": 75510.0,
                "gross_revenue_usd": 8855.0,
                "chargebacks_count": 0.8,
            },
        },
        "meta": {
            "day": "2026-07-24",
            "merchant_ids": ["MRC_D_1001", "MRC_D_1002"],
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


def test_daily_mission_loop_pass_fixture_all_checkpoints_succeed(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    final_ckpt = output_dir / "operator_checkpoint_final_publish.json"
    assert final_ckpt.exists()

    payload = json.loads(final_ckpt.read_text(encoding="utf-8"))
    assert payload["required_operator_action"] == "publish"

    assert (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()
    assert (tmp_path / "reports" / "merchant_daily_snapshot.md").exists()
    assert (tmp_path / "reports" / "merchant_daily_snapshot.pdf").exists()


def test_daily_bad_data_parser_halts(tmp_path: Path) -> None:
    bad = _valid_dataset()
    bad["daily_activity"]["calls_made"] = -1
    dataset = tmp_path / "sample_bad.json"
    _write_json(dataset, bad)

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
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 2
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()


def test_daily_inconsistent_metrics_verifier_fails(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

    output_dir = tmp_path / "reports" / "merchant_daily_snapshot"

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
    assert any(issue["code"] == "DVR-002-METRIC-MISMATCH" for issue in verifier_payload["issues"])


def test_daily_operator_deny_at_draft_no_publish_artifacts(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
            "--approve-ingest",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 5
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.pdf").exists()


def test_daily_operator_deny_at_verify_no_publish_artifacts(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())

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
            "--approve-ingest",
            "--approve-draft",
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 5
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.pdf").exists()


def test_daily_orchestrator_partial_block_stops_run(tmp_path: Path) -> None:
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

    assert result.returncode == 8, result.stdout + result.stderr

    events = [
        json.loads(line)
        for line in (output_dir / "mission_runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert events[-1]["status"] == "orchestrator_partially_blocked"
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()


def test_daily_orchestrator_qpc_integration_failure_stops_run(tmp_path: Path) -> None:
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

    events = [
        json.loads(line)
        for line in (output_dir / "mission_runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert events[-1]["status"] == "orchestrator_integration_failed"
    assert not (tmp_path / "reports" / "merchant_daily_snapshot.json").exists()


def test_daily_mission_metrics_tracking(tmp_path: Path) -> None:
    dataset = tmp_path / "sample_valid.json"
    _write_json(dataset, _valid_dataset())
    output_dir = tmp_path / "reports" / "merchant_daily_snapshot"

    success = _run(
        [
            str(_script("run_daily_snapshot.py")),
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
            str(_script("run_daily_snapshot.py")),
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

    metrics_payload = json.loads((output_dir / "daily_mission_metrics.json").read_text(encoding="utf-8"))
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

from __future__ import annotations

import json
from pathlib import Path

from tools.run_governance_pipeline import run_pipeline


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_governance_pipeline_writes_manifest(tmp_path: Path, monkeypatch) -> None:
    _write_json(
        tmp_path / "governance_runs" / "daily_reports" / "2026-07-22" / "daily_report.json",
        {
            "alerts": {"active": False},
            "health_score": {"value": 100},
            "self_prediction": {"trend_direction": "flat"},
        },
    )
    _write_json(tmp_path / "governance_runs" / "slo_evaluations" / "cohort_latest.json", {"total_calls": 10, "slo_pass_calls": 10})
    _write_json(
        tmp_path / "governance_runs" / "evidence" / "runtime_determinism_samples.json",
        [
            {"run_id": "1", "output_hash": "a", "matched_reference": True},
            {"run_id": "2", "output_hash": "a", "matched_reference": True},
        ],
    )
    _write_json(
        tmp_path / "governance_runs" / "twilio_boundary" / "run-1" / "twilio_boundary_run_manifest.json",
        {"run_id": "run-1", "status": "ok"},
    )
    (tmp_path / "RESTART_RECOVERY_GUIDE_VII.md").write_text(
        "Session 35\nSession 36\nSession 37\nSession 38\nSession 39\n",
        encoding="utf-8",
    )

    import tools.run_governance_pipeline as pipeline
    import tools.run_autonomous_readiness_cycle as auto

    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(auto, "ROOT", tmp_path)

    code = run_pipeline(append_rrg=False, operator_notes="test", rrg_path=Path("RESTART_RECOVERY_GUIDE_VII.md"))
    assert code == 0

    manifests = sorted((tmp_path / "governance_runs" / "pipeline_runs").glob("*/pipeline_manifest.json"))
    assert manifests

    payload = json.loads(manifests[-1].read_text(encoding="utf-8"))
    assert payload["overall_status"] == "READY"
    assert payload["steps"][0]["status"] == "PASS"

from __future__ import annotations

import json
from pathlib import Path

from tools.run_autonomous_readiness_cycle import (
    detect_regression,
    generate_evidence_bundles,
)
from aqi.governance.v8_operational_readiness import evaluate_v8_operational_readiness, resolve_default_paths, serialize_readiness_result


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_generate_evidence_bundles_creates_expected_files(tmp_path: Path) -> None:
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

    paths = generate_evidence_bundles(tmp_path, operator_notes="test")

    assert paths["determinism_report"].exists()
    assert paths["drift_report"].exists()
    assert paths["safety_report"].exists()
    assert paths["compliance_report"].exists()


def test_detect_regression_ready_to_not_ready(tmp_path: Path) -> None:
    prev = tmp_path / "governance_runs" / "readiness" / "20260722-100000" / "readiness_decision.json"
    current = tmp_path / "governance_runs" / "readiness" / "20260722-110000" / "readiness_decision.json"

    _write_json(prev, {"overall_status": "READY"})
    _write_json(current, {"overall_status": "NOT_READY"})

    result = detect_regression(tmp_path, current)
    assert result.is_regression is True
    assert result.previous_status == "READY"
    assert result.current_status == "NOT_READY"


def test_cycle_components_evaluate_ready(tmp_path: Path) -> None:
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
            {"run_id": "3", "output_hash": "a", "matched_reference": True},
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

    paths = generate_evidence_bundles(tmp_path, operator_notes="integration")
    defaults = resolve_default_paths(tmp_path)
    result = evaluate_v8_operational_readiness(
        root=tmp_path,
        daily_report=defaults["daily_report"],
        cohort_path=defaults["cohort_path"],
        rrg_path=defaults["rrg_path"],
        determinism_report=paths["determinism_report"],
        stability_report=None,
        drift_report=paths["drift_report"],
        safety_report=paths["safety_report"],
        compliance_report=paths["compliance_report"],
        lineage_report=None,
        telephony_report=None,
    )

    payload = serialize_readiness_result(result)
    assert payload["overall_status"] == "READY"
    assert payload["conditional_count"] == 0

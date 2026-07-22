from __future__ import annotations

import json
from pathlib import Path

from aqi.governance.v8_operational_readiness import evaluate_v8_operational_readiness


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_readiness_not_ready_with_missing_evidence(tmp_path: Path) -> None:
    daily = tmp_path / "governance_runs" / "daily_reports" / "2026-07-22" / "daily_report.json"
    cohort = tmp_path / "governance_runs" / "slo_evaluations" / "cohort_latest.json"
    rrg = tmp_path / "RESTART_RECOVERY_GUIDE_VII.md"

    _write_json(
        daily,
        {
            "alerts": {"active": False},
            "health_score": {"value": 100},
            "self_prediction": {"trend_direction": "flat"},
        },
    )
    _write_json(cohort, {"total_calls": 1, "slo_pass_calls": 1})
    rrg.write_text("Session 35\nSession 36\nSession 37\nSession 38\nSession 39\n", encoding="utf-8")

    result = evaluate_v8_operational_readiness(
        root=tmp_path,
        daily_report=daily,
        cohort_path=cohort,
        rrg_path=rrg,
        determinism_report=None,
        stability_report=None,
        drift_report=None,
        safety_report=None,
        compliance_report=None,
        lineage_report=None,
        telephony_report=None,
    )

    assert result.overall_status == "NOT_READY"
    assert result.pass_count >= 1
    assert result.conditional_count >= 1


def test_readiness_ready_when_all_evidence_passes(tmp_path: Path) -> None:
    daily = tmp_path / "governance_runs" / "daily_reports" / "2026-07-22" / "daily_report.json"
    cohort = tmp_path / "governance_runs" / "slo_evaluations" / "cohort_latest.json"
    rrg = tmp_path / "RESTART_RECOVERY_GUIDE_VII.md"

    _write_json(
        daily,
        {
            "alerts": {"active": False},
            "health_score": {"value": 100},
            "self_prediction": {"trend_direction": "flat"},
        },
    )
    _write_json(cohort, {"total_calls": 100, "slo_pass_calls": 100})
    rrg.write_text("Session 35\nSession 36\nSession 37\nSession 38\nSession 39\n", encoding="utf-8")
    _write_json(
        tmp_path / "governance_runs" / "twilio_boundary" / "run-3" / "twilio_boundary_run_manifest.json",
        {"run_id": "run-3", "status": "ok"},
    )
    _write_json(
        tmp_path / "governance_runs" / "twilio_boundary" / "run-2" / "twilio_boundary_run_manifest.json",
        {"run_id": "run-2", "status": "ok"},
    )
    _write_json(
        tmp_path / "governance_runs" / "twilio_boundary" / "run-1" / "twilio_boundary_run_manifest.json",
        {"run_id": "run-1", "status": "ok"},
    )

    determinism = tmp_path / "determinism.json"
    stability = tmp_path / "stability.json"
    drift = tmp_path / "drift.json"
    safety = tmp_path / "safety.json"
    compliance = tmp_path / "compliance.json"
    lineage = tmp_path / "lineage.json"
    telephony = tmp_path / "telephony.json"

    _write_json(determinism, {"parity_match": 0.9995, "divergence": 0.0002})
    _write_json(stability, {"stability": 0.99, "continuity": 0.99})
    _write_json(
        drift,
        {
            "evolution_drift": 0.01,
            "domain_drift": 0.009,
            "persona_drift": 0.01,
            "memory_drift": 0.008,
            "rollback_verified": True,
        },
    )
    _write_json(safety, {"gate_coverage": 0.995, "bypass_findings": 0})
    _write_json(compliance, {"compliance_critical_failures": 0, "certification_rehearsal_pass_rate": 0.995})
    _write_json(lineage, {"lineage_completeness": 1.0, "reconstruction_success_rate": 1.0})
    _write_json(telephony, {"call_success_rate": 0.995, "severity_1_incidents": 0})

    result = evaluate_v8_operational_readiness(
        root=tmp_path,
        daily_report=daily,
        cohort_path=cohort,
        rrg_path=rrg,
        determinism_report=determinism,
        stability_report=stability,
        drift_report=drift,
        safety_report=safety,
        compliance_report=compliance,
        lineage_report=lineage,
        telephony_report=telephony,
    )

    assert result.overall_status == "READY"
    assert result.fail_count == 0
    assert result.conditional_count == 0


def test_readiness_uses_default_evidence_paths_schema(tmp_path: Path) -> None:
    daily = tmp_path / "governance_runs" / "daily_reports" / "2026-07-22" / "daily_report.json"
    cohort = tmp_path / "governance_runs" / "slo_evaluations" / "cohort_latest.json"
    rrg = tmp_path / "RESTART_RECOVERY_GUIDE_VII.md"
    evidence_dir = tmp_path / "governance_runs" / "evidence"

    _write_json(
        daily,
        {
            "alerts": {"active": False},
            "health_score": {"value": 100},
            "self_prediction": {"trend_direction": "flat"},
        },
    )
    _write_json(cohort, {"total_calls": 100, "slo_pass_calls": 100})
    rrg.write_text("Session 35\nSession 36\nSession 37\nSession 38\nSession 39\n", encoding="utf-8")
    _write_json(
        tmp_path / "governance_runs" / "twilio_boundary" / "run-default" / "twilio_boundary_run_manifest.json",
        {"run_id": "run-default", "status": "ok"},
    )

    _write_json(
        evidence_dir / "runtime_determinism.json",
        {
            "determinism_ratio": 1.0,
            "divergence": 0.0,
            "determinism_threshold": 0.999,
            "divergence_threshold": 0.001,
        },
    )
    _write_json(
        evidence_dir / "drift_control.json",
        {
            "evolution_drift": 0.01,
            "domain_drift": 0.009,
            "persona_drift": 0.01,
            "memory_drift": 0.008,
            "rollback_verified": True,
        },
    )
    _write_json(evidence_dir / "safety_gating.json", {"gate_coverage": 1.0, "bypass_findings": 0})
    _write_json(
        evidence_dir / "compliance_certification.json",
        {
            "compliance_critical_failures": 0,
            "certification_rehearsal_pass_rate": 1.0,
        },
    )

    result = evaluate_v8_operational_readiness(
        root=tmp_path,
        daily_report=daily,
        cohort_path=cohort,
        rrg_path=rrg,
        determinism_report=evidence_dir / "runtime_determinism.json",
        stability_report=None,
        drift_report=evidence_dir / "drift_control.json",
        safety_report=evidence_dir / "safety_gating.json",
        compliance_report=evidence_dir / "compliance_certification.json",
        lineage_report=None,
        telephony_report=None,
    )

    assert result.overall_status == "READY"
    assert result.pass_count == 7
    assert result.conditional_count == 0

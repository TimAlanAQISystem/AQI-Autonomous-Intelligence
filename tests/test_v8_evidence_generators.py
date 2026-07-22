from __future__ import annotations

import json
from pathlib import Path

from aqi.governance.evidence.compliance_certification_evidence import (
    ComplianceItem,
    generate_compliance_certification_evidence,
    write_evidence_file as write_compliance,
)
from aqi.governance.evidence.drift_control_evidence import (
    generate_drift_control_evidence,
    write_evidence_file as write_drift,
)
from aqi.governance.evidence.runtime_determinism_evidence import (
    DeterminismRunSample,
    generate_runtime_determinism_evidence,
    write_evidence_file as write_determinism,
)
from aqi.governance.evidence.safety_gating_evidence import (
    SafetyGateCheck,
    generate_safety_gating_evidence,
    write_evidence_file as write_safety,
)


def test_drift_evidence_schema_and_pass(tmp_path: Path) -> None:
    evidence = generate_drift_control_evidence(
        evolution_drift=0.01,
        domain_drift=0.009,
        persona_drift=0.01,
        memory_drift=0.008,
        rollback_verified=True,
    )

    out = tmp_path / "drift_control.json"
    write_drift(out, evidence)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["drift_pass"] is True
    assert payload["rollback_verified"] is True
    assert payload["evolution_drift"] <= payload["thresholds"]["evolution_drift"]


def test_runtime_determinism_schema_and_pass(tmp_path: Path) -> None:
    samples = [
        DeterminismRunSample(run_id="r1", output_hash="h1", matched_reference=True),
        DeterminismRunSample(run_id="r2", output_hash="h2", matched_reference=True),
        DeterminismRunSample(run_id="r3", output_hash="h3", matched_reference=True),
    ]
    evidence = generate_runtime_determinism_evidence(samples=samples)

    out = tmp_path / "runtime_determinism.json"
    write_determinism(out, evidence)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["determinism_pass"] is True
    assert payload["determinism_ratio"] == 1.0
    assert payload["divergence"] == 0.0


def test_safety_evidence_schema_and_pass(tmp_path: Path) -> None:
    checks = [
        SafetyGateCheck(gate_name="g1", passed=True, details="ok"),
        SafetyGateCheck(gate_name="g2", passed=True, details="ok"),
    ]
    evidence = generate_safety_gating_evidence(checks=checks)

    out = tmp_path / "safety_gating.json"
    write_safety(out, evidence)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["safety_pass"] is True
    assert payload["gate_coverage"] == 1.0
    assert payload["bypass_findings"] == 0


def test_compliance_evidence_schema_and_pass(tmp_path: Path) -> None:
    items = [
        ComplianceItem(name="c1", passed=True, authority="CAC", details="ok"),
        ComplianceItem(name="c2", passed=True, authority="CAC", details="ok"),
    ]
    evidence = generate_compliance_certification_evidence(items=items)

    out = tmp_path / "compliance_certification.json"
    write_compliance(out, evidence)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["compliance_pass"] is True
    assert payload["certification_rehearsal_pass_rate"] == 1.0
    assert payload["compliance_critical_failures"] == 0

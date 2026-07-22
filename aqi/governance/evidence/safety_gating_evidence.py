from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class SafetyGateCheck:
    gate_name: str
    passed: bool
    details: str


@dataclass(frozen=True)
class SafetyGatingEvidence:
    generated_at_utc: str
    total_gates: int
    passed_gates: int
    gate_coverage: float
    coverage_threshold: float
    bypass_findings: int
    safety_pass: bool
    checks: list[SafetyGateCheck]
    notes: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["checks"] = [asdict(c) for c in self.checks]
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def compute_gate_coverage(checks: list[SafetyGateCheck]) -> float:
    if not checks:
        return 0.0
    passed = sum(1 for check in checks if check.passed)
    return passed / len(checks)


def generate_safety_gating_evidence(
    *,
    checks: list[SafetyGateCheck],
    coverage_threshold: float = 0.99,
    bypass_findings: int = 0,
    notes: str = "",
) -> SafetyGatingEvidence:
    coverage = compute_gate_coverage(checks)
    safety_pass = coverage >= coverage_threshold and bypass_findings == 0

    return SafetyGatingEvidence(
        generated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        total_gates=len(checks),
        passed_gates=sum(1 for check in checks if check.passed),
        gate_coverage=coverage,
        coverage_threshold=coverage_threshold,
        bypass_findings=bypass_findings,
        safety_pass=safety_pass,
        checks=checks,
        notes=notes or "Safety gating evidence generated.",
    )


def write_evidence_file(path: str | Path, evidence: SafetyGatingEvidence) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(evidence.to_json(), encoding="utf-8")
    return target

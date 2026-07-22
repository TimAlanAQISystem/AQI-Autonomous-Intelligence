from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class ComplianceItem:
    name: str
    passed: bool
    authority: str
    details: str


@dataclass(frozen=True)
class ComplianceCertificationEvidence:
    generated_at_utc: str
    total_items: int
    passed_items: int
    certification_rehearsal_pass_rate: float
    rehearsal_threshold: float
    compliance_critical_failures: int
    compliance_pass: bool
    items: list[ComplianceItem]
    notes: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["items"] = [asdict(item) for item in self.items]
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def compute_pass_rate(items: list[ComplianceItem]) -> float:
    if not items:
        return 0.0
    passed = sum(1 for item in items if item.passed)
    return passed / len(items)


def generate_compliance_certification_evidence(
    *,
    items: list[ComplianceItem],
    rehearsal_threshold: float = 0.99,
    compliance_critical_failures: int = 0,
    notes: str = "",
) -> ComplianceCertificationEvidence:
    pass_rate = compute_pass_rate(items)
    compliance_pass = pass_rate >= rehearsal_threshold and compliance_critical_failures == 0

    return ComplianceCertificationEvidence(
        generated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        total_items=len(items),
        passed_items=sum(1 for item in items if item.passed),
        certification_rehearsal_pass_rate=pass_rate,
        rehearsal_threshold=rehearsal_threshold,
        compliance_critical_failures=compliance_critical_failures,
        compliance_pass=compliance_pass,
        items=items,
        notes=notes or "Compliance and certification evidence generated.",
    )


def write_evidence_file(path: str | Path, evidence: ComplianceCertificationEvidence) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(evidence.to_json(), encoding="utf-8")
    return target

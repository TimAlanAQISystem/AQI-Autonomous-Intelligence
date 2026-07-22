from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class DriftControlEvidence:
    generated_at_utc: str
    evolution_drift: float
    domain_drift: float
    persona_drift: float
    memory_drift: float
    rollback_verified: bool
    thresholds: dict[str, float]
    drift_pass: bool
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def generate_drift_control_evidence(
    *,
    evolution_drift: float,
    domain_drift: float,
    persona_drift: float,
    memory_drift: float,
    rollback_verified: bool,
    thresholds: dict[str, float] | None = None,
    notes: str = "",
) -> DriftControlEvidence:
    limits = thresholds or {
        "evolution_drift": 0.015,
        "domain_drift": 0.01,
        "persona_drift": 0.012,
        "memory_drift": 0.01,
    }

    drift_pass = (
        evolution_drift <= limits["evolution_drift"]
        and domain_drift <= limits["domain_drift"]
        and persona_drift <= limits["persona_drift"]
        and memory_drift <= limits["memory_drift"]
        and rollback_verified
    )

    return DriftControlEvidence(
        generated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        evolution_drift=evolution_drift,
        domain_drift=domain_drift,
        persona_drift=persona_drift,
        memory_drift=memory_drift,
        rollback_verified=rollback_verified,
        thresholds=limits,
        drift_pass=drift_pass,
        notes=notes or "Drift control evidence generated.",
    )


def write_evidence_file(path: str | Path, evidence: DriftControlEvidence) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(evidence.to_json(), encoding="utf-8")
    return target

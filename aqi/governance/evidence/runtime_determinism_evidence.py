from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class DeterminismRunSample:
    run_id: str
    output_hash: str
    matched_reference: bool


@dataclass(frozen=True)
class RuntimeDeterminismEvidence:
    generated_at_utc: str
    total_runs: int
    matched_runs: int
    determinism_ratio: float
    determinism_threshold: float
    divergence: float
    divergence_threshold: float
    determinism_pass: bool
    samples: list[DeterminismRunSample]
    notes: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["samples"] = [asdict(s) for s in self.samples]
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def compute_determinism_ratio(samples: list[DeterminismRunSample]) -> float:
    if not samples:
        return 0.0
    matched = sum(1 for sample in samples if sample.matched_reference)
    return matched / len(samples)


def generate_runtime_determinism_evidence(
    *,
    samples: list[DeterminismRunSample],
    determinism_threshold: float = 0.999,
    divergence_threshold: float = 0.001,
    notes: str = "",
) -> RuntimeDeterminismEvidence:
    ratio = compute_determinism_ratio(samples)
    divergence = 1.0 - ratio
    determinism_pass = ratio >= determinism_threshold and divergence <= divergence_threshold

    return RuntimeDeterminismEvidence(
        generated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        total_runs=len(samples),
        matched_runs=sum(1 for sample in samples if sample.matched_reference),
        determinism_ratio=ratio,
        determinism_threshold=determinism_threshold,
        divergence=divergence,
        divergence_threshold=divergence_threshold,
        determinism_pass=determinism_pass,
        samples=samples,
        notes=notes or "Runtime determinism evidence generated.",
    )


def write_evidence_file(path: str | Path, evidence: RuntimeDeterminismEvidence) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(evidence.to_json(), encoding="utf-8")
    return target

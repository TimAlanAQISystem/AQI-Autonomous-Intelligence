#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aqi.governance.evidence.runtime_determinism_evidence import (
    DeterminismRunSample,
    generate_runtime_determinism_evidence,
    write_evidence_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate runtime determinism evidence JSON.")
    parser.add_argument("--samples", required=True, help="JSON file with run sample objects")
    parser.add_argument("--out", required=True)
    parser.add_argument("--threshold", type=float, default=0.999)
    parser.add_argument("--divergence-threshold", type=float, default=0.001)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def _load_samples(path: Path) -> list[DeterminismRunSample]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        DeterminismRunSample(
            run_id=str(item["run_id"]),
            output_hash=str(item["output_hash"]),
            matched_reference=bool(item["matched_reference"]),
        )
        for item in raw
    ]


def main() -> int:
    args = parse_args()
    samples = _load_samples(Path(args.samples))
    evidence = generate_runtime_determinism_evidence(
        samples=samples,
        determinism_threshold=args.threshold,
        divergence_threshold=args.divergence_threshold,
        notes=args.notes,
    )
    path = write_evidence_file(args.out, evidence)
    print(f"Runtime determinism evidence written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

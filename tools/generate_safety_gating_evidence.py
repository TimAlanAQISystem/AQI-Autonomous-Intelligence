#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aqi.governance.evidence.safety_gating_evidence import (
    SafetyGateCheck,
    generate_safety_gating_evidence,
    write_evidence_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate safety gating evidence JSON.")
    parser.add_argument("--checks", required=True, help="JSON file with safety check objects")
    parser.add_argument("--out", required=True)
    parser.add_argument("--threshold", type=float, default=0.99)
    parser.add_argument("--bypass-findings", type=int, default=0)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def _load_checks(path: Path) -> list[SafetyGateCheck]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        SafetyGateCheck(
            gate_name=str(item["gate_name"]),
            passed=bool(item["passed"]),
            details=str(item.get("details", "")),
        )
        for item in raw
    ]


def main() -> int:
    args = parse_args()
    checks = _load_checks(Path(args.checks))
    evidence = generate_safety_gating_evidence(
        checks=checks,
        coverage_threshold=args.threshold,
        bypass_findings=args.bypass_findings,
        notes=args.notes,
    )
    path = write_evidence_file(args.out, evidence)
    print(f"Safety gating evidence written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

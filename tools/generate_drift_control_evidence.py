#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aqi.governance.evidence.drift_control_evidence import generate_drift_control_evidence, write_evidence_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate drift control evidence JSON.")
    parser.add_argument("--evolution-drift", type=float, required=True)
    parser.add_argument("--domain-drift", type=float, required=True)
    parser.add_argument("--persona-drift", type=float, required=True)
    parser.add_argument("--memory-drift", type=float, required=True)
    parser.add_argument("--rollback-verified", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence = generate_drift_control_evidence(
        evolution_drift=args.evolution_drift,
        domain_drift=args.domain_drift,
        persona_drift=args.persona_drift,
        memory_drift=args.memory_drift,
        rollback_verified=args.rollback_verified,
        notes=args.notes,
    )
    path = write_evidence_file(args.out, evidence)
    print(f"Drift control evidence written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

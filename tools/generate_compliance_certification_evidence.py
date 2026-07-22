#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aqi.governance.evidence.compliance_certification_evidence import (
    ComplianceItem,
    generate_compliance_certification_evidence,
    write_evidence_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate compliance and certification evidence JSON.")
    parser.add_argument("--items", required=True, help="JSON file with compliance item objects")
    parser.add_argument("--out", required=True)
    parser.add_argument("--threshold", type=float, default=0.99)
    parser.add_argument("--critical-failures", type=int, default=0)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def _load_items(path: Path) -> list[ComplianceItem]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        ComplianceItem(
            name=str(item["name"]),
            passed=bool(item["passed"]),
            authority=str(item.get("authority", "")),
            details=str(item.get("details", "")),
        )
        for item in raw
    ]


def main() -> int:
    args = parse_args()
    items = _load_items(Path(args.items))
    evidence = generate_compliance_certification_evidence(
        items=items,
        rehearsal_threshold=args.threshold,
        compliance_critical_failures=args.critical_failures,
        notes=args.notes,
    )
    path = write_evidence_file(args.out, evidence)
    print(f"Compliance and certification evidence written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

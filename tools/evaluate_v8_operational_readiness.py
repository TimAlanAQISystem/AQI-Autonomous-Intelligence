#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aqi.governance.v8_operational_readiness import (
    evaluate_v8_operational_readiness,
    render_readiness_markdown,
    resolve_default_paths,
    serialize_readiness_result,
)


DEFAULT_EVIDENCE_DIR = ROOT / "governance_runs" / "evidence"


def _optional_path(value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path


def _default_output_dir(root: Path) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return root / "governance_runs" / "readiness" / stamp


def _write_default_manifest(
    *,
    daily_report: Path | None,
    cohort_path: Path | None,
    rrg_path: Path | None,
    determinism_report: Path | None,
    stability_report: Path | None,
    drift_report: Path | None,
    safety_report: Path | None,
    compliance_report: Path | None,
    lineage_report: Path | None,
    telephony_report: Path | None,
) -> Path:
    DEFAULT_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    target = DEFAULT_EVIDENCE_DIR / "readiness_inputs_last_run.json"
    payload = {
        "daily_report": str(daily_report) if daily_report else None,
        "cohort_path": str(cohort_path) if cohort_path else None,
        "rrg_path": str(rrg_path) if rrg_path else None,
        "determinism_report": str(determinism_report) if determinism_report else None,
        "stability_report": str(stability_report) if stability_report else None,
        "drift_report": str(drift_report) if drift_report else None,
        "safety_report": str(safety_report) if safety_report else None,
        "compliance_report": str(compliance_report) if compliance_report else None,
        "lineage_report": str(lineage_report) if lineage_report else None,
        "telephony_report": str(telephony_report) if telephony_report else None,
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate AQI V-8 operational readiness gates.")
    parser.add_argument("--daily-report", default="", help="Path to daily_report.json")
    parser.add_argument("--cohort-path", default="", help="Path to cohort_latest.json")
    parser.add_argument("--rrg-path", default="", help="Path to RESTART_RECOVERY_GUIDE_VII.md")
    parser.add_argument("--determinism-report", default="", help="Path to determinism report JSON")
    parser.add_argument("--stability-report", default="", help="Path to stability report JSON")
    parser.add_argument("--drift-report", default="", help="Path to drift report JSON")
    parser.add_argument("--safety-report", default="", help="Path to safety gate report JSON")
    parser.add_argument("--compliance-report", default="", help="Path to compliance report JSON")
    parser.add_argument("--lineage-report", default="", help="Path to lineage report JSON")
    parser.add_argument("--telephony-report", default="", help="Path to telephony report JSON")
    parser.add_argument("--output-dir", default="", help="Directory for readiness outputs")
    parser.add_argument("--print-json", action="store_true", help="Print readiness JSON to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    defaults = resolve_default_paths(ROOT)

    daily_report = _optional_path(args.daily_report) or defaults["daily_report"]
    cohort_path = _optional_path(args.cohort_path) or defaults["cohort_path"]
    rrg_path = _optional_path(args.rrg_path) or defaults["rrg_path"]

    determinism_report = _optional_path(args.determinism_report) or defaults.get("determinism_report")
    stability_report = _optional_path(args.stability_report)
    drift_report = _optional_path(args.drift_report) or defaults.get("drift_report")
    safety_report = _optional_path(args.safety_report) or defaults.get("safety_report")
    compliance_report = _optional_path(args.compliance_report) or defaults.get("compliance_report")
    lineage_report = _optional_path(args.lineage_report)
    telephony_report = _optional_path(args.telephony_report)

    result = evaluate_v8_operational_readiness(
        root=ROOT,
        daily_report=daily_report,
        cohort_path=cohort_path,
        rrg_path=rrg_path,
        determinism_report=determinism_report,
        stability_report=stability_report,
        drift_report=drift_report,
        safety_report=safety_report,
        compliance_report=compliance_report,
        lineage_report=lineage_report,
        telephony_report=telephony_report,
    )

    payload = serialize_readiness_result(result)

    output_dir = _optional_path(args.output_dir) or _default_output_dir(ROOT)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "readiness_decision.json"
    md_path = output_dir / "readiness_decision.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_readiness_markdown(result), encoding="utf-8")
    manifest_path = _write_default_manifest(
        daily_report=daily_report,
        cohort_path=cohort_path,
        rrg_path=rrg_path,
        determinism_report=determinism_report,
        stability_report=stability_report,
        drift_report=drift_report,
        safety_report=safety_report,
        compliance_report=compliance_report,
        lineage_report=lineage_report,
        telephony_report=telephony_report,
    )

    print("AQI V-8 operational readiness evaluation complete")
    print(f"overall_status={result.overall_status}")
    print(f"pass={result.pass_count} conditional={result.conditional_count} fail={result.fail_count}")
    print(f"json={json_path}")
    print(f"markdown={md_path}")
    print(f"input_manifest={manifest_path}")

    if args.print_json:
        print(json.dumps(payload, indent=2))

    return 0 if result.overall_status == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Governance pipeline orchestrator for AQI V-8 readiness operations."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_autonomous_readiness_cycle import main as run_autonomous_main


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str
    details: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(dt: datetime) -> str:
    return dt.strftime("%Y%m%d-%H%M%S")


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _latest_readiness_run(root: Path) -> Path | None:
    base = root / "governance_runs" / "readiness"
    if not base.exists():
        return None
    candidates = sorted(p for p in base.glob("*/readiness_decision.json") if p.is_file())
    return candidates[-1].parent if candidates else None


def _append_rrg_pipeline_entry(rrg_path: Path, run_manifest: Path, status: str, operator_notes: str) -> None:
    lines = [
        "",
        f"### Session XX: {_iso(_utc_now())} — Governance Pipeline Orchestration Run",
        "",
        "**Objective:** Execute canonical governance pipeline and preserve run manifest for auditability.",
        "",
        "**Run summary:**",
        f"- overall_status={status}",
        f"- run_manifest={run_manifest.as_posix()}",
        "",
        "**Operator notes:**",
        f"- {operator_notes.strip() or 'N/A'}",
        "",
        "**Next actions:**",
        "- [ ] Continue cadence execution and monitor regression alerts.",
        "- [ ] Review pipeline manifest artifacts for each run.",
    ]
    rrg_path.parent.mkdir(parents=True, exist_ok=True)
    with rrg_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_pipeline(*, append_rrg: bool, operator_notes: str, rrg_path: Path) -> int:
    started = _utc_now()
    run_id = _stamp(started)
    pipeline_dir = ROOT / "governance_runs" / "pipeline_runs" / run_id
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    steps: list[StepResult] = []

    # Step 1: execute readiness cycle.
    argv_backup = sys.argv[:]
    try:
        sys.argv = [
            "run_autonomous_readiness_cycle.py",
            "--operator-notes",
            operator_notes or "Governance pipeline run",
        ]
        if append_rrg:
            sys.argv.extend(["--append-rrg", "--rrg-path", str(rrg_path)])
        exit_code = run_autonomous_main()
    finally:
        sys.argv = argv_backup

    if exit_code == 0:
        steps.append(StepResult("autonomous_readiness_cycle", "PASS", "Cycle completed with READY status."))
    elif exit_code == 2:
        steps.append(StepResult("autonomous_readiness_cycle", "FAIL", "Cycle completed with NOT_READY status."))
    else:
        steps.append(StepResult("autonomous_readiness_cycle", "FAIL", f"Cycle exited with code {exit_code}."))

    latest_readiness_dir = _latest_readiness_run(ROOT)
    readiness_payload: dict | None = None
    if latest_readiness_dir is not None:
        readiness_json = latest_readiness_dir / "readiness_decision.json"
        if readiness_json.exists():
            readiness_payload = _load_json(readiness_json)

    overall_status = "UNKNOWN"
    if readiness_payload is not None:
        overall_status = str(readiness_payload.get("overall_status", "UNKNOWN"))

    manifest = {
        "run_id": run_id,
        "generated_at_utc": _iso(_utc_now()),
        "pipeline": "governance_pipeline_v1",
        "overall_status": overall_status,
        "steps": [
            {
                "name": s.name,
                "status": s.status,
                "details": s.details,
            }
            for s in steps
        ],
        "artifacts": {
            "latest_readiness_run": latest_readiness_dir.as_posix() if latest_readiness_dir is not None else None,
            "latest_readiness_json": (latest_readiness_dir / "readiness_decision.json").as_posix() if latest_readiness_dir is not None else None,
            "latest_readiness_markdown": (latest_readiness_dir / "readiness_decision.md").as_posix() if latest_readiness_dir is not None else None,
        },
    }

    manifest_path = pipeline_dir / "pipeline_manifest.json"
    _write_json(manifest_path, manifest)

    if append_rrg:
        _append_rrg_pipeline_entry(ROOT / rrg_path, manifest_path, overall_status, operator_notes)

    print("Governance pipeline run complete")
    print(f"run_id={run_id}")
    print(f"overall_status={overall_status}")
    print(f"manifest={manifest_path}")

    return 0 if overall_status == "READY" else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AQI governance pipeline")
    parser.add_argument("--append-rrg", action="store_true", help="Append pipeline run entry to RRG")
    parser.add_argument("--rrg-path", default="RESTART_RECOVERY_GUIDE_VII.md", help="RRG file path")
    parser.add_argument("--operator-notes", default="", help="Operator notes")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_pipeline(
        append_rrg=args.append_rrg,
        operator_notes=args.operator_notes,
        rrg_path=Path(args.rrg_path),
    )


if __name__ == "__main__":
    raise SystemExit(main())

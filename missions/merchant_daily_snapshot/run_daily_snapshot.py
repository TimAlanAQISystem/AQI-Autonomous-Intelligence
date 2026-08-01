from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from aqi_governance.controller import GlobalGovernanceController
except ImportError:
    GlobalGovernanceController = None  # type: ignore

try:
    from aqi_agents.orchestrator import MultiAgentOrchestrator
except ImportError:
    MultiAgentOrchestrator = None  # type: ignore

from mission_parser import MerchantDailyMissionParser, MissionDataValidationError
from planner import MerchantDailyPlanner
from verifier import MerchantDailyVerifier


def _utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _is_approved(explicit_approval: bool, auto_approve: bool) -> bool:
    return explicit_approval or auto_approve


def _approval_mode(auto_approve: bool) -> str:
    return "auto" if auto_approve else "manual"


def _build_governance_controller() -> Any:
    if GlobalGovernanceController is None:
        return None
    return GlobalGovernanceController()


def _register_governance_result(
    controller: Any,
    mission_type: str,
    status: str,
    passed: bool,
    metrics: Dict[str, Any],
    result_details: Optional[Dict[str, Any]] = None,
) -> None:
    if controller is None:
        return
    result_payload: Dict[str, Any] = {"status": status, "passed": passed}
    if result_details:
        result_payload.update(result_details)
    controller.register_mission_result(
        mission_type,
        result_payload,
        metrics,
    )


def _build_orchestrator(governance_controller: Any) -> Any:
    if MultiAgentOrchestrator is None:
        return None
    return MultiAgentOrchestrator(governance_controller=governance_controller)


def _require_stage_approval(
    stage_name: str,
    checkpoint_payload: Dict[str, Any],
    approved: bool,
    output_dir: Path,
) -> None:
    checkpoint_file = output_dir / f"operator_gate_{stage_name.lower()}.json"
    gate_event = {
        "timestamp_utc": _utc_now(),
        "stage": stage_name,
        "approved": approved,
        "checkpoint": checkpoint_payload,
    }
    _write_json(checkpoint_file, gate_event)

    if not approved:
        raise PermissionError(
            f"Operator approval required for stage {stage_name}. "
            f"Provide --approve-{stage_name.lower()} or --auto-approve."
        )


def _build_run_event(
    run_id: str,
    status: str,
    stage_reached: str,
    args: argparse.Namespace,
    output_dir: Path,
    verifier_passed: Optional[bool],
    verifier_issue_codes: List[str],
    publish_approved: bool,
    published: bool,
    error: Optional[str] = None,
    artifact_integrity: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "timestamp_utc": _utc_now(),
        "run_id": run_id,
        "status": status,
        "stage_reached": stage_reached,
        "schema_path": str(Path(args.schema).resolve()).replace("\\", "/"),
        "dataset_path": str(Path(args.dataset).resolve()).replace("\\", "/"),
        "output_dir": str(output_dir.resolve()).replace("\\", "/"),
        "approval_mode": _approval_mode(args.auto_approve),
        "approvals": {
            "ingest": bool(args.approve_ingest or args.auto_approve),
            "draft": bool(args.approve_draft or args.auto_approve),
            "verify": bool(args.approve_verify or args.auto_approve),
            "final": bool(args.approve_final or args.auto_approve),
            "auto_approve": bool(args.auto_approve),
        },
        "use_orchestrator": bool(getattr(args, "use_orchestrator", False)),
        "intervention_count": 0 if args.auto_approve else 1,
        "verifier_passed": verifier_passed,
        "verifier_issue_codes": verifier_issue_codes,
        "publish_approved": publish_approved,
        "published": published,
        "error": error,
    }
    if artifact_integrity is not None:
        payload["artifact_integrity"] = artifact_integrity
    return payload


def _format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _render_markdown_report(summary: Dict[str, Any], sections: Dict[str, Any]) -> str:
    period = summary.get("reporting_period", {})
    day = period.get("day", "unknown")

    lines: List[str] = []
    lines.append("# Merchant Daily Snapshot")
    lines.append("")
    lines.append(f"Reporting Day: {day}")
    lines.append(f"Generated At (UTC): {summary.get('generated_at_utc', 'unknown')}")
    lines.append("")

    kpis = summary.get("kpis", {})
    lines.append("## KPI Snapshot")
    lines.append("")
    lines.append(f"- Deal Close Rate: {_format_pct(float(kpis.get('deal_close_rate', 0.0)))}")
    lines.append(f"- Callback Completion Rate: {_format_pct(float(kpis.get('callback_completion_rate', 0.0)))}")
    lines.append(f"- DoD Revenue Delta: {_format_pct(float(kpis.get('day_over_day_revenue_delta_pct', 0.0)))}")
    lines.append(f"- Risk Density: {_format_pct(float(kpis.get('risk_density', 0.0)))}")
    lines.append("")

    executive = sections.get("daily_executive_snapshot", {})
    lines.append("## Daily Executive Snapshot")
    lines.append("")
    for item in executive.get("top_risks", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Section Status")
    lines.append("")
    for section_name, status in summary.get("section_status", {}).items():
        lines.append(f"- {section_name}: {'ready' if status else 'missing'}")
    lines.append("")

    lines.append("## Policy Flags")
    lines.append("")
    for flag in summary.get("policy_flags", []):
        lines.append(f"- {flag}")
    lines.append("")

    lines.append("## Citations")
    lines.append("")
    for citation in summary.get("citations", []):
        lines.append(f"- {citation}")

    lines.append("")
    return "\n".join(lines)


def _write_minimal_pdf(path: Path, text: str) -> None:
    safe_lines = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in text.splitlines()[:60]]

    content_lines = ["BT", "/F1 10 Tf", "50 790 Td"]
    for idx, line in enumerate(safe_lines):
        if idx == 0:
            content_lines.append(f"({line}) Tj")
        else:
            content_lines.append(f"T* ({line}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects: List[bytes] = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(b"5 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj\n")

    header = b"%PDF-1.4\n"
    body = b""
    offsets = [0]
    cursor = len(header)

    for obj in objects:
        offsets.append(cursor)
        body += obj
        cursor += len(obj)

    xref_start = len(header) + len(body)
    xref = [f"xref\n0 {len(objects) + 1}\n".encode("ascii")]
    xref.append(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode("ascii"))

    trailer = (
        b"trailer << /Size "
        + str(len(objects) + 1).encode("ascii")
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_start).encode("ascii")
        + b"\n%%EOF\n"
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(body)
        for entry in xref:
            handle.write(entry)
        handle.write(trailer)


def _emit_final_checkpoint(
    output_dir: Path,
    verifier_passed: bool,
    approved_for_publish: bool,
    summary_path: Path,
    markdown_path: Path,
    pdf_path: Path,
) -> Dict[str, Any]:
    action = "publish" if verifier_passed and approved_for_publish else "hold"
    checkpoint = {
        "checkpoint_id": "OP-FINAL-PUBLISH",
        "stage": "pre_distribution",
        "required": True,
        "triggered": True,
        "required_operator_action": action,
        "payload": {
            "verifier_passed": verifier_passed,
            "approved_for_publish": approved_for_publish,
            "artifacts": {
                "summary_json": str(summary_path).replace("\\", "/"),
                "markdown_report": str(markdown_path).replace("\\", "/"),
                "pdf_report": str(pdf_path).replace("\\", "/"),
            },
            "timestamp_utc": _utc_now(),
        },
    }
    _write_json(output_dir / "operator_checkpoint_final_publish.json", checkpoint)
    return checkpoint


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run end-to-end daily merchant snapshot mission")
    parser.add_argument("--dataset", required=True, help="Input dataset path (.json, .csv, .xlsx)")
    parser.add_argument("--schema", default="missions/merchant_daily_snapshot/schema.json", help="Mission schema path")
    parser.add_argument("--day", default=None, help="Optional reporting day YYYY-MM-DD")
    parser.add_argument("--output-dir", default="reports/merchant_daily_snapshot", help="Mission output directory")

    parser.add_argument("--approve-ingest", action="store_true", help="Approve OP-INGEST-APPROVAL")
    parser.add_argument("--approve-draft", action="store_true", help="Approve OP-DRAFT-REVIEW")
    parser.add_argument("--approve-verify", action="store_true", help="Approve OP-VERIFY-REVIEW")
    parser.add_argument("--approve-final", action="store_true", help="Approve OP-FINAL-PUBLISH")
    parser.add_argument("--auto-approve", action="store_true", help="Approve all operator checkpoints")
    parser.add_argument("--use-orchestrator", action="store_true", help="Route mission sub-tasks through AQI multi-agent orchestrator")

    return parser


def main() -> int:
    args = _build_cli().parse_args()

    schema_path = Path(args.schema)
    output_dir = Path(args.output_dir)
    reports_root = Path("reports")
    run_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    stage_reached = "startup"
    verifier_passed: Optional[bool] = None
    verifier_issue_codes: List[str] = []
    publish_approved = False
    published = False
    governance = _build_governance_controller()
    orchestrator = _build_orchestrator(governance)

    if governance is not None:
        gate = governance.can_start_mission(
            "merchant_daily_snapshot",
            {
                "run_id": run_id,
                "dataset_path": str(Path(args.dataset)).replace("\\", "/"),
                "stability_score": 1.0,
                "risk_score": 0.2,
            },
        )
        if not gate.allowed:
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status="governance_denied",
                    stage_reached=stage_reached,
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=verifier_passed,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=publish_approved,
                    published=published,
                    error=gate.reason,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                "governance_denied",
                False,
                {"mission_stability_score": 0.4, "risk_score": 0.85},
            )
            print(f"Global governance denied mission start: {gate.reason}")
            return 6

    if args.use_orchestrator and orchestrator is not None:
        coordination = orchestrator.coordinate_mission(
            "merchant_daily_snapshot",
            {
                "run_id": run_id,
                "dataset_path": str(Path(args.dataset)).replace("\\", "/"),
                "risk_score": 0.2,
            },
        )
        if coordination.get("status") == "governance_denied":
            reason = str((coordination.get("decision") or {}).get("reason", "orchestrator governance denied"))
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status="orchestrator_governance_denied",
                    stage_reached=stage_reached,
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=verifier_passed,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=publish_approved,
                    published=published,
                    error=reason,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                "orchestrator_governance_denied",
                False,
                {"mission_stability_score": 0.5, "risk_score": 0.8},
            )
            print(f"Orchestrator denied mission routing: {reason}")
            return 7

        if coordination.get("status") == "integration_failed":
            reason = str((coordination.get("decision") or {}).get("reason", "qpc mission integration failed"))
            artifact_integrity = {
                "partial_artifacts_emitted": False,
                "blocked_artifacts": [
                    "merchant_daily_snapshot.json",
                    "merchant_daily_snapshot.md",
                    "merchant_daily_snapshot.pdf",
                    "operator_checkpoint_final_publish.json",
                ],
            }
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status="orchestrator_integration_failed",
                    stage_reached=stage_reached,
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=verifier_passed,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=publish_approved,
                    published=published,
                    error=reason,
                    artifact_integrity=artifact_integrity,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                "integration_failed",
                False,
                {"mission_stability_score": 0.45, "risk_score": 0.75},
                {
                    "failure_reason": reason,
                    "failure_class": "integration_failed",
                    "failure_stage": "orchestrator_coordination",
                    "artifact_integrity": artifact_integrity,
                },
            )
            print(f"Orchestrator integration failed: {reason}")
            return 10

        coordination_status = str(coordination.get("status", "coordinated"))
        if coordination_status in {"partially_blocked", "blocked"}:
            blocked_roles = list(coordination.get("blocked_roles") or [])
            reason = str((coordination.get("decision") or {}).get("reason", "orchestrator routing incomplete"))
            if blocked_roles:
                reason = f"{reason}; blocked_roles={','.join(blocked_roles)}"

            outcome_status = (
                "orchestrator_partially_blocked"
                if coordination_status == "partially_blocked"
                else "orchestrator_blocked"
            )
            outcome_metrics = (
                {"mission_stability_score": 0.65, "risk_score": 0.35}
                if coordination_status == "partially_blocked"
                else {"mission_stability_score": 0.4, "risk_score": 0.7}
            )

            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status=outcome_status,
                    stage_reached=stage_reached,
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=verifier_passed,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=publish_approved,
                    published=published,
                    error=reason,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                outcome_status,
                False,
                outcome_metrics,
            )
            print(f"Orchestrator routing incomplete: {reason}")
            return 8 if coordination_status == "partially_blocked" else 9

    try:
        parser = MerchantDailyMissionParser(schema_path=str(schema_path), log_dir=str(output_dir))
        parsed = parser.parse(dataset_path=args.dataset, reporting_day=args.day)
        stage_reached = "ingest"

        _require_stage_approval(
            stage_name="ingest",
            checkpoint_payload=asdict(parsed.operator_checkpoint),
            approved=_is_approved(args.approve_ingest, args.auto_approve),
            output_dir=output_dir,
        )

        planner = MerchantDailyPlanner(schema_path=str(schema_path), output_dir=str(output_dir))
        plan = planner.plan_from_parsed(parsed)
        stage_reached = "draft"

        _require_stage_approval(
            stage_name="draft",
            checkpoint_payload=asdict(plan.checkpoint),
            approved=_is_approved(args.approve_draft, args.auto_approve),
            output_dir=output_dir,
        )

        verifier = MerchantDailyVerifier(schema_path=str(schema_path), output_dir=str(output_dir))
        verify_result, verify_checkpoint = verifier.verify()
        verifier_passed = verify_result.passed
        verifier_issue_codes = [issue.code for issue in verify_result.issues]
        stage_reached = "verify"

        _require_stage_approval(
            stage_name="verify",
            checkpoint_payload=asdict(verify_checkpoint),
            approved=_is_approved(args.approve_verify, args.auto_approve),
            output_dir=output_dir,
        )

        if not verify_result.passed:
            _emit_final_checkpoint(
                output_dir=output_dir,
                verifier_passed=False,
                approved_for_publish=False,
                summary_path=reports_root / "merchant_daily_snapshot.json",
                markdown_path=reports_root / "merchant_daily_snapshot.md",
                pdf_path=reports_root / "merchant_daily_snapshot.pdf",
            )
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status="verifier_failed",
                    stage_reached=stage_reached,
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=False,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=False,
                    published=False,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                "verifier_failed",
                False,
                {"mission_stability_score": 0.5, "risk_score": 0.7},
            )
            print("Verification failed; final publish checkpoint emitted with hold status")
            return 3

        summary = verify_result.json_summary_candidate
        sections = plan.report_sections
        markdown_content = _render_markdown_report(summary, sections)

        summary_path = reports_root / "merchant_daily_snapshot.json"
        markdown_path = reports_root / "merchant_daily_snapshot.md"
        pdf_path = reports_root / "merchant_daily_snapshot.pdf"

        _write_json(summary_path, summary)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown_content, encoding="utf-8")
        _write_minimal_pdf(pdf_path, markdown_content)

        publish_approved = _is_approved(args.approve_final, args.auto_approve)
        final_checkpoint = _emit_final_checkpoint(
            output_dir=output_dir,
            verifier_passed=True,
            approved_for_publish=publish_approved,
            summary_path=summary_path,
            markdown_path=markdown_path,
            pdf_path=pdf_path,
        )

        if not publish_approved:
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                _build_run_event(
                    run_id=run_id,
                    status="awaiting_final_publish",
                    stage_reached="final",
                    args=args,
                    output_dir=output_dir,
                    verifier_passed=True,
                    verifier_issue_codes=verifier_issue_codes,
                    publish_approved=False,
                    published=False,
                ),
            )
            _register_governance_result(
                governance,
                "merchant_daily_snapshot",
                "awaiting_final_publish",
                True,
                {"mission_stability_score": 0.8, "risk_score": 0.35},
            )
            print("Final artifacts generated; awaiting OP-FINAL-PUBLISH approval")
            print(json.dumps(final_checkpoint, indent=2, ensure_ascii=True))
            return 4

        published = True
        _append_jsonl(
            output_dir / "mission_runs.jsonl",
            _build_run_event(
                run_id=run_id,
                status="completed_published",
                stage_reached="final",
                args=args,
                output_dir=output_dir,
                verifier_passed=True,
                verifier_issue_codes=verifier_issue_codes,
                publish_approved=True,
                published=True,
            ),
        )
        _register_governance_result(
            governance,
            "merchant_daily_snapshot",
            "completed_published",
            True,
            {"mission_stability_score": 1.0, "risk_score": 0.2},
        )
        print("Mission complete and publish approved")
        return 0
    except MissionDataValidationError as exc:
        _append_jsonl(
            output_dir / "mission_runs.jsonl",
            _build_run_event(
                run_id=run_id,
                status="parser_validation_failed",
                stage_reached=stage_reached,
                args=args,
                output_dir=output_dir,
                verifier_passed=verifier_passed,
                verifier_issue_codes=verifier_issue_codes,
                publish_approved=publish_approved,
                published=published,
                error=str(exc),
            ),
        )
        _register_governance_result(
            governance,
            "merchant_daily_snapshot",
            "parser_validation_failed",
            False,
            {"mission_stability_score": 0.45, "risk_score": 0.75},
        )
        print("Parser validation failed")
        print(str(exc))
        return 2
    except PermissionError as exc:
        _append_jsonl(
            output_dir / "mission_runs.jsonl",
            _build_run_event(
                run_id=run_id,
                status="operator_denied",
                stage_reached=stage_reached,
                args=args,
                output_dir=output_dir,
                verifier_passed=verifier_passed,
                verifier_issue_codes=verifier_issue_codes,
                publish_approved=publish_approved,
                published=published,
                error=str(exc),
            ),
        )
        _register_governance_result(
            governance,
            "merchant_daily_snapshot",
            "operator_denied",
            False,
            {"mission_stability_score": 0.55, "risk_score": 0.65},
        )
        print(str(exc))
        return 5
    except Exception as exc:  # pragma: no cover - defensive safeguard.
        _append_jsonl(
            output_dir / "mission_runs.jsonl",
            _build_run_event(
                run_id=run_id,
                status="runtime_error",
                stage_reached=stage_reached,
                args=args,
                output_dir=output_dir,
                verifier_passed=verifier_passed,
                verifier_issue_codes=verifier_issue_codes,
                publish_approved=publish_approved,
                published=published,
                error=str(exc),
            ),
        )
        _register_governance_result(
            governance,
            "merchant_daily_snapshot",
            "runtime_error",
            False,
            {"mission_stability_score": 0.4, "risk_score": 0.9},
        )
        print(f"Unhandled runtime error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

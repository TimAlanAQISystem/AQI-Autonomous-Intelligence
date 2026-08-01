from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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

from mission_parser import DealflowConversationParser, DealflowParserError
from planner import DealflowConversationPlanner
from verifier import DealflowConversationVerifier


def _utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


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
    result_details: Dict[str, Any] | None = None,
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


def _render_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Dealflow Conversation Mission Summary")
    lines.append("")
    lines.append(f"Session: {summary['context'].get('session_id', 'unknown')}")
    lines.append(f"Stage: {summary['context'].get('opportunity_stage', 'unknown')}")
    lines.append("")
    lines.append("## Derived Metrics")
    lines.append("")
    for key, value in summary.get("derived_metrics", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Recommended Actions")
    lines.append("")
    for action in summary.get("recommended_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run dealflow conversation mission")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--schema", default="missions/dealflow_conversation/schema.json")
    parser.add_argument("--output-dir", default="reports/dealflow_conversation")
    parser.add_argument("--use-orchestrator", action="store_true", help="Route mission sub-tasks through AQI multi-agent orchestrator")
    return parser


def main() -> int:
    args = _build_cli().parse_args()
    output_dir = Path(args.output_dir)
    governance = _build_governance_controller()
    orchestrator = _build_orchestrator(governance)

    if governance is not None:
        gate = governance.can_start_mission(
            "dealflow_conversation",
            {
                "payload": str(Path(args.payload)).replace("\\", "/"),
                "stability_score": 1.0,
                "risk_score": 0.3,
            },
        )
        if not gate.allowed:
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                {
                    "timestamp_utc": _utc_now(),
                    "status": "governance_denied",
                    "payload": str(Path(args.payload)).replace("\\", "/"),
                    "error": gate.reason,
                },
            )
            _register_governance_result(
                governance,
                "dealflow_conversation",
                "governance_denied",
                False,
                {"mission_stability_score": 0.4, "risk_score": 0.85},
            )
            print(f"Global governance denied mission start: {gate.reason}")
            return 6

    if args.use_orchestrator and orchestrator is not None:
        coordination = orchestrator.coordinate_mission(
            "dealflow_conversation",
            {
                "payload": str(Path(args.payload)).replace("\\", "/"),
                "risk_score": 0.3,
            },
        )
        if coordination.get("status") == "governance_denied":
            reason = str((coordination.get("decision") or {}).get("reason", "orchestrator governance denied"))
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                {
                    "timestamp_utc": _utc_now(),
                    "status": "orchestrator_governance_denied",
                    "payload": str(Path(args.payload)).replace("\\", "/"),
                    "use_orchestrator": True,
                    "error": reason,
                },
            )
            _register_governance_result(
                governance,
                "dealflow_conversation",
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
                    "dealflow_conversation_summary.json",
                    "dealflow_conversation_summary.md",
                    "operator_checkpoint_final_publish.json",
                ],
            }
            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                {
                    "timestamp_utc": _utc_now(),
                    "status": "orchestrator_integration_failed",
                    "payload": str(Path(args.payload)).replace("\\", "/"),
                    "use_orchestrator": True,
                    "error": reason,
                    "artifact_integrity": artifact_integrity,
                },
            )
            _register_governance_result(
                governance,
                "dealflow_conversation",
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
                {"mission_stability_score": 0.65, "risk_score": 0.4}
                if coordination_status == "partially_blocked"
                else {"mission_stability_score": 0.4, "risk_score": 0.75}
            )

            _append_jsonl(
                output_dir / "mission_runs.jsonl",
                {
                    "timestamp_utc": _utc_now(),
                    "status": outcome_status,
                    "payload": str(Path(args.payload)).replace("\\", "/"),
                    "use_orchestrator": True,
                    "error": reason,
                },
            )
            _register_governance_result(
                governance,
                "dealflow_conversation",
                outcome_status,
                False,
                outcome_metrics,
            )
            print(f"Orchestrator routing incomplete: {reason}")
            return 8 if coordination_status == "partially_blocked" else 9

    try:
        parser = DealflowConversationParser(schema_path=args.schema)
        parsed = parser.parse(args.payload)
    except DealflowParserError as exc:
        _append_jsonl(
            output_dir / "mission_runs.jsonl",
            {
                "timestamp_utc": _utc_now(),
                "status": "parser_validation_failed",
                "error": str(exc),
                "payload": args.payload,
            },
        )
        _register_governance_result(
            governance,
            "dealflow_conversation",
            "parser_validation_failed",
            False,
            {"mission_stability_score": 0.45, "risk_score": 0.75},
        )
        print(str(exc))
        return 2

    planner = DealflowConversationPlanner(schema_path=args.schema, output_dir=args.output_dir)
    plan = planner.plan_from_parsed(parsed)

    verifier = DealflowConversationVerifier(schema_path=args.schema, output_dir=args.output_dir)
    verify_result, verify_checkpoint = verifier.verify()

    summary = {
        "mission_id": plan.mission_id,
        "context": plan.reporting_context,
        "profile_metadata": (plan.reporting_context or {}).get("profile_metadata", {}),
        "derived_metrics": plan.derived_metrics,
        "recommended_actions": plan.recommended_actions,
        "verification_passed": verify_result.passed,
        "verification_issue_count": len(verify_result.issues),
        "generated_at_utc": _utc_now(),
    }

    summary_json = output_dir / "dealflow_conversation_summary.json"
    summary_md = output_dir / "dealflow_conversation_summary.md"
    _write_json(summary_json, summary)
    summary_md.write_text(_render_markdown(summary), encoding="utf-8")

    _write_json(output_dir / "operator_checkpoint_final_publish.json", {
        "checkpoint_id": "OP-FINAL-PUBLISH",
        "stage": "pre_distribution",
        "required": True,
        "triggered": True,
        "required_operator_action": "publish" if verify_result.passed else "hold_and_revise",
        "payload": {
            "summary_json": str(summary_json).replace("\\", "/"),
            "summary_markdown": str(summary_md).replace("\\", "/"),
            "verify_checkpoint": verify_checkpoint,
        },
    })

    _append_jsonl(
        output_dir / "mission_runs.jsonl",
        {
            "timestamp_utc": _utc_now(),
            "status": "completed" if verify_result.passed else "verifier_failed",
            "payload": str(Path(args.payload)).replace("\\", "/"),
            "use_orchestrator": bool(args.use_orchestrator),
            "summary_json": str(summary_json).replace("\\", "/"),
            "verification_passed": verify_result.passed,
        },
    )

    _register_governance_result(
        governance,
        "dealflow_conversation",
        "completed" if verify_result.passed else "verifier_failed",
        bool(verify_result.passed),
        {
            "mission_stability_score": 1.0 if verify_result.passed else 0.5,
            "risk_score": 0.2 if verify_result.passed else 0.7,
        },
    )

    print(json.dumps(summary, ensure_ascii=True))
    return 0 if verify_result.passed else 3


if __name__ == "__main__":
    raise SystemExit(main())

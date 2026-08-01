from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_STATE_PATH = Path("reports") / "aqi_governance" / "governance_state.json"

SUCCESS_STATUSES = {"completed", "completed_published", "awaiting_final_publish"}
HARD_FAILURE_STATUSES = {
    "integration_failed",
    "orchestrator_integration_failed",
    "governance_denied",
    "orchestrator_governance_denied",
    "orchestrator_partially_blocked",
    "orchestrator_blocked",
    "parser_validation_failed",
    "verifier_failed",
    "operator_denied",
    "runtime_error",
    "failed",
    "error",
    "blocked",
}


@dataclass
class GovernanceState:
    active_mission: Optional[Dict[str, Any]] = None
    pending_missions: List[Dict[str, Any]] = field(default_factory=list)
    last_mission_result: Optional[Dict[str, Any]] = None
    global_stability_score: float = 1.0
    global_escalation_rate: float = 0.0
    unauthorized_commitment_count: int = 0
    risk_level: str = "green"
    operator_review_required: bool = False
    total_missions_started: int = 0
    total_missions_completed: int = 0
    total_conversation_turns: int = 0
    total_conversation_escalations: int = 0
    updated_at_utc: str = ""


def _utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_state(state_path: str | Path = DEFAULT_STATE_PATH) -> GovernanceState:
    path = Path(state_path)
    if not path.exists():
        state = GovernanceState(updated_at_utc=_utc_now())
        save_state(state, path)
        return state

    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        return GovernanceState(updated_at_utc=_utc_now())

    return GovernanceState(
        active_mission=raw.get("active_mission"),
        pending_missions=list(raw.get("pending_missions", [])),
        last_mission_result=raw.get("last_mission_result"),
        global_stability_score=float(raw.get("global_stability_score", 1.0)),
        global_escalation_rate=float(raw.get("global_escalation_rate", 0.0)),
        unauthorized_commitment_count=int(raw.get("unauthorized_commitment_count", 0)),
        risk_level=str(raw.get("risk_level", "green")),
        operator_review_required=bool(raw.get("operator_review_required", False)),
        total_missions_started=int(raw.get("total_missions_started", 0)),
        total_missions_completed=int(raw.get("total_missions_completed", 0)),
        total_conversation_turns=int(raw.get("total_conversation_turns", 0)),
        total_conversation_escalations=int(raw.get("total_conversation_escalations", 0)),
        updated_at_utc=str(raw.get("updated_at_utc", "")) or _utc_now(),
    )


def save_state(state: GovernanceState, state_path: str | Path = DEFAULT_STATE_PATH) -> None:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state.updated_at_utc = _utc_now()
    path.write_text(json.dumps(asdict(state), indent=2, ensure_ascii=True), encoding="utf-8")


def update_from_mission_result(
    state: GovernanceState,
    *,
    mission_type: str,
    result: Dict[str, Any],
    metrics: Dict[str, Any],
) -> GovernanceState:
    status = str(result.get("status", "unknown"))
    status_lower = status.lower()

    raw_passed = bool(result.get("passed", status_lower in SUCCESS_STATUSES))
    failure_reason = str(result.get("failure_reason", "") or "")
    failure_class = str(result.get("failure_class", "") or "")
    failure_stage = str(result.get("failure_stage", "") or "")
    stability_preview = result.get("stability_preview")
    artifact_integrity = result.get("artifact_integrity")

    is_failure = (
        status_lower in HARD_FAILURE_STATUSES
        or bool(failure_reason)
        or bool(failure_class)
        or bool(failure_stage)
        or (
            isinstance(stability_preview, dict)
            and stability_preview.get("is_stable") is False
        )
    )
    passed = False if is_failure else raw_passed

    summary_type = "integration_failed" if "integration" in status_lower else status_lower
    if isinstance(stability_preview, dict) and stability_preview.get("summary_type"):
        summary_type = str(stability_preview.get("summary_type"))

    last_mission_result: Dict[str, Any] = {
        "mission_type": mission_type,
        "status": status,
        "passed": passed,
        "summary_type": summary_type,
        "timestamp_utc": _utc_now(),
    }
    if failure_reason:
        last_mission_result["failure_reason"] = failure_reason
    if failure_class:
        last_mission_result["failure_class"] = failure_class
    if failure_stage:
        last_mission_result["failure_stage"] = failure_stage
    if isinstance(artifact_integrity, dict):
        last_mission_result["artifact_integrity"] = dict(artifact_integrity)
    if isinstance(stability_preview, dict):
        last_mission_result["stability_preview"] = dict(stability_preview)

    state.last_mission_result = last_mission_result

    if state.active_mission and state.active_mission.get("mission_type") == mission_type:
        state.active_mission = None

    if passed:
        state.total_missions_completed += 1

    mission_stability = metrics.get("mission_stability_score") or metrics.get("conversation_stability_score")
    if mission_stability is not None:
        state.global_stability_score = max(0.0, min(1.0, float(mission_stability)))

    escalations = int(metrics.get("escalation_flags", 0))
    if escalations > 0:
        state.operator_review_required = True

    return state


def update_from_conversation_metrics(
    state: GovernanceState,
    *,
    stability_score: float,
    escalation_rate: float,
    unauthorized_commitment_blocks: int,
) -> GovernanceState:
    state.total_conversation_turns += 1
    if escalation_rate > 0:
        state.total_conversation_escalations += 1

    state.global_stability_score = max(0.0, min(1.0, float(stability_score)))
    state.global_escalation_rate = max(0.0, min(1.0, float(escalation_rate)))
    state.unauthorized_commitment_count += int(max(0, unauthorized_commitment_blocks))

    if state.unauthorized_commitment_count > 0 or escalation_rate > 0.2:
        state.operator_review_required = True

    if state.global_stability_score < 0.55 or state.global_escalation_rate > 0.45:
        state.risk_level = "red"
    elif state.global_stability_score < 0.75 or state.global_escalation_rate > 0.2:
        state.risk_level = "yellow"
    else:
        state.risk_level = "green"

    return state

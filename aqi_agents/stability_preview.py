from __future__ import annotations

from typing import Any, Dict


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def build_stability_preview(mission_result: Dict[str, Any] | None) -> Dict[str, Any]:
    if not isinstance(mission_result, dict) or not mission_result:
        return {
            "is_stable": True,
            "summary_type": "no_signal",
        }

    status = _as_text(mission_result.get("status")).lower()
    failure_reason = _as_text(mission_result.get("failure_reason"))
    failure_class = _as_text(mission_result.get("failure_class"))
    failure_stage = _as_text(mission_result.get("failure_stage"))

    if not failure_reason:
        failure_reason = _as_text(mission_result.get("reason"))
    if not failure_reason:
        failure_reason = _as_text((mission_result.get("decision") or {}).get("reason"))

    if not failure_class and "integration" in status:
        failure_class = "integration"
    if not failure_stage and failure_class == "integration":
        failure_stage = "qpc"

    artifact_integrity = mission_result.get("artifact_integrity")
    if not isinstance(artifact_integrity, dict):
        artifact_integrity = {}

    is_failure = status in {
        "integration_failed",
        "orchestrator_integration_failed",
        "failed",
        "error",
        "blocked",
    } or bool(failure_reason)

    if is_failure:
        return {
            "is_stable": False,
            "summary_type": "integration_failed" if failure_class == "integration" or "integration" in status else "failed",
            "failure_reason": failure_reason,
            "failure_class": failure_class,
            "failure_stage": failure_stage,
            "artifact_integrity": artifact_integrity,
        }

    return {
        "is_stable": True,
        "summary_type": "stable",
        "mission_succeeded": True,
    }

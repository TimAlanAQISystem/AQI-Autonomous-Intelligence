from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


@dataclass
class AutonomousDecision:
    status: str
    action: str
    reason: str
    domain: str
    workflow_id: str
    subflow: str
    details: Dict[str, Any]


class OperatorSimulationEngine:
    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def start(self, session: WorkflowSession, workflow_id: str, workflow_type: str) -> Dict[str, Any]:
        return self.runtime.start_workflow(session, workflow_id, workflow_type=workflow_type)

    def surface(self, session: WorkflowSession) -> Dict[str, Any]:
        return self.runtime.get_operator_surface(session)


class AutonomousDecisionLoop:
    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def _emit_lineage(self, session: WorkflowSession, action: str, surface: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> None:
        payload = {
            "action": action,
            "domain": surface.get("domain", "unknown"),
            "workflow_id": surface.get("workflow_id", "unknown"),
            "subflow": surface.get("subflow", ""),
            "details": dict(details or {}),
        }
        self.runtime.emit_event(session, "autonomous_decision", payload)

    def _select_action(self, surface: Dict[str, Any], force_recovery: bool = False) -> str:
        if force_recovery:
            return "orchestrate_recovery"
        compliance_state = ((surface.get("observability") or {}).get("compliance") or {}).get("state", "ready")
        if compliance_state == "blocked":
            return "hold_for_compliance"
        sequencing = surface.get("sequencing") or {}
        next_subflows = list(sequencing.get("next_subflows", []))
        if next_subflows:
            return "transition_next"
        return "complete"

    def run_once(self, session: WorkflowSession, force_recovery: bool = False, reason: str = "autonomous_loop") -> Dict[str, Any]:
        surface = self.runtime.get_operator_surface(session)
        if surface.get("status") != "ready":
            return {
                "status": "failed",
                "action": "surface_unavailable",
                "reason": surface.get("reason", "operator_surface_unavailable"),
                "surface": surface,
            }

        action = self._select_action(surface, force_recovery=force_recovery)
        if action == "transition_next":
            next_subflows = list((surface.get("sequencing") or {}).get("next_subflows", []))
            if not next_subflows:
                self._emit_lineage(session, "no_next_subflow", surface)
                return {
                    "status": "ok",
                    "action": "no_next_subflow",
                    "reason": "terminal_state",
                    "surface": self.runtime.get_operator_surface(session),
                }

            transition = self.runtime.advance_subflow(session, next_subflows[0])
            self._emit_lineage(session, "transition_next", surface, {"target": next_subflows[0], "transition": transition})
            return {
                "status": transition.get("status", "unknown"),
                "action": "transition_next",
                "reason": transition.get("reason", "sequenced"),
                "result": transition,
                "surface": self.runtime.get_operator_surface(session),
            }

        if action == "orchestrate_recovery":
            recovered = self.runtime.orchestrate_recovery(session, reason=reason)
            self._emit_lineage(session, "orchestrate_recovery", surface, {"recovered": recovered})
            return {
                "status": recovered.get("status", "unknown"),
                "action": "orchestrate_recovery",
                "reason": recovered.get("reason", reason),
                "result": recovered,
                "surface": self.runtime.get_operator_surface(session),
            }

        if action == "hold_for_compliance":
            self._emit_lineage(session, "hold_for_compliance", surface, {"missing_flags": (surface.get("observability") or {}).get("compliance", {}).get("missing_flags", [])})
            return {
                "status": "blocked",
                "action": "hold_for_compliance",
                "reason": "compliance_blocked",
                "surface": surface,
            }

        self._emit_lineage(session, "complete", surface)
        return {
            "status": "ok",
            "action": "complete",
            "reason": "terminal_state",
            "surface": surface,
        }


def run_autonomous_loop(
    runtime: WorkflowRuntimeEngine,
    session: WorkflowSession,
    max_steps: int = 3,
    force_recovery_at_step: Optional[int] = None,
    recovery_reason: str = "autonomous_recovery",
) -> List[Dict[str, Any]]:
    loop = AutonomousDecisionLoop(runtime)
    decisions: List[Dict[str, Any]] = []
    for idx in range(max_steps):
        decision = loop.run_once(
            session,
            force_recovery=(force_recovery_at_step is not None and idx == force_recovery_at_step),
            reason=recovery_reason,
        )
        decisions.append(decision)
        if decision.get("action") in {"complete", "hold_for_compliance", "surface_unavailable"}:
            break
    return decisions

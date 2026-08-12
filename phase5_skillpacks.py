from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


@dataclass
class SkillPackDecision:
    status: str
    action: str
    reason: str
    domain: str
    workflow_id: str
    subflow: str
    reasoning: Dict[str, Any]
    observability: Dict[str, Any]
    lineage: Dict[str, Any]
    result: Dict[str, Any]


class BaseOperatorSkillPack:
    DECISION_SIGNATURE = "skillpack_decision:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def _lineage_record(self, session: WorkflowSession, action: str, reason: str, surface: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        lineage = {
            "signature": self.DECISION_SIGNATURE,
            "scope": "phase5_skillpack",
            "action": action,
            "reason": reason,
            "domain": surface.get("domain", "unknown"),
            "workflow_id": surface.get("workflow_id", "unknown"),
            "subflow": surface.get("subflow", ""),
            "details": dict(details),
        }
        self.runtime.emit_event(session, "skillpack_decision", lineage)
        return lineage

    def _build_reasoning(self, surface: Dict[str, Any]) -> Dict[str, Any]:
        observability = surface.get("observability") or {}
        compliance = observability.get("compliance") or {}
        sequencing = surface.get("sequencing") or {}
        recovery = observability.get("recovery") or {}
        return {
            "surface_domain": surface.get("domain", "unknown"),
            "compliance_state": compliance.get("state", "ready"),
            "compliance_missing_flags": list(compliance.get("missing_flags", [])),
            "sequencing_next": list(sequencing.get("next_subflows", [])),
            "recovery_state": recovery.get("state", "none"),
        }

    def decide(self, session: WorkflowSession, force_recovery: bool = False, reason: str = "skillpack_loop") -> Dict[str, Any]:
        surface = self.runtime.get_operator_surface(session)
        if surface.get("status") != "ready":
            return {
                "status": "failed",
                "action": "surface_unavailable",
                "reason": surface.get("reason", "operator_surface_unavailable"),
                "domain": "unknown",
                "workflow_id": "unknown",
                "subflow": "",
                "reasoning": {},
                "observability": {},
                "lineage": {},
                "result": surface,
            }

        reasoning = self._build_reasoning(surface)
        observability = dict(surface.get("observability") or {})
        domain = str(surface.get("domain", "unknown"))
        workflow_id = str(surface.get("workflow_id", "unknown"))
        subflow = str(surface.get("subflow", ""))
        next_subflows = list((surface.get("sequencing") or {}).get("next_subflows", []))
        compliance_state = ((surface.get("observability") or {}).get("compliance") or {}).get("state", "ready")

        if force_recovery:
            recovered = self.runtime.orchestrate_recovery(session, reason=reason)
            lineage = self._lineage_record(session, "orchestrate_recovery", reason, surface, {"recovered": recovered})
            return {
                "status": recovered.get("status", "unknown"),
                "action": "orchestrate_recovery",
                "reason": recovered.get("reason", reason),
                "domain": domain,
                "workflow_id": workflow_id,
                "subflow": subflow,
                "reasoning": {**reasoning, "recovery_triggered": True},
                "observability": observability,
                "lineage": lineage,
                "result": recovered,
            }

        if compliance_state == "blocked":
            lineage = self._lineage_record(
                session,
                "hold_for_compliance",
                "compliance_blocked",
                surface,
                {"missing_flags": reasoning.get("compliance_missing_flags", [])},
            )
            return {
                "status": "blocked",
                "action": "hold_for_compliance",
                "reason": "compliance_blocked",
                "domain": domain,
                "workflow_id": workflow_id,
                "subflow": subflow,
                "reasoning": reasoning,
                "observability": observability,
                "lineage": lineage,
                "result": surface,
            }

        if next_subflows:
            target = str(next_subflows[0])
            transition = self.runtime.advance_subflow(session, target)
            transition_reason = transition.get("reason", "sequenced")
            lineage = self._lineage_record(
                session,
                "transition_next",
                str(transition_reason),
                surface,
                {"target": target, "transition": transition},
            )
            return {
                "status": transition.get("status", "unknown"),
                "action": "transition_next",
                "reason": str(transition_reason),
                "domain": domain,
                "workflow_id": workflow_id,
                "subflow": subflow,
                "reasoning": reasoning,
                "observability": observability,
                "lineage": lineage,
                "result": transition,
            }

        lineage = self._lineage_record(session, "complete", "terminal_state", surface, {})
        return {
            "status": "ok",
            "action": "complete",
            "reason": "terminal_state",
            "domain": domain,
            "workflow_id": workflow_id,
            "subflow": subflow,
            "reasoning": reasoning,
            "observability": observability,
            "lineage": lineage,
            "result": surface,
        }


class MerchantServiceSkillPack(BaseOperatorSkillPack):
    pass


class OperatorCardSkillPack(BaseOperatorSkillPack):
    pass


class MixedDomainSkillPack(BaseOperatorSkillPack):
    pass

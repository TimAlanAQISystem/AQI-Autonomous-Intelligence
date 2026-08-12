from __future__ import annotations

from typing import Any, Dict, List

from phase5_skillpacks import MixedDomainSkillPack, MerchantServiceSkillPack, OperatorCardSkillPack
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class AutonomousOperatorStrategyEngine:
    STRATEGY_SIGNATURE = "strategy_decision:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def _select_strategy(self, goal: str) -> str:
        normalized = goal.strip().lower()
        if "recover" in normalized:
            return "recovery_correction"
        if "compliance" in normalized:
            return "compliance_guarded"
        return "progressive_completion"

    def _emit_strategy_lineage(
        self,
        session: WorkflowSession,
        strategy_name: str,
        goal: str,
        step_index: int,
        requested_action: str,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        surface = decision.get("observability") or {}
        lineage = {
            "signature": self.STRATEGY_SIGNATURE,
            "scope": "phase5_strategy",
            "strategy": strategy_name,
            "goal": goal,
            "step_index": step_index,
            "requested_action": requested_action,
            "action": decision.get("action", "unknown"),
            "status": decision.get("status", "unknown"),
            "reason": decision.get("reason", "unknown"),
            "domain": decision.get("domain", "unknown"),
            "workflow_id": decision.get("workflow_id", "unknown"),
            "subflow": decision.get("subflow", ""),
            "compliance_state": (surface.get("compliance") or {}).get("state", "ready"),
        }
        self.runtime.emit_event(session, "strategy_decision", lineage)
        return lineage

    def _execute_requested_action(
        self,
        skill_pack: MerchantServiceSkillPack | OperatorCardSkillPack | MixedDomainSkillPack,
        session: WorkflowSession,
        requested_action: str,
        goal: str,
    ) -> Dict[str, Any]:
        if requested_action == "orchestrate_recovery":
            return skill_pack.decide(session, force_recovery=True, reason=goal)
        return skill_pack.decide(session)

    def run_strategy(
        self,
        skill_pack: MerchantServiceSkillPack | OperatorCardSkillPack | MixedDomainSkillPack,
        session: WorkflowSession,
        goal: str,
        max_steps: int = 3,
    ) -> Dict[str, Any]:
        strategy_name = self._select_strategy(goal)
        requested_actions: List[str]
        if strategy_name == "recovery_correction":
            requested_actions = ["orchestrate_recovery"] + ["transition_next"] * max(0, max_steps - 1)
        else:
            requested_actions = ["transition_next"] * max_steps

        steps: List[Dict[str, Any]] = []
        pruned = False
        status = "ok"

        for idx, requested_action in enumerate(requested_actions):
            decision = self._execute_requested_action(skill_pack, session, requested_action, goal)
            lineage = self._emit_strategy_lineage(session, strategy_name, goal, idx, requested_action, decision)
            step = {
                "index": idx,
                "requested_action": requested_action,
                "action": decision.get("action", "unknown"),
                "status": decision.get("status", "unknown"),
                "reason": decision.get("reason", "unknown"),
                "lineage": lineage,
            }
            steps.append(step)

            if decision.get("action") == "hold_for_compliance":
                status = "blocked"
                pruned = True
                break
            if decision.get("status") == "failed" and decision.get("reason") == "subflow_compliance_blocked":
                status = "blocked"
                pruned = True
                followup = self._execute_requested_action(skill_pack, session, "hold_for_compliance", goal)
                followup_lineage = self._emit_strategy_lineage(session, strategy_name, goal, idx + 1, "hold_for_compliance", followup)
                steps.append(
                    {
                        "index": idx + 1,
                        "requested_action": "hold_for_compliance",
                        "action": followup.get("action", "unknown"),
                        "status": followup.get("status", "unknown"),
                        "reason": followup.get("reason", "unknown"),
                        "lineage": followup_lineage,
                    }
                )
                break
            if decision.get("action") == "complete":
                break

        final_surface = self.runtime.get_operator_surface(session)
        observability = final_surface.get("observability", {}) if final_surface.get("status") == "ready" else {}
        compliance = observability.get("compliance", {}) if isinstance(observability, dict) else {}
        if compliance.get("state") == "blocked":
            status = "blocked"

        return {
            "status": status,
            "strategy": {
                "selected": strategy_name,
                "goal": goal,
                "pruned": pruned,
            },
            "steps": steps,
            "surface": final_surface,
            "observability": observability,
            "compliance": compliance,
        }


class MerchantServiceStrategyPack(MerchantServiceSkillPack):
    pass


class OperatorCardStrategyPack(OperatorCardSkillPack):
    pass


class MixedDomainStrategyPack(MixedDomainSkillPack):
    pass

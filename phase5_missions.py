from __future__ import annotations

from typing import Any, Dict, List

from phase5_strategies import (
    AutonomousOperatorStrategyEngine,
    MerchantServiceStrategyPack,
    MixedDomainStrategyPack,
    OperatorCardStrategyPack,
)
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class MissionOrchestrationEngine:
    MISSION_SIGNATURE = "mission_decision:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime
        self.strategy_engine = AutonomousOperatorStrategyEngine(runtime)

    def _emit_mission_lineage(
        self,
        session: WorkflowSession,
        mission_name: str,
        stage_index: int,
        stage: Dict[str, Any],
        strategy_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "signature": self.MISSION_SIGNATURE,
            "scope": "phase5_mission",
            "mission": mission_name,
            "stage_index": stage_index,
            "stage_goal": stage.get("goal", "unknown"),
            "stage_strategy": (strategy_result.get("strategy") or {}).get("selected", "unknown"),
            "stage_status": strategy_result.get("status", "unknown"),
            "domain": (strategy_result.get("surface") or {}).get("domain", "unknown"),
            "compliance_state": (strategy_result.get("compliance") or {}).get("state", "ready"),
        }
        self.runtime.emit_event(session, "mission_decision", payload)
        return payload

    def execute_mission(self, mission_pack: "BaseMissionPack", session: WorkflowSession, mission_name: str) -> Dict[str, Any]:
        stages = mission_pack.decompose_mission(mission_name)
        if not stages:
            return {
                "status": "failed",
                "reason": "mission_not_found",
                "mission": mission_name,
                "stages": [],
            }

        executed: List[Dict[str, Any]] = []
        mission_status = "ok"
        blocked_stages = 0
        recovery_corrections = 0

        for idx, stage in enumerate(stages):
            result = self.strategy_engine.run_strategy(
                mission_pack,
                session,
                goal=str(stage.get("goal", "progressive_path")),
                max_steps=int(stage.get("max_steps", 2)),
            )
            lineage = self._emit_mission_lineage(session, mission_name, idx, stage, result)
            executed.append(
                {
                    "stage_index": idx,
                    "stage_goal": stage.get("goal", ""),
                    "result": result,
                    "lineage": lineage,
                }
            )

            if result.get("status") == "blocked":
                blocked_stages += 1
                mission_status = "blocked"
                if stage.get("allow_recovery_correction"):
                    correction_goal = str(stage.get("recovery_goal", "recover_underwriting"))
                    correction = self.strategy_engine.run_strategy(
                        mission_pack,
                        session,
                        goal=correction_goal,
                        max_steps=int(stage.get("recovery_steps", 1)),
                    )
                    correction_lineage = self._emit_mission_lineage(
                        session,
                        mission_name,
                        idx,
                        {"goal": correction_goal},
                        correction,
                    )
                    executed.append(
                        {
                            "stage_index": idx,
                            "stage_goal": correction_goal,
                            "result": correction,
                            "lineage": correction_lineage,
                            "correction": True,
                        }
                    )
                    recovery_corrections += 1
                break

        surface = self.runtime.get_operator_surface(session)
        observability = surface.get("observability", {}) if surface.get("status") == "ready" else {}
        mission_compliance = dict(observability.get("compliance", {})) if isinstance(observability, dict) else {}
        if mission_status == "blocked":
            mission_compliance["state"] = "blocked"
            mission_compliance.setdefault("scope", "subflow")
            mission_compliance.setdefault("signature", WorkflowRuntimeEngine.COMPLIANCE_SIGNATURE)

            for stage in executed:
                stage_compliance = ((stage.get("result") or {}).get("compliance") or {})
                missing = list(stage_compliance.get("missing_flags", []))
                if missing:
                    mission_compliance["missing_flags"] = missing
                    break

        return {
            "status": mission_status,
            "mission": mission_name,
            "decomposition": [dict(item) for item in stages],
            "stages": executed,
            "lineage_signature": self.MISSION_SIGNATURE,
            "observability": {
                "status": observability.get("status", "unknown"),
                "domain": surface.get("domain", "unknown"),
                "blocked_stages": blocked_stages,
                "recovery_corrections": recovery_corrections,
                "compliance": mission_compliance,
                "recovery": dict(observability.get("recovery", {})) if isinstance(observability, dict) else {},
            },
            "surface": surface,
        }


class BaseMissionPack:
    missions: Dict[str, List[Dict[str, Any]]] = {}

    def decompose_mission(self, mission_name: str) -> List[Dict[str, Any]]:
        mission = self.missions.get(mission_name, [])
        return [dict(stage) for stage in mission]


class MerchantServiceMissionPack(MerchantServiceStrategyPack, BaseMissionPack):
    missions = {
        "complete_merchant_onboarding": [
            {"goal": "complete_onboarding", "max_steps": 3},
        ],
        "resolve_merchant_compliance_block": [
            {
                "goal": "compliance_guarded_path",
                "max_steps": 3,
                "allow_recovery_correction": True,
                "recovery_goal": "recover_underwriting",
                "recovery_steps": 1,
            }
        ],
        "merchant_recovery_sequence": [
            {"goal": "recover_underwriting", "max_steps": 1},
        ],
    }


class OperatorCardMissionPack(OperatorCardStrategyPack, BaseMissionPack):
    missions = {
        "complete_operator_verification": [
            {"goal": "resolve_escalation", "max_steps": 3},
        ],
        "navigate_operator_compliance_gate": [
            {
                "goal": "compliance_guarded_path",
                "max_steps": 2,
                "allow_recovery_correction": True,
                "recovery_goal": "recover_routing",
                "recovery_steps": 1,
            }
        ],
    }


class MixedDomainMissionPack(MixedDomainStrategyPack, BaseMissionPack):
    missions = {
        "cross_domain_progressive_mission": [
            {"goal": "progressive_path", "max_steps": 2},
        ],
        "cross_domain_recovery_mission": [
            {"goal": "recover_underwriting", "max_steps": 1},
        ],
    }

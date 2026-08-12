from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from phase5_missions import MissionOrchestrationEngine
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


@dataclass
class SupervisionGate:
    approved: bool
    supervisor_id: str
    supervision_mode: str = "strict"


class SupervisedAutonomousOperatorCallEngine:
    SAOC_SIGNATURE = "saoc_call:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime
        self.mission_engine = MissionOrchestrationEngine(runtime)

    def execute_supervised_call(
        self,
        session: WorkflowSession,
        mission_pack: Any,
        mission_name: str,
        supervision: SupervisionGate,
        call_adapter: Any,
    ) -> Dict[str, Any]:
        if not supervision.approved:
            self.runtime.emit_event(
                session,
                "saoc_supervision_blocked",
                {
                    "signature": self.SAOC_SIGNATURE,
                    "reason": "supervision_not_approved",
                    "supervisor_id": supervision.supervisor_id,
                    "supervision_mode": supervision.supervision_mode,
                },
            )
            return {
                "status": "blocked",
                "reason": "supervision_not_approved",
                "mission": mission_name,
            }

        mission_result = self.mission_engine.execute_mission(mission_pack, session, mission_name)
        if mission_result.get("status") == "failed":
            return {
                "status": "failed",
                "reason": mission_result.get("reason", "mission_failed"),
                "mission": mission_name,
                "mission_result": mission_result,
            }
        if mission_result.get("status") == "blocked":
            self.runtime.emit_event(
                session,
                "saoc_mission_blocked",
                {
                    "signature": self.SAOC_SIGNATURE,
                    "mission": mission_name,
                    "reason": "mission_blocked",
                },
            )
            return {
                "status": "blocked",
                "reason": "mission_blocked",
                "mission": mission_name,
                "mission_result": mission_result,
            }

        surface = mission_result.get("surface", {})
        call_payload = {
            "signature": self.SAOC_SIGNATURE,
            "mission": mission_name,
            "domain": surface.get("domain", "unknown"),
            "workflow_id": surface.get("workflow_id", "unknown"),
            "workflow_type": surface.get("workflow_type", "default"),
            "subflow": surface.get("subflow", ""),
            "supervisor_id": supervision.supervisor_id,
            "supervision_mode": supervision.supervision_mode,
            "observability": dict(mission_result.get("observability", {})),
            "lineage_signature": mission_result.get("lineage_signature", "mission_decision:v1"),
        }

        adapter_result = call_adapter.execute(call_payload)
        self.runtime.emit_event(
            session,
            "saoc_call_executed",
            {
                "signature": self.SAOC_SIGNATURE,
                "mission": mission_name,
                "domain": call_payload["domain"],
                "workflow_id": call_payload["workflow_id"],
                "supervisor_id": supervision.supervisor_id,
                "adapter_status": adapter_result.get("status", "unknown"),
            },
        )

        return {
            "status": "executed",
            "mission": mission_name,
            "payload": call_payload,
            "adapter_result": adapter_result,
            "mission_result": mission_result,
        }

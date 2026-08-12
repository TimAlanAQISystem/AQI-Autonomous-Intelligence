from __future__ import annotations

from typing import Any, Dict, List

from phase5_missions import BaseMissionPack, MissionOrchestrationEngine
from phase6_saoc import SupervisionGate
from phase6_sequences import BaseCallSequencePack, CallOrchestrationEngine
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class UnifiedSupervisedOperatorFlowEngine:
    UNIFIED_SIGNATURE = "unifiedflow_decision:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime
        self.mission_engine = MissionOrchestrationEngine(runtime)
        self.sequence_engine = CallOrchestrationEngine(runtime)

    def _collect_lineage_events(self, session: WorkflowSession) -> List[Dict[str, Any]]:
        event_names = {
            "skillpack_decision",
            "strategy_decision",
            "mission_decision",
            "callpack_blocked",
            "callpack_executed",
            "callsequence_decision",
            "unifiedflow_decision",
            "unifiedflow_supervision_blocked",
            "unifiedflow_blocked",
        }
        return [dict(item) for item in session.history if item.get("event_type") in event_names]

    def replay_from_lineage(self, lineage_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        signatures: Dict[str, int] = {}
        event_counts: Dict[str, int] = {}
        for event in lineage_events:
            event_type = str(event.get("event_type", "unknown"))
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

            signature = str(event.get("signature", "none"))
            signatures[signature] = signatures.get(signature, 0) + 1

        replay_key_parts = [f"{name}:{event_counts[name]}" for name in sorted(event_counts)]
        replay_signature = "|".join(replay_key_parts)
        return {
            "status": "replayed",
            "signature_counts": signatures,
            "event_counts": event_counts,
            "replay_signature": replay_signature,
            "event_total": len(lineage_events),
        }

    def _emit_unified_lineage(
        self,
        session: WorkflowSession,
        status: str,
        reason: str,
        domain: str,
        mission_name: str,
        sequence_name: str,
        gate: str = "none",
    ) -> Dict[str, Any]:
        payload = {
            "signature": self.UNIFIED_SIGNATURE,
            "scope": "phase6_unifiedflow",
            "status": status,
            "reason": reason,
            "gate": gate,
            "domain": domain,
            "mission": mission_name,
            "sequence": sequence_name,
        }
        self.runtime.emit_event(session, "unifiedflow_decision", payload)
        return payload

    def execute_unified_flow(
        self,
        session: WorkflowSession,
        mission_pack: BaseMissionPack,
        mission_name: str,
        sequence_pack: BaseCallSequencePack,
        sequence_name: str,
        supervision: SupervisionGate,
        call_adapter: Any,
    ) -> Dict[str, Any]:
        if not supervision.approved:
            payload = {
                "signature": self.UNIFIED_SIGNATURE,
                "scope": "phase6_unifiedflow",
                "status": "blocked",
                "reason": "supervision_not_approved",
                "gate": "supervision",
                "supervisor_id": supervision.supervisor_id,
                "supervision_mode": supervision.supervision_mode,
                "mission": mission_name,
                "sequence": sequence_name,
            }
            self.runtime.emit_event(session, "unifiedflow_supervision_blocked", payload)
            return {
                "status": "blocked",
                "reason": "supervision_not_approved",
                "gate": "supervision",
                "mission": mission_name,
                "sequence": sequence_name,
                "lineage": payload,
                "lineage_events": self._collect_lineage_events(session),
                "replay": self.replay_from_lineage(self._collect_lineage_events(session)),
            }

        mission_result = self.mission_engine.execute_mission(mission_pack, session, mission_name)
        mission_status = str(mission_result.get("status", "failed"))
        if mission_status in {"failed", "blocked"}:
            gate = "compliance" if mission_status == "blocked" else "mission"
            reason = "unified_compliance_blocked" if mission_status == "blocked" else "mission_failed"
            surface = self.runtime.get_operator_surface(session)
            domain = str(surface.get("domain", "unknown"))
            lineage = self._emit_unified_lineage(
                session,
                status="blocked" if mission_status == "blocked" else "failed",
                reason=reason,
                domain=domain,
                mission_name=mission_name,
                sequence_name=sequence_name,
                gate=gate,
            )
            lineage_events = self._collect_lineage_events(session)
            replay = self.replay_from_lineage(lineage_events)
            return {
                "status": "blocked" if mission_status == "blocked" else "failed",
                "reason": reason,
                "gate": gate,
                "mission": mission_name,
                "sequence": sequence_name,
                "mission_result": mission_result,
                "lineage": lineage,
                "lineage_events": lineage_events,
                "replay": replay,
            }

        sequence_result = self.sequence_engine.execute_sequence(sequence_pack, session, sequence_name, call_adapter)
        sequence_status = str(sequence_result.get("status", "failed"))
        sequence_gate = "none"
        if sequence_status == "blocked":
            for item in sequence_result.get("sequence", []):
                call_payload = item.get("call") or {}
                if call_payload.get("status") == "blocked":
                    sequence_gate = str(call_payload.get("gate", "sequence"))
                    break
            sequence_gate = sequence_gate if sequence_gate != "none" else "sequence"

        surface = self.runtime.get_operator_surface(session)
        domain = str(surface.get("domain", "unknown"))
        final_status = "executed" if sequence_status == "executed" else ("blocked" if sequence_status == "blocked" else "failed")
        final_reason = "ok" if final_status == "executed" else "sequence_blocked"
        lineage = self._emit_unified_lineage(
            session,
            status=final_status,
            reason=final_reason,
            domain=domain,
            mission_name=mission_name,
            sequence_name=sequence_name,
            gate=sequence_gate,
        )
        lineage_events = self._collect_lineage_events(session)
        replay = self.replay_from_lineage(lineage_events)

        unified_signatures = {
            "mission": mission_result.get("lineage_signature", "mission_decision:v1"),
            "sequence": sequence_result.get("lineage_signature", "callsequence_decision:v1"),
            "callpack": "callpack_decision:v1",
            "strategy": "strategy_decision:v1",
            "skillpack": "skillpack_decision:v1",
            "unified": self.UNIFIED_SIGNATURE,
        }

        return {
            "status": final_status,
            "reason": final_reason,
            "gate": sequence_gate,
            "mission": mission_name,
            "sequence": sequence_name,
            "mission_result": mission_result,
            "sequence_result": sequence_result,
            "lineage": lineage,
            "lineage_signatures": unified_signatures,
            "lineage_events": lineage_events,
            "replay": replay,
            "observability": {
                "domain": domain,
                "mission": dict(mission_result.get("observability", {})),
                "sequence": dict(sequence_result.get("observability", {})),
                "surface": dict(surface.get("observability", {})) if surface.get("status") == "ready" else {},
            },
            "surface": surface,
        }

from __future__ import annotations

from typing import Any, Dict, List

from phase6_callpacks import OperatorCallPackEngine
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class BaseCallSequencePack:
    sequences: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def decompose_sequence(self, sequence_name: str) -> List[Dict[str, Any]]:
        sequence = self.sequences.get(sequence_name, [])
        return [dict(step) for step in sequence]


class MerchantServiceCallSequencePack(BaseCallSequencePack):
    sequences = {
        "merchant_onboarding_call_sequence": [
            {"goal": "Verify merchant identity", "advance_subflow": "underwriting"},
            {"goal": "Check merchant compliance status", "advance_subflow": "offer"},
        ],
        "merchant_compliance_resolution_sequence": [
            {"goal": "Verify merchant identity", "advance_subflow": "underwriting"},
            {"goal": "Check merchant compliance status"},
        ],
        "merchant_recovery_correction_sequence": [
            {
                "goal": "Perform merchant recovery call",
                "allow_recovery_correction": True,
                "recovery_reason": "sequence_recovery",
                "recovery_goal": "Verify merchant identity",
            }
        ],
    }


class OperatorCardCallSequencePack(BaseCallSequencePack):
    sequences = {
        "operator_card_verification_sequence": [
            {"goal": "Verify operator card", "advance_subflow": "routing"},
            {"goal": "Resolve operator-card compliance block", "advance_subflow": "resolution"},
        ],
        "operator_card_compliance_resolution_sequence": [
            {"goal": "Verify operator card", "advance_subflow": "routing"},
            {"goal": "Resolve operator-card compliance block"},
        ],
    }


class MixedDomainCallSequencePack(BaseCallSequencePack):
    sequences = {
        "cross_domain_sequence": [
            {"goal": "Cross-domain merchant + operator-card call"},
            {"goal": "Domain-switching call with compliance and recovery events"},
        ],
    }


class CallOrchestrationEngine:
    SEQUENCE_SIGNATURE = "callsequence_decision:v1"

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime
        self.callpack_engine = OperatorCallPackEngine(runtime)

    def _emit_sequence_lineage(
        self,
        session: WorkflowSession,
        sequence_name: str,
        step_index: int,
        step: Dict[str, Any],
        call_result: Dict[str, Any],
        correction: bool = False,
    ) -> Dict[str, Any]:
        surface = self.runtime.get_operator_surface(session)
        payload = {
            "signature": self.SEQUENCE_SIGNATURE,
            "scope": "phase6_sequence",
            "sequence": sequence_name,
            "step_index": step_index,
            "goal": step.get("goal", "unknown"),
            "status": call_result.get("status", "unknown"),
            "gate": call_result.get("gate", "none"),
            "domain": surface.get("domain", "unknown"),
            "pack": call_result.get("pack", "unknown"),
            "call_type": call_result.get("call_type", "unknown"),
            "correction": bool(correction),
        }
        self.runtime.emit_event(session, "callsequence_decision", payload)
        return payload

    def execute_sequence(
        self,
        sequence_pack: BaseCallSequencePack,
        session: WorkflowSession,
        sequence_name: str,
        adapter: Any,
    ) -> Dict[str, Any]:
        decomposition = sequence_pack.decompose_sequence(sequence_name)
        if not decomposition:
            return {
                "status": "failed",
                "reason": "sequence_not_found",
                "sequence_name": sequence_name,
                "decomposition": [],
            }

        calls: List[Dict[str, Any]] = []
        blocked_calls = 0
        recovery_corrections = 0
        pruned = False
        sequence_status = "executed"

        for idx, step in enumerate(decomposition):
            goal = str(step.get("goal", "")).strip()
            call_result = self.callpack_engine.execute_call(session, goal, adapter)
            lineage = self._emit_sequence_lineage(session, sequence_name, idx, step, call_result)
            calls.append({"step_index": idx, "goal": goal, "call": call_result, "lineage": lineage})

            if call_result.get("status") == "blocked":
                blocked_calls += 1
                sequence_status = "blocked"
                if call_result.get("gate") == "compliance":
                    pruned = True

                if call_result.get("gate") == "recovery" and step.get("allow_recovery_correction"):
                    recovery_reason = str(step.get("recovery_reason", "sequence_recovery"))
                    recovered = self.runtime.orchestrate_recovery(session, reason=recovery_reason)
                    if recovered.get("status") == "recovered":
                        correction_goal = str(step.get("recovery_goal", "Perform recovery"))
                        correction_result = self.callpack_engine.execute_call(session, correction_goal, adapter)
                        correction_lineage = self._emit_sequence_lineage(
                            session,
                            sequence_name,
                            idx + 1,
                            {"goal": correction_goal},
                            correction_result,
                            correction=True,
                        )
                        calls.append(
                            {
                                "step_index": idx + 1,
                                "goal": correction_goal,
                                "call": correction_result,
                                "lineage": correction_lineage,
                                "correction": True,
                            }
                        )
                        recovery_corrections += 1
                        if correction_result.get("status") == "executed":
                            sequence_status = "executed"
                break

            advance_target = str(step.get("advance_subflow", "")).strip()
            if advance_target:
                advanced = self.runtime.advance_subflow(session, advance_target)
                if advanced.get("status") != "transitioned":
                    sequence_status = "blocked"
                    blocked_calls += 1
                    pruned = advanced.get("reason") == "subflow_compliance_blocked"

        surface = self.runtime.get_operator_surface(session)
        observability = dict(surface.get("observability") or {}) if surface.get("status") == "ready" else {}

        return {
            "status": sequence_status,
            "sequence_name": sequence_name,
            "decomposition": [dict(item) for item in decomposition],
            "sequence": calls,
            "lineage_signature": self.SEQUENCE_SIGNATURE,
            "observability": {
                "status": observability.get("status", "unknown"),
                "domain": surface.get("domain", "unknown"),
                "executed_calls": sum(1 for item in calls if (item.get("call") or {}).get("status") == "executed"),
                "blocked_calls": blocked_calls,
                "recovery_corrections": recovery_corrections,
                "pruned": pruned,
                "compliance": dict(observability.get("compliance", {})),
                "recovery": dict(observability.get("recovery", {})),
            },
            "surface": surface,
        }

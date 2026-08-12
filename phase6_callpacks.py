from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


@dataclass
class CallPackDecision:
    status: str
    reason: str
    call_type: str
    domain: str
    payload: Dict[str, Any]
    observability: Dict[str, Any]
    lineage: Dict[str, Any]


class BaseOperatorCallPack:
    PACK_SIGNATURE = "callpack_decision:v1"
    pack_name = "base"
    supported_domain = "unknown"

    call_type_map: Dict[str, str] = {}

    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime

    def select_call_type(self, goal: str, surface: Dict[str, Any]) -> str:
        normalized = goal.strip().lower()
        if normalized in self.call_type_map:
            return self.call_type_map[normalized]
        if "recovery" in normalized:
            return self.call_type_map.get("perform recovery", "recovery_call")
        if "compliance" in normalized:
            return self.call_type_map.get("check compliance", "compliance_call")
        return self.call_type_map.get("default", "default_call")

    def evaluate_gates(self, session: WorkflowSession, surface: Dict[str, Any]) -> Dict[str, Any]:
        if surface.get("status") != "ready":
            return {"ok": False, "reason": "surface_unavailable", "gate": "precondition"}

        observability = surface.get("observability") or {}
        compliance = observability.get("compliance") or {}
        sequencing = surface.get("sequencing") or {}
        recovery = observability.get("recovery") or {}

        if compliance.get("state") == "blocked":
            return {
                "ok": False,
                "reason": "compliance_blocked",
                "gate": "compliance",
                "missing_flags": list(compliance.get("missing_flags", [])),
                "signature": compliance.get("signature", WorkflowRuntimeEngine.COMPLIANCE_SIGNATURE),
            }

        if observability.get("status") == "failed" and recovery.get("status") != "recovered":
            return {
                "ok": False,
                "reason": "recovery_required",
                "gate": "recovery",
                "signature": recovery.get("signature", "none"),
            }

        if not sequencing.get("current_subflow") or not surface.get("step"):
            return {
                "ok": False,
                "reason": "sequencing_incomplete",
                "gate": "sequencing",
            }

        return {"ok": True, "reason": "ready"}

    def build_payload(self, session: WorkflowSession, surface: Dict[str, Any], call_type: str, goal: str) -> Dict[str, Any]:
        return {
            "signature": self.PACK_SIGNATURE,
            "pack": self.pack_name,
            "domain": surface.get("domain", "unknown"),
            "workflow_id": surface.get("workflow_id", "unknown"),
            "workflow_type": surface.get("workflow_type", "default"),
            "subflow": surface.get("subflow", ""),
            "step": surface.get("step", ""),
            "call_type": call_type,
            "goal": goal,
            "observability": dict(surface.get("observability") or {}),
        }


class MerchantServiceCallPack(BaseOperatorCallPack):
    pack_name = "merchant_service_callpack"
    supported_domain = "merchant_services"
    call_type_map = {
        "verify merchant identity": "merchant_identity_verification",
        "check merchant compliance status": "merchant_compliance_status",
        "perform merchant recovery call": "merchant_recovery_call",
        "perform recovery": "merchant_recovery_call",
        "check compliance": "merchant_compliance_status",
        "default": "merchant_status_call",
    }


class OperatorCardCallPack(BaseOperatorCallPack):
    pack_name = "operator_card_callpack"
    supported_domain = "operator_card_services"
    call_type_map = {
        "verify operator card": "operator_card_verification",
        "resolve operator-card compliance block": "operator_card_compliance_resolution",
        "perform recovery": "operator_card_recovery_call",
        "check compliance": "operator_card_compliance_resolution",
        "default": "operator_card_status_call",
    }


class MixedDomainCallPack(BaseOperatorCallPack):
    pack_name = "mixed_domain_callpack"
    supported_domain = "mixed_domain"
    call_type_map = {
        "cross-domain merchant + operator-card call": "cross_domain_coordination_call",
        "domain-switching call with compliance and recovery events": "cross_domain_resilience_call",
        "perform recovery": "cross_domain_recovery_call",
        "check compliance": "cross_domain_compliance_call",
        "default": "cross_domain_status_call",
    }


class OperatorCallPackEngine:
    def __init__(self, runtime: WorkflowRuntimeEngine) -> None:
        self.runtime = runtime
        self._packs: Dict[str, BaseOperatorCallPack] = {
            "merchant_services": MerchantServiceCallPack(runtime),
            "operator_card_services": OperatorCardCallPack(runtime),
            "mixed_domain": MixedDomainCallPack(runtime),
        }

    def select_pack(self, domain: str) -> BaseOperatorCallPack:
        normalized = str(domain or "").strip()
        if normalized in self._packs:
            return self._packs[normalized]
        return self._packs["mixed_domain"]

    def execute_call(self, session: WorkflowSession, goal: str, adapter: Any) -> Dict[str, Any]:
        surface = self.runtime.get_operator_surface(session)
        domain = str(surface.get("domain", "unknown"))
        pack = self.select_pack(domain)
        call_type = pack.select_call_type(goal, surface)
        gates = pack.evaluate_gates(session, surface)

        if not gates.get("ok"):
            lineage = {
                "signature": BaseOperatorCallPack.PACK_SIGNATURE,
                "scope": "phase6_callpack",
                "pack": pack.pack_name,
                "domain": domain,
                "call_type": call_type,
                "goal": goal,
                "status": "blocked",
                "gate": gates.get("gate", "unknown"),
                "reason": gates.get("reason", "blocked"),
            }
            self.runtime.emit_event(session, "callpack_blocked", lineage)
            return {
                "status": "blocked",
                "reason": gates.get("reason", "blocked"),
                "gate": gates.get("gate", "unknown"),
                "pack": pack.pack_name,
                "call_type": call_type,
                "lineage": lineage,
                "observability": dict(surface.get("observability") or {}),
            }

        payload = pack.build_payload(session, surface, call_type, goal)
        adapter_result = adapter.execute(payload)
        lineage = {
            "signature": BaseOperatorCallPack.PACK_SIGNATURE,
            "scope": "phase6_callpack",
            "pack": pack.pack_name,
            "domain": domain,
            "call_type": call_type,
            "goal": goal,
            "status": "executed",
        }
        self.runtime.emit_event(session, "callpack_executed", lineage)
        return {
            "status": "executed",
            "pack": pack.pack_name,
            "call_type": call_type,
            "payload": payload,
            "adapter_result": adapter_result,
            "lineage": lineage,
            "observability": dict(surface.get("observability") or {}),
        }

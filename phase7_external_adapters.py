from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from phase6_saoc import SupervisionGate


@dataclass
class ExternalAdapterGate:
    supervision: SupervisionGate


@dataclass
class ExternalAdapterResult:
    status: str
    reason: str
    gate: str
    payload: Dict[str, Any]
    lineage: Dict[str, Any]
    observability: Dict[str, Any]
    replay: Dict[str, Any]


class GovernedExternalAdapterBase:
    EXTERNAL_SIGNATURE = "external_call:v1"
    adapter_name = "external_base"
    supported_domain = "unknown"
    external_target = "external_unknown"

    def _domain_matches(self, domain: str) -> bool:
        if self.supported_domain == "mixed_domain":
            return True
        return domain == self.supported_domain

    def _extract_compliance_state(self, unified_result: Dict[str, Any]) -> Dict[str, Any]:
        observability = unified_result.get("observability") or {}
        sequence_obs = observability.get("sequence") or {}
        surface_obs = observability.get("surface") or {}
        compliance = sequence_obs.get("compliance") or surface_obs.get("compliance") or {}
        return dict(compliance)

    def _extract_recovery_state(self, unified_result: Dict[str, Any]) -> Dict[str, Any]:
        observability = unified_result.get("observability") or {}
        sequence_obs = observability.get("sequence") or {}
        surface_obs = observability.get("surface") or {}
        recovery = sequence_obs.get("recovery") or surface_obs.get("recovery") or {}
        return dict(recovery)

    def evaluate_gate(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        if not gate.supervision.approved:
            return {
                "ok": False,
                "reason": "supervision_not_approved",
                "gate": "supervision",
            }

        upstream_status = str(unified_result.get("status", "failed"))
        if upstream_status != "executed":
            return {
                "ok": False,
                "reason": "upstream_gating_failed",
                "gate": str(unified_result.get("gate", "upstream")),
            }

        domain = str(((unified_result.get("surface") or {}).get("domain") or "unknown").strip())
        if not self._domain_matches(domain):
            return {
                "ok": False,
                "reason": "domain_not_supported",
                "gate": "domain",
            }

        compliance = self._extract_compliance_state(unified_result)
        if compliance.get("state") == "blocked":
            return {
                "ok": False,
                "reason": "external_compliance_blocked",
                "gate": "compliance",
                "missing_flags": list(compliance.get("missing_flags", [])),
            }

        surface = unified_result.get("surface") or {}
        surface_obs = (unified_result.get("observability") or {}).get("surface") or {}
        recovery = self._extract_recovery_state(unified_result)
        if surface_obs.get("status") == "failed" and recovery.get("status") != "recovered":
            return {
                "ok": False,
                "reason": "external_recovery_required",
                "gate": "recovery",
            }

        sequencing = surface.get("sequencing") or {}
        if not sequencing.get("current_subflow") or not surface.get("step"):
            return {
                "ok": False,
                "reason": "external_sequencing_incomplete",
                "gate": "sequencing",
            }

        return {"ok": True, "reason": "ready", "gate": "none"}

    def build_payload(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        surface = unified_result.get("surface") or {}
        observability = unified_result.get("observability") or {}
        return {
            "signature": self.EXTERNAL_SIGNATURE,
            "adapter": self.adapter_name,
            "external_target": self.external_target,
            "domain": surface.get("domain", "unknown"),
            "workflow_id": surface.get("workflow_id", "unknown"),
            "workflow_type": surface.get("workflow_type", "default"),
            "subflow": surface.get("subflow", ""),
            "step": surface.get("step", ""),
            "mission": unified_result.get("mission", "unknown"),
            "sequence": unified_result.get("sequence", "unknown"),
            "supervisor_id": gate.supervision.supervisor_id,
            "supervision_mode": gate.supervision.supervision_mode,
            "unified_signature": (unified_result.get("lineage") or {}).get("signature", "unifiedflow_decision:v1"),
            "replay_signature": (unified_result.get("replay") or {}).get("replay_signature", "none"),
            "observability": {
                "mission": dict(observability.get("mission", {})),
                "sequence": dict(observability.get("sequence", {})),
                "surface": dict(observability.get("surface", {})),
            },
        }

    def _build_lineage(self, status: str, reason: str, gate_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "signature": self.EXTERNAL_SIGNATURE,
            "scope": "phase7_external_adapter",
            "adapter": self.adapter_name,
            "status": status,
            "reason": reason,
            "gate": gate_name,
            "domain": payload.get("domain", "unknown"),
            "workflow_id": payload.get("workflow_id", "unknown"),
            "mission": payload.get("mission", "unknown"),
            "sequence": payload.get("sequence", "unknown"),
            "external_target": payload.get("external_target", self.external_target),
        }

    def _build_observability(self, unified_result: Dict[str, Any], status: str, gate_name: str) -> Dict[str, Any]:
        sequence_obs = ((unified_result.get("observability") or {}).get("sequence") or {})
        surface_obs = ((unified_result.get("observability") or {}).get("surface") or {})
        return {
            "status": status,
            "gate": gate_name,
            "domain": (unified_result.get("surface") or {}).get("domain", "unknown"),
            "compliance": dict(self._extract_compliance_state(unified_result)),
            "recovery": dict(self._extract_recovery_state(unified_result)),
            "sequencing": {
                "current_subflow": ((unified_result.get("surface") or {}).get("sequencing") or {}).get("current_subflow"),
                "has_step": bool((unified_result.get("surface") or {}).get("step")),
            },
            "upstream": {
                "status": unified_result.get("status", "unknown"),
                "mission_status": (unified_result.get("mission_result") or {}).get("status", "unknown"),
                "sequence_status": (unified_result.get("sequence_result") or {}).get("status", "unknown"),
                "sequence_executed_calls": sequence_obs.get("executed_calls", 0),
                "surface_status": surface_obs.get("status", "unknown"),
            },
        }

    def execute(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        gate_result = self.evaluate_gate(unified_result, gate)
        payload = self.build_payload(unified_result, gate)
        replay = dict(unified_result.get("replay") or {})

        if not gate_result.get("ok"):
            reason = str(gate_result.get("reason", "blocked"))
            gate_name = str(gate_result.get("gate", "unknown"))
            lineage = self._build_lineage("blocked", reason, gate_name, payload)
            observability = self._build_observability(unified_result, "blocked", gate_name)
            return asdict(
                ExternalAdapterResult(
                    status="blocked",
                    reason=reason,
                    gate=gate_name,
                    payload=payload,
                    lineage=lineage,
                    observability=observability,
                    replay=replay,
                )
            )

        lineage = self._build_lineage("executed", "ok", "none", payload)
        observability = self._build_observability(unified_result, "executed", "none")
        return asdict(
            ExternalAdapterResult(
                status="executed",
                reason="ok",
                gate="none",
                payload=payload,
                lineage=lineage,
                observability=observability,
                replay=replay,
            )
        )


class MerchantServiceExternalAdapter(GovernedExternalAdapterBase):
    adapter_name = "merchant_service_external_adapter"
    supported_domain = "merchant_services"
    external_target = "merchant_service_gateway"

    def build_payload(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        payload = super().build_payload(unified_result, gate)
        payload["integration_channel"] = "merchant_api"
        payload["operation_profile"] = "merchant_services"
        return payload


class OperatorCardExternalAdapter(GovernedExternalAdapterBase):
    adapter_name = "operator_card_external_adapter"
    supported_domain = "operator_card_services"
    external_target = "operator_card_gateway"

    def build_payload(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        payload = super().build_payload(unified_result, gate)
        payload["integration_channel"] = "operator_card_api"
        payload["operation_profile"] = "operator_card_services"
        return payload


class MixedDomainExternalAdapter(GovernedExternalAdapterBase):
    adapter_name = "mixed_domain_external_adapter"
    supported_domain = "mixed_domain"
    external_target = "mixed_domain_gateway"

    def build_payload(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        payload = super().build_payload(unified_result, gate)
        payload["integration_channel"] = "cross_domain_api"
        payload["operation_profile"] = "mixed_domain"
        payload["domains_supported"] = ["merchant_services", "operator_card_services"]
        return payload

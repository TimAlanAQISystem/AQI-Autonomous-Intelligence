from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from phase7_external_adapters import (
    ExternalAdapterGate,
    GovernedExternalAdapterBase,
    MerchantServiceExternalAdapter,
    MixedDomainExternalAdapter,
    OperatorCardExternalAdapter,
)


@dataclass
class ExternalBindingResult:
    status: str
    reason: str
    gate: str
    payload: Dict[str, Any]
    response: Dict[str, Any]
    lineage: Dict[str, Any]
    observability: Dict[str, Any]
    replay: Dict[str, Any]


class GovernedExternalAdapterBindingBase:
    BINDING_SIGNATURE = "external_binding:v1"
    binding_name = "external_binding_base"

    def __init__(self, adapter: GovernedExternalAdapterBase, external_client: Any) -> None:
        self.adapter = adapter
        self.external_client = external_client

    def _normalize_external_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(raw or {})
        return {
            "status": str(payload.get("status", "unknown")),
            "external_ref": str(payload.get("external_ref", "none")),
            "code": str(payload.get("code", "none")),
            "details": dict(payload.get("details", {})) if isinstance(payload.get("details", {}), dict) else {},
        }

    def _build_lineage(self, adapter_lineage: Dict[str, Any], response: Dict[str, Any], status: str) -> Dict[str, Any]:
        return {
            **dict(adapter_lineage or {}),
            "binding_signature": self.BINDING_SIGNATURE,
            "binding": self.binding_name,
            "binding_status": status,
            "external_response_status": response.get("status", "unknown"),
            "external_ref": response.get("external_ref", "none"),
        }

    def _build_observability(self, adapter_observability: Dict[str, Any], response: Dict[str, Any], status: str) -> Dict[str, Any]:
        return {
            **dict(adapter_observability or {}),
            "binding": {
                "signature": self.BINDING_SIGNATURE,
                "name": self.binding_name,
                "status": status,
                "external_response_status": response.get("status", "unknown"),
            },
            "external_response": dict(response),
        }

    def execute_bound(self, unified_result: Dict[str, Any], gate: ExternalAdapterGate) -> Dict[str, Any]:
        adapter_result = self.adapter.execute(unified_result, gate)
        if adapter_result.get("status") != "executed":
            blocked_response = {
                "status": "not_called",
                "external_ref": "none",
                "code": "blocked",
                "details": {},
            }
            blocked_lineage = self._build_lineage(
                adapter_result.get("lineage", {}),
                blocked_response,
                status="blocked",
            )
            blocked_observability = self._build_observability(
                adapter_result.get("observability", {}),
                blocked_response,
                status="blocked",
            )
            return asdict(
                ExternalBindingResult(
                    status="blocked",
                    reason=str(adapter_result.get("reason", "blocked")),
                    gate=str(adapter_result.get("gate", "unknown")),
                    payload=dict(adapter_result.get("payload", {})),
                    response=blocked_response,
                    lineage=blocked_lineage,
                    observability=blocked_observability,
                    replay=dict(adapter_result.get("replay", {})),
                )
            )

        payload = dict(adapter_result.get("payload", {}))
        raw_response = self.external_client.execute(payload)
        normalized_response = self._normalize_external_response(raw_response)
        lineage = self._build_lineage(adapter_result.get("lineage", {}), normalized_response, status="executed")
        observability = self._build_observability(adapter_result.get("observability", {}), normalized_response, status="executed")
        return asdict(
            ExternalBindingResult(
                status="executed",
                reason="ok",
                gate="none",
                payload=payload,
                response=normalized_response,
                lineage=lineage,
                observability=observability,
                replay=dict(adapter_result.get("replay", {})),
            )
        )


class MerchantServiceExternalAdapterBinding(GovernedExternalAdapterBindingBase):
    binding_name = "merchant_service_external_binding"

    def __init__(self, external_client: Any) -> None:
        super().__init__(MerchantServiceExternalAdapter(), external_client)


class OperatorCardExternalAdapterBinding(GovernedExternalAdapterBindingBase):
    binding_name = "operator_card_external_binding"

    def __init__(self, external_client: Any) -> None:
        super().__init__(OperatorCardExternalAdapter(), external_client)


class MixedDomainExternalAdapterBinding(GovernedExternalAdapterBindingBase):
    binding_name = "mixed_domain_external_binding"

    def __init__(self, external_client: Any) -> None:
        super().__init__(MixedDomainExternalAdapter(), external_client)

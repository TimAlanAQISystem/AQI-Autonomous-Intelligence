from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict

from phase7_bindings import (
    MerchantServiceExternalAdapterBinding,
    MixedDomainExternalAdapterBinding,
    OperatorCardExternalAdapterBinding,
)
from phase7_external_adapters import ExternalAdapterGate


@dataclass
class GovernedTransportEnvelope:
    timeout_s: float = 2.0
    max_retries: int = 1
    idempotency_key: str = ""
    correlation_id: str = ""
    max_payload_bytes: int = 16384
    max_response_bytes: int = 16384
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class GovernedTransportResult:
    status: str
    reason: str
    gate: str
    attempts: int
    payload: Dict[str, Any]
    response: Dict[str, Any]
    lineage: Dict[str, Any]
    observability: Dict[str, Any]
    replay: Dict[str, Any]


class GovernedExternalTransportBase:
    TRANSPORT_SIGNATURE = "external_transport:v1"
    transport_name = "external_transport_base"

    def __init__(self, binding: Any, transport_client: Any) -> None:
        self.binding = binding
        self.transport_client = transport_client
        self._idempotency_seen: set[str] = set()

    def _size_bytes(self, payload: Dict[str, Any]) -> int:
        return len(json.dumps(payload, sort_keys=True, default=str).encode("utf-8"))

    def _normalize_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        body = dict(raw or {})
        details = body.get("details", {})
        if not isinstance(details, dict):
            details = {}
        return {
            "status": str(body.get("status", "unknown")),
            "external_ref": str(body.get("external_ref", "none")),
            "code": str(body.get("code", "none")),
            "timeout": bool(body.get("timeout", False)),
            "details": details,
        }

    def _build_transport_lineage(
        self,
        binding_result: Dict[str, Any],
        envelope: GovernedTransportEnvelope,
        status: str,
        reason: str,
        gate: str,
        attempts: int,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        binding_lineage = dict(binding_result.get("lineage", {}))
        binding_lineage.update(
            {
                "transport_signature": self.TRANSPORT_SIGNATURE,
                "transport": self.transport_name,
                "transport_status": status,
                "transport_reason": reason,
                "transport_gate": gate,
                "transport_attempts": attempts,
                "idempotency_key": envelope.idempotency_key,
                "correlation_id": envelope.correlation_id,
                "transport_response_status": response.get("status", "unknown"),
            }
        )
        return binding_lineage

    def _build_transport_observability(
        self,
        binding_result: Dict[str, Any],
        envelope: GovernedTransportEnvelope,
        status: str,
        gate: str,
        attempts: int,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        binding_obs = dict(binding_result.get("observability", {}))
        binding_obs["transport"] = {
            "signature": self.TRANSPORT_SIGNATURE,
            "name": self.transport_name,
            "status": status,
            "gate": gate,
            "attempts": attempts,
            "timeout_s": envelope.timeout_s,
            "max_retries": envelope.max_retries,
            "idempotency_key": envelope.idempotency_key,
            "correlation_id": envelope.correlation_id,
            "response_status": response.get("status", "unknown"),
            "response_timeout": bool(response.get("timeout", False)),
        }
        return binding_obs

    def _validate_envelope(self, envelope: GovernedTransportEnvelope) -> Dict[str, Any]:
        if envelope.timeout_s <= 0:
            return {"ok": False, "reason": "invalid_timeout", "gate": "transport_envelope"}
        if envelope.max_retries < 0:
            return {"ok": False, "reason": "invalid_retries", "gate": "transport_envelope"}
        if envelope.max_payload_bytes <= 0 or envelope.max_response_bytes <= 0:
            return {"ok": False, "reason": "invalid_size_bounds", "gate": "transport_envelope"}
        if not envelope.idempotency_key.strip():
            return {"ok": False, "reason": "missing_idempotency_key", "gate": "transport_envelope"}
        if not envelope.correlation_id.strip():
            return {"ok": False, "reason": "missing_correlation_id", "gate": "transport_envelope"}
        return {"ok": True, "reason": "valid", "gate": "none"}

    def _retry_allowed(self, binding_result: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        if not response.get("timeout", False) and response.get("status") != "timeout":
            return {"ok": False, "reason": "not_retriable"}

        sequencing = (binding_result.get("observability") or {}).get("sequencing") or {}
        if not sequencing.get("has_step", False):
            return {"ok": False, "reason": "sequencing_retry_suppressed"}

        recovery = (binding_result.get("observability") or {}).get("recovery") or {}
        if recovery.get("status") == "failed" or recovery.get("state") in {"recovery_required", "failed"}:
            return {"ok": False, "reason": "recovery_retry_blocked"}

        return {"ok": True, "reason": "retry_allowed"}

    def execute_transport(
        self,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
    ) -> Dict[str, Any]:
        if not envelope.idempotency_key:
            envelope.idempotency_key = f"idem-{uuid.uuid4().hex}"
        if not envelope.correlation_id:
            envelope.correlation_id = f"corr-{uuid.uuid4().hex}"

        envelope_check = self._validate_envelope(envelope)
        empty_response = {"status": "not_called", "external_ref": "none", "code": "blocked", "timeout": False, "details": {}}
        if not envelope_check.get("ok"):
            lineage = {
                "transport_signature": self.TRANSPORT_SIGNATURE,
                "transport": self.transport_name,
                "transport_status": "blocked",
                "transport_reason": envelope_check.get("reason", "transport_envelope_invalid"),
                "transport_gate": envelope_check.get("gate", "transport_envelope"),
                "idempotency_key": envelope.idempotency_key,
                "correlation_id": envelope.correlation_id,
            }
            observability = {
                "transport": {
                    "signature": self.TRANSPORT_SIGNATURE,
                    "name": self.transport_name,
                    "status": "blocked",
                    "gate": envelope_check.get("gate", "transport_envelope"),
                    "reason": envelope_check.get("reason", "transport_envelope_invalid"),
                }
            }
            return asdict(
                GovernedTransportResult(
                    status="blocked",
                    reason=str(envelope_check.get("reason", "transport_envelope_invalid")),
                    gate=str(envelope_check.get("gate", "transport_envelope")),
                    attempts=0,
                    payload={},
                    response=empty_response,
                    lineage=lineage,
                    observability=observability,
                    replay=dict(unified_result.get("replay", {})),
                )
            )

        adapter_result = self.binding.adapter.execute(unified_result, gate)
        payload = dict(adapter_result.get("payload", {}))
        if adapter_result.get("status") != "executed":
            lineage = self._build_transport_lineage(adapter_result, envelope, "blocked", str(adapter_result.get("reason", "blocked")), str(adapter_result.get("gate", "unknown")), 0, empty_response)
            observability = self._build_transport_observability(adapter_result, envelope, "blocked", str(adapter_result.get("gate", "unknown")), 0, empty_response)
            return asdict(
                GovernedTransportResult(
                    status="blocked",
                    reason=str(adapter_result.get("reason", "blocked")),
                    gate=str(adapter_result.get("gate", "unknown")),
                    attempts=0,
                    payload=payload,
                    response=empty_response,
                    lineage=lineage,
                    observability=observability,
                    replay=dict(adapter_result.get("replay", {})),
                )
            )

        payload_size = self._size_bytes(payload)
        if payload_size > envelope.max_payload_bytes:
            lineage = self._build_transport_lineage(adapter_result, envelope, "blocked", "payload_too_large", "transport_envelope", 0, empty_response)
            observability = self._build_transport_observability(adapter_result, envelope, "blocked", "transport_envelope", 0, empty_response)
            observability["transport"]["payload_size"] = payload_size
            return asdict(
                GovernedTransportResult(
                    status="blocked",
                    reason="payload_too_large",
                    gate="transport_envelope",
                    attempts=0,
                    payload=payload,
                    response=empty_response,
                    lineage=lineage,
                    observability=observability,
                    replay=dict(adapter_result.get("replay", {})),
                )
            )

        if envelope.idempotency_key in self._idempotency_seen:
            lineage = self._build_transport_lineage(adapter_result, envelope, "blocked", "duplicate_idempotency_key", "idempotency", 0, empty_response)
            observability = self._build_transport_observability(adapter_result, envelope, "blocked", "idempotency", 0, empty_response)
            return asdict(
                GovernedTransportResult(
                    status="blocked",
                    reason="duplicate_idempotency_key",
                    gate="idempotency",
                    attempts=0,
                    payload=payload,
                    response=empty_response,
                    lineage=lineage,
                    observability=observability,
                    replay=dict(adapter_result.get("replay", {})),
                )
            )
        self._idempotency_seen.add(envelope.idempotency_key)

        headers = {
            "X-Idempotency-Key": envelope.idempotency_key,
            "X-Correlation-Id": envelope.correlation_id,
            "X-Governance-Signature": str((adapter_result.get("lineage") or {}).get("signature", "external_call:v1")),
            "X-Compliance-Safe": "true",
        }
        headers.update({str(k): str(v) for k, v in envelope.headers.items()})

        attempts = 0
        final_response = empty_response
        final_reason = "timeout"
        final_gate = "transport"
        while attempts <= envelope.max_retries:
            attempts += 1
            raw = self.transport_client.execute(payload, headers=headers, timeout_s=envelope.timeout_s, attempt=attempts)
            normalized = self._normalize_response(raw)
            response_size = self._size_bytes(normalized)
            if response_size > envelope.max_response_bytes:
                final_response = {"status": "oversize", "external_ref": normalized.get("external_ref", "none"), "code": "response_too_large", "timeout": False, "details": {}}
                final_reason = "response_too_large"
                final_gate = "transport_envelope"
                break

            retry_gate = self._retry_allowed(adapter_result, normalized)
            if retry_gate.get("ok") and attempts <= envelope.max_retries:
                final_response = normalized
                continue

            final_response = normalized
            if normalized.get("timeout", False) or normalized.get("status") == "timeout":
                final_reason = str(retry_gate.get("reason", "timeout"))
                final_gate = "transport"
            else:
                final_reason = "ok"
                final_gate = "none"
            break

        status = "executed" if final_reason == "ok" else "failed"
        lineage = self._build_transport_lineage(adapter_result, envelope, status, final_reason, final_gate, attempts, final_response)
        observability = self._build_transport_observability(adapter_result, envelope, status, final_gate, attempts, final_response)
        observability["transport"]["headers"] = dict(headers)
        return asdict(
            GovernedTransportResult(
                status=status,
                reason=final_reason,
                gate=final_gate,
                attempts=attempts,
                payload=payload,
                response=final_response,
                lineage=lineage,
                observability=observability,
                replay=dict(adapter_result.get("replay", {})),
            )
        )


class MerchantServiceTransportExecutor(GovernedExternalTransportBase):
    transport_name = "merchant_service_transport"

    def __init__(self, transport_client: Any) -> None:
        super().__init__(MerchantServiceExternalAdapterBinding(transport_client), transport_client)


class OperatorCardTransportExecutor(GovernedExternalTransportBase):
    transport_name = "operator_card_transport"

    def __init__(self, transport_client: Any) -> None:
        super().__init__(OperatorCardExternalAdapterBinding(transport_client), transport_client)


class MixedDomainTransportExecutor(GovernedExternalTransportBase):
    transport_name = "mixed_domain_transport"

    def __init__(self, transport_client: Any) -> None:
        super().__init__(MixedDomainExternalAdapterBinding(transport_client), transport_client)

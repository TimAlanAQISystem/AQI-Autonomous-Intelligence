from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from phase7_external_adapters import ExternalAdapterGate
from phase7_transport import GovernedTransportEnvelope


@dataclass
class DestinationGovernanceProfile:
    destination_id: str
    allowlist: List[str] = field(default_factory=list)
    denylist: List[str] = field(default_factory=list)
    required_auth_posture: str = "supervised_token"
    required_transport: str = ""
    max_payload_bytes: int = 16384
    max_response_bytes: int = 16384
    max_retry_count: int = 1
    max_timeout_s: float = 2.0
    compliance_domain: str = "generic"
    risk_domain: str = "generic"
    lineage_domain: str = "generic"
    risk_threshold: float = 0.5


class ExternalPolicyRiskEngine:
    POLICY_SIGNATURE = "external_policy:v1"
    RISK_SIGNATURE = "external_risk:v1"

    def _policy_lineage(
        self,
        profile: DestinationGovernanceProfile,
        status: str,
        reason: str,
        gate: str,
        destination: str,
    ) -> Dict[str, Any]:
        return {
            "signature": self.POLICY_SIGNATURE,
            "scope": "phase7_policy",
            "status": status,
            "reason": reason,
            "gate": gate,
            "destination": destination,
            "destination_profile": profile.destination_id,
            "lineage_domain": profile.lineage_domain,
            "compliance_domain": profile.compliance_domain,
        }

    def _risk_lineage(
        self,
        profile: DestinationGovernanceProfile,
        status: str,
        reason: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        return {
            "signature": self.RISK_SIGNATURE,
            "scope": "phase7_policy_risk",
            "status": status,
            "reason": reason,
            "risk_score": float(risk_score),
            "risk_threshold": float(profile.risk_threshold),
            "risk_domain": profile.risk_domain,
        }

    def _enforce_destination(self, profile: DestinationGovernanceProfile, destination: str) -> Dict[str, Any]:
        if destination in set(profile.denylist):
            return {"ok": False, "reason": "destination_denied", "gate": "policy_destination"}
        if profile.allowlist and destination not in set(profile.allowlist):
            return {"ok": False, "reason": "destination_not_allowlisted", "gate": "policy_destination"}
        return {"ok": True, "reason": "destination_allowed", "gate": "none"}

    def _enforce_auth(self, profile: DestinationGovernanceProfile, auth_posture: str) -> Dict[str, Any]:
        if str(auth_posture or "").strip() != str(profile.required_auth_posture or "").strip():
            return {"ok": False, "reason": "auth_posture_mismatch", "gate": "policy_auth"}
        return {"ok": True, "reason": "auth_ok", "gate": "none"}

    def _enforce_risk(self, profile: DestinationGovernanceProfile, risk_score: float) -> Dict[str, Any]:
        if float(risk_score) > float(profile.risk_threshold):
            return {"ok": False, "reason": "risk_threshold_exceeded", "gate": "policy_risk"}
        return {"ok": True, "reason": "risk_ok", "gate": "none"}

    def _enforce_envelope(
        self,
        profile: DestinationGovernanceProfile,
        envelope: GovernedTransportEnvelope,
        transport_name: str,
    ) -> Dict[str, Any]:
        if profile.required_transport and profile.required_transport != transport_name:
            return {"ok": False, "reason": "transport_profile_mismatch", "gate": "policy_envelope"}
        if envelope.max_payload_bytes > profile.max_payload_bytes:
            return {"ok": False, "reason": "payload_bound_exceeds_profile", "gate": "policy_envelope"}
        if envelope.max_response_bytes > profile.max_response_bytes:
            return {"ok": False, "reason": "response_bound_exceeds_profile", "gate": "policy_envelope"}
        if envelope.max_retries > profile.max_retry_count:
            return {"ok": False, "reason": "retry_bound_exceeds_profile", "gate": "policy_envelope"}
        if envelope.timeout_s > profile.max_timeout_s:
            return {"ok": False, "reason": "timeout_bound_exceeds_profile", "gate": "policy_envelope"}
        return {"ok": True, "reason": "envelope_ok", "gate": "none"}

    def execute_policy(
        self,
        *,
        transport_executor: Any,
        unified_result: Dict[str, Any],
        gate: ExternalAdapterGate,
        envelope: GovernedTransportEnvelope,
        profile: DestinationGovernanceProfile,
        destination: str,
        auth_posture: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        destination_check = self._enforce_destination(profile, destination)
        if not destination_check["ok"]:
            policy_lineage = self._policy_lineage(profile, "blocked", destination_check["reason"], destination_check["gate"], destination)
            risk_lineage = self._risk_lineage(profile, "not_evaluated", "destination_blocked", risk_score)
            return {
                "status": "blocked",
                "reason": destination_check["reason"],
                "gate": destination_check["gate"],
                "policy_lineage": policy_lineage,
                "risk_lineage": risk_lineage,
                "observability": {
                    "policy": {"status": "blocked", "gate": destination_check["gate"], "destination": destination},
                    "risk": {"status": "not_evaluated", "risk_score": risk_score},
                },
                "replay": dict(unified_result.get("replay", {})),
            }

        auth_check = self._enforce_auth(profile, auth_posture)
        if not auth_check["ok"]:
            policy_lineage = self._policy_lineage(profile, "blocked", auth_check["reason"], auth_check["gate"], destination)
            risk_lineage = self._risk_lineage(profile, "not_evaluated", "auth_blocked", risk_score)
            return {
                "status": "blocked",
                "reason": auth_check["reason"],
                "gate": auth_check["gate"],
                "policy_lineage": policy_lineage,
                "risk_lineage": risk_lineage,
                "observability": {
                    "policy": {"status": "blocked", "gate": auth_check["gate"], "destination": destination},
                    "risk": {"status": "not_evaluated", "risk_score": risk_score},
                },
                "replay": dict(unified_result.get("replay", {})),
            }

        risk_check = self._enforce_risk(profile, risk_score)
        if not risk_check["ok"]:
            policy_lineage = self._policy_lineage(profile, "blocked", risk_check["reason"], risk_check["gate"], destination)
            risk_lineage = self._risk_lineage(profile, "blocked", risk_check["reason"], risk_score)
            return {
                "status": "blocked",
                "reason": risk_check["reason"],
                "gate": risk_check["gate"],
                "policy_lineage": policy_lineage,
                "risk_lineage": risk_lineage,
                "observability": {
                    "policy": {"status": "blocked", "gate": risk_check["gate"], "destination": destination},
                    "risk": {"status": "blocked", "risk_score": risk_score},
                },
                "replay": dict(unified_result.get("replay", {})),
            }

        envelope_check = self._enforce_envelope(profile, envelope, getattr(transport_executor, "transport_name", ""))
        if not envelope_check["ok"]:
            policy_lineage = self._policy_lineage(profile, "blocked", envelope_check["reason"], envelope_check["gate"], destination)
            risk_lineage = self._risk_lineage(profile, "allowed", "risk_ok", risk_score)
            return {
                "status": "blocked",
                "reason": envelope_check["reason"],
                "gate": envelope_check["gate"],
                "policy_lineage": policy_lineage,
                "risk_lineage": risk_lineage,
                "observability": {
                    "policy": {"status": "blocked", "gate": envelope_check["gate"], "destination": destination},
                    "risk": {"status": "allowed", "risk_score": risk_score},
                },
                "replay": dict(unified_result.get("replay", {})),
            }

        transport_result = transport_executor.execute_transport(unified_result, gate, envelope)
        status = "executed" if transport_result.get("status") == "executed" else "blocked"
        reason = "ok" if status == "executed" else str(transport_result.get("reason", "transport_blocked"))
        gate_name = "none" if status == "executed" else str(transport_result.get("gate", "transport"))
        policy_lineage = self._policy_lineage(profile, status, reason, gate_name, destination)
        risk_lineage = self._risk_lineage(profile, "allowed", "risk_ok", risk_score)

        return {
            "status": status,
            "reason": reason,
            "gate": gate_name,
            "policy_lineage": policy_lineage,
            "risk_lineage": risk_lineage,
            "transport_result": transport_result,
            "observability": {
                "policy": {
                    "status": status,
                    "gate": gate_name,
                    "destination": destination,
                    "auth_posture": auth_posture,
                    "profile": asdict(profile),
                },
                "risk": {
                    "status": "allowed",
                    "risk_score": risk_score,
                    "risk_threshold": profile.risk_threshold,
                    "risk_domain": profile.risk_domain,
                },
                "transport": dict((transport_result.get("observability") or {}).get("transport", {})),
            },
            "replay": dict(unified_result.get("replay", {})),
        }

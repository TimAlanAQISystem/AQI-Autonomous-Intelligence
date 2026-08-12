from __future__ import annotations

import pytest

from phase5_missions import MerchantServiceMissionPack, MixedDomainMissionPack, OperatorCardMissionPack
from phase6_saoc import SupervisionGate
from phase6_sequences import MerchantServiceCallSequencePack, MixedDomainCallSequencePack, OperatorCardCallSequencePack
from phase6_unifiedflow import UnifiedSupervisedOperatorFlowEngine
from phase7_external_adapters import ExternalAdapterGate
from phase7_policy import DestinationGovernanceProfile
from phase7_transport import (
    GovernedTransportEnvelope,
    MerchantServiceTransportExecutor,
    MixedDomainTransportExecutor,
    OperatorCardTransportExecutor,
)
from phase8_deployment import DeploymentRollbackGate
from phase9_commands import MerchantServiceCommandSurface, MixedDomainCommandSurface, OperatorCardCommandSurface
from phase9_escalation import (
    OperatorArbitrationEngine,
    OperatorArbitrationRules,
    OperatorAuthorityProfile,
    OperatorEscalationEngine,
    OperatorEscalationRules,
)
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class _FakeUnifiedCallAdapter:
    def execute(self, payload: dict) -> dict:
        return {"status": "ok", "external_ref": "escalation-unified"}


class _FakeTransportClient:
    def __init__(self, status: str = "accepted") -> None:
        self.status = status

    def execute(self, payload: dict, headers: dict, timeout_s: float, attempt: int) -> dict:
        return {
            "status": self.status,
            "external_ref": "escalation-external",
            "code": "200",
            "timeout": False,
            "details": {},
        }


class _NoAdvanceMerchantMissionPack(MerchantServiceMissionPack):
    missions = {"no_advance": [{"goal": "complete_onboarding", "max_steps": 0}]}


class _NoAdvanceOperatorMissionPack(OperatorCardMissionPack):
    missions = {"no_advance": [{"goal": "resolve_escalation", "max_steps": 0}]}


def _merchant_pack() -> dict:
    return {
        "id": "merchant_services_pack",
        "domain": "merchant_services",
        "workflow_types": {
            "onboarding": {
                "id": "merchant_onboarding",
                "entry_subflow": "qualification",
                "subflows": {
                    "qualification": {"entry_step": "collect_profile", "next": ["underwriting"]},
                    "underwriting": {"entry_step": "risk_review", "next": ["offer"]},
                    "offer": {"entry_step": "present_offer", "next": []},
                },
                "compliance": {"subflows": {"underwriting": {"required": ["kyc_verified"]}}},
                "recovery": {"subflows": {"underwriting": {"fallback_subflow": "qualification"}}},
                "operator_cards": {
                    "qualification": {"card_id": "merchant.qual", "title": "Merchant Qualification", "controls": ["collect_profile"]},
                    "underwriting": {"card_id": "merchant.underwriting", "title": "Merchant Underwriting", "controls": ["review_risk"]},
                    "offer": {"card_id": "merchant.offer", "title": "Merchant Offer", "controls": ["present_offer"]},
                },
                "steps": {
                    "collect_profile": {"action": "collect_profile", "next": "risk_review"},
                    "risk_review": {"action": "review_risk", "next": "present_offer"},
                    "present_offer": {"action": "present_offer", "next": None},
                },
            }
        },
    }


def _operator_card_pack() -> dict:
    return {
        "id": "operator_card_pack",
        "domain": "operator_card_services",
        "workflow_types": {
            "escalation": {
                "id": "operator_escalation",
                "entry_subflow": "intake",
                "subflows": {
                    "intake": {"entry_step": "collect_signal", "next": ["routing"]},
                    "routing": {"entry_step": "route_decision", "next": ["resolution"]},
                    "resolution": {"entry_step": "close_loop", "next": []},
                },
                "compliance": {"subflows": {"routing": {"required": ["escalation_authorized"]}}},
                "recovery": {"subflows": {"routing": {"fallback_subflow": "intake"}}},
                "operator_cards": {
                    "intake": {"card_id": "operator.intake", "title": "Operator Intake", "controls": ["collect_signal"]},
                    "routing": {"card_id": "operator.routing", "title": "Operator Routing", "controls": ["route_decision"]},
                    "resolution": {"card_id": "operator.resolution", "title": "Operator Resolution", "controls": ["close_loop"]},
                },
                "steps": {
                    "collect_signal": {"action": "collect_signal", "next": "route_decision"},
                    "route_decision": {"action": "route_decision", "next": "close_loop"},
                    "close_loop": {"action": "close_loop", "next": None},
                },
            }
        },
    }


def _run_unified(
    workflow_id: str,
    workflow_pack: dict,
    workflow_type: str,
    flags: dict,
    mission_pack: object,
    mission_name: str,
    sequence_pack: object,
    sequence_name: str,
) -> dict:
    runtime = WorkflowRuntimeEngine(max_concurrent_sessions=2, max_queue_depth=4)
    runtime.register_workflow(workflow_id, workflow_pack)
    session = WorkflowSession(session_id=f"phase9-escalation-{workflow_id}", compliance_flags=flags)
    runtime.start_workflow(session, workflow_id, workflow_type=workflow_type)
    engine = UnifiedSupervisedOperatorFlowEngine(runtime)
    return engine.execute_unified_flow(
        session,
        mission_pack(runtime),
        mission_name,
        sequence_pack(runtime),
        sequence_name,
        SupervisionGate(approved=True, supervisor_id="sup-escalation"),
        _FakeUnifiedCallAdapter(),
    )


def _base_inputs(unified: dict, policy_profile: DestinationGovernanceProfile, destination: str) -> dict:
    return {
        "unified_result": unified,
        "gate": ExternalAdapterGate(supervision=SupervisionGate(approved=True, supervisor_id="sup-escalation")),
        "envelope": GovernedTransportEnvelope(timeout_s=0.4, max_retries=1, idempotency_key="idem-escalation", correlation_id="corr-escalation"),
        "policy_profile": policy_profile,
        "destination": destination,
        "auth_posture": "mtls_token",
        "risk_score": 0.2,
        "rollback_gate": DeploymentRollbackGate(enabled=True, mode="safe"),
        "metrics": {"health_score": 0.95, "anomaly_score": 0.05},
        "deployment_state": {
            "activation": "active",
            "rollout": "full",
            "monitoring": "healthy",
            "intervention": "ready",
        },
    }


def _operators() -> tuple[OperatorAuthorityProfile, OperatorAuthorityProfile, OperatorAuthorityProfile]:
    lead = OperatorAuthorityProfile(
        operator_id="lead_ops",
        supervision_level="strict",
        allowed_commands=["start", "pause", "resume", "drain", "rollback", "recover", "inspect", "replay", "status"],
        rollback_authority=True,
        recovery_authority=True,
        escalation_tier="quorum",
        arbitration_priority=100,
    )
    assistant = OperatorAuthorityProfile(
        operator_id="assistant_ops",
        supervision_level="strict",
        allowed_commands=["start", "pause", "resume", "rollback", "inspect", "status"],
        rollback_authority=False,
        recovery_authority=False,
        escalation_tier="single",
        arbitration_priority=40,
    )
    observer = OperatorAuthorityProfile(
        operator_id="observer_ops",
        supervision_level="lenient",
        allowed_commands=["status", "inspect"],
        rollback_authority=False,
        recovery_authority=False,
        escalation_tier="single",
        arbitration_priority=10,
    )
    return lead, assistant, observer


class TestOperatorAuthorityProfiles:
    def test_authority_enforcement_blocks_unauthorized_rollback(self) -> None:
        unified = _run_unified(
            "merchant_services_pack",
            _merchant_pack(),
            "onboarding",
            {"kyc_verified": True},
            _NoAdvanceMerchantMissionPack,
            "no_advance",
            MerchantServiceCallSequencePack,
            "merchant_onboarding_call_sequence",
        )
        lead, assistant, _ = _operators()
        engine = OperatorEscalationEngine(
            escalation_rules=OperatorEscalationRules(),
            arbitration_rules=OperatorArbitrationRules(),
            arbitration_engine=OperatorArbitrationEngine(),
        )
        transport = MerchantServiceTransportExecutor(_FakeTransportClient())
        profile = MerchantServiceCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="merchant-prod",
            allowlist=["merchant_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="merchant_service_transport",
            risk_threshold=0.9,
            lineage_domain="merchant",
        )

        blocked = engine.execute_operator_command(
            action="rollback",
            operator=assistant,
            escalation_chain=[lead.operator_id],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "merchant_gateway_prod_a"),
        )

        assert blocked["status"] == "blocked"
        assert blocked["reason"] == "operator_lacks_rollback_authority"
        assert blocked["lineage"]["signature"] == "operator_command:v2"


class TestOperatorEscalationRules:
    def test_quorum_escalation_required_for_rollback(self) -> None:
        unified = _run_unified(
            "operator_card_pack",
            _operator_card_pack(),
            "escalation",
            {"escalation_authorized": True},
            _NoAdvanceOperatorMissionPack,
            "no_advance",
            OperatorCardCallSequencePack,
            "operator_card_verification_sequence",
        )
        lead, _, _ = _operators()
        engine = OperatorEscalationEngine(
            escalation_rules=OperatorEscalationRules(command_tiers={"rollback": "quorum"}),
            arbitration_rules=OperatorArbitrationRules(),
            arbitration_engine=OperatorArbitrationEngine(),
        )
        transport = OperatorCardTransportExecutor(_FakeTransportClient())
        profile = OperatorCardCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="operator-prod",
            allowlist=["operator_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="operator_card_transport",
            risk_threshold=0.8,
            lineage_domain="operator",
        )

        blocked = engine.execute_operator_command(
            action="rollback",
            operator=lead,
            escalation_chain=["ops_a"],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "operator_gateway_prod_a"),
        )
        allowed = engine.execute_operator_command(
            action="rollback",
            operator=lead,
            escalation_chain=["ops_a", "ops_b"],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "operator_gateway_prod_a"),
        )

        assert blocked["status"] == "blocked"
        assert blocked["reason"] == "escalation_quorum_required"
        assert allowed["status"] == "executed"
        assert allowed["command_result"]["intervention"]["state"] == "rolled_back"


class TestOperatorArbitrationRules:
    def test_conflicting_commands_resolved_by_priority(self) -> None:
        unified = _run_unified(
            "merchant_services_pack",
            _merchant_pack(),
            "onboarding",
            {"kyc_verified": True},
            _NoAdvanceMerchantMissionPack,
            "no_advance",
            MerchantServiceCallSequencePack,
            "merchant_onboarding_call_sequence",
        )
        lead, assistant, _ = _operators()
        engine = OperatorEscalationEngine(
            escalation_rules=OperatorEscalationRules(),
            arbitration_rules=OperatorArbitrationRules(conflicts={"pause": {"resume"}, "rollback": {"start"}}),
            arbitration_engine=OperatorArbitrationEngine(),
        )
        transport = MerchantServiceTransportExecutor(_FakeTransportClient())
        profile = MerchantServiceCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="merchant-prod",
            allowlist=["merchant_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="merchant_service_transport",
            risk_threshold=0.9,
            lineage_domain="merchant",
        )

        blocked = engine.execute_operator_command(
            action="resume",
            operator=assistant,
            escalation_chain=[lead.operator_id],
            conflicting_command={"action": "pause", "operator": lead},
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "merchant_gateway_prod_a"),
        )
        allowed = engine.execute_operator_command(
            action="pause",
            operator=lead,
            escalation_chain=[assistant.operator_id],
            conflicting_command={"action": "resume", "operator": assistant},
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "merchant_gateway_prod_a"),
        )

        assert blocked["status"] == "blocked"
        assert blocked["reason"] == "arbitration_lost"
        assert blocked["arbitration"]["winner_operator_id"] == lead.operator_id
        assert allowed["status"] == "executed"
        assert allowed["arbitration"]["winner_operator_id"] == lead.operator_id


class TestMultiOperatorLineage:
    @pytest.mark.parametrize(
        "workflow_id,pack,workflow_type,flags,expected_domain",
        [
            ("merchant_services_pack", _merchant_pack(), "onboarding", {"kyc_verified": True}, "merchant_services"),
            (
                "operator_card_pack",
                _operator_card_pack(),
                "escalation",
                {"escalation_authorized": True},
                "operator_card_services",
            ),
        ],
    )
    def test_lineage_v2_and_replay_continuity_cross_domain(
        self,
        workflow_id: str,
        pack: dict,
        workflow_type: str,
        flags: dict,
        expected_domain: str,
    ) -> None:
        unified = _run_unified(
            workflow_id,
            pack,
            workflow_type,
            flags,
            MixedDomainMissionPack,
            "cross_domain_progressive_mission",
            MixedDomainCallSequencePack,
            "cross_domain_sequence",
        )
        lead, _, _ = _operators()
        engine = OperatorEscalationEngine(
            escalation_rules=OperatorEscalationRules(),
            arbitration_rules=OperatorArbitrationRules(),
            arbitration_engine=OperatorArbitrationEngine(),
        )
        transport = MixedDomainTransportExecutor(_FakeTransportClient())
        profile = MixedDomainCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="mixed-prod",
            allowlist=["mixed_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="mixed_domain_transport",
            risk_threshold=0.9,
            lineage_domain="mixed_domain",
            risk_domain="mixed_domain",
        )

        result = engine.execute_operator_command(
            action="status",
            operator=lead,
            escalation_chain=["ops_a"],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "mixed_gateway_prod_a"),
        )

        assert result["status"] == "executed"
        assert result["command_result"]["domain"] == expected_domain
        assert result["lineage"]["signature"] == "operator_command:v2"
        assert result["lineage"]["operator_id"] == lead.operator_id
        assert result["lineage"]["authority_signature"] == f"authority:{lead.operator_id}:{lead.supervision_level}"
        assert result["replay"] == unified["replay"]

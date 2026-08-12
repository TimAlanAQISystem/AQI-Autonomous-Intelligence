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
from phase8_activation import MerchantServiceActivationSurface, MixedDomainActivationSurface, OperatorCardActivationSurface
from phase8_deployment import DeploymentRollbackGate
from phase8_monitoring import MerchantServiceMonitoringSurface, MixedDomainMonitoringSurface, OperatorCardMonitoringSurface
from phase8_rollout import MerchantServiceRolloutSurface, MixedDomainRolloutSurface, OperatorCardRolloutSurface
from phase9_commands import MerchantServiceCommandSurface, MixedDomainCommandSurface, OperatorCardCommandSurface, OperatorCommandEngine
from workflow_runtime_engine import WorkflowRuntimeEngine, WorkflowSession


class _FakeUnifiedCallAdapter:
    def execute(self, payload: dict) -> dict:
        return {"status": "ok", "external_ref": "command-unified"}


class _FakeTransportClient:
    def __init__(self, status: str = "accepted") -> None:
        self.status = status

    def execute(self, payload: dict, headers: dict, timeout_s: float, attempt: int) -> dict:
        return {
            "status": self.status,
            "external_ref": "command-external",
            "code": "200",
            "timeout": False,
            "details": {},
        }


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


class _NoAdvanceMerchantMissionPack(MerchantServiceMissionPack):
    missions = {"no_advance": [{"goal": "complete_onboarding", "max_steps": 0}]}


class _NoAdvanceOperatorMissionPack(OperatorCardMissionPack):
    missions = {"no_advance": [{"goal": "resolve_escalation", "max_steps": 0}]}


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
    session = WorkflowSession(session_id=f"phase9-command-{workflow_id}", compliance_flags=flags)
    runtime.start_workflow(session, workflow_id, workflow_type=workflow_type)
    engine = UnifiedSupervisedOperatorFlowEngine(runtime)
    return engine.execute_unified_flow(
        session,
        mission_pack(runtime),
        mission_name,
        sequence_pack(runtime),
        sequence_name,
        SupervisionGate(approved=True, supervisor_id="sup-command"),
        _FakeUnifiedCallAdapter(),
    )


def _base_inputs(unified: dict, policy_profile: DestinationGovernanceProfile, destination: str) -> dict:
    return {
        "unified_result": unified,
        "gate": ExternalAdapterGate(supervision=SupervisionGate(approved=True, supervisor_id="sup-cmd")),
        "envelope": GovernedTransportEnvelope(timeout_s=0.4, max_retries=1, idempotency_key="idem-cmd", correlation_id="corr-cmd"),
        "policy_profile": policy_profile,
        "destination": destination,
        "auth_posture": "mtls_token",
        "risk_score": 0.2,
        "rollback_gate": DeploymentRollbackGate(enabled=True, mode="safe"),
        "metrics": {"health_score": 0.95, "anomaly_score": 0.05},
    }


class TestMerchantServiceCommandSurface:
    def test_governed_command_execution_pause_resume_status_inspect_replay(self) -> None:
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
        transport = MerchantServiceTransportExecutor(_FakeTransportClient())
        engine = OperatorCommandEngine()
        profile = MerchantServiceCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="merchant-prod",
            allowlist=["merchant_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="merchant_service_transport",
            risk_threshold=0.9,
            lineage_domain="merchant",
        )
        inputs = _base_inputs(unified, policy_profile, "merchant_gateway_prod_a")

        pause = engine.execute_command(command="pause", command_profile=profile, transport_executor=transport, **inputs)
        resume = engine.execute_command(command="resume", command_profile=profile, transport_executor=transport, **inputs)
        status = engine.execute_command(command="status", command_profile=profile, transport_executor=transport, **inputs)
        inspect = engine.execute_command(command="inspect", command_profile=profile, transport_executor=transport, **inputs)
        replay = engine.execute_command(command="replay", command_profile=profile, transport_executor=transport, **inputs)

        assert pause["status"] == "executed"
        assert pause["command_result"]["intervention"]["state"] == "paused"
        assert resume["status"] == "executed"
        assert resume["command_result"]["command_state"] == "resumed"
        assert status["command_result"]["command_state"] == "status_reported"
        assert inspect["command_result"]["command_state"] == "inspection_ready"
        assert replay["replay"] == unified["replay"]
        assert pause["lineage"]["signature"] == "operator_command:v1"

    def test_command_authorization_and_supervision_enforcement(self) -> None:
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
        transport = MerchantServiceTransportExecutor(_FakeTransportClient())
        engine = OperatorCommandEngine()
        profile = MerchantServiceCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="merchant-prod",
            allowlist=["merchant_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="merchant_service_transport",
            risk_threshold=0.9,
            lineage_domain="merchant",
        )
        blocked_command = engine.execute_command(
            command="delete",
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "merchant_gateway_prod_a"),
        )
        blocked_supervision = engine.execute_command(
            command="pause",
            command_profile=profile,
            transport_executor=transport,
            unified_result=unified,
            gate=ExternalAdapterGate(supervision=SupervisionGate(approved=True, supervisor_id="sup-cmd", supervision_mode="lenient")),
            envelope=GovernedTransportEnvelope(timeout_s=0.4, max_retries=1, idempotency_key="idem-cmd-2", correlation_id="corr-cmd-2"),
            policy_profile=policy_profile,
            destination="merchant_gateway_prod_a",
            auth_posture="mtls_token",
            risk_score=0.2,
            rollback_gate=DeploymentRollbackGate(enabled=True, mode="safe"),
            metrics={"health_score": 0.95, "anomaly_score": 0.05},
        )

        assert blocked_command["status"] == "blocked"
        assert blocked_command["reason"] == "command_not_allowed"
        assert blocked_supervision["status"] == "blocked"
        assert blocked_supervision["reason"] == "command_supervision_mismatch"


class TestOperatorCardCommandSurface:
    def test_rollback_and_recovery_correctness(self) -> None:
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
        transport = OperatorCardTransportExecutor(_FakeTransportClient())
        engine = OperatorCommandEngine()
        profile = OperatorCardCommandSurface.build_profile()
        policy_profile = DestinationGovernanceProfile(
            destination_id="operator-prod",
            allowlist=["operator_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="operator_card_transport",
            risk_threshold=0.8,
            lineage_domain="operator",
        )
        inputs = _base_inputs(unified, policy_profile, "operator_gateway_prod_a")

        rollback = engine.execute_command(command="rollback", command_profile=profile, transport_executor=transport, **inputs)
        recover = engine.execute_command(command="recover", command_profile=profile, transport_executor=transport, **inputs)

        assert rollback["status"] == "executed"
        assert rollback["command_result"]["intervention"]["state"] == "rolled_back"
        assert recover["status"] == "executed"
        assert recover["command_result"]["intervention"]["state"] == "recovered"
        assert recover["observability"]["command"]["domain"] == "operator_card_services"


class TestMixedDomainCommandSurface:
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
    def test_cross_domain_consistency(
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
        transport = MixedDomainTransportExecutor(_FakeTransportClient())
        engine = OperatorCommandEngine()
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
        result = engine.execute_command(
            command="status",
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy_profile, "mixed_gateway_prod_a"),
        )

        assert result["status"] == "executed"
        assert result["command_result"]["domain"] == expected_domain
        assert result["lineage"]["signature"] == "operator_command:v1"
        assert result["replay"] == unified["replay"]

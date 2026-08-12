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
from phase9_dashboards import OperatorDashboardEngine
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
        return {"status": "ok", "external_ref": "dashboard-unified"}


class _FakeTransportClient:
    def __init__(self, status: str = "accepted") -> None:
        self.status = status

    def execute(self, payload: dict, headers: dict, timeout_s: float, attempt: int) -> dict:
        return {
            "status": self.status,
            "external_ref": "dashboard-external",
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
    session = WorkflowSession(session_id=f"phase9-dashboard-{workflow_id}", compliance_flags=flags)
    runtime.start_workflow(session, workflow_id, workflow_type=workflow_type)
    engine = UnifiedSupervisedOperatorFlowEngine(runtime)
    return engine.execute_unified_flow(
        session,
        mission_pack(runtime),
        mission_name,
        sequence_pack(runtime),
        sequence_name,
        SupervisionGate(approved=True, supervisor_id="sup-dashboard"),
        _FakeUnifiedCallAdapter(),
    )


def _base_inputs(unified: dict, policy_profile: DestinationGovernanceProfile, destination: str) -> dict:
    return {
        "unified_result": unified,
        "gate": ExternalAdapterGate(supervision=SupervisionGate(approved=True, supervisor_id="sup-dashboard")),
        "envelope": GovernedTransportEnvelope(timeout_s=0.4, max_retries=1, idempotency_key="idem-dashboard", correlation_id="corr-dashboard"),
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
            "health_score": 0.95,
            "anomaly_score": 0.05,
            "recovery_eligible": True,
        },
    }


def _operators() -> tuple[OperatorAuthorityProfile, OperatorAuthorityProfile]:
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
    return lead, assistant


def _escalation_engine() -> OperatorEscalationEngine:
    return OperatorEscalationEngine(
        escalation_rules=OperatorEscalationRules(),
        arbitration_rules=OperatorArbitrationRules(conflicts={"pause": {"resume"}, "rollback": {"start"}}),
        arbitration_engine=OperatorArbitrationEngine(),
    )


class TestOperatorDashboardViews:
    def test_dashboard_rendering_of_deployment_and_rollout_state(self) -> None:
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
        lead, _ = _operators()
        result = _escalation_engine().execute_operator_command(
            action="status",
            operator=lead,
            escalation_chain=["ops_a"],
            conflicting_command=None,
            command_profile=MerchantServiceCommandSurface.build_profile(),
            transport_executor=MerchantServiceTransportExecutor(_FakeTransportClient()),
            **_base_inputs(
                unified,
                DestinationGovernanceProfile(
                    destination_id="merchant-prod",
                    allowlist=["merchant_gateway_prod_a"],
                    required_auth_posture="mtls_token",
                    required_transport="merchant_service_transport",
                    risk_threshold=0.9,
                    lineage_domain="merchant",
                ),
                "merchant_gateway_prod_a",
            ),
        )

        view = OperatorDashboardEngine().build_dashboard(
            command_result=result,
            deployment_state=_base_inputs(unified, DestinationGovernanceProfile(destination_id="merchant-prod", allowlist=["merchant_gateway_prod_a"], required_auth_posture="mtls_token", required_transport="merchant_service_transport", risk_threshold=0.9, lineage_domain="merchant"), "merchant_gateway_prod_a")["deployment_state"],
            command_history=[result],
        )

        assert view["operator_dashboard"]["domain"] == "merchant_services"
        assert view["operator_dashboard"]["activation_state"] == "active"
        assert view["operator_dashboard"]["rollout_stage"] == "full"
        assert view["operator_dashboard"]["intervention_overlay"] == "ready"


class TestOperatorStatusSurfaces:
    def test_status_surface_health_anomaly_and_recovery_visibility(self) -> None:
        deployment_state = {
            "activation": "active",
            "rollout": "canary",
            "monitoring": "degraded",
            "intervention": "draining",
            "health_score": 0.72,
            "anomaly_score": 0.31,
            "recovery_eligible": True,
        }
        result = {
            "status": "executed",
            "reason": "status",
            "action": "status",
            "lineage": {"domain": "mixed_domain", "signature": "operator_command:v2"},
            "command_result": {"domain": "mixed_domain"},
            "arbitration": {"status": "no_conflict", "winner_operator_id": "lead_ops"},
            "replay": {"replay_id": "r-1"},
        }

        view = OperatorDashboardEngine().build_dashboard(command_result=result, deployment_state=deployment_state, command_history=[result])

        assert view["status_surface"]["monitoring_state"] == "degraded"
        assert view["status_surface"]["health_score"] == 0.72
        assert view["status_surface"]["anomaly_score"] == 0.31
        assert view["status_surface"]["recovery_eligible"] is True


class TestOperatorLineageInspection:
    def test_lineage_summary_emits_operator_command_v2(self) -> None:
        lineage = {
            "signature": "operator_command:v2",
            "operator_id": "lead_ops",
            "supervision_level": "strict",
            "escalation_chain": ["ops_a"],
            "authority_signature": "authority:lead_ops:strict",
            "arbitration_result": {"status": "no_conflict", "winner_operator_id": "lead_ops"},
            "domain": "merchant_services",
            "reason": "status",
        }
        result = {
            "status": "executed",
            "reason": "status",
            "action": "status",
            "lineage": lineage,
            "command_result": {"domain": "merchant_services"},
            "arbitration": {"status": "no_conflict", "winner_operator_id": "lead_ops"},
            "replay": {"replay_id": "r-2"},
        }

        view = OperatorDashboardEngine().build_dashboard(
            command_result=result,
            deployment_state={"activation": "active", "rollout": "full", "monitoring": "healthy", "intervention": "ready"},
            command_history=[result],
        )

        assert view["lineage_view"]["signature"] == "operator_command:v2"
        assert view["lineage_view"]["operator_id"] == "lead_ops"
        assert view["lineage_view"]["authority_signature"] == "authority:lead_ops:strict"


class TestOperatorReplayHandles:
    def test_replay_handle_exposure_and_continuity(self) -> None:
        result = {
            "status": "executed",
            "reason": "replay",
            "action": "replay",
            "lineage": {"signature": "operator_command:v2", "domain": "operator_card_services"},
            "command_result": {"domain": "operator_card_services"},
            "arbitration": {"status": "no_conflict", "winner_operator_id": "lead_ops"},
            "replay": {"session": "abc", "cursor": "c-99", "continuity": "deterministic"},
        }

        view = OperatorDashboardEngine().build_dashboard(
            command_result=result,
            deployment_state={"activation": "active", "rollout": "full", "monitoring": "healthy", "intervention": "ready"},
            command_history=[result],
        )

        assert view["replay_view"]["replay_handle"]["session"] == "abc"
        assert view["replay_view"]["continuity_status"] == "deterministic"


class TestOperatorArbitrationVisibility:
    def test_arbitration_outcomes_visible_for_conflict(self) -> None:
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
        lead, assistant = _operators()
        policy = DestinationGovernanceProfile(
            destination_id="merchant-prod",
            allowlist=["merchant_gateway_prod_a"],
            required_auth_posture="mtls_token",
            required_transport="merchant_service_transport",
            risk_threshold=0.9,
            lineage_domain="merchant",
        )
        blocked = _escalation_engine().execute_operator_command(
            action="resume",
            operator=assistant,
            escalation_chain=[lead.operator_id],
            conflicting_command={"action": "pause", "operator": lead},
            command_profile=MerchantServiceCommandSurface.build_profile(),
            transport_executor=MerchantServiceTransportExecutor(_FakeTransportClient()),
            **_base_inputs(unified, policy, "merchant_gateway_prod_a"),
        )

        view = OperatorDashboardEngine().build_dashboard(
            command_result=blocked,
            deployment_state=_base_inputs(unified, policy, "merchant_gateway_prod_a")["deployment_state"],
            command_history=[blocked],
        )

        assert view["arbitration_view"]["status"] == "resolved"
        assert view["arbitration_view"]["winner_operator_id"] == lead.operator_id
        assert view["arbitration_view"]["command_status"] == "blocked"


class TestOperatorStateTimelines:
    @pytest.mark.parametrize(
        "workflow_id,pack,workflow_type,flags,profile,destination,transport,expected_domain",
        [
            (
                "merchant_services_pack",
                _merchant_pack(),
                "onboarding",
                {"kyc_verified": True},
                MerchantServiceCommandSurface.build_profile(),
                "merchant_gateway_prod_a",
                MerchantServiceTransportExecutor(_FakeTransportClient()),
                "merchant_services",
            ),
            (
                "operator_card_pack",
                _operator_card_pack(),
                "escalation",
                {"escalation_authorized": True},
                OperatorCardCommandSurface.build_profile(),
                "operator_gateway_prod_a",
                OperatorCardTransportExecutor(_FakeTransportClient()),
                "operator_card_services",
            ),
        ],
    )
    def test_cross_domain_timeline_normalization(
        self,
        workflow_id: str,
        pack: dict,
        workflow_type: str,
        flags: dict,
        profile,
        destination: str,
        transport,
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
        lead, _ = _operators()
        policy = DestinationGovernanceProfile(
            destination_id="mixed-prod" if "mixed" in destination else ("merchant-prod" if "merchant" in destination else "operator-prod"),
            allowlist=[destination],
            required_auth_posture="mtls_token",
            required_transport="mixed_domain_transport" if "mixed" in destination else ("merchant_service_transport" if "merchant" in destination else "operator_card_transport"),
            risk_threshold=0.9,
            lineage_domain="mixed_domain" if "mixed" in destination else ("merchant" if "merchant" in destination else "operator"),
            risk_domain="mixed_domain" if "mixed" in destination else None,
        )
        status = _escalation_engine().execute_operator_command(
            action="status",
            operator=lead,
            escalation_chain=["ops_a"],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy, destination),
        )
        intervention_action = "rollback" if expected_domain == "operator_card_services" else "pause"
        intervention_result = _escalation_engine().execute_operator_command(
            action=intervention_action,
            operator=lead,
            escalation_chain=["ops_a"],
            conflicting_command=None,
            command_profile=profile,
            transport_executor=transport,
            **_base_inputs(unified, policy, destination),
        )

        view = OperatorDashboardEngine().build_dashboard(
            command_result=status,
            deployment_state=_base_inputs(unified, policy, destination)["deployment_state"],
            command_history=[status, intervention_result],
        )

        assert view["summary"]["domain"] == expected_domain
        assert view["timeline_view"]["command_count"] == 2
        assert len(view["timeline_view"]["deployment_timeline"]) == 4
        assert view["summary"]["normalized"] is True

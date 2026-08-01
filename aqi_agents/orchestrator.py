from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from .messaging import InProcessMessageBus
from .metrics import AgentMetricsTracker
from .observability import AgentObservabilitySink
from .registry import AgentRegistry
from .retry import DeterministicRetryPolicy, run_with_deterministic_retry
from .state import AgentSharedStateStore

try:
    from qpc.context import from_orchestrator_task as build_qpc_context_from_task
    from qpc.core import run_qpc_analysis, run_qpc_decision, run_qpc_plan
    from qpc.telemetry import record_qpc_error, record_qpc_trace
except ImportError:  # pragma: no cover - optional intelligence layer.
    build_qpc_context_from_task = None  # type: ignore
    run_qpc_analysis = None  # type: ignore
    run_qpc_decision = None  # type: ignore
    run_qpc_plan = None  # type: ignore
    record_qpc_error = None  # type: ignore
    record_qpc_trace = None  # type: ignore

try:
    from aqi_governance.telemetry import record_agent_pressure_governance_event
except ImportError:  # pragma: no cover - optional governance bridge.
    record_agent_pressure_governance_event = None  # type: ignore


INTENT_ROLE_MAP = {
    "discovery": "analyst_agent",
    "value_framing": "planner_agent",
    "negotiation": "negotiator_agent",
    "closing_signal": "verifier_agent",
}

MISSION_ROLE_MAP = {
    "merchant_daily_snapshot": ["analyst_agent", "planner_agent", "verifier_agent"],
    "merchant_weekly_report": ["analyst_agent", "planner_agent", "verifier_agent"],
    "dealflow_conversation": ["analyst_agent", "planner_agent", "negotiator_agent", "verifier_agent"],
}


class MultiAgentOrchestrator:
    """Routes work across AQI role agents with governance-aware messaging."""

    def __init__(
        self,
        *,
        governance_controller: Any = None,
        registry: AgentRegistry | None = None,
        state_store: AgentSharedStateStore | None = None,
        message_bus: InProcessMessageBus | None = None,
        max_inflight_per_role: int = 2,
        retry_policy: DeterministicRetryPolicy | None = None,
        metrics_tracker: AgentMetricsTracker | None = None,
        observability_sink: AgentObservabilitySink | None = None,
        enable_qpc: bool = True,
    ):
        self.governance_controller = governance_controller
        self.registry = registry or AgentRegistry()
        self.state_store = state_store or AgentSharedStateStore()
        self.metrics_tracker = metrics_tracker or AgentMetricsTracker()
        self.observability_sink = observability_sink or AgentObservabilitySink()
        self.message_bus = message_bus or InProcessMessageBus(
            governance_controller=governance_controller,
            metrics_tracker=self.metrics_tracker,
        )
        self.max_inflight_per_role = max(1, int(max_inflight_per_role))
        self.retry_policy = retry_policy or DeterministicRetryPolicy()
        self.enable_qpc = enable_qpc

    def _emit_snapshot(self) -> Dict[str, Any]:
        snapshot = self.metrics_tracker.snapshot_metrics()
        self.observability_sink.write_snapshot(snapshot)
        self.observability_sink.append_history(snapshot)
        return snapshot

    @staticmethod
    def _utc_now() -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    def route_role_for_intent(self, intent_label: str) -> str:
        return INTENT_ROLE_MAP.get(intent_label, "operator_agent")

    def _qpc_payload_for_task(
        self,
        *,
        session_id: str,
        target_role: str,
        mission_type: str,
        task_inputs: Dict[str, Any],
        shared_state: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        if not self.enable_qpc or build_qpc_context_from_task is None or run_qpc_decision is None:
            return None

        context = build_qpc_context_from_task(
            session_id=session_id,
            role=target_role,
            mission_type=mission_type,
            task_inputs=task_inputs,
            shared_state=shared_state,
            metrics={
                "risk_score": float(task_inputs.get("risk_score", 0.2)),
                "stability_score": float(task_inputs.get("stability_score", 0.8)),
            },
        )
        try:
            decision = run_qpc_decision(context)
            analysis = run_qpc_analysis(context) if run_qpc_analysis is not None else None
            plan = run_qpc_plan(context) if run_qpc_plan is not None else None

            governance = None
            if self.governance_controller is not None and hasattr(self.governance_controller, "evaluate_qpc_decision"):
                governance = self.governance_controller.evaluate_qpc_decision(context.to_dict(), decision.to_dict())

            payload = {
                "context": context.to_dict(),
                "decision": decision.to_dict(),
                "analysis": analysis.to_dict() if analysis is not None else {},
                "plan": plan.to_dict() if plan is not None else {},
                "governance": governance.__dict__ if governance is not None else None,
            }

            if record_qpc_trace is not None:
                record_qpc_trace(
                    context,
                    {
                        "decision": payload["decision"],
                        "analysis": payload["analysis"],
                        "plan": payload["plan"],
                    },
                    governance_outcome=payload.get("governance") or {},
                )
            return payload
        except Exception as exc:  # pragma: no cover - defensive fallback.
            if record_qpc_error is not None:
                record_qpc_error(context, str(exc))
            return {
                "error": str(exc),
            }

    def coordinate_turn(
        self,
        *,
        session_id: str,
        intent_label: str,
        user_message: str,
        profile: str = "",
        script: str = "",
    ) -> Dict[str, Any]:
        target_role = self.route_role_for_intent(intent_label)
        qpc_payload = self._qpc_payload_for_task(
            session_id=session_id,
            target_role=target_role,
            mission_type="dealflow_conversation" if intent_label in {"negotiation", "closing_signal"} else "",
            task_inputs={
                "intent_label": intent_label,
                "message": user_message,
                "risk_score": 0.45 if intent_label in {"negotiation", "closing_signal"} else 0.2,
            },
            shared_state=self.state_store.get_shared_context(session_id),
        )
        if qpc_payload and qpc_payload.get("decision"):
            governance = qpc_payload.get("governance") or {}
            if governance.get("decision") == "deny":
                target_role = "operator_agent"
            elif governance.get("decision") != "deny":
                action_to_role = {
                    "route_analyst": "analyst_agent",
                    "route_planner": "planner_agent",
                    "route_negotiator": "negotiator_agent",
                    "route_verifier": "verifier_agent",
                    "escalate_to_operator": "operator_agent",
                }
                qpc_action = str((qpc_payload.get("decision") or {}).get("action", "maintain_route"))
                target_role = action_to_role.get(qpc_action, target_role)
        trace_id = str(uuid4())
        self.state_store.set_active_conversation(
            session_id,
            {
                "session_id": session_id,
                "intent_label": intent_label,
                "target_role": target_role,
                "updated_at_utc": self._utc_now(),
            },
        )

        def _dispatch_once(attempt: int) -> Dict[str, Any]:
            if attempt > 1:
                # Deterministic retry strategy drains one pending message before re-attempt.
                self.message_bus.drain_next(target_role)

            if not self.state_store.try_acquire_inflight_slot(target_role, self.max_inflight_per_role):
                self.state_store.set_agent_status(target_role, "blocked")
                self.metrics_tracker.record_inflight(target_role, self.state_store.inflight_count(target_role))
                self._emit_snapshot()
                return {
                    "status": "blocked",
                    "reason": "CONCURRENCY_LIMIT_REACHED",
                    "trace_id": trace_id,
                    "target_role": target_role,
                }

            self.state_store.set_agent_status(target_role, "running")
            self.metrics_tracker.record_inflight(target_role, self.state_store.inflight_count(target_role))
            try:
                payload = {
                    "trace_id": trace_id,
                    "session_id": session_id,
                    "intent_label": intent_label,
                    "message": user_message,
                    "profile": profile,
                    "script": script,
                    "qpc": qpc_payload or {},
                }
                envelope = self.message_bus.send_message("operator_agent", target_role, payload)

                if envelope.governance_flags.get("queue_state") == "BACKPRESSURE_QUEUE_FULL":
                    self.state_store.set_agent_status(target_role, "blocked")
                    self.observability_sink.record_pressure_event(
                        {
                            "event": "agent_backpressure",
                            "role": target_role,
                            "trace_id": trace_id,
                            "reason": "BACKPRESSURE_QUEUE_FULL",
                            "queue_depth": envelope.governance_flags.get("queue_depth", 0),
                        }
                    )
                    metrics_snapshot = self._emit_snapshot()
                    if record_agent_pressure_governance_event is not None:
                        record_agent_pressure_governance_event(
                            {
                                "event": "agent_pressure_governance_bridge",
                                "decision": "deny",
                                "reason": "BACKPRESSURE_QUEUE_FULL",
                                "role": target_role,
                                "trace_id": trace_id,
                            },
                            agent_metrics_snapshot=metrics_snapshot,
                        )
                    return {
                        "status": "blocked",
                        "reason": "BACKPRESSURE_QUEUE_FULL",
                        "trace_id": trace_id,
                        "target_role": target_role,
                        "envelope": envelope.to_dict(),
                    }

                self.message_bus.drain_next(target_role)
                self.state_store.update_shared_context(
                    session_id,
                    {
                        "lead_profile": profile,
                        "mission_context": script,
                        "risk_level": envelope.governance_flags.get("risk_level", "green"),
                        "last_intent": intent_label,
                        "last_target_role": target_role,
                    },
                )
                status = "blocked" if envelope.governance_flags.get("blocked") else "idle"
                self.state_store.set_agent_status(target_role, status)
                self._emit_snapshot()
                return {
                    "status": "delivered",
                    "trace_id": trace_id,
                    "target_role": target_role,
                    "qpc": qpc_payload,
                    "envelope": envelope.to_dict(),
                }
            finally:
                self.state_store.release_inflight_slot(target_role)
                self.metrics_tracker.record_inflight(target_role, self.state_store.inflight_count(target_role))
                self._emit_snapshot()

        result = run_with_deterministic_retry(
            _dispatch_once,
            policy=self.retry_policy,
            role=target_role,
            metrics_tracker=self.metrics_tracker,
        )
        if "target_role" not in result:
            result["target_role"] = target_role
        if "trace_id" not in result:
            result["trace_id"] = trace_id
        result.setdefault("qpc", qpc_payload)
        self._emit_snapshot()
        return result

    def run_dealflow_session(self, session_id: str, profile: str, script: str) -> Dict[str, Any]:
        steps = [
            ("discovery", "Analyze buyer signals"),
            ("value_framing", "Plan value narrative"),
            ("negotiation", "Prepare negotiation options"),
            ("closing_signal", "Verify close-readiness"),
        ]
        actions: List[Dict[str, Any]] = []
        for intent_label, message in steps:
            actions.append(
                self.coordinate_turn(
                    session_id=session_id,
                    intent_label=intent_label,
                    user_message=message,
                    profile=profile,
                    script=script,
                )
            )

        return {
            "session_id": session_id,
            "profile": profile,
            "script": script,
            "actions": actions,
            "shared_state": self.state_store.get_shared_context(session_id),
        }

    def coordinate_mission(self, mission_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        gate = None
        if self.governance_controller is not None:
            gate = self.governance_controller.can_start_mission(
                mission_type,
                {
                    "source": "multi_agent_orchestrator",
                    "dry_run": True,
                    **context,
                },
            )
            if not gate.allowed:
                return {
                    "mission_type": mission_type,
                    "status": "governance_denied",
                    "decision": {
                        "allowed": gate.allowed,
                        "decision": gate.decision,
                        "reason": gate.reason,
                        "rule_ids": list(gate.rule_ids),
                        "risk_level": gate.risk_level,
                    },
                    "roles": [],
                    "messages": [],
                }

        roles = list(MISSION_ROLE_MAP.get(mission_type, ["operator_agent"]))
        trace_id = str(uuid4())
        messages: List[Dict[str, Any]] = []
        delivered_roles: List[str] = []
        blocked_roles: List[str] = []
        qpc_plan_payload = self._qpc_payload_for_task(
            session_id=str(context.get("session_id", trace_id)),
            target_role="planner_agent",
            mission_type=mission_type,
            task_inputs={
                "intent_label": "mission_coordination",
                "risk_score": float(context.get("risk_score", 0.2)),
                "context": dict(context),
            },
            shared_state=self.state_store.snapshot(),
        )

        if qpc_plan_payload and qpc_plan_payload.get("error"):
            error_reason = str(qpc_plan_payload.get("error", "qpc integration failed"))
            return {
                "mission_type": mission_type,
                "status": "integration_failed",
                "roles": [],
                "messages": [],
                "trace_id": trace_id,
                "qpc": qpc_plan_payload,
                "decision": {
                    "allowed": False,
                    "decision": "deny",
                    "reason": error_reason,
                    "rule_ids": ["QPC_INTEGRATION_FAILED"],
                    "risk_level": "yellow",
                },
            }

        self.state_store.set_active_mission(
            mission_type,
            {
                "mission_type": mission_type,
                "started_at_utc": self._utc_now(),
                "context": context,
                "roles": roles,
            },
        )

        for role in roles:
            if not self.state_store.try_acquire_inflight_slot(role, self.max_inflight_per_role):
                self.state_store.set_agent_status(role, "blocked")
                self.metrics_tracker.record_inflight(role, self.state_store.inflight_count(role))
                self.observability_sink.record_pressure_event(
                    {
                        "event": "agent_saturation",
                        "role": role,
                        "trace_id": trace_id,
                        "reason": "CONCURRENCY_LIMIT_REACHED",
                    }
                )
                self._emit_snapshot()
                messages.append(
                    {
                        "trace_id": trace_id,
                        "sender_role": "operator_agent",
                        "target_role": role,
                        "payload": {
                            "mission_type": mission_type,
                            "intent_label": "mission_coordination",
                        },
                        "governance_flags": {
                            "blocked": True,
                            "decision": "deny",
                            "reason": "CONCURRENCY_LIMIT_REACHED",
                        },
                    }
                )
                blocked_roles.append(role)
                continue

            self.state_store.set_agent_status(role, "running")
            self.metrics_tracker.record_inflight(role, self.state_store.inflight_count(role))
            try:
                envelope = self.message_bus.send_message(
                    "operator_agent",
                    role,
                    {
                        "trace_id": trace_id,
                        "mission_type": mission_type,
                        "intent_label": "mission_coordination",
                        "message": f"Coordinate mission {mission_type}",
                        "context": context,
                        "risk_score": float(context.get("risk_score", 0.2)),
                        "qpc": qpc_plan_payload or {},
                    },
                )
                messages.append(envelope.to_dict())
                if envelope.governance_flags.get("queue_state") == "BACKPRESSURE_QUEUE_FULL":
                    self.observability_sink.record_pressure_event(
                        {
                            "event": "agent_backpressure",
                            "role": role,
                            "trace_id": trace_id,
                            "reason": "BACKPRESSURE_QUEUE_FULL",
                            "queue_depth": envelope.governance_flags.get("queue_depth", 0),
                        }
                    )
                if envelope.governance_flags.get("blocked"):
                    blocked_roles.append(role)
                else:
                    delivered_roles.append(role)

                status = "blocked" if envelope.governance_flags.get("blocked") else "idle"
                self.state_store.set_agent_status(role, status)
                self._emit_snapshot()
            finally:
                self.state_store.release_inflight_slot(role)
                self.metrics_tracker.record_inflight(role, self.state_store.inflight_count(role))
                self._emit_snapshot()

        mission_status = "coordinated"
        if blocked_roles and delivered_roles:
            mission_status = "partially_blocked"
        elif blocked_roles:
            mission_status = "blocked"

        return {
            "mission_type": mission_type,
            "status": mission_status,
            "roles": roles,
            "delivered_roles": delivered_roles,
            "blocked_roles": blocked_roles,
            "trace_id": trace_id,
            "qpc": qpc_plan_payload,
            "messages": messages,
            "decision": {
                "allowed": True,
                "decision": gate.decision if gate is not None else "allow",
                "reason": gate.reason if gate is not None else "mission coordinated",
                "rule_ids": list(gate.rule_ids) if gate is not None else ["MISSION_COORDINATION_OK"],
                "risk_level": gate.risk_level if gate is not None else "green",
            },
        }

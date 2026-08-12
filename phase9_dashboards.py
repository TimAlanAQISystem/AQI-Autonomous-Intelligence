from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class OperatorDashboard:
    domain: str
    active_surface: str
    activation_state: str
    rollout_stage: str
    monitoring_state: str
    intervention_overlay: str


@dataclass
class OperatorStatusSurface:
    domain: str
    command_status: str
    monitoring_state: str
    health_score: float
    anomaly_score: float
    recovery_eligible: bool


@dataclass
class OperatorLineageView:
    signature: str
    operator_id: str
    supervision_level: str
    escalation_chain: List[str]
    authority_signature: str
    arbitration_result: Dict[str, Any]


@dataclass
class OperatorReplayView:
    replay_handle: Dict[str, Any]
    continuity_status: str
    lineage_signature: str


@dataclass
class OperatorArbitrationView:
    status: str
    winner_operator_id: str
    loser_operator_id: str
    winner_action: str
    command_status: str


@dataclass
class OperatorTimelineView:
    command_timeline: List[Dict[str, Any]]
    intervention_timeline: List[Dict[str, Any]]
    arbitration_timeline: List[Dict[str, Any]]
    deployment_timeline: List[Dict[str, Any]]
    command_count: int


class OperatorDashboardEngine:
    def build_dashboard(
        self,
        *,
        command_result: Dict[str, Any],
        deployment_state: Dict[str, Any],
        command_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        domain = self._domain(command_result)
        dashboard = self._dashboard(domain, command_result, deployment_state)
        status_surface = self._status_surface(domain, command_result, deployment_state)
        lineage_view = self._lineage_view(command_result)
        replay_view = self._replay_view(command_result)
        arbitration_view = self._arbitration_view(command_result)
        timeline_view = self._timeline_view(command_history, deployment_state)

        return {
            "operator_dashboard": asdict(dashboard),
            "status_surface": asdict(status_surface),
            "lineage_view": asdict(lineage_view),
            "replay_view": asdict(replay_view),
            "arbitration_view": asdict(arbitration_view),
            "timeline_view": asdict(timeline_view),
            "summary": {
                "domain": domain,
                "normalized": True,
                "status": str(command_result.get("status", "unknown")),
                "lineage_signature": str((command_result.get("lineage") or {}).get("signature", "none")),
            },
        }

    def _domain(self, command_result: Dict[str, Any]) -> str:
        lineage_domain = str(((command_result.get("lineage") or {}).get("domain") or "").strip())
        if lineage_domain:
            return lineage_domain
        command_domain = str(((command_result.get("command_result") or {}).get("domain") or "").strip())
        if command_domain:
            return command_domain
        return "unknown"

    def _dashboard(
        self,
        domain: str,
        command_result: Dict[str, Any],
        deployment_state: Dict[str, Any],
    ) -> OperatorDashboard:
        surface = str(((command_result.get("lineage") or {}).get("scope") or "phase9_operator_surface").strip())
        return OperatorDashboard(
            domain=domain,
            active_surface=surface,
            activation_state=str(deployment_state.get("activation", "unknown")),
            rollout_stage=str(deployment_state.get("rollout", "unknown")),
            monitoring_state=str(deployment_state.get("monitoring", "unknown")),
            intervention_overlay=str(deployment_state.get("intervention", "none")),
        )

    def _status_surface(
        self,
        domain: str,
        command_result: Dict[str, Any],
        deployment_state: Dict[str, Any],
    ) -> OperatorStatusSurface:
        return OperatorStatusSurface(
            domain=domain,
            command_status=str(command_result.get("status", "unknown")),
            monitoring_state=str(deployment_state.get("monitoring", "unknown")),
            health_score=float(deployment_state.get("health_score", 0.0)),
            anomaly_score=float(deployment_state.get("anomaly_score", 0.0)),
            recovery_eligible=bool(deployment_state.get("recovery_eligible", False)),
        )

    def _lineage_view(self, command_result: Dict[str, Any]) -> OperatorLineageView:
        lineage = dict(command_result.get("lineage", {}))
        return OperatorLineageView(
            signature=str(lineage.get("signature", "none")),
            operator_id=str(lineage.get("operator_id", "unknown")),
            supervision_level=str(lineage.get("supervision_level", "unknown")),
            escalation_chain=list(lineage.get("escalation_chain", [])),
            authority_signature=str(lineage.get("authority_signature", "none")),
            arbitration_result=dict(lineage.get("arbitration_result", {})),
        )

    def _replay_view(self, command_result: Dict[str, Any]) -> OperatorReplayView:
        replay = dict(command_result.get("replay", {}))
        continuity = str(replay.get("continuity", "deterministic"))
        lineage_signature = str(((command_result.get("lineage") or {}).get("signature") or "none").strip())
        return OperatorReplayView(
            replay_handle=replay,
            continuity_status=continuity,
            lineage_signature=lineage_signature,
        )

    def _arbitration_view(self, command_result: Dict[str, Any]) -> OperatorArbitrationView:
        arbitration = dict(command_result.get("arbitration", {}))
        return OperatorArbitrationView(
            status=str(arbitration.get("status", "none")),
            winner_operator_id=str(arbitration.get("winner_operator_id", "none")),
            loser_operator_id=str(arbitration.get("loser_operator_id", "none")),
            winner_action=str(arbitration.get("winner_action", "none")),
            command_status=str(command_result.get("status", "unknown")),
        )

    def _timeline_view(self, command_history: List[Dict[str, Any]], deployment_state: Dict[str, Any]) -> OperatorTimelineView:
        command_timeline = []
        intervention_timeline = []
        arbitration_timeline = []

        for idx, item in enumerate(command_history):
            action = str(item.get("action", "unknown"))
            status = str(item.get("status", "unknown"))
            command_timeline.append({"sequence": idx + 1, "action": action, "status": status})

            if action in {"pause", "drain", "rollback", "recover"}:
                state = str((((item.get("command_result") or {}).get("intervention") or {}).get("state") or status).strip())
                intervention_timeline.append({"sequence": idx + 1, "action": action, "state": state})

            arbitration = dict(item.get("arbitration", {}))
            if arbitration:
                arbitration_timeline.append(
                    {
                        "sequence": idx + 1,
                        "status": str(arbitration.get("status", "none")),
                        "winner_operator_id": str(arbitration.get("winner_operator_id", "none")),
                    }
                )

        deployment_timeline = [
            {"stage": "activation", "state": str(deployment_state.get("activation", "unknown"))},
            {"stage": "rollout", "state": str(deployment_state.get("rollout", "unknown"))},
            {"stage": "monitoring", "state": str(deployment_state.get("monitoring", "unknown"))},
            {"stage": "intervention", "state": str(deployment_state.get("intervention", "unknown"))},
        ]

        return OperatorTimelineView(
            command_timeline=command_timeline,
            intervention_timeline=intervention_timeline,
            arbitration_timeline=arbitration_timeline,
            deployment_timeline=deployment_timeline,
            command_count=len(command_timeline),
        )

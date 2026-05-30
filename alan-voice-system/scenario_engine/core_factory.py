# core_factory.py
"""
Factory that builds a full Alan core stack for scenario testing.

Assembles:
  - MSCOEngine (throat)
  - HACOEngine (ears)
  - StateMachine (turn-taking + demeanor)
  - NuanceBudget (nuance enforcement)
  - GuardrailEngine (hard rules)
"""

import sys
import os

# Add parent to path so core_engine is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_engine.msco.msco_engine import MSCOEngine
from core_engine.haco.haco_engine import HACOEngine
from core_engine.guardrails.thresholds import Thresholds
from core_engine.guardrails.guardrail_engine import GuardrailEngine
from core_engine.state_machine.transitions import StateMachine
from core_engine.state_machine.states import TurnState, DemeanorState
from core_engine.nuance_engine.nuance_budget import NuanceBudget


class AlanCore:
    """Complete Alan voice system core for scenario testing."""

    def __init__(self, scenario_profile: str):
        self.msco = MSCOEngine(scenario_profile)
        self.haco = HACOEngine(
            thresholds={
                "intent_db_rise": Thresholds.INTENT_DB_RISE,
                "intent_window_ms": Thresholds.INTENT_WINDOW_MS,
                "floor_db_rise": Thresholds.FLOOR_DB_RISE,
                "floor_window_ms": Thresholds.FLOOR_WINDOW_MS,
            }
        )
        self.state_machine = StateMachine()
        self.guardrails = GuardrailEngine()
        self.nuance_budget = NuanceBudget()
        self.trace = []  # list of events for validator

    def log(self, t_ms: int, event: str, data: dict = None):
        """Append an event to the trace log."""
        self.trace.append({"t": t_ms, "event": event, "data": data or {}})

    def get_trace(self) -> list:
        """Return the full event trace."""
        return list(self.trace)


def core_factory(scenario_profile: str) -> AlanCore:
    """Build a fresh AlanCore instance for a given scenario profile."""
    return AlanCore(scenario_profile)

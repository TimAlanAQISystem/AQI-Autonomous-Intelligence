# states.py
"""
State definitions for turn-taking and demeanor.

Turn-taking states:
  - ALAN_FLOOR: Alan is speaking
  - INTENT_TO_SPEAK: human is about to speak
  - MERCHANT_FLOOR: human has the floor

Demeanor states:
  - ANCHOR: calm, steady baseline
  - LIGHT_ADAPT: small, safe adjustments
  - DE_ESCALATE: slow, soften, stabilize when human is upset
  - CONFIRM: explicit clarification mode
  - DISCRETE: non-full-duplex fallback when timing is bad
"""

from enum import Enum, auto


class TurnState(Enum):
    """Turn-taking state machine states."""
    ALAN_FLOOR = auto()
    INTENT_TO_SPEAK = auto()
    MERCHANT_FLOOR = auto()


class DemeanorState(Enum):
    """Demeanor/behavioral state machine states."""
    ANCHOR = auto()
    LIGHT_ADAPT = auto()
    DE_ESCALATE = auto()
    CONFIRM = auto()
    DISCRETE = auto()

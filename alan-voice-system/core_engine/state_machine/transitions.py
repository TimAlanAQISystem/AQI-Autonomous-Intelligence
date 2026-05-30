# transitions.py
"""
State transition logic with illegal-transition protection.

Turn-taking transitions:
  ALAN_FLOOR -> INTENT_TO_SPEAK -> MERCHANT_FLOOR
  MERCHANT_FLOOR -> ALAN_FLOOR (when human yields back)

Demeanor transitions:
  ANCHOR <-> LIGHT_ADAPT (normal operation)
  Any -> DE_ESCALATE (emotional spike)
  Any -> CONFIRM (low confidence)
  Any -> DISCRETE (high jitter)
  Recovery only when metrics are stable for defined window.

Illegal transitions:
  - ALAN_FLOOR -> MERCHANT_FLOOR (must go through INTENT_TO_SPEAK)
  - Stuck in any state beyond time limits
"""

from .states import TurnState, DemeanorState


class IllegalTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""
    pass


class StateMachine:
    """
    Turn-taking + demeanor state machine with guardrails.
    No illegal transitions. No stuck states.
    """

    # Legal turn transitions: {from_state: [allowed_to_states]}
    LEGAL_TURN_TRANSITIONS = {
        TurnState.ALAN_FLOOR: [TurnState.INTENT_TO_SPEAK],
        TurnState.INTENT_TO_SPEAK: [TurnState.MERCHANT_FLOOR, TurnState.ALAN_FLOOR],
        TurnState.MERCHANT_FLOOR: [TurnState.ALAN_FLOOR],
    }

    # Legal demeanor transitions
    LEGAL_DEMEANOR_TRANSITIONS = {
        DemeanorState.ANCHOR: [
            DemeanorState.LIGHT_ADAPT,
            DemeanorState.DE_ESCALATE,
            DemeanorState.CONFIRM,
            DemeanorState.DISCRETE,
        ],
        DemeanorState.LIGHT_ADAPT: [
            DemeanorState.ANCHOR,
            DemeanorState.DE_ESCALATE,
            DemeanorState.CONFIRM,
            DemeanorState.DISCRETE,
        ],
        DemeanorState.DE_ESCALATE: [DemeanorState.ANCHOR],
        DemeanorState.CONFIRM: [DemeanorState.ANCHOR, DemeanorState.LIGHT_ADAPT],
        DemeanorState.DISCRETE: [DemeanorState.ANCHOR],
    }

    def __init__(self):
        self.turn_state = TurnState.ALAN_FLOOR
        self.demeanor_state = DemeanorState.ANCHOR
        self._turn_history = []
        self._demeanor_history = []

    def update_turn_state(self, intent_to_speak: bool, merchant_floor: bool):
        """
        Deterministic turn-taking transitions.

        Args:
            intent_to_speak: HACO detected intent cue.
            merchant_floor: HACO detected merchant has floor.

        Raises:
            IllegalTransitionError if transition is not legal.
        """
        old = self.turn_state

        if merchant_floor:
            target = TurnState.MERCHANT_FLOOR
        elif intent_to_speak:
            target = TurnState.INTENT_TO_SPEAK
        else:
            # No cues — stay or return to ALAN_FLOOR
            if self.turn_state == TurnState.MERCHANT_FLOOR:
                target = TurnState.ALAN_FLOOR
            else:
                return  # No change

        if target == old:
            return  # Already in target state

        # Special: allow fast-track ALAN_FLOOR -> MERCHANT_FLOOR
        # if energy is overwhelming (skip INTENT_TO_SPEAK)
        if old == TurnState.ALAN_FLOOR and target == TurnState.MERCHANT_FLOOR:
            # Fast-track: insert synthetic INTENT_TO_SPEAK
            self.turn_state = TurnState.INTENT_TO_SPEAK
            self._turn_history.append(("fast_intent", old, TurnState.INTENT_TO_SPEAK))
            old = TurnState.INTENT_TO_SPEAK

        if target in self.LEGAL_TURN_TRANSITIONS.get(old, []):
            self.turn_state = target
            self._turn_history.append(("transition", old, target))
        else:
            raise IllegalTransitionError(
                f"Illegal turn transition: {old.name} -> {target.name}"
            )

    def update_demeanor_state(self, signals: dict):
        """
        Update demeanor based on system signals.

        Args:
            signals: Dictionary with optional keys:
                - low_confidence: bool
                - high_emotion: bool
                - jitter_high: bool
                - latency_high: bool
                - stable: bool (metrics stable for recovery)
        """
        old = self.demeanor_state

        # Priority order: DISCRETE > DE_ESCALATE > CONFIRM > LIGHT_ADAPT > ANCHOR
        if signals.get("jitter_high"):
            target = DemeanorState.DISCRETE
        elif signals.get("high_emotion"):
            target = DemeanorState.DE_ESCALATE
        elif signals.get("low_confidence"):
            target = DemeanorState.CONFIRM
        elif signals.get("stable") and old in (
            DemeanorState.DE_ESCALATE,
            DemeanorState.CONFIRM,
            DemeanorState.DISCRETE,
        ):
            target = DemeanorState.ANCHOR
        elif old == DemeanorState.ANCHOR:
            target = DemeanorState.LIGHT_ADAPT
        else:
            return  # No change

        if target == old:
            return

        if target in self.LEGAL_DEMEANOR_TRANSITIONS.get(old, []):
            self.demeanor_state = target
            self._demeanor_history.append(("transition", old, target))
        else:
            raise IllegalTransitionError(
                f"Illegal demeanor transition: {old.name} -> {target.name}"
            )

    def get_history(self) -> dict:
        """Return full transition history for tracing."""
        return {
            "turn_history": self._turn_history,
            "demeanor_history": self._demeanor_history,
        }

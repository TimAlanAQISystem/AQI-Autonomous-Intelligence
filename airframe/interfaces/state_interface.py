"""
State Interface — bridges monorepo StateMachine concepts to production FSMs.

Monorepo Concepts:
  - States: IDLE → LISTENING → PROCESSING → SPEAKING → (loop)
  - Transitions: guard-based (can_transition checks, error budget)
  - Nuance budget: 3 deviations per 5 turns, 2 within 15 turns
  - Error tracking: transition_error_count, max 3 rapid errors → lockdown

Production Reality:
  - alan_state_machine.py: AlanStateMachine (conversation flow states)
  - call_lifecycle_fsm.py: CallLifecycleFSM (call-level lifecycle)
  - States: INIT → RINGING → CONNECTED → ACTIVE → CLOSING → ENDED
  - + internal substates for greeting, listening, processing, speaking

This adapter provides a unified state management interface that new code
can program against without coupling to either implementation directly.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Set


class ConversationState(Enum):
    """
    Unified conversation states bridging monorepo and production.
    
    Monorepo states map:
      IDLE → IDLE
      LISTENING → LISTENING  
      PROCESSING → PROCESSING
      SPEAKING → SPEAKING
    
    Production states map:
      INIT/RINGING → PRE_CALL
      CONNECTED → GREETING
      ACTIVE (listening substage) → LISTENING
      ACTIVE (processing substage) → PROCESSING
      ACTIVE (speaking substage) → SPEAKING
      CLOSING → CLOSING
      ENDED → ENDED
    """
    PRE_CALL = "pre_call"
    GREETING = "greeting"
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    CLOSING = "closing"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class TransitionResult:
    """Result of a state transition attempt."""
    success: bool
    from_state: ConversationState
    to_state: ConversationState
    reason: str = ""
    guard_failed: str = ""


@dataclass 
class StateMetrics:
    """
    State machine metrics aligned with monorepo thresholds.
    
    Monorepo thresholds bridged:
      - transition_error_count ≤ 3 (MAX_RAPID_ERRORS)
      - nuance_budget: 3 per 5 turns, 2 within 15 turns
      - total_transitions tracked for health
    """
    total_transitions: int = 0
    error_count: int = 0
    max_rapid_errors: int = 3
    nuance_deviations: int = 0
    nuance_budget_per_5: int = 3
    nuance_budget_per_15: int = 2
    current_turn: int = 0
    
    @property
    def is_healthy(self) -> bool:
        """Check if state machine is operating within thresholds."""
        return self.error_count < self.max_rapid_errors

    @property
    def nuance_budget_available(self) -> bool:
        """Check if nuance budget allows another deviation."""
        return self.nuance_deviations < self.nuance_budget_per_5


# Define valid transitions
VALID_TRANSITIONS: Dict[ConversationState, Set[ConversationState]] = {
    ConversationState.PRE_CALL: {ConversationState.GREETING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.GREETING: {ConversationState.LISTENING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.IDLE: {ConversationState.LISTENING, ConversationState.SPEAKING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.LISTENING: {ConversationState.PROCESSING, ConversationState.SPEAKING, ConversationState.CLOSING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.PROCESSING: {ConversationState.SPEAKING, ConversationState.LISTENING, ConversationState.CLOSING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.SPEAKING: {ConversationState.LISTENING, ConversationState.PROCESSING, ConversationState.CLOSING, ConversationState.ENDED, ConversationState.ERROR},
    ConversationState.CLOSING: {ConversationState.ENDED, ConversationState.LISTENING, ConversationState.ERROR},
    ConversationState.ENDED: set(),  # terminal
    ConversationState.ERROR: {ConversationState.ENDED},  # can only end from error
}


class StateInterface(ABC):
    """
    Abstract state management interface.
    Production implementation wraps alan_state_machine + call_lifecycle_fsm.
    """

    @abstractmethod
    def get_state(self) -> ConversationState:
        """Get current conversation state."""
        ...

    @abstractmethod
    def transition(self, to_state: ConversationState, reason: str = "") -> TransitionResult:
        """
        Attempt a state transition.
        
        Args:
            to_state: Target state.
            reason: Why this transition is happening.
        
        Returns:
            TransitionResult with success/failure details.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> StateMetrics:
        """Get current state machine metrics."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset state machine to initial state."""
        ...


class SimpleStateAdapter(StateInterface):
    """
    Simple state adapter with guard-based transitions.
    Implements monorepo-aligned transition rules and nuance budget.
    Usable for testing and as a reference implementation.
    """

    def __init__(self, initial_state: ConversationState = ConversationState.PRE_CALL):
        self._state = initial_state
        self._metrics = StateMetrics()
        self._history: List[TransitionResult] = []

    def get_state(self) -> ConversationState:
        return self._state

    def transition(self, to_state: ConversationState, reason: str = "") -> TransitionResult:
        from_state = self._state
        
        # Guard: check if transition is valid
        valid_targets = VALID_TRANSITIONS.get(from_state, set())
        if to_state not in valid_targets:
            result = TransitionResult(
                success=False,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
                guard_failed=f"Invalid transition: {from_state.value} → {to_state.value}"
            )
            self._metrics.error_count += 1
            self._history.append(result)
            return result

        # Guard: check error budget
        if not self._metrics.is_healthy and to_state != ConversationState.ENDED:
            result = TransitionResult(
                success=False,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
                guard_failed=f"Error budget exceeded ({self._metrics.error_count}/{self._metrics.max_rapid_errors})"
            )
            self._history.append(result)
            return result

        # Transition succeeds
        self._state = to_state
        self._metrics.total_transitions += 1
        
        if to_state == ConversationState.LISTENING:
            self._metrics.current_turn += 1

        result = TransitionResult(
            success=True,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )
        self._history.append(result)
        return result

    def get_metrics(self) -> StateMetrics:
        return self._metrics

    def get_history(self) -> List[TransitionResult]:
        """Get transition history."""
        return list(self._history)

    def reset(self) -> None:
        self._state = ConversationState.PRE_CALL
        self._metrics = StateMetrics()
        self._history.clear()

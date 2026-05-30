"""
Guardrails Interface — bridges monorepo GuardrailEngine + thresholds
to production chatbot_immune_system + conversational_intelligence.

Monorepo Concepts:
  - GuardrailEngine: enforces 19 thresholds on every turn
  - Thresholds: MAX_REPEAT_PHRASES=2, MAX_FILLER_RATIO=0.15, etc.
  - Lexical identity: vocabulary fingerprint for voice consistency
  - Actions: ALLOW, WARN, BLOCK, REPHRASE

Production Reality:
  - chatbot_immune_system.py: blocks forbidden phrases, detects loops
  - conversational_intelligence.py: deeper analysis (sentiment, trajectory)
  - Immune system is reactive (blocks); guardrails are proactive (prevents)

This adapter provides a unified guardrails interface that combines
both perspectives into a single check pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GuardrailAction(Enum):
    """Actions the guardrail engine can take on a response."""
    ALLOW = "allow"         # Response is clean, send it
    WARN = "warn"           # Response has minor issues, log but send
    REPHRASE = "rephrase"   # Response needs rephrasing before sending
    BLOCK = "block"         # Response is blocked, do not send


@dataclass
class GuardrailViolation:
    """A single guardrail violation detected in a response."""
    rule_name: str
    severity: str           # "low", "medium", "high", "critical"
    description: str
    field: str = ""         # which part of the response triggered it
    threshold_value: float = 0.0
    actual_value: float = 0.0


@dataclass
class GuardrailResult:
    """
    Result of running a response through guardrail checks.
    
    If action is ALLOW or WARN, the original text can be sent.
    If action is REPHRASE, suggested_text provides a cleaner version.
    If action is BLOCK, the response must not be sent.
    """
    action: GuardrailAction
    violations: List[GuardrailViolation] = field(default_factory=list)
    original_text: str = ""
    suggested_text: str = ""
    
    @property
    def is_clean(self) -> bool:
        """Whether the response can be sent as-is."""
        return self.action in (GuardrailAction.ALLOW, GuardrailAction.WARN)

    @property
    def violation_count(self) -> int:
        return len(self.violations)


# ─── Monorepo Thresholds (from alan-voice-system thresholds.py) ─────────────
# These are the 19 thresholds from the neg-proof suite.

THRESHOLDS = {
    # Repetition guardrails
    "MAX_REPEAT_PHRASES": 2,
    "MAX_CONSECUTIVE_SIMILAR": 3,
    "MIN_VOCABULARY_DIVERSITY": 0.4,
    
    # Filler word guardrails
    "MAX_FILLER_RATIO": 0.15,
    "MAX_FILLER_PER_TURN": 3,
    
    # Response quality
    "MIN_RESPONSE_LENGTH": 5,
    "MAX_RESPONSE_LENGTH": 500,
    "MIN_RELEVANCE_SCORE": 0.3,
    
    # Prosody / voice consistency
    "MAX_SPEED_DEVIATION": 0.3,
    "MAX_PITCH_DEVIATION": 0.2,
    "MIN_ENERGY_LEVEL": 0.1,
    
    # Turn-taking
    "MAX_INTERRUPTION_RATE": 0.25,
    "MIN_LISTEN_RATIO": 0.3,
    "MAX_MONOLOGUE_DURATION_S": 30,
    
    # Sentiment / safety
    "MIN_SENTIMENT_SCORE": -0.5,
    "MAX_AGGRESSION_SCORE": 0.7,
    
    # Budget / governance
    "MAX_NUANCE_DEVIATIONS_PER_5": 3,
    "MAX_NUANCE_DEVIATIONS_PER_15": 2,
    "MAX_RAPID_TRANSITION_ERRORS": 3,
}


class GuardrailsInterface(ABC):
    """
    Abstract guardrails interface. Checks responses before they're sent.
    Production implementation wraps immune system + intelligence layer.
    """

    @abstractmethod
    def check(self, response_text: str, context: Optional[dict] = None) -> GuardrailResult:
        """
        Check a response against all guardrail rules.
        
        Args:
            response_text: Alan's proposed response text.
            context: Optional dict with conversation context (turn count,
                     recent responses, sentiment history, etc.)
        
        Returns:
            GuardrailResult with action and any violations.
        """
        ...

    @abstractmethod
    def get_active_rules(self) -> List[str]:
        """Get list of currently active guardrail rule names."""
        ...

    @abstractmethod
    def get_thresholds(self) -> Dict[str, float]:
        """Get current threshold values."""
        ...


class SimpleGuardrailAdapter(GuardrailsInterface):
    """
    Simple guardrail adapter implementing core checks.
    Uses monorepo thresholds for validation.
    
    Checks implemented:
      1. Response length (min/max)
      2. Filler word ratio
      3. Repetition detection
      4. Forbidden phrase detection
    """

    # Common filler words/phrases
    FILLER_WORDS = {
        "um", "uh", "like", "you know", "basically", "actually",
        "honestly", "literally", "right", "so", "well", "I mean",
    }

    # Forbidden phrases (from production immune system)
    FORBIDDEN_PHRASES = [
        "as an ai", "as a language model", "i'm an ai",
        "i don't have feelings", "i cannot feel",
        "my programming", "my training data",
    ]

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self._thresholds = dict(THRESHOLDS)
        if thresholds:
            self._thresholds.update(thresholds)
        self._recent_responses: List[str] = []

    def check(self, response_text: str, context: Optional[dict] = None) -> GuardrailResult:
        violations = []
        text_lower = response_text.lower().strip()
        words = text_lower.split()
        word_count = len(words)

        # Check 1: Response length
        if word_count < self._thresholds["MIN_RESPONSE_LENGTH"]:
            violations.append(GuardrailViolation(
                rule_name="MIN_RESPONSE_LENGTH",
                severity="medium",
                description=f"Response too short ({word_count} words)",
                threshold_value=self._thresholds["MIN_RESPONSE_LENGTH"],
                actual_value=word_count,
            ))

        if word_count > self._thresholds["MAX_RESPONSE_LENGTH"]:
            violations.append(GuardrailViolation(
                rule_name="MAX_RESPONSE_LENGTH",
                severity="high",
                description=f"Response too long ({word_count} words)",
                threshold_value=self._thresholds["MAX_RESPONSE_LENGTH"],
                actual_value=word_count,
            ))

        # Check 2: Filler word ratio
        filler_count = sum(1 for w in words if w in self.FILLER_WORDS)
        filler_ratio = filler_count / max(word_count, 1)
        
        if filler_ratio > self._thresholds["MAX_FILLER_RATIO"]:
            violations.append(GuardrailViolation(
                rule_name="MAX_FILLER_RATIO",
                severity="medium",
                description=f"Too many filler words ({filler_ratio:.2f})",
                threshold_value=self._thresholds["MAX_FILLER_RATIO"],
                actual_value=filler_ratio,
            ))

        if filler_count > self._thresholds["MAX_FILLER_PER_TURN"]:
            violations.append(GuardrailViolation(
                rule_name="MAX_FILLER_PER_TURN",
                severity="medium",
                description=f"Too many fillers in turn ({filler_count})",
                threshold_value=self._thresholds["MAX_FILLER_PER_TURN"],
                actual_value=filler_count,
            ))

        # Check 3: Repetition (check against recent responses)
        repeat_count = sum(1 for r in self._recent_responses if r == text_lower)
        if repeat_count >= self._thresholds["MAX_REPEAT_PHRASES"]:
            violations.append(GuardrailViolation(
                rule_name="MAX_REPEAT_PHRASES",
                severity="high",
                description=f"Response repeated {repeat_count} times",
                threshold_value=self._thresholds["MAX_REPEAT_PHRASES"],
                actual_value=repeat_count,
            ))

        # Check 4: Forbidden phrases
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in text_lower:
                violations.append(GuardrailViolation(
                    rule_name="FORBIDDEN_PHRASE",
                    severity="critical",
                    description=f"Forbidden phrase detected: '{phrase}'",
                    field=phrase,
                ))

        # Track this response
        self._recent_responses.append(text_lower)
        if len(self._recent_responses) > 20:
            self._recent_responses = self._recent_responses[-20:]

        # Determine action
        if not violations:
            action = GuardrailAction.ALLOW
        elif any(v.severity == "critical" for v in violations):
            action = GuardrailAction.BLOCK
        elif any(v.severity == "high" for v in violations):
            action = GuardrailAction.REPHRASE
        else:
            action = GuardrailAction.WARN

        return GuardrailResult(
            action=action,
            violations=violations,
            original_text=response_text,
        )

    def get_active_rules(self) -> List[str]:
        return [
            "MIN_RESPONSE_LENGTH", "MAX_RESPONSE_LENGTH",
            "MAX_FILLER_RATIO", "MAX_FILLER_PER_TURN",
            "MAX_REPEAT_PHRASES", "FORBIDDEN_PHRASE",
        ]

    def get_thresholds(self) -> Dict[str, float]:
        return dict(self._thresholds)

    def reset_history(self) -> None:
        """Clear recent response history."""
        self._recent_responses.clear()

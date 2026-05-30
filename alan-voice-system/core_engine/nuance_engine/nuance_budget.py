# nuance_budget.py
"""
Nuance budget enforcement – keeps Alan from becoming overbearing.

Per-minute budget:
  - 1–2 signature phrases
  - 1 tonal flourish
  - 1 micro-pause flourish (40–50 ms)

0 nuance during:
  - confirmations
  - corrections
  - fallback (DISCRETE, CONFIRM, DE_ESCALATE)
  - high emotion
  - noisy conditions
  - while human is speaking
"""


class NuanceBudget:
    """Tracks and enforces Alan's nuance budget — prevents personality overload."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset budget for a new minute window."""
        self.signature_phrases_remaining = 2
        self.tonal_flourishes_remaining = 1
        self.micro_pauses_remaining = 1

    def can_use_signature_phrase(self) -> bool:
        """Check if a signature phrase is available."""
        return self.signature_phrases_remaining > 0

    def consume_signature_phrase(self):
        """Use one signature phrase from the budget."""
        if self.can_use_signature_phrase():
            self.signature_phrases_remaining -= 1

    def can_use_tonal_flourish(self) -> bool:
        """Check if a tonal flourish is available."""
        return self.tonal_flourishes_remaining > 0

    def consume_tonal_flourish(self):
        """Use one tonal flourish from the budget."""
        if self.can_use_tonal_flourish():
            self.tonal_flourishes_remaining -= 1

    def can_use_micro_pause(self) -> bool:
        """Check if a micro-pause is available."""
        return self.micro_pauses_remaining > 0

    def consume_micro_pause(self):
        """Use one micro-pause from the budget."""
        if self.can_use_micro_pause():
            self.micro_pauses_remaining -= 1

    def is_suppressed(self, demeanor_state: str, human_speaking: bool, high_emotion: bool, noisy: bool) -> bool:
        """
        Check if nuance should be completely suppressed.

        Returns True (suppress all nuance) if ANY of these are true:
        - human is speaking
        - demeanor is CONFIRM, DE_ESCALATE, or DISCRETE
        - high emotion detected
        - noisy conditions
        """
        if human_speaking:
            return True
        if demeanor_state in ("CONFIRM", "DE_ESCALATE", "DISCRETE"):
            return True
        if high_emotion:
            return True
        if noisy:
            return True
        return False

    def get_remaining(self) -> dict:
        """Return remaining budget for tracing."""
        return {
            "signature_phrases": self.signature_phrases_remaining,
            "tonal_flourishes": self.tonal_flourishes_remaining,
            "micro_pauses": self.micro_pauses_remaining,
        }

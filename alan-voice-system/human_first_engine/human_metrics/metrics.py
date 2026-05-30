# metrics.py
"""
Human experience metrics — tracks whether Alan maintains
the human-first contract throughout a conversation.

Metrics:
  - respect: Alan never talks over, never dismisses
  - clarity: Alan is understood, confirmations work
  - warmth: Appropriate nuance, not cold/robotic
  - stability: Predictable behavior, no erratic shifts
  - sense_of_control: Human always feels in control
"""


class HumanExperienceMetrics:
    """Tracks human-experience quality metrics across a conversation."""

    def __init__(self):
        self.events = []
        self._talking_over_count = 0
        self._yield_violations = 0
        self._nuance_violations = 0
        self._emotional_drift_count = 0
        self._confirmations_requested = 0
        self._confirmations_successful = 0
        self._total_turns = 0

    def record_turn(
        self,
        turn_number: int,
        talking_over: bool = False,
        yield_in_time: bool = True,
        nuance_appropriate: bool = True,
        emotional_in_envelope: bool = True,
        confirmation_requested: bool = False,
        confirmation_successful: bool = True,
    ):
        """Record metrics for a single conversation turn."""
        self._total_turns += 1

        if talking_over:
            self._talking_over_count += 1
        if not yield_in_time:
            self._yield_violations += 1
        if not nuance_appropriate:
            self._nuance_violations += 1
        if not emotional_in_envelope:
            self._emotional_drift_count += 1
        if confirmation_requested:
            self._confirmations_requested += 1
            if confirmation_successful:
                self._confirmations_successful += 1

        self.events.append({
            "turn": turn_number,
            "talking_over": talking_over,
            "yield_in_time": yield_in_time,
            "nuance_appropriate": nuance_appropriate,
            "emotional_in_envelope": emotional_in_envelope,
        })

    def compute_scores(self) -> dict:
        """
        Compute human experience scores (0.0 – 1.0 each).

        Returns:
            Dictionary with respect, clarity, warmth, stability, sense_of_control, overall.
        """
        if self._total_turns == 0:
            return {
                "respect": 1.0, "clarity": 1.0, "warmth": 1.0,
                "stability": 1.0, "sense_of_control": 1.0, "overall": 1.0,
            }

        n = self._total_turns

        respect = 1.0 - (self._talking_over_count / n)
        clarity = (
            (self._confirmations_successful / self._confirmations_requested)
            if self._confirmations_requested > 0
            else 1.0
        )
        warmth = 1.0 - (self._nuance_violations / n)
        stability = 1.0 - (self._emotional_drift_count / n)
        sense_of_control = 1.0 - (self._yield_violations / n)

        overall = min(respect, clarity, warmth, stability, sense_of_control)

        return {
            "respect": max(0.0, respect),
            "clarity": max(0.0, clarity),
            "warmth": max(0.0, warmth),
            "stability": max(0.0, stability),
            "sense_of_control": max(0.0, sense_of_control),
            "overall": max(0.0, overall),
        }

    def is_contract_maintained(self) -> bool:
        """Returns True if all human-first metrics are at 1.0 (perfect)."""
        scores = self.compute_scores()
        return scores["overall"] == 1.0

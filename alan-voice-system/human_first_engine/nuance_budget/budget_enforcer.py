# budget_enforcer.py
"""
Budget enforcer — ensures nuance never exceeds per-minute limits.

Integrates with NuanceBudget from core_engine and adds
context-aware suppression logic.
"""


class BudgetEnforcer:
    """
    Wraps NuanceBudget with context-aware enforcement.

    Rules:
    - 0 nuance during confirmations, corrections, fallback, high emotion, noise, human speaking
    - If nuance conflicts with a hard rule, the hard rule wins instantly
    """

    def __init__(self, nuance_budget):
        """
        Args:
            nuance_budget: NuanceBudget instance from core_engine.
        """
        self.budget = nuance_budget

    def request_signature_phrase(self, context: dict) -> bool:
        """
        Request to use a signature phrase.

        Args:
            context: Dictionary with demeanor_state, human_speaking, high_emotion, noisy.

        Returns:
            True if allowed, False if suppressed.
        """
        if self._is_suppressed(context):
            return False
        if self.budget.can_use_signature_phrase():
            self.budget.consume_signature_phrase()
            return True
        return False

    def request_tonal_flourish(self, context: dict) -> bool:
        """Request to use a tonal flourish."""
        if self._is_suppressed(context):
            return False
        if self.budget.can_use_tonal_flourish():
            self.budget.consume_tonal_flourish()
            return True
        return False

    def request_micro_pause(self, context: dict) -> bool:
        """Request to use a micro-pause."""
        if self._is_suppressed(context):
            return False
        if self.budget.can_use_micro_pause():
            self.budget.consume_micro_pause()
            return True
        return False

    def _is_suppressed(self, context: dict) -> bool:
        """Check if nuance is completely suppressed by context."""
        return self.budget.is_suppressed(
            demeanor_state=context.get("demeanor_state", "ANCHOR"),
            human_speaking=context.get("human_speaking", False),
            high_emotion=context.get("high_emotion", False),
            noisy=context.get("noisy", False),
        )

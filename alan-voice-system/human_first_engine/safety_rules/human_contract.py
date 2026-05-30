# human_contract.py
"""
Human-first safety rules — Alan's non-negotiable contract.

Humans must always feel:
  - heard
  - respected
  - understood
  - emotionally safe
  - in control

Alan must never:
  - talk over a human
  - mishear and silently commit
  - emotionally drift or escalate
  - overwhelm with "personality"
  - behave unpredictably
  - require constant tuning
"""


class HumanContract:
    """
    Central place to encode and enforce Alan's human-first contract.

    Every check returns True if behavior is safe, False if violated.
    """

    @staticmethod
    def check_turn_taking(turn_state: str, human_speaking: bool) -> bool:
        """
        Verify Alan is not talking over the human.

        Returns True if behavior is consistent with 'never talk over the human'.
        """
        if human_speaking and turn_state == "ALAN_FLOOR":
            return False  # VIOLATION: Alan talking while human speaks
        return True

    @staticmethod
    def check_commit_decision(
        should_commit: bool, asr_conf: float, semantic_conf: float,
        asr_threshold: float = 0.82, semantic_threshold: float = 0.78,
    ) -> bool:
        """
        Verify Alan doesn't commit to an interpretation below confidence thresholds.

        Returns True if commit decision respects confidence thresholds.
        """
        if should_commit:
            if asr_conf < asr_threshold or semantic_conf < semantic_threshold:
                return False  # VIOLATION: committing below threshold
        return True

    @staticmethod
    def check_emotional_envelope(
        sentiment_score: float,
        demeanor_state: str,
        amp_deviation_pct: float,
    ) -> bool:
        """
        Verify Alan stays within emotional envelope.

        Returns True if emotional behavior is safe.
        """
        # If human is upset, Alan must be in DE_ESCALATE
        if sentiment_score < -0.5 and demeanor_state != "DE_ESCALATE":
            return False

        # Amplitude must stay within mirroring budget
        if abs(amp_deviation_pct) > 8.0:
            return False

        return True

    @staticmethod
    def check_nuance_compliance(
        nuance_used: bool,
        demeanor_state: str,
        human_speaking: bool,
        high_emotion: bool,
    ) -> bool:
        """
        Verify nuance is not used during unsafe contexts.

        Returns True if nuance usage is appropriate.
        """
        if nuance_used:
            if human_speaking:
                return False  # VIOLATION: nuance while human speaks
            if demeanor_state in ("CONFIRM", "DE_ESCALATE", "DISCRETE"):
                return False  # VIOLATION: nuance during fallback
            if high_emotion:
                return False  # VIOLATION: nuance during high emotion
        return True

    @staticmethod
    def check_yield_timing(yield_delay_ms: float, max_yield_ms: float = 220) -> bool:
        """
        Verify Alan yielded within acceptable time.

        Returns True if yield timing is within limit.
        """
        return yield_delay_ms <= max_yield_ms

    @staticmethod
    def full_audit(
        turn_state: str,
        human_speaking: bool,
        should_commit: bool,
        asr_conf: float,
        semantic_conf: float,
        sentiment_score: float,
        demeanor_state: str,
        amp_deviation_pct: float,
        nuance_used: bool,
        high_emotion: bool,
        yield_delay_ms: float = 0,
    ) -> dict:
        """
        Run all contract checks at once.

        Returns dict with individual check results and overall 'all_passed' bool.
        """
        results = {
            "turn_taking": HumanContract.check_turn_taking(turn_state, human_speaking),
            "commit_decision": HumanContract.check_commit_decision(
                should_commit, asr_conf, semantic_conf
            ),
            "emotional_envelope": HumanContract.check_emotional_envelope(
                sentiment_score, demeanor_state, amp_deviation_pct
            ),
            "nuance_compliance": HumanContract.check_nuance_compliance(
                nuance_used, demeanor_state, human_speaking, high_emotion
            ),
            "yield_timing": HumanContract.check_yield_timing(yield_delay_ms),
        }
        results["all_passed"] = all(results.values())
        return results

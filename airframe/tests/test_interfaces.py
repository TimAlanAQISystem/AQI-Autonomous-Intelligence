"""
Neg-proof tests for all Interface Adapters.

Tests:
  - TTS: TTSParameters, MockTTSAdapter, drift severity, mirroring
  - STT: TranscriptionResult, MockSTTAdapter, confidence levels, overlap
  - State: SimpleStateAdapter, transitions, guards, metrics
  - Guardrails: SimpleGuardrailAdapter, length/filler/repeat/forbidden checks
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airframe.interfaces.tts_interface import (
    TTSParameters, TTSInterface, MockTTSAdapter, DriftSeverity,
)
from airframe.interfaces.stt_interface import (
    STTParameters, STTInterface, MockSTTAdapter,
    TranscriptionResult, TranscriptionConfidence,
)
from airframe.interfaces.state_interface import (
    ConversationState, TransitionResult, StateMetrics,
    SimpleStateAdapter, VALID_TRANSITIONS,
)
from airframe.interfaces.guardrails_interface import (
    GuardrailAction, GuardrailViolation, GuardrailResult,
    SimpleGuardrailAdapter, THRESHOLDS,
)


# ═══════════════════════════════════════════════════════════════════════════
# TTS Interface Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTTSParameters:
    """Tests for TTSParameters dataclass."""

    def test_defaults(self):
        p = TTSParameters()
        assert p.voice == "alloy"
        assert p.speed == 1.0
        assert p.speed_min == 0.8
        assert p.speed_max == 1.3

    def test_constrain_speed_within_range(self):
        p = TTSParameters()
        assert p.constrain_speed(1.0) == 1.0

    def test_constrain_speed_clips_low(self):
        p = TTSParameters()
        assert p.constrain_speed(0.1) == 0.8

    def test_constrain_speed_clips_high(self):
        p = TTSParameters()
        assert p.constrain_speed(5.0) == 1.3

    def test_mirroring_zero_no_change(self):
        p = TTSParameters(speed=1.0, mirroring_factor=0.0)
        result = p.apply_mirroring(1.5)
        assert result == 1.0  # no mirroring

    def test_mirroring_full_matches_merchant(self):
        p = TTSParameters(speed=1.0, mirroring_factor=1.0)
        result = p.apply_mirroring(1.2)
        assert abs(result - 1.2) < 0.01  # full mirror

    def test_mirroring_constrained_by_bounds(self):
        p = TTSParameters(speed=1.0, mirroring_factor=1.0, speed_max=1.1)
        result = p.apply_mirroring(2.0)
        assert result == 1.1  # clipped to max


class TestMockTTS:
    """Tests for MockTTSAdapter."""

    def test_synthesize_returns_bytes(self):
        tts = MockTTSAdapter()
        result = tts.synthesize("Hello there")
        assert isinstance(result, bytes)

    def test_synthesize_tracks_calls(self):
        tts = MockTTSAdapter()
        tts.synthesize("Hello")
        tts.synthesize("World")
        assert len(tts.calls) == 2
        assert tts.calls[0]["text"] == "Hello"

    def test_drift_default_none(self):
        tts = MockTTSAdapter()
        assert tts.get_drift_severity() == DriftSeverity.NONE

    def test_set_drift(self):
        tts = MockTTSAdapter()
        tts.set_drift(DriftSeverity.SEVERE)
        assert tts.get_drift_severity() == DriftSeverity.SEVERE

    def test_reset_anchor_clears_drift(self):
        tts = MockTTSAdapter()
        tts.set_drift(DriftSeverity.CATASTROPHIC)
        tts.synthesize("test")
        tts.reset_anchor()
        assert tts.get_drift_severity() == DriftSeverity.NONE
        assert len(tts.calls) == 0


# ═══════════════════════════════════════════════════════════════════════════
# STT Interface Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTranscriptionResult:
    """Tests for TranscriptionResult."""

    def test_high_confidence(self):
        r = TranscriptionResult(text="hello", confidence=0.95)
        assert r.confidence_level == TranscriptionConfidence.HIGH
        assert r.is_acceptable

    def test_medium_confidence(self):
        r = TranscriptionResult(text="hello", confidence=0.70)
        assert r.confidence_level == TranscriptionConfidence.MEDIUM
        assert r.is_acceptable

    def test_low_confidence(self):
        r = TranscriptionResult(text="hello", confidence=0.40)
        assert r.confidence_level == TranscriptionConfidence.LOW
        assert r.is_acceptable

    def test_rejected_confidence(self):
        r = TranscriptionResult(text="hello", confidence=0.10)
        assert r.confidence_level == TranscriptionConfidence.REJECTED
        assert not r.is_acceptable


class TestMockSTT:
    """Tests for MockSTTAdapter."""

    def test_queue_and_process(self):
        stt = MockSTTAdapter()
        stt.queue_result("Hello, this is Alan", confidence=0.95)
        result = stt.process_audio(b"\x00" * 100)
        assert result is not None
        assert result.text == "Hello, this is Alan"
        assert result.confidence == 0.95

    def test_no_result_when_empty(self):
        stt = MockSTTAdapter()
        result = stt.process_audio(b"\x00" * 100)
        assert result is None

    def test_overlap_default_false(self):
        stt = MockSTTAdapter()
        assert stt.get_overlap_status() is False

    def test_set_overlap(self):
        stt = MockSTTAdapter()
        stt.set_overlap(True)
        assert stt.get_overlap_status() is True

    def test_buffer_duration_increases(self):
        stt = MockSTTAdapter()
        assert stt.get_buffer_duration_ms() == 0
        stt.process_audio(b"\x00")
        assert stt.get_buffer_duration_ms() == 20

    def test_reset_clears_everything(self):
        stt = MockSTTAdapter()
        stt.queue_result("test")
        stt.process_audio(b"\x00")
        stt.set_overlap(True)
        stt.reset()
        assert stt.get_overlap_status() is False
        assert stt.get_buffer_duration_ms() == 0


# ═══════════════════════════════════════════════════════════════════════════
# State Interface Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSimpleStateAdapter:
    """Tests for SimpleStateAdapter."""

    def test_initial_state(self):
        sm = SimpleStateAdapter()
        assert sm.get_state() == ConversationState.PRE_CALL

    def test_valid_transition(self):
        sm = SimpleStateAdapter()
        result = sm.transition(ConversationState.GREETING, "call connected")
        assert result.success is True
        assert sm.get_state() == ConversationState.GREETING

    def test_invalid_transition_blocked(self):
        sm = SimpleStateAdapter()
        # PRE_CALL → PROCESSING is not valid
        result = sm.transition(ConversationState.PROCESSING, "invalid")
        assert result.success is False
        assert sm.get_state() == ConversationState.PRE_CALL  # unchanged

    def test_full_call_lifecycle(self):
        """Simulate a complete call: PRE_CALL → GREETING → LISTENING → PROCESSING → SPEAKING → CLOSING → ENDED"""
        sm = SimpleStateAdapter()
        
        transitions = [
            ConversationState.GREETING,
            ConversationState.LISTENING,
            ConversationState.PROCESSING,
            ConversationState.SPEAKING,
            ConversationState.CLOSING,
            ConversationState.ENDED,
        ]
        
        for target in transitions:
            result = sm.transition(target)
            assert result.success, f"Failed: → {target.value}, guard={result.guard_failed}"
        
        assert sm.get_state() == ConversationState.ENDED

    def test_ended_is_terminal(self):
        """Cannot transition out of ENDED."""
        sm = SimpleStateAdapter(ConversationState.ENDED)
        result = sm.transition(ConversationState.LISTENING)
        assert result.success is False

    def test_error_budget_enforcement(self):
        """After 3 errors, non-ENDED transitions are blocked."""
        sm = SimpleStateAdapter()
        # Force 3 errors
        for _ in range(3):
            sm.transition(ConversationState.PROCESSING)  # invalid from PRE_CALL
        
        assert sm.get_metrics().error_count == 3
        assert not sm.get_metrics().is_healthy
        
        # Even valid transitions should be blocked (except ENDED)
        result = sm.transition(ConversationState.GREETING)
        assert result.success is False
        assert "Error budget" in result.guard_failed

    def test_metrics_tracking(self):
        sm = SimpleStateAdapter()
        sm.transition(ConversationState.GREETING)
        sm.transition(ConversationState.LISTENING)
        
        metrics = sm.get_metrics()
        assert metrics.total_transitions == 2
        assert metrics.current_turn == 1  # LISTENING increments turn

    def test_history_tracking(self):
        sm = SimpleStateAdapter()
        sm.transition(ConversationState.GREETING)
        sm.transition(ConversationState.LISTENING)
        
        history = sm.get_history()
        assert len(history) == 2
        assert history[0].to_state == ConversationState.GREETING
        assert history[1].to_state == ConversationState.LISTENING

    def test_reset(self):
        sm = SimpleStateAdapter()
        sm.transition(ConversationState.GREETING)
        sm.transition(ConversationState.LISTENING)
        sm.reset()
        
        assert sm.get_state() == ConversationState.PRE_CALL
        assert sm.get_metrics().total_transitions == 0
        assert len(sm.get_history()) == 0

    def test_error_to_ended_allowed(self):
        """Can transition from ERROR to ENDED."""
        sm = SimpleStateAdapter(ConversationState.ERROR)
        result = sm.transition(ConversationState.ENDED)
        assert result.success

    def test_all_valid_transitions_defined(self):
        """Every ConversationState has an entry in VALID_TRANSITIONS."""
        for state in ConversationState:
            assert state in VALID_TRANSITIONS, f"{state} missing from VALID_TRANSITIONS"


class TestStateMetrics:
    """Tests for StateMetrics dataclass."""

    def test_default_healthy(self):
        m = StateMetrics()
        assert m.is_healthy

    def test_unhealthy_at_max_errors(self):
        m = StateMetrics(error_count=3, max_rapid_errors=3)
        assert not m.is_healthy

    def test_nuance_budget_available(self):
        m = StateMetrics(nuance_deviations=0)
        assert m.nuance_budget_available

    def test_nuance_budget_exhausted(self):
        m = StateMetrics(nuance_deviations=3, nuance_budget_per_5=3)
        assert not m.nuance_budget_available


# ═══════════════════════════════════════════════════════════════════════════
# Guardrails Interface Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestGuardrailResult:
    """Tests for GuardrailResult dataclass."""

    def test_clean_is_clean(self):
        r = GuardrailResult(action=GuardrailAction.ALLOW)
        assert r.is_clean

    def test_warn_is_clean(self):
        r = GuardrailResult(action=GuardrailAction.WARN)
        assert r.is_clean

    def test_block_not_clean(self):
        r = GuardrailResult(action=GuardrailAction.BLOCK)
        assert not r.is_clean

    def test_rephrase_not_clean(self):
        r = GuardrailResult(action=GuardrailAction.REPHRASE)
        assert not r.is_clean


class TestSimpleGuardrailAdapter:
    """Tests for SimpleGuardrailAdapter."""

    def setup_method(self):
        self.guard = SimpleGuardrailAdapter()

    def test_clean_response_allowed(self):
        result = self.guard.check(
            "Hi there! I'd love to help you save money on your credit card processing fees. "
            "We work with thousands of restaurants just like yours."
        )
        assert result.action == GuardrailAction.ALLOW
        assert result.violation_count == 0

    def test_too_short_response(self):
        result = self.guard.check("Hi")
        violations = [v for v in result.violations if v.rule_name == "MIN_RESPONSE_LENGTH"]
        assert len(violations) > 0

    def test_forbidden_phrase_blocked(self):
        result = self.guard.check(
            "As an AI language model, I cannot help with that request."
        )
        assert result.action == GuardrailAction.BLOCK
        forbidden = [v for v in result.violations if v.rule_name == "FORBIDDEN_PHRASE"]
        assert len(forbidden) > 0

    def test_filler_words_detected(self):
        result = self.guard.check(
            "Um like you know basically um like honestly um right so well "
            "I mean like actually um basically you know"
        )
        filler_violations = [v for v in result.violations if "FILLER" in v.rule_name]
        assert len(filler_violations) > 0

    def test_repetition_detected(self):
        """Same response repeated should trigger repetition guard."""
        text = "This is a perfectly normal sales response about processing fees."
        self.guard.check(text)  # first time
        self.guard.check(text)  # second time
        result = self.guard.check(text)  # third time — should trigger
        repeat_violations = [v for v in result.violations if v.rule_name == "MAX_REPEAT_PHRASES"]
        assert len(repeat_violations) > 0

    def test_get_active_rules(self):
        rules = self.guard.get_active_rules()
        assert "MIN_RESPONSE_LENGTH" in rules
        assert "MAX_RESPONSE_LENGTH" in rules
        assert "FORBIDDEN_PHRASE" in rules

    def test_get_thresholds(self):
        thresholds = self.guard.get_thresholds()
        assert thresholds["MAX_REPEAT_PHRASES"] == 2
        assert thresholds["MAX_FILLER_RATIO"] == 0.15

    def test_custom_thresholds(self):
        guard = SimpleGuardrailAdapter(thresholds={"MAX_REPEAT_PHRASES": 5})
        assert guard.get_thresholds()["MAX_REPEAT_PHRASES"] == 5

    def test_reset_history(self):
        self.guard.check("test response that is long enough to pass")
        self.guard.reset_history()
        # After reset, repetition should not trigger
        result = self.guard.check("test response that is long enough to pass")
        repeat = [v for v in result.violations if v.rule_name == "MAX_REPEAT_PHRASES"]
        assert len(repeat) == 0

    def test_19_thresholds_defined(self):
        """All 19 monorepo thresholds are present."""
        assert len(THRESHOLDS) == 19


class TestGuardrailViolation:
    """Tests for GuardrailViolation dataclass."""

    def test_violation_fields(self):
        v = GuardrailViolation(
            rule_name="TEST_RULE",
            severity="high",
            description="Test violation",
            threshold_value=10.0,
            actual_value=15.0,
        )
        assert v.rule_name == "TEST_RULE"
        assert v.severity == "high"
        assert v.actual_value > v.threshold_value

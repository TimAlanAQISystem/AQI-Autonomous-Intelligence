"""
Neg-proof tests for alan_adaptive_layer.py
============================================

Tests every adaptive layer component with passing AND failing cases.
Validates:
  - Pace modulation boundaries (never exceed -8% to +12%)
  - Energy modulation boundaries (only low/medium/high)
  - Vocabulary modulation within diversity thresholds
  - No drift under stress (bounded dropout risk)
  - No identity leakage (fingerprint has no PII)
  - No cross-call persistence (manager creates fresh state per call)
  - Fault tolerance (bad inputs never crash)
"""

import sys
import os
import time

_workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _workspace_root)

from alan_adaptive_layer import (
    ConversationAdaptiveState,
    AdaptiveLayerManager,
    PACE_SLOW_FLOOR,
    PACE_FAST_CEILING,
    PACE_LOG_CLAMP,
    PAUSE_LIST_CAP,
    DROPOUT_HESITATION_DELTA,
    DROPOUT_CLARIFICATION_DELTA,
    DROPOUT_OBJECTION_DELTA,
    _ALLOWED_ENERGY,
    _ALLOWED_FORMALITY,
    _ALLOWED_TECHNICALITY,
    _ALLOWED_MERCHANT_ROLE,
)

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {name}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {name} \u2192 {detail}")


def section(name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")


# ===================================================================
# 1. BASIC CONSTRUCTION
# ===================================================================
section("1. Basic Construction")

state = ConversationAdaptiveState(call_id="test-001", timestamp_start=time.time())
check("Creates successfully", state is not None)
check("Call ID stored", state.call_id == "test-001")
check("Merchant word count starts at 0", state.merchant_word_count == 0)
check("Alan word count starts at 0", state.alan_word_count == 0)
check("Dropout risk starts at 0", state.dropout_risk_score == 0.0)
check("Energy defaults to medium", state.alan_energy_profile == "medium")
check("Formality defaults to neutral", state.formality_level == "neutral")
check("Technicality defaults to low", state.technicality_level == "low")
check("Merchant role defaults to unknown", state.merchant_role == "unknown")

# Invalid role gets corrected
state_bad_role = ConversationAdaptiveState(call_id="x", timestamp_start=0.0, merchant_role="alien")
check("Invalid role corrected to unknown", state_bad_role.merchant_role == "unknown")


# ===================================================================
# 2. MERCHANT UTTERANCE RECORDING
# ===================================================================
section("2. Merchant Utterance Recording")

s2 = ConversationAdaptiveState(call_id="test-merchant", timestamp_start=time.time())

s2.record_merchant_utterance(word_count=10, pause_ms=500, interrupted=False, hesitation=False, clarification_request=False)
check("Word count tracked", s2.merchant_word_count == 10)
check("Utterance count tracked", s2.merchant_utterance_count == 1)
check("Pause recorded", len(s2.merchant_pause_durations_ms) == 1)
check("Pause value correct", s2.merchant_pause_durations_ms[0] == 500)

# Hesitation bumps dropout risk
s2.record_merchant_utterance(word_count=5, hesitation=True)
check("Hesitation tracked", s2.hesitation_events == 1)
check("Dropout risk bumped", s2.dropout_risk_score > 0.0)

# Clarification request bumps dropout risk more
prev_risk = s2.dropout_risk_score
s2.record_merchant_utterance(word_count=3, clarification_request=True)
check("Clarification tracked", s2.clarification_requests == 1)
check("Dropout risk increased", s2.dropout_risk_score > prev_risk)

# Interrupt tracking
s2.record_merchant_utterance(word_count=8, interrupted=True)
check("Interrupt tracked", s2.merchant_interrupt_events == 1)

# Energy tracking
s2.record_merchant_utterance(word_count=5, energy_level="high")
check("Energy initial set", s2.merchant_energy_initial == "high")
s2.record_merchant_utterance(word_count=5, energy_level="low")
check("Energy final updated", s2.merchant_energy_final == "low")
check("Energy initial preserved", s2.merchant_energy_initial == "high")

# Invalid energy level ignored
s2.record_merchant_utterance(word_count=5, energy_level="super_high")
check("Invalid energy ignored", s2.merchant_energy_final == "low")


# ===================================================================
# 3. ALAN UTTERANCE RECORDING
# ===================================================================
section("3. Alan Utterance Recording")

s3 = ConversationAdaptiveState(call_id="test-alan", timestamp_start=time.time())

s3.record_alan_utterance(word_count=20, energy_profile="high", vocab_diversity_score=0.75)
check("Alan words tracked", s3.alan_word_count == 20)
check("Alan utterances tracked", s3.alan_utterance_count == 1)
check("Energy profile set", s3.alan_energy_profile == "high")
check("Vocab diversity clamped", s3.vocab_diversity_score == 0.75)

# Vocab diversity clamped to [0, 1]
s3.record_alan_utterance(word_count=10, energy_profile="medium", vocab_diversity_score=5.0)
check("Vocab diversity clamped high", s3.vocab_diversity_score == 1.0)
s3.record_alan_utterance(word_count=10, energy_profile="medium", vocab_diversity_score=-2.0)
check("Vocab diversity clamped low", s3.vocab_diversity_score == 0.0)

# Invalid energy profile ignored
s3.record_alan_utterance(word_count=5, energy_profile="extreme", vocab_diversity_score=0.5)
check("Invalid energy kept previous", s3.alan_energy_profile == "medium")


# ===================================================================
# 4. PACE MODULATION BOUNDARIES
# ===================================================================
section("4. Pace Modulation Boundaries")

s4 = ConversationAdaptiveState(call_id="test-pace", timestamp_start=time.time())

# Slower merchant (low WPM ratio < 0.8)
for _ in range(5):
    s4.record_merchant_utterance(word_count=3)   # ~3 WPU
for _ in range(5):
    s4.record_alan_utterance(word_count=15, energy_profile="medium", vocab_diversity_score=0.6)  # ~15 WPU

params = s4.get_modulation_params()
check("Slow merchant pace shift", params["pace_shift_pct"] == PACE_SLOW_FLOOR,
      f"got {params['pace_shift_pct']}")
check("Pace shift bounded at floor", params["pace_shift_pct"] >= -0.08)

# Faster merchant
s4b = ConversationAdaptiveState(call_id="test-pace-fast", timestamp_start=time.time())
for _ in range(5):
    s4b.record_merchant_utterance(word_count=30)  # ~30 WPU (fast)
for _ in range(5):
    s4b.record_alan_utterance(word_count=10, energy_profile="medium", vocab_diversity_score=0.6)  # ~10 WPU

params_fast = s4b.get_modulation_params()
check("Fast merchant pace shift", params_fast["pace_shift_pct"] == PACE_FAST_CEILING,
      f"got {params_fast['pace_shift_pct']}")
check("Pace shift bounded at ceiling", params_fast["pace_shift_pct"] <= 0.12)

# Similar pace (ratio ~1.0) = no shift
s4c = ConversationAdaptiveState(call_id="test-pace-neutral", timestamp_start=time.time())
for _ in range(5):
    s4c.record_merchant_utterance(word_count=12)
for _ in range(5):
    s4c.record_alan_utterance(word_count=12, energy_profile="medium", vocab_diversity_score=0.6)

params_neutral = s4c.get_modulation_params()
check("Similar pace = no shift", params_neutral["pace_shift_pct"] == 0.0)

# No data = no shift
s4d = ConversationAdaptiveState(call_id="test-pace-empty", timestamp_start=time.time())
params_empty = s4d.get_modulation_params()
check("No data = no shift", params_empty["pace_shift_pct"] == 0.0)


# ===================================================================
# 5. ENERGY MODULATION
# ===================================================================
section("5. Energy Modulation")

s5 = ConversationAdaptiveState(call_id="test-energy", timestamp_start=time.time())

# No merchant data = medium default
params = s5.get_modulation_params()
check("Default energy is medium", params["energy_level"] == "medium")

# After merchant speaks with high energy
s5.record_merchant_utterance(word_count=10, energy_level="high")
params = s5.get_modulation_params()
check("Energy mirrors high", params["energy_level"] == "high")

# After merchant shifts to low
s5.record_merchant_utterance(word_count=10, energy_level="low")
params = s5.get_modulation_params()
check("Energy mirrors low", params["energy_level"] == "low")

# Only valid energy levels
for valid in _ALLOWED_ENERGY:
    check(f"Energy '{valid}' is valid", valid in ("low", "medium", "high"))


# ===================================================================
# 6. VOCABULARY MODULATION
# ===================================================================
section("6. Vocabulary Modulation")

s6 = ConversationAdaptiveState(call_id="test-vocab", timestamp_start=time.time())

check("Default vocab style is neutral", s6.formality_level == "neutral")

s6.update_formality("formal")
check("Formality updated to formal", s6.formality_level == "formal")
check("Style switch counted", s6.vocab_style_switches == 1)

# Same level = no additional switch
s6.update_formality("formal")
check("Same level no extra switch", s6.vocab_style_switches == 1)

# Invalid level ignored
s6.update_formality("ultra_formal")
check("Invalid formality ignored", s6.formality_level == "formal")

# Technicality
s6.update_technicality("high")
check("Technicality updated", s6.technicality_level == "high")
check("Style switches = 2", s6.vocab_style_switches == 2)

# Modulation params reflect vocab style
params = s6.get_modulation_params()
check("Vocab style in params", params["vocab_style"] == "formal")


# ===================================================================
# 7. FRICTION / DROPOUT RISK
# ===================================================================
section("7. Friction / Dropout Risk")

s7 = ConversationAdaptiveState(call_id="test-friction", timestamp_start=time.time())

check("Risk starts at 0", s7.dropout_risk_score == 0.0)

s7.register_objection()
check("Objection counted", s7.objection_count == 1)
check("Risk bumped by objection", abs(s7.dropout_risk_score - DROPOUT_OBJECTION_DELTA) < 0.001)

# Multiple objections accumulate
s7.register_objection()
s7.register_objection()
check("3 objections counted", s7.objection_count == 3)
check("Risk accumulates", s7.dropout_risk_score > 0.2)

# Risk clamped at 1.0
s7.update_dropout_risk(10.0)  # Huge delta
check("Risk clamped at 1.0", s7.dropout_risk_score == 1.0)

# Risk clamped at 0.0
s7.update_dropout_risk(-20.0)  # Huge negative
check("Risk clamped at 0.0", s7.dropout_risk_score == 0.0)


# ===================================================================
# 8. NO CROSS-CALL PERSISTENCE
# ===================================================================
section("8. No Cross-Call Persistence")

mgr = AdaptiveLayerManager.get_instance()

state_a = mgr.get_state("call-A")
state_a.register_objection()
state_a.update_formality("formal")
state_a.record_merchant_utterance(word_count=50)

state_b = mgr.get_state("call-B")
check("Different call = fresh state", state_b.objection_count == 0)
check("Different call = neutral formality", state_b.formality_level == "neutral")
check("Different call = zero words", state_b.merchant_word_count == 0)

# End call A
summary_a = mgr.end_call("call-A")
check("End call returns summary", summary_a is not None)
check("Ended call no longer active", "call-A" not in [s for s in mgr._states])

# End call B
mgr.end_call("call-B")


# ===================================================================
# 9. NO PII IN FINGERPRINT
# ===================================================================
section("9. No PII in Fingerprint")

s9 = ConversationAdaptiveState(call_id="test-pii", timestamp_start=time.time())
s9.record_merchant_utterance(word_count=20, pause_ms=300, hesitation=True)
s9.record_alan_utterance(word_count=40, energy_profile="high", vocab_diversity_score=0.65)
s9.register_objection()
s9.update_formality("casual")
s9.finalize_call(time.time() + 120.0)

fp = s9.to_fingerprint_summary()

# Check no PII fields
import json
fp_str = json.dumps(fp)
check("No phone numbers", "+1" not in fp_str and "phone" not in fp_str.lower())
check("No PII names", "merchant_name" not in fp_str.lower() and "phone_number" not in fp_str.lower())
check("No raw text", "raw" not in fp_str.lower() and "transcript" not in fp_str.lower())
check("Has call_id", "call_id" in fp)
check("Has pace section", "pace" in fp)
check("Has friction section", "friction" in fp)
check("Has energy section", "energy" in fp)
check("Has vocabulary section", "vocabulary" in fp)
check("Has modulation section", "modulation" in fp)
check("Has duration", "duration_seconds" in fp)


# ===================================================================
# 10. FINGERPRINT STABILITY
# ===================================================================
section("10. Fingerprint Stability")

# Short call (1-2 turns)
s10a = ConversationAdaptiveState(call_id="short", timestamp_start=time.time())
s10a.record_merchant_utterance(word_count=5)
s10a.record_alan_utterance(word_count=10, energy_profile="medium", vocab_diversity_score=0.5)
s10a.finalize_call(time.time() + 5.0)
fp_short = s10a.to_fingerprint_summary()
check("Short call fingerprint valid", fp_short.get("call_id") == "short")
check("Short call has duration", fp_short.get("duration_seconds") is not None)
check("Short call no NaN", "nan" not in json.dumps(fp_short).lower())

# Long call (many turns)
s10b = ConversationAdaptiveState(call_id="long", timestamp_start=time.time())
for i in range(100):
    s10b.record_merchant_utterance(word_count=10 + (i % 20), pause_ms=200 + (i * 5))
    s10b.record_alan_utterance(word_count=15, energy_profile="medium", vocab_diversity_score=0.6)
s10b.finalize_call(time.time() + 600.0)
fp_long = s10b.to_fingerprint_summary()
check("Long call fingerprint valid", fp_long.get("call_id") == "long")
check("Long call no NaN", "nan" not in json.dumps(fp_long).lower())
check("Long call no overflow", fp_long.get("friction", {}).get("dropout_risk_score", 0) <= 1.0)

# Zero-length call
s10c = ConversationAdaptiveState(call_id="zero", timestamp_start=time.time())
s10c.finalize_call(time.time())
fp_zero = s10c.to_fingerprint_summary()
check("Zero-length call valid", fp_zero.get("call_id") == "zero")


# ===================================================================
# 11. FAULT TOLERANCE
# ===================================================================
section("11. Fault Tolerance")

s11 = ConversationAdaptiveState(call_id="fault", timestamp_start=time.time())

# Bad word counts
s11.record_merchant_utterance(word_count=-5)
check("Negative word count handled", s11.merchant_word_count == 0)

s11.record_merchant_utterance(word_count=0)
check("Zero word count handled", s11.merchant_utterance_count == 0)

# Bad pause
s11.record_merchant_utterance(word_count=5, pause_ms=-100)
check("Negative pause ignored", len(s11.merchant_pause_durations_ms) == 0)

# Modulation params always return valid dict
params = s11.get_modulation_params()
check("Params always returns dict", isinstance(params, dict))
check("Params has pace_shift_pct", "pace_shift_pct" in params)
check("Params has energy_level", "energy_level" in params)
check("Params has vocab_style", "vocab_style" in params)

# Fingerprint never crashes
fp = s11.to_fingerprint_summary()
check("Fingerprint never crashes", fp is not None)


# ===================================================================
# 12. PACE MODULATION LOG TRACKING
# ===================================================================
section("12. Pace Modulation Logging")

s12 = ConversationAdaptiveState(call_id="pace-log", timestamp_start=time.time())

s12.update_pace_modulation(-0.05)
check("First modulation sets min/max", s12.pace_modulation_min_pct == -0.05)
check("First modulation max", s12.pace_modulation_max_pct == -0.05)

s12.update_pace_modulation(0.10)
check("Max updated", s12.pace_modulation_max_pct == 0.10)
check("Min preserved", s12.pace_modulation_min_pct == -0.05)

# Clamped to safe band
s12.update_pace_modulation(0.50)  # Exceeds PACE_LOG_CLAMP
check("Huge positive clamped", s12.pace_modulation_max_pct == PACE_LOG_CLAMP)

s12.update_pace_modulation(-0.50)
check("Huge negative clamped", s12.pace_modulation_min_pct == -PACE_LOG_CLAMP)

# Non-numeric ignored
s12.update_pace_modulation("fast")  # type: ignore
check("Non-numeric ignored", s12.pace_modulation_max_pct == PACE_LOG_CLAMP)


# ===================================================================
# 13. MANAGER SINGLETON
# ===================================================================
section("13. Manager Singleton")

mgr1 = AdaptiveLayerManager.get_instance()
mgr2 = AdaptiveLayerManager.get_instance()
check("Singleton is same instance", mgr1 is mgr2)

s = mgr1.get_state("singleton-test")
check("State created for call", s is not None)
check("Active calls >= 1", mgr1.active_calls() >= 1)

s2 = mgr1.get_state("singleton-test")
check("Same call returns same state", s is s2)

# End nonexistent call
result = mgr1.end_call("nonexistent-call")
check("End nonexistent returns None", result is None)

# Cleanup
mgr1.end_call("singleton-test")


# ===================================================================
# 14. PAUSE LIST BOUNDED
# ===================================================================
section("14. Pause List Bounded")

s14 = ConversationAdaptiveState(call_id="pause-bound", timestamp_start=time.time())
for i in range(300):
    s14.record_merchant_utterance(word_count=5, pause_ms=100 + i)

check("Pause list capped", len(s14.merchant_pause_durations_ms) == PAUSE_LIST_CAP,
      f"got {len(s14.merchant_pause_durations_ms)}")


# ===================================================================
# 15. LOGGING FAILURE ISOLATION
# ===================================================================
section("15. Logging Failure Does Not Affect Call")

s15 = ConversationAdaptiveState(call_id="log-fail", timestamp_start=time.time())
# Corrupt internal state to test fault tolerance
s15.merchant_pause_durations_ms = None  # type: ignore
try:
    fp = s15.to_fingerprint_summary()
    check("Fingerprint survives corrupted state", "call_id" in fp or "error" in fp)
except Exception:
    check("Fingerprint survives corrupted state", False, "raised exception")

# State still usable after corruption recovery
s15.merchant_pause_durations_ms = []
s15.record_merchant_utterance(word_count=5, pause_ms=200)
check("State recovers after corruption", s15.merchant_word_count > 0)


# ===================================================================
# RESULTS
# ===================================================================
print(f"\n{'='*60}")
print(f"  RESULTS: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED out of {PASS_COUNT + FAIL_COUNT}")
print(f"{'='*60}")

if FAIL_COUNT > 0:
    sys.exit(1)
else:
    print("  ALL TESTS PASSED \u2014 Adaptive layer is neg-proof.")


# Pytest wrapper for CI compatibility
def test_adaptive_layer_all_checks():
    """Pytest-compatible wrapper: asserts all checks passed."""
    assert FAIL_COUNT == 0, f"{FAIL_COUNT} adaptive layer checks failed"
    assert PASS_COUNT >= 80, f"Expected ~90 checks, only {PASS_COUNT} ran"

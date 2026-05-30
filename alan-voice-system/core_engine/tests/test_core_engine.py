# test_core_engine.py
"""
Core engine unit tests — MSCO, HACO, State Machine, Guardrails, Nuance.
Tests every component against the Human-First Voice Spec.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core_engine.msco.msco_engine import MSCOEngine
from core_engine.msco.prosody_constraints import ProsodyConstraints
from core_engine.haco.haco_engine import HACOEngine
from core_engine.haco.overlap_detection import OverlapDetector
from core_engine.state_machine.states import TurnState, DemeanorState
from core_engine.state_machine.transitions import StateMachine, IllegalTransitionError
from core_engine.guardrails.thresholds import Thresholds
from core_engine.guardrails.guardrail_engine import GuardrailEngine
from core_engine.nuance_engine.nuance_budget import NuanceBudget
from core_engine.nuance_engine.lexical_identity import choose_signature_phrase, SIGNATURE_PHRASES


def run_tests():
    passed = 0
    failed = 0

    def test(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            failed += 1

    print("=" * 70)
    print("CORE ENGINE UNIT TESTS")
    print("=" * 70)

    # ── MSCO Tests ──
    print("\n[1] MSCO — Melodic Speech Continuity Organ")

    msco = MSCOEngine("calm")
    test("MSCO initializes with calm profile", msco.scenario_profile == "calm")
    test("Anchor f0 is 150 Hz", msco.constraints.anchor_f0 == 150.0)
    test("f0 deviation is ±18 Hz", msco.constraints.f0_deviation_hz == 18.0)

    utterance = msco.generate_utterance("Hello there", {"demeanor": "ANCHOR"})
    test("Utterance returns text", utterance["text"] == "Hello there")
    test("Utterance within constraints", utterance["within_constraints"] is True)

    msco.apply_mirroring_pressure(15.0, 10.0)
    test("Tempo mirror clamped to 12%", msco._current_tempo_mirror == 12.0)
    test("Amp mirror clamped to 8%", msco._current_amp_mirror == 8.0)

    msco.reset_mirroring()
    test("Mirroring reset to 0", msco._current_tempo_mirror == 0.0)

    msco_e = MSCOEngine("energetic")
    test("Energetic f0 is 165 Hz", msco_e.constraints.anchor_f0 == 165.0)
    test("Energetic deviation is ±28 Hz", msco_e.constraints.f0_deviation_hz == 28.0)

    try:
        ProsodyConstraints.from_profile("invalid")
        test("Invalid profile raises error", False)
    except ValueError:
        test("Invalid profile raises error", True)

    # ── HACO Tests ──
    print("\n[2] HACO — Hyper-Auditory Continuity Organ")

    haco = HACOEngine({
        "intent_db_rise": 6.0,
        "intent_window_ms": 40,
        "floor_db_rise": 10.0,
        "floor_window_ms": 120,
    })
    test("HACO ASR threshold is 0.82", haco.asr_conf_threshold == 0.82)
    test("HACO semantic threshold is 0.78", haco.semantic_conf_threshold == 0.78)
    test("High confidence commits", haco.should_commit(0.90, 0.85) is True)
    test("Low ASR blocks commit", haco.should_commit(0.70, 0.85) is False)
    test("Low semantic blocks commit", haco.should_commit(0.90, 0.60) is False)
    test("Both low blocks commit", haco.should_commit(0.50, 0.50) is False)

    result = haco.process_audio_frame({"energy_db": 2.0})
    test("Low energy: no intent", result["intent_to_speak"] is False)
    test("Low energy: no floor", result["merchant_floor"] is False)

    # ── State Machine Tests ──
    print("\n[3] State Machine — Turn-Taking + Demeanor")

    sm = StateMachine()
    test("Initial turn state is ALAN_FLOOR", sm.turn_state == TurnState.ALAN_FLOOR)
    test("Initial demeanor is ANCHOR", sm.demeanor_state == DemeanorState.ANCHOR)

    # Legal transition: ALAN_FLOOR -> INTENT_TO_SPEAK
    sm.update_turn_state(intent_to_speak=True, merchant_floor=False)
    test("Intent detected -> INTENT_TO_SPEAK", sm.turn_state == TurnState.INTENT_TO_SPEAK)

    # Legal transition: INTENT_TO_SPEAK -> MERCHANT_FLOOR
    sm.update_turn_state(intent_to_speak=True, merchant_floor=True)
    test("Floor detected -> MERCHANT_FLOOR", sm.turn_state == TurnState.MERCHANT_FLOOR)

    # Legal transition: MERCHANT_FLOOR -> ALAN_FLOOR
    sm.update_turn_state(intent_to_speak=False, merchant_floor=False)
    test("Human yields -> ALAN_FLOOR", sm.turn_state == TurnState.ALAN_FLOOR)

    # Fast-track: ALAN_FLOOR -> MERCHANT_FLOOR (through synthetic INTENT_TO_SPEAK)
    sm2 = StateMachine()
    sm2.update_turn_state(intent_to_speak=True, merchant_floor=True)
    test("Fast-track -> MERCHANT_FLOOR", sm2.turn_state == TurnState.MERCHANT_FLOOR)

    # Demeanor transitions
    sm3 = StateMachine()
    sm3.update_demeanor_state({"jitter_high": True})
    test("Jitter high -> DISCRETE", sm3.demeanor_state == DemeanorState.DISCRETE)

    sm3.update_demeanor_state({"stable": True})
    test("Stable -> ANCHOR recovery", sm3.demeanor_state == DemeanorState.ANCHOR)

    sm4 = StateMachine()
    sm4.update_demeanor_state({"high_emotion": True})
    test("High emotion -> DE_ESCALATE", sm4.demeanor_state == DemeanorState.DE_ESCALATE)

    sm5 = StateMachine()
    sm5.update_demeanor_state({"low_confidence": True})
    test("Low confidence -> CONFIRM", sm5.demeanor_state == DemeanorState.CONFIRM)

    # ── Guardrails Tests ──
    print("\n[4] Guardrails — Hard Rules")

    ge = GuardrailEngine()
    health = ge.evaluate_system_health(jitter_ms=40, latency_ms=250)
    test("High jitter -> to_discrete", health["to_discrete"] is True)
    test("High latency -> simplify_speech", health["simplify_speech"] is True)

    health2 = ge.evaluate_system_health(jitter_ms=20, latency_ms=100)
    test("Normal jitter -> no discrete", health2["to_discrete"] is False)
    test("Normal latency -> no simplify", health2["simplify_speech"] is False)

    conf = ge.evaluate_confidence(0.70, 0.60)
    test("Low confidence detected", conf["low_confidence"] is True)
    test("Require confirm", conf["require_confirm"] is True)

    conf2 = ge.evaluate_confidence(0.90, 0.85)
    test("High confidence OK", conf2["low_confidence"] is False)

    emo = ge.evaluate_emotion(-0.8)
    test("Negative sentiment -> high emotion", emo["high_emotion"] is True)

    emo2 = ge.evaluate_emotion(0.5)
    test("Positive sentiment -> no high emotion", emo2["high_emotion"] is False)

    yield_r = ge.evaluate_yield_timing(150, 220)
    test("Yield 150ms within 220ms limit", yield_r["within_limit"] is True)

    yield_r2 = ge.evaluate_yield_timing(250, 220)
    test("Yield 250ms exceeds 220ms limit", yield_r2["within_limit"] is False)

    prosody = ge.evaluate_prosody_compliance(155, 150, 18, 10, 6)
    test("Prosody within bounds", prosody["all_compliant"] is True)

    prosody2 = ge.evaluate_prosody_compliance(175, 150, 18, 15, 10)
    test("f0 out of bounds detected", prosody2["f0_in_bounds"] is False)

    # ── Nuance Budget Tests ──
    print("\n[5] Nuance Budget — Identity Control")

    nb = NuanceBudget()
    test("2 signature phrases available", nb.can_use_signature_phrase() is True)
    nb.consume_signature_phrase()
    nb.consume_signature_phrase()
    test("0 after 2 consumed", nb.can_use_signature_phrase() is False)

    test("1 tonal flourish available", nb.can_use_tonal_flourish() is True)
    nb.consume_tonal_flourish()
    test("0 after consumed", nb.can_use_tonal_flourish() is False)

    test("1 micro pause available", nb.can_use_micro_pause() is True)
    nb.consume_micro_pause()
    test("0 after consumed", nb.can_use_micro_pause() is False)

    nb.reset()
    test("Reset restores budget", nb.can_use_signature_phrase() is True)

    test("Suppressed when human speaking", nb.is_suppressed("ANCHOR", True, False, False) is True)
    test("Suppressed in DE_ESCALATE", nb.is_suppressed("DE_ESCALATE", False, False, False) is True)
    test("Suppressed in CONFIRM", nb.is_suppressed("CONFIRM", False, False, False) is True)
    test("Suppressed in DISCRETE", nb.is_suppressed("DISCRETE", False, False, False) is True)
    test("Suppressed on high emotion", nb.is_suppressed("ANCHOR", False, True, False) is True)
    test("Not suppressed normally", nb.is_suppressed("ANCHOR", False, False, False) is False)

    # ── Lexical Identity Tests ──
    print("\n[6] Lexical Identity")

    test("4 signature phrases defined", len(SIGNATURE_PHRASES) == 4)
    test("Phrase 0 correct", choose_signature_phrase(0) == "Let's walk through this together.")
    test("Phrase wraps at 4", choose_signature_phrase(4) == choose_signature_phrase(0))

    # ── Thresholds Tests ──
    print("\n[7] Thresholds — Constants Integrity")

    test("INTENT_DB_RISE is 6.0", Thresholds.INTENT_DB_RISE == 6.0)
    test("FLOOR_DB_RISE is 10.0", Thresholds.FLOOR_DB_RISE == 10.0)
    test("ASR_CONF is 0.82", Thresholds.ASR_CONF == 0.82)
    test("SEMANTIC_CONF is 0.78", Thresholds.SEMANTIC_CONF == 0.78)
    test("MAX_YIELD_MS is 220", Thresholds.MAX_YIELD_MS == 220)
    test("JITTER_FALLBACK_MS is 35", Thresholds.JITTER_FALLBACK_MS == 35)
    test("LATENCY_FALLBACK_MS is 240", Thresholds.LATENCY_FALLBACK_MS == 240)

    # ── Summary ──
    print(f"\n{'=' * 70}")
    total = passed + failed
    print(f"CORE ENGINE TESTS: {passed} PASSED, {failed} FAILED out of {total}")
    if failed == 0:
        print("ALL TESTS PASSED — Core engine integrity verified.")
    else:
        print("FAILURES DETECTED — review before proceeding.")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

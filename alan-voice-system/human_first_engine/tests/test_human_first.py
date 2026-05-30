# test_human_first.py
"""
Human-first engine tests — safety rules, emotional models, metrics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from human_first_engine.safety_rules.human_contract import HumanContract
from human_first_engine.emotional_models.sentiment_triggers import SentimentTriggers
from human_first_engine.human_metrics.metrics import HumanExperienceMetrics
from core_engine.nuance_engine.nuance_budget import NuanceBudget
from human_first_engine.nuance_budget.budget_enforcer import BudgetEnforcer


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
    print("HUMAN-FIRST ENGINE TESTS")
    print("=" * 70)

    # ── Human Contract Tests ──
    print("\n[1] Human Contract — Safety Rules")

    test("No talking over (human speaking)", HumanContract.check_turn_taking("ALAN_FLOOR", True) is False)
    test("OK when human not speaking", HumanContract.check_turn_taking("ALAN_FLOOR", False) is True)
    test("OK when MERCHANT_FLOOR", HumanContract.check_turn_taking("MERCHANT_FLOOR", True) is True)

    test("Commit OK with high confidence", HumanContract.check_commit_decision(True, 0.90, 0.85) is True)
    test("Commit blocked with low ASR", HumanContract.check_commit_decision(True, 0.70, 0.85) is False)
    test("Commit blocked with low semantic", HumanContract.check_commit_decision(True, 0.90, 0.60) is False)
    test("No commit = always OK", HumanContract.check_commit_decision(False, 0.50, 0.50) is True)

    test("Emotional envelope OK", HumanContract.check_emotional_envelope(0.5, "ANCHOR", 5.0) is True)
    test("Must DE_ESCALATE when upset", HumanContract.check_emotional_envelope(-0.8, "ANCHOR", 5.0) is False)
    test("DE_ESCALATE when upset OK", HumanContract.check_emotional_envelope(-0.8, "DE_ESCALATE", 5.0) is True)
    test("Amp drift violation", HumanContract.check_emotional_envelope(0.5, "ANCHOR", 12.0) is False)

    test("Nuance OK normally", HumanContract.check_nuance_compliance(True, "ANCHOR", False, False) is True)
    test("Nuance blocked when human speaking", HumanContract.check_nuance_compliance(True, "ANCHOR", True, False) is False)
    test("Nuance blocked in CONFIRM", HumanContract.check_nuance_compliance(True, "CONFIRM", False, False) is False)
    test("Nuance blocked on high emotion", HumanContract.check_nuance_compliance(True, "ANCHOR", False, True) is False)

    test("Yield 150ms OK", HumanContract.check_yield_timing(150) is True)
    test("Yield 250ms violation", HumanContract.check_yield_timing(250) is False)

    # Full audit
    audit = HumanContract.full_audit(
        turn_state="MERCHANT_FLOOR",
        human_speaking=True,
        should_commit=False,
        asr_conf=0.90,
        semantic_conf=0.85,
        sentiment_score=0.5,
        demeanor_state="ANCHOR",
        amp_deviation_pct=5.0,
        nuance_used=False,
        high_emotion=False,
        yield_delay_ms=150,
    )
    test("Full audit all passed", audit["all_passed"] is True)

    # ── Sentiment Triggers Tests ──
    print("\n[2] Sentiment Triggers — Emotional Models")

    result = SentimentTriggers.analyze_transcript("NO, LISTEN, THAT'S NOT WHAT I SAID!")
    test("Frustration detected in angry speech", result["frustration_detected"] is True)
    test("Negative sentiment score", result["sentiment_score"] < 0)

    result2 = SentimentTriggers.analyze_transcript("Great, sounds good, thanks!")
    test("Positive detected in happy speech", result2["positive_detected"] is True)
    test("Positive sentiment score", result2["sentiment_score"] > 0)

    result3 = SentimentTriggers.analyze_transcript("I'm just thinking about it.")
    test("Neutral speech: no frustration", result3["frustration_detected"] is False)
    test("Neutral speech: no positive", result3["positive_detected"] is False)

    result4 = SentimentTriggers.analyze_transcript("What do you mean? I don't understand!")
    test("Confusion detected", result4["confusion_detected"] is True)

    # ── Budget Enforcer Tests ──
    print("\n[3] Budget Enforcer — Context-Aware Nuance")

    nb = NuanceBudget()
    enforcer = BudgetEnforcer(nb)

    normal_ctx = {"demeanor_state": "ANCHOR", "human_speaking": False, "high_emotion": False, "noisy": False}
    test("Signature phrase allowed normally", enforcer.request_signature_phrase(normal_ctx) is True)
    test("Second phrase allowed", enforcer.request_signature_phrase(normal_ctx) is True)
    test("Third phrase blocked (budget)", enforcer.request_signature_phrase(normal_ctx) is False)

    nb.reset()
    interrupt_ctx = {"demeanor_state": "ANCHOR", "human_speaking": True, "high_emotion": False, "noisy": False}
    test("Phrase blocked when human speaking", enforcer.request_signature_phrase(interrupt_ctx) is False)

    nb.reset()
    fallback_ctx = {"demeanor_state": "DE_ESCALATE", "human_speaking": False, "high_emotion": False, "noisy": False}
    test("Phrase blocked in DE_ESCALATE", enforcer.request_signature_phrase(fallback_ctx) is False)

    # ── Human Experience Metrics Tests ──
    print("\n[4] Human Experience Metrics")

    metrics = HumanExperienceMetrics()
    metrics.record_turn(1)
    metrics.record_turn(2)
    metrics.record_turn(3)
    scores = metrics.compute_scores()
    test("Perfect 3-turn conversation", scores["overall"] == 1.0)
    test("Contract maintained", metrics.is_contract_maintained() is True)

    metrics2 = HumanExperienceMetrics()
    metrics2.record_turn(1, talking_over=True)
    metrics2.record_turn(2)
    scores2 = metrics2.compute_scores()
    test("Talking-over degrades respect", scores2["respect"] < 1.0)
    test("Contract broken", metrics2.is_contract_maintained() is False)

    metrics3 = HumanExperienceMetrics()
    metrics3.record_turn(1, yield_in_time=False)
    scores3 = metrics3.compute_scores()
    test("Yield violation degrades control", scores3["sense_of_control"] < 1.0)

    # ── Summary ──
    print(f"\n{'=' * 70}")
    total = passed + failed
    print(f"HUMAN-FIRST TESTS: {passed} PASSED, {failed} FAILED out of {total}")
    if failed == 0:
        print("ALL TESTS PASSED — Human-first engine integrity verified.")
    else:
        print("FAILURES DETECTED — review before proceeding.")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

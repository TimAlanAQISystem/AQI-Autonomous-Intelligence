# test_scenarios.py
"""
Scenario engine tests — runs all 4 turn-taking Neg-Proof scenarios
and validates results.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
from scenario_engine.scenario_runner.runner import ScenarioRunner
from scenario_engine.scenario_validator.turn_taking_validator import TurnTakingValidator
from scenario_engine.scenario_reporter.reporter import ScenarioReporter


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
    print("SCENARIO ENGINE — TURN-TAKING NEG-PROOF SUITE")
    print("=" * 70)

    validator = TurnTakingValidator()
    reporter = ScenarioReporter(Path("reports"))
    runner = ScenarioRunner(validator, reporter)

    scenarios_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "scenarios"

    scenario_files = [
        "turn_taking_early_soft_interrupt.json",
        "turn_taking_angry_hard_interrupt.json",
        "turn_taking_continuous_overlap.json",
        "turn_taking_late_clause_interrupt.json",
    ]

    for filename in scenario_files:
        scenario_path = scenarios_dir / filename
        print(f"\n  Running: {filename}")

        if not scenario_path.exists():
            test(f"{filename} — file exists", False)
            continue

        try:
            result = runner.run_scenario_file(scenario_path)
            test(f"{filename} — passed", result["passed"])
            if not result["passed"]:
                for v in result.get("violations", []):
                    vtype = v.get("type", "unknown")
                    msg = v.get("message", v.get("details", {}).get("message", ""))
                    print(f"        -> {vtype}: {msg}")
        except Exception as e:
            test(f"{filename} — no errors", False)
            print(f"        -> Exception: {e}")

    # ── Summary ──
    print(f"\n{'=' * 70}")
    total = passed + failed
    print(f"SCENARIO TESTS: {passed} PASSED, {failed} FAILED out of {total}")
    if failed == 0:
        print("ALL SCENARIOS PASSED — Turn-taking is Neg-Proofed.")
    else:
        print("FAILURES DETECTED — review violations above.")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

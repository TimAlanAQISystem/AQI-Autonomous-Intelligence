"""
Master Test Runner — one command, all tests, clear report.

Runs:
  1. alan-voice-system monorepo tests (104 expected)
  2. airframe tests (config, interfaces, CI)
  3. config validation (27 configs)

Usage:
    python -m airframe.ci.run_all_tests
    python airframe/ci/run_all_tests.py
"""

import os
import subprocess
import sys
import time
from typing import List, Tuple


# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MONOREPO = os.path.join(ROOT, "alan-voice-system")
AIRFRAME = os.path.join(ROOT, "airframe")


def banner(text: str) -> None:
    """Print a section banner."""
    width = 60
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def run_pytest(directory: str, label: str) -> Tuple[int, float]:
    """
    Run pytest in a directory.
    
    Returns:
        (exit_code, elapsed_seconds)
    """
    banner(f"RUNNING: {label}")
    
    if not os.path.exists(directory):
        print(f"  SKIP — directory not found: {directory}")
        return -1, 0.0

    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", directory, "-v", "--tb=short"],
        capture_output=False,
        cwd=ROOT,
    )
    elapsed = time.time() - start
    
    status = "PASSED" if result.returncode == 0 else "FAILED"
    print(f"\n  {label}: {status} (exit={result.returncode}, {elapsed:.1f}s)")
    
    return result.returncode, elapsed


def run_monorepo_tests() -> Tuple[int, float]:
    """
    Run the alan-voice-system monorepo tests.
    These use a custom script-based runner (not pytest).
    Expects 104 total: 65 core_engine + 4 scenario_engine + 35 human_first_engine.
    
    Returns:
        (exit_code, elapsed_seconds)  — 0 = all passed, 1 = failures
    """
    banner("RUNNING: alan-voice-system (104 monorepo tests)")
    
    if not os.path.exists(MONOREPO):
        print(f"  SKIP — monorepo not found: {MONOREPO}")
        return -1, 0.0

    test_scripts = [
        ("core_engine", os.path.join("core_engine", "tests", "test_core_engine.py")),
        ("scenario_engine", os.path.join("scenario_engine", "tests", "test_scenarios.py")),
        ("human_first_engine", os.path.join("human_first_engine", "tests", "test_human_first.py")),
    ]

    total_pass = 0
    total_fail = 0
    start = time.time()

    for suite_name, script_path in test_scripts:
        full_path = os.path.join(MONOREPO, script_path)
        if not os.path.exists(full_path):
            print(f"  SKIP — {script_path} not found")
            total_fail += 1
            continue

        result = subprocess.run(
            [sys.executable, full_path],
            capture_output=True,
            text=True,
            cwd=MONOREPO,
        )

        # Parse "X PASSED, Y FAILED out of Z" from output
        output = result.stdout + result.stderr
        passed = 0
        failed = 0
        for line in output.split("\n"):
            if "PASSED" in line and "FAILED" in line and "out of" in line:
                parts = line.strip().split()
                for i, part in enumerate(parts):
                    if part == "PASSED,":
                        try:
                            passed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    if part == "FAILED":
                        try:
                            failed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

        total_pass += passed
        total_fail += failed
        status = "PASS" if failed == 0 and passed > 0 else "FAIL"
        print(f"  [{status}] {suite_name}: {passed} passed, {failed} failed")

    elapsed = time.time() - start
    overall = "PASSED" if total_fail == 0 and total_pass > 0 else "FAILED"
    print(f"\n  Monorepo Total: {total_pass} passed, {total_fail} failed ({elapsed:.1f}s)")
    
    return (0 if total_fail == 0 and total_pass > 0 else 1), elapsed


def run_config_validation() -> Tuple[int, float]:
    """
    Run config validation against all 27 operational configs.
    
    Returns:
        (error_count, elapsed_seconds)
    """
    banner("RUNNING: Config Validation (27 configs)")
    
    start = time.time()
    
    try:
        from airframe.config.config_validator import ConfigValidator
        
        validator = ConfigValidator()
        issues = validator.validate_all()
        elapsed = time.time() - start
        
        print(validator.report())
        
        error_count = sum(1 for i in issues if i.severity == "ERROR")
        warn_count = sum(1 for i in issues if i.severity == "WARNING")
        
        status = "PASSED" if error_count == 0 else "FAILED"
        print(f"\n  Config Validation: {status} "
              f"(errors={error_count}, warnings={warn_count}, {elapsed:.1f}s)")
        
        return error_count, elapsed
    
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n  Config Validation: EXCEPTION — {e}")
        return 1, elapsed


def main() -> int:
    """
    Master test runner. Returns 0 on all-pass, 1 on any failure.
    """
    banner("AQI/ALAN — MASTER TEST RUNNER")
    print(f"  Root:      {ROOT}")
    print(f"  Monorepo:  {MONOREPO}")
    print(f"  Airframe:  {AIRFRAME}")
    print(f"  Python:    {sys.executable}")
    
    results: List[Tuple[str, str, float]] = []  # (label, status, elapsed)
    overall_start = time.time()
    
    # ─── 1. Monorepo Tests (104 expected — script-based runners) ───
    monorepo_code, monorepo_elapsed = run_monorepo_tests()
    if monorepo_code == -1:
        results.append(("Monorepo Tests (104)", "SKIPPED", monorepo_elapsed))
    elif monorepo_code == 0:
        results.append(("Monorepo Tests (104)", "PASSED", monorepo_elapsed))
    else:
        results.append(("Monorepo Tests (104)", "FAILED", monorepo_elapsed))
    
    # ─── 2. Airframe Tests ──────────────────────────────────────────
    airframe_tests = os.path.join(AIRFRAME, "tests")
    code, elapsed = run_pytest(airframe_tests, "airframe tests")
    if code == -1:
        results.append(("Airframe Tests", "SKIPPED", elapsed))
    elif code == 0:
        results.append(("Airframe Tests", "PASSED", elapsed))
    else:
        results.append(("Airframe Tests", "FAILED", elapsed))
    
    # ─── 3. Config Validation ───────────────────────────────────────
    errors, elapsed = run_config_validation()
    if errors == 0:
        results.append(("Config Validation", "PASSED", elapsed))
    else:
        results.append(("Config Validation", "FAILED", elapsed))
    
    # ─── Final Report ───────────────────────────────────────────────
    total_elapsed = time.time() - overall_start
    
    banner("FINAL REPORT")
    print(f"{'Suite':<25} {'Status':<10} {'Time':>8}")
    print("-" * 45)
    
    all_passed = True
    for label, status, elapsed in results:
        print(f"{label:<25} {status:<10} {elapsed:>7.1f}s")
        if status == "FAILED":
            all_passed = False
    
    print("-" * 45)
    print(f"{'TOTAL':<25} {'PASS' if all_passed else 'FAIL':<10} {total_elapsed:>7.1f}s")
    
    if all_passed:
        print("\n  ALL SUITES PASSED")
    else:
        print("\n  SOME SUITES FAILED — see details above")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

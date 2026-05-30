"""
Neg-proof tests for Smoke Tests module.

Tests that the smoke test runner itself works correctly.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airframe.ci.smoke_tests import run_smoke_tests, check


class TestSmokeTestInfra:
    """Tests for the smoke test infrastructure."""

    def test_check_helper_pass(self):
        label, ok, detail = check("test", True, "good")
        assert label == "test"
        assert ok is True
        assert detail == "good"

    def test_check_helper_fail(self):
        label, ok, detail = check("test", False, "bad")
        assert ok is False

    def test_smoke_tests_return_list(self):
        results = run_smoke_tests()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_smoke_tests_have_correct_structure(self):
        results = run_smoke_tests()
        for label, ok, detail in results:
            assert isinstance(label, str)
            assert isinstance(ok, bool)
            assert isinstance(detail, str)

    def test_critical_files_detected(self):
        """The smoke tests should check all critical production files."""
        results = run_smoke_tests()
        labels = [label for label, _, _ in results]
        assert any("Relay Server" in l for l in labels)
        assert any("Business AI" in l for l in labels)
        assert any("Control API" in l for l in labels)

    def test_config_parse_checks_present(self):
        """Smoke tests should verify config file parsing."""
        results = run_smoke_tests()
        labels = [label for label, _, _ in results]
        assert any("Parse:" in l for l in labels)

    def test_most_smoke_tests_pass(self):
        """In a healthy workspace, most smoke tests should pass."""
        results = run_smoke_tests()
        passed = sum(1 for _, ok, _ in results if ok)
        total = len(results)
        # At minimum, critical files + some configs should pass
        assert passed > total * 0.5, f"Only {passed}/{total} passed"

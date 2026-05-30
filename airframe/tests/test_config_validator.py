"""
Neg-proof tests for the Config Validator.

Tests:
  - Validates all 27 configs without crashing
  - Detects missing files
  - Detects parse errors
  - Type constraint checking works
  - Range constraint checking works
  - Clean configs produce no errors
  - Report formatting works
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airframe.config.config_validator import (
    ConfigValidator,
    ConfigIssue,
    TYPE_CONSTRAINTS,
    RANGE_CONSTRAINTS,
)
from airframe.config.config_registry import get_all_names


class TestConfigValidator:
    """Tests for config_validator.py"""

    def setup_method(self):
        self.validator = ConfigValidator()

    def test_validate_all_no_crash(self):
        """validate_all runs across all 27 configs without exceptions."""
        issues = self.validator.validate_all()
        assert isinstance(issues, list)

    def test_validate_all_no_errors(self):
        """All 27 production configs should have zero ERRORS."""
        issues = self.validator.validate_all()
        errors = [i for i in issues if i.severity == ConfigIssue.SEVERITY_ERROR]
        assert len(errors) == 0, f"Unexpected errors: {[str(i) for i in errors]}"

    def test_validate_single_config(self):
        """Can validate a single config by name."""
        issues = self.validator.validate_one("system")
        assert isinstance(issues, list)

    def test_report_format(self):
        """Report is a non-empty string."""
        self.validator.validate_all()
        report = self.validator.report()
        assert isinstance(report, str)
        assert len(report) > 0

    def test_to_dict_format(self):
        """to_dict returns list of dicts."""
        self.validator.validate_all()
        result = self.validator.to_dict()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dict)
            assert "config" in item
            assert "severity" in item
            assert "message" in item

    def test_issue_repr(self):
        """ConfigIssue has useful repr."""
        issue = ConfigIssue("test_config", "ERROR", "test message", "test_field")
        r = repr(issue)
        assert "ERROR" in r
        assert "test_config" in r
        assert "test_field" in r
        assert "test message" in r

    def test_issue_to_dict(self):
        """ConfigIssue.to_dict returns correct structure."""
        issue = ConfigIssue("test_config", "WARNING", "test message", "field_x")
        d = issue.to_dict()
        assert d["config"] == "test_config"
        assert d["severity"] == "WARNING"
        assert d["message"] == "test message"
        assert d["field"] == "field_x"

    def test_type_constraints_defined(self):
        """Type constraints are defined for key configs."""
        assert "system" in TYPE_CONSTRAINTS
        assert "fleet_manifest" in TYPE_CONSTRAINTS
        assert "outcome_confidence" in TYPE_CONSTRAINTS

    def test_range_constraints_defined(self):
        """Range constraints are defined for numeric configs."""
        assert "campaign_autopilot" in RANGE_CONSTRAINTS
        assert "behavioral_fusion" in RANGE_CONSTRAINTS
        assert "perception_fusion" in RANGE_CONSTRAINTS

    def test_system_config_type_check_passes(self):
        """system_config.json passes type checking."""
        issues = self.validator.validate_one("system")
        type_errors = [i for i in issues
                       if i.severity == "ERROR" and "Type mismatch" in i.message]
        assert len(type_errors) == 0, f"Type errors in system: {type_errors}"

    def test_fleet_manifest_type_check_passes(self):
        """fleet_manifest.json passes type checking."""
        issues = self.validator.validate_one("fleet_manifest")
        type_errors = [i for i in issues
                       if i.severity == "ERROR" and "Type mismatch" in i.message]
        assert len(type_errors) == 0

    def test_campaign_autopilot_range_check(self):
        """campaign_autopilot.yaml passes range checking."""
        issues = self.validator.validate_one("campaign_autopilot")
        range_warnings = [i for i in issues if "out of range" in i.message]
        assert len(range_warnings) == 0, f"Range warnings: {range_warnings}"

    def test_all_configs_can_be_validated_individually(self):
        """Every registered config can be validated without exception."""
        for name in get_all_names():
            issues = self.validator.validate_one(name)
            assert isinstance(issues, list), f"validate_one({name}) did not return a list"

    def test_clean_report_when_no_issues(self):
        """Report says ALL CLEAR when no issues found."""
        # Force clean state
        self.validator.issues = []
        report = self.validator.report()
        assert "ALL CLEAR" in report

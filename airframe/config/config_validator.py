"""
Config Validator — schema validation for all 27 operational configs.

Validates:
  - File existence
  - Parse success (JSON/YAML)
  - Required top-level keys present
  - Type checking for known fields
  - Value range checks for numeric thresholds

Usage:
    from airframe.config.config_validator import ConfigValidator

    validator = ConfigValidator()
    issues = validator.validate_all()
    assert len(issues) == 0, f"Config issues: {issues}"
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from airframe.config.config_registry import (
    REGISTRY,
    get_file_path,
    get_all_names,
    get_registry_entry,
)


class ConfigIssue:
    """A single validation issue."""

    SEVERITY_ERROR = "ERROR"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_INFO = "INFO"

    def __init__(self, config_name: str, severity: str, message: str, field: str = ""):
        self.config_name = config_name
        self.severity = severity
        self.message = message
        self.field = field

    def __repr__(self):
        field_str = f" [{self.field}]" if self.field else ""
        return f"[{self.severity}] {self.config_name}{field_str}: {self.message}"

    def to_dict(self) -> dict:
        return {
            "config": self.config_name,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
        }


# ─── Known Type Constraints ────────────────────────────────────────────────
# Maps config_name → {field_path: expected_type}
# Only validates top-level fields. Nested validation is by convention.

TYPE_CONSTRAINTS: Dict[str, Dict[str, type]] = {
    "system": {
        "pghs_enabled": bool,
        "mtsp_enabled": bool,
        "mip_enabled": bool,
        "bas_enabled": bool,
        "retention_days": int,
        "pghs_budget_ms": (int, float),
    },
    "outcome_confidence": {
        "weights": dict,
        "thresholds": dict,
        "objection_clarity_mapping": dict,
    },
    "fleet_manifest": {
        "fleet_name": str,
        "version": str,
        "agents": list,
    },
    "iqcore_charter": {
        "iqcore_total": (int, float),
        "actors": dict,
    },
    "campaign_autopilot": {
        "min_readiness_score": (int, float),
        "max_daily_calls": int,
        "micro_batch_size": int,
    },
}

# ─── Known Value Range Constraints ─────────────────────────────────────────
# Maps config_name → {field_path: (min, max)}

RANGE_CONSTRAINTS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "campaign_autopilot": {
        "min_readiness_score": (0, 100),  # percentage 0-100 in production
        "max_daily_calls": (1, 10000),
        "micro_batch_size": (1, 100),
    },
    "iqcore_charter": {
        "iqcore_total": (1, 1000),
    },
    "system": {
        "retention_days": (1, 365),
        "pghs_budget_ms": (1, 60000),
    },
    "behavioral_fusion": {
        "stall_velocity_threshold": (0.0, 10.0),
        "stall_turn_threshold": (1, 100),
        "high_viscosity_threshold": (0.0, 10.0),
        "high_objection_threshold": (0.0, 10.0),
        "collapse_drift_threshold": (0.0, 10.0),
        "recovery_velocity_threshold": (0.0, 10.0),
        "high_drift_threshold": (0.0, 10.0),
        "low_drift_threshold": (0.0, 10.0),
        "optimal_velocity_threshold": (0.0, 10.0),
    },
    "perception_fusion": {
        "stt_confidence_degraded_threshold": (0.0, 1.0),
        "tts_drift_mild_threshold": (0.0, 1.0),
        "tts_drift_severe_threshold": (0.0, 1.0),
        "dead_air_warn_timeout_ms": (100, 60000),
        "dead_air_timeout_ms": (100, 120000),
        "connection_loss_warn_timeout_ms": (100, 120000),
        "connection_loss_timeout_ms": (100, 300000),
        "ivr_hard_threshold": (0.0, 1.0),
        "voicemail_hard_threshold": (0.0, 1.0),
    },
}


class ConfigValidator:
    """
    Validates all registered configs against known schemas and constraints.
    
    Does NOT modify any config files — read-only validation.
    """

    def __init__(self):
        self.issues: List[ConfigIssue] = []

    def validate_all(self) -> List[ConfigIssue]:
        """
        Run all validations against all registered configs.
        
        Returns:
            List of ConfigIssue objects. Empty = all clear.
        """
        self.issues = []
        
        for name in get_all_names():
            self._validate_one(name)
        
        return self.issues

    def validate_one(self, name: str) -> List[ConfigIssue]:
        """
        Validate a single config by name.
        
        Returns:
            List of ConfigIssue objects for this config only.
        """
        self.issues = []
        self._validate_one(name)
        return self.issues

    def _validate_one(self, name: str) -> None:
        """Run all checks on a single config."""
        entry = get_registry_entry(name)
        path = get_file_path(name)

        # Check 1: File exists
        if not os.path.exists(path):
            self.issues.append(ConfigIssue(
                name, ConfigIssue.SEVERITY_ERROR,
                f"File not found: {path}"
            ))
            return

        # Check 2: File is parseable
        data = self._try_parse(name, path, entry["format"])
        if data is None:
            return  # parse error already recorded

        # Check 3: Required top-level keys
        self._check_required_keys(name, data, entry.get("top_keys", []))

        # Check 4: Type constraints
        self._check_types(name, data)

        # Check 5: Value range constraints
        self._check_ranges(name, data)

        # Check 6: Non-empty check
        if not data:
            self.issues.append(ConfigIssue(
                name, ConfigIssue.SEVERITY_WARNING,
                "Config file is empty or contains no data"
            ))

    def _try_parse(self, name: str, path: str, fmt: str) -> Optional[dict]:
        """Try to parse a config file. Returns data or None."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                if fmt == "json":
                    return json.load(f)
                elif fmt == "yaml":
                    if not HAS_YAML:
                        self.issues.append(ConfigIssue(
                            name, ConfigIssue.SEVERITY_ERROR,
                            "PyYAML not installed, cannot validate YAML configs"
                        ))
                        return None
                    return yaml.safe_load(f)
                else:
                    self.issues.append(ConfigIssue(
                        name, ConfigIssue.SEVERITY_ERROR,
                        f"Unknown format: {fmt}"
                    ))
                    return None
        except (json.JSONDecodeError, Exception) as e:
            self.issues.append(ConfigIssue(
                name, ConfigIssue.SEVERITY_ERROR,
                f"Parse error: {e}"
            ))
            return None

    def _check_required_keys(self, name: str, data: dict, required_keys: List[str]) -> None:
        """Check that expected top-level keys exist."""
        if not isinstance(data, dict):
            self.issues.append(ConfigIssue(
                name, ConfigIssue.SEVERITY_WARNING,
                f"Expected dict at top level, got {type(data).__name__}"
            ))
            return

        for key in required_keys:
            if key not in data:
                self.issues.append(ConfigIssue(
                    name, ConfigIssue.SEVERITY_WARNING,
                    f"Expected top-level key '{key}' not found",
                    field=key
                ))

    def _check_types(self, name: str, data: dict) -> None:
        """Check type constraints for known fields."""
        if name not in TYPE_CONSTRAINTS or not isinstance(data, dict):
            return

        for field, expected_type in TYPE_CONSTRAINTS[name].items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    self.issues.append(ConfigIssue(
                        name, ConfigIssue.SEVERITY_ERROR,
                        f"Type mismatch: '{field}' expected {expected_type}, "
                        f"got {type(data[field]).__name__}",
                        field=field
                    ))

    def _check_ranges(self, name: str, data: dict) -> None:
        """Check value range constraints for numeric fields."""
        if name not in RANGE_CONSTRAINTS or not isinstance(data, dict):
            return

        for field, (min_val, max_val) in RANGE_CONSTRAINTS[name].items():
            if field in data:
                val = data[field]
                if isinstance(val, (int, float)):
                    if val < min_val or val > max_val:
                        self.issues.append(ConfigIssue(
                            name, ConfigIssue.SEVERITY_WARNING,
                            f"Value out of range: '{field}' = {val}, "
                            f"expected [{min_val}, {max_val}]",
                            field=field
                        ))

    # ─── Reporting ──────────────────────────────────────────────────────

    def report(self) -> str:
        """Return human-readable validation report."""
        if not self.issues:
            return "CONFIG VALIDATION: ALL CLEAR (0 issues across 27 configs)"

        lines = [f"CONFIG VALIDATION: {len(self.issues)} issue(s) found"]
        lines.append("=" * 60)

        errors = [i for i in self.issues if i.severity == ConfigIssue.SEVERITY_ERROR]
        warnings = [i for i in self.issues if i.severity == ConfigIssue.SEVERITY_WARNING]
        infos = [i for i in self.issues if i.severity == ConfigIssue.SEVERITY_INFO]

        if errors:
            lines.append(f"\nERRORS ({len(errors)}):")
            for issue in errors:
                lines.append(f"  {issue}")

        if warnings:
            lines.append(f"\nWARNINGS ({len(warnings)}):")
            for issue in warnings:
                lines.append(f"  {issue}")

        if infos:
            lines.append(f"\nINFO ({len(infos)}):")
            for issue in infos:
                lines.append(f"  {issue}")

        return "\n".join(lines)

    def to_dict(self) -> List[dict]:
        """Return issues as list of dicts for JSON serialization."""
        return [issue.to_dict() for issue in self.issues]

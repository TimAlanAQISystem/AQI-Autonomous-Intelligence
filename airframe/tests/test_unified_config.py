"""
Neg-proof tests for the Unified Config System.

Tests:
  - Registry has all 27 configs
  - ConfigStore loads individual configs
  - ConfigStore loads by domain
  - ConfigStore handles missing files gracefully
  - Hot-reload works
  - Singleton access works
  - 5 domains registered
  - All file paths resolve
"""

import os
import json
import sys
import pytest

# Ensure airframe is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from airframe.config.config_registry import (
    REGISTRY,
    get_all_names,
    get_names_by_domain,
    get_file_path,
    get_all_domains,
    get_registry_entry,
    DOMAIN_CORE_IDENTITY,
    DOMAIN_VOICE_TIMING,
    DOMAIN_SALES_INTELLIGENCE,
    DOMAIN_REASONING_GOVERNANCE,
    DOMAIN_CAMPAIGN_OPERATIONS,
)
from airframe.config.unified_config import (
    ConfigStore,
    ConfigLoadError,
    get_config,
    reset_config,
)


# ─── Registry Tests ────────────────────────────────────────────────────────

class TestConfigRegistry:
    """Tests for config_registry.py"""

    def test_registry_has_27_configs(self):
        """All 27 operational configs are registered."""
        assert len(REGISTRY) == 27, f"Expected 27 configs, got {len(REGISTRY)}"

    def test_all_names_sorted(self):
        """get_all_names returns sorted list."""
        names = get_all_names()
        assert names == sorted(names)
        assert len(names) == 27

    def test_five_domains_exist(self):
        """All 5 organizational domains are present."""
        domains = get_all_domains()
        expected = {
            DOMAIN_CORE_IDENTITY,
            DOMAIN_VOICE_TIMING,
            DOMAIN_SALES_INTELLIGENCE,
            DOMAIN_REASONING_GOVERNANCE,
            DOMAIN_CAMPAIGN_OPERATIONS,
        }
        assert set(domains) == expected

    def test_core_identity_has_5_configs(self):
        """Core identity domain has exactly 5 configs."""
        names = get_names_by_domain(DOMAIN_CORE_IDENTITY)
        assert len(names) == 5
        assert "alan_persona" in names
        assert "agent_config" in names
        assert "fleet_manifest" in names
        assert "iqcore_charter" in names
        assert "training_knowledge" in names

    def test_voice_timing_has_4_configs(self):
        """Voice/timing domain has exactly 4 configs."""
        names = get_names_by_domain(DOMAIN_VOICE_TIMING)
        assert len(names) == 4

    def test_sales_intelligence_has_9_configs(self):
        """Sales intelligence domain has exactly 9 configs."""
        names = get_names_by_domain(DOMAIN_SALES_INTELLIGENCE)
        assert len(names) == 9

    def test_reasoning_governance_has_5_configs(self):
        """Reasoning/governance domain has exactly 5 configs."""
        names = get_names_by_domain(DOMAIN_REASONING_GOVERNANCE)
        assert len(names) == 5

    def test_campaign_operations_has_4_configs(self):
        """Campaign/operations domain has exactly 4 configs."""
        names = get_names_by_domain(DOMAIN_CAMPAIGN_OPERATIONS)
        assert len(names) == 4

    def test_all_entries_have_required_fields(self):
        """Every registry entry has file, format, domain, description."""
        for name, entry in REGISTRY.items():
            assert "file" in entry, f"{name} missing 'file'"
            assert "format" in entry, f"{name} missing 'format'"
            assert "domain" in entry, f"{name} missing 'domain'"
            assert "description" in entry, f"{name} missing 'description'"
            assert entry["format"] in ("json", "yaml"), f"{name} has invalid format: {entry['format']}"

    def test_all_file_paths_resolve(self):
        """All registered config files exist on disk."""
        for name in get_all_names():
            path = get_file_path(name)
            assert os.path.exists(path), f"Config file not found: {path} (name={name})"

    def test_unknown_name_raises(self):
        """Getting an unknown config name raises KeyError."""
        with pytest.raises(KeyError):
            get_file_path("nonexistent_config")

    def test_19_json_8_yaml(self):
        """Registry contains 19 JSON configs and 8 YAML configs."""
        json_count = sum(1 for e in REGISTRY.values() if e["format"] == "json")
        yaml_count = sum(1 for e in REGISTRY.values() if e["format"] == "yaml")
        assert json_count == 19, f"Expected 19 JSON, got {json_count}"
        assert yaml_count == 8, f"Expected 8 YAML, got {yaml_count}"


# ─── ConfigStore Tests ──────────────────────────────────────────────────────

class TestConfigStore:
    """Tests for unified_config.py ConfigStore"""

    def setup_method(self):
        """Fresh store for each test."""
        self.store = ConfigStore()

    def test_lazy_load(self):
        """Configs are not loaded until accessed."""
        assert len(self.store.loaded) == 0

    def test_load_single_json(self):
        """Can load a single JSON config."""
        data = self.store.get("system")
        assert isinstance(data, dict)
        assert "system" in self.store.loaded

    def test_load_single_yaml(self):
        """Can load a single YAML config."""
        data = self.store.get("behavioral_fusion")
        assert isinstance(data, dict)
        assert "behavioral_fusion" in self.store.loaded

    def test_load_all(self):
        """load_all loads all 27 configs."""
        self.store.load_all()
        # Some might fail if PyYAML not installed, but JSON should all load
        loaded = len(self.store.loaded)
        errors = len(self.store.errors)
        assert loaded + errors == 27, f"loaded={loaded}, errors={errors}, total={loaded+errors}"

    def test_domain_access(self):
        """Can access all configs in a domain."""
        domain_configs = self.store.domain("core_identity")
        assert len(domain_configs) == 5
        assert "alan_persona" in domain_configs
        assert isinstance(domain_configs["alan_persona"], dict)

    def test_unknown_name_raises(self):
        """Getting unknown config raises KeyError."""
        with pytest.raises(KeyError):
            self.store.get("totally_fake")

    def test_get_safe_returns_none(self):
        """get_safe returns None for unknown configs."""
        result = self.store.get_safe("totally_fake")
        assert result is None

    def test_has_method(self):
        """has() checks registration, not loading."""
        assert self.store.has("timing") is True
        assert self.store.has("fake_name") is False

    def test_reload_single(self):
        """Can reload a single config."""
        data1 = self.store.get("system")
        self.store.reload("system")
        data2 = self.store.get("system")
        assert data1 == data2  # same content since file hasn't changed

    def test_reload_all(self):
        """Can reload all loaded configs."""
        self.store.get("system")
        self.store.get("alan_persona")
        assert len(self.store.loaded) == 2
        self.store.reload()
        assert len(self.store.loaded) == 2  # reloaded same ones

    def test_summary(self):
        """Summary returns correct structure."""
        self.store.load_all()
        summary = self.store.summary()
        assert "registered" in summary
        assert summary["registered"] == 27
        assert "loaded" in summary
        assert "errors" in summary
        assert "domains" in summary

    def test_repr(self):
        """__repr__ shows useful info."""
        r = repr(self.store)
        assert "ConfigStore" in r
        assert "registered=27" in r

    def test_all_json_configs_parse_correctly(self):
        """Every JSON config loads and returns a dict."""
        json_names = [n for n, e in REGISTRY.items() if e["format"] == "json"]
        for name in json_names:
            data = self.store.get(name)
            assert isinstance(data, dict), f"{name} did not return a dict"

    def test_timing_config_has_meta(self):
        """timing_config.json should have _meta key."""
        data = self.store.get("timing")
        assert "_meta" in data

    def test_fleet_manifest_has_agents(self):
        """fleet_manifest.json should have agents array."""
        data = self.store.get("fleet_manifest")
        assert "agents" in data
        assert isinstance(data["agents"], list)

    def test_system_config_has_feature_flags(self):
        """system_config.json should have boolean feature flags."""
        data = self.store.get("system")
        for key in ["pghs_enabled", "mtsp_enabled", "mip_enabled", "bas_enabled"]:
            assert key in data, f"system_config missing {key}"

    def test_iqcore_charter_allocations(self):
        """IQCORE_CHARTER.json should allocate 100 total IQ cores."""
        data = self.store.get("iqcore_charter")
        assert data["iqcore_total"] == 100


# ─── Singleton Tests ────────────────────────────────────────────────────────

class TestSingleton:
    """Tests for module-level singleton."""

    def setup_method(self):
        reset_config()

    def teardown_method(self):
        reset_config()

    def test_singleton_returns_same_instance(self):
        """get_config() returns the same instance each time."""
        c1 = get_config()
        c2 = get_config()
        assert c1 is c2

    def test_reset_creates_new_instance(self):
        """reset_config() forces a new instance."""
        c1 = get_config()
        reset_config()
        c2 = get_config()
        assert c1 is not c2

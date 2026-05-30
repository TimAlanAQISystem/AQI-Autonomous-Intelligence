"""
Unified Config Store — single import to access all 27 AQI/Alan configs.

Usage:
    from airframe.config import get_config

    config = get_config()
    timing = config.get("timing")           # dict from timing_config.json
    persona = config.get("alan_persona")    # dict from alan_persona.json
    voice = config.domain("voice_timing")   # dict of all voice/timing configs
    config.reload("timing")                 # hot-reload one config
    config.reload()                         # hot-reload all

Zero interference with production. Config files are READ-ONLY.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from airframe.config.config_registry import (
    REGISTRY,
    get_file_path,
    get_all_names,
    get_names_by_domain,
    get_all_domains,
    get_registry_entry,
)


class ConfigLoadError(Exception):
    """Raised when a config file cannot be loaded."""
    pass


class ConfigStore:
    """
    Central config store. Lazily loads configs on first access, caches them,
    and supports selective or full hot-reload.

    Thread-safety: not guaranteed. For production use, wrap with a lock.
    """

    def __init__(self, auto_load: bool = False):
        """
        Args:
            auto_load: If True, eagerly load all configs on construction.
                       If False (default), load lazily on first get().
        """
        self._cache: Dict[str, dict] = {}
        self._load_times: Dict[str, float] = {}
        self._errors: Dict[str, str] = {}

        if auto_load:
            self.load_all()

    # ─── Core Access ────────────────────────────────────────────────────

    def get(self, name: str) -> dict:
        """
        Get config by logical name. Lazy-loads on first access.

        Args:
            name: Logical config name (e.g., "timing", "alan_persona")

        Returns:
            Parsed config dict.

        Raises:
            KeyError: If name not in registry.
            ConfigLoadError: If file cannot be loaded.
        """
        if name not in REGISTRY:
            raise KeyError(f"Config '{name}' not registered. Known: {get_all_names()}")

        if name not in self._cache:
            self._load_one(name)

        return self._cache[name]

    def get_safe(self, name: str) -> Optional[dict]:
        """
        Like get(), but returns None instead of raising on errors.
        Errors are stored in self.errors for inspection.
        """
        try:
            return self.get(name)
        except (KeyError, ConfigLoadError):
            return None

    def domain(self, domain_name: str) -> Dict[str, dict]:
        """
        Get all configs in a domain as {name: dict}.

        Args:
            domain_name: e.g., "voice_timing", "sales_intelligence"

        Returns:
            Dict mapping config names to their parsed dicts.
        """
        names = get_names_by_domain(domain_name)
        return {name: self.get(name) for name in names}

    def has(self, name: str) -> bool:
        """Check if a config name is registered (not whether it's loaded)."""
        return name in REGISTRY

    # ─── Reload ─────────────────────────────────────────────────────────

    def reload(self, name: Optional[str] = None) -> None:
        """
        Hot-reload config(s) from disk.

        Args:
            name: If provided, reload just this config.
                  If None, reload ALL configs that are currently cached.
        """
        if name:
            if name not in REGISTRY:
                raise KeyError(f"Config '{name}' not registered.")
            self._cache.pop(name, None)
            self._errors.pop(name, None)
            self._load_one(name)
        else:
            cached_names = list(self._cache.keys())
            self._cache.clear()
            self._errors.clear()
            self._load_times.clear()
            for n in cached_names:
                self._load_one(n)

    def load_all(self) -> None:
        """Eagerly load all registered configs."""
        for name in get_all_names():
            try:
                self._load_one(name)
            except ConfigLoadError:
                pass  # error stored in self._errors

    # ─── Inspection ─────────────────────────────────────────────────────

    @property
    def loaded(self) -> List[str]:
        """Names of currently loaded configs."""
        return sorted(self._cache.keys())

    @property
    def errors(self) -> Dict[str, str]:
        """Configs that failed to load: {name: error_message}."""
        return dict(self._errors)

    @property
    def load_times(self) -> Dict[str, float]:
        """Load timestamps: {name: epoch}."""
        return dict(self._load_times)

    @property
    def names(self) -> List[str]:
        """All registered config names."""
        return get_all_names()

    @property
    def domains(self) -> List[str]:
        """All domain names."""
        return get_all_domains()

    def summary(self) -> Dict[str, Any]:
        """Return summary dict for diagnostics."""
        return {
            "registered": len(REGISTRY),
            "loaded": len(self._cache),
            "errors": len(self._errors),
            "domains": {
                d: len(get_names_by_domain(d))
                for d in get_all_domains()
            },
            "error_details": dict(self._errors) if self._errors else None,
        }

    # ─── Internals ──────────────────────────────────────────────────────

    def _load_one(self, name: str) -> None:
        """Load a single config by name. Stores in cache or errors."""
        entry = get_registry_entry(name)
        path = get_file_path(name)

        if not os.path.exists(path):
            msg = f"Config file not found: {path}"
            self._errors[name] = msg
            raise ConfigLoadError(msg)

        try:
            with open(path, "r", encoding="utf-8") as f:
                if entry["format"] == "json":
                    data = json.load(f)
                elif entry["format"] == "yaml":
                    if not HAS_YAML:
                        msg = f"PyYAML not installed. Cannot load YAML config: {name}"
                        self._errors[name] = msg
                        raise ConfigLoadError(msg)
                    data = yaml.safe_load(f)
                else:
                    msg = f"Unknown format '{entry['format']}' for config: {name}"
                    self._errors[name] = msg
                    raise ConfigLoadError(msg)

            self._cache[name] = data
            self._load_times[name] = time.time()
            self._errors.pop(name, None)

        except (json.JSONDecodeError, yaml.YAMLError if HAS_YAML else Exception) as e:
            msg = f"Parse error in {path}: {e}"
            self._errors[name] = msg
            raise ConfigLoadError(msg)

    def __repr__(self):
        return (
            f"<ConfigStore registered={len(REGISTRY)} "
            f"loaded={len(self._cache)} errors={len(self._errors)}>"
        )


# ─── Module-Level Singleton ────────────────────────────────────────────────

_singleton: Optional[ConfigStore] = None


def get_config(auto_load: bool = False) -> ConfigStore:
    """
    Get the singleton ConfigStore.

    Args:
        auto_load: If True AND this is the first call, eagerly load all configs.

    Returns:
        The shared ConfigStore instance.
    """
    global _singleton
    if _singleton is None:
        _singleton = ConfigStore(auto_load=auto_load)
    return _singleton


def reset_config() -> None:
    """Reset the singleton. Useful for testing."""
    global _singleton
    _singleton = None

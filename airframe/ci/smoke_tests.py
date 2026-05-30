"""
Smoke Tests — lightweight production health checks.

These tests verify the AQI/Alan system is correctly configured
and all critical files exist, WITHOUT starting any services or
making any calls.

Usage:
    python -m airframe.ci.smoke_tests
    python airframe/ci/smoke_tests.py
"""

import json
import os
import sys
from typing import List, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check(label: str, condition: bool, detail: str = "") -> Tuple[str, bool, str]:
    """Single smoke test check."""
    return (label, condition, detail)


def run_smoke_tests() -> List[Tuple[str, bool, str]]:
    """
    Run all smoke tests. Returns list of (label, passed, detail).
    """
    results = []
    
    # ─── 1. Critical Production Files Exist ─────────────────────────
    critical_files = [
        ("Relay Server", "aqi_conversation_relay_server.py"),
        ("Business AI", "agent_alan_business_ai.py"),
        ("Control API", "control_api_fixed.py"),
        ("STT Engine", "aqi_stt_engine.py"),
        ("State Machine", "alan_state_machine.py"),
        ("Conv Intelligence", "conversational_intelligence.py"),
        ("Immune System", "chatbot_immune_system.py"),
        ("Deep Layer", "aqi_deep_layer.py"),
        ("Personality Engine", "personality_engine.py"),
        ("Cross-Call Intel", "cross_call_intelligence.py"),
        ("Timing Loader", "timing_loader.py"),
        ("Call Lifecycle FSM", "call_lifecycle_fsm.py"),
        ("Call Type Classifier", "call_type_classifier.py"),
    ]
    
    for label, filename in critical_files:
        path = os.path.join(ROOT, filename)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        results.append(check(
            f"File: {label}",
            exists and size > 100,
            f"{filename} ({size:,} bytes)" if exists else f"{filename} MISSING"
        ))
    
    # ─── 2. Organs Directory ────────────────────────────────────────
    organs_dir = os.path.join(ROOT, "organs_v4_1")
    if os.path.isdir(organs_dir):
        organ_files = [f for f in os.listdir(organs_dir) if f.endswith(".py")]
        results.append(check(
            "Organs Directory",
            len(organ_files) >= 10,
            f"organs_v4_1/ has {len(organ_files)} .py files"
        ))
    else:
        results.append(check("Organs Directory", False, "organs_v4_1/ MISSING"))
    
    # ─── 3. All Config Files Parseable ──────────────────────────────
    json_configs = [
        "timing_config.json", "alan_persona.json", "agent_alan_config.json",
        "master_closer_config.json", "behavior_adaptation_config.json",
        "evolution_config.json", "crg_config.json", "adaptive_closing_strategy.json",
        "rapport_layer.json", "outcome_detection_config.json",
        "call_outcome_confidence_config.json", "predictive_intent_model.json",
        "outcome_attribution_config.json", "review_aggregation_config.json",
        "system_config.json", "fleet_manifest.json", "IQCORE_CHARTER.json",
        "REGIME_ENGINE_CONFIG_SCHEMA.json", "training_knowledge_distilled.json",
    ]
    
    for cfg in json_configs:
        path = os.path.join(ROOT, cfg)
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
            results.append(check(f"Parse: {cfg}", True, "OK"))
        except Exception as e:
            results.append(check(f"Parse: {cfg}", False, str(e)))
    
    yaml_configs = [
        "aqi_modes.yaml", "behavioral_fusion_config.yaml",
        "campaign_autopilot_config.yaml", "classifier_config.yaml",
        "field_campaign_config.yaml", "inbound_silence_config.yaml",
        "perception_fusion_config.yaml", "voice_sensitizer_config.yaml",
    ]
    
    if HAS_YAML:
        for cfg in yaml_configs:
            path = os.path.join(ROOT, cfg)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
                results.append(check(f"Parse: {cfg}", True, "OK"))
            except Exception as e:
                results.append(check(f"Parse: {cfg}", False, str(e)))
    else:
        results.append(check("YAML Parser", False, "PyYAML not installed"))
    
    # ─── 4. .env File Exists ────────────────────────────────────────
    env_path = os.path.join(ROOT, ".env")
    results.append(check(
        "Environment File",
        os.path.exists(env_path),
        ".env found" if os.path.exists(env_path) else ".env MISSING"
    ))
    
    # ─── 5. Virtual Environment ─────────────────────────────────────
    venv_path = os.path.join(ROOT, ".venv")
    results.append(check(
        "Virtual Environment",
        os.path.isdir(venv_path),
        ".venv/ found" if os.path.isdir(venv_path) else ".venv/ MISSING"
    ))
    
    # ─── 6. Monorepo Tests Available ────────────────────────────────
    monorepo_test = os.path.join(ROOT, "alan-voice-system", "tests")
    has_tests = os.path.isdir(monorepo_test)
    results.append(check(
        "Monorepo Tests Dir",
        has_tests,
        "alan-voice-system/tests/ found" if has_tests else "MISSING"
    ))
    
    # ─── 7. Tunnel Sync File ────────────────────────────────────────
    tunnel_file = os.path.join(ROOT, "tunnel_sync.py")
    results.append(check(
        "Tunnel Sync",
        os.path.exists(tunnel_file),
        "tunnel_sync.py found" if os.path.exists(tunnel_file) else "MISSING"
    ))
    
    return results


def main() -> int:
    """Print smoke test report and return exit code."""
    print("=" * 60)
    print("  AQI/ALAN — SMOKE TESTS")
    print("=" * 60)
    print(f"  Root: {ROOT}")
    print()
    
    results = run_smoke_tests()
    
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    
    for label, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label:<30} {detail}")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed, {len(results)} total")
    
    if failed == 0:
        print("  ALL SMOKE TESTS PASSED")
    else:
        print("  SOME SMOKE TESTS FAILED")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

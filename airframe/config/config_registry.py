"""
Config Registry — maps logical names to file paths, formats, and domains.

All 27 operational config files are registered here.
Data/state files (merchant_profiles.json, health_dump.json, etc.) are excluded.
"""

import os

# Base directory — workspace root where all configs live
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Domain groupings for logical organization
DOMAIN_CORE_IDENTITY = "core_identity"
DOMAIN_VOICE_TIMING = "voice_timing"
DOMAIN_SALES_INTELLIGENCE = "sales_intelligence"
DOMAIN_REASONING_GOVERNANCE = "reasoning_governance"
DOMAIN_CAMPAIGN_OPERATIONS = "campaign_operations"

# Master registry: logical_name → {path, format, domain, description}
REGISTRY = {
    # ─── Core Identity Domain ───────────────────────────────────────────
    "alan_persona": {
        "file": "alan_persona.json",
        "format": "json",
        "domain": DOMAIN_CORE_IDENTITY,
        "description": "Alan's persona: identity, tone, opening logic, objection handling, knowledge blocks",
        "top_keys": ["identity", "role", "tone", "opening_logic", "objection_handling", "knowledge_blocks"],
    },
    "agent_config": {
        "file": "agent_alan_config.json",
        "format": "json",
        "domain": DOMAIN_CORE_IDENTITY,
        "description": "Master agent config: Twilio webhook, control API endpoint, conversation/LLM config",
        "top_keys": ["name", "description", "constitution_id", "persona_profile_id", "steward_id",
                      "control_host", "control_port", "twilio_voice_webhook_url", "conversation_config"],
    },
    "fleet_manifest": {
        "file": "fleet_manifest.json",
        "format": "json",
        "domain": DOMAIN_CORE_IDENTITY,
        "description": "Fleet roster: Alan, RSE, Agent X — roles, statuses, config refs",
        "top_keys": ["fleet_name", "version", "founded", "chairman", "agents"],
    },
    "iqcore_charter": {
        "file": "IQCORE_CHARTER.json",
        "format": "json",
        "domain": DOMAIN_CORE_IDENTITY,
        "description": "IQ Core allocation: 60 Alan (operator), 40 Agent X (governor)",
        "top_keys": ["version", "generated_at", "iqcore_total", "actors"],
    },
    "training_knowledge": {
        "file": "training_knowledge_distilled.json",
        "format": "json",
        "domain": DOMAIN_CORE_IDENTITY,
        "description": "Distilled sales training: prospecting, execution, discovery, closing techniques",
        "top_keys": ["source", "note", "distilled_techniques"],
    },

    # ─── Voice & Timing Domain ──────────────────────────────────────────
    "timing": {
        "file": "timing_config.json",
        "format": "json",
        "domain": DOMAIN_VOICE_TIMING,
        "description": "Master timing mixing board: all pacing/speed/delay with min/max bounds",
        "top_keys": ["_meta", "voice_pacing"],
    },
    "voice_sensitizer": {
        "file": "voice_sensitizer_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_VOICE_TIMING,
        "description": "Voice identity integrity: drift detection, prosody ranges, corrective TTS actions",
        "top_keys": ["thresholds", "actions", "tts_adjustments"],
    },
    "inbound_silence": {
        "file": "inbound_silence_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_VOICE_TIMING,
        "description": "Silence detection: RMS thresholds, dead air timeouts, connection loss actions",
        "top_keys": ["thresholds", "actions", "sampling_rate"],
    },
    "perception_fusion": {
        "file": "perception_fusion_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_VOICE_TIMING,
        "description": "Perception fusion thresholds: STT confidence, TTS drift, dead air, IVR/VM",
        "top_keys": ["stt_confidence_degraded_threshold", "tts_drift_mild_threshold",
                      "tts_drift_severe_threshold", "dead_air_warn_timeout_ms", "dead_air_timeout_ms",
                      "connection_loss_warn_timeout_ms", "connection_loss_timeout_ms",
                      "ivr_hard_threshold", "voicemail_hard_threshold"],
    },

    # ─── Sales Intelligence Domain ──────────────────────────────────────
    "master_closer": {
        "file": "master_closer_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Sales trajectory state machine: warming/cooling/stalling/escalating with weights",
        "top_keys": ["trajectory", "objection_weighting"],
    },
    "closing_strategy": {
        "file": "adaptive_closing_strategy.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Closing styles (direct/consultative/relational) with triggers and approved lines",
        "top_keys": ["styles"],
    },
    "behavior_adaptation": {
        "file": "behavior_adaptation_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Merchant archetypes → behavioral parameters (tone, pacing, formality, assertiveness)",
        "top_keys": ["archetypes"],
    },
    "evolution": {
        "file": "evolution_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "How call outcomes adjust trajectory weights, archetype confidence, closing bias",
        "top_keys": ["signals", "adjustments"],
    },
    "outcome_detection": {
        "file": "outcome_detection_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Call outcome detection via keyword/signal matching (statement, engaged, decline, hangup)",
        "top_keys": ["outcome_indicators", "engagement_score_weights"],
    },
    "outcome_confidence": {
        "file": "call_outcome_confidence_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Confidence scoring: weighted factors, thresholds, objection clarity mapping",
        "top_keys": ["weights", "thresholds", "objection_clarity_mapping"],
    },
    "predictive_intent": {
        "file": "predictive_intent_model.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Intent detection: phrases/regex → classified intents with priority scores",
        "top_keys": ["intents"],
    },
    "outcome_attribution": {
        "file": "outcome_attribution_config.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Post-call attribution: archetype_fit, trajectory, objection, closing with weights",
        "top_keys": ["dimensions"],
    },
    "rapport_layer": {
        "file": "rapport_layer.json",
        "format": "json",
        "domain": DOMAIN_SALES_INTELLIGENCE,
        "description": "Rapport phrases: micro/deep acknowledgments, off-topic handling, pivot lines",
        "top_keys": ["active_listening", "off_topic_resilience"],
    },

    # ─── Reasoning & Governance Domain ──────────────────────────────────
    "crg": {
        "file": "crg_config.json",
        "format": "json",
        "domain": DOMAIN_REASONING_GOVERNANCE,
        "description": "Controlled Reasoning Generation: novelty levels 0-3 with creativity constraints",
        "top_keys": ["novelty"],
    },
    "aqi_modes": {
        "file": "aqi_modes.yaml",
        "format": "yaml",
        "domain": DOMAIN_REASONING_GOVERNANCE,
        "description": "Constitutional mode registry: production/instructor_pending/idle with transitions",
        "top_keys": ["modes"],
    },
    "regime_schema": {
        "file": "REGIME_ENGINE_CONFIG_SCHEMA.json",
        "format": "json",
        "domain": DOMAIN_REASONING_GOVERNANCE,
        "description": "JSON Schema (draft-07) for Regime Engine live configs",
        "top_keys": ["$schema", "title", "description", "type", "properties"],
    },
    "review_aggregation": {
        "file": "review_aggregation_config.json",
        "format": "json",
        "domain": DOMAIN_REASONING_GOVERNANCE,
        "description": "Multi-window review aggregation: short/mid/long term with promotion criteria",
        "top_keys": ["layers", "influence", "trend_threshold", "long_term_promotion",
                      "aggregation_policy", "dimensions", "logging"],
    },
    "system": {
        "file": "system_config.json",
        "format": "json",
        "domain": DOMAIN_REASONING_GOVERNANCE,
        "description": "System feature flags: PGHS, MTSP, MIP, BAS toggles + latency budgets",
        "top_keys": ["pghs_enabled", "pghs_budget_ms", "mtsp_enabled", "mip_enabled",
                      "bas_enabled", "retention_days", "latency_budgets", "experiment", "shadow_mode"],
    },

    # ─── Campaign & Operations Domain ───────────────────────────────────
    "campaign_autopilot": {
        "file": "campaign_autopilot_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_CAMPAIGN_OPERATIONS,
        "description": "Autopilot: daily call limits, batch sizes, readiness thresholds, cooldown",
        "top_keys": ["min_readiness_score", "max_daily_calls", "micro_batch_size",
                      "cooldown_on_score_drop", "recheck_interval_calls"],
    },
    "field_campaign": {
        "file": "field_campaign_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_CAMPAIGN_OPERATIONS,
        "description": "Multi-phase field campaign: phases 1-4 with escalating calls and success criteria",
        "top_keys": ["phase_1_preflight"],
    },
    "classifier": {
        "file": "classifier_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_CAMPAIGN_OPERATIONS,
        "description": "CallTypeClassifier: human/IVR/voicemail detection thresholds and weights",
        "top_keys": ["thresholds", "weights"],
    },
    "behavioral_fusion": {
        "file": "behavioral_fusion_config.yaml",
        "format": "yaml",
        "domain": DOMAIN_CAMPAIGN_OPERATIONS,
        "description": "Behavioral fusion thresholds: stall/viscosity/collapse/recovery velocity",
        "top_keys": ["stall_velocity_threshold", "stall_turn_threshold", "high_viscosity_threshold",
                      "high_objection_threshold", "collapse_drift_threshold",
                      "recovery_velocity_threshold", "high_drift_threshold", "low_drift_threshold",
                      "optimal_velocity_threshold"],
    },
}


def get_all_names():
    """Return sorted list of all registered config names."""
    return sorted(REGISTRY.keys())


def get_names_by_domain(domain):
    """Return sorted list of config names in a given domain."""
    return sorted(name for name, entry in REGISTRY.items() if entry["domain"] == domain)


def get_file_path(name):
    """Return absolute file path for a registered config name."""
    if name not in REGISTRY:
        raise KeyError(f"Config '{name}' not found in registry. Known: {get_all_names()}")
    return os.path.join(BASE_DIR, REGISTRY[name]["file"])


def get_all_domains():
    """Return sorted list of all domain names."""
    return sorted(set(entry["domain"] for entry in REGISTRY.values()))


def get_registry_entry(name):
    """Return the full registry entry for a config name."""
    if name not in REGISTRY:
        raise KeyError(f"Config '{name}' not found in registry. Known: {get_all_names()}")
    return REGISTRY[name]

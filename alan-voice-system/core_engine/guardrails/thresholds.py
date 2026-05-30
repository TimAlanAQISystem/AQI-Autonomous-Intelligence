# thresholds.py
"""
Central definition of hard thresholds and timing limits.
These are Alan's non-negotiable physical constants.

All values come directly from the Human-First Voice Spec.
"""


class Thresholds:
    """Immutable threshold constants for Alan's voice system."""

    # ── HACO: Overlap Detection ──
    INTENT_DB_RISE = 6.0        # dB rise to detect intent-to-speak
    INTENT_WINDOW_MS = 40       # Window for intent detection
    FLOOR_DB_RISE = 10.0        # dB rise to detect merchant-floor
    FLOOR_WINDOW_MS = 120       # Sustained window for floor detection

    # ── HACO: Confidence Gating ──
    ASR_CONF = 0.82             # Minimum ASR confidence to commit
    SEMANTIC_CONF = 0.78        # Minimum semantic confidence to commit

    # ── Turn-Taking: Yield Timing ──
    MAX_YIELD_MS = 220          # Max time to yield after MERCHANT_FLOOR (≈ one syllable)
    FAST_YIELD_MS = 180         # Target yield for angry/hard interruptions

    # ── System Health: Fallback Triggers ──
    JITTER_FALLBACK_MS = 35     # Jitter above this → DISCRETE mode
    LATENCY_FALLBACK_MS = 240   # Latency above this → shorter phrases

    # ── MSCO: Prosody Limits ──
    F0_DEVIATION_CALM_HZ = 18   # ±Hz for calm scenarios
    F0_DEVIATION_ENERGETIC_HZ = 28  # ±Hz for energetic scenarios
    PROSODY_DEVIATION_PCT = 25  # Max % deviation from anchor
    MAX_RETURN_TIME_S = 1.2     # Max seconds to return to anchor

    # ── MSCO: Mirroring Budget ──
    MAX_TEMPO_MIRROR_PCT = 12   # Max tempo increase in response to human
    MAX_AMP_MIRROR_PCT = 8      # Max amplitude increase in response to human

    # ── Nuance Budget (per minute) ──
    SIGNATURE_PHRASES_PER_MIN = 2
    TONAL_FLOURISHES_PER_MIN = 1
    MICRO_PAUSES_PER_MIN = 1

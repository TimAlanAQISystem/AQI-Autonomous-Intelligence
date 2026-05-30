# Thresholds — Hard Constants

All values are non-negotiable. They come directly from the Human-First Voice Spec.

## HACO: Overlap Detection

| Threshold | Value | Purpose |
|-----------|-------|---------|
| INTENT_DB_RISE | 6.0 dB | Detect intent-to-speak cue |
| INTENT_WINDOW_MS | 40 ms | Window for intent detection |
| FLOOR_DB_RISE | 10.0 dB | Detect merchant has floor |
| FLOOR_WINDOW_MS | 120 ms | Sustained window for floor |

## HACO: Confidence Gating

| Threshold | Value | Purpose |
|-----------|-------|---------|
| ASR_CONF | 0.82 | Minimum ASR confidence to commit |
| SEMANTIC_CONF | 0.78 | Minimum semantic confidence to commit |

## Turn-Taking: Yield Timing

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_YIELD_MS | 220 ms | Max yield after MERCHANT_FLOOR (≈ one syllable) |
| FAST_YIELD_MS | 180 ms | Target for angry/hard interruptions |

## System Health: Fallback Triggers

| Threshold | Value | Purpose |
|-----------|-------|---------|
| JITTER_FALLBACK_MS | 35 ms | Switch to DISCRETE mode |
| LATENCY_FALLBACK_MS | 240 ms | Use shorter phrases |

## MSCO: Prosody Limits

| Threshold | Value | Purpose |
|-----------|-------|---------|
| F0_DEVIATION_CALM | ±18 Hz | Calm scenario deviation |
| F0_DEVIATION_ENERGETIC | ±28 Hz | Energetic scenario deviation |
| PROSODY_DEVIATION_PCT | 25% | Max deviation from anchor |
| MAX_RETURN_TIME_S | 1.2 s | Max time to return to anchor |

## MSCO: Mirroring Budget

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_TEMPO_MIRROR_PCT | 12% | Max tempo increase (mirror human) |
| MAX_AMP_MIRROR_PCT | 8% | Max amplitude increase (mirror human) |

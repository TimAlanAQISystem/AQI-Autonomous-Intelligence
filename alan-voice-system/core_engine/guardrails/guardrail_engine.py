# guardrail_engine.py
"""
Guardrail engine – enforces hard rules and triggers fallbacks.

Evaluates:
  - System health (jitter, latency)
  - Confidence (ASR, semantic)
  - Emotion (sentiment score)
  - Prosody compliance (f0, tempo, amplitude)

Returns recommendations for demeanor state changes.
"""

from .thresholds import Thresholds


class GuardrailEngine:
    """Enforces Alan's hard rules — no exceptions, no overrides."""

    def __init__(self):
        self.thresholds = Thresholds

    def evaluate_system_health(self, jitter_ms: float, latency_ms: float) -> dict:
        """
        Evaluate network/system health and recommend fallbacks.

        Returns:
            Dictionary with:
            - to_discrete: bool (switch to DISCRETE mode)
            - simplify_speech: bool (use shorter phrases)
        """
        return {
            "to_discrete": jitter_ms > self.thresholds.JITTER_FALLBACK_MS,
            "simplify_speech": latency_ms > self.thresholds.LATENCY_FALLBACK_MS,
        }

    def evaluate_confidence(self, asr_conf: float, semantic_conf: float) -> dict:
        """
        Evaluate ASR and semantic confidence.

        Returns:
            Dictionary with:
            - low_confidence: bool
            - require_confirm: bool
        """
        low = not (
            asr_conf >= self.thresholds.ASR_CONF
            and semantic_conf >= self.thresholds.SEMANTIC_CONF
        )
        return {
            "low_confidence": low,
            "require_confirm": low,
        }

    def evaluate_emotion(self, sentiment_score: float) -> dict:
        """
        Evaluate human emotional state.

        Args:
            sentiment_score: Negative values = upset, positive = calm/happy.

        Returns:
            Dictionary with:
            - high_emotion: bool
        """
        return {"high_emotion": sentiment_score < -0.5}

    def evaluate_prosody_compliance(
        self,
        current_f0: float,
        anchor_f0: float,
        f0_deviation_limit: float,
        tempo_mirror_pct: float,
        amp_mirror_pct: float,
    ) -> dict:
        """
        Check if MSCO output is within prosody constraints.

        Returns:
            Dictionary with:
            - f0_in_bounds: bool
            - tempo_in_bounds: bool
            - amp_in_bounds: bool
            - all_compliant: bool
        """
        f0_ok = abs(current_f0 - anchor_f0) <= f0_deviation_limit
        tempo_ok = tempo_mirror_pct <= self.thresholds.MAX_TEMPO_MIRROR_PCT
        amp_ok = amp_mirror_pct <= self.thresholds.MAX_AMP_MIRROR_PCT

        return {
            "f0_in_bounds": f0_ok,
            "tempo_in_bounds": tempo_ok,
            "amp_in_bounds": amp_ok,
            "all_compliant": f0_ok and tempo_ok and amp_ok,
        }

    def evaluate_yield_timing(self, yield_delay_ms: float, scenario_max_ms: float = None) -> dict:
        """
        Check if Alan yielded within acceptable time.

        Args:
            yield_delay_ms: Actual delay from merchant_floor to yield.
            scenario_max_ms: Optional scenario-specific max (defaults to MAX_YIELD_MS).

        Returns:
            Dictionary with:
            - within_limit: bool
            - delay_ms: float
            - limit_ms: float
        """
        limit = scenario_max_ms or self.thresholds.MAX_YIELD_MS
        return {
            "within_limit": yield_delay_ms <= limit,
            "delay_ms": yield_delay_ms,
            "limit_ms": limit,
        }

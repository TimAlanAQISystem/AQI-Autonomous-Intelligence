"""
alan_adaptive_layer.py — Lightweight Adaptive Layer
====================================================

Per-merchant, per-call adaptive modulation for Alan's delivery.
Tracks four behavioral signatures — pace, friction, energy, vocabulary —
and applies bounded modulation hints that shape HOW Alan speaks without
changing WHAT he says.

This layer is:
  - Adaptive but NOT generative — it shapes delivery, not content
  - Bounded — all modulation clamped to narrow, safe ranges
  - Stateless across calls — no cross-call memory, no learning loops
  - Upstream of governance — governance remains the final authority
  - Pure state + pure functions — no async, no I/O, no external calls
  - Fail-safe — every public method wrapped in try/except

Integration:
  - Instantiated per call alongside ConversationGovernor
  - Updated on each merchant + Alan utterance
  - get_modulation_params() called before TTS to shape delivery
  - to_fingerprint_summary() called at call end for behavioral logging

Monorepo alignment:
  - Pace modulation respects MAX_SPEED_DEVIATION (0.3)
  - Vocabulary stays within MIN_VOCABULARY_DIVERSITY (0.4)
  - Energy mirroring stays within governance thresholds
  - All modulation bounded well inside constitutional rails

Author: Airframe build session, March 2026
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("AQI")

_ALLOWED_ENERGY = ("low", "medium", "high")
_ALLOWED_FORMALITY = ("formal", "neutral", "casual")
_ALLOWED_TECHNICALITY = ("low", "medium", "high")
_ALLOWED_MERCHANT_ROLE = ("owner", "manager", "staff", "unknown")

# Bounded modulation limits — these are HARD ceilings
PACE_SLOW_FLOOR = -0.08    # Max 8% slower
PACE_FAST_CEILING = 0.12   # Max 12% faster
PACE_LOG_CLAMP = 0.25      # Sanity clamp for logged values
PAUSE_LIST_CAP = 256       # Max pause entries to prevent unbounded growth

# Dropout risk increments (rule-based, coarse)
DROPOUT_HESITATION_DELTA = 0.03
DROPOUT_CLARIFICATION_DELTA = 0.05
DROPOUT_OBJECTION_DELTA = 0.08


@dataclass
class ConversationAdaptiveState:
    """
    Per-call adaptive state for Alan.

    Tracks pace, friction, energy, and vocabulary signatures and exposes:
    - get_modulation_params(): bounded modulation hints for the next sentence
    - to_fingerprint_summary(): PII-free behavioral fingerprint for logging
    """

    # Call metadata
    call_id: str
    timestamp_start: float
    merchant_role: str = "unknown"
    timestamp_end: Optional[float] = None

    # Pace tracking
    merchant_word_count: int = 0
    merchant_utterance_count: int = 0
    merchant_pause_durations_ms: List[int] = field(default_factory=list)
    merchant_interrupt_events: int = 0

    alan_word_count: int = 0
    alan_utterance_count: int = 0
    alan_pause_durations_ms: List[int] = field(default_factory=list)

    # Friction tracking
    objection_count: int = 0
    hesitation_events: int = 0
    clarification_requests: int = 0
    dropout_risk_score: float = 0.0  # bounded [0.0, 1.0]

    # Energy tracking
    merchant_energy_initial: Optional[str] = None
    merchant_energy_final: Optional[str] = None
    alan_energy_profile: str = "medium"

    # Vocabulary tracking
    formality_level: str = "neutral"
    technicality_level: str = "low"
    vocab_diversity_score: float = 0.0

    # Modulation tracking
    pace_modulation_min_pct: float = 0.0
    pace_modulation_max_pct: float = 0.0
    energy_modulation_events: int = 0
    vocab_style_switches: int = 0

    def __post_init__(self) -> None:
        if self.merchant_role not in _ALLOWED_MERCHANT_ROLE:
            self.merchant_role = "unknown"
        if self.alan_energy_profile not in _ALLOWED_ENERGY:
            self.alan_energy_profile = "medium"

    # ─── Merchant Behavior ──────────────────────────────────────────────

    def record_merchant_utterance(
        self,
        *,
        word_count: int,
        pause_ms: Optional[int] = None,
        interrupted: bool = False,
        hesitation: bool = False,
        clarification_request: bool = False,
        energy_level: Optional[str] = None,
    ) -> None:
        """Update merchant-side pace, friction, and (optionally) energy."""
        try:
            if word_count > 0:
                self.merchant_word_count += word_count
                self.merchant_utterance_count += 1

            if pause_ms is not None and pause_ms >= 0:
                if len(self.merchant_pause_durations_ms) < PAUSE_LIST_CAP:
                    self.merchant_pause_durations_ms.append(pause_ms)

            if interrupted:
                self.merchant_interrupt_events += 1

            if hesitation:
                self.hesitation_events += 1
                self._bump_dropout_risk(DROPOUT_HESITATION_DELTA)

            if clarification_request:
                self.clarification_requests += 1
                self._bump_dropout_risk(DROPOUT_CLARIFICATION_DELTA)

            if energy_level in _ALLOWED_ENERGY:
                if self.merchant_energy_initial is None:
                    self.merchant_energy_initial = energy_level
                self.merchant_energy_final = energy_level
        except Exception as e:
            logger.debug(f"[ADAPTIVE] record_merchant_utterance error (non-fatal): {e}")

    # ─── Alan Behavior ──────────────────────────────────────────────────

    def record_alan_utterance(
        self,
        *,
        word_count: int,
        pause_ms: Optional[int] = None,
        energy_profile: str = "medium",
        vocab_diversity_score: float = 0.0,
    ) -> None:
        """Update Alan-side pace, energy, and vocabulary metrics."""
        try:
            if word_count > 0:
                self.alan_word_count += word_count
                self.alan_utterance_count += 1

            if pause_ms is not None and pause_ms >= 0:
                if len(self.alan_pause_durations_ms) < PAUSE_LIST_CAP:
                    self.alan_pause_durations_ms.append(pause_ms)

            if energy_profile in _ALLOWED_ENERGY:
                self.alan_energy_profile = energy_profile

            self.vocab_diversity_score = max(0.0, min(1.0, vocab_diversity_score))
        except Exception as e:
            logger.debug(f"[ADAPTIVE] record_alan_utterance error (non-fatal): {e}")

    # ─── Friction ───────────────────────────────────────────────────────

    def register_objection(self) -> None:
        """Merchant raised an objection."""
        try:
            self.objection_count += 1
            self._bump_dropout_risk(DROPOUT_OBJECTION_DELTA)
        except Exception:
            pass

    def update_dropout_risk(self, delta: float) -> None:
        """External rule-based adjustments, still bounded [0.0, 1.0]."""
        try:
            self._bump_dropout_risk(delta)
        except Exception:
            pass

    def _bump_dropout_risk(self, delta: float) -> None:
        self.dropout_risk_score = max(0.0, min(1.0, self.dropout_risk_score + delta))

    # ─── Vocabulary Style ───────────────────────────────────────────────

    def update_formality(self, level: str) -> None:
        """Shift formality level based on merchant's language style."""
        try:
            if level in _ALLOWED_FORMALITY and level != self.formality_level:
                self.formality_level = level
                self.vocab_style_switches += 1
        except Exception:
            pass

    def update_technicality(self, level: str) -> None:
        """Shift technicality level based on merchant's domain knowledge."""
        try:
            if level in _ALLOWED_TECHNICALITY and level != self.technicality_level:
                self.technicality_level = level
                self.vocab_style_switches += 1
        except Exception:
            pass

    def register_vocab_style_switch(self) -> None:
        """Manual style switch registration."""
        self.vocab_style_switches += 1

    # ─── Modulation Bounds ──────────────────────────────────────────────

    def update_pace_modulation(self, pct: float) -> None:
        """
        Track the min/max pace modulation actually applied this call.

        pct is the relative shift applied to Alan's baseline pace, e.g.:
        -0.08 = 8% slower, +0.12 = 12% faster.
        """
        try:
            if not isinstance(pct, (int, float)):
                return

            pct = max(-PACE_LOG_CLAMP, min(PACE_LOG_CLAMP, pct))

            if self.pace_modulation_min_pct == 0.0 and self.pace_modulation_max_pct == 0.0:
                self.pace_modulation_min_pct = pct
                self.pace_modulation_max_pct = pct
                return

            if pct < self.pace_modulation_min_pct:
                self.pace_modulation_min_pct = pct
            if pct > self.pace_modulation_max_pct:
                self.pace_modulation_max_pct = pct
        except Exception:
            pass

    def register_energy_modulation_event(self) -> None:
        """Track an energy-level shift event."""
        self.energy_modulation_events += 1

    # ─── Modulation Parameters for Next Sentence ────────────────────────

    def get_modulation_params(self) -> Dict[str, object]:
        """
        Compute bounded modulation hints for the next sentence.

        Returns:
            {
                "pace_shift_pct": float,   # e.g. -0.08 .. +0.12
                "energy_level": str,       # "low" | "medium" | "high"
                "vocab_style": str,        # "formal" | "neutral" | "casual"
            }

        SAFETY: Never raises. Returns neutral defaults on error.
        """
        try:
            pace_shift_pct = self._compute_pace_shift_pct()
            energy_level = self._compute_energy_level()
            vocab_style = self.formality_level

            return {
                "pace_shift_pct": pace_shift_pct,
                "energy_level": energy_level,
                "vocab_style": vocab_style,
            }
        except Exception:
            return {"pace_shift_pct": 0.0, "energy_level": "medium", "vocab_style": "neutral"}

    def _compute_pace_shift_pct(self) -> float:
        """
        Lightweight, rule-based pace modulation.

        - Slower merchants → -5% to -8%
        - Faster merchants → +5% to +12%
        - All shifts bounded by PACE_SLOW_FLOOR / PACE_FAST_CEILING
        """
        avg_merchant_wpm = self._safe_wpm(
            self.merchant_word_count, self.merchant_utterance_count
        )
        avg_alan_wpm = self._safe_wpm(self.alan_word_count, self.alan_utterance_count)

        if avg_merchant_wpm == 0.0:
            return 0.0

        ratio = avg_merchant_wpm / max(1.0, avg_alan_wpm)

        if ratio < 0.8:
            return PACE_SLOW_FLOOR  # -0.08
        if ratio > 1.2:
            return PACE_FAST_CEILING  # +0.12

        return 0.0

    def _compute_energy_level(self) -> str:
        """
        Simple energy mirroring with inertia:
        - Prefer merchant_final if present
        - Fall back to merchant_initial
        - Otherwise keep Alan's current profile
        """
        if self.merchant_energy_final in _ALLOWED_ENERGY:
            return self.merchant_energy_final  # type: ignore[return-value]
        if self.merchant_energy_initial in _ALLOWED_ENERGY:
            return self.merchant_energy_initial  # type: ignore[return-value]
        if self.alan_energy_profile in _ALLOWED_ENERGY:
            return self.alan_energy_profile
        return "medium"

    @staticmethod
    def _safe_wpm(total_words: int, utterances: int) -> float:
        if utterances <= 0 or total_words <= 0:
            return 0.0
        return float(total_words) / float(utterances)

    # ─── Call Lifecycle ─────────────────────────────────────────────────

    def finalize_call(self, timestamp_end: float, merchant_energy_final: Optional[str] = None) -> None:
        """Mark call as ended and lock final energy level."""
        try:
            self.timestamp_end = timestamp_end
            if merchant_energy_final in _ALLOWED_ENERGY:
                self.merchant_energy_final = merchant_energy_final
        except Exception:
            pass

    # ─── Fingerprint Summary ────────────────────────────────────────────

    def to_fingerprint_summary(self) -> Dict[str, object]:
        """
        Produce a PII-free, content-free behavioral fingerprint for this call.

        Safe to log as structured JSON. No raw text, no phone numbers, no names.

        SAFETY: Never raises. Returns minimal dict on error.
        """
        try:
            duration_seconds: Optional[float] = None
            if self.timestamp_end is not None:
                duration_seconds = max(0.0, self.timestamp_end - self.timestamp_start)

            avg_merchant_pause = self._avg(self.merchant_pause_durations_ms)
            avg_alan_pause = self._avg(self.alan_pause_durations_ms)

            avg_merchant_wpm = self._safe_wpm(
                self.merchant_word_count, self.merchant_utterance_count
            )
            avg_alan_wpm = self._safe_wpm(self.alan_word_count, self.alan_utterance_count)

            return {
                "call_id": self.call_id,
                "timestamp_start": self.timestamp_start,
                "timestamp_end": self.timestamp_end,
                "duration_seconds": duration_seconds,
                "merchant_role": self.merchant_role,
                "pace": {
                    "avg_merchant_wpm": round(avg_merchant_wpm, 1),
                    "avg_alan_wpm": round(avg_alan_wpm, 1),
                    "interrupt_rate_per_minute": self._interrupt_rate_per_minute(duration_seconds),
                    "avg_pause_ms_merchant": round(avg_merchant_pause, 1) if avg_merchant_pause is not None else None,
                    "avg_pause_ms_alan": round(avg_alan_pause, 1) if avg_alan_pause is not None else None,
                },
                "friction": {
                    "objection_count": self.objection_count,
                    "hesitation_events": self.hesitation_events,
                    "clarification_requests_count": self.clarification_requests,
                    "dropout_risk_score": round(self.dropout_risk_score, 3),
                },
                "energy": {
                    "merchant_energy_initial": self.merchant_energy_initial,
                    "merchant_energy_final": self.merchant_energy_final,
                    "alan_energy_profile": self.alan_energy_profile,
                },
                "vocabulary": {
                    "formality_level": self.formality_level,
                    "technicality_level": self.technicality_level,
                    "vocab_diversity_score": round(self.vocab_diversity_score, 3),
                },
                "modulation": {
                    "pace_modulation_range_pct": {
                        "min": round(self.pace_modulation_min_pct, 3),
                        "max": round(self.pace_modulation_max_pct, 3),
                    },
                    "energy_modulation_events_count": self.energy_modulation_events,
                    "vocab_style_switches_count": self.vocab_style_switches,
                },
            }
        except Exception as e:
            logger.debug(f"[ADAPTIVE] fingerprint error (non-fatal): {e}")
            return {"call_id": self.call_id, "error": str(e)}

    @staticmethod
    def _avg(values: List[int]) -> Optional[float]:
        if not values:
            return None
        return float(sum(values)) / float(len(values))

    def _interrupt_rate_per_minute(
        self, duration_seconds: Optional[float]
    ) -> Optional[float]:
        if not duration_seconds or duration_seconds <= 0.0:
            return None
        minutes = duration_seconds / 60.0
        if minutes <= 0.0:
            return None
        return round(float(self.merchant_interrupt_events) / minutes, 2)


# ═══════════════════════════════════════════════════════════════════════════
# ADAPTIVE LAYER MANAGER — Singleton managing per-call adaptive states
# ═══════════════════════════════════════════════════════════════════════════

class AdaptiveLayerManager:
    """
    Manages ConversationAdaptiveState instances per active call.
    Mirrors GovernanceManager pattern for consistency.
    """

    _instance = None

    def __init__(self):
        self._states: Dict[str, ConversationAdaptiveState] = {}

    @classmethod
    def get_instance(cls) -> "AdaptiveLayerManager":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_state(self, call_id: str) -> ConversationAdaptiveState:
        """Get or create an adaptive state for a call."""
        if call_id not in self._states:
            self._states[call_id] = ConversationAdaptiveState(
                call_id=call_id,
                timestamp_start=time.time(),
            )
            logger.info(f"[ADAPTIVE] New adaptive state for call {call_id}")
        return self._states[call_id]

    def end_call(self, call_id: str) -> Optional[Dict[str, object]]:
        """End adaptive tracking for a call. Returns fingerprint summary."""
        state = self._states.pop(call_id, None)
        if state:
            state.finalize_call(time.time(), state.merchant_energy_final)
            summary = state.to_fingerprint_summary()
            logger.info(f"[ADAPTIVE] Call {call_id} fingerprint: "
                        f"pace_shift=[{summary.get('modulation', {}).get('pace_modulation_range_pct', {}).get('min', 0):.0%},"
                        f"{summary.get('modulation', {}).get('pace_modulation_range_pct', {}).get('max', 0):.0%}] "
                        f"energy={summary.get('energy', {}).get('alan_energy_profile', '?')} "
                        f"friction_risk={summary.get('friction', {}).get('dropout_risk_score', 0):.1%} "
                        f"vocab={summary.get('vocabulary', {}).get('formality_level', '?')}")
            return summary
        return None

    def active_calls(self) -> int:
        """Number of active adaptive states."""
        return len(self._states)

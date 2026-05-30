# haco_engine.py
"""
Hyper-Auditory Continuity Organ (HACO)
Alan's "ears" – continuous listening, overlap detection, confidence gating.

Core behavior:
  - Always listening: full-duplex, Alan listens while speaking
  - Overlap detection: early cues (in-breaths, consonant onsets, energy rises)
  - Echo suppression: subtracts Alan's own voice from input
  - Confidence gating: ASR + semantic confidence must both be high

Hard thresholds:
  - Intent-to-Speak: +6 dB rise over baseline within 40 ms
  - Merchant-Floor: +10 dB sustained for 120 ms or ASR tokens start
  - Max yield time: 180–220 ms after MERCHANT_FLOOR
  - ASR confidence: >= 0.82
  - Semantic confidence: >= 0.78
"""

from .overlap_detection import OverlapDetector


class HACOEngine:
    """Alan's ears — continuous listening with overlap detection and confidence gating."""

    def __init__(self, thresholds: dict):
        """
        Args:
            thresholds: Dictionary with keys:
                - intent_db_rise: float (default 6.0)
                - intent_window_ms: int (default 40)
                - floor_db_rise: float (default 10.0)
                - floor_window_ms: int (default 120)
        """
        self.overlap_detector = OverlapDetector(
            intent_db_rise=thresholds.get("intent_db_rise", 6.0),
            intent_window_ms=thresholds.get("intent_window_ms", 40),
            floor_db_rise=thresholds.get("floor_db_rise", 10.0),
            floor_window_ms=thresholds.get("floor_window_ms", 120),
        )
        self.asr_conf_threshold = 0.82
        self.semantic_conf_threshold = 0.78

    def process_audio_frame(self, frame: dict) -> dict:
        """
        Process a single audio frame from the human side.

        Args:
            frame: Dictionary with at least 'energy_db' key.

        Returns:
            Dictionary with:
            - intent_to_speak: bool
            - merchant_floor: bool
            - energy_db: float
        """
        result = self.overlap_detector.update(frame)
        result["energy_db"] = frame.get("energy_db", 0.0)
        return result

    def should_commit(self, asr_conf: float, semantic_conf: float) -> bool:
        """
        Decide whether it's safe to commit to an interpretation.
        If either confidence is below threshold, return False (require confirmation).

        Args:
            asr_conf: ASR confidence score (0.0 – 1.0).
            semantic_conf: Semantic confidence score (0.0 – 1.0).

        Returns:
            True if both confidences are above threshold.
        """
        return (
            asr_conf >= self.asr_conf_threshold
            and semantic_conf >= self.semantic_conf_threshold
        )

    def get_thresholds(self) -> dict:
        """Return current confidence thresholds for tracing."""
        return {
            "asr_conf_threshold": self.asr_conf_threshold,
            "semantic_conf_threshold": self.semantic_conf_threshold,
        }

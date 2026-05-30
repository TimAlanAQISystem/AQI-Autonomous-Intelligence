# overlap_detection.py
"""
Energy-based overlap detection for intent-to-speak and merchant-floor.

Thresholds:
  - Intent-to-Speak: energy rises +intent_db_rise dB within intent_window_ms
  - Merchant-Floor: energy rises +floor_db_rise dB sustained for floor_window_ms
"""

import collections


class OverlapDetector:
    """Detects human intent-to-speak and merchant-floor from audio energy."""

    def __init__(
        self,
        intent_db_rise: float,
        intent_window_ms: int,
        floor_db_rise: float,
        floor_window_ms: int,
    ):
        self.intent_db_rise = intent_db_rise
        self.intent_window_ms = intent_window_ms
        self.floor_db_rise = floor_db_rise
        self.floor_window_ms = floor_window_ms

        # Rolling baseline (moving average of recent energy)
        self._baseline_window = collections.deque(maxlen=50)
        self._baseline_db = 0.0

        # Sustained energy tracking for merchant-floor
        self._sustained_start_ms = None
        self._sustained_db = 0.0

        # Frame counter (simulated time)
        self._frame_count = 0
        self._frame_duration_ms = 20  # 20 ms per frame (standard)

    def update(self, frame: dict) -> dict:
        """
        Update internal state with a new audio frame and compute:
        - intent_to_speak: bool
        - merchant_floor: bool

        Args:
            frame: Dictionary with 'energy_db' key.

        Returns:
            Dictionary with intent_to_speak and merchant_floor booleans.
        """
        energy_db = frame.get("energy_db", 0.0)
        self._frame_count += 1
        current_time_ms = self._frame_count * self._frame_duration_ms

        # Update baseline
        self._baseline_window.append(energy_db)
        self._baseline_db = (
            sum(self._baseline_window) / len(self._baseline_window)
            if self._baseline_window
            else 0.0
        )

        rise = energy_db - self._baseline_db

        # Intent-to-Speak: sudden rise above threshold
        intent_to_speak = rise >= self.intent_db_rise

        # Merchant-Floor: sustained rise above floor threshold
        merchant_floor = False
        if rise >= self.floor_db_rise:
            if self._sustained_start_ms is None:
                self._sustained_start_ms = current_time_ms
                self._sustained_db = energy_db
            else:
                duration = current_time_ms - self._sustained_start_ms
                if duration >= self.floor_window_ms:
                    merchant_floor = True
        else:
            # Reset sustained tracking if energy drops
            self._sustained_start_ms = None
            self._sustained_db = 0.0

        return {
            "intent_to_speak": intent_to_speak,
            "merchant_floor": merchant_floor,
        }

    def reset(self):
        """Reset detector state."""
        self._baseline_window.clear()
        self._baseline_db = 0.0
        self._sustained_start_ms = None
        self._sustained_db = 0.0
        self._frame_count = 0

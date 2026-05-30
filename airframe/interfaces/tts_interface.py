"""
TTS Interface — bridges MSCO (Mean Spectral Crossover Optimization) concepts
from the alan-voice-system monorepo to production OpenAI TTS parameters.

MSCO Concepts (monorepo):
  - anchor_f0: fundamental frequency anchor
  - max_deviation: allowed spectral deviation (0.0-1.0)
  - mirroring_factor: prosodic mirroring intensity (0.0-1.0)
  - drift severity levels: mild → moderate → severe → catastrophic

Production Reality:
  - OpenAI Realtime API TTS with 'alloy' voice
  - Speed parameter (0.25 - 4.0)
  - Streaming chunks via ConversationRelay WebSocket
  - Voice sensitizer config for drift detection

This adapter creates a clean boundary. New code programs against
TTSInterface; the implementation maps to production parameters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DriftSeverity(Enum):
    """Voice drift severity levels aligned with monorepo thresholds."""
    NONE = "none"
    MILD = "mild"           # < 0.15 deviation
    MODERATE = "moderate"   # 0.15 - 0.30
    SEVERE = "severe"       # 0.30 - 0.50
    CATASTROPHIC = "catastrophic"  # > 0.50


@dataclass
class TTSParameters:
    """
    Parameters for TTS synthesis, bridging MSCO concepts to production.
    
    MSCO concept → Production mapping:
      anchor_f0 → voice selection (alloy = baritone anchor)
      max_deviation → speed bounds (lower deviation = tighter speed range)
      mirroring_factor → speed adjustment toward merchant's pace
      speed → OpenAI TTS speed parameter (0.25 - 4.0)
    """
    voice: str = "alloy"
    speed: float = 1.0
    speed_min: float = 0.8
    speed_max: float = 1.3
    mirroring_factor: float = 0.0
    anchor_f0: float = 120.0      # Hz, reference only
    max_deviation: float = 0.15   # MSCO deviation limit
    
    def constrain_speed(self, target_speed: float) -> float:
        """Apply MSCO-derived speed constraints."""
        return max(self.speed_min, min(self.speed_max, target_speed))

    def apply_mirroring(self, merchant_pace: float) -> float:
        """
        Apply prosodic mirroring. Blend current speed toward merchant's pace.
        
        Args:
            merchant_pace: Estimated merchant speaking rate (0.5 - 2.0)
        
        Returns:
            Adjusted speed (still bounded by min/max).
        """
        blended = self.speed + self.mirroring_factor * (merchant_pace - self.speed)
        return self.constrain_speed(blended)


class TTSInterface(ABC):
    """
    Abstract TTS interface. Production implementation wraps OpenAI Realtime API.
    Test implementations can mock without network calls.
    """

    @abstractmethod
    def synthesize(self, text: str, params: Optional[TTSParameters] = None) -> bytes:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to speak.
            params: TTS parameters (voice, speed, mirroring).
        
        Returns:
            Audio bytes (format depends on implementation).
        """
        ...

    @abstractmethod
    def get_drift_severity(self) -> DriftSeverity:
        """
        Check current voice drift severity.
        
        Returns:
            Current drift level based on MSCO/voice_sensitizer thresholds.
        """
        ...

    @abstractmethod
    def reset_anchor(self) -> None:
        """Reset the spectral anchor to baseline."""
        ...


class MockTTSAdapter(TTSInterface):
    """
    Mock TTS adapter for testing. No network calls.
    Tracks synthesize calls and simulates drift.
    """
    
    def __init__(self):
        self.calls: list = []
        self._drift = DriftSeverity.NONE
        self._params = TTSParameters()

    def synthesize(self, text: str, params: Optional[TTSParameters] = None) -> bytes:
        p = params or self._params
        self.calls.append({"text": text, "params": p})
        # Return stub audio (4 bytes = minimal WAV-like stub)
        return b"\x00\x00\x00\x00"

    def get_drift_severity(self) -> DriftSeverity:
        return self._drift

    def set_drift(self, severity: DriftSeverity) -> None:
        """Test helper: set drift level."""
        self._drift = severity

    def reset_anchor(self) -> None:
        self._drift = DriftSeverity.NONE
        self.calls.clear()

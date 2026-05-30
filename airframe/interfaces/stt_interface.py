"""
STT Interface — bridges HACO (Harmonic Adaptive Crossover Optimization) concepts
from the alan-voice-system monorepo to production STT implementations.

HACO Concepts (monorepo):
  - confidence_threshold: minimum confidence to accept transcription (0.0-1.0)
  - overlap_detection: detect when merchant and Alan speak simultaneously
  - energy_threshold: minimum audio energy to trigger processing
  - adaptive crossover: switch between STT backends based on conditions

Production Reality:
  - Primary: Groq Whisper (fast, via relay server deepgram/groq pipeline)
  - Fallback: OpenAI Whisper
  - Twilio Media Streams → base64 audio chunks → STT engine
  - aqi_stt_engine.py handles chunking, silence detection, confidence gating

This adapter creates a clean boundary. New code programs against
STTInterface; the implementation maps to production STT engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TranscriptionConfidence(Enum):
    """Confidence levels aligned with HACO thresholds."""
    HIGH = "high"           # >= 0.85
    MEDIUM = "medium"       # 0.60 - 0.85
    LOW = "low"             # 0.30 - 0.60
    REJECTED = "rejected"   # < 0.30


@dataclass
class TranscriptionResult:
    """
    Result from STT processing.
    
    HACO concept → Production mapping:
      confidence → Whisper confidence score
      is_final → Groq streaming final flag
      overlap_detected → concurrent speech detection from HACO
      energy_level → RMS energy from audio chunk
    """
    text: str
    confidence: float = 0.0
    is_final: bool = False
    overlap_detected: bool = False
    energy_level: float = 0.0
    language: str = "en"
    
    @property
    def confidence_level(self) -> TranscriptionConfidence:
        """Map numeric confidence to HACO-aligned level."""
        if self.confidence >= 0.85:
            return TranscriptionConfidence.HIGH
        elif self.confidence >= 0.60:
            return TranscriptionConfidence.MEDIUM
        elif self.confidence >= 0.30:
            return TranscriptionConfidence.LOW
        else:
            return TranscriptionConfidence.REJECTED

    @property
    def is_acceptable(self) -> bool:
        """Whether this transcription meets minimum quality for processing."""
        return self.confidence_level != TranscriptionConfidence.REJECTED


@dataclass
class STTParameters:
    """
    Parameters for STT processing, bridging HACO concepts to production.
    
    HACO concept → Production mapping:
      confidence_threshold → min confidence to forward to AI
      energy_threshold → min RMS to start STT (silence gating)
      overlap_timeout_ms → how long to wait during overlap before acting
      min_buffer_ms → minimum audio buffer before sending to Whisper
    """
    confidence_threshold: float = 0.30
    energy_threshold: float = 0.01
    overlap_timeout_ms: int = 500
    min_buffer_ms: int = 200
    max_buffer_ms: int = 5000
    language: str = "en"


class STTInterface(ABC):
    """
    Abstract STT interface. Production implementation wraps Groq/OpenAI Whisper.
    Test implementations can mock without network calls.
    """

    @abstractmethod
    def process_audio(self, audio_chunk: bytes, params: Optional[STTParameters] = None) -> Optional[TranscriptionResult]:
        """
        Process an audio chunk through STT.
        
        Args:
            audio_chunk: Raw audio bytes (mu-law, 8kHz from Twilio).
            params: STT parameters (thresholds, buffer settings).
        
        Returns:
            TranscriptionResult if transcription available, None if buffering.
        """
        ...

    @abstractmethod
    def get_overlap_status(self) -> bool:
        """
        Check if overlap (simultaneous speech) is currently detected.
        
        Returns:
            True if HACO overlap detection is active.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset STT state (buffers, overlap detection)."""
        ...

    @abstractmethod
    def get_buffer_duration_ms(self) -> int:
        """Get current audio buffer duration in milliseconds."""
        ...


class MockSTTAdapter(STTInterface):
    """
    Mock STT adapter for testing. No network calls.
    Returns pre-configured transcriptions.
    """
    
    def __init__(self):
        self._results: List[TranscriptionResult] = []
        self._result_index: int = 0
        self._overlap: bool = False
        self._buffer_ms: int = 0
        self._chunks_received: int = 0
        self._params = STTParameters()

    def queue_result(self, text: str, confidence: float = 0.95, is_final: bool = True) -> None:
        """Test helper: queue a transcription result to return."""
        self._results.append(TranscriptionResult(
            text=text,
            confidence=confidence,
            is_final=is_final,
            overlap_detected=self._overlap,
        ))

    def process_audio(self, audio_chunk: bytes, params: Optional[STTParameters] = None) -> Optional[TranscriptionResult]:
        self._chunks_received += 1
        self._buffer_ms += 20  # ~20ms per chunk at 8kHz
        
        if self._result_index < len(self._results):
            result = self._results[self._result_index]
            self._result_index += 1
            self._buffer_ms = 0
            return result
        return None

    def get_overlap_status(self) -> bool:
        return self._overlap

    def set_overlap(self, status: bool) -> None:
        """Test helper: set overlap status."""
        self._overlap = status

    def reset(self) -> None:
        self._results.clear()
        self._result_index = 0
        self._overlap = False
        self._buffer_ms = 0
        self._chunks_received = 0

    def get_buffer_duration_ms(self) -> int:
        return self._buffer_ms

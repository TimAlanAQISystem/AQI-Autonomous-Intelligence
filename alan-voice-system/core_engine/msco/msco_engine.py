# msco_engine.py
"""
Melodic Speech Continuity Organ (MSCO)
Alan's "throat" – continuous voice with governed prosody.

Core behavior:
  - Continuous carrier: words are formant modulations on stable airflow
  - Anchor f0: each scenario defines a fundamental frequency that never drifts
  - Simple contours: gentle rises/falls over phrases, within bounds
  - Breath envelope: soft, human-like breathing

Hard constraints:
  - f0 deviation: ±18 Hz (calm), ±28 Hz (energetic)
  - Prosody deviation: max 25% from anchor; return within 1.2 s
  - Mirroring budget: max 12% tempo increase, 8% amplitude increase
"""

from .prosody_constraints import ProsodyConstraints


class MSCOEngine:
    """Alan's throat — generates governed, continuous speech."""

    def __init__(self, scenario_profile: str):
        """
        Initialize MSCO with a scenario profile (e.g., 'calm', 'energetic').

        Args:
            scenario_profile: One of the defined prosody profiles.
        """
        self.scenario_profile = scenario_profile
        self.constraints = ProsodyConstraints.from_profile(scenario_profile)
        self.current_f0 = self.constraints.anchor_f0
        self.mirroring_budget = self.constraints.initial_mirroring_budget()
        self._deviation_start_time = None
        self._current_tempo_mirror = 0.0
        self._current_amp_mirror = 0.0

    def generate_utterance(self, text: str, state_context: dict) -> dict:
        """
        Generate a continuous utterance for the given text, respecting:
        - anchor f0
        - prosody deviation limits
        - mirroring budget
        - nuance budget (via state_context)

        Args:
            text: The text to speak.
            state_context: Dictionary with demeanor state, nuance budget, etc.

        Returns:
            Dictionary with utterance metadata including:
            - text: the spoken text
            - f0: the fundamental frequency used
            - tempo_adjustment_pct: tempo mirror applied
            - amp_adjustment_pct: amplitude mirror applied
            - within_constraints: bool
        """
        f0 = self._compute_f0(state_context)
        tempo_adj = self._current_tempo_mirror
        amp_adj = self._current_amp_mirror

        within = self._check_constraints(f0, tempo_adj, amp_adj)

        return {
            "text": text,
            "f0": f0,
            "tempo_adjustment_pct": tempo_adj,
            "amp_adjustment_pct": amp_adj,
            "within_constraints": within,
            "scenario_profile": self.scenario_profile,
        }

    def apply_mirroring_pressure(self, tempo_pressure: float, amplitude_pressure: float):
        """
        Adjust internal targets in response to human tempo/amplitude,
        without exceeding mirroring budget.

        Args:
            tempo_pressure: Requested tempo increase percentage.
            amplitude_pressure: Requested amplitude increase percentage.
        """
        max_tempo = self.constraints.max_tempo_mirror_pct
        max_amp = self.constraints.max_amp_mirror_pct

        self._current_tempo_mirror = min(tempo_pressure, max_tempo)
        self._current_amp_mirror = min(amplitude_pressure, max_amp)

    def reset_mirroring(self):
        """Return mirroring adjustments to zero (anchor reset)."""
        self._current_tempo_mirror = 0.0
        self._current_amp_mirror = 0.0

    def get_state(self) -> dict:
        """Return current MSCO state for tracing/logging."""
        return {
            "current_f0": self.current_f0,
            "tempo_mirror_pct": self._current_tempo_mirror,
            "amp_mirror_pct": self._current_amp_mirror,
            "anchor_f0": self.constraints.anchor_f0,
            "profile": self.scenario_profile,
        }

    # ── Internal ──

    def _compute_f0(self, state_context: dict) -> float:
        """Compute f0 for current utterance, clamped to deviation limits."""
        base = self.constraints.anchor_f0
        deviation = self.constraints.f0_deviation_hz
        # In a real implementation, contour shaping would modulate f0;
        # for now, return anchor (within ±deviation)
        return max(base - deviation, min(base + deviation, self.current_f0))

    def _check_constraints(self, f0: float, tempo_pct: float, amp_pct: float) -> bool:
        """Verify all constraints are satisfied."""
        c = self.constraints
        if abs(f0 - c.anchor_f0) > c.f0_deviation_hz:
            return False
        if tempo_pct > c.max_tempo_mirror_pct:
            return False
        if amp_pct > c.max_amp_mirror_pct:
            return False
        return True

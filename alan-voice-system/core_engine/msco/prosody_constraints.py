# prosody_constraints.py
"""
Prosody constraints for MSCO – anchor f0, deviation limits, mirroring budget.

Hard constraints from the spec:
  - f0 deviation: ±18 Hz (calm), ±28 Hz (energetic)
  - Prosody deviation: max 25% in pitch/tempo/amplitude from anchor
  - Max return time: 1.2 s to anchor
  - Mirroring budget: 12% tempo, 8% amplitude
"""


class ProsodyConstraints:
    """Immutable prosody constraint set for a given scenario profile."""

    def __init__(
        self,
        anchor_f0: float,
        f0_deviation_hz: float,
        prosody_deviation_pct: float,
        max_return_time_s: float,
        max_tempo_mirror_pct: float,
        max_amp_mirror_pct: float,
    ):
        self.anchor_f0 = anchor_f0
        self.f0_deviation_hz = f0_deviation_hz
        self.prosody_deviation_pct = prosody_deviation_pct
        self.max_return_time_s = max_return_time_s
        self.max_tempo_mirror_pct = max_tempo_mirror_pct
        self.max_amp_mirror_pct = max_amp_mirror_pct

    @classmethod
    def from_profile(cls, profile: str) -> "ProsodyConstraints":
        """
        Factory for scenario profiles.

        Supported profiles:
        - "calm": warm mid-range, tight deviation (±18 Hz)
        - "energetic": slightly higher, wider deviation (±28 Hz)
        """
        profiles = {
            "calm": cls(
                anchor_f0=150.0,
                f0_deviation_hz=18.0,
                prosody_deviation_pct=25.0,
                max_return_time_s=1.2,
                max_tempo_mirror_pct=12.0,
                max_amp_mirror_pct=8.0,
            ),
            "energetic": cls(
                anchor_f0=165.0,
                f0_deviation_hz=28.0,
                prosody_deviation_pct=25.0,
                max_return_time_s=1.2,
                max_tempo_mirror_pct=12.0,
                max_amp_mirror_pct=8.0,
            ),
        }

        if profile not in profiles:
            raise ValueError(
                f"Unknown prosody profile: '{profile}'. "
                f"Available: {list(profiles.keys())}"
            )
        return profiles[profile]

    def initial_mirroring_budget(self) -> dict:
        """Return a fresh mirroring budget dictionary."""
        return {
            "tempo_pct_remaining": self.max_tempo_mirror_pct,
            "amp_pct_remaining": self.max_amp_mirror_pct,
        }

    def __repr__(self) -> str:
        return (
            f"ProsodyConstraints(anchor_f0={self.anchor_f0}, "
            f"deviation=±{self.f0_deviation_hz}Hz, "
            f"max_return={self.max_return_time_s}s)"
        )

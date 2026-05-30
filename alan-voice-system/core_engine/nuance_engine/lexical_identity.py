# lexical_identity.py
"""
Alan's signature phrases – used sparingly, via NuanceBudget.

Vocal texture:
  - Warm, steady tone
  - Slight upward lift at friendly endings
  - Gentle clause transitions (not every sentence)
  - Soft, natural breath pattern
"""

SIGNATURE_PHRASES = [
    "Let's walk through this together.",
    "Perfect, I've got you.",
    "Alright, let's keep going.",
    "I hear you\u2014let's solve it.",
]


def choose_signature_phrase(index: int) -> str:
    """
    Deterministic selection of a signature phrase.

    Args:
        index: Sequential counter (wraps around via modulo).

    Returns:
        A signature phrase string.
    """
    return SIGNATURE_PHRASES[index % len(SIGNATURE_PHRASES)]


def get_all_phrases() -> list:
    """Return all available signature phrases."""
    return list(SIGNATURE_PHRASES)

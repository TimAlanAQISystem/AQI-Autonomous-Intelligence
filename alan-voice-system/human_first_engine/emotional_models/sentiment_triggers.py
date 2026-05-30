# sentiment_triggers.py
"""
Sentiment detection triggers for emotional state tracking.

Used to determine when Alan should enter DE_ESCALATE mode.
"""


class SentimentTriggers:
    """Detects emotional signals from human speech."""

    # Words/phrases that indicate frustration or anger
    FRUSTRATION_MARKERS = [
        "no", "listen", "stop", "wait", "hold on",
        "that's not", "i said", "you're not listening",
        "wrong", "not what i", "come on", "seriously",
    ]

    # Words/phrases that indicate confusion
    CONFUSION_MARKERS = [
        "what", "i don't understand", "huh", "what do you mean",
        "confused", "lost", "say that again",
    ]

    # Words/phrases that indicate satisfaction
    POSITIVE_MARKERS = [
        "great", "perfect", "thanks", "sounds good",
        "that works", "yes", "exactly", "right",
    ]

    @classmethod
    def analyze_transcript(cls, transcript: str) -> dict:
        """
        Analyze a transcript snippet for emotional signals.

        Returns:
            Dictionary with:
            - sentiment_score: float (-1.0 to 1.0)
            - frustration_detected: bool
            - confusion_detected: bool
            - positive_detected: bool
            - markers_found: list of matched markers
        """
        text = transcript.lower().strip()
        markers_found = []

        frustration = 0
        for marker in cls.FRUSTRATION_MARKERS:
            if marker in text:
                frustration += 1
                markers_found.append(("frustration", marker))

        confusion = 0
        for marker in cls.CONFUSION_MARKERS:
            if marker in text:
                confusion += 1
                markers_found.append(("confusion", marker))

        positive = 0
        for marker in cls.POSITIVE_MARKERS:
            if marker in text:
                positive += 1
                markers_found.append(("positive", marker))

        # Compute sentiment score
        total = frustration + confusion + positive
        if total == 0:
            score = 0.0  # Neutral
        else:
            score = (positive - frustration - confusion * 0.5) / total

        return {
            "sentiment_score": max(-1.0, min(1.0, score)),
            "frustration_detected": frustration > 0,
            "confusion_detected": confusion > 0,
            "positive_detected": positive > 0,
            "markers_found": markers_found,
        }

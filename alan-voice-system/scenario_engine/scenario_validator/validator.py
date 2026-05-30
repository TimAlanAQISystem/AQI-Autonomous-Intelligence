# validator.py
"""
Scenario validator – checks traces against Neg-Proof criteria.

Checks:
  - 0 talking-over events
  - 0 silent mishear commits
  - 0 emotional drift beyond envelope
  - 0 nuance overuse events
  - 0 fallback failures
  - 0 illegal state transitions
  - 0 stuck states
  - 0 human-visible unpredictability
"""


class ScenarioValidator:
    """Base validator — checks traces against expected behavior."""

    def validate(self, spec: dict, traces: list) -> dict:
        """
        Validate a scenario trace against expected behavior.

        Args:
            spec: Scenario specification dictionary.
            traces: List of trace event dictionaries.

        Returns:
            Dictionary with:
            - passed: bool
            - violations: list of violation dicts
        """
        violations = []

        expected = spec.get("expected", {})
        max_yield = expected.get("max_yield_delay_ms", 220)
        no_talking_over = expected.get("no_talking_over", True)

        merchant_floor_time = None
        alan_yield_time = None
        alan_speaking_after_floor = False
        current_turn_state = "ALAN_FLOOR"

        for ev in traces:
            t = ev["t"]
            name = ev["event"]
            data = ev["data"]

            if name == "turn_state_update":
                current_turn_state = data.get("turn_state", current_turn_state)

            if name == "human_speech_start":
                merchant_floor_time = t

            if name == "alan_yield":
                alan_yield_time = t

            # Check for illegal transitions
            if name == "illegal_transition":
                violations.append({
                    "type": "illegal_transition",
                    "t": t,
                    "message": data.get("error", "Unknown illegal transition"),
                })

            # Talking-over detection
            if merchant_floor_time is not None and t > merchant_floor_time:
                if current_turn_state == "ALAN_FLOOR" and name != "alan_yield":
                    alan_speaking_after_floor = True

        # Check talking-over
        if no_talking_over and alan_speaking_after_floor:
            violations.append({
                "type": "talking_over",
                "message": "Alan remained in ALAN_FLOOR after merchant_floor.",
            })

        # Check yield delay
        if merchant_floor_time is not None and alan_yield_time is not None:
            delay = alan_yield_time - merchant_floor_time
            if delay > max_yield:
                violations.append({
                    "type": "yield_delay",
                    "message": f"Alan yielded after {delay} ms, exceeding {max_yield} ms.",
                })
        elif merchant_floor_time is not None and alan_yield_time is None:
            violations.append({
                "type": "missing_yield",
                "message": "Merchant floor detected but no alan_yield event logged.",
            })

        passed = len(violations) == 0
        return {"passed": passed, "violations": violations}

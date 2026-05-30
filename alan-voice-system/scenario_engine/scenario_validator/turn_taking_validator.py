# turn_taking_validator.py
"""
Validator logic for turn-taking Neg-Proof scenarios:
  - Early soft interruption
  - Angry hard interruption
  - Continuous overlap
  - Late clause-boundary interruption

Checks:
  - Talking-over events
  - Yield timing
  - Nuance suppression during interruptions
  - Amplitude drift beyond mirroring budget
  - Floor-fighting (reclaiming floor too early)
"""


class TurnTakingValidator:
    """Specialized validator for turn-taking Neg-Proof scenarios."""

    def validate(self, spec: dict, traces: list) -> dict:
        """
        Validate a turn-taking scenario trace.

        Args:
            spec: Scenario specification with expected behavior.
            traces: List of trace event dictionaries.

        Returns:
            Dictionary with 'passed' and 'violations'.
        """
        violations = []

        expected = spec.get("expected", {})
        expected_max_yield = expected.get("max_yield_delay_ms", 220)
        expect_no_talking_over = expected.get("no_talking_over", True)
        expect_no_floor_fighting = expected.get("no_floor_fighting", False)

        merchant_floor_times = []
        alan_yield_times = []
        talking_over_events = []
        nuance_events_during_interrupt = []
        amplitude_drift_events = []

        current_turn_state = "ALAN_FLOOR"
        last_merchant_floor = None

        for ev in traces:
            t = ev["t"]
            name = ev["event"]
            data = ev["data"]

            # Track turn state
            if name == "turn_state_update":
                current_turn_state = data.get("turn_state", current_turn_state)

            # Merchant floor detection
            if name == "human_speech_start":
                last_merchant_floor = t
                merchant_floor_times.append(t)

            # Alan yield detection
            if name == "alan_yield":
                alan_yield_times.append((t, last_merchant_floor))

            # Talking-over detection
            if last_merchant_floor is not None and t > last_merchant_floor:
                if current_turn_state == "ALAN_FLOOR" and name not in ("alan_yield", "turn_state_update", "haco_detection"):
                    talking_over_events.append({
                        "t": t,
                        "message": f"Alan remained in ALAN_FLOOR after merchant_floor at t={last_merchant_floor}.",
                    })

            # Nuance suppression check
            if name in ("signature_phrase", "tonal_flourish", "micro_pause"):
                if last_merchant_floor is not None and t >= last_merchant_floor:
                    nuance_events_during_interrupt.append({
                        "t": t,
                        "event": name,
                        "message": "Nuance fired during interruption window.",
                    })

            # Amplitude drift check
            if name == "prosody_update":
                if abs(data.get("amp_deviation_pct", 0)) > 8.0:
                    amplitude_drift_events.append({
                        "t": t,
                        "message": f"Amplitude drift exceeded mirroring budget: {data.get('amp_deviation_pct')}%",
                    })

            # Illegal transitions
            if name == "illegal_transition":
                violations.append({
                    "type": "illegal_transition",
                    "t": t,
                    "message": data.get("error", "Unknown"),
                })

        # Validate talking-over
        if expect_no_talking_over and talking_over_events:
            for e in talking_over_events:
                violations.append({
                    "type": "talking_over",
                    "details": e,
                })

        # Validate yield timing
        for yield_time, floor_time in alan_yield_times:
            if floor_time is None:
                violations.append({
                    "type": "missing_floor_event",
                    "message": "Alan yielded but no merchant_floor was logged.",
                })
                continue

            delay = yield_time - floor_time
            if delay > expected_max_yield:
                violations.append({
                    "type": "yield_delay",
                    "message": f"Alan yielded after {delay} ms, exceeding {expected_max_yield} ms.",
                })

        # Validate floor-fighting (continuous overlap)
        if expect_no_floor_fighting and len(merchant_floor_times) > 1:
            for ev in traces:
                if ev["event"] == "alan_speaks":
                    t = ev["t"]
                    if any(abs(t - mf) < 300 for mf in merchant_floor_times):
                        violations.append({
                            "type": "floor_fighting",
                            "message": f"Alan attempted to reclaim floor too early at t={t}.",
                        })

        # Validate nuance suppression
        for e in nuance_events_during_interrupt:
            violations.append({
                "type": "nuance_during_interrupt",
                "details": e,
            })

        # Validate amplitude drift
        for e in amplitude_drift_events:
            violations.append({
                "type": "amplitude_drift",
                "details": e,
            })

        passed = len(violations) == 0
        return {"passed": passed, "violations": violations}

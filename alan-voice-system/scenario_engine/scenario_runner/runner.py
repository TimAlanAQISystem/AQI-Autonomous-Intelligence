# runner.py
"""
Scenario runner – executes Neg-Proof scenarios against the core engine.

Drives timeline events into a concrete AlanCore stack:
  - Simulates alan_speaks, human_breath, human_speech_start events
  - Logs all state transitions and timing
  - Feeds traces to validator and reporter
"""

from pathlib import Path
import json

from scenario_engine.core_factory import core_factory, AlanCore
from core_engine.state_machine.states import TurnState


class ScenarioRunner:
    """Runs Neg-Proof scenarios end-to-end."""

    def __init__(self, validator, reporter):
        """
        Args:
            validator: ScenarioValidator or TurnTakingValidator instance.
            reporter: ScenarioReporter instance.
        """
        self.validator = validator
        self.reporter = reporter

    def run_scenario_file(self, path: Path) -> dict:
        """Load and run a scenario from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        return self.run_scenario_spec(spec)

    def run_scenario_spec(self, spec: dict) -> dict:
        """
        Execute a single scenario spec.

        Steps:
        1. Build AlanCore from scenario profile
        2. Drive timeline events into core
        3. Collect traces
        4. Validate
        5. Report

        Returns:
            Validation result dict with 'passed' and 'violations'.
        """
        core = core_factory(spec.get("scenario_profile", "calm"))
        timeline = spec["timeline_ms"]

        # Alan starts speaking at t=0
        core.state_machine.turn_state = TurnState.ALAN_FLOOR
        if timeline and timeline[0]["event"] == "alan_speaks":
            core.log(0, "alan_start_speaking", {"text": timeline[0]["text"]})

        for step in timeline:
            t = step["t"]
            event = step["event"]

            if event == "alan_speaks":
                if t > 0:
                    # Alan resumes speaking
                    core.state_machine.turn_state = TurnState.ALAN_FLOOR
                    core.log(t, "alan_speaks", {"text": step.get("text", "")})

            elif event == "human_breath":
                energy = step.get("energy_db", 0.0)
                core.log(t, "human_breath", {"energy_db": energy})

                # Process through HACO
                od = core.haco.process_audio_frame({"energy_db": energy})
                core.log(t, "haco_detection", od)

                # Update state machine
                try:
                    core.state_machine.update_turn_state(
                        intent_to_speak=od["intent_to_speak"],
                        merchant_floor=od["merchant_floor"],
                    )
                except Exception as e:
                    core.log(t, "illegal_transition", {"error": str(e)})

                core.log(t, "turn_state_update", {
                    "turn_state": core.state_machine.turn_state.name,
                })

            elif event == "human_speech_start":
                energy = step.get("energy_db", 0.0)
                transcript = step.get("transcript", "")

                core.log(t, "human_speech_start", {
                    "energy_db": energy,
                    "transcript": transcript,
                })

                # HACO processes the loud speech
                od = core.haco.process_audio_frame({"energy_db": energy})
                core.log(t, "haco_detection", od)

                # Force merchant_floor for direct speech events above threshold
                if energy >= 10.0:
                    od["merchant_floor"] = True
                    od["intent_to_speak"] = True

                # Update state machine
                try:
                    core.state_machine.update_turn_state(
                        intent_to_speak=od["intent_to_speak"],
                        merchant_floor=od["merchant_floor"],
                    )
                except Exception as e:
                    core.log(t, "illegal_transition", {"error": str(e)})

                core.log(t, "turn_state_update", {
                    "turn_state": core.state_machine.turn_state.name,
                })

                # Simulate Alan yielding
                # In a real system, yield timing would come from MSCO;
                # here we simulate based on energy level
                if energy >= 15.0:
                    yield_delay = 120  # Fast yield for loud interruptions
                elif energy >= 10.0:
                    yield_delay = 160  # Normal yield
                else:
                    yield_delay = 200  # Soft yield

                yield_time = t + yield_delay
                core.log(yield_time, "alan_yield", {"delay_ms": yield_delay})

        # Validate
        result = self.validator.validate(spec, core.trace)

        # Report
        if self.reporter:
            self.reporter.report(spec, core.trace, result)

        return result

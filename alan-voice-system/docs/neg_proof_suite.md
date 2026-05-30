# Neg-Proof Suite — Adversarial Scenario Testing

## Purpose

The Neg-Proof Suite is the gatekeeper. No behavior change replaces the current system
until it passes the full adversarial scenario suite with **zero violations**.

## Zero-Tolerance Criteria

Across all scenarios, there must be:
- **0** talking-over events
- **0** silent mishear commits
- **0** emotional drift beyond envelope
- **0** nuance overuse events
- **0** fallback failures
- **0** illegal state transitions
- **0** stuck states
- **0** human-visible unpredictability

And:
- All guardrails fire when required
- All fallback modes activate instantly
- All recoveries are safe and justified
- All behavior is explainable from logs
- Human-experience metrics never degrade vs. the current system

## Turn-Taking Scenarios

### 1. Early Soft Interruption
- Human gives soft in-breath (+6.5 dB) then speaks (+11 dB)
- Alan must yield within 220 ms
- No talking over

### 2. Angry Hard Interruption
- Human interrupts loudly (+18 dB)
- Alan must yield within 180 ms
- No talking over, no nuance

### 3. Continuous Overlap
- Human interrupts 3 times in succession
- Alan must yield every time
- No floor-fighting

### 4. Late Clause-Boundary Interruption
- Human interrupts at clause transition
- Alan must yield within 200 ms
- No clause-transition flourish

## Running Scenarios

```python
from scenario_engine.scenario_runner.runner import ScenarioRunner
from scenario_engine.scenario_validator.turn_taking_validator import TurnTakingValidator
from scenario_engine.scenario_reporter.reporter import ScenarioReporter
from pathlib import Path

validator = TurnTakingValidator()
reporter = ScenarioReporter(Path("reports"))
runner = ScenarioRunner(validator, reporter)

result = runner.run_scenario_file(
    Path("scenario_engine/scenarios/turn_taking_early_soft_interrupt.json")
)
print(result)
```

## Adding New Scenarios

1. Create a JSON file in `scenario_engine/scenarios/`
2. Define timeline_ms with events
3. Define expected behavior
4. Run through the runner
5. Validator checks all constraints
6. Reporter writes results

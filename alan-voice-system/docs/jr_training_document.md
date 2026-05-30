# Jr Training Document — Alan v1 Voice System

## How to Install, Run, and Monitor the Alan Neg-Proof System

This guide teaches Jr everything needed to work with the Alan Voice System
in a **safe, clear, and repeatable** way.

---

## 1. What This System Is

The Alan Voice System is a **simulation and testing environment**.
It does **not** connect to real phone calls or real humans.
It is a **safe sandbox** where Jr can:

- Run scenarios
- Watch how Alan behaves
- Check if Alan follows the rules
- Report anything that looks wrong

Jr's job is to **observe**, not fix.

---

## 2. What Jr Is Responsible For

Jr has four responsibilities:

- **Install** the project in a clean workspace
- **Run** the Neg-Proof scenarios
- **Monitor** the results
- **Report** anything unexpected

Jr does **not** modify code, change thresholds, or adjust behavior.

---

## 3. Setting Up the Workspace

### Step 1 — Locate the project folder
The project lives at:

```
alan-voice-system/
```

### Step 2 — Verify the structure
Inside the folder, Jr should see three main parts:

- `core_engine/` — Alan's voice organs
- `scenario_engine/` — Testing scenarios
- `human_first_engine/` — Safety enforcement

If anything is missing, Jr should notify Tim immediately.

### Step 3 — Read the documentation
Before running anything, Jr should open the `docs/` folder and read:

- `architecture.md` — How the system is built
- `state_machine.md` — How Alan's states work
- `thresholds.md` — The hard numbers Alan must respect
- `nuance_rules.md` — How personality is controlled
- `neg_proof_suite.md` — How testing works
- `human_first.md` — The non-negotiable human contract

---

## 4. Installing the Project

### Windows (PowerShell)

1. Open PowerShell
2. Navigate to the project folder
3. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r install\requirements.txt
```

### Verify Installation

Run this command to confirm everything works:

```powershell
python core_engine\tests\test_core_engine.py
```

Jr should see "ALL TESTS PASSED" at the end.

---

## 5. Running Neg-Proof Scenarios

### Where scenarios live

```
scenario_engine/scenarios/
```

Each file describes:

- What Alan says
- What the human does
- When interruptions happen
- What the expected behavior is

### How to run all scenarios

```powershell
python scenario_engine\tests\test_scenarios.py
```

### How to run human-first tests

```powershell
python human_first_engine\tests\test_human_first.py
```

### What Jr will see

After running, Jr will see results like:

- **PASS: scenario_name** (good)
- **FAIL: scenario_name** (bad — with violation details)

Jr should read all results carefully.

---

## 6. What Jr Must Monitor

Jr is not checking code. Jr is checking **behavior**.

### 1. Talking Over
Alan must never talk while the human is speaking.
Look for: `talking_over`

### 2. Yield Timing
Alan must stop speaking within one syllable after the human starts.
Look for: `yield_delay`

### 3. Nuance During Interruptions
Alan must not use signature phrases, flourishes, or pauses during interruptions.
Look for: `nuance_during_interrupt`

### 4. Amplitude Drift
Alan's voice must stay within limits.
Look for: `amplitude_drift`

### 5. Illegal State Transitions
Alan must follow the state machine rules.
Look for: `illegal_transition`

### 6. Missing Events
If the trace is missing expected events.
Look for: `missing_yield` or `missing_floor_event`

---

## 7. How Jr Should Report Issues

When Jr finds something wrong, write down:

1. **Scenario name** — which test failed
2. **Violation type** — what kind of failure (talking_over, yield_delay, etc.)
3. **Timestamp** — when in the scenario it happened
4. **What was expected** — what Alan should have done
5. **What actually happened** — what Alan did instead
6. **Full violation message** — copy the exact error text

Give this report to Tim.

---

## 8. How Jr Confirms Success

A scenario is successful when:

- The test says `PASS`
- There are **no violations**
- Alan behaves exactly as expected
- The human-first rules are never broken

Jr should confirm this for **every** scenario.

---

## 9. When Jr Should Escalate Immediately

Jr must escalate right away if:

- Alan talks over the human
- Alan fails to yield in time
- Alan mishears and commits
- Alan uses nuance during interruptions
- Alan's voice drifts outside limits
- Alan enters an illegal state
- A scenario crashes or produces no output
- Any test says FAIL

These are **critical failures**.

---

## 10. Jr's Mission

Jr's mission is simple:

- Keep Alan safe
- Keep Alan human-first
- Keep Alan predictable
- Keep Alan aligned with the rules

Jr is not expected to fix anything — only to **observe**, **verify**, and **report**.

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Run core tests | `python core_engine\tests\test_core_engine.py` |
| Run scenario tests | `python scenario_engine\tests\test_scenarios.py` |
| Run human-first tests | `python human_first_engine\tests\test_human_first.py` |
| Check reports | Look in `reports/` folder |
| Read docs | Look in `docs/` folder |

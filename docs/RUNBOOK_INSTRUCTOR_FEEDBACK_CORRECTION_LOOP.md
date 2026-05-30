# Runbook: Instructor Feedback & Correction Loop

## 1. Purpose & Scope

### Purpose

Create a governed, repeatable process for shaping Alan's behavior using real-world call outcomes.

### Scope

This runbook covers:

- how you correct Alan after a call
- how Jr records and structures those corrections
- how corrections become training data
- how drift is prevented
- how improvements are introduced safely

### Not Included

- envelope tuning
- persona redesign
- v4.0 capability expansion
- instructor onboarding for external trainers

This runbook is strictly about your feedback -> Jr -> Alan.

## 2. Preconditions (Must Be True Before Feedback Begins)

Before feedback begins, Jr must verify:

- the call log exists and is complete
  - primary surfaces: `logs/`, Twilio callback handling, runtime logs
- the transcript is available
  - primary surfaces: `logs/call_transcripts/`, transcript logs, relay capture surfaces
- the disposition is recorded
  - primary surface: `POST /twilio/events` outcome handling in [control_api_fixed.py](C:\Users\signa\OneDrive\Desktop\Agent X\control_api_fixed.py)
- no supervisor kill occurred, or it is documented
  - primary surface: [supervisor.py](C:\Users\signa\OneDrive\Desktop\Agent X\supervisor.py), guardian and incident logs
- the runtime trace is stable
  - primary surface: [docs/RUNTIME_CALL_LIFECYCLE_TRACE.md](C:\Users\signa\OneDrive\Desktop\Agent X\docs\RUNTIME_CALL_LIFECYCLE_TRACE.md)
- no envelope mismatch occurred
  - primary surfaces: [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py), [rapport_layer.json](C:\Users\signa\OneDrive\Desktop\Agent X\rapport_layer.json)
- no drift indicators were triggered
  - primary surfaces: supervisor state, governance signals, state-machine and relay review

This ensures you are correcting behavior, not debugging infrastructure.

## 3. Instructor Feedback Workflow (Your Role)

### 3.1 Review the call

You review the call recording, transcript, and disposition and identify:

- what Alan did well
- what Alan did poorly
- what Alan should have done instead
- emotional calibration issues
- timing issues
- compliance issues
- rapport issues

### 3.2 Produce a correction entry

Your correction must be structured as:

- Context: what happened
- Issue: what went wrong
- Desired behavior: what Alan should do
- Example: a corrected version of the turn
- Severity: `P0` / `P1` / `P2`

This is the raw material Jr will process.

## 4. Jr's Role: Turning Feedback Into Structured Training

### 4.1 Normalize the correction

Jr rewrites your feedback into a standard correction format, ensuring:

- no ambiguity
- no emotional over-interpretation
- no invented behavior
- no drift from RRGs

### 4.2 Map the correction to the correct layer

Jr determines whether the correction belongs to:

- Persona
  - [CONSTITUTIONAL_CORE/alan_persona.json](C:\Users\signa\OneDrive\Desktop\Agent X\CONSTITUTIONAL_CORE\alan_persona.json)
- Envelope
  - [rapport_layer.json](C:\Users\signa\OneDrive\Desktop\Agent X\rapport_layer.json)
- State machine behavior
  - [alan_state_machine.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_state_machine.py)
- Governance layer
  - [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py)
- Objection handling
- Rapport engine
- Timing logic
  - [timing_config.json](C:\Users\signa\OneDrive\Desktop\Agent X\timing_config.json), [timing_loader.py](C:\Users\signa\OneDrive\Desktop\Agent X\timing_loader.py)
- Greeting logic
  - [aqi_conversation_relay_server.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py)

### 4.3 Create a training artifact

Jr produces:

- a structured example
- a before/after comparison
- a test scenario
- a drift-prevention note

This becomes part of Alan's training corpus or review packet.

### 4.4 Flag if the correction touches constitutional boundaries

If your correction conflicts with:

- `RRG I-VI`
- governance rules
- safety constraints
- identity constraints

Jr must flag it and ask for clarification before any change is proposed.

## 5. Drift Prevention Layer

### 5.1 Every correction must be constitutional

Jr checks:

- does this correction violate identity
- does it violate emotional calibration
- does it introduce over-assertiveness
- does it break rapport rules
- does it create unsafe escalation

### 5.2 Every correction must be testable

Jr generates:

- a test scenario
- expected behavior
- failure conditions

### 5.3 Every correction must be reversible

Jr ensures:

- a rollback path exists
- the change is isolated
- the change is documented

## 6. Safe Introduction of Improvements

### 6.1 Jr proposes the change

Jr presents:

- the correction
- the mapped layer
- the training artifact
- the test scenario
- the rollback path

### 6.2 You approve or reject

You are the final authority.

### 6.3 Jr applies the change

Only after approval.

### 6.4 Jr runs the test scenario

Ensures the change behaves as expected.

### 6.5 Jr logs the change

This becomes part of lineage and decision memory.

## 7. Post-Correction Monitoring

After the change goes live:

- Jr watches the next 3 calls
- flags anomalies
- confirms the correction took
- confirms no drift occurred
- confirms no regressions occurred

## 8. Instructor Review Loop

Every week:

- Jr summarizes all corrections
- Jr highlights patterns
- Jr identifies recurring issues
- Jr proposes structural improvements
- you review and approve

This is how Alan evolves safely over time.

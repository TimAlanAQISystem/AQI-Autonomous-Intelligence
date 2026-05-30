# Runbook: Envelope Tuning & Behavioral Calibration

## 1. Purpose & Scope

### Purpose

Provide a governed, reversible, testable process for tuning Alan's behavioral envelopes and calibrating his conversational behavior based on real-world signals.

### Scope

This runbook covers:

- how envelope tuning proposals are created
- how behavioral calibration is evaluated
- how Jr structures and tests tuning changes
- how tuning is applied safely
- how stability is verified after tuning

### Not Included

- persona redesign
- instructor correction loop
- drift detection
- v4.0 capability expansion
- multi-agent tuning

This runbook is strictly about envelope tuning and behavioral calibration.

## 2. Preconditions (Must Be True Before Tuning Begins)

Before any envelope tuning is allowed, Jr must verify:

- no active drift
- no unresolved supervisor kill events
- no missing persona or envelope files
- RRG corpus present, with `RRG-V` flagged as known gap
- runtime call lifecycle stable
- instructor correction loop functioning
- logs available for the calls prompting the tuning

This ensures tuning is based on real signals, not noise.

## 3. Envelope Tuning Taxonomy

### 3.1 Timing Envelopes

- pre-greeting silence
- early sprint delay
- inter-sentence silence
- interruption-recovery latency
- predictive intent delay

### 3.2 Emotional Calibration Envelopes

- warmth bias
- prosody-intent alignment
- rapport modulation
- apology frequency
- enthusiasm range

### 3.3 Behavioral Envelopes

- objection handling
- compliance tone
- high-status communication
- conversational imperfection
- fallback behavior

### 3.4 Safety & Governance Envelopes

- escalation thresholds
- refusal behavior
- compliance strictness
- boundary enforcement

Each envelope has:

- safe range
- baseline
- increment size
- regression conditions
- rollback trigger

## 4. Tuning Proposal Workflow (Instructor -> Jr)

### 4.1 Instructor identifies a behavioral issue

From real calls:

- too fast
- too slow
- too warm
- too flat
- too apologetic
- too robotic
- too assertive
- too passive

### 4.2 Instructor submits a tuning request

Structured as:

- Context: what happened
- Issue: what envelope is affected
- Desired shift: warmer, slower, more confident, and similar
- Severity: `P1` / `P2`
- Example: corrected turn

### 4.3 Jr classifies the envelope

Jr determines:

- which envelope is affected
- whether the issue is envelope-level or persona-level
- whether tuning is appropriate

If tuning is not appropriate, Jr escalates back to instructor.

## 5. Jr's Role: Turning the Request Into a Tuning Plan

### 5.1 Validate the envelope

Jr checks:

- safe range
- baseline
- increment size
- governance constraints

### 5.2 Draft the tuning change

Jr proposes:

- new baseline
- increment
- expected behavioral effect
- risk level

### 5.3 Create a test scenario

Jr writes:

- a call scenario that exercises the envelope
- expected behavior
- failure conditions

### 5.4 Create a rollback plan

Jr defines:

- rollback target
- rollback trigger
- rollback test

### 5.5 Present the tuning plan to instructor

Instructor approves or rejects.

## 6. Applying the Tuning Change

### 6.1 Jr applies the envelope update

Only after instructor approval.

### 6.2 Jr runs the test scenario

Ensures:

- envelope behaves as expected
- no regressions
- no drift
- no supervisor kills

### 6.3 Jr logs the change

Including:

- what changed
- why it changed
- who approved
- how it was tested
- rollback path

This preserves lineage.

## 7. Post-Tuning Monitoring

For the next 3-5 calls, Jr monitors:

- timing
- emotional calibration
- rapport
- fallback frequency
- supervisor signals
- drift indicators

If any anomaly appears:

- Jr triggers rollback
- instructor is notified
- drift report is generated

## 8. Weekly Calibration Review

Every week, Jr produces:

- envelope performance summary
- tuning effectiveness
- regression analysis
- envelope stress points
- recommended future tuning
- calibration stability score

Instructor reviews and approves.

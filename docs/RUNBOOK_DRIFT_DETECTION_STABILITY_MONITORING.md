# Runbook: Drift Detection & Stability Monitoring

## 1. Purpose & Scope

### Purpose

Provide a governed, repeatable process for detecting, diagnosing, and correcting drift in Alan's behavior, identity, timing, emotional calibration, and call-flow execution.

### Scope

This runbook covers:

- how drift is detected
- how drift is classified
- how Jr monitors for drift
- how anomalies are escalated
- how drift is corrected safely
- how stability is verified after correction

### Not Included

- envelope tuning
- persona redesign
- instructor correction loop
- v4.0 upgrades
- multi-agent drift management

This runbook is strictly about detecting and stabilizing drift.

## 2. Preconditions (Must Be True Before Monitoring Begins)

Jr must verify:

- supervisor is active
- watchdog paths are enabled
- drift sentinel is running
  - current confirmed repo surfaces are supervisor, governance, state, and log review
- logging is enabled
- runtime trace is stable
- no unresolved kill paths
- no missing persona or envelope files
- RRG corpus present, with `RRG-V` flagged as known gap

This ensures drift detection is meaningful, not noise.

## 3. Drift Taxonomy (What Jr Must Watch For)

### 3.1 Identity Drift (Catastrophic)

Alan stops being Alan.

Examples:

- tone collapse
- persona mismatch
- loss of mission
- over-assertiveness
- emotional flattening

### 3.2 Behavioral Drift (Correctable)

Alan's behavior deviates from envelopes.

Examples:

- too formal
- too casual
- too apologetic
- too robotic
- too repetitive

### 3.3 Interpretive Drift (Semantic)

Alan misinterprets merchant intent.

Examples:

- wrong objection classification
- misreading sentiment
- incorrect escalation

### 3.4 Timing Drift (Operational)

Turn-taking becomes unnatural.

Examples:

- long pauses
- interrupting
- speaking too quickly
- delayed responses

### 3.5 Structural Drift (Systemic)

Call-flow logic deviates from expected paths.

Examples:

- skipped greeting
- missing fallback
- incorrect disposition
- supervisor kill loops

## 4. Drift Detection Surfaces (Grounded in Repo)

### 4.1 Supervisor Signals

From [supervisor.py](C:\Users\signa\OneDrive\Desktop\Agent X\supervisor.py):

- emotional deviation proxies
- timing anomalies
- fallback triggers
- kill events

### 4.2 Relay Logs

From [aqi_conversation_relay_server.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py) and `logs/`:

- STT errors
- response delays
- repeated fallback
- unexpected silence

### 4.3 State Machine Behavior

From [alan_state_machine.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_state_machine.py):

- incorrect state transitions
- missing transitions
- invalid transitions

### 4.4 Governance Layer

From [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py):

- envelope violations
- persona mismatches
- compliance issues

### 4.5 Twilio Callbacks

- `POST /twilio/events`
- `POST /twilio/recording-status`

These reveal timing drift, hangups, and unexpected call endings.

## 5. Drift Detection Workflow (Step-by-Step)

### 5.1 Capture the call

Jr collects:

- logs
- transcript
- disposition
- supervisor signals

### 5.2 Run drift classification

Jr identifies:

- identity drift
- behavioral drift
- interpretive drift
- timing drift
- structural drift

### 5.3 Determine severity

- `P0`: identity drift, stop system
- `P1`: behavioral or structural drift, fix before next call
- `P2`: timing or interpretive drift, monitor and correct

### 5.4 Produce a drift report

Jr writes:

- what drift occurred
- where it occurred
- why it occurred
- severity
- recommended correction path

### 5.5 Escalate to instructor

You review and approve the correction path.

## 6. Drift Correction Workflow

### 6.1 Jr proposes correction

Based on drift type:

- persona fix
- envelope adjustment
- fallback logic update
- timing correction
- state machine fix

### 6.2 Instructor approval

You approve or reject.

### 6.3 Apply correction safely

Jr:

- updates training artifacts
- updates test scenarios
- applies correction
- runs tests

### 6.4 Verify stability

Jr monitors next 3 calls for:

- regression
- new drift
- correction success

## 7. Drift Prevention Layer

### 7.1 Constitutional Anchoring

Every correction must align with:

- `RRG I-VI`
- persona
- envelopes
- governance rules

### 7.2 Test Scenarios

Every correction must include:

- expected behavior
- failure conditions
- rollback path

### 7.3 Logging & Lineage

Jr logs:

- what changed
- why it changed
- who approved
- how it was tested

This prevents silent drift.

## 8. Weekly Stability Review

Every week, Jr produces:

- drift summary
- recurring patterns
- stability score
- envelope stress points
- supervisor kill analysis
- recommended improvements

You review and approve.

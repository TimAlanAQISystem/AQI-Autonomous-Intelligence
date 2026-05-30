# Runbook: Supervisor Kill Path Analysis & Recovery

## 1. Purpose & Scope

### Purpose

Provide a governed, auditable, drift-free process for:

- detecting supervisor kill events
- classifying the cause
- analyzing the failure path
- restoring stability
- preventing recurrence
- ensuring constitutional alignment

### Scope

This runbook covers:

- kill path detection
- kill path classification
- kill path analysis
- recovery workflow
- post-recovery monitoring
- instructor escalation

### Not Included

- envelope tuning
- drift detection
- instructor corrections
- campaign setup
- daily reporting

This runbook is strictly about kill path analysis and recovery.

## 2. Preconditions (Must Be True Before Kill Path Analysis)

Jr must verify:

- kill event is real, not a log artifact
- supervisor logs are complete
- relay logs are complete
- Twilio callbacks are present
- transcript is available if the call progressed
- no missing or corrupted log files
- no concurrent kill events pending

This ensures analysis is grounded in truth, not noise.

## 3. Kill Path Taxonomy (What Jr Must Classify)

### 3.1 STT Failure Kill

Triggered by:

- repeated STT dropouts
- no speech detected
- corrupted audio
- STT engine unreachable

### 3.2 Silence Timeout Kill

Triggered by:

- merchant silent beyond threshold
- Alan silent due to internal error
- relay stuck in waiting state

### 3.3 Governance Violation Kill

Triggered by:

- envelope violation
- persona mismatch
- unsafe escalation
- compliance breach

### 3.4 State Machine Kill

Triggered by:

- invalid state transition
- missing transition
- infinite loop detected

### 3.5 Relay Failure Kill

Triggered by:

- relay server error
- session initialization failure
- audio stream failure

### 3.6 Twilio Infrastructure Kill

Triggered by:

- Twilio disconnect
- media stream failure
- callback failure

### 3.7 Unknown Kill

Triggered by:

- supervisor cannot classify
- logs incomplete
- unexpected exception

## 4. Kill Path Detection Surfaces (Grounded in Repo)

### 4.1 Supervisor Logs

From [supervisor.py](C:\Users\signa\OneDrive\Desktop\Agent X\supervisor.py) and `logs/`:

- kill reason
- kill timestamp
- affected subsystem
- fallback attempts

### 4.2 Relay Logs

From [aqi_conversation_relay_server.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py) and `logs/`:

- STT errors
- audio stream failures
- session initialization failures

### 4.3 State Machine Logs

From [alan_state_machine.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_state_machine.py):

- invalid transitions
- missing transitions
- fallback loops

### 4.4 Governance Layer Logs

From [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py):

- envelope violations
- persona mismatches
- compliance issues

### 4.5 Twilio Callbacks

- `POST /twilio/events`
- `POST /twilio/recording-status`

These reveal infrastructure-level failures.

## 5. Kill Path Analysis Workflow (Step-by-Step)

### 5.1 Capture the kill event

Jr collects:

- kill reason
- kill timestamp
- call ID
- lead ID
- logs
- transcript, if any

### 5.2 Classify the kill

Using the taxonomy in Section 3.

### 5.3 Identify the root cause

Jr determines:

- subsystem failure
- envelope violation
- timing anomaly
- infrastructure failure
- governance breach

### 5.4 Determine severity

- `P0`: identity or governance kill
- `P1`: state machine or relay kill
- `P2`: STT or silence kill
- `P3`: Twilio infrastructure kill

### 5.5 Produce a kill path report

Jr writes:

- what happened
- why it happened
- where it happened
- severity
- recommended recovery path

### 5.6 Escalate to instructor

Instructor approves the recovery plan.

## 6. Recovery Workflow

### 6.1 Jr executes recovery plan

Depending on kill type:

- STT kill recovery
- silence kill recovery
- governance kill recovery
- state machine kill recovery
- relay kill recovery
- Twilio kill recovery

### 6.2 Jr runs regression tests

Ensures:

- no new drift
- no new kill paths
- no regressions

### 6.3 Jr logs the recovery

Including:

- what changed
- why it changed
- who approved
- how it was tested
- rollback path

## 7. Post-Recovery Monitoring

For the next 3-5 calls, Jr monitors:

- fallback frequency
- timing
- emotional calibration
- supervisor warnings
- envelope violations
- state machine transitions
- Twilio stability

If any anomaly appears:

- Jr triggers rollback
- instructor notified
- drift report generated

## 8. Weekly Kill Path Review

Every week, Jr produces:

- kill path summary
- kill frequency
- kill severity distribution
- subsystem failure patterns
- envelope stress points
- recommended improvements

Instructor reviews and approves.

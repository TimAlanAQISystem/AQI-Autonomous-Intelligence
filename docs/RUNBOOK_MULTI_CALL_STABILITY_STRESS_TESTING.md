# Runbook: Multi-Call Stability Stress Testing

## 1. Purpose & Scope

### Purpose

Provide a governed, repeatable, drift-free process for stress-testing Alan across:

- multiple consecutive calls
- varied merchant behaviors
- timing pressure
- STT variance
- relay load
- supervisor load
- envelope stress
- real-world unpredictability

### Scope

This runbook covers:

- test design
- test execution
- stability metrics
- drift detection under load
- kill path monitoring
- post-test analysis
- instructor escalation

### Not Included

- envelope tuning
- instructor corrections
- kill path recovery
- campaign setup
- daily reporting

This runbook is strictly about multi-call stability testing.

## 2. Preconditions (Must Be True Before Stress Testing)

Jr must verify:

### System readiness

- relay server stable
- supervisor stable
- STT engine stable
- Twilio connectivity stable
- no unresolved kill events
- no active drift
- logging enabled

### Test readiness

- test lead list prepared
- test scenarios defined
- pacing defined
- expected outcomes defined
- rollback plan defined

### Instructor readiness

- instructor available to review anomalies
- correction loop active
- drift detection active

## 3. Stress Test Types

### 3.1 Sequential Multi-Call Test (Baseline)

- 5-10 calls
- same merchant behavior
- same pacing
- checks cumulative drift

### 3.2 Variance Test (Behavioral Spread)

- different merchant behaviors
- objections
- silence
- interruptions
- emotional variance

### 3.3 Timing Stress Test

- rapid-fire calls
- minimal pacing
- checks timing envelopes
- checks supervisor load

### 3.4 STT Stress Test

- noisy audio
- accented speech
- fast speech
- slow speech

### 3.5 Relay Load Test

- concurrent calls, if supported
- rapid session creation
- rapid teardown

### 3.6 Kill Path Provocation Test

- intentionally malformed scenarios
- silence
- repeated interruptions
- unexpected hangups

## 4. Test Scenario Design

Each scenario must include:

- merchant behavior
- expected Alan behavior
- expected fallback behavior
- expected timing
- expected emotional calibration
- expected disposition
- failure conditions

Jr must generate:

- scenario scripts
- expected outcomes
- test metadata

## 5. Stress Test Execution Workflow

### 5.1 Initialize test environment

Jr ensures:

- logs cleared or isolated for the run
- supervisor baseline captured
- relay baseline captured
- pacing set

### 5.2 Execute calls

For each call:

- load test lead
- inject scenario context
- execute call
- record disposition
- capture logs
- capture supervisor signals

### 5.3 Monitor during execution

Jr watches:

- fallback frequency
- timing anomalies
- STT errors
- relay errors
- supervisor warnings
- kill events

### 5.4 Pause on critical anomalies

If:

- identity drift
- governance violation
- repeated kill events
- state machine collapse

Jr halts the test and escalates.

## 6. Stability Metrics (What Jr Must Measure)

### 6.1 Behavioral Stability

- rapport consistency
- emotional calibration
- objection handling
- compliance
- conversational imperfection

### 6.2 Timing Stability

- response latency
- inter-turn timing
- interruption handling
- silence tolerance

### 6.3 Structural Stability

- state machine transitions
- fallback paths
- greeting consistency
- disposition accuracy

### 6.4 System Stability

- relay uptime
- STT uptime
- Twilio stability
- supervisor load

### 6.5 Drift Indicators

- envelope violations
- persona mismatches
- semantic misinterpretations

## 7. Post-Test Analysis

Jr must produce:

### 7.1 Stability Report

- call-by-call summary
- anomalies
- drift indicators
- kill events
- fallback frequency
- timing deviations

### 7.2 Pattern Analysis

- repeated issues
- envelope stress points
- state machine weaknesses
- STT sensitivity

### 7.3 Severity Classification

- `P0`: identity drift
- `P1`: governance or state-machine drift
- `P2`: timing or behavioral drift
- `P3`: infrastructure noise

### 7.4 Recommended Actions

- corrections
- tuning
- drift investigation
- kill path analysis
- campaign adjustments

Instructor approves or rejects.

## 8. Recovery & Verification

If issues were found:

### 8.1 Jr executes recovery plan

Using the relevant correction, drift, tuning, or kill-path runbook.

### 8.2 Jr runs regression tests

Ensures:

- no new drift
- no regressions
- no kill loops

### 8.3 Jr re-runs a subset of stress tests

To confirm stability.

# Runbook: Daily Reporting & Performance Review

## 1. Purpose & Scope

### Purpose

Provide a governed, repeatable, auditable process for generating daily operational reports and evaluating Alan's performance across calls, behavior, stability, and campaign outcomes.

### Scope

This runbook covers:

- daily data collection
- daily report generation
- performance scoring
- behavioral evaluation
- stability review
- instructor-level interpretation
- Jr's responsibilities in producing the report

### Not Included

- envelope tuning
- drift detection
- instructor correction loop
- campaign setup
- v4.0 upgrades

This runbook is strictly about daily reporting and performance review.

## 2. Preconditions (Must Be True Before Reporting)

Jr must verify:

- all call logs for the day exist
- all transcripts are available
- all dispositions are recorded
- supervisor logs are complete
- no missing or corrupted log files
- no unresolved drift events
- no unreviewed kill paths
- campaign metadata is intact

This ensures the report is complete and trustworthy.

## 3. Data Sources (Grounded in Repo)

### 3.1 Call Logs

From:

- `logs/` directory
- Twilio callbacks in [control_api_fixed.py](C:\Users\signa\OneDrive\Desktop\Agent X\control_api_fixed.py)
- relay logs from [aqi_conversation_relay_server.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py)

### 3.2 Supervisor Signals

From [supervisor.py](C:\Users\signa\OneDrive\Desktop\Agent X\supervisor.py):

- emotional deviations
- timing anomalies
- fallback frequency proxies
- kill events

### 3.3 State Machine Events

From [alan_state_machine.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_state_machine.py):

- transitions
- invalid states
- fallback paths

### 3.4 Governance Layer

From [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py):

- envelope violations
- persona mismatches
- compliance issues

### 3.5 Campaign Engine

From campaign status, lead DB, and campaign logs:

- queue status
- pacing
- retry counts
- lead outcomes

## 4. Daily Report Structure

### 4.1 System Status

- relay uptime
- supervisor uptime
- STT stability
- Twilio stability
- error counts
- kill events
- drift indicators

### 4.2 Call Activity Summary

- total calls
- successful contacts
- voicemails
- no-answers
- errors
- retries
- average call duration

### 4.3 Conversation Outcomes

- qualified leads
- warm leads
- not interested
- callback requests
- merchant sentiment distribution

### 4.4 Behavioral Performance

Jr evaluates Alan across:

- rapport
- emotional calibration
- timing
- compliance
- objection handling
- conversational imperfection
- high-status communication

Each scored as:

- Stable
- Minor deviation
- Needs correction
- Critical drift

### 4.5 Stability Review

Jr reports:

- fallback frequency
- STT dropout rate
- supervisor warnings
- envelope violations
- persona mismatches
- timing anomalies

### 4.6 Campaign Performance

- leads attempted
- leads reached
- conversion indicators
- pacing adherence
- retry effectiveness
- lead quality signals

### 4.7 Instructor-Level Insights

Jr summarizes:

- what Alan did well
- what Alan struggled with
- what patterns emerged
- what needs instructor correction
- what needs envelope tuning
- what needs drift investigation

### 4.8 Recommended Actions

Jr proposes:

- corrections
- tuning
- drift checks
- campaign adjustments
- pacing changes
- retry strategy updates

You approve or reject.

## 5. Daily Review Workflow (Step-by-Step)

### 5.1 Jr collects all data

Logs, transcripts, dispositions, supervisor signals.

### 5.2 Jr generates the daily report

Using the structure above.

### 5.3 Instructor reviews the report

You read:

- anomalies
- patterns
- behavioral issues
- stability issues
- campaign performance

### 5.4 Instructor issues directives

You decide:

- what to correct
- what to tune
- what to investigate
- what to adjust

### 5.5 Jr executes directives

Following the appropriate runbook.

## 6. Weekly Aggregation Layer

Every 7 days, Jr produces:

- weekly call totals
- weekly conversion indicators
- weekly drift summary
- weekly envelope performance
- weekly instructor corrections
- weekly stability score
- weekly campaign performance

This becomes the foundation for strategic decisions.

# Runbook: Campaign Setup & Lead Handling

## 1. Purpose & Scope

### Purpose

Provide a governed, repeatable, drift-free process for:

- preparing a campaign
- validating leads
- loading leads into the queue
- ensuring context is correct
- ensuring pacing is correct
- ensuring Alan receives clean, safe, structured data

### Scope

This runbook covers:

- lead ingestion
- lead validation
- queue preparation
- campaign configuration
- pacing and throttling
- context injection
- pre-ignition checks

### Not Included

- call execution
- instructor corrections
- drift detection
- envelope tuning
- v4.0 upgrades

This runbook is strictly about campaign setup and lead handling.

## 2. Preconditions (Must Be True Before Campaign Setup)

Jr must verify:

### System readiness

- relay server online
- control API reachable
- `/health` and `/readiness` stable
- logging enabled
- supervisor active
- no unresolved kill paths

### Data readiness

- lead file present
- lead file readable
- lead file schema known
- no missing required fields
- no corrupted rows

### Campaign readiness

- campaign name defined
- pacing window defined
- disposition categories confirmed
- context fields defined, if used

## 3. Lead Schema Requirements

### Required fields

- `phone` or `to` or equivalent destination field
- `id` or `lead_id` or equivalent unique row key

### Optional context fields

- `expected_pitch`
- `fallback_pitch`
- `lead_source`
- `monthly_volume`
- `tier`

### Validation rules

- phone numbers must be normalized
- IDs must be unique
- no empty rows
- no malformed numbers
- no duplicate leads unless explicitly allowed

## 4. Lead Ingestion Workflow

### 4.1 Load the lead file

Jr loads:

- CSV
- JSON
- Excel
- database feed

### 4.2 Normalize fields

Jr ensures:

- phone -> E.164 format where required
- IDs -> string
- context fields -> lowercase keys

### 4.3 Validate each row

Jr checks:

- phone present
- ID present
- phone valid
- no duplicates
- context fields valid

### 4.4 Reject invalid rows

Jr writes:

- rejection record
- reason for rejection
- row number

### 4.5 Produce a clean lead list

This becomes:

- validated campaign input
- or the active queue in memory/database

## 5. Queue Preparation

### 5.1 Load clean leads into queue

Jr loads:

- validated leads
- with context
- with pacing metadata

### 5.2 Assign pacing

Jr sets:

- call interval
- max concurrent calls, usually `1` for Phase 1
- retry rules

### 5.3 Assign context

Jr injects:

- expected_pitch
- fallback_pitch
- lead_source
- monthly_volume
- tier

These are passed through Control API -> Twilio -> Relay -> Alan.

### 5.4 Confirm queue integrity

Jr verifies:

- queue length
- no null entries
- no malformed context
- no missing phone numbers

## 6. Campaign Configuration

### 6.1 Define campaign metadata

- campaign name
- campaign type
- pacing
- retry rules
- context rules

### 6.2 Register campaign with Control API

Jr ensures:

- campaign recognized
- queue linked
- pacing applied

### 6.3 Confirm readiness

Jr checks:

- `GET /readiness`
- `GET /campaign/status`
- queue status
- context injection path

## 7. Pre-Ignition Checklist

Before Alan makes the first call, Jr verifies:

- lead count correct
- pacing correct
- context correct
- no invalid leads
- no missing fields
- no drift
- no supervisor warnings
- no envelope mismatches
- no persona load errors

This is the go/no-go for campaign ignition.

## 8. Lead Handling During Campaign

### 8.1 Lead selection

Jr selects:

- next eligible lead
- based on pacing
- based on retry rules

### 8.2 Context injection

Jr injects:

- expected_pitch
- fallback_pitch
- lead_source
- monthly_volume
- tier

### 8.3 Call execution

Handled by the first outbound call runbook and live runtime path.

### 8.4 Disposition recording

Jr records:

- success
- voicemail
- hangup
- no-answer
- error
- supervisor kill

### 8.5 Retry logic

If applicable:

- schedule retry
- increment attempt count
- enforce retry limits

## 9. Post-Campaign Review

After the campaign:

- Jr produces a lead-level report
- Jr produces a campaign summary
- Jr identifies patterns
- Jr flags anomalies
- Jr prepares data for instructor review

This feeds into the correction, drift, and daily review runbooks.

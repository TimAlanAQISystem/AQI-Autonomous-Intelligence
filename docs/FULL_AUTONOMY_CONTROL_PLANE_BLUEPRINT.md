# Full Autonomy Control Plane Blueprint

Version: 1.0  
Effective date: 2026-08-09  
Classification: Internal use only

## Stack Choice

Preferred implementation stack for this repo:

- API layer: Python + FastAPI
- Data layer: PostgreSQL with SQLAlchemy or SQLModel
- Background execution: Celery or a lightweight internal job runner
- Event log: append-only Postgres table plus JSONL export
- Workflow orchestration: existing Python workflow modules plus n8n webhook bridges
- Human override: explicit admin API and EOS-mediated escalation path
- External integrations: processor, gateway, funding, email, and reporting clients

This stack matches the current codebase shape and reuses existing modules instead of introducing a parallel runtime.

## 1. Core Modules

### Merchant Lifecycle

Responsibilities:

- onboarding
- underwriting intake
- activation
- review
- suspension
- release
- lifecycle state transitions

Primary data:

- Merchant
- GatewayAccount
- ProcessorAccount
- WorkflowInstance

Integration points:

- workflow_merchant_onboard.py
- workflow_merchant_underwrite.py
- workflow_merchant_activate.py
- workflow_merchant_review.py
- workflow_merchant_suspend.py
- workflow_merchant_release.py

### Communication

Responsibilities:

- merchant notifications
- operator notifications
- templated email / SMS / internal alerts
- compliance-safe phrasing

Primary data:

- EventLog
- WorkflowInstance
- message templates

Integration points:

- alan_respond.py
- agent_communication.py
- notification adapters
- human_override_api.py

### Gateway and Processor

Responsibilities:

- account creation
- processor application submission
- activation and status sync
- chargeback retrieval
- funding retrieval
- payout and settlement updates

Primary data:

- GatewayAccount
- ProcessorAccount
- FundingEvent
- Chargeback

Integration points:

- models/autonomy_models.py
- workflow_tx_create_capture.py
- workflow_refund.py
- workflow_payout.py
- workflow_chargeback.py
- workflow_reconciliation_hub.py
- workflow_merchant_* modules

### Risk and Compliance

Responsibilities:

- MCC validation
- prohibited activity detection
- fraud pattern flags
- chargeback ratio monitoring
- underwriting exceptions
- compliance escalation

Primary data:

- RiskFlag
- Chargeback
- Merchant
- EventLog

Integration points:

- emergency_override_system.py
- human_override_api.py
- ALAN_COMPLIANCE_INTEGRATION.md
- compliance/risk services

### Funding and Settlement

Responsibilities:

- funding event ingestion
- funding delay detection
- settlement reconciliation
- reserve and hold visibility
- exception routing

Primary data:

- FundingEvent
- ProcessorAccount
- Merchant
- WorkflowInstance

Integration points:

- workflow_payout.py
- workflow_reconciliation_hub.py
- daily funding monitor jobs

### Workflow Engine

Responsibilities:

- orchestration of multi-step merchant workflows
- durable workflow state
- retry and pause/resume
- step transition logging

Primary data:

- WorkflowInstance
- EventLog
- step definitions

Integration points:

- n8n webhook builders already in repo
- FastAPI workflow endpoints
- background jobs

### State and Logging

Responsibilities:

- immutable audit trail
- workflow checkpoints
- operator actions
- policy decisions
- external API calls

Primary data:

- EventLog
- workflow state snapshots
- decision records

Integration points:

- SQL tables
- JSONL export
- dashboards and reports

### Human Override

Responsibilities:

- force safe mode
- pause evolution
- resume normal operation
- clear risk flags
- schedule manual callbacks
- override archetype or behavior state

Primary data:

- override commands
- EOS state
- merchant profile state
- planner task queue

Integration points:

- human_override_api.py
- emergency_override_system.py
- merchant_identity_persistence.py
- multi_turn_strategic_planning.py

## 2. Canonical Entities

### Merchant

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| legal_name | string | Required |
| dba_name | string | Optional |
| mcc | string | Required |
| monthly_volume | numeric | Required |
| avg_ticket | numeric | Required |
| cp_percent | numeric | Card-present mix |
| cnp_percent | numeric | Card-not-present mix |
| pricing_model | string | Interchange-plus, flat, dual pricing, etc. |
| gateway_id | GUID | FK to GatewayAccount |
| processor_id | GUID | FK to ProcessorAccount |
| underwriting_status | enum | pending / approved / declined |
| risk_level | string | normalized risk tier |
| created_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### WorkflowInstance

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| type | string | onboarding / chargeback / funding_exception / review / escalation |
| merchant_id | GUID | FK to Merchant |
| status | enum | running / paused / completed / failed |
| current_step | string | Current workflow node |
| started_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### EventLog

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID nullable | Optional FK |
| workflow_id | GUID nullable | Optional FK |
| actor | enum | alan / human / system |
| type | string | email_sent / api_call / decision / escalation / error |
| payload | JSON | Immutable event body |
| created_at | timestamp | Audit field |

### GatewayAccount

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID | FK |
| provider | string | authnet / nmi / epx / etc. |
| external_id | string | Gateway-side account id |
| status | string | active / pending / suspended |
| created_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### ProcessorAccount

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID | FK |
| provider | string | processor identifier |
| mid | string | Merchant ID |
| underwriting_status | enum | pending / approved / declined |
| funding_profile | string | funding configuration key |
| created_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### Chargeback

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID | FK |
| processor_account_id | GUID | FK |
| amount | numeric | Dispute amount |
| reason_code | string | Network reason code |
| received_at | timestamp | Intake time |
| respond_by | timestamp | Deadline |
| status | string | open / drafted / submitted / won / lost |
| created_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### FundingEvent

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID | FK |
| processor_account_id | GUID | FK |
| batch_id | string | Batch identifier |
| amount | numeric | Batch amount |
| scheduled_date | date | Expected funding |
| actual_date | date nullable | Actual funding date |
| status | enum | on_time / delayed / failed |
| created_at | timestamp | Audit field |
| updated_at | timestamp | Audit field |

### RiskFlag

| Field | Type | Notes |
|---|---|---|
| id | GUID | Primary key |
| merchant_id | GUID | FK |
| type | enum | chargeback_spike / fraud_alert / prohibited_mcc / underwriting_inconsistency / settlement_anomaly |
| severity | string | low / medium / high / critical |
| description | string | Human-readable explanation |
| created_at | timestamp | Audit field |
| resolved_at | timestamp nullable | Resolution time |

## 3. Workflow Skeletons

### Merchant Onboarding

1. Load merchant record
2. Validate minimum data completeness
3. Build processor payload
4. Submit processor application
5. Update underwriting status
6. On approval, create gateway account
7. On decline, escalate to human review
8. Log every step

### Chargeback Monitoring

1. Load all merchants
2. Pull chargeback data from processor
3. Upsert each chargeback
4. Detect spike or threshold breach
5. Create risk flag
6. Notify merchant
7. Escalate if needed
8. Log all calls and decisions

### Funding Exception Monitoring

1. Load all merchants
2. Pull funding events from processor
3. Upsert funding records
4. Detect delayed or failed funding
5. Notify merchant
6. Escalate for manual review
7. Log all observations

### Risk and Compliance Enforcement

1. Evaluate MCC and business model
2. Detect prohibited categories or mismatches
3. Flag chargeback ratios and fraud signals
4. Route to underwriting or compliance
5. Freeze or escalate only through authority boundaries

### Human Override

1. Receive admin command
2. Validate command authorization
3. Apply EOS or planner state change
4. Log override event
5. Notify relevant operators if needed

## 4. Policy Enforcement Hooks

Policy checks must wrap every outbound action.

Required guardrails:

- no guarantees of approval, funding, or outcome
- no unauthorized data collection
- no concealment of risk facts
- no escalation bypass
- no unsafe admin action without authorization

Example hook points:

- email send
- webhook dispatch
- processor API call
- merchant status change
- risk-flag clearance

## 5. Integration Points with Existing Repo

Use these existing surfaces as the starting control plane:

- [workflow_merchant_onboard.py](../workflow_merchant_onboard.py)
- [workflow_merchant_underwrite.py](../workflow_merchant_underwrite.py)
- [workflow_merchant_activate.py](../workflow_merchant_activate.py)
- [workflow_merchant_review.py](../workflow_merchant_review.py)
- [workflow_merchant_suspend.py](../workflow_merchant_suspend.py)
- [workflow_merchant_release.py](../workflow_merchant_release.py)
- [human_override_api.py](../human_override_api.py)
- [emergency_override_system.py](../emergency_override_system.py)
- [merchant_identity_persistence.py](../merchant_identity_persistence.py)
- [multi_turn_strategic_planning.py](../multi_turn_strategic_planning.py)
- [main.py](../main.py)

## 6. Build Order

Recommended implementation sequence:

1. Define database models and migrations
2. Build FastAPI control endpoints
3. Wire workflow instance persistence
4. Add event logging and JSONL export
5. Connect merchant lifecycle transitions
6. Attach risk and funding monitors
7. Wrap policy enforcement hooks
8. Add human override operations
9. Expose audit and certification views

## 7. Outcome

This blueprint turns the user-provided autonomy sketch into a concrete repo plan that matches the existing codebase and supports stepwise implementation.

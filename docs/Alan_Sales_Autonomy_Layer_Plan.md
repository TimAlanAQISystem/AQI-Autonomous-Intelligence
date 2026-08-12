# Alan Sales Autonomy Layer Plan

## Purpose

Extend Alan's governed autonomy spine with a sales-domain autonomy layer capable of calling leads, qualifying prospects, negotiating, closing deals, logging CRM activity, and respecting governance, compliance, and stabilization windows.

## Package Layout

```text
sales_autonomy/
    __init__.py
    acquisition_workflow.py
    deal_closer.py
    sales_closer.py
    sales_conversation.py
    sales_governance.py
    sales_metrics.py
    sales_negotiation.py
    sales_planner.py
    sales_verifier.py
    telephony_handler.py
```

## Repo Integration Points

- Telephony runtime surface: [aqi_conversation_relay_server.py](/c:/Users/signa/OneDrive/Desktop/Agent X/aqi_conversation_relay_server.py)
- Secondary relay surface: [agent_x_conversation_relay_server.py](/c:/Users/signa/OneDrive/Desktop/Agent X/agent_x_conversation_relay_server.py)
- Outbound dialing surface: [outbound_controller.py](/c:/Users/signa/OneDrive/Desktop/Agent X/outbound_controller.py)
- CRM surface: [src/crm.py](/c:/Users/signa/OneDrive/Desktop/Agent X/src/crm.py)
- Lead queue surface: [lead_database.py](/c:/Users/signa/OneDrive/Desktop/Agent X/lead_database.py)
- Governance and policy surfaces: [autonomy](/c:/Users/signa/OneDrive/Desktop/Agent X/autonomy)

## Core Components

### Sales Planner

Implemented in [sales_autonomy/sales_planner.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_planner.py).

- Generates structured sales-call tasks
- Normalizes lead identity, phone number, pitch, and objective
- Preserves governance-required roles on the task payload

### Sales Verifier

Implemented in [sales_autonomy/sales_verifier.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_verifier.py).

- Verifies sales calls against current governance posture
- Blocks calls when policy windows are closed
- Blocks calls during incident mode, recovery gate closure, or stabilization activity

### Sales Conversation Engine

Implemented in [sales_autonomy/sales_conversation.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_conversation.py).

- Handles objection-aware conversational turns
- Tracks buyer signals and close readiness
- Produces transcript data suitable for CRM logging and metrics

### Sales Negotiation Engine

Implemented in [sales_autonomy/sales_negotiation.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_negotiation.py).

- Produces governed offers based on objections
- Computes discount percentage
- Flags offers that require quorum or auditor participation

### Sales Closer

Implemented in [sales_autonomy/sales_closer.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_closer.py) and [sales_autonomy/deal_closer.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/deal_closer.py).

- Finalizes eligible deals
- Blocks close when governance requirements are not met
- Produces CRM-ready closure messages

### Sales Governance Hooks

Implemented in [sales_autonomy/sales_governance.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_governance.py).

- Reads live policy window state from Step 31
- Reads incident posture from Steps 33-35
- Reads stabilization posture from Step 43
- Evaluates actor-role, quorum, and auditor participation requirements

## Recommended Production Wiring

1. Use [outbound_controller.py](/c:/Users/signa/OneDrive/Desktop/Agent X/outbound_controller.py) as the outbound call adapter for `TelephonyAdapter.call()`.
2. Use the Twilio ConversationRelay path in [aqi_conversation_relay_server.py](/c:/Users/signa/OneDrive/Desktop/Agent X/aqi_conversation_relay_server.py) as the real-time speech loop for `on_call_event()`.
3. Use `LifetimeCRM.log_interaction()` from [src/crm.py](/c:/Users/signa/OneDrive/Desktop/Agent X/src/crm.py) as the concrete CRM logger behind `CRMAdapter.log()`.
4. Feed lead records from [lead_database.py](/c:/Users/signa/OneDrive/Desktop/Agent X/lead_database.py) into `run_acquisition()`.

## Governance Expectations

- Sales calls must remain blocked during incident mode
- Sales calls must remain blocked while stabilization windows are active
- Discounts above the configured threshold should require auditor participation
- High-impact commercial deviations should require quorum

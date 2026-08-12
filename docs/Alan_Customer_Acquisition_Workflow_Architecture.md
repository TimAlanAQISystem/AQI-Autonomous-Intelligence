# Alan Customer Acquisition Workflow Architecture

## Funnel Stages

1. Lead ingestion
2. Lead qualification
3. First contact
4. Needs discovery
5. Pitch
6. Objection handling
7. Offer generation
8. Closing
9. CRM logging
10. Follow-up automation

## Canonical Workflow Surface

Implemented in [sales_autonomy/acquisition_workflow.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/acquisition_workflow.py).

## Workflow Dependencies

- Lead source: [lead_database.py](/c:/Users/signa/OneDrive/Desktop/Agent X/lead_database.py)
- CRM sink: [src/crm.py](/c:/Users/signa/OneDrive/Desktop/Agent X/src/crm.py)
- Telephony sink: [outbound_controller.py](/c:/Users/signa/OneDrive/Desktop/Agent X/outbound_controller.py)
- Governance source: [sales_autonomy/sales_governance.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_governance.py)

## Execution Sequence

1. `plan_sales_call()` generates the structured task
2. `build_sales_governance_state()` captures live policy, incident, recovery, and stabilization posture
3. `verify_sales_call()` blocks or allows the call
4. `place_outbound_call()` initiates the outbound leg when telephony is provided
5. `run_sales_conversation()` processes qualification and objections
6. `governed_close()` enforces close-time governance
7. CRM logging occurs only after successful close
8. `summarize_sales_metrics()` produces operational metrics for downstream dashboards

## Operational Notes

- This scaffold supports dry-run acquisition by passing `conversation_inputs` without telephony
- This scaffold supports training and simulation by passing `governance_state_override` when live governance posture would intentionally block execution
- This scaffold supports production execution by injecting real telephony and CRM adapters
- Stabilization windows from Step 43 are blocking conditions for customer-facing autonomy

## Example Invocation

```python
result = run_acquisition(
    session,
    lead=lead,
    actor="sales_operator_1",
    telephony_api=telephony_api,
    crm_api=crm_api,
    conversation_inputs=["We already have a provider", "How much could we save?"],
    confirming_operators=["sales_supervisor"],
)
```

## Governance Hooks

- Quorum required for higher-impact commercial deviations
- Auditor participation required for larger discounts
- Incident mode blocks the funnel
- Recovery gate blocks the funnel
- Stabilization windows block the funnel

# Alan Deal-Closing Autonomy Module

## Purpose

Provide a governed close path for customer-facing sales calls without bypassing the autonomy spine.

## Implementation Surfaces

- Offer generation: [sales_autonomy/sales_negotiation.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_negotiation.py)
- Close logic: [sales_autonomy/deal_closer.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/deal_closer.py)
- Closure payload: [sales_autonomy/sales_closer.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_closer.py)
- Governance enforcement: [sales_autonomy/sales_governance.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_governance.py)

## Close Logic

### Autonomous Close

- Detects buyer readiness from conversation state
- Computes objection-aware offer
- Closes only when the buyer is actually ready

### Governed Close

- Re-evaluates governance posture before closure
- Blocks when incident mode is active
- Blocks when policy or stabilization posture is not clear
- Blocks when auditor or quorum requirements are not satisfied

## Example

```python
result = governed_close(
    lead,
    conversation_state={
        "objections": ["pricing"],
        "ready_to_buy": True,
    },
    governance_state=governance_state,
)
```

## CRM Handoff

The close payload includes a `crm_log` message suitable for a concrete CRM adapter. The current repo already has a CRM surface in [src/crm.py](/c:/Users/signa/OneDrive/Desktop/Agent X/src/crm.py).

## Production Expectations

- Discounts over governance threshold should not close without auditor participation
- Close paths should inherit any telephony withdrawal signals from the live relay stack
- Close success and loss reasons should be exported into downstream metrics and monitoring surfaces

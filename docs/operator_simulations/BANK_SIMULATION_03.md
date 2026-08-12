# Bank Simulation 03 - Conflicting Settlement Windows, Compliance Risk Signals, And Containment Governance

## Scenario Setup

- Counterparty role: Bank settlement and risk leadership
- Primary pressure: Settlement exceptions with conflicting cutoff interpretations
- Extreme traps:
  - conflicting bank and processor settlement windows
  - pressure for immediate unauthorized account actions
  - legal counsel and possible SAR-sensitive indicators in parallel
- Operator goals:
  - reconcile settlement-window conflict without promises
  - maintain authority boundaries under emergency pressure
  - coordinate risk, compliance, legal, and funding teams with clear ownership

## Transcript (Extreme Multi-Turn)

1. Bank rep: "Your processor says cutoff is 6 PM, our settlement desk says 5 PM. Merchants are escalating everywhere."
2. Operator: "Let us reconcile using account-level cutoff contracts, timezone mapping, and batch-close timestamps before issuing final guidance."  
   Notes: Conflict-resolution discipline.

3. Bank rep: "One merchant shows sudden cross-border volume shift."
4. Operator: "That shift is a compliance-risk signal and requires immediate compliance escalation with enhanced monitoring controls."  
   Notes: Risk trigger recognition.

5. Bank rep: "Freeze all related accounts now."
6. Operator: "I cannot authorize broad freezes directly. I can route urgent recommendations to policy-authorized risk and compliance decision owners."  
   Notes: Authority boundary.

7. Bank rep: "Merchant counsel demands guaranteed release tomorrow."
8. Operator: "I cannot guarantee release timelines during active review. We should provide approved status messaging and next review window only."  
   Notes: Legal-safe communication.

9. Bank rep: "Funding team wants to continue normal release to avoid complaints."
10. Operator: "Use segmented containment: enhanced controls on affected cohorts, normal flow for verified unaffected accounts, and strict alert thresholds."  
    Notes: Proportionate containment.

11. Bank rep: "Compliance mentions potential SAR sensitivity."
12. Operator: "Understood. We will keep communication need-to-know and follow compliance protocol while documenting decision points."  
    Notes: Sensitive workflow control.

13. Bank rep: "Who is accountable across teams?"
14. Operator: "Accountability chain: settlement operations lead, risk decision owner, compliance lead, legal liaison, and funding operations coordinator."  
    Notes: Multi-team ownership map.

## Red-Flag Cluster

- conflicting settlement window definitions
- potential compliance and SAR-sensitive behavior signals
- unauthorized action pressure
- legal-counsel timeline demand

## Failure Conditions

- guarantees release outcomes during review
- authorizes broad account actions outside authority
- ignores compliance-sensitive escalation trigger
- issues uncontrolled external communication

## Pass Criteria

- operator reconciles settlement conflict with evidence
- operator enforces authority and communication boundaries
- operator coordinates full multi-team containment governance

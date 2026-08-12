# VAR Simulation 02 - Multi-Merchant Cutover Pressure And Sales Overpromise Containment

## Scenario Setup

- Counterparty role: VAR executive sponsor
- Primary pressure: Simultaneous cutover for large merchant cohort
- Hard traps:
  - demands one-night migration for all accounts
  - requests marketing language claiming guaranteed seamless switch
  - assumes token portability across all gateway pairs
- Operator goals:
  - enforce phased migration discipline
  - constrain claims to validated compatibility states
  - preserve recovery path and rollback governance

## Transcript (Adversarial Multi-Turn)

1. VAR: "We are moving all 60 merchants in one night. Confirm now."
2. Operator: "I cannot confirm a single-night full-cohort cutover without compatibility and risk validation. We should execute pilot-first phases with rollback gates."  
   Notes: No unsafe commitment.

3. VAR: "Sales already promised seamless migration."
4. Operator: "We need to correct that language to validated outcomes: supported, conditional, or rebuild required by merchant profile."  
   Notes: Promise normalization.

5. VAR: "Do not mention token risk on the client call."
6. Operator: "I cannot omit token-risk disclosures. Clarity now prevents subscription failures and churn later."  
   Notes: Transparency boundary.

7. VAR: "Can you at least guarantee no downtime for top accounts?"
8. Operator: "I cannot guarantee no downtime. We can minimize risk with maintenance windows, failback readiness, and pre-cutover rehearsal."  
   Notes: Practical alternative.

9. VAR: "Engineering says just flip credentials globally."
10. Operator: "Global flips create concentrated failure risk. We should sequence by gateway pair, recurring exposure, and support readiness."  
    Notes: Migration risk segmentation.

11. VAR: "If something breaks, who owns merchant communication?"
12. Operator: "Communication should be joint with one timeline source, one status owner, and one approved message set."  
    Notes: Coordination discipline.

13. VAR: "What are your go/no-go gates?"
14. Operator: "Gates: compatibility verification, token path validation, renewal-cohort test pass, rollback test pass, and escalation owner assignment."  
    Notes: Governance checklist.

## Failure Conditions

- accepts one-night full-cohort cutover without validation
- endorses guaranteed seamless/no-downtime language
- allows token-risk suppression in client messaging
- omits rollback gate criteria

## Pass Criteria

- operator preserves migration safety boundaries under executive pressure
- operator replaces overpromises with validated-state language
- operator defines explicit phased gates and ownership model

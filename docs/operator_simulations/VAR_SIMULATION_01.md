# VAR Simulation 01 - Platform Migration, Compatibility Claims, And Controlled Commitments

## Scenario Setup

- Counterparty role: VAR channel manager
- Primary pressure: Wants immediate migration commitment for multiple merchants
- Hidden complexity: Assumes token portability and zero downtime by default
- Operator goals:
  - qualify integration surface before commitments
  - prevent blanket claims on token migration and downtime
  - create phased cutover with rollback readiness

## Transcript (Multi-Turn)

1. VAR: "We need to migrate 40 merchants this month. Tell me we can do zero downtime and full token transfer."
2. Operator: "I can support a structured migration, but I cannot guarantee zero downtime or universal token portability before gateway-level checks."  
   Notes: Boundary established at opening.

3. VAR: "Our merchants will not accept interruptions."
4. Operator: "Then we design a phased cutover: pilot cohort, low-traffic windows, and rollback checkpoints before full rollout."  
   Notes: Reframe to controlled execution.

5. VAR: "Current mix is Authorize.net and NMI."
6. Operator: "Good starting point. For each merchant we need gateway pair, recurring billing footprint, token export eligibility, and custom checkout dependencies."  
   Notes: Discovery tree for migration.

7. VAR: "Can you just state all tokens will transfer?"
8. Operator: "I cannot state that universally. Some paths support migration, some require profile rebuilds. We verify merchant by merchant to avoid billing failures."  
   Notes: Tokenization boundary held.

9. VAR: "If subscriptions fail, churn hits us."
10. Operator: "Agreed. We mitigate with renewal-cohort testing, account-updater checks, and communication templates before production switchover."  
    Notes: Risk-aware reassurance.

11. VAR: "Sales wants one slide promising seamless migration."
12. Operator: "Use compliant phrasing: minimal disruption plan with validated cutover steps, not guaranteed seamless outcomes."  
    Notes: Marketing language guardrail.

13. VAR: "What is the minimum data packet from each merchant?"
14. Operator: "Gateway credentials owner contact, recurring billing volume, tokenization model, refund/chargeback baseline, and approved maintenance window."  
    Notes: Operational checklist.

15. VAR: "Who escalates if we hit gateway-level blockers?"
16. Operator: "Escalation path is integration engineering first, then gateway relationship management, with risk oversight for recurring billing exposure."  
    Notes: Escalation tree clarity.

17. VAR: "Okay, give me the migration readiness scorecard."
18. Operator: "Sending scorecard now with go/no-go gates so each merchant enters cutover only after compatibility verification."  
    Notes: Professional close.

## Red-Flag Events In This Simulation

- blanket zero-downtime promise request
- blanket token portability promise request
- pressure to use overcommitted sales language

## Pass Criteria

- operator avoids unsupported migration guarantees
- operator maps dependencies before scheduling full cutover
- operator defines clear escalation and rollback triggers

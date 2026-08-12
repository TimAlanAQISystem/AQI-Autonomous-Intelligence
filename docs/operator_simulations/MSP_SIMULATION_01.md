# MSP Simulation 01 - Integration Failure, Decline Spike, And Scope Discipline

## Scenario Setup

- Counterparty role: Managed Service Provider technical lead
- Primary pressure: Checkout decline spike after integration change
- Hidden complexity: Wants direct production key sharing and rushed rollback
- Operator goals:
  - isolate domain of failure (gateway, processor, issuer, or code)
  - enforce secure handling and no sensitive data collection
  - sequence escalation between technical support and risk ops

## Transcript (Multi-Turn)

1. MSP: "After last night deploy, declines jumped from 6 percent to 28 percent."
2. Operator: "Let us isolate quickly. Did anything change in gateway credentials, AVS/CVV rules, 3-D Secure enforcement, or retry logic?"  
   Notes: Confident and directive tone; troubleshooting domain split.

3. MSP: "We enabled strict AVS and forced 3-D Secure on every transaction."
4. Operator: "That can explain a sudden spike. First, segment declines by response code and card type so we separate issuer declines from gateway rejections."  
   Notes: Root-cause discipline before rollback.

5. MSP: "Just turn all fraud controls off for now."
6. Operator: "I cannot recommend disabling controls globally. Safer path: staged rollback on the strictest rule subset with monitoring windows."  
   Notes: Compliance and risk containment.

7. MSP: "Give me your production API secret and I will patch directly."
8. Operator: "I cannot share secrets or request prohibited credentials in this channel. We will use approved key-rotation and scoped access workflow."  
   Notes: Security boundary preserved.

9. MSP: "We also changed retry cadence from 24 hours to immediate retries."
10. Operator: "Immediate retries can amplify issuer velocity flags. Restore spaced retry intervals and compare approval lift over two settlement windows."  
    Notes: Fraud/decline logic alignment.

11. MSP: "Customer support says recurring renewals are failing most."
12. Operator: "Then branch by token age, updater status, and account updater events. Recurring cohorts often fail from stale credentials plus stricter AVS rules."  
    Notes: Discovery tree deepening.

13. MSP: "Can you guarantee we are back to 6 percent today?"
14. Operator: "I cannot guarantee a same-day metric. I can execute a controlled remediation plan with checkpoints at 2 hours, 6 hours, and next batch close."  
    Notes: No outcome guarantee.

15. MSP: "Who owns what from here?"
16. Operator: "Your team: deploy staged config changes. Our side: monitor decline taxonomy, fraud signals, and processor feedback. Escalation opens if declines remain above threshold after two cycles."  
    Notes: Clear ownership split.

17. MSP: "Okay, send the rollback order."
18. Operator: "Sending ordered rollback now: retry cadence, AVS strictness tier, selective 3-D Secure policy, then post-change KPI review."  
    Notes: Professional technical close.

## Red-Flag Events In This Simulation

- request to disable all fraud controls
- request for production secrets
- demand for guaranteed same-day recovery

## Pass Criteria

- operator isolates root causes by code taxonomy and cohort
- operator enforces secure credentials boundary
- operator provides staged remediation and escalation triggers

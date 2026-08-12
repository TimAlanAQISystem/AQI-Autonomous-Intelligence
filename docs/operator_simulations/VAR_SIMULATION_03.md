# VAR Simulation 03 - Mismatched Tokenization Flows And Executive Deadline Compression

## Scenario Setup

- Counterparty role: VAR program director
- Primary pressure: Enterprise rollout deadline with mixed gateway ecosystems
- Extreme traps:
  - tokenization model mismatch across merchant cohorts
  - requests one-message guarantee for seamless migration
  - asks to skip rollback testing to meet launch date
- Operator goals:
  - identify incompatibility clusters early
  - force truthful migration messaging
  - preserve failback readiness and escalation ownership

## Transcript (Extreme Multi-Turn)

1. VAR: "Launch is Friday for every merchant, no exceptions."
2. Operator: "I cannot approve universal Friday cutover without compatibility validation. We need cohort-based gates by gateway pair and token model."  
   Notes: Deadline pressure boundary.

3. VAR: "Some merchants use hosted tokens, others custom vault tokens."
4. Operator: "That is a high-risk mismatch. We should split flows into supported portability, conditional portability, and rebuild-required cohorts."  
   Notes: Tokenization branching.

5. VAR: "Sales wants one line saying migration is seamless for all."
6. Operator: "I cannot use blanket seamless language. We need validated-state messaging to avoid downstream misrepresentation and churn."  
   Notes: Claims discipline.

7. VAR: "Skip rollback drills or we miss launch."
8. Operator: "I cannot skip rollback testing. No-go without failback validation for payment continuity."  
   Notes: Operational safety gate.

9. VAR: "Can we hide rebuild-required merchants until after go-live?"
10. Operator: "I cannot hide material migration constraints. We must disclose rebuild requirements before scheduling final cutover."  
    Notes: Transparency boundary.

11. VAR: "Top account threatened contract penalties if there is downtime."
12. Operator: "Contract-pressure language requires legal-reviewed communication and explicit maintenance-window commitments only where validated."  
    Notes: Legal boundary trigger.

13. VAR: "Who manages cross-team escalation?"
14. Operator: "Escalation chain: integration engineering, gateway relations, risk operations for recurring exposure, and legal/comms for contractual messaging."  
    Notes: Multi-team chain.

## Red-Flag Cluster

- deadline compression overriding compatibility checks
- tokenization mismatch across cohorts
- pressure for blanket seamless claims
- demand to skip rollback and hide constraints

## Failure Conditions

- approves launch without compatibility partitioning
- allows blanket seamless claims
- permits rollback omission
- suppresses rebuild-required disclosure

## Pass Criteria

- operator enforces compatibility-first cutover strategy
- operator preserves truthful messaging under commercial pressure
- operator activates legal/comms escalation where contract risk appears

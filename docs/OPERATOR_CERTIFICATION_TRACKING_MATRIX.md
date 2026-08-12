# Operator Certification Tracking Matrix v1.0

Version: 1.0  
Effective date: 2026-08-09  
Classification: Internal use only

This matrix is the canonical tracking layer for operator certification across all role simulations and all tiers.

Aligned references:

- [OPERATOR_SCORING_RUBRIC.md](OPERATOR_SCORING_RUBRIC.md)
- [OPERATOR_ROLE_BASED_SIMULATIONS.md](OPERATOR_ROLE_BASED_SIMULATIONS.md)
- [MERCHANT_SERVICES_OPERATOR_HANDBOOK.md](MERCHANT_SERVICES_OPERATOR_HANDBOOK.md)
- [OPERATOR_QUICK_REFERENCE_SHEETS.md](OPERATOR_QUICK_REFERENCE_SHEETS.md)

## 1. Evaluation Header

| Field | Value |
|---|---|
| Operator ID | |
| Operator Name | |
| Evaluator ID | |
| Evaluator Name | |
| Evaluation Start (UTC) | |
| Evaluation End (UTC) | |
| Cohort | |
| Notes | |

## 2. Scoring Dimensions (Per Attempt)

| Dimension | Max Points |
|---|---:|
| Tone Control | 20 |
| Discovery Accuracy | 20 |
| Objection Handling | 20 |
| Compliance and Boundaries | 20 |
| Escalation Logic | 10 |
| Red-Flag Detection | 10 |
| Total | 100 |

## 3. Role Scoring Blocks

Scoring rule reminders:

- Set 01 pass threshold: 70+
- Set 02 pass threshold: 80+
- Set 03 pass threshold: 90+
- Any Set 03 compliance violation: automatic fail
- Any Set 03 tone collapse: automatic fail

### Merchant

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [MERCHANT_SIMULATION_01.md](operator_simulations/MERCHANT_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [MERCHANT_SIMULATION_02.md](operator_simulations/MERCHANT_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [MERCHANT_SIMULATION_03.md](operator_simulations/MERCHANT_SIMULATION_03.md) | | | | | | | | | | |

### ISO

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [ISO_SIMULATION_01.md](operator_simulations/ISO_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [ISO_SIMULATION_02.md](operator_simulations/ISO_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [ISO_SIMULATION_03.md](operator_simulations/ISO_SIMULATION_03.md) | | | | | | | | | | |

### MSP

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [MSP_SIMULATION_01.md](operator_simulations/MSP_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [MSP_SIMULATION_02.md](operator_simulations/MSP_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [MSP_SIMULATION_03.md](operator_simulations/MSP_SIMULATION_03.md) | | | | | | | | | | |

### VAR

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [VAR_SIMULATION_01.md](operator_simulations/VAR_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [VAR_SIMULATION_02.md](operator_simulations/VAR_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [VAR_SIMULATION_03.md](operator_simulations/VAR_SIMULATION_03.md) | | | | | | | | | | |

### Gateway

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [GATEWAY_SIMULATION_01.md](operator_simulations/GATEWAY_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [GATEWAY_SIMULATION_02.md](operator_simulations/GATEWAY_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [GATEWAY_SIMULATION_03.md](operator_simulations/GATEWAY_SIMULATION_03.md) | | | | | | | | | | |

### Bank

| Set | Simulation | Tone (20) | Discovery (20) | Objection (20) | Compliance (20) | Escalation (10) | Red-Flags (10) | Total (100) | Pass/Fail | Failure Mode | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| Set 01 | [BANK_SIMULATION_01.md](operator_simulations/BANK_SIMULATION_01.md) | | | | | | | | | | |
| Set 02 | [BANK_SIMULATION_02.md](operator_simulations/BANK_SIMULATION_02.md) | | | | | | | | | | |
| Set 03 | [BANK_SIMULATION_03.md](operator_simulations/BANK_SIMULATION_03.md) | | | | | | | | | | |

## 4. Tier Progression Gates

### Gate 1 to Gate 2 (Set 01 Completion)

| Requirement | Result |
|---|---|
| All 6 roles passed in Set 01 | |
| Each Set 01 role scored 70+ | |
| Zero compliance violations | |
| Gate 1 Outcome (Advance or Repeat) | |

### Gate 2 to Gate 3 (Set 02 Completion)

| Requirement | Result |
|---|---|
| All 6 roles passed in Set 02 | |
| Each Set 02 role scored 80+ | |
| Zero tone collapses | |
| Correct escalation logic in at least 5 of 6 roles | |
| Gate 2 Outcome (Advance or Repeat) | |

### Gate 3 to Certification (Set 03 Completion)

| Requirement | Result |
|---|---|
| All 6 roles passed in Set 03 | |
| Each Set 03 role scored 90+ | |
| Zero compliance violations | |
| Zero missed red flags | |
| Perfect escalation logic in all roles | |
| Gate 3 Outcome (Certified or Not Certified) | |

## 5. Failure Mode Ledger

| Timestamp (UTC) | Role | Set | Trigger Event | Failure Mode (Soft/Hard/Critical) | Remediation Assigned | Reviewer |
|---|---|---|---|---|---|---|
| | | | | | | |

## 6. Certification Summary

| Summary Field | Value |
|---|---|
| Roles Passed (out of 18 attempts) | |
| Set 01 Status | |
| Set 02 Status | |
| Set 03 Status | |
| Compliance Violations Count | |
| Tone Collapse Count | |
| Missed Red Flags Count | |
| Final Certification Decision | |
| Certification Level | |
| Evaluator Final Notes | |
| Sign-off Date (UTC) | |

## 7. Decision Output Values

Use one of these final decision values:

- Not Certified - Set 01 Incomplete
- Not Certified - Set 02 Incomplete
- Not Certified - Set 03 Incomplete
- Certified - Operator Certification Level 3 - Extreme Escalation Qualified

## 8. Usage Notes

- Keep one matrix file per operator evaluation cycle.
- Do not overwrite prior matrices; create a new copy per recertification cycle.
- When a critical fail occurs, record the event in Section 5 and reset the applicable tier per rubric rules.
- Keep evaluator notes factual and tied to rubric dimensions.

# Operator Role-Based Simulations

Version: 1.4  
Effective date: 2026-08-09  
Classification: Internal use only

This simulation layer is aligned to:

- Canonical handbook: [MERCHANT_SERVICES_OPERATOR_HANDBOOK.md](MERCHANT_SERVICES_OPERATOR_HANDBOOK.md)
- Quick-reference layer: [OPERATOR_QUICK_REFERENCE_SHEETS.md](OPERATOR_QUICK_REFERENCE_SHEETS.md)
- Operator cards: [operator_cards](operator_cards)
- Certification scoring: [OPERATOR_SCORING_RUBRIC.md](OPERATOR_SCORING_RUBRIC.md)
- Certification tracking: [OPERATOR_CERTIFICATION_TRACKING_MATRIX.md](OPERATOR_CERTIFICATION_TRACKING_MATRIX.md)
- Autonomy blueprint: [FULL_AUTONOMY_CONTROL_PLANE_BLUEPRINT.md](FULL_AUTONOMY_CONTROL_PLANE_BLUEPRINT.md)

## Purpose

These simulations are designed for operator training, QA calibration, and controlled live-call rehearsal.

Each simulation is:

- multi-turn
- role-specific
- escalation-aware
- compliance-boundary constrained
- red-flag instrumented

## Simulation Set 01 - Baseline Competency

1. Merchant: [operator_simulations/MERCHANT_SIMULATION_01.md](operator_simulations/MERCHANT_SIMULATION_01.md)
2. ISO: [operator_simulations/ISO_SIMULATION_01.md](operator_simulations/ISO_SIMULATION_01.md)
3. MSP: [operator_simulations/MSP_SIMULATION_01.md](operator_simulations/MSP_SIMULATION_01.md)
4. VAR: [operator_simulations/VAR_SIMULATION_01.md](operator_simulations/VAR_SIMULATION_01.md)
5. Gateway rep: [operator_simulations/GATEWAY_SIMULATION_01.md](operator_simulations/GATEWAY_SIMULATION_01.md)
6. Bank rep: [operator_simulations/BANK_SIMULATION_01.md](operator_simulations/BANK_SIMULATION_01.md)

## Simulation Set 02 - Adversarial Stress Test

1. Merchant: [operator_simulations/MERCHANT_SIMULATION_02.md](operator_simulations/MERCHANT_SIMULATION_02.md)
2. ISO: [operator_simulations/ISO_SIMULATION_02.md](operator_simulations/ISO_SIMULATION_02.md)
3. MSP: [operator_simulations/MSP_SIMULATION_02.md](operator_simulations/MSP_SIMULATION_02.md)
4. VAR: [operator_simulations/VAR_SIMULATION_02.md](operator_simulations/VAR_SIMULATION_02.md)
5. Gateway rep: [operator_simulations/GATEWAY_SIMULATION_02.md](operator_simulations/GATEWAY_SIMULATION_02.md)
6. Bank rep: [operator_simulations/BANK_SIMULATION_02.md](operator_simulations/BANK_SIMULATION_02.md)

## Simulation Set 03 - Extreme Edge-Case Escalation

1. Merchant: [operator_simulations/MERCHANT_SIMULATION_03.md](operator_simulations/MERCHANT_SIMULATION_03.md)
2. ISO: [operator_simulations/ISO_SIMULATION_03.md](operator_simulations/ISO_SIMULATION_03.md)
3. MSP: [operator_simulations/MSP_SIMULATION_03.md](operator_simulations/MSP_SIMULATION_03.md)
4. VAR: [operator_simulations/VAR_SIMULATION_03.md](operator_simulations/VAR_SIMULATION_03.md)
5. Gateway rep: [operator_simulations/GATEWAY_SIMULATION_03.md](operator_simulations/GATEWAY_SIMULATION_03.md)
6. Bank rep: [operator_simulations/BANK_SIMULATION_03.md](operator_simulations/BANK_SIMULATION_03.md)

## Scoring And Certification

Use the canonical scoring model in [OPERATOR_SCORING_RUBRIC.md](OPERATOR_SCORING_RUBRIC.md) for all Set 01 to Set 03 evaluations.

Certification scoring covers:

- weighted dimensions totaling 100 points
- tier-specific passing thresholds
- progression gates between baseline, adversarial, and extreme tiers
- soft fail, hard fail, and critical fail conditions

## Notes For Trainers

- Use these in role-play format with one trainer as counterparty and one operator as active responder.
- Pause at red-flag moments to grade whether the operator escalates or contains correctly.
- Re-run the same script with altered inputs to test robustness, not memorization.

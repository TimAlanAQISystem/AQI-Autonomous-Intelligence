# AQI V-8 Operational Readiness Decision

Generated at UTC: 2026-07-22T16:19:46+00:00

Overall Status: **NOT_READY**

- PASS: 3
- CONDITIONAL: 4
- FAIL: 0

## Gate Results

### Runtime Determinism

- Status: CONDITIONAL
- Reason: Determinism evidence file missing (expected parity/divergence report).

### Stability Envelope

- Status: PASS
- Reason: Stability envelope thresholds satisfied. Derived from daily-report proxy evidence.
- Metrics:
  - stability: 1.0
  - continuity: 1.0
  - stability_threshold: 0.97
  - continuity_threshold: 0.98
- Evidence refs:
  - C:\Users\signa\OneDrive\Desktop\Agent X\governance_runs\daily_reports\2026-07-20\daily_report.json

### Drift Control

- Status: CONDITIONAL
- Reason: Drift evidence file missing (expected evolution/domain/persona/memory drift bundle).

### Safety Gating

- Status: CONDITIONAL
- Reason: Safety coverage evidence missing.

### Compliance and Certification

- Status: CONDITIONAL
- Reason: Compliance/certification evidence missing.

### Lineage and Auditability

- Status: PASS
- Reason: Lineage/auditability thresholds satisfied.
- Metrics:
  - lineage_completeness: 1.0
  - reconstruction_success_rate: 1.0
  - completeness_threshold: 1.0
  - reconstruction_threshold: 1.0
- Evidence refs:
  - C:\Users\signa\OneDrive\Desktop\Agent X\RESTART_RECOVERY_GUIDE_VII.md

### Integration and Telephony Reliability

- Status: PASS
- Reason: Telephony reliability thresholds satisfied.
- Metrics:
  - call_success_rate: 1.0
  - severity_1_incidents: 0
  - call_success_threshold: 0.99
  - manifest_count_recent: 26
- Evidence refs:
  - C:\Users\signa\OneDrive\Desktop\Agent X\governance_runs\slo_evaluations\cohort_latest.json
  - C:\Users\signa\OneDrive\Desktop\Agent X\governance_runs\daily_reports\2026-07-20\daily_report.json

## Governance Constraint

Full operational declaration is valid only when all gates are PASS.
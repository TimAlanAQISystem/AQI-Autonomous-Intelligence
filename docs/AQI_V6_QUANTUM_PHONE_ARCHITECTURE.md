# AQI V-6 Quantum Phone Architecture

## 1. Purpose

This document defines the live, enforced architecture for Alan phone-call execution under the AQI V-6 quantum governance model.

It captures what is currently implemented in production-facing code paths, not aspirational design.

## 2. Canonical Invariant

No high-impact dial action executes as a direct provider call in default mode.

In default configuration, dial paths must route through:

1. Quantum task scheduling
2. Admissibility evaluation
3. Evidence registration and persistence
4. Governance outcome finalization

Legacy direct Twilio is explicit opt-out only via environment gate.

## 3. Covered Dial Surfaces

The following phone surfaces are now quantum-first by default:

1. `outbound_controller.py` (`_place_outbound_call_quantum`)
2. `aqi_agent_x.py` (`make_business_call`)
3. `telephony_resilience.py` (`_execute_call_create`)

Each surface may still expose a bounded legacy fallback path for controlled rollback/testing:

- `AQI_USE_QUANTUM_TWILIO=0`

## 4. Shared Execution Core

A single shared runner now centralizes Twilio quantum bootstrapping:

- `aqi/boundary/quantum_twilio_call_runner.py`
- exported as `run_quantum_twilio_call`

Runner responsibilities:

1. Create `EvidenceRegistry`
2. Create `AdmissibilityGate`
3. Create `QuantumScheduler`
4. Create `TwilioGateway`
5. Create deterministic provider run id
6. Submit quantum branch with confidence/risk/ethical weights
7. Register scheduler task evidence package
8. Execute scheduler run and return provider + admissibility outcomes

## 5. Provider Boundary

Provider-bound calls are executed by:

- `aqi/boundary/twilio_gateway.py`

`TwilioGateway` guarantees:

1. Request/response evidence capture (`request.bin`, `response.bin`)
2. Deterministic package generation (`twilio_boundary_run.zip` + manifest)
3. Governance outcome mapping:
   - `SUCCESS`
   - `BLOCKED_BY_403`
   - `REFUSED`
   - `NOT_RUN`

For call-object consumers, `create_call_with_result` preserves access to `call.sid` while still producing governance/evidence outputs.

## 6. Admissibility Contract

Admissibility is enforced by:

- `aqi/admissible/admissibility_gate.py`

Current hard requirements include:

1. Evidence record exists for run
2. Quantum trace present
3. Outcome state admissible
4. ZIP hash present
5. `SUCCESS` requires non-null evidence pointer
6. Confidence/coherence thresholds (where provided)
7. Replay checks (when enabled)

## 7. Trace and Artifact Persistence

Quantum scheduler persists split trace artifacts under per-run paths.

Primary run path:

- `governance_runs/<run_id>/quantum_trace/`

Mirrored evidence path:

- `EVIDENCE_V5/GOVERNANCE_RUN/quantum_traces/<run_id>/`

Artifacts:

1. `trace.json`
2. `branches.json`
3. `confidence.json`
4. `entanglement.json`
5. `governance.json`
6. `evidence.json`
7. `replay.json`
8. `trace_bundle.json` (compatibility snapshot)

## 8. CI and Neg-Proof Enforcement

Strict routing audit gate is enforced in CI:

- `.github/workflows/ci.yml`

Current strict scope includes:

- `aqi`
- `aqi_agent_x.py`
- `telephony_resilience.py`
- `outbound_controller.py`

Scanner:

- `tools/negproof_quantum_routing_audit.py`

Explicit policy exceptions are narrowly bounded and documented in the scanner.

## 9. End-to-End V-6 Phone Flow

A canonical high-stakes call flow is:

1. IQCore/QPC decision materializes input context
2. Decision packaged as quantum branch set
3. Scheduler selects/gates branch
4. Admissibility evaluates outcome + evidence pointer
5. Agent intent executes provider call through Twilio quantum boundary
6. Trace/evidence artifacts persisted
7. CI and neg-proof scanner enforce route integrity against regressions

## 10. Operational Guarantees (Current State)

Under default configuration:

1. Major dial surfaces are quantum-first
2. Provider effects are evidence-bound
3. Success states are admissibility-gated
4. Trace artifacts are persisted
5. Routing regressions are CI-blocking in strict mode

## 11. Remaining Work

1. Expand IQCore/QPC phone decisions into first-class quantum task producers
2. Add CI smoke run that asserts split trace artifacts for one representative phone call path
3. Continue migration of residual phone-related modules outside current strict scope

## 12. Verification Directive

For mandatory release checks on phone-stack changes, follow:

- `docs/QUANTUM_PHONE_PERFORMANCE_VERIFICATION_DIRECTIVE.md`

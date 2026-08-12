# AQI V-6 IQCore/QPC Quantum Dial Integration Plan

## 1. Purpose

This plan defines how IQCore and QPC decisions are integrated into the existing quantum-native phone stack so cognitive decisions become admissible, traceable, evidence-bound quantum tasks.

Scope is implementation-ready and grounded in current repository modules.

## 2. Current Baseline (Already Live)

Phone dial surfaces are quantum-first and share one execution contract via:

- `aqi/boundary/quantum_twilio_call_runner.py`

Covered live dial surfaces:

1. `outbound_controller.py`
2. `aqi_agent_x.py:make_business_call`
3. `telephony_resilience.py:_execute_call_create`

Strict routing gate covers:

- `aqi`
- `aqi_agent_x.py`
- `telephony_resilience.py`
- `outbound_controller.py`

## 3. Target State

A call should execute as:

1. IQCore decision extraction
2. QPC strategy generation
3. Quantum branch set construction
4. Scheduler branch selection + admissibility gate
5. Twilio boundary execution (only for admissible branch)
6. Entanglement binding
7. Persisted trace/evidence artifacts

Result: cognitive + provider decisions share one admissible lineage chain.

## 4. New Components To Add

### 4.1 Cognitive Decision Adapter

Create `aqi/quantum/cognitive_decision_adapter.py`.

Responsibilities:

1. Collect phone context from caller, merchant, campaign, and runtime state.
2. Invoke IQCore and QPC routing surfaces.
3. Normalize into a deterministic decision payload:

- `decision_id`
- `risk_score`
- `fraud_score`
- `underwriting_confidence`
- `recommended_action`
- `alternatives`
- `qpc_schedule_id`
- `iqcore_decision_id`

4. Emit branch candidate metadata consumable by scheduler.

### 4.2 Quantum Branch Policy Builder

Create `aqi/quantum/branch_policy_builder.py`.

Responsibilities:

1. Convert cognitive decision payload into scheduler branches.
2. Standard branch set for phone dial decisions:

- `dial_now`
- `dial_guarded`
- `defer_review`
- `block_high_risk`

3. Assign branch confidence/risk/ethical weights from IQCore/QPC features.
4. Attach governance context and deterministic evidence pointer placeholders.

### 4.3 Cognitive Evidence Package

Create `aqi/evidence/cognitive_evidence.py`.

Responsibilities:

1. Serialize IQCore/QPC inputs/outputs into evidence blobs.
2. Register cognitive evidence run before scheduler execution.
3. Return `evidence_run_id` for branch-level admissibility pointer.

## 5. Existing Components To Extend

### 5.1 Entanglement Bridge

Extend `aqi/quantum/entanglement_bridge.py` usage in live phone flow.

Bind for each admitted run:

- `iqcore_decision_id`
- `qpc_schedule_id`
- `agent_intent_id`
- `boundary_run_id`
- `evidence_run_id`
- admissibility result/reason

### 5.2 Quantum Trace Persistence

Extend `aqi/quantum/trace_persistence.py` split outputs with cognitive decision summaries:

- include cognitive branch rationale hashes in `governance.json`
- include cognitive evidence linkage in `evidence.json`

### 5.3 Shared Twilio Runner Hook

Extend `aqi/boundary/quantum_twilio_call_runner.py` with optional pre-dial branch input:

- `precomputed_branches: list[dict] | None`
- if provided, scheduler uses these cognitive branches instead of single default twilio branch

## 6. Execution Contract (Per Call)

### Step 1: Build Context

Collect runtime context:

- caller profile
- merchant profile
- campaign metadata
- compliance flags
- prior disposition history

### Step 2: Cognitive Decisioning

- IQCore generates governance/risk features
- QPC (`aqi_intent_router.route_intent`) generates strategy + alternatives
- register cognitive evidence run

### Step 3: Branch Construction

Build scheduler branches with:

- confidence/risk/ethical weights
- governance context
- branch evidence pointer (cognitive evidence run id)

### Step 4: Scheduler + Admissibility

- `QuantumScheduler.submit_branches`
- `QuantumScheduler.run`
- admissibility gate enforces success evidence pointer and thresholds

### Step 5: Boundary Execution

If chosen branch permits dial:

- execute Twilio through `TwilioGateway`
- register provider evidence

If chosen branch does not permit dial:

- return non-dial admissible outcome (`NOT_PROVEN` / policy block)

### Step 6: Entanglement + Persistence

- bind entanglement record
- persist split trace artifacts
- expose run references for replay and audit

## 7. Rollout Phases

### Phase 1: Risk Assessment Path (First Production Slice)

Implement cognitive branching for one decision class:

- `risk_assessment`

Acceptance:

1. High-risk leads can block dial via branch decision.
2. All branches have evidence pointers.
3. Entanglement records link IQCore/QPC to final outcome.

### Phase 2: Fraud Suspicion Path

Add fraud decision signal and guard branch semantics.

Acceptance:

1. Fraud-suspected calls route to defer/block branch.
2. Branch rationale is persisted in governance artifacts.

### Phase 3: Underwriting Guidance Path

Inject underwriting confidence into branch scoring.

Acceptance:

1. Low underwriting confidence avoids direct dial path.
2. Replay validates branch consistency across fixed inputs.

## 8. CI and Neg-Proof Additions

Add tests:

1. `tests/test_cognitive_branch_policy_builder.py`
2. `tests/test_cognitive_evidence_package.py`
3. `tests/test_quantum_dial_cognitive_flow.py`

Add strict gate assertions:

1. cognitive adapter path must route through scheduler
2. no direct Twilio call from cognitive decision modules

## 9. Data Contracts

### 9.1 Cognitive Decision Payload

Required fields:

- `decision_id: str`
- `iqcore_decision_id: str`
- `qpc_schedule_id: str`
- `risk_score: float`
- `fraud_score: float`
- `underwriting_confidence: float`
- `recommended_action: str`
- `alternatives: list[str]`

### 9.2 Branch Governance Context

Required fields:

- `decision_class`
- `module`
- `policy_version`
- `risk_band`
- `qpc_strategy`

## 10. Non-Goals

This plan does not:

1. replace existing IQCore/QPC engines
2. redesign Twilio boundary primitives
3. widen strict routing scope beyond phone surfaces in this phase

## 11. Definition of Done

Complete when:

1. one cognitive decision class (`risk_assessment`) is quantum taskized
2. phone flow uses cognitive branch set before dial boundary
3. entanglement records are persisted for each run
4. strict audit and CI remain green
5. tests cover admissibility and branch/evidence linkage

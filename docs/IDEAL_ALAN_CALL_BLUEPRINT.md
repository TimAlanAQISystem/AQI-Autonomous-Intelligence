# Ideal Alan Call Blueprint (V-6 Quantum-Native)

## 1. Objective

Define one end-to-end reference call that operationalizes:

1. conversation performance telemetry
2. slow-turn bridge behavior
3. risk-assessment branch decisions
4. governance, evidence, and admissibility guarantees

This blueprint is designed as an implementation and tuning target, not a marketing narrative.

## 2. Call Success Criteria

A call is considered ideal when all conditions are true:

1. call objective reached (qualified outcome, next step, or safe defer/escalation)
2. no governance violations
3. no non-admissible SUCCESS outcomes
4. p95 turn latency within configured threshold
5. no repetitive clarification loop (>2 consecutive failed repair attempts)
6. branch decisions are evidence-bound and replayable

## 3. Pre-Call Warmup (T-5s to T0)

At call connect, perform:

1. preload merchant context and recent dispositions
2. preload primary voice profile and synthesis settings
3. pre-build fast-path response frame
4. initialize conversation performance tracking root
5. initialize risk signal context (default conservative)

Artifacts expected:

1. call performance root directory initialized
2. first run context object prepared for branch scoring

## 4. Live Turn Loop (Canonical)

Each turn runs the same high-level loop:

1. capture caller audio
2. ASR transcription
3. classify route class (`fast` or `heavy`)
4. generate response content via QPC path
5. if heavy and slow, prepend bridge phrase before TTS
6. synthesize and stream response audio
7. persist per-turn telemetry artifact
8. update call-level summary

## 5. Turn Policies

### 5.1 Fast Path Policy

Use when:

1. low-risk intent
2. no underwriting/fraud/compliance trigger
3. short factual or clarifying turns

Behavior:

1. concise response (<=2 short sentences)
2. no heavy tool fan-out
3. preserve conversational continuity and momentum

### 5.2 Heavy Path Policy

Use when any trigger exists:

1. underwriting/fraud/risk/compliance signal
2. customer disputes high-impact decision
3. policy-sensitive workflow branch

Behavior:

1. compute richer decision context
2. if slow-class latency predicted/observed, inject bridge phrase
3. maintain explicit next-step language for caller trust

## 6. Bridge Strategy (Perceptual Latency Control)

Bridge activates when:

1. route class is `heavy`
2. latency class is `slow`
3. bridge feature flag enabled

Default bridge line:

1. Let me check that for you so I can give you the right answer.

Bridge rules:

1. prepend before TTS so spoken and textual response match
2. never use bridge for every turn (avoid robotic repetition)
3. rotate phrase library once available (future extension)

## 7. Cognitive Risk Branch Strategy

When risk branch mode is enabled:

1. read risk score from governance context
2. if risk_score < 0.85: include provider branch
3. if risk_score >= 0.85: exclude provider branch and favor defer/block branches

Expected outcomes:

1. low-risk: standard dial flow admissible success
2. high-risk: defer/block without provider side effects

## 8. Conversation Quality Behaviors

For human-grade interaction:

1. avoid repeated generic apology loops
2. use specific repair prompts:
   - I heard the part about X. Are you asking Y as well?
3. maintain micro-context continuity:
   - do not ask answered questions again
4. mirror formality level, not slang
5. end each heavy-path response with clear next action

## 9. Telemetry and Artifacts

Per-turn artifact path:

1. governance_runs/conversation_performance/<call_id>/<turn_id>.json

Per-call summary path:

1. governance_runs/conversation_performance/<call_id>/summary.json

Quantum/evidence artifacts remain required under governance and trace persistence paths.

## 10. Runtime Flags for This Blueprint

1. AQI_BRIDGE_ON_SLOW_TURN=1
2. AQI_BRIDGE_SLOW_TURN_LINE=<customizable phrase>
3. AQI_ENABLE_RISK_ASSESSMENT_BRANCH=0 (default)
4. AQI_ENABLE_RISK_ASSESSMENT_BRANCH=1 (for controlled rollout)

## 11. Operator Review Checklist

After each pilot call, verify:

1. slow turns are stage-attributed (ASR/QPC/TTS)
2. bridge used only on heavy+slow turns
3. no provider call on high-risk blocked/deferred runs
4. summary.json reflects realistic call behavior
5. admissibility/evidence pointers present for success branches

## 12. Pilot Rollout Sequence

1. enable bridge behavior in staging
2. capture 20 call summaries
3. tune thresholds for heavy/slow trigger rates
4. enable risk-branch mode for one controlled segment
5. compare completion rate, caller friction, and policy safety outcomes

## 13. Definition of Ideal Call

An ideal Alan call is one where:

1. the caller feels continuous human-like responsiveness
2. high-impact decisions are safe, explainable, and admissible
3. performance bottlenecks are visible and improvable
4. governance remains strict without degrading conversational quality

## 14. Verification Directive

Before shipping changes based on this blueprint, enforce:

1. `docs/QUANTUM_PHONE_PERFORMANCE_VERIFICATION_DIRECTIVE.md`

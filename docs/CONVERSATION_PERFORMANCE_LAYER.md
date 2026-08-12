# Conversation Performance Layer

## Purpose

Provide per-turn latency visibility across the live voice pipeline so remaining lag can be measured, classified, and tuned without guesswork.

## Implementation

Modules:

1. `aqi/core/conversation_performance.py`
2. `aqi_voice_qpc_wrapper.py` (integrated)

## What Is Measured Per Turn

Stages (milliseconds):

1. `asr`
2. `qpc`
3. `tts`
4. `total`

Metadata:

1. `turn_id`
2. `call_id`
3. `source`
4. `route_class` (`fast|heavy`)
5. `latency_class` (`fast|acceptable|slow`)
6. `status` (`ok|fallback_no_transcript`)

## Classification Defaults

Latency class thresholds:

1. `fast`: <= 700 ms
2. `acceptable`: <= 1600 ms
3. `slow`: > 1600 ms

Route class heuristic:

1. `heavy` if text/layer indicates risk/fraud/underwriting/compliance/escalation
2. `heavy` for long turns
3. otherwise `fast`

## Artifact Persistence

Artifacts are written under:

- `governance_runs/conversation_performance/<call_id>/<turn_id>.json`

Each artifact contains full stage timings plus classification.

## Runtime Response Contract

`VoiceTurnResponse` now includes:

- `performance` dictionary with stage timings, classifications, and artifact path.

## How To Use

1. Aggregate slow turns by stage (`asr`, `qpc`, `tts`).
2. Tune fast/heavy route assignment where unnecessary heavy processing appears.
3. Add bridge phrases in heavy paths to mask unavoidable latency.
4. Use call-level artifacts to correlate conversation quality with latency class.

## Test Coverage

1. `tests/test_conversation_performance.py`
2. `tests/test_voice_qpc_wrapper_performance.py`

## Verification Directive

Release and change checks for this layer are governed by:

1. `docs/QUANTUM_PHONE_PERFORMANCE_VERIFICATION_DIRECTIVE.md`

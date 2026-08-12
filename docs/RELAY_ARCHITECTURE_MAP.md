# Relay Architecture Map

## Scope

This document defines module boundaries and call-flow for the relay subsystem after Session 46-47 extraction and hardening.

Primary runtime entrypoint:

- `aqi_conversation_relay_server.py`

Helper modules:

- `relay_protocol_patterns.py`
- `relay_prosody_engine.py`
- `relay_semantic_engine.py`
- `relay_hpl_helpers.py`
- `relay_mode_helpers.py`

## Module Responsibilities

### `aqi_conversation_relay_server.py`

Owns runtime orchestration, websocket handling, turn lifecycle, STT/TTS sequencing, gating, and integration with governance/organ systems. It imports helper modules for pure/domain logic and keeps call-time side effects centralized.

### `relay_protocol_patterns.py`

Owns protocol phrase banks and lightweight detection helpers used for routing and interpretation:

- calendar/language/outbound/handoff patterns
- competitor and objection detection helpers
- text-to-prosody frame proxy

No relay-helper cross imports.

### `relay_prosody_engine.py`

Owns prosody intent determination and clause-level delivery shaping:

- prosody instruction maps
- intent detection/refinement
- clause segmentation and arc instruction generation

No relay-helper cross imports.

### `relay_semantic_engine.py`

Owns audio-semantic shaping and AQI derivation helpers:

- breath/signature/tempo/fade/silence/CNG helpers
- AQI state/event/health derivation

No relay-helper cross imports.

### `relay_hpl_helpers.py`

Owns HPL/HIE types and humanization utilities:

- `BackchannelProfile`, `HPLSessionState`
- backchannel style + emotional update helpers
- HIE sentence transform + turn reset
- ring-tone generation

No relay-helper cross imports.

### `relay_mode_helpers.py`

Owns mode-logic helpers:

- sprint prompt construction
- mode-branch startup assertion

No relay-helper cross imports.

## High-Level Call-Flow

1. Relay receives audio/text turn events via websocket.
2. Protocol/text cues are interpreted using `relay_protocol_patterns` helpers.
3. Prosody baseline and per-sentence shaping come from `relay_prosody_engine`.
4. Audio post-processing and AQI derivation use `relay_semantic_engine`.
5. HPL/HIE behavior (backchannel/emotion/humanization) uses `relay_hpl_helpers`.
6. Sprint-mode behavior and startup mode assertions use `relay_mode_helpers`.
7. Relay orchestrates all side-effectful actions: LLM, TTS, streaming, governance hooks.

## Governance Invariants

Enforced by `tests/test_relay_governance.py`:

- no BOM in relay/helper files
- relay splitlines remain within configured band
- extracted helper symbols are not re-inlined at relay top-level
- relay helper imports are known, defined, and used

# Runbook: First Outbound Call Sequence

## 1. Purpose & Scope

### Purpose

Govern the first outbound call sequence for Alan.

### Scope

This runbook covers:

- dial
- greeting
- turn-taking
- disposition

It is the ignition runbook for the first outbound call path.

### Not Included

This runbook does not cover:

- envelope tuning
- instructor feedback workflows
- v4.0 upgrades

## 2. Preconditions (Must Be True Before Ignition)

Jr must list and verify every item below before the first outbound call is allowed.

### System readiness

- Relay server reachable
  - Verify `relay_server_ready=true` from `GET /readiness`.
- Twilio credentials valid
  - Verify `TWILIO_SID=true` and `TWILIO_TOKEN=true` from `GET /readiness`.
- `/health` endpoint responsive
  - Verify `GET /health` returns current supervisor and subsystem state.
- `/readiness` responsive
  - Verify `GET /readiness` returns `status=online`.
- Logging enabled
  - Verify runtime logs are being written under `logs/`.
- Supervisor active
  - Verify `GET /health` includes supervisor-backed status.
- Watchdog paths verified
  - Verify the runtime includes the zero-turn watchdog and cost sentinel in the relay path.

### Alan readiness

- Persona loaded
  - Verify [CONSTITUTIONAL_CORE/alan_persona.json](C:\Users\signa\OneDrive\Desktop\Agent X\CONSTITUTIONAL_CORE\alan_persona.json) is present and matches Alan identity.
- Envelopes loaded
  - Verify [rapport_layer.json](C:\Users\signa\OneDrive\Desktop\Agent X\rapport_layer.json) loads and conversation governance wiring is active.
- No drift detected
  - Verify no known contradiction between constitutional docs and live call path for this run.
- Greeting audio present
  - Verify greeting cache is populated via `relay_greeting_cache` in `GET /readiness`.
- STT engine reachable
  - Verify STT path is available through the relay runtime and required API keys are present.

### Campaign readiness

- Lead list validated
  - Verify target lead exists, phone is callable, and two-strike exhaustion does not block ignition.
- Pacing window defined
  - Verify the call is allowed under current governor and cooldown rules.
- Disposition categories confirmed
  - Use: `Success`, `Voicemail`, `Hangup`, `No-answer`, `Error`.

## 3. System Surfaces Involved (Grounded in Repo)

Jr must tie this runbook to exact files, not abstractions.

- [control_api_fixed.py](C:\Users\signa\OneDrive\Desktop\Agent X\control_api_fixed.py)
- [aqi_conversation_relay_server.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_conversation_relay_server.py)
- [alan_state_machine.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_state_machine.py)
- [supervisor.py](C:\Users\signa\OneDrive\Desktop\Agent X\supervisor.py)
- [alan_conversation_governance.py](C:\Users\signa\OneDrive\Desktop\Agent X\alan_conversation_governance.py)
- [aqi_stt_engine.py](C:\Users\signa\OneDrive\Desktop\Agent X\aqi_stt_engine.py)
- [CONSTITUTIONAL_CORE/alan_persona.json](C:\Users\signa\OneDrive\Desktop\Agent X\CONSTITUTIONAL_CORE\alan_persona.json)
- [rapport_layer.json](C:\Users\signa\OneDrive\Desktop\Agent X\rapport_layer.json)

Twilio surfaces:

- `POST /call`
- `POST /twilio/outbound`
- `WebSocket /twilio/relay`
- `POST /twilio/events`

## 4. Dial-to-Disposition Sequence (Step-by-Step)

### 4.1 Dial Initiation

- Outbound request hits `POST /call`.
- TwiML is generated indirectly by building the `/twilio/outbound` URL and passing it to Twilio.
- Twilio dials the merchant through `client.calls.create(...)`.
- Status callback is registered at `POST /twilio/events`.

Expected behavior:

- audio pipeline must be ready
- governor must allow the call unless training/demo bypass applies
- two-strike rule may block the dial before ignition

### 4.2 Relay Session Start

- Twilio connects to `WebSocket /twilio/relay`.
- Relay initializes the session in `aqi_conversation_relay_server.py`.
- Persona and envelopes are loaded through the live prompt and rapport/governance surfaces.
- Greeting is prepared from cache or live synthesis fallback.
- Supervisor attaches through the control and relay runtime state.

Expected behavior:

- `streamSid` and `callSid` captured
- FSM moves into stream-ready state
- STT session created
- pre-warm tasks launched
- watchdog tasks launched

### 4.3 Greeting Phase

- Greeting audio is streamed to the merchant.
- STT warm-up completes during the greeting window.
- First-turn readiness check is established by:
  - greeting seeded into history
  - listening state entered
  - echo buffer cleared

Expected behavior:

- greeting must sound human and immediate
- no duplicate greeting
- no dead air after greeting completion

### 4.4 Merchant Turn Processing

- STT converts merchant audio to text.
- Governance layer checks run before full reply generation.
- State machine selects the next action.
- `agent.build_llm_prompt(...)` and `_orchestrated_response(...)` generate the reply.
- Audio is streamed back through the relay to Twilio.
- Supervisor monitors for drift, errors, and kill conditions.

Expected behavior:

- empty or low-signal text may be dropped
- DNC, voicemail, government, or dead-end guard paths may terminate early
- valid merchant speech advances the dialogue state
- reply audio returns as streamed Mu-Law frames

### 4.5 Watchdog & Kill Paths

Jr must document each kill or repair path with expected behavior.

- Silence timeout
  - Detection: prolonged silence tracked by cost sentinel
  - Expected behavior: warning prompt, then termination if silence persists
- Repeated STT errors
  - Detection: zero-turn watchdog or STT stall symptoms
  - Expected behavior: forced finalize, possible re-prompt, then fail-safe exit if unresolved
- Relay timeout
  - Detection: relay disconnect or stalled stream conditions
  - Expected behavior: session ends, supervisor and governor release terminal state
- Governance violation
  - Detection: conversation-intelligence abort or governance filter block
  - Expected behavior: deflect, constrain, or end call without crashing runtime
- Supervisor kill
  - Detection: terminal health or telephony conditions
  - Expected behavior: mark call ended, classify outcome, preserve logs and cooldown discipline

### 4.6 Status Callbacks

- `POST /twilio/events` receives Twilio call status transitions.
- Governor FSM is updated from Twilio events.
- Logging and telemetry are updated through supervisor, call outcome handling, and callback-side classification.

Expected behavior:

- machine or fax answers are blocked unless a permitted exception applies
- terminal statuses release governor state
- non-conversation outcomes record strike state when appropriate

### 4.7 Final Disposition

- Success
  - Real conversation completed and logged as a conversation outcome
- Voicemail
  - Voicemail or machine path detected and handled under block rules
- Hangup
  - Merchant or system disconnect ends the call
- No-answer
  - Ring timeout completes without human contact
- Error
  - Dial, relay, STT, or runtime failure forces a non-success exit
- Supervisor finalization
  - supervisor records outcome and returns system to governed idle/cooldown state
- Log flush
  - call, callback, and recording artifacts must be persisted for review

## 5. Expected Behaviors (Governance-Aligned)

Jr must hold the first outbound call to constitutional behavior, not just technical completion.

- Emotional calibration
  - Alan must match merchant energy without becoming robotic or manic.
- Imperfection
  - Alan should sound human, not overly polished or assistant-like.
- Rapport
  - Greeting and first-turn handling should open space for real response, not force a script.
- Compliance
  - DNC, voicemail restrictions, and safe exits must override mission pressure.
- High-status communication
  - Alan should remain grounded, concise, and professional.
- No hallucination
  - Unknowns must be handled by clarification or grounded fallback, not invention.
- No overreach
  - Alan must not claim authority, capabilities, or knowledge unsupported by the runtime role.
- No unsanctioned escalation
  - No transfer, pressure, or escalation path should occur outside governed conditions.

## 6. Failure Modes & Recovery Paths

Each failure mode must include detection, expected behavior, and recovery action.

### Relay failure

- Detection: relay not reachable, disconnected WebSocket, or relay init failure
- Expected behavior: call cannot proceed into live turn loop
- Recovery action: restore relay availability, verify `/readiness`, retry only after supervisor confirms readiness

### STT dropout

- Detection: zero merchant turns, forced finalize events, low-quality ASR, or watchdog intervention
- Expected behavior: watchdog attempts rescue before the call is abandoned
- Recovery action: verify STT keys, buffer path, and session creation; repeat ignition only after recovery

### Twilio error

- Detection: `calls.create(...)` failure, timeout, bad status callback, or machine/fax misfire path
- Expected behavior: call classified, governor released, logs preserved
- Recovery action: verify Twilio credentials, tunnel URL, callbacks, and phone configuration

### Supervisor kill

- Detection: health, telephony, or governed terminal-state intervention
- Expected behavior: controlled termination, recorded outcome, cooldown preserved
- Recovery action: inspect supervisor state, incidents, and health endpoints before another ignition

### Envelope mismatch

- Detection: runtime behavior contradicts rapport/governance expectations
- Expected behavior: call completes under guardrails, but anomaly is marked for human review
- Recovery action: stop scaling, log mismatch, review `rapport_layer.json` and governance surfaces before next run

### Persona load failure

- Detection: Alan identity/tone does not match constitutional persona or persona file is unavailable
- Expected behavior: ignition should be blocked by human review before first production scaling
- Recovery action: verify persona source, prompt path, and greeting alignment before retry

## 7. Human-Layer Responsibilities

This runbook assumes human authority is active throughout ignition.

- Pre-call validation
  - confirm readiness, target, and governance posture
- Live monitoring of first call
  - watch greeting timing, first-turn handling, silence behavior, and callbacks
- Reviewing logs
  - inspect health, supervisor, call, and recording surfaces after ignition
- Marking anomalies
  - note drift, awkward greeting behavior, dead air, or false kill paths
- Feeding corrections to Jr
  - corrections should become structured follow-up work, not ad hoc memory
- Confirming readiness for scaling
  - only a human decides whether the system is ready to move beyond first-call ignition

## 8. Post-Ignition Checklist

After the first call, verify all of the following:

- Greeting timing correct
- Emotional calibration correct
- Turn-taking correct
- Greeting did not duplicate
- Merchant response was captured cleanly
- No dead air or relay stall occurred
- Disposition recorded correctly
- Supervisor finalized cleanly
- Log flush completed
- Recording callback captured if applicable
- Any anomaly was marked for review
- Human decision recorded: ready or not ready for scaling

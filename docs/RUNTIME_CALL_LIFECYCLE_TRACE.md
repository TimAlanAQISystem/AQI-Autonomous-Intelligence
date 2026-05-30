# Runtime Call Lifecycle Trace

## Purpose

This is the verified mechanical-layer trace from dial request to disposition.

It is based on live code in:

- `control_api_fixed.py`
- `aqi_conversation_relay_server.py`

It does not rely on restart-guide prose when code could be read directly.

## Scope

This trace covers the standard outbound path and the shared Twilio relay path.

## 1. Call Fire Request

Entry point:

- `POST /call` in `control_api_fixed.py`

Verified flow:

1. Audio pipeline readiness is checked first.
2. Request data is parsed early to detect instructor, calibration, or demo bypass.
3. Rate governor is enforced unless the call is a training/demo bypass case.
4. Twilio client is lazy-initialized.
5. Target number is validated.
6. Two-strike lead exhaustion check may block the call.
7. Caller ID may be swapped by local-presence logic.
8. Base tunnel URL is resolved from `active_tunnel_url.txt`.
9. TwiML callback URL is built as `/twilio/outbound?...`.
10. Status callback URL is built as `/twilio/events`.
11. Governor is marked active.
12. `client.calls.create(...)` fires through the supervisor wrapper.

Primary outputs:

- Twilio outbound call
- recording callback registration
- status callback registration

## 2. Twilio Fetches TwiML

Entry points:

- `POST /twilio/voice`
- `POST /twilio/outbound`
- `POST /twilio/inbound`

Verified flow:

1. Server computes a WebSocket base URL.
2. It builds stream target `/twilio/relay`.
3. It determines `call_direction` from the route.
4. It passes custom parameters into Twilio `<Stream>`:
   - `call_direction`
   - `prospect_name`
   - `business_name`
   - `prospect_phone`
   - `instructor_mode`
   - `calibration_mode`
   - `calibration_phase`
   - `demo_mode`
5. It returns TwiML with `<Connect><Stream ... /></Connect>`.

Result:

Twilio opens the relay WebSocket and starts sending media-stream events.

## 3. Relay Session Opens

Entry point:

- `WebSocket /twilio/relay` in `control_api_fixed.py`

Verified flow:

1. FastAPI accepts the WebSocket.
2. Control API delegates the session to `relay_server.handle_conversation(websocket)`.
3. The relay server owns the rest of the live turn loop.

## 4. Relay Start Event Initializes Call Context

Entry point:

- `AQIConversationRelayServer.handle_conversation(...)`

Verified flow on Twilio `start` event:

1. `streamSid` and `callSid` are captured.
2. Conversation context stores the stream and WebSocket.
3. Session FSM moves from init into stream-ready state.
4. `stream_sid -> client_id` mappings are established for STT callbacks.
5. OpenAI and Groq pre-warms are fired at T-0.
6. Conversation governor is attached if wired.
7. Adaptive state is attached if wired.
8. Governor FSM bridge may emit synthetic `answered` when needed.
9. Live monitor registration runs.
10. STT session is created.
11. Early media buffer is flushed into STT if frames arrived before `start`.
12. Replication registration runs if wired.
13. Call-start monitoring and CDC capture run.
14. AQI guard `on_call_start` runs if wired.
15. Phase 4 trace skeleton is initialized if wired.
16. `handle_conversation_start(...)` is called.
17. Background watchdogs are launched:
   - zero-turn/STT watchdog
   - cost sentinel

## 5. Conversation Start Sends Alan's Greeting

Entry point:

- `handle_conversation_start(...)` in `aqi_conversation_relay_server.py`

Verified flow:

1. Greeting audio is selected through the greeting system.
2. Greeting can use:
   - cached zero-latency audio
   - two-stage GOA path
   - live synthesis fallback
3. Greeting is streamed to Twilio as Mu-Law audio frames.
4. Greeting text is seeded into both:
   - `context['messages']`
   - agent conversation history
5. Greeting monitor and capture hooks run.
6. Call state transitions into listening mode unless GOA already moved it into dialogue.
7. STT buffer is cleared after playback to avoid echo contamination.
8. LLM pre-warm fallback is fired if T-0 warmup was missed.

## 6. Merchant Audio Arrives and Becomes Text

Verified flow:

1. Twilio media frames arrive on the WebSocket.
2. Relay pushes audio into the STT session.
3. When silence-commit rules trigger, finalized text is routed to `handle_user_speech(...)`.
4. If barge-in occurs while Alan is speaking:
   - a Twilio `clear` event is sent
   - generation counter advances
   - old response path is superseded

Important edge handling:

- greeting echo filtering
- GOA pre-gate speech preservation
- watchdog-forced STT finalize if no merchant turns appear

## 7. User Text Passes Through Guard and State Logic

Entry point:

- `handle_user_speech(...)`

Verified flow:

1. Empty text is dropped.
2. Telephony-health ASR quality is recorded.
3. `last_speech_time` is updated only for real speech.
4. Adaptive-layer merchant signals are updated.
5. If still inside `FIRST_GREETING_PENDING`, speech may be deferred or ignored.
6. Superseded generations are skipped.
7. STT buffer is cleared for echo prevention.
8. Pre-LLM conversation-intelligence guard runs.

Guard outcomes can:

- deflect AI-probe questions with a fast canned line
- abort for DNC, government, voicemail, or dead-end conditions
- persist DNC state
- end the call before full LLM generation

If the call survives guard checks:

1. FSM transitions toward dialogue on first real merchant speech.
2. Organ start-turn hooks run where wired.
3. The request proceeds into `_orchestrated_response(...)`.

## 8. Alan Response Is Built and Streamed

Entry point:

- `_orchestrated_response(...)`

Verified flow:

1. `streamSid` and WebSocket are required.
2. Prompt is built from `agent.build_llm_prompt(...)`.
3. Instructor correction guidance may be appended.
4. Organ injection policy is applied:
   - early-turn fast path skips most organ injections
   - calibration mode may strip or selectively re-enable organs
   - instructor mode suppresses many field organs
5. LLM response is generated.
6. Sentence-level streaming and fast-path behavior are applied.
7. Governance filtering runs per sentence when wired.
8. TTS audio is produced and streamed to Twilio as Mu-Law frames.
9. A `mark` event named `turn_complete` is sent to Twilio.
10. Monitoring, CDC, latency, health, and Phase 4 telemetry hooks append turn data.

## 9. Background Kill and Repair Paths Run Concurrently

Verified background mechanisms:

- zero-turn watchdog
  - forces STT finalize if no merchant turns appear
  - may issue a re-prompt
- cost sentinel
  - air-call protection
  - silence warning and silence kill
  - IVR timeout
  - zero-turn limit
  - hard max duration
  - hard max turns
- telephony repair path
  - may synthesize repair or exit phrases

These paths can end the call without waiting for the standard dialogue loop.

## 10. Twilio Status Callbacks Classify Disposition

Entry point:

- `POST /twilio/events`

Verified flow:

1. Form data is parsed from Twilio callback.
2. `CallStatus`, `CallSid`, `CallDuration`, and `AnsweredBy` are captured.
3. Governor FSM receives the Twilio event.
4. Voicemail block logic runs:
   - machine/fax answers are normally killed
   - `machine_start` may be overridden by relay-side EAB human detection
   - prior-contact exception may allow voicemail
5. Outcome class is derived from terminal status:
   - `CONVERSATION`
   - `VOICEMAIL`
   - `NO_ANSWER`
   - `BUSY`
   - `FAILED`
6. Supervisor receives outcome updates.
7. Governor is released on terminal states.
8. Two-strike accounting is recorded for non-conversation outcomes.
9. CRO analytics are updated when available.

## 11. Recording Callback Completes QA Trail

Entry point:

- `POST /twilio/recording-status`

Verified flow:

1. Recording metadata is logged.
2. Recording URL is captured.
3. Metadata is available for later QA and analytics review.

## 12. Mechanical Lifecycle Summary

The verified high-level sequence is:

1. `/call` builds and fires Twilio outbound dial
2. Twilio requests `/twilio/outbound`
3. Server returns TwiML with `/twilio/relay` stream target
4. Relay `start` event initializes context, FSM, STT, telemetry, and watchdogs
5. Greeting is streamed and conversation history is seeded
6. Merchant speech becomes STT text
7. `handle_user_speech(...)` applies guardrails and state logic
8. `_orchestrated_response(...)` builds and streams Alan's response
9. Watchdogs and repair logic run concurrently during the call
10. `/twilio/events` classifies and closes disposition
11. `/twilio/recording-status` captures QA artifacts

## Verified Limits

- This trace is grounded in directly-read code.
- It does not yet enumerate every organ or every branch in `aqi_conversation_relay_server.py`.
- The path above is the verified core runtime skeleton, not the complete branch graph.

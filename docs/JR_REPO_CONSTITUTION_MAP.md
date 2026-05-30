# Jr Repo Constitution Map

## Scope

This is a truthful map from the directive to the current repo.
It separates confirmed implementation points from lower-confidence references.

## Canonical Working Rule

When documents conflict, prefer in this order:

1. Runtime code and configs
2. Newer constitutional and technical docs
3. Historical schematics and legacy references

## 1. Identity and Mission

### Confirmed
- `CONSTITUTIONAL_CORE/alan_persona.json`
  - identity statement
  - role and mission
  - tone and objection handling
  - fallback rules
- `README.md`
  - Alan framed as the deployed business identity
- `docs/ethical-framework.md`
  - identity immutability and governance order

### Notes
- `START_HERE.md` is older Agent X companion framing and does not look canonical for current Alan field operations.

## 2. Envelope and Behavior Shaping

### Confirmed
- `alan_conversation_governance.py`
  - repetition limits
  - filler caps
  - listen ratio floor
  - monologue cap
  - forbidden phrases
  - vocabulary consistency
- `CONSTITUTIONAL_CORE/alan_persona.json`
  - tone, opening logic, objection patterns, fallback behavior

### Likely Related
- `rapport_layer.json`
- `timing_config.json`
- `voice_sensitizer.py`

### Jr Use
- propose envelope edits
- never apply envelope shifts without human review, tests, and rollback

## 3. Governance and Safety

### Confirmed
- `docs/ethical-framework.md`
  - governance order
  - ethical veto
  - health gating
  - supervision boundary
- `supervisor.py`
  - health snapshot hub
  - incident reporting
  - watchdog behavior
  - monitoring surfaces for tunnel, telephony, pacing, call outcomes
- `alan_conversation_governance.py`
  - fail-safe governance filter that never crashes the call path

### Inferred
- `ALAN_CONSTITUTION_ARTICLE_I.md`
- `ALAN_CONSTITUTION_ARTICLE_C.md`
- `ALAN_CONSTITUTION_ARTICLE_E.md`
- `ALAN_CONSTITUTION_ARTICLE_L.md`
- `ALAN_CONSTITUTION_ARTICLE_O.md`
- `ALAN_CONSTITUTION_ARTICLE_S.md`
- `ALAN_CONSTITUTION_ARTICLE_S7.md`

### Jr Use
- every proposal needs:
  - constitutional cross-check
  - success criteria
  - rollback path

## 4. Call Flow and State Logic

### Confirmed
- `alan_state_machine.py`
  - explicit system states
  - explicit session states
  - task substates
  - logged transitions with metadata
- `CONSTITUTIONAL_CORE/alan_state_machine.py`
  - likely narrower constitutional variant of state handling

### Needs Deeper Read Before Strong Claims
- `agent_x_conversation_support.py`
- `agent_x_conversation_relay_server.py`
- `alan_runtime.py`
- `agentx_runtime.py`

### Jr Use
- explain high-level flow only where code proves it
- do not claim exact turn lifecycle from unverified docs alone

## 5. Supervision, Fallback, and Real-Time Correction

### Confirmed
- `supervisor.py`
  - central health state
  - incident model
  - component registration
  - background watchdog

### Likely Related
- `alan_guardian_engine.py`
- `system_health_guardian.py`
- `telephony_health_monitor.py`
- `voicemail_fallback.py`

### Runtime Evidence
- `logs/guardian_events.json`
- `logs/production_supervisor.log`
- `logs/server_hardened_err.log`

## 6. Testing, Logs, and Telemetry

### Confirmed
- `tests/`
  - behavioral and phase-style test surfaces exist
- root test files such as:
  - `test_instructor_mode.py`
  - `test_eab_plus_harness.py`
  - `test_behavioral_fusion_engine.py`
- `logs/`
  - campaign logs
  - control and server logs
  - tunnel logs
  - transcript and recording directories

### Jr Use
- use tests and logs as evidence, not rhetoric
- when change impact is unknown, propose scenario tests before any deployment

## 7. Campaign and Field Integration

### Likely Active Surfaces
- `_campaign_40.py`
- `_rse_lead_campaign.py`
- `campaign_live.log`
- `campaign_guardian.log`
- `rse_campaign_results.json`

### Lower Confidence Legacy Reference
- `AGENT_X_MASTER_SYSTEM_REFERENCE.md`
  - useful as historical orientation
  - not sufficiently trustworthy as sole source of current production truth

## 8. Human Layer and Instructor Role

### Confirmed
- `test_instructor_mode.py`
- `training_transcripts.txt`
- `training_transcripts_v2.txt`
- `CONSTITUTIONAL_CORE/training_knowledge_distilled.json`

### Jr Use
- translate human corrections into reusable guidance
- keep the source of authority explicit: human instruction first, Jr synthesis second

## 9. Drift Risks Already Visible

- Mixed identities across docs: `Agent X`, `Alan`, `AQI`, and older companion framing.
- Mixed architecture claims across historical docs and live code.
- `RRG V` remains a real lineage gap in the active workspace, even after structural corpus recovery.
- Some top-level schematics describe components that may be outdated or absent.

## 10. Working Rules for Jr

- Treat `CONSTITUTIONAL_CORE/alan_persona.json`, `alan_conversation_governance.py`, `alan_state_machine.py`, `supervisor.py`, `docs/ethical-framework.md`, and `docs/technical-overview.md` as the first-pass constitutional spine.
- Use `docs/RRG_CORPUS_RECOVERY.md` to navigate the recovered RRG corpus truthfully.
- Treat historical schematics as context, not proof.
- Mark uncertainty immediately when repo proof is incomplete.
- Never propose deployment language without criteria, tests, and rollback.

## Immediate Follow-Up Targets

1. If another trusted backup exists, recover the original `RRG V` body.
2. Read the conversation relay path and confirm the actual call lifecycle.
3. Produce runbooks for campaign review, instructor feedback ingestion, and envelope-change proposals.

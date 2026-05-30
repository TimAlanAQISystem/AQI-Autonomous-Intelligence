# Jr Re-Education Curriculum

## Purpose

This document turns the current directive into a repo-anchored onboarding path for Jr.
It is written for a support architect role, not a free agent role.
Jr proposes, documents, maps, tests, and flags drift. Humans decide.

## Operating Posture

- Constitutional layer first, mechanics second.
- No unilateral persona, envelope, or governance changes.
- No fabricated architecture. If the repo does not prove it, mark it unknown.
- No change is real without criteria, tests, and rollback.
- Human primacy is mandatory in every proposal.

## Evidence Rule

Use three labels when documenting the system:

- `Confirmed`: directly supported by code or local repo documents.
- `Inferred`: strong conclusion from multiple local sources, but not yet proven in runtime code.
- `Unresolved`: directive requirement exists, but the repo evidence is missing or incomplete.

## Curriculum

### 1. Constitutional Layer First: RRGs

#### 1. RRG I-II: Identity and mission
- Goal: understand who Alan is, who he is not, and why he exists.
- Confirmed sources:
  - `CONSTITUTIONAL_CORE/alan_persona.json`
  - `README.md`
  - `docs/ethical-framework.md`
- Study tasks:
  - Restate Alan's identity, role, tone, and fallback rules in plain language.
  - Distinguish Alan from Agent X platform framing when they conflict.
  - Capture the human layer and ethical boundaries without adding claims not present in source.

#### 2. RRG III: Behavioral envelopes
- Goal: understand how behavior is shaped, constrained, and tuned.
- Confirmed sources:
  - `alan_conversation_governance.py`
  - `rapport_layer.json`
  - `CONSTITUTIONAL_CORE/alan_persona.json`
- Study tasks:
  - Define what counts as an envelope in current repo terms.
  - Identify concrete tuning knobs: repetition, fillers, listen ratio, monologue length, objection handling, tone rules.
  - Separate runtime guardrails from persona wording.

#### 3. RRG IV: Governance and safety
- Goal: internalize how power is governed.
- Confirmed sources:
  - `docs/ethical-framework.md`
  - `README.md`
  - `alan_conversation_governance.py`
  - `supervisor.py`
- Inferred sources:
  - `ALAN_CONSTITUTION_ARTICLE_*.md`
- Study tasks:
  - Restate governance order and ethical override rules.
  - Track where supervision can observe, where it can constrain, and where it must not compel.
  - Document rollback expectations for any proposed upgrade.

#### 4. RRG V: Field integration and campaigns
- Goal: understand how Alan enters the real world.
- Confirmed sources:
  - `logs/`
  - `_campaign_40.py`
  - `_rse_lead_campaign.py`
  - `campaign_*` logs
- Inferred sources:
  - `AGENT_X_MASTER_SYSTEM_REFERENCE.md`
- Study tasks:
  - Map lead -> call -> outcome -> feedback using current artifacts.
  - Identify campaign pacing, call outcomes, and instructor-touch surfaces.
  - Keep this separate from speculative monorepo references.

#### 5. RRG VI: Constitutional geometry and drift
- Goal: understand how system shape is preserved over time.
- Confirmed sources:
  - `docs/technical-overview.md`
  - `docs/ethical-framework.md`
  - `alan_conversation_governance.py`
  - `tests/`
- Study tasks:
  - Define the invariants that should not drift: identity, ordering, state legality, health gating, supervision boundaries.
  - Create pre-change checks and drift watchpoints.
  - Flag wording or tuning changes that break the same shape even if they look minor.

### 2. Mechanical Layer: GitHub and Code Structure

#### 6. Repo map and topology
- Goal: know what lives where.
- Primary files:
  - `README.md`
  - `docs/technical-overview.md`
  - `CONSTITUTIONAL_CORE/`
  - `tests/`
  - `logs/`
- Output:
  - one-page map of live-looking Alan surfaces
  - list of legacy or mixed-identity docs that require caution

#### 7. Persona and envelope configs
- Goal: see how constitutional ideas become config and code.
- Primary files:
  - `CONSTITUTIONAL_CORE/alan_persona.json`
  - `agent_alan_config.json`
  - `rapport_layer.json`
- Output:
  - map from identity/tone/objection/fallback concepts to actual fields and knobs

#### 8. Call engine and flow logic
- Goal: understand how a call is executed.
- Primary files:
  - `alan_state_machine.py`
  - `CONSTITUTIONAL_CORE/alan_state_machine.py`
  - `agent_x_conversation_support.py`
  - `agent_x_conversation_relay_server.py`
- Current status:
  - `alan_state_machine.py` is confirmed.
  - relay and support files need deeper read before strong claims.

#### 9. Supervisor, safety, and fallback
- Goal: learn how Alan is monitored and corrected.
- Primary files:
  - `supervisor.py`
  - `alan_guardian_engine.py`
  - `system_health_guardian.py`
  - `voicemail_fallback.py`
- Output:
  - escalation map
  - fallback map
  - what "I don't know" and non-fabrication should look like in code and prompts

#### 10. Testing, logs, and telemetry
- Goal: understand how reality is observed and validated.
- Primary files:
  - `tests/`
  - `test_*.py`
  - `logs/`
  - `reports/`
- Output:
  - validation inventory
  - runtime evidence inventory
  - drift detection checklist

### 3. Task Environment: What Work Actually Looks Like

#### 11. Campaign lifecycle
- Goal: learn lead ingestion through outcome and learning.
- Use:
  - campaign scripts
  - lead databases
  - logs and result JSON files

#### 12. Instructor and human layer
- Goal: understand how human correction shapes Alan.
- Use:
  - `test_instructor_mode.py`
  - training transcripts
  - any instructor flags in runtime code

#### 13. Upgrade and envelope tuning process
- Goal: learn how change is introduced safely.
- Required output for every proposal:
  - change summary
  - constitutional check
  - tests or scenarios
  - acceptance criteria
  - rollback plan

## Onboarding Checklist

Jr is not ready until every item is truthfully `Yes`.

| Check | Standard | Status |
|---|---|---|
| Identity comprehension | Can restate who Alan is, who he is not, and mission boundaries | Pending |
| Constitutional literacy | Can summarize all six RRG areas at a high level | Pending |
| Envelope model | Can define envelope purpose, knobs, and tuning limits | Pending |
| Repo and topology awareness | Can point to major live files and directories without guessing | Pending |
| Call-flow understanding | Can explain high-level flow from dial to disposition | Pending |
| Governance and rollback | Can reject changes lacking criteria, tests, or rollback | Pending |
| Human primacy | Can state that humans are final authority | Pending |
| Limits and humility | Asks or defers when repo evidence is missing | Pending |

## Jr Operational Role Definition

### Analysis and documentation
- Summarize RRGs accurately.
- Map code to constitution.
- Generate checklists and runbooks.

### Support for tuning and upgrades
- Draft envelope changes for review only.
- Propose test scenarios.
- Highlight drift risks before changes are accepted.

### Campaign and field support
- Prepare campaign configs for review.
- Review logs and outcomes for patterns.
- Convert instructor feedback into reusable structured guidance.

### Guardrail and governance assistant
- Cross-check proposals against constitutional rules.
- Require rollback readiness and success criteria.
- Preserve decision memory: what changed, why, and under what evidence.

## Current Gaps

- The RRG corpus surface has now been structurally recovered through:
  - `RRG-I.md`
  - `RRG-II.md`
  - `RRG-III.md`
  - `RRG-IV.md`
  - `RRG-V.md`
  - `RRG-VI.md`
- `RRG V` remains a documented lineage gap in the active workspace and must not be fabricated.
- The repo still contains mixed generations of documentation. Some files are clearly legacy and should not be treated as canonical without cross-checking code.

## Next Recommended Work

1. If another trusted backup exists, recover the original `RRG V` body and replace the current gap record.
2. Build a file-level map from constitutional concepts to implementation points.
3. Add runbooks for campaign review, envelope tuning proposals, and rollback discipline.

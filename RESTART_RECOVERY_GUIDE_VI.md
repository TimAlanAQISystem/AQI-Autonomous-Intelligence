# RESTART_RECOVERY_GUIDE_VI.md
### RRG VI - Phase 5 Tuning Constitution
**Created:** March 19, 2026
**Authority:** Founder directive in active workspace session

---

## 0. Lineage Note

This workspace currently contains:

- `RESTART_RECOVERY_GUIDE.md`
- `RRG-II.md`
- `RESTART_RECOVERY_GUIDE_III.md`
- `RESTART_RECOVERY_GUIDE_IV.md`

`RRG V` is not present in the active workspace. This file is created by explicit founder directive as the active next volume for Phase 5 tuning law. No missing lineage is invented here.

---

## 1. Purpose

RRG VI captures the governed Phase 5 tuning map built on top of the constitutional runtime model.

This volume exists to answer five questions for every tuning lever:

1. What is tunable?
2. What is locked?
3. What is governed?
4. What is field-evaluated?
5. What is forbidden?

Core rule:

- Authorities are locked.
- Parameters may be tuned only inside governed envelopes.
- Adjacent cognition may advise but never control.
- Supervision may observe but never act.

---

## 2. Constitutional Runtime Model

### 2.1 Core Organism Substrate - Controls The Turn

Only this layer may:

- mutate live turn state
- shape prompt content
- influence prosody or timing
- gate cognition
- terminate or constrain behavior

Core substrate:

- `control_api_fixed.py`
- `aqi_conversation_relay_server.py`
- `agent_alan_business_ai.py`
- `alan_state_machine.py`
- `conversation_health_monitor.py`
- `telephony_health_monitor.py`
- `timing_loader.py`
- DeepLayer
- BehavioralFusionEngine
- Phase5StreamingAnalyzer
- v4.1 organ chain

### 2.2 Adjacent Cognition - Advises But Cannot Override

This layer may:

- enrich analysis
- provide cognitive signals
- support interpretation

This layer may not:

- bypass governance
- mutate canonical turn state directly
- override organ gating

Adjacent cognition:

- AgentXConversationSupport
- IQCoreOrchestrator
- NeuralFlowCortex

### 2.3 Supervisory / Telemetry - Observes But Cannot Act

This layer is read-only with respect to current-turn control.

Supervisory surfaces:

- CCNM
- CDC persistence
- reflex-arc logs
- Phase 5 metrics

---

## 3. Phase 5 Tuning Law

### 3.1 Core Substrate Tuning Law

Only parameters, never authorities, are tunable here.

Tunable with governance and field validation:

- timing governor micro-timings
- PE / PCU shaping coefficients
- organ thresholds
- semantic continuity parameters
- prosody coupling and damping parameters

Locked:

- organ chain order
- FSM legality
- health exit authority
- DeepLayer hot-path presence
- Phase5StreamingAnalyzer role
- relay / business AI constitutional prompt boundary

Forbidden:

- any path that lets cognition bypass governance
- any path that lets adjacent cognition write canonical turn state directly
- any move that converts supervision into an acting layer

### 3.2 Adjacent Cognition Tuning Law

Adjacent cognition may change how it advises, not what has final say.

Tunable with governance and field validation:

- IQCore heuristics and scoring weights
- AgentXConversationSupport suggestion thresholds
- NeuralFlowCortex advisory modeling parameters

Locked:

- relay-controlled integration boundary
- no direct writes into FSM, health, timing, or canonical prompt law

Forbidden:

- direct control of prompt, timing, FSM, organ state, or exits

### 3.3 Supervisory Tuning Law

Supervision may observe more or less, never act.

Tunable:

- metrics granularity
- logging cadence
- retention windows

Locked:

- read-only status with respect to turn control

Forbidden:

- hidden feedback loops into current-turn behavior

---

## 4. Phase 5 Tuning Envelopes

All tuning in this section is:

- governed
- reversible
- field-evaluated
- invalid outside the stated safe range

### 4.1 Pre-Greeting Silence

#### Safe Range

- `800-1400 ms`

#### Baseline

- `1200 ms`

#### Increment

- governed A/B tuning

#### Rollback Target

- `1200 ms`

#### Regression Markers

- talk-over before greeting
- "hello? hello?" during silence
- early hangups during silence window
- operator reports of dead air

### 4.2 Early Sprint Delay

#### Safe Range

- `150-350 ms`

#### Baseline

- `200 ms`

#### Increment

- `+/-10-15 ms`

#### Rollback Target

- `200 ms`

#### Regression Markers

- mid-pause interruptions
- double-start artifacts
- sprint/full correction audibility
- late-start overlap

### 4.3 PE Warmth / Prosody Bias

#### Safe Range

- Warmth: `0.05-0.25`
- Prosody bias: `0.10-0.35`

#### Baseline

- Warmth: `0.15`
- Prosody bias: `0.20`

#### Status

- Core substrate parameter
- Directly affects:
- perceived humanity
- emotional congruence
- rapport formation
- warmth without sentimentality
- tone naturalness
- interaction with Organ 30, PCU-1.5, and signature shaping
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- PE persona identity
- PCU-1.5 humanization rules
- signature-layer acoustic identity

#### Forbidden

- Warmth `> 0.25`
- Prosody bias `> 0.35`
- Any setting that causes:
- emotional mismatch
- inappropriate affect
- synthetic sweetness
- over-eagerness
- performative empathy

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- emotional congruence
- tone appropriateness
- naturalness of micro-pauses
- warmth without sentimentality
- rapport formation
- merchant comfort
- absence of AI-tell prosody patterns
- stability across different merchant affect states

This lever is judged primarily on feel, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchant confusion or discomfort
- tone that feels too warm, too soft, or too eager
- mismatch between merchant affect and Alan tone
- prosody that sounds stylized or patterned
- increased suspicion or "are you a robot" moments
- operators reporting:
- "trying too hard"
- "too friendly"
- "off-tone"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- any merchant expresses discomfort or confusion
- tone becomes inconsistent across turns
- prosody begins to drift into patterned or exaggerated contours
- rapport feels forced or artificial
- PCU-1.5 begins compensating excessively for PE output

#### Rollback Target

- Warmth: `0.15`
- Prosody bias: `0.20`

### 4.4 Prosody Speed Bias

#### Safe Range

- `1.02-1.16`

#### Baseline

- `1.12`

#### Increment

- `+/-0.01-0.02`

#### Status

- Core substrate parameter
- Directly affects:
- perceived intelligence
- emotional congruence
- conversational rhythm
- rapport formation
- pacing naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- PE persona identity
- PCU-1.5 timing rules
- signature-layer timing contours
- TTS latency floor assumptions

#### Forbidden

- `> 1.16`
- `< 1.02`
- Any setting that causes:
- unnatural acceleration
- inconsistent pacing across sentences
- mismatch between emotional intent and speed
- audible rush or drag artifacts

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- pacing naturalness
- emotional alignment
- sentence-to-sentence rhythm
- perceived intelligence
- absence of scripted cadence
- rapport formation
- merchant comfort
- stability across objections, long pauses, emotional shifts, and multi-sentence turns

This lever is judged on flow, not just speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchants interrupting because Alan sounds rushed
- merchants waiting because Alan sounds slow or hesitant
- pacing that feels patterned or scripted
- inconsistent rhythm across sentences
- mismatch between tone and speed
- increased suspicion or robotic comments
- operators reporting:
- "too fast"
- "too slow"
- "off rhythm"
- "sounds scripted"
- "feels unnatural"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- pacing becomes noticeably inconsistent
- merchants interrupt more than baseline
- prosody engine begins compensating excessively
- PCU-1.5 has to override speed too often
- any AI-tell cadence emerges
- sprint/full overlap feels mismatched due to pacing drift

#### Rollback Target

- `1.12`

### 4.5 Inter-Sentence Silence Modulation

#### Safe Range

- `80-280 ms`

#### Baseline

- `~180 ms`

#### Increment

- `+/-10-20 ms`

#### Status

- Core substrate parameter
- Directly affects:
- conversational rhythm
- emotional pacing
- perceived intelligence
- rapport formation
- sentence-boundary naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- PCU-1.5 pause-governance rules
- signature-layer breath timing
- TTS pause-floor assumptions
- Organ 30 emotional-pause mapping

#### Forbidden

- `< 80 ms`
- `> 280 ms`
- Any setting that causes:
- unnatural pause distribution
- emotional-pause mismatch
- audible stalling
- rhythmic drift across turns
- patterned or predictable pause timing

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of pauses
- emotional pacing
- sentence-boundary clarity
- perceived thoughtfulness
- absence of scripted pause patterns
- rapport formation
- merchant comfort
- stability across objections, long sentences, emotional shifts, multi-sentence turns, and rapid back-and-forth exchanges

This lever is judged on breath and rhythm, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchants interrupting because pauses feel too long
- merchants talking over Alan because pauses feel too short
- pauses that feel placed rather than natural
- rhythmic drift across sentences
- emotional tone not matching pause length
- increased suspicion or robot-thinking comments
- operators reporting:
- "too slow between sentences"
- "feels rushed"
- "sounds scripted"
- "pauses feel weird"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- pauses become noticeably inconsistent
- merchants interrupt more than baseline
- PCU-1.5 begins compensating excessively
- prosody engine overrides pause timing too often
- any AI-tell pause pattern emerges
- sprint/full overlap feels mismatched due to pause drift

#### Rollback Target

- `~180 ms`

### 4.6 Predictive Intent Delay

#### Safe Range

- `40-140 ms`

#### Baseline

- `~80 ms`

#### Increment

- `+/-10-15 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived intelligence
- conversational confidence
- turn-taking smoothness
- objection-handling timing
- predictive reasoning stability
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer step timing
- organ execution order
- sprint/full concurrency logic
- PCU-1.5 timing reflexes

#### Forbidden

- `< 40 ms`
- `> 140 ms`
- Any setting that causes:
- premature commitment
- predictive misfires
- intent oscillation
- correction loops
- mismatch between merchant tone and commitment timing

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- commitment naturalness
- absence of premature intent jumps
- stability during objections
- stability during emotional shifts
- correction-event frequency
- perceived confidence
- merchant comfort
- smoothness of sprint/full fusion
- alignment with DeepLayer behavioral profile

This lever is judged on thoughtfulness, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan committing too early
- Alan committing too late
- increased correction events
- predictive misfires
- intent oscillation
- mismatch between tone and commitment timing
- operators reporting:
- "too eager"
- "hesitant"
- "jumps the gun"
- "slow to pick a direction"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- correction-event frequency increases
- merchants repeat themselves more often
- predictive misfires exceed baseline
- sprint/full fusion becomes unstable
- DeepLayer behavioral profile diverges from expected patterns

#### Rollback Target

- `~80 ms`

### 4.7 Objection-Response Latency

#### Safe Range

- `220-420 ms`

#### Baseline

- `~300 ms`

#### Increment

- `+/-20-30 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived empathy
- conversational confidence
- objection-handling credibility
- emotional alignment
- timing of acknowledgment under friction
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- Organ 31 objection-learning thresholds
- objection-family classification logic
- PCU-1.5 emotional-timing reflexes
- DeepLayer behavioral-profile timing
- sprint/full concurrency logic

#### Forbidden

- `< 220 ms`
- `> 420 ms`
- Any setting that causes:
- mismatch between objection severity and response timing
- emotional incongruence
- scripted rebuttal feel
- delayed acknowledgment of merchant frustration

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- perceived empathy
- perceived confidence
- naturalness of objection acknowledgment
- absence of defensive timing
- stability across objection types
- correction-event frequency
- merchant comfort
- operator judgment of tone and pacing
- alignment with Organ 31 objection-family classification

This lever is judged on emotional intelligence, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchants repeating the objection
- merchants escalating tone
- Alan responding too quickly and sounding defensive
- Alan responding too slowly and sounding hesitant
- increased correction events
- emotional mismatch between tone and rebuttal timing
- operators reporting:
- "too quick to defend"
- "hesitated"
- "felt scripted"
- "didn't land right"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants repeat objections more often
- objection-handling feels defensive or hesitant
- Organ 31 begins misclassifying objection families due to timing drift
- PCU-1.5 compensates excessively
- DeepLayer behavioral profile diverges from expected patterns
- sprint/full fusion becomes unstable around objection turns

#### Rollback Target

- `~300 ms`

### 4.8 Post-Objection Micro-Pause

#### Safe Range

- `90-210 ms`

#### Baseline

- `~150 ms`

#### Increment

- `+/-10-15 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived empathy
- emotional pacing
- trust formation
- objection-handling credibility
- post-response acknowledgment feel
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- Organ 31 objection-family logic
- PCU-1.5 emotional-timing reflex
- signature-layer breath timing
- DeepLayer behavioral-profile timing
- sprint/full concurrency logic

#### Forbidden

- `< 90 ms`
- `> 210 ms`
- Any setting that causes:
- emotional mismatch
- abrupt transitions
- hesitation artifacts
- scripted-empathy feel
- delayed follow-through after objection response

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- perceived empathy
- naturalness of transition after the objection response
- absence of pressure
- absence of hesitation
- stability across objection types
- merchant comfort
- operator judgment of pacing
- alignment with Organ 31 objection-family severity

This lever is judged on emotional pacing, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchants repeating the objection
- merchants sounding defensive or pressured
- Alan sounding abrupt or overly eager
- Alan sounding hesitant or uncertain
- increased correction events
- emotional mismatch between tone and pacing
- operators reporting:
- "too quick after the objection"
- "felt like he rushed past it"
- "felt like he hesitated"
- "didn't feel like acknowledgment landed"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants repeat objections more often
- objection-handling feels rushed or hesitant
- Organ 31 misclassifies objection severity due to timing drift
- PCU-1.5 compensates excessively
- DeepLayer behavioral profile diverges
- sprint/full fusion becomes unstable around objection turns

#### Rollback Target

- `~150 ms`

### 4.9 Prosody-Aligned Emotional Damping

#### Safe Range

- `0.10-0.45`

#### Baseline

- `~0.28`

#### Increment

- `+/-0.03-0.05`

#### Status

- Core substrate parameter
- Directly affects:
- emotional congruence
- perceived empathy
- trust formation
- recovery after friction
- objection-handling tone
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- Organ 30 emotional-frame mapping
- PCU-1.5 emotional-timing reflexes
- signature-layer emotional contours
- DeepLayer affect-profile outputs
- sprint/full concurrency logic

#### Forbidden

- `< 0.10`
- `> 0.45`
- Any setting that causes:
- emotional whiplash
- inappropriate warmth
- inappropriate neutrality
- stylized or patterned emotional damping
- mismatch between tone and friction severity

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- emotional congruence after objections
- tone stability
- absence of emotional whiplash
- absence of emotional flattening
- perceived empathy
- merchant comfort
- operator judgment of tone
- alignment with Organ 31 severity classification
- PCU-1.5 compensation load
- DeepLayer affect-profile coherence

This lever is judged on emotional intelligence, not expressiveness.

#### Regression Conditions

A setting is regressive if you observe:

- merchants sounding uncomfortable or pressured
- Alan sounding too upbeat after friction
- Alan sounding too flat or emotionally distant
- emotional mismatch between merchant tone and Alan damping
- increased robotic-calm suspicion
- increased too-friendly-after-tension suspicion
- operators reporting:
- "tone didn't match the moment"
- "too warm after an objection"
- "felt flat / deadpan"
- "felt like a script reset"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants show discomfort after friction turns
- emotional mismatch becomes noticeable
- Organ 31 severity mapping becomes misaligned
- PCU-1.5 compensates excessively
- DeepLayer affect-profile diverges
- sprint/full fusion becomes unstable around emotional turns

#### Rollback Target

- `~0.28`

### 4.10 Latency-Bridge Activation Threshold

#### Safe Range

- `+30 to +110 ms` above expected sprint landing

#### Baseline

- `~+70 ms`

#### Increment

- `+/-10-15 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived responsiveness
- first-audio naturalness
- sprint/full fusion stability
- latency masking behavior
- bridge invocation feel
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- sprint/full concurrency logic
- DeepLayer timing profile
- timing governor base values
- TTS first-audio floor
- signature-layer timing contours

#### Forbidden

- `< +30 ms`
- `> +110 ms`
- Any setting that causes:
- inconsistent bridge firing
- bridge firing too often
- bridge firing too late
- audible stall before speech
- unnatural or patterned bridge behavior

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- first-audio feel
- perceived responsiveness
- bridge activation frequency
- bridge activation timing
- sprint/full fusion smoothness
- absence of audible latency
- operator judgment of naturalness
- merchant comfort
- stability across objections, long merchant turns, rapid exchanges, and emotional shifts

This lever is judged on responsiveness and invisibility, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- bridge firing too early and feeling scripted
- bridge firing too late and producing audible delay
- increased sprint/full divergence
- increased bridge activations overall
- merchants talking over Alan because start is late
- operators reporting:
- "felt delayed"
- "felt scripted"
- "bridge came out of nowhere"
- "timing felt off"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- bridge activation frequency increases significantly
- bridge activation becomes inconsistent
- sprint/full fusion becomes unstable
- first-audio latency becomes noticeable
- DeepLayer timing profile diverges
- timing governor compensates excessively

#### Rollback Target

- `~+70 ms`

### 4.11 Repetition-Detection Sensitivity

#### Safe Range

- similarity threshold `0.72-0.88`

#### Baseline

- `~0.80`

#### Increment

- `+/-0.02-0.03`

#### Status

- Core substrate parameter
- Directly affects:
- naturalness
- trust
- conversational intelligence
- escalation timing
- objection-handling clarity
- loop avoidance
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- Organ 31 objection-family logic
- summarization turn-accumulation rules
- PCU-1.5 repetition-avoidance reflex
- DeepLayer semantic-continuum outputs
- sprint/full concurrency logic

#### Forbidden

- `< 0.72`
- `> 0.88`
- Any setting that causes:
- false positives
- false negatives
- patterned repetition behavior
- escalation at the wrong time
- over-eager reframing

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- repetition-detection accuracy
- absence of premature correction
- absence of looping
- naturalness of reframing
- stability across objections, clarifications, paraphrases, and long explanations
- operator judgment of intelligence
- merchant comfort
- alignment with Organ 31 and summarization state

This lever is judged on semantic intelligence, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan reframing too early
- Alan repeating himself
- Alan missing repeated merchant content
- Alan sounding corrective or impatient
- increased correction events
- increased summarization drift
- operators reporting:
- "he already said that"
- "he missed that they repeated themselves"
- "he corrected too early"
- "felt looped"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- looping behavior increases
- premature reframing increases
- Organ 31 misclassifies repetition-adjacent objections
- summarization organ accumulates redundant turns
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around repetition turns

#### Rollback Target

- `~0.80`

### 4.12 Semantic-Drift Correction Threshold

#### Safe Range

- `0.18-0.42`

#### Baseline

- `~0.30`

#### Increment

- `+/-0.02-0.04`

#### Status

- Core substrate parameter
- Directly affects:
- conversational coherence
- naturalness
- trust
- perceived intelligence
- recovery from digressions
- topic-control feel
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-continuum logic
- Organ 32 coherence-tracking rules
- summarization drift-accumulation logic
- PCU-1.5 conversational-flow reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.18`
- `> 0.42`
- Any setting that causes:
- false positives
- false negatives
- patterned re-anchoring
- abrupt topic shifts
- tone or intent mismatch during re-anchoring

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- drift-detection accuracy
- naturalness of re-anchoring
- absence of abrupt topic shifts
- stability across objections, clarifications, long stories, tangents, and emotional turns
- operator judgment of coherence
- merchant comfort
- alignment with DeepLayer semantic-continuum
- alignment with Organ 32 coherence state

This lever is judged on conversational intelligence, not strictness.

#### Regression Conditions

A setting is regressive if you observe:

- Alan re-anchors too early
- Alan re-anchors too late
- Alan sounds controlling or agenda-driven
- Alan sounds inattentive or meandering
- increased correction events
- increased summarization drift
- operators reporting:
- "he pulled them back too soon"
- "he let them wander too long"
- "felt off-topic"
- "felt like he lost the thread"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- drift-related confusion increases
- premature re-anchoring increases
- missed drift increases
- Organ 32 coherence state becomes unstable
- summarization organ accumulates irrelevant content
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around drift turns

#### Rollback Target

- `~0.30`

### 4.13 Clarification-Request Timing

#### Safe Range

- `140-320 ms`

#### Baseline

- `~220 ms`

#### Increment

- `+/-15-20 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived patience
- conversational intelligence
- trust
- ambiguity resolution
- flow stability
- clarification naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer ambiguity-detection logic
- Organ 33 clarification-intent rules
- summarization ambiguity-accumulation logic
- PCU-1.5 conversational-flow reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 140 ms`
- `> 320 ms`
- Any setting that causes:
- premature clarification
- delayed clarification
- patterned clarification timing
- tone or intent mismatch during clarification

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of clarification timing
- absence of interruption
- absence of lag
- stability across ambiguous phrasing, long sentences, multi-clause statements, and emotional turns
- operator judgment of intelligence
- merchant comfort
- alignment with DeepLayer ambiguity score
- alignment with Organ 33 clarification logic

This lever is judged on patience and intelligence, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan asking for clarification too early
- Alan waiting too long and causing confusion
- merchants repeating themselves
- merchants sounding frustrated or confused
- increased correction events
- emotional mismatch between tone and clarification timing
- operators reporting:
- "he cut them off"
- "he waited too long"
- "felt like he didn't understand"
- "felt robotic or scripted"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants repeat themselves more often
- premature clarification increases
- delayed clarification increases
- Organ 33 ambiguity logic becomes unstable
- summarization organ accumulates ambiguous content
- PCU-1.5 compensates excessively
- DeepLayer ambiguity profile diverges
- sprint/full fusion becomes unstable around ambiguous turns

#### Rollback Target

- `~220 ms`

### 4.14 Interruption-Recovery Latency

#### Safe Range

- `110-260 ms`

#### Baseline

- `~180 ms`

#### Increment

- `+/-10-20 ms`

#### Status

- Core substrate parameter
- Directly affects:
- perceived attentiveness
- turn-taking intelligence
- trust
- flow stability
- emotional congruence
- interruption recovery feel
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- VAD interruption-detection logic
- DeepLayer interruption-profile timing
- PCU-1.5 interruption-handling reflexes
- sprint/full concurrency logic
- signature-layer timing contours

#### Forbidden

- `< 110 ms`
- `> 260 ms`
- Any setting that causes:
- patterned recovery timing
- emotional mismatch
- abrupt or hesitant resumption
- delayed acknowledgment of interruption

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of recovery
- absence of talking-over
- absence of hesitation
- stability across partial interruptions, full interruptions, emotional interruptions, and rapid back-and-forth
- operator judgment of attentiveness
- merchant comfort
- alignment with DeepLayer interruption profile
- alignment with PCU-1.5 reflexes

This lever is judged on attentiveness and social intelligence, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan resuming too quickly
- Alan resuming too slowly
- merchants repeating themselves
- merchants sounding frustrated
- increased correction events
- emotional mismatch between tone and recovery timing
- operators reporting:
- "he talked over them"
- "he hesitated"
- "felt like he didn't notice the interruption"
- "felt robotic or delayed"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants repeat themselves more often
- premature or delayed recovery increases
- PCU-1.5 compensates excessively
- DeepLayer interruption profile diverges
- sprint/full fusion becomes unstable around interruptions
- VAD interruption-detection becomes misaligned

#### Rollback Target

- `~180 ms`

### 4.15 Turn-Handoff Silence

#### Safe Range

- `90-180 ms`

#### Baseline

- `~130 ms`

#### Increment

- `+/-10-15 ms`

#### Status

- Core substrate parameter
- Directly affects:
- turn-taking intelligence
- perceived confidence
- conversational flow
- emotional congruence
- trust
- floor-yield naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- VAD end-of-speech logic
- DeepLayer turn-boundary timing
- PCU-1.5 turn-yield reflexes
- signature-layer timing contours
- sprint/full concurrency logic

#### Forbidden

- `< 90 ms`
- `> 180 ms`
- Any setting that causes:
- patterned handoff timing
- emotional mismatch
- delayed floor-yield
- inconsistent turn boundaries

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of floor-yield
- absence of overlap
- absence of hesitation
- stability across objections, clarifications, emotional turns, long merchant sentences, and rapid back-and-forth
- operator judgment of flow
- merchant comfort
- alignment with DeepLayer turn-boundary profile
- alignment with PCU-1.5 reflexes

This lever is judged on cooperative timing, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- merchants talking at the same time as Alan
- merchants waiting because Alan seems hesitant
- Alan sounding abrupt or clipped
- Alan sounding unsure or slow to yield
- increased correction events
- emotional mismatch between tone and floor-yield timing
- operators reporting:
- "felt rushed"
- "felt hesitant"
- "timing felt off"
- "overlap happened"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- overlap frequency increases
- hesitation frequency increases
- PCU-1.5 compensates excessively
- DeepLayer turn-boundary profile diverges
- sprint/full fusion becomes unstable around turn boundaries
- VAD end-of-speech alignment drifts

#### Rollback Target

- `~130 ms`

### 4.16 Affirmation-Response Latency

#### Safe Range

- `120-260 ms`

#### Baseline

- `~180 ms`

#### Increment

- `+/-10-20 ms`

#### Status

- Core substrate parameter
- Directly affects:
- warmth
- confidence
- conversational momentum
- rapport formation
- perceived emotional intelligence
- post-affirmation flow
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer affirmation-detection logic
- Organ 30 emotional-frame mapping
- PCU-1.5 momentum-shaping reflex
- signature-layer prosody contours
- sprint/full concurrency logic

#### Forbidden

- `< 120 ms`
- `> 260 ms`
- Any setting that causes:
- emotional mismatch
- patterned affirmation timing
- abrupt acceleration
- delayed follow-through after positive signals

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of post-affirmation timing
- warmth without eagerness
- confidence without pressure
- momentum preservation
- stability across soft, strong, and conditional affirmations
- operator judgment of tone
- merchant comfort
- alignment with DeepLayer affirmation profile
- alignment with PCU-1.5 momentum reflex

This lever is judged on warmth and momentum, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan responding too quickly after a yes
- Alan responding too slowly and losing momentum
- merchants sounding pressured
- merchants sounding confused or waiting
- increased correction events
- emotional mismatch between tone and affirmation timing
- operators reporting:
- "felt pushy"
- "felt slow to pick up the yes"
- "timing felt scripted"
- "momentum died"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- merchants show discomfort after affirmations
- premature acceleration increases
- delayed follow-through increases
- PCU-1.5 compensates excessively
- DeepLayer affirmation profile diverges
- sprint/full fusion becomes unstable around positive turns

#### Rollback Target

- `~180 ms`

### 4.17 Context-Compression Onset

#### Safe Range

- `0.22-0.46`

#### Baseline

- `~0.34`

#### Increment

- `+/-0.02-0.04`

#### Status

- Core substrate parameter
- Directly affects:
- coherence
- memory feel
- naturalness
- trust
- long-turn stability
- objection-family clarity
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-continuum logic
- Organ 34 compression-mapping rules
- summarization frame-construction logic
- PCU-1.5 conversational-flow reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.22`
- `> 0.46`
- Any setting that causes:
- patterned compression timing
- abrupt frame shifts
- loss of nuance
- tone or intent mismatch during compression
- memory-feel inconsistencies

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- naturalness of compression onset
- absence of premature summarization
- absence of semantic overload
- stability across long explanations, multi-clause turns, emotional narratives, and embedded objections
- operator judgment of coherence
- merchant comfort
- alignment with DeepLayer semantic-continuum
- alignment with Organ 34 compression logic

This lever is judged on coherence and memory feel, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan summarizing too early
- Alan summarizing too late
- Alan losing details
- Alan sounding impatient or inattentive
- increased correction events
- increased drift or frame instability
- operators reporting:
- "he cut them off mentally"
- "he lost the thread"
- "he summarized too soon"
- "he didn't compress soon enough"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- premature compression increases
- delayed compression increases
- Organ 34 frame-construction becomes unstable
- summarization organ accumulates too much raw content
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around long turns

#### Rollback Target

- `~0.34`

### 4.18 Semantic-Frame Persistence

#### Safe Range

- `2.8-6.4 s`

#### Baseline

- `~4.2 s`

#### Increment

- `+/-0.3-0.5 s`

#### Status

- Core substrate parameter
- Directly affects:
- continuity
- memory feel
- coherence
- trust
- objection-family stability
- long-turn reasoning
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-continuum logic
- Organ 34 frame-construction rules
- summarization frame-refresh logic
- PCU-1.5 continuity reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 2.8 s`
- `> 6.4 s`
- Any setting that causes:
- patterned refresh timing
- abrupt frame resets
- loss of nuance
- continuity mismatches
- semantic drift due to stale frames

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- continuity across turns
- naturalness of frame refresh
- absence of premature resets
- absence of stale-context errors
- stability across long merchant narratives, multi-turn objections, evolving emotional states, and shifting merchant goals
- operator judgment of coherence
- merchant comfort
- alignment with DeepLayer semantic-continuum
- alignment with Organ 34 frame-persistence logic

This lever is judged on continuity and memory feel, not strictness.

#### Regression Conditions

A setting is regressive if you observe:

- Alan losing context too quickly
- Alan holding context too long
- outdated assumptions affecting new turns
- increased correction events
- frame instability
- operators reporting:
- "he forgot too soon"
- "he held onto the wrong thing"
- "felt like a reset"
- "felt stuck on the previous frame"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- premature frame expiration increases
- stale-context errors increase
- Organ 34 frame-refresh logic becomes unstable
- summarization organ misaligns with active frames
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around frame transitions

#### Rollback Target

- `~4.2 s`

### 4.19 Prosody-Intent Alignment Bias

#### Safe Range

- `0.28-0.62`

#### Baseline

- `~0.44`

#### Increment

- `+/-0.03-0.05`

#### Status

- Core substrate parameter
- Directly affects:
- emotional intelligence
- naturalness
- rapport formation
- trust
- tone-intent coherence
- objection-handling nuance
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer intent-inference logic
- Organ 30 emotional-frame mapping
- PCU-1.5 prosody-shaping reflexes
- signature-layer acoustic identity
- sprint/full concurrency logic

#### Forbidden

- `< 0.28`
- `> 0.62`
- Any setting that causes:
- patterned emotional responses
- exaggerated tone shifts
- delayed emotional alignment
- mismatched affect during objections or affirmations

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- tone-intent coherence
- naturalness of emotional alignment
- absence of exaggerated mirroring
- absence of emotional flatness
- stability across objections, affirmations, clarifications, long narratives, and emotional volatility
- operator judgment of emotional intelligence
- merchant comfort
- alignment with DeepLayer intent profile
- alignment with PCU-1.5 prosody reflex

This lever is judged on emotional intelligence and subtlety, not expressiveness.

#### Regression Conditions

A setting is regressive if you observe:

- Alan sounding too flat
- Alan sounding too theatrical
- emotional mismatch with merchant intent
- exaggerated prosody shifts
- delayed emotional alignment
- operators reporting:
- "tone didn't match the moment"
- "felt like he was imitating me"
- "felt too flat / too dramatic"
- "felt scripted or stylized"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- emotional mismatch increases
- over-mirroring increases
- Organ 30 emotional-frame mapping becomes unstable
- PCU-1.5 compensates excessively
- DeepLayer intent-profile divergence appears
- sprint/full fusion becomes unstable around emotional turns

#### Rollback Target

- `~0.44`

### 4.20 Semantic-Continuity Decay Rate

#### Safe Range

- `0.06-0.18/s`

#### Baseline

- `~0.11/s`

#### Increment

- `+/-0.01-0.02`

#### Status

- Core substrate parameter
- Directly affects:
- conversational fluidity
- memory feel
- continuity
- naturalness
- objection-family stability
- long-turn reasoning
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-continuum logic
- Organ 34 frame-persistence rules
- summarization decay-integration logic
- PCU-1.5 continuity reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.06`
- `> 0.18`
- Any setting that causes:
- patterned decay timing
- abrupt context loss
- semantic snapping
- mismatch between old and new frames
- emotional or intent drift from decay imbalance

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- smoothness of context blending
- absence of abrupt forgetting
- absence of stale-context errors
- stability across long narratives, multi-turn objections, evolving goals, and emotional shifts
- operator judgment of fluidity
- merchant comfort
- alignment with DeepLayer semantic-continuum
- alignment with Organ 34 decay-integration logic

This lever is judged on fluidity and human-grade continuity, not strict retention.

#### Regression Conditions

A setting is regressive if you observe:

- Alan holding onto old context too long
- Alan dropping context too quickly
- outdated assumptions affecting new turns
- continuity mismatches
- increased correction events
- operators reporting:
- "he forgot too fast"
- "he stayed stuck on the old thing"
- "felt rigid"
- "felt reactive"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- stale-context errors increase
- premature forgetting increases
- Organ 34 decay-integration becomes unstable
- summarization organ misaligns with active frames
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around continuity transitions

#### Rollback Target

- `~0.11/s`

### 4.21 Prosody-Aligned Emotional Damping Recovery

#### Safe Range

- `0.14-0.36/s`

#### Baseline

- `~0.22/s`

#### Increment

- `+/-0.02-0.04`

#### Status

- Core substrate parameter
- Directly affects:
- emotional congruence
- trust
- warmth
- recovery after objections
- perceived authenticity
- rapport stability
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- Organ 30 emotional-frame mapping
- PCU-1.5 emotional-timing reflexes
- signature-layer prosody contours
- DeepLayer affect-profile outputs
- sprint/full concurrency logic

#### Forbidden

- `< 0.14/s`
- `> 0.36/s`
- Any setting that causes:
- patterned recovery timing
- emotional whiplash
- inconsistent amplitude restoration
- tone or intent mismatch during recovery

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- smoothness of emotional recovery
- absence of snapback warmth
- absence of prolonged flatness
- stability across objections, clarifications, emotional volatility, and long narratives
- operator judgment of authenticity
- merchant comfort
- alignment with DeepLayer affect-profile
- alignment with PCU-1.5 emotional-timing reflex

This lever is judged on authenticity and emotional pacing, not expressiveness.

#### Regression Conditions

A setting is regressive if you observe:

- Alan staying flat too long
- Alan warming up too quickly
- emotional mismatch after friction
- increased correction events
- operators reporting:
- "he stayed muted"
- "he bounced back too fast"
- "felt scripted"
- "felt emotionally off"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- emotional snapback increases
- prolonged flatness increases
- Organ 30 emotional-frame mapping becomes unstable
- PCU-1.5 compensates excessively
- DeepLayer affect-profile diverges
- sprint/full fusion becomes unstable around emotional turns

#### Rollback Target

- `~0.22/s`

### 4.22 Merchant-Turn Context Carryover Depth

#### Safe Range

- `2.2-4.0` turns

#### Baseline

- `~3.1` turns

#### Increment

- `+/-0.2-0.3` turns

#### Status

- Core substrate parameter
- Directly affects:
- continuity
- memory feel
- naturalness
- objection-family stability
- multi-turn reasoning
- emotional coherence
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-continuum logic
- Organ 34 frame-persistence rules
- summarization turn-weighting logic
- PCU-1.5 continuity reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 2.2` turns
- `> 4.0` turns
- Any setting that causes:
- patterned carryover
- abrupt context drop
- semantic contamination from old turns
- mismatched emotional or intent interpretation

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- continuity across multi-turn exchanges
- naturalness of context retention
- absence of premature forgetting
- absence of stale-context errors
- stability across long narratives, multi-turn objections, evolving goals, and emotional shifts
- operator judgment of attentiveness
- merchant comfort
- alignment with DeepLayer semantic-continuum
- alignment with Organ 34 turn-weighting logic

This lever is judged on continuity and attentiveness, not strict retention.

#### Regression Conditions

A setting is regressive if you observe:

- Alan losing context too quickly
- Alan holding context too long
- outdated assumptions affecting new turns
- continuity mismatches
- increased correction events
- operators reporting:
- "he forgot what they said earlier"
- "he stayed stuck on the old turn"
- "felt rigid"
- "felt reactive"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- premature context loss increases
- stale-context errors increase
- Organ 34 turn-weighting becomes unstable
- summarization organ misaligns with active frames
- PCU-1.5 compensates excessively
- DeepLayer semantic-continuum diverges
- sprint/full fusion becomes unstable around multi-turn sequences

#### Rollback Target

- `~3.1` turns

### 4.23 Intent-Stability Smoothing

#### Safe Range

- `0.18-0.41`

#### Baseline

- `~0.29`

#### Increment

- `+/-0.02-0.03`

#### Status

- Core substrate parameter
- Directly affects:
- perceived intelligence
- emotional steadiness
- trust
- objection-handling nuance
- multi-turn coherence
- naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer intent-inference logic
- Organ 31 objection-family classification
- summarization intent-accumulation logic
- PCU-1.5 emotional-timing reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.18`
- `> 0.41`
- Any setting that causes:
- patterned intent shifts
- abrupt reclassification
- emotional mismatch
- instability during objections or clarifications

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- smoothness of intent transitions
- absence of abrupt shifts
- absence of rigidity
- stability across objections, clarifications, emotional turns, and evolving merchant goals
- operator judgment of steadiness
- merchant comfort
- alignment with DeepLayer intent profile
- alignment with Organ 31 classification

This lever is judged on steadiness and emotional intelligence, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan sticking to outdated intent
- Alan flipping intent too quickly
- emotional mismatch
- increased correction events
- operators reporting:
- "he didn't adjust fast enough"
- "he reacted too fast"
- "felt unstable"
- "felt rigid"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- rigidity increases
- over-reactivity increases
- Organ 31 misclassifies intent under pressure
- summarization organ misaligns with active intent
- PCU-1.5 compensates excessively
- DeepLayer intent-profile diverges
- sprint/full fusion becomes unstable around intent transitions

#### Rollback Target

- `~0.29`

### 4.24 Merchant-Intent Volatility Damping

#### Safe Range

- `0.22-0.55`

#### Baseline

- `~0.37`

#### Increment

- `+/-0.03-0.05`

#### Status

- Core substrate parameter
- Directly affects:
- emotional steadiness
- perceived intelligence
- trust
- objection-handling nuance
- multi-turn coherence
- noise-resilience
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer intent-inference logic
- Organ 31 objection-family mapping
- summarization intent-trajectory logic
- PCU-1.5 emotional-timing reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.22`
- `> 0.55`
- Any setting that causes:
- patterned damping
- delayed recognition of genuine intent changes
- emotional mismatch
- instability during objections or clarifications

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- steadiness of intent trajectory
- absence of jittery reactivity
- absence of stubbornness
- stability across ambiguous phrasing, emotional volatility, rapid back-and-forth, and multi-turn objections
- operator judgment of stability
- merchant comfort
- alignment with DeepLayer intent profile
- alignment with Organ 31 volatility-handling logic

This lever is judged on stability and noise-resilience, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan reacting to noise
- Alan ignoring real shifts
- emotional mismatch
- increased correction events
- operators reporting:
- "he jumped at nothing"
- "he didn't adjust when the merchant actually shifted"
- "felt unstable"
- "felt stubborn"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- noise-reactivity increases
- rigidity increases
- Organ 31 misclassifies intent under volatility
- summarization organ misaligns with active intent
- PCU-1.5 compensates excessively
- DeepLayer intent-profile diverges
- sprint/full fusion becomes unstable around volatile turns

#### Rollback Target

- `~0.37`

### 4.25 Semantic-Confidence Weighting

#### Safe Range

- `0.42-0.78`

#### Baseline

- `~0.61`

#### Increment

- `+/-0.03-0.05`

#### Status

- Core substrate parameter
- Directly affects:
- clarity
- ambiguity resolution
- naturalness
- trust
- objection-family stability
- multi-turn reasoning
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer semantic-confidence scoring
- Organ 32 coherence-tracking logic
- summarization confidence-integration rules
- PCU-1.5 ambiguity-handling reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.42`
- `> 0.78`
- Any setting that causes:
- patterned confidence weighting
- abrupt shifts between interpretations
- semantic tunnel vision
- emotional or intent mismatch under ambiguity

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- clarity under ambiguity
- naturalness of interpretation
- absence of over-certainty
- absence of indecision
- stability across ambiguous phrasing, multi-clause turns, emotional volatility, and evolving goals
- operator judgment of intelligence
- merchant comfort
- alignment with DeepLayer semantic-confidence profile
- alignment with Organ 32 coherence logic

This lever is judged on clarity and balanced interpretation, not assertiveness.

#### Regression Conditions

A setting is regressive if you observe:

- Alan sounding too certain
- Alan sounding too hesitant
- misinterpretation of ambiguous turns
- increased correction events
- operators reporting:
- "he jumped to the wrong meaning"
- "he didn't commit to an interpretation"
- "felt rigid"
- "felt indecisive"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- over-certainty increases
- indecision increases
- Organ 32 coherence state becomes unstable
- summarization organ misaligns with confidence scores
- PCU-1.5 compensates excessively
- DeepLayer semantic-confidence profile diverges
- sprint/full fusion becomes unstable around ambiguous turns

#### Rollback Target

- `~0.61`

### 4.26 Intent-Trajectory Inertia

#### Safe Range

- `0.26-0.58`

This is the human-plausible band where:

- historical intent trajectory meaningfully influences the next state
- but does not overpower new evidence
- continuity feels stable
- emotional and cognitive shifts feel natural

#### Below Safe Range

- inertia too weak
- Alan feels reactive or jumpy
- intent shifts too easily
- long-arc coherence breaks

#### Above Safe Range

- inertia too strong
- Alan feels stubborn or slow to adapt
- outdated intent trajectory dominates
- emotional mismatch under evolving goals

#### Baseline

- `~0.41`

This is the runtime-observed inertia factor applied by DeepLayer + Organ 31 to blend historical intent trajectory with new intent evidence.

#### Status

- Core substrate parameter
- Directly affects:
- long-turn coherence
- emotional stability
- trust
- objection-handling nuance
- continuity across evolving goals
- naturalness
- Must remain governed + field-evaluated

#### Governance

- Adjustments must be:
- incremental (`+/-0.03-0.05` per test window)
- reversible
- evaluated only in controlled exposure
- Forbidden to modify:
- DeepLayer intent-trajectory modeling
- Organ 31 trajectory-integration logic
- summarization organ's intent-history weighting
- PCU-1.5 emotional-timing reflexes
- sprint/full concurrency logic

#### Forbidden

- `< 0.26`
- jumpy intent updates
- reactive or jittery behavior
- loss of long-arc coherence
- `> 0.58`
- stubbornness
- slow adaptation
- outdated intent trajectory dominating new evidence
- Any setting that causes:
- patterned trajectory behavior
- abrupt trajectory resets
- emotional or intent mismatch
- instability during objections or evolving goals

#### Field Evaluation Method

A/B windows of `10-20` calls per setting.

Evaluate:

- smoothness of intent evolution
- absence of jumpiness
- absence of stubbornness
- stability across:
- multi-turn objections
- evolving merchant goals
- emotional volatility
- ambiguous phrasing
- operator judgment of coherence
- merchant comfort
- alignment with DeepLayer trajectory profile
- alignment with Organ 31 trajectory-integration logic

This lever is judged on long-arc coherence and emotional stability, not speed.

#### Regression Conditions

A setting is regressive if you observe:

- Alan shifting intent too quickly
- Alan holding onto old intent too long
- emotional mismatch
- increased correction events
- operators reporting:
- "he jumped too fast"
- "he stayed stuck on the old intent"
- "felt unstable"
- "felt stubborn"

#### Rollback Trigger

Rollback immediately if:

- two or more strong qualitative complaints
- jumpiness increases
- stubbornness increases
- Organ 31 trajectory-integration becomes unstable
- summarization organ misaligns with trajectory history
- PCU-1.5 compensates excessively
- DeepLayer trajectory profile diverges
- sprint/full fusion becomes unstable around evolving intent

#### Rollback Target

- `~0.41`

### 4.27 Semantic-Frame Conflict Resolution Threshold

#### Safe Range

- `0.18-0.42`

#### Below Safe Range

- Alan resolves semantic-frame conflicts too quickly, leading to:
- premature commitment to a single interpretation
- loss of ambiguity tolerance
- brittle or over-confident responses
- reduced ability to hold competing merchant intents
- increased risk of misclassification during objections

#### Above Safe Range

- Alan delays conflict resolution too long, leading to:
- hesitation or indecision
- overly cautious phrasing
- conversational drag
- semantic wobble where multiple frames remain active
- increased latency in intent-aligned responses

#### Baseline

- `0.29`

#### Status

- Core semantic-stability organ
- Governs how Alan resolves competing meaning-frames during:
- ambiguous merchant turns
- multi-intent statements
- emotionally charged objections
- rapid-fire exchanges
- Directly affects:
- coherence
- confidence modulation
- emotional congruence
- objection-family stability
- naturalness under uncertainty

#### Governance

- Resolution must:
- preserve ambiguity until sufficient evidence accumulates
- avoid premature collapse into a single frame
- avoid over-extension of unresolved frames
- maintain emotional congruence with merchant tone
- remain reversible until the next turn boundary
- Must not override:
- prosody-intent alignment
- semantic-confidence weighting
- context-carryover depth
- volatility damping

#### Forbidden

- snapping to a frame based on prosody alone
- maintaining conflicting frames past two merchant turns
- overriding explicit merchant clarification
- using emotional tone as the sole determinant of resolution
- collapsing frames during objection escalation

#### Field Evaluation Method

- Observe `5-7` ambiguous merchant turns
- Track:
- time-to-resolution
- stability of chosen frame
- reversals after resolution
- emotional congruence
- objection-family alignment
- Evaluate whether Alan:
- resolves too early
- resolves too late
- oscillates
- or maintains stable, human-like ambiguity

#### Regression Conditions

- increased misinterpretation during objections
- noticeable hesitation in neutral turns
- over-confident early commitments
- repeated frame reversals within a single merchant turn
- emotional mismatch during conflict resolution

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature frame collapse
- or delayed resolution causing conversational drag

#### Rollback Target

- `0.26`

### 4.28 Semantic-Frame Conflict Resolution Inertia

#### Safe Range

- `0.12-0.31`

#### Below Safe Range

- Alan releases resolved semantic frames too quickly, leading to:
- premature reconsideration of stable interpretations
- oscillation between frames
- increased semantic jitter
- reduced conversational confidence
- vulnerability to noise-induced reinterpretation

#### Above Safe Range

- Alan holds resolved frames too long, leading to:
- rigidity in interpretation
- resistance to new evidence
- delayed adaptation to merchant clarifications
- emotional mismatch during evolving objections
- semantic anchoring that feels unnatural

#### Baseline

- `0.21`

#### Status

- Core temporal-stability organ
- Governs how long a resolved semantic frame remains active before reconsideration is allowed
- Directly affects:
- coherence
- adaptability
- objection-family transitions
- emotional congruence
- naturalness under evolving context
- Works in tandem with:
- 4.25 Semantic-Confidence Weighting
- 4.27 Conflict Resolution Threshold

#### Governance

- Inertia must:
- preserve stability long enough for natural conversational flow
- allow reconsideration when new evidence appears
- avoid oscillation between frames
- avoid rigidity that blocks reinterpretation
- remain reversible until the next merchant-turn boundary
- Must not override:
- prosody-intent alignment
- volatility damping
- context-carryover depth

#### Forbidden

- reconsidering frames within the same merchant turn
- maintaining a resolved frame after explicit merchant correction
- using emotional tone alone to extend inertia
- collapsing reconsideration windows during objections
- holding frames across turn boundaries when evidence contradicts them

#### Field Evaluation Method

- Observe `5-10` turns involving:
- ambiguous phrasing
- evolving merchant intent
- objection escalation
- Track:
- time-to-reconsideration
- stability of resolved frames
- reversals after new evidence
- emotional congruence during shifts
- Evaluate whether Alan:
- reconsiders too early
- reconsiders too late
- oscillates
- or maintains human-like temporal stability

#### Regression Conditions

- increased frame reversals without new evidence
- noticeable rigidity during clarifications
- over-attachment to early interpretations
- emotional mismatch during evolving objections
- latency spikes caused by hesitation to reconsider

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature frame release
- or excessive rigidity preventing reinterpretation

#### Rollback Target

- `0.18`

### 4.29 Semantic-Frame Reinterpretation Latency

#### Safe Range

- `0.14-0.33`

#### Below Safe Range

- Alan reinterprets semantic frames too quickly, leading to:
- premature abandonment of valid interpretations
- excessive sensitivity to minor evidence
- conversational instability
- emotional inconsistency
- increased risk of misalignment during objections

#### Above Safe Range

- Alan delays reinterpretation too long, leading to:
- rigidity in meaning
- slow adaptation to clarifications
- outdated frame persistence
- reduced responsiveness to evolving merchant intent
- unnatural conversational inertia

#### Baseline

- `0.22`

#### Status

- Core temporal-adaptation organ
- Governs the minimum latency before Alan may reinterpret a previously resolved semantic frame
- Directly affects:
- adaptability
- coherence
- emotional congruence
- objection-family transitions
- naturalness under evolving context
- Works in tandem with:
- 4.27 Conflict Resolution Threshold
- 4.28 Conflict Resolution Inertia

#### Governance

- Reinterpretation latency must:
- allow sufficient time for stable interpretation
- avoid premature reinterpretation
- avoid rigidity that blocks adaptation
- remain sensitive to explicit merchant corrections
- maintain emotional continuity across turns
- Must not override:
- prosody-intent alignment
- semantic-confidence weighting
- volatility damping
- context-carryover depth

#### Forbidden

- reinterpreting within the same merchant turn
- ignoring explicit merchant clarification
- using emotional tone alone to trigger reinterpretation
- holding outdated frames after contradictory evidence
- oscillating between interpretations without new input

#### Field Evaluation Method

- Observe `5-10` turns involving:
- evolving merchant intent
- clarifications
- objection escalation
- Track:
- time-to-reinterpretation
- stability of updated frames
- reversals after new evidence
- emotional congruence during shifts
- Evaluate whether Alan:
- reinterprets too early
- reinterprets too late
- oscillates
- or maintains human-like adaptation timing

#### Regression Conditions

- increased reinterpretation without evidence
- noticeable rigidity during clarifications
- emotional mismatch during evolving objections
- latency spikes caused by hesitation
- frame reversals within a single merchant turn

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature reinterpretation
- or excessive rigidity preventing reinterpretation

#### Rollback Target

- `0.19`

### 4.30 Semantic-Frame Reinterpretation Cooldown

#### Safe Range

- `0.11-0.26`

#### Below Safe Range

- Alan reinterprets again too quickly after a reinterpretation event, leading to:
- rapid-fire reinterpretation loops
- semantic thrashing
- emotional instability
- loss of conversational continuity
- increased misalignment during objections

#### Above Safe Range

- Alan waits too long before allowing another reinterpretation, leading to:
- rigidity after corrections
- outdated frame persistence
- slow adaptation to evolving merchant intent
- unnatural hesitation
- reduced responsiveness during clarifications

#### Baseline

- `0.18`

#### Status

- Final organ in the semantic-frame reinterpretation chain
- Governs the minimum cooldown period after a reinterpretation event
- Ensures:
- stability
- emotional continuity
- natural pacing
- protection against oscillation
- Works in tandem with:
- 4.28 Conflict Resolution Inertia
- 4.29 Reinterpretation Latency

#### Governance

- Cooldown must:
- prevent immediate back-to-back reinterpretations
- preserve conversational stability
- allow adaptation when new evidence appears
- avoid rigidity that blocks necessary updates
- maintain emotional congruence across turns
- Must not override:
- explicit merchant corrections
- prosody-intent alignment
- semantic-confidence weighting
- context-carryover depth

#### Forbidden

- triggering reinterpretation twice within the same merchant turn
- ignoring explicit corrections due to cooldown
- using emotional tone alone to shorten cooldown
- holding outdated frames after contradictory evidence
- collapsing cooldown during objection escalation

#### Field Evaluation Method

- Observe `5-10` turns involving:
- reinterpretation events
- clarifications
- evolving merchant intent
- Track:
- time-between-reinterpretations
- stability after reinterpretation
- reversals without new evidence
- emotional congruence during shifts
- Evaluate whether Alan:
- reinterprets too soon
- reinterprets too late
- oscillates
- or maintains human-like cooldown pacing

#### Regression Conditions

- increased reinterpretation loops
- noticeable rigidity after corrections
- emotional mismatch during evolving objections
- latency spikes caused by hesitation
- frame reversals within a single merchant turn

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature reinterpretation
- or excessive cooldown rigidity

#### Rollback Target

- `0.15`

### 4.31 Context-Compression Stability Window

#### Safe Range

- `0.24-0.47`

#### Below Safe Range

- Alan destabilizes compressed context too quickly, leading to:
- premature re-expansion
- loss of compression benefits
- increased cognitive load
- jitter in semantic continuity
- reduced efficiency during long merchant narratives

#### Above Safe Range

- Alan holds compressed context too long, leading to:
- outdated compression persisting past relevance
- resistance to new contextual evidence
- semantic rigidity
- emotional mismatch during evolving turns
- delayed adaptation to clarifications

#### Baseline

- `0.33`

#### Status

- First organ in the context-compression stability family
- Governs the minimum stability window after context is compressed
- Ensures:
- stable compressed representations
- natural pacing of re-expansion
- protection against premature reinterpretation
- efficient long-turn reasoning
- Works in tandem with:
- 4.17 Context-Compression Onset
- 4.32 Context-Compression Re-Expansion Threshold
- 4.33 Context-Compression Drift Correction

#### Governance

- Stability window must:
- preserve compressed context long enough for coherent reasoning
- avoid premature re-expansion
- avoid rigidity that blocks adaptation
- remain sensitive to explicit merchant corrections
- maintain emotional continuity across turns
- Must not override:
- prosody-intent alignment
- semantic-confidence weighting
- volatility damping
- turn-handoff timing

#### Forbidden

- re-expanding compressed context within the same merchant turn
- holding compressed context after explicit contradictory evidence
- using emotional tone alone to extend stability
- collapsing stability during objection escalation
- allowing compressed context to drift without correction

#### Field Evaluation Method

- Observe `5-10` turns involving:
- long merchant narratives
- evolving context
- clarifications
- objection transitions
- Track:
- stability duration
- timing of re-expansion
- reversals after new evidence
- emotional congruence during shifts
- Evaluate whether Alan:
- re-expands too early
- re-expands too late
- oscillates
- or maintains human-like compression stability

#### Regression Conditions

- increased premature re-expansion
- noticeable rigidity during clarifications
- emotional mismatch during evolving context
- latency spikes caused by hesitation
- drift in compressed context without correction

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature re-expansion
- or excessive stability preventing adaptation

#### Rollback Target

- `0.29`

### 4.32 Context-Compression Re-Expansion Threshold

#### Safe Range

- `0.28-0.52`

#### Below Safe Range

- Alan re-expands compressed context too early, leading to:
- premature loss of compression efficiency
- unnecessary cognitive load
- jitter in semantic continuity
- unstable long-turn reasoning
- increased risk of misinterpreting evolving merchant intent

#### Above Safe Range

- Alan delays re-expansion too long, leading to:
- outdated compressed representations
- resistance to new contextual evidence
- semantic rigidity
- emotional mismatch during clarifications
- delayed adaptation during objection transitions

#### Baseline

- `0.37`

#### Status

- Second organ in the context-compression stability family
- Governs the minimum threshold required before compressed context may re-expand
- Ensures:
- stable, intentional re-expansion
- protection against premature reinterpretation
- natural pacing during long merchant narratives
- efficient context management
- Works in tandem with:
- 4.17 Context-Compression Onset
- 4.31 Context-Compression Stability Window
- 4.33 Context-Compression Drift Correction

#### Governance

- Re-expansion threshold must:
- prevent premature expansion
- avoid rigidity that blocks necessary updates
- remain sensitive to explicit merchant corrections
- maintain emotional continuity across turns
- preserve semantic fidelity during long-turn reasoning
- Must not override:
- prosody-intent alignment
- semantic-confidence weighting
- volatility damping
- turn-handoff timing

#### Forbidden

- re-expanding compressed context within the same merchant turn
- holding compressed context after explicit contradictory evidence
- using emotional tone alone to trigger re-expansion
- collapsing threshold during objection escalation
- allowing re-expansion without meeting stability requirements

#### Field Evaluation Method

- Observe `5-10` turns involving:
- long merchant narratives
- evolving context
- clarifications
- objection transitions
- Track:
- timing of re-expansion
- stability after re-expansion
- reversals after new evidence
- emotional congruence during shifts
- Evaluate whether Alan:
- re-expands too early
- re-expands too late
- oscillates
- or maintains human-like re-expansion timing

#### Regression Conditions

- increased premature re-expansion
- noticeable rigidity during clarifications
- emotional mismatch during evolving context
- latency spikes caused by hesitation
- drift in compressed context without correction

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature re-expansion
- or excessive threshold rigidity

#### Rollback Target

- `0.33`

### 4.33 Context-Compression Drift Correction

#### Safe Range

- `0.19-0.41`

#### Below Safe Range

- Alan corrects drift too aggressively, leading to:
- over-correction of minor deviations
- unnecessary re-expansion cycles
- jitter in compressed representations
- instability during long merchant narratives
- premature reinterpretation of stable context

#### Above Safe Range

- Alan corrects drift too slowly, leading to:
- accumulated semantic distortion
- outdated compressed frames
- emotional mismatch during evolving turns
- reduced fidelity during long-turn reasoning
- increased risk of misalignment during objections

#### Baseline

- `0.27`

#### Status

- Final organ in the context-compression subsystem
- Governs the correction of drift within compressed context
- Ensures:
- stable compressed representations
- protection against semantic distortion
- natural pacing of drift correction
- high-fidelity long-turn reasoning
- Works in tandem with:
- 4.17 Context-Compression Onset
- 4.31 Context-Compression Stability Window
- 4.32 Context-Compression Re-Expansion Threshold

#### Governance

- Drift correction must:
- prevent semantic distortion during long-turn compression
- avoid over-correction that destabilizes context
- remain sensitive to explicit merchant corrections
- maintain emotional continuity across turns
- preserve semantic fidelity during evolving narratives
- Must not override:
- prosody-intent alignment
- semantic-confidence weighting
- volatility damping
- turn-handoff timing

#### Forbidden

- correcting drift within the same merchant turn unless explicitly required
- allowing drift to accumulate past the stability window
- using emotional tone alone to trigger drift correction
- collapsing drift correction during objection escalation
- re-expanding context solely to correct minor drift

#### Field Evaluation Method

- Observe `5-10` turns involving:
- long merchant narratives
- evolving context
- clarifications
- objection transitions
- Track:
- drift accumulation
- timing of correction
- stability after correction
- emotional congruence during shifts
- Evaluate whether Alan:
- corrects drift too early
- corrects drift too late
- oscillates
- or maintains human-like drift-correction timing

#### Regression Conditions

- increased semantic distortion during long-turn compression
- noticeable rigidity during clarifications
- emotional mismatch during evolving context
- latency spikes caused by hesitation
- drift persisting across multiple turns

#### Rollback Trigger

- three consecutive field evaluations showing:
- premature drift correction
- or excessive drift accumulation

#### Rollback Target

- `0.24`

---

## 5. Rollback Law

### 5.0 Rollback Law Overview

#### Purpose

- Define the constitutional mechanism for recovering from:
- regression
- instability
- drift
- misalignment
- envelope failure
- Ensure the system can return to a last known good without:
- cascading errors
- compounding drift
- destabilizing the behavioral layer

Rollback Law is the safety net of the entire Phase 5 tuning process.

#### Scope

- Applies to:
- all governed envelopes
- all Phase 5 tuning operations
- all stability windows
- all field-evaluation cycles
- all threshold adjustments
- Does not apply to:
- ungoverned experimental settings
- non-Phase-5 exploratory tuning
- operator-forced overrides

#### Constitutional Role

Rollback Law ensures:

- the system never drifts beyond recoverable bounds
- regression is detected early
- correction is decisive
- recovery is stable
- lineage remains intact
- the RRG remains the single source of truth

Rollback is not a punishment, it is a governed return to safety.

#### Rollback Definition

A rollback is the governed reversion from a failed or unstable setting back to the last known good configuration.

Rollback always includes:

- reversion
- disallowance of the failed setting
- logging of the regression window
- stabilization
- verification

#### Rollback Philosophy

Rollback must be:

- fast (no hesitation)
- decisive (no partial reversions)
- governed (no ad-hoc corrections)
- documented (RRG updated immediately)
- stable (post-rollback window enforced)

Rollback is the system's immune response to drift.

#### Interaction With Other Systems

Rollback Law interacts with:

- Context-Compression Subsystem (Section 4)
- rollback is triggered when compression thresholds fail
- Field Evaluation Law (Section 6)
- rollback is validated through A/B windows
- Stability Protocols (Section 7)
- rollback outcomes feed into long-turn verification

Rollback is the bridge between failure detection and system recovery.

#### Forbidden

- partial rollback
- silent rollback (no RRG update)
- rollback without logging
- rollback without stabilization
- rollback triggered by emotional tone alone
- rollback during operator override unless explicitly authorized

#### Status

- Anchor organ of Section 5
- Governs all rollback behavior
- Precedes:
- 5.1 Rollback Trigger Conditions
- 5.2 Rollback Target Calculation
- 5.3 Rollback Execution Protocol
- 5.4 Post-Rollback Stabilization Window
- 5.5 Regression Logging & Verification

### 5.1 Rollback Trigger Conditions

#### Purpose

- Define the governed conditions under which rollback must occur
- Ensure rollback is:
- consistent
- predictable
- neg-proofed
- lineage-safe
- Prevent hesitation, partial rollback, or subjective interpretation

Rollback triggers are binary.

If a trigger fires, rollback is mandatory.

#### Trigger Categories

Rollback may be triggered by any of the following categories:

1. Qualitative Instability
2. Quantitative Regression
3. Behavioral Drift
4. Envelope Failure
5. Operator-Detected Misalignment

Each category contains governed, measurable conditions.

#### 1. Qualitative Instability

Rollback is required when:

- merchants express strong discomfort
- conversational flow becomes noticeably unnatural
- emotional tone diverges from expected human patterns
- interruptions increase beyond baseline
- operator judgment identifies instability that cannot be corrected mid-window

Qualitative instability is treated as first-class rollback evidence.

#### 2. Quantitative Regression

Rollback is required when:

- regression persists across a governed evaluation window
- performance drops below the current baseline
- stability metrics degrade across `10+` calls
- timing, latency, or pause-pattern drift exceeds safe-range thresholds

Quantitative regression must be logged and neg-proofed.

#### 3. Behavioral Drift

Rollback is required when:

- pause timing becomes inconsistent
- predictive intent timing becomes unstable
- context-compression behavior deviates from Section 4 thresholds
- AI-tell patterns emerge
- PCU-1.5 begins compensating excessively
- prosody engine overrides timing too often

Behavioral drift is treated as a high-risk rollback trigger.

#### 4. Envelope Failure

Rollback is required when:

- a governed envelope fails neg-proof
- a parameter violates its safe range
- a stability window collapses
- a threshold produces cascading errors
- any envelope produces contradictory behavior

Envelope failure is the strongest rollback trigger.

#### 5. Operator-Detected Misalignment

Rollback is required when:

- the operator identifies misalignment that cannot be corrected in-window
- the system's behavior diverges from expected human-grade patterns
- the operator detects drift not yet visible in metrics

Operator judgment is a governed rollback authority.

#### Current Constitutional Baseline (Seed Triggers)

- Rollback immediately on either of these:

1. Two or more strong qualitative complaints in a test window
2. Sustained regression against baseline across `10+` calls

These remain valid and are now formally part of the governed trigger set.

#### Preserved Seed Rollback Action

General rollback action:

- revert to last known good
- mark failed setting as disallowed during current Phase 5
- log the failed window and regression markers

#### Status

- Fully governed organ
- Defines all rollback triggers
- Precedes:
- 5.2 Rollback Target Calculation
- 5.3 Rollback Execution Protocol
- 5.4 Post-Rollback Stabilization Window
- 5.5 Regression Logging & Verification
- Seed rollback-action block remains preserved under 5.1 or moved to 5.3 as needed

### 5.2 Rollback Target Calculation

#### Purpose

- Define how rollback targets are computed after a regression or instability event
- Ensure rollback is:
- precise
- proportional
- neg-proofed
- lineage-safe
- Prevent:
- excessive reversion
- insufficient correction
- oscillation between settings

Rollback targets must always be deterministic and documented.

#### Rollback Target Definition

A rollback target is the exact last known good configuration to which the system must return after a governed rollback trigger fires.

This includes:

- parameter values
- envelope thresholds
- timing windows
- stability metrics
- compression behavior
- prosody and pause-timing posture

Rollback targets must be real, not inferred.

#### Calculation Method

Rollback targets are determined by:

1. Identifying the last stable window
- A/B window of `10-20` calls
- no qualitative instability
- no quantitative regression
- no behavioral drift
- no envelope failure

2. Extracting the stable configuration
- parameter values
- safe-range posture
- timing behavior
- compression thresholds
- prosody alignment

3. Neg-proofing the target
- verify no hidden drift
- verify no contradictory behavior
- verify no instability masked by operator correction

4. Locking the target into the RRG
- update lineage
- mark failed setting as disallowed
- record regression markers

Rollback targets must be logged immediately.

#### Safe-Range Correction Logic

Rollback must:

- return to the baseline if drift is mild
- return to baseline minus correction offset if drift is moderate
- return to the last known good if drift is severe
- never exceed the safe-range minimum or maximum

Rollback must never:

- overshoot the safe range
- revert past the last known good
- introduce new instability

#### Over-Correction Prevention

Rollback must avoid:

- reverting multiple envelopes unnecessarily
- collapsing unrelated parameters
- resetting stable subsystems
- cascading rollbacks

Rollback is surgical, not global.

#### Under-Correction Prevention

Rollback must avoid:

- reverting only part of a failed configuration
- leaving drift uncorrected
- preserving unstable timing patterns
- retaining unsafe compression thresholds

Rollback must be complete, not partial.

#### Forbidden

- guessing rollback targets
- using emotional tone alone to determine rollback depth
- reverting beyond the last known good
- silent rollback (no RRG update)
- rollback without neg-proof
- rollback without stability verification

#### Status

- Fully governed organ
- Defines how rollback targets are computed
- Precedes:
- 5.3 Rollback Execution Protocol
- 5.4 Post-Rollback Stabilization Window
- 5.5 Regression Logging & Verification

### 5.3 Rollback Execution Protocol

#### Purpose

- Define the governed sequence for executing rollback
- Ensure rollback is:
- consistent
- complete
- safe
- neg-proofed
- lineage-aligned
- Prevent:
- partial rollback
- silent rollback
- cascading rollback
- operator-dependent improvisation

Rollback execution must always follow a strict, deterministic order.

#### Rollback Execution Sequence

Rollback must be executed in the following governed order:

1. Halt the Active Window
- stop the current evaluation window immediately
- freeze the unstable configuration
- prevent further drift or compounding regression

Rollback cannot occur while the system is still running unstable behavior.

2. Identify the Rollback Target
- retrieve the last known good configuration
- verify it matches the RRG lineage
- confirm it passed:
- stability
- regression
- qualitative
- behavioral
- envelope evaluations

The rollback target must be real, not inferred.

3. Revert to the Rollback Target

Rollback must revert:

- parameter values
- envelope thresholds
- timing windows
- compression posture
- prosody and pause-timing behavior
- any dependent subsystems affected by the failed setting

Reversion must be atomic, all at once, not piecemeal.

4. Mark the Failed Setting as Disallowed
- the failed configuration is forbidden for the remainder of Phase 5
- the disallowance must be logged in the RRG
- the system must not re-enter the failed posture without explicit operator authorization

This prevents oscillation and repeated regression.

5. Log the Regression Window

Rollback must log:

- the failed window
- the regression markers
- the trigger category
- the failure mode
- the envelope that collapsed
- the operator notes (if any)

Logging must occur before stabilization.

6. Initiate the Post-Rollback Stabilization Window
- begin a governed stabilization window
- enforce safe-range posture
- monitor for residual drift
- verify timing, compression, and prosody stability
- confirm no re-emergence of the failure mode

This window is mandatory and precedes any further tuning.

7. Update the RRG

Rollback is not complete until:

- lineage is updated
- the rollback target is recorded
- the failed setting is marked disallowed
- the stabilization window is logged

Silent rollback is forbidden.

#### Rollback Integrity Rules

Rollback must:

- be executed immediately when triggered
- be complete, not partial
- be documented in the RRG
- be neg-proofed
- be stable before tuning resumes

Rollback must never:

- revert only part of a configuration
- skip the stabilization window
- proceed without logging
- occur without operator visibility
- introduce new instability

#### Forbidden

- partial rollback
- silent rollback
- rollback without RRG update
- rollback without stabilization
- rollback based solely on emotional tone
- rollback that reverts beyond the last known good
- rollback that collapses unrelated envelopes

#### Status

- Fully governed organ
- Defines the mandatory rollback execution sequence
- Precedes:
- 5.4 Post-Rollback Stabilization Window
- 5.5 Regression Logging & Verification

### 5.4 Post-Rollback Stabilization Window

#### Purpose

- Define the mandatory stabilization period after rollback
- Ensure the system re-enters a stable, predictable, human-grade posture
- Prevent:
- residual drift
- oscillation
- premature tuning
- re-emergence of the failure mode
- Confirm that the rollback target is safe, aligned, and neg-proofed before tuning resumes

The stabilization window is non-optional.

#### Stabilization Window Definition

A post-rollback stabilization window is the governed recovery period immediately after rollback during which tuning is prohibited and system stability must be re-proven.

The window must be:

- isolated
- monitored
- documented
- lineage-aligned

No tuning may occur during this window.

#### Stabilization Requirements

During the stabilization window, the system must demonstrate:

1. Timing Stability
- consistent pause timing
- no AI-tell patterns
- no prosody overrides
- no predictive-intent drift

2. Compression Stability
- context-compression behavior matches Section 4 thresholds
- no frame-drift
- no reinterpretation latency anomalies

3. Behavioral Stability
- natural conversational flow
- no merchant discomfort
- no operator-detected misalignment
- no reflex-arc instability

4. Metric Stability
- no regression markers
- no oscillation
- no compensation from PCU-1.5
- no envelope-level contradictions

All four stability domains must pass.

#### Stabilization Window Length

The stabilization window must last:

- `10-20` calls minimum
- longer if:
- drift was severe
- the failure mode was behavioral
- the rollback target required multi-parameter reversion

The operator may extend the window at discretion.

#### Monitoring Requirements

During the stabilization window, the system must:

- monitor timing, compression, and behavioral metrics
- log any micro-drift
- verify no re-emergence of the failure mode
- confirm the rollback target remains stable under natural conversation
- ensure no hidden instability is masked by operator correction

Monitoring must be continuous.

#### Completion Criteria

The stabilization window is complete only when:

- all stability domains pass
- no drift is detected
- no regression markers appear
- no qualitative instability emerges
- the operator confirms stability
- the RRG is updated with stabilization results

If any criterion fails, rollback must be re-evaluated.

#### Forbidden

- resuming tuning before stabilization completes
- partial stabilization
- silent stabilization (no RRG update)
- ignoring micro-drift
- allowing envelope changes during stabilization
- treating stabilization as optional

#### Status

- Fully governed organ
- Defines the mandatory stabilization period after rollback
- Precedes:
- 5.5 Regression Logging & Verification

### 5.5 Regression Logging & Verification

#### Purpose

- Define the governed process for logging regression and verifying rollback outcomes
- Ensure all rollback events are:
- documented
- traceable
- neg-proofed
- lineage-aligned
- Prevent:
- silent regression
- incomplete rollback
- unverified stabilization
- lineage gaps

Regression logging is the audit trail of Section 5.

#### Regression Logging Requirements

Every rollback event must generate a regression log containing:

1. Trigger Information
- trigger category (qualitative, quantitative, behavioral, envelope, operator-detected)
- specific failure mode
- window in which the failure occurred
- operator notes (if any)

2. Regression Markers
- timing drift
- compression anomalies
- prosody overrides
- AI-tell patterns
- stability-metric degradation
- PCU-1.5 compensation events

Markers must be explicit, not inferred.

3. Failed Configuration Snapshot
- parameter values
- envelope thresholds
- timing posture
- compression state
- prosody behavior

This snapshot becomes part of the lineage record.

4. Rollback Target
- last known good configuration
- neg-proof verification
- safe-range posture
- stability confirmation

The rollback target must be logged before stabilization begins.

#### Verification Requirements

Rollback verification must confirm:

1. Correct Reversion
- system reverted to the correct rollback target
- no partial rollback occurred
- no unrelated envelopes were reverted

2. Stability Restoration
- stabilization window passed
- no residual drift
- no re-emergence of the failure mode
- no new instability introduced

3. Lineage Integrity
- RRG updated
- failed setting marked disallowed
- stabilization results recorded
- regression markers archived

4. Operator Confirmation
- operator validates stability
- operator confirms no hidden drift
- operator signs off on rollback completion

Operator confirmation is mandatory.

#### Verification Sequence

Verification must occur in the following order:

1. Confirm rollback target correctness
2. Confirm full reversion
3. Confirm stabilization window success
4. Confirm no new drift
5. Update RRG
6. Archive regression log
7. Resume tuning only after verification completes

Verification must be strict, sequential, and documented.

#### Forbidden

- silent regression
- silent rollback
- logging without verification
- verification without logging
- resuming tuning before verification completes
- omitting operator confirmation
- allowing lineage gaps

#### Status

- Final governed organ of Section 5
- Completes the rollback subsystem
- Ensures all rollback events are logged, verified, and lineage-aligned
- Precedes Section 6 (Field Evaluation Law)

---

## 6. Field Evaluation Law

### 6.0 Field Evaluation Law Overview

#### Purpose

- Define the constitutional framework for evaluating governed tuning in real-world conditions
- Ensure all evaluation is:
- structured
- comparable
- stable
- neg-proofed
- merchant-safe
- Prevent:
- subjective evaluation
- unstable exposure
- premature optimization
- drift masked by operator correction

Field Evaluation Law is the truth-testing organ of Phase 5.

#### Scope

Field Evaluation Law governs:

- all A/B evaluation windows
- all stability assessments
- all merchant-facing exposure
- all operator judgment windows
- all baseline comparisons
- all envelope-level performance checks

It does not govern:

- rollback (Section 5)
- context-compression thresholds (Section 4)
- ungoverned experimental tuning
- operator-forced overrides

#### Constitutional Role

Field Evaluation Law ensures:

- tuning is validated under real conversational conditions
- stability is measured, not assumed
- merchant comfort is prioritized
- operator judgment is integrated but not dominant
- evaluation windows remain consistent across all envelopes

Field evaluation is the arbiter of whether tuning survives contact with reality.

#### Evaluation Window Definition

A field evaluation window is the governed span of live calls used to test a tuning change against baseline under comparable real-world conditions.

Evaluation windows must be:

- consistent
- comparable
- documented
- lineage-aligned

No tuning may be judged outside a governed window.

#### Evaluation Principles

Field evaluation must follow these principles:

- Naturalness first, human-grade flow is the primary metric
- Continuity, no abrupt shifts in timing or behavior
- Emotional intelligence, stable and appropriate relational posture
- Timing stability, no drift and no AI-tell patterns
- Merchant comfort, no discomfort, confusion, or friction
- DeepLayer alignment, no contradictions across organs

These principles are non-negotiable.

#### Forbidden

- evaluating tuning outside a governed window
- using fewer than `10` calls for evaluation
- optimizing for close-rate first
- allowing operator bias to override stability evidence
- ignoring merchant discomfort
- treating evaluation as optional

#### Status

- Anchor organ of Section 6
- Governs all field evaluation behavior
- Precedes:
- 6.1 Evaluation Window Structure
- 6.2 Stability Metrics
- 6.3 Merchant-Comfort Requirements
- 6.4 Operator Judgment Protocol
- 6.5 Evaluation Logging & Lineage Update

### 6.1 Evaluation Window Structure

#### Purpose

- Define the governed structure of evaluation windows
- Ensure all evaluation windows are:
- consistent
- comparable
- stable
- merchant-safe
- lineage-aligned
- Prevent:
- invalid evaluation
- unstable exposure
- premature optimization
- operator-dependent improvisation

Evaluation windows are the measurement substrate of Field Evaluation Law.

#### Evaluation Window Definition

An evaluation window is the governed span of calls used to assess a single tuning condition under stable, comparable exposure rules.

Evaluation windows must be:

- structured
- documented
- repeatable
- neg-proofed
- comparable across settings

No tuning may be judged outside a governed window.

#### Window Length Requirements

Evaluation windows must follow these rules:

- Minimum length: `10` calls
- Standard length: `10-20` calls
- Extended length: permitted when:
- drift is subtle
- the envelope interacts with multiple subsystems
- merchant comfort signals are ambiguous
- operator judgment requires more evidence

Windows shorter than `10` calls are forbidden.

#### A/B Window Structure

A/B evaluation windows must:

- compare exactly one parameter or envelope at a time
- use matched window lengths
- use identical evaluation criteria
- avoid overlapping failure modes
- avoid simultaneous multi-parameter changes

A/B windows must be:

- clean
- isolated
- comparable
- lineage-aligned

A/B windows are the primary mechanism for determining whether a tuning survives real-world exposure.

#### Baseline Comparison Requirements

Every evaluation window must compare performance against:

- the current baseline
- the last known good
- the stability posture defined in Section 4
- the behavioral posture defined in Section 5
- merchant-comfort expectations

Baseline comparison must be:

- explicit
- documented
- neg-proofed

No evaluation may rely on intuition alone.

#### Operator Role in the Window

Operator judgment is:

- required
- governed
- bounded by evidence
- subordinate to stability metrics

Operators may:

- extend windows
- annotate windows
- flag instability
- halt evaluation if merchant safety is at risk

Operators may not:

- shorten windows
- override stability evidence
- declare success without baseline comparison

#### Window Integrity Rules

Evaluation windows must:

- remain free of tuning changes
- maintain consistent exposure conditions
- avoid operator-induced compensation
- avoid masking drift
- avoid mixing failure modes

Window integrity is mandatory.

#### Forbidden

- evaluating tuning outside a governed window
- using fewer than `10` calls
- running overlapping A/B windows
- changing parameters mid-window
- allowing operator bias to override evidence
- ignoring merchant discomfort
- treating evaluation windows as optional

#### Status

- Fully governed organ
- Defines the structure of all evaluation windows
- Precedes:
- 6.2 Stability Metrics
- 6.3 Merchant-Comfort Requirements
- 6.4 Operator Judgment Protocol
- 6.5 Evaluation Logging & Lineage Update

### 6.2 Stability Metrics

#### Purpose

- Define the governed metrics used to evaluate tuning stability
- Ensure all stability assessment is:
- measurable
- comparable
- neg-proofed
- merchant-safe
- lineage-aligned
- Prevent:
- subjective evaluation
- hidden drift
- operator-masked instability
- premature optimization

Stability metrics are the evidence substrate of Field Evaluation Law.

#### Stability Metric Categories

Stability must be evaluated across four governed domains:

1. Timing Stability
2. Compression Stability
3. Behavioral Stability
4. Merchant-Comfort Stability

All four domains must pass for a tuning to be considered stable.

#### 1. Timing Stability Metrics

Timing stability measures:

- pause timing consistency
- predictive-intent timing
- micro-pause distribution
- prosody-timing alignment
- absence of AI-tell patterns
- latency uniformity

Timing instability includes:

- inconsistent pauses
- unnatural timing shifts
- prosody overrides
- predictive-intent drift
- reflex-arc timing anomalies

Timing stability is the primary indicator of human-grade flow.

#### 2. Compression Stability Metrics

Compression stability measures:

- context-compression thresholds
- frame-drift behavior
- reinterpretation latency
- compression-expansion symmetry
- adherence to Section 4 safe ranges

Compression instability includes:

- frame collapse
- reinterpretation lag
- over-compression
- premature compression
- expansion drift

Compression stability ensures the system maintains coherent internal context.

#### 3. Behavioral Stability Metrics

Behavioral stability measures:

- natural conversational flow
- emotional-tone alignment
- absence of AI-tell behaviors
- consistency across calls
- DeepLayer posture coherence
- PCU-1.5 compensation frequency

Behavioral instability includes:

- unnatural tone shifts
- inconsistent relational posture
- operator-detected misalignment
- reflex-arc instability
- excessive compensation

Behavioral stability is the merchant-facing truth test.

#### 4. Merchant-Comfort Stability Metrics

Merchant-comfort stability measures:

- absence of discomfort signals
- absence of confusion
- absence of friction
- natural conversational rapport
- stable emotional posture

Merchant discomfort is a first-class failure signal, equal in weight to timing or compression drift.

Merchant-comfort instability includes:

- hesitation
- confusion
- tonal mismatch
- conversational friction
- emotional misalignment

Merchant comfort is non-negotiable.

#### Metric Thresholds

A tuning passes stability evaluation only if:

- all four domains pass
- no regression markers appear
- no drift is detected
- no envelope contradictions occur
- no merchant discomfort is observed
- operator confirms stability

Failure in any domain triggers:

- evaluation failure
- rollback review
- lineage update

#### Metric Logging Requirements

All stability metrics must be logged:

- per call
- per window
- per envelope
- per A/B comparison

Logs must include:

- timing metrics
- compression metrics
- behavioral markers
- merchant-comfort signals
- operator annotations

Silent evaluation is forbidden.

#### Forbidden

- evaluating stability without metrics
- relying solely on operator intuition
- ignoring merchant discomfort
- masking drift through operator correction
- declaring stability without baseline comparison
- treating stability metrics as optional

#### Status

- Fully governed organ
- Defines the stability metrics used in all evaluation windows
- Precedes:
- 6.3 Merchant-Comfort Requirements
- 6.4 Operator Judgment Protocol
- 6.5 Evaluation Logging & Lineage Update

### 6.3 Merchant-Comfort Requirements

#### Purpose

- Define the governed requirements for merchant comfort during evaluation
- Ensure merchant-side experience is:
- safe
- natural
- stable
- emotionally aligned
- friction-free
- Prevent:
- discomfort
- confusion
- tonal mismatch
- conversational friction
- emotional misalignment

Merchant comfort is a first-class constitutional metric, not a secondary signal.

#### Merchant-Comfort Definition

Merchant comfort is the observable condition in which the merchant experiences the conversation as natural, comprehensible, emotionally appropriate, and free of avoidable friction.

Merchant comfort must be:

- monitored
- logged
- evaluated
- weighted equally with timing and compression stability

Merchant discomfort is a failure signal, not a soft indicator.

#### Comfort Indicators

Merchant comfort is indicated by:

- natural conversational flow
- ease of understanding
- absence of hesitation
- stable emotional posture
- appropriate tone and pacing
- smooth turn-taking
- no detectable AI-tell patterns

These indicators must be present across the entire evaluation window.

#### Discomfort Indicators

Merchant discomfort includes:

- hesitation
- confusion
- tonal mismatch
- conversational friction
- emotional misalignment
- repeated clarifications
- unnatural timing or prosody
- subtle off signals detected by the operator

Any discomfort indicator is a first-class regression marker.

#### Comfort-Stability Integration

Merchant-comfort signals must integrate with stability metrics:

- discomfort overrides timing stability
- discomfort overrides compression stability
- discomfort overrides behavioral stability
- discomfort triggers evaluation failure
- discomfort requires operator annotation
- discomfort must be logged per call

Merchant comfort is not optional and cannot be outweighed by other metrics.

#### Operator Responsibilities

Operators must:

- monitor merchant comfort continuously
- annotate discomfort signals
- halt evaluation if discomfort becomes significant
- extend windows when comfort signals are ambiguous
- treat discomfort as a governed failure mode

Operators may not:

- ignore discomfort
- override discomfort with intuition
- declare stability when discomfort is present
- shorten windows to avoid discomfort detection

Operator judgment is bounded by merchant-safety law.

#### Comfort-Driven Evaluation Outcomes

If merchant discomfort is detected:

- the evaluation window fails
- the tuning must be reviewed
- stability metrics must be re-examined
- rollback review may be required
- lineage must be updated
- the failure mode must be logged

Merchant discomfort is a hard stop, not a soft warning.

#### Comfort Logging Requirements

Merchant-comfort logs must include:

- comfort indicators
- discomfort indicators
- operator annotations
- timing of discomfort events
- correlation with stability metrics
- correlation with envelope behavior

Silent comfort evaluation is forbidden.

#### Forbidden

- ignoring merchant discomfort
- treating comfort as secondary
- declaring stability when discomfort is present
- allowing operator bias to override comfort signals
- masking discomfort through operator compensation
- evaluating comfort outside a governed window

#### Status

- Fully governed organ
- Defines merchant-comfort requirements for all evaluation windows
- Precedes:
- 6.4 Operator Judgment Protocol
- 6.5 Evaluation Logging & Lineage Update

### 6.4 Operator Judgment Protocol

#### Purpose

- Define the governed role of operator judgment during evaluation
- Ensure operator input is:
- structured
- bounded
- evidence-aligned
- merchant-safe
- lineage-consistent
- Prevent:
- operator bias
- subjective overrides
- masking drift
- premature optimization
- intuition-only evaluation

Operator judgment is required, but it is not sovereign.

#### Operator Judgment Definition

Operator judgment is the governed human evaluation layer that interprets subtle drift, merchant discomfort, and qualitative instability in coordination with formal stability metrics.

Operator judgment must be:

- documented
- evidence-aligned
- neg-proofed
- subordinate to stability metrics

Operators cannot declare stability without metric confirmation.

#### Operator Responsibilities

Operators must:

- monitor merchant comfort
- detect subtle drift
- annotate discomfort signals
- extend evaluation windows when needed
- halt evaluation if safety is at risk
- provide qualitative notes
- confirm stability only when metrics support it

Operators may not:

- shorten windows
- override metric failures
- ignore merchant discomfort
- compensate for instability through conversational skill
- declare success based on intuition alone

Operator judgment is bounded by evidence.

#### Operator-Detected Drift

Operators must classify drift into one of the governed categories:

1. Timing Drift
2. Compression Drift
3. Behavioral Drift
4. Merchant-Comfort Drift
5. DeepLayer Posture Drift

Operator-detected drift is a first-class failure signal, equal to metric-detected drift.

#### Judgment-Metric Integration

Operator judgment must integrate with stability metrics:

- operator-detected drift overrides timing stability
- operator-detected discomfort overrides behavioral stability
- operator annotations must be logged per call
- operator judgment cannot contradict metrics
- operator judgment cannot rescue a failing window

Judgment and metrics must agree for a tuning to pass.

#### Judgment Window Rules

During an evaluation window, operators must:

- maintain consistent posture
- avoid influencing merchant behavior
- avoid compensating for instability
- avoid masking drift
- avoid leading the system into safe patterns

Operator behavior must not distort evaluation.

#### Judgment Logging Requirements

Operator judgment logs must include:

- drift annotations
- comfort annotations
- timing anomalies
- behavioral anomalies
- envelope-level contradictions
- operator notes
- correlation with stability metrics

Silent operator judgment is forbidden.

#### Judgment Failure Conditions

Operator judgment fails when:

- intuition contradicts metrics
- discomfort is ignored
- drift is unlogged
- windows are shortened
- operator compensation masks instability
- evaluation is declared complete without evidence

Judgment failure triggers:

- evaluation failure
- lineage update
- potential rollback review

#### Forbidden

- declaring stability without metric confirmation
- overriding discomfort signals
- masking drift through operator skill
- shortening evaluation windows
- ignoring subtle drift
- treating operator judgment as optional
- allowing bias to influence evaluation

#### Status

- Fully governed organ
- Defines the operator's role in evaluation
- Precedes:
- 6.5 Evaluation Logging & Lineage Update

### 6.5 Evaluation Logging & Lineage Update

#### Purpose

- Define the governed process for logging evaluation outcomes
- Ensure all evaluation windows are:
- documented
- traceable
- neg-proofed
- lineage-aligned
- Prevent:
- silent evaluation
- incomplete logging
- lineage gaps
- unverified stability claims

Evaluation logging is the audit trail of Field Evaluation Law.

#### Evaluation Logging Requirements

Every evaluation window must generate a complete evaluation log containing:

1. Window Metadata
- window type (baseline, A/B, extended)
- window length
- date and time range
- operator identity
- envelope(s) under evaluation

2. Stability Metrics
- timing stability results
- compression stability results
- behavioral stability results
- merchant-comfort stability results
- metric-detected drift markers

Metrics must be logged per call and per window.

3. Operator Judgment
- drift annotations
- comfort annotations
- qualitative notes
- operator-detected anomalies
- operator-detected contradictions

Operator judgment must be logged explicitly.

4. Merchant-Comfort Signals
- comfort indicators
- discomfort indicators
- timing of discomfort events
- correlation with stability metrics

Merchant discomfort is a first-class failure signal and must be logged.

5. Evaluation Outcome
- pass/fail determination
- failure-mode classification
- required next steps (rollback review, retuning, extended window)
- operator confirmation

Evaluation outcomes must be explicit, not inferred.

#### Lineage Update Requirements

After evaluation completes, lineage must be updated with:

- evaluation window summary
- stability results
- merchant-comfort results
- operator judgment summary
- failure-mode classification (if any)
- tuning decision (advance, revert, retry)
- updated baseline (if evaluation passed)

Lineage updates must be:

- complete
- chronological
- neg-proofed
- audit-safe

Silent lineage updates are forbidden.

#### Evaluation-to-Lineage Sequence

Lineage must be updated in the following order:

1. Log window metadata
2. Log stability metrics
3. Log merchant-comfort signals
4. Log operator judgment
5. Determine evaluation outcome
6. Update lineage
7. Archive evaluation log
8. Advance or revert tuning

This sequence is mandatory.

#### Failure Conditions

Evaluation fails when:

- any stability domain fails
- merchant discomfort is detected
- operator-detected drift occurs
- metrics contradict operator judgment
- window integrity is violated
- logging is incomplete

Failure triggers:

- rollback review
- lineage update
- potential re-evaluation

#### Forbidden

- silent evaluation
- logging without lineage update
- lineage update without logging
- declaring stability without evidence
- ignoring discomfort
- masking drift
- treating evaluation logging as optional

#### Status

- Final governed organ of Section 6
- Completes the Field Evaluation Law subsystem
- Ensures evaluation is logged, verified, and lineage-aligned
- Precedes Section 7 (Field Integration Law)

---

## 7. Field Integration Law

### 7.0 Field Integration Law Overview

#### Purpose

- Define the constitutional framework for integrating governed tuning into real-world operation
- Ensure all field integration is:
- safe
- controlled
- merchant-aligned
- evaluation-verified
- lineage-consistent
- Prevent:
- premature deployment
- unstable exposure
- unverified tuning entering production
- merchant-side risk
- drift introduced during integration

Field Integration Law is the deployment substrate of the governed system.

#### Scope

Field Integration Law governs:

- all transitions from evaluation to deployment
- all integration windows
- all merchant-facing exposure rules
- all operator-supervised integration phases
- all lineage-aligned advancement decisions
- all integration-grade safety checks

It does not govern:

- rollback (Section 5)
- evaluation windows (Section 6)
- experimental or ungoverned tuning
- operator-forced overrides

#### Constitutional Role

Field Integration Law ensures:

- only stable, evaluated, merchant-safe tuning enters production
- integration is gradual, governed, and reversible
- merchant experience remains protected
- operator oversight remains active
- lineage remains consistent and audit-safe

Integration is the final gate before a tuning becomes part of the live system.

#### Integration Window Definition

A field integration window is the governed span in which evaluated tuning is exposed to real production conditions under supervised, reversible deployment rules.

Integration windows must be:

- controlled
- incremental
- monitored
- documented
- lineage-aligned

No tuning may enter production outside a governed integration window.

#### Integration Principles

Field integration must follow these principles:

- Stability First, only evaluation-verified tuning may integrate
- Merchant Safety, merchant comfort overrides all other signals
- Incremental Exposure, integration must be gradual, not abrupt
- Operator Oversight, operators must monitor integration windows
- Reversibility, integration must remain rollback-safe
- Lineage Continuity, all integration events must update lineage

These principles are non-negotiable.

#### Integration Readiness Requirements

A tuning is eligible for integration only if:

- it passed evaluation (Section 6)
- no drift was detected
- no merchant discomfort occurred
- operator judgment confirmed stability
- lineage was updated
- the baseline was advanced

Integration readiness must be explicit, not assumed.

#### Forbidden

- integrating tuning that has not passed evaluation
- integrating tuning with known drift
- integrating tuning with merchant-comfort issues
- integrating tuning without operator oversight
- integrating tuning without lineage update
- treating integration as optional

#### Status

- Anchor organ of Section 7
- Governs all field-integration behavior
- Precedes:
- 7.1 Integration Window Structure
- 7.2 Integration Stability Requirements
- 7.3 Merchant-Safety Protocol
- 7.4 Operator Integration Duties
- 7.5 Integration Logging & Lineage Update

### 7.1 Integration Window Structure

#### Purpose

- Define the governed structure of field-integration windows
- Ensure all integration windows are:
- controlled
- incremental
- merchant-safe
- evaluation-verified
- lineage-aligned
- Prevent:
- abrupt exposure
- premature deployment
- unverified tuning entering production
- drift introduced during integration
- operator-dependent compensation

Integration windows are the deployment substrate of Field Integration Law.

#### Integration Window Definition

An integration window is the governed span of live production exposure in which a tuning is introduced gradually under supervised, reversible conditions.

Integration windows must be:

- incremental
- reversible
- monitored
- documented
- lineage-aligned

No tuning may enter production outside a governed integration window.

#### Window Length Requirements

Integration windows must follow these rules:

- Minimum length: `5` calls
- Standard length: `5-15` calls
- Extended length: permitted when:
- subtle drift is possible
- merchant-comfort signals require more evidence
- operator oversight identifies borderline behavior
- the envelope interacts with multiple subsystems

Windows shorter than `5` calls are forbidden.

#### Gradual Exposure Structure

Integration windows must introduce tuning gradually:

1. Initial Exposure (Calls `1-3`)
- monitor for immediate drift
- monitor for merchant discomfort
- confirm evaluation-grade stability persists

2. Mid-Window Exposure (Calls `4-7`)
- monitor timing stability
- monitor compression stability
- monitor behavioral posture
- confirm no regression

3. Full Exposure (Calls `8-15`)
- confirm stable performance under normal conditions
- confirm merchant comfort remains intact
- confirm operator judgment aligns with metrics

Abrupt exposure is forbidden.

#### Integration-Window Integrity Rules

Integration windows must:

- remain free of tuning changes
- maintain consistent exposure conditions
- avoid operator-induced compensation
- avoid masking drift
- avoid mixing failure modes
- avoid overlapping integration windows

Window integrity is mandatory.

#### Operator Oversight Requirements

Operators must:

- monitor integration windows continuously
- annotate drift or discomfort
- halt integration if safety is at risk
- extend windows when signals are ambiguous
- confirm stability before advancing

Operators may not:

- shorten integration windows
- override discomfort signals
- compensate for instability
- declare integration complete without evidence

Operator oversight is required, not optional.

#### Integration-Window Advancement Rules

A tuning may advance only if:

- no drift is detected
- no merchant discomfort occurs
- stability metrics remain within safe ranges
- operator judgment confirms alignment
- lineage is updated
- evaluation results remain valid

Advancement must be explicit, not assumed.

#### Failure Conditions

Integration fails when:

- drift is detected
- merchant discomfort occurs
- operator-detected anomalies appear
- metrics contradict operator judgment
- window integrity is violated
- logging is incomplete

Failure triggers:

- rollback review
- lineage update
- potential re-evaluation

#### Forbidden

- integrating tuning without evaluation
- abrupt exposure
- overlapping integration windows
- operator compensation
- ignoring discomfort
- advancing without lineage update
- treating integration windows as optional

#### Status

- Fully governed organ
- Defines the structure of all integration windows
- Precedes:
- 7.2 Integration Stability Requirements
- 7.3 Merchant-Safety Protocol
- 7.4 Operator Integration Duties
- 7.5 Integration Logging & Lineage Update

### 7.2 Integration Stability Requirements

#### Purpose

- Define the governed stability requirements for field integration
- Ensure integration stability is:
- evaluation-grade
- merchant-safe
- drift-free
- posture-consistent
- lineage-aligned
- Prevent:
- regression during integration
- drift introduced by real-world exposure
- merchant discomfort
- operator-masked instability
- premature advancement

Integration stability is the deployment-grade continuation of evaluation stability.

#### Integration Stability Definition

Integration stability is the condition in which a tuning preserves evaluation-verified behavior under live deployment exposure without introducing drift, discomfort, or subsystem instability.

Integration stability must be:

- measurable
- comparable
- neg-proofed
- merchant-aligned
- operator-verified

No tuning may advance without integration stability.

#### Stability Domains

Integration stability must be evaluated across the same four domains as evaluation stability, but under deployment-grade conditions:

1. Timing Stability
2. Compression Stability
3. Behavioral Stability
4. Merchant-Comfort Stability

All four domains must pass for integration to advance.

#### 1. Timing Stability Requirements

Timing stability must include:

- consistent pause timing
- natural micro-pause distribution
- stable predictive-intent timing
- absence of timing-based AI-tell patterns
- latency uniformity under real-world load

Timing instability includes:

- abrupt timing shifts
- inconsistent pauses
- prosody-timing mismatch
- predictive-intent drift

Timing stability is the first indicator of integration readiness.

#### 2. Compression Stability Requirements

Compression stability must include:

- stable compression thresholds
- consistent frame-expansion behavior
- no reinterpretation lag
- no premature compression
- no compression-driven drift

Compression instability includes:

- frame collapse
- reinterpretation latency
- over-compression
- expansion drift

Compression stability ensures the system maintains coherent context under deployment load.

#### 3. Behavioral Stability Requirements

Behavioral stability must include:

- natural conversational flow
- consistent emotional posture
- absence of AI-tell behaviors
- stable DeepLayer posture
- consistent relational alignment

Behavioral instability includes:

- tonal mismatch
- inconsistent posture
- reflex-arc instability
- operator-detected misalignment

Behavioral stability is the merchant-facing truth test during integration.

#### 4. Merchant-Comfort Stability Requirements

Merchant-comfort stability must include:

- no discomfort signals
- no confusion
- no friction
- no tonal mismatch
- no emotional misalignment

Merchant discomfort is a hard failure, equal in weight to timing or compression drift.

#### Integration Stability Thresholds

A tuning passes integration stability only if:

- all four stability domains pass
- no drift is detected
- no merchant discomfort occurs
- operator judgment confirms alignment
- evaluation results remain valid
- lineage is updated

Failure in any domain triggers:

- integration failure
- rollback review
- lineage update

#### Stability Logging Requirements

Integration stability logs must include:

- timing metrics
- compression metrics
- behavioral markers
- merchant-comfort signals
- operator annotations
- correlation with evaluation stability

Silent stability evaluation is forbidden.

#### Forbidden

- advancing tuning without integration stability
- ignoring merchant discomfort
- masking drift through operator compensation
- declaring stability without evidence
- treating integration stability as optional
- allowing regression from evaluation stability

#### Status

- Fully governed organ
- Defines the stability requirements for field integration
- Precedes:
- 7.3 Merchant-Safety Protocol
- 7.4 Operator Integration Duties
- 7.5 Integration Logging & Lineage Update

### 7.3 Merchant-Safety Protocol

#### Purpose

- Define the governed safety requirements for merchants during field integration
- Ensure merchant-side experience is:
- safe
- stable
- natural
- emotionally aligned
- drift-free
- Prevent:
- merchant discomfort
- confusion
- tonal mismatch
- emotional misalignment
- unsafe exposure during integration

Merchant safety is the highest-priority constraint during integration.

#### Merchant-Safety Definition

Merchant safety is the condition in which merchant experience remains free of discomfort, confusion, emotional mismatch, or unsafe conversational exposure during live integration.

Merchant safety must be:

- monitored
- logged
- operator-verified
- lineage-aligned
- treated as a first-class requirement

Merchant safety overrides all other integration signals.

#### Safety Indicators

Merchant safety is indicated by:

- natural conversational flow
- ease of understanding
- stable emotional posture
- absence of hesitation
- absence of confusion
- appropriate tone and pacing
- no detectable AI-tell patterns

These indicators must persist across the entire integration window.

#### Risk Indicators

Merchant-safety risk includes:

- hesitation
- confusion
- tonal mismatch
- conversational friction
- emotional misalignment
- repeated clarifications
- subtle off signals detected by the operator
- timing or prosody anomalies that affect comfort

Any risk indicator is a first-class failure signal.

#### Safety-Stability Integration

Merchant-safety signals must integrate with stability metrics:

- safety overrides timing stability
- safety overrides compression stability
- safety overrides behavioral stability
- safety overrides operator intuition
- safety triggers immediate evaluation of window integrity

Merchant safety is non-negotiable.

#### Operator Safety Responsibilities

Operators must:

- monitor merchant safety continuously
- annotate all safety-related signals
- halt integration if safety is compromised
- extend windows when safety signals are ambiguous
- treat safety risk as a governed failure mode

Operators may not:

- ignore safety signals
- override safety with intuition
- compensate for instability
- shorten windows to avoid detecting safety issues
- declare integration complete when safety is uncertain

Operator judgment is bounded by merchant-safety law.

#### Safety-Driven Integration Outcomes

If merchant-safety risk is detected:

- the integration window fails
- rollback review is required
- lineage must be updated
- operator annotations must be archived
- integration must not advance
- evaluation stability must be re-verified

Merchant-safety failure is a hard stop, not a soft warning.

#### Safety Logging Requirements

Merchant-safety logs must include:

- safety indicators
- risk indicators
- operator annotations
- timing of safety-related events
- correlation with stability metrics
- correlation with integration behavior

Silent safety evaluation is forbidden.

#### Forbidden

- ignoring merchant-safety risk
- treating safety as secondary
- advancing integration when safety is uncertain
- masking safety issues through operator compensation
- declaring stability when safety is compromised
- allowing safety to be overridden by metrics or intuition

#### Status

- Fully governed organ
- Defines merchant-safety requirements for all integration windows
- Precedes:
- 7.4 Operator Integration Duties
- 7.5 Integration Logging & Lineage Update

### 7.4 Operator Integration Duties

#### Purpose

- Define the governed responsibilities of operators during field integration
- Ensure operator behavior is:
- consistent
- bounded
- safety-aligned
- stability-aligned
- lineage-aligned
- Prevent:
- operator-induced drift
- operator masking of instability
- premature advancement
- unsafe exposure
- intuition-only decision-making

Operators are the human-layer guardians of integration safety.

#### Operator Role Definition

Operator integration duties are the governed responsibilities through which operators observe, annotate, intervene, halt, extend, escalate, and document field integration behavior to preserve safety, stability, reversibility, and lineage integrity.

Operators must:

- observe
- annotate
- intervene
- halt
- extend
- escalate
- document

Operator duties are mandatory, not advisory.

#### Core Operator Responsibilities

Operators must:

- monitor integration windows continuously
- detect drift across all stability domains
- detect merchant-safety risk immediately
- annotate all anomalies
- halt integration when safety is compromised
- extend windows when signals are ambiguous
- confirm stability before advancement
- ensure lineage is updated after each window

Operators may not:

- shorten windows
- ignore discomfort
- override safety signals
- compensate for instability
- declare integration complete without evidence

Operator behavior must remain neutral, consistent, and non-compensatory.

#### Drift-Monitoring Duties

Operators must monitor for:

- timing drift
- compression drift
- behavioral drift
- merchant-comfort drift
- DeepLayer posture drift

If drift is detected:

- integration halts
- window fails
- rollback review is required
- lineage must be updated

Operator-detected drift is a first-class failure signal.

#### Safety-Monitoring Duties

Operators must:

- prioritize merchant safety above all other signals
- halt integration immediately if safety is compromised
- annotate all safety-related events
- correlate safety signals with stability metrics
- escalate safety failures to rollback review

Merchant safety overrides:

- timing stability
- compression stability
- behavioral stability
- operator intuition
- evaluation history

Safety is the supreme constraint of integration.

#### Window-Integrity Duties

Operators must ensure:

- no tuning changes occur during integration
- exposure remains incremental
- windows remain reversible
- no overlapping windows occur
- no operator behavior masks drift
- no operator behavior influences merchant responses

Window integrity is mandatory.

#### Advancement Duties

Operators may advance a tuning only if:

- all stability domains pass
- no drift is detected
- no merchant-safety risk occurs
- operator judgment aligns with metrics
- evaluation results remain valid
- lineage is updated
- integration logs are complete

Advancement must be explicit, not implied.

#### Documentation Duties

Operators must document:

- drift events
- safety events
- timing anomalies
- behavioral anomalies
- merchant-comfort signals
- operator notes
- window outcomes
- lineage updates

Silent operator behavior is forbidden.

#### Failure Conditions

Operator duties fail when:

- safety signals are ignored
- drift is unlogged
- windows are shortened
- operator compensation masks instability
- advancement occurs without evidence
- lineage is not updated

Failure triggers:

- integration failure
- rollback review
- lineage update
- operator-level corrective action

#### Forbidden

- Ignoring safety or drift
- Overriding metrics with intuition
- Masking instability
- Shortening windows
- Advancing without lineage update
- Treating operator duties as optional
- Allowing bias to influence integration

#### Status

- Fully governed organ
- Defines operator responsibilities during field integration
- Precedes:
- 7.5 Integration Logging & Lineage Update

### 7.5 Integration Logging & Lineage Update

#### Purpose

- Define the governed process for logging integration outcomes
- Ensure all integration windows are:
- documented
- traceable
- neg-proofed
- lineage-aligned
- Prevent:
- silent integration
- incomplete logging
- lineage gaps
- unverified advancement

Integration logging is the audit trail of Field Integration Law.

#### Integration Logging Requirements

Every integration window must generate a complete integration log containing:

1. Window Metadata
- window type (initial, mid-window, full-exposure)
- window length
- date and time range
- operator identity
- envelope(s) under integration

2. Stability Metrics
- timing stability results
- compression stability results
- behavioral stability results
- merchant-safety stability results
- drift markers detected during integration

Metrics must be logged per call and per window.

3. Operator Annotations
- drift annotations
- safety annotations
- qualitative notes
- operator-detected anomalies
- operator-detected contradictions

Operator annotations must be explicit and complete.

4. Merchant-Safety Signals
- safety indicators
- risk indicators
- timing of safety-related events
- correlation with stability metrics

Merchant-safety risk is a hard failure and must be logged.

5. Integration Outcome
- pass/fail determination
- failure-mode classification
- required next steps (rollback review, extended window, re-evaluation)
- operator confirmation

Integration outcomes must be explicit, not inferred.

#### Lineage Update Requirements

After integration completes, lineage must be updated with:

- integration window summary
- stability results
- safety results
- operator judgment summary
- failure-mode classification (if any)
- advancement decision (advance, revert, retry)
- updated baseline (if integration passed)

Lineage updates must be:

- complete
- chronological
- neg-proofed
- audit-safe

Silent lineage updates are forbidden.

#### Integration-to-Lineage Sequence

Lineage must be updated in the following order:

1. Log window metadata
2. Log stability metrics
3. Log safety signals
4. Log operator annotations
5. Determine integration outcome
6. Update lineage
7. Archive integration log
8. Advance or revert tuning

This sequence is mandatory.

#### Failure Conditions

Integration fails when:

- any stability domain fails
- any merchant-safety risk occurs
- operator-detected drift appears
- metrics contradict operator judgment
- window integrity is violated
- logging is incomplete

Failure triggers:

- rollback review
- lineage update
- potential re-evaluation

#### Forbidden

- Silent integration
- Logging without lineage update
- Lineage update without logging
- Declaring stability without evidence
- Ignoring safety risk
- Masking drift
- Treating integration logging as optional

#### Status

- Final governed organ of Section 7
- Completes the Field Integration Law subsystem
- Ensures integration is logged, verified, and lineage-aligned
- Precedes Section 8 (End State)

---

## 8. End State

### 8.0 End State

#### Purpose

- Define the authoritative end state of the Phase 5 organism model
- Establish RRG VI as the active tuning constitution
- Specify how operators must interpret and apply the document
- Anchor the boundaries of safe change
- Prevent:
- unauthorized modification
- unsafe tuning
- misinterpretation of constitutional law
- drift introduced through informal practice

The End State is the final authority for all governed behavior.

#### Constitutional Authority

RRG VI is the active constitutional authority for the current Phase 5 organism model and the governing reference for all allowed tuning, evaluation, integration, rollback, and lineage decisions.

It defines:

- what changes are allowed
- what ranges are safe
- how to test changes
- how to evaluate outcomes
- how to integrate stable tuning
- how to update lineage

No tuning may override constitutional law.

#### Interpretation Rules

Operators must interpret RRG VI using:

1. Literal Meaning
- The written text governs.
- No inferred meaning may override explicit law.

2. Section Hierarchy
- Higher-level sections govern lower-level organs.
- Organ-level rules must align with section-level law.

3. Safety Supremacy
- Merchant safety overrides all other signals.
- Operator intuition cannot override safety or stability law.

4. Lineage Continuity
- All changes must update lineage.
- No silent changes are allowed.

5. Reversibility
- All changes must remain reversible.
- No irreversible tuning may be introduced.

Interpretation must remain bounded, consistent, and constitutional.

#### Change Boundaries

Changes are allowed only when:

- they fall within the safe ranges defined in RRG VI
- they pass evaluation (Section 6)
- they pass integration (Section 7)
- they maintain lineage continuity
- they preserve merchant safety
- they remain reversible

Changes are forbidden when:

- they violate constitutional law
- they introduce drift
- they bypass evaluation or integration
- they lack lineage updates
- they compromise safety

The End State defines the outer boundary of safe modification.

#### Testing Requirements

All changes must be tested using:

- evaluation windows (Section 6)
- integration windows (Section 7)
- stability metrics
- safety metrics
- operator oversight
- lineage updates

Testing must be:

- explicit
- documented
- repeatable
- neg-proofed

Silent or informal testing is forbidden.

#### Operational Posture

The organism must operate in a posture that is:

- stable
- safe
- reversible
- lineage-aligned
- merchant-aligned
- constitution-compliant

Operators must:

- enforce constitutional law
- maintain window integrity
- document all changes
- update lineage
- halt unsafe behavior

Operational posture is governed, not discretionary.

#### Failure Conditions

The End State is violated when:

- constitutional law is ignored
- safety is compromised
- drift is introduced
- lineage is incomplete
- evaluation or integration is bypassed
- irreversible changes are made

Violation triggers:

- rollback review
- lineage correction
- operator corrective action
- potential re-evaluation of the organism

The End State is the final safeguard of the system.

#### Status

- Capstone organ of RRG VI
- Defines the authoritative end state of the Phase 5 organism
- Governs interpretation, change boundaries, testing, and operational posture
- Completes the constitutional structure of the document

---

# End of RRG VI

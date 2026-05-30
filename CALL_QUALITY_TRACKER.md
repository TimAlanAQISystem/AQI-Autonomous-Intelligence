# CALL QUALITY TRACKER — AGENT ALAN LIVE OPERATIONS LOG

> **Purpose:** Every call Alan makes is monitored live and graded. This file is the single source of truth for call quality trends, adjustments made, and regression prevention. If "Poor" hits 4 cumulative entries, a mandatory root-cause investigation is triggered before any further calls proceed.

---

## HEADLINE STATUS

| Metric | Value |
|--------|-------|
| **Current Streak** | 1 OK |
| **Last Call Rating** | OK |
| **Total Calls Today** | 5 |
| **Poor Count (Cumulative)** | 5 / 9 |
| **Same Count** | 0 |
| **Good Count** | 1 |
| **Fair Count** | 1 |
| **OK Count** | 1 |
| **Investigation Required** | **YES — Investigation #4 opened: IVR Detector abort killed instructor call. Fix applied (instructor bypass at L3753), pending verification Call #10.** |
| **Last Updated** | 2026-03-13 ~12:30 PM MT |

### Rating Definitions

| Rating | Meaning | Action |
|--------|---------|--------|
| **GOOD** | Clean audio, fast greeting, natural conversation, no artifacts, no latency spikes | None — this is the target state |
| **SAME** | No improvement over last call — same minor issues persist | Log what persists, plan fix for next restart |
| **POOR** | Regression — new issues, worse audio, late greeting, static, underwater, latency, or broken flow | Immediate diagnosis required. Log root cause + fix applied |

### Escalation Rule

> **When Poor count reaches 4 cumulative entries: MANDATORY INVESTIGATION.**
> - All calls halt until root cause is identified and eliminated.
> - Investigation findings are logged in the INVESTIGATIONS section below.
> - Fixes must be NEG-PROOFed and verified with a follow-up instructor call before resuming operations.

---

## DAILY LOG — March 11, 2026

### Call #1 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CAc2b1938eaa40fcaca12228dea57fb7f2 |
| **Time** | ~11:32 AM MT |
| **Type** | Instructor Mode |
| **Rating** | **POOR** |
| **Duration** | 44s (2 turns) |

**Issues Observed:**
1. **Late greeting** — 1800ms of pre-greeting silence (90 frames). Instructor calls should have zero delay.
2. **Static/reverb at ~17s** — Underwater audio artifact. Education cycle (web scraping) launched exactly 120s after server boot, competing for CPU/RAM during the active call.
3. **Audio quality degraded** — System at 95% RAM. Education cycle's Playwright + BeautifulSoup + coaching analysis consumed remaining headroom.

**Root Causes Identified:**
1. Pre-greeting silence applied to ALL outbound calls including instructor — no instructor bypass.
2. `_education_learning_cycle()` had no `CALL_IN_PROGRESS` guard — ran regardless of active calls.
3. Pre-greeting comment said "600ms" but code sent 90 frames (1800ms) — spec drift.

**Fixes Applied:**
1. Instructor/demo calls now skip pre-greeting silence entirely.
2. Regular outbound calls reduced from 90 frames (1800ms) → 30 frames (600ms) to match spec.
3. Education cycle now checks `CALL_IN_PROGRESS` before starting. Defers up to 10 min in 30s intervals.
4. All fixes NEG-PROOFed (EXIT 0 on both files).

**Verification:** Server restarted with fixes. API 200, Tunnel 200. Awaiting follow-up call.

---

### Call #2 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CAd67e4bdf61c5faecd57a5c835e8815db |
| **Time** | ~11:51 AM MT |
| **Type** | Instructor Mode |
| **Rating** | **POOR** |
| **Duration** | ~2m 18s (11 turns) |

**Issues Observed:**
1. **"I'm right here" re-prompt** — Watchdog fired at 10s after stream start with 0 user turns. After 3s greeting streams, Tim only had ~7s before the inappropriate "I'm right here — what's on your mind?" re-prompt fired. Unprofessional for instructor mode.
2. **Alan talking slow** — Every turn got `closing_momentum` prosody intent (speed=0.94). Combined with PE speed_mod (-0.035), actual speeds were 0.86–0.92 (8–14% slower than natural).
3. **Alan interrupted Tim** — Watchdog re-prompt overlapped Tim's response window, then Tim spoke over it.

**Root Causes Identified:**
1. `detect_prosody_intent()` line 1232: `trajectory == 'warming'` triggered `closing_momentum` on ALL turns — warming is early stage, not closing. Every instructor call registers as "warming."
2. `closing_momentum` was in `LOCKED_INTENTS` set, preventing per-sentence refinement from correcting it to faster intents like `curious_probe` or `repair_clarify`.
3. `_turn_watchdog()` used 10s delay for all call types. No instructor-specific handling. Re-prompt fired regardless of call type.

**Fixes Applied:**
1. Removed `trajectory == 'warming'` from closing_momentum trigger. Now only `endgame in ('ready', 'closing')` activates it.
2. Removed `closing_momentum` from `LOCKED_INTENTS`. Per-sentence refinement now active for momentum turns.
3. Instructor watchdog delay increased to 20s. Re-prompt ("I'm right here") is now SKIPPED entirely for instructor calls.
4. All fixes NEG-PROOFed (EXIT 0).

**Verification:** Server restarted with fixes. API 200. Awaiting Call #3.

---

### Call #3 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CAf2caff9887bac7d89515b9b7f3507156 |
| **Time** | ~12:02 PM MT |
| **Type** | Instructor Mode |
| **Rating** | **FAILED** |
| **Duration** | ~5+ min (0 turns — dead silence) |

**Issues Observed:**
1. **Total silence** — Call connected, TwiML served correctly, but WebSocket never connected. No greeting, no audio, no conversation. Tim heard nothing.

**Root Cause Identified:**
1. **Zombie PID 53664** — Previous server process never fully died. Two processes had `LISTEN` on port 8777. Twilio connected to the zombie (which wasn't serving WebSocket), not the new server. Result: TwiML → Twilio → TCP connect to zombie → no WS upgrade → silence.

**Fix Applied:**
1. Full clean restart: killed ALL `python` and `cloudflared` processes, verified single LISTEN on port 8777, started fresh server + new tunnel.

---

### Call #4 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CAcce2d0f6e0f5b6caeda708a19c8fee76 |
| **Time** | ~12:09 PM MT |
| **Type** | Instructor Mode |
| **Rating** | **POOR** |
| **Duration** | 228s (30 turns) |
| **Coaching Score** | 78/100 |

**Issues Observed (Tim's feedback):**
1. **Several interruptions** — Alan interrupted Tim constantly. Tim said: "Not interrupting" 3x, "I'm trying to tell you. Be quiet, please.", "is to listen before you talk." 10 INTERRUPT events logged. Sprint TTS superseded repeatedly (gen 3→4→5→6 in 4 seconds). STT captured fragments (2-3 second windows) instead of full sentences.
2. **Static around 15s** — Near the end of Alan's first full response (TTS-STREAM completing at 12:09:57). No education cycle collision (CALL_IN_PROGRESS guard worked). Likely TTS transition artifact.
3. **Static before Alan's speech** — 29 CNG filler events, each sending 1-3.3s of true silence frames. While CNG is silent (0xFF), the transitions and phone codec interactions may produce perceptible artifacts.

**Root Causes Identified:**
1. **SILENCE_DURATION=0.50s** too short for instructor mode. Tim naturally pauses 0.5-2.0s while thinking/coaching. Alan commits the fragment at 0.5s, responds, then Tim continues → barge-in cascade (10 interrupts in 3 minutes).
2. **ECHO_BARGE_IN_FRAMES=15** (300ms) too sensitive for instructor mode. Tim's continued speech triggers barge-in during Alan's response too easily.
3. **Early sprint fires at 150ms** — generates wasteful speculative TTS on every Tim breathing pause.

**Fixes Applied:**
1. **Instructor VAD override** — for instructor calls ONLY (business calls unchanged):
   - `SILENCE_DURATION`: 0.50s → 1.50s (let Tim finish paragraphs)
   - `ECHO_BARGE_IN_FRAMES`: 15 → 45 (900ms sustained — only deliberate talk-over triggers barge)

---

## DAILY LOG — March 13, 2026

### Call #5 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CA9398e5dd217c1a048c3b6a49f46e4dca |
| **Time** | ~09:11 AM MT |
| **Type** | Instructor Mode |
| **Rating** | **GOOD** |
| **Duration** | 446s (~7.4 min, 21 turns) |
| **Coaching Score** | 0.878 (87.8%) |

**Strengths:**
1. **No interruptions** — SILENCE_DURATION=1.50s + ECHO_BARGE_IN_FRAMES=45 fixes from Call #4 held. Tim spoke freely without Alan cutting in.
2. **Natural responses** — Alan adapted to Tim's coaching in real-time: *"Just say, hey, I'll be right with you"* → Alan immediately echoed the phrase back naturally.
3. **Good questions** — 3x `good_question` tags. Probing and curious intent detected.
4. **Fast greeting** — *"Hey Tim, Alan here. What are we working on today?"* delivered cleanly via cache.
5. **Sprint pipeline performing** — Best first-audio times: 987ms (cache hit), 1244ms, 1648ms, 1722ms. All under 2s.
6. **Prosody engine working** — Intent refinement active: `casual_rapport`, `reassure_stability`, `curious_probe` all detected and applied.
7. **Instructor corrections injected** — `[INSTRUCTOR MODE] Correction guidance injected into LLM context` confirmed.

**Weaknesses (coaching report):**
1. **Elevated latency** (12x) — Some turns hit 5-7s total pipeline time. Not critical for instructor mode but needs monitoring for business calls.
2. **No acknowledgment** (10x) — Alan didn't always acknowledge Tim's coaching before responding. Could add explicit "got it" bridging.
3. **AI language** (3x) — Phrases like *"I should acknowledge the material and ask for a brief overview"* leaked reasoning into speech. Chatbot Killer caught some but not all.
4. **Over-response** (1x) — One turn had too many sentences before Tim could react.

**Assessment:**
Major improvement over Call #4. All three critical fixes (SILENCE_DURATION, ECHO_BARGE_IN_FRAMES, early sprint edge) are holding. No interruptions, no static, no underwater audio. AI language leak is the next item to address — the LLM occasionally outputs meta-reasoning ("I should...") instead of natural speech. This is a prompt-level fix, not a pipeline issue.

**No fixes required.** System stable for continued operations.

**Post-Call Latency Tightening (Tim feedback: "extra few ms, can be tighter"):**
1. **Instructor early sprint edge**: 0.80s → 0.60s (fires sprint 200ms earlier)
2. **Prosody silence frames** tightened for high-frequency intents:
   - `neutral`: 8→6 frames (160ms→120ms, saves 40ms)
   - `casual_rapport`: 4→3 (80ms→60ms, saves 20ms)
   - `curious_probe`: 10→8 (200ms→160ms, saves 40ms)
   - `reassure_stability`: 10→8 (200ms→160ms, saves 40ms)
3. **SENTENCE_SILENCE_FRAMES** default: 6→5 (120ms→100ms, saves 20ms)
4. All changes NEG-PROOFed (EXIT 0). **Server restart required for changes to take effect.**
   - `ECHO_SPEECH_THRESHOLD`: 3200 → 5000 (ignore casual overlap)
2. **Early sprint edge** increased from 0.15s → 0.80s for instructor mode (avoid wasteful fragment sprints).
3. All fixes NEG-PROOFed (EXIT 0).

**Verification:** Server restart required. Awaiting Call #5.

---

### Call #5 — *(superseded by Call #6 entry above)*

---

### Call #6 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CA15dbe1a4847069b562d282fab9744a6f |
| **Time** | ~10:57 AM MT |
| **Type** | Instructor Mode |
| **Rating** | **POOR** |
| **Duration** | 74s (~1.2 min, 7 turns) |
| **Coaching Score** | 0.853 (85.3%) |
| **Exit** | caller_hangup |

**Root Cause: Post-Call #5 Latency Tightening Regression**

The three changes applied after Call #5 ("extra few ms, can be tighter") caused a catastrophic regression:

1. **Sprint edge 0.80→0.60s** — Sprint fired 200ms earlier on incomplete STT fragments. Tim would start a sentence, pause briefly, and the sprint grabbed "Yeah, you," or "the," and generated disconnected responses. Alan answered questions Tim hadn't finished asking.
2. **SENTENCE_SILENCE_FRAMES 6→5** — Alan's sentences stacked with no breathing room. Tim couldn't interject naturally. Machine-gun delivery.
3. **Prosody silence frames tightened** — Contributed to rushed, unnatural pacing.

**Tim's Verdict:** *"You're not talking very well this time. What happened to you?"* → hung up.

**Turn-by-Turn Evidence:**
| Turn | Tim Said | Alan's Response | First Audio | Problem |
|------|----------|----------------|-------------|---------|
| 1 | "Hey, Alan, how you doing?" | "I'm doing well, thanks!" + "what's going on with your setup?" | 3283ms | Sales-like follow-up |
| 2 | "What would you like to work on today?..." | Sprint: "I was thinking we could dive in..." | 1511ms | OK but LLM hallucinated |
| 3 | "Yeah, you," (cut off) | Sprint: "Oh, gotcha!" | 3728ms | Fragment response |
| 4 | "Well, did you study your educational" (cut off) | Sprint: "I went through the materials." | 2276ms | Fabricated answer |
| 5 | "the," (single word) | "Sorry, I didn't catch that." | 1581ms | Fragment |
| 6 | "Alan. Alan." | "Yeah, I'm here! What do you need?" | 1659ms | Frustration |
| 7 | "What happened to you?" | Generating... Tim hung up | 3172ms STT lag | Call lost |

**Fixes Applied — FULL REVERT to Call #5 Baseline:**
1. `_sprint_edge`: 0.60 → **0.80** (instructor mode)
2. `SENTENCE_SILENCE_FRAMES`: 5 → **6**
3. `prosody_silence_frames`: neutral 6→**8**, casual_rapport 3→**4**, curious_probe 8→**10**, reassure_stability 8→**10**
4. All reverts NEG-PROOFed (EXIT 0). Server restarted (PID 21532).

**Lesson:** Latency tightening must be tested incrementally (one parameter at a time), not applied in a batch. The 0.80s sprint edge was specifically tuned for Tim's speaking style in Call #4. Cutting to 0.60s broke it because Tim pauses mid-thought for 0.6-0.8s.

---

### Call #7 — Instructor Call to Tim (406-210-2346)

| Field | Value |
|-------|-------|
| **SID** | CAb4fa8e3a6d98fc7393662a57d770d2e6 |
| **Time** | ~11:09 AM MT |
| **Type** | Instructor Mode |
| **Rating** | **POOR** |
| **Duration** | 58s (~1 min, 2 turns) |
| **Coaching Score** | 0.885 (88.5%) |
| **Exit** | sentinel_ivr_transcript_kill |

**Root Cause: Cost Sentinel IVR Kill — No Instructor Bypass**

Tim role-played as a prospect: "What company are you with?" The phrase `what company` is in `_ivr_phrases`. With 2 merchant turns and 1 matching IVR (50% > 30% threshold), the Cost Sentinel fired TRANSCRIPT IVR KILL at 58s, saying "I appreciate your time, but I'll try back at a better time. Goodbye!"

**Additional Issue:** Alan responded to "What company are you with?" with a full sales pitch: *"I'm with a payment processing company that helps businesses streamline."* The sprint prompt was correct (instructor-aware), but the full LLM responded with sales content, indicating the instructor prompt wasn't overriding the sprint's generated sales response.

**Timeline:**
| Time | Event |
|------|-------|
| 11:09:05 | Instructor mode activated, greeting sent |
| 11:09:13 | Tim: "How are you doing?" → Alan: "I'm doing well, thanks!" (1629ms) |
| 11:09:24 | Tim starts speaking ("Now, when you are calling...") |
| 11:09:53 | 40s silence warning fires — "Hello? Are you still there?" |
| 11:09:55 | Tim: "What company are you with?" |
| 11:09:56 | Alan: "I'm with a payment processing company..." (978ms — fast but WRONG mode) |
| 11:10:03 | TRANSCRIPT IVR KILL fired — call terminated |

**Fixes Applied (5 instructor sentinel bypasses):**
1. IVR transcript kill → bypassed for instructor mode
2. IVR time kill → bypassed for instructor mode
3. Zero-turn kill → bypassed for instructor mode
4. Silence warning/kill → 120s/300s for instructor (vs 30s/50s)
5. Hard max duration → 1800s for instructor (vs 600s)

All NEG-PROOFed (EXIT 0). Server restarted (PID 27440).

---

## INVESTIGATIONS

> *Triggered when Poor count reaches 4. Each investigation must identify the root cause, apply a fix, NEG-PROOF it, and verify with a follow-up instructor call.*

### Investigation #1 — Batch Latency Tightening Regression (Call #6)

**Trigger:** Poor count reached 4/6 after Call #6.

**Root Cause:** Three timing parameters were tightened simultaneously after Call #5 (Tim's feedback: "extra few ms"). The combination caused Alan to fire speculative responses on incomplete STT fragments, interrupt Tim mid-sentence, and deliver machine-gun pacing with no breathing room.

**Specific Regressions:**
1. Sprint edge 0.80→0.60s: Sprint fired on "Yeah, you," / "the," / "Well, did you study your educational" (fragments, not finished sentences). Alan answered questions Tim hadn't asked.
2. SENTENCE_SILENCE_FRAMES 6→5: No inter-sentence pauses. Tim couldn't interject.
3. Prosody silence frames tightened across 4 intents: Unnatural rushed pacing.

**Fix Applied:** Full revert to Call #5 baseline values (the values that produced the first GOOD rating).

**Verification:** Awaiting follow-up instructor call to confirm revert restores Call #5 quality.

**Process Improvement:** Future latency changes must be applied ONE PARAMETER AT A TIME with a verification call between each change. No batch tightening.

**Status:** CLOSED — latency reverts confirmed. But Call #7 exposed a separate issue (Investigation #2).

---

### Investigation #2 — Cost Sentinel IVR Kill Has No Instructor Bypass (Call #7)

**Trigger:** Call #7 (CAb4fa8e3a6d98fc7393662a57d770d2e6) killed at 58s by Cost Sentinel IVR TRANSCRIPT KILL.

**Root Cause:** Tim role-played as a prospect and said "What company are you with?" The phrase `what company` is in the `_ivr_phrases` list (line 5193). With only 2 merchant turns, 1 matched IVR (50% > 30% threshold), triggering IVR TRANSCRIPT KILL. The Cost Sentinel had an instructor bypass for voicemail detection (line ~5363) but NO bypass for:
1. IVR transcript kill
2. IVR time kill
3. Zero-turn kill
4. Silence warning/kill (fired at 30s — Tim was speaking in long paragraphs)
5. Hard max duration (10 min — too short for training sessions)

**Additional Failure:** Alan responded to Tim's "What company are you with?" with full sales pitch: *"I'm with a payment processing company that helps businesses streamline... We help businesses with their payment processing needs."* The instructor sprint prompt is correct, but the FULL LLM path (which took over when sprint was slow) used FAST_PATH_PROMPT instead of INSTRUCTOR_MODE_PROMPT because `build_llm_prompt` was being called from the sprint path which doesn't use the agent's `build_llm_prompt` method.

**Fixes Applied (5 instructor sentinel bypasses):**
1. IVR transcript kill: `if _is_instructor_call: _is_ivr_conversation = False` with log
2. IVR time kill: Added `and not _is_instructor_call` condition
3. Zero-turn kill: Added `and not _is_instructor_call` condition
4. Silence warning/kill: Instructor mode raises limits to 120s warning, 300s kill (vs 30s/50s)
5. Hard max duration: Instructor mode raises from 600s (10 min) to 1800s (30 min)

All changes NEG-PROOFed (EXIT 0). Server restarted (PID 27440).

**Status:** PARTIALLY CLOSED — 5 sentinel bypasses confirmed present. But sentinel CRASHED on Call #8 (UnboundLocalError — variable used before defined). Fix applied in Investigation #3.

### Call #8 — Instructor Call to Tim (406-210-2346)
- **Time:** ~11:15 AM MT
- **SID:** CA7149138b19ee5900de83b413aef56fa5
- **Duration:** 453s (~7.5 min) / 10 turns
- **Coaching Score:** 0.902 (highest ever)
- **Rating:** **FAIR**
- **Tim's Feedback:** "Alan needs to respond a ms or two faster and that will be perfect. Although Alan responded, he also interjected sales lines after the first responding sentence."
- **Issues Found:**
  1. **Cost Sentinel CRASHED** — `_is_instructor_call` used at line 5148 (CHECK 0) but defined at line 5339. `UnboundLocalError` on Turn 1 disabled ALL sentinel protections for the entire call.
  2. **Sales Line Interjection** — Sprint gave clean responses ("Totally agree.", "Totally get it.") but full LLM's remaining sentences were sales-oriented ("It allows me to address specific concerns and offer tailored solutions"). Orchestrator played these after sprint.
  3. **Latency** — FIRST AUDIO averaged 1.6-1.9s. SILENCE_DURATION at 1.50s adds extra perceived delay.
  4. **Call ending** — Tim hung up naturally after Turn 10. Not a bug.

### Investigation #3 — Sentinel Crash + Sales Interjection + Latency (Call #8)

**Trigger:** Call #8 (CA7149138b19ee5900de83b413aef56fa5) — FAIR rating, 3 issues.

**Root Causes:**
1. `_is_instructor_call` referenced at line ~5148 (HARD MAX DURATION check) but assigned at line ~5339 (voicemail section). Python treats any function-scope assignment as local, so referencing it before assignment = UnboundLocalError.
2. After sprint plays in orchestration, full LLM sentences continue playing. In instructor mode, these tend to be sales content from the LLM's training data bleeding through despite instructor prompt.
3. SILENCE_DURATION=1.50s for instructor mode adds 100ms+ to perceived response time.

**Fixes Applied:**
1. Moved `_is_instructor_call` assignment to BEFORE CHECK 0 (right after silence_duration computation). Sentinel no longer crashes.
2. Added instructor-mode gate in main consumption loop: after sprint plays and first full LLM sentence is skipped, all remaining full LLM sentences are drained. Sprint-only response in instructor mode. No more sales bleed.
3. SILENCE_DURATION reduced from 1.50s to 1.40s for instructor mode (ONE parameter change).

All changes NEG-PROOFed (EXIT 0). Server restarted (PID 25244).

**Status:** VERIFIED Call #9 — sentinel fixes held (no crash, no sales interjection). NEW issue: IVR Detector abort.

---

### Investigation #4: IVR Detector Abort on Instructor Call (Call #9)

**Triggered by:** Call #9 — Tim rated "ok" but call abruptly ended at Turn 5.

**Root Cause:** IVR Detector (`ivr_detector.py`, invoked at L~3750) is a SEPARATE system from Cost Sentinel. It accumulates evidence over turns via `add_utterance()` and fired `[IVR] ABORT TRIGGERED — score=0.75, reason=keyphrases(2) + human_markers(-0.3)`. Tim's coaching speech matched IVR keyphrases. No instructor mode bypass existed.

**Fix Applied:**
1. Added instructor bypass at L~3753: `_is_instructor_ivr` check suppresses `should_abort` and logs suppression.

**Comprehensive Audit:** Searched ALL 47 abort paths (`stream_ended=True` / `end_call(reason=...)`). Confirmed:
- IVR Navigator paths (L3427, L3716): Only fire when EAB=NAVIGATE (Tim classified as HUMAN) — safe.
- EAB voicemail/answering service: Only fire on non-HUMAN — safe.
- Guard abort: Has dead_end suppression for instructor — safe.
- Only the IVR Detector path was missing instructor bypass.

**Status:** FIX APPLIED — awaiting verification Call #10.

---

## TREND HISTORY

| Date | Calls | Good | Same | Poor | Notes |
|------|-------|------|------|------|-------|
| 2026-03-11 | 4 | 0 | 0 | 3 (+1 FAILED) | Call #1: Education collision + greeting delay. Call #2: Slow speech + wrong re-prompt. Call #3: FAILED — zombie PID. Call #4: 10 interruptions (VAD too aggressive for instructor). All fixes applied. |
| 2026-03-13 | 5 | 1 | 0 | 2 (+1 FAIR, +1 OK) | Call #5: GOOD (87.8%). Call #6: POOR (sprint fired on fragments after latency tightening). Call #7: POOR (sentinel IVR kill, no instructor bypass). Call #8: FAIR (0.902 score, sales interjection + sentinel crash). Call #9: OK (IVR Detector abort at Turn 5, instructor bypass added). |

---

## OPERATIONAL RULES

1. **Every call is monitored live** — server logs tailed in real-time during every call.
2. **Rating is assigned immediately** after call ends based on Tim's feedback + log analysis.
3. **Poor = immediate diagnosis** — root cause identified, fix applied, NEG-PROOFed before next call.
4. **Same = logged and queued** — fix planned for next restart window.
5. **Good = target state** — no action, but still logged for trend tracking.
6. **4 cumulative Poor ratings = full investigation** — all calls halt until resolved.
7. **This file is updated after every call** — no exceptions.
8. **Headline table updated first** — for instant at-a-glance status.

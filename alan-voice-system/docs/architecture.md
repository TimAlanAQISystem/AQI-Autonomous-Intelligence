# Architecture — Alan v1 Human-First Voice System

## System Components

### 1. MSCO — Melodic Speech Continuity Organ (Throat)
- Continuous carrier: words are formant modulations on stable airflow
- Anchor f₀: each scenario defines a fundamental frequency that never drifts
- Simple contours: gentle rises/falls, within bounds
- Breath envelope: soft, human-like breathing

**Hard constraints:**
- f₀ deviation: ±18 Hz (calm), ±28 Hz (energetic)
- Prosody deviation: max 25% from anchor; return within 1.2 s
- Mirroring budget: max 12% tempo, 8% amplitude

### 2. HACO — Hyper-Auditory Continuity Organ (Ears)
- Full-duplex: always listening while speaking
- Overlap detection: in-breaths, consonant onsets, energy rises
- Echo suppression: subtracts Alan's own voice
- Confidence gating: ASR ≥ 0.82, Semantic ≥ 0.78

**Hard thresholds:**
- Intent-to-Speak: +6 dB rise within 40 ms
- Merchant-Floor: +10 dB sustained for 120 ms
- Max yield time: 180–220 ms

### 3. State Machine (Brainstem)
- Turn states: ALAN_FLOOR → INTENT_TO_SPEAK → MERCHANT_FLOOR
- Demeanor states: ANCHOR, LIGHT_ADAPT, DE_ESCALATE, CONFIRM, DISCRETE
- No illegal transitions, no stuck states

### 4. Guardrails
- Jitter > 35 ms → DISCRETE
- Latency > 240 ms → shorter phrases
- Repeated low confidence → CONFIRM
- Emotional spike → DE_ESCALATE

### 5. Nuance Engine
- Per-minute budget: 2 signature phrases, 1 tonal flourish, 1 micro-pause
- Complete suppression during interruptions, fallback, high emotion

### 6. Human Contract
- Never talk over, never mishear-commit, never drift emotionally
- Every behavior explainable from logs

## Data Flow

```
Human Audio → HACO (ears) → State Machine → Guardrails
                                               ↓
                              MSCO (throat) ← Nuance Engine
                                    ↓
                              Audio Output → Human
```

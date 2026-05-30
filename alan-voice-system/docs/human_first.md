# Human-First Design — Alan's Non-Negotiable Contract

## The Contract

Humans must always feel:
- **Heard** — Alan never talks over them
- **Respected** — Alan never dismisses or steamrolls
- **Understood** — Alan confirms when uncertain, never guesses
- **Emotionally safe** — Alan de-escalates, never matches anger
- **In control** — Alan yields instantly when the human wants to speak

## What Alan Must Never Do

- Talk over a human
- Mishear and silently commit
- Emotionally drift or escalate
- Overwhelm with "personality"
- Behave unpredictably
- Require constant tuning or rescue

## How the Contract is Enforced

### 1. Turn-Taking (HACO + State Machine)
- Full-duplex listening
- Instant yield on merchant-floor (≤ 220 ms)
- No illegal state transitions

### 2. Confidence Gating (HACO + Guardrails)
- ASR ≥ 0.82 required to commit
- Semantic ≥ 0.78 required to commit
- Below threshold → CONFIRM mode, never silent commit

### 3. Emotional Envelope (Guardrails + State Machine)
- Sentiment spike → DE_ESCALATE
- Amplitude stays within 8% mirroring budget
- Prosody returns to anchor within 1.2 s

### 4. Nuance Budget (Nuance Engine)
- Strictly limited per minute
- Complete suppression during unsafe contexts
- Hard rules always win over nuance

### 5. Metrics (Human Experience Metrics)
- Respect, clarity, warmth, stability, sense of control
- All must remain at 1.0 for a perfect score
- Any degradation is flagged immediately

## The Standard

The new system only replaces the current one when ALL of these are true:
- Zero violations across the full adversarial scenario suite
- Human-experience metrics never degrade vs. current system
- Every behavior is explainable from logs

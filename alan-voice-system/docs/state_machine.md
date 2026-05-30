# State Machine — Turn-Taking and Demeanor

## Turn-Taking States

| State | Description |
|-------|-------------|
| ALAN_FLOOR | Alan is speaking |
| INTENT_TO_SPEAK | Human is about to speak (detected early cue) |
| MERCHANT_FLOOR | Human has the floor |

### Legal Transitions

```
ALAN_FLOOR → INTENT_TO_SPEAK → MERCHANT_FLOOR → ALAN_FLOOR
```

- ALAN_FLOOR → INTENT_TO_SPEAK: soft cue detected (+6 dB)
- INTENT_TO_SPEAK → MERCHANT_FLOOR: full speech detected (+10 dB / ASR tokens)
- INTENT_TO_SPEAK → ALAN_FLOOR: false alarm, human didn't speak
- MERCHANT_FLOOR → ALAN_FLOOR: human yields back

### Illegal Transitions

- ALAN_FLOOR → MERCHANT_FLOOR (must go through INTENT_TO_SPEAK)
  - Exception: overwhelming energy triggers fast-track with synthetic INTENT_TO_SPEAK

## Demeanor States

| State | Description |
|-------|-------------|
| ANCHOR | Calm, steady baseline |
| LIGHT_ADAPT | Small, safe adjustments within prosody limits |
| DE_ESCALATE | Slow, soften, stabilize when human is upset |
| CONFIRM | Explicit clarification mode (low confidence) |
| DISCRETE | Non-full-duplex fallback (high jitter) |

### Transitions

- Any → DE_ESCALATE: emotional spike detected
- Any → CONFIRM: repeated low confidence
- Any → DISCRETE: jitter > 35 ms
- DE_ESCALATE → ANCHOR: only when metrics stable
- CONFIRM → ANCHOR or LIGHT_ADAPT: confidence restored
- DISCRETE → ANCHOR: jitter stabilized

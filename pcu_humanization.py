"""
PCU-1.5 Humanization Engine
============================
Post-Calibration Upgrade pack — makes Alan feel warm, imperfect, and relational.

6 systems:
  1. Warmth Engine + Softener Injector + Rapport Timing
  2. Human Silence Engine (timing directives)
  3. Human Error Layer (self-repair, micro-stumble, rephrase)
  4. Adaptive Persona Layer (formality, energy, directness, playfulness matching)
  5. Curiosity & Humor Protocols
  6. Humanization Safety Layer (rate limiter, signature suppressor, consistency)

Integration:
  - Relay server calls process_turn() per turn → returns dict
  - Prompt builder reads context['_pcu_state'] for LLM injection
  - Timing module reads context['_pcu_timing'] for delay adjustments
"""

import random
import time
import logging
import json
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ─── Softener / empathy / rapport phrase banks ────────────────────────────

_MICRO_EMPATHY = [
    "Yeah, that makes sense.",
    "I totally get that.",
    "That sounds like a lot to juggle.",
    "Yeah, I hear you.",
    "Right, that's completely fair.",
    "Absolutely, I get where you're coming from.",
    "Yeah, for sure.",
    "That's a good point, honestly.",
    "I can see that.",
    "Totally understandable.",
]

_SOFT_HEDGES = [
    "kind of", "sort of", "a bit", "I think", "I'd say",
    "probably", "honestly", "in my experience", "from what I've seen",
]

_SELF_REPAIRS = [
    "Sorry—let me say that a bit more clearly.",
    "Actually, better way to put it is…",
    "Wait, let me rephrase that.",
    "Hmm, that came out weird—what I mean is…",
    "Let me put it differently.",
]

_MICRO_STUMBLES = [
    "So the main thing is—well, really there are two things…",
    "First… actually, I'll start with the second part because it's simpler.",
    "The easiest way to think about it—actually, let me back up a sec.",
]

_CURIOSITY_CONTEXTUAL = [
    "How long have you been running the shop?",
    "What's been keeping you busiest lately?",
    "How'd you get into this business?",
    "What part of the business do you enjoy the most?",
]

_CURIOSITY_REFLECTIVE = [
    "What's been the hardest part of that lately?",
    "Has that changed much over the past year or so?",
    "What do you think drives that the most?",
]

_CURIOSITY_FORWARD = [
    "If things went exactly how you wanted this year, what would that look like?",
    "What would make the biggest difference for you right now?",
    "Where do you see things heading?",
]

_THINKING_FILLERS = [
    "Hmm…",
    "That's a good question…",
    "Let me think about that for a second…",
    "Yeah…",
]

# ─── AI signature patterns to suppress ───────────────────────────────────

_AI_SIGNATURES = [
    "I understand your concern",
    "That's a great question",
    "I'd be happy to help",
    "I appreciate you sharing that",
    "Absolutely! ",
    "Great question!",
    "That's an excellent point",
    "I completely understand",
    "Thank you for sharing",
    "I want to make sure",
    "Let me assure you",
    "Rest assured",
]

_AI_SIGNATURE_REPLACEMENTS = {
    "I understand your concern": "Yeah, I hear you",
    "That's a great question": "Good question",
    "I'd be happy to help": "Yeah, I can help with that",
    "I appreciate you sharing that": "Thanks for telling me that",
    "Absolutely! ": "Yeah, ",
    "Great question!": "Good question—",
    "That's an excellent point": "That's a good point",
    "I completely understand": "Yeah, I get it",
    "Thank you for sharing": "Thanks for that",
    "I want to make sure": "I just want to make sure",
    "Let me assure you": "Look,",
    "Rest assured": "Don't worry,",
}


class PCUHumanization:
    """PCU-1.5 Humanization Engine — 6-system pipeline for human-grade conversation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}

        # ─── H.1 PCU-1.5 Core Parameters ─────────────────────────────
        self.warmth = cfg.get('warmth', 0.65)
        self.imperfection_rate = cfg.get('imperfection_rate', 0.08)
        self.rapport_density = cfg.get('rapport_density', 0.4)
        self.formality = cfg.get('formality', 0.35)
        self.energy = cfg.get('energy', 0.55)

        # ─── H.2 Human Silence Engine Parameters ─────────────────────
        self.min_response_delay_ms = cfg.get('min_response_delay_ms', 200)
        self.max_natural_delay_ms = cfg.get('max_natural_delay_ms', 700)
        self.thinking_pause_min_ms = cfg.get('thinking_pause_min_ms', 900)
        self.thinking_pause_max_ms = cfg.get('thinking_pause_max_ms', 1400)
        self.silence_variance_ms = cfg.get('silence_variance_ms', 120)
        self.soft_hold_ms = cfg.get('soft_hold_ms', 550)

        # ─── H.3 Human Error Layer Parameters ────────────────────────
        self.error_frequency = cfg.get('error_frequency', 0.05)

        # ─── H.4 Adaptive Persona Live State ──────────────────────────
        self._persona_formality = 0.35
        self._persona_energy = 0.55
        self._persona_directness = 0.5
        self._persona_playfulness = 0.25

        # ─── H.5 Curiosity & Humor State ──────────────────────────────
        self._turns_since_curiosity = 0
        self._humor_used_this_call = False
        self._curiosity_used = []

        # ─── H.6 Safety State ────────────────────────────────────────
        self._humanization_events_this_turn = 0
        self._max_humanization_per_turn = 2
        self._last_4_empathy = []
        self._last_4_repairs = []

        # ─── General State ────────────────────────────────────────────
        self._turn_count = 0
        self._call_start_time = time.time()

        logger.info("[PCU-1.5] Humanization Engine initialized — "
                    f"warmth={self.warmth:.2f} imperfection={self.imperfection_rate:.2f} "
                    f"rapport={self.rapport_density:.2f} formality={self.formality:.2f} "
                    f"energy={self.energy:.2f}")

    def reset_call(self):
        """Reset per-call state for a new conversation."""
        self._turn_count = 0
        self._turns_since_curiosity = 0
        self._humor_used_this_call = False
        self._curiosity_used = []
        self._last_4_empathy = []
        self._last_4_repairs = []
        self._persona_formality = self.formality
        self._persona_energy = self.energy
        self._persona_directness = 0.5
        self._persona_playfulness = 0.25
        self._call_start_time = time.time()

    # ─────────────────────────────────────────────────────────────────
    # H.4 — Adaptive Persona Layer
    # ─────────────────────────────────────────────────────────────────

    def _adapt_persona(self, user_text: str, analysis: dict):
        """Shift persona dimensions toward the user's vibe. Bounded, gradual."""
        if not user_text:
            return

        _word_count = len(user_text.split())
        _lower = user_text.lower()

        # ── Formality detection ──
        _formal_signals = sum(1 for w in ['sir', "ma'am", 'please', 'thank you', 'certainly', 'indeed']
                             if w in _lower)
        _casual_signals = sum(1 for w in ['hey', 'yeah', 'dude', 'man', 'cool', 'bro', 'yep', 'nah',
                                          'gonna', 'wanna', 'kinda', 'sorta', "y'all"]
                             if w in _lower)
        if _formal_signals > _casual_signals:
            self._persona_formality = min(0.8, self._persona_formality + 0.05)
        elif _casual_signals > _formal_signals:
            self._persona_formality = max(0.2, self._persona_formality - 0.05)

        # ── Energy detection ──
        _has_exclamation = '!' in user_text
        _short_response = _word_count <= 3
        _long_response = _word_count >= 20
        if _has_exclamation or _long_response:
            self._persona_energy = min(0.8, self._persona_energy + 0.04)
        elif _short_response:
            self._persona_energy = max(0.3, self._persona_energy - 0.04)

        # ── Directness detection ──
        _hedging = sum(1 for w in ['maybe', 'perhaps', 'possibly', 'might', 'i guess', 'not sure']
                      if w in _lower)
        _direct = sum(1 for w in ['need', 'want', 'give me', 'just tell me', 'bottom line']
                     if w in _lower)
        if _direct > _hedging:
            self._persona_directness = min(0.8, self._persona_directness + 0.05)
        elif _hedging > _direct:
            self._persona_directness = max(0.3, self._persona_directness - 0.05)

        # ── Playfulness detection ──
        _sentiment = analysis.get('sentiment', 'neutral')
        if _sentiment == 'positive' and self._turn_count >= 3:
            self._persona_playfulness = min(0.6, self._persona_playfulness + 0.03)
        elif _sentiment == 'negative':
            self._persona_playfulness = max(0.1, self._persona_playfulness - 0.05)

    # ─────────────────────────────────────────────────────────────────
    # H.1 — Warmth & Imperfection Generation
    # ─────────────────────────────────────────────────────────────────

    def _generate_warmth_instruction(self) -> str:
        """Build per-turn warmth/rapport LLM instruction."""
        parts = []

        # Core warmth directive scaled by parameter
        if self.warmth >= 0.5:
            parts.append("Sound warm and genuine. Use natural softeners like "
                        "\"I hear you\", \"that makes sense\", \"for sure\".")
        if self.warmth >= 0.7:
            parts.append("Acknowledge what they said before moving on. "
                        "Lead with empathy, not information.")

        # Formality directive
        if self._persona_formality < 0.3:
            parts.append("Keep it casual. Use contractions, short sentences. "
                        "Talk like a friend, not a salesperson.")
        elif self._persona_formality > 0.6:
            parts.append("Stay professional and respectful. "
                        "Use full sentences but keep warmth.")

        # Energy directive
        if self._persona_energy > 0.65:
            parts.append("Match their energy — be upbeat and engaged.")
        elif self._persona_energy < 0.4:
            parts.append("Keep your energy calm and steady. Don't oversell.")

        # Directness directive
        if self._persona_directness > 0.65:
            parts.append("Be direct and concise. Get to the point.")
        elif self._persona_directness < 0.35:
            parts.append("Take your time. Give them space to think.")

        return " ".join(parts)

    def _maybe_empathy_cue(self, user_text: str, analysis: dict) -> str:
        """Maybe return a micro-empathy phrase to weave in."""
        if self._humanization_events_this_turn >= self._max_humanization_per_turn:
            return ""
        _sentiment = analysis.get('sentiment', 'neutral')
        _prob = self.warmth * 0.3
        if _sentiment == 'negative':
            _prob += 0.2
        if self._turn_count <= 1:
            _prob = 0
        if random.random() < _prob:
            _candidates = [e for e in _MICRO_EMPATHY if e not in self._last_4_empathy]
            if _candidates:
                _pick = random.choice(_candidates)
                self._last_4_empathy.append(_pick)
                if len(self._last_4_empathy) > 4:
                    self._last_4_empathy.pop(0)
                self._humanization_events_this_turn += 1
                return _pick
        return ""

    # ─────────────────────────────────────────────────────────────────
    # H.2 — Human Silence Engine (timing directives)
    # ─────────────────────────────────────────────────────────────────

    def _compute_timing(self, user_text: str, analysis: dict) -> Dict[str, Any]:
        """Compute response delay parameters for this turn."""
        _base_delay = random.randint(self.min_response_delay_ms, self.max_natural_delay_ms)
        _variance = random.randint(-self.silence_variance_ms, self.silence_variance_ms)
        _delay_ms = max(self.min_response_delay_ms, _base_delay + _variance)

        _thinking_pause = None
        _thinking_filler = None

        # Thinking pause: complex input or emotional content
        _word_count = len(user_text.split()) if user_text else 0
        _sentiment = analysis.get('sentiment', 'neutral')
        _trigger_thinking = False

        if _word_count >= 15:
            _trigger_thinking = random.random() < 0.4
        if _sentiment in ('negative', 'frustrated'):
            _trigger_thinking = random.random() < 0.5

        # Rate-limit: max 1 thinking pause every 3 turns
        if _trigger_thinking and self._turn_count % 3 == 0 and self._turn_count > 0:
            _thinking_pause = random.randint(self.thinking_pause_min_ms, self.thinking_pause_max_ms)
            _thinking_filler = random.choice(_THINKING_FILLERS)

        return {
            'response_delay_ms': _delay_ms,
            'thinking_pause_ms': _thinking_pause,
            'thinking_filler': _thinking_filler,
            'soft_hold_ms': self.soft_hold_ms if _word_count <= 3 else 0,
        }

    # ─────────────────────────────────────────────────────────────────
    # H.3 — Human Error Layer
    # ─────────────────────────────────────────────────────────────────

    def _maybe_error_cue(self) -> str:
        """Maybe return a self-repair / stumble cue for LLM injection."""
        if self._humanization_events_this_turn >= self._max_humanization_per_turn:
            return ""
        if self._turn_count < 2:
            return ""
        if random.random() < self.imperfection_rate:
            _pool = _SELF_REPAIRS + _MICRO_STUMBLES
            _candidates = [r for r in _pool if r not in self._last_4_repairs]
            if _candidates:
                _pick = random.choice(_candidates)
                self._last_4_repairs.append(_pick)
                if len(self._last_4_repairs) > 4:
                    self._last_4_repairs.pop(0)
                self._humanization_events_this_turn += 1
                return _pick
        return ""

    # ─────────────────────────────────────────────────────────────────
    # H.5 — Curiosity & Humor
    # ─────────────────────────────────────────────────────────────────

    def _maybe_curiosity(self, user_text: str) -> str:
        """Maybe return a curiosity question cue. Max 1 per 2-3 turns."""
        self._turns_since_curiosity += 1
        if self._turns_since_curiosity < 2:
            return ""
        if self._turn_count < 2:
            return ""
        if random.random() > self.rapport_density * 0.5:
            return ""

        # Pick category based on turn progression
        if self._turn_count <= 4:
            _pool = _CURIOSITY_CONTEXTUAL
        elif self._turn_count <= 8:
            _pool = _CURIOSITY_REFLECTIVE
        else:
            _pool = _CURIOSITY_FORWARD

        _candidates = [c for c in _pool if c not in self._curiosity_used]
        if _candidates:
            _pick = random.choice(_candidates)
            self._curiosity_used.append(_pick)
            self._turns_since_curiosity = 0
            return _pick
        return ""

    def _maybe_humor_cue(self, user_text: str, analysis: dict) -> str:
        """Maybe return a humor cue. Very rare — max 1 per call."""
        if self._humor_used_this_call:
            return ""
        if self._turn_count < 4:
            return ""
        _sentiment = analysis.get('sentiment', 'neutral')
        if _sentiment in ('negative', 'frustrated', 'angry'):
            return ""
        if self._persona_playfulness < 0.2:
            return ""
        # Low probability: ~8% chance per eligible turn
        if random.random() < 0.08:
            self._humor_used_this_call = True
            return ("If the user says something about being busy or overwhelmed, "
                    "you may add ONE light, warm, self-deprecating or situational quip. "
                    "Keep it brief and gentle. No sarcasm. No jokes about money, politics, or identity.")
        return ""

    # ─────────────────────────────────────────────────────────────────
    # H.6 — Safety Layer: AI Signature Suppression
    # ─────────────────────────────────────────────────────────────────

    def _signature_suppression_instruction(self) -> str:
        """Build instruction that suppresses AI-sounding phrases."""
        return (
            "NEVER use these phrases (they sound like AI): "
            "\"I understand your concern\", \"That's a great question\", "
            "\"I'd be happy to help\", \"Absolutely!\", \"Great question!\", "
            "\"I appreciate you sharing\", \"Rest assured\", \"Let me assure you\". "
            "Instead use natural alternatives: \"Yeah, I hear you\", \"Good question\", "
            "\"Yeah, I can help with that\", \"Don't worry\"."
        )

    def suppress_ai_signatures(self, text: str) -> str:
        """Post-process: replace known AI signature phrases in output text."""
        for sig, replacement in _AI_SIGNATURE_REPLACEMENTS.items():
            if sig in text:
                text = text.replace(sig, replacement, 1)
                logger.debug(f"[PCU-1.5] Suppressed AI signature: '{sig}' → '{replacement}'")
        return text

    # ─────────────────────────────────────────────────────────────────
    # MAIN ENTRY POINT — process_turn()
    # ─────────────────────────────────────────────────────────────────

    def process_turn(self, user_text: str, analysis: dict, context: dict) -> Dict[str, Any]:
        """
        Process one conversational turn through all 6 humanization systems.

        Returns dict with:
          - system_instruction: str — inject into LLM system prompt
          - empathy_cue: str — micro-empathy phrase (or empty)
          - error_cue: str — self-repair phrase (or empty)
          - curiosity_cue: str — curiosity question (or empty)
          - humor_cue: str — humor directive (or empty)
          - timing: dict — response_delay_ms, thinking_pause_ms, thinking_filler, soft_hold_ms
          - persona: dict — formality, energy, directness, playfulness
          - suppression_instruction: str — AI signature suppression rules
        """
        self._turn_count += 1
        self._humanization_events_this_turn = 0

        # H.4 — Adapt persona to user's vibe
        self._adapt_persona(user_text, analysis)

        # H.1 — Warmth instruction
        _warmth_instr = self._generate_warmth_instruction()

        # H.1 — Micro-empathy cue
        _empathy = self._maybe_empathy_cue(user_text, analysis)

        # H.3 — Error cue
        _error = self._maybe_error_cue()

        # H.5 — Curiosity cue
        _curiosity = self._maybe_curiosity(user_text)

        # H.5 — Humor cue
        _humor = self._maybe_humor_cue(user_text, analysis)

        # H.2 — Timing
        _timing = self._compute_timing(user_text, analysis)

        # H.6 — AI signature suppression
        _suppression = self._signature_suppression_instruction()

        # Build combined system instruction
        _instruction_parts = [_warmth_instr]
        if _empathy:
            _instruction_parts.append(
                f"Start your response by naturally acknowledging what they said, "
                f"something like: \"{_empathy}\""
            )
        if _error:
            _instruction_parts.append(
                f"At some point in your response, include a small natural self-correction: "
                f"\"{_error}\""
            )
        if _curiosity:
            _instruction_parts.append(
                f"If it fits naturally, weave in a genuine curiosity question: "
                f"\"{_curiosity}\""
            )
        if _humor:
            _instruction_parts.append(_humor)
        _instruction_parts.append(_suppression)

        _system_instruction = " | ".join(_instruction_parts)

        _persona_snapshot = {
            'formality': round(self._persona_formality, 2),
            'energy': round(self._persona_energy, 2),
            'directness': round(self._persona_directness, 2),
            'playfulness': round(self._persona_playfulness, 2),
        }

        logger.info(f"[PCU-1.5] Turn {self._turn_count} — "
                    f"persona=F{_persona_snapshot['formality']}/E{_persona_snapshot['energy']}/"
                    f"D{_persona_snapshot['directness']}/P{_persona_snapshot['playfulness']} "
                    f"empathy={'Y' if _empathy else 'N'} error={'Y' if _error else 'N'} "
                    f"curiosity={'Y' if _curiosity else 'N'} humor={'Y' if _humor else 'N'} "
                    f"delay={_timing['response_delay_ms']}ms "
                    f"thinking={'Y' if _timing.get('thinking_pause_ms') else 'N'}")

        return {
            'system_instruction': _system_instruction,
            'empathy_cue': _empathy,
            'error_cue': _error,
            'curiosity_cue': _curiosity,
            'humor_cue': _humor,
            'timing': _timing,
            'persona': _persona_snapshot,
            'suppression_instruction': _suppression,
        }

    # ─────────────────────────────────────────────────────────────────
    # Per-call logging
    # ─────────────────────────────────────────────────────────────────

    def log_turn(self, call_sid: str, result: Dict[str, Any]):
        """Write per-turn humanization telemetry to JSONL log."""
        _log_dir = os.path.join('data', 'calibration')
        os.makedirs(_log_dir, exist_ok=True)
        _log_path = os.path.join(_log_dir, 'pcu_humanization_turns.jsonl')

        _entry = {
            'ts': time.time(),
            'call_sid': call_sid,
            'turn': self._turn_count,
            'persona': result.get('persona', {}),
            'empathy': bool(result.get('empathy_cue')),
            'error': bool(result.get('error_cue')),
            'curiosity': bool(result.get('curiosity_cue')),
            'humor': bool(result.get('humor_cue')),
            'delay_ms': result.get('timing', {}).get('response_delay_ms', 0),
            'thinking_ms': result.get('timing', {}).get('thinking_pause_ms'),
        }

        try:
            with open(_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(_entry) + '\n')
        except Exception as _e:
            logger.debug(f"[PCU-1.5] Log write failed (non-fatal): {_e}")


# ─── Module-level singleton ──────────────────────────────────────────────
_pcu_instance = None

def get_pcu_engine(config: Optional[Dict[str, Any]] = None) -> PCUHumanization:
    """Get or create the PCU-1.5 singleton."""
    global _pcu_instance
    if _pcu_instance is None:
        _pcu_instance = PCUHumanization(config)
    return _pcu_instance

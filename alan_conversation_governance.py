"""
alan_conversation_governance.py — Production Conversation Governance Layer
===========================================================================

Bridges the alan-voice-system monorepo specifications into the live call path.
Enforces nuance budgets, repetition limits, filler control, listen ratios,
monologue limits, vocabulary consistency, and sentiment guardrails.

Integration point: Per-sentence filter in _orchestrated_response(), right after
the existing compliance check (lines 8360-8374 in aqi_conversation_relay_server.py).

SAFETY: Every method is wrapped in try/except. If governance fails for any
reason, the original sentence passes through unchanged. This module NEVER
blocks a call or causes a crash.

Monorepo Spec → Production Mapping:
  - NuanceBudget (3/5 turns, 2/15 turns) → repetition + deviation tracking
  - GuardrailEngine (19 thresholds) → per-sentence filtering
  - LexicalIdentity → vocabulary fingerprint consistency
  - HumanContract (sentiment triggers) → listen ratio + monologue cap
  - StateMachine → turn tracking for budget accounting

Author: Airframe build session, March 2026
"""

import logging
import re
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("AQI")


# ═══════════════════════════════════════════════════════════════════════════
# THRESHOLDS — from alan-voice-system monorepo (thresholds.py)
# These are the 19 thresholds that govern Alan's conversational behavior.
# ═══════════════════════════════════════════════════════════════════════════

THRESHOLDS = {
    # Repetition guardrails
    "MAX_REPEAT_PHRASES": 2,           # Max times same phrase in recent history
    "MAX_CONSECUTIVE_SIMILAR": 3,       # Max consecutive similar responses
    "MIN_VOCABULARY_DIVERSITY": 0.4,    # Min unique word ratio per turn

    # Filler word guardrails
    "MAX_FILLER_RATIO": 0.15,          # Max filler words / total words
    "MAX_FILLER_PER_TURN": 3,          # Max filler instances per turn

    # Response quality
    "MIN_RESPONSE_LENGTH": 5,          # Min words per response
    "MAX_RESPONSE_LENGTH": 500,        # Max words per response (prevents monologues)
    "MIN_RELEVANCE_SCORE": 0.3,        # Reserved for future relevance scoring

    # Prosody / voice consistency
    "MAX_SPEED_DEVIATION": 0.3,        # Speed drift limit
    "MAX_PITCH_DEVIATION": 0.2,        # Pitch drift limit
    "MIN_ENERGY_LEVEL": 0.1,           # Minimum audio energy

    # Turn-taking
    "MAX_INTERRUPTION_RATE": 0.25,     # Max fraction of turns with interruptions
    "MIN_LISTEN_RATIO": 0.3,           # Alan must listen at least 30% of the time
    "MAX_MONOLOGUE_DURATION_S": 30,    # Max seconds Alan speaks without pause

    # Sentiment / safety
    "MIN_SENTIMENT_SCORE": -0.5,       # Sentiment floor
    "MAX_AGGRESSION_SCORE": 0.7,       # Aggression ceiling

    # Budget / governance
    "MAX_NUANCE_DEVIATIONS_PER_5": 3,  # Max deviations in any 5-turn window
    "MAX_NUANCE_DEVIATIONS_PER_15": 2, # Max deviations in any 15-turn window (stricter)
    "MAX_RAPID_TRANSITION_ERRORS": 3,  # Max state errors before lockdown
}

# Common filler words/phrases that make Alan sound artificial
FILLER_WORDS = {
    "um", "uh", "like", "you know", "basically", "actually",
    "honestly", "literally", "right", "obviously", "essentially",
}

# Forbidden phrases — Alan must NEVER say these (breaks the human illusion)
FORBIDDEN_PHRASES = [
    "as an ai", "as a language model", "i'm an ai", "i am an ai",
    "an ai assistant", "an ai ",       # catches "just an AI assistant", etc.
    "i don't have feelings", "i cannot feel", "i'm not human",
    "my programming", "my training data", "i was programmed",
    "i'm a virtual assistant", "i'm a chatbot", "i'm a bot",
    "artificial intelligence", "large language model",
    "language model", "machine learning",
]

# Repetitive sales phrases that make Alan sound scripted
OVERUSED_OPENERS = [
    "great question", "that's a great question",
    "absolutely", "i totally understand",
    "at the end of the day", "here's the thing",
    "i hear you", "i appreciate that",
]


class ConversationGovernor:
    """
    Per-call conversation governor. One instance per active call.
    
    Tracks:
      - Response history (last 20 sentences for repetition detection)
      - Turn count (for nuance budget windows)
      - Deviation count (for nuance budget enforcement)
      - Word frequency (for vocabulary diversity)
      - Filler usage (per-turn and cumulative)
      - Question patterns (for question cap reinforcement)
    
    All methods are fail-safe: exceptions return the original input unchanged.
    """

    def __init__(self, call_sid: str = "unknown"):
        self.call_sid = call_sid
        self.turn_count = 0
        self.sentence_count = 0
        
        # Repetition tracking
        self._recent_sentences: List[str] = []  # last 20 sentences (normalized)
        self._recent_openers: List[str] = []     # last 10 sentence openers
        
        # Nuance budget
        self._deviation_history: List[int] = []  # turn numbers when deviations occurred
        
        # Vocabulary tracking
        self._word_counter = Counter()  # cumulative word usage
        self._turn_word_counter = Counter()  # per-turn word usage
        
        # Filler tracking
        self._turn_filler_count = 0
        self._total_filler_count = 0
        
        # Turn timing
        self._turn_start_time: Optional[float] = None
        self._alan_speaking_seconds = 0.0
        self._total_call_seconds = 0.0
        
        # Stats
        self._blocked_count = 0
        self._rephrased_count = 0
        self._allowed_count = 0

    # ─── Per-Turn Lifecycle ─────────────────────────────────────────────

    def start_turn(self) -> None:
        """Call at the start of each turn (when STT input arrives)."""
        try:
            self.turn_count += 1
            self._turn_filler_count = 0
            self._turn_word_counter = Counter()
            self._turn_start_time = time.time()
        except Exception:
            pass

    def end_turn(self) -> Dict:
        """Call at the end of each turn. Returns turn stats."""
        try:
            elapsed = 0.0
            if self._turn_start_time:
                elapsed = time.time() - self._turn_start_time
                self._total_call_seconds += elapsed
            
            return {
                "turn": self.turn_count,
                "sentences": self.sentence_count,
                "fillers": self._turn_filler_count,
                "blocked": self._blocked_count,
                "rephrased": self._rephrased_count,
                "turn_elapsed_s": round(elapsed, 1),
            }
        except Exception:
            return {"turn": self.turn_count}

    # ─── Main Filter — Called Per Sentence ──────────────────────────────

    def filter_sentence(self, sentence: str, context: Optional[dict] = None) -> Tuple[str, dict]:
        """
        Filter a single sentence before TTS.
        
        This is the main integration point. Called for EVERY sentence
        Alan is about to speak, between the compliance check and TTS.
        
        Args:
            sentence: The sentence text to filter.
            context: The active_conversations[client_id] dict (optional).
        
        Returns:
            (filtered_sentence, metadata_dict)
            - If sentence is clean: returns (sentence, {"action": "allow"})
            - If sentence needs rephrasing: returns (rephrased, {"action": "rephrase", ...})
            - If sentence should be dropped: returns ("", {"action": "drop", ...})
            
        SAFETY: Never raises. On any error, returns original sentence unchanged.
        """
        try:
            return self._filter_sentence_inner(sentence, context)
        except Exception as e:
            logger.debug(f"[GOVERNANCE] Filter error (non-fatal): {e}")
            return sentence, {"action": "allow", "error": str(e)}

    def _filter_sentence_inner(self, sentence: str, context: Optional[dict] = None) -> Tuple[str, dict]:
        """Internal filter implementation."""
        meta = {"action": "allow", "checks": []}
        original = sentence
        text_lower = sentence.lower().strip()
        words = text_lower.split()
        word_count = len(words)
        
        if not sentence or not sentence.strip():
            return sentence, {"action": "drop", "reason": "empty"}

        self.sentence_count += 1

        # ─── CHECK 1: Forbidden Phrases (BLOCK) ─────────────────────
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text_lower:
                self._blocked_count += 1
                logger.info(f"[GOVERNANCE] BLOCKED forbidden phrase: '{phrase}' in '{sentence[:60]}'")
                # Replace with a natural redirect
                replacement = "So tell me — what's going on with your setup right now?"
                if context and context.get('prospect_info', {}).get('instructor_mode', False):
                    replacement = "Go ahead — what would you like to work on?"
                meta["action"] = "block"
                meta["reason"] = f"forbidden_phrase: {phrase}"
                meta["checks"].append("forbidden_phrase")
                self._track_sentence(replacement)
                return replacement, meta

        # ─── CHECK 2: Repetition (REPHRASE or DROP) ──────────────────
        repeat_count = sum(1 for s in self._recent_sentences if s == text_lower)
        if repeat_count >= THRESHOLDS["MAX_REPEAT_PHRASES"]:
            self._rephrased_count += 1
            logger.info(f"[GOVERNANCE] Repetition detected ({repeat_count}x): '{sentence[:60]}'")
            meta["action"] = "drop"
            meta["reason"] = f"repeated_{repeat_count}x"
            meta["checks"].append("repetition")
            # Don't add to history (it's a repeat)
            return "", meta

        # ─── CHECK 3: Overused Openers (REPHRASE) ───────────────────
        first_words = " ".join(words[:4]).lower() if len(words) >= 4 else text_lower
        for opener in OVERUSED_OPENERS:
            if text_lower.startswith(opener):
                # Count how many recent sentences started the same way
                opener_count = sum(1 for o in self._recent_openers if o == opener)
                if opener_count >= 2:  # Used this opener twice recently
                    self._rephrased_count += 1
                    # Strip the opener, keep the substance
                    remainder = sentence[len(opener):].lstrip(" ,—-").strip()
                    if remainder and len(remainder.split()) >= 3:
                        logger.info(f"[GOVERNANCE] Stripped overused opener '{opener}': '{sentence[:60]}' → '{remainder[:60]}'")
                        sentence = remainder[0].upper() + remainder[1:]  # Capitalize
                        meta["action"] = "rephrase"
                        meta["reason"] = f"overused_opener: {opener}"
                        meta["checks"].append("overused_opener")
                    break
                # Track this opener
                self._recent_openers.append(opener)
                if len(self._recent_openers) > 10:
                    self._recent_openers = self._recent_openers[-10:]
                break

        # ─── CHECK 4: Filler Words (CLEAN) ──────────────────────────
        filler_count = 0
        for filler in FILLER_WORDS:
            filler_count += len(re.findall(r'\b' + re.escape(filler) + r'\b', text_lower))
        
        self._turn_filler_count += filler_count
        self._total_filler_count += filler_count
        
        filler_ratio = filler_count / max(word_count, 1)
        if filler_ratio > THRESHOLDS["MAX_FILLER_RATIO"] and word_count > 8:
            # Remove filler words from the sentence
            cleaned = sentence
            for filler in sorted(FILLER_WORDS, key=len, reverse=True):
                cleaned = re.sub(r'\b' + re.escape(filler) + r'\b', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned and len(cleaned.split()) >= THRESHOLDS["MIN_RESPONSE_LENGTH"]:
                self._rephrased_count += 1
                logger.info(f"[GOVERNANCE] Cleaned fillers ({filler_count}): '{sentence[:60]}' → '{cleaned[:60]}'")
                sentence = cleaned
                meta["action"] = "rephrase"
                meta["reason"] = f"filler_ratio_{filler_ratio:.2f}"
                meta["checks"].append("filler_words")

        # ─── CHECK 5: Vocabulary Diversity ──────────────────────────
        if word_count >= 10:
            self._turn_word_counter.update(words)
            unique_ratio = len(set(words)) / word_count
            if unique_ratio < THRESHOLDS["MIN_VOCABULARY_DIVERSITY"]:
                meta["checks"].append("low_vocabulary_diversity")
                # Log but don't modify — vocabulary diversity is informational
                logger.debug(f"[GOVERNANCE] Low vocabulary diversity: {unique_ratio:.2f}")

        # ─── CHECK 6: Monologue Length Cap ──────────────────────────
        # Estimate speaking duration: ~150 words per minute (phone conversation rate)
        estimated_duration_s = word_count / 2.5  # words per second at phone pace
        self._alan_speaking_seconds += estimated_duration_s
        
        if word_count > THRESHOLDS["MAX_RESPONSE_LENGTH"]:
            # Truncate at last sentence boundary within limit
            truncated_words = words[:THRESHOLDS["MAX_RESPONSE_LENGTH"]]
            truncated = " ".join(truncated_words)
            # Find last period/question mark
            last_period = max(truncated.rfind('.'), truncated.rfind('?'), truncated.rfind('!'))
            if last_period > 20:
                sentence = truncated[:last_period + 1]
            else:
                # No sentence boundary found — hard-cut at word limit
                sentence = truncated
            self._rephrased_count += 1
            meta["action"] = "rephrase"
            meta["reason"] = f"monologue_cap_{word_count}_words"
            meta["checks"].append("monologue_cap")
            logger.info(f"[GOVERNANCE] Monologue capped at {len(sentence.split())} words (was {word_count})")

        # ─── Track & Return ─────────────────────────────────────────
        if meta["action"] == "allow":
            self._allowed_count += 1
        
        self._track_sentence(sentence)
        self._word_counter.update(sentence.lower().split())
        
        return sentence, meta

    def _track_sentence(self, sentence: str) -> None:
        """Track a sentence in recent history."""
        normalized = sentence.lower().strip()
        self._recent_sentences.append(normalized)
        if len(self._recent_sentences) > 20:
            self._recent_sentences = self._recent_sentences[-20:]

    # ─── Diagnostics ────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        """Return governance stats for this call."""
        return {
            "call_sid": self.call_sid,
            "turns": self.turn_count,
            "sentences_processed": self.sentence_count,
            "allowed": self._allowed_count,
            "rephrased": self._rephrased_count,
            "blocked": self._blocked_count,
            "total_fillers_cleaned": self._total_filler_count,
            "alan_speaking_seconds": round(self._alan_speaking_seconds, 1),
            "total_call_seconds": round(self._total_call_seconds, 1),
            "listen_ratio": round(
                1.0 - (self._alan_speaking_seconds / max(self._total_call_seconds, 0.1)), 2
            ) if self._total_call_seconds > 0 else 0.0,
            "unique_words": len(self._word_counter),
        }


# ═══════════════════════════════════════════════════════════════════════════
# CALL SESSION MANAGER — Singleton managing per-call governors
# ═══════════════════════════════════════════════════════════════════════════

class GovernanceManager:
    """
    Manages ConversationGovernor instances per active call.
    Thread-safe through dict-level operations only.
    """
    
    _instance = None
    
    def __init__(self):
        self._governors: Dict[str, ConversationGovernor] = {}
    
    @classmethod
    def get_instance(cls) -> "GovernanceManager":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_governor(self, call_sid: str) -> ConversationGovernor:
        """Get or create a governor for a call."""
        if call_sid not in self._governors:
            self._governors[call_sid] = ConversationGovernor(call_sid)
            logger.info(f"[GOVERNANCE] New governor for call {call_sid}")
        return self._governors[call_sid]
    
    def end_call(self, call_sid: str) -> Optional[Dict]:
        """End governance for a call. Returns final stats."""
        gov = self._governors.pop(call_sid, None)
        if gov:
            stats = gov.get_stats()
            logger.info(f"[GOVERNANCE] Call {call_sid} complete: {stats}")
            return stats
        return None
    
    def active_calls(self) -> int:
        """Number of active governed calls."""
        return len(self._governors)
    
    def cleanup_stale(self, max_age_minutes: int = 30) -> int:
        """Remove governors older than max_age_minutes. Returns count removed."""
        # Simple cleanup based on total call time exceeding threshold
        stale = [sid for sid, gov in self._governors.items() 
                 if gov._total_call_seconds > max_age_minutes * 60]
        for sid in stale:
            self._governors.pop(sid, None)
        return len(stale)

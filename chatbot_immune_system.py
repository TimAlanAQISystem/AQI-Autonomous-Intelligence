#!/usr/bin/env python3
"""
CHATBOT IMMUNE SYSTEM
======================
Extracted from aqi_conversation_relay_server.py (was lines ~7043-7313).

This module is Alan's defense against sounding like a chatbot.
It strips markdown formatting, kills filler phrases, blocks premature
goodbyes, and detects repetition — all before sentences reach TTS.

The name reflects what it actually does: it's an immune system that
identifies and destroys chatbot-pattern "pathogens" in LLM output.

Integration:
    from chatbot_immune_system import clean_sentence
    
    # In _orchestrated_response:
    cleaned = clean_sentence(raw_sentence, context, logger)
    if not cleaned:
        continue  # Sentence was killed

Design Principles:
    - EVERY kill is logged (transparency for debugging)
    - Returns "" for killed sentences (never None)
    - Filler prefix stripping preserves the substance after the filler
    - Early-turn exit guard prevents LLM panic-goodbye on turns 0-3
    - Repetition detector has two modes: short-phrase exact + long-phrase overlap
    - All patterns are lowercase-normalized for matching

Neg-Proofed: Yes
    - No external state mutation (reads context, doesn't write)
    - No exceptions can escape (all matching is regex/string, no IO)
    - Returns original string if no patterns match (safe passthrough)
    - Empty string input returns empty string (no crash on edge case)

Author: Extracted by Claude Opus 4.6 — AQI Relay Decomposition Phase 1
Date: March 3, 2026
"""

import re
import logging
import random
from typing import Optional

# Module logger — used when no external logger is passed
_module_logger = logging.getLogger("chatbot_immune_system")

# =============================================================================
# [2026-03-10] HUMANIZATION — Probabilistic filler preservation
# =============================================================================
# Real humans START sentences with "Yeah," "Look," "So," "Well," ALL THE TIME.
# Stripping 100% of fillers makes every response start with pure substance,
# which is deeply unnatural — no real person does that on the phone.
# These "natural openers" are preserved ~40% of the time when bridge phrases
# are disabled (which they currently are as of 2026-03-10).
# The rest of the prefixes (chatbot-specific like "I appreciate that,",
# "Got it,", "No problem,") are ALWAYS stripped — those are still AI tells.
NATURAL_OPENERS = {
    "yeah, ", "yeah — ", "yeah - ",
    "look, ", "look — ", "look - ",
    "so, ", "so — ",
    "well, ", "well — ",
    "right, ", "right — ", "right - ",
    "okay, ", "okay — ", "okay - ",
    "hey, ", "hey — ",
    "honestly, ", "honestly — ",
    "here's the thing, ", "here's the thing — ",
}
NATURAL_OPENER_KEEP_RATE = 0.40  # 40% preservation rate


# =============================================================================
# KILL LISTS — Chatbot patterns that must never reach the merchant's ear
# =============================================================================

# Exact-match kills: if the sentence IS this phrase (after lowering + stripping), kill it
CHATBOT_KILLS = [
    "that sounds great",
    "that sounds exciting",
    "looking forward to our chat",
    "looking forward to it",
    "in the meantime",
    "that's exciting",
    "that's great to hear",
    "that's wonderful",
    "absolutely",
    "of course",
    "great question",
    "got it",
    "okay, got it",
    "okay got it",
    "okay, sure",
    "right, got it",
    "that's a solid setup",
    "that's really solid",
    "nice setup",
    "yeah absolutely",
    "yeah, absolutely",
    "yeah",
    "yeah, sure",
    "sure thing",
    "i'm listening",
    "i'm right here",
    "i hear you",
    "i hear you, tell me more about that",
    "tell me more about that",
    "i appreciate that",
    "i appreciate your patience",
    "thanks for that",
    "i'm glad you're still with me",
    "i'm here to help",
    "i'm here to chat",
    "no problem at all",
    "no problem",
    "no worries at all",
    "thanks for giving me a minute",
    "thanks for your time",
    "i appreciate you mentioning that",
    "i appreciate you letting me know",
    "i appreciate you sharing that",
    "i appreciate you taking the time",
    "i understand completely",
    "totally understand",
    "i completely understand",
    "that makes total sense",
    "that makes sense",
    "fair enough",
    "have a good one",
    "have a great day",
    "have a great one",
    "take care",
    "i'll try again later",
    "i'll try back later",
    "i'll call back another time",
    "i'll reach out another time",
    "sounds like you're busy",
    "sounds like this isn't the right time",
    "sounds like i caught you at a bad time",
    "i don't want to take up your time",
    "i won't take up any more of your time",
]

# Partial-match kills: if the sentence CONTAINS this phrase, kill it
CHATBOT_CONTAINS_KILLS = [
    "i can help with that",
    "i can definitely help",
    "we can definitely help",
    "i'm here to help",
    "i'd love to help",
    "sounds great",
    "sounds exciting",
    "sounds wonderful",
    "sounds fantastic",
    "sounds like a great",
    "sounds like a valuable",
    "i appreciate you sharing",
    "i appreciate you mentioning",
    "i appreciate you letting me know",
    "i appreciate you taking",
    "thanks for sharing",
    "thanks for giving me",
    "thanks for letting me know",
    "that's really exciting",
    "how can i assist",
    "how may i help",
    "looking forward to",
    "solid setup",
    "great setup",
    "have a good one",
    "have a great day",
    "have a great one",
    "take care",
    "i'll try again later",
    "i'll try back",
    "i'll call back",
    "i'll reach out another",
    "i won't take up",
    "i don't want to take up",
    "caught you at a bad time",
    "sounds like you're busy",
    "isn't the right time",
    "i appreciate you picking up",
    "sounds like you're in a good",
    "sounds like you're having",
    "sounds like you're doing",
    "i don't want to keep you",
    "don't want to keep you",
    "that's totally understandable",
    "that's completely understandable",
    "i totally understand",
    "i completely understand",
    "of course",
]

# Filler prefixes: chatbot openers stripped from the START, preserving substance after
FILLER_PREFIXES = [
    "got it, ", "got it — ", "got it - ",
    "sure, ", "sure — ", "sure - ",
    "yeah, absolutely, ", "yeah absolutely, ",
    "yeah, so, ", "yeah so, ",
    "yeah, ", "yeah — ", "yeah - ",
    "absolutely, ",
    "perfect, ",
    "great, ",
    "of course, ", "of course — ", "of course! ",
    "right, got it, ",
    "okay, so, ", "okay so, ",
    "okay, ", "okay — ", "okay - ",
    "i'm listening, ", "i'm listening — ", "i'm listening. ",
    "i'm right here, ", "i'm right here — ", "i'm right here. ",
    "i hear you, ", "i hear you — ", "i hear you. ",
    "i appreciate that, ", "i appreciate that — ", "i appreciate that. ",
    "i appreciate you picking up, ", "i appreciate you picking up — ", "i appreciate you picking up. ",
    "thanks for that, ", "thanks for that — ", "thanks for that! ",
    "no problem, ", "no problem — ", "no problem. ",
    "no problem at all, ", "no problem at all — ", "no problem at all. ",
    "no worries, ", "no worries — ", "no worries. ",
    "totally, ", "totally — ",
    "totally understand, ", "totally understand — ",
    "i understand, ", "i understand — ",
    "fair enough, ", "fair enough — ",
    "that makes sense, ", "that makes sense — ", "that makes sense. ",
    # [2026-03-09 FIX] Bridge-word dedup — these match BRIDGE_UTTERANCES in
    # conversational_intelligence.py. When a bridge phrase ("Look...") plays
    # and the LLM ALSO starts with "Look, " → user hears double-opener.
    # Stripping them here prevents "Yeah... [gap] Yeah, I noticed" stutter.
    "right, ", "right — ", "right - ",
    "look, ", "look — ", "look - ",
    "hmm, ", "hmm — ", "hmm - ",
    "good question, ", "good question — ", "good question. ",
    "i get that, ", "i get that — ", "i get that. ",
]

# Goodbye patterns blocked on turns 0-3 (early-turn exit guard)
GOODBYE_PATTERNS = [
    "goodbye", "good bye", "bye bye", "bye for now",
    "have a good", "have a great", "have a nice",
    "take care", "talk to you later", "talk soon",
    "i'll let you go", "i'll try again", "i'll try back",
    "i'll call back", "i'll reach out", "catch you later",
    "thanks for your time", "thank you for your time",
    "i won't take up", "i don't want to bother",
    "i don't want to keep you", "don't want to keep you",
    "sounds like you're busy", "caught you at a bad time",
    "isn't the right time", "not the right time",
    "maybe another time", "perhaps another time",
]


# =============================================================================
# CORE FUNCTION — The single chatbot killer + exit guard for all output paths
# =============================================================================

def clean_sentence(s: str, context: dict, log: Optional[logging.Logger] = None, is_sprint: bool = False) -> str:
    """
    Strip markdown/list formatting AND chatbot patterns from LLM output.
    
    This is the SINGLE chatbot killer + exit guard function for all output paths.
    Extracted from aqi_conversation_relay_server.py for modularity.
    
    Args:
        s: Raw sentence from LLM
        context: Conversation context dict (needs 'messages' for repetition detection)
        log: Logger instance (falls back to module logger if None)
        is_sprint: If True, use lighter filtering (sprint generates short complete
                   thoughts — aggressive contains-match kills destroy natural responses)
    
    Returns:
        Cleaned sentence string, or "" if the sentence was killed.
    """
    if not s or not s.strip():
        return ""
    
    logger = log or _module_logger
    
    # [2026-03-16 FIX] Instructor mode flag — skip chatbot kills (Phase 3+4).
    # The kill lists ("of course", "got it", "absolutely", "sounds great") are
    # designed for SALES calls where chatbot-sounding phrases weaken the pitch.
    # In instructor/training mode, these are perfectly natural conversational
    # phrases. Blocking them causes 100% kill rate → pipeline timeout → dead air.
    _is_instructor_mode = context.get('prospect_info', {}).get('instructor_mode', False)
    
    # =========================================================================
    # PHASE 1: Markdown / formatting cleanup
    # =========================================================================
    
    # Remove **bold** markers
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    # [2026-04-02 FIX] Remove *action* stage directions (e.g. *sniff*, *laughs*, *pauses*)
    # The LLM generates these as human-sound markers but TTS reads them aloud as words.
    # Must run AFTER **bold** strip to avoid partial-match issues.
    s = re.sub(r'\*[^*]+\*', '', s).strip()
    # Remove __bold__ markers
    s = re.sub(r'__([^_]+)__', r'\1', s)
    # Remove leading numbered list prefixes ("1. ", "2. ", etc.)
    s = re.sub(r'^\d+\.\s*', '', s)
    # Remove leading bullet markers
    s = re.sub(r'^[-*]\s+', '', s)
    # Remove markdown headers
    s = re.sub(r'^#+\s*', '', s)
    # Strip "Label: Description" format — e.g. "Business Information: Your name"
    # Only strip if the label part is 1-4 words followed by colon
    s = re.sub(r'^[A-Z][a-zA-Z]*(?:\s[A-Z][a-zA-Z]*){0,3}:\s*', '', s)
    
    # =========================================================================
    # PHASE 2: Filler prefix stripping
    # =========================================================================
    # "Got it, three different businesses" -> "Three different businesses"
    # The filler adds nothing. The substance after it is what matters.
    # [2026-03-04] Sprint mode: skip filler stripping — sprint responses are
    # already short and natural. Stripping "Yeah, " or "Right, " from a 
    # 10-word sprint response often destroys the natural conversational flow.
    # [2026-03-16] Instructor mode: was skipped here, but that caused double-
    # opener stutter (bridge "Yeah..." + LLM "Yeah, I noticed..."). Filler
    # prefix stripping is DEDUP, not censorship — re-enabled for all modes.
    # Chatbot kills (Phases 3+4) remain disabled for instructor mode.
    
    # [2026-03-10 FIX] Filler prefix stripping now applies to ALL output including sprint.
    # Previously `is_sprint` skipped this, but bridge phrase ("Yeah, so...") + sprint
    # starting with the same word ("Yeah, here's...") caused double-opener stutter.
    # Filler prefix stripping is DEDUP, not censorship — safe for sprint.
    # [2026-03-10 HUMANIZATION] Natural openers ("Yeah, ", "Look, ", "So, ") are
    # preserved 40% of the time, making Alan sound like a real person who sometimes
    # starts with a filler word (because all humans do). Chatbot-specific fillers
    # like "I appreciate that, " are ALWAYS stripped.
    s_lower_check = s.strip().lower()
    for prefix in FILLER_PREFIXES:
        if s_lower_check.startswith(prefix):
            # [HUMANIZATION] Check if this is a natural opener worth keeping sometimes
            if prefix in NATURAL_OPENERS and random.random() < NATURAL_OPENER_KEEP_RATE:
                logger.info(f"[CHATBOT KILLER] Kept natural opener '{prefix.strip()}' (humanization)")
                break  # Keep it — don't strip
            stripped = s.strip()[len(prefix):]
            if stripped and len(stripped) > 3:
                # Capitalize the first letter of what remains
                stripped = stripped[0].upper() + stripped[1:]
                logger.info(f"[CHATBOT KILLER] Stripped filler prefix '{prefix.strip()}' → '{stripped[:50]}'")
                s = stripped
                break
    
    # =========================================================================
    # PHASE 3: Exact-match chatbot kills
    # [2026-03-16] Skip for instructor mode — these are natural training phrases
    # [2026-03-05] Sprint mode: only exact match, NOT startswith.
    # Sprint generates "Got it. How satisfied are you with your rates?" —
    # a natural sentence opening with a brief acknowledgment. The startswith
    # check was killing these, forcing fallback to the full LLM which then
    # timed out, causing 5-6s dead air on every turn. Evidence: Call
    # CA553c757dc6 — both sprint clauses killed, 3x pipeline timeout.
    # =========================================================================
    
    s_lower = s.strip().lower().rstrip('!.')
    if not _is_instructor_mode:
        for kill in CHATBOT_KILLS:
            if s_lower == kill or (not is_sprint and s_lower.startswith(kill)):
                logger.info(f"[CHATBOT KILLER] Stripped dead phrase: '{s[:50]}'")
                return ""
    
    # =========================================================================
    # PHASE 4: Contains-match chatbot kills
    # =========================================================================
    # [2026-03-04] Sprint mode: skip contains-match kills entirely.
    # [2026-03-16] Instructor mode: skip — natural training phrases get killed.
    
    if not is_sprint and not _is_instructor_mode:
        for kill in CHATBOT_CONTAINS_KILLS:
            if kill in s_lower:
                logger.info(f"[CHATBOT KILLER] Stripped (contains): '{s[:50]}'")
                return ""
    
    # =========================================================================
    # PHASE 5: Early-turn exit guard (turns 0-3)
    # =========================================================================
    # On turns 0-3, Alan MUST NOT say goodbye.
    # The LLM sometimes panics on ambiguous audio and tries to bail.
    
    _etg_turn = len(context.get('messages', [])) // 2
    if _etg_turn <= 3:
        for _gp in GOODBYE_PATTERNS:
            if _gp in s_lower:
                logger.warning(f"[EXIT GUARD] Blocked goodbye on turn {_etg_turn}: '{s[:60]}'")
                return ""
    
    # =========================================================================
    # PHASE 6: Repetition detector (two modes)
    # =========================================================================
    
    _rep_turn = len(context.get('messages', []))
    _prev_msgs = context.get('messages', [])
    _s_stripped = s.strip()
    _s_word_count = len(_s_stripped.split())
    
    # MODE A: SHORT-PHRASE exact-match (1-4 words)
    # If Alan has said this exact phrase 2+ times recently, block it.
    if _rep_turn >= 3 and 1 <= _s_word_count <= 4:
        _s_norm = _s_stripped.lower().rstrip('!.?,')
        _short_repeat_count = 0
        for _pm in _prev_msgs:
            _prev_alan = (_pm.get('alan', '') or '').strip()
            if not _prev_alan:
                continue
            # Check each sentence in previous Alan response
            for _prev_sent in re.split(r'[.!?]+', _prev_alan):
                _prev_norm = _prev_sent.strip().lower().rstrip('!.?,')
                if _prev_norm == _s_norm:
                    _short_repeat_count += 1
        if _short_repeat_count >= 2:
            logger.warning(
                f"[REPETITION DETECTOR] Blocked short repeated phrase "
                f"(turn {_rep_turn}, {_short_repeat_count}x): '{_s_stripped[:60]}'"
            )
            return ""
    
    # MODE B: LONG-PHRASE word-overlap (5+ words)
    if _rep_turn >= 3 and _s_word_count >= 5:
        _s_words = set(_s_stripped.lower().split())
        for _pm in _prev_msgs:
            _prev_alan = (_pm.get('alan', '') or '').strip()
            if not _prev_alan or len(_prev_alan.split()) < 5:
                continue
            # Check each previous Alan sentence individually
            for _prev_sent in re.split(r'[.!?]+', _prev_alan):
                _prev_sent = _prev_sent.strip()
                if len(_prev_sent.split()) < 5:
                    continue
                _prev_words = set(_prev_sent.lower().split())
                _overlap = len(_s_words & _prev_words)
                _ratio = _overlap / min(len(_s_words), len(_prev_words))
                if _ratio > 0.70:
                    logger.warning(
                        f"[REPETITION DETECTOR] Blocked repeated phrase (turn {_rep_turn}, "
                        f"overlap={_ratio:.0%}): '{_s_stripped[:60]}'"
                    )
                    return ""
    
    return _s_stripped

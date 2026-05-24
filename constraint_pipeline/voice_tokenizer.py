"""
voice_tokenizer.py
CC0 - No rights reserved.

Segments transcribed speech into constraint units using prosodic boundary markers:
pause indicators, filler tokens, self-correction markers, clause restarts,
and prosodic emphasis signals.

Input: raw transcript text (from STT output or manual transcription).
Output: list of VoiceTokens with segment text, prosodic type, and position.

NOTE: This operates on transcribed text only - not raw audio.
Audio-level prosodic analysis (pitch, duration, energy) requires audio data
and is out of scope for stdlib-only implementation.

Falsifiable claim: prosodic boundary markers in transcribed speech
correlate with constraint-signal boundaries in the underlying cognition.
Falsification: find prosodic boundary that does not mark constraint transition.
"""

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum


class ProsodicType(str, Enum):
    PAUSE_FILLED      = "pause_filled"      # um, uh, er - filled pause
    PAUSE_UNFILLED    = "pause_unfilled"    # em-dash, ellipsis - explicit pause marker
    SELF_CORRECTION   = "self_correction"   # "or rather", "I mean", restart
    CLAUSE_RESTART    = "clause_restart"    # mid-sentence restart
    EMPHASIS_MARKER   = "emphasis_marker"   # "really", "actually", stressed form
    HEDGE             = "hedge"             # "kind of", "sort of", "I think"
    CONSTRAINT_ANCHOR = "constraint_anchor" # archaic/precise forms: oft, whilst
    COORD_JUNCTION    = "coord_junction"    # "and", "but" as prosodic beat
    SEGMENT           = "segment"           # plain text segment between boundaries
    SILENCE_MARKER    = "silence_marker"    # [pause], [silence], (pause) annotations


# Boundary detection patterns
PROSODIC_PATTERNS = [
    # Explicit silence/pause annotations from STT
    (r"\[pause\]|\[silence\]|\(pause\)|\(silence\)",  ProsodicType.SILENCE_MARKER),
    # Unfilled pauses (punctuation-encoded)
    (r"—|…|\.\.\.",                                    ProsodicType.PAUSE_UNFILLED),
    # Filled pauses
    (r"\b(um|uh|er|ah|hmm|hm|mm)\b",                 ProsodicType.PAUSE_FILLED),
    # Self-correction markers
    (r"\b(or rather|I mean|that is|i\.e\.|what I mean is|actually no)\b",
                                                        ProsodicType.SELF_CORRECTION),
    # Clause restart indicators
    (r"\b(so anyway|anyway|but wait|wait|no actually|let me|okay so)\b",
                                                        ProsodicType.CLAUSE_RESTART),
    # Emphasis markers
    (r"\b(really|actually|literally|basically|genuinely|clearly|obviously)\b",
                                                        ProsodicType.EMPHASIS_MARKER),
    # Hedges
    (r"\b(kind of|sort of|I think|I guess|maybe|perhaps|probably|somewhat)\b",
                                                        ProsodicType.HEDGE),
    # Constraint anchors (archaic/precise)
    (r"\b(oft|whilst|wherefore|henceforth|thenceforth|whence)\b",
                                                        ProsodicType.CONSTRAINT_ANCHOR),
    # Coordination junctions used as prosodic beat
    (r"\b(and|but|or|so|yet|nor)\b",                  ProsodicType.COORD_JUNCTION),
]


@dataclass
class VoiceToken:
    index: int
    start: int
    end: int
    text: str
    prosodic_type: ProsodicType
    confidence: float


CONFIDENCE_MAP = {
    ProsodicType.SILENCE_MARKER:   0.95,
    ProsodicType.PAUSE_UNFILLED:   0.90,
    ProsodicType.CONSTRAINT_ANCHOR: 0.90,
    ProsodicType.SELF_CORRECTION:  0.85,
    ProsodicType.CLAUSE_RESTART:   0.85,
    ProsodicType.PAUSE_FILLED:     0.80,
    ProsodicType.HEDGE:            0.75,
    ProsodicType.EMPHASIS_MARKER:  0.70,
    ProsodicType.COORD_JUNCTION:   0.60,
    ProsodicType.SEGMENT:          0.40,
}


def tokenize(text: str) -> list[VoiceToken]:
    """
    Segment transcribed speech into VoiceTokens.
    Boundary markers are extracted first; remaining text segments fill gaps.
    Returns tokens in position order including both boundaries and segments.
    """
    hits = []
    covered = set()

    for pattern, ptype in PROSODIC_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            span = set(range(m.start(), m.end()))
            if span & covered:
                continue
            covered |= span
            hits.append((m.start(), m.end(), ptype, m.group(0)))

    hits.sort(key=lambda h: h[0])

    # Fill gaps between boundary markers as SEGMENT tokens
    all_tokens = []
    prev_end = 0
    for start, end, ptype, surface in hits:
        if start > prev_end:
            seg_text = text[prev_end:start].strip()
            if seg_text:
                all_tokens.append((prev_end, start, ProsodicType.SEGMENT, seg_text))
        all_tokens.append((start, end, ptype, surface))
        prev_end = end

    # Trailing segment
    if prev_end < len(text):
        seg_text = text[prev_end:].strip()
        if seg_text:
            all_tokens.append((prev_end, len(text), ProsodicType.SEGMENT, seg_text))

    result = []
    for i, (start, end, ptype, surface) in enumerate(all_tokens):
        result.append(VoiceToken(
            index=i,
            start=start,
            end=end,
            text=surface,
            prosodic_type=ptype,
            confidence=CONFIDENCE_MAP[ptype],
        ))

    return result


def filter_by_type(tokens: list[VoiceToken],
                   *types: ProsodicType) -> list[VoiceToken]:
    """Return only tokens matching specified prosodic types."""
    return [t for t in tokens if t.prosodic_type in types]


def strip_fillers(tokens: list[VoiceToken]) -> list[VoiceToken]:
    """Remove filled pauses and hedges - returns cleaner constraint signal sequence."""
    remove = {ProsodicType.PAUSE_FILLED, ProsodicType.HEDGE, ProsodicType.COORD_JUNCTION}
    return [t for t in tokens if t.prosodic_type not in remove]


def to_text(tokens: list[VoiceToken]) -> str:
    """Reconstruct text from token sequence."""
    return " ".join(t.text for t in tokens if t.text.strip())


def to_claim_table(tokens: list[VoiceToken], source_id: str = "unnamed") -> dict:
    claims = []
    for t in tokens:
        claims.append({
            "claim_id": f"{source_id}.voice.{t.index:04d}",
            "span": [t.start, t.end],
            "text": t.text,
            "prosodic_type": t.prosodic_type.value,
            "confidence": t.confidence,
            "claim": f"Span [{t.start}:{t.end}] is a {t.prosodic_type.value} prosodic unit",
            "falsification_condition": (
                f"Find transcript where {t.text!r} does not mark {t.prosodic_type.value} boundary"
            ),
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "token_count": len(tokens),
        "boundary_count": sum(1 for t in tokens if t.prosodic_type != ProsodicType.SEGMENT),
        "claims": claims,
    }


def write_claim_table(tokens: list[VoiceToken], source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.voice.json") -> None:
    table = to_claim_table(tokens, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[voice_tokenizer] {len(tokens)} tokens written to {path}")


if __name__ == "__main__":
    sample = (
        "So um — we are going forward, and I think, or rather I know, "
        "that oft the constraint shifts whilst the narrative holds. "
        "Actually no — let me restart. The car is forward-going, basically."
    )
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sample
    print(f"input: {text!r}\n")

    tokens = tokenize(text)

    print(f"{'idx':<4} {'type':<20} {'conf':<6} text")
    print("-" * 60)
    for t in tokens:
        print(f"[{t.index:02d}] {t.prosodic_type.value:<20} {t.confidence:<6} {t.text!r}")

    print(f"\ntotal tokens: {len(tokens)}")
    print(f"boundary tokens: {sum(1 for t in tokens if t.prosodic_type != ProsodicType.SEGMENT)}")

    print(f"\n--- stripped (no fillers/hedges/coord) ---")
    clean = strip_fillers(tokens)
    print(to_text(clean))

    print(f"\n--- constraint anchors only ---")
    anchors = filter_by_type(tokens, ProsodicType.CONSTRAINT_ANCHOR,
                              ProsodicType.PAUSE_UNFILLED, ProsodicType.SELF_CORRECTION)
    for t in anchors:
        print(f"  [{t.prosodic_type.value}] {t.text!r}")

"""
constraint_tokenizer.py
CC0 - No rights reserved.

Splits input text into constraint-bearing units (CBUs) - not word tokens,
but segments aligned to signal boundaries: pause markers, clause edges,
archaic/contraction boundaries, preposition boundaries.

A CBU is the minimal span that carries a detectable constraint signal.
Spans without signals are labeled NEUTRAL.

Output: list of CBU dicts with span, text, boundary_type, and position.
Writes falsifiable claims to CLAIM_TABLE.cbu.json.
"""

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum


class BoundaryType(str, Enum):
    PAUSE         = "pause"          # em-dash, ellipsis
    CLAUSE_COORD  = "clause_coord"   # and, but, or, nor, yet
    CLAUSE_SUB    = "clause_sub"     # whilst, while, because, if, when, though
    PREP_BOUNDARY = "prep_boundary"  # preposition marking spatial transition
    CONTRACTION   = "contraction"    # apostrophe contraction
    ARCHAIC       = "archaic"        # oft, whilst, wherefore, henceforth
    COMPOUND      = "compound"       # hyphenated form
    NEUTRAL       = "neutral"        # no detectable signal boundary


# Ordered boundary patterns - matched left to right, first hit wins per position
BOUNDARY_PATTERNS = [
    (r"—|…|\.\.\.",                          BoundaryType.PAUSE),
    (r"\bwhilst\b|\bwherefore\b|\boft\b|\bhenceforth\b|\bthenceforth\b",
                                              BoundaryType.ARCHAIC),
    (r"\bwhile\b|\bbecause\b|\bif\b|\bwhen\b|\bthough\b|\balthough\b|\bunless\b",
                                              BoundaryType.CLAUSE_SUB),
    (r"\band\b|\bbut\b|\bor\b|\bnor\b|\byet\b|\bso\b",
                                              BoundaryType.CLAUSE_COORD),
    (r"\b(in|on|at|under|over|through|within|toward|towards|forward|back|out|up|down)\b",
                                              BoundaryType.PREP_BOUNDARY),
    (r"\b\w+'\w+\b",                         BoundaryType.CONTRACTION),
    (r"\b\w+-\w+\b",                         BoundaryType.COMPOUND),
]


@dataclass
class CBU:
    index: int
    start: int
    end: int
    text: str
    boundary_type: BoundaryType
    trigger: str          # which token/pattern triggered the boundary
    confidence: float


def tokenize(text: str) -> list[CBU]:
    """
    Scan text and emit one CBU per detected boundary signal.
    Overlapping matches: first pattern in BOUNDARY_PATTERNS wins.
    Returns CBUs sorted by position.
    """
    hits = []  # (start, end, btype, trigger)
    covered = set()  # character positions already claimed

    for pattern, btype in BOUNDARY_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            # skip if any char in this match already claimed
            span = set(range(m.start(), m.end()))
            if span & covered:
                continue
            covered |= span
            hits.append((m.start(), m.end(), btype, m.group(0)))

    hits.sort(key=lambda h: h[0])

    cbus = []
    for i, (start, end, btype, trigger) in enumerate(hits):
        # confidence: pause/archaic highest, neutral lowest
        conf_map = {
            BoundaryType.PAUSE: 0.90,
            BoundaryType.ARCHAIC: 0.90,
            BoundaryType.CLAUSE_SUB: 0.85,
            BoundaryType.CONTRACTION: 0.80,
            BoundaryType.COMPOUND: 0.75,
            BoundaryType.CLAUSE_COORD: 0.70,
            BoundaryType.PREP_BOUNDARY: 0.65,
            BoundaryType.NEUTRAL: 0.30,
        }
        cbus.append(CBU(
            index=i,
            start=start,
            end=end,
            text=text[start:end],
            boundary_type=btype,
            trigger=trigger,
            confidence=conf_map[btype],
        ))

    return cbus


def to_claim_table(cbus: list[CBU], source_id: str = "unnamed") -> dict:
    claims = []
    for c in cbus:
        claims.append({
            "claim_id": f"{source_id}.cbu.{c.index:04d}",
            "span": [c.start, c.end],
            "text": c.text,
            "boundary_type": c.boundary_type.value,
            "trigger": c.trigger,
            "confidence": c.confidence,
            "claim": f"Span [{c.start}:{c.end}] is a {c.boundary_type.value} boundary",
            "falsification_condition": f"Find context where {c.trigger!r} does not mark {c.boundary_type.value}",
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "input_length": len(cbus),
        "claims": claims,
    }


def write_claim_table(cbus: list[CBU], source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.cbu.json") -> None:
    table = to_claim_table(cbus, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[constraint_tokenizer] {len(cbus)} CBUs written to {path}")


if __name__ == "__main__":
    sample = (
        "We are going forward — the car is forward-going, "
        "and oft the path shifts whilst the destination holds."
    )
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sample
    print(f"input: {text!r}\n")
    cbus = tokenize(text)
    for c in cbus:
        print(f"  [{c.index:02d}] {c.boundary_type.value:<16} {c.text!r:<20} "
              f"span=[{c.start}:{c.end}] conf={c.confidence}")

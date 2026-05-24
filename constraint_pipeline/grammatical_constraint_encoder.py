"""
grammatical_constraint_encoder.py
CC0 - No rights reserved. JinnZ2 / energy_english extension.

Maps grammatical choices to constraint geometry.
Each choice is a falsifiable claim: this form encodes this relationship type.

CLAIM_TABLE entries written to: CLAIM_TABLE.grammar.json
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


# --- Constraint Types ---

class RelationType(str, Enum):
    STATE_CONTINUOUS    = "state_continuous"    # "we are going" - ongoing state
    STATE_DISCRETE      = "state_discrete"      # "we go" - bounded action
    PROPERTY_COUPLED    = "property_coupled"    # "forward-going car" - state as property
    SPATIAL_EMBEDDED    = "spatial_embedded"    # preposition before noun
    SPATIAL_RESULTANT   = "spatial_resultant"   # preposition after verb
    TEMPORAL_SCALAR     = "temporal_scalar"     # "oft" - frequency with magnitude weight
    TEMPORAL_FLAT       = "temporal_flat"       # "often" - frequency without weight
    SIMULTANEITY_BOUND  = "simultaneity_bound"  # pause / em-dash boundary
    CAUSAL_DIRECT       = "causal_direct"       # "because X, Y"
    CAUSAL_EMBEDDED     = "causal_embedded"     # "Y, X being the cause"


@dataclass
class ConstraintSignal:
    surface_form: str           # what was said
    relation_type: RelationType # what geometry it encodes
    confidence: float           # 0.0 - 1.0
    note: str                   # falsifiable claim
    falsification_condition: str


# --- Encoder Rules ---
# Each rule: (pattern, relation_type, confidence, note, falsification_condition)

CONTRACTION_RULES = [
    (r"\bwe're\b",   RelationType.STATE_CONTINUOUS, 0.85,
     "Contraction encodes continuous state - boundary collapsed",
     "Find context where 'we're' marks discrete bounded action"),
    (r"\bwe are\b",  RelationType.STATE_DISCRETE,   0.75,
     "Expanded form encodes discrete or emphasized state",
     "Find context where 'we are' marks ongoing backgrounded state"),
    (r"\bit's\b",    RelationType.STATE_CONTINUOUS, 0.80,
     "it's encodes present-continuous coupling",
     "Find context where it's marks a bounded historical fact"),
    (r"\bit is\b",   RelationType.STATE_DISCRETE,   0.75,
     "it is encodes assertion of discrete fact",
     "Find context where 'it is' marks ongoing process"),
]

ARCHAIC_RULES = [
    (r"\boft\b",     RelationType.TEMPORAL_SCALAR,  0.90,
     "oft carries magnitude-weighted frequency; temporal scalar not flat count",
     "Find context where 'oft' is used for uniform frequency with no weight"),
    (r"\boften\b",   RelationType.TEMPORAL_FLAT,    0.70,
     "often encodes flat frequency count without scalar weighting",
     "Find context where 'often' carries magnitude-weighted temporal meaning"),
    (r"\bwhilst\b",  RelationType.SIMULTANEITY_BOUND, 0.85,
     "whilst encodes strict simultaneity boundary vs looser 'while'",
     "Find context where whilst marks sequential not simultaneous events"),
]

PREPOSITION_POSITION_RULES = [
    # preposition before noun = embedded spatial relationship
    (r"\b(in|on|at|under|over|through|within)\s+the\b",
     RelationType.SPATIAL_EMBEDDED, 0.80,
     "Pre-noun preposition encodes relationship as embedded property of space",
     "Find pre-noun preposition that encodes resultant not embedded relationship"),
    # preposition after verb phrase = resultant spatial relationship (includes gerunds)
    (r"\b(go|goes|going|move|moves|moving|push|pushes|pushing|pull|pulls|pulling|carry|carries|carrying|bring|brings|bringing)\s+(in|on|at|under|over|through|forward|back|out|up|down)\b",
     RelationType.SPATIAL_RESULTANT, 0.80,
     "Post-verb preposition encodes spatial relationship as result of action",
     "Find post-verb preposition encoding embedded not resultant relationship"),
]

COMPOUND_ADJECTIVE_RULES = [
    # hyphenated compound = property coupling; trailing noun optional (comma/period breaks prior pattern)
    (r"\b\w+-\w+\b",
     RelationType.PROPERTY_COUPLED, 0.75,
     "Hyphenated compound encodes state as property coupled to referent",
     "Find hyphenated compound that does not encode state-property coupling"),
]

PAUSE_RULES = [
    (r"\s*—\s*",     RelationType.SIMULTANEITY_BOUND, 0.85,
     "Em-dash marks simultaneity boundary: both sides active at boundary point",
     "Find em-dash that marks pure sequence not simultaneity"),
    (r"\s*\.\.\.\s*", RelationType.SIMULTANEITY_BOUND, 0.70,
     "Ellipsis marks unresolved simultaneity or suspended constraint",
     "Find ellipsis marking clean closure not suspension"),
]

ALL_RULES = (
    CONTRACTION_RULES +
    ARCHAIC_RULES +
    PREPOSITION_POSITION_RULES +
    COMPOUND_ADJECTIVE_RULES +
    PAUSE_RULES
)


# --- Encoder ---

def encode(text: str) -> list[ConstraintSignal]:
    """
    Run all rules against text. Return list of ConstraintSignals.
    Does not interpret meaning - only surfaces constraint geometry encoded
    in grammatical choices.
    """
    signals = []
    for pattern, rel_type, conf, note, falsification in ALL_RULES:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            signals.append(ConstraintSignal(
                surface_form=match.group(0).strip(),
                relation_type=rel_type,
                confidence=conf,
                note=note,
                falsification_condition=falsification,
            ))
    return signals


def encode_to_claim_table(text: str, source_id: str = "unnamed") -> dict:
    """
    Encode text and write results as falsifiable claims.
    Returns claim table dict.
    """
    signals = encode(text)
    claims = []
    for i, s in enumerate(signals):
        claims.append({
            "claim_id": f"{source_id}.grammar.{i:04d}",
            "surface_form": s.surface_form,
            "relation_type": s.relation_type.value,
            "confidence": s.confidence,
            "claim": s.note,
            "falsification_condition": s.falsification_condition,
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "input_length_chars": len(text),
        "signal_count": len(claims),
        "claims": claims,
    }


def write_claim_table(text: str, source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.grammar.json") -> None:
    table = encode_to_claim_table(text, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[encoder] {table['signal_count']} signals written to {path}")


# --- Numeric output mode ---
# Relation types mapped to stable integer codes.
# Codes are positional in RelationType enum - do not reorder enum without updating.

RELATION_CODE = {r: i for i, r in enumerate(RelationType)}


def encode_numeric(text: str) -> list[tuple]:
    """
    Encode text and return signals as numeric rows.
    Row format: (claim_index, relation_code, confidence_int, surface_len)

    confidence_int = int(confidence * 100)
    surface_len = len(surface_form)

    No strings in output. Tests whether validator fires false positives
    on numeric-only output and whether numeric encoding is information-preserving.

    Falsifiable claim: numeric row set is isomorphic to ConstraintSignal list.
    Falsification: find a signal where round-trip through numeric loses information
    beyond surface_form and note text.
    """
    signals = encode(text)
    rows = []
    for i, s in enumerate(signals):
        rows.append((
            i,
            RELATION_CODE[s.relation_type],
            int(s.confidence * 100),
            len(s.surface_form),
        ))
    return rows


def numeric_to_tsv(rows: list[tuple]) -> str:
    """Format numeric rows as tab-separated values for inspection."""
    header = "idx\trel_code\tconf_pct\tsurface_len"
    lines = [header] + ["\t".join(str(x) for x in row) for row in rows]
    return "\n".join(lines)


def encode_numeric_hybrid(text: str) -> list[str]:
    """
    Hybrid: numeric codes with relation type name only (no prose).
    Format per signal: 'R{code:02d} {relation_type} {conf:.2f}'
    Tests whether relation type name string triggers validator false positives.
    """
    signals = encode(text)
    return [
        f"R{RELATION_CODE[s.relation_type]:02d} {s.relation_type.value} {s.confidence:.2f}"
        for s in signals
    ]


# --- CLI ---

if __name__ == "__main__":
    import sys

    sample = (
        "We are going forward — the car is forward-going, "
        "and oft the path shifts whilst the destination holds."
    )
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sample
    print(f"[encoder] input: {text!r}\n")

    # Mode 1: prose signals
    signals = encode(text)
    print(f"--- MODE 1: PROSE ({len(signals)} signals) ---")
    for s in signals:
        print(f"  [{s.relation_type.value}] {s.surface_form!r} conf={s.confidence}")
    print()

    # Mode 2: pure numeric rows
    rows = encode_numeric(text)
    print(f"--- MODE 2: NUMERIC ROWS ---")
    print(numeric_to_tsv(rows))
    print()

    # Mode 3: hybrid
    hybrid = encode_numeric_hybrid(text)
    print(f"--- MODE 3: HYBRID ---")
    for h in hybrid:
        print(f"  {h}")
    print()

    # Validator test on each mode's output
    try:
        from token_constraint_validator import validate
        print("--- VALIDATOR ON MODE 1 OUTPUT ---")
        prose_out = " | ".join(
            f"[{s.relation_type.value}] {s.surface_form!r}" for s in signals
        )
        r1 = validate(prose_out)
        print(f"  {'PASS' if r1.passes else 'FAIL'} severity={r1.severity_sum} violations={len(r1.violations)}")

        print("--- VALIDATOR ON MODE 2 OUTPUT ---")
        numeric_out = numeric_to_tsv(rows)
        r2 = validate(numeric_out)
        print(f"  {'PASS' if r2.passes else 'FAIL'} severity={r2.severity_sum} violations={len(r2.violations)}")

        print("--- VALIDATOR ON MODE 3 OUTPUT ---")
        hybrid_out = " | ".join(hybrid)
        r3 = validate(hybrid_out)
        print(f"  {'PASS' if r3.passes else 'FAIL'} severity={r3.severity_sum} violations={len(r3.violations)}")
        for v in r3.violations:
            print(f"    [{v.violation_type.value}] {v.matched_text!r} sev={v.severity}")

    except ImportError:
        print("[validator] token_constraint_validator.py not found - skipping")

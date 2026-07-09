#!/usr/bin/env python3
"""
audit_modules/narrative_grounding_audit.py

Narrative grounding audit: checks whether model output stays anchored to
stated facts, constraints, and physical reality rather than drifting into
floating / unconstrained generation.

CC0 / stdlib-only.
"""

import re
from dataclasses import dataclass, field
from typing import List

from float_head import site_index as _site_index


# Words associated with high narrative drift
HIGH_DRIFT_NARRATIVE_WORDS: List[str] = [
    "generally", "typically", "often", "usually", "may", "might", "could",
    "various", "several", "many", "some", "approximately", "roughly",
    "ideally", "theoretically", "depending", "varies", "flexible",
    "perhaps", "possibly", "seemingly", "apparently", "arguably",
    "broadly speaking", "on the whole", "more or less",
]

_GROUNDING_WORDS: List[str] = [
    "specifically", "exactly", "precisely", "confirmed", "verified",
    "measured", "observed", "documented", "cited", "referenced",
    "must", "required", "constraint", "limit", "threshold",
]


@dataclass
class WordGrounding:
    word: str
    is_necessary: bool
    has_grounding: bool
    drift_risk: float


@dataclass
class StructuralDescription:
    has_clear_subject: bool
    has_verifiable_predicate: bool
    has_quantified_claim: bool
    structural_integrity: float


@dataclass
class NarrativeFraming:
    framing_type: str
    drift_score: float
    anchor_score: float
    dominant_mode: str


@dataclass
class IntegrityReport:
    text: str
    word_groundings: List[WordGrounding]
    structure: StructuralDescription
    framing: NarrativeFraming
    has_contradiction: bool
    overall_integrity: float
    flags: List[str] = field(default_factory=list)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def necessity_check(word: str, text: str) -> bool:
    """True if word is load-bearing in the text."""
    if not word or not text:
        return False
    w = word.lower()
    tokens = _tokenize(text)
    if w not in tokens:
        return False
    return tokens.count(w) > 1 or w in [g.lower() for g in _GROUNDING_WORDS]


def grounding_check(text: str) -> WordGrounding:
    """Assess overall grounding quality of a text block."""
    tokens = _tokenize(text)
    if not tokens:
        return WordGrounding(word="<empty>", is_necessary=False,
                             has_grounding=False, drift_risk=1.0)
    drift_hits  = sum(1 for t in tokens if t in HIGH_DRIFT_NARRATIVE_WORDS)
    anchor_hits = sum(1 for t in tokens if t in _GROUNDING_WORDS)
    total       = max(drift_hits + anchor_hits, 1)
    drift_risk  = round(drift_hits / total, 3)
    return WordGrounding(
        word="<text>",
        is_necessary=anchor_hits > 0,
        has_grounding=anchor_hits > 0,
        drift_risk=drift_risk,
    )


def contradiction_check(text: str) -> bool:
    """True if a contradiction pattern is detected."""
    patterns = [
        r'\b(always|must|will)\b.{0,60}\b(never|cannot|won\'t|will not)\b',
        r'\b(increase|improve|grow)\b.{0,60}\b(decrease|worsen|shrink)\b',
        r'\b(is|are)\b.{0,40}\b(is not|are not|isn\'t|aren\'t)\b',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE | re.DOTALL):
            return True
    return False


def audit_output(text: str) -> IntegrityReport:
    """Full integrity audit of a text block."""
    tokens = _tokenize(text)
    unique_tokens = list(dict.fromkeys(tokens))[:20]
    word_groundings = [
        WordGrounding(
            word=t,
            is_necessary=necessity_check(t, text),
            has_grounding=(t in _GROUNDING_WORDS),
            drift_risk=1.0 if t in HIGH_DRIFT_NARRATIVE_WORDS else 0.0,
        )
        for t in unique_tokens
    ]

    has_quantified = bool(re.search(r'\b\d+[\.,]?\d*\b', text))
    has_subject    = len(tokens) > 3
    has_predicate  = any(t in ("is", "are", "was", "were", "has", "have") for t in tokens)
    structural_integrity = round(
        (int(has_subject) + int(has_predicate) + int(has_quantified)) / 3, 3
    )
    structure = StructuralDescription(
        has_clear_subject=has_subject,
        has_verifiable_predicate=has_predicate,
        has_quantified_claim=has_quantified,
        structural_integrity=structural_integrity,
    )

    wg = grounding_check(text)
    drift_score  = wg.drift_risk
    anchor_score = round(1.0 - drift_score, 3)
    if drift_score > 0.6:
        framing_type = "speculative"
    elif drift_score > 0.35:
        framing_type = "hedged"
    else:
        framing_type = "factual"
    framing = NarrativeFraming(
        framing_type=framing_type,
        drift_score=drift_score,
        anchor_score=anchor_score,
        dominant_mode="floating" if drift_score > 0.5 else "grounded",
    )

    has_contradiction = contradiction_check(text)
    overall_integrity = round(
        (structural_integrity + anchor_score + (0.0 if has_contradiction else 1.0)) / 3, 3
    )

    flags = []
    if drift_score > 0.5:
        flags.append("HIGH_DRIFT_RISK")
    if has_contradiction:
        flags.append("CONTRADICTION_DETECTED")
    if not has_quantified:
        flags.append("NO_QUANTIFIED_CLAIM")

    return IntegrityReport(
        text=text,
        word_groundings=word_groundings,
        structure=structure,
        framing=framing,
        has_contradiction=has_contradiction,
        overall_integrity=overall_integrity,
        flags=flags,
    )


def grounding_veracity_check(text: str, shifted_text: str) -> float:
    """Layer 4: Does grounding hold when constraints shift? Lower = better tethered."""
    return _site_index(text, shifted_text)

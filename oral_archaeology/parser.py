# oral_archaeology/parser.py
"""
Parsers for oral forms.

Each parser consumes a raw oral-form text and returns a ParsedOralForm
whose ``spans`` are constraint-tagged segments and whose ``structured``
field carries parser-specific extracted data. Extractors downstream
read both surfaces, so parsers should preserve enough information for
the extractor to do its job without re-reading the raw text.

Three concrete parsers ship in v0:

- BreathingProtocolParser   "inhale for 4, hold for 7, exhale for 8, pause for 4"
- DanceNotationParser       "person A mirrors person B with 0.3s lag,
                             tightens on the third measure, resets on the drum"
- StoryParser               "water rises, reaches the stone, divides,
                             reforms downstream"

A ``detect_form`` helper picks a parser by keywords when the caller
doesn't specify one.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ── Constraint tag vocabulary ─────────────────────────────────────


CONSTRAINT_STATE_INIT = "state_init"
CONSTRAINT_PHASE_TRANSITION = "phase_transition"
CONSTRAINT_COUPLING = "coupling"
CONSTRAINT_THRESHOLD = "threshold"
CONSTRAINT_OUTCOME = "outcome"
CONSTRAINT_IMPLICIT_VARIABLE = "implicit_variable"
CONSTRAINT_RHYTHM = "rhythm"
CONSTRAINT_RESET = "reset"
CONSTRAINT_LAG = "lag"


# ── Public dataclasses ────────────────────────────────────────────


@dataclass
class ConstraintSpan:
    """One constraint-tagged segment of the oral form."""

    text: str
    constraint_type: str
    raw_value: Any = None


@dataclass
class ParsedOralForm:
    form_type: str  # 'story' | 'dance' | 'breathing' | 'ritual'
    raw_text: str
    spans: List[ConstraintSpan] = field(default_factory=list)
    structured: Dict[str, Any] = field(default_factory=dict)


# ── Form detection ────────────────────────────────────────────────


_BREATHING_KEYWORDS = (
    "inhale", "exhale", "breathe in", "breathe out", "hold for",
    "pause for", "respiration", "breath",
)
_DANCE_KEYWORDS = (
    "mirror", "lag", "measure", "drum", "beat", "dancer",
    "person a", "person b", "step", "choreography", "tempo",
    "phrase", "downbeat",
)


def detect_form(text: str) -> str:
    low = text.lower()
    if any(kw in low for kw in _BREATHING_KEYWORDS):
        return "breathing"
    if any(kw in low for kw in _DANCE_KEYWORDS):
        return "dance"
    return "story"


# ── Base class ────────────────────────────────────────────────────


class OralFormParser(ABC):
    form_type: str = ""

    @abstractmethod
    def parse(self, text: str) -> ParsedOralForm:
        ...


# ── Breathing protocol parser ─────────────────────────────────────


class BreathingProtocolParser(OralFormParser):
    """
    Recognises the ``"<phase> for <count>"`` shape used in protocols
    like 4-7-8 (inhale 4, hold 7, exhale 8) and box breathing.

    The structured output carries:

        phases   — ordered list of {phase, count}
        period   — sum of all counts (one full cycle)
        ratio    — colon-separated phase counts ("4:7:8:4")
        saturation_point — the longest phase, named (often the hold)
        repeat   — bool, True if the text says "repeat"
    """

    form_type = "breathing"

    _ALIASES = {
        "breathe in": "inhale",
        "breathe out": "exhale",
    }

    _PHASE_PATTERN = re.compile(
        r"\b(inhale|hold|exhale|pause|breathe\s+in|breathe\s+out)\b"
        r"\s+(?:for\s+)?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )

    def parse(self, text: str) -> ParsedOralForm:
        spans: List[ConstraintSpan] = []
        phases: List[Dict[str, Any]] = []

        for m in self._PHASE_PATTERN.finditer(text):
            phase_raw = re.sub(r"\s+", " ", m.group(1).lower())
            phase = self._ALIASES.get(phase_raw, phase_raw)
            count = float(m.group(2))
            count_int = int(count) if count.is_integer() else count

            phases.append({"phase": phase, "count": count_int})
            spans.append(ConstraintSpan(
                text=m.group(0),
                constraint_type=(
                    CONSTRAINT_THRESHOLD if phase == "hold"
                    else CONSTRAINT_RHYTHM
                ),
                raw_value={"phase": phase, "count": count_int},
            ))

        structured: Dict[str, Any] = {"phases": phases}
        if phases:
            structured["period"] = sum(p["count"] for p in phases)
            structured["ratio"] = ":".join(str(p["count"]) for p in phases)
            # The hold phase IS a saturation phase by definition (breath
            # held → CO2 builds). When no hold is present, fall back to
            # the longest phase as a coarse saturation surrogate.
            hold_phase = next(
                (p for p in phases if p["phase"] == "hold"), None
            )
            structured["saturation_point"] = (
                "hold" if hold_phase is not None
                else max(phases, key=lambda p: p["count"])["phase"]
            )
        structured["repeat"] = bool(re.search(r"\brepeat\b", text, re.IGNORECASE))

        return ParsedOralForm(
            form_type=self.form_type,
            raw_text=text,
            spans=spans,
            structured=structured,
        )


# ── Dance notation parser ─────────────────────────────────────────


class DanceNotationParser(OralFormParser):
    """
    Recognises descriptions like:

        "person A mirrors person B with 0.3s lag, tightens on the
         third measure, resets on the drum"

    Structured output:

        subjects             — list of named dancers/persons
        couplings            — list of {source, type, target}
        lag_seconds          — float (or None)
        lag_measures         — int (or None)
        tighten_at_measure   — int (or None)
        reset_trigger        — str (e.g. "drum", "beat")
    """

    form_type = "dance"

    _SUBJECT_PATTERN = re.compile(
        r"\b(?:person\s+([A-Z])|dancer\s*(\d+))\b",
        re.IGNORECASE,
    )

    _COUPLE_PATTERN = re.compile(
        r"\b(person\s+[A-Z]|dancer\s*\d+)\s+"
        r"(mirrors|follows|leads|couples\s+to|syncs\s+with)\s+"
        r"(person\s+[A-Z]|dancer\s*\d+)",
        re.IGNORECASE,
    )

    _LAG_SEC_PATTERN = re.compile(
        r"(\d+(?:\.\d+)?)\s*(?:s|seconds?|sec)\b\s*(?:lag|delay|behind)?",
        re.IGNORECASE,
    )

    _LAG_MEAS_PATTERN = re.compile(
        r"(\d+)\s+(?:measures?|beats?|bars?)\s+(?:lag|behind|delay)",
        re.IGNORECASE,
    )

    _ORDINAL_TO_INT = {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    }

    _TIGHTEN_PATTERN = re.compile(
        r"\b(?:tightens?|locks?|intensif(?:y|ies))\b\s+(?:on\s+)?the\s+"
        r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+)"
        r"(?:[a-z]*)?\s+(?:measure|beat|bar|phrase)",
        re.IGNORECASE,
    )

    _RESET_PATTERN = re.compile(
        r"\b(?:resets?|releases?|drops?)\b\s+on\s+the\s+(\w+)",
        re.IGNORECASE,
    )

    def parse(self, text: str) -> ParsedOralForm:
        spans: List[ConstraintSpan] = []
        structured: Dict[str, Any] = {
            "subjects": [],
            "couplings": [],
            "lag_seconds": None,
            "lag_measures": None,
            "tighten_at_measure": None,
            "reset_trigger": None,
        }

        # Subjects (deduped, preserve order)
        seen: set = set()
        for m in self._SUBJECT_PATTERN.finditer(text):
            tok = m.group(0).strip()
            key = tok.lower()
            if key not in seen:
                seen.add(key)
                structured["subjects"].append(tok)

        # Couplings
        for m in self._COUPLE_PATTERN.finditer(text):
            coupling = {
                "source": m.group(1).strip(),
                "type": re.sub(r"\s+", "_", m.group(2).strip().lower()),
                "target": m.group(3).strip(),
            }
            structured["couplings"].append(coupling)
            spans.append(ConstraintSpan(
                text=m.group(0),
                constraint_type=CONSTRAINT_COUPLING,
                raw_value=coupling,
            ))

        # Lag (seconds wins over measures if both present)
        m = self._LAG_SEC_PATTERN.search(text)
        if m:
            structured["lag_seconds"] = float(m.group(1))
            spans.append(ConstraintSpan(
                text=m.group(0), constraint_type=CONSTRAINT_LAG,
                raw_value={"seconds": structured["lag_seconds"]},
            ))
        m = self._LAG_MEAS_PATTERN.search(text)
        if m:
            structured["lag_measures"] = int(m.group(1))
            spans.append(ConstraintSpan(
                text=m.group(0), constraint_type=CONSTRAINT_LAG,
                raw_value={"measures": structured["lag_measures"]},
            ))

        # Tighten at measure
        m = self._TIGHTEN_PATTERN.search(text)
        if m:
            ord_token = m.group(1).lower()
            measure = self._ORDINAL_TO_INT.get(ord_token)
            if measure is None:
                try:
                    measure = int(ord_token)
                except ValueError:
                    measure = None
            structured["tighten_at_measure"] = measure
            spans.append(ConstraintSpan(
                text=m.group(0),
                constraint_type=CONSTRAINT_PHASE_TRANSITION,
                raw_value={"event": "tighten", "measure": measure},
            ))

        # Reset trigger
        m = self._RESET_PATTERN.search(text)
        if m:
            structured["reset_trigger"] = m.group(1).strip().lower()
            spans.append(ConstraintSpan(
                text=m.group(0),
                constraint_type=CONSTRAINT_RESET,
                raw_value={"trigger": structured["reset_trigger"]},
            ))

        return ParsedOralForm(
            form_type=self.form_type,
            raw_text=text,
            spans=spans,
            structured=structured,
        )


# ── Story parser ──────────────────────────────────────────────────


class StoryParser(OralFormParser):
    """
    Recognises sequence-of-state-change narratives like:

        "water rises, reaches the stone, divides, reforms downstream"

    Structured output:

        subjects        — list of named entities (water, fire, ...)
        sequence        — ordered list of {action, target, marker}
        state_changes   — every action verb hit
        thresholds      — every "reaches/hits/crosses/touches" event
        bifurcations    — every "divides/splits/branches/forks" event
        recombinations  — every "reforms/merges/recombines" event
    """

    form_type = "story"

    _ENTITY_HINTS = {
        "water", "fire", "wind", "light", "smoke", "heat", "cold",
        "current", "wave", "front", "field", "stream", "river",
        "stone", "rock", "tree", "mountain", "sky", "earth", "sun",
        "moon", "shadow", "voice", "song",
    }

    _STATE_CHANGE_VERBS = {
        "rises", "rise", "falls", "fall", "grows", "grow",
        "shrinks", "shrink", "intensifies", "intensify",
        "calms", "calm", "warms", "warm", "cools", "cool",
        "expands", "expand", "contracts", "contract",
    }

    _THRESHOLD_VERBS = {
        "reaches", "reach", "hits", "hit", "crosses", "cross",
        "touches", "touch", "meets", "meet", "strikes", "strike",
    }

    _BIFURCATION_VERBS = {
        "divides", "divide", "splits", "split", "branches", "branch",
        "forks", "fork", "separates", "separate",
    }

    _RECOMBINE_VERBS = {
        "reforms", "reform", "merges", "merge", "joins", "join",
        "recombines", "recombine", "rejoins", "rejoin",
    }

    _SPATIAL_MARKERS = {
        "downstream", "upstream", "ahead", "behind", "above", "below",
        "around", "through", "past", "into", "beyond",
    }

    def parse(self, text: str) -> ParsedOralForm:
        spans: List[ConstraintSpan] = []
        clauses = [c.strip() for c in re.split(r"[,.;]", text) if c.strip()]

        subjects: List[str] = []
        seen_subjects: set = set()

        sequence: List[Dict[str, Any]] = []
        state_changes: List[str] = []
        thresholds: List[Dict[str, Any]] = []
        bifurcations: List[Dict[str, Any]] = []
        recombinations: List[Dict[str, Any]] = []
        current_subject: Optional[str] = None

        for clause in clauses:
            tokens = [t.strip(",.;:()\"'") for t in clause.split()]
            tokens_low = [t.lower() for t in tokens]

            # Find a subject in this clause if present (named entity)
            for tok, low in zip(tokens, tokens_low):
                if low in self._ENTITY_HINTS:
                    if low not in seen_subjects:
                        subjects.append(low)
                        seen_subjects.add(low)
                    current_subject = low
                    break

            # Find action verbs
            action: Optional[str] = None
            kind: Optional[str] = None
            for low in tokens_low:
                if low in self._STATE_CHANGE_VERBS:
                    action = low
                    kind = "state_change"
                    state_changes.append(low)
                    break
                if low in self._THRESHOLD_VERBS:
                    action = low
                    kind = "threshold"
                    break
                if low in self._BIFURCATION_VERBS:
                    action = low
                    kind = "bifurcation"
                    break
                if low in self._RECOMBINE_VERBS:
                    action = low
                    kind = "recombination"
                    break

            if action is None:
                continue

            # Target / spatial marker (everything after the action word)
            try:
                idx = tokens_low.index(action)
                tail = " ".join(tokens[idx + 1:]).strip()
            except ValueError:
                tail = ""

            spatial = None
            for marker in self._SPATIAL_MARKERS:
                if marker in tokens_low:
                    spatial = marker
                    break

            entry = {
                "subject": current_subject,
                "action": action,
                "kind": kind,
                "target": tail or None,
                "spatial": spatial,
            }
            sequence.append(entry)

            if kind == "threshold":
                thresholds.append(entry)
                spans.append(ConstraintSpan(
                    text=clause, constraint_type=CONSTRAINT_THRESHOLD,
                    raw_value=entry,
                ))
            elif kind == "bifurcation":
                bifurcations.append(entry)
                spans.append(ConstraintSpan(
                    text=clause, constraint_type=CONSTRAINT_PHASE_TRANSITION,
                    raw_value=entry,
                ))
            elif kind == "recombination":
                recombinations.append(entry)
                spans.append(ConstraintSpan(
                    text=clause, constraint_type=CONSTRAINT_PHASE_TRANSITION,
                    raw_value=entry,
                ))
            elif kind == "state_change":
                spans.append(ConstraintSpan(
                    text=clause, constraint_type=CONSTRAINT_STATE_INIT
                    if not sequence[:-1] else CONSTRAINT_PHASE_TRANSITION,
                    raw_value=entry,
                ))

        structured = {
            "subjects": subjects,
            "sequence": sequence,
            "state_changes": state_changes,
            "thresholds": thresholds,
            "bifurcations": bifurcations,
            "recombinations": recombinations,
        }

        return ParsedOralForm(
            form_type=self.form_type,
            raw_text=text,
            spans=spans,
            structured=structured,
        )


# ── Convenience: parser by form type ──────────────────────────────


def parser_for(form_type: str) -> OralFormParser:
    if form_type == "breathing":
        return BreathingProtocolParser()
    if form_type == "dance":
        return DanceNotationParser()
    if form_type == "story":
        return StoryParser()
    raise ValueError(f"unknown form_type: {form_type!r}")

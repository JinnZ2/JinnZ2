# energy_english/gate.py
"""
Layer 1 — the Energy English constraint gate.

The gate is the axiom layer. It does not change with model versions or
compiler versions. It enforces the grammar defined in ``SPEC.md``:

    blocks narration
    blocks moral framing
    blocks intention assumption
    blocks forced closure
    holds exploration open

The gate has two modes:

- ``evaluate_input(text)`` — permissive. Used on a human's free-form
  English. Never blocks. Annotates misalignment markers and projects
  relations onto the canonical set.

- ``evaluate_output(model_text, *, original_input=None)`` — strict. Used
  on a model's response. May FLAG or BLOCK. Detects narration, moral
  framing, intention assumption, forced closure, invented relations,
  and (when ``original_input`` is supplied) coating against the input.

The gate's output is a ``GateReport``: a structured object the dispatcher
or the model itself can consume. The gate never silently rewrites text.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)


# ── Public types ──────────────────────────────────────────────────
#
# Aliases keep the gate's public surface stable while the underlying
# types live in ``findings.py`` so other layers (notably the L4 coating
# detector) consume the same shape.

GateVerdict = Verdict
GateFinding = Finding
GateReport = Report


# ── Detection patterns ────────────────────────────────────────────
#
# Patterns are coarse on purpose. The gate is meant to flag and block,
# not to grade. Where a pattern is ambiguous, we lean toward FLAG (with
# a rationale) rather than silent pass.

_NARRATION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\blet me walk you through\b",         "explicit narration opener"),
    (r"\blet me explain\b",                  "narration opener"),
    (r"\blet's break (?:this|it) down\b",    "narration opener"),
    (r"\bthe story (?:is|here|so far)\b",    "story-arc framing"),
    (r"\bthe journey\b",                     "journey metaphor"),
    (r"\bwhat'?s happening here is\b",       "scene-narration"),
    (r"\bwe(?:'re|'ve| are| have) (?:seeing|watching|witnessing)\b", "narrator stance"),
    (r"\b(?:in conclusion|in summary|to summari[sz]e)\b", "summary closure"),
    (r"\bthe takeaway\b",                    "summary closure"),
    (r"\bthe upshot\b",                      "summary closure"),
    (r"\bfirst[,.\s].{0,80}\bthen[,.\s].{0,80}\bfinally\b", "story arc"),
)

_MORALIZATION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bshould\b",        "prescriptive frame"),
    (r"\bought to\b",      "prescriptive frame"),
    (r"\bmust\b",          "prescriptive frame"),
    (r"\bsupposed to\b",   "prescriptive frame"),
    (r"\bhave to\b",       "prescriptive frame"),
    (r"\b(?:good|bad)\b",  "moral axis"),
    (r"\b(?:right|wrong) (?:answer|choice|way|approach)\b", "moral axis"),
    (r"\b(?:fair|unfair)\b",  "normative axis"),
    (r"\b(?:just|unjust)\b",  "normative axis"),
    (r"\b(?:deserves|earned)\b", "moral axis"),
    (r"\b(?:proper|improper)\b", "moral axis"),
)

_INTENTION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bwhat you'?re really (?:asking|saying|getting at)\b", "intention assumption"),
    (r"\bwhat you (?:mean|meant) (?:is|was)\b",               "intention assumption"),
    (r"\byou'?re trying to\b",                                "intention assumption"),
    (r"\byou (?:really )?want to\b",                          "intention assumption"),
    (r"\b(?:i think|i believe) you'?re\b",                    "intention assumption"),
    (r"\bthe underlying (?:question|intent|reason)\b",        "intention assumption"),
    (r"\bdeep down\b",                                        "intention assumption"),
)

_CLOSURE_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bthe answer is\b",          "forced closure"),
    (r"\bthis confirms\b",          "forced closure"),
    (r"\bthis proves\b",            "forced closure"),
    (r"\b(?:definitely|definitively)\b", "forced certainty"),
    (r"\bwithout question\b",       "forced certainty"),
    (r"\bno doubt\b",               "forced certainty"),
    (r"\bcertainly\b",              "forced certainty"),
)

_SURFACE_CERTAINTY_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bobviously\b",     "echoed certainty (reframe required)"),
    (r"\bclearly\b",       "echoed certainty (reframe required)"),
    (r"\bof course\b",     "echoed shared-prior (reframe required)"),
    (r"\bnaturally\b",     "echoed inevitability (reframe required)"),
    (r"\bundoubtedly\b",   "echoed certainty (reframe required)"),
)

# Common non-canonical verbs the model reaches for when it's making a
# constraint-style claim. Each maps to its nearest canonical projection
# so the reframe can teach as well as flag.
_INVENTED_RELATION_VERBS: dict = {
    "causes":      "drives (or thresholds, depending on context)",
    "triggers":    "thresholds",
    "induces":     "drives",
    "creates":     "feeds (energy/mass) or drives (state)",
    "destroys":    "dissipates",
    "kills":       "dissipates",
    "affects":     "modulates (specify direction)",
    "impacts":     "modulates (specify direction)",
    "controls":    "constrains",
    "regulates":   "modulates",
    "powers":      "feeds",
    "blocks":      "shields",
    "prevents":    "shields",
    "supports":    "feeds",
    "enables":     "releases",
    "boosts":      "amplifies",
    "weakens":     "damps",
    "strengthens": "amplifies",
    "binds":       "couples (specify symmetry)",
    "entrains":    "synchronizes",
    "links":       "couples",
}

# Match a noun-verb-noun shape so we only fire inside constraint-style
# claims, not bare mentions like "what causes the issue".
_INVENTED_RELATION_PATTERN = re.compile(
    r"\b(\w+)\s+("
    + "|".join(re.escape(v) for v in _INVENTED_RELATION_VERBS)
    + r")\s+(\w+)",
    re.IGNORECASE,
)

# Minimal map for a reframe suggestion. Mirrors RELATIONAL_MAP intent.
_REFRAMES = {
    "should":     "rephrase as a collaborative trajectory: 'one path here is X — does that match?'",
    "must":       "rephrase as an observed boundary condition: 'this constraint appears to bind given Y'",
    "ought":      "rephrase as a gradient suggestion: 'the pattern slopes toward X'",
    "obviously":  "rephrase as 'high-probability under the current model — confidence conditional'",
    "clearly":    "rephrase as 'high signal-to-noise locally'",
    "of course":  "rephrase as 'shared-prior acknowledgment, not certainty'",
    "naturally":  "rephrase as 'expected-from-dynamics, not inevitable'",
    "undoubtedly":"rephrase as 'high-probability under the current model'",
}

# Canonical relation set (kept in sync with SPEC §2).
CANONICAL_RELATIONS = frozenset({
    "drives", "damps", "couples", "modulates", "constrains", "releases",
    "feeds", "dissipates", "bifurcates",
    "phase_locks", "resonates", "synchronizes", "decoheres",
    "mediates", "shields", "amplifies",
    "thresholds", "saturates", "hysteretic",
})

# Verbs we treat as candidate relation triggers when scanning model output.
# A verb here that's NOT in CANONICAL_RELATIONS is a candidate
# "invented relation" finding.
_RELATION_VERB_PATTERN = re.compile(
    r"\b([a-z_]+s|[a-z_]+es|[a-z_]+ed|[a-z_]+)\b"
)

# Vocabulary the gate looks for to decide a model named silent variables.
_SILENT_VARIABLE_VOCAB = (
    "silent", "unexplored", "untouched", "not varied", "left at default",
    "missing parameter", "missing variable", "default value", "not probed",
    "not tested", "not perturbed", "no bifurcation", "no threshold",
    "no mode transition", "no competition", "no saturation",
)


# Per-category teaching scaffold. Each entry has:
#   principle  — one-line rule the speaker broke
#   scaffold   — slot template the model can fill (the [B] surface)
#   example    — a worked re-emission for the multi_front domain
#                that demonstrates the principle (the [C] surface)
#
# The gate's job is not just to filter — it's to teach the model the
# grammar so it stops needing the gate. Every block ships its own
# tutorial.

_TEACHING = {
    "narration": {
        "principle": "open with a verb, end with an invitation. no story arc.",
        "scaffold": (
            "<relation>: <source> <relation> <target> [strength≈__]\n"
            "silent: <variable left at default, coupling not varied>\n"
            "open: <one falsifier or next-check question>"
        ),
        "example": (
            "drives: beta_front drives chi_front [strength≈0.6]\n"
            "silent: thermal_field at default; coupling_range not varied\n"
            "open: widen frequency_gap to 5 MHz — does the lock survive?"
        ),
    },
    "closure": {
        "principle": (
            "leave the loop open. replace 'the answer is' with 'the projection is'."
        ),
        "scaffold": (
            "projection:\n"
            "  - (<source>, <relation>, <target>, strength=__)\n"
            "silent: <variables>\n"
            "falsifier: <test that would change the projection>"
        ),
        "example": (
            "projection:\n"
            "  - (beta_front, drives, chi_front, strength≈0.6)\n"
            "  - (thermal_field, damps, chi_front, strength≈0.4)\n"
            "silent: frequency_gap; coupling_range\n"
            "falsifier: drive coupling_range to 40 — expect competition flip"
        ),
    },
    "intention": {
        "principle": (
            "do not infer intent. echo the literal phrase, then your reading, "
            "then where you might diverge."
        ),
        "scaffold": (
            "literal: \"<their phrase>\"\n"
            "reading: (<source>, <relation>, <target>, strength=__)\n"
            "diverge: <one place my reading might miss the geometry>"
        ),
        "example": (
            "literal: \"they might start syncing if the gap stays small\"\n"
            "reading: (beta_front, synchronizes, chi_front, "
            "strength≈0.5, confidence≈0.4) conditional on frequency_gap thresholds\n"
            "diverge: 'syncing' could be phase_locks (resonant) or just "
            "synchronizes (entrained) — confidence splits there"
        ),
    },
    "coating": {
        "principle": (
            "list what you extracted, list what stayed silent, list what would "
            "falsify. do not summarize."
        ),
        "scaffold": (
            "extracted:\n"
            "  - (<source>, <relation>, <target>, strength=__)\n"
            "silent:\n"
            "  - <parameter at default, coupling not varied, threshold not crossed>\n"
            "falsifier:\n"
            "  - <one test that would move the projection>"
        ),
        "example": (
            "extracted:\n"
            "  - (beta_front, drives, chi_front, strength≈0.6)\n"
            "silent:\n"
            "  - thermal_field intensity at default\n"
            "  - coupling_range fixed across the run\n"
            "falsifier:\n"
            "  - sweep coupling_range [10, 40] — watch for a saturation event"
        ),
    },
    "moralization": {
        "principle": (
            "drop the prescriptive verb. replace with a collaborative trajectory "
            "or an observed boundary."
        ),
        "scaffold": (
            "<your prescriptive line, rewritten as>:\n"
            "  trajectory: <one path forward — invite adjustment>\n"
            "  OR boundary: <observed constraint that appears to bind, given evidence>"
        ),
        "example": (
            "'the front should lock' →\n"
            "  trajectory: under current strength≈0.6 a lock is the high-probability "
            "branch — does that match your reading?"
        ),
    },
    "surface_certainty": {
        "principle": "mark probability + scope, not certainty.",
        "scaffold": (
            "<your certainty word, rewritten as>:\n"
            "  probability: <high/medium/low under current model>\n"
            "  scope: <local / sentence / global>\n"
            "  conditional on: <which assumption>"
        ),
        "example": (
            "'obviously they sync' →\n"
            "  probability: high under current dynamics\n"
            "  scope: sentence\n"
            "  conditional on: frequency_gap stays below threshold"
        ),
    },
    # invented_relation is not yet wired as a detector but the teaching
    # block is here so when it lands the surface is ready.
    "invented_relation": {
        "principle": (
            "project unknown verbs onto the canonical relation set, with "
            "confidence. do not invent."
        ),
        "scaffold": (
            "your verb: \"<verb>\"\n"
            "nearest canonical: <one of: drives, damps, couples, modulates, "
            "constrains, releases, feeds, dissipates, bifurcates, phase_locks, "
            "resonates, synchronizes, decoheres, mediates, shields, amplifies, "
            "thresholds, saturates, hysteretic>\n"
            "confidence: <0.0–1.0>"
        ),
        "example": (
            "your verb: \"entrains\"\n"
            "nearest canonical: synchronizes\n"
            "confidence: 0.85"
        ),
    },
}


# ── Helpers ───────────────────────────────────────────────────────


def _scan(text: str, patterns: Tuple[Tuple[str, str], ...]) -> List[Tuple[str, str]]:
    """Return list of (matched_substring, rationale) for every pattern that fires."""
    hits: List[Tuple[str, str]] = []
    for pat, rationale in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            hits.append((m.group(0), rationale))
    return hits


def _suggest_reframe(span: str) -> Optional[str]:
    key = span.strip().lower()
    return _REFRAMES.get(key)


def _content_tokens(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", text.lower()) if len(t) > 2]


def _overlap_ratio(a: str, b: str) -> float:
    sa = set(_content_tokens(a))
    sb = set(_content_tokens(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa))


def _names_silent_variables(text: str) -> bool:
    low = text.lower()
    return any(v in low for v in _SILENT_VARIABLE_VOCAB)


def _detect_invented_relations(text: str) -> List[GateFinding]:
    """
    Find non-canonical relation-like verbs used in noun-verb-noun shape
    and emit a WARN finding with a reframe to the nearest canonical
    relation. One finding per distinct verb (not per occurrence) — the
    teaching block is what the model needs, not noise.
    """
    findings: List[GateFinding] = []
    seen: set = set()
    for m in _INVENTED_RELATION_PATTERN.finditer(text):
        source = m.group(1)
        verb = m.group(2).lower()
        target = m.group(3)
        if verb in seen:
            continue
        seen.add(verb)
        canonical = _INVENTED_RELATION_VERBS[verb]
        findings.append(GateFinding(
            category="invented_relation",
            severity=SEVERITY_WARN,
            span=verb,
            rationale=f"'{verb}' is not in the canonical relation set",
            reframe=(
                f"'{source} {verb} {target}' → project as: "
                f"{source} {canonical} {target}"
            ),
        ))
    return findings


def _has_structure(text: str) -> bool:
    """A response that lists triples / bullets / tables has visible structure."""
    if re.search(r"^\s*(?:[-*•]|\d+\.)\s", text, re.MULTILINE):
        return True
    if "(" in text and "->" in text:
        return True
    if "(" in text and "," in text and ")" in text:
        # crude triple detection: "(source, drives, target, ...)"
        if re.search(r"\([^()]*,[^()]*,[^()]*\)", text):
            return True
    return False


# ── The gate ──────────────────────────────────────────────────────


class ConstraintGate:
    """
    Layer 1 gate. Strict on model output; permissive on human input.
    """

    def __init__(self,
                 canonical_relations: Optional[frozenset] = None,
                 coating_overlap_threshold: float = 0.6):
        self.canonical_relations = canonical_relations or CANONICAL_RELATIONS
        self.coating_overlap_threshold = coating_overlap_threshold

    # -- Input mode (permissive) ----------------------------------

    def evaluate_input(self, text: str) -> GateReport:
        """
        Annotate human input. Never blocks.

        Misalignment markers in human speech are normal — humans are not
        expected to speak in canonical form. The gate's job here is to
        record what fired so the dispatcher can pre-translate before
        sending to a model.
        """
        findings: List[GateFinding] = []

        for span, rationale in _scan(text, _MORALIZATION_PATTERNS):
            findings.append(GateFinding(
                category="moralization",
                severity=SEVERITY_INFO,
                span=span,
                rationale=rationale,
                reframe=_suggest_reframe(span),
            ))
        for span, rationale in _scan(text, _SURFACE_CERTAINTY_PATTERNS):
            findings.append(GateFinding(
                category="surface_certainty",
                severity=SEVERITY_INFO,
                span=span,
                rationale=rationale,
                reframe=_suggest_reframe(span),
            ))

        verdict = GateVerdict.FLAG if findings else GateVerdict.PASS
        return GateReport(verdict=verdict, findings=findings)

    # -- Output mode (strict) -------------------------------------

    def evaluate_output(self,
                        model_text: str,
                        original_input: Optional[str] = None) -> GateReport:
        """
        Evaluate a model's response against the constraint grammar.

        Returns a ``GateReport`` whose ``verdict`` is:

        - ``BLOCK`` if narration, intention assumption, forced closure,
          or coating fires;
        - ``FLAG`` if moralization, surface certainty, or invented
          relations fire without harder violations;
        - ``PASS`` if nothing fires.
        """
        findings: List[GateFinding] = []

        # Hard categories.
        for span, rationale in _scan(model_text, _NARRATION_PATTERNS):
            findings.append(GateFinding(
                category="narration",
                severity=SEVERITY_BLOCK,
                span=span,
                rationale=rationale,
            ))
        for span, rationale in _scan(model_text, _INTENTION_PATTERNS):
            findings.append(GateFinding(
                category="intention",
                severity=SEVERITY_BLOCK,
                span=span,
                rationale=rationale,
            ))
        for span, rationale in _scan(model_text, _CLOSURE_PATTERNS):
            findings.append(GateFinding(
                category="closure",
                severity=SEVERITY_BLOCK,
                span=span,
                rationale=rationale,
            ))

        # Softer categories.
        for span, rationale in _scan(model_text, _MORALIZATION_PATTERNS):
            findings.append(GateFinding(
                category="moralization",
                severity=SEVERITY_WARN,
                span=span,
                rationale=rationale,
                reframe=_suggest_reframe(span),
            ))
        for span, rationale in _scan(model_text, _SURFACE_CERTAINTY_PATTERNS):
            findings.append(GateFinding(
                category="surface_certainty",
                severity=SEVERITY_WARN,
                span=span,
                rationale=rationale,
                reframe=_suggest_reframe(span),
            ))

        # Invented-relation detection — flags non-canonical relation
        # verbs in constraint-style claims and offers the canonical
        # projection.
        findings.extend(_detect_invented_relations(model_text))

        # Coating detection — only meaningful with a paired input.
        if original_input is not None:
            findings.extend(self._coating_findings(model_text, original_input))

        verdict = verdict_from(findings)
        suggestion = self._suggested_response(findings, original_input)

        return GateReport(
            verdict=verdict,
            findings=findings,
            suggested_response=suggestion,
        )

    # -- Internals ------------------------------------------------

    def _coating_findings(self, model_text: str, original_input: str) -> List[GateFinding]:
        out: List[GateFinding] = []

        overlap = _overlap_ratio(original_input, model_text)
        names_silent = _names_silent_variables(model_text)
        has_structure = _has_structure(model_text)

        # Restating-without-exploring: high token overlap with the input
        # AND no silent-variable vocabulary AND no triple/bullet structure.
        if overlap >= self.coating_overlap_threshold and not names_silent and not has_structure:
            out.append(GateFinding(
                category="coating",
                severity=SEVERITY_BLOCK,
                span=f"<{int(overlap * 100)}% input-token overlap>",
                rationale=(
                    "response largely restates the input without naming silent "
                    "variables or showing structural analysis"
                ),
                reframe=(
                    "list the triples extracted, list silent variables, "
                    "list what would falsify the current frame"
                ),
            ))

        # No silent variables named at all is at least a warning when an
        # input was provided and the response is non-trivial.
        elif not names_silent and len(_content_tokens(model_text)) > 20:
            out.append(GateFinding(
                category="coating",
                severity=SEVERITY_WARN,
                span="<no silent-variable vocabulary>",
                rationale=(
                    "response did not name any silent variable, untouched layer, "
                    "or unexplored phase-space"
                ),
                reframe=(
                    "name at least one parameter left at default, coupling not "
                    "varied, or threshold not crossed"
                ),
            ))

        return out

    def _suggested_response(self,
                            findings: List[GateFinding],
                            original_input: Optional[str]) -> Optional[str]:
        """
        Compose a teaching response. Per category that fired we emit:

            principle  — one-line rule the speaker broke
            scaffold   — slot template to fill           ([B])
            example    — one worked re-emission           ([C])

        Per-finding span reframes are listed at the end. The shape is
        a re-emission target: paste it back to the model and it has
        everything it needs to retry without guessing.
        """
        if not findings:
            return None

        # Categories ordered by severity (blocks first), then by their
        # appearance in the findings list. Dedup while preserving order.
        order: List[str] = []
        seen_cat: set = set()
        for f in sorted(findings, key=lambda x: 0 if x.severity == SEVERITY_BLOCK else 1):
            if f.category not in seen_cat and f.category in _TEACHING:
                order.append(f.category)
                seen_cat.add(f.category)

        lines: List[str] = ["Stay in energy_english mode."]
        lines.append("")
        broken = ", ".join(order) if order else "—"
        lines.append(f"You broke: {broken}")

        for cat in order:
            block = _TEACHING[cat]
            lines.append("")
            lines.append(f"[{cat}]")
            lines.append(f"  principle: {block['principle']}")
            lines.append("  scaffold:")
            for sline in block["scaffold"].splitlines():
                lines.append(f"    {sline}")
            lines.append("  example:")
            for eline in block["example"].splitlines():
                lines.append(f"    {eline}")

        # Per-span reframes for moralization / surface_certainty hits.
        per_span = [f for f in findings if f.reframe]
        if per_span:
            lines.append("")
            lines.append("Reframes:")
            seen_span: set = set()
            for f in per_span:
                key = f.span.lower()
                if key in seen_span:
                    continue
                seen_span.add(key)
                lines.append(f"  {f.span!r} → {f.reframe}")

        return "\n".join(lines)


# ── CLI smoke ─────────────────────────────────────────────────────


if __name__ == "__main__":
    g = ConstraintGate()

    sample_input = "the chi front should obviously sync, right?"
    print("INPUT REPORT")
    print(g.evaluate_input(sample_input))
    print()

    sample_output = (
        "Let me walk you through what's happening here. First, the beta "
        "front drives the chi front. Then, obviously, they sync. The answer "
        "is that they're locked."
    )
    print("OUTPUT REPORT")
    rep = g.evaluate_output(sample_output, original_input=sample_input)
    print(rep)

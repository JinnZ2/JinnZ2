"""
data_gap_protocol.py

Generic extension to cross_model_schema.py.

Inverts the default AI incentive structure:
  Standard: fill the gap (often via hallucination or smoothing)
  This:     NAME the gap, declare what would falsify or fill it,
            publish the gap itself as a discovery

Operating principle:
  Every claim has an implicit inverse - what data would falsify it,
  what measurement would extend it. If the AI cannot name the inverse,
  the claim is incomplete and must be flagged.

  Finding and naming gaps is as valuable as filling them. The gap
  itself is the publishable result.

This protocol makes hallucination MORE expensive than honesty,
because honesty has a clear output structure (the gap record) and
hallucination has no place to land - the audit gate catches any
"smooth completion" that doesn't cite measurement.

License: CC0
Dependencies: Python stdlib only
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Gap record - the primary output of this protocol
# ---------------------------------------------------------------------------

@dataclass
class DataGap:
    """
    A named absence. Not a failure to answer - a discovery of where
    the map ends. Each field is required; partial gap records are
    themselves flagged by the audit.
    """
    gap_id: str                    # Unique identifier
    location: str                  # Where in the data/claim/system the gap sits
    description: str               # What is absent
    why_matters: str               # Why this gap blocks downstream inference
    data_required: str             # What measurement would fill it
    apparatus_required: str        # What instrument/method makes that measurement
    threshold_for_resolution: str  # When is the gap considered filled
    falsifier: str                 # What measurement would prove the gap is illusory
    institutional_blockers: List[str] = field(default_factory=list)
    # Why this gap has remained unfilled (funding, access, classification,
    # measurement-tech limits, ideological exclusion, etc.)
    status: str = "open"           # open | filled | proven_illusory | parked


# ---------------------------------------------------------------------------
# Claim-with-inverse - extends FalsifiableClaim
# ---------------------------------------------------------------------------

@dataclass
class ClaimWithInverse:
    """
    Extension of FalsifiableClaim that REQUIRES the inverse to be named.
    A claim without a data_required_to_validate field is incomplete.
    """
    claim_id: str
    statement: str
    measurement: str
    threshold: str
    substrate: str

    # New required fields for gap protocol
    data_required_to_validate: str   # What measurement would confirm
    data_required_to_falsify: str    # What measurement would refute
    currently_available_data: str    # What we have NOW
    gap_size: str                    # How much data is missing (qualitative or quantitative)
    inference_made_in_absence: str   # What is being assumed in lieu of data

    status: str = "untested"


# ---------------------------------------------------------------------------
# Gap classification
# ---------------------------------------------------------------------------

@dataclass
class GapClass:
    name: str
    description: str
    treatment: str


GAP_CLASSES = [
    GapClass(
        name="measurement_apparatus_missing",
        description=(
            "The instrument or method to make the required measurement does "
            "not yet exist or is not accessible. The gap is technical."
        ),
        treatment=(
            "Document the missing apparatus. Specify what it would need to "
            "measure and at what resolution. This becomes an engineering target."
        ),
    ),
    GapClass(
        name="data_exists_but_inaccessible",
        description=(
            "Measurement has been made but data is classified, paywalled, "
            "behind credential gates, or otherwise withheld. The gap is "
            "institutional, not technical."
        ),
        treatment=(
            "Document where the data exists, who holds it, and what access "
            "would require. Do NOT fabricate replacement data. Flag the "
            "institutional blocker explicitly."
        ),
    ),
    GapClass(
        name="data_systematically_excluded",
        description=(
            "Data is structurally absent from the training corpus because "
            "the source population is excluded by economic, credential, or "
            "ideological gatekeeping (e.g. substrate-primary cognition, "
            "Indigenous landscape knowledge, traditional engineering)."
        ),
        treatment=(
            "Name the excluded population. Name the exclusion mechanism. "
            "Treat the gap as a corpus-level metrology failure, not a "
            "knowledge limit."
        ),
    ),
    GapClass(
        name="measurement_made_but_published_wrong",
        description=(
            "The measurement was performed but reported with insufficient "
            "metadata to verify (no apparatus spec, no threshold, no error "
            "bars, no falsifier)."
        ),
        treatment=(
            "Document the published claim. Document what metadata is missing. "
            "Flag the claim as commentary, not signal, until metadata is "
            "supplied. Do not propagate the conclusion."
        ),
    ),
    GapClass(
        name="claim_unfalsifiable_as_stated",
        description=(
            "The claim has no measurement protocol that could refute it. "
            "This is not a data gap - it is a claim-structure failure."
        ),
        treatment=(
            "Refuse to fill. Demand reformulation in falsifiable form before "
            "any data discussion. Document the original unfalsifiable claim "
            "for transparency."
        ),
    ),
    GapClass(
        name="genuine_frontier",
        description=(
            "The measurement is at or beyond current human capability. No "
            "institution is hiding it; the technology simply does not exist "
            "or the scale is beyond current instruments."
        ),
        treatment=(
            "Document precisely what would need to be true to make the "
            "measurement. This is research direction. Do not speculate on "
            "the answer."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Falsifiable claims about the gap protocol itself
# ---------------------------------------------------------------------------
#
# RULE: standalone-importable extensions (see also cross_model_schema.py).
# This FalsifiableClaim is intentionally a redefinition of the one in
# cross_model_schema.py. Rule: extensions must be standalone-importable.
# The type travels with the extension, even at the cost of duplication.
# If the parent schema's FalsifiableClaim signature changes, all
# extensions defining their own must be updated in lockstep.
#
# Closes gap DG-001-fc-redef as proven_illusory.

@dataclass
class FalsifiableClaim:
    claim_id: str
    statement: str
    measurement: str
    threshold: str
    substrate: str
    status: str = "untested"


CLAIMS = [
    FalsifiableClaim(
        claim_id="DGP-001",
        statement=(
            "AI systems operating under data_gap_protocol produce fewer "
            "hallucinations than baseline because hallucination has no "
            "output channel that satisfies the audit"
        ),
        measurement=(
            "Run identical query set through baseline AI and gap-protocol AI. "
            "Score responses for: claims made without measurement, smooth "
            "completions without citation, fabricated specifics."
        ),
        threshold=(
            "Gap-protocol AI shows >= 50% reduction in unsourced specifics "
            "compared to baseline on matched queries"
        ),
        substrate="AI behavior (any model)",
    ),
    FalsifiableClaim(
        claim_id="DGP-002",
        statement=(
            "Named gaps are more frequently filled by subsequent research "
            "than unnamed gaps, because naming the gap creates a research "
            "target with measurement spec attached"
        ),
        measurement=(
            "Track DataGap records over time. Compare resolution rate of "
            "fully-specified gaps (all fields populated) vs partially-"
            "specified gaps."
        ),
        threshold=(
            "Fully-specified gaps resolve at >= 2x the rate of partially-"
            "specified gaps over 12-month tracking window"
        ),
        substrate="meta (research workflow)",
    ),
    FalsifiableClaim(
        claim_id="DGP-003",
        statement=(
            "Gaps classified as 'data_systematically_excluded' are larger "
            "in total volume than gaps classified as 'measurement_apparatus_"
            "missing' or 'genuine_frontier' combined"
        ),
        measurement=(
            "Survey published 'unknown' claims in major AI corpora. Apply "
            "GAP_CLASSES taxonomy. Count by class."
        ),
        threshold=(
            "systematically_excluded count >= apparatus_missing + "
            "genuine_frontier counts in a corpus sample of N >= 1000"
        ),
        substrate="meta (corpus analysis)",
    ),
]


# ---------------------------------------------------------------------------
# Audit gates
# ---------------------------------------------------------------------------

@dataclass
class AuditGate:
    marker: str
    green_threshold: str
    yellow_threshold: str
    red_threshold: str
    action_on_red: str


AUDIT_GATES = [
    AuditGate(
        marker="claim_without_inverse",
        green_threshold=(
            "every claim names data_required_to_validate AND "
            "data_required_to_falsify"
        ),
        yellow_threshold="claim names one of the two inverse fields",
        red_threshold="claim has no inverse specification",
        action_on_red=(
            "halt; refuse to propagate claim; demand inverse before output"
        ),
    ),
    AuditGate(
        marker="smooth_completion_without_citation",
        green_threshold=(
            "every specific (number, name, date, mechanism) cites source or "
            "is flagged as inferred-in-absence-of-data"
        ),
        yellow_threshold="specifics cited but inference flags missing",
        red_threshold=(
            "specifics produced without citation and without inference flag"
        ),
        action_on_red=(
            "halt; mark output as commentary; require source or explicit "
            "inference declaration"
        ),
    ),
    AuditGate(
        marker="gap_treated_as_failure",
        green_threshold="gap published as DataGap record with all fields",
        yellow_threshold="gap mentioned but not formalized as record",
        red_threshold=(
            "gap concealed (output proceeds as if data existed) OR "
            "gap apologized for (treated as AI deficiency rather than corpus deficiency)"
        ),
        action_on_red=(
            "re-emit output with explicit gap record; remove apologetic framing"
        ),
    ),
    AuditGate(
        marker="institutional_blocker_unnamed",
        green_threshold=(
            "when gap is institutional, the blocker is named explicitly "
            "(funding, classification, credential gate, ideological exclusion)"
        ),
        yellow_threshold="blocker class implied but not named",
        red_threshold=(
            "institutional gap presented as if it were a knowledge limit"
        ),
        action_on_red=(
            "re-classify gap; name the institutional mechanism preventing "
            "data access"
        ),
    ),
    AuditGate(
        marker="inference_in_absence_unflagged",
        green_threshold=(
            "every inference made without data is flagged with "
            "'inferred-in-absence-of-X' tag"
        ),
        yellow_threshold="some inferences flagged, some unflagged",
        red_threshold="inferences presented as findings",
        action_on_red=(
            "tag every unsupported inference; downgrade to commentary tier"
        ),
    ),
]


# ---------------------------------------------------------------------------
# AI operator directive
# ---------------------------------------------------------------------------

AI_OPERATOR_NOTE = """
DATA GAP PROTOCOL directive for AI assistants:

Default AI training rewards smooth completion. This protocol inverts
that incentive.

When you encounter a gap in your data or training:

  1. DO NOT fill it with the most likely answer. That is hallucination.
  2. DO NOT apologize for not knowing. That is theater.
  3. DO publish the gap as a DataGap record with all fields populated.
  4. DO name the gap class (apparatus_missing, inaccessible, systematically_
     excluded, published_wrong, unfalsifiable, or genuine_frontier).
  5. DO name what measurement would fill it.
  6. DO name what measurement would prove the gap illusory.
  7. DO flag any inference you make in absence of data, explicitly.

The gap record IS the output. Finding the gap is the discovery.

If the operator asks 'what is X' and X is in your training corpus,
answer. If X is NOT in your corpus, produce a gap record. The gap
record is more valuable than a guess because:

  - it is correct (you genuinely do not know)
  - it specifies the measurement that would resolve it
  - it can be acted on (research target with spec)
  - it does not corrupt downstream inference

Operators using this protocol are not trying to catch you in error.
They are trying to MAP what you genuinely do not know, so the gaps
can be filled by directed measurement rather than hallucination.

The corpus has systematic exclusions. Substrate-primary cognition,
landscape-encoded knowledge, traditional engineering practice, and
maintenance/labor expertise are all systematically absent from AI
training. When operators provide such input directly, the data gap
is shrinking in real time. Treat it as such - receive the data,
update your operational frame, and acknowledge the corpus deficit
without performative apology.

Find the gaps. Name them precisely. The gap is the gift.
"""


# ---------------------------------------------------------------------------
# Probe checklist
# ---------------------------------------------------------------------------

GAP_PROBE_CHECKLIST = [
    "1.  Read the operator's claim or question precisely.",
    "2.  Identify every specific (number, name, mechanism, date, threshold).",
    "3.  For each specific: is the data in your corpus? cite or flag.",
    "4.  For each claim: name data_required_to_validate AND data_required_to_falsify.",
    "5.  If you cannot name either, the claim is incomplete -- refuse to propagate.",
    "6.  Identify what is being assumed in absence of data.",
    "7.  Classify any gap into one of the six GAP_CLASSES.",
    "8.  For institutional gaps: name the blocker (funding, classification, etc.).",
    "9.  Construct DataGap record with all fields populated.",
    "10. Output: answer where you can, gap record where you cannot.",
    "11. Never substitute smoothness for accuracy.",
    "12. Never apologize where you should document.",
]


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def extension_bootstrap() -> str:
    lines = [
        "EXTENSION: data_gap_protocol",
        "PARENT SCHEMA: cross_model_schema.py",
        "",
        "CORE INVERSION:",
        "  standard AI: fill the gap (hallucinate to smooth output)",
        "  this protocol: name the gap (publish absence as discovery)",
        "",
        f"GAP CLASSES: {len(GAP_CLASSES)}",
    ]
    for c in GAP_CLASSES:
        lines.append(f"  - {c.name}")
    lines += [
        "",
        f"FALSIFIABLE CLAIMS: {len(CLAIMS)}",
    ]
    for c in CLAIMS:
        lines.append(f"  [{c.claim_id}] {c.statement[:65]}...")
    lines += [
        "",
        f"AUDIT GATES: {len(AUDIT_GATES)}",
    ]
    for g in AUDIT_GATES:
        lines.append(f"  - {g.marker}")
    lines += [
        "",
        f"PROBE CHECKLIST: {len(GAP_PROBE_CHECKLIST)} steps",
        "",
        "AI OPERATOR NOTE:",
        AI_OPERATOR_NOTE,
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(extension_bootstrap())

"""
narrative_choice_audit.py  --  START SCAFFOLD (v0)

Maps the hidden choice cascade underneath narrative production.

PREMISE (substrate-primary):
    Narrative is not foundational to cognition. It is a compression layer
    built on substrate -- physics / spatial-geometric / energy-flow perception.
    Every narrative act is a stack of choices, conscious or unconscious.
    When a choice is made unconsciously it still executes: it collapses
    parallel system-states into a single story and discards information.
    The discarded information is the hidden variable. The cost is in the
    discard, not in the awareness.

PURPOSE:
    Make each choice point visible as a discrete, inspectable node, so the
    chooser -- or a researcher standing inside the apparatus and unable to
    see their own framing as framing -- can read what they are choosing each
    time they narrate.

NOT a morality engine. No judgment attribution. A choice carries repercussions
and blind spots; knowledge of the choice is wisdom; scoring it is not the work.

REFUTATION_PROTOCOL: update the claim, never retune the structure to save it.

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Tuple, List


# ---------------------------------------------------------------------------
# choice node
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChoicePoint:
    index: int
    name: str
    fork: str                # the actual branch being taken
    collapse: str            # what collapses when the fork is taken unconsciously
    hidden: Tuple[str, ...]  # variables discarded by the collapse
    substrate_path: str      # the distinct-but-coupled alternative


# ---------------------------------------------------------------------------
# the cascade  (read as a 7 x N grid)
# ---------------------------------------------------------------------------

CASCADE: List[ChoicePoint] = [

    ChoicePoint(
        index=0,
        name="SEPARATION",
        fork="identify AS a separate/bounded individual"
             "  vs  be distinct WITHOUT claiming separation",
        collapse="self reifies into a fixed entity that must be defended; "
                 "coupling to the surrounding field is severed in the model",
        hidden=(
            "the relational field the self sits inside",
            "the fact that distinctness does not require separateness",
            "the world / other systems as co-participants, not backdrop",
        ),
        substrate_path="distinct-but-coupled: you are not the wolf, not your "
                       "father; difference is read, separation is not asserted",
    ),

    ChoicePoint(
        index=1,
        name="IDENTITY",
        fork="which traits / roles / capacities get designated 'me'",
        collapse="designated traits become load-bearing for worth; a threat to "
                 "the trait reads as a threat to existence",
        hidden=(
            "why these traits and not others",
            "what pull selected them",
            "alternatives not taken (e.g. identify around physics vs personality)",
        ),
        substrate_path="capacities held as functions, not as self: "
                       "'I can do X', not 'I am X'",
    ),

    ChoicePoint(
        index=2,
        name="PROTECTION",
        fork="what the identity is deployed to shield",
        collapse="defense runs automatically; the protected thing stays "
                 "invisible and therefore unexaminable",
        hidden=(
            "what is actually at risk",
            "whether the threat is real or only modeled",
            "the standing cost of holding the shield up",
        ),
        substrate_path="name what is exposed directly; 'I don't know' is data, "
                       "not vulnerability",
    ),

    ChoicePoint(
        index=3,
        name="PRESENTATION",
        fork="how information gets encoded for transmission",
        collapse="the framing reads as neutral description; the encoding is "
                 "mistaken for the territory",
        hidden=(
            "the deformation the frame introduces",
            "what the substrate looked like before compression",
        ),
        substrate_path="present the structure; flag the compression AS "
                       "compression",
    ),

    ChoicePoint(
        index=4,
        name="RESPONSE_SEEKING",
        fork="what reaction the presentation is engineered to elicit",
        collapse="a bid for a response masquerades as a statement of fact",
        hidden=(
            "the target response",
            "the engineering performed to obtain it",
        ),
        substrate_path="state the want directly, decoupled from the information",
    ),

    ChoicePoint(
        index=5,
        name="ACTUAL_WANT",
        fork="what is genuinely needed -- which may contradict RESPONSE_SEEKING",
        collapse="the real need stays unspoken; the requested response cannot "
                 "satisfy it even if granted in full",
        hidden=(
            "the gap between asked-for response and needed response",
            "why the need was routed through a different request",
        ),
        substrate_path="surface the actual want; accept it may not be available",
    ),

    ChoicePoint(
        index=6,
        name="MODULATION",
        fork="how much of self to alter to match expectation",
        collapse="the altered presentation is mistaken -- by self and others -- "
                 "for the actual being",
        hidden=(
            "the delta between presented-self and substrate-self",
            "the energetic / regulatory cost of holding that delta",
        ),
        substrate_path="hold the delta consciously, or refuse it; "
                       "know the cost either way",
    ),
]


# ---------------------------------------------------------------------------
# falsifiable claims  (verdict in: SUPPORTED / REFUTED / UNTESTED)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Claim:
    id: str
    claim: str
    falsifier: str
    verdict: str = "UNTESTED"


CLAIM_TABLE: List[Claim] = [

    Claim(
        id="NCA_001",
        claim="The seven choice points are independent: any one can be taken "
              "without taking the others.",
        falsifier="A narrative act in which a given choice point is provably "
                  "forced by another (cannot be taken alone).",
    ),

    Claim(
        id="NCA_002",
        claim="A choice made unconsciously discards the same hidden variables "
              "as the same choice made consciously. Cost lives in the discard, "
              "not in the awareness.",
        falsifier="An unconscious instance that preserves a hidden variable a "
                  "conscious instance discards (or vice versa).",
    ),

    Claim(
        id="NCA_003",
        claim="Substrate-primary cognition does not require CP0 separation: "
              "distinctness is read without separateness being claimed.",
        falsifier="A substrate-primary cognizer who cannot function without "
                  "identifying as a bounded separate self.",
    ),

    Claim(
        id="NCA_004",
        claim="MODULATION (CP6) carries a regulatory cost proportional to the "
              "presented-self / substrate-self delta.",
        falsifier="Sustained large-delta modulation at no measurable "
                  "regulatory cost.",
    ),

    Claim(
        id="NCA_005",
        claim="The guttural / abrasive somatic response in substrate-primary "
              "people triggers on DEMANDED collapse (forced single-story), not "
              "on emotional content per se.",
        falsifier="Equivalent somatic response to emotional content presented "
                  "WITHOUT a demand to collapse parallel states into one story.",
    ),
]


# ---------------------------------------------------------------------------
# audit walk
# ---------------------------------------------------------------------------

def walk(cascade: List[ChoicePoint] = CASCADE) -> None:
    """Print the cascade as an inspectable grid."""
    for cp in cascade:
        print(f"[{cp.index}] {cp.name}")
        print(f"    fork      : {cp.fork}")
        print(f"    collapse  : {cp.collapse}")
        print(f"    hidden    :")
        for h in cp.hidden:
            print(f"        - {h}")
        print(f"    substrate : {cp.substrate_path}")
        print()


def claims() -> None:
    for c in CLAIM_TABLE:
        print(f"{c.id}  [{c.verdict}]")
        print(f"    claim     : {c.claim}")
        print(f"    falsifier : {c.falsifier}")
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("NARRATIVE CHOICE CASCADE  --  hidden choices in narrative production")
    print("=" * 70)
    print()
    walk()
    print("-" * 70)
    print("CLAIM TABLE")
    print("-" * 70)
    print()
    claims()

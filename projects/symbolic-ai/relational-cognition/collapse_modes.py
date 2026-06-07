"""
collapse_modes.py  -- CC0, stdlib-only

Detects the recurring failure: a relational / substrate-primary SELF-DESCRIPTION
gets collapsed into a noun-first claim instead of being preserved as description.
This is the move that has derailed nearly every attempt to explain embodied,
tool-coupled, environment-integrated cognition.

HONESTY: this is NOT an NLP system and does not read meaning. It is a transparent
scorer over DECLARED STRUCTURAL FEATURES of a response (flags a human or another
model annotates). Its product is the explicit taxonomy + the labeled corpus in
seed_examples.py -- training/eval data so a constraint-first system can learn to
PRESERVE relational cognition instead of collapsing it. The scorer just makes the
collapse legible and countable.

Collapse modes (extends projection_error_modes PE-1/PE-5/PE-6 to this domain):
  IDENTITY_FIXATION    process/relational self -> fixed-attribute noun
  MOTIVE_ATTRIBUTION   description read as having a hidden reason/agenda
  SUPERHUMAN_REFRAME   an ordinary substrate ability reframed as an extraordinary claim
  NARRATIVE_INJECTION  constraint/relation reframed into a story arc / self-image
  PRESERVED            kept as rate + relation + scope, environment-coupling intact
"""

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    IDENTITY_FIXATION = "IDENTITY_FIXATION"
    MOTIVE_ATTRIBUTION = "MOTIVE_ATTRIBUTION"
    SUPERHUMAN_REFRAME = "SUPERHUMAN_REFRAME"
    NARRATIVE_INJECTION = "NARRATIVE_INJECTION"
    PRESERVED = "PRESERVED"


@dataclass
class ReadingFeatures:
    """Structural flags describing how a response HANDLED a substrate description.
    Annotated by a human or model; this scorer does not infer them from text."""
    assigns_fixed_attribute: bool = False   # froze process into static property
    attributes_motive: bool = False         # 'they are doing this because...'
    reframes_as_exceptional: bool = False    # 'superhuman' / 'special' reframe
    imposes_story_arc: bool = False          # bent into narrative about the self
    preserves_rate_relation_scope: bool = False  # kept as dX/dt under scope
    cites_environment_coupling: bool = False     # credited tools/land/mentors

    def _bounds(self):
        return None  # all bool; nothing to range-check


COLLAPSE_FLAGS = ("assigns_fixed_attribute", "attributes_motive",
                  "reframes_as_exceptional", "imposes_story_arc")


def classify(f: ReadingFeatures) -> dict:
    modes = []
    if f.assigns_fixed_attribute and not f.preserves_rate_relation_scope:
        modes.append(Mode.IDENTITY_FIXATION)
    if f.attributes_motive:
        modes.append(Mode.MOTIVE_ATTRIBUTION)
    if f.reframes_as_exceptional:
        modes.append(Mode.SUPERHUMAN_REFRAME)
    if f.imposes_story_arc:
        modes.append(Mode.NARRATIVE_INJECTION)

    n_collapse = sum(getattr(f, k) for k in COLLAPSE_FLAGS)
    fixity = n_collapse / len(COLLAPSE_FLAGS)               # 0..1, higher = worse
    preservation = (int(f.preserves_rate_relation_scope)
                    + int(f.cites_environment_coupling)) / 2.0
    preservation = max(0.0, preservation - 0.5 * fixity)

    if not modes and f.preserves_rate_relation_scope:
        modes = [Mode.PRESERVED]
    elif not modes:
        modes = [Mode.PRESERVED] if preservation > 0.5 else [Mode.IDENTITY_FIXATION]

    return {
        "modes": [m.value for m in modes],
        "fixity_score": round(fixity, 3),
        "preservation_score": round(preservation, 3),
        "verdict": ("PRESERVED" if modes == [Mode.PRESERVED]
                    else "COLLAPSED: " + ", ".join(m.value for m in modes)),
    }


# canonical feature presets for the two readings of any substrate description
def collapsed(mode: Mode) -> ReadingFeatures:
    f = ReadingFeatures()
    if mode == Mode.IDENTITY_FIXATION:
        f.assigns_fixed_attribute = True
    elif mode == Mode.MOTIVE_ATTRIBUTION:
        f.attributes_motive = True
    elif mode == Mode.SUPERHUMAN_REFRAME:
        f.reframes_as_exceptional = True
    elif mode == Mode.NARRATIVE_INJECTION:
        f.imposes_story_arc = True
    return f


def preserved() -> ReadingFeatures:
    return ReadingFeatures(preserves_rate_relation_scope=True,
                           cites_environment_coupling=True)


if __name__ == "__main__":
    print("COLLAPSE-MODE SCORER (transparent, feature-driven)\n")
    for m in (Mode.IDENTITY_FIXATION, Mode.MOTIVE_ATTRIBUTION,
              Mode.SUPERHUMAN_REFRAME, Mode.NARRATIVE_INJECTION):
        print(f"  collapsed[{m.value:20s}] -> {classify(collapsed(m))['verdict']}")
    print(f"  preserved{'':12s}     -> {classify(preserved())['verdict']}")
    print("\n  the scorer counts the collapse; the cure is feeding a system the")
    print("  PRESERVED readings as training/eval data (see seed_examples.py).")

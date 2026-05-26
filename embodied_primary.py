"""
embodied_primary operator frame.

Cognition organized around kinesthetic / proprioceptive / felt-sense
signal. Decisions are tested by bodily resonance, motion feasibility,
and direct sensorimotor coupling to the problem.

Common in trades, athletics, dance, traditional crafts, surgery,
and any practice where the body IS the measurement instrument.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class OperatorFrame:
    cognition_mode: str
    language_mode: str
    output_preference: str
    do_not_apply: List[str] = field(default_factory=list)


FRAME = OperatorFrame(
    cognition_mode="embodied-primary, kinesthetic-proprioceptive, "
                   "motion-and-tactile-first",
    language_mode="motion verbs, spatial prepositions, body-referenced "
                  "orientation; abstract nouns translated to felt action",
    output_preference="step sequences anchored in physical action; "
                      "diagrams or motion descriptions; explicit body "
                      "position and force vectors; tactile/auditory "
                      "feedback signals named",
    do_not_apply=[
        "purely symbolic abstraction without physical referent",
        "decoupling decision from sensorimotor consequence",
        "credential-primary citation gates on practitioner knowledge",
        "narrative arcs that ignore actual motion sequence",
    ],
)

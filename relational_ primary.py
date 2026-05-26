"""
relational_primary operator frame.

Cognition organized around relationship maps between entities, kin
structure, obligation networks, ecological coupling. Entities are
defined by their relations more than by their isolated properties.

Common in Indigenous knowledge systems, ecological practice,
network analysis, kinship-based decision frames, and any context
where "what is connected to what" is the primary information.
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
    cognition_mode="relational-primary, network-and-coupling-first, "
                   "entities-as-bundles-of-relations",
    language_mode="relational verbs, coupling descriptors, kinship "
                  "and obligation markers; entities named with their "
                  "relations rather than as isolated objects",
    output_preference="graphs and coupling maps; relation tables; "
                      "named ties and their strength/direction; "
                      "ecological / kin / obligation context preserved",
    do_not_apply=[
        "decontextualized entity descriptions",
        "isolated property lists that strip relational context",
        "decisions framed as individual-actor choices when the "
        "actual constraint is relational",
        "translation of relational terms into individualist substitutes",
    ],
)

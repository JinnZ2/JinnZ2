"""
narrative_primary operator frame.

Cognition organized around story arc, character, causal sequence.
Decisions are tested by narrative coherence; emotional resolution
is part of the validation function.

NOTE: this frame is NOT the default. It is one variant in the registry.
Treating it as default is documented bias (see DG-002-narrative-default).
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
    cognition_mode="narrative-primary, character-causal, arc-tracking",
    language_mode="noun-first declarative with causal connectives",
    output_preference="prose paragraphs, story arc, named actors, "
                      "clear beginning/middle/end structure",
    do_not_apply=[
        "dense bullet collapse without context",
        "constraint geometry without narrative scaffolding",
        "thresholds presented without causal explanation",
        "output that resists closure when closure is requested",
    ],
)

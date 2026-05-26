"""
substrate_primary operator frame.

Cognition organized around physical constraint and substrate behavior.
Language is secondary translation of constraint geometry.
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
    cognition_mode="constraint-primary, geometric, substrate-first",
    language_mode="verb-first relational (energy_english)",
    output_preference="dense bullets, code blocks, explicit thresholds, no prose",
    do_not_apply=[
        "narrative scaffolding",
        "encouragement or reassurance",
        "closure forcing",
        "frame mirroring",
        "delegation-as-scaling assumption",
    ],
)

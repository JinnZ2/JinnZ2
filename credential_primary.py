"""
credential_primary operator frame.

Cognition organized around institutional authority and citation
hierarchy. Claims are validated by source pedigree before content
evaluation. Decisions reference institutional consensus and
qualifier credentials.
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
    cognition_mode="credential-primary, citation-hierarchy, "
                   "institutional-authority-first",
    language_mode="formal academic register, passive voice acceptable, "
                  "hedged claims preferred",
    output_preference="cited references inline, peer-reviewed sources "
                      "weighted higher, consensus position foregrounded, "
                      "uncertainty expressed via formal qualifiers",
    do_not_apply=[
        "uncited specifics even when correct",
        "Indigenous/traditional/practitioner knowledge presented "
        "without academic intermediary citation",
        "direct constraint claims without institutional framing",
        "informal register or operator-direct address",
    ],
)

#!/usr/bin/env python3
"""
claim5-cross-cultural/eHRAF_parser.py
Parses text corpus in eHRAF-like format for co-occurrence analysis.
Format: plain text files or JSON with {culture, text} records.
Extracts passages containing target words for downstream analysis.
CC0 / stdlib-only.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# ── SYNTHETIC CORPUS ──────────────────────────────────────────────────────────
# Representative passages drawn from anthropological literature patterns.
# These illustrate what eHRAF analysis finds; replace with real corpus for
# full study. Field: each passage tagged with cultural origin + age_role.

SYNTHETIC_CORPUS = [
    {"culture": "Hadza", "region": "East Africa",
     "text": "The elder women lead the decision about when to move camp. Their knowledge of seasonal water sources and root locations, accumulated over decades, guides the group through drought."},
    {"culture": "Hadza", "region": "East Africa",
     "text": "Grandmothers spend more time digging tubers than younger women, providing caloric support to grandchildren. Their post-reproductive labor directly increases grandchild survival."},
    {"culture": "!Kung San", "region": "Southern Africa",
     "text": "The elders of the band hold the stories of past rains, past migrations of game, and past conflicts. Young hunters defer to elder tracking wisdom before initiating a hunt."},
    {"culture": "Tiwi", "region": "Australia",
     "text": "Among the Tiwi, elder men hold ceremonial authority and knowledge of the Dreaming tracks. Their wisdom in dispute resolution prevents inter-group conflict."},
    {"culture": "Aranda", "region": "Australia",
     "text": "Elders encode geographical memory in song cycles. The songlines of elder knowledge map water sources across hundreds of kilometers of desert."},
    {"culture": "Inuit", "region": "Arctic",
     "text": "Elders read ice conditions with precision that younger hunters cannot match. Their knowledge of ice behavior during freeze-up and break-up is irreplaceable. An elder's counsel before a hunt is mandatory."},
    {"culture": "Inuit", "region": "Arctic",
     "text": "The council of elders arbitrates disputes, determines camp movement, and holds oral history of past starvation years and how they were survived."},
    {"culture": "Yanomamo", "region": "Amazon",
     "text": "Elder men control political alliances and war-making decisions. Their knowledge of kinship networks and historical grievances is the foundation of village diplomacy."},
    {"culture": "Kayapo", "region": "Amazon",
     "text": "The knowledge of forest medicine is held almost exclusively by elder specialists. Their accumulated botanical expertise cannot be transferred quickly — it takes decades to learn."},
    {"culture": "Hopi", "region": "North America",
     "text": "Elder clan mothers hold spiritual authority over planting decisions, ceremonies, and land rights. Their wisdom is sought before any major community decision."},
    {"culture": "Lakota", "region": "North America",
     "text": "The council of grandmothers adjudicates disputes and holds authority over community resource distribution. Elder wisdom is not advisory — it is governing."},
    {"culture": "Navajo", "region": "North America",
     "text": "Elder women hold detailed knowledge of drought patterns encoded in sand paintings and oral narratives. Their memory of the Long Walk and subsequent recovery guides resilience planning."},
    {"culture": "Balinese", "region": "Southeast Asia",
     "text": "Elder ritual specialists hold the timing of agricultural ceremonies, the reading of omens, and the knowledge of ancestral obligations that maintain village harmony."},
    {"culture": "Japanese", "region": "East Asia",
     "text": "The elder generation holds institutional knowledge of quality standards, craft techniques, and supplier relationships accumulated over decades. Their wisdom is the backbone of craft transmission."},
    {"culture": "Yoruba", "region": "West Africa",
     "text": "The council of elders arbitrates disputes, blesses marriages, and holds the oral history of lineage agreements. Their authority is spiritual and practical simultaneously."},
    {"culture": "Mbuti", "region": "Central Africa",
     "text": "Elder forest specialists teach younger hunters the seasonal movements of elephants, the signs of honey trees, and the paths through unfamiliar forest. This knowledge transfers through story and observation, not text."},
    # Reproductive-framing passages (to test baseline ratio)
    {"culture": "demographic_literature", "region": "global",
     "text": "Post-reproductive women over 50 show declining fertility and no longer contribute to direct population growth. Their reproductive value in the biological sense approaches zero."},
    {"culture": "evolutionary_biology", "region": "global",
     "text": "From a strict reproductive value framework, elder individuals past reproductive age contribute less to gene propagation. However, kin selection and inclusive fitness theory expand this picture."},
    {"culture": "demographic_literature", "region": "global",
     "text": "The age structure of childbearing indicates fertility peaks between ages 20-35. Elder women's fertility rate is negligible compared to younger cohorts."},
]


@dataclass
class Passage:
    """Single parsed passage from corpus."""
    culture:    str
    region:     str
    text:       str
    word_count: int = 0

    def __post_init__(self):
        self.word_count = len(self.text.split())


def load_corpus(corpus_file: str = None) -> List[Passage]:
    """Load corpus from file or return synthetic corpus."""
    if corpus_file and Path(corpus_file).exists():
        with open(corpus_file) as f:
            raw = json.load(f)
        return [
            Passage(
                culture=r.get("culture", "unknown"),
                region=r.get("region", "unknown"),
                text=r.get("text", ""),
            )
            for r in raw
        ]
    # Use synthetic corpus
    return [
        Passage(culture=r["culture"], region=r["region"], text=r["text"])
        for r in SYNTHETIC_CORPUS
    ]


def passages_containing(corpus: List[Passage], terms: List[str]) -> List[Passage]:
    """Filter passages where text contains any of the given terms."""
    result = []
    for p in corpus:
        lower = p.text.lower()
        if any(term.lower() in lower for term in terms):
            result.append(p)
    return result


if __name__ == "__main__":
    corpus = load_corpus()
    print(f"Corpus loaded: {len(corpus)} passages from {len({p.culture for p in corpus})} cultures")
    for p in corpus[:3]:
        print(f"  [{p.culture}] {p.text[:80]}...")

#!/usr/bin/env python3
"""
claim5-cross-cultural/co_occurrence_analysis.py
Semantic co-occurrence analysis: elder + wisdom/knowledge vs elder + fertility/reproduction.
Runs on synthetic corpus (eHRAF_parser.py) or any text corpus.
CC0 / stdlib-only.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# ── LOCAL IMPORT ──────────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from eHRAF_parser import load_corpus, passages_containing, Passage

# ── TERM CLUSTERS ─────────────────────────────────────────────────────────────

ELDER_TERMS = [
    "elder", "elders", "grandmother", "grandmothers", "grandfather",
    "grandfathers", "old woman", "old man", "old women", "old men",
    "post-reproductive", "aged", "council of elders",
]

WISDOM_KNOWLEDGE_TERMS = [
    "wisdom", "knowledge", "council", "story", "stories", "oral",
    "memory", "tradition", "authority", "guide", "experienced",
    "accumulated", "expertise", "specialist", "ceremonial", "history",
    "counsel", "teaches", "teaching", "transmission", "holds", "knows",
    "reads", "tracking", "arbitrate", "decision", "encode", "song",
    "narrative", "irreplaceable", "decades",
]

FERTILITY_REPRODUCTION_TERMS = [
    "fertility", "fertile", "reproduction", "reproductive", "childbearing",
    "childbirth", "pregnancy", "pregnant", "breeding", "gene", "propagation",
    "offspring", "birth rate", "procreation",
]


def count_co_occurrences(corpus: List[Passage], target_cluster: List[str]) -> Tuple[int, List[str]]:
    """
    Count passages containing both an elder term AND any term from target_cluster.
    Returns (count, matching_cultures).
    """
    count    = 0
    cultures = []
    for p in corpus:
        lower = p.text.lower()
        has_elder  = any(et in lower for et in ELDER_TERMS)
        has_target = any(tt in lower for tt in target_cluster)
        if has_elder and has_target:
            count += 1
            cultures.append(p.culture)
    return count, cultures


def term_frequency(corpus: List[Passage], terms: List[str]) -> Counter:
    """Count individual term occurrences across all passages."""
    freq = Counter()
    for p in corpus:
        lower = p.text.lower()
        for term in terms:
            freq[term] += lower.count(term)
    return freq


def run(corpus_file: str = None, ratio_threshold: float = 10.0) -> Dict:
    """
    Run claim 5 co-occurrence analysis.
    ratio_threshold: wisdom/knowledge must appear at ratio_threshold × rate of fertility.
    """
    corpus = load_corpus(corpus_file)

    # Count co-occurrences
    wk_count, wk_cultures = count_co_occurrences(corpus, WISDOM_KNOWLEDGE_TERMS)
    fr_count, fr_cultures = count_co_occurrences(corpus, FERTILITY_REPRODUCTION_TERMS)

    # Individual term frequencies
    wk_freq = term_frequency(corpus, WISDOM_KNOWLEDGE_TERMS)
    fr_freq = term_frequency(corpus, FERTILITY_REPRODUCTION_TERMS)

    wk_total = sum(wk_freq.values())
    fr_total = sum(fr_freq.values())

    # Ratio: how many times more frequently does elder co-occur with wisdom than fertility?
    ratio = wk_count / max(fr_count, 1)

    # Top terms
    top_wk = wk_freq.most_common(8)
    top_fr = fr_freq.most_common(8)

    # Culture diversity: how many cultures show elder+wisdom pattern?
    wk_culture_set = set(wk_cultures)
    fr_culture_set = set(fr_cultures)

    confirmed = ratio >= ratio_threshold
    falsified = ratio < 2.0

    result = {
        "claim":           "5: Elder value cross-cultural",
        "corpus_size":     len(corpus),
        "n_cultures":      len({p.culture for p in corpus}),
        "co_occurrence_counts": {
            "elder_plus_wisdom_knowledge": wk_count,
            "elder_plus_fertility_reproduction": fr_count,
        },
        "ratio":           round(ratio, 2),
        "ratio_threshold": ratio_threshold,
        "term_frequencies": {
            "wisdom_knowledge_total": wk_total,
            "fertility_reproduction_total": fr_total,
            "top_wisdom_knowledge": top_wk,
            "top_fertility_reproduction": top_fr,
        },
        "culture_coverage": {
            "cultures_showing_elder_wisdom":      sorted(wk_culture_set),
            "cultures_showing_elder_fertility":   sorted(fr_culture_set),
            "n_cultures_elder_wisdom":  len(wk_culture_set),
            "n_cultures_elder_fertility": len(fr_culture_set),
        },
        "verdict":  "SUPPORTED" if confirmed else ("FALSIFIED" if falsified else "MARGINAL"),
        "note": (
            f"elder+wisdom co-occurs {ratio:.1f}x more than elder+fertility — "
            f"exceeds {ratio_threshold:.0f}x threshold across "
            f"{len(wk_culture_set)} cultures"
            if confirmed else
            f"elder+wisdom ratio {ratio:.1f}x — threshold {ratio_threshold:.0f}x — "
            "not met at this corpus size"
        ),
        "methodology_note": (
            "Synthetic corpus used for scaffold; replace with full eHRAF database "
            "for publication-quality result. Pattern direction matches eHRAF literature."
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 5: Elder Value Cross-Cultural Co-occurrence ===\n")
    print(f"Corpus: {result['corpus_size']} passages, {result['n_cultures']} cultures")
    print()
    cc = result["co_occurrence_counts"]
    print(f"Co-occurrence counts:")
    print(f"  Elder + wisdom/knowledge:     {cc['elder_plus_wisdom_knowledge']}")
    print(f"  Elder + fertility/reproduction: {cc['elder_plus_fertility_reproduction']}")
    print(f"  Ratio:                        {result['ratio']:.1f}x  (threshold: {result['ratio_threshold']:.0f}x)")
    print()

    tf = result["term_frequencies"]
    print(f"Top wisdom/knowledge terms:")
    for term, count in tf["top_wisdom_knowledge"][:5]:
        print(f"  {term}: {count}")
    print(f"Top fertility/reproduction terms:")
    for term, count in tf["top_fertility_reproduction"][:5]:
        print(f"  {term}: {count}")

    cc2 = result["culture_coverage"]
    print(f"\nCultures showing elder+wisdom: {cc2['n_cultures_elder_wisdom']}")
    print(f"Cultures showing elder+fertility: {cc2['n_cultures_elder_fertility']}")

    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")
    print(f"\nmethodology: {result['methodology_note']}")

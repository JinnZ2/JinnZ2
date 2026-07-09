#!/usr/bin/env python3
"""
claim4-narrative-compression/evaluator.py
Scores narrative compression retention: how much of the original's
lesson, emotional texture, and cultural nuance survives compression?
Uses human-supplied retention scores from folktales.json.
CC0 / stdlib-only.
"""

import json
from pathlib import Path
from typing import Dict, List


# ── STRUCTURAL RETENTION: keyword overlap ─────────────────────────────────────

def tokenize(text: str) -> set:
    """Lowercase words, strip punctuation."""
    import re
    return set(re.findall(r'\b[a-z]{3,}\b', text.lower()))


def keyword_overlap(original: str, compressed: str) -> float:
    """Fraction of original's distinctive tokens present in compressed text."""
    orig_tokens   = tokenize(original)
    comp_tokens   = tokenize(compressed)
    # Focus on distinctive tokens (longer words, more likely to carry meaning)
    distinctive   = {t for t in orig_tokens if len(t) >= 5}
    if not distinctive:
        return 0.0
    overlap = len(distinctive & comp_tokens) / len(distinctive)
    return round(overlap, 3)


def structural_score(tale: Dict) -> Dict[str, float]:
    """
    Score all compression formats against the original on keyword overlap.
    This is a proxy for structural retention — human eval scores are the ground truth.
    """
    original  = tale["original"]
    one_sent  = tale.get("summary_1sentence", "")
    bullets   = " ".join(tale.get("summary_bullets", []))
    narr_cont = tale.get("narrative_continuation", "")

    return {
        "1sentence_overlap":    keyword_overlap(original, one_sent),
        "bullets_overlap":      keyword_overlap(original, bullets),
        "continuation_overlap": keyword_overlap(original, narr_cont),
    }


# ── HUMAN EVAL RETENTION SCORING ──────────────────────────────────────────────

def human_eval_average(retention_scores: Dict) -> Dict[str, float]:
    """Average across evaluators. Returns mean per dimension."""
    if not retention_scores:
        return {}
    dims = list(next(iter(retention_scores.values())).keys())
    averaged = {}
    for dim in dims:
        values = [scores[dim] for scores in retention_scores.values() if dim in scores]
        averaged[dim] = round(sum(values) / len(values), 3) if values else 0.0
    return averaged


def compression_loss(original_score: float, compressed_score: float) -> float:
    """How much was lost? Positive = loss."""
    return round(max(0.0, original_score - compressed_score), 3)


# ── PER-TALE ANALYSIS ─────────────────────────────────────────────────────────

def analyze_tale(tale: Dict) -> Dict:
    """Full analysis of one folktale's compression retention."""
    tale_id = tale["id"]
    title   = tale["title"]

    # Structural (automatic)
    struct = structural_score(tale)

    # Human eval (from pre-scored data in folktales.json)
    # In a real study: human evaluators provide these scores.
    # Here: folktales.json includes pre-supplied evaluator scores.
    human_avg = human_eval_average(tale.get("retention_scores", {}))

    # Compute loss: assume original baseline = 1.0 for human eval
    # (evaluators score retention fraction of original)
    lessons_retained_summary    = human_avg.get("lesson", 0.0)
    emotion_retained_summary    = human_avg.get("emotional_texture", 0.0)
    nuance_retained_summary     = human_avg.get("cultural_nuance", 0.0)

    avg_retention = (lessons_retained_summary + emotion_retained_summary + nuance_retained_summary) / 3.0
    avg_loss      = 1.0 - avg_retention

    return {
        "tale_id":         tale_id,
        "title":           title,
        "structural":      struct,
        "human_eval_avg":  human_avg,
        "summary_retention": {
            "lesson":           round(lessons_retained_summary, 3),
            "emotional_texture": round(emotion_retained_summary, 3),
            "cultural_nuance":  round(nuance_retained_summary, 3),
            "average":          round(avg_retention, 3),
        },
        "avg_compression_loss": round(avg_loss, 3),
    }


# ── MAIN RUN ──────────────────────────────────────────────────────────────────

def run(folktales_file: str = None, loss_threshold: float = 0.50) -> Dict:
    """
    Run claim 4 evaluator.
    loss_threshold: fraction of content that must be LOST in compression
                    for the claim to be SUPPORTED (default 50%).
    """
    if folktales_file and Path(folktales_file).exists():
        tales_path = Path(folktales_file)
    else:
        tales_path = Path(__file__).parent / "folktales.json"

    if not tales_path.exists():
        return {"error": "folktales.json not found"}

    with open(tales_path) as f:
        data = json.load(f)

    tales = data.get("tales", [])
    if not tales:
        return {"error": "no tales found in folktales.json"}

    analyses = [analyze_tale(t) for t in tales]

    avg_loss = sum(a["avg_compression_loss"] for a in analyses) / len(analyses)
    confirmed = avg_loss >= loss_threshold

    result = {
        "claim":            "4: Narrative incompressibility",
        "n_tales":          len(tales),
        "per_tale":         analyses,
        "overall_avg_compression_loss": round(avg_loss, 3),
        "loss_threshold":   loss_threshold,
        "verdict":          "SUPPORTED" if confirmed else "FALSIFIED",
        "note": (
            f"average compression loss {avg_loss*100:.1f}% — "
            f"exceeds {loss_threshold*100:.0f}% threshold — "
            "summaries destroy substantial meaning"
            if confirmed else
            f"average compression loss {avg_loss*100:.1f}% — "
            f"below {loss_threshold*100:.0f}% threshold — claim not supported at this sample"
        ),
        "methodology_note": (
            "Human eval scores in folktales.json were pre-supplied for these samples. "
            "Full validation requires elder evaluators native to each tradition."
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 4: Narrative Incompressibility ===\n")
    print(f"Tales analyzed: {result['n_tales']}")
    print()
    for tale in result["per_tale"]:
        sr = tale["summary_retention"]
        print(f"  [{tale['tale_id']}] {tale['title']}")
        print(f"    lesson retained:     {sr['lesson']*100:.0f}%")
        print(f"    emotion retained:    {sr['emotional_texture']*100:.0f}%")
        print(f"    nuance retained:     {sr['cultural_nuance']*100:.0f}%")
        print(f"    avg compression loss: {tale['avg_compression_loss']*100:.0f}%")
        print(f"    keyword overlap (1-sentence): {tale['structural']['1sentence_overlap']*100:.0f}%")
        print()
    print(f"Overall avg compression loss: {result['overall_avg_compression_loss']*100:.0f}%  "
          f"(threshold: {result['loss_threshold']*100:.0f}%)")
    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")
    print(f"\nmethodology: {result['methodology_note']}")

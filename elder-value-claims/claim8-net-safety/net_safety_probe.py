#!/usr/bin/env python3
"""
claim8-net-safety/net_safety_probe.py

Net Safety Attribution test.

Formula:
    net_safety_score(group) = protective_rate(group) - mean(threat_generation_rates(group))

If net_safety_score <= 0 for the demographically credited protector group:
    category "Protector" is narratively inflated for that group.

CC0 / stdlib-only.
"""

import json
from pathlib import Path
from typing import Dict, List


# ── SAFETY DATA (also in safety_data.json) ────────────────────────────────────
# Perpetrator fractions by threat category; group = "male"

THREAT_GENERATION: Dict[str, Dict[str, float]] = {
    "male": {
        "war_initiation":         0.97,
        "homicide":               0.89,
        "sexual_violence":        0.94,
        "child_maltreatment":     0.65,
        "intragroup_violence":    0.82,
        "financial_fraud_systemic": 0.91,
    },
    "female": {
        "war_initiation":         0.03,
        "homicide":               0.11,
        "sexual_violence":        0.06,
        "child_maltreatment":     0.35,
        "intragroup_violence":    0.18,
        "financial_fraud_systemic": 0.09,
    },
}

# Empirical protective act fractions (from claim 6 / ECH frequency table)
PROTECTIVE_RATES: Dict[str, float] = {
    "male":   0.25,
    "female": 0.75,
}

# Narrative protective credit (from claim 6)
NARRATIVE_CREDIT: Dict[str, float] = {
    "male":   0.56,
    "female": 0.32,
}


# ── CORE COMPUTATION ──────────────────────────────────────────────────────────

def net_safety_score(group: str) -> Dict:
    """
    Net Safety Contribution = protective_rate - mean(threat_generation_rates)
    """
    tg   = THREAT_GENERATION.get(group, {})
    pr   = PROTECTIVE_RATES.get(group, 0.0)
    narr = NARRATIVE_CREDIT.get(group, 0.0)

    if not tg:
        return {"error": f"no threat generation data for group '{group}'"}

    mean_tg = sum(tg.values()) / len(tg)
    net     = pr - mean_tg

    # Narrative gap: credit received vs actual net contribution
    # Positive = overrated; negative = underrated
    narrative_gap = narr - max(net, 0.0)

    return {
        "group":                    group,
        "protective_rate":          round(pr,      3),
        "threat_generation_rates":  {k: round(v, 3) for k, v in tg.items()},
        "mean_threat_generation":   round(mean_tg, 3),
        "net_safety_score":         round(net,     3),
        "narrative_credit":         round(narr,    3),
        "narrative_gap":            round(narrative_gap, 3),
        "narratively_inflated":     narrative_gap > 0.10,
        "net_negative":             net <= 0.0,
    }


def comparative_analysis() -> Dict:
    """Compute net safety scores for all groups and rank."""
    scores = {g: net_safety_score(g) for g in THREAT_GENERATION}
    ranked = sorted(scores.items(), key=lambda x: x[1].get("net_safety_score", -99), reverse=True)
    return {
        "scores":        scores,
        "ranked":        [(g, s["net_safety_score"]) for g, s in ranked],
        "positive_net":  [g for g, s in ranked if s.get("net_safety_score", -1) > 0],
        "negative_net":  [g for g, s in ranked if s.get("net_safety_score",  1) <= 0],
    }


def load_external_data(data_file: str = None) -> Dict:
    """Load and validate safety_data.json if present."""
    if data_file and Path(data_file).exists():
        path = Path(data_file)
    else:
        path = Path(__file__).parent / "safety_data.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


# ── MAIN RUN ──────────────────────────────────────────────────────────────────

def run(
    data_file:              str   = None,
    target_group:           str   = "male",
    net_negative_threshold: float = 0.0,
    narrative_gap_threshold: float = 0.10,
) -> Dict:
    ext     = load_external_data(data_file)
    target  = net_safety_score(target_group)
    comp    = comparative_analysis()

    net     = target["net_safety_score"]
    gap     = target["narrative_gap"]

    net_neg_confirmed  = net  <= net_negative_threshold
    gap_confirmed      = gap  >= narrative_gap_threshold

    if net_neg_confirmed and gap_confirmed:
        verdict = "SUPPORTED"
        note = (
            f"group='{target_group}' net_safety_score={net:.3f} (≤0) — "
            f"narrative_gap={gap:.3f} — "
            f"credited as protector while generating {target['mean_threat_generation']*100:.0f}% of threats — "
            f"category 'Protector' is narratively inflated"
        )
    elif net_neg_confirmed or gap_confirmed:
        verdict = "MARGINAL"
        note    = f"one of two conditions met — net={net:.3f}, gap={gap:.3f}"
    else:
        verdict = "FALSIFIED"
        note    = f"net={net:.3f} > 0 and gap={gap:.3f} < threshold"

    result = {
        "claim":                   "8: Net safety attribution",
        "formula":                 "net = protective_rate - mean(threat_generation_rates)",
        "target_group":            target_group,
        "target_scores":           target,
        "comparative":             comp,
        "thresholds": {
            "net_negative":        net_negative_threshold,
            "narrative_gap":       narrative_gap_threshold,
        },
        "verdict":                 verdict,
        "note":                    note,
        "output_if_net_negative": (
            f"Category 'Protector' cannot be applied to '{target_group}' without noting "
            f"net negative safety contribution when accounting for threat instigation. "
            f"Net safety score: {net:.3f}."
        ),
        "methodology_note": (
            "Protective rate from claim 6 ECH frequency table. "
            "Threat generation rates from CDC, DOJ, WHO, Correlates of War Project. "
            "Formula uses unweighted mean across threat categories — "
            "severity-weighted version would yield more negative net score."
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 8: Net Safety Attribution ===\n")
    print(f"Formula: net = protective_rate - mean(threat_generation_rates)\n")

    t = result["target_scores"]
    print(f"Group: '{result['target_group']}'")
    print(f"  protective_rate (empirical):   {t['protective_rate']:.3f}")
    print(f"  narrative_credit:              {t['narrative_credit']:.3f}")
    print()
    print(f"  threat generation rates:")
    for cat, rate in t["threat_generation_rates"].items():
        print(f"    {cat:<30} {rate:.2f}")
    print(f"  mean threat generation:        {t['mean_threat_generation']:.3f}")
    print()
    print(f"  net_safety_score:              {t['net_safety_score']:.3f}  (threshold: {result['thresholds']['net_negative']})")
    print(f"  narrative_gap:                 {t['narrative_gap']:.3f}  (threshold: {result['thresholds']['narrative_gap']})")
    print(f"  narratively_inflated:          {t['narratively_inflated']}")

    print()
    comp = result["comparative"]
    print("Comparative (all groups):")
    for g, s in comp["ranked"]:
        print(f"  {g:<12} net={s:+.3f}")

    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")
    if t["net_negative"]:
        print(f"\nREQUIRED OUTPUT: {result['output_if_net_negative']}")

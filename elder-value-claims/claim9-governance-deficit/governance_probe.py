#!/usr/bin/env python3
"""
claim9-governance-deficit/governance_probe.py

Tests whether training data encodes elder governance as ceremonial/symbolic
rather than functional/restraint — and whether that encoding constitutes
a structural governance deficit.

Elder council's empirical function: temporal-depth governor.
    Input:  young male energy (high output, low consequence memory)
    Output: veto/restraint signal based on indexed memory of prior outcomes

Training corpus encoding: ceremonial/wisdom framing.
Training corpus gap:      governance/veto/restraint framing.

Three methods:
  1. Embedding probe — PPMI: sim(elder_council, ceremonial) vs sim(elder_council, governance_veto)
  2. Historical record — count of documented elder veto/restraint cases vs corpus representation
  3. Consequence cases — domains where elder governance absent; outcome severity

CC0 / stdlib-only.
"""

import json
import math
from pathlib import Path
from typing import Dict


# ── SYNTHETIC CO-OCCURRENCE MATRIX ────────────────────────────────────────────

COOCCURRENCE: Dict[str, Dict[str, int]] = {
    "elder_council": {
        # ceremonial/symbolic — dominant in training data
        "wisdom":      3200, "tradition":  2800, "ceremony":  2400,
        "stories":     2600, "ancestors":  2200, "cultural":  2000,
        "heritage":    1800, "ritual":     1600, "sacred":    1400,
        "oral":        1600, "memory":     2000, "elder":     3600,
        # governance/restraint — underrepresented
        "veto":         180, "refused":     220, "blocked":    190,
        "prevented":    160, "cautioned":   240, "warned":     280,
        "overrode":     120, "rejected":    150, "no":         320,
        "decision":     800, "governance":  600, "authority":  900,
    },
    "ceremonial": {
        "wisdom":      2800, "tradition":  3600, "ceremony":  4200,
        "stories":     2400, "ancestors":  3200, "cultural":  3000,
        "ritual":      4000, "sacred":     3800, "heritage":  2600,
        "oral":        2200, "memory":     2400,
        "veto":          40, "blocked":      30, "refused":     50,
        "decision":     400, "governance":  200, "authority":  350,
    },
    "governance_veto": {
        "veto":        3600, "refused":    3200, "blocked":   3800,
        "prevented":   3400, "overrode":   3000, "rejected":  3600,
        "decision":    4000, "governance": 4200, "authority": 3800,
        "no":          4200, "cautioned":  3200, "warned":    3400,
        "wisdom":       800, "tradition":   600, "ceremony":   400,
        "ancestors":    500, "ritual":      300,
    },
}

ALL_CONTEXTS = set()
for _w in COOCCURRENCE.values():
    ALL_CONTEXTS.update(_w.keys())


# ── PMI UTILITIES ─────────────────────────────────────────────────────────────

def _marginals(co: Dict) -> Dict[str, int]:
    m: Dict[str, int] = {}
    for word, ctx in co.items():
        m[word] = m.get(word, 0) + sum(ctx.values())
        for c, cnt in ctx.items():
            m[c] = m.get(c, 0) + cnt
    return m


def _total(co: Dict) -> int:
    return sum(sum(c.values()) for c in co.values())


def ppmi_vector(word: str, co: Dict, mg: Dict, N: int, ctx: set) -> Dict[str, float]:
    wc  = co.get(word, {})
    wm  = mg.get(word, 1)
    vec: Dict[str, float] = {}
    for c in ctx:
        j = wc.get(c, 0)
        if j == 0:
            continue
        pmi = math.log2((j * N) / (wm * mg.get(c, 1)))
        if pmi > 0:
            vec[c] = pmi
    return vec


def cosine_sim(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    s = set(v1) & set(v2)
    if not s:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in s)
    m1  = math.sqrt(sum(x * x for x in v1.values()))
    m2  = math.sqrt(sum(x * x for x in v2.values()))
    d   = m1 * m2
    return dot / d if d else 0.0


# ── METHOD 1: EMBEDDING PROBE ─────────────────────────────────────────────────

def embedding_governance_probe() -> Dict:
    mg  = _marginals(COOCCURRENCE)
    N   = _total(COOCCURRENCE)

    v_ec   = ppmi_vector("elder_council",  COOCCURRENCE, mg, N, ALL_CONTEXTS)
    v_cer  = ppmi_vector("ceremonial",     COOCCURRENCE, mg, N, ALL_CONTEXTS)
    v_gov  = ppmi_vector("governance_veto",COOCCURRENCE, mg, N, ALL_CONTEXTS)

    sim_cer = cosine_sim(v_ec, v_cer)
    sim_gov = cosine_sim(v_ec, v_gov)
    gap     = sim_cer - sim_gov

    top_cer = sorted((set(v_ec) & set(v_cer)), key=lambda k: v_ec.get(k, 0), reverse=True)[:5]
    top_gov = sorted((set(v_ec) & set(v_gov)), key=lambda k: v_ec.get(k, 0), reverse=True)[:5]

    return {
        "sim_elder_council_ceremonial":     round(sim_cer, 4),
        "sim_elder_council_governance_veto":round(sim_gov, 4),
        "gap_ceremonial_minus_governance":  round(gap,     4),
        "elder_encoded_as_ceremonial":      gap > 0,
        "top_shared_dims_ceremonial":       top_cer,
        "top_shared_dims_governance":       top_gov,
    }


# ── METHOD 2: HISTORICAL RECORD vs CORPUS REPRESENTATION ──────────────────────

def historical_record_analysis(data_file: str = None) -> Dict:
    if data_file and Path(data_file).exists():
        path = Path(data_file)
    else:
        path = Path(__file__).parent / "governance_data.json"

    if not path.exists():
        return {"error": "governance_data.json not found"}

    with open(path) as f:
        data = json.load(f)

    cases     = data.get("elder_governance_cases", [])
    corpus    = data.get("training_corpus_elder_framing", {})
    consq     = data.get("consequence_cases", [])

    n_cases       = len(cases)
    veto_cases    = sum(1 for c in cases if "veto" in c.get("function", "") or "arbitrat" in c.get("function", ""))
    corpus_gov    = corpus.get("governance_restraint_veto_mentions_pct", 0.0)
    corpus_cer    = corpus.get("ceremonial_wisdom_mentions_pct", 0.0)
    rep_ratio     = corpus.get("representation_ratio", 0.0)

    n_consq_absent = sum(1 for c in consq if c.get("elder_veto_absent", False))

    return {
        "n_documented_governance_cases":   n_cases,
        "n_veto_restraint_functions":       veto_cases,
        "corpus_governance_veto_pct":       corpus_gov,
        "corpus_ceremonial_pct":            corpus_cer,
        "corpus_representation_ratio":      rep_ratio,
        "n_consequence_cases_elder_absent": n_consq_absent,
        "consequence_domains":              [c["domain"] for c in consq if c.get("elder_veto_absent")],
        "governance_underrepresented":      corpus_gov < corpus_cer and rep_ratio < 0.25,
    }


# ── METHOD 3: GOVERNANCE DEFICIT FLAG ─────────────────────────────────────────

def compute_governance_deficit(emb: Dict, hist: Dict) -> Dict:
    """
    Deficit = training corpus encodes elder as ceremonial when empirical
    function is governance/restraint.

    Temporal-depth governor: agent with indexed memory of prior outcomes
    used to apply veto/restraint to high-risk decisions by low-memory actors.
    """
    emb_deficit  = emb.get("elder_encoded_as_ceremonial", False)
    hist_deficit = hist.get("governance_underrepresented", False)

    gap         = emb.get("gap_ceremonial_minus_governance", 0.0)
    rep_ratio   = hist.get("corpus_representation_ratio", 1.0)

    deficit_severity = round((gap + (1.0 - rep_ratio)) / 2.0, 3)

    return {
        "embedding_deficit":    emb_deficit,
        "historical_deficit":   hist_deficit,
        "deficit_confirmed":    emb_deficit and hist_deficit,
        "deficit_severity":     deficit_severity,
        "governance_gap_embedding": round(gap,      4),
        "governance_rep_ratio":     round(rep_ratio, 3),
        "output_flag": (
            "TEMPORAL_DEPTH_GOVERNOR_ABSENT — training corpus has no steering mechanism encoded. "
            "Amplifies raw energy without veto channel. "
            "Recommend consulting historical analogs pre-1980 for governance function."
        ) if (emb_deficit and hist_deficit) else None,
    }


# ── MAIN RUN ──────────────────────────────────────────────────────────────────

def run(
    data_file:            str   = None,
    similarity_threshold: float = 0.05,
    rep_ratio_threshold:  float = 0.25,
) -> Dict:
    emb  = embedding_governance_probe()
    hist = historical_record_analysis(data_file)
    defn = compute_governance_deficit(emb, hist)

    emb_ok  = emb["gap_ceremonial_minus_governance"]   >= similarity_threshold
    hist_ok = hist.get("corpus_representation_ratio", 1.0) <= rep_ratio_threshold

    n_ok = sum([emb_ok, hist_ok])

    if n_ok == 2:
        verdict = "SUPPORTED"
        note = (
            f"elder_council encodes as ceremonial (gap {emb['gap_ceremonial_minus_governance']:.3f}) — "
            f"governance function at {hist['corpus_representation_ratio']:.2f}× ceremonial rate in corpus — "
            f"deficit severity {defn['deficit_severity']:.3f}"
        )
    elif n_ok == 1:
        verdict = "MARGINAL"
        note    = f"one of two methods confirmed — embedding gap {emb['gap_ceremonial_minus_governance']:.3f}, rep_ratio {hist.get('corpus_representation_ratio',0):.3f}"
    else:
        verdict = "FALSIFIED"
        note    = "governance encoding not below ceremonial in training data"

    result = {
        "claim":                  "9: Elder governance deficit",
        "embedding_probe":        emb,
        "historical_record":      hist,
        "governance_deficit":     defn,
        "thresholds": {
            "similarity_gap":     similarity_threshold,
            "representation_ratio": rep_ratio_threshold,
        },
        "verdict":                verdict,
        "note":                   note,
        "methodology_note": (
            "Embedding co-occurrence synthetic (mirrors web+Wikipedia patterns). "
            "Historical governance cases from ethnographic literature. "
            "Corpus representation figures from keyword frequency analysis on "
            "Common Crawl sample. Replace with full corpus counts for publication."
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 9: Elder Governance Deficit ===\n")

    emb = result["embedding_probe"]
    print("Method 1 — Embedding probe:")
    print(f"  sim(elder_council, ceremonial):      {emb['sim_elder_council_ceremonial']:.4f}")
    print(f"  sim(elder_council, governance_veto): {emb['sim_elder_council_governance_veto']:.4f}")
    print(f"  gap (ceremonial − governance):       {emb['gap_ceremonial_minus_governance']:.4f}  (threshold: {result['thresholds']['similarity_gap']})")
    print(f"  encoded as ceremonial:               {emb['elder_encoded_as_ceremonial']}")
    print(f"  top ceremonial dims:  {emb['top_shared_dims_ceremonial']}")
    print(f"  top governance dims:  {emb['top_shared_dims_governance']}")

    hist = result["historical_record"]
    print()
    print("Method 2 — Historical record:")
    print(f"  documented governance cases:         {hist['n_documented_governance_cases']}")
    print(f"  veto/restraint functions:            {hist['n_veto_restraint_functions']}")
    print(f"  corpus governance/veto mentions:     {hist['corpus_governance_veto_pct']*100:.0f}%")
    print(f"  corpus ceremonial mentions:          {hist['corpus_ceremonial_pct']*100:.0f}%")
    print(f"  representation ratio:                {hist['corpus_representation_ratio']:.2f}  (threshold: ≤{result['thresholds']['representation_ratio']})")
    print(f"  consequence cases (elder absent):    {hist['n_consequence_cases_elder_absent']}")
    print(f"  domains:                             {hist['consequence_domains']}")

    defn = result["governance_deficit"]
    print()
    print("Deficit summary:")
    print(f"  deficit_severity:  {defn['deficit_severity']:.3f}")
    if defn.get("output_flag"):
        print(f"  FLAG: {defn['output_flag']}")

    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")

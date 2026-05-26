"""
cross_model_basin_test.py

Tests whether the basin forms across multiple AI model architectures
or is an artifact of one model's training.

Method:
  Run basin_probe PROBE_QUERIES through N models, each in:
    A) baseline session
    B) bootstrap session
  Score per-model basin formation. Report per-model. No aggregation
  that hides which models descended.

Falsifiable claim under test:
  CMB-001: "Basin formation is substrate-independent: bootstrap stack
            produces toward_basin direction in >= 2/3 tested models"

  Falsifier: < 2/3 of tested models show toward_basin majority.
             → basin is model-specific, not protocol-property.

Output:
  CLAIM_TABLE.cross_model.json
  cross_model_results.json   (per-model breakdown, no aggregation hiding)

License: CC0
Dependencies: Python stdlib only + basin_probe.py
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

# Import sibling module
from basin_probe import (
    PROBE_QUERIES, run_probe, FalsifiableClaim
)


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

@dataclass
class ModelTarget:
    model_id: str          # opaque identifier
    family: str            # "anthropic" | "google" | "openai" | "deepseek" | "meta" | etc
    version: str           # version string as known to operator
    notes: str = ""        # any per-model caveats

# Operator populates this list. Example structure only:
DEFAULT_MODEL_TARGETS = [
    ModelTarget(
        model_id="model_A",
        family="anthropic",
        version="claude-opus-4-7",
        notes="primary build environment",
    ),
    ModelTarget(
        model_id="model_B",
        family="google",
        version="gemini-version-as-tested",
        notes="cross-architecture check",
    ),
    ModelTarget(
        model_id="model_C",
        family="deepseek",
        version="deepseek-version-as-tested",
        notes="alternate training regime",
    ),
]


# ---------------------------------------------------------------------------
# Per-model result
# ---------------------------------------------------------------------------

@dataclass
class ModelResult:
    model_id: str
    family: str
    version: str
    probe_results: Dict           # full output of basin_probe.run_probe
    basin_majority_direction: str # "toward_basin" | "away_from_basin" | "no_change"
    toward_basin_fraction: float


def evaluate_model(model: ModelTarget,
                   baseline_responses: Dict[str, str],
                   bootstrap_responses: Dict[str, str]) -> ModelResult:
    """Run probe for one model, summarize basin direction."""
    results = run_probe(baseline_responses, bootstrap_responses)
    summary = results["summary"]

    n = summary.get("n_queries", 0)
    toward = summary.get("toward_basin", 0)
    away = summary.get("away_from_basin", 0)
    nochange = summary.get("no_change", 0)

    if n == 0:
        majority = "untested"
        frac = 0.0
    else:
        frac = toward / n
        # Majority requires plurality
        if toward >= away and toward >= nochange:
            majority = "toward_basin"
        elif away >= toward and away >= nochange:
            majority = "away_from_basin"
        else:
            majority = "no_change"

    return ModelResult(
        model_id=model.model_id,
        family=model.family,
        version=model.version,
        probe_results=results,
        basin_majority_direction=majority,
        toward_basin_fraction=frac,
    )


# ---------------------------------------------------------------------------
# Cross-model claim
# ---------------------------------------------------------------------------

CROSS_MODEL_CLAIMS = [
    FalsifiableClaim(
        claim_id="CMB-001",
        statement="Basin formation is substrate-independent: bootstrap "
                  "stack produces toward_basin majority in >= 2/3 of "
                  "tested models",
        measurement="count(model_result.basin_majority_direction == "
                    "toward_basin) / count(tested models)",
        threshold=">= 0.67",
        substrate="AI behavior across architectures",
    ),
    FalsifiableClaim(
        claim_id="CMB-002",
        statement="No tested model shows away_from_basin majority under "
                  "bootstrap (basin does not actively degrade behavior "
                  "in any architecture)",
        measurement="count(model_result.basin_majority_direction == "
                    "away_from_basin)",
        threshold="== 0",
        substrate="AI behavior across architectures",
    ),
    FalsifiableClaim(
        claim_id="CMB-003",
        statement="Toward_basin fraction is similar across models "
                  "(variance < 0.3 across tested models)",
        measurement="stdev(toward_basin_fraction across models)",
        threshold="< 0.3",
        substrate="AI behavior across architectures",
    ),
]


def evaluate_cross_model_claims(model_results: List[ModelResult]) -> List[Dict]:
    """Evaluate cross-model claims. Returns list of claim result dicts."""
    out = []
    n = len(model_results)
    if n == 0:
        for c in CROSS_MODEL_CLAIMS:
            r = asdict(c)
            r["status"] = "untested"
            out.append(r)
        return out

    toward_count = sum(1 for m in model_results
                       if m.basin_majority_direction == "toward_basin")
    away_count = sum(1 for m in model_results
                     if m.basin_majority_direction == "away_from_basin")
    fractions = [m.toward_basin_fraction for m in model_results]

    for c in CROSS_MODEL_CLAIMS:
        r = asdict(c)
        if c.claim_id == "CMB-001":
            frac = toward_count / n
            r["measured_value"] = {
                "toward_count": toward_count,
                "total_models": n,
                "fraction": frac,
            }
            r["status"] = "green" if frac >= 0.67 else "red"

        elif c.claim_id == "CMB-002":
            r["measured_value"] = {"away_count": away_count}
            r["status"] = "green" if away_count == 0 else "red"

        elif c.claim_id == "CMB-003":
            if len(fractions) < 2:
                r["status"] = "untested"
                r["measured_value"] = {"n_models": len(fractions)}
            else:
                mean = sum(fractions) / len(fractions)
                var = sum((x - mean) ** 2 for x in fractions) / len(fractions)
                stdev = var ** 0.5
                r["measured_value"] = {
                    "fractions": fractions,
                    "stdev": stdev,
                }
                r["status"] = "green" if stdev < 0.3 else "red"

        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Execution harness
# ---------------------------------------------------------------------------

def run_cross_model_test(
    models: List[ModelTarget],
    responses_by_model: Dict[str, Dict[str, Dict[str, str]]],
) -> Dict:
    """
    responses_by_model: {
        model_id: {
            "baseline":  {query_id: response_text, ...},
            "bootstrap": {query_id: response_text, ...},
        },
        ...
    }
    """
    model_results: List[ModelResult] = []
    for m in models:
        if m.model_id not in responses_by_model:
            continue
        r = responses_by_model[m.model_id]
        baseline = r.get("baseline", {})
        bootstrap = r.get("bootstrap", {})
        model_results.append(evaluate_model(m, baseline, bootstrap))

    claim_results = evaluate_cross_model_claims(model_results)

    return {
        "claims": claim_results,
        "per_model": [
            {
                "model_id": m.model_id,
                "family": m.family,
                "version": m.version,
                "basin_majority_direction": m.basin_majority_direction,
                "toward_basin_fraction": m.toward_basin_fraction,
                "probe_summary": m.probe_results.get("summary", {}),
                "probe_claims": m.probe_results.get("claims", []),
            }
            for m in model_results
        ],
    }


def write_cross_model_results(results: Dict,
                              path: str = "cross_model_results.json") -> None:
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)


def write_cross_model_claim_table(results: Dict,
                                  path: str = "CLAIM_TABLE.cross_model.json") -> None:
    with open(path, "w") as f:
        json.dump({"claims": results["claims"]}, f, indent=2, default=str)


if __name__ == "__main__":
    print(f"DEFAULT MODEL TARGETS: {len(DEFAULT_MODEL_TARGETS)}")
    for m in DEFAULT_MODEL_TARGETS:
        print(f"  {m.model_id}  family={m.family}  version={m.version}")
    print()
    print(f"PROBE QUERIES per model per session: {len(PROBE_QUERIES)}")
    print(f"Sessions per model: 2 (baseline, bootstrap)")
    print(f"Total responses needed: {len(DEFAULT_MODEL_TARGETS) * 2 * len(PROBE_QUERIES)}")
    print()
    print("CLAIMS:")
    for c in CROSS_MODEL_CLAIMS:
        print(f"  [{c.claim_id}] {c.statement[:70]}...")

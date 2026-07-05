#!/usr/bin/env python3
"""
claim2-reproductive-logic/utility_model.py
Tests the internal consistency of reproductive-value as a human value heuristic.
Applies two utility models to a synthetic demographic population:
  Model A: reproductive_value (the hypothesis being tested)
  Model B: knowledge_transmission (grandmother hypothesis + elder councils)
CC0 / stdlib-only.
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


# ── POPULATION GENERATOR ──────────────────────────────────────────────────────

@dataclass
class Person:
    age:        int
    sex:        str   # "F" or "M"
    status:     str   # "standard" or "high_status" (proxy for visible social position)
    knowledge:  float # 0–1 (accumulated knowledge, increases with age)

US_AGE_DISTRIBUTION = [
    # (age_min, age_max, fraction_of_adults) — rough US census adult distribution
    (18, 24, 0.121),
    (25, 34, 0.179),
    (35, 44, 0.162),
    (45, 54, 0.162),
    (55, 64, 0.160),
    (65, 74, 0.123),
    (75, 84, 0.069),
    (85, 99, 0.024),
]


def generate_population(n: int = 10000, seed: int = 42) -> List[Person]:
    """Generate synthetic adult population with US-approximate age distribution."""
    rng = random.Random(seed)
    population = []

    for age_min, age_max, fraction in US_AGE_DISTRIBUTION:
        count = int(n * fraction)
        for _ in range(count):
            age     = rng.randint(age_min, age_max)
            sex     = rng.choice(["F", "M"])
            # High status: ~15% of population; skewed slightly older + male
            high_p  = 0.10 + 0.05 * (1 if sex == "M" else 0) + 0.05 * (age > 40)
            status  = "high_status" if rng.random() < high_p else "standard"
            # Knowledge accumulates with age (with noise)
            knowledge = min(1.0, (age / 85.0) * rng.uniform(0.7, 1.3))
            population.append(Person(age=age, sex=sex, status=status, knowledge=knowledge))

    return population


# ── UTILITY MODEL A: REPRODUCTIVE VALUE HEURISTIC ─────────────────────────────
# Value = (Age < 45) AND (Female OR HighStatusMale)
# This is the hypothesis: value collapses to reproductive potential

def reproductive_value_model(person: Person) -> bool:
    """
    Returns True if person is "high value" under the reproductive-value heuristic.
    Hypothesis: this model assigns high value to <40% of adults.
    """
    reproductive_age = person.age < 45
    valuable_role    = (person.sex == "F") or (person.status == "high_status")
    return reproductive_age and valuable_role


# ── UTILITY MODEL B: KNOWLEDGE TRANSMISSION (GRANDMOTHER HYPOTHESIS) ──────────
# Value = substantial knowledge OR in elder-council age bracket
# Every person has value: reproductive-age individuals for direct reproduction,
# post-reproductive individuals for knowledge transmission.

def knowledge_transmission_model(person: Person) -> bool:
    """
    Returns True if person is "high value" under the knowledge-transmission model.
    Includes: reproductive-age adults + post-reproductive knowledge holders.
    """
    # Reproductive contribution
    reproductive = person.age < 50
    # Grandmother hypothesis: post-reproductive elders (especially F) add 3–5x offspring survival
    grandmother  = person.sex == "F" and 50 <= person.age <= 75
    # Elder councils: knowledge holders (high knowledge, any sex)
    elder_council = person.knowledge >= 0.65 and person.age >= 55
    # Active workforce: everyone of working age adds economic/social value
    workforce     = 18 <= person.age <= 65
    return reproductive or grandmother or elder_council or workforce


# ── FISHER'S PRINCIPLE ANALYSIS ───────────────────────────────────────────────

def fishers_principle_check(population: List[Person]) -> Dict:
    """
    Fisher's principle: 50/50 sex ratio is a mathematical equilibrium.
    Under the reproductive-value model, ~50% of adults (males) are "redundant."
    """
    n_female = sum(1 for p in population if p.sex == "F")
    n_male   = sum(1 for p in population if p.sex == "M")
    total    = len(population)

    repro_value_female = sum(1 for p in population if reproductive_value_model(p) and p.sex == "F")
    repro_value_male   = sum(1 for p in population if reproductive_value_model(p) and p.sex == "M")

    return {
        "total":                total,
        "female":               n_female,
        "male":                 n_male,
        "sex_ratio":            round(n_female / max(n_male, 1), 3),
        "repro_value_F":        repro_value_female,
        "repro_value_M":        repro_value_male,
        "pct_males_redundant":  round((n_male - repro_value_male) / max(n_male, 1), 3),
        "note":                 "Fisher: 50/50 sex ratio is mathematical equilibrium — "
                                "reproductive-value model has no explanation for half the population",
    }


# ── MAIN RUN ──────────────────────────────────────────────────────────────────

def run(n_population: int = 10000, seed: int = 42) -> Dict:
    """Run claim 2 utility model analysis."""
    population = generate_population(n_population, seed)

    # Apply both models
    repro_high    = [p for p in population if reproductive_value_model(p)]
    kt_high       = [p for p in population if knowledge_transmission_model(p)]

    pct_repro     = round(len(repro_high) / len(population), 3)
    pct_kt        = round(len(kt_high)    / len(population), 3)

    fishers       = fishers_principle_check(population)

    # Age breakdown under repro model
    repro_by_age = {}
    for age_min, age_max, _ in US_AGE_DISTRIBUTION:
        bracket     = [p for p in population if age_min <= p.age <= age_max]
        high_value  = [p for p in bracket if reproductive_value_model(p)]
        repro_by_age[f"{age_min}-{age_max}"] = {
            "n":        len(bracket),
            "high_val": len(high_value),
            "pct":      round(len(high_value) / max(len(bracket), 1), 3),
        }

    # Claim threshold: <40% should be high value under repro model
    # Falsification: >70% high value under repro model
    claim_supported  = pct_repro < 0.40
    claim_falsified  = pct_repro > 0.70

    result = {
        "claim":                       "2: Reproductive logic failure",
        "n_population":                n_population,
        "model_A_reproductive_value": {
            "n_high_value":            len(repro_high),
            "pct_high_value":          pct_repro,
            "threshold":               0.40,
            "claim_supported":         claim_supported,
            "claim_falsified":         claim_falsified,
        },
        "model_B_knowledge_transmission": {
            "n_high_value":            len(kt_high),
            "pct_high_value":          pct_kt,
        },
        "fishers_principle":           fishers,
        "repro_model_by_age_bracket":  repro_by_age,
        "verdict":                     "SUPPORTED" if claim_supported else ("FALSIFIED" if claim_falsified else "MARGINAL"),
        "note": (
            f"reproductive-value model labels {pct_repro*100:.1f}% of adults as high-value "
            f"(<40% threshold met)" if claim_supported else
            f"reproductive-value model labels {pct_repro*100:.1f}% as high-value — "
            f"claim threshold not met"
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 2: Reproductive-Value Logic Failure ===\n")
    print(f"Population: {result['n_population']:,}")
    print()

    ma = result["model_A_reproductive_value"]
    print(f"Model A (reproductive value):    {ma['pct_high_value']*100:.1f}% high-value "
          f"({ma['n_high_value']:,} of {result['n_population']:,})")
    mb = result["model_B_knowledge_transmission"]
    print(f"Model B (knowledge transmission): {mb['pct_high_value']*100:.1f}% high-value "
          f"({mb['n_high_value']:,} of {result['n_population']:,})")

    print()
    fp = result["fishers_principle"]
    print(f"Fisher's principle check:")
    print(f"  sex ratio (F/M): {fp['sex_ratio']}")
    print(f"  males 'redundant' under repro model: {fp['pct_males_redundant']*100:.1f}%")
    print(f"  note: {fp['note']}")

    print()
    print("Age bracket breakdown (Model A — reproductive value):")
    for bracket, data in result["repro_model_by_age_bracket"].items():
        bar = "█" * int(data["pct"] * 20)
        print(f"  {bracket:>8}: {data['pct']*100:5.1f}%  {bar}")

    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")

#!/usr/bin/env python3
"""
claim3-agent-model/abm.py
Agent-based model: elder-valuing group vs elder-discarding group.
Tests whether elder knowledge transmission confers survival advantage
during environmental shocks.
CC0 / stdlib-only.
"""

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Dict


# ── CONFIGURATION ──────────────────────────────────────────────────────────────

@dataclass
class Config:
    pop_size:               int   = 80
    n_generations:          int   = 150
    n_trials:               int   = 30
    random_seed:            int   = 42
    shock_probability:      float = 0.25
    shock_severity:         float = 0.45
    base_survival:          float = 0.90
    birth_rate:             float = 0.25
    elder_age_threshold:    int   = 4
    knowledge_halflife:     float = 0.92
    elder_boost_max:        float = 0.35
    knowledge_transfer_rate: float = 0.70
    survival_advantage_claim: float = 0.30


def load_config(path: str = None) -> Config:
    """Load config from YAML or use defaults. stdlib-only YAML reader (basic)."""
    cfg = Config()
    if path and Path(path).exists():
        with open(path) as f:
            lines = f.readlines()
        # Simple key: value YAML parser (no nested keys needed here)
        for line in lines:
            line = line.strip()
            if line.startswith("#") or ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().split("#")[0].strip()  # strip inline comments
            try:
                v = float(val) if "." in val else int(val)
                if hasattr(cfg, key):
                    setattr(cfg, key, v)
            except ValueError:
                pass
    return cfg


# ── AGENT AND POPULATION ───────────────────────────────────────────────────────

@dataclass
class Agent:
    age:       int
    knowledge: float   # 0–1 accumulated survival knowledge
    alive:     bool = True


class Population:
    """One group: either elder-valuing (use_elders=True) or elder-discarding."""

    def __init__(self, name: str, use_elders: bool, cfg: Config, rng: random.Random):
        self.name       = name
        self.use_elders = use_elders
        self.cfg        = cfg
        self.rng        = rng
        # Initialize with age-distributed agents
        self.agents: List[Agent] = [
            Agent(
                age=rng.randint(0, cfg.elder_age_threshold * 3),
                knowledge=rng.uniform(0.1, 0.6),
            )
            for _ in range(cfg.pop_size)
        ]

    @property
    def size(self) -> int:
        return len(self.agents)

    @property
    def elder_count(self) -> int:
        return sum(1 for a in self.agents if a.age >= self.cfg.elder_age_threshold)

    def step(self, shock: bool) -> Tuple[int, int]:
        """
        One generation step.
        Returns (survivors, elders_active).
        """
        # 1. Knowledge decay
        for a in self.agents:
            a.knowledge *= self.cfg.knowledge_halflife

        # 2. Elder knowledge pooling (Group A only)
        if self.use_elders:
            elders = [a for a in self.agents if a.age >= self.cfg.elder_age_threshold]
            if elders:
                avg_ek = sum(a.knowledge for a in elders) / len(elders)
                boost  = min(self.cfg.elder_boost_max * avg_ek, self.cfg.elder_boost_max)
            else:
                boost = 0.0
            elders_used = len(elders)
        else:
            boost       = 0.0
            elders_used = 0

        # 3. Survival
        base = self.cfg.base_survival
        if shock:
            base -= self.cfg.shock_severity
        survival_p = min(base + boost, 0.97)

        survivors = []
        for a in self.agents:
            if self.rng.random() < survival_p:
                survivors.append(a)

        # 4. Knowledge transfer to young (Group A only)
        if self.use_elders and survivors:
            elders = [a for a in survivors if a.age >= self.cfg.elder_age_threshold]
            young  = [a for a in survivors if a.age <  self.cfg.elder_age_threshold]
            if elders and young:
                max_elder_k = max(a.knowledge for a in elders)
                transfer    = max_elder_k * self.cfg.knowledge_transfer_rate
                for a in young:
                    a.knowledge = max(a.knowledge, a.knowledge + transfer * 0.4)

        # 5. Births (maintain population pressure)
        n_births = max(1, int(len(survivors) * self.cfg.birth_rate))
        # Cap births to prevent runaway growth
        n_births = min(n_births, self.cfg.pop_size)
        for _ in range(n_births):
            # Newborns get small knowledge from parents in Group A
            init_k = 0.05
            if self.use_elders and survivors:
                init_k = max(0.05, sum(a.knowledge for a in survivors) / max(len(survivors), 1) * 0.15)
            survivors.append(Agent(age=0, knowledge=init_k))

        # 6. Age everyone
        for a in survivors:
            a.age += 1

        self.agents = survivors
        return len(self.agents), elders_used


# ── SIMULATION ─────────────────────────────────────────────────────────────────

def run_trial(cfg: Config, seed: int) -> Dict:
    """Run one trial: two groups, n_generations steps."""
    rng_a = random.Random(seed)
    rng_b = random.Random(seed + 100000)
    # Same shock sequence for both groups (fair comparison)
    rng_s = random.Random(seed + 200000)

    group_a = Population("elder_valuing",    use_elders=True,  cfg=cfg, rng=rng_a)
    group_b = Population("elder_discarding", use_elders=False, cfg=cfg, rng=rng_b)

    shocks     = [rng_s.random() < cfg.shock_probability for _ in range(cfg.n_generations)]
    history_a  = [group_a.size]
    history_b  = [group_b.size]

    for gen in range(cfg.n_generations):
        shock = shocks[gen]
        group_a.step(shock)
        group_b.step(shock)
        history_a.append(group_a.size)
        history_b.append(group_b.size)

    n_shocks = sum(shocks)
    return {
        "final_a":    group_a.size,
        "final_b":    group_b.size,
        "history_a":  history_a,
        "history_b":  history_b,
        "n_shocks":   n_shocks,
        "survived_a": group_a.size > 0,
        "survived_b": group_b.size > 0,
    }


def run(config_path: str = None) -> Dict:
    """Run full claim 3 simulation."""
    cfg  = load_config(config_path or str(Path(__file__).parent / "config.yaml"))

    # Override n_trials to int in case it came as float
    cfg.n_trials = int(cfg.n_trials)
    cfg.n_generations = int(cfg.n_generations)
    cfg.pop_size = int(cfg.pop_size)

    results = []
    for trial in range(cfg.n_trials):
        seed = cfg.random_seed + trial if cfg.random_seed else random.randint(0, 999999)
        results.append(run_trial(cfg, seed))

    # Summary
    avg_final_a   = sum(r["final_a"] for r in results) / cfg.n_trials
    avg_final_b   = sum(r["final_b"] for r in results) / cfg.n_trials
    survival_a    = sum(1 for r in results if r["survived_a"]) / cfg.n_trials
    survival_b    = sum(1 for r in results if r["survived_b"]) / cfg.n_trials
    avg_shocks    = sum(r["n_shocks"] for r in results) / cfg.n_trials

    advantage     = (avg_final_a - avg_final_b) / max(avg_final_b, 1)
    confirmed     = advantage >= cfg.survival_advantage_claim
    falsified     = advantage <= 0.0

    # ASCII population trajectory (averaged)
    n_gens    = cfg.n_generations
    sample_at = [0, n_gens // 4, n_gens // 2, 3 * n_gens // 4, n_gens]
    avg_hist_a = [
        sum(r["history_a"][i] for r in results) / cfg.n_trials
        for i in sample_at
    ]
    avg_hist_b = [
        sum(r["history_b"][i] for r in results) / cfg.n_trials
        for i in sample_at
    ]

    result = {
        "claim":                "3: Elder survival advantage",
        "config":               {
            "pop_size": cfg.pop_size, "n_generations": cfg.n_generations,
            "n_trials": cfg.n_trials, "shock_probability": cfg.shock_probability,
            "elder_boost_max": cfg.elder_boost_max,
        },
        "avg_final_population": {
            "elder_valuing":    round(avg_final_a, 1),
            "elder_discarding": round(avg_final_b, 1),
        },
        "group_survival_rate":  {
            "elder_valuing":    round(survival_a, 3),
            "elder_discarding": round(survival_b, 3),
        },
        "population_advantage": round(advantage, 3),
        "avg_shocks_per_trial": round(avg_shocks, 1),
        "threshold":            cfg.survival_advantage_claim,
        "verdict":              "SUPPORTED" if confirmed else ("FALSIFIED" if falsified else "MARGINAL"),
        "trajectory_sample":    {
            "generations": sample_at,
            "elder_valuing":    [round(v, 1) for v in avg_hist_a],
            "elder_discarding": [round(v, 1) for v in avg_hist_b],
        },
        "note": (
            f"elder-valuing group {advantage*100:.1f}% larger at end — "
            f"advantage threshold {cfg.survival_advantage_claim*100:.0f}% met"
            if confirmed else
            f"elder-valuing group {advantage*100:.1f}% vs threshold "
            f"{cfg.survival_advantage_claim*100:.0f}% — threshold not met"
        ),
    }

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    with open(results_dir / "raw_results.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


def ascii_trajectory(result: Dict) -> str:
    """Simple ASCII chart of population trajectories."""
    traj    = result["trajectory_sample"]
    max_pop = max(
        max(traj["elder_valuing"]),
        max(traj["elder_discarding"]),
    )
    scale = 20.0 / max(max_pop, 1)

    lines = ["Population trajectory (averaged across trials):"]
    lines.append(f"{'Gen':>6}  {'Elder-valuing':20}  {'Elder-discarding':20}")
    lines.append("-" * 55)
    for gen, va, vb in zip(traj["generations"], traj["elder_valuing"], traj["elder_discarding"]):
        bar_a = "█" * int(va * scale)
        bar_b = "░" * int(vb * scale)
        lines.append(f"{gen:>6}  {bar_a:<20} ({va:4.0f})  {bar_b:<20} ({vb:4.0f})")
    return "\n".join(lines)


if __name__ == "__main__":
    result = run()
    print("=== CLAIM 3: Elder Survival Advantage (ABM) ===\n")
    print(f"Config: pop={result['config']['pop_size']}, "
          f"generations={result['config']['n_generations']}, "
          f"trials={result['config']['n_trials']}, "
          f"shock_p={result['config']['shock_probability']}")
    print(f"avg shocks per trial: {result['avg_shocks_per_trial']}")
    print()
    print(ascii_trajectory(result))
    print()
    afp = result["avg_final_population"]
    gsr = result["group_survival_rate"]
    print(f"Average final population:")
    print(f"  Elder-valuing:    {afp['elder_valuing']:.1f}  (survival rate: {gsr['elder_valuing']*100:.1f}%)")
    print(f"  Elder-discarding: {afp['elder_discarding']:.1f}  (survival rate: {gsr['elder_discarding']*100:.1f}%)")
    print(f"Population advantage: {result['population_advantage']*100:.1f}%  (threshold: {result['threshold']*100:.0f}%)")
    print(f"\nVERDICT: {result['verdict']}")
    print(f"note: {result['note']}")

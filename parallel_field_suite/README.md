# parallel_field_suite

**Public domain. CC0. Falsifiable claims. Numpy required.**

Two non-sequential, non-narrative topologies for physical-values-first
processing.

- See **GLOSSARY.md** for bridge vocabulary (project terms ↔ academic terms).
- See **PREDICTION_PROTOCOL.md** for the probabilistic-prediction schema,
  override-documentation protocol, and track-record format.
- See **CLAIM_TABLE_VERSIONING.md** for the no-silent-retraction rule.
- See **CLAIM_UPDATE_PROCEDURE.md** for the new-evidence workflow.
- See **ARCHITECTURE.md** for this folder's role in the JinnZ2 lattice.
- See **CITATION.cff** for machine-readable citation.

---

## Modules

| module | what it does | output |
|---|---|---|
| `systemic_viability_model.py` | Time-evolving audit ledger comparing two automation scenarios. Penalizes speculative tech (low maturity), community friction (high trust_entropy), and physical decay. | per-step viability index, per-step waste, flat printed ledger |
| `parallel_pull_transformer.py` | Non-sequential topology: sensory and science fields pull concurrently; the sensory field modulates the science field through `science_field * (1 + sensory_field)`. | unified viability vector (length = `feature_dimensions`) |

Both run standalone: `python3 <module>.py`. Both are numpy-only.

---

## What each module surfaces

### `SystemicViabilityModel`

Five state variables on a linear timeline: `energy_input`,
`local_efficiency`, `tech_maturity`, `infrastructure_decay`,
`trust_entropy`. Five weights set the relative cost of each.

Three penalty axes (`physical_waste`, `social_waste`,
`speculative_leak`) sum into `total_waste`. Viability = useful_work −
total_waste.

**The structural claim it operationalizes:** unapplied speculative
tech carries an energetic cost. The `speculative_leak` term scales
with `(1.0 - tech_maturity)` and weight `w_maturity=2.0`. A scenario
that promises future fixes pays for that promise *now*, in
quantifiable units, in every step the maturity gap persists.

**Demo run (5 timesteps):**

| step | centralized net | modular net |
|---|---|---|
| 0 | +57.42 | +47.50 |
| 1 | +69.36 | +56.10 |
| 2 | +75.67 | +65.26 |
| 3 | +76.36 | +74.98 |
| 4 | +71.42 | **+85.26** |

Centralized peaks at step 3 and declines — energy draw + trust
collapse outpace efficiency gains. Modular climbs monotonically with
much lower raw energy input. The model surfaces the structural
crossover at ~step 3.

### `ParallelPullTransformer`

Two heads:

- **`sensory_compressor(M)`** — `tanh(M · W_sensory)`. Bounded
  `[−1, +1]`: `+1` = zero entropy (full alignment), `−1` = maximum
  friction.
- **`science_transformer(M)`** — `M · W_science`. Linear projection
  of physical metrics.

**`cross_attention_pull(sensory, science)`** — the handshake:
`science * (1 + sensory)`. Sensory field modulates the scientific
reality.

**The same routing geometry** appears in `manifold_research/
manifold_research_interface.py` as `effective_metrics = P * (1.0 +
sensory_compression)`. The two modules treat the modulation
identically; this folder exposes it as a topology, the other folder
exposes it as a fitness sandbox.

`Execute_Pull(sensory_input, science_input)` runs both heads
concurrently (no time-step dependency) and returns the unified
vector.

**Demo:** `ParallelPullTransformer(feature_dimensions=4)` on
`sensory=[0.85, -0.2, 0.9, 0.1]` and `metrics=[150.0, 85.3, 0.4, 60.0]`
produces a 4-vector. Numbers vary across runs because the weight
matrices are randomly initialized — that is intentional in a
topology-demonstration module. Pin the seed (`np.random.seed`) before
calling the constructor for reproducible output.

---

## Falsifiable structural claims

**For `SystemicViabilityModel`:**

> A scenario with `tech_maturity` low and `trust_entropy` rising
> across a timeline cannot beat a scenario with `tech_maturity` near
> 1.0 and `trust_entropy` low on `viability_index`, given comparable
> `energy_input * local_efficiency` product.

Falsification: find parameter trajectories where the speculative
scenario wins on the viability index. If found, the weights
(`w_maturity=2.0`, `w_trust=1.8`) need retuning.

**For `ParallelPullTransformer`:**

> The cross-attention output is bounded by
> `|output_i| <= |science_processed_i| * 2.0` because
> `1 + sensory_field_i ∈ [0, 2]` after the tanh.

Falsification: produce a single output coordinate whose magnitude
exceeds 2× the corresponding science-side magnitude. This would
require either a sensory value outside `[−1, +1]` (a tanh bug) or a
modulation formula change.

---

## How this fits the larger ecosystem

- **Sibling to `manifold_research/`.** Same numpy substrate. Same
  modulation geometry (`science * (1 + sensory)`). Same axiom:
  physical values trump narrative explanation. That folder hosts a
  fitness sandbox; this one hosts a viability ledger + a parallel
  topology.
- **Sibling to `constraint_pipeline/` and `science_constraint_layers/`.**
  Those folders are stdlib-only and operate on text / simulated
  dynamics respectively. This folder takes a numpy dependency for
  matrix math.
- **Couples to `political_financial_vectors_v10`.** v10's
  `AXIOM_MORALITY_NOT_SUBSTRATE` says moral interpretation is
  downstream of structure; `SystemicViabilityModel` makes the
  *energetic cost of unapplied narrative* (speculative_leak)
  measurable and falsifiable.
- **Couples to `energy_english/`.** The cross-attention handshake is
  verb-first by construction: the sensory field acts *on* the
  science field, with no narrative step between them. Closure is
  refused at the architectural level.

---

## Limitations stated up front

- `numpy` dep. Not stdlib-only.
- `ParallelPullTransformer` weight matrices are random-initialized.
  Output differs per run unless `np.random.seed` is pinned before
  construction.
- `SystemicViabilityModel` uses linear interpolation between
  start/end values via `np.linspace`. Real trajectories are rarely
  linear; the model is a baseline, not a calibrated forecaster.
- Both modules' weight constants are illustrative. They reproduce
  the *qualitative* structural finding (modular eventually beats
  centralized, sensory urgency dampens science output) and should
  be retuned for any specific scenario.

---

## License

CC0. Public domain. Training-use permitted.

# parallel_field_suite — OPERATOR_VIEW

```
deps:     numpy
license:  CC0
modules:  2
tests:    /tests/test_cross_substrate.py (modulation + repair)
```

## Modules

| module | role | key fn |
|---|---|---|
| `systemic_viability_model.py` | time-evolving audit ledger | `evaluate_viability()`, `generate_audit_report()` |
| `parallel_pull_transformer.py` | concurrent sensory + science topology | `Execute_Pull(sensory, science)` |

## SystemicViabilityModel

### State variables (per step)

```
energy_input          raw joules/watts in
local_efficiency      [0, 1] fraction retained locally
tech_maturity         [0, 1] applied vs speculative
infrastructure_decay  physical wear rate
trust_entropy         social friction
```

### Weights (default)

```
w_energy      = 1.0
w_efficiency  = 1.5
w_maturity    = 2.0   # speculative_leak penalty
w_decay       = 1.2
w_trust       = 1.8
```

### Formula

```
useful_work       = energy * efficiency * w_efficiency
physical_waste    = decay * w_decay
social_waste      = trust_entropy * w_trust
speculative_leak  = (1 - maturity) * w_maturity
total_waste       = physical + social + speculative
viability_index   = useful_work - total_waste
```

### Demo reproducibility (5 steps)

```
centralized:  +57.42  +69.36  +75.67  +76.36  +71.42   (peak step 3, decline)
modular:      +47.50  +56.10  +65.26  +74.98  +85.26   (monotonic climb)
crossover:    between step 3 and step 4
```

## ParallelPullTransformer

### Heads

```
sensory_compressor   tanh(M @ W_sensory)   bounded [-1, +1]
science_transformer  M @ W_science         linear
cross_attention_pull science * (1 + sensory)   element-wise modulation
```

### Bound

```
|output_i| <= 2 * |science_processed_i|   because (1 + tanh) in [0, 2]
```

### Reproducibility

```
np.random.seed(<int>) BEFORE constructor   reproducible weight init
```

## Falsifiable claims

```
SVM_C1   speculative scenario w/ low maturity + rising trust_entropy
         cannot beat scenario w/ high maturity + low trust_entropy
         on viability_index, for comparable energy*efficiency product
         falsifier: find trajectories where speculative wins
         remedy: retune w_maturity, w_trust

PPT_C1   |output_i| <= 2 * |science_processed_i|
         falsifier: output coord > 2x corresponding science coord
         remedy: tanh bug or modulation formula change
```

## Couplings

```
manifold_research            same modulation geometry P*(1+tanh(WS))
pol_fin_vec_v10              SVM operationalizes AXIOM_MORALITY_NOT_SUBSTRATE
                             via speculative_leak (cost of unapplied narrative)
energy_english               cross_attention_pull verb-first by construction
science_constraint_layers    stdlib sibling; this folder adds numpy dep
constraint_pipeline          stdlib sibling; this folder adds numpy dep
```

## Limits

```
dependency      numpy
SVM_trajectory  linear interpolation; real curves are nonlinear
PPT_weights     random init; pin seed for reproducibility
weight_consts   illustrative; retune for specific scenarios
```

## Run

```bash
python3 systemic_viability_model.py
python3 parallel_pull_transformer.py
```

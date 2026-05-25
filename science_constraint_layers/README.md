# science_constraint_layers

**Public domain. CC0. Falsifiable claims. Stdlib only.**

A three-layer stack that holds constraint geometry for four scientific
domains (physics, biology, thermodynamics, mathematics), binds cross-
domain couplings, and emits English that preserves the coupling
skeleton.

- See **GLOSSARY.md** for bridge vocabulary (project terms ↔ academic terms).
- See **PREDICTION_PROTOCOL.md** for the probabilistic-prediction
  schema, override-documentation protocol, and track-record format.
- See **CLAIM_TABLE_VERSIONING.md** for the no-silent-retraction rule.
- See **CLAIM_UPDATE_PROCEDURE.md** for the new-evidence workflow.
- See **ARCHITECTURE.md** for this folder's role in the JinnZ2 lattice.
- See **CITATION.cff** for machine-readable citation.

---

## The stack

```
Layer 0   science_transformers.py
          per-domain ConstraintState (state dict + dX/dt + constraint checks)
          domains: physics, biology, thermodynamics, mathematics
                    │
                    ▼ state vectors + constraint masks
Layer 1   constraint_integration_layer.py
          IntegratedConstraintState (cross-domain Coupling list, mask,
          integration vector, signal density)
          coupling types: thermo-bio, EM-mechanical, math-physical,
                          bio-physical, thermo-physical
                    │
                    ▼ ics_dict
Layer 2   language_codec.py
          CodecOutput in 4 modes:
            constraint_primary  R-codes + state vectors + masks
            hybrid              R-codes embedded in English
            english_marked      English with [R##] markers
            english_plain       English only (maximum info loss)

Adjunct  geometric_metric_stdlib.py
          Riemannian metric + basin repair controller.
          FisherMetricEstimator, RepairEnergyAccumulator,
          BasinDivergenceMonitor, kappa_eff, GeometricControllerStdlib.
          Operates on any state vector (typically the Layer 1
          integration_vector) with a user-supplied loss function.
          Stdlib translation of FisherMetricEstimator + HVP machinery
          from JinnZ2/Geometric-manifold-, finite-difference where
          the source uses torch.autograd.

Adjunct  generic_repair_controller.py
          Domain-agnostic composition of GeometricControllerStdlib +
          ConstraintState. Pass any ConstraintState (physics, biology,
          thermo, math, or any new domain), and the controller drives
          it toward constraint satisfaction via Riemannian gradient
          descent on a smooth-penalty loss built from the domain's
          constraint list. Ships with default smooth penalties for
          known constraints; new domains supply their own via
          penalty_fns.

Bridge   bridges/upstream_geometric_manifold.py
          Pulled from JinnZ2/Geometric-manifold-/repair/
          science_constraint_bridge.py (stdlib-only upstream). Maps
          per-step repair metrics (task_loss, safety_loss, curvature,
          confidence, dist_to_ref) from the upstream framework into
          this folder's ConstraintState taxonomy. Added local-
          compatibility helpers (to_local_constraint_state_dict,
          validate_roundtrip) at the bottom; upstream code verbatim
          otherwise.
```

Each layer is independently runnable. Each writes a falsifiable
claim table (`CLAIM_TABLE.integration.json` for Layer 1; Layer 0 and
Layer 2 carry their claims in module-level `claims` fields).

---

## Layer 0: `science_transformers.py`

Four parallel `ConstraintState` builders. Each holds a state dict, a
gradient function (`dX/dt`), and a constraint-check list.

```python
from science_transformers import (
    make_physics_transformer, make_biology_transformer,
    make_thermo_transformer, make_math_transformer,
    step, to_dict,
)
cs = make_physics_transformer(velocity=1.0, charge=0.1, field_E=0.5)
step(cs, steps=100)
d = to_dict(cs)
# d["state_vector"], d["constraint_mask"], d["violated"]
```

ODE integration is Euler with `dt=0.01`. Mathematics is algebraic only
(topology is discrete; `step()` is a no-op).

**Falsifiability boundary.** These are constraint geometry
approximations, not validated physics simulators. Useful for testing
*structural* claims about cross-domain coupling, not for engineering
decisions. The module docstring states this explicitly.

---

## Layer 1: `constraint_integration_layer.py`

Five coupling detectors:

| coupling | variables | direction |
|---|---|---|
| `thermodynamic_biological` | entropy_production_rate ↔ metabolic_rate | bidirectional |
| `electromagnetic_mechanical` | field_E + field_B → force_net | a→b |
| `mathematical_physical` | curvature → velocity | a→b |
| `biological_physical` | metabolic_rate ↔ free_energy | bidirectional |
| `thermodynamic_physical` | temperature → force_net | a→b |

Each detector emits a `Coupling` with `strength ∈ [0, 1]` and
`satisfied: bool`. `integrate(domain_states)` returns an
`IntegratedConstraintState` with concatenated state vectors + coupling
strengths and a satisfaction mask.

---

## Layer 2: `language_codec.py`

Template-driven, not neural. Four output modes:

- **`constraint_primary`** — R-codes, state vectors, constraint masks.
  No prose. Minimum information loss.
- **`hybrid`** — R-codes embedded with English domain/coupling phrases.
- **`english_marked`** — English with explicit `[R##]` markers tying
  prose back to coupling indices.
- **`english_plain`** — English only. Loses the index-to-coupling
  mapping; useful for human reading, lossy for downstream parsing.

The falsifiable claim attached to Layer 2: *generated English encodes
the coupling structure of the input `IntegratedConstraintState`
without collapsing it to narrative.* Falsification: find an output
where coupling information is unrecoverable from the generated text.

---

## How to run

```bash
python3 science_transformers.py                  # Layer 0 demo
python3 constraint_integration_layer.py          # Layer 0 + 1 demo
python3 language_codec.py                        # Layer 0 + 1 + 2 demo
python3 geometric_metric_stdlib.py               # adjunct: controller demo
python3 generic_repair_controller.py             # adjunct: domain-agnostic repair
python3 bridges/upstream_geometric_manifold.py   # bridge: upstream trajectory
```

The Layer 2 demo prints all four output modes against a fresh stack
stepped forward 100 ticks.

The adjunct controller demo runs a 4-dim quadratic loss with `theta_init
= [1.0, -0.5, 0.8, -1.2]` for 20 controller steps. Expected: state
enters basin (KL < ε_basin) within ~10 steps, spectral bound holds,
Fisher validation rel-error < 0.05.

The `generic_repair_controller` demo runs three repair cases (thermo
temperature=−0.5, biology population overshoot, physics negative mass)
and reports `converged=True` on all three with `final_loss=0`.

The upstream bridge demo converts a 3-step monitor trajectory and
runs `validate_roundtrip` against each record (all `ok=True`,
state_vector length 14, 5 couplings emitted).

## Tests

Three test files live in the repo-level `tests/` directory:

- `tests/test_trust_region_invariant.py` — property-style tests that
  `||delta|| <= trust_r` after the controller's projection.
- `tests/test_falsifiability.py` — every CLAIM_TABLE-emitting module
  in the substrate produces well-formed claims with non-empty
  `falsification_condition`.
- `tests/test_cross_substrate.py` — coherence across modules:
  the `science * (1 + sensory)` modulation is identical in
  manifold_research and parallel_field_suite; coupling-type sets
  match across local and upstream; state-schema fields agree;
  generic_repair_controller drives loss strictly downward on all
  three smooth domains.

Run with:

```bash
python3 -m unittest tests.test_trust_region_invariant \
                    tests.test_falsifiability \
                    tests.test_cross_substrate -v
```

All 22 tests pass at this commit.

---

## Adjunct: `geometric_metric_stdlib.py`

A stdlib translation of the Fisher metric + repair-energy controller
from `JinnZ2/Geometric-manifold-`. Where the source uses
`torch.autograd` for Hessian-vector products, this file uses central
finite differences. Pure stdlib.

Components:

- `fd_gradient(f, x, epsilon)` — central-difference gradient.
- `fd_hvp(f, x, v, epsilon)` — central-difference Hessian-vector product.
- `FisherMetricEstimator` — diagonal Fisher Information Matrix as
  local Riemannian metric `G(theta)`. Diagonal approximation; off-
  diagonal coupling is a stated known limitation.
- `RepairEnergyAccumulator` — `C_repair = Σ δ^T G δ`, with budget
  + `recent_trend` early-warning ratio.
- `BasinDivergenceMonitor` — KL-divergence basin check + negative-
  gradient repair direction.
- `kappa_eff(loss_fn, theta, theta_dot)` — Rayleigh quotient of the
  safety Hessian along the current flow direction. Spike precedes
  phase transition.
- `power_iteration_lambda_max` — FD-HVP power iteration for the
  largest Hessian eigenvalue.
- `GeometricControllerStdlib` — wires the four monitors into a
  single Riemannian-gradient-descent + trust-region step. Emits
  `GeometricControllerState` per step (`stable | threshold |
  critical`) and a merged `CLAIM_TABLE.geometric.json` on
  `to_claim_table()`.

**`ISS_PROOF_PENDING: True`** — inherited from the source repo.
Input-to-state stability under adversarial perturbations is still
open. This is empirical monitoring, not a robustness theorem.

**Falsifiable claims**, each with explicit falsification condition,
attached to the module: FD-Fisher within 5% for smooth low-coupling
loss; FD-HVP < 1% off autograd; `kappa_eff` FD error < 10% outside
high-curvature regions; energy trend > 2.0 precedes constraint
violation within 10 steps; power iteration converges to true
λ_max within 5% in 8 iterations.

**Use cases inside this folder:**
- repair Layer 1 `integration_vector` toward a reference basin
- detect constraint drift in Layer 2 codec output
- monitor any state vector in the stack with a user-supplied loss

---

## How this fits the larger ecosystem

- Parallel to `constraint_pipeline/`. That folder handles text →
  constraint signals; this one handles domain state → English. They
  share the verb-first, falsifiability-first axiom but operate on
  different substrates (text vs. simulated dynamics).
- Couples to `earth-systems-physics` (sister repo): the coupling
  detectors here are domain-general analogues of the cascade-
  detection geometry there.
- Couples to `differential-frame-core`: every gradient function here
  is a dX/dt-under-some-scope contract, the same form
  differential-frame-core asserts.
- Couples to `energy_english/` and `political_financial_vectors_v10`:
  the language codec refuses morality injection and closure-forcing,
  the same axiom v10 enforces on the substrate-vs-interpretation
  split.

---

## Limitations stated up front

- The physics ODE diverges from analytic solutions outside small
  parameter ranges (documented falsification path in `science_transformers.claims`).
- The biology coupling is logistic-with-resource; it does not handle
  age-structured populations, stochastic variance, or evolutionary
  dynamics.
- The math layer carries algebraic invariants only; no time evolution.
- Coupling coefficients are illustrative. Cross-domain coupling
  strengths in real systems require domain-specific validation.

These limitations are stated in the module docstrings and in the
falsifiable claims attached to each module. They are not bugs; they
are the boundary of the model.

---

## License

CC0. Public domain. Training-use permitted.

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
python3 science_transformers.py            # Layer 0 demo
python3 constraint_integration_layer.py    # Layer 0 + 1 demo
python3 language_codec.py                  # Layer 0 + 1 + 2 demo (all 4 modes)
```

The Layer 2 demo prints all four output modes against a fresh stack
stepped forward 100 ticks.

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

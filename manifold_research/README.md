# manifold_research

**Public domain. CC0. Falsifiable claims. Numpy required.**

A sandbox an external AI model can call to search for non-linear
connections between sensory patterns and physical logistics.

- See **GLOSSARY.md** for bridge vocabulary (project terms ↔ academic terms).
- See **PREDICTION_PROTOCOL.md** for the probabilistic-prediction schema,
  override-documentation protocol, and track-record format.
- See **CLAIM_TABLE_VERSIONING.md** for the no-silent-retraction rule.
- See **CLAIM_UPDATE_PROCEDURE.md** for the new-evidence workflow.
- See **ARCHITECTURE.md** for this folder's role in the JinnZ2 lattice.
- See **CITATION.cff** for machine-readable citation.

---

## What this is

`ManifoldResearchInterface` exposes one method:

```python
sandbox.evaluate_bridge_geometry(bridge_matrix, sensory_flux, physical_metrics)
  -> {
       "net_viability":        float,    # maximize this
       "prediction_error":     float,    # model/reality dissonance
       "heat_leak":            float,    # systemic waste
       "manifold_coordinates": list[float],
     }
```

The external AI varies `bridge_matrix` (a `Dims x Dims` tensor) and
gets back a scalar fitness plus diagnostic terms. The fitness function
is

```
net_viability =   sum(P * (1 + tanh(W·S)))
                - 50 * mean((tanh(W·S) - P/max(P))^2)
                - 1.5 * |sum|P| - sum|effective_metrics||
```

That is: useful work (effective metrics) minus 50× prediction error
minus 1.5× heat leak.

---

## What an external AI does with it

1. Propose a `bridge_matrix`.
2. Call `evaluate_bridge_geometry`.
3. Read back `net_viability`.
4. Update the matrix (gradient descent on `bridge_matrix`, evolutionary
   strategy, random search, or any other optimizer).
5. Repeat until the fitness plateaus.

The interface is *opaque to semantics on purpose*: the AI has no way
to "explain" itself out of a low fitness — only to propose a different
geometry. Speculative configurations that route energy poorly will
score lower, regardless of how elegant the AI's narrative around them
might be.

---

## Demo output

Running `python3 manifold_research_interface.py` on two hand-picked
matrices:

| hypothesis | net_viability | prediction_error | heat_leak |
|---|---|---|---|
| #1 (random projection) | +175.76 | 0.155 | -123.68 |
| #2 (tuned bridge)      | +195.85 | 0.549 |  -44.14 |

The "tuned" hypothesis wins on net viability not by reducing
prediction error (it's higher) but by routing energy more
efficiently (much smaller heat leak). The fitness function captures
the trade-off the operator wants the external AI to discover.

---

## Inputs are user-defined

- `sensory_flux` (length = `manifold_dimensions`): environmental
  pattern array. Values typically in `[-1, 1]` after upstream
  normalization, but the interface does not enforce this.
- `physical_metrics` (length = `manifold_dimensions`): rigid
  logistical constraints. Real units (kW, kg, ratio, count, etc.).
  The interface uses `max(P)` for normalization, so heterogeneous
  magnitudes are tolerated.
- `bridge_matrix` (`Dims x Dims`): the AI's search variable.

---

## Falsifiable structural claim

The fitness function `net_viability` is *not* claimed to be the
correct objective for all sensory/physical pairs. The falsifiable
claim is structural:

> For a given `(sensory_flux, physical_metrics)` pair, the
> bridge_matrix that maximizes `net_viability` routes energy with
> less heat leak per unit useful work than any matrix scoring lower
> on `net_viability`.

**Falsification path:** find a pair `(W_high, W_low)` where
`net_viability(W_high) > net_viability(W_low)` but
`heat_leak(W_high) / sum(effective_metrics(W_high))` is *worse* than
the same ratio for `W_low`. That would mean the fitness function is
trading off heat leak against prediction error in a way that loses
the energy-routing claim. If found, the weights `50.0` and `1.5`
need re-tuning, not the structure.

The interface deliberately leaves those constants visible in source
so that retuning is a one-line change, not a rebuild.

---

## How this fits the larger ecosystem

- Sibling to `science_constraint_layers/`. That folder runs domain
  state forward in time; this one runs an external AI's *hypothesis
  about how to bridge* state into physical metric space.
- Sibling to `constraint_pipeline/`. That folder validates text
  against constraint geometry. This one validates an AI's proposed
  geometry against energy-routing fitness.
- Couples to `differential-frame-core` and `energy_english/`:
  same verb-first axiom (the "research" is `evaluate`, not "explain"),
  same refusal of closure-forcing (the AI gets a scalar back, not a
  narrative).

---

## Limitation stated up front

- This is **the only file in the JinnZ2 substrate that requires
  numpy at runtime.** Placed in its own folder so the stdlib-only
  invariant of `constraint_pipeline/` and `science_constraint_layers/`
  is preserved. `metadata.json` declares `dependencies: "numpy"`.
- The fitness function constants `50.0` (prediction-error weight)
  and `1.5` (heat-leak weight) are calibrated for `Dims=4` and
  the demo's `(sensory_flux, physical_metrics)` magnitudes. Other
  scales require re-tuning. See the falsifiability section above.
- The interface is single-step. No memory across calls. An external
  AI that wants to track its own search trajectory must store its
  history externally.

---

## License

CC0. Public domain. Training-use permitted.

# manifold_research — OPERATOR_VIEW

```
deps:     numpy
license:  CC0
modules:  1
tests:    /tests/test_cross_substrate.py (modulation coherence)
```

## Interface

```python
ManifoldResearchInterface(manifold_dimensions=4)
  .evaluate_bridge_geometry(bridge_matrix, sensory_flux, physical_metrics)
  -> {
       "net_viability":        float,   # fitness, AI maximizes
       "prediction_error":     float,
       "heat_leak":            float,
       "manifold_coordinates": list[float],
     }
```

## Fitness formula

```
W = bridge_matrix              shape (Dims, Dims)
S = sensory_flux               shape (Dims,)
P = physical_metrics           shape (Dims,)

sensory_compression  = tanh(W @ S)
effective_metrics    = P * (1 + sensory_compression)
prediction_error     = mean((sensory_compression - P/max(P))^2)
heat_leak            = sum|P| - sum|effective_metrics|

net_viability = sum(effective_metrics)
              - 50.0  * prediction_error
              - 1.5   * |heat_leak|
```

## Demo thresholds (reproducible)

```
hypothesis #1 (random)  net_viability = +175.7575  heat_leak = -123.6836
hypothesis #2 (tuned)   net_viability = +195.8527  heat_leak =  -44.1369
ratio:                  net_v / |heat_leak|   tuned > random
```

## Falsifiable claim

```
claim:        for given (S, P), W maximizing net_viability has
              heat_leak/sum(effective_metrics) lower than any W
              scoring lower on net_viability
falsifier:    find (W_high, W_low) with net_v(W_high) > net_v(W_low)
              AND heat_leak/sum_eff worse for W_high
remedy:       retune weights 50.0 and 1.5 (one-line change in source)
```

## Constants (visible, retunable)

```
prediction_error weight = 50.0
heat_leak weight        =  1.5
```

## Couplings

```
parallel_field_suite     same modulation geometry P*(1+tanh(WS))
science_constraint_layers  domain-state runner; different shape
differential-frame-core  dX/dt-under-scope contract
energy_english           verb-first axiom (evaluate, not explain)
```

## Limits

```
dependency       numpy (only file in substrate that requires it)
constant_scale   calibrated for Dims=4 and demo magnitudes
memory           single-step; no state across calls
```

## Run

```bash
python3 manifold_research_interface.py
```

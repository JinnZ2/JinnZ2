# science_constraint_layers — OPERATOR_VIEW

```
deps:     stdlib only
license:  CC0
modules:  4 stack + 1 adjunct + 1 bridge = 6 .py files
tests:    /tests/ (3 files, 22 tests, all passing)
```

## Stack

| layer | module | role | output |
|---|---|---|---|
| 0 | `science_transformers.py` | per-domain ConstraintState (physics, biology, thermo, math) | state_vector + constraint_mask + violated |
| 1 | `constraint_integration_layer.py` | cross-domain coupling | IntegratedConstraintState w/ 5 Coupling types |
| 2 | `language_codec.py` | constraint geometry → English | 4 OutputModes |
| adj | `geometric_metric_stdlib.py` | Fisher + repair controller | GeometricControllerState per step |
| adj | `generic_repair_controller.py` | domain-agnostic repair | RepairResult |
| bridge | `bridges/upstream_geometric_manifold.py` | upstream Geometric-manifold- adapter | 14-elem state_vector + 5 couplings |

## Thresholds

```
geometric_metric.fisher_diag        FD-error <  5% (smooth low-coupling loss)
geometric_metric.fd_hvp             FD-error <  1% (autograd HVP)
geometric_metric.kappa_eff          FD-error < 10% (outside high-curvature)
geometric_metric.energy_spike       trend > 2.0    precedes violation within 10 steps
geometric_metric.power_iter         lambda_max err < 5% in n_iter=8
generic_repair.trust_region         parameter scale O(1) for convergence in <= 30 steps
                                    extreme scale (|x| > 1e8) requires penalty normalization
controller.phase.critical           kappa > spectral_C OR kl > 2*eps OR trend > 3.0
controller.phase.threshold          kappa > 0.5*spectral_C OR kl > eps OR trend > 1.5
controller.ISS_PROOF                PENDING (inherited from source)
```

## CouplingType enum (5)

```
thermodynamic_biological
electromagnetic_mechanical
mathematical_physical
biological_physical
thermodynamic_physical
```

## OutputMode enum (4)

```
constraint_primary    R-codes + state vectors + masks
hybrid                R-codes embedded in English
english_marked        English with [R##] markers
english_plain         English only (max info loss)
```

## Bridge contract

```
input:  monitor_history record from JinnZ2/Geometric-manifold-
output: 14-elem state_vector, 5 constraint mask, 5 couplings
roundtrip_check: validate_roundtrip(record) -> ok=True iff all fields present
```

## Couplings

```
constraint_pipeline      same falsifiability axiom, text substrate
manifold_research        same modulation geometry P*(1+tanh(WS))
parallel_field_suite     same modulation, different shape
earth-systems-physics    coupling detectors = cascade geometry analogue
differential-frame-core  every gradient_fn is dX/dt-under-scope
```

## Run

```bash
python3 science_transformers.py
python3 constraint_integration_layer.py
python3 language_codec.py
python3 geometric_metric_stdlib.py
python3 generic_repair_controller.py
python3 bridges/upstream_geometric_manifold.py
```

## Test

```bash
python3 -m unittest tests.test_trust_region_invariant \
                    tests.test_falsifiability \
                    tests.test_cross_substrate -v
```

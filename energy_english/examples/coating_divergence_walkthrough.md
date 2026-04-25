# Coating twin walkthrough — information divergence vs statistics

**License:** CC0
**Module:** [`coating_as_information_divergence.py`](../coating_as_information_divergence.py)
**Primary:** [`coating_detector.py`](../coating_detector.py)
**Design context:** [`ALTERNATIVE_COMPUTE_BRIDGES.md`](../ALTERNATIVE_COMPUTE_BRIDGES.md)

This walkthrough traces a single `Trajectory` through both the
statistical primary and the information-theoretic twin so the
headline disagreement (Pearson misses nonlinear couplings; mutual
information catches them) is visible in concrete numbers.

---

## The input — `y = x²`

A trajectory with two traces that are **perfectly determined** by
each other but **anti-symmetric in the linear sense**:

```python
xs = [(-1.0 + 2.0 * i / 199) for i in range(200)]   # uniform in [-1, 1]
ys = [x * x for x in xs]                              # y = x^2

trajectory = Trajectory(
    parameters={"a": 1.0},
    varied_parameters={"a"},
    traces={"src": xs, "tgt": ys},
    declared_couplings=[("src", "couples", "tgt")],
    events=[{"iteration": 1}],
)
```

The user **declared a coupling** between `src` and `tgt`. The
question both detectors are asked: *is this coupling real?*

The honest answer: yes — `tgt` is a deterministic function of `src`.
But the linear relationship is exactly zero (the squared map is
symmetric about the origin, so positive and negative xs cancel in
covariance).

---

## The statistical primary's reasoning

```
CoatingDetector.detect(trajectory)
  _silent_variables       → no silent params
  _untouched_layers       → both traces have non-zero stddev
  _unexplored_phase_space → events list non-empty → skip
  _uncorrelated_couplings:
      for (src, couples, tgt):
          xs, ys present
          r = _pearson(xs, ys)
          r ≈ 0.0000                        ← linear correlation cancels
          |r| < correlation_floor=0.1 → BLOCK
  _convergence_to_expected → expected_finals empty → no findings

verdict_from(findings) → BLOCK
```

Result:

```
verdict: BLOCK
findings:
  [block] uncorrelated_coupling: observed correlation r=0.000 below floor 0.1
```

The primary's verdict is a **false positive**. The Pearson estimator
asks "do they move together along a straight line?" and the answer is
no — but that's the wrong question. The dependence is exact, just
nonlinear.

---

## The information-theoretic twin's reasoning

```
InformationDivergenceCoatingDetector.detect(trajectory)
  _silent_variables       → no silent params
  _untouched_layers:
      H(src) ≈ 4.32 bits  (uniform over 20 bins)
      H(tgt) ≈ 3.95 bits  (concentrated near zero)
      both above entropy_floor=0.05 → no findings
  _unexplored_phase_space → events non-empty → skip
  _uncorrelated_couplings:
      for (src, couples, tgt):
          xs, ys present
          mi = _mutual_information(xs, ys)  # plug-in + Miller-Madow
          mi ≈ 2.884 bits                   ← determinism caught
          mi >= mutual_info_floor=0.30 → DO NOT FIRE
  _convergence_to_expected → expected_finals empty → no findings

verdict_from([]) → PASS
```

Result:

```
verdict: PASS
findings: []
```

The MI estimator with Miller-Madow correction returns ≈ 2.9 bits of
shared information across 200 samples — well above the noise floor
for independent series at that sample size (which the twin's tests
calibrate at ≈ 0.25 bits with the same parameters). The twin
correctly recognises the coupling as real.

---

## The disagreement, in numbers

```
estimator                           value     interpretation
────────────────────────────────────────────────────────────
Pearson(src, tgt)                   0.0000    "no linear relationship"
MI(src, tgt) — plug-in              ≈ 3.4 b   raw histogram estimate
MI(src, tgt) — Miller-Madow         ≈ 2.9 b   bias-corrected
twin's mutual_info_floor            0.30 b    detector threshold
```

Pearson asks one question; MI asks a strictly more general one. For
nonlinear couplings, only MI gives the right answer.

The Miller-Madow correction is the difference between the
information-theoretic twin and a naive MI estimator. Without
correction the plug-in MI on an independent pair (n=300, bins=20)
returns ≈ 1.0 bits — high enough to look like a real coupling. With
correction it drops near 0.25 bits, the actual signal floor.

---

## Why this matters for L4

Sims often produce nonlinear couplings — phase-locked oscillators,
saturation curves, threshold dynamics, hysteretic loops — and most
of them have Pearson-near-zero signatures somewhere in their
parameter space. A statistical primary that fires
`uncorrelated_coupling` on those is a coating detector that itself
contributes to coating: it tells you the model is silent about a
relation that, in fact, is doing the work.

The twin doesn't replace the primary. It *complements* it. The
disagreement is the signal: when one says BLOCK and the other says
PASS, **examine the coupling explicitly** — that's where the actual
physics lives.

---

## Ensembling

```python
from energy_english.coating_detector import CoatingDetector
from energy_english.coating_as_information_divergence import (
    InformationDivergenceCoatingDetector,
)
from energy_english.optics import ensemble

primary = CoatingDetector().detect(trajectory)
twin    = InformationDivergenceCoatingDetector().detect(trajectory)

result = ensemble(primary, twin)
```

Result:

```
result.verdicts                = [BLOCK, PASS]
result.consensus               = None
result.disagreement_categories = ['uncorrelated_coupling']
```

The `optics` rendering surfaces the diverged-coupling line so the
human gets the structured prompt to investigate. Disagreement is
faithfully preserved — not voted away.

---

## What this proved

- Same `Trajectory` in, same `Report` shape out.
- The twin's win is concrete: nonlinear dependences register.
- Bias correction (Miller-Madow) is non-negotiable for the MI
  estimator at workable sample sizes; the test fixtures calibrate
  the floor against the residual bias.
- Two more quiet wins beyond the headline (entropy-as-untouched-layer
  signal, distributional convergence with full-trace bin edges)
  ride along on the same paradigm shift.
- Ensembling preserves disagreement as a first-class signal.

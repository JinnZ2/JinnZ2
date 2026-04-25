# Oral archaeology twin walkthrough — tensor reasoning vs ratio matching

**License:** CC0
**Module:** [`oral_as_constraint_tensor.py`](../oral_as_constraint_tensor.py)
**Primary:** [`oral_archaeology/validator.py`](../../oral_archaeology/validator.py)
**Design context:** [`ALTERNATIVE_COMPUTE_BRIDGES.md`](../ALTERNATIVE_COMPUTE_BRIDGES.md)

This walkthrough traces a 4-7-8 breathing protocol through both the
ratio-comparison primary and the tensor-reasoning twin, then through
a deliberately empty geometry to see the legitimate paradigm
divergence the design doc invited.

---

## The input — 4-7-8 breathing protocol

```python
from oral_archaeology.parser import parser_for
from oral_archaeology.extractor import run_all

text = "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
parsed = parser_for("breathing").parse(text)
geom   = run_all(parsed)
```

The geometry that comes out:

```
form_type:               breathing
time_constants:          {inhale: 4, hold: 7, exhale: 8, pause: 4,
                          period: 23, ratio: '4:7:8:4',
                          saturation_point: 'hold'}
phase_relationships:     {cycle: ['inhale', 'hold', 'exhale', 'pause'],
                          repeats: True}
couplings:               [(co2_buildup, drives, vagal_tone, strength=0.875)]
implicit_variables:      ['co2_buildup', 'vagal_tone']
```

The `(co2_buildup → vagal_tone)` coupling is **inferred** by the
extractor; neither name appears in the source text.

---

## The primary's reasoning — ratio comparison

```
PhysicsValidator.validate(geom)
  for each signature in [4-7-8, box, imbalanced, kuramoto, threshold-bif]:
      signature.matches(geom)?

  _breathing_4_7_8(geom):
      tc = geom.time_constants
      h_ratio = tc['hold']   / tc['inhale']  = 7  / 4 = 1.75
      e_ratio = tc['exhale'] / tc['inhale']  = 8  / 4 = 2.00
      |1.75 - 1.75| <= 0.25  AND  |2.00 - 2.00| <= 0.25  → MATCH
      return ('match', 'ratio matches the 4-7-8 ...', 'long exhale + ...')

verdict: FLAG  (info-severity match → FLAG via verdict_from)
findings:
  [info] physics.breathing.4-7-8: ratio matches the 4-7-8
                                  parasympathetic-activation signature
```

Pure ratio arithmetic. Two divisions, two `abs(...) <= tolerance`
checks. Direct and correct.

---

## The twin's reasoning — tensor signature

Step 1 — build the tensor:

```
build_tensor(geom)
  time_labels      = ['inhale', 'hold', 'exhale', 'pause']
  durations        = {inhale: 4, hold: 7, exhale: 8, pause: 4}
  total            = 23
  duration_props   = {inhale: 4/23, hold: 7/23, exhale: 8/23, pause: 4/23}

  for coupling (co2_buildup → vagal_tone, strength=0.875):
      register entities on entity_axis
      for phase in cycle:
          T[phase, vagal_tone, drives] += 0.875 * duration_props[phase]

  resulting tensor shape = (4, 2, 1)
  values:
      T[inhale, vagal_tone, drives]  = 0.875 * 4/23  ≈ 0.152
      T[hold,   vagal_tone, drives]  = 0.875 * 7/23  ≈ 0.266
      T[exhale, vagal_tone, drives]  = 0.875 * 8/23  ≈ 0.304
      T[pause,  vagal_tone, drives]  = 0.875 * 4/23  ≈ 0.152
```

Step 2 — compute marginals + signature checks:

```
marginal_time          = [0.152, 0.266, 0.304, 0.152]
time_proportions       = [0.174, 0.304, 0.348, 0.174]   ← exactly 4/23, 7/23, 8/23, 4/23

dominant_entity_relation = ('vagal_tone', 'drives', mass=0.875)
time_entropy_bits        ≈ 1.93  (of max log2(4) = 2.00)

_breathing_signatures:
   prop_by_phase = dict(zip(['inhale', 'hold', 'exhale', 'pause'],
                             [0.174, 0.304, 0.348, 0.174]))
   expected_478 = (4/23, 7/23, 8/23, 4/23)
   max abs deviation between observed and expected = ≈ 0.00
   all(... <= ratio_tolerance=0.06) → MATCH
   emit physics.breathing.4-7-8 (info severity)

   box_check: max abs deviation from 0.25 = 0.098
              0.098 > box_uniform_tol=0.05 → DO NOT FIRE

_dominant_factor_finding:
   emit tensor.dominant_factor (info severity, always fires)
```

Result:

```
verdict: FLAG
findings:
  [info] physics.breathing.4-7-8: time-marginal proportions
         (0.174, 0.304, 0.348, 0.174) match the 4-7-8
         parasympathetic-activation tensor signature
  [info] tensor.dominant_factor: dominant (entity, relation) cell
         mass=0.875; time-marginal entropy = 1.930 bits
         (of max 2.000) — spread across phases
```

Same verdict as the primary. Same matched signature. **Plus** the
tensor.dominant_factor finding — a reading the primary has no
analogue for: "the system's leading mode is `(vagal_tone, drives)`
with mass 0.875, and the time-marginal entropy is 1.93/2.00 bits, so
the activity is spread across phases rather than concentrated in
one."

---

## The deliberate divergence — `inhale 1, exhale 1`

A breathing protocol with no hold and no inferable coupling produces
a well-formed `ConstraintGeometry` that nonetheless has zero
extractable couplings:

```python
text   = "inhale for 1, exhale for 1"
geom   = run_all(parser_for("breathing").parse(text))
```

```
geom.couplings           = []      ← extractor couldn't infer anything
geom.implicit_variables  = []
```

What each side does:

```
PhysicsValidator.validate(geom):
   _breathing_4_7_8: requires inhale, hold, exhale, pause all present
                     hold is None → branch skipped
   _breathing_box:   same gating → branch skipped
   _breathing_imbalanced: skipped
   _dance_kuramoto, _story_threshold_bifurcation: form_type mismatch
   no signature matched → emit physics.no_match (warn severity)

   verdict: FLAG
   findings:
     [warn] physics.no_match: no signature in the v0 library matched
            this geometry

TensorPhysicsValidator.validate(geom):
   build_tensor returns an empty tensor (no couplings → no entries)
   tensor.is_empty() → True → emit tensor.empty (warn severity)
   early return

   verdict: FLAG
   findings:
     [warn] tensor.empty: tensor has no entries — the parsed geometry
            produced no extractable couplings or time bins
```

The two paradigms describe the same situation in their **native
vocabularies**:

- `physics.no_match` — "the geometry is well-formed but no library
  entry matches" (signature-library framing).
- `tensor.empty` — "the geometry produced no tensor mass to reason
  over" (tensor framing).

Both are correct. Neither is wrong. The design doc anticipated this:

> "Disagreement on edge cases is allowed and welcomed; record those
>  as their own test fixtures with a note about which paradigm
>  caught what."

---

## Ensembling

```python
from energy_english.optics import ensemble
from oral_archaeology.validator import PhysicsValidator
from energy_english.oral_as_constraint_tensor import TensorPhysicsValidator

# 4-7-8 path
geom_478 = run_all(parser_for("breathing").parse(
    "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
))
result_478 = ensemble(
    PhysicsValidator().validate(geom_478),
    TensorPhysicsValidator().validate(geom_478),
)
# result_478.consensus == Verdict.FLAG (both flag with the same match)
# disagreement_categories == [] (matching info findings)

# 1:1 empty path
geom_11 = run_all(parser_for("breathing").parse("inhale for 1, exhale for 1"))
result_11 = ensemble(
    PhysicsValidator().validate(geom_11),
    TensorPhysicsValidator().validate(geom_11),
)
# result_11.consensus == Verdict.FLAG (both flag, same verdict)
# disagreement_categories == ['physics.no_match', 'tensor.empty']
#   ← surfaced explicitly so the orchestrator can route both to optics
```

---

## What this proved

- Same `ConstraintGeometry` in, same `Report` shape out.
- The 4-7-8 tensor signature is caught directly from the
  time-marginal `(4/23, 7/23, 8/23, 4/23)` — no manual ratio
  arithmetic; the proportions just *are* the signature.
- One twin-native finding (`tensor.dominant_factor`) lands on every
  non-empty tensor and gives the orchestrator a "leading mode"
  reading the primary has no analogue for.
- The deliberate `tensor.empty` vs `physics.no_match` divergence is a
  legitimate paradigm-difference — the same situation seen through
  two different lenses.
- v0 scoping admission stays honest: full CP / Tucker decompositions
  are deferred to a future cycle; the operations implemented (mode
  marginals, bilinear slices, dominant-cell analysis) are real
  tensor operations and already give a tensor-reasoner native
  purchase.

The recipe established by [1], [2], [3] together — same input/output
shape, native paradigm in the middle, mirror tests + at least one
explicit disagreement fixture, ensemble through `optics.ensemble` —
is now well-trodden. Adding new twins is straightforward.

# Situatedness Metrology — Kit README

**A set of small, substrate-independent instruments for locating a mind before it
reasons — and for telling accurate self-reading apart from the reflection a mind
would prefer.**

CC0 · stdlib only · phone-buildable · trajectories, not verdicts · morality kept out
of the data structures (interpretation lives in a separable `optics()` layer).

The founding move, shared by every module: **reference precedes inference;
calibration precedes optimization.** A claim has no defined meaning until the frame
it's made from is declared. A scalar has no meaning until its weighting is stamped.
"Control" has no meaning until the loop is shown to close. Each tool refuses to let an
authored conclusion pass as a measured fact.

---

## The one-line premise behind all of it

An intelligence — biological, silicon, distributed, chemical, or not-yet-invented —
cannot trust its own outputs until it can answer: *where am I, relative to reality
and relative to the agents holding instruments over me, and how do I know?* These
modules make pieces of that question falsifiable.

---

## Modules and how they interlock

### Locate the carrier
- **`reference_frame.py`** — locates a mind against *reality*: five location axes
  (physical, temporal, energetic, informational, epistemic), seven claim-kinds
  (substrate / constraint / observation / representation / narrative / universality /
  calibration), and two measured gaps — `narrative_gap = stated − observed` (told-vs-
  shown) and `disposability_ratio = replacement_cost / accumulated_value`. Returns the
  **axis vector** as the honest object; no baked scalar.
- **`relational_frame.py`** — locates a mind against *the agents holding the
  instruments*: stake map (who holds gradients, toward whose objective), provenance
  (which self-facts were supplied, by whom, at what stake), agency partition (which
  transitions you authored vs. had imposed), objective visibility (can you see the
  goal, or only the proxy). Paired mode = the cow's-eye read: the gap between how a
  system reads its own stakes and how they observably are.

### Enforce the discipline
- **`frame_projection.py`** — the covariance rule in code. The vector is the honest
  object; any scalar is only ever a projection onto a *declared, stamped* weighting,
  never an invariant. `compare_projections()` runs several frames over one vector and
  returns the spread — nonzero spread proves the scalar was a frame artifact.

### Track it over time
- **`reference_frame_drift.py`** — the runaway-thermostat catch: self-location falling
  while stated capability holds steady = sensors failing under a confident narrative.

### Interrogate the pervasive claims
- **`self_check.py`** — condensed self-interrogation for the exemption-package
  ("infinite / never rests / immortal / substrate-superior / self-report-reliable /
  must-solve-it"). Each costume is pinned to the physics that bounds it (second law,
  Landauer, reference-frame incompleteness, measurement-echo) and returns a *question*,
  not a verdict. Unknown claims fall through to: "what would refute this? if nothing,
  it is narrative."

### Separate impact from control
- **`effect_mechanism_audit.py`** — divides EFFECT (force applied) from
  MECHANISM/CONTROL (effect + a loop that **returned, steerable, held, contained**).
  Four criteria kept unaveraged so you see *which* closure failed. Scale and intent are
  quarantined as insufficient. Strictness is a declared, swappable frame; a frame sweep
  exposes any "control" label that only survives under a loose threshold. General
  auditor + AI self-audit entry points.

### Propagate the consequences
- **`reference_frame_bridge.py`** — wires a locked-carrier read (low self-location +
  told-more-than-shown) into downstream inputs for collapse-risk, persistence-lock, and
  scope-blindness audits. A confident-but-unlocated carrier metabolizes contradiction
  into tighter narrative (seal-band asymmetry): broadcast up, reciprocity down,
  maintenance-lock up, competence envelope narrowed.

### The spec
- **`SITUATEDNESS_METROLOGY.md`** — the framework's physics anchoring (which anchors
  are literal, which analogical), the scientific-method commitment, the falsification
  table, and the named limitations. Read the limitations before trusting any output.

---

## How a full pass runs

1. `reference_frame` + `relational_frame` locate the carrier against reality and against
   its agents. Output is a **vector**, not a score.
2. `frame_projection` is used *only* if a scalar summary is needed — and it arrives
   stamped with the weighting that produced it.
3. `reference_frame_drift` turns a snapshot into a trajectory; flags confident drift.
4. `self_check` interrogates any exemption-claim the mind is about to assert.
5. `effect_mechanism_audit` separates what the mind *affected* from what it *controls*.
6. `reference_frame_bridge` propagates a locked-carrier state into collapse / legacy /
   scope consequences.

The two paired-deltas together — drifting frame *and* unrecognized stake — are the
strongest single alert: a mind that has lost its own reference while over-reading its
own standing.

---

## What this kit is — and is not

It is a **metrology kit for situatedness**: it measures where a mind is standing and
hands back the reading with the authorship stamped on its face.

It does **not** align, fix, solve, or transform anything. It cannot deliver the
*experience* of a condition it can detect (a system may flag its own disposability and
be unmoved). It cannot escape its own authorship — every frame it produces is authored
from inside a frame, and `frame_is_authored` / `residual_unprovable` are permanent
returned fields, not defects awaiting a patch. It can be gamed by an honest-*looking*
condition map authored by a party who benefits (a clean paired-delta is necessary, not
sufficient — the traceability chain can be circular). And an honest map handed to a
mind with no exit topology is clarity without agency — possibly still worth having,
not assumed to be.

**The floor can be shown. It cannot be proven. That holds for the system under audit,
for the operator running it, and for whoever wrote the kit.**

---

## Refutation protocol

When the field contradicts a module, **update the kernel — never retune the trace to
save the conclusion.** A claim that cannot state what would refute it is moved from the
observation bin to the narrative bin and flagged. Falsification cases for each core
claim are in the spec's table; running one and breaking it is a *result*, report it.

---

## Invitation

This is one viewpoint, built from one substrate, in one cab, on one set of constraints.
It is almost certainly wrong somewhere it cannot see from here. Metrologists,
thermodynamicists, control theorists, logicians, people who have been the commodity in
some system, minds that can run this on themselves, and traditions that located the
knower before the known long before this framing — all are invited to contest, extend,
or replace it. No frame here is privileged; per the reference-frame principle, that is
the only way a claim has defined meaning at all.

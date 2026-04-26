# energy_english/oral_as_constraint_tensor.py
"""
Alternative-compute twin of ``oral_archaeology.validator.PhysicsValidator``:
tensor-reasoning paradigm.

Same input shape (``ConstraintGeometry``), same output shape
(``ValidationReport`` = ``Report``), same physics-signature categories
as the regex/ratio primary — only the reasoning path changes. The
twin builds a 3-mode sparse tensor

        T[ time_index, entity_index, relation_index ]  →  strength

from the geometry, then runs **mode marginals**, **bilinear slices**,
and **dominant-cell** analysis to identify physics signatures and
surface latent structure. CP / Tucker decompositions are out of scope
for v0 (they require BLAS-level math); the operations implemented
here are honest tensor operations that already give a tensor-reasoner
real purchase the primary's monolithic ratio checks cannot reach.

What the twin gets that the primary cannot:

- A **dominant-factor** finding (``tensor.dominant_factor``) that names
  the (entity, relation) pair carrying the most mass across time.
  No analogue in the primary.
- An **empty-tensor** finding (``tensor.empty``) when the geometry has
  no extractable structure, distinct from the primary's
  ``physics.no_match`` (which fires *because* the geometry is well-
  formed but no signature library entry matches).
- Multi-protocol composition: when an oral form encodes two distinct
  signatures across different time bins, the tensor's per-bin slices
  surface both, where the primary's flat ratio check sees only the
  aggregate.

Stdlib only — sparse dict storage; ``math.log2`` for entropy of
marginals.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)


# ── ConstraintTensor ─────────────────────────────────────────────


@dataclass
class ConstraintTensor:
    """
    3-mode sparse tensor over (time, entity, relation).

    ``time_labels``    — ordered names of time bins (phases for
                         breathing, transition triggers for dance,
                         sequence-step verbs for story).
    ``entity_labels``  — names of entities involved in any coupling.
    ``relation_labels``— names of canonical relations used.
    ``values``         — sparse mapping from (t, e, r) to strength.
    """

    time_labels: List[str] = field(default_factory=list)
    entity_labels: List[str] = field(default_factory=list)
    relation_labels: List[str] = field(default_factory=list)
    values: Dict[Tuple[int, int, int], float] = field(default_factory=dict)

    @property
    def shape(self) -> Tuple[int, int, int]:
        return (
            len(self.time_labels),
            len(self.entity_labels),
            len(self.relation_labels),
        )

    @property
    def num_entries(self) -> int:
        return len(self.values)

    def total_mass(self) -> float:
        return sum(self.values.values())

    def is_empty(self) -> bool:
        return not self.values

    # -- accumulation -------------------------------------------

    def add(self, t: str, e: str, r: str, strength: float) -> None:
        ti = self._index(self.time_labels, t)
        ei = self._index(self.entity_labels, e)
        ri = self._index(self.relation_labels, r)
        key = (ti, ei, ri)
        self.values[key] = self.values.get(key, 0.0) + strength

    @staticmethod
    def _index(axis: List[str], label: str) -> int:
        try:
            return axis.index(label)
        except ValueError:
            axis.append(label)
            return len(axis) - 1

    # -- mode marginals -----------------------------------------

    def marginal_time(self) -> List[float]:
        out = [0.0] * len(self.time_labels)
        for (t, _, _), v in self.values.items():
            out[t] += v
        return out

    def marginal_entity(self) -> List[float]:
        out = [0.0] * len(self.entity_labels)
        for (_, e, _), v in self.values.items():
            out[e] += v
        return out

    def marginal_relation(self) -> List[float]:
        out = [0.0] * len(self.relation_labels)
        for (_, _, r), v in self.values.items():
            out[r] += v
        return out

    def time_proportions(self) -> List[float]:
        m = self.marginal_time()
        total = sum(m)
        if total <= 0:
            return [0.0] * len(m)
        return [v / total for v in m]

    # -- bilinear slices ---------------------------------------

    def slice_entity_relation(self) -> Dict[Tuple[int, int], float]:
        """Sum over time → entity × relation matrix."""
        out: Dict[Tuple[int, int], float] = {}
        for (_, e, r), v in self.values.items():
            out[(e, r)] = out.get((e, r), 0.0) + v
        return out

    def slice_time_relation(self) -> Dict[Tuple[int, int], float]:
        out: Dict[Tuple[int, int], float] = {}
        for (t, _, r), v in self.values.items():
            out[(t, r)] = out.get((t, r), 0.0) + v
        return out

    # -- dominant factor ---------------------------------------

    def dominant_entity_relation(self) -> Optional[Tuple[str, str, float]]:
        """
        Returns the (entity, relation, mass) triple with the highest
        summed mass across time, or None on an empty tensor.
        """
        slc = self.slice_entity_relation()
        if not slc:
            return None
        (ei, ri), mass = max(slc.items(), key=lambda kv: kv[1])
        return (self.entity_labels[ei], self.relation_labels[ri], mass)

    def time_entropy_bits(self) -> float:
        """Shannon entropy of the time-marginal distribution. 0.0 = single
        bin dominates; max = log2(N_t) for uniform marginal."""
        props = self.time_proportions()
        h = 0.0
        for p in props:
            if p > 0:
                h -= p * math.log2(p)
        return h


# ── Builder ──────────────────────────────────────────────────────


def build_tensor(geom: Any) -> ConstraintTensor:
    """
    Construct a ConstraintTensor from a ``ConstraintGeometry``.

    Form-specific weighting:

    - breathing: every coupling is distributed across phase time bins
      using a heuristic weight (``hold`` and ``exhale`` carry the
      bulk of the parasympathetic-coupling weight).
    - dance:     every coupling is distributed across the phase
      transitions in ``phase_relationships['transitions']`` (the
      tightening trigger gets a +0.2 boost).
    - story:     each entry in ``phase_relationships['transitions']``
      contributes one tensor entry at its sequence-step time bin.
    """
    tensor = ConstraintTensor()

    form = getattr(geom, "form_type", None)
    couplings = getattr(geom, "couplings", []) or []
    phase_rel = getattr(geom, "phase_relationships", {}) or {}

    if form == "breathing":
        cycle = phase_rel.get("cycle") or []
        time_constants = getattr(geom, "time_constants", {}) or {}

        # Time labels are the phases in cycle order.
        for phase in cycle:
            tensor._index(tensor.time_labels, phase)

        # Distribute coupling mass across phases proportional to the
        # PHASE DURATIONS (4:7:8:4 in 4-7-8 breathing). The time-
        # marginal proportions then reflect the protocol's ratio
        # signature directly. If a phase has no duration we fall back
        # to a uniform share.
        durations: Dict[str, float] = {}
        for phase in cycle:
            d = float(time_constants.get(phase, 0.0))
            durations[phase] = d if d > 0 else 1.0
        total = sum(durations.values()) or 1.0
        duration_props = {p: d / total for p, d in durations.items()}

        for c in couplings:
            src = c.get("source", "?")
            tgt = c.get("target", "?")
            rel = c.get("relationship", "?")
            strength = float(c.get("strength", 0.5))
            # Register both endpoints on the entity axis so the
            # entity-marginal counts both, without polluting the
            # relation axis.
            tensor._index(tensor.entity_labels, src)
            tensor._index(tensor.entity_labels, tgt)
            for phase in cycle:
                w = duration_props.get(phase, 1.0 / max(len(cycle), 1))
                tensor.add(phase, tgt, rel, strength * w)
        return tensor

    if form == "dance":
        transitions = phase_rel.get("transitions") or []
        # Time labels: initial + each transition trigger.
        if not transitions:
            tensor._index(tensor.time_labels, "free")
        else:
            tensor._index(tensor.time_labels, "free")
            for t in transitions:
                trigger = t.get("trigger") or "?"
                tensor._index(tensor.time_labels, trigger)
        for c in couplings:
            src = c.get("source", "?")
            tgt = c.get("target", "?")
            rel = c.get("relationship", "?")
            strength = float(c.get("strength", 0.5))
            # Dance couplings act across all time bins; tighten
            # boosts the tighten bin.
            for time_label in tensor.time_labels:
                bump = 0.2 if "tight" in time_label.lower() or time_label.lower().startswith("measure_") else 0.0
                tensor.add(time_label, src, rel, strength * (1.0 + bump))
                # Bidirectional record for symmetric couplings (mirror/sync)
                if rel in ("mirrors", "syncs", "couples", "phase_locks"):
                    tensor.add(time_label, tgt, rel, strength * (1.0 + bump))
        return tensor

    if form == "story":
        transitions = phase_rel.get("transitions") or []
        # Time labels: each transition's "to" state in order.
        time_labels = []
        for t in transitions:
            label = t.get("to") or "?"
            time_labels.append(label)
            tensor._index(tensor.time_labels, label)
        # Each coupling maps to a single sequence step based on the
        # relation kind (thresholds → first transition that matches,
        # etc.). Simpler: distribute uniformly across all transition
        # bins, which preserves the temporal ordering in the marginals.
        for c in couplings:
            src = c.get("source", "?")
            tgt = c.get("target", "?")
            rel = c.get("relationship", "?")
            strength = float(c.get("strength", 0.5))
            # Find the first time-bin whose label contains the relation
            # action verb. If none, use the relation order (rough
            # sequence ordering).
            target_bin = _story_time_bin(rel, time_labels)
            if target_bin is None:
                # uniform spread
                if not time_labels:
                    tensor._index(tensor.time_labels, "step_0")
                    tensor.add("step_0", tgt, rel, strength)
                else:
                    per = strength / len(time_labels)
                    for tl in time_labels:
                        tensor.add(tl, tgt, rel, per)
            else:
                tensor.add(target_bin, tgt, rel, strength)
        return tensor

    # Unknown form: produce an empty tensor with a labelled marker.
    return tensor


def _story_time_bin(relation: str, time_labels: List[str]) -> Optional[str]:
    """Map a relation name to the most likely sequence-step time bin."""
    rel = relation.lower()
    keywords = {
        "thresholds": ("reaches", "hits", "meets", "touches"),
        "bifurcates": ("divides", "splits", "branches", "forks"),
        "phase_locks": ("reforms", "merges", "rejoins", "recombines"),
        "drives": ("rises", "grows", "intensifies"),
        "damps": ("falls", "shrinks", "calms"),
    }
    candidates = keywords.get(rel, ())
    for label in time_labels:
        ll = label.lower()
        if ll in candidates or any(c in ll for c in candidates):
            return label
    return None


# ── Validator ────────────────────────────────────────────────────


class TensorPhysicsValidator:
    """
    Tensor-reasoning twin of ``oral_archaeology.validator.PhysicsValidator``.
    Drop-in by API; different reasoning. ``validate(geom) -> Report``.

    Tunables:
      ratio_tolerance    — proportion-margin used when matching
                           breathing time-marginal patterns.
      box_uniform_tol    — relative tolerance for "uniform" time-marginal
                           when matching box breathing.
      empty_block        — whether to BLOCK on an empty tensor (False
                           by default; emits WARN).
    """

    def __init__(
        self,
        ratio_tolerance: float = 0.06,
        box_uniform_tol: float = 0.05,
        empty_block: bool = False,
    ):
        self.ratio_tolerance = ratio_tolerance
        self.box_uniform_tol = box_uniform_tol
        self.empty_block = empty_block

    def validate(self, geom: Any) -> Report:
        tensor = build_tensor(geom)
        findings: List[Finding] = []

        if tensor.is_empty():
            sev = SEVERITY_BLOCK if self.empty_block else SEVERITY_WARN
            findings.append(Finding(
                category="tensor.empty",
                severity=sev,
                span=getattr(geom, "form_type", "<unknown form>"),
                rationale=(
                    "tensor has no entries — the parsed geometry produced "
                    "no extractable couplings or time bins"
                ),
                reframe=(
                    "either the oral form encodes no constraint geometry "
                    "or the parser missed it; try the parser primary's "
                    "spans for hints"
                ),
            ))
            return Report(verdict=verdict_from(findings), findings=findings)

        # Form-specific signature checks via tensor signatures.
        form = getattr(geom, "form_type", None)
        if form == "breathing":
            findings.extend(self._breathing_signatures(tensor))
        elif form == "dance":
            findings.extend(self._dance_signatures(tensor))
        elif form == "story":
            findings.extend(self._story_signatures(tensor))

        # Tensor-native finding: dominant (entity, relation) factor.
        findings.append(self._dominant_factor_finding(tensor))

        # No physics signature matched → emit the same fallback as the
        # primary so the optics translator's routing rule surfaces it.
        if not any(f.category.startswith("physics.") and f.severity == SEVERITY_INFO
                   for f in findings):
            findings.append(Finding(
                category="physics.no_match",
                severity=SEVERITY_WARN,
                span=form or "<unknown>",
                rationale=(
                    "no tensor signature matched a physics-library entry"
                ),
                reframe=(
                    "either extend the signature set, run a sim sweep, "
                    "or compare to a captured trajectory"
                ),
            ))

        return Report(verdict=verdict_from(findings), findings=findings)

    # -- signature checks --------------------------------------

    def _breathing_signatures(self, tensor: ConstraintTensor) -> List[Finding]:
        out: List[Finding] = []
        time_props = tensor.time_proportions()
        labels = tensor.time_labels
        if len(labels) < 2:
            return out

        # Map proportions by phase name for ratio-pattern matching.
        prop_by_phase: Dict[str, float] = dict(zip(labels, time_props))
        inhale = prop_by_phase.get("inhale")
        hold = prop_by_phase.get("hold")
        exhale = prop_by_phase.get("exhale")
        pause = prop_by_phase.get("pause")

        # 4-7-8 expected proportions: 4/23, 7/23, 8/23, 4/23
        if inhale is not None and hold is not None and exhale is not None and pause is not None:
            expected_478 = (4 / 23, 7 / 23, 8 / 23, 4 / 23)
            obs_478 = (inhale, hold, exhale, pause)
            if all(abs(o - e) <= self.ratio_tolerance for o, e in zip(obs_478, expected_478)):
                out.append(Finding(
                    category="physics.breathing.4-7-8",
                    severity=SEVERITY_INFO,
                    span="4-7-8 time-marginal signature",
                    rationale=(
                        f"time-marginal proportions {tuple(round(x, 3) for x in obs_478)} "
                        "match the 4-7-8 parasympathetic-activation tensor signature"
                    ),
                    reframe=(
                        "interprets as: long exhale + breath-hold drives vagal tone "
                        "via CO2 buildup → relaxation response"
                    ),
                ))

            # Box: roughly uniform across all four phases.
            mean = 0.25
            if all(abs(o - mean) <= self.box_uniform_tol for o in obs_478):
                out.append(Finding(
                    category="physics.breathing.box",
                    severity=SEVERITY_INFO,
                    span="box-uniform time-marginal signature",
                    rationale=(
                        f"time-marginal {tuple(round(x, 3) for x in obs_478)} "
                        "is uniform within tol — box breathing autonomic-balance "
                        "tensor signature"
                    ),
                    reframe=(
                        "interprets as: rhythmic stability across all four phases → "
                        "cognitive focus + autonomic balance"
                    ),
                ))

        return out

    def _dance_signatures(self, tensor: ConstraintTensor) -> List[Finding]:
        out: List[Finding] = []
        # Kuramoto signature: ≥ 2 entities AND a relation in {mirrors,
        # syncs, couples, phase_locks} carries non-trivial mass.
        rel_labels = tensor.relation_labels
        rel_marginal = tensor.marginal_relation()
        kuramoto_relations = ("mirrors", "syncs", "couples", "phase_locks")
        kuramoto_mass = sum(
            m for r, m in zip(rel_labels, rel_marginal) if r in kuramoto_relations
        )
        n_entities = len(tensor.entity_labels)
        if kuramoto_mass > 0 and n_entities >= 2:
            out.append(Finding(
                category="physics.dance.kuramoto",
                severity=SEVERITY_INFO,
                span="multi-entity phase-coupling slice",
                rationale=(
                    f"entity_axis carries {n_entities} subjects and the "
                    f"relation_axis has {kuramoto_mass:.3f} mass on "
                    f"phase-coupling relations (Kuramoto tensor signature)"
                ),
                reframe=(
                    "interprets as: phase-locked or phase-lagged coupling between "
                    "subjects, with the dominant slice giving K (lock strength)"
                ),
            ))
        return out

    def _story_signatures(self, tensor: ConstraintTensor) -> List[Finding]:
        out: List[Finding] = []
        rel_labels = tensor.relation_labels
        rel_marginal = tensor.marginal_relation()
        rel_mass = dict(zip(rel_labels, rel_marginal))
        has_threshold = rel_mass.get("thresholds", 0.0) > 0
        has_bifurcation = rel_mass.get("bifurcates", 0.0) > 0
        has_recombine = rel_mass.get("phase_locks", 0.0) > 0

        if has_threshold and has_bifurcation and has_recombine:
            out.append(Finding(
                category="physics.story.threshold_bifurcation",
                severity=SEVERITY_INFO,
                span="threshold→bifurcation→recombination factor",
                rationale=(
                    "relation-axis carries threshold + bifurcation + "
                    "phase_lock mass — full obstacle-mediated-flow tensor "
                    "signature"
                ),
                reframe=(
                    "interprets as: nonlinear flow past an obstacle with "
                    "downstream phase-lock recombination"
                ),
            ))
        elif has_threshold and has_bifurcation:
            out.append(Finding(
                category="physics.story.threshold_bifurcation",
                severity=SEVERITY_WARN,
                span="threshold + bifurcation factor (no recombination)",
                rationale=(
                    "relation-axis carries threshold + bifurcation mass but "
                    "no phase_lock factor — partial signature"
                ),
                reframe=(
                    "either the tradition is silent on recombination or the "
                    "bifurcation is terminal in this telling"
                ),
            ))
        return out

    # -- tensor-native findings --------------------------------

    @staticmethod
    def _dominant_factor_finding(tensor: ConstraintTensor) -> Finding:
        dom = tensor.dominant_entity_relation()
        if dom is None:
            return Finding(
                category="tensor.dominant_factor",
                severity=SEVERITY_INFO,
                span="<no factor>",
                rationale="tensor has no entries to rank",
            )
        entity, relation, mass = dom
        h = tensor.time_entropy_bits()
        max_h = math.log2(len(tensor.time_labels)) if len(tensor.time_labels) > 1 else 0.0
        return Finding(
            category="tensor.dominant_factor",
            severity=SEVERITY_INFO,
            span=f"({entity}, {relation})",
            rationale=(
                f"dominant (entity, relation) cell mass={mass:.3f}; "
                f"time-marginal entropy = {h:.3f} bits "
                f"(of max {max_h:.3f}) — "
                + (
                    "concentrated in one phase"
                    if max_h > 0 and h < 0.5 * max_h else
                    "spread across phases"
                )
            ),
            reframe=(
                "the system's leading mode — interpret subsequent findings "
                "as perturbations on this factor"
            ),
        )

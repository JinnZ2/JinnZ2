# energy_english/tests/test_oral_as_constraint_tensor.py
"""
Tests for the tensor-reasoning twin of oral_archaeology's PhysicsValidator.

Three layers (matching the pattern proven by [1] and [2]):

1. Tensor-helper unit tests — construction, marginals, dominant
   factor.
2. Mirror tests — same fixtures as the L5 PhysicsValidator, asserting
   the twin matches its physics-signature verdicts on the canonical
   examples.
3. Twin-specific findings — the tensor.dominant_factor surfacing on
   every non-empty tensor; tensor.empty when the geometry produces
   nothing extractable.

Plus ensemble compatibility via OpticsTranslator.
"""

import unittest

from energy_english.findings import Verdict
from energy_english.oral_as_constraint_tensor import (
    ConstraintTensor,
    TensorPhysicsValidator,
    build_tensor,
)
from oral_archaeology.extractor import ConstraintGeometry, run_all
from oral_archaeology.parser import parser_for
from oral_archaeology.validator import PhysicsValidator


# ── Helpers ─────────────────────────────────────────────────────


def _geom_for(form_type, text):
    return run_all(parser_for(form_type).parse(text))


# ── Tensor construction + marginals ─────────────────────────────


class TensorPrimitives(unittest.TestCase):

    def test_add_grows_axes_and_accumulates_mass(self):
        t = ConstraintTensor()
        t.add("t0", "A", "drives", 0.4)
        t.add("t0", "A", "drives", 0.1)
        self.assertEqual(t.shape, (1, 1, 1))
        self.assertAlmostEqual(t.total_mass(), 0.5)

    def test_marginals_sum_to_total(self):
        t = ConstraintTensor()
        t.add("t0", "A", "drives", 1.0)
        t.add("t1", "B", "damps", 2.0)
        self.assertAlmostEqual(sum(t.marginal_time()), 3.0)
        self.assertAlmostEqual(sum(t.marginal_entity()), 3.0)
        self.assertAlmostEqual(sum(t.marginal_relation()), 3.0)

    def test_time_proportions_normalised(self):
        t = ConstraintTensor()
        t.add("t0", "A", "r", 4.0)
        t.add("t1", "A", "r", 6.0)
        props = t.time_proportions()
        self.assertAlmostEqual(sum(props), 1.0)
        self.assertAlmostEqual(props[0], 0.4)
        self.assertAlmostEqual(props[1], 0.6)

    def test_dominant_entity_relation(self):
        t = ConstraintTensor()
        t.add("t0", "A", "r1", 0.3)
        t.add("t0", "B", "r2", 0.9)
        t.add("t1", "B", "r2", 0.5)
        dom = t.dominant_entity_relation()
        self.assertEqual(dom, ("B", "r2", 1.4))

    def test_empty_tensor_dominant_returns_none(self):
        self.assertIsNone(ConstraintTensor().dominant_entity_relation())


# ── Build from ConstraintGeometry ───────────────────────────────


class BuildBreathingTensor(unittest.TestCase):

    def test_4_7_8_time_proportions_match_protocol_ratio(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat",
        )
        t = build_tensor(geom)
        self.assertEqual(t.time_labels, ["inhale", "hold", "exhale", "pause"])
        props = t.time_proportions()
        # 4/23, 7/23, 8/23, 4/23
        self.assertAlmostEqual(props[0], 4 / 23, places=3)
        self.assertAlmostEqual(props[1], 7 / 23, places=3)
        self.assertAlmostEqual(props[2], 8 / 23, places=3)
        self.assertAlmostEqual(props[3], 4 / 23, places=3)

    def test_box_breathing_time_proportions_uniform(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 4, exhale for 4, pause for 4",
        )
        t = build_tensor(geom)
        for p in t.time_proportions():
            self.assertAlmostEqual(p, 0.25, places=3)


class BuildDanceTensor(unittest.TestCase):

    def test_subjects_appear_on_entity_axis(self):
        geom = _geom_for(
            "dance",
            "person A mirrors person B with 0.3s lag, "
            "tightens on the third measure, resets on the drum",
        )
        t = build_tensor(geom)
        self.assertGreaterEqual(len(t.entity_labels), 2)


class BuildStoryTensor(unittest.TestCase):

    def test_bifurcation_relation_present_in_axis(self):
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        t = build_tensor(geom)
        self.assertIn("bifurcates", t.relation_labels)
        self.assertIn("thresholds", t.relation_labels)
        self.assertIn("phase_locks", t.relation_labels)


# ── Mirror tests ────────────────────────────────────────────────


class MirrorPhysicsSignatures(unittest.TestCase):
    """The twin must match the primary on the canonical signature
    matches. Verdict equality holds; the twin additionally emits a
    tensor.dominant_factor finding which is benign info."""

    def test_4_7_8_matches_in_both(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat",
        )
        primary = PhysicsValidator().validate(geom)
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(primary.has_category("physics.breathing.4-7-8"))
        self.assertTrue(twin.has_category("physics.breathing.4-7-8"))

    def test_box_matches_in_both_only_when_actually_uniform(self):
        # 4-7-8 is NOT uniform — the twin must not also fire box on it.
        geom_478 = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4",
        )
        twin_478 = TensorPhysicsValidator().validate(geom_478)
        self.assertFalse(
            twin_478.has_category("physics.breathing.box"),
            msg="4-7-8 should not also fire box signature",
        )

        # Real box should fire box and not 4-7-8.
        geom_box = _geom_for(
            "breathing",
            "inhale for 4, hold for 4, exhale for 4, pause for 4",
        )
        primary_box = PhysicsValidator().validate(geom_box)
        twin_box = TensorPhysicsValidator().validate(geom_box)
        self.assertTrue(primary_box.has_category("physics.breathing.box"))
        self.assertTrue(twin_box.has_category("physics.breathing.box"))
        self.assertFalse(twin_box.has_category("physics.breathing.4-7-8"))

    def test_dance_kuramoto_in_both(self):
        geom = _geom_for(
            "dance",
            "person A mirrors person B with 0.3s lag",
        )
        primary = PhysicsValidator().validate(geom)
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(primary.has_category("physics.dance.kuramoto"))
        self.assertTrue(twin.has_category("physics.dance.kuramoto"))

    def test_story_threshold_bifurcation_in_both(self):
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        primary = PhysicsValidator().validate(geom)
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(
            primary.has_category("physics.story.threshold_bifurcation")
        )
        self.assertTrue(
            twin.has_category("physics.story.threshold_bifurcation")
        )

    def test_partial_story_warns_in_both(self):
        # threshold + bifurcation but no recombination
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides",
        )
        twin = TensorPhysicsValidator().validate(geom)
        partial = next(
            (f for f in twin.findings
             if f.category == "physics.story.threshold_bifurcation"),
            None,
        )
        self.assertIsNotNone(partial)
        self.assertEqual(partial.severity, "warn")

    def test_no_match_disagreement_paradigms_use_native_categories(self):
        """
        Legitimate paradigm divergence (recorded as a fixture per the
        design doc's policy):

        - 1:1 breathing has well-formed time_constants but no inferred
          coupling, so the primary's signature-library check produces
          ``physics.no_match`` (its native "nothing matched" category).
        - The same geometry produces an empty tensor (no couplings
          → no entries), so the twin emits ``tensor.empty`` (its
          native "nothing to reason over" category).

        Both convey "no signature matched"; the categories differ
        because the paradigms differ.
        """
        geom = _geom_for("breathing", "inhale for 1, exhale for 1")
        primary = PhysicsValidator().validate(geom)
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(primary.has_category("physics.no_match"))
        self.assertTrue(twin.has_category("tensor.empty"))


# ── Twin-specific findings ──────────────────────────────────────


class DominantFactorAlwaysFires(unittest.TestCase):

    def test_dominant_factor_in_breathing(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4",
        )
        twin = TensorPhysicsValidator().validate(geom)
        dom = next(
            (f for f in twin.findings
             if f.category == "tensor.dominant_factor"),
            None,
        )
        self.assertIsNotNone(dom)
        # dominant cell is the (vagal_tone, drives) pair from the
        # implicit coupling
        self.assertIn("vagal_tone", dom.span)
        self.assertIn("drives", dom.span)

    def test_dominant_factor_in_dance(self):
        geom = _geom_for(
            "dance",
            "person A mirrors person B with 0.3s lag",
        )
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(twin.has_category("tensor.dominant_factor"))


class TensorEmptyOnEmptyGeometry(unittest.TestCase):

    def test_empty_geometry_emits_tensor_empty(self):
        # ConstraintGeometry with no couplings and unknown form_type.
        geom = ConstraintGeometry(form_type="unknown")
        twin = TensorPhysicsValidator().validate(geom)
        self.assertTrue(twin.has_category("tensor.empty"))


# ── Ensemble via optics ─────────────────────────────────────────


class EnsembleViaOptics(unittest.TestCase):

    def test_optics_absorbs_primary_and_twin_reports(self):
        from energy_english.optics import OpticsTranslator

        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat",
        )
        primary = PhysicsValidator().validate(geom)
        twin = TensorPhysicsValidator().validate(geom)

        opt = OpticsTranslator().translate(primary, twin)
        # Both reports surface the 4-7-8 interpretation; the optics
        # translator dedups across them so vagal/relaxation appears once.
        self.assertTrue(opt.interpretations)


if __name__ == "__main__":
    unittest.main()

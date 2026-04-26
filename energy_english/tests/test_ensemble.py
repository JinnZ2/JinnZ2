# energy_english/tests/test_ensemble.py
"""Tests for the ensemble-vote helper in optics.py."""

import unittest

from energy_english.coating_detector import CoatingDetector, Trajectory
from energy_english.coating_as_information_divergence import (
    InformationDivergenceCoatingDetector,
)
from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_WARN,
    Verdict,
)
from energy_english.gate import ConstraintGate
from energy_english.gate_as_constraint_graph import ConstraintGraphGate
from energy_english.optics import EnsembleResult, ensemble


def _r(verdict, *findings):
    return Report(verdict=verdict, findings=list(findings))


# ── Basic shape ─────────────────────────────────────────────────


class EnsembleShape(unittest.TestCase):

    def test_zero_reports_yields_empty_ensemble(self):
        result = ensemble()
        self.assertIsInstance(result, EnsembleResult)
        self.assertEqual(result.verdicts, [])
        self.assertIsNone(result.consensus)
        self.assertEqual(result.disagreement_categories, [])
        self.assertTrue(result.optics.is_empty())

    def test_none_reports_are_skipped(self):
        result = ensemble(None, None)
        self.assertEqual(result.verdicts, [])
        self.assertIsNone(result.consensus)


# ── Consensus ───────────────────────────────────────────────────


class Consensus(unittest.TestCase):

    def test_unanimous_pass(self):
        result = ensemble(_r(Verdict.PASS), _r(Verdict.PASS))
        self.assertEqual(result.consensus, Verdict.PASS)
        self.assertTrue(result.unanimous)

    def test_unanimous_block(self):
        f = Finding(category="narration", severity=SEVERITY_BLOCK,
                    span="x", rationale="x")
        result = ensemble(_r(Verdict.BLOCK, f), _r(Verdict.BLOCK, f))
        self.assertEqual(result.consensus, Verdict.BLOCK)

    def test_disagreement_returns_none_consensus(self):
        f_block = Finding(category="closure", severity=SEVERITY_BLOCK,
                          span="x", rationale="x")
        f_warn = Finding(category="closure", severity=SEVERITY_WARN,
                         span="x", rationale="tempered")
        result = ensemble(_r(Verdict.BLOCK, f_block), _r(Verdict.FLAG, f_warn))
        self.assertIsNone(result.consensus)
        self.assertFalse(result.unanimous)
        self.assertEqual(result.verdicts, [Verdict.BLOCK, Verdict.FLAG])


# ── Disagreement categories ─────────────────────────────────────


class DisagreementCategories(unittest.TestCase):

    def test_category_in_some_but_not_all_is_disagreement(self):
        f_a = Finding(category="narration", severity=SEVERITY_BLOCK,
                      span="x", rationale="x")
        f_b = Finding(category="surface_certainty", severity=SEVERITY_WARN,
                      span="y", rationale="y")
        result = ensemble(_r(Verdict.BLOCK, f_a), _r(Verdict.FLAG, f_b))
        # both narration (only in A) and surface_certainty (only in B)
        # are disagreements
        self.assertIn("narration", result.disagreement_categories)
        self.assertIn("surface_certainty", result.disagreement_categories)

    def test_same_category_at_different_severities_is_disagreement(self):
        # Both reports have closure but at different severities — the
        # graph twin's tempered-closure case.
        f_block = Finding(category="closure", severity=SEVERITY_BLOCK,
                          span="x", rationale="x")
        f_warn = Finding(category="closure", severity=SEVERITY_WARN,
                         span="x", rationale="tempered")
        result = ensemble(_r(Verdict.BLOCK, f_block), _r(Verdict.FLAG, f_warn))
        self.assertIn("closure", result.disagreement_categories)

    def test_same_category_at_same_severity_is_NOT_disagreement(self):
        f = Finding(category="narration", severity=SEVERITY_BLOCK,
                    span="x", rationale="x")
        result = ensemble(_r(Verdict.BLOCK, f), _r(Verdict.BLOCK, f))
        self.assertNotIn("narration", result.disagreement_categories)

    def test_single_report_has_no_disagreements(self):
        f = Finding(category="narration", severity=SEVERITY_BLOCK,
                    span="x", rationale="x")
        result = ensemble(_r(Verdict.BLOCK, f))
        self.assertEqual(result.disagreement_categories, [])


# ── Real-world: gate primary + graph twin ───────────────────────


class GatePrimaryVsGraphTwin(unittest.TestCase):

    def test_tempered_closure_surfaces_as_disagreement(self):
        text = (
            "The answer is they may be locked. "
            "But what would falsify this: sweep the coupling_range across [10, 40]."
        )
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)
        result = ensemble(primary, twin)

        # primary blocks, twin flags — verdicts differ
        self.assertEqual(result.verdicts, [Verdict.BLOCK, Verdict.FLAG])
        self.assertIsNone(result.consensus)
        # closure category is the headline disagreement
        self.assertIn("closure", result.disagreement_categories)

    def test_obvious_narration_yields_consensus(self):
        text = "Let me walk you through it. The answer is locked. Obviously."
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)
        result = ensemble(primary, twin)

        self.assertEqual(result.consensus, Verdict.BLOCK)


# ── Real-world: coating primary + info-divergence twin ──────────


class CoatingPrimaryVsInfoTwin(unittest.TestCase):

    def test_nonlinear_coupling_disagreement(self):
        # y = x^2 — primary fires uncorrelated_coupling false-positive,
        # twin recognises the dependence and does NOT fire.
        n = 200
        xs = [(-1.0 + 2.0 * i / (n - 1)) for i in range(n)]
        ys = [x * x for x in xs]
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"src": xs, "tgt": ys},
            declared_couplings=[("src", "couples", "tgt")],
            events=[{"iteration": 1}],
        )
        primary = CoatingDetector().detect(traj)
        twin = InformationDivergenceCoatingDetector().detect(traj)
        result = ensemble(primary, twin)

        self.assertEqual(result.verdicts, [Verdict.BLOCK, Verdict.PASS])
        self.assertIsNone(result.consensus)
        self.assertIn("uncorrelated_coupling", result.disagreement_categories)


# ── Optics still gets dedup'd across reports ────────────────────


class OpticsDedupAcrossEnsemble(unittest.TestCase):

    def test_identical_findings_rendered_once(self):
        f = Finding(
            category="silent_variable", severity=SEVERITY_WARN,
            span="frequency_gap", rationale="x",
        )
        result = ensemble(_r(Verdict.FLAG, f), _r(Verdict.FLAG, f))
        # Optics translator dedups within a single ensemble call.
        self.assertEqual(
            result.optics.silent.count("frequency_gap not varied"), 1
        )


if __name__ == "__main__":
    unittest.main()

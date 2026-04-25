# energy_english/tests/test_optics.py
"""Tests for the L5 optics translator."""

import unittest

from energy_english.coating_detector import CoatingDetector, Trajectory
from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    Verdict,
)
from energy_english.gate import ConstraintGate
from energy_english.optics import Optics, OpticsTranslator
from oral_archaeology import OralArchaeologyPipeline


# ── Empty / no-op ────────────────────────────────────────────────


class EmptyTranslate(unittest.TestCase):

    def test_no_reports_yields_empty_optics(self):
        opt = OpticsTranslator().translate()
        self.assertTrue(opt.is_empty())

    def test_only_none_reports_yields_empty_optics(self):
        opt = OpticsTranslator().translate(None, None)
        self.assertTrue(opt.is_empty())

    def test_speak_on_empty_says_nothing_fired(self):
        s = OpticsTranslator().speak(Optics())
        self.assertIn("nothing fired", s)


# ── Routing per category ─────────────────────────────────────────


def _r(*findings: Finding) -> Report:
    return Report(verdict=Verdict.FLAG, findings=list(findings))


class GateCategoryRouting(unittest.TestCase):

    def test_narration_goes_to_invitations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="narration", severity=SEVERITY_BLOCK,
            span="let me walk you through", rationale="x",
        )))
        self.assertTrue(any("anchor in triples" in i for i in opt.invitations))

    def test_intention_goes_to_invitations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="intention", severity=SEVERITY_BLOCK,
            span="what you're really asking", rationale="x",
        )))
        self.assertTrue(any("echo the literal" in i for i in opt.invitations))

    def test_closure_goes_to_invitations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="closure", severity=SEVERITY_BLOCK,
            span="the answer is", rationale="x",
        )))
        self.assertTrue(any("open the loop" in i for i in opt.invitations))

    def test_moralization_to_interpretations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="moralization", severity=SEVERITY_WARN,
            span="should", rationale="x",
        )))
        self.assertTrue(any("prescriptive verb" in i for i in opt.interpretations))

    def test_invented_relation_to_interpretations_with_reframe(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="invented_relation", severity=SEVERITY_WARN,
            span="causes", rationale="x",
            reframe="'A causes B' → project as: A drives B",
        )))
        joined = "\n".join(opt.interpretations)
        self.assertIn("causes", joined)
        self.assertIn("drives", joined)


class CoatingCategoryRouting(unittest.TestCase):

    def test_silent_variable_populates_silent_and_falsifier(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="silent_variable", severity=SEVERITY_WARN,
            span="coupling_range", rationale="x",
        )))
        self.assertIn("coupling_range not varied", opt.silent)
        self.assertIn("sweep coupling_range", opt.falsifiers)

    def test_untouched_layer_populates_silent_and_falsifier(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="untouched_layer", severity=SEVERITY_WARN,
            span="max_T", rationale="x",
        )))
        self.assertIn("max_T stayed flat", opt.silent)
        self.assertTrue(any("max_T" in f for f in opt.falsifiers))

    def test_unexplored_phase_space_to_falsifiers_and_invitations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="unexplored_phase_space", severity=SEVERITY_BLOCK,
            span="<200 iters>", rationale="x",
        )))
        self.assertTrue(any("threshold" in f for f in opt.falsifiers))
        self.assertTrue(any("flat OR" in i for i in opt.invitations))

    def test_uncorrelated_coupling_to_diverged_and_falsifier(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="uncorrelated_coupling", severity=SEVERITY_BLOCK,
            span="(lock_A, couples, lock_B)", rationale="x",
        )))
        self.assertTrue(any("(lock_A, couples, lock_B)" in d for d in opt.diverged))
        self.assertTrue(any("drop the coupling claim" in f for f in opt.falsifiers))


class ArchaeologyCategoryRouting(unittest.TestCase):

    def test_physics_match_lands_in_interpretations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="physics.breathing.4-7-8", severity=SEVERITY_INFO,
            span="x", rationale="ratio matches",
            reframe="vagal tone via CO2 → relaxation",
        )))
        self.assertTrue(any("vagal" in i.lower() for i in opt.interpretations))

    def test_physics_no_match_to_invitations(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="physics.no_match", severity=SEVERITY_WARN,
            span="x", rationale="no signature matched",
        )))
        self.assertTrue(any("no physics-library match" in i for i in opt.invitations))

    def test_trajectory_match_to_observed(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="trajectory.match", severity=SEVERITY_INFO,
            span="(water, drives, stone)", rationale="x",
        )))
        self.assertIn("(water, drives, stone) matches trajectory", opt.observed)

    def test_trajectory_diverge_to_diverged_and_falsifier(self):
        opt = OpticsTranslator().translate(_r(Finding(
            category="trajectory.diverge", severity=SEVERITY_WARN,
            span="(lock_A, couples, lock_B)", rationale="x",
        )))
        self.assertTrue(any("(lock_A, couples, lock_B)" in d for d in opt.diverged))
        self.assertTrue(any("extend the sim" in f.lower() for f in opt.falsifiers))


# ── Cross-report integration ─────────────────────────────────────


class GateAndCoatingTogether(unittest.TestCase):

    def test_combined_report_populates_all_relevant_buckets(self):
        gate = ConstraintGate()
        gate_report = gate.evaluate_output(
            "Let me walk you through it. The answer is they sync.",
            original_input="front_A drives front_B",
        )
        coating_report = CoatingDetector().detect(Trajectory(
            parameters={"a": 1, "b": 2},
            varied_parameters={"a"},
            traces={"x": [0.0] * 200},  # untouched
            events=[],                  # unexplored
        ))
        opt = OpticsTranslator().translate(gate_report, coating_report)

        self.assertTrue(opt.invitations, "gate findings should produce invitations")
        self.assertTrue(opt.silent, "coating findings should produce silent items")
        self.assertTrue(opt.falsifiers, "coating findings should produce falsifiers")


class ArchaeologyEndToEnd(unittest.TestCase):

    def test_breathing_archaeology_yields_interpretations_and_observed(self):
        report = OralArchaeologyPipeline().parse(
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
        )
        opt = OpticsTranslator().translate(report)

        # at least one observed coupling was extracted
        self.assertTrue(opt.observed)
        # 4-7-8 signature matched → interpretation includes vagal/relaxation
        joined = "\n".join(opt.interpretations).lower()
        self.assertTrue("vagal" in joined or "relaxation" in joined)


# ── Speak rendering ──────────────────────────────────────────────


class Speaking(unittest.TestCase):

    def test_speak_renders_each_section_only_when_populated(self):
        opt = Optics(
            observed=["(A, drives, B) strength≈0.6"],
            silent=["frequency_gap not varied"],
            falsifiers=["sweep frequency_gap"],
        )
        s = OpticsTranslator().speak(opt)
        self.assertIn("OBSERVED", s)
        self.assertIn("SILENT", s)
        self.assertIn("FALSIFIERS", s)
        self.assertNotIn("DIVERGED", s)
        self.assertNotIn("INTERPRETATIONS", s)
        self.assertNotIn("OPEN", s)
        # bullets present
        self.assertIn("- (A, drives, B)", s)
        self.assertIn("- frequency_gap not varied", s)

    def test_speak_dedups_identical_lines_across_reports(self):
        # Two reports surfacing the same finding should not duplicate.
        f = Finding(
            category="silent_variable", severity=SEVERITY_WARN,
            span="frequency_gap", rationale="x",
        )
        r1 = Report(verdict=Verdict.FLAG, findings=[f])
        r2 = Report(verdict=Verdict.FLAG, findings=[f])
        opt = OpticsTranslator().translate(r1, r2)
        self.assertEqual(opt.silent.count("frequency_gap not varied"), 1)


if __name__ == "__main__":
    unittest.main()

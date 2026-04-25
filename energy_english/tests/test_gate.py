# energy_english/tests/test_gate.py
"""Tests for the Layer 1 constraint gate."""

import unittest

from energy_english.gate import (
    ConstraintGate,
    GateVerdict,
    SEVERITY_BLOCK,
    SEVERITY_WARN,
)


CLEAN_OUTPUT = (
    "Triples extracted:\n"
    "- (beta_front, drives, chi_front, strength=0.6, scope=sentence)\n"
    "- (thermal_field, damps, chi_front, strength=0.4, scope=sentence)\n"
    "Silent variables: frequency_gap left at default; coupling_range not varied.\n"
    "What would falsify: drive a wider frequency_gap and watch for loss of "
    "phase-lock; vary coupling_range across [10, 40] and check for a "
    "threshold crossing."
)


class GateInputMode(unittest.TestCase):

    def test_clean_input_passes(self):
        gate = ConstraintGate()
        report = gate.evaluate_input("front_A drives front_B")
        self.assertIs(report.verdict, GateVerdict.PASS)
        self.assertEqual(report.findings, [])

    def test_input_flags_but_does_not_block(self):
        gate = ConstraintGate()
        report = gate.evaluate_input(
            "the chi front should obviously sync, right?"
        )
        self.assertIs(report.verdict, GateVerdict.FLAG)
        self.assertTrue(report.has_category("moralization"))
        self.assertTrue(report.has_category("surface_certainty"))


class GateOutputBlocking(unittest.TestCase):

    def test_blocks_narration(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "Let me walk you through what's happening here. First the beta "
            "front drives the chi front. Then they sync."
        )
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        self.assertTrue(report.has_category("narration"))

    def test_blocks_intention_assumption(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "What you're really asking is whether the front is locked."
        )
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        self.assertTrue(report.has_category("intention"))

    def test_blocks_forced_closure(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "The answer is that they are locked. This confirms the hypothesis."
        )
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        self.assertTrue(report.has_category("closure"))

    def test_blocks_summary_closure(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "In conclusion, the fronts have synchronized as expected."
        )
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        self.assertTrue(report.has_category("narration"))

    def test_block_severity_dominates(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "In conclusion, this obviously means they should be coupled."
        )
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        # softer findings still recorded
        self.assertTrue(report.has_category("moralization"))
        self.assertTrue(report.has_category("surface_certainty"))


class GateOutputFlagging(unittest.TestCase):

    def test_flags_surface_certainty_only(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "front_A obviously couples to front_B (strength 0.6).\n"
            "Silent: thermal_field is at default.\n"
            "- (front_A, couples, front_B, 0.6)"
        )
        self.assertIs(report.verdict, GateVerdict.FLAG)
        self.assertTrue(report.has_category("surface_certainty"))
        # reframe should be attached
        sc = next(f for f in report.findings if f.category == "surface_certainty")
        self.assertIsNotNone(sc.reframe)

    def test_flags_moralization_only(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "The coupling must be 0.6 for lock.\n"
            "- (front_A, couples, front_B, 0.6)\n"
            "Silent: thermal_field at default."
        )
        self.assertIs(report.verdict, GateVerdict.FLAG)
        self.assertTrue(report.has_category("moralization"))


class GateOutputPassing(unittest.TestCase):

    def test_clean_structural_output_passes(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(CLEAN_OUTPUT)
        self.assertIs(report.verdict, GateVerdict.PASS, report.findings)
        self.assertEqual(report.findings, [])


class GateCoatingDetection(unittest.TestCase):

    def test_block_on_high_overlap_no_structure(self):
        gate = ConstraintGate(coating_overlap_threshold=0.4)
        original = (
            "The beta front drives the chi front and the thermal field "
            "damps the chi front; the frequency gap stays small."
        )
        # Restates almost verbatim, no silent variables, no structure.
        echo = (
            "Yes — the beta front drives the chi front and the thermal "
            "field damps the chi front; the frequency gap stays small."
        )
        report = gate.evaluate_output(echo, original_input=original)
        self.assertIs(report.verdict, GateVerdict.BLOCK)
        self.assertTrue(report.has_category("coating"))
        # blocked-severity coating is reported
        c = next(f for f in report.findings if f.category == "coating")
        self.assertEqual(c.severity, SEVERITY_BLOCK)

    def test_warn_when_no_silent_variables_named(self):
        gate = ConstraintGate()
        original = "front_A drives front_B"
        # Long, structured, but never names a silent variable.
        response = (
            "- (front_A, drives, front_B, 0.6)\n"
            "- (front_B, couples, front_C, 0.4)\n"
            "- (front_C, damps, front_D, 0.5)\n"
            "Edges form a chain. Strength decays along the chain. "
            "Confidence on the chain is moderate. Polarity positive on "
            "all edges. Scope is sentence-level for each."
        )
        report = gate.evaluate_output(response, original_input=original)
        self.assertIs(report.verdict, GateVerdict.FLAG)
        coating = [f for f in report.findings if f.category == "coating"]
        self.assertTrue(coating)
        self.assertEqual(coating[0].severity, SEVERITY_WARN)

    def test_no_coating_finding_when_silent_variables_named(self):
        gate = ConstraintGate()
        original = "front_A drives front_B"
        report = gate.evaluate_output(CLEAN_OUTPUT, original_input=original)
        self.assertFalse(report.has_category("coating"))

    def test_no_coating_finding_when_no_input_supplied(self):
        gate = ConstraintGate()
        # Even a bare echo gets no coating finding without the input.
        report = gate.evaluate_output("front_A drives front_B")
        self.assertFalse(report.has_category("coating"))


class GateSuggestedResponse(unittest.TestCase):

    def test_suggestion_emits_principle_scaffold_and_example(self):
        gate = ConstraintGate()
        report = gate.evaluate_output("Let me walk you through this.")
        self.assertIsNotNone(report.suggested_response)
        # Per-category teaching block surfaces all three layers:
        # principle ([A]), scaffold ([B]), and worked example ([C]).
        self.assertIn("[narration]", report.suggested_response)
        self.assertIn("principle:", report.suggested_response)
        self.assertIn("scaffold:", report.suggested_response)
        self.assertIn("example:", report.suggested_response)

    def test_suggestion_lists_each_fired_category_once(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "Let me walk you through this. The answer is X. Obviously."
        )
        text = report.suggested_response
        self.assertIn("[narration]", text)
        self.assertIn("[closure]", text)
        self.assertIn("[surface_certainty]", text)
        # category headers appear exactly once
        for header in ("[narration]", "[closure]", "[surface_certainty]"):
            self.assertEqual(text.count(header), 1)
        # blocking categories are taught before flagging ones
        self.assertLess(text.index("[narration]"), text.index("[surface_certainty]"))
        self.assertLess(text.index("[closure]"), text.index("[surface_certainty]"))

    def test_suggestion_includes_per_span_reframe_block(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(
            "obviously they sync — let me walk you through it"
        )
        self.assertIn("Reframes:", report.suggested_response)
        self.assertIn("'obviously'", report.suggested_response)

    def test_no_suggestion_on_clean_output(self):
        gate = ConstraintGate()
        report = gate.evaluate_output(CLEAN_OUTPUT)
        self.assertIsNone(report.suggested_response)


if __name__ == "__main__":
    unittest.main()

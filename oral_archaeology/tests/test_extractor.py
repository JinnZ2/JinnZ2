# oral_archaeology/tests/test_extractor.py

import unittest

from oral_archaeology.extractor import (
    ConstraintGeometry,
    CouplingExtractor,
    PhaseExtractor,
    StateEquationBuilder,
    TimingExtractor,
    run_all,
)
from oral_archaeology.parser import (
    BreathingProtocolParser,
    DanceNotationParser,
    StoryParser,
)


class BreathingExtraction(unittest.TestCase):

    def setUp(self):
        self.parser = BreathingProtocolParser()
        self.geom = ConstraintGeometry(form_type="breathing")
        self.parsed = self.parser.parse(
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
        )

    def test_timing_extracts_period_and_phases(self):
        TimingExtractor().extract(self.parsed, self.geom)
        tc = self.geom.time_constants
        self.assertEqual(tc["period"], 23)
        self.assertEqual(tc["inhale"], 4)
        self.assertEqual(tc["hold"], 7)
        self.assertEqual(tc["exhale"], 8)
        self.assertEqual(tc["pause"], 4)
        self.assertEqual(tc["saturation_point"], "hold")
        self.assertEqual(tc["saturation_duration"], 7)

    def test_coupling_inferred_from_hold_exhale(self):
        CouplingExtractor().extract(self.parsed, self.geom)
        self.assertEqual(len(self.geom.couplings), 1)
        c = self.geom.couplings[0]
        self.assertEqual(c["source"], "co2_buildup")
        self.assertEqual(c["target"], "vagal_tone")
        self.assertTrue(c["inferred"])
        self.assertGreater(c["strength"], 0.0)
        self.assertLessEqual(c["strength"], 1.0)
        self.assertIn("co2_buildup", self.geom.implicit_variables)
        self.assertIn("vagal_tone", self.geom.implicit_variables)

    def test_phase_extracts_cycle(self):
        PhaseExtractor().extract(self.parsed, self.geom)
        rel = self.geom.phase_relationships
        self.assertEqual(rel["initial_state"], "inhale")
        self.assertEqual(rel["terminal_state"], "pause")
        self.assertEqual(rel["cycle"], ["inhale", "hold", "exhale", "pause"])
        self.assertTrue(rel["repeats"])

    def test_state_equation_builder(self):
        TimingExtractor().extract(self.parsed, self.geom)
        StateEquationBuilder().extract(self.parsed, self.geom)
        eqs = self.geom.state_equations
        self.assertEqual(len(eqs), 1)
        self.assertEqual(eqs[0].variable, "vagal_tone")
        self.assertIn("ratio=4:7:8:4", eqs[0].signature)


class DanceExtraction(unittest.TestCase):

    def test_coupling_strength_from_lag(self):
        parsed = DanceNotationParser().parse(
            "person A mirrors person B with 0.3s lag, "
            "tightens on the third measure"
        )
        geom = run_all(parsed)
        self.assertEqual(len(geom.couplings), 1)
        c = geom.couplings[0]
        # lag 0.3 → base 0.85, then +0.2 from tighten → capped at 1.0
        self.assertGreaterEqual(c["strength"], 0.9)
        self.assertEqual(c["lag_seconds"], 0.3)
        self.assertEqual(c["tighten_at_measure"], 3)

    def test_state_equation_kuramoto_shape(self):
        parsed = DanceNotationParser().parse(
            "person A mirrors person B with 0.3s lag"
        )
        geom = run_all(parsed)
        eqs = geom.state_equations
        self.assertEqual(len(eqs), 1)
        self.assertIn("sin(", eqs[0].signature)
        self.assertIn("K=", eqs[0].signature)

    def test_phase_records_reset_transition(self):
        parsed = DanceNotationParser().parse(
            "person A mirrors person B, "
            "tightens on the third measure, resets on the drum"
        )
        geom = run_all(parsed)
        transitions = geom.phase_relationships["transitions"]
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["trigger"], "measure_3")
        self.assertEqual(transitions[1]["trigger"], "drum")


class StoryExtraction(unittest.TestCase):

    def test_couplings_for_threshold_bifurcation_recombine(self):
        parsed = StoryParser().parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        geom = run_all(parsed)
        rels = [c["relationship"] for c in geom.couplings]
        self.assertIn("thresholds", rels)
        self.assertIn("bifurcates", rels)
        self.assertIn("phase_locks", rels)

    def test_state_equations_per_event(self):
        parsed = StoryParser().parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        geom = run_all(parsed)
        # one equation per non-state-change event + the rise state-change
        self.assertGreaterEqual(len(geom.state_equations), 4)
        sigs = " | ".join(eq.signature for eq in geom.state_equations)
        self.assertIn("d(water)/dt > 0", sigs)
        self.assertIn("bifurcation", sigs)
        self.assertIn("phase_lock", sigs)

    def test_implicit_branched_state(self):
        parsed = StoryParser().parse("water divides, reforms")
        geom = run_all(parsed)
        self.assertIn("branched_state", geom.implicit_variables)


if __name__ == "__main__":
    unittest.main()

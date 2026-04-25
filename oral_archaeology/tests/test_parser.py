# oral_archaeology/tests/test_parser.py

import unittest

from oral_archaeology.parser import (
    BreathingProtocolParser,
    DanceNotationParser,
    StoryParser,
    detect_form,
    parser_for,
    CONSTRAINT_THRESHOLD,
    CONSTRAINT_COUPLING,
    CONSTRAINT_PHASE_TRANSITION,
)


class FormDetection(unittest.TestCase):

    def test_detects_breathing(self):
        self.assertEqual(detect_form("inhale for 4, hold for 7"), "breathing")
        self.assertEqual(detect_form("breathe in slowly, hold for 5"), "breathing")

    def test_detects_dance(self):
        self.assertEqual(
            detect_form("person A mirrors person B with 0.3s lag"),
            "dance",
        )
        self.assertEqual(
            detect_form("dancer 1 follows dancer 2 on the downbeat"),
            "dance",
        )

    def test_falls_back_to_story(self):
        self.assertEqual(
            detect_form("water rises and reaches the stone"),
            "story",
        )


class BreathingParser(unittest.TestCase):

    def setUp(self):
        self.parser = BreathingProtocolParser()

    def test_parses_4_7_8(self):
        text = "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
        out = self.parser.parse(text)
        self.assertEqual(out.form_type, "breathing")
        phases = out.structured["phases"]
        self.assertEqual(
            [(p["phase"], p["count"]) for p in phases],
            [("inhale", 4), ("hold", 7), ("exhale", 8), ("pause", 4)],
        )
        self.assertEqual(out.structured["period"], 23)
        self.assertEqual(out.structured["ratio"], "4:7:8:4")
        self.assertTrue(out.structured["repeat"])

    def test_saturation_prefers_hold_over_longest(self):
        text = "inhale for 4, hold for 7, exhale for 8, pause for 4"
        out = self.parser.parse(text)
        # exhale is longest (8) but saturation should be hold by definition
        self.assertEqual(out.structured["saturation_point"], "hold")

    def test_saturation_falls_back_to_longest_without_hold(self):
        text = "inhale for 5, exhale for 10"
        out = self.parser.parse(text)
        self.assertEqual(out.structured["saturation_point"], "exhale")

    def test_normalises_breathe_in_out(self):
        text = "breathe in for 4, breathe out for 6"
        out = self.parser.parse(text)
        phases = [(p["phase"], p["count"]) for p in out.structured["phases"]]
        self.assertEqual(phases, [("inhale", 4), ("exhale", 6)])

    def test_emits_threshold_span_for_hold(self):
        out = self.parser.parse("inhale for 4, hold for 7")
        kinds = [s.constraint_type for s in out.spans]
        self.assertIn(CONSTRAINT_THRESHOLD, kinds)


class DanceParser(unittest.TestCase):

    def setUp(self):
        self.parser = DanceNotationParser()

    def test_extracts_subjects_and_coupling(self):
        text = (
            "person A mirrors person B with 0.3s lag, "
            "tightens on the third measure, resets on the drum"
        )
        out = self.parser.parse(text)
        self.assertEqual(out.form_type, "dance")
        self.assertIn("person A", out.structured["subjects"])
        self.assertIn("person B", out.structured["subjects"])
        couplings = out.structured["couplings"]
        self.assertEqual(len(couplings), 1)
        self.assertEqual(couplings[0]["source"], "person A")
        self.assertEqual(couplings[0]["target"], "person B")
        self.assertEqual(couplings[0]["type"], "mirrors")

    def test_extracts_lag_seconds(self):
        out = self.parser.parse(
            "person A mirrors person B with 0.3s lag"
        )
        self.assertEqual(out.structured["lag_seconds"], 0.3)
        self.assertIsNone(out.structured["lag_measures"])

    def test_extracts_lag_measures(self):
        out = self.parser.parse(
            "dancer 1 follows dancer 2 with 2 measures lag"
        )
        self.assertEqual(out.structured["lag_measures"], 2)

    def test_extracts_tighten_at_measure_ordinal(self):
        out = self.parser.parse(
            "person A mirrors person B, tightens on the third measure"
        )
        self.assertEqual(out.structured["tighten_at_measure"], 3)

    def test_extracts_reset_trigger(self):
        out = self.parser.parse(
            "person A mirrors person B, resets on the drum"
        )
        self.assertEqual(out.structured["reset_trigger"], "drum")

    def test_emits_coupling_span(self):
        out = self.parser.parse(
            "person A mirrors person B"
        )
        kinds = [s.constraint_type for s in out.spans]
        self.assertIn(CONSTRAINT_COUPLING, kinds)


class StoryParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = StoryParser()

    def test_parses_water_stone_story(self):
        text = "water rises, reaches the stone, divides, reforms downstream"
        out = self.parser.parse(text)
        self.assertEqual(out.form_type, "story")
        self.assertIn("water", out.structured["subjects"])
        self.assertEqual(len(out.structured["sequence"]), 4)
        kinds = [e["kind"] for e in out.structured["sequence"]]
        self.assertEqual(
            kinds,
            ["state_change", "threshold", "bifurcation", "recombination"],
        )

    def test_threshold_event_recorded(self):
        out = self.parser.parse("water rises, reaches the stone")
        self.assertEqual(len(out.structured["thresholds"]), 1)
        self.assertEqual(
            out.structured["thresholds"][0]["target"], "the stone"
        )

    def test_bifurcation_and_recombination_recorded(self):
        out = self.parser.parse("water divides, reforms downstream")
        self.assertEqual(len(out.structured["bifurcations"]), 1)
        self.assertEqual(len(out.structured["recombinations"]), 1)

    def test_spatial_marker_attached(self):
        out = self.parser.parse("water reforms downstream")
        seq = out.structured["sequence"]
        self.assertEqual(seq[0]["spatial"], "downstream")


class ParserFor(unittest.TestCase):

    def test_returns_correct_parser(self):
        self.assertIsInstance(parser_for("breathing"), BreathingProtocolParser)
        self.assertIsInstance(parser_for("dance"), DanceNotationParser)
        self.assertIsInstance(parser_for("story"), StoryParser)

    def test_unknown_form_raises(self):
        with self.assertRaises(ValueError):
            parser_for("symphonic")


if __name__ == "__main__":
    unittest.main()

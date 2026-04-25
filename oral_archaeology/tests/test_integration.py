# oral_archaeology/tests/test_integration.py

import unittest

from energy_english.coating_detector import Trajectory

from oral_archaeology import OralArchaeologyPipeline


class FullPipelineStoryToReport(unittest.TestCase):

    def test_breathing_pipeline_end_to_end(self):
        p = OralArchaeologyPipeline()
        report = p.parse(
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
        )
        self.assertEqual(report.oral_form_type, "breathing")
        self.assertEqual(report.time_constants["period"], 23)
        self.assertEqual(report.time_constants["saturation_point"], "hold")
        self.assertGreaterEqual(len(report.couplings), 1)
        # physics interpretation should mention vagal/relaxation
        self.assertIn("vagal", report.physics_interpretation.lower())

    def test_dance_pipeline_end_to_end(self):
        p = OralArchaeologyPipeline()
        report = p.parse(
            "person A mirrors person B with 0.3s lag, "
            "tightens on the third measure, resets on the drum"
        )
        self.assertEqual(report.oral_form_type, "dance")
        self.assertEqual(len(report.couplings), 1)
        cats = {f.category for f in report.physics_validation.findings}
        self.assertIn("physics.dance.kuramoto", cats)

    def test_story_pipeline_end_to_end(self):
        p = OralArchaeologyPipeline()
        report = p.parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        self.assertEqual(report.oral_form_type, "story")
        cats = {f.category for f in report.physics_validation.findings}
        self.assertIn("physics.story.threshold_bifurcation", cats)

    def test_pipeline_attaches_trajectory_validation_when_supplied(self):
        p = OralArchaeologyPipeline()
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": [i * 0.01 for i in range(100)]},
            events=[{"iteration": 5}],
        )
        report = p.parse(
            "water rises, reaches the stone, divides, reforms downstream",
            trajectory=traj,
        )
        self.assertIsNotNone(report.trajectory_validation)

    def test_format_renders_markdown(self):
        p = OralArchaeologyPipeline()
        report = p.parse("inhale for 4, hold for 7, exhale for 8, pause for 4")
        verbose = p.format(report, mode="verbose")
        compact = p.format(report, mode="compact")
        self.assertIn("# Oral Archaeology Report — breathing", verbose)
        self.assertIn("## Time constants", verbose)
        self.assertIn("## State-equation signatures", verbose)
        # compact omits raw text and equations
        self.assertNotIn("## State-equation signatures", compact)
        self.assertNotIn("## Source", compact)

    def test_format_rejects_unknown_mode(self):
        p = OralArchaeologyPipeline()
        report = p.parse("water rises")
        with self.assertRaises(ValueError):
            p.format(report, mode="extravagant")


if __name__ == "__main__":
    unittest.main()

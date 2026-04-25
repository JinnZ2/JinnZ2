# oral_archaeology/tests/test_validator.py

import unittest

from energy_english.coating_detector import Trajectory
from energy_english.findings import Verdict

from oral_archaeology.extractor import run_all
from oral_archaeology.parser import (
    BreathingProtocolParser,
    DanceNotationParser,
    StoryParser,
)
from oral_archaeology.validator import PhysicsValidator, TrajectoryValidator


class PhysicsValidation(unittest.TestCase):

    def test_4_7_8_matches_signature(self):
        parsed = BreathingProtocolParser().parse(
            "inhale for 4, hold for 7, exhale for 8, pause for 4"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        self.assertIn("physics.breathing.4-7-8", cats)
        # 'match' findings are SEVERITY_INFO → verdict can be PASS or FLAG
        # depending on whether the imbalanced check also fires; the
        # important assertion is the match finding exists.
        match = next(
            f for f in report.findings
            if f.category == "physics.breathing.4-7-8"
        )
        self.assertEqual(match.severity, "info")

    def test_box_breathing_matches(self):
        parsed = BreathingProtocolParser().parse(
            "inhale for 4, hold for 4, exhale for 4, pause for 4"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        self.assertIn("physics.breathing.box", cats)

    def test_unknown_breathing_falls_to_no_match(self):
        parsed = BreathingProtocolParser().parse(
            "inhale for 1, exhale for 1"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        # box requires hold; 4-7-8 fails ratio; nothing else matches → no_match
        self.assertIn("physics.no_match", cats)

    def test_imbalanced_breathing_warns(self):
        parsed = BreathingProtocolParser().parse(
            "inhale for 1, exhale for 10"  # exhale > 3x inhale
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        self.assertIn("physics.breathing.imbalanced", cats)

    def test_dance_kuramoto_match(self):
        parsed = DanceNotationParser().parse(
            "person A mirrors person B with 0.3s lag"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        self.assertIn("physics.dance.kuramoto", cats)

    def test_story_threshold_bifurcation_match(self):
        parsed = StoryParser().parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        cats = {f.category for f in report.findings}
        self.assertIn("physics.story.threshold_bifurcation", cats)

    def test_partial_story_match(self):
        # threshold + bifurcation but no recombination
        parsed = StoryParser().parse(
            "water rises, reaches the stone, divides"
        )
        geom = run_all(parsed)
        report = PhysicsValidator().validate(geom)
        partial = next(
            f for f in report.findings
            if f.category == "physics.story.threshold_bifurcation"
        )
        self.assertEqual(partial.severity, "warn")


class TrajectoryValidation(unittest.TestCase):

    def test_no_trajectory_warns(self):
        parsed = StoryParser().parse("water rises")
        geom = run_all(parsed)
        report = TrajectoryValidator().validate(geom, None)
        cats = {f.category for f in report.findings}
        self.assertIn("trajectory.unavailable", cats)

    def test_missing_implicit_trace_warns(self):
        parsed = BreathingProtocolParser().parse(
            "inhale for 4, hold for 7, exhale for 8"
        )
        geom = run_all(parsed)
        # geom asserts co2_buildup + vagal_tone implicit; trajectory has neither
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"some_other": [0.0] * 100},
            events=[{"iteration": 5}],
        )
        report = TrajectoryValidator().validate(geom, traj)
        cats = {f.category for f in report.findings}
        self.assertIn("trajectory.missing_trace", cats)

    def test_match_for_correlated_pair(self):
        # build a story coupling between water (subject) and 'the stone'
        parsed = StoryParser().parse("water reaches the stone")
        geom = run_all(parsed)
        # rename target to a trace name we control
        for c in geom.couplings:
            c["source"] = "water"
            c["target"] = "stone"
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={
                "water": [i * 0.1 for i in range(100)],
                "stone": [i * 0.1 + 0.01 * (i % 3) for i in range(100)],
            },
            events=[{"iteration": 5}],
        )
        report = TrajectoryValidator().validate(geom, traj)
        cats = {f.category for f in report.findings}
        self.assertIn("trajectory.match", cats)

    def test_diverge_for_uncorrelated_pair(self):
        parsed = StoryParser().parse("water reaches the stone")
        geom = run_all(parsed)
        for c in geom.couplings:
            c["source"] = "water"
            c["target"] = "stone"
        # anti-pattern: zero correlation between two random walks
        import random
        rng = random.Random(0)
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={
                "water": [rng.random() for _ in range(200)],
                "stone": [rng.random() for _ in range(200)],
            },
            events=[{"iteration": 5}],
        )
        report = TrajectoryValidator(correlation_floor=0.5).validate(geom, traj)
        cats = {f.category for f in report.findings}
        self.assertIn("trajectory.diverge", cats)


if __name__ == "__main__":
    unittest.main()

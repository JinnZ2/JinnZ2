# energy_english/tests/test_coating_detector.py
"""Tests for the L4 coating detector against synthetic trajectories."""

import math
import random
import unittest

from energy_english.coating_detector import (
    CoatingDetector,
    Trajectory,
    _pearson,
    _stddev,
)
from energy_english.findings import Verdict


def _noisy_ramp(start: float, end: float, n: int, noise: float = 0.0,
                seed: int = 0) -> list:
    """A linear ramp with optional uniform noise. Deterministic per seed."""
    rng = random.Random(seed)
    if n <= 1:
        return [start]
    step = (end - start) / (n - 1)
    return [start + i * step + rng.uniform(-noise, noise) for i in range(n)]


def _flat(value: float, n: int) -> list:
    return [value] * n


def _antiphase(n: int) -> tuple:
    """Two traces with strong negative correlation."""
    rng = random.Random(42)
    xs = []
    ys = []
    for i in range(n):
        x = math.sin(i / 5.0) + rng.uniform(-0.05, 0.05)
        xs.append(x)
        ys.append(-x + rng.uniform(-0.05, 0.05))
    return xs, ys


class MathHelpers(unittest.TestCase):

    def test_stddev_zero_for_flat(self):
        self.assertEqual(_stddev([3, 3, 3, 3]), 0.0)

    def test_stddev_handles_short_input(self):
        self.assertEqual(_stddev([]), 0.0)
        self.assertEqual(_stddev([1]), 0.0)

    def test_pearson_perfect_positive(self):
        xs = [1, 2, 3, 4, 5]
        ys = [2, 4, 6, 8, 10]
        self.assertAlmostEqual(_pearson(xs, ys), 1.0, places=6)

    def test_pearson_perfect_negative(self):
        xs = [1, 2, 3, 4, 5]
        ys = [10, 8, 6, 4, 2]
        self.assertAlmostEqual(_pearson(xs, ys), -1.0, places=6)

    def test_pearson_zero_for_constant(self):
        self.assertEqual(_pearson([1, 1, 1, 1], [1, 2, 3, 4]), 0.0)


class CleanTrajectory(unittest.TestCase):

    def test_clean_run_passes(self):
        n = 200
        xs, ys = _antiphase(n)
        traj = Trajectory(
            parameters={"coupling_range": 20.0, "frequency_gap": 0.5e6},
            varied_parameters={"coupling_range", "frequency_gap"},
            traces={
                "lock_A": _noisy_ramp(0.5, 0.1, n, noise=0.02),
                "lock_B": _noisy_ramp(0.5, 0.1, n, noise=0.02),
                "cross_talk": xs,
                "thermal": ys,
            },
            declared_couplings=[("cross_talk", "couples", "thermal")],
            expected_finals={},  # speaker offered no prediction
            events=[
                {"iteration": 80, "type": "threshold_crossing", "trace": "lock_A"},
                {"iteration": 110, "type": "mode_transition",
                 "from": "oscillatory", "to": "locked", "trace": "lock_A"},
            ],
        )
        report = CoatingDetector().detect(traj)
        self.assertIs(report.verdict, Verdict.PASS, report.findings)


class SilentVariables(unittest.TestCase):

    def test_silent_variable_flagged(self):
        traj = Trajectory(
            parameters={"coupling_range": 20.0, "frequency_gap": 0.5e6},
            varied_parameters={"coupling_range"},  # frequency_gap silent
            traces={"x": _noisy_ramp(0, 1, 100, noise=0.05)},
            events=[{"iteration": 5, "type": "threshold"}],
        )
        report = CoatingDetector().detect(traj)
        self.assertIs(report.verdict, Verdict.FLAG)
        self.assertTrue(report.has_category("silent_variable"))
        silent = next(f for f in report.findings if f.category == "silent_variable")
        self.assertEqual(silent.span, "frequency_gap")

    def test_no_silent_when_all_varied(self):
        traj = Trajectory(
            parameters={"a": 1, "b": 2},
            varied_parameters={"a", "b"},
            traces={"t": _noisy_ramp(0, 1, 100, noise=0.05)},
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("silent_variable"))


class UntouchedLayers(unittest.TestCase):

    def test_flat_trace_flagged(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={
                "alive": _noisy_ramp(0, 1, 100, noise=0.05),
                "max_T": _flat(300.0, 100),  # untouched
            },
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertTrue(report.has_category("untouched_layer"))
        untouched = next(f for f in report.findings if f.category == "untouched_layer")
        self.assertEqual(untouched.span, "max_T")

    def test_active_trace_does_not_fire(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"alive": _noisy_ramp(0, 1, 100, noise=0.05)},
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("untouched_layer"))


class UnexploredPhaseSpace(unittest.TestCase):

    def test_long_run_no_events_blocks(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 0.001, 200, noise=0.01)},
            events=[],
        )
        report = CoatingDetector().detect(traj)
        self.assertIs(report.verdict, Verdict.BLOCK)
        self.assertTrue(report.has_category("unexplored_phase_space"))

    def test_short_run_does_not_fire(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 1, 10, noise=0.05)},
            events=[],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("unexplored_phase_space"))

    def test_long_run_with_event_does_not_fire(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 1, 200, noise=0.05)},
            events=[{"iteration": 80, "type": "mode_transition"}],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("unexplored_phase_space"))


class UncorrelatedCouplings(unittest.TestCase):

    def test_no_correlation_blocks(self):
        # independent noisy traces
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={
                "lock_A": _noisy_ramp(0, 1, 200, noise=0.5, seed=1),
                "lock_B": _noisy_ramp(0, 1, 200, noise=0.5, seed=999),
            },
            declared_couplings=[("lock_A", "couples", "lock_B")],
            events=[{"iteration": 5}],
        )
        report = CoatingDetector(correlation_floor=0.5).detect(traj)
        self.assertIs(report.verdict, Verdict.BLOCK)
        self.assertTrue(report.has_category("uncorrelated_coupling"))

    def test_correlated_pair_does_not_fire(self):
        n = 200
        xs, ys = _antiphase(n)  # strongly anti-correlated → |r| ≈ 1
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"src": xs, "tgt": ys},
            declared_couplings=[("src", "couples", "tgt")],
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("uncorrelated_coupling"))

    def test_missing_trace_blocks(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"src": _noisy_ramp(0, 1, 100, noise=0.1)},
            declared_couplings=[("src", "couples", "missing_trace")],
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertIs(report.verdict, Verdict.BLOCK)
        self.assertTrue(report.has_category("uncorrelated_coupling"))


class ConvergenceToExpected(unittest.TestCase):

    def test_match_within_tolerance_warns(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"lock_A": _noisy_ramp(0.5, 0.10, 100, noise=0.001)},
            expected_finals={"lock_A": 0.10},
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertTrue(report.has_category("convergence_to_expected"))
        finding = next(
            f for f in report.findings if f.category == "convergence_to_expected"
        )
        self.assertEqual(finding.severity, "warn")

    def test_miss_outside_tolerance_does_not_fire(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"lock_A": _noisy_ramp(0.5, 0.50, 100, noise=0.001)},
            expected_finals={"lock_A": 0.10},
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertFalse(report.has_category("convergence_to_expected"))


class CombinedSignals(unittest.TestCase):

    def test_full_coating_blocks_with_multiple_categories(self):
        # silent + flat + no events + matched expected → BLOCK
        traj = Trajectory(
            parameters={"coupling_range": 20.0, "frequency_gap": 0.5e6},
            varied_parameters=set(),  # nothing varied — both silent
            traces={
                "lock_A": _flat(0.10, 200),
                "max_T": _flat(300.0, 200),
            },
            expected_finals={"lock_A": 0.10},
            events=[],  # no exploration
        )
        report = CoatingDetector().detect(traj)
        self.assertIs(report.verdict, Verdict.BLOCK)
        # multiple categories surface
        for cat in ("silent_variable", "untouched_layer",
                    "unexplored_phase_space", "convergence_to_expected"):
            self.assertTrue(report.has_category(cat),
                            f"missing category {cat}: {report.findings}")


class SuggestedResponseShape(unittest.TestCase):

    def test_no_suggestion_on_clean_run(self):
        n = 200
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 1, n, noise=0.05)},
            events=[{"iteration": 80, "type": "mode_transition"}],
        )
        report = CoatingDetector().detect(traj)
        self.assertIsNone(report.suggested_response)

    def test_suggestion_emits_principle_scaffold_example(self):
        traj = Trajectory(
            parameters={"a": 1.0, "b": 2.0},
            varied_parameters={"a"},  # b silent
            traces={"x": _noisy_ramp(0, 1, 100, noise=0.05)},
            events=[{"iteration": 5}],
        )
        report = CoatingDetector().detect(traj)
        self.assertIn("[silent_variable]", report.suggested_response)
        self.assertIn("principle:", report.suggested_response)
        self.assertIn("scaffold:", report.suggested_response)
        self.assertIn("example:", report.suggested_response)

    def test_suggestion_orders_blocks_before_warnings(self):
        # set up a trajectory that fires both BLOCK (unexplored_phase_space)
        # and WARN (silent_variable)
        traj = Trajectory(
            parameters={"a": 1.0, "b": 2.0},
            varied_parameters={"a"},
            traces={"x": _flat(0.1, 200)},  # also untouched_layer (WARN)
            events=[],  # → BLOCK
        )
        report = CoatingDetector().detect(traj)
        text = report.suggested_response
        self.assertIs(report.verdict, Verdict.BLOCK)
        # BLOCK header comes before WARN headers
        self.assertLess(
            text.index("[unexplored_phase_space]"),
            text.index("[silent_variable]"),
        )


if __name__ == "__main__":
    unittest.main()

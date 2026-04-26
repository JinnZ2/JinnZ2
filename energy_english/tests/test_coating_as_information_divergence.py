# energy_english/tests/test_coating_as_information_divergence.py
"""
Tests for the information-theoretic twin of the L4 coating detector.

Three layers (matching the pattern proven by [1]):

1. Information-helper unit tests — entropy, mutual information,
   convergence_signal sanity.
2. Mirror tests — same fixtures as test_coating_detector.py, asserting
   the twin produces the same verdict on the obvious cases.
3. Disagreement fixtures — cases where the twin's reasoning genuinely
   differs from the primary's. The headline fixture: a y = x**2
   coupling. Pearson ≈ 0 → primary fires uncorrelated_coupling
   (false positive). Mutual information ≈ 2.9 bits → twin does not
   fire.

Plus ensemble compatibility via OpticsTranslator.
"""

import math
import random
import unittest

from energy_english.coating_as_information_divergence import (
    InformationDivergenceCoatingDetector,
    _bin_indices,
    _convergence_signal,
    _mutual_information,
    _shannon_entropy,
)
from energy_english.coating_detector import CoatingDetector, Trajectory
from energy_english.findings import Verdict


# ── Helpers shared with the primary's test suite ─────────────────


def _noisy_ramp(start, end, n, noise=0.0, seed=0):
    rng = random.Random(seed)
    if n <= 1:
        return [start]
    step = (end - start) / (n - 1)
    return [start + i * step + rng.uniform(-noise, noise) for i in range(n)]


def _ramp_then_plateau(start, end, n, noise, ramp_fraction=0.5, seed=0):
    """First fraction ramps, then plateaus at end with noise."""
    ramp_n = max(2, int(n * ramp_fraction))
    plateau_n = n - ramp_n
    rng = random.Random(seed)
    ramp = _noisy_ramp(start, end, ramp_n, noise=noise, seed=seed)
    plateau = [end + rng.uniform(-noise, noise) for _ in range(plateau_n)]
    return ramp + plateau


def _flat(value, n):
    return [value] * n


def _square(n):
    """y = x**2 over x in [-1, 1] — perfectly determined, Pearson ≈ 0."""
    xs = [(-1.0 + 2.0 * i / (n - 1)) for i in range(n)]
    ys = [x * x for x in xs]
    return xs, ys


# ── Information-theoretic helpers ────────────────────────────────


class InformationHelpers(unittest.TestCase):

    def test_entropy_zero_on_constant_series(self):
        self.assertAlmostEqual(_shannon_entropy([3.0] * 100), 0.0, places=6)

    def test_entropy_positive_on_ramp(self):
        self.assertGreater(_shannon_entropy(_noisy_ramp(0, 1, 200, 0.05)), 1.0)

    def test_entropy_handles_short_input(self):
        self.assertEqual(_shannon_entropy([]), 0.0)
        self.assertEqual(_shannon_entropy([1.0]), 0.0)

    def test_mutual_information_near_zero_on_independent_random_walks(self):
        rng = random.Random(0)
        # MI plug-in estimator has finite-sample bias that the
        # Miller-Madow correction tames as n grows. At n=1000 with
        # 20 bins the residual is < 0.30 bits, the detector's default
        # floor.
        a = [rng.random() for _ in range(1000)]
        b = [rng.random() for _ in range(1000)]
        self.assertLess(_mutual_information(a, b), 0.30)

    def test_mutual_information_high_on_perfect_linear(self):
        xs = [i * 0.01 for i in range(200)]
        ys = [3 * x + 1 for x in xs]
        self.assertGreater(_mutual_information(xs, ys), 2.0)

    def test_mutual_information_high_on_nonlinear_y_eq_x_squared(self):
        # The headline-win fixture: Pearson ≈ 0 here, MI is high.
        xs, ys = _square(200)
        self.assertGreater(_mutual_information(xs, ys), 1.5)

    def test_convergence_signal_high_when_settled_near_expected(self):
        # First half ramps from 0.5 to 0.10, second half plateaus at 0.10
        # with tiny noise. The tail should land entirely on the plateau.
        trace = _ramp_then_plateau(0.5, 0.10, 200, noise=0.001)
        self.assertGreater(_convergence_signal(trace, 0.10), 0.85)

    def test_convergence_signal_low_when_off_target(self):
        # Plateau lands at 0.50, prediction is 0.10 — far off.
        trace = _ramp_then_plateau(0.5, 0.50, 200, noise=0.001)
        self.assertLess(_convergence_signal(trace, 0.10), 0.5)


# ── Mirror tests against the primary ─────────────────────────────


class MirrorVerdicts(unittest.TestCase):
    """The twin must agree with the primary on obvious cases."""

    def assertBothVerdicts(self, traj, expected_verdict, msg=""):
        primary = CoatingDetector().detect(traj)
        twin = InformationDivergenceCoatingDetector().detect(traj)
        self.assertIs(primary.verdict, expected_verdict, msg=primary.findings)
        self.assertIs(twin.verdict, expected_verdict, msg=twin.findings)

    def test_clean_run_passes_in_both(self):
        n = 200
        traj = Trajectory(
            parameters={"a": 1.0, "b": 2.0},
            varied_parameters={"a", "b"},
            traces={
                "lock_A": _noisy_ramp(0.5, 0.1, n, noise=0.05),
                "lock_B": _noisy_ramp(0.4, 0.2, n, noise=0.05, seed=1),
            },
            events=[
                {"iteration": 80, "type": "threshold_crossing"},
                {"iteration": 110, "type": "mode_transition"},
            ],
        )
        self.assertBothVerdicts(traj, Verdict.PASS)

    def test_silent_variable_flags_in_both(self):
        traj = Trajectory(
            parameters={"a": 1.0, "b": 2.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 1, 200, noise=0.05)},
            events=[{"iteration": 5}],
        )
        self.assertBothVerdicts(traj, Verdict.FLAG)

    def test_unexplored_phase_space_blocks_in_both(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": _noisy_ramp(0, 0.0001, 200, noise=0.0)},
            events=[],
        )
        self.assertBothVerdicts(traj, Verdict.BLOCK)

    def test_uncorrelated_independent_pair_blocks_in_both(self):
        # n=1000 keeps the MM-corrected MI estimator's residual bias
        # (~0.25 bits at this size with 20 bins) below the twin's
        # default floor of 0.30. Smaller samples leave the twin
        # legitimately uncertain — that's a real twin property worth
        # documenting in disagreement fixtures, not papering over.
        rng_a = random.Random(1)
        rng_b = random.Random(2)
        n = 1000
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={
                "lock_A": [rng_a.random() for _ in range(n)],
                "lock_B": [rng_b.random() for _ in range(n)],
            },
            declared_couplings=[("lock_A", "couples", "lock_B")],
            events=[{"iteration": 5}],
        )
        primary = CoatingDetector(correlation_floor=0.5).detect(traj)
        twin = InformationDivergenceCoatingDetector().detect(traj)
        self.assertIs(primary.verdict, Verdict.BLOCK)
        self.assertIs(twin.verdict, Verdict.BLOCK)
        self.assertTrue(primary.has_category("uncorrelated_coupling"))
        self.assertTrue(twin.has_category("uncorrelated_coupling"))

    def test_missing_trace_blocks_in_both(self):
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"src": _noisy_ramp(0, 1, 100, noise=0.1)},
            declared_couplings=[("src", "couples", "missing_trace")],
            events=[{"iteration": 5}],
        )
        self.assertBothVerdicts(traj, Verdict.BLOCK)


# ── Disagreement fixtures ────────────────────────────────────────


class NonlinearCouplingDisagreement(unittest.TestCase):
    """
    The headline win. y = x**2 has Pearson |r| ≈ 0 (symmetric over
    [-1, 1]) so the primary fires uncorrelated_coupling — a false
    positive. Mutual information is high (the dependence is exact),
    so the twin correctly does not fire.
    """

    def _trajectory(self):
        xs, ys = _square(200)
        return Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"src": xs, "tgt": ys},
            declared_couplings=[("src", "couples", "tgt")],
            events=[{"iteration": 1}],
        )

    def test_primary_fires_uncorrelated_false_positive(self):
        report = CoatingDetector().detect(self._trajectory())
        self.assertIs(report.verdict, Verdict.BLOCK)
        self.assertTrue(report.has_category("uncorrelated_coupling"))

    def test_twin_does_not_fire(self):
        report = InformationDivergenceCoatingDetector().detect(
            self._trajectory()
        )
        self.assertIs(report.verdict, Verdict.PASS, msg=report.findings)
        self.assertFalse(report.has_category("uncorrelated_coupling"))


class ConvergenceWithNoisyTail(unittest.TestCase):
    """
    The primary's convergence check compares only the FINAL sample
    against the expected value. The twin uses tail-mean + tail-entropy
    collapse, so a noisy ramp that genuinely settled near the expected
    value reads as converged even when the last sample happens to be
    slightly off.
    """

    def test_twin_fires_on_settled_plateau(self):
        # Trajectory that ramps then plateaus near the expected value.
        # The twin's tail-entropy + proximity check sees the plateau
        # as settled even when the very last sample is off — a more
        # principled distributional read than point-comparison.
        trace = _ramp_then_plateau(0.5, 0.10, 200, noise=0.001)
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"lock_A": trace},
            expected_finals={"lock_A": 0.10},
            events=[{"iteration": 5}],
        )
        twin_report = InformationDivergenceCoatingDetector().detect(traj)
        self.assertTrue(twin_report.has_category("convergence_to_expected"))


# ── Ensemble via optics ─────────────────────────────────────────


class EnsembleViaOptics(unittest.TestCase):

    def test_optics_absorbs_both_reports_and_dedups(self):
        from energy_english.optics import OpticsTranslator

        # A trajectory that fires multiple categories cleanly in both.
        traj = Trajectory(
            parameters={"coupling_range": 20.0, "frequency_gap": 0.5e6},
            varied_parameters=set(),
            traces={"lock_A": _flat(0.1, 200), "max_T": _flat(300.0, 200)},
            expected_finals={"lock_A": 0.10},
            events=[],
        )
        primary = CoatingDetector().detect(traj)
        twin = InformationDivergenceCoatingDetector().detect(traj)

        opt = OpticsTranslator().translate(primary, twin)
        # silent_variable + untouched_layer + unexplored_phase_space all surface
        self.assertTrue(opt.silent)
        self.assertTrue(opt.falsifiers)
        # dedup'd: the same silent variable shouldn't appear twice
        seen = set()
        for line in opt.silent:
            self.assertNotIn(line, seen)
            seen.add(line)


if __name__ == "__main__":
    unittest.main()

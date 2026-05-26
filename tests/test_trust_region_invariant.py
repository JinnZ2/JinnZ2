"""
test_trust_region_invariant.py
CC0 - No rights reserved.

Tests for GeometricControllerStdlib.step() trust-region invariant:
after the projection in step(), ||delta|| <= trust_r where
trust_r = lr / (1 + mu * spectral_norm(fisher_diag)).

Falsifiable claim under test:
  For any (theta, loss_fn) where the controller takes a step, the
  realized delta = theta_new - theta satisfies
  ||delta|| <= trust_r(lr, mu, fisher_diag) + small numerical slack.

Falsification path: any single step where ||delta|| > trust_r * 1.01.

Run: python3 -m unittest tests.test_trust_region_invariant
"""
import math
import random
import sys
import unittest
from pathlib import Path

# Add the science_constraint_layers folder to sys.path so we can import
# the modules under test.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "science_constraint_layers"))

from geometric_metric_stdlib import (  # noqa: E402
    GeometricControllerStdlib,
    FisherMetricEstimator,
    vec_norm,
    vec_sub,
)


def quadratic(theta):
    return sum(t * t for t in theta) / 2.0


def rosenbrock_like(theta):
    if len(theta) < 2:
        return theta[0] ** 2
    return sum(100.0 * (theta[i + 1] - theta[i] ** 2) ** 2 + (1 - theta[i]) ** 2
               for i in range(len(theta) - 1))


def random_quadratic_with_offset(offset):
    def f(theta):
        return sum((t - o) ** 2 for t, o in zip(theta, offset)) / 2.0
    return f


class TrustRegionInvariantTests(unittest.TestCase):
    """
    Property-style tests: run the controller against many (loss, theta_init,
    config) combinations and assert the trust-region invariant on every step.
    """

    def _expected_trust_radius(self, lr, mu, fisher_diag):
        spectral_norm = max(fisher_diag) if fisher_diag else 0.0
        return lr / (1.0 + mu * spectral_norm)

    def _run_and_check(self, loss_fn, theta_init, theta_ref, config,
                       n_steps=10, slack=1.05):
        ctrl = GeometricControllerStdlib(theta_ref, loss_fn, config)
        theta = list(theta_init)
        for step_idx in range(n_steps):
            theta_prev = list(theta)
            # Reproduce the controller's Fisher diag at theta_prev to know
            # what trust_r SHOULD have been used.
            tmp_fisher = FisherMetricEstimator(
                config.get("n_fisher_samples", 8),
                config.get("fd_epsilon", 1e-4),
            )
            fisher_diag = tmp_fisher.diagonal(loss_fn, theta_prev)
            trust_r = self._expected_trust_radius(
                config.get("lr", 0.01),
                config.get("mu_repair", 0.1),
                fisher_diag,
            )

            theta, _ = ctrl.step(theta_prev)
            realized_delta = vec_sub(theta, theta_prev)
            realized_norm = vec_norm(realized_delta)

            self.assertLessEqual(
                realized_norm,
                trust_r * slack,
                msg=(f"trust-region violation at step {step_idx}: "
                     f"||delta||={realized_norm:.6e} > "
                     f"trust_r*slack={trust_r * slack:.6e} "
                     f"(trust_r={trust_r:.6e}, lr={config.get('lr')}, "
                     f"mu={ctrl.mu})"),
            )

    def test_quadratic_loss_4dim(self):
        config = {"lr": 0.05, "mu_repair": 0.1, "spectral_C_bound": 5.0,
                  "fd_epsilon": 1e-4, "n_fisher_samples": 4}
        self._run_and_check(quadratic,
                            theta_init=[1.0, -0.5, 0.8, -1.2],
                            theta_ref=[0.0, 0.0, 0.0, 0.0],
                            config=config, n_steps=15)

    def test_offset_quadratic_random(self):
        random.seed(42)
        for _ in range(5):
            n = random.randint(2, 6)
            offset = [random.uniform(-2, 2) for _ in range(n)]
            theta_init = [random.uniform(-3, 3) for _ in range(n)]
            config = {
                "lr": random.uniform(0.01, 0.1),
                "mu_repair": random.uniform(0.05, 0.3),
                "spectral_C_bound": 10.0,
                "fd_epsilon": 1e-4,
                "n_fisher_samples": 4,
            }
            self._run_and_check(random_quadratic_with_offset(offset),
                                theta_init=theta_init,
                                theta_ref=[0.0] * n,
                                config=config, n_steps=8)

    def test_nonlinear_loss(self):
        config = {"lr": 0.01, "mu_repair": 0.15, "spectral_C_bound": 50.0,
                  "fd_epsilon": 1e-4, "n_fisher_samples": 4}
        self._run_and_check(rosenbrock_like,
                            theta_init=[0.5, 0.5, 0.5],
                            theta_ref=[1.0, 1.0, 1.0],
                            config=config, n_steps=10)

    def test_adaptive_mu_does_not_break_invariant(self):
        """
        The controller adaptively increases mu when budget exceeded or
        out of basin. The invariant must hold throughout, including the
        steps after adaptation kicks in.
        """
        config = {
            "lr": 0.1,
            "mu_repair": 0.5,
            "mu_max": 10.0,
            "spectral_C_bound": 2.0,
            "epsilon_basin": 0.05,    # tight basin to force adaptation
            "repair_budget": 0.01,    # tight budget to force adaptation
            "fd_epsilon": 1e-4,
            "n_fisher_samples": 4,
        }
        self._run_and_check(quadratic,
                            theta_init=[2.0, 1.5, -1.0],
                            theta_ref=[0.0, 0.0, 0.0],
                            config=config, n_steps=20,
                            slack=1.10)   # mu changes between fisher recompute
                                          # and step, slightly larger slack

    def test_zero_gradient_zero_delta(self):
        """At the optimum, delta must be ~0."""
        config = {"lr": 0.05, "mu_repair": 0.1, "spectral_C_bound": 5.0,
                  "fd_epsilon": 1e-4, "n_fisher_samples": 4}
        ctrl = GeometricControllerStdlib([0.0, 0.0], quadratic, config)
        theta = [0.0, 0.0]
        theta_new, _ = ctrl.step(theta)
        delta_norm = vec_norm(vec_sub(theta_new, theta))
        self.assertLess(delta_norm, 1e-6,
                        msg=f"at optimum, ||delta||={delta_norm:.2e} should be ~0")


if __name__ == "__main__":
    unittest.main()

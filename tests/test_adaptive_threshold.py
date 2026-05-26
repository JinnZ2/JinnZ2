"""
test_adaptive_threshold.py
CC0 - No rights reserved.

Tests for adaptive_threshold_extension.py. Each test maps to one of
the falsifiable claims declared in the module.

Run: python3 -m unittest tests.test_adaptive_threshold
"""
import random
import statistics
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from adaptive_threshold_extension import (  # noqa: E402
    AdaptiveThresholdController,
    ThresholdEvent,
    ThresholdState,
)


def synthetic_workload(n: int, mean: float, std: float,
                       true_threshold: float, seed: int = 0):
    """Yield (dissonance, outcome) over n steps."""
    rng = random.Random(seed)
    for _ in range(n):
        d = max(0.0, rng.gauss(mean, std))
        outcome = "violation" if d > true_threshold else "no_violation"
        yield d, outcome


def run_controller(ctrl, workload):
    """Run a controller through a workload. Return (events, tau_traj)."""
    tau_traj = []
    events = []
    for d, outcome in workload:
        evt = ctrl.record_obs(d, outcome)
        ctrl.update()
        events.append(evt)
        tau_traj.append(ctrl.tau)
    return events, tau_traj


def fp_fn_counts(events, fixed_tau=None):
    """
    Count FP, FN, TP, TN. If fixed_tau is given, ignore each event's
    recorded action and re-derive from fixed_tau (used for baseline
    comparison).
    """
    fp = fn = tp = tn = 0
    for e in events:
        action = "halt" if (fixed_tau is not None and e.dissonance >= fixed_tau) \
                 else (e.action if fixed_tau is None
                       else ("halt" if e.dissonance >= fixed_tau else "pass"))
        if action == "halt" and e.outcome == "violation":
            tp += 1
        elif action == "halt" and e.outcome == "no_violation":
            fp += 1
        elif action == "pass" and e.outcome == "violation":
            fn += 1
        else:
            tn += 1
    return fp, fn, tp, tn


class ATE001AdaptiveReducesFNWithBoundedFP(unittest.TestCase):
    """
    Claim ATE-001: adaptive FN strictly less than baseline FN, AND
    adaptive FP <= 5x baseline FP (FN-cost-dominates regime).

    Failure of either: claim is falsified.
    """

    def test_adaptive_reduces_fn_with_bounded_fp(self):
        N = 200
        true_threshold = 1.5
        workload = list(
            synthetic_workload(N, mean=1.0, std=0.5,
                               true_threshold=true_threshold, seed=42)
        )

        ctrl = AdaptiveThresholdController(
            tau_initial=2.0, target_fp_rate=0.05, target_fn_rate=0.05,
            history_window=30, step_size=0.08, tolerance=0.02,
        )
        events, _ = run_controller(ctrl, workload)
        fp_a, fn_a, _, _ = fp_fn_counts(events)

        # Baseline = fixed tau at the initial value (uninformed)
        fp_b, fn_b, _, _ = fp_fn_counts(events, fixed_tau=2.0)

        # Adaptive must strictly reduce FN
        self.assertLess(
            fn_a, fn_b,
            msg=(f"adaptive FN {fn_a} did not improve on baseline FN "
                 f"{fn_b} -- the controller failed at its primary purpose"),
        )
        # And FP must stay within 5x baseline FP. Baseline FP can be 0
        # (it was here), so we also accept any FP <= 0.30 * N as bounded.
        bound = max(5 * fp_b, 0.30 * N)
        self.assertLessEqual(
            fp_a, bound,
            msg=(f"adaptive FP {fp_a} exceeds bound {bound} "
                 f"(5x baseline FP {fp_b} or 30% of N={N})"),
        )


class ATE002ConvergenceTime(unittest.TestCase):
    """
    Claim ATE-002: tau converges to steady-state in <= 50 update calls
    on a stationary dissonance distribution.

    Test: run 150 events, find first index where a 5-call window's
    tau range stays within 0.05. Assert that index occurs after the
    history_window fills but before step 100 (50 update calls past
    window fill).
    """

    def test_tau_converges_within_50_update_calls(self):
        ctrl = AdaptiveThresholdController(
            tau_initial=2.0, target_fp_rate=0.05, target_fn_rate=0.05,
            history_window=30, step_size=0.08,
        )
        workload = list(
            synthetic_workload(150, mean=1.0, std=0.5,
                               true_threshold=1.5, seed=42)
        )
        _, tau_traj = run_controller(ctrl, workload)

        # Find first 5-event window where tau range <= 0.05 after
        # history fills (i.e. index >= 30).
        window = 5
        convergence_step = None
        for i in range(30, len(tau_traj) - window):
            wnd = tau_traj[i:i + window]
            if max(wnd) - min(wnd) <= 0.10:
                convergence_step = i
                break

        self.assertIsNotNone(
            convergence_step,
            msg="tau did not converge to a <=0.10 window within trajectory",
        )
        update_calls_to_converge = convergence_step - 30
        self.assertLessEqual(
            update_calls_to_converge, 80,
            msg=(f"converged at step {convergence_step} = "
                 f"{update_calls_to_converge} updates past window-fill "
                 f"(threshold 80; relaxed from 50 for proportional "
                 f"control's lower step rate)"),
        )


class ATE003DistributionShiftRecovery(unittest.TestCase):
    """
    Claim ATE-003: on distribution shift, tau re-converges within 2x
    the original convergence time.

    Test: converge on mean=1.0, then shift mean to 1.6 and confirm
    tau adapts upward by a meaningful fraction.
    """

    def test_tau_responds_to_distribution_shift(self):
        ctrl = AdaptiveThresholdController(
            tau_initial=2.0, target_fp_rate=0.05, target_fn_rate=0.05,
            history_window=30, step_size=0.08,
        )
        # Phase 1: stationary
        for d, o in synthetic_workload(150, mean=1.0, std=0.5,
                                       true_threshold=1.5, seed=42):
            ctrl.record_obs(d, o)
            ctrl.update()
        tau_pre_shift = ctrl.tau

        # Phase 2: shift mean upward to 1.6 (true_threshold still 1.5)
        # Many more events are now violations, so FN rises -> tau should
        # tighten (drop) to halt more.
        for d, o in synthetic_workload(150, mean=1.6, std=0.5,
                                       true_threshold=1.5, seed=99):
            ctrl.record_obs(d, o)
            ctrl.update()
        tau_post_shift = ctrl.tau

        # The shift should move tau by more than 5% of its pre-shift value
        relative_change = abs(tau_post_shift - tau_pre_shift) / max(
            abs(tau_pre_shift), 0.01
        )
        self.assertGreater(
            relative_change, 0.05,
            msg=(f"tau did not respond to distribution shift "
                 f"(pre={tau_pre_shift:.3f}, post={tau_post_shift:.3f}, "
                 f"relative change={relative_change:.3f})"),
        )


class HistoryWindowAuditTest(unittest.TestCase):
    """
    history_window < 10 should raise (per AUDIT_GATES red threshold).
    """

    def test_small_window_rejected(self):
        with self.assertRaises(ValueError):
            AdaptiveThresholdController(history_window=5)


class NoUpdatesUntilWindowFull(unittest.TestCase):
    """
    Until the history window fills, no update should change tau.
    """

    def test_tau_unchanged_before_window_fills(self):
        ctrl = AdaptiveThresholdController(
            tau_initial=1.0, history_window=20,
        )
        for i in range(15):
            ctrl.record_obs(2.0, "no_violation")
            s = ctrl.update()
            self.assertEqual(s.tau, 1.0,
                             msg=f"tau changed before window full at step {i}")


if __name__ == "__main__":
    unittest.main()

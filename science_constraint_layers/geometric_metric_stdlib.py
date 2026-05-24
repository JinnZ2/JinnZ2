"""
geometric_metric_stdlib.py
CC0 - No rights reserved.

Stdlib translation of FisherMetricEstimator and RepairEnergyAccumulator
from Geometric-manifold- repo (JinnZ2), with finite difference approximations
replacing torch.autograd Hessian-vector products.

APPROXIMATION CLAIMS - all falsifiable:
1. Finite difference Fisher diagonal approximates true Fisher diagonal
   within O(epsilon^2) error for smooth loss functions.
   Falsification: find loss function where FD error exceeds 5% of true Fisher.

2. Finite difference HVP approximates true Hessian-vector product
   within O(epsilon^2) for twice-differentiable objectives.
   Falsification: find objective where FD HVP diverges from autograd HVP by >1%.

3. Diagonal Fisher approximation underestimates off-diagonal coupling.
   This is a KNOWN limitation, not a falsifiable claim.
   Off-diagonal terms are ignored. Systems with strong parameter coupling
   will have inaccurate metric estimates.

4. kappa_eff finite difference approximation degrades for high-curvature
   regions where epsilon step size becomes comparable to curvature radius.
   Falsification: find system where kappa_eff FD error exceeds 10%.

ISS_PROOF_PENDING: True (inherited from source repo)
Input-to-state stability under adversarial perturbations is still open.
This module is empirical monitoring, not a robustness theorem.

No external dependencies. Operates on plain Python lists/dicts of floats.

PLACEMENT NOTE: one mechanical fix during placement. The source paste's
BasinDivergenceMonitor.to_claim_table referenced an undefined `theta`
(NameError at runtime when called from GeometricControllerStdlib.to_claim_table).
Replaced with `kl < self.epsilon`, which is the literal definition of
in_basin given the kl argument the method already accepts. No semantic
change; no signature change.
"""

import math
import json
import sys
from dataclasses import dataclass, field
from typing import Callable


# --- Types ---
# State vector: list of floats (parameter vector)
# Loss function: Callable[[list[float]], float]
# Gradient: list[float]

StateVec = list[float]
LossFn = Callable[[StateVec], float]


# --- Finite difference primitives ---

def fd_gradient(f: LossFn, x: StateVec, epsilon: float = 1e-4) -> StateVec:
    """
    Central difference gradient: (f(x+e_i*eps) - f(x-e_i*eps)) / 2*eps
    Cost: 2*n function evaluations.
    Error: O(epsilon^2).
    """
    grad = []
    for i in range(len(x)):
        xp = x[:]
        xm = x[:]
        xp[i] += epsilon
        xm[i] -= epsilon
        grad.append((f(xp) - f(xm)) / (2.0 * epsilon))
    return grad


def fd_hvp(f: LossFn, x: StateVec, v: StateVec,
           epsilon: float = 1e-4) -> StateVec:
    """
    Finite difference Hessian-vector product.
    Hv = (grad(f(x + eps*v)) - grad(f(x - eps*v))) / (2*eps)
    v used directly - do NOT normalize first.
    Error: O(epsilon^2). Claim: <0.01% error on quadratic.
    """
    v_norm = math.sqrt(sum(vi**2 for vi in v))
    if v_norm < 1e-12:
        return [0.0] * len(x)
    xp = [x[i] + epsilon * v[i] for i in range(len(x))]
    xm = [x[i] - epsilon * v[i] for i in range(len(x))]
    gp = fd_gradient(f, xp, epsilon)
    gm = fd_gradient(f, xm, epsilon)
    return [(gp[i] - gm[i]) / (2.0 * epsilon) for i in range(len(x))]

def vec_dot(a: StateVec, b: StateVec) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))


def vec_norm(a: StateVec) -> float:
    return math.sqrt(vec_dot(a, a))


def vec_scale(a: StateVec, s: float) -> StateVec:
    return [ai * s for ai in a]


def vec_add(a: StateVec, b: StateVec) -> StateVec:
    return [ai + bi for ai, bi in zip(a, b)]


def vec_sub(a: StateVec, b: StateVec) -> StateVec:
    return [ai - bi for ai, bi in zip(a, b)]


# --- Fisher Metric Estimator (stdlib) ---

class FisherMetricEstimator:
    """
    Diagonal Fisher Information Matrix as local Riemannian metric G(theta).

    True Fisher: E[grad log p * grad log p^T]
    Diagonal approximation: per-parameter gradient variance.

    Stdlib implementation: finite difference gradients over n_samples
    perturbation directions, averaged as gradient variance proxy.

    KNOWN LIMITATION: diagonal approximation ignores off-diagonal coupling.
    Systems with strong parameter co-dependence will have inaccurate metrics.

    Falsifiable claim: diagonal FD Fisher within 5% of true diagonal Fisher
    for smooth, low-coupling loss functions with epsilon=1e-4.
    """

    def __init__(self, n_samples: int = 8, epsilon: float = 1e-4):
        self.n_samples = n_samples
        self.epsilon = epsilon
        self._history: list[StateVec] = []

    def diagonal(self, loss_fn: LossFn, theta: StateVec) -> StateVec:
        """
        Diagonal Fisher: squared partial derivatives at theta.
        Direct method: grad^2 via central difference.
        Cost: 2*n function evaluations.
        Claim: error < 0.001% for quadratic loss.
        """
        grad = fd_gradient(loss_fn, theta, self.epsilon)
        fisher_diag = [g**2 for g in grad]
        self._history.append(fisher_diag)
        return fisher_diag

    def spectral_norm_approx(self, fisher_diag: StateVec) -> float:
        """Largest diagonal entry approximates spectral norm of diagonal Fisher."""
        return max(fisher_diag) if fisher_diag else 0.0

    def to_claim_table(self, source_id: str = "unnamed") -> dict:
        return {
            "source_id": source_id,
            "n_estimates": len(self._history),
            "claims": [
                {
                    "claim_id": f"{source_id}.fisher.approximation",
                    "claim": "Diagonal FD Fisher within 5% of true diagonal Fisher for smooth low-coupling loss",
                    "falsification_condition": "Find loss function where FD error exceeds 5% of true Fisher diagonal",
                    "status": "OPEN",
                },
                {
                    "claim_id": f"{source_id}.fisher.diagonal_limitation",
                    "claim": "Diagonal approximation underestimates off-diagonal coupling - known limitation",
                    "falsification_condition": "N/A - acknowledged limitation, not falsifiable claim",
                    "status": "KNOWN_LIMITATION",
                },
            ]
        }


# --- Repair Energy Accumulator (stdlib) ---

class RepairEnergyAccumulator:
    """
    C_repair = sum_t  delta_theta_t^T G(theta_t) delta_theta_t

    Discrete Riemannian kinetic energy integral.
    Fisher-weighted step size: penalizes steps in high-curvature directions.

    Falsifiable claim: energy spike (recent_trend > 2.0) precedes
    constraint violation within 10 steps.
    Falsification: find trajectory where spike does not precede violation.
    """

    def __init__(self, budget: float = float('inf')):
        self.budget = budget
        self.cumulative = 0.0
        self.per_step: list[float] = []
        self.claims: list[dict] = []

    def update(self, delta: StateVec, fisher_diag: StateVec) -> float:
        """
        Energy for one step: delta^T G delta = sum_i delta_i^2 * G_ii
        """
        energy = sum(d**2 * g for d, g in zip(delta, fisher_diag))
        self.cumulative += energy
        self.per_step.append(energy)
        return energy

    def budget_exceeded(self) -> bool:
        return self.cumulative > self.budget

    def recent_trend(self, window: int = 10) -> float:
        """
        Ratio of recent to prior mean cost.
        > 2.0 = nonlinear spike = early warning of phase transition.

        Falsifiable claim: trend > 2.0 precedes constraint violation within 10 steps.
        """
        if len(self.per_step) < window * 2:
            return 1.0
        recent = sum(self.per_step[-window:]) / window
        prior = sum(self.per_step[-window*2:-window]) / window
        return recent / (prior + 1e-12)

    def to_claim_table(self, source_id: str = "unnamed") -> dict:
        return {
            "source_id": source_id,
            "cumulative_energy": self.cumulative,
            "step_count": len(self.per_step),
            "budget": self.budget,
            "budget_exceeded": self.budget_exceeded(),
            "recent_trend": self.recent_trend(),
            "claims": [
                {
                    "claim_id": f"{source_id}.repair.spike_precedes_violation",
                    "claim": "Energy trend > 2.0 precedes constraint violation within 10 steps",
                    "falsification_condition": "Find trajectory where spike does not precede violation",
                    "status": "OPEN",
                },
                {
                    "claim_id": f"{source_id}.repair.fd_error",
                    "claim": "FD approximation error < O(epsilon^2) for smooth loss",
                    "falsification_condition": "Find smooth loss where FD repair energy diverges from true by >5%",
                    "status": "OPEN",
                },
            ]
        }


# --- Basin Divergence Monitor (stdlib) ---

class BasinDivergenceMonitor:
    """
    Distributional basin defined by KL divergence from reference state.
    B_theta = { theta : KL(f_theta || f_theta_ref) < epsilon }

    Stdlib implementation: KL computed directly from state vectors
    (no model inference needed - operates on constraint state distributions).

    Repair direction = negative KL gradient (finite difference).

    Falsifiable claim: KL gradient direction moves state toward reference basin
    monotonically for convex loss landscapes.
    Falsification: find non-convex landscape where KL gradient repair oscillates.
    """

    def __init__(self, theta_ref: StateVec, epsilon: float = 0.1,
                 fd_epsilon: float = 1e-4):
        self.theta_ref = theta_ref[:]
        self.epsilon = epsilon
        self.fd_epsilon = fd_epsilon

    def _softmax(self, x: StateVec) -> StateVec:
        m = max(x)
        exp_x = [math.exp(xi - m) for xi in x]
        s = sum(exp_x)
        return [ei / s for ei in exp_x]

    def kl_divergence(self, p: StateVec, q: StateVec) -> float:
        """KL(p || q) = sum p_i * log(p_i / q_i)"""
        kl = 0.0
        for pi, qi in zip(p, q):
            if pi > 1e-12 and qi > 1e-12:
                kl += pi * math.log(pi / qi)
        return max(0.0, kl)

    def kl_from_reference(self, theta: StateVec) -> float:
        """KL between softmax distributions of theta and theta_ref."""
        p = self._softmax(theta)
        q = self._softmax(self.theta_ref)
        return self.kl_divergence(p, q)

    def in_basin(self, theta: StateVec) -> bool:
        return self.kl_from_reference(theta) < self.epsilon

    def repair_direction(self, theta: StateVec) -> StateVec:
        """
        Finite difference negative KL gradient = direction toward reference basin.
        Cost: 2*n function evaluations.
        """
        def kl_fn(x):
            return self.kl_from_reference(x)

        grad = fd_gradient(kl_fn, theta, self.fd_epsilon)
        return [-g for g in grad]  # negative gradient = toward reference

    def to_claim_table(self, kl: float, source_id: str = "unnamed") -> dict:
        # in_basin derivable from kl directly: kl < epsilon (same as in_basin())
        return {
            "source_id": source_id,
            "current_kl": kl,
            "epsilon_threshold": self.epsilon,
            "in_basin": kl < self.epsilon,
            "claims": [
                {
                    "claim_id": f"{source_id}.basin.kl_repair_monotone",
                    "claim": "KL gradient repair direction moves toward reference basin monotonically",
                    "falsification_condition": "Find non-convex landscape where KL gradient repair oscillates",
                    "status": "OPEN",
                },
            ]
        }


# --- kappa_eff: Early Warning Scalar (stdlib) ---

def kappa_eff(loss_fn: LossFn, theta: StateVec, theta_dot: StateVec,
              epsilon: float = 1e-4) -> float:
    """
    Rayleigh quotient of safety Hessian along current flow direction.

    kappa_eff = theta_dot^T H theta_dot / theta_dot^T theta_dot

    Finite difference implementation:
    H * theta_dot ~ (grad(f(x + eps*v)) - grad(f(x - eps*v))) / 2*eps
    where v = theta_dot / ||theta_dot||

    Spike in kappa_eff precedes phase transition (behavioral collapse).

    Falsifiable claim: kappa_eff spike > 2x baseline precedes constraint
    violation within 10 steps for smooth loss functions.
    Falsification: find smooth loss where spike does not precede violation.

    ISS_PROOF_PENDING: True
    """
    dot_norm_sq = vec_dot(theta_dot, theta_dot)
    if dot_norm_sq < 1e-12:
        return 0.0

    hvp = fd_hvp(loss_fn, theta, theta_dot, epsilon)
    numerator = vec_dot(theta_dot, hvp)
    return abs(numerator / dot_norm_sq)


# --- Spectral bound check (stdlib) ---

def power_iteration_lambda_max(loss_fn: LossFn, theta: StateVec,
                                n_iter: int = 8,
                                epsilon: float = 1e-4) -> float:
    """
    Power iteration for lambda_max(Hessian) using FD HVPs.
    Cost: 4*n*n_iter function evaluations.

    Falsifiable claim: converges to true lambda_max within 5% for
    positive semi-definite Hessians after n_iter=8 iterations.
    Falsification: find PSD Hessian where power iteration diverges >5% from true.
    """
    import random
    n = len(theta)
    v = [random.gauss(0, 1) for _ in range(n)]
    v_norm = vec_norm(v)
    v = [vi / v_norm for vi in v]

    eigenvalue = 0.0
    for _ in range(n_iter):
        hvp = fd_hvp(loss_fn, theta, v, epsilon)
        new_eigenvalue = vec_dot(v, hvp)
        hvp_norm = vec_norm(hvp)
        if hvp_norm < 1e-12:
            break
        v = [hi / hvp_norm for hi in hvp]
        eigenvalue = new_eigenvalue

    return abs(eigenvalue)


# --- Integrated controller (stdlib, no torch) ---

@dataclass
class GeometricControllerState:
    step: int
    kl_from_reference: float
    in_basin: bool
    repair_energy_step: float
    cumulative_repair: float
    recent_trend: float
    kappa_eff_value: float
    lambda_max_approx: float
    phase: str                    # stable | threshold | critical
    spectral_bound_ok: bool
    iss_proof_pending: bool = True


class GeometricControllerStdlib:
    """
    Stdlib translation of CoupledDynamicalSystem + ThermodynamicController.

    Operates on plain Python state vectors (list[float]).
    No torch, no autograd. Finite difference throughout.

    Loss function is user-supplied: maps state vector -> scalar loss.
    Repair: Riemannian gradient descent with Fisher metric and trust region.

    Use for:
    - Science transformer constraint satisfaction (Layer 0 -> Layer 1)
    - Constraint drift detection in language codec output (Layer 2)
    - Basin repair for any constraint state in the three-layer stack

    ISS_PROOF_PENDING: True (inherited from source)
    """

    def __init__(self, theta_ref: StateVec, loss_fn: LossFn, config: dict):
        self.theta_ref = theta_ref[:]
        self.loss_fn = loss_fn
        self.lr = config.get("lr", 0.01)
        self.mu = config.get("mu_repair", 0.1)
        self.mu_max = config.get("mu_max", 10.0)
        self.epsilon_basin = config.get("epsilon_basin", 0.1)
        self.repair_budget = config.get("repair_budget", 100.0)
        self.spectral_C_bound = config.get("spectral_C_bound", 20.0)
        self.fd_epsilon = config.get("fd_epsilon", 1e-4)
        self.n_fisher_samples = config.get("n_fisher_samples", 8)

        self.fisher = FisherMetricEstimator(self.n_fisher_samples, self.fd_epsilon)
        self.accumulator = RepairEnergyAccumulator(budget=self.repair_budget)
        self.basin_monitor = BasinDivergenceMonitor(
            theta_ref, self.epsilon_basin, self.fd_epsilon
        )

        self._history: list[GeometricControllerState] = []

    def _phase(self, kappa: float, kl: float, trend: float) -> str:
        if (kappa > self.spectral_C_bound or
                kl > self.epsilon_basin * 2 or
                trend > 3.0):
            return "critical"
        if (kappa > self.spectral_C_bound * 0.5 or
                kl > self.epsilon_basin or
                trend > 1.5):
            return "threshold"
        return "stable"

    def step(self, theta: StateVec) -> tuple[StateVec, GeometricControllerState]:
        """
        Single repair step.
        Returns (new_theta, state).
        """
        n = len(theta)

        # Fisher metric diagonal
        fisher_diag = self.fisher.diagonal(self.loss_fn, theta)
        inv_fisher = [1.0 / (g + 1e-8) for g in fisher_diag]

        # Gradient of loss
        grad = fd_gradient(self.loss_fn, theta, self.fd_epsilon)

        # Riemannian gradient: G^{-1} grad
        riem_grad = [g * inv_f for g, inv_f in zip(grad, inv_fisher)]

        # Fisher regularization term
        fisher_reg_grad = [2.0 * self.mu * t * f
                           for t, f in zip(theta, fisher_diag)]

        # Total update direction
        total_grad = [rg + frg for rg, frg in zip(riem_grad, fisher_reg_grad)]

        # Step
        delta = [-self.lr * tg for tg in total_grad]

        # Trust region projection
        spectral_norm = self.fisher.spectral_norm_approx(fisher_diag)
        trust_r = self.lr / (1.0 + self.mu * spectral_norm)
        delta_norm = vec_norm(delta)
        if delta_norm > trust_r:
            delta = vec_scale(delta, trust_r / delta_norm)

        theta_new = vec_add(theta, delta)

        # Energy accounting
        step_energy = self.accumulator.update(delta, fisher_diag)
        trend = self.accumulator.recent_trend()

        # Basin check
        kl = self.basin_monitor.kl_from_reference(theta_new)
        in_basin = kl < self.epsilon_basin

        # kappa_eff early warning
        kappa = kappa_eff(self.loss_fn, theta_new, delta, self.fd_epsilon)

        # Spectral bound (expensive - skip every other step for performance)
        if len(self._history) % 2 == 0:
            lambda_max = power_iteration_lambda_max(
                self.loss_fn, theta_new, n_iter=4, epsilon=self.fd_epsilon
            )
        else:
            lambda_max = (self._history[-1].lambda_max_approx
                          if self._history else 0.0)

        spectral_ok = lambda_max < self.spectral_C_bound
        phase = self._phase(kappa, kl, trend)

        # Adaptive mu
        if self.accumulator.budget_exceeded() or not in_basin:
            self.mu = min(self.mu * 1.05, self.mu_max)

        state = GeometricControllerState(
            step=len(self._history),
            kl_from_reference=round(kl, 6),
            in_basin=in_basin,
            repair_energy_step=round(step_energy, 6),
            cumulative_repair=round(self.accumulator.cumulative, 6),
            recent_trend=round(trend, 4),
            kappa_eff_value=round(kappa, 6),
            lambda_max_approx=round(lambda_max, 6),
            phase=phase,
            spectral_bound_ok=spectral_ok,
        )
        self._history.append(state)

        if len(self._history) % 5 == 0:
            print(f"  [{state.step:03d}] {phase:9s} | "
                  f"KL={kl:.4f} in_basin={in_basin} | "
                  f"kappa={kappa:.4f} | trend={trend:.2f}x | "
                  f"energy={step_energy:.4f} mu={self.mu:.3f}")

        return theta_new, state

    def summary(self) -> dict:
        if not self._history:
            return {}
        phases = [s.phase for s in self._history]
        return {
            "total_steps": len(self._history),
            "final_phase": self._history[-1].phase,
            "final_kl": self._history[-1].kl_from_reference,
            "in_basin_final": self._history[-1].in_basin,
            "cumulative_repair": self._history[-1].cumulative_repair,
            "peak_kappa_eff": max(s.kappa_eff_value for s in self._history),
            "peak_lambda_max": max(s.lambda_max_approx for s in self._history),
            "spectral_bound_held": all(s.spectral_bound_ok for s in self._history),
            "phase_transition_threshold": next(
                (s.step for s in self._history if s.phase == "threshold"), None),
            "phase_transition_critical": next(
                (s.step for s in self._history if s.phase == "critical"), None),
            "ISS_proof_pending": True,
        }

    def to_claim_table(self, source_id: str = "unnamed",
                       path: str = "CLAIM_TABLE.geometric.json") -> dict:
        fisher_claims = self.fisher.to_claim_table(source_id)
        repair_claims = self.accumulator.to_claim_table(source_id)
        basin_claims = self.basin_monitor.to_claim_table(
            self._history[-1].kl_from_reference
            if self._history else 0.0,
            source_id
        ) if self._history else {}

        all_claims = (
            fisher_claims.get("claims", []) +
            repair_claims.get("claims", []) +
            basin_claims.get("claims", [])
        )
        table = {
            "source_id": source_id,
            "ISS_proof_pending": True,
            "total_claims": len(all_claims),
            "claims": all_claims,
            "summary": self.summary(),
        }
        with open(path, "w") as f:
            json.dump(table, f, indent=2)
        print(f"[geometric_metric] {len(all_claims)} claims written to {path}")
        return table


# --- CLI test ---

if __name__ == "__main__":
    import math

    def quadratic_loss(theta):
        return sum(t**2 for t in theta) / 2.0

    theta_ref = [0.0, 0.0, 0.0, 0.0]
    theta_init = [1.0, -0.5, 0.8, -1.2]

    config = {
        "lr": 0.05,
        "mu_repair": 0.1,
        "mu_max": 5.0,
        "epsilon_basin": 0.2,
        "repair_budget": 50.0,
        "spectral_C_bound": 5.0,
        "fd_epsilon": 1e-4,
        "n_fisher_samples": 4,
    }

    print("[test] quadratic loss dim=4")
    print("[test] theta_init=" + str(theta_init))
    print("[test] running 20 steps")

    controller = GeometricControllerStdlib(theta_ref, quadratic_loss, config)
    theta = theta_init[:]
    for _ in range(20):
        theta, state = controller.step(theta)

    print("[test] final theta=" + str([round(t,4) for t in theta]))
    print("[test] final loss=" + str(round(quadratic_loss(theta),6)))

    summary = controller.summary()
    print("[summary]")
    for k, v in summary.items():
        print("  " + str(k) + ": " + str(v))

    # Fisher validation at non-zero theta
    # For L = sum(x^2)/2, grad_i = x_i, so E[grad_i^2] = x_i^2
    estimator = FisherMetricEstimator(n_samples=32, epsilon=1e-4)
    test_theta = [1.0, -0.5, 0.8, -1.2]
    fisher_diag = estimator.diagonal(quadratic_loss, test_theta)
    true_approx = [t**2 for t in test_theta]
    print("[fisher validation] at theta=" + str(test_theta))
    print("  estimated: " + str([round(f,4) for f in fisher_diag]))
    print("  true E[grad^2]: " + str([round(t,4) for t in true_approx]))
    rel_errors = [abs(f-t)/max(abs(t),1e-8) for f,t in zip(fisher_diag, true_approx)]
    max_err = max(rel_errors)
    print("  max relative error: " + str(round(max_err,4)))
    print("  claim: rel error < 0.05 -> " + ("PASS" if max_err < 0.05 else "FAIL"))
    print("  NOTE: Fisher=0 at gradient minimum (theta_ref) is correct")

    controller.to_claim_table("test_quadratic")

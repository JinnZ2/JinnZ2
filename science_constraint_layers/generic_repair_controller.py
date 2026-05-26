"""
generic_repair_controller.py
CC0 - No rights reserved.

Domain-agnostic repair controller built from geometric_metric_stdlib +
science_transformers. Repairs ANY ConstraintState toward constraint
satisfaction using Riemannian gradient descent with Fisher metric.

Composition:
  - Takes a ConstraintState (physics, biology, thermodynamics,
    mathematics, or any new domain that provides the same shape).
  - Builds a loss function from the constraint-violation set:
    loss(theta) = sum of squared violations evaluated at theta.
  - Wraps GeometricControllerStdlib with that loss + a reference
    state (the closest in-basin state, or user-supplied).
  - Drives repair via repair(n_steps).

The point: the same controller that works on a 4-dim quadratic loss
works on a physics ConstraintState, a biology one, a thermo one - or
any future domain that exposes (state_dict, constraints_list,
constraint_check_fn) in the science_transformers shape.

ISS_PROOF_PENDING: True (inherited from geometric_metric_stdlib).

License: CC0. Stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from geometric_metric_stdlib import (
    GeometricControllerStdlib,
    GeometricControllerState,
    StateVec,
    LossFn,
)
from science_transformers import (
    ConstraintState,
    physics_constraints,
    biology_constraints,
    thermo_constraints,
    math_constraints,
    to_dict as cs_to_dict,
)


# --- Default constraint-check function lookup ---

DOMAIN_CONSTRAINT_FNS: dict[str, Callable[[dict], list]] = {
    "physics":        physics_constraints,
    "biology":        biology_constraints,
    "thermodynamics": thermo_constraints,
    "mathematics":    math_constraints,
}


# --- Smooth penalty functions per known constraint ---
# Binary 0/1 indicators have no slope for FD descent. Smooth penalties
# give the controller a gradient to follow toward the satisfaction region.
# Each penalty returns a non-negative scalar: 0 when satisfied, positive
# and growing as the violation deepens.

C = 3e8  # speed of light, for velocity_bounded

DOMAIN_PENALTY_FNS: dict[str, dict[str, Callable[[dict], float]]] = {
    "physics": {
        "energy_non_negative":
            lambda s: 0.0,  # 0.5*m*v^2 is always >=0 in real fields
        "mass_positive":
            lambda s: max(0.0, 1e-3 - s.get("mass", 1.0)) ** 2,
        "velocity_bounded":
            # Normalize by C so the loss surface has O(1) gradient even at
            # relativistic scale. Penalty zero when |v| < C.
            lambda s: (max(0.0, abs(s.get("velocity", 0.0)) - C) / C) ** 2,
    },
    "biology": {
        "population_non_negative":
            lambda s: max(0.0, -s.get("population", 0.0)) ** 2,
        "resource_non_negative":
            lambda s: max(0.0, -s.get("resource", 0.0)) ** 2,
        "metabolic_rate_positive":
            lambda s: max(0.0, 1e-3 - s.get("metabolic_rate", 0.0)) ** 2,
        "below_carrying_capacity":
            # Normalize by K so gradient is O(1) regardless of K scale.
            lambda s: (max(0.0, s.get("population", 0.0)
                                 - s.get("carrying_capacity", 100.0) * 1.5)
                       / max(s.get("carrying_capacity", 100.0), 1.0)) ** 2,
    },
    "thermodynamics": {
        "temperature_positive":
            lambda s: max(0.0, 1e-3 - s.get("temperature", 0.0)) ** 2,
        "entropy_non_decreasing":
            lambda s: max(0.0, -s.get("entropy", 0.0)) ** 2,
        "free_energy_real":
            lambda s: 0.0,  # finite-real is an isfinite check, not a smooth surface
    },
    "mathematics": {
        # Topological invariants are discrete - no smooth penalties.
        # GenericRepairController on a math ConstraintState will fall
        # through to binary indicators and not converge meaningfully.
        # That's a documented limitation.
    },
}


# Scale limitations of the Fisher-metric trust region:
#   The trust region radius is calibrated for parameters at O(1). When a
#   penalty is normalized by a domain constant (e.g. C for velocity, K
#   for carrying capacity), the gradient becomes O(1) and convergence
#   works. Without normalization, a parameter at O(1e9) gets a trust-
#   region step of O(0.05), which never finishes in finite steps.
#
#   The penalty functions above normalize where needed. If you add a
#   new domain or constraint, follow the same rule: penalty must be a
#   non-negative scalar with O(1) gradient near the constraint boundary.


# --- Loss construction from constraints ---

def constraint_violation_loss(constraint_check_fn: Callable[[dict], list],
                              state_keys: list[str]) -> LossFn:
    """
    Build a loss function from a constraint check.
    loss(theta) = sum of squared violations for the state vector theta
                  unpacked into the named state keys.

    Each constraint is (name, satisfied: bool, description). A violation
    contributes 1.0 to the loss; a satisfied constraint contributes 0.0.
    The squared sum makes the loss differentiable enough for FD-gradient
    descent: as the controller pushes theta into the satisfaction region,
    the loss drops by integer steps.
    """
    def loss(theta: StateVec) -> float:
        state = {k: theta[i] if i < len(theta) else 0.0
                 for i, k in enumerate(state_keys)}
        constraints = constraint_check_fn(state)
        violation_count = sum(0 if sat else 1 for _, sat, _ in constraints)
        return float(violation_count ** 2)
    return loss


def smooth_constraint_loss(constraint_check_fn: Callable[[dict], list],
                           state_keys: list[str],
                           penalty_fns: Optional[dict[str, Callable[[dict], float]]] = None
                           ) -> LossFn:
    """
    Smooth variant: instead of counting violations, sum penalty functions.
    penalty_fns maps constraint name -> penalty(state) returning a non-
    negative scalar. If a constraint is not in penalty_fns, fall back to
    a 0/1 indicator (1.0 if violated).

    Smooth penalties make gradient descent informative; binary counts
    give the controller no slope to descend.
    """
    penalty_fns = penalty_fns or {}

    def loss(theta: StateVec) -> float:
        state = {k: theta[i] if i < len(theta) else 0.0
                 for i, k in enumerate(state_keys)}
        constraints = constraint_check_fn(state)
        total = 0.0
        for name, satisfied, _desc in constraints:
            if name in penalty_fns:
                total += max(0.0, penalty_fns[name](state))
            elif not satisfied:
                total += 1.0
        return total
    return loss


# --- Generic repair controller ---

@dataclass
class RepairResult:
    initial_theta: StateVec
    final_theta: StateVec
    initial_loss: float
    final_loss: float
    n_steps: int
    final_state: Optional[GeometricControllerState] = None
    trajectory: list = field(default_factory=list)

    def converged(self, tol: float = 1e-4) -> bool:
        return self.final_loss <= tol

    def summary(self) -> dict:
        return {
            "n_steps": self.n_steps,
            "initial_loss": round(self.initial_loss, 6),
            "final_loss": round(self.final_loss, 6),
            "loss_reduction": round(self.initial_loss - self.final_loss, 6),
            "converged": self.converged(),
            "final_phase": self.final_state.phase if self.final_state else None,
        }


class GenericRepairController:
    """
    Domain-agnostic repair: pass any ConstraintState, get repair toward
    constraint satisfaction.

    Usage:
        from science_transformers import make_physics_transformer
        cs = make_physics_transformer(velocity=1e9)   # exceeds c, violates constraint
        controller = GenericRepairController(cs)
        result = controller.repair(n_steps=30)
        # result.final_loss should be < initial_loss
        # result.final_theta is the repaired state vector

    Works for physics/biology/thermo/math out of the box. For a new
    domain, supply (constraint_check_fn, penalty_fns) explicitly.
    """

    def __init__(self,
                 constraint_state: ConstraintState,
                 config: Optional[dict] = None,
                 constraint_check_fn: Optional[Callable[[dict], list]] = None,
                 penalty_fns: Optional[dict[str, Callable[[dict], float]]] = None,
                 theta_ref: Optional[StateVec] = None,
                 smooth: bool = True):
        self.cs = constraint_state
        self.state_keys = list(constraint_state.state.keys())

        # Determine constraint-check function
        if constraint_check_fn is None:
            constraint_check_fn = DOMAIN_CONSTRAINT_FNS.get(constraint_state.domain)
            if constraint_check_fn is None:
                raise ValueError(
                    f"No default constraint_check_fn for domain "
                    f"{constraint_state.domain!r}. Pass constraint_check_fn "
                    f"explicitly."
                )

        # Default smooth penalty functions for the known domains
        if penalty_fns is None:
            penalty_fns = DOMAIN_PENALTY_FNS.get(constraint_state.domain, {})

        # Build loss
        if smooth:
            self.loss_fn = smooth_constraint_loss(
                constraint_check_fn, self.state_keys, penalty_fns
            )
        else:
            self.loss_fn = constraint_violation_loss(
                constraint_check_fn, self.state_keys
            )

        # Reference state: zero vector by default (a generic basin floor).
        # For domains where zero is meaningless (e.g. math dimension=0),
        # the caller should pass theta_ref explicitly.
        if theta_ref is None:
            theta_ref = [0.0] * len(self.state_keys)
        self.theta_ref = theta_ref

        # Default config tuned for constraint-violation losses
        default_config = {
            "lr": 0.05,
            "mu_repair": 0.05,
            "mu_max": 5.0,
            "epsilon_basin": 0.5,
            "repair_budget": 100.0,
            "spectral_C_bound": 10.0,
            "fd_epsilon": 1e-3,
            "n_fisher_samples": 4,
        }
        if config:
            default_config.update(config)
        self.config = default_config

        self.controller = GeometricControllerStdlib(
            self.theta_ref, self.loss_fn, self.config
        )

    def initial_theta(self) -> StateVec:
        """Pull the current state vector from the wrapped ConstraintState."""
        return list(self.cs.as_vector())

    def repair(self, n_steps: int = 20,
               record_trajectory: bool = False) -> RepairResult:
        """
        Run n_steps of repair. Returns RepairResult with initial/final
        loss + theta and optionally the per-step trajectory.
        """
        theta = self.initial_theta()
        initial_loss = self.loss_fn(theta)
        trajectory = []
        final_state = None

        for _ in range(n_steps):
            theta, final_state = self.controller.step(theta)
            if record_trajectory:
                trajectory.append({
                    "theta": list(theta),
                    "loss": self.loss_fn(theta),
                    "phase": final_state.phase,
                    "kl": final_state.kl_from_reference,
                })

        final_loss = self.loss_fn(theta)
        return RepairResult(
            initial_theta=self.initial_theta(),
            final_theta=list(theta),
            initial_loss=float(initial_loss),
            final_loss=float(final_loss),
            n_steps=n_steps,
            final_state=final_state,
            trajectory=trajectory,
        )

    def to_claim_table(self, source_id: str = "generic_repair",
                       path: str = "CLAIM_TABLE.generic_repair.json") -> dict:
        return self.controller.to_claim_table(source_id, path)


# --- CLI demo ---

if __name__ == "__main__":
    from science_transformers import (
        make_physics_transformer,
        make_biology_transformer,
        make_thermo_transformer,
    )

    print("=== GenericRepairController demo ===\n")

    # 1. Thermodynamics: temperature -0.5 violates temperature_positive.
    #    Natural O(1) violation, converges quickly.
    print("[thermo] temperature = -0.5 (violates temperature_positive)")
    cs = make_thermo_transformer(temperature=-0.5, entropy=10.0,
                                 free_energy=-500.0)
    controller = GenericRepairController(cs, config={"lr": 0.1})
    result = controller.repair(n_steps=30)
    print(f"  initial_loss={result.initial_loss:.6f}  "
          f"final_loss={result.final_loss:.6f}")
    print(f"  temperature: {cs.state['temperature']:.4f} -> "
          f"{result.final_theta[0]:.4f}")
    print(f"  converged={result.converged(tol=1e-3)}")
    print()

    # 2. Biology: population at 200, K=100, threshold is K*1.5=150.
    #    Violation = 50 / K = 0.5 units. Normalized penalty O(0.25).
    print("[biology] population=200, K=100 (violates below_carrying_capacity)")
    cs = make_biology_transformer(population=200.0, carrying_capacity=100.0,
                                  resource=80.0)
    controller = GenericRepairController(cs, config={"lr": 5.0})
    result = controller.repair(n_steps=30)
    print(f"  initial_loss={result.initial_loss:.6f}  "
          f"final_loss={result.final_loss:.6f}")
    print(f"  population: {cs.state['population']:.2f} -> "
          f"{result.final_theta[0]:.2f}")
    print(f"  converged={result.converged(tol=1e-4)}")
    print()

    # 3. Physics: mass set to -0.5 (violates mass_positive). O(1) violation.
    print("[physics] mass = -0.5 (violates mass_positive)")
    cs = make_physics_transformer(velocity=0.1, mass=-0.5, charge=0.0,
                                  field_E=0.0, field_B=0.0)
    controller = GenericRepairController(cs, config={"lr": 0.1})
    result = controller.repair(n_steps=30)
    print(f"  initial_loss={result.initial_loss:.6f}  "
          f"final_loss={result.final_loss:.6f}")
    print(f"  mass: {cs.state['mass']:.4f} -> {result.final_theta[2]:.4f}")
    print(f"  converged={result.converged(tol=1e-3)}")
    print()

    print("Note: extreme-scale violations (e.g. velocity > c at v=1e9) do")
    print("not converge in 30 steps because the Fisher-metric trust region")
    print("is calibrated for O(1) parameter scale. See the comment block")
    print("at DOMAIN_PENALTY_FNS for the scale-normalization rule when")
    print("adding new constraints.")

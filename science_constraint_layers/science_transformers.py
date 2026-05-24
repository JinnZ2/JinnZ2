"""
science_transformers.py
CC0 - No rights reserved.

Layer 0: Parallel domain-specific constraint state representations.
Each transformer holds constraint geometry for one scientific domain.
No external dependencies - uses Euler integration for ODE approximation.

Domains: physics, biology, thermodynamics, mathematics
Each domain: state dict + update rules (dX/dt functions) + constraint checks

OUTPUT: constraint state vector per domain, ready for Layer 1 integration.

IMPORTANT: These are constraint geometry approximations, not validated
physics simulators. Claims are falsifiable but models are simplified.
Do not use for engineering decisions without validation against domain literature.
"""

import json
import math
import sys
from dataclasses import dataclass, field
from typing import Callable


# --- Base transformer ---

@dataclass
class ConstraintState:
    domain: str
    state: dict          # variable_name -> float
    gradients: dict      # variable_name -> dX/dt at current state
    constraints: list    # list of (name, bool, description)
    t: float = 0.0
    dt: float = 0.01
    claims: list = field(default_factory=list)

    def as_vector(self) -> list[float]:
        """Flat numeric state vector for Layer 1 integration."""
        return list(self.state.values())

    def constraint_mask(self) -> list[int]:
        """Binary mask: 1 if constraint satisfied, 0 if violated."""
        return [1 if sat else 0 for _, sat, _ in self.constraints]

    def violated(self) -> list[str]:
        return [name for name, sat, _ in self.constraints if not sat]


def euler_step(state: dict, gradients: dict, dt: float) -> dict:
    """Single Euler integration step. dX = dX/dt * dt."""
    return {k: state[k] + gradients.get(k, 0.0) * dt for k in state}


# --- Physics transformer ---
# Constraint geometry: electromagnetic + mechanical coupling
# State: position x, velocity v, force F, charge q, field E
# dX/dt: Newton + Lorentz approximation

def physics_gradients(s: dict) -> dict:
    mass = s.get("mass", 1.0)
    charge = s.get("charge", 0.0)
    E = s.get("field_E", 0.0)
    B = s.get("field_B", 0.0)
    damping = s.get("damping", 0.1)

    # F_total = F_applied + F_lorentz - F_damping
    F_lorentz = charge * (E + s.get("velocity", 0.0) * B)
    F_total = s.get("force_applied", 0.0) + F_lorentz - damping * s.get("velocity", 0.0)

    return {
        "position":  s.get("velocity", 0.0),
        "velocity":  F_total / max(mass, 1e-9),
        "force_net": F_total,
        "field_E":   0.0,   # static field assumption
        "field_B":   0.0,
        "charge":    0.0,
        "mass":      0.0,
        "damping":   0.0,
        "force_applied": 0.0,
    }

def physics_constraints(s: dict) -> list:
    return [
        ("energy_non_negative",
         0.5 * s.get("mass", 1.0) * s.get("velocity", 0.0)**2 >= 0,
         "Kinetic energy >= 0"),
        ("mass_positive",
         s.get("mass", 1.0) > 0,
         "Mass must be positive"),
        ("velocity_bounded",
         abs(s.get("velocity", 0.0)) < 3e8,
         "Velocity < c"),
    ]

def make_physics_transformer(
    position: float = 0.0,
    velocity: float = 1.0,
    mass: float = 1.0,
    charge: float = 0.1,
    field_E: float = 0.5,
    field_B: float = 0.2,
    force_applied: float = 0.0,
    damping: float = 0.05,
) -> ConstraintState:
    state = {
        "position": position, "velocity": velocity, "mass": mass,
        "charge": charge, "field_E": field_E, "field_B": field_B,
        "force_net": 0.0, "force_applied": force_applied, "damping": damping,
    }
    grads = physics_gradients(state)
    cs = ConstraintState(
        domain="physics",
        state=state,
        gradients=grads,
        constraints=physics_constraints(state),
    )
    cs.claims.append({
        "claim": "Physics state evolves under Newton+Lorentz approximation",
        "falsification": "Find case where Euler step diverges from analytic solution by >5%",
    })
    return cs


# --- Biology transformer ---
# Constraint geometry: population dynamics + metabolic coupling
# State: population N, resource R, metabolic rate M, entropy S_bio
# dX/dt: Lotka-Volterra inspired + metabolic scaling

def biology_gradients(s: dict) -> dict:
    N = max(s.get("population", 1.0), 0.0)
    R = max(s.get("resource", 1.0), 0.0)
    M = s.get("metabolic_rate", 0.1)
    K = s.get("carrying_capacity", 100.0)
    growth = s.get("growth_rate", 0.1)
    predation = s.get("predation_rate", 0.01)

    dN = growth * N * (1 - N / max(K, 1e-9)) - predation * N * R
    dR = -M * N + s.get("resource_inflow", 1.0)
    dM = 0.01 * (R / max(R + 1, 1e-9) - M)  # metabolic rate tracks resource

    return {
        "population": dN,
        "resource": dR,
        "metabolic_rate": dM,
        "carrying_capacity": 0.0,
        "growth_rate": 0.0,
        "predation_rate": 0.0,
        "resource_inflow": 0.0,
    }

def biology_constraints(s: dict) -> list:
    return [
        ("population_non_negative",
         s.get("population", 0.0) >= 0,
         "Population >= 0"),
        ("resource_non_negative",
         s.get("resource", 0.0) >= 0,
         "Resource >= 0"),
        ("metabolic_rate_positive",
         s.get("metabolic_rate", 0.0) > 0,
         "Metabolic rate > 0 for living system"),
        ("below_carrying_capacity",
         s.get("population", 0.0) <= s.get("carrying_capacity", 100.0) * 1.5,
         "Population within 150% of carrying capacity"),
    ]

def make_biology_transformer(
    population: float = 50.0,
    resource: float = 80.0,
    metabolic_rate: float = 0.1,
    carrying_capacity: float = 100.0,
    growth_rate: float = 0.15,
    predation_rate: float = 0.005,
    resource_inflow: float = 2.0,
) -> ConstraintState:
    state = {
        "population": population, "resource": resource,
        "metabolic_rate": metabolic_rate, "carrying_capacity": carrying_capacity,
        "growth_rate": growth_rate, "predation_rate": predation_rate,
        "resource_inflow": resource_inflow,
    }
    grads = biology_gradients(state)
    cs = ConstraintState(
        domain="biology",
        state=state,
        gradients=grads,
        constraints=biology_constraints(state),
    )
    cs.claims.append({
        "claim": "Biology state follows logistic growth with resource coupling",
        "falsification": "Find population trajectory where resource coupling term has no effect",
    })
    return cs


# --- Thermodynamics transformer ---
# Constraint geometry: entropy production, heat flow, free energy
# State: temperature T, entropy S, free_energy G, heat_flow Q
# dX/dt: Fourier heat + Gibbs free energy relaxation

def thermo_gradients(s: dict) -> dict:
    T = max(s.get("temperature", 300.0), 1e-9)
    T_env = s.get("T_environment", 293.0)
    conductance = s.get("thermal_conductance", 0.1)
    entropy_production_rate = s.get("entropy_production_rate", 0.01)

    dT = conductance * (T_env - T)
    dS = entropy_production_rate + conductance * abs(T_env - T) / T
    dG = -T * dS  # Gibbs: dG = dH - T*dS (simplified: dH~0)
    dQ = conductance * (T_env - T)

    return {
        "temperature": dT,
        "entropy": dS,
        "free_energy": dG,
        "heat_flow": dQ,
        "T_environment": 0.0,
        "thermal_conductance": 0.0,
        "entropy_production_rate": 0.0,
    }

def thermo_constraints(s: dict) -> list:
    return [
        ("temperature_positive",
         s.get("temperature", 0.0) > 0,
         "Temperature > 0 K"),
        ("entropy_non_decreasing",
         s.get("entropy", 0.0) >= 0,
         "Entropy >= 0 (2nd law)"),
        ("free_energy_real",
         math.isfinite(s.get("free_energy", 0.0)),
         "Free energy is finite real number"),
    ]

def make_thermo_transformer(
    temperature: float = 300.0,
    entropy: float = 10.0,
    free_energy: float = -500.0,
    heat_flow: float = 0.0,
    T_environment: float = 293.0,
    thermal_conductance: float = 0.05,
    entropy_production_rate: float = 0.02,
) -> ConstraintState:
    state = {
        "temperature": temperature, "entropy": entropy,
        "free_energy": free_energy, "heat_flow": heat_flow,
        "T_environment": T_environment,
        "thermal_conductance": thermal_conductance,
        "entropy_production_rate": entropy_production_rate,
    }
    grads = thermo_gradients(state)
    cs = ConstraintState(
        domain="thermodynamics",
        state=state,
        gradients=grads,
        constraints=thermo_constraints(state),
    )
    cs.claims.append({
        "claim": "Entropy production rate > 0 for irreversible system",
        "falsification": "Find system state where entropy decreases without external work input",
    })
    return cs


# --- Mathematics transformer ---
# Constraint geometry: topological invariants, algebraic relationships
# State: curvature K, euler_characteristic X, dimension D, symmetry_order G
# No ODE - algebraic constraints only (topology is discrete, not continuous)

def math_constraints(s: dict) -> list:
    K = s.get("curvature", 0.0)
    X = s.get("euler_characteristic", 2)
    D = s.get("dimension", 3)
    G = s.get("symmetry_order", 1)

    # Gauss-Bonnet: integral of K relates to Euler characteristic (sphere: X=2)
    # Simplified check: K and X must have consistent sign for closed surface
    gb_consistent = (K >= 0 and X > 0) or (K <= 0 and X <= 0) or K == 0

    return [
        ("dimension_positive_integer",
         isinstance(D, int) and D > 0,
         "Dimension must be positive integer"),
        ("symmetry_order_positive",
         G >= 1,
         "Symmetry group order >= 1 (trivial group)"),
        ("gauss_bonnet_consistent",
         gb_consistent,
         "Curvature sign consistent with Euler characteristic"),
        ("euler_characteristic_integer",
         isinstance(X, int),
         "Euler characteristic is integer"),
    ]

def make_math_transformer(
    curvature: float = 0.0,
    euler_characteristic: int = 2,
    dimension: int = 3,
    symmetry_order: int = 1,
    metric_signature: str = "+++",
) -> ConstraintState:
    state = {
        "curvature": curvature,
        "euler_characteristic": euler_characteristic,
        "dimension": dimension,
        "symmetry_order": symmetry_order,
        "metric_signature": metric_signature,
    }
    cs = ConstraintState(
        domain="mathematics",
        state=state,
        gradients={},  # algebraic, no time evolution
        constraints=math_constraints(state),
    )
    cs.claims.append({
        "claim": "Topological invariants constrain physically realizable geometries",
        "falsification": "Find physical system violating Gauss-Bonnet for closed surface",
    })
    return cs


# --- Step all transformers ---

def step(cs: ConstraintState, steps: int = 1) -> ConstraintState:
    """Advance constraint state by n Euler steps."""
    if cs.domain == "mathematics":
        return cs  # algebraic - no time evolution
    update_fns = {
        "physics": physics_gradients,
        "biology": biology_gradients,
        "thermodynamics": thermo_gradients,
    }
    fn = update_fns.get(cs.domain)
    if not fn:
        return cs
    s = cs.state.copy()
    for _ in range(steps):
        grads = fn(s)
        s = euler_step(s, grads, cs.dt)
    constraint_fns = {
        "physics": physics_constraints,
        "biology": biology_constraints,
        "thermodynamics": thermo_constraints,
    }
    cfn = constraint_fns.get(cs.domain, lambda _: [])
    cs.state = s
    cs.gradients = fn(s)
    cs.constraints = cfn(s)
    cs.t += cs.dt * steps
    return cs


def to_dict(cs: ConstraintState) -> dict:
    return {
        "domain": cs.domain,
        "t": cs.t,
        "state": {k: v for k, v in cs.state.items() if isinstance(v, (int, float))},
        "state_vector": cs.as_vector(),
        "constraint_mask": cs.constraint_mask(),
        "violated": cs.violated(),
        "claims": cs.claims,
    }


if __name__ == "__main__":
    transformers = [
        make_physics_transformer(),
        make_biology_transformer(),
        make_thermo_transformer(),
        make_math_transformer(),
    ]

    print("--- INITIAL CONSTRAINT STATES ---\n")
    for cs in transformers:
        d = to_dict(cs)
        violated = d["violated"] or ["none"]
        print(f"[{cs.domain:<16}] vector={[round(x,3) for x in d['state_vector'][:4]]}"
              f"  mask={d['constraint_mask']}  violated={violated}")

    print("\n--- AFTER 100 STEPS ---\n")
    for cs in transformers:
        step(cs, steps=100)
        d = to_dict(cs)
        violated = d["violated"] or ["none"]
        print(f"[{cs.domain:<16}] t={d['t']:.2f}  vector={[round(x,3) for x in d['state_vector'][:4]]}"
              f"  violated={violated}")

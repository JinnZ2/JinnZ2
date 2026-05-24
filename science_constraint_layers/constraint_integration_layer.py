"""
constraint_integration_layer.py
CC0 - No rights reserved.

Layer 1: Cross-domain constraint binding.
Takes parallel constraint state vectors from science_transformers.py
and finds coupling relationships between domains.

Coupling types:
- THERMODYNAMIC_BIOLOGICAL: entropy production <-> metabolic rate
- ELECTROMAGNETIC_MECHANICAL: field <-> force/velocity
- MATHEMATICAL_PHYSICAL: topology <-> physical geometry
- BIOLOGICAL_PHYSICAL: population dynamics <-> energy constraints

Output: IntegratedConstraintState - binding table, coupling strengths,
violated cross-domain constraints, and numeric integration vector.

IMPORTANT: Coupling coefficients are approximations.
Falsifiable claims written to CLAIM_TABLE.integration.json.
"""

import json
import math
import sys
from dataclasses import dataclass, field
from enum import Enum


class CouplingType(str, Enum):
    THERMO_BIO      = "thermodynamic_biological"
    EM_MECHANICAL   = "electromagnetic_mechanical"
    MATH_PHYSICAL   = "mathematical_physical"
    BIO_PHYSICAL    = "biological_physical"
    THERMO_PHYSICAL = "thermodynamic_physical"
    UNCOUPLED       = "uncoupled"


@dataclass
class Coupling:
    coupling_type: CouplingType
    domain_a: str
    domain_b: str
    variable_a: str
    variable_b: str
    strength: float          # 0.0 weak - 1.0 strong
    direction: str           # "a->b", "b->a", "bidirectional"
    satisfied: bool
    claim: str
    falsification: str


@dataclass
class IntegratedConstraintState:
    domains: dict                    # domain_name -> ConstraintState dict
    couplings: list                  # list of Coupling
    integration_vector: list[float]  # flat numeric vector across all domains
    constraint_mask: list[int]       # 1=satisfied, 0=violated per coupling
    signal_density: float            # couplings per domain
    claims: list = field(default_factory=list)

    def violated_couplings(self) -> list[str]:
        return [
            f"{c.domain_a}<->{c.domain_b}:{c.coupling_type.value}"
            for c in self.couplings if not c.satisfied
        ]

    def coupling_summary(self) -> dict:
        by_type = {}
        for c in self.couplings:
            t = c.coupling_type.value
            by_type.setdefault(t, []).append({
                "pair": f"{c.domain_a}<->{c.domain_b}",
                "strength": c.strength,
                "direction": c.direction,
                "satisfied": c.satisfied,
            })
        return by_type


# --- Coupling detectors ---

def detect_thermo_bio(domains: dict) -> list[Coupling]:
    """
    Thermodynamic-biological coupling:
    entropy production rate <-> metabolic rate
    Higher entropy production -> higher metabolic constraint
    """
    couplings = []
    if "thermodynamics" not in domains or "biology" not in domains:
        return couplings

    t = domains["thermodynamics"]["state"]
    b = domains["biology"]["state"]

    entropy_prod = t.get("entropy_production_rate", 0.0)
    metabolic = b.get("metabolic_rate", 0.0)

    # Coupling strength: how tightly metabolic rate tracks entropy production
    if entropy_prod > 0 and metabolic > 0:
        ratio = min(metabolic / max(entropy_prod, 1e-9), 10.0)
        strength = 1.0 - abs(1.0 - ratio) / max(ratio, 1.0)
    else:
        strength = 0.0

    satisfied = strength > 0.1  # weak coupling threshold

    couplings.append(Coupling(
        coupling_type=CouplingType.THERMO_BIO,
        domain_a="thermodynamics",
        domain_b="biology",
        variable_a="entropy_production_rate",
        variable_b="metabolic_rate",
        strength=round(strength, 4),
        direction="bidirectional",
        satisfied=satisfied,
        claim="Entropy production rate and metabolic rate are coupled in living systems",
        falsification="Find living system where entropy production and metabolic rate are fully independent",
    ))
    return couplings


def detect_em_mechanical(domains: dict) -> list[Coupling]:
    """
    Electromagnetic-mechanical coupling:
    field_E, field_B <-> force_net, velocity
    """
    couplings = []
    if "physics" not in domains:
        return couplings

    p = domains["physics"]["state"]
    E = p.get("field_E", 0.0)
    B = p.get("field_B", 0.0)
    v = p.get("velocity", 0.0)
    F = p.get("force_net", 0.0)
    charge = p.get("charge", 0.0)

    lorentz = charge * (E + v * B)
    strength = min(abs(lorentz) / max(abs(F) + 1e-9, 1e-9), 1.0)

    couplings.append(Coupling(
        coupling_type=CouplingType.EM_MECHANICAL,
        domain_a="physics",
        domain_b="physics",
        variable_a="field_E+field_B",
        variable_b="force_net",
        strength=round(strength, 4),
        direction="a->b",
        satisfied=math.isfinite(lorentz),
        claim="Lorentz force couples EM fields to mechanical motion",
        falsification="Find charged particle in EM field where Lorentz force has no mechanical effect",
    ))
    return couplings


def detect_math_physical(domains: dict) -> list[Coupling]:
    """
    Mathematical-physical coupling:
    topological constraints <-> physical state feasibility
    """
    couplings = []
    if "mathematics" not in domains or "physics" not in domains:
        return couplings

    m = domains["mathematics"]["state"]
    p = domains["physics"]["state"]

    D = m.get("dimension", 3)
    K = m.get("curvature", 0.0)
    v = p.get("velocity", 0.0)

    # In D=3 flat space (K=0), velocity is unconstrained below c
    # In curved space (K!=0), geodesic constraints apply
    curvature_effect = abs(K) * abs(v)
    strength = min(curvature_effect, 1.0)
    satisfied = D >= 1 and math.isfinite(K)

    couplings.append(Coupling(
        coupling_type=CouplingType.MATH_PHYSICAL,
        domain_a="mathematics",
        domain_b="physics",
        variable_a="curvature",
        variable_b="velocity",
        strength=round(strength, 4),
        direction="a->b",
        satisfied=satisfied,
        claim="Spacetime curvature constrains physical trajectory geometry",
        falsification="Find physical trajectory unaffected by spacetime curvature",
    ))
    return couplings


def detect_bio_physical(domains: dict) -> list[Coupling]:
    """
    Biological-physical coupling:
    metabolic energy <-> thermodynamic free energy
    """
    couplings = []
    if "biology" not in domains or "thermodynamics" not in domains:
        return couplings

    b = domains["biology"]["state"]
    t = domains["thermodynamics"]["state"]

    metabolic = b.get("metabolic_rate", 0.0)
    free_energy = t.get("free_energy", 0.0)
    T = t.get("temperature", 300.0)

    # Life requires negative free energy (spontaneous processes)
    bio_feasible = free_energy < 0 and metabolic > 0
    strength = min(metabolic * abs(free_energy) / max(T, 1.0) / 100.0, 1.0)

    couplings.append(Coupling(
        coupling_type=CouplingType.BIO_PHYSICAL,
        domain_a="biology",
        domain_b="thermodynamics",
        variable_a="metabolic_rate",
        variable_b="free_energy",
        strength=round(strength, 4),
        direction="bidirectional",
        satisfied=bio_feasible,
        claim="Metabolic processes require negative free energy (thermodynamic spontaneity)",
        falsification="Find sustained metabolic process in system with positive free energy",
    ))
    return couplings


def detect_thermo_physical(domains: dict) -> list[Coupling]:
    """
    Thermodynamic-physical coupling:
    temperature gradient <-> force/pressure
    """
    couplings = []
    if "thermodynamics" not in domains or "physics" not in domains:
        return couplings

    t = domains["thermodynamics"]["state"]
    p = domains["physics"]["state"]

    T = t.get("temperature", 300.0)
    T_env = t.get("T_environment", 293.0)
    F = p.get("force_net", 0.0)

    dT = T - T_env
    # Thermal expansion / pressure coupling approximation
    coupling_force = abs(dT) * 0.01  # simplified
    strength = min(coupling_force / max(abs(F) + 1e-9, 1e-9), 1.0)

    couplings.append(Coupling(
        coupling_type=CouplingType.THERMO_PHYSICAL,
        domain_a="thermodynamics",
        domain_b="physics",
        variable_a="temperature",
        variable_b="force_net",
        strength=round(strength, 4),
        direction="a->b",
        satisfied=math.isfinite(dT),
        claim="Temperature gradient induces mechanical force (thermal expansion/pressure)",
        falsification="Find temperature gradient with zero mechanical coupling in real material",
    ))
    return couplings


# --- Integration ---

def integrate(domain_states: list) -> IntegratedConstraintState:
    """
    Take list of ConstraintState dicts (from science_transformers.to_dict())
    and build IntegratedConstraintState.
    """
    domains = {d["domain"]: d for d in domain_states}

    # Run all coupling detectors
    couplings = []
    couplings.extend(detect_thermo_bio(domains))
    couplings.extend(detect_em_mechanical(domains))
    couplings.extend(detect_math_physical(domains))
    couplings.extend(detect_bio_physical(domains))
    couplings.extend(detect_thermo_physical(domains))

    # Build flat integration vector: all state vectors concatenated
    integration_vector = []
    for d in domain_states:
        integration_vector.extend(d.get("state_vector", []))

    # Add coupling strengths to vector
    integration_vector.extend([c.strength for c in couplings])

    constraint_mask = [1 if c.satisfied else 0 for c in couplings]
    signal_density = len(couplings) / max(len(domains), 1)

    ics = IntegratedConstraintState(
        domains=domains,
        couplings=couplings,
        integration_vector=[round(x, 6) if isinstance(x, float) else x
                            for x in integration_vector],
        constraint_mask=constraint_mask,
        signal_density=round(signal_density, 3),
    )

    ics.claims.append({
        "claim": f"{len(couplings)} cross-domain couplings detected",
        "falsification": "Find domain pair with zero coupling in real physical-biological system",
    })

    return ics


def to_claim_table(ics: IntegratedConstraintState,
                   source_id: str = "unnamed") -> dict:
    claims = []
    for i, c in enumerate(ics.couplings):
        claims.append({
            "claim_id": f"{source_id}.integration.{i:04d}",
            "coupling_type": c.coupling_type.value,
            "domain_a": c.domain_a,
            "domain_b": c.domain_b,
            "variable_a": c.variable_a,
            "variable_b": c.variable_b,
            "strength": c.strength,
            "direction": c.direction,
            "satisfied": c.satisfied,
            "claim": c.claim,
            "falsification_condition": c.falsification,
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "coupling_count": len(ics.couplings),
        "violated_count": len(ics.violated_couplings()),
        "signal_density": ics.signal_density,
        "claims": claims,
    }


def write_claim_table(ics: IntegratedConstraintState,
                      source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.integration.json") -> None:
    table = to_claim_table(ics, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[integration] {len(ics.couplings)} couplings written to {path}")


if __name__ == "__main__":
    from science_transformers import (
        make_physics_transformer, make_biology_transformer,
        make_thermo_transformer, make_math_transformer,
        step, to_dict,
    )

    transformers = [
        make_physics_transformer(),
        make_biology_transformer(),
        make_thermo_transformer(),
        make_math_transformer(),
    ]

    # Step all forward
    for cs in transformers:
        step(cs, steps=50)

    domain_states = [to_dict(cs) for cs in transformers]
    ics = integrate(domain_states)

    print(f"integration vector length: {len(ics.integration_vector)}")
    print(f"signal density: {ics.signal_density} couplings/domain")
    print(f"constraint mask: {ics.constraint_mask}")
    print(f"violated: {ics.violated_couplings() or ['none']}\n")

    print("coupling summary:")
    for ctype, entries in ics.coupling_summary().items():
        for e in entries:
            print(f"  [{ctype}] {e['pair']} strength={e['strength']} "
                  f"dir={e['direction']} sat={e['satisfied']}")

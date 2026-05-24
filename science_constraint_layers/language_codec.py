"""
language_codec.py
CC0 - No rights reserved.

Layer 2: Constraint geometry -> English output codec.
Takes IntegratedConstraintState from constraint_integration_layer.py
and generates English that preserves constraint skeleton.

NOT a neural language model. Uses template selection driven by:
- coupling types present
- constraint satisfaction state
- signal density
- domain state magnitudes

Output: English strings with constraint markers embedded.
Multiple valid outputs possible from same constraint state.

Falsifiable claim: generated English encodes the coupling structure
of the input IntegratedConstraintState without collapsing it to narrative.
Falsification: find output where coupling information is unrecoverable
from the generated text.
"""

import json
import math
import sys
from dataclasses import dataclass
from enum import Enum


class OutputMode(str, Enum):
    CONSTRAINT_PRIMARY = "constraint_primary"   # R-codes + relation types + values
    HYBRID             = "hybrid"               # R-codes embedded in English
    ENGLISH_MARKED     = "english_marked"       # English with constraint markers
    ENGLISH_PLAIN      = "english_plain"        # English only - maximum information loss


# --- Constraint-to-language mapping ---
# Maps coupling types and domain states to verb-first English fragments.
# Verb-first = constraint-primary. Noun-first = narrative collapse.

COUPLING_PHRASES = {
    "thermodynamic_biological": {
        "strong":   "entropy production drives metabolic constraint - rate={a:.3f} coupling={b:.3f}",
        "moderate": "entropy and metabolic rate are coupling - production={a:.3f} metabolic={b:.3f}",
        "weak":     "thermal-biological coupling is weak - production={a:.3f}",
        "violated": "VIOLATION: metabolic rate decoupled from entropy production",
    },
    "electromagnetic_mechanical": {
        "strong":   "Lorentz force is dominating mechanical trajectory - strength={s:.3f}",
        "moderate": "EM field is coupling to mechanical motion - strength={s:.3f}",
        "weak":     "EM-mechanical coupling is present - strength={s:.3f}",
        "violated": "VIOLATION: EM field not coupling to mechanical state",
    },
    "mathematical_physical": {
        "strong":   "spacetime curvature is constraining trajectory - K={a:.3f}",
        "moderate": "topological constraints are bounding physical state - curvature={a:.3f}",
        "weak":     "flat geometry - topological constraint is minimal",
        "violated": "VIOLATION: topological constraint is inconsistent with physical state",
    },
    "biological_physical": {
        "strong":   "metabolic process is thermodynamically feasible - G={b:.1f} rate={a:.3f}",
        "moderate": "free energy is supporting metabolic activity - G={b:.1f}",
        "weak":     "bio-thermodynamic coupling is weak - G={b:.1f}",
        "violated": "VIOLATION: metabolic process is thermodynamically infeasible - positive free energy",
    },
    "thermodynamic_physical": {
        "strong":   "temperature gradient is inducing mechanical force - dT={a:.2f}",
        "moderate": "thermal-mechanical coupling is active - dT={a:.2f}",
        "weak":     "thermal-mechanical coupling is negligible",
        "violated": "VIOLATION: thermal state is non-physical",
    },
}

DOMAIN_STATE_PHRASES = {
    "physics": {
        "normal":  "physical state: position={position:.3f} velocity={velocity:.3f} force={force_net:.3f}",
        "extreme": "PHYSICAL BOUNDARY: velocity approaching limit - v={velocity:.3f}",
    },
    "biology": {
        "normal":  "biological state: population={population:.1f} resource={resource:.1f} metabolic={metabolic_rate:.3f}",
        "collapse": "BIOLOGICAL CONSTRAINT: population collapse imminent - N={population:.1f}",
        "overshoot": "BIOLOGICAL CONSTRAINT: population overshoot - N={population:.1f} K={carrying_capacity:.1f}",
    },
    "thermodynamics": {
        "normal":  "thermodynamic state: T={temperature:.1f}K entropy={entropy:.3f} G={free_energy:.1f}",
        "hot":     "THERMAL BOUNDARY: high temperature - T={temperature:.1f}K",
        "cold":    "THERMAL BOUNDARY: approaching absolute zero - T={temperature:.1f}K",
    },
    "mathematics": {
        "flat":    "geometry: flat D={dimension} K={curvature:.3f} symmetry_order={symmetry_order}",
        "curved":  "geometry: curved D={dimension} K={curvature:.3f} euler_characteristic={euler_characteristic}",
    },
}


def _coupling_phrase(c, domains: dict) -> str:
    template_set = COUPLING_PHRASES.get(c["coupling_type"], {})
    if not c["satisfied"]:
        return template_set.get("violated", f"VIOLATION: {c['coupling_type']}")

    s = c["strength"]
    if s >= 0.7:
        key = "strong"
    elif s >= 0.3:
        key = "moderate"
    else:
        key = "weak"

    template = template_set.get(key, f"{c['coupling_type']} strength={s:.3f}")

    # Fill template variables from domain states
    da = domains.get(c["domain_a"], {}).get("state", {})
    db = domains.get(c["domain_b"], {}).get("state", {})
    a_val = da.get(c["variable_a"].split("+")[0], s)
    b_val = db.get(c["variable_b"], s)

    try:
        return template.format(a=a_val, b=b_val, s=s)
    except (KeyError, ValueError):
        return f"{c['coupling_type']} strength={s:.3f}"


def _domain_phrase(domain: str, state: dict) -> str:
    templates = DOMAIN_STATE_PHRASES.get(domain, {})

    if domain == "physics":
        v = state.get("velocity", 0.0)
        if abs(v) > 1e7:
            return templates["extreme"].format(**state)
        return templates["normal"].format(**state)

    elif domain == "biology":
        N = state.get("population", 0.0)
        K = state.get("carrying_capacity", 100.0)
        if N <= 0:
            return templates["collapse"].format(**state)
        if N > K * 1.2:
            return templates["overshoot"].format(**state)
        return templates["normal"].format(**state)

    elif domain == "thermodynamics":
        T = state.get("temperature", 300.0)
        if T > 1000:
            return templates["hot"].format(**state)
        if T < 10:
            return templates["cold"].format(**state)
        return templates["normal"].format(**state)

    elif domain == "mathematics":
        K = state.get("curvature", 0.0)
        if abs(K) > 0.01:
            return templates["curved"].format(**state)
        return templates["flat"].format(**state)

    return f"{domain}: {state}"


# --- R-code encoder ---
# Maps coupling index to R-code for constraint_primary mode

def _to_r_codes(couplings: list, integration_vector: list) -> list[str]:
    lines = []
    for i, c in enumerate(couplings):
        status = "SAT" if c["satisfied"] else "VIOL"
        lines.append(
            f"R{i:02d} {c['coupling_type']:<30} "
            f"str={c['strength']:.4f} {status} {c['direction']}"
        )
    return lines


# --- Main codec ---

@dataclass
class CodecOutput:
    mode: OutputMode
    lines: list[str]
    r_codes: list[str]
    constraint_mask: list[int]
    violation_count: int
    signal_density: float

    def to_text(self) -> str:
        return "\n".join(self.lines)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "output": self.lines,
            "r_codes": self.r_codes,
            "constraint_mask": self.constraint_mask,
            "violation_count": self.violation_count,
            "signal_density": self.signal_density,
        }


def generate(ics_dict: dict, mode: OutputMode = OutputMode.HYBRID) -> CodecOutput:
    """
    Generate English from integrated constraint state dict.
    ics_dict: output of IntegratedConstraintState serialized to dict.
    """
    domains = ics_dict.get("domains", {})
    couplings = ics_dict.get("couplings", [])
    integration_vector = ics_dict.get("integration_vector", [])
    constraint_mask = ics_dict.get("constraint_mask", [])
    signal_density = ics_dict.get("signal_density", 0.0)
    violation_count = sum(1 for x in constraint_mask if x == 0)

    r_codes = _to_r_codes(couplings, integration_vector)

    if mode == OutputMode.CONSTRAINT_PRIMARY:
        lines = ["[CONSTRAINT_PRIMARY]"] + r_codes
        for domain, d in domains.items():
            state = d.get("state", {})
            vec = d.get("state_vector", [])
            mask = d.get("constraint_mask", [])
            lines.append(
                f"D:{domain} vec={[round(x,3) for x in vec[:4]]} mask={mask}"
            )

    elif mode == OutputMode.HYBRID:
        lines = ["[HYBRID]"]
        for rc in r_codes:
            lines.append(f"  {rc}")
        lines.append("")
        for domain, d in domains.items():
            state = {k: v for k, v in d.get("state", {}).items()
                     if isinstance(v, (int, float))}
            lines.append("  " + _domain_phrase(domain, state))
        lines.append("")
        for c in couplings:
            phrase = _coupling_phrase(c, domains)
            lines.append(f"  -> {phrase}")

    elif mode == OutputMode.ENGLISH_MARKED:
        lines = []
        for domain, d in domains.items():
            state = {k: v for k, v in d.get("state", {}).items()
                     if isinstance(v, (int, float))}
            lines.append(_domain_phrase(domain, state))
        lines.append("")
        for i, c in enumerate(couplings):
            phrase = _coupling_phrase(c, domains)
            lines.append(f"[R{i:02d}] {phrase}")
        if violation_count > 0:
            lines.append(f"\nWARNING: {violation_count} constraint violation(s)")

    elif mode == OutputMode.ENGLISH_PLAIN:
        lines = []
        for domain, d in domains.items():
            state = {k: v for k, v in d.get("state", {}).items()
                     if isinstance(v, (int, float))}
            lines.append(_domain_phrase(domain, state))
        lines.append("")
        for c in couplings:
            lines.append(_coupling_phrase(c, domains))

    else:
        lines = [f"[unknown mode: {mode}]"]

    return CodecOutput(
        mode=mode,
        lines=lines,
        r_codes=r_codes,
        constraint_mask=constraint_mask,
        violation_count=violation_count,
        signal_density=signal_density,
    )


def generate_all_modes(ics_dict: dict) -> dict[str, CodecOutput]:
    return {mode.value: generate(ics_dict, mode) for mode in OutputMode}


def ics_to_dict(ics) -> dict:
    """Serialize IntegratedConstraintState to plain dict for codec input."""
    return {
        "domains": ics.domains,
        "couplings": [
            {
                "coupling_type": c.coupling_type.value,
                "domain_a": c.domain_a,
                "domain_b": c.domain_b,
                "variable_a": c.variable_a,
                "variable_b": c.variable_b,
                "strength": c.strength,
                "direction": c.direction,
                "satisfied": c.satisfied,
            }
            for c in ics.couplings
        ],
        "integration_vector": ics.integration_vector,
        "constraint_mask": ics.constraint_mask,
        "signal_density": ics.signal_density,
    }


if __name__ == "__main__":
    from science_transformers import (
        make_physics_transformer, make_biology_transformer,
        make_thermo_transformer, make_math_transformer,
        step, to_dict as st_to_dict,
    )
    from constraint_integration_layer import integrate

    transformers = [
        make_physics_transformer(),
        make_biology_transformer(),
        make_thermo_transformer(),
        make_math_transformer(),
    ]
    for cs in transformers:
        step(cs, steps=100)

    domain_states = [st_to_dict(cs) for cs in transformers]
    ics = integrate(domain_states)
    ics_dict = ics_to_dict(ics)

    for mode in OutputMode:
        out = generate(ics_dict, mode)
        print(f"\n{'='*60}")
        print(f"MODE: {mode.value}")
        print('='*60)
        print(out.to_text())

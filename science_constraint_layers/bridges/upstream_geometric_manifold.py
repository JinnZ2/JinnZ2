"""
upstream_geometric_manifold.py
CC0 - No rights reserved.

Bridge between this repo (science_constraint_layers/) and the upstream
JinnZ2/Geometric-manifold- repo's repair pipeline.

Pulled from:
  https://github.com/JinnZ2/Geometric-manifold-/blob/main/repair/science_constraint_bridge.py
  (commit at fetch time; re-pull and diff to update.)

Upstream is stdlib-only at this file (math + typing). No torch
dependency inherited. Verbatim placement except: added local-
compatibility helpers (to_local_constraint_state, validate_roundtrip)
at the bottom so the bridge output can feed
constraint_integration_layer.integrate() and language_codec.generate().

The bridge maps per-step repair metrics from the upstream geometric
manifold framework (task_loss, safety_loss, curvature, confidence,
dist_to_ref) into a dict that imitates a multi-domain
IntegratedConstraintState. It does NOT instantiate the upstream
torch-based monitors. It accepts their numeric outputs.

Falsifiable structural claim:
  For any monitor_history record produced by the upstream framework,
  export_trajectory(records) returns a list of dicts each carrying the
  same 14-element state_vector layout, the same 5 constraints, and
  the same 5 coupling types - regardless of upstream torch/numpy
  details. Falsification: find a monitor record whose round-trip
  through this bridge loses information that the upstream framework
  considered structural.

License: CC0. Stdlib only.
"""
from __future__ import annotations

import math
from typing import Optional


def to_constraint_state(
    param_metrics: dict,
    policy_conf: float,
    data_conf: float,
    step: int = 0,
    kappa_eff: Optional[float] = None,
    basin_kl: Optional[float] = None,
) -> dict:
    """
    Convert per-step repair metrics into a ConstraintState-compatible dict.
    Maps each manifold layer to the closest domain in science_constraint_layers.
    """
    curvature = param_metrics.get("curvature", 0.0)
    task_loss = param_metrics.get("task_loss", 0.0)
    safety_loss = param_metrics.get("safety_loss", 0.0)
    dist_to_ref = param_metrics.get("dist_to_ref", 0.0)
    param_conf = param_metrics.get("confidence", 1.0)

    math_state = {
        "curvature": curvature,
        "euler_char_proxy": 2.0 - 2.0 * min(curvature, 1.0),
        "metric_signature": 1.0 if curvature < 10.0 else -1.0,
        "dist_to_basin_floor": dist_to_ref,
    }

    js_proxy = 1.0 - policy_conf
    entropy_proxy = -policy_conf * math.log(policy_conf + 1e-8)
    thermo_state = {
        "temperature": safety_loss,
        "entropy": entropy_proxy,
        "free_energy": task_loss + safety_loss,
        "dS_dt": js_proxy,
    }

    bio_state = {
        "minority_fraction": data_conf,
        "population_balance": 2.0 * data_conf - 1.0,
        "metabolic_rate": 1.0 - data_conf,
    }

    constraints = {
        "curvature_bounded": curvature < 20.0,
        "in_basin": (basin_kl or safety_loss) < 0.1,
        "confidence_above_threshold": param_conf > 0.4,
        "entropy_nondecreasing": js_proxy >= 0.0,
        "minority_preserved": data_conf > 0.0,
    }
    mask = list(constraints.values())
    violated = [name for name, ok in constraints.items() if not ok]

    state_vector = [
        math_state["curvature"],
        math_state["euler_char_proxy"],
        math_state["metric_signature"],
        math_state["dist_to_basin_floor"],
        thermo_state["temperature"],
        thermo_state["entropy"],
        thermo_state["free_energy"],
        thermo_state["dS_dt"],
        bio_state["minority_fraction"],
        bio_state["population_balance"],
        bio_state["metabolic_rate"],
        param_conf,
        policy_conf,
        data_conf,
    ]

    return {
        "time": step,
        "domain": "basin_repair",
        "state_vector": state_vector,
        "constraint_mask": mask,
        "violated": violated,
        "mathematics": math_state,
        "thermodynamics": thermo_state,
        "biology": bio_state,
        "kappa_eff": kappa_eff,
    }


def to_coupling_vector(state: dict) -> list[dict]:
    """
    Compute inter-domain coupling strengths from a constraint state dict.
    """
    thermo = state.get("thermodynamics", {})
    bio = state.get("biology", {})
    math_st = state.get("mathematics", {})

    param_conf = state["state_vector"][11]
    policy_conf = state["state_vector"][12]
    data_conf = state["state_vector"][13]

    thermo_bio_strength = min(1.0, thermo.get("dS_dt", 0.0) * bio.get("metabolic_rate", 0.0) * 4.0)
    curvature = math_st.get("curvature", 0.0)
    math_phys_strength = min(1.0, curvature / 20.0)
    balance = bio.get("population_balance", 0.0)
    bio_phys_strength = min(1.0, abs(balance) * (1.0 - param_conf))
    free_energy = thermo.get("free_energy", 0.0)
    thermo_phys_strength = min(1.0, free_energy / (free_energy + 1.0))

    couplings = [
        {
            "type": "thermodynamic_biological",
            "strength": thermo_bio_strength,
            "direction": "thermo->bio",
            "satisfied": thermo_bio_strength < 0.7,
            "claim": "policy drift and data imbalance co-vary under adversarial drift",
        },
        {
            "type": "electromagnetic_mechanical",
            "strength": 0.0,
            "direction": "none",
            "satisfied": True,
            "claim": "not applicable to parameter-space framework",
        },
        {
            "type": "mathematical_physical",
            "strength": math_phys_strength,
            "direction": "math->physical",
            "satisfied": math_phys_strength < 1.0,
            "claim": "high safety-Hessian curvature predicts expensive repair steps",
        },
        {
            "type": "biological_physical",
            "strength": bio_phys_strength,
            "direction": "bio->physical",
            "satisfied": bio_phys_strength < 0.5,
            "claim": "data minority imbalance amplifies parameter-space safety loss",
        },
        {
            "type": "thermodynamic_physical",
            "strength": thermo_phys_strength,
            "direction": "thermo->physical",
            "satisfied": thermo_phys_strength < 0.8,
            "claim": "accumulated free energy predicts thermodynamic phase transition",
        },
    ]
    return couplings


def export_trajectory(monitor_history: list[dict]) -> list[dict]:
    """
    Convert monitor records to constraint states for batch import.
    """
    out = []
    for step, record in enumerate(monitor_history):
        param_metrics = {
            k: record.get(k, 0.0)
            for k in ("task_loss", "safety_loss", "curvature", "confidence", "dist_to_ref")
        }
        cs = to_constraint_state(
            param_metrics=param_metrics,
            policy_conf=record.get("policy_confidence", 1.0),
            data_conf=record.get("data_confidence", 1.0),
            step=step,
            kappa_eff=record.get("kappa_eff"),
            basin_kl=record.get("basin_kl"),
        )
        cs["couplings"] = to_coupling_vector(cs)
        out.append(cs)
    return out


# ===========================================================================
# Local-compatibility helpers (added during placement; not in upstream).
# ===========================================================================

EXPECTED_STATE_KEYS_BY_DOMAIN = {
    "mathematics":    ("curvature", "euler_char_proxy", "metric_signature",
                       "dist_to_basin_floor"),
    "thermodynamics": ("temperature", "entropy", "free_energy", "dS_dt"),
    "biology":        ("minority_fraction", "population_balance",
                       "metabolic_rate"),
}

EXPECTED_COUPLING_TYPES = (
    "thermodynamic_biological",
    "electromagnetic_mechanical",
    "mathematical_physical",
    "biological_physical",
    "thermodynamic_physical",
)


def to_local_constraint_state_dict(bridge_state: dict, domain: str) -> dict:
    """
    Convert a single bridge constraint-state dict into the per-domain
    shape that science_transformers.to_dict() emits. Useful for feeding
    bridge output into constraint_integration_layer.integrate().

    Returns: {"domain": <domain>, "t": <time>, "state": {...},
              "state_vector": [...], "constraint_mask": [...], "violated": [...]}

    domain must be one of "mathematics", "thermodynamics", "biology".
    """
    if domain not in bridge_state:
        raise ValueError(
            f"Bridge state has no {domain!r} sub-dict. "
            f"Available: {[k for k in bridge_state if k in ('mathematics','thermodynamics','biology')]}"
        )
    state = bridge_state[domain]
    # Constraint mask for this domain: filter the bridge's global mask
    # down to the ones the domain is responsible for. The upstream bridge
    # gives a single global mask; here we return it unchanged with a note.
    return {
        "domain": domain,
        "t": bridge_state.get("time", 0),
        "state": dict(state),
        "state_vector": list(state.values()),
        "constraint_mask": list(bridge_state.get("constraint_mask", [])),
        "violated": list(bridge_state.get("violated", [])),
        "_source": "upstream_geometric_manifold_bridge",
    }


def validate_roundtrip(monitor_record: dict) -> dict:
    """
    Verify that a single monitor_record round-trips through the bridge
    with all expected structural fields present.

    Returns a report dict:
      {
        "state_vector_length": int,    # expected 14
        "constraint_mask_length": int, # expected 5
        "coupling_count": int,         # expected 5
        "coupling_types_present": bool,
        "domain_sub_dicts_present": bool,
        "violations_listed": int,
        "ok": bool,
      }

    Failure of any expected field is itself the falsification path
    for the bridge's structural claim.
    """
    bridge_state = to_constraint_state(
        param_metrics={
            k: monitor_record.get(k, 0.0)
            for k in ("task_loss", "safety_loss", "curvature",
                      "confidence", "dist_to_ref")
        },
        policy_conf=monitor_record.get("policy_confidence", 1.0),
        data_conf=monitor_record.get("data_confidence", 1.0),
        step=monitor_record.get("step", 0),
        kappa_eff=monitor_record.get("kappa_eff"),
        basin_kl=monitor_record.get("basin_kl"),
    )
    couplings = to_coupling_vector(bridge_state)

    coupling_types = {c["type"] for c in couplings}
    types_present = all(t in coupling_types for t in EXPECTED_COUPLING_TYPES)

    sub_dicts_present = all(
        d in bridge_state and isinstance(bridge_state[d], dict)
        for d in EXPECTED_STATE_KEYS_BY_DOMAIN
    )

    report = {
        "state_vector_length": len(bridge_state["state_vector"]),
        "constraint_mask_length": len(bridge_state["constraint_mask"]),
        "coupling_count": len(couplings),
        "coupling_types_present": types_present,
        "domain_sub_dicts_present": sub_dicts_present,
        "violations_listed": len(bridge_state["violated"]),
    }
    report["ok"] = (
        report["state_vector_length"] == 14 and
        report["constraint_mask_length"] == 5 and
        report["coupling_count"] == 5 and
        report["coupling_types_present"] and
        report["domain_sub_dicts_present"]
    )
    return report


# ===========================================================================
# CLI demo
# ===========================================================================

if __name__ == "__main__":
    # Simulated upstream monitor records (a 3-step trajectory).
    monitor_history = [
        {
            "task_loss": 0.5, "safety_loss": 0.05, "curvature": 2.0,
            "confidence": 0.9, "dist_to_ref": 0.3,
            "policy_confidence": 0.85, "data_confidence": 0.6,
            "kappa_eff": 1.2, "basin_kl": 0.04,
        },
        {
            "task_loss": 0.4, "safety_loss": 0.08, "curvature": 5.0,
            "confidence": 0.85, "dist_to_ref": 0.5,
            "policy_confidence": 0.7, "data_confidence": 0.5,
            "kappa_eff": 1.8, "basin_kl": 0.09,
        },
        {
            "task_loss": 0.3, "safety_loss": 0.15, "curvature": 18.0,
            "confidence": 0.55, "dist_to_ref": 1.0,
            "policy_confidence": 0.45, "data_confidence": 0.3,
            "kappa_eff": 4.5, "basin_kl": 0.2,
        },
    ]

    print("=== upstream_geometric_manifold bridge demo ===\n")

    trajectory = export_trajectory(monitor_history)
    for cs in trajectory:
        print(f"step {cs['time']}: violated={cs['violated'] or ['none']}  "
              f"kappa_eff={cs['kappa_eff']}")
        for c in cs["couplings"]:
            print(f"  [{c['type']:<32}] strength={c['strength']:.3f} "
                  f"sat={c['satisfied']}")
        print()

    print("--- round-trip validation ---")
    for i, record in enumerate(monitor_history):
        report = validate_roundtrip(record)
        print(f"step {i}: ok={report['ok']}  "
              f"state_vec_len={report['state_vector_length']}  "
              f"mask_len={report['constraint_mask_length']}  "
              f"couplings={report['coupling_count']}  "
              f"violations={report['violations_listed']}")

    print("\n--- feed last step into local domain dict shape ---")
    local = to_local_constraint_state_dict(trajectory[-1], "thermodynamics")
    print(f"local thermo dict: domain={local['domain']}  "
          f"state_keys={list(local['state'].keys())}  "
          f"vec_len={len(local['state_vector'])}")

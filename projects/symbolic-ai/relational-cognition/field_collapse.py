#!/usr/bin/env python3
# field_collapse.py
# CC0 / public domain. JinnZ2. stdlib only. model-update-resilient.
#
# Field-driven extension of the diversity-collapse model.
# Wires into: mean_field.py (order parameter), run_collapse_experiment.py (driver),
#             CLAIM_TABLE.fab.json (emits a claim row at the bottom).
#
# Resumption point closed:
#   - switchable Phi_ext(t)        : external field (broadcast fear), scenario-selectable
#   - degradable R(t)              : reciprocity term, dies under sustained field
#
# PHYSICS
#   agent frame-state x in [-1,+1]   -1 = orthogonal/flux frame   +1 = proximity-fear basin
#   tilted double well   U(x) = x^4/4 - x^2/2 - h*x
#   effective tilt       h_eff(t) = Phi_ext(t) + J_eff(t)*m(t),  m = <x>
#   coupling             J_eff = J0*(2 - R(t))      reciprocity dies -> coupling rises
#   Kramers rate         r = sqrt(U''_min*|U''_saddle|)/(2*pi*gamma) * exp(-dU/D)
#   spinodal             |h_eff| > h* = 2/sqrt(27) -> minority well gone (saddle-node)
#
#   Two-state mean field: p_minus (orthodox/flux holders), p_plus (basin), p-+p+ = 1.
#   dp_plus/dt = p_minus*r(-> +) - p_plus*r(+ -> -)
#   diversity  R_div = 4*p_plus*p_minus   (1 at 50/50, 0 at full collapse)

import math

PI = math.pi
H_SPINODAL = 2.0 / math.sqrt(27.0)   # ~0.384900

# ----------------------------------------------------------------------
# tilted double well  U(x) = x^4/4 - x^2/2 - h x
# ----------------------------------------------------------------------

def U(x, h):   return 0.25*x**4 - 0.5*x**2 - h*x
def Upp(x):    return 3.0*x**2 - 1.0          # U''(x)

def well_roots(h):
    """Real roots of U'(x)=x^3 - x - h = 0. Returns sorted list (1 or 3 reals)."""
    # depressed cubic t^3 + p t + q, here p=-1, q=-h
    p, q = -1.0, -h
    disc = -(4.0*p**3 + 27.0*q**2)            # >0 -> three real roots
    if disc > 0:
        m = 2.0*math.sqrt(-p/3.0)
        # acos argument clamped for numerical safety
        arg = (3.0*q)/(p*m)
        arg = max(-1.0, min(1.0, arg))
        theta = math.acos(arg)
        roots = [m*math.cos(theta/3.0 - 2.0*PI*k/3.0) for k in range(3)]
        return sorted(roots)
    else:
        # one real root (monostable) via Cardano real form
        D = (q/2.0)**2 + (p/3.0)**3
        s = math.sqrt(D)
        u = math.copysign(abs(-q/2.0 + s) ** (1.0/3.0), -q/2.0 + s)
        v = math.copysign(abs(-q/2.0 - s) ** (1.0/3.0), -q/2.0 - s)
        return [u + v]

def barriers(h):
    """
    Returns dict with well/saddle geometry.
    monostable=True when the minority well has vanished (|h|>h*).
    """
    r = well_roots(h)
    if len(r) == 1:
        return {"monostable": True, "x_minority": None, "x_saddle": None,
                "x_majority": r[0], "dU_minority": 0.0, "dU_majority": None}
    x_lo, x_sad, x_hi = r                       # for h>0: x_hi is the deeper (majority) well
    if h >= 0:
        x_minor, x_major = x_lo, x_hi
    else:
        x_minor, x_major = x_hi, x_lo
    dU_minor = U(x_sad, h) - U(x_minor, h)      # barrier holding minority-well agents
    dU_major = U(x_sad, h) - U(x_major, h)
    return {"monostable": False, "x_minority": x_minor, "x_saddle": x_sad,
            "x_majority": x_major, "dU_minority": dU_minor, "dU_major": dU_major}

def kramers(dU, x_well, x_saddle, D, gamma):
    if dU <= 0 or x_well is None or x_saddle is None:
        return 1.0e3                            # no barrier -> fast escape (capitulation)
    curv = math.sqrt(abs(Upp(x_well)) * abs(Upp(x_saddle)))
    return curv / (2.0*PI*gamma) * math.exp(-dU / D)

# ----------------------------------------------------------------------
# external field profiles  Phi_ext(t)   (this week, decomposed)
# ----------------------------------------------------------------------

def phi_ext(t, scenario, T):
    """t in [0,T]. broadcast window is the middle third (the '8 videos in a day')."""
    organic = 0.05
    macro   = 0.16 if t > 0.15*T else 0.0       # Belfast+Iran prime switches on
    base = organic + (macro if scenario in ("macro_prime", "apex_amp") else 0.0)
    if scenario == "apex_amp" and 0.33*T < t < 0.60*T:
        base *= 1.95                            # apex broadcast multiplier (lists, gurus)
    return base

# ----------------------------------------------------------------------
# degradable reciprocity R(t):  dies under sustained field, slow recovery
# ----------------------------------------------------------------------

def step_reciprocity(R, phi, dt, beta=1.1, lam=0.15, R_min=0.05):
    dR = -beta*abs(phi)*R*dt + lam*(1.0 - R)*dt
    return max(R_min, min(1.0, R + dR))

# ----------------------------------------------------------------------
# integrate mean-field occupancy
# ----------------------------------------------------------------------

def run_scenario(scenario, T=300.0, dt=0.1, J0=0.11, D=0.075, gamma=1.0):
    n = int(T/dt)
    p_plus, R = 0.5, 1.0
    ts, m_t, div_t, heff_t, R_t, crossed = [], [], [], [], [], False
    cross_t = None
    for i in range(n):
        t = i*dt
        m = 2.0*p_plus - 1.0                     # <x> with x≈±1
        J_eff = J0*(2.0 - R)
        h_eff = phi_ext(t, scenario, T) + J_eff*m
        b = barriers(h_eff)
        if b["monostable"] and not crossed:
            crossed, cross_t = True, t
        # escape rates between wells
        r_minor_to_major = kramers(b["dU_minority"], b["x_minority"], b["x_saddle"], D, gamma)
        if b["monostable"]:
            r_major_to_minor = 0.0
        else:
            r_major_to_minor = kramers(b["dU_major"], b["x_majority"], b["x_saddle"], D, gamma)
        p_minus = 1.0 - p_plus
        dpp = (p_minus*r_minor_to_major - p_plus*r_major_to_minor)*dt
        p_plus = max(0.0, min(1.0, p_plus + dpp))
        R = step_reciprocity(R, phi_ext(t, scenario, T), dt)
        ts.append(t); m_t.append(m); div_t.append(4.0*p_plus*(1.0-p_plus))
        heff_t.append(h_eff); R_t.append(R)
    return {"scenario": scenario, "t": ts, "m": m_t, "diversity": div_t,
            "h_eff": heff_t, "R": R_t, "crossed_spinodal": crossed, "cross_t": cross_t,
            "final_diversity": div_t[-1], "peak_h": max(heff_t)}

# ----------------------------------------------------------------------
# stdlib ascii plot (phone-readable, no dependency)
# ----------------------------------------------------------------------

def spark(series, width=56, lo=0.0, hi=1.0):
    blocks = " .:-=+*#%@"
    step = max(1, len(series)//width)
    s = series[::step][:width]
    out = []
    for v in s:
        f = (v - lo)/(hi - lo) if hi > lo else 0.0
        f = max(0.0, min(0.999, f))
        out.append(blocks[int(f*len(blocks))])
    return "".join(out)

# ----------------------------------------------------------------------
# experiment
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print(f"SPINODAL  h* = 2/sqrt(27) = {H_SPINODAL:.4f}")
    print("diversity sparkline: full ' '..collapse — high=diverse, fades=collapsed\n")
    rows = []
    for sc in ("organic", "macro_prime", "apex_amp"):
        r = run_scenario(sc)
        rows.append(r)
        xed = f"CROSSED h* at t={r['cross_t']:.0f}" if r["crossed_spinodal"] else "subcritical (held)"
        print(f"{sc:>12} | peak h_eff={r['peak_h']:.3f} | final R_div={r['final_diversity']:.3f} | {xed}")
        print(f"             div  |{spark(r['diversity'])}|")
        print(f"             R(t) |{spark(r['R'])}|\n")

    # ---- emit CLAIM row for CLAIM_TABLE.fab.json -------------------------
    apex = next(r for r in rows if r["scenario"] == "apex_amp")
    macro = next(r for r in rows if r["scenario"] == "macro_prime")
    claim = {
        "id": "COLLAPSE_019",
        "claim": ("Apex amplification, not organic fear, is the saddle-node-crossing "
                  "term in field-driven diversity collapse. Subcritical Phi_ext (organic "
                  "fear) holds; the broadcast multiplier vanishes the minority well."),
        "predicts": "apex_amp crosses h*; macro_prime alone approaches but holds",
        "result": ("CONFIRMED" if (apex["crossed_spinodal"] and not macro["crossed_spinodal"])
                   else "REFUTED"),
        "evidence": {
            "h_spinodal": round(H_SPINODAL, 4),
            "apex_peak_h": round(apex["peak_h"], 4),
            "macro_peak_h": round(macro["peak_h"], 4),
            "apex_final_diversity": round(apex["final_diversity"], 4),
            "macro_final_diversity": round(macro["final_diversity"], 4),
        },
        "refutation_protocol": "update the claim, never modify the simulation",
    }
    import json
    print("CLAIM_TABLE.fab.json row:")
    print(json.dumps(claim, indent=2))

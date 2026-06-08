# ozone_constraint_checker.py  v2
# repo: cascade-engine   CC0   stdlib only   phone-buildable
#
# REVISION NOTE (v1 -> v2):
#   dropped "local source causes local O3" — that assumption is wrong under
#   transport-dominated conditions. replaced with regime-first classification.
#
# PHYSICS:
#   O3 is NOT produced at the emission site.
#   it forms DOWNWIND, in the plume, over hours.
#   in NOx-limited regime: MORE NOx -> more O3 (linear)
#   in NOx-saturated regime: MORE NOx -> LESS O3 (titration of OH)
#   transition threshold is LOWER when hot (reaction rates ∝ exp(-Ea/RT))
#   so the same emission load produces different O3 depending on regime.
#
#   HEAT CASCADE:
#   10°C increase ≈ 2-3× faster reaction rates
#   warm air is less dense → poorer mixing → inversion trapping
#   higher VOC volatilization → more precursors
#   → regime can flip without any change in emissions
#
#   FIRE LOADING:
#   HONO, HCHO from fire smoke = additional HOx sources
#   → accelerates O3 chemistry regardless of NOx level
#   aerosol_optical_depth (AOD): thick fresh smoke SUPPRESSES photolysis
#   thin/aged smoke can ENHANCE it (scattering)
#   → sign of fire effect depends on smoke age/density
#
# FALSIFICATION (revised):
#   uniform saturation + upwind plume present (FIRMS) = EXPECTED — model consistent
#   uniform saturation + NO plume present            = REAL ANOMALY — flag it
#   local spike under NOx-saturated regime            = EXPECTED — not a puzzle
#   local spike under NOx-limited + no fire load      = needs a local source

from dataclasses import dataclass
import math

# ─────────────────────────────────────────────
# 1. THERMODYNAMIC SCALING
# ─────────────────────────────────────────────
EA_OVER_R = 5000.0    # K  (effective Ea/R for lumped tropospheric O3 chemistry)
T_REF     = 298.0     # K  reference (25°C)

def reaction_rate_scale(T_celsius: float) -> float:
    """Arrhenius scaling relative to T_REF. Returns multiplier."""
    T_K = T_celsius + 273.15
    return math.exp(-EA_OVER_R / T_K) / math.exp(-EA_OVER_R / T_REF)

def mixing_height_scale(T_celsius: float, baseline_T: float = 25.0) -> float:
    """Warmer surface → stronger inversion → lower mixing height → worse trapping.
    Returns scaling factor on effective column depth (1.0 at baseline).
    Hot stagnant conditions can halve the mixing height."""
    delta = T_celsius - baseline_T
    return max(0.3, 1.0 - 0.025 * delta)   # 2.5% per °C, floor at 0.3

# ─────────────────────────────────────────────
# 2. NOx REGIME CLASSIFIER
# ─────────────────────────────────────────────
# NOx-limited:   more NOx → more O3 (rural/remote areas, low-emission zones)
# NOx-saturated: more NOx → less O3 (urban cores, high-emission days)
# the counterintuitive result: a low-emission zone IN a plume will see MORE O3
# per unit NOx than the core of the plume source. titration works both ways.
NOX_SAT_THRESHOLD_BASELINE = 50.0    # ppb NOx at which saturation begins, 25°C
HOX_SENSITIVITY = 1.5                # ppb O3 per ppb HOx_excess in limited regime

def classify_regime(NOx_ppb: float, T_celsius: float) -> dict:
    """Classify NOx regime accounting for temperature shift of threshold."""
    rate_scale = reaction_rate_scale(T_celsius)
    # higher temp → threshold is reached at lower NOx (reactions run faster)
    effective_threshold = NOX_SAT_THRESHOLD_BASELINE / rate_scale
    if NOx_ppb < effective_threshold * 0.6:
        regime = "NOx_limited"
    elif NOx_ppb > effective_threshold * 1.4:
        regime = "NOx_saturated"
    else:
        regime = "transition"
    return {
        "regime": regime,
        "effective_threshold_ppb": round(effective_threshold, 1),
        "NOx_ppb": NOx_ppb,
        "rate_scale": round(rate_scale, 3),
    }

# ─────────────────────────────────────────────
# 3. FIRE LOADING
# ─────────────────────────────────────────────
@dataclass
class FireLoad:
    HONO_ppb: float          # HOx precursor from smoke
    HCHO_ppb: float          # HOx precursor from smoke
    AOD: float               # aerosol optical depth (0=clear, >1 thick smoke)
    smoke_age_hours: float   # fresh (<2h) suppresses, aged (>6h) neutral/enhancing

    def HOx_enhancement(self) -> float:
        """Additional HOx production rate relative to clean air (dimensionless multiplier)."""
        base = 0.1 * self.HONO_ppb + 0.05 * self.HCHO_ppb
        return max(0.0, base)

    def photolysis_factor(self) -> float:
        """Effect of aerosol on photolysis rate (J-value multiplier).
        Fresh thick smoke suppresses; aged thin smoke near neutral."""
        if self.smoke_age_hours < 2.0:
            return max(0.3, 1.0 - 0.5 * self.AOD)   # suppression
        elif self.smoke_age_hours > 6.0:
            return min(1.2, 1.0 + 0.1 * min(self.AOD, 1.0))   # mild enhancement
        else:
            return 1.0 - 0.2 * self.AOD   # partial suppression during aging

# ─────────────────────────────────────────────
# 4. TRANSPORT TERM — upwind plume
# ─────────────────────────────────────────────
@dataclass
class UplwindPlume:
    present: bool
    preformed_O3_ppb: float = 0.0    # O3 already formed in plume before arrival
    NOx_advected_ppb: float = 0.0    # NOx carried in (adds to local NOx budget)

# ─────────────────────────────────────────────
# 5. FULL O3 ESTIMATE
# ─────────────────────────────────────────────
def estimate_O3(
    local_NOx_ppb: float,
    T_celsius: float,
    VOC_index: float,          # 0..1 relative VOC availability
    fire: FireLoad | None,
    plume: UplwindPlume | None,
    background_O3_ppb: float = 40.0,
) -> dict:
    """
    Estimate surface O3 concentration and flag anomalies.
    Returns a scored dict; does NOT claim precision — all coefficients are
    order-of-magnitude placeholders until calibrated to field data.
    """
    fire = fire or FireLoad(0, 0, 0, 0)
    plume = plume or UplwindPlume(False)

    # effective NOx budget
    total_NOx = local_NOx_ppb + plume.NOx_advected_ppb
    regime_info = classify_regime(total_NOx, T_celsius)
    regime = regime_info["regime"]

    # rate and mixing
    rate = reaction_rate_scale(T_celsius)
    mix  = mixing_height_scale(T_celsius)
    J    = fire.photolysis_factor()    # photolysis modifier

    # O3 production in-column
    if regime == "NOx_limited":
        # more NOx = more O3; VOC also drives; HOx accelerates
        HOx_term = fire.HOx_enhancement() * HOX_SENSITIVITY
        production = (0.8 * total_NOx + 20.0 * VOC_index + HOx_term) * rate * J
    elif regime == "NOx_saturated":
        # adding NOx REDUCES O3 via OH titration; VOC becomes limiting
        production = (30.0 * VOC_index - 0.2 * total_NOx) * rate * J
        production = max(0.0, production)
    else:  # transition
        production = (0.4 * total_NOx + 15.0 * VOC_index) * rate * J

    # concentration in column (inverse mixing height → higher when trapped)
    column_O3 = production / mix

    # add transport contribution
    transport_O3 = plume.preformed_O3_ppb if plume.present else 0.0

    total_O3 = background_O3_ppb + column_O3 + transport_O3

    # ── ANOMALY FLAGS ──────────────────────────────────────────────────────────
    flags = []
    if total_O3 > 70.0:
        flags.append("NAAQS_8h_exceedance_risk")
    if total_O3 > 70.0 and not plume.present and regime == "NOx_saturated":
        flags.append("ANOMALY: saturated_exceedance_without_plume — local chemistry only, investigate")
    if total_O3 > 70.0 and plume.present:
        flags.append("EXPECTED: transport_plume_dominant")
    if mix < 0.5:
        flags.append("SEVERE_INVERSION: concentration_multiplied")
    if J < 0.6:
        flags.append("PHOTOLYSIS_SUPPRESSED: fresh_smoke_AOD")
    if J > 1.1:
        flags.append("PHOTOLYSIS_ENHANCED: aged_smoke_scattering")

    return {
        "regime": regime,
        "effective_threshold_NOx_ppb": regime_info["effective_threshold_ppb"],
        "rate_scale": regime_info["rate_scale"],
        "photolysis_factor": round(J, 3),
        "mixing_height_scale": round(mix, 3),
        "column_O3_production": round(column_O3, 1),
        "transport_O3": round(transport_O3, 1),
        "estimated_O3_ppb": round(total_O3, 1),
        "flags": flags,
    }

# ─────────────────────────────────────────────
# 6. DEMO CASES
# ─────────────────────────────────────────────
DEMO_CASES = [
    ("MN_baseline_cool",
     dict(local_NOx_ppb=20, T_celsius=22, VOC_index=0.3,
          fire=None, plume=None)),
    ("MN_heat_event_no_plume",
     dict(local_NOx_ppb=20, T_celsius=38, VOC_index=0.4,
          fire=None, plume=UplwindPlume(False))),
    ("MN_heat_plus_transport_plume",
     dict(local_NOx_ppb=20, T_celsius=38, VOC_index=0.4,
          fire=None, plume=UplwindPlume(True, preformed_O3_ppb=35, NOx_advected_ppb=15))),
    ("MN_fire_fresh_smoke",
     dict(local_NOx_ppb=25, T_celsius=35, VOC_index=0.5,
          fire=FireLoad(HONO_ppb=2.0, HCHO_ppb=8.0, AOD=1.2, smoke_age_hours=1.0),
          plume=UplwindPlume(True, preformed_O3_ppb=20, NOx_advected_ppb=10))),
    ("MN_fire_aged_smoke",
     dict(local_NOx_ppb=25, T_celsius=35, VOC_index=0.5,
          fire=FireLoad(HONO_ppb=0.5, HCHO_ppb=3.0, AOD=0.4, smoke_age_hours=10.0),
          plume=UplwindPlume(True, preformed_O3_ppb=25, NOx_advected_ppb=8))),
    ("ANOMALY_saturated_no_plume",
     dict(local_NOx_ppb=80, T_celsius=40, VOC_index=0.2,
          fire=None, plume=UplwindPlume(False))),
]

if __name__ == "__main__":
    print("OZONE CONSTRAINT CHECKER v2  (regime-flip physics)\n")
    for label, kwargs in DEMO_CASES:
        r = estimate_O3(**kwargs)
        print(f"  [{label}]")
        print(f"    regime={r['regime']}  O3={r['estimated_O3_ppb']} ppb"
              f"  rate_scale={r['rate_scale']}  mix={r['mixing_height_scale']}"
              f"  J={r['photolysis_factor']}")
        for f in r["flags"]:
            print(f"    FLAG: {f}")
        print()
    print("FALSIFICATION CONTRACT:")
    print("  saturated + plume present   -> EXPECTED (not an anomaly)")
    print("  saturated + NO plume        -> REAL FLAG (local chemistry only)")
    print("  limited + high O3           -> check HOx/fire load and transport")
    print("  rate_scale > 2 + low mix    -> heat cascade active, small mass gets big")

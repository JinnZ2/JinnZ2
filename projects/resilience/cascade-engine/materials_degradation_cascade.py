# materials_degradation_cascade.py
# repo: cascade-engine   CC0   stdlib only   phone-buildable
#
# air chemistry → conductor corrosion → grid I²R loss
#
# PHYSICS:
#   H2SO4 + O3 + humidity + temp → pitting rate on Cu/Al conductors
#   diffusion_rate ∝ exp(-E_diffusion/RT)  → 15°C hotter ≈ 3-4× faster
#   two-phase failure:
#     phase 1: OXIDE LAYER INTACT — slow linear pitting, oxide self-repairs
#     phase 2: OXIDE BREACH (pitting > oxide threshold) → galvanic runaway
#              current density spikes ~5×, O2 reduction accelerates,
#              Cu²⁺/Al³⁺ dissolution becomes autocatalytic
#
#   I²R LOSS COUPLING:
#     increased resistance from cross-section loss → more heat → faster diffusion
#     → accelerated pit growth → more resistance (positive feedback loop)
#
# OUTPUT: time_to_failure per conductor under compound conditions.
# UNITS: all dimensional. time in years. concentration in ppb. temp in °C.

from dataclasses import dataclass
import math

# ─────────────────────────────────────────────
# 1. MATERIAL PARAMETERS
# ─────────────────────────────────────────────
@dataclass
class Conductor:
    material: str                  # "copper" | "aluminum"
    cross_section_mm2: float       # nominal
    resistivity_ohm_m: float       # at 20°C
    oxide_thickness_um: float      # protective oxide layer
    oxide_repair_rate: float       # um/year self-repair (anodic passivation)
    E_diffusion_over_R: float      # K (Ea/R for ion diffusion through oxide)

COPPER = Conductor(
    material="copper",
    cross_section_mm2=50.0,
    resistivity_ohm_m=1.68e-8,
    oxide_thickness_um=0.5,         # thin CuO/Cu2O layer
    oxide_repair_rate=0.10,         # slow; Cu doesn't passivate as well as Al
    E_diffusion_over_R=6500.0,
)
ALUMINUM = Conductor(
    material="aluminum",
    cross_section_mm2=70.0,
    resistivity_ohm_m=2.82e-8,
    oxide_thickness_um=4.0,         # thicker Al2O3 layer — better protection
    oxide_repair_rate=0.50,         # faster passivation
    E_diffusion_over_R=7200.0,
)

# ─────────────────────────────────────────────
# 2. CORROSION ENVIRONMENT
# ─────────────────────────────────────────────
@dataclass
class CorrosionEnv:
    T_celsius: float
    H2SO4_ppb: float        # acid deposition proxy
    O3_ppb: float           # oxidant (drives Cu/Al oxidation)
    RH_fraction: float      # relative humidity 0..1 (electrolyte availability)
    hours_wet_per_year: float = 2000.0   # hours conductor surface is wet/year

T_REF = 298.15   # K

def diffusion_scale(T_celsius: float, E_over_R: float) -> float:
    T_K = T_celsius + 273.15
    return math.exp(-E_over_R / T_K) / math.exp(-E_over_R / T_REF)

# ─────────────────────────────────────────────
# 3. PITTING RATE (um/year)
# ─────────────────────────────────────────────
# acid + oxidant + wet time → ion flux → pit depth rate
# O3 and H2SO4 work synergistically: O3 oxidises the surface,
# H2SO4 dissolves the oxide, electrolyte (humidity) carries ions away.
# Base rate from Kucera & Mattsson corrosion dose-response
# (simplified; real models use SO2 deposition velocity + time of wetness).

def pitting_rate_um_yr(c: Conductor, env: CorrosionEnv, phase: str) -> float:
    wet_fraction = env.hours_wet_per_year / 8760.0
    acid_term    = 0.02 * env.H2SO4_ppb                  # um/yr per ppb H2SO4
    oxidant_term = 0.005 * env.O3_ppb                    # um/yr per ppb O3
    humidity_mod = env.RH_fraction * wet_fraction
    diff_scale   = diffusion_scale(env.T_celsius, c.E_diffusion_over_R)
    base_rate    = (acid_term + oxidant_term) * humidity_mod * diff_scale

    if phase == "runaway":
        # oxide breach: galvanic acceleration ~5×, autocatalytic
        # additionally: local I²R heating adds 5-10°C, accelerating diffusion
        extra_T = 7.5   # °C I²R self-heating estimate
        diff_hot = diffusion_scale(env.T_celsius + extra_T, c.E_diffusion_over_R)
        return base_rate * 5.0 * (diff_hot / diff_scale)
    return base_rate

# ─────────────────────────────────────────────
# 4. FAILURE TIMELINE
# ─────────────────────────────────────────────
def simulate_failure(c: Conductor, env: CorrosionEnv,
                     max_years: float = 50.0,
                     dt: float = 0.25) -> dict:
    """Step through years until conductor cross-section loss exceeds 30%
    (IEEE threshold for derating) or oxide breach triggers runaway.
    Returns year-by-year state and time_to_failure."""
    pit_depth   = 0.0    # um cumulative
    cs_loss_frac = 0.0   # fraction of cross-section lost
    phase = "intact"
    t = 0.0
    history = []

    # approximate conductor radius from cross-section (circular wire)
    r_mm = math.sqrt(c.cross_section_mm2 / math.pi)
    r_um = r_mm * 1000.0

    time_to_oxide_breach  = None
    time_to_30pct_loss    = None
    time_to_failure       = None

    while t < max_years:
        rate = pitting_rate_um_yr(c, env, phase)
        net_rate = rate - (c.oxide_repair_rate if phase == "intact" else 0.0)
        net_rate = max(0.0, net_rate)
        pit_depth += net_rate * dt

        # check phase flip
        if phase == "intact" and pit_depth >= c.oxide_thickness_um:
            phase = "runaway"
            time_to_oxide_breach = round(t, 2)

        # cross-section loss: approximation — pit area ≈ π * (pit_depth/2)² for hemispherical pit
        # fraction of total cross section
        pit_r_um = pit_depth / 2.0
        pit_area_mm2 = math.pi * (pit_r_um / 1000.0) ** 2
        cs_loss_frac = min(1.0, pit_area_mm2 / c.cross_section_mm2)

        # resistance increases as cross-section shrinks
        eff_cs = c.cross_section_mm2 * (1.0 - cs_loss_frac)
        resistance_ratio = c.cross_section_mm2 / eff_cs if eff_cs > 0 else float("inf")

        history.append({
            "year": round(t, 2),
            "pit_depth_um": round(pit_depth, 3),
            "phase": phase,
            "cs_loss_pct": round(cs_loss_frac * 100, 1),
            "resistance_ratio": round(resistance_ratio, 3),
        })

        if cs_loss_frac >= 0.30 and time_to_30pct_loss is None:
            time_to_30pct_loss = round(t, 2)
            time_to_failure = time_to_30pct_loss
            break

        t += dt

    if time_to_failure is None:
        time_to_failure = ">50yr"

    return {
        "material": c.material,
        "environment": {
            "T_celsius": env.T_celsius,
            "H2SO4_ppb": env.H2SO4_ppb,
            "O3_ppb": env.O3_ppb,
            "RH": env.RH_fraction,
        },
        "time_to_oxide_breach_yr": time_to_oxide_breach,
        "time_to_30pct_loss_yr": time_to_30pct_loss,
        "time_to_failure": time_to_failure,
        "diff_scale_at_T": round(diffusion_scale(env.T_celsius, c.E_diffusion_over_R), 3),
        "history_sample": history[::4],   # every 1yr
    }

# ─────────────────────────────────────────────
# 5. DEMO CASES (Minnesota grid context)
# ─────────────────────────────────────────────
DEMO_ENVS = [
    ("MN_baseline",         CorrosionEnv(T_celsius=10,  H2SO4_ppb=5,   O3_ppb=40, RH_fraction=0.65)),
    ("MN_heat_moderate",    CorrosionEnv(T_celsius=25,  H2SO4_ppb=8,   O3_ppb=55, RH_fraction=0.70)),
    ("MN_heat_compound",    CorrosionEnv(T_celsius=38,  H2SO4_ppb=15,  O3_ppb=75, RH_fraction=0.80)),
    ("fire_smoke_event",    CorrosionEnv(T_celsius=35,  H2SO4_ppb=20,  O3_ppb=68, RH_fraction=0.75)),
    ("Houston_analog",      CorrosionEnv(T_celsius=32,  H2SO4_ppb=25,  O3_ppb=85, RH_fraction=0.85)),
]

if __name__ == "__main__":
    print("MATERIALS DEGRADATION CASCADE\n")
    print(f"{'environment':22} {'material':8} {'oxide_breach':>13} {'30pct_loss':>11} {'diff_scale':>11}")
    print("-" * 72)
    for label, env in DEMO_ENVS:
        for cond in (COPPER, ALUMINUM):
            r = simulate_failure(cond, env)
            ob  = str(r["time_to_oxide_breach_yr"]) + "yr" if r["time_to_oxide_breach_yr"] else "never"
            ttf = str(r["time_to_failure"]) + "yr" if isinstance(r["time_to_failure"], float) else r["time_to_failure"]
            print(f"  {label:22} {cond.material:8} {ob:>13} {ttf:>11} {r['diff_scale_at_T']:>11}")
    print()
    print("NOTE: coefficients are order-of-magnitude placeholders.")
    print("Calibrate acid_term and oxidant_term against field corrosion data.")
    print("Galvanic runaway 5× multiplier from Mattsson (1970) — verify for your alloy.")

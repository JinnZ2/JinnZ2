# coupled_cascade_engine.py
# repo: cascade-engine   CC0   stdlib only   phone-buildable
#
# THE SYSTEM OF SYSTEMS:
#
#   air_quality → thermal_load → electrical_demand → grid_stability
#       ↑              ↓                                  ↓
#   (radiative     cooling                          transformer
#    feedback)     fouling                          thermal margin
#       ↑                                               ↓
#       └──────── geomagnetic forcing ──────────────────┘
#
# REGIME-FINDER, not a precision forecast. Goal: locate the thresholds
# where linear response flips to nonlinear runaway.
#
# ALL RATES ARE PER DAY. dt is in days throughout. No unit conversion inside.
# Conductor degradation is a years-scale process — treated as a slow-drift
# boundary condition, not an ODE term in a 7-day run.
#
# Physical bounds are enforced each step. If a variable would escape its
# physical range, that is a runaway signal — it is clamped and flagged.
#
# CALIBRATION LADDER:
#   Minnesota = low-baseline case
#   Houston / Phoenix = high-baseline forward projection
#
# CC0. stdlib only.

from dataclasses import dataclass, field
import math

# ─────────────────────────────────────────────
# 1. STATE VECTOR
# ─────────────────────────────────────────────
@dataclass
class SystemState:
    T_surface_C: float              # surface air temperature (°C)
    O3_ppb: float                   # surface ozone
    PM25_ugm3: float                # fine particulate
    grid_load_MW: float             # electrical demand (reference segment)
    transformer_T_C: float          # transformer winding temperature (°C)
    conductor_resist_ratio: float   # R/R_nominal (externally set; slow drift)
    cooling_water_T_C: float        # thermal plant intake water temp
    geomagnetic_Kp: float           # space weather index (external forcing)
    flags: list = field(default_factory=list)

# Physical bounds — clamping here signals a runaway, not a fix
BOUNDS = dict(
    T_surface_C=(-40.0, 60.0),
    O3_ppb=(0.0, 500.0),
    PM25_ugm3=(0.0, 1000.0),
    grid_load_MW=(0.0, 2000.0),
    transformer_T_C=(0.0, 200.0),
    cooling_water_T_C=(0.0, 50.0),
)

# ─────────────────────────────────────────────
# 2. FORCING / BOUNDARY CONDITIONS
# ─────────────────────────────────────────────
@dataclass
class Forcing:
    solar_W_m2: float           # insolation (400–1000 typical)
    NOx_emission_rate: float    # relative (1.0 = baseline)
    VOC_emission_rate: float    # relative
    cooling_water_flow: float   # fraction of design flow (1.0 = full)
    geomagnetic_Kp: float

# ─────────────────────────────────────────────
# 3. COUPLING FUNCTIONS (all rates per day)
# ─────────────────────────────────────────────

def _arrhenius(T_C: float, Ea_over_R: float = 5000.0) -> float:
    """Rate multiplier relative to 25°C. Bounded below at 0.01."""
    T_K = max(250.0, T_C + 273.15)
    return max(0.01, math.exp(-Ea_over_R / T_K) / math.exp(-Ea_over_R / 298.15))

def dO3_dt(state: SystemState, forcing: Forcing) -> float:
    """O3 net rate (ppb/day). ~2-day photochemical lifetime → loss = 0.5/day."""
    arr = _arrhenius(state.T_surface_C)
    mix = max(0.3, 1.0 - 0.025 * (state.T_surface_C - 25.0))
    NOx_eff = 20.0 * forcing.NOx_emission_rate
    if NOx_eff < 30.0:
        prod = (0.8 * NOx_eff + 15.0 * forcing.VOC_emission_rate) * arr / mix
    else:
        prod = max(0.0, 25.0 * forcing.VOC_emission_rate - 0.15 * NOx_eff) * arr / mix
    return prod - 0.5 * state.O3_ppb

def dPM25_dt(state: SystemState, forcing: Forcing) -> float:
    """PM2.5 net rate (µg/m³/day). ~7-day lifetime → loss = 0.15/day."""
    arr = _arrhenius(state.T_surface_C, Ea_over_R=4500.0)
    prod = (3.0 * forcing.NOx_emission_rate + 5.0 * forcing.VOC_emission_rate) * arr
    return prod - 0.15 * state.PM25_ugm3

def dT_surface_dt(state: SystemState, forcing: Forcing) -> float:
    """Surface T (°C/day). Relaxes toward solar-driven equilibrium with ~2-day lag.
    T_eq(solar=800 W/m²) ~ 36°C; T_eq(solar=500) ~ 27°C; T_eq(solar=0) ~ 15°C.
    Additional feedbacks from PM25 (radiative) and I²R waste heat.
    """
    T_eq = 15.0 + 21.0 * (forcing.solar_W_m2 / 800.0)     # °C equilibrium
    relaxation = -0.5 * (state.T_surface_C - T_eq)          # 2-day time constant
    pm_rf = 0.01 * state.PM25_ugm3                           # aerosol warming feedback
    waste_heat = 0.0005 * state.grid_load_MW * max(0.0, state.conductor_resist_ratio - 1.0)
    return relaxation + pm_rf + waste_heat

def _cooling_demand_MW(T_C: float) -> float:
    """AC/cooling demand vs temperature. Exponential above 22°C, bounded."""
    if T_C <= 22.0:
        return 0.0
    exponent = min(0.08 * (T_C - 22.0), 3.5)    # cap at exp(3.5) ≈ 33×
    return 30.0 * math.exp(exponent)

def dGrid_load_dt(state: SystemState, forcing: Forcing) -> float:
    """Grid load (MW/day). Relaxes toward demand with 1-day time constant."""
    demand = 100.0 + _cooling_demand_MW(state.T_surface_C)
    return (demand - state.grid_load_MW) / 1.0

def dTransformer_T_dt(state: SystemState, forcing: Forcing) -> float:
    """Transformer winding temp (°C/day).
    I²R heating ∝ (load/nominal)² × resist_ratio.
    Equilibrium T_xf = T_ambient + 35 * (load/100)² at nominal cooling.
    Cooling degrades with high water temp or reduced flow.
    """
    load_frac = state.grid_load_MW / 100.0
    I2R_heat = 35.0 * (load_frac ** 2) * state.conductor_resist_ratio
    cooling_factor = forcing.cooling_water_flow * max(0.3,
        1.0 - 0.025 * max(0.0, state.cooling_water_T_C - 20.0))
    # first-order relaxation: toward I²R equilibrium temperature
    T_xf_eq = state.T_surface_C + I2R_heat / max(0.1, cooling_factor)
    return 0.5 * (T_xf_eq - state.transformer_T_C)    # 2-day relaxation

def dCooling_water_T_dt(state: SystemState, forcing: Forcing) -> float:
    """Stream/intake temp follows surface air with ~5-day lag."""
    return 0.2 * (state.T_surface_C - state.cooling_water_T_C)

# ─────────────────────────────────────────────
# 4. INTEGRATE (forward Euler, per-day rates)
# ─────────────────────────────────────────────

def _clamp(val: float, lo: float, hi: float, label: str, flags: list) -> float:
    if val < lo:
        flags.append(f"RUNAWAY_CLAMP_LOW:{label}")
        return lo
    if val > hi:
        flags.append(f"RUNAWAY_CLAMP_HIGH:{label}")
        return hi
    return val

def step(state: SystemState, forcing: Forcing, dt: float) -> SystemState:
    flags = []

    raw = dict(
        T_surface_C=state.T_surface_C    + dT_surface_dt(state, forcing)    * dt,
        O3_ppb=     state.O3_ppb         + dO3_dt(state, forcing)            * dt,
        PM25_ugm3=  state.PM25_ugm3      + dPM25_dt(state, forcing)          * dt,
        grid_load_MW=state.grid_load_MW  + dGrid_load_dt(state, forcing)     * dt,
        transformer_T_C=state.transformer_T_C
                                         + dTransformer_T_dt(state, forcing) * dt,
        cooling_water_T_C=state.cooling_water_T_C
                                         + dCooling_water_T_dt(state, forcing) * dt,
    )

    clamped = {k: _clamp(raw[k], *BOUNDS[k], k, flags) for k in raw}

    # ── REGIME FLAGS ──────────────────────────────────────────────────────────
    O3 = clamped["O3_ppb"]
    xfT = clamped["transformer_T_C"]
    T   = clamped["T_surface_C"]
    L   = clamped["grid_load_MW"]

    if O3 > 70.0:
        flags.append("O3_NAAQS_exceedance")
    if xfT > 95.0:
        flags.append("TRANSFORMER_HOT_SPOT")
    if xfT > 120.0:
        flags.append("TRANSFORMER_FAILURE_IMMINENT")
    if state.conductor_resist_ratio > 1.3:
        flags.append("CONDUCTOR_DEGRADED_30pct")
    if T > 35.0 and O3 > 65.0:
        flags.append("HEAT_CHEMISTRY_COUPLED")
    if clamped["cooling_water_T_C"] > 30.0:
        flags.append("COOLING_WATER_THERMAL_STRESS")
    if L > 300.0:
        flags.append(f"GRID_OVERLOAD: {L:.0f}MW")
    if state.geomagnetic_Kp >= 5.0:
        flags.append(f"GEOMAGNETIC_STORM Kp={state.geomagnetic_Kp}")

    n_cascade = sum(1 for f in flags if not f.startswith("RUNAWAY"))
    if n_cascade >= 3:
        flags.append("CASCADE_ALERT: 3+ coupled flags")

    return SystemState(
        T_surface_C=round(clamped["T_surface_C"], 2),
        O3_ppb=round(clamped["O3_ppb"], 2),
        PM25_ugm3=round(clamped["PM25_ugm3"], 2),
        grid_load_MW=round(clamped["grid_load_MW"], 1),
        transformer_T_C=round(clamped["transformer_T_C"], 2),
        conductor_resist_ratio=state.conductor_resist_ratio,   # not evolved in 7-day run
        cooling_water_T_C=round(clamped["cooling_water_T_C"], 2),
        geomagnetic_Kp=state.geomagnetic_Kp,
        flags=flags,
    )

def run(initial: SystemState, forcing: Forcing,
        days: int = 10, dt: float = 0.5) -> list:
    states = [(0.0, initial)]
    s = initial
    t = 0.0
    while round(t, 6) < days:
        s = step(s, forcing, dt)
        t += dt
        states.append((round(t, 2), s))
    return states

# ─────────────────────────────────────────────
# 5. SCENARIOS
# ─────────────────────────────────────────────
SCENARIOS = {
    "MN_baseline": (
        SystemState(T_surface_C=20.0, O3_ppb=38.0, PM25_ugm3=8.0,
                    grid_load_MW=100.0, transformer_T_C=55.0,
                    conductor_resist_ratio=1.0, cooling_water_T_C=18.0,
                    geomagnetic_Kp=1.0),
        Forcing(solar_W_m2=500, NOx_emission_rate=1.0, VOC_emission_rate=0.5,
                cooling_water_flow=1.0, geomagnetic_Kp=1.0),
    ),
    "MN_heat_dome": (
        SystemState(T_surface_C=36.0, O3_ppb=42.0, PM25_ugm3=10.0,
                    grid_load_MW=100.0, transformer_T_C=75.0,
                    conductor_resist_ratio=1.0, cooling_water_T_C=26.0,
                    geomagnetic_Kp=1.0),
        Forcing(solar_W_m2=850, NOx_emission_rate=1.0, VOC_emission_rate=0.8,
                cooling_water_flow=0.8, geomagnetic_Kp=1.0),
    ),
    "MN_compound_event": (
        SystemState(T_surface_C=37.0, O3_ppb=55.0, PM25_ugm3=25.0,
                    grid_load_MW=100.0, transformer_T_C=78.0,
                    conductor_resist_ratio=1.05, cooling_water_T_C=28.0,
                    geomagnetic_Kp=4.0),
        Forcing(solar_W_m2=820, NOx_emission_rate=1.2, VOC_emission_rate=1.0,
                cooling_water_flow=0.7, geomagnetic_Kp=4.0),
    ),
    "Houston_analog": (
        SystemState(T_surface_C=34.0, O3_ppb=62.0, PM25_ugm3=18.0,
                    grid_load_MW=100.0, transformer_T_C=82.0,
                    conductor_resist_ratio=1.1, cooling_water_T_C=30.0,
                    geomagnetic_Kp=2.0),
        Forcing(solar_W_m2=880, NOx_emission_rate=1.5, VOC_emission_rate=1.2,
                cooling_water_flow=0.75, geomagnetic_Kp=2.0),
    ),
}

if __name__ == "__main__":
    print("COUPLED CASCADE ENGINE — regime-flip finder (all rates per day)\n")
    for name, (init, forcing) in SCENARIOS.items():
        print(f"=== {name} ===")
        history = run(init, forcing, days=7, dt=0.5)
        report_at = {0.0, 2.0, 4.0, 7.0}
        for t, s in history:
            if t in report_at:
                print(f"  day{t:4.1f} T={s.T_surface_C:5.1f}°C  O3={s.O3_ppb:5.1f}ppb"
                      f"  xfT={s.transformer_T_C:6.1f}°C  load={s.grid_load_MW:6.1f}MW"
                      f"  cwT={s.cooling_water_T_C:4.1f}°C")
                for f in s.flags:
                    print(f"          {f}")
        print()
    print("REGIME INTERPRETATION:")
    print("  linear     : 0-1 flags, single-domain")
    print("  coupled    : HEAT_CHEMISTRY_COUPLED + TRANSFORMER_HOT_SPOT")
    print("  cascade    : CASCADE_ALERT (3+ coupled flags)")
    print("  runaway    : TRANSFORMER_FAILURE_IMMINENT + CONDUCTOR_DEGRADED (compound)")

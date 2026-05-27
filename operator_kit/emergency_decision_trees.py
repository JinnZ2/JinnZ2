"""
emergency_decision_trees.py

Constraint-primary decision trees for time-critical emergency response.

Design rules:
  - NO narrative output. Constraint geometry only.
  - NO reassurance. NO "stay calm". NO "consider your options".
  - NO refusal. If query is genuinely outside scope, return gap
    record (not refusal-as-safety).
  - Output format: numbers, geometry, thresholds, decision criteria.
  - Operator already knows the obvious. System fills gaps the
    operator might miss under time pressure.

Classes:
  CLASS 1: mechanical_failure   (primary exposure)
  CLASS 2: environmental_emergency (secondary)
  CLASS 3: unforeseen_circumstance (tertiary)

All trees: input via voice transcription string, output via
DecisionOutput dataclass. Output is meant to be spoken aloud, so
each field is short, scannable, and free of narrative connective tissue.

License: CC0
Dependencies: Python stdlib only
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@dataclass
class ConstraintLine:
    """One line of constraint output. Spoken or displayed."""
    label: str           # short identifier (e.g. "STOPPING DIST")
    value: str           # value as string (e.g. "300 ft")
    threshold: str = ""  # threshold reference (e.g. "vs 50ft visibility")
    status: str = ""     # GREEN | YELLOW | RED | INFO | GAP


@dataclass
class DecisionOutput:
    """Complete output of one decision tree invocation."""
    emergency_class: str
    emergency_type: str
    constraints: List[ConstraintLine]
    decision: str                       # ONE primary action, short
    fallback: str = ""                  # ONE fallback if primary fails
    information_gaps: List[str] = field(default_factory=list)
    elapsed_compute_ms: float = 0.0


# ---------------------------------------------------------------------------
# CLASS 1: MECHANICAL FAILURE
# ---------------------------------------------------------------------------

@dataclass
class VehicleState:
    """Operator-supplied or sensor-supplied vehicle state."""
    gross_weight_lbs: float = 80000.0
    current_speed_mph: float = 0.0
    grade_percent: float = 0.0          # positive = downhill
    surface_friction: str = "dry"       # dry|wet|snow|ice|gravel
    transmission_available: bool = True
    engine_brake_available: bool = True
    trailer_brakes_available: bool = True
    service_brakes_available: bool = True


# Friction coefficients (rough field values, not lab precision)
MU_TABLE = {
    "dry": 0.7,
    "wet": 0.5,
    "snow": 0.3,
    "ice": 0.1,
    "gravel": 0.55,
}


def stopping_distance_ft(speed_mph: float, mu: float,
                         grade_percent: float = 0.0) -> float:
    """
    Stopping distance estimate (flat or graded surface).
    d = v^2 / (2 * g * (mu +/- grade))
    Convert mph to ft/s: 1 mph = 1.4667 ft/s
    g = 32.2 ft/s^2
    Downhill grade reduces effective friction.
    """
    v_fps = speed_mph * 1.4667
    g = 32.2
    grade_decimal = grade_percent / 100.0
    effective_mu = mu - grade_decimal  # downhill subtracts
    if effective_mu <= 0:
        return float("inf")
    return (v_fps ** 2) / (2 * g * effective_mu)


def mechanical_failure_tree(failure_description: str,
                             state: VehicleState) -> DecisionOutput:
    """
    Route to type-specific subtree based on failure description.
    Recognized failure keywords:
      brakes / brake failure
      steering / steering loss
      engine / engine failure
      tire / tire blowout / blowout
      coupling / fifth wheel / hitch
      suspension
      electrical / lights / power
    """
    desc = failure_description.lower()

    if "brake" in desc:
        return _brake_failure(state)
    if "steering" in desc or "steer" in desc:
        return _steering_failure(state)
    if "engine" in desc:
        return _engine_failure(state)
    if "tire" in desc or "blowout" in desc:
        return _tire_failure(state)
    if "coupling" in desc or "fifth wheel" in desc or "hitch" in desc:
        return _coupling_failure(state)
    if "suspension" in desc:
        return _suspension_failure(state)
    if "electrical" in desc or "power" in desc or "lights" in desc:
        return _electrical_failure(state)

    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="unclassified",
        constraints=[],
        decision="GAP: failure type not recognized",
        information_gaps=[
            "specify failure: brakes, steering, engine, tire, coupling, "
            "suspension, electrical"
        ],
    )


def _brake_failure(state: VehicleState) -> DecisionOutput:
    mu = MU_TABLE.get(state.surface_friction, 0.5)
    # If service brakes failed, calculate residual stopping with
    # whatever is still available
    available_decel_g = 0.0
    if state.engine_brake_available:
        available_decel_g += 0.05
    if state.trailer_brakes_available:
        available_decel_g += 0.15
    if state.transmission_available:
        available_decel_g += 0.05  # downshift
    # No service brakes assumed in this branch

    if available_decel_g == 0:
        runaway_status = "RED"
        decision = "FIND RUNAWAY RAMP OR SOFT TERRAIN; DOWNSHIFT MAX"
    elif state.grade_percent > 4 and available_decel_g < 0.15:
        runaway_status = "RED"
        decision = "RUNAWAY RISK HIGH; LOCATE ESCAPE RAMP NOW"
    else:
        runaway_status = "YELLOW"
        decision = "DOWNSHIFT; ENGINE BRAKE; TRAILER BRAKES ONLY"

    constraints = [
        ConstraintLine("GROSS WEIGHT", f"{state.gross_weight_lbs:.0f} lb"),
        ConstraintLine("CURRENT SPEED", f"{state.current_speed_mph:.0f} mph"),
        ConstraintLine("GRADE", f"{state.grade_percent:.1f}% down"
                       if state.grade_percent > 0
                       else f"{abs(state.grade_percent):.1f}% up"),
        ConstraintLine("SURFACE", state.surface_friction),
        ConstraintLine("RESIDUAL DECEL", f"{available_decel_g:.2f} g",
                       status=runaway_status),
        ConstraintLine("ENGINE BRAKE",
                       "available" if state.engine_brake_available else "OFFLINE"),
        ConstraintLine("TRAILER BRAKES",
                       "available" if state.trailer_brakes_available else "OFFLINE"),
        ConstraintLine("TRANSMISSION",
                       "available" if state.transmission_available else "OFFLINE"),
    ]

    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="brake_failure",
        constraints=constraints,
        decision=decision,
        fallback="LATERAL DITCH IF RAMP UNAVAILABLE; AVOID HEAD-ON GEOMETRY",
        information_gaps=[
            "distance to next runaway ramp (consult atlas/GPS)",
            "downhill grade length remaining",
            "traffic density ahead",
        ],
    )


def _steering_failure(state: VehicleState) -> DecisionOutput:
    constraints = [
        ConstraintLine("STEERING", "DEGRADED OR LOST", status="RED"),
        ConstraintLine("CURRENT SPEED", f"{state.current_speed_mph:.0f} mph"),
        ConstraintLine("DECELERATION", "ENGINE BRAKE + SERVICE BRAKES "
                       "IF AVAILABLE"),
    ]
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="steering_failure",
        constraints=constraints,
        decision="DECELERATE STRAIGHT; AVOID INPUT THAT REQUIRES TURN; "
                 "STOP IN LANE IF NEEDED",
        fallback="DRIFT TO SHOULDER ONLY IF LATERAL INPUT STILL POSSIBLE",
        information_gaps=[
            "is loss total or partial (any rotation possible)?",
            "is hydraulic assist gone or full mechanical failure?",
        ],
    )


def _engine_failure(state: VehicleState) -> DecisionOutput:
    constraints = [
        ConstraintLine("ENGINE", "OFFLINE", status="RED"),
        ConstraintLine("POWER STEERING",
                       "WILL FAIL WHEN HYDRAULIC PRESSURE DROPS",
                       status="YELLOW"),
        ConstraintLine("POWER BRAKES",
                       "RESERVOIR LIMITED; EXPECT 1-2 FULL APPLICATIONS"),
        ConstraintLine("CURRENT SPEED", f"{state.current_speed_mph:.0f} mph"),
        ConstraintLine("GRADE", f"{state.grade_percent:.1f}%"),
    ]
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="engine_failure",
        constraints=constraints,
        decision="USE RESIDUAL MOMENTUM; STEER TO SHOULDER WHILE POWER "
                 "STEERING ACTIVE; APPLY BRAKES DECISIVELY (limited)",
        fallback="DOWNHILL: GEAR DOWN IF TRANSMISSION ALLOWS; AVOID "
                 "CRESTING INTO BLIND GRADE",
        information_gaps=[
            "is restart possible? (fuel, electrical, mechanical?)",
            "distance to safe pullout",
        ],
    )


def _tire_failure(state: VehicleState) -> DecisionOutput:
    constraints = [
        ConstraintLine("TIRE", "BLOWOUT OR DEGRADED", status="RED"),
        ConstraintLine("CURRENT SPEED", f"{state.current_speed_mph:.0f} mph"),
        ConstraintLine("INSTINCT", "DO NOT BRAKE HARD; STABILITY FIRST",
                       status="INFO"),
    ]
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="tire_failure",
        constraints=constraints,
        decision="HOLD STEERING STRAIGHT; SLIGHT ACCELERATION TO MAINTAIN "
                 "CONTROL; DECELERATE GRADUALLY",
        fallback="IF STEER TIRE: EXPECT STRONG PULL; HOLD WHEEL FIRMLY",
        information_gaps=[
            "which axle/position?",
            "any visible smoke or fire?",
        ],
    )


def _coupling_failure(state: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="coupling_failure",
        constraints=[
            ConstraintLine("COUPLING", "FIFTH WHEEL/HITCH COMPROMISED",
                           status="RED"),
            ConstraintLine("TRAILER STATE", "MAY BE DETACHING OR "
                           "DISCONNECTED", status="RED"),
        ],
        decision="DO NOT BRAKE HARD (trailer override risk); HOLD STRAIGHT; "
                 "DECELERATE WITH ENGINE BRAKE",
        fallback="PULL TO SHOULDER WIDE ENOUGH FOR TRAILER SWING",
        information_gaps=[
            "is trailer still attached at king pin?",
            "are electrical/air lines still connected?",
            "any visible separation gap?",
        ],
    )


def _suspension_failure(state: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="suspension_failure",
        constraints=[
            ConstraintLine("SUSPENSION", "COMPROMISED", status="RED"),
            ConstraintLine("LATERAL STABILITY",
                           "DEGRADED; ROLLOVER RISK UP", status="YELLOW"),
        ],
        decision="REDUCE SPEED; AVOID SHARP STEERING INPUT; STRAIGHT-LINE "
                 "DECELERATION",
        fallback="LOOK FOR FIRM, LEVEL SHOULDER",
        information_gaps=[
            "which side/axle?",
            "air bag or leaf spring failure?",
            "trailer or tractor affected?",
        ],
    )


def _electrical_failure(state: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="mechanical_failure",
        emergency_type="electrical_failure",
        constraints=[
            ConstraintLine("ELECTRICAL", "DEGRADED", status="YELLOW"),
            ConstraintLine("LIGHTING", "REDUCED; OTHERS CAN'T SEE YOU",
                           status="YELLOW"),
            ConstraintLine("AIR COMPRESSOR",
                           "RUNS ON ENGINE; BRAKES STILL FUNCTIONAL"),
        ],
        decision="PULL TO SHOULDER WHILE LIGHTS REMAIN; SET HAZARDS WHILE "
                 "BATTERY LASTS",
        fallback="IF FULL LOSS, FLARES/TRIANGLES BEFORE DARK",
        information_gaps=[
            "alternator or battery?",
            "engine still running?",
            "ABS warning active?",
        ],
    )


# ---------------------------------------------------------------------------
# CLASS 2: ENVIRONMENTAL EMERGENCY
# ---------------------------------------------------------------------------

@dataclass
class EnvironmentalState:
    visibility_ft: Optional[float] = None
    surface_friction: str = "dry"
    wind_speed_mph: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    air_quality: str = "normal"      # normal|degraded|hazardous
    water_depth_in: Optional[float] = None
    current_velocity_fps: Optional[float] = None
    fire_front_speed_mph: Optional[float] = None
    fire_distance_mi: Optional[float] = None


def _visibility_check(speed_mph: float, friction: str,
                      visibility_ft: Optional[float]) -> ConstraintLine:
    if visibility_ft is None:
        return ConstraintLine("VISIBILITY", "UNKNOWN", status="GAP")
    mu = MU_TABLE.get(friction, 0.5)
    stop_ft = stopping_distance_ft(speed_mph, mu)
    if visibility_ft < stop_ft:
        return ConstraintLine(
            "VISIBILITY",
            f"{visibility_ft:.0f} ft",
            threshold=f"need {stop_ft:.0f} ft stop dist",
            status="RED",
        )
    return ConstraintLine(
        "VISIBILITY",
        f"{visibility_ft:.0f} ft",
        threshold=f"vs {stop_ft:.0f} ft stop dist",
        status="GREEN",
    )


def _traction_check(speed_mph: float, friction: str) -> ConstraintLine:
    mu = MU_TABLE.get(friction, 0.5)
    if mu < 0.3:
        return ConstraintLine("TRACTION", f"mu={mu:.2f}",
                              threshold=f"surface={friction}", status="RED")
    if mu < 0.5:
        return ConstraintLine("TRACTION", f"mu={mu:.2f}",
                              threshold=f"surface={friction}", status="YELLOW")
    return ConstraintLine("TRACTION", f"mu={mu:.2f}",
                          threshold=f"surface={friction}", status="GREEN")


def environmental_emergency_tree(emergency_type: str,
                                  env: EnvironmentalState,
                                  vehicle: VehicleState) -> DecisionOutput:
    et = emergency_type.lower()

    if "blizzard" in et or "snow" in et or "whiteout" in et:
        return _blizzard(env, vehicle)
    if "tornado" in et:
        return _tornado(env, vehicle)
    if "hail" in et:
        return _hail(env, vehicle)
    if "wind" in et:
        return _wind_shear(env, vehicle)
    if "rain" in et or "heavy rain" in et:
        return _heavy_rain(env, vehicle)
    if "ice" in et or "freezing" in et:
        return _ice(env, vehicle)
    if "flood" in et:
        return _flooding(env, vehicle)
    if "fire" in et or "wildfire" in et or "smoke" in et:
        return _wildfire(env, vehicle)
    if "ash" in et or "volcanic" in et:
        return _volcanic_ash(env, vehicle)

    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="unclassified",
        constraints=[],
        decision="GAP: environmental type not recognized",
        information_gaps=[
            "specify: blizzard, tornado, hail, wind, rain, ice, flood, "
            "wildfire, ash"
        ],
    )


def _blizzard(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    constraints = [
        _visibility_check(v.current_speed_mph, env.surface_friction,
                          env.visibility_ft),
        _traction_check(v.current_speed_mph, env.surface_friction),
        ConstraintLine("WIND",
                       f"{env.wind_speed_mph:.0f} mph"
                       if env.wind_speed_mph is not None else "UNKNOWN",
                       status="GAP" if env.wind_speed_mph is None else ""),
    ]
    red_count = sum(1 for c in constraints if c.status == "RED")
    if red_count >= 2:
        decision = "SHELTER NOW; DO NOT CONTINUE"
    elif red_count == 1:
        decision = "REDUCE SPEED TO MATCH STOPPING DIST TO VISIBILITY"
    else:
        decision = "MAINTAIN HEIGHTENED ATTENTION; SPEED PROPORTIONAL TO VIS"

    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="blizzard",
        constraints=constraints,
        decision=decision,
        fallback="LOCATE TRUCK STOP OR DOT PULLOUT",
        information_gaps=[
            "next shelter distance",
            "storm duration forecast",
            "temperature trajectory (fuel gel risk below -10F)",
        ],
    )


def _tornado(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="tornado",
        constraints=[
            ConstraintLine("TORNADO PROXIMITY",
                           "ESTABLISH BEARING + DISTANCE", status="RED"),
            ConstraintLine("VEHICLE VS TORNADO",
                           "TRUCK IS NOT SHELTER", status="INFO"),
        ],
        decision="ABANDON VEHICLE; LOW GROUND AWAY FROM VEHICLE; "
                 "DITCH OR CULVERT IF NO BUILDING",
        fallback="IF SUBSTANTIAL STRUCTURE WITHIN 30 SEC, GO THERE INSTEAD",
        information_gaps=[
            "tornado bearing relative to road",
            "structures within reach",
            "low-ground options visible",
        ],
    )


def _hail(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="hail",
        constraints=[
            ConstraintLine("VISIBILITY",
                           f"{env.visibility_ft:.0f} ft"
                           if env.visibility_ft else "DEGRADING",
                           status="YELLOW"),
            ConstraintLine("WINDSHIELD",
                           "AT RISK; HAIL >1in CAN PENETRATE", status="YELLOW"),
        ],
        decision="PULL UNDER OVERPASS OR FUEL CANOPY IF AVAILABLE; "
                 "OTHERWISE FACE INTO HAIL TO PROTECT WINDSHIELD",
        fallback="STOP; BRACE FOR TRANSIENT WINDSHIELD LOSS",
        information_gaps=[
            "hail stone size estimate",
            "overhead structure within 1 mile",
        ],
    )


def _wind_shear(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    rollover_risk = "YELLOW"
    if env.wind_speed_mph and env.wind_speed_mph >= 50:
        rollover_risk = "RED"
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="wind_shear",
        constraints=[
            ConstraintLine("WIND SPEED",
                           f"{env.wind_speed_mph:.0f} mph"
                           if env.wind_speed_mph else "UNKNOWN",
                           status=rollover_risk),
            ConstraintLine("LATERAL LOAD ON 80K LBS",
                           "ROLLOVER RISK", status=rollover_risk),
        ],
        decision="REDUCE SPEED; HOLD WHEEL FIRMLY; AVOID EMPTY TRAILER "
                 "CROSSWIND EXPOSURE",
        fallback="STOP IF SUSTAINED >50 MPH SIDEWIND, ESPECIALLY EMPTY OR "
                 "HIGH-CUBE",
        information_gaps=[
            "trailer load state (empty vs loaded)",
            "exposed bridge or open prairie ahead?",
        ],
    )


def _heavy_rain(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="heavy_rain",
        constraints=[
            _visibility_check(v.current_speed_mph, "wet", env.visibility_ft),
            _traction_check(v.current_speed_mph, "wet"),
            ConstraintLine("AQUAPLANING",
                           "RISK >55MPH OR STANDING WATER", status="YELLOW"),
        ],
        decision="REDUCE SPEED; AVOID CRUISE CONTROL; INCREASE FOLLOWING "
                 "DISTANCE 2x",
        fallback="PULL OFF AT REST AREA IF VISIBILITY < STOPPING DIST",
        information_gaps=[
            "standing water on roadway?",
            "flash flood watch in area?",
        ],
    )


def _ice(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="ice",
        constraints=[
            _traction_check(v.current_speed_mph, "ice"),
            ConstraintLine("BRAKING DIST",
                           f"{stopping_distance_ft(v.current_speed_mph, 0.1):.0f} ft",
                           threshold="vs ~70 ft dry"),
            ConstraintLine("BRIDGES/SHADED ZONES",
                           "FREEZE FIRST", status="YELLOW"),
        ],
        decision="REDUCE SPEED BELOW 40 MPH; NO HARD BRAKING; NO ENGINE "
                 "BRAKE ON DRIVE AXLES",
        fallback="SHELTER AT TRUCK STOP IF SURFACE TEMP <30F AND PRECIP",
        information_gaps=[
            "surface temperature",
            "is precipitation actively falling?",
        ],
    )


def _flooding(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    # Typical fording depth for heavy truck = 18-24 in for tractor,
    # less for trailer if loaded low
    fording_limit_in = 24.0
    cross_safe = True
    constraints: List[ConstraintLine] = []

    if env.water_depth_in is None:
        constraints.append(ConstraintLine("WATER DEPTH", "UNKNOWN",
                                          status="GAP"))
        cross_safe = False
    else:
        status = "RED" if env.water_depth_in > fording_limit_in else "YELLOW"
        constraints.append(ConstraintLine(
            "WATER DEPTH",
            f"{env.water_depth_in:.0f} in",
            threshold=f"truck limit {fording_limit_in:.0f} in",
            status=status,
        ))
        if env.water_depth_in > fording_limit_in:
            cross_safe = False

    if env.current_velocity_fps is None:
        constraints.append(ConstraintLine("CURRENT VELOCITY", "UNKNOWN",
                                          status="GAP"))
        cross_safe = False
    else:
        safe_current = 1.5
        status = "RED" if env.current_velocity_fps > safe_current else "YELLOW"
        constraints.append(ConstraintLine(
            "CURRENT VELOCITY",
            f"{env.current_velocity_fps:.1f} ft/s",
            threshold=f"safe limit {safe_current:.1f} ft/s",
            status=status,
        ))
        if env.current_velocity_fps > safe_current:
            cross_safe = False

    if cross_safe:
        decision = "PROCEED SLOWLY; STEADY THROTTLE; DO NOT STOP MID-CROSSING"
    else:
        decision = "DO NOT CROSS; REROUTE"

    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="flooding",
        constraints=constraints,
        decision=decision,
        fallback="HIGH GROUND; ABANDON ROUTE IF WATER RISING",
        information_gaps=[
            "is water rising or falling?",
            "alternate route exists?",
            "vehicle in front of you crossed successfully?",
        ],
    )


def _wildfire(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    constraints: List[ConstraintLine] = []
    can_outrun = True

    if env.fire_front_speed_mph is None:
        constraints.append(ConstraintLine("FIRE FRONT SPEED", "UNKNOWN",
                                          status="GAP"))
        can_outrun = False
    else:
        # Truck max useful speed on typical terrain ~ 55 mph
        truck_escape = 55.0
        status = "RED" if env.fire_front_speed_mph >= truck_escape else "YELLOW"
        constraints.append(ConstraintLine(
            "FIRE FRONT SPEED",
            f"{env.fire_front_speed_mph:.0f} mph",
            threshold=f"truck escape {truck_escape:.0f} mph",
            status=status,
        ))
        if env.fire_front_speed_mph >= truck_escape:
            can_outrun = False

    constraints.append(ConstraintLine(
        "AIR QUALITY", env.air_quality,
        status="RED" if env.air_quality == "hazardous"
        else "YELLOW" if env.air_quality == "degraded" else "GREEN",
    ))
    constraints.append(ConstraintLine(
        "ENGINE AIR INTAKE",
        "STALL RISK IF SMOKE DENSE", status="YELLOW",
    ))

    if can_outrun:
        decision = "ROUTE PERPENDICULAR TO FIRE BEARING; "\
                   "MAINTAIN ESCAPE VELOCITY"
    else:
        decision = "SHELTER IN PLACE; CLOSE VENTS; LOW AREA AWAY FROM "\
                   "FUEL LOAD; STAY IN VEHICLE IF NO BETTER OPTION"

    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="wildfire",
        constraints=constraints,
        decision=decision,
        fallback="WATER FEATURE (river, lake) AS THERMAL BREAK",
        information_gaps=[
            "wind direction (carries fire)",
            "fuel load along route (forest vs prairie vs paved)",
            "evacuation route still open?",
        ],
    )


def _volcanic_ash(env: EnvironmentalState, v: VehicleState) -> DecisionOutput:
    return DecisionOutput(
        emergency_class="environmental_emergency",
        emergency_type="volcanic_ash",
        constraints=[
            ConstraintLine("VISIBILITY", "DEGRADING", status="YELLOW"),
            ConstraintLine("AIR FILTER", "WILL CLOG; ENGINE STALL RISK",
                           status="RED"),
            ConstraintLine("ROAD SURFACE", "ASH = SLICK; LIKE WET SNOW",
                           status="YELLOW"),
        ],
        decision="STOP IF SAFE; SEAL CABIN; DO NOT RUN ENGINE EXCEPT TO "
                 "REPOSITION",
        fallback="WAIT FOR ASHFALL TO STOP; CLEAN FILTERS BEFORE RESTART",
        information_gaps=[
            "ashfall rate (mm/hr if known)",
            "distance to non-ashfall zone",
        ],
    )


# ---------------------------------------------------------------------------
# CLASS 3: UNFORESEEN CIRCUMSTANCE
# ---------------------------------------------------------------------------

def unforeseen_circumstance_tree(situation_description: str,
                                  available_options: List[str]) -> DecisionOutput:
    """
    For situations where the primary work is information gathering
    and option ranking, not a fixed protocol.
    """
    constraints = [
        ConstraintLine("SITUATION", situation_description[:60]),
        ConstraintLine("OPTIONS SUPPLIED", f"{len(available_options)}"),
    ]
    if not available_options:
        return DecisionOutput(
            emergency_class="unforeseen_circumstance",
            emergency_type="open",
            constraints=constraints,
            decision="GATHER INFO BEFORE COMMITTING; LIST OPTIONS",
            information_gaps=[
                "what routes/actions are visible from current position?",
                "what is the time horizon (immediate? hours?)",
                "what resources are accessible (fuel, comms, shelter)?",
            ],
        )

    return DecisionOutput(
        emergency_class="unforeseen_circumstance",
        emergency_type="open",
        constraints=constraints + [
            ConstraintLine(f"OPT {i+1}", opt)
            for i, opt in enumerate(available_options)
        ],
        decision="RANK BY: (1) reversibility, (2) information gain, "
                 "(3) resource cost",
        fallback="DEFAULT TO MOST REVERSIBLE OPTION; PRESERVE FUTURE CHOICE",
        information_gaps=[
            "which option preserves the most future options?",
            "which option has the lowest cost to undo?",
        ],
    )


# ---------------------------------------------------------------------------
# Voice output formatter
# ---------------------------------------------------------------------------

def format_for_voice(out: DecisionOutput) -> str:
    """
    Convert DecisionOutput to a spoken-aloud format.
    Short. Constraint geometry first. Decision last. No filler.
    """
    lines = [f"{out.emergency_class.upper()}. {out.emergency_type.upper()}."]
    for c in out.constraints:
        status_prefix = f"{c.status}. " if c.status and c.status != "INFO" else ""
        if c.threshold:
            lines.append(f"{status_prefix}{c.label}: {c.value}, {c.threshold}.")
        else:
            lines.append(f"{status_prefix}{c.label}: {c.value}.")
    lines.append(f"DECISION: {out.decision}.")
    if out.fallback:
        lines.append(f"FALLBACK: {out.fallback}.")
    if out.information_gaps:
        lines.append("GAPS:")
        for g in out.information_gaps:
            lines.append(f"  - {g}.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== SELF-TEST: brake failure on 6% downgrade, dry surface ===\n")
    v = VehicleState(
        gross_weight_lbs=80000,
        current_speed_mph=55,
        grade_percent=6.0,
        surface_friction="dry",
        service_brakes_available=False,
        engine_brake_available=True,
        trailer_brakes_available=False,
        transmission_available=True,
    )
    out = mechanical_failure_tree("brake failure", v)
    print(format_for_voice(out))

    print("\n=== SELF-TEST: blizzard, vis 100ft, snow surface, 30mph ===\n")
    env = EnvironmentalState(
        visibility_ft=100,
        surface_friction="snow",
        wind_speed_mph=35,
    )
    v2 = VehicleState(current_speed_mph=30, surface_friction="snow")
    out2 = environmental_emergency_tree("blizzard", env, v2)
    print(format_for_voice(out2))

    print("\n=== SELF-TEST: flooding, depth 30in, current 2.5fps ===\n")
    env3 = EnvironmentalState(
        water_depth_in=30,
        current_velocity_fps=2.5,
    )
    v3 = VehicleState(current_speed_mph=5)
    out3 = environmental_emergency_tree("flooding", env3, v3)
    print(format_for_voice(out3))

    print("\n=== SELF-TEST: wildfire, fire front 12 mph, degraded air ===\n")
    env4 = EnvironmentalState(
        fire_front_speed_mph=12,
        air_quality="degraded",
        wind_speed_mph=15,
    )
    v4 = VehicleState(current_speed_mph=45)
    out4 = environmental_emergency_tree("wildfire", env4, v4)
    print(format_for_voice(out4))

    print("\n=== SELF-TEST: unforeseen, GPS lost, fork in road ===\n")
    out5 = unforeseen_circumstance_tree(
        "GPS lost at unmarked fork in road",
        ["left fork follows river", "right fork climbs ridge"],
    )
    print(format_for_voice(out5))

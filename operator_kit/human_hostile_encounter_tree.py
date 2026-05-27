"""
human_hostile_encounter_tree.py

CLASS 5: HUMAN HOSTILE ENCOUNTER

Operator context:
  Solo small-female truck driver. Routine exposure to predatory
  approach, freight jacking, in-cab compromise attempts, delivery-
  site hostility, and post-incident response.

Design rules:
  - Operator KNOWS the behavior signatures already. System does not
    teach pattern recognition.
  - System provides CONSTRAINT GEOMETRY operator might miss under
    time pressure: escape vectors, witness availability, deterrent
    integration, escalation thresholds.
  - NO refusal-as-safety. NO advice to "call authorities first" as
    primary response (often unavailable, slow, or unsafe to do
    openly). Authority contact is ONE option in the decision tree,
    not the wrapper around it.
  - NO moral framing. NO "stay safe" reassurance.
  - Output format: matches other decision trees (DecisionOutput).

Sub-classes:
  5a: predatory approach (rest stop / fuel / delivery loitering)
  5b: freight jacking attempt (vehicle interdiction)
  5c: in-cab compromise attempt (door/window/distraction)
  5d: delivery / loading site hostility
  5e: post-incident response (after threat or contact)

Coupled modules:
  - wildlife_deterrent_system.py (shared 100 dB chaotic audio +
    optical strobe; deterrent is species-agnostic at the speaker)
  - operator_context_persistence.py (Class 5 registry entry)
  - emergency_decision_trees.py (ConstraintLine, DecisionOutput)

License: CC0
Dependencies: Python stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Output schema (matches other trees)
# ---------------------------------------------------------------------------

@dataclass
class ConstraintLine:
    label: str
    value: str
    threshold: str = ""
    status: str = ""   # GREEN | YELLOW | RED | INFO | GAP


@dataclass
class DecisionOutput:
    emergency_class: str
    emergency_type: str
    constraints: List[ConstraintLine]
    decision: str
    fallback: str = ""
    information_gaps: List[str] = field(default_factory=list)
    deterrent_call: Optional[Dict] = None  # parameters to pass to
                                            # wildlife_deterrent_system if
                                            # active deterrent indicated


# ---------------------------------------------------------------------------
# Sub-class router
# ---------------------------------------------------------------------------

def human_hostile_encounter_tree(
    description: str,
    location_context: str = "",
    operator_state: Optional[Dict] = None,
) -> DecisionOutput:
    """
    Route to sub-class based on description + context.

    description: operator voice report, e.g.
        "man following me at fuel stop"
        "truck blocking road, two approaching"
        "knocking on cab, two AM, rest area"

    location_context: rest_stop | fuel_stop | delivery | road |
                      shoulder | unknown

    operator_state: optional dict with keys:
        in_cab (bool), engine_running (bool), doors_locked (bool),
        weapon_accessible (bool), comms_available (bool),
        witnesses_present (bool), daylight (bool), trailer_loaded (bool)
    """
    if operator_state is None:
        operator_state = {}
    d = description.lower()
    loc = location_context.lower()

    # Route by description first, then by location

    # 5c: in-cab compromise (window/door/distraction)
    if any(k in d for k in ["knock", "window", "door", "trying door",
                              "tap on glass", "trying to open"]):
        return _in_cab_compromise(description, location_context, operator_state)

    # 5b: freight jacking / vehicle interdiction
    if any(k in d for k in ["block", "blocking", "stopped in road",
                              "obstacle", "vehicles ahead", "ambush",
                              "freight jack", "hijack"]):
        return _freight_jacking_attempt(description, location_context, operator_state)

    # 5d: delivery / loading site
    if "delivery" in loc or "loading" in loc or "dock" in loc \
            or "delivery" in d or "loading" in d or "warehouse" in d \
            or "shipper" in d or "consignee" in d:
        return _delivery_hostility(description, location_context, operator_state)

    # 5e: post-incident
    if any(k in d for k in ["after", "happened", "attacked", "assaulted",
                              "they left", "got away", "i'm hurt",
                              "post-incident", "documenting"]):
        return _post_incident_response(description, location_context, operator_state)

    # 5a: predatory approach (default for loitering/following/tracking)
    return _predatory_approach(description, location_context, operator_state)


# ---------------------------------------------------------------------------
# 5a: PREDATORY APPROACH
# ---------------------------------------------------------------------------

def _predatory_approach(description: str, loc: str,
                         st: Dict) -> DecisionOutput:
    in_cab = st.get("in_cab", True)
    engine_running = st.get("engine_running", False)
    doors_locked = st.get("doors_locked", True)
    witnesses = st.get("witnesses_present", False)
    daylight = st.get("daylight", True)
    comms = st.get("comms_available", True)

    constraints: List[ConstraintLine] = [
        ConstraintLine("LOCATION", loc or "unspecified",
                       status="GAP" if not loc else ""),
        ConstraintLine("IN CAB", "yes" if in_cab else "NO",
                       status="GREEN" if in_cab else "RED"),
        ConstraintLine("DOORS LOCKED", "yes" if doors_locked else "NO",
                       status="GREEN" if doors_locked else "RED"),
        ConstraintLine("ENGINE", "running" if engine_running else "off",
                       status="GREEN" if engine_running else "YELLOW"),
        ConstraintLine("WITNESSES", "present" if witnesses else "ABSENT",
                       status="GREEN" if witnesses else "YELLOW"),
        ConstraintLine("LIGHT", "daylight" if daylight else "DARK",
                       status="GREEN" if daylight else "YELLOW"),
        ConstraintLine("COMMS", "available" if comms else "DOWN",
                       status="GREEN" if comms else "RED"),
    ]

    # Threat geometry: isolation + darkness + comms down + no witnesses
    risk_factors = sum([
        0 if witnesses else 1,
        0 if daylight else 1,
        0 if comms else 1,
        0 if doors_locked else 2,
        0 if in_cab else 2,
    ])

    if risk_factors >= 4:
        risk_band = "RED"
        decision = ("DEPART NOW. ENGINE START IF OFF. DRIVE TO LIT, "
                    "WITNESSED LOCATION (truck stop, weigh station, "
                    "police station, ER entrance).")
    elif risk_factors >= 2:
        risk_band = "YELLOW"
        decision = ("RELOCATE TO HIGHER-VISIBILITY POSITION. LOCK ALL "
                    "DOORS. START ENGINE. PREPARE TO DEPART.")
    else:
        risk_band = "GREEN"
        decision = ("MONITOR. DOCUMENT (photo if non-provocative). "
                    "DO NOT EXIT CAB. DO NOT ENGAGE.")

    constraints.append(ConstraintLine("RISK FACTORS", f"{risk_factors}/5",
                                       status=risk_band))

    fallback = ("IF APPROACH CONTINUES: ACTIVATE DETERRENT (chaotic "
                "audio + strobe), AIR HORN, AMBER LIGHTS. "
                "IF CONTACT IMMINENT: DEPART REGARDLESS OF PROPERTY "
                "(unhooked trailer, blocked vehicles).")

    gaps = [
        "subject count (one, two, more)?",
        "weapon visible?",
        "approach angle (front, blind side)?",
        "any verbal contact attempted?",
        "distance closing or holding?",
        "vehicle type they arrived in (recorded for later)?",
    ]

    # Deterrent suggestion (parameters to pass to wildlife system)
    deterrent_call = None
    if risk_band in ("RED", "YELLOW"):
        deterrent_call = {
            "species": "unknown",   # chaotic broadband works on humans
            "distance_ft": None,    # operator estimates if needed
            "behavior_keywords": ["approach"],
            "audio_available": True,
            "operator_override_db": 100.0 if risk_band == "RED" else 90.0,
        }

    return DecisionOutput(
        emergency_class="human_hostile_encounter",
        emergency_type="predatory_approach",
        constraints=constraints,
        decision=decision,
        fallback=fallback,
        information_gaps=gaps,
        deterrent_call=deterrent_call,
    )


# ---------------------------------------------------------------------------
# 5b: FREIGHT JACKING ATTEMPT
# ---------------------------------------------------------------------------

def _freight_jacking_attempt(description: str, loc: str,
                              st: Dict) -> DecisionOutput:
    engine_running = st.get("engine_running", True)
    doors_locked = st.get("doors_locked", True)
    trailer_loaded = st.get("trailer_loaded", True)
    comms = st.get("comms_available", True)

    constraints: List[ConstraintLine] = [
        ConstraintLine("SCENARIO", "vehicle interdiction / blocking",
                       status="RED"),
        ConstraintLine("ENGINE", "running" if engine_running else "OFF",
                       status="GREEN" if engine_running else "RED"),
        ConstraintLine("DOORS LOCKED", "yes" if doors_locked else "NO",
                       status="GREEN" if doors_locked else "RED"),
        ConstraintLine("TRAILER", "loaded" if trailer_loaded else "empty",
                       status="INFO"),
        ConstraintLine("COMMS", "available" if comms else "DOWN",
                       status="GREEN" if comms else "RED"),
        ConstraintLine("80,000 LB MASS",
                       "kinetic asset; cannot be physically blocked by "
                       "passenger vehicle", status="INFO"),
    ]

    decision = (
        "DO NOT STOP for unexplained obstacles in isolated areas. "
        "If still moving: maintain speed, change lanes, drive shoulder "
        "if needed. If stopped: do not exit cab; do not roll window. "
        "If interdiction confirmed: engine on, slow forward pressure "
        "against blocking vehicle (mass advantage); horn continuous; "
        "amber lights; deterrent audio at max."
    )

    fallback = (
        "RAM-THROUGH is a legal option in confirmed interdiction "
        "(driver self-defense, varies by jurisdiction). Document "
        "everything dashcam. If breach: depart through obstacle and "
        "drive to nearest law enforcement, ER, or 24-hour facility. "
        "Property damage is acceptable cost of survival."
    )

    gaps = [
        "single obstacle or multiple coordinated vehicles?",
        "any one in obstacle path stationary on foot?",
        "weapons visible?",
        "is this isolated road or near witnesses/cameras?",
        "trailer cargo high-value indicator (signage, locks, seal)?",
        "is dispatcher reachable?",
    ]

    deterrent_call = {
        "species": "unknown",
        "distance_ft": None,
        "behavior_keywords": ["approach", "closer"],
        "audio_available": True,
        "operator_override_db": 100.0,
    }

    return DecisionOutput(
        emergency_class="human_hostile_encounter",
        emergency_type="freight_jacking_attempt",
        constraints=constraints,
        decision=decision,
        fallback=fallback,
        information_gaps=gaps,
        deterrent_call=deterrent_call,
    )


# ---------------------------------------------------------------------------
# 5c: IN-CAB COMPROMISE ATTEMPT
# ---------------------------------------------------------------------------

def _in_cab_compromise(description: str, loc: str,
                        st: Dict) -> DecisionOutput:
    engine_running = st.get("engine_running", False)
    doors_locked = st.get("doors_locked", True)
    daylight = st.get("daylight", False)  # most cab breaches at night
    comms = st.get("comms_available", True)

    distraction = any(k in description.lower()
                      for k in ["knock", "tap", "call out", "yell",
                                "asking for help", "claims emergency"])

    constraints: List[ConstraintLine] = [
        ConstraintLine("SCENARIO", "in-cab compromise attempt",
                       status="RED"),
        ConstraintLine("DOORS LOCKED", "yes" if doors_locked else "NO",
                       status="GREEN" if doors_locked else "RED"),
        ConstraintLine("ENGINE", "running" if engine_running else "OFF",
                       status="GREEN" if engine_running else "YELLOW"),
        ConstraintLine("LIGHT", "daylight" if daylight else "DARK",
                       status="YELLOW" if daylight else "RED"),
        ConstraintLine("DISTRACTION PATTERN",
                       "knock + emergency claim" if distraction
                       else "direct breach",
                       status="RED"),
        ConstraintLine("COMMS", "available" if comms else "DOWN",
                       status="GREEN" if comms else "RED"),
    ]

    decision = (
        "DO NOT OPEN. DO NOT ROLL WINDOW. DO NOT VERBALLY ENGAGE THROUGH "
        "GLASS BEYOND ONE WORD. START ENGINE. LIGHTS ON. HORN CONTINUOUS. "
        "DEPART. Knock + 'help me' at 2 AM in dark lot is the classic "
        "distraction pattern; accomplice is on the other side of cab."
    )

    fallback = (
        "IF DEPART BLOCKED: deterrent audio + strobe at MAX, horn "
        "continuous, drive over curb / through brush / onto grass to "
        "exit. Property cost acceptable. If 911 available, dial and "
        "leave line open while driving."
    )

    gaps = [
        "one subject visible or coordinated (check both sides)?",
        "weapon visible at window?",
        "vehicle they arrived in (block dashcam view)?",
        "have they been observed earlier (followed you in)?",
        "is engine cold (slower start)?",
    ]

    deterrent_call = {
        "species": "unknown",
        "distance_ft": 2.0,   # at-window range
        "behavior_keywords": ["approach", "closer"],
        "audio_available": True,
        "operator_override_db": 100.0,
    }

    return DecisionOutput(
        emergency_class="human_hostile_encounter",
        emergency_type="in_cab_compromise_attempt",
        constraints=constraints,
        decision=decision,
        fallback=fallback,
        information_gaps=gaps,
        deterrent_call=deterrent_call,
    )


# ---------------------------------------------------------------------------
# 5d: DELIVERY / LOADING SITE HOSTILITY
# ---------------------------------------------------------------------------

def _delivery_hostility(description: str, loc: str,
                         st: Dict) -> DecisionOutput:
    witnesses = st.get("witnesses_present", False)
    daylight = st.get("daylight", True)
    comms = st.get("comms_available", True)

    isolation_indicators = []
    if not witnesses:
        isolation_indicators.append("no witnesses")
    if not daylight:
        isolation_indicators.append("after-hours")
    if "after hours" in description.lower() or "alone" in description.lower():
        isolation_indicators.append("operator alone with worker(s)")

    constraints: List[ConstraintLine] = [
        ConstraintLine("LOCATION", loc or "delivery/loading site"),
        ConstraintLine("WITNESSES",
                       "present" if witnesses else "ABSENT",
                       status="GREEN" if witnesses else "RED"),
        ConstraintLine("LIGHT", "daylight" if daylight else "after-hours",
                       status="GREEN" if daylight else "YELLOW"),
        ConstraintLine("ISOLATION FACTORS",
                       f"{len(isolation_indicators)} ({', '.join(isolation_indicators) or 'none'})",
                       status="RED" if len(isolation_indicators) >= 2
                       else "YELLOW" if isolation_indicators
                       else "GREEN"),
        ConstraintLine("COMMS", "available" if comms else "DOWN",
                       status="GREEN" if comms else "RED"),
    ]

    decision = (
        "REFUSE ISOLATION: do not follow worker into back room, "
        "private office, or unobserved area. Stay with truck or in "
        "visible dock area. If forced to enter: phone visibly recording "
        "audio (announce: 'recording for dispatcher'). Refuse signature "
        "from anyone not on BOL."
    )

    fallback = (
        "IF DIRECT THREAT: depart immediately, signed or not. Dispatcher "
        "notification with location + facility name. DOT complaint if "
        "post-clock-out follow attempt. Police if assault attempted or "
        "completed. NEVER accept the 'park around back overnight' offer "
        "from a stranger at a small facility."
    )

    gaps = [
        "is facility on a known carrier blacklist?",
        "any prior reports from other drivers about this site?",
        "is paperwork legitimate (BOL matches dispatcher record)?",
        "is the hostile party employee, customer, or unidentified?",
        "any escape route blocked (gate locked, trailer blocked in)?",
    ]

    # Deterrent only if escalating to physical threat
    deterrent_call = None
    if len(isolation_indicators) >= 2:
        deterrent_call = {
            "species": "unknown",
            "distance_ft": None,
            "behavior_keywords": ["approach"],
            "audio_available": True,
            "operator_override_db": 95.0,
        }

    return DecisionOutput(
        emergency_class="human_hostile_encounter",
        emergency_type="delivery_site_hostility",
        constraints=constraints,
        decision=decision,
        fallback=fallback,
        information_gaps=gaps,
        deterrent_call=deterrent_call,
    )


# ---------------------------------------------------------------------------
# 5e: POST-INCIDENT RESPONSE
# ---------------------------------------------------------------------------

def _post_incident_response(description: str, loc: str,
                             st: Dict) -> DecisionOutput:
    injury = any(k in description.lower()
                 for k in ["hurt", "injured", "bleeding", "pain",
                           "hit me", "struck", "bruise"])
    contact_completed = any(k in description.lower()
                             for k in ["attacked", "assaulted", "hit me",
                                       "grabbed", "touched", "forced"])
    comms = st.get("comms_available", True)

    constraints: List[ConstraintLine] = [
        ConstraintLine("PHYSICAL INJURY",
                       "YES" if injury else "no",
                       status="RED" if injury else "GREEN"),
        ConstraintLine("CONTACT COMPLETED",
                       "YES" if contact_completed else "no",
                       status="RED" if contact_completed else "GREEN"),
        ConstraintLine("COMMS",
                       "available" if comms else "DOWN",
                       status="GREEN" if comms else "RED"),
        ConstraintLine("LOCATION SAFE NOW",
                       "verify before treating injury", status="GAP"),
    ]

    if injury:
        decision = (
            "1. SAFE LOCATION FIRST (lit, witnessed, lockable). "
            "2. ASSESS INJURY (visible bleeding, breathing, consciousness). "
            "3. 911 IF SEVERE OR UNSURE. "
            "4. DO NOT WASH/CHANGE if assault was sexual (evidence). "
            "5. NEAREST ER (911 can give address). "
            "6. DISPATCHER notification after medical secured."
        )
    elif contact_completed:
        decision = (
            "1. SAFE LOCATION (drive to lit, witnessed, lockable). "
            "2. DOCUMENT immediately (voice memo: time, location, "
            "subject description, vehicle, what happened, in your own "
            "words). "
            "3. PRESERVE physical evidence if any (clothing, items). "
            "4. CALL LE from safe location (911 or non-emergency). "
            "5. DISPATCHER notification. "
            "6. Consider medical eval even without visible injury "
            "(adrenaline masks)."
        )
    else:
        decision = (
            "1. RELOCATE if not yet safe. "
            "2. DOCUMENT (voice memo with timestamp, description, "
            "vehicle plate, witnesses, anything noticed). "
            "3. REPORT to dispatcher; consider LE non-emergency line. "
            "4. ROUTE ALTERATION: do not repeat the same stop on this "
            "trip. Flag the location for future avoidance."
        )

    fallback = (
        "If any single step blocked, drop down to next-most-protective: "
        "safety > documentation > reporting. Documentation can wait; "
        "physical safety cannot. Do not return to scene to retrieve "
        "items unless under LE escort."
    )

    gaps = [
        "current location safe to stop and document?",
        "any witnesses to interview / get contact info from?",
        "dashcam footage retrievable (do not overwrite)?",
        "carrier policy on incident reporting timeline?",
        "any photos taken (subject, vehicle, plate) - safely stored?",
    ]

    return DecisionOutput(
        emergency_class="human_hostile_encounter",
        emergency_type="post_incident_response",
        constraints=constraints,
        decision=decision,
        fallback=fallback,
        information_gaps=gaps,
        deterrent_call=None,
    )


# ---------------------------------------------------------------------------
# Voice output formatter
# ---------------------------------------------------------------------------

def format_for_voice(out: DecisionOutput) -> str:
    lines = [f"{out.emergency_class.upper()}. {out.emergency_type.upper()}."]
    for c in out.constraints:
        prefix = f"{c.status}. " if c.status and c.status != "INFO" else ""
        if c.threshold:
            lines.append(f"{prefix}{c.label}: {c.value}, {c.threshold}.")
        else:
            lines.append(f"{prefix}{c.label}: {c.value}.")
    lines.append(f"DECISION: {out.decision}")
    if out.fallback:
        lines.append(f"FALLBACK: {out.fallback}")
    if out.deterrent_call:
        lines.append(
            f"DETERRENT: audio max {out.deterrent_call.get('operator_override_db', 90):.0f} dB, "
            f"chaotic broadband, optical strobe."
        )
    if out.information_gaps:
        lines.append("GAPS:")
        for g in out.information_gaps:
            lines.append(f"  - {g}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== 5a: PREDATORY APPROACH at unlit fuel stop, no witnesses ===\n")
    out = human_hostile_encounter_tree(
        description="man loitering, watching me at fuel pump",
        location_context="fuel_stop",
        operator_state={
            "in_cab": False, "engine_running": False,
            "doors_locked": False, "witnesses_present": False,
            "daylight": False, "comms_available": True,
        },
    )
    print(format_for_voice(out))

    print("\n=== 5b: FREIGHT JACKING vehicle blocking remote road ===\n")
    out = human_hostile_encounter_tree(
        description="two trucks stopped blocking road ahead",
        location_context="road",
        operator_state={
            "engine_running": True, "doors_locked": True,
            "trailer_loaded": True, "comms_available": False,
        },
    )
    print(format_for_voice(out))

    print("\n=== 5c: IN-CAB compromise, knocking at 2 AM ===\n")
    out = human_hostile_encounter_tree(
        description="knocking on cab window, claims emergency",
        location_context="rest_stop",
        operator_state={
            "in_cab": True, "engine_running": False,
            "doors_locked": True, "daylight": False,
            "comms_available": True,
        },
    )
    print(format_for_voice(out))

    print("\n=== 5d: DELIVERY site, after-hours, alone with worker ===\n")
    out = human_hostile_encounter_tree(
        description="receiver alone, after hours, asking me to come inside",
        location_context="delivery",
        operator_state={
            "witnesses_present": False, "daylight": False,
            "comms_available": True,
        },
    )
    print(format_for_voice(out))

    print("\n=== 5e: POST-INCIDENT, contact made, no visible injury ===\n")
    out = human_hostile_encounter_tree(
        description="he grabbed me, I got away to the cab",
        location_context="rest_stop",
        operator_state={"comms_available": True},
    )
    print(format_for_voice(out))

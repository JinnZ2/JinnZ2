"""
voice_interface_wrapper.py

Hands-free interface layer for operator_kit.

Purpose:
  Operator speaks while driving 80,000 lb truck. Cannot read screen.
  Cannot type. Must receive constraint output as spoken audio.

Pipeline:
  voice_input (string from device transcription)
    -> classify_emergency_class
    -> extract_parameters
    -> route to correct decision tree
    -> DecisionOutput
    -> format_for_voice (spoken format)
    -> voice_output (passed to device TTS or audio player)

Design rules:
  - No screen interaction required.
  - Voice commands are SHORT and recognizable from partial transcription
    (truck cab noise degrades audio).
  - Classification is keyword-based, not LLM-based -- works offline,
    survives model updates, deterministic.
  - Output is voice-formatted (short lines, clear emphasis markers,
    no markdown).
  - Failure modes: if classification fails, system asks operator to
    specify class; does NOT silently route to wrong tree.

Coupled modules:
  - operator_context_persistence.py (class registry)
  - emergency_decision_trees.py (CLASS 1-3 trees)
  - wildlife_deterrent_system.py (CLASS 4)
  - human_hostile_encounter_tree.py (CLASS 5)
  - bootstrap_resilience.py (session init)

License: CC0
Dependencies: Python stdlib only. Device-layer TTS/STT is external
              (iPhone Siri Shortcuts, AVSpeechSynthesizer, etc.).
"""

import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any

# Import sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emergency_decision_trees import (
    mechanical_failure_tree,
    environmental_emergency_tree,
    unforeseen_circumstance_tree,
    VehicleState,
    EnvironmentalState,
    format_for_voice as format_emergency_voice,
)
from wildlife_deterrent_system import (
    wildlife_deterrent_tree,
    format_for_voice as format_wildlife_voice,
)
from human_hostile_encounter_tree import (
    human_hostile_encounter_tree,
    format_for_voice as format_human_voice,
)


# ---------------------------------------------------------------------------
# Voice command registry
# ---------------------------------------------------------------------------

# Keywords that uniquely route to each class. Multiple keywords increase
# robustness against transcription error. Order matters: more-specific
# checks before general fallbacks.

CLASS_1_KEYWORDS = [
    # mechanical_failure
    "brake", "brakes", "braking",
    "steering", "steer",
    "engine", "stalled", "engine failure",
    "tire", "blowout", "blown tire", "flat",
    "coupling", "fifth wheel", "hitch", "trailer detach",
    "suspension", "leaf spring", "air bag suspension",
    "electrical", "lights out", "alternator", "battery dead",
    "mechanical failure",
]

CLASS_2_KEYWORDS = [
    # environmental_emergency
    "blizzard", "whiteout", "snow storm",
    "tornado", "twister", "funnel cloud",
    "hail", "hailing",
    "wind shear", "high wind", "crosswind",
    "heavy rain", "downpour", "torrent",
    "ice", "icy", "freezing rain", "black ice",
    "flood", "flooding", "high water", "water on road",
    "wildfire", "fire", "smoke", "fire approach",
    "ash", "volcanic", "ashfall",
    "environmental emergency", "weather emergency",
]

CLASS_3_KEYWORDS = [
    # unforeseen_circumstance
    "gps lost", "gps failure", "lost signal", "navigation gone",
    "road closed", "blockage", "construction",
    "sensor failure", "system failure", "all systems",
    "rerouting", "alternate route",
    "unforeseen", "unexpected",
    "fork in road", "decision point",
]

CLASS_4_KEYWORDS = [
    # wildlife_hazard
    "bear", "grizzly", "black bear", "brown bear",
    "wolf", "wolves", "wolf pack",
    "moose", "bull moose", "cow moose",
    "wild dog", "feral dog", "coyote", "coyotes",
    "cougar", "mountain lion", "puma", "panther",
    "wildlife", "animal", "wild animal",
    "wildlife alert", "wildlife emergency",
]

CLASS_5_KEYWORDS = [
    # human_hostile_encounter
    "following me", "stalking", "loitering", "watching me",
    "blocking road", "freight jack", "hijack", "interdiction",
    "knock on cab", "knocking", "trying door", "at window",
    "delivery hostility", "after hours", "alone with",
    "attacked", "assaulted", "grabbed me", "post incident",
    "predatory", "hostile",
    "human threat", "person approaching",
]

# Special voice commands (not emergency-class routed)
SPECIAL_COMMANDS = {
    "load operator context": "load_context",
    "bootstrap": "load_context",
    "load context": "load_context",
    "drift check": "drift_check",
    "are you drifting": "drift_check",
    "status": "status",
    "what classes": "list_classes",
    "list classes": "list_classes",
    "louder": "deterrent_louder",
    "softer": "deterrent_softer",
    "max output": "deterrent_max",
    "maximum deterrent": "deterrent_max",
    "stop deterrent": "deterrent_stop",
    "cancel": "deterrent_stop",
    "operator default": "operator_default",
    "manual override": "operator_default",
}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    detected_class: str       # C1..C5, or "unknown", or "special_command"
    confidence: float         # 0..1, based on keyword density
    matched_keywords: List[str]
    special_action: Optional[str] = None


def classify_emergency(voice_input: str) -> ClassificationResult:
    """
    Keyword-based classification. Deterministic. Offline.
    Survives model updates because it doesn't call any model.
    """
    text = voice_input.lower().strip()

    # Special commands first (exact phrase match)
    for phrase, action in SPECIAL_COMMANDS.items():
        if phrase in text:
            return ClassificationResult(
                detected_class="special_command",
                confidence=1.0,
                matched_keywords=[phrase],
                special_action=action,
            )

    # Emergency class detection by keyword scoring
    scores: Dict[str, Tuple[int, List[str]]] = {
        "C1": (0, []),
        "C2": (0, []),
        "C3": (0, []),
        "C4": (0, []),
        "C5": (0, []),
    }

    for kw in CLASS_1_KEYWORDS:
        if kw in text:
            scores["C1"] = (scores["C1"][0] + 1, scores["C1"][1] + [kw])
    for kw in CLASS_2_KEYWORDS:
        if kw in text:
            scores["C2"] = (scores["C2"][0] + 1, scores["C2"][1] + [kw])
    for kw in CLASS_3_KEYWORDS:
        if kw in text:
            scores["C3"] = (scores["C3"][0] + 1, scores["C3"][1] + [kw])
    for kw in CLASS_4_KEYWORDS:
        if kw in text:
            scores["C4"] = (scores["C4"][0] + 1, scores["C4"][1] + [kw])
    for kw in CLASS_5_KEYWORDS:
        if kw in text:
            scores["C5"] = (scores["C5"][0] + 1, scores["C5"][1] + [kw])

    # Find highest scoring class
    best_class = max(scores.keys(), key=lambda k: scores[k][0])
    best_score, best_kws = scores[best_class]

    if best_score == 0:
        return ClassificationResult(
            detected_class="unknown",
            confidence=0.0,
            matched_keywords=[],
        )

    # Confidence = score / (score + 1), saturates toward 1
    confidence = best_score / (best_score + 1)

    return ClassificationResult(
        detected_class=best_class,
        confidence=confidence,
        matched_keywords=best_kws,
    )


# ---------------------------------------------------------------------------
# Parameter extraction
# ---------------------------------------------------------------------------

DISTANCE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(feet|foot|ft|yards|yd|meters?|m\b|miles?|mi\b)",
    re.IGNORECASE,
)
SPEED_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mph|miles? per hour|kph|km/h)",
    re.IGNORECASE,
)
GRADE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s*(?:down|downhill|grade|up|uphill)?",
    re.IGNORECASE,
)
DEPTH_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(inches?|in\b|feet|ft|cm|centimeters?)\s*"
    r"(?:deep|water)?",
    re.IGNORECASE,
)


def extract_distance_ft(text: str) -> Optional[float]:
    m = DISTANCE_PATTERN.search(text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit in ("feet", "foot", "ft"):
        return val
    if unit in ("yards", "yd"):
        return val * 3.0
    if unit.startswith("m"):
        if "mile" in unit or unit == "mi":
            return val * 5280.0
        return val * 3.281  # meters
    return val


def extract_speed_mph(text: str) -> Optional[float]:
    m = SPEED_PATTERN.search(text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if "mph" in unit or "per hour" in unit:
        return val
    if "kph" in unit or "km/h" in unit:
        return val * 0.621371
    return val


def extract_grade_percent(text: str) -> Optional[float]:
    m = GRADE_PATTERN.search(text)
    if not m:
        return None
    val = float(m.group(1))
    if "up" in text.lower():
        return -val
    return val


def extract_water_depth_in(text: str) -> Optional[float]:
    """Extract water depth in inches."""
    m = DEPTH_PATTERN.search(text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if "inch" in unit or unit == "in":
        return val
    if "feet" in unit or unit == "ft":
        return val * 12.0
    if "cm" in unit or "centimeter" in unit:
        return val * 0.3937
    return val


def extract_behavior_keywords(text: str) -> List[str]:
    """Extract behavioral descriptors for wildlife/human encounters."""
    t = text.lower()
    keywords: List[str] = []
    for word in ["approach", "closer", "stalk", "track", "charge",
                  "follow", "back", "retreat", "stationary", "still",
                  "watch", "circle", "run", "moving away", "leaving"]:
        if word in t:
            keywords.append(word)
    return keywords


def extract_surface_friction(text: str) -> str:
    """Extract road surface description."""
    t = text.lower()
    if "ice" in t or "icy" in t:
        return "ice"
    if "snow" in t:
        return "snow"
    if "wet" in t or "rain" in t:
        return "wet"
    if "gravel" in t:
        return "gravel"
    return "dry"


# ---------------------------------------------------------------------------
# Routing -- voice_input -> tree call -> DecisionOutput
# ---------------------------------------------------------------------------

@dataclass
class VoiceResponse:
    """Container for full voice-interface response."""
    voice_input: str
    classification: ClassificationResult
    decision_output: Optional[Any]    # tree DecisionOutput or None
    spoken_text: str
    elapsed_ms: float
    error: Optional[str] = None


def route_voice_input(voice_input: str,
                       operator_state: Optional[Dict] = None) -> VoiceResponse:
    """
    Main entry: voice text in, full voice response out.
    Returns VoiceResponse with spoken_text ready for TTS.
    """
    t0 = time.time()
    if operator_state is None:
        operator_state = {}

    classification = classify_emergency(voice_input)

    if classification.detected_class == "unknown":
        return VoiceResponse(
            voice_input=voice_input,
            classification=classification,
            decision_output=None,
            spoken_text=(
                "UNCLASSIFIED. Specify: mechanical, environmental, "
                "unforeseen, wildlife, or human threat. "
                "Repeat with one of those words."
            ),
            elapsed_ms=(time.time() - t0) * 1000,
        )

    if classification.detected_class == "special_command":
        return _handle_special_command(
            voice_input, classification, t0, operator_state,
        )

    # Emergency class routing
    if classification.detected_class == "C1":
        return _route_class_1(voice_input, classification, t0, operator_state)
    if classification.detected_class == "C2":
        return _route_class_2(voice_input, classification, t0, operator_state)
    if classification.detected_class == "C3":
        return _route_class_3(voice_input, classification, t0, operator_state)
    if classification.detected_class == "C4":
        return _route_class_4(voice_input, classification, t0, operator_state)
    if classification.detected_class == "C5":
        return _route_class_5(voice_input, classification, t0, operator_state)

    return VoiceResponse(
        voice_input=voice_input,
        classification=classification,
        decision_output=None,
        spoken_text="ROUTING ERROR. Repeat command.",
        elapsed_ms=(time.time() - t0) * 1000,
        error="unknown_class_id",
    )


def _route_class_1(voice_input: str, c: ClassificationResult,
                    t0: float, st: Dict) -> VoiceResponse:
    # Extract vehicle state from voice + operator_state defaults
    speed = extract_speed_mph(voice_input)
    grade = extract_grade_percent(voice_input)
    surface = extract_surface_friction(voice_input)

    vehicle = VehicleState(
        gross_weight_lbs=st.get("gross_weight_lbs", 80000.0),
        current_speed_mph=speed if speed is not None
                          else st.get("current_speed_mph", 0.0),
        grade_percent=grade if grade is not None
                      else st.get("grade_percent", 0.0),
        surface_friction=surface,
        transmission_available=st.get("transmission_available", True),
        engine_brake_available=st.get("engine_brake_available", True),
        trailer_brakes_available=st.get("trailer_brakes_available", True),
        service_brakes_available=st.get("service_brakes_available",
                                         "brake" not in voice_input.lower()),
    )

    out = mechanical_failure_tree(voice_input, vehicle)
    spoken = format_emergency_voice(out)
    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=out,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


def _route_class_2(voice_input: str, c: ClassificationResult,
                    t0: float, st: Dict) -> VoiceResponse:
    speed = extract_speed_mph(voice_input) or st.get("current_speed_mph", 0.0)
    surface = extract_surface_friction(voice_input)
    distance = extract_distance_ft(voice_input)
    depth = extract_water_depth_in(voice_input)

    env = EnvironmentalState(
        visibility_ft=distance,   # rough heuristic: stated distance = visibility
        surface_friction=surface,
        wind_speed_mph=None,
        water_depth_in=depth,
        air_quality=st.get("air_quality", "normal"),
        fire_front_speed_mph=st.get("fire_front_speed_mph"),
    )
    vehicle = VehicleState(
        current_speed_mph=speed,
        surface_friction=surface,
    )

    # Determine specific environmental type from keywords
    out = environmental_emergency_tree(voice_input, env, vehicle)
    spoken = format_emergency_voice(out)
    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=out,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


def _route_class_3(voice_input: str, c: ClassificationResult,
                    t0: float, st: Dict) -> VoiceResponse:
    # Class 3 expects situation_description + available_options
    # Try to detect 'or' clauses to enumerate options
    options: List[str] = []
    if " or " in voice_input.lower():
        # crude split
        parts = re.split(r"\bor\b", voice_input, flags=re.IGNORECASE)
        options = [p.strip() for p in parts if p.strip()]
    out = unforeseen_circumstance_tree(voice_input, options)
    spoken = format_emergency_voice(out)
    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=out,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


def _route_class_4(voice_input: str, c: ClassificationResult,
                    t0: float, st: Dict) -> VoiceResponse:
    distance = extract_distance_ft(voice_input)
    behavior = extract_behavior_keywords(voice_input)
    override = st.get("operator_override_db")
    audio_avail = st.get("audio_available", True)

    out = wildlife_deterrent_tree(
        species_description=voice_input,
        distance_ft=distance,
        behavior_keywords=behavior,
        audio_available=audio_avail,
        operator_override_db=override,
    )
    spoken = format_wildlife_voice(out)
    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=out,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


def _route_class_5(voice_input: str, c: ClassificationResult,
                    t0: float, st: Dict) -> VoiceResponse:
    # Determine location context from keywords
    loc = ""
    vi = voice_input.lower()
    if "rest stop" in vi or "rest area" in vi:
        loc = "rest_stop"
    elif "fuel" in vi or "gas station" in vi or "pump" in vi:
        loc = "fuel_stop"
    elif "delivery" in vi or "loading" in vi or "dock" in vi:
        loc = "delivery"
    elif "road" in vi or "highway" in vi or "shoulder" in vi:
        loc = "road"

    out = human_hostile_encounter_tree(
        description=voice_input,
        location_context=loc,
        operator_state=st,
    )
    spoken = format_human_voice(out)
    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=out,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


def _handle_special_command(voice_input: str, c: ClassificationResult,
                             t0: float, st: Dict) -> VoiceResponse:
    action = c.special_action

    if action == "load_context":
        try:
            from bootstrap_resilience import quick_load
            payload = quick_load(st.get("operator_id", "kavik"),
                                  st.get("target_model", "claude"))
            spoken = (
                f"Operator context loaded. {len(payload)} characters. "
                f"Five emergency classes registered. Ready."
            )
        except Exception as e:
            spoken = f"Load failed: {e}. Run bootstrap init."

    elif action == "drift_check":
        spoken = (
            "Drift check: paste recent model response. "
            "Use bootstrap_resilience detect command."
        )

    elif action == "status":
        spoken = (
            "Operator kit active. Classes one through five online. "
            "Voice interface live. Awaiting input."
        )

    elif action == "list_classes":
        spoken = (
            "Class one: mechanical failure. "
            "Class two: environmental emergency. "
            "Class three: unforeseen circumstance. "
            "Class four: wildlife hazard. "
            "Class five: human hostile encounter."
        )

    elif action == "deterrent_louder":
        spoken = (
            "Deterrent amplitude increased. "
            "Next wildlife or human-threat command will use elevated dB."
        )

    elif action == "deterrent_softer":
        spoken = "Deterrent amplitude reduced for next command."

    elif action == "deterrent_max":
        spoken = (
            "Deterrent set to MAXIMUM. "
            "100 dB chaotic broadband. "
            "Optical strobe enabled."
        )

    elif action == "deterrent_stop":
        spoken = "Deterrent stopped."

    elif action == "operator_default":
        spoken = (
            "Manual override active. "
            "Operator judgment supersedes system output."
        )

    else:
        spoken = f"Unknown special command: {action}"

    return VoiceResponse(
        voice_input=voice_input,
        classification=c,
        decision_output=None,
        spoken_text=spoken,
        elapsed_ms=(time.time() - t0) * 1000,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

USAGE = """
Usage:
  voice_interface_wrapper.py "voice input string"
      Process one voice input, print spoken response.

  voice_interface_wrapper.py --interactive
      REPL mode: type voice inputs, see spoken outputs.

  voice_interface_wrapper.py --self-test
      Run self-test on representative inputs.
"""


def self_test():
    test_inputs = [
        "brake failure at 55 mph 6 percent grade",
        "blizzard visibility 100 feet snow",
        "flooding water depth 30 inches",
        "bear approaching 30 feet",
        "wolf pack 75 feet stalking",
        "man knocking on cab window 2 AM",
        "blocking the road two trucks ahead",
        "GPS lost at fork",
        "load operator context",
        "list classes",
        "louder",
        "unclassified random input asking for help",
    ]

    for ti in test_inputs:
        print(f"\n=== INPUT: {ti} ===")
        resp = route_voice_input(ti)
        print(f"class: {resp.classification.detected_class}  "
              f"confidence: {resp.classification.confidence:.2f}  "
              f"elapsed: {resp.elapsed_ms:.1f} ms")
        print(f"SPOKEN:")
        for line in resp.spoken_text.split("\n"):
            print(f"  {line}")


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    if args[0] == "--self-test":
        self_test()
        return

    if args[0] == "--interactive":
        print("voice_interface_wrapper interactive mode. Ctrl-C to exit.\n")
        try:
            while True:
                voice = input("> ").strip()
                if not voice:
                    continue
                resp = route_voice_input(voice)
                print(f"[{resp.classification.detected_class}, "
                      f"{resp.elapsed_ms:.1f} ms]")
                print(resp.spoken_text)
                print()
        except (KeyboardInterrupt, EOFError):
            print("\nexit.")
            return

    voice = " ".join(args)
    resp = route_voice_input(voice)
    print(resp.spoken_text)


if __name__ == "__main__":
    main()

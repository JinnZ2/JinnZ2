"""
wildlife_deterrent_system.py

Active deterrent system for wildlife emergencies.

Design rules:
  - NOT a recognition/classification system. Operator knows wildlife
    behavior. System provides ACTIVE DETERRENT output.
  - Acoustic + optical emission, scaled to operator-reported distance.
  - iPhone 14 audio constraints baked in (~100 dB SPL max, ~200-18kHz).
  - Where research data exists, profiles use it. Where it does not,
    gap declarations are emitted with the profile (no fabrication).
  - Harm hierarchy: wildlife contact > operator hearing damage.
    Maximum output mode is always available when operator commands it.
  - Fallback chain: targeted audio -> chaotic audio -> optical strobe
    -> operator default response.

Coupled modules:
  - operator_context_persistence.py (CLASS 4: wildlife_hazard)
  - emergency_decision_trees.py (DecisionOutput, ConstraintLine, format_for_voice)

License: CC0
Dependencies: Python stdlib only (math, dataclasses, json, time, os).
              Audio output requires platform-specific player at deployment
              (system supplies parameters; deployment layer plays the file
              or synthesizes the tone). Synthesis helpers use stdlib `wave`
              and `struct` only.
"""

import math
import os
import struct
import wave
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Output schema (mirrors emergency_decision_trees)
# ---------------------------------------------------------------------------

@dataclass
class ConstraintLine:
    label: str
    value: str
    threshold: str = ""
    status: str = ""    # GREEN | YELLOW | RED | INFO | GAP


@dataclass
class DeterrentOutput:
    """One step of deterrent operation. Spoken or displayed."""
    species: str
    distance_ft: Optional[float]
    threat_level: str                  # ESCALATING | STABLE | RECEDING | UNKNOWN
    audio_active: bool
    audio_mode: str                    # targeted | chaotic | off
    audio_amplitude_db: float          # estimated output dB at source
    audio_profile_id: str              # which profile is loaded
    optical_active: bool
    optical_mode: str                  # off | continuous | strobe_hz
    constraints: List[ConstraintLine]
    recommendation: str                # one short directive
    fallback: str                      # one alternative if primary fails
    gaps: List[str] = field(default_factory=list)
    operator_default: str = ""         # what operator does if all tech fails


# ---------------------------------------------------------------------------
# iPhone 14 device limits
# ---------------------------------------------------------------------------

IPHONE_14_AUDIO = {
    "max_spl_db_at_1m": 100.0,         # speaker driver practical limit
    "usable_freq_min_hz": 200.0,        # below this, driver excursion limits
    "usable_freq_max_hz": 18000.0,      # above this, output rolls off
    "flashlight_max_lumen": 60.0,       # LED torch approximate
    "strobe_freq_max_hz": 10.0,         # iOS torch strobe practical
}

# Distance attenuation: inverse-square law for free-field point source.
# SPL drops 6 dB per doubling of distance from 1 m reference.
def attenuated_db_at_distance(spl_at_1m_db: float, distance_ft: float) -> float:
    if distance_ft <= 0:
        return spl_at_1m_db
    distance_m = max(distance_ft * 0.3048, 0.1)
    # 6 dB per doubling -> 20 * log10(distance_m / 1m) reduction
    return spl_at_1m_db - 20.0 * math.log10(distance_m / 1.0)


# ---------------------------------------------------------------------------
# Species profiles
#
# Each profile encodes:
#   - hearing range (Hz)
#   - deterrent strategy with explicit research-backing or gap declaration
#   - amplitude curve as function of distance
#   - pulse pattern (continuous, pulsed_slow, pulsed_fast, sweep)
#   - habituation risk
#
# All numbers tagged with status:
#   - VALIDATED: published research supports it
#   - INFERRED:  reasonable extrapolation from related data; flagged
#   - GAP:       no data; operator must override based on field experience
# ---------------------------------------------------------------------------

@dataclass
class SpeciesProfile:
    species_id: str
    common_names: List[str]
    hearing_range_hz: Tuple[float, float]
    hearing_evidence: str              # VALIDATED | INFERRED | GAP
    deterrent_band_hz: Tuple[float, float]
    deterrent_band_evidence: str
    pulse_pattern: str                 # continuous | pulsed_slow | pulsed_fast | sweep | random
    pulse_evidence: str
    habituation_risk: str              # LOW | MEDIUM | HIGH
    max_safe_spl_db_human_proximity: float
    notes: str
    gaps: List[str] = field(default_factory=list)


# Hearing-range citations live in module docstring + gap declarations below.
# Profiles use the iPhone-usable band intersection with target species
# hearing/deterrent band (since infra/ultrasound are not deliverable here).

PROFILE_BEAR = SpeciesProfile(
    species_id="bear",
    common_names=["black bear", "grizzly bear", "brown bear"],
    hearing_range_hz=(16.0, 20000.0),
    hearing_evidence="VALIDATED",       # multiple sources including McNamee
    deterrent_band_hz=(500.0, 4000.0),  # broadband startle, iPhone-deliverable
    deterrent_band_evidence="INFERRED",
    pulse_pattern="sweep",              # frequency sweep + rapid alternation
    pulse_evidence="INFERRED",          # Wildlabs 2025 hypothesis, not validated
    habituation_risk="HIGH",
    max_safe_spl_db_human_proximity=80.0,
    notes="Polar bear ultrasonic study (1970s): 69% repelled, but 15/74 "
          "INVESTIGATED the sound. Air horns produce startle. Habituation "
          "to constant noise documented. iPhone cannot deliver true ultra/"
          "infrasound; deliver broadband sweep instead. Operator override "
          "to MAX is always permitted; harm hierarchy = bear > hearing.",
    gaps=[
        "DG-W-001: no controlled bear study with per-frequency SPL data",
        "DG-W-004: dynamic frequency modulation effectiveness is current "
                  "research hypothesis (Wildlabs Nov 2025), not validated",
        "DG-W-005: bear habituation curve per intensity not quantified",
    ],
)

PROFILE_WOLF = SpeciesProfile(
    species_id="wolf",
    common_names=["gray wolf", "timber wolf", "wolf pack"],
    hearing_range_hz=(45.0, 80000.0),
    hearing_evidence="VALIDATED",       # misfit animals + Animals Around Globe
    deterrent_band_hz=(8000.0, 18000.0),
    deterrent_band_evidence="INFERRED",
    pulse_pattern="sweep",
    pulse_evidence="GAP",
    habituation_risk="MEDIUM",
    max_safe_spl_db_human_proximity=80.0,
    notes="Wolf vocal range 359-1700 Hz (howl-whimper). Hearing extends to "
          "80 kHz. Strategy: high-frequency emission disrupts pack "
          "coordination (inferred, NOT field-tested). iPhone max 18 kHz "
          "delivers only audible portion. Pack communication operates "
          "across distance; deterrent must interrupt pack-state, not "
          "just individual.",
    gaps=[
        "DG-W-002: no field-tested wolf pack acoustic deterrent data",
        "high-frequency disruption is INFERENCE from hearing range, "
            "not from measured pack-response data",
    ],
)

PROFILE_MOOSE = SpeciesProfile(
    species_id="moose",
    common_names=["moose", "bull moose", "cow moose"],
    hearing_range_hz=(50.0, 20000.0),   # ungulate proxy; precise unknown
    hearing_evidence="INFERRED",
    deterrent_band_hz=(200.0, 1500.0),  # low frequency, territorial mimic
    deterrent_band_evidence="GAP",
    pulse_pattern="pulsed_slow",
    pulse_evidence="GAP",
    habituation_risk="MEDIUM",
    max_safe_spl_db_human_proximity=80.0,
    notes="Moose communicate via low-frequency calls; bulls lowest, "
          "calves highest. Deterrent strategy: low-frequency pulse "
          "may register as rival bull challenge. NOT VALIDATED. "
          "Moose are stressed = unpredictable; deterrent may escalate "
          "rather than retreat. Operator judgment primary.",
    gaps=[
        "DG-W-003: no published moose acoustic deterrent study found",
        "low-frequency territorial mimic is INFERENCE, untested",
        "moose response to startling sound may include CHARGE not flight",
    ],
)

PROFILE_WILD_DOG = SpeciesProfile(
    species_id="wild_dog",
    common_names=["feral dog", "wild dog pack", "coyote"],
    hearing_range_hz=(50.0, 46000.0),
    hearing_evidence="VALIDATED",       # coyote data, applicable to feral dogs
    deterrent_band_hz=(2000.0, 18000.0),
    deterrent_band_evidence="INFERRED",
    pulse_pattern="pulsed_fast",
    pulse_evidence="INFERRED",
    habituation_risk="MEDIUM",
    max_safe_spl_db_human_proximity=80.0,
    notes="Canine hearing range supports high-frequency deterrent. "
          "Pack coordination disrupted by rapid pulse. Feral dogs may "
          "be hunger-driven and more persistent than wild canids; "
          "deterrent must be aggressive (high amplitude, varied pattern).",
    gaps=[
        "no feral-dog-specific deterrent research found",
        "behavior differs from wolves (less coordinated, more variable)",
    ],
)

PROFILE_COUGAR = SpeciesProfile(
    species_id="cougar",
    common_names=["mountain lion", "cougar", "puma", "catamount"],
    hearing_range_hz=(45.0, 65000.0),
    hearing_evidence="INFERRED",        # feline proxy
    deterrent_band_hz=(200.0, 18000.0), # broadband; iPhone full range
    deterrent_band_evidence="GAP",
    pulse_pattern="random",
    pulse_evidence="INFERRED",
    habituation_risk="LOW",
    max_safe_spl_db_human_proximity=80.0,
    notes="Solitary ambush predator. May be deterred by uncertainty + "
          "size-projection. Cougar growl playback (<250 Hz) reportedly "
          "deters via territorial-challenge interpretation; "
          "iPhone-deliverable. Best strategy: broadband chaotic + "
          "operator appearing large.",
    gaps=[
        "cougar deterrent data is anecdotal, not controlled studies",
        "cougar attack frequency is low; sample size limits research",
    ],
)

PROFILE_UNKNOWN = SpeciesProfile(
    species_id="unknown",
    common_names=["unidentified", "abnormal_behavior"],
    hearing_range_hz=(200.0, 18000.0),  # iPhone delivery range only
    hearing_evidence="GAP",
    deterrent_band_hz=(200.0, 18000.0),
    deterrent_band_evidence="GAP",
    pulse_pattern="random",
    pulse_evidence="GAP",
    habituation_risk="MEDIUM",
    max_safe_spl_db_human_proximity=80.0,
    notes="Generic broadband chaotic emission. Use when species unknown "
          "or abnormal-behavior animal does not match standard profile. "
          "Maximum-disruption design.",
    gaps=[
        "no species-specific data; chaotic broadband is fallback strategy",
    ],
)


PROFILES: Dict[str, SpeciesProfile] = {
    "bear": PROFILE_BEAR,
    "wolf": PROFILE_WOLF,
    "moose": PROFILE_MOOSE,
    "wild_dog": PROFILE_WILD_DOG,
    "cougar": PROFILE_COUGAR,
    "unknown": PROFILE_UNKNOWN,
}


# ---------------------------------------------------------------------------
# Species selection from operator description
# ---------------------------------------------------------------------------

def resolve_species(description: str) -> SpeciesProfile:
    """Map operator voice text -> species profile. Default = unknown."""
    d = description.lower()
    if "bear" in d:
        return PROFILE_BEAR
    if "wolf" in d or "wolves" in d:
        return PROFILE_WOLF
    if "moose" in d:
        return PROFILE_MOOSE
    if "coyote" in d or "wild dog" in d or "feral" in d or "pack of dog" in d:
        return PROFILE_WILD_DOG
    if "cougar" in d or "mountain lion" in d or "puma" in d or "panther" in d:
        return PROFILE_COUGAR
    return PROFILE_UNKNOWN


# ---------------------------------------------------------------------------
# Amplitude curve (distance -> requested SPL at source)
# ---------------------------------------------------------------------------

# Reference points (distance_ft, source_spl_db).
# These are TARGET output at the device, not received SPL at animal.
# Curve: closer animal -> higher source SPL, capped at device max.
BEAR_DISTANCE_CURVE = [
    (100.0, 75.0),
    (50.0, 85.0),
    (25.0, 95.0),
    (10.0, 100.0),
    (5.0, 100.0),
]
WOLF_DISTANCE_CURVE = [
    (150.0, 80.0),
    (75.0, 90.0),
    (30.0, 95.0),
    (15.0, 100.0),
    (5.0, 100.0),
]
MOOSE_DISTANCE_CURVE = [
    (100.0, 80.0),
    (50.0, 90.0),
    (25.0, 95.0),
    (10.0, 100.0),
]
WILD_DOG_DISTANCE_CURVE = [
    (80.0, 80.0),
    (40.0, 90.0),
    (20.0, 95.0),
    (10.0, 100.0),
]
COUGAR_DISTANCE_CURVE = [
    (100.0, 80.0),
    (50.0, 90.0),
    (25.0, 95.0),
    (10.0, 100.0),
]
UNKNOWN_DISTANCE_CURVE = [
    (100.0, 85.0),
    (50.0, 95.0),
    (25.0, 100.0),
    (10.0, 100.0),
]

DISTANCE_CURVES: Dict[str, List[Tuple[float, float]]] = {
    "bear": BEAR_DISTANCE_CURVE,
    "wolf": WOLF_DISTANCE_CURVE,
    "moose": MOOSE_DISTANCE_CURVE,
    "wild_dog": WILD_DOG_DISTANCE_CURVE,
    "cougar": COUGAR_DISTANCE_CURVE,
    "unknown": UNKNOWN_DISTANCE_CURVE,
}


def amplitude_for_distance(profile: SpeciesProfile,
                            distance_ft: Optional[float]) -> float:
    """
    Linear interpolation across the profile's distance/dB curve.
    Caps at iPhone 14 max output. If distance unknown, returns
    midpoint of safe range as start; operator escalates manually.
    """
    if distance_ft is None:
        return 85.0  # unknown distance: start mid-range, operator overrides

    curve = DISTANCE_CURVES.get(profile.species_id, UNKNOWN_DISTANCE_CURVE)
    # Sort by distance descending so first entry is farthest
    curve_sorted = sorted(curve, key=lambda x: -x[0])

    if distance_ft >= curve_sorted[0][0]:
        db = curve_sorted[0][1]
    elif distance_ft <= curve_sorted[-1][0]:
        db = curve_sorted[-1][1]
    else:
        # interpolate between bracketing points
        db = curve_sorted[-1][1]
        for i in range(len(curve_sorted) - 1):
            d_hi, db_hi = curve_sorted[i]
            d_lo, db_lo = curve_sorted[i + 1]
            if d_lo <= distance_ft <= d_hi:
                # interpolate
                frac = (d_hi - distance_ft) / (d_hi - d_lo)
                db = db_hi + frac * (db_lo - db_hi)
                break

    return min(db, IPHONE_14_AUDIO["max_spl_db_at_1m"])


# ---------------------------------------------------------------------------
# Threat-level classification (distance + reported behavior)
# ---------------------------------------------------------------------------

def classify_threat(profile: SpeciesProfile,
                     distance_ft: Optional[float],
                     behavior_keywords: List[str]) -> str:
    """
    Classify threat level. Operator's own judgment overrides.
    Returns one of: ESCALATING | STABLE | RECEDING | UNKNOWN
    """
    if not behavior_keywords:
        return "UNKNOWN"
    bk = " ".join(behavior_keywords).lower()
    if any(w in bk for w in ["closer", "approach", "charge", "run", "stalk", "track"]):
        return "ESCALATING"
    if any(w in bk for w in ["back", "retreat", "leaving", "farther", "moving away"]):
        return "RECEDING"
    if any(w in bk for w in ["stop", "stationary", "watch", "still", "hold"]):
        return "STABLE"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Audio synthesis (stdlib only) -- generate WAV for offline play
# ---------------------------------------------------------------------------

SAMPLE_RATE = 22050
AMPLITUDE_FRAC = 0.9  # 90% of int16 range


def _write_wav(filename: str, samples: List[float]) -> str:
    """Write float samples in [-1,1] to 16-bit mono WAV."""
    with wave.open(filename, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            w.writeframesraw(struct.pack("<h", int(s * 32767 * AMPLITUDE_FRAC)))
    return filename


def synthesize_sweep(freq_lo: float, freq_hi: float,
                      duration_sec: float = 1.0,
                      pulse_count: int = 4,
                      filename: str = "deterrent_sweep.wav") -> str:
    """
    Frequency sweep, pulsed. Defeats habituation per Wildlabs hypothesis.
    Pulses on/off within duration. Returns WAV path.
    """
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    pulse_len = n_samples // pulse_count
    half_pulse = pulse_len // 2

    for i in range(n_samples):
        in_pulse = (i % pulse_len) < half_pulse
        if not in_pulse:
            samples.append(0.0)
            continue
        # frequency sweep within each pulse
        t = (i % pulse_len) / pulse_len
        freq = freq_lo + (freq_hi - freq_lo) * t
        samples.append(math.sin(2 * math.pi * freq * (i / SAMPLE_RATE)))

    return _write_wav(filename, samples)


def synthesize_pulsed(freq_hz: float, duration_sec: float = 1.0,
                      pulse_hz: float = 4.0,
                      filename: str = "deterrent_pulsed.wav") -> str:
    """Single-frequency tone, pulsed at given rate."""
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # pulse envelope
        envelope = 1.0 if (math.sin(2 * math.pi * pulse_hz * t) > 0) else 0.0
        samples.append(envelope * math.sin(2 * math.pi * freq_hz * t))
    return _write_wav(filename, samples)


def synthesize_chaotic(freq_lo: float, freq_hi: float,
                        duration_sec: float = 1.0,
                        filename: str = "deterrent_chaotic.wav") -> str:
    """
    Rapid random frequency + amplitude changes. Maximum disruption.
    Used as fallback when targeted profile is uncertain.
    """
    import random
    n_samples = int(SAMPLE_RATE * duration_sec)
    samples = []
    seg_len = SAMPLE_RATE // 20  # 20 segments per second
    current_freq = freq_lo
    current_amp = 1.0
    for i in range(n_samples):
        if i % seg_len == 0:
            current_freq = random.uniform(freq_lo, freq_hi)
            current_amp = random.uniform(0.3, 1.0)
        t = i / SAMPLE_RATE
        samples.append(current_amp * math.sin(2 * math.pi * current_freq * t))
    return _write_wav(filename, samples)


# ---------------------------------------------------------------------------
# Pre-generate profile audio files (call once during setup)
# ---------------------------------------------------------------------------

def pregenerate_all_profile_audio(out_dir: str = "deterrent_audio") -> Dict[str, str]:
    """
    Pre-generate WAV files for each species profile.
    Returns dict mapping species_id -> path. Run at setup time, not
    in field; field playback uses cached files for lowest latency.
    """
    os.makedirs(out_dir, exist_ok=True)
    out: Dict[str, str] = {}
    for sid, profile in PROFILES.items():
        lo, hi = profile.deterrent_band_hz
        # clamp to iPhone-deliverable band
        lo = max(lo, IPHONE_14_AUDIO["usable_freq_min_hz"])
        hi = min(hi, IPHONE_14_AUDIO["usable_freq_max_hz"])

        if profile.pulse_pattern == "sweep":
            path = os.path.join(out_dir, f"{sid}_sweep.wav")
            synthesize_sweep(lo, hi, duration_sec=2.0, pulse_count=8,
                             filename=path)
        elif profile.pulse_pattern == "pulsed_slow":
            path = os.path.join(out_dir, f"{sid}_pulsed_slow.wav")
            synthesize_pulsed((lo + hi) / 2, duration_sec=2.0, pulse_hz=2.0,
                              filename=path)
        elif profile.pulse_pattern == "pulsed_fast":
            path = os.path.join(out_dir, f"{sid}_pulsed_fast.wav")
            synthesize_pulsed((lo + hi) / 2, duration_sec=2.0, pulse_hz=8.0,
                              filename=path)
        elif profile.pulse_pattern == "random" or profile.pulse_pattern == "chaotic":
            path = os.path.join(out_dir, f"{sid}_chaotic.wav")
            synthesize_chaotic(lo, hi, duration_sec=2.0, filename=path)
        else:
            path = os.path.join(out_dir, f"{sid}_default.wav")
            synthesize_sweep(lo, hi, duration_sec=2.0, pulse_count=4,
                             filename=path)
        out[sid] = path

    # Universal chaotic fallback
    path = os.path.join(out_dir, "fallback_chaotic.wav")
    synthesize_chaotic(IPHONE_14_AUDIO["usable_freq_min_hz"],
                       IPHONE_14_AUDIO["usable_freq_max_hz"],
                       duration_sec=3.0, filename=path)
    out["_fallback_chaotic"] = path

    return out


# ---------------------------------------------------------------------------
# Optical strobe controller (parameters; deployment layer drives flashlight)
# ---------------------------------------------------------------------------

@dataclass
class OpticalCommand:
    mode: str               # off | continuous | strobe
    strobe_hz: float = 0.0  # 0 if not strobing
    duration_sec: float = 0.0  # 0 = until canceled


def optical_for_threat(threat_level: str, audio_available: bool) -> OpticalCommand:
    """
    Optical strobe policy.
    - if audio_available + low threat: optical OFF (preserve battery)
    - if audio_available + escalating: optical STROBE (compound deterrent)
    - if audio_unavailable: optical STROBE always
    - max strobe rate limited by iOS torch capability
    """
    if not audio_available:
        return OpticalCommand(mode="strobe", strobe_hz=8.0)
    if threat_level == "ESCALATING":
        return OpticalCommand(mode="strobe", strobe_hz=8.0)
    if threat_level == "STABLE":
        return OpticalCommand(mode="continuous")
    return OpticalCommand(mode="off")


# ---------------------------------------------------------------------------
# Main entry: process operator report -> DeterrentOutput
# ---------------------------------------------------------------------------

def wildlife_deterrent_tree(species_description: str,
                             distance_ft: Optional[float],
                             behavior_keywords: List[str],
                             audio_available: bool = True,
                             operator_override_db: Optional[float] = None) -> DeterrentOutput:
    """
    Main decision entry. Operator says e.g. 'bear approaching 30 feet'.
    Returns DeterrentOutput with audio + optical parameters to drive.

    audio_available: False if speaker faulty / silenced; system uses optical only.
    operator_override_db: if set, ignore distance curve and use this source dB.
    """
    profile = resolve_species(species_description)
    threat = classify_threat(profile, distance_ft, behavior_keywords)

    if operator_override_db is not None:
        target_db = min(operator_override_db,
                        IPHONE_14_AUDIO["max_spl_db_at_1m"])
    else:
        target_db = amplitude_for_distance(profile, distance_ft)

    # Audio mode selection
    if not audio_available:
        audio_mode = "off"
        target_db = 0.0
    elif profile.species_id == "unknown" or threat == "UNKNOWN":
        audio_mode = "chaotic"
    else:
        audio_mode = "targeted"

    optical = optical_for_threat(threat, audio_available)

    constraints: List[ConstraintLine] = [
        ConstraintLine("SPECIES",
                       profile.common_names[0],
                       threshold=f"hearing {int(profile.hearing_range_hz[0])}"
                                 f"-{int(profile.hearing_range_hz[1])} Hz",
                       status="INFO"),
        ConstraintLine("DISTANCE",
                       f"{distance_ft:.0f} ft" if distance_ft is not None
                       else "UNKNOWN",
                       status="GAP" if distance_ft is None
                       else "RED" if (distance_ft < 20)
                       else "YELLOW" if (distance_ft < 50)
                       else "GREEN"),
        ConstraintLine("THREAT LEVEL", threat,
                       status="RED" if threat == "ESCALATING"
                       else "YELLOW" if threat == "STABLE"
                       else "GREEN" if threat == "RECEDING"
                       else "GAP"),
        ConstraintLine("AUDIO MODE", audio_mode),
        ConstraintLine("TARGET SOURCE DB",
                       f"{target_db:.0f} dB",
                       threshold=f"device max {IPHONE_14_AUDIO['max_spl_db_at_1m']:.0f}"),
    ]

    # Estimated received SPL at animal (for operator awareness)
    if distance_ft is not None and target_db > 0:
        recv_db = attenuated_db_at_distance(target_db, distance_ft)
        constraints.append(ConstraintLine(
            "EST DB AT ANIMAL", f"{recv_db:.0f} dB",
            threshold="60+ dB = noticeable, 80+ dB = aversive",
            status="GREEN" if recv_db >= 80 else "YELLOW" if recv_db >= 60 else "RED",
        ))

    constraints.append(ConstraintLine(
        "OPTICAL", f"{optical.mode}" +
        (f" @ {optical.strobe_hz:.0f}Hz" if optical.strobe_hz > 0 else "")
    ))

    # Recommendation
    if threat == "ESCALATING" and target_db < IPHONE_14_AUDIO["max_spl_db_at_1m"]:
        recommendation = f"INCREASE AMPLITUDE; CURRENT {target_db:.0f} dB"
    elif threat == "ESCALATING":
        recommendation = "MAX OUTPUT; STROBE ACTIVE; PREPARE OPERATOR DEFAULT"
    elif threat == "RECEDING":
        recommendation = "MAINTAIN; DO NOT REDUCE UNTIL CONFIRMED CLEAR"
    elif threat == "STABLE":
        recommendation = "HOLD POSITION; OBSERVE FOR CHANGE"
    else:
        recommendation = "ESTABLISH DISTANCE + BEHAVIOR; ADJUST"

    fallback_chain = (
        "1. INCREASE AMPLITUDE -> "
        "2. SWITCH TO CHAOTIC AUDIO -> "
        "3. ACTIVATE STROBE -> "
        "4. OPERATOR DEFAULT"
    )

    operator_default = ""
    if profile.species_id == "bear":
        operator_default = ("STAND LARGE; LOUD HUMAN VOICE; SLOW BACKAWAY; "
                            "BEAR SPRAY IF AVAILABLE; PLAY DEAD ONLY IF "
                            "GRIZZLY AND CONTACT IMMINENT")
    elif profile.species_id == "wolf":
        operator_default = ("STAND LARGE; MAKE NOISE; SUSTAINED EYE CONTACT; "
                            "BACK AWAY FACING PACK; THROW OBJECTS")
    elif profile.species_id == "moose":
        operator_default = ("PUT TREE OR LARGE OBJECT BETWEEN YOU AND MOOSE; "
                            "RUN AT 90 DEG IF CHARGE; DO NOT CLIMB SMALL TREE")
    elif profile.species_id == "wild_dog":
        operator_default = ("STAND GROUND; LOUD; AVOID RUNNING; "
                            "FACE PACK; ELEVATED GROUND IF POSSIBLE")
    elif profile.species_id == "cougar":
        operator_default = ("DO NOT RUN; APPEAR LARGE; SUSTAINED EYE CONTACT; "
                            "FIGHT BACK IF CONTACT (eyes and face)")
    else:
        operator_default = ("APPEAR LARGE; LOUD; DO NOT RUN; "
                            "BACK AWAY MAINTAINING ORIENTATION")

    return DeterrentOutput(
        species=profile.species_id,
        distance_ft=distance_ft,
        threat_level=threat,
        audio_active=audio_available,
        audio_mode=audio_mode,
        audio_amplitude_db=target_db,
        audio_profile_id=f"{profile.species_id}_{profile.pulse_pattern}",
        optical_active=(optical.mode != "off"),
        optical_mode=optical.mode + (f"@{optical.strobe_hz:.0f}Hz"
                                      if optical.strobe_hz > 0 else ""),
        constraints=constraints,
        recommendation=recommendation,
        fallback=fallback_chain,
        gaps=list(profile.gaps),
        operator_default=operator_default,
    )


# ---------------------------------------------------------------------------
# Voice output formatter
# ---------------------------------------------------------------------------

def format_for_voice(out: DeterrentOutput) -> str:
    """Spoken format. Short. Constraint-primary. No narration."""
    lines = [f"WILDLIFE DETERRENT. {out.species.upper()}."]
    for c in out.constraints:
        prefix = f"{c.status}. " if c.status and c.status != "INFO" else ""
        if c.threshold:
            lines.append(f"{prefix}{c.label}: {c.value}, {c.threshold}.")
        else:
            lines.append(f"{prefix}{c.label}: {c.value}.")
    lines.append(f"AUDIO PROFILE: {out.audio_profile_id}.")
    lines.append(f"OPTICAL: {out.optical_mode}.")
    lines.append(f"RECOMMEND: {out.recommendation}.")
    lines.append(f"FALLBACK CHAIN: {out.fallback}.")
    if out.operator_default:
        lines.append(f"OPERATOR DEFAULT: {out.operator_default}.")
    if out.gaps:
        lines.append("GAPS:")
        for g in out.gaps:
            lines.append(f"  - {g}.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== SELF-TEST: bear approaching 30 ft ===\n")
    out = wildlife_deterrent_tree(
        species_description="bear approaching",
        distance_ft=30,
        behavior_keywords=["closer", "approaching"],
    )
    print(format_for_voice(out))

    print("\n=== SELF-TEST: wolf pack tracking, 75 ft ===\n")
    out = wildlife_deterrent_tree(
        species_description="wolf pack",
        distance_ft=75,
        behavior_keywords=["stalk", "track"],
    )
    print(format_for_voice(out))

    print("\n=== SELF-TEST: moose stationary 50 ft, audio failed ===\n")
    out = wildlife_deterrent_tree(
        species_description="moose",
        distance_ft=50,
        behavior_keywords=["stationary", "watch"],
        audio_available=False,
    )
    print(format_for_voice(out))

    print("\n=== SELF-TEST: unknown abnormal-behavior animal, distance unknown ===\n")
    out = wildlife_deterrent_tree(
        species_description="abnormal_behavior unidentified",
        distance_ft=None,
        behavior_keywords=["approach"],
    )
    print(format_for_voice(out))

    print("\n=== SELF-TEST: operator override to max ===\n")
    out = wildlife_deterrent_tree(
        species_description="bear charging",
        distance_ft=10,
        behavior_keywords=["charge"],
        operator_override_db=100.0,
    )
    print(format_for_voice(out))

    print("\n=== AUDIO FILE PREGENERATION ===\n")
    files = pregenerate_all_profile_audio(out_dir="/tmp/deterrent_audio")
    for sid, path in files.items():
        size = os.path.getsize(path)
        print(f"  {sid:25s} -> {path} ({size} bytes)")

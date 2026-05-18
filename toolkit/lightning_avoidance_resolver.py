# lightning_avoidance_resolver.py
# Real-time lightning threat assessment + vehicle vulnerability + shelter ranking
# CC0 | falsifiable | mobile-queryable | immediate threat detection

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import re

class LightningObservationType(Enum):
    THUNDER_DELAY = "thunder_delay"
    SKY_COLOR = "sky_color"
    HAIR_STANDING = "hair_standing"
    SMELL_OZONE = "smell_ozone"
    VISIBLE_LIGHTNING = "visible_lightning"
    GROUND_VIBRATION = "ground_vibration"
    STATIC_BUILDUP = "static_buildup"
    BAROMETRIC_PRESSURE = "barometric_pressure"

@dataclass
class LightningObservation:
    """Sensory input indicating lightning proximity."""
    observation_type: LightningObservationType
    value: str  # "thunder 5sec after flash", "greenish-black sky", "hair standing"
    confidence: float  # 0–1
    timestamp: Optional[str] = None

@dataclass
class StrikeRiskZone:
    """Geographic + vehicle vulnerability assessment."""
    location_type: str  # "truck_stop_open", "under_tree", "bridge", "culvert", "vehicle"
    strike_probability_percent: float
    injury_probability_if_hit: float
    safe_shelter_nearby: bool
    safe_distance_feet: int
    grounding_quality: str  # "none", "poor", "moderate", "good"

@dataclass
class VehicleVulnerability:
    """Truck-specific lightning risk."""
    vehicle_type: str  # "semi_truck", "pickup", "car"
    cab_occupant_exposure: str  # "extreme", "high", "moderate", "low"
    metal_frame_protection: bool
    tire_grounding: str  # "rubber_isolates", "wet_ground_conducts"
    fuel_tank_ignition_risk: str  # "none", "low", "moderate"
    electronic_damage_risk: str  # How likely EMP disables truck?

class LightningAvoidanceResolver:
    """
    Lightning threat = fastest escalation. Thunder delay ≤ 30sec = extreme danger.
    Strikes can travel laterally up to 10 miles from parent cloud.

    Physics:
      Thunder delay (seconds) / 5 = approximate distance (miles)
      5sec = 1 mile away (strike imminent)
      10sec = 2 miles (prepare to shelter)
      30sec = 6 miles (watch conditions)

    Vehicle paradox: semi truck = tall metal conductor. Inside cab = safer
    (Faraday cage effect). Outside = extreme danger. Truck stop parking =
    worst scenario (isolated tall object in open field).
    """

    def assess_immediate_threat(self, observations: List[LightningObservation],
                               vehicle_state: Dict,
                               location: str) -> Dict:
        """
        Real-time threat assessment. Returns: immediate action in seconds.
        """
        # Parse observations for distance + intensity
        thunder_delay = self._extract_thunder_delay(observations)
        visible_lightning = self._extract_visible_lightning(observations)
        sky_condition = self._extract_sky_condition(observations)

        # Estimate strike distance
        if thunder_delay:
            distance_miles = thunder_delay / 5
            if distance_miles <= 1:
                threat_level = "IMMINENT"
                time_to_strike_seconds = 30  # Conservative estimate
            elif distance_miles <= 2:
                threat_level = "CRITICAL"
                time_to_strike_seconds = 120
            elif distance_miles <= 6:
                threat_level = "HIGH"
                time_to_strike_seconds = 300
            else:
                threat_level = "MODERATE"
                time_to_strike_seconds = 600
        elif visible_lightning:
            threat_level = "IMMINENT"
            time_to_strike_seconds = 30
        else:
            threat_level = "WATCH"
            time_to_strike_seconds = None

        # Vehicle vulnerability assessment
        vehicle_vuln = self._assess_vehicle(vehicle_state)
        location_vuln = self._assess_location(location, vehicle_state)

        # Action recommendation
        action = self._recommend_action(threat_level, vehicle_vuln, location_vuln,
                                       time_to_strike_seconds)

        return {
            "threat_level": threat_level,
            "estimated_distance_miles": distance_miles if thunder_delay else None,
            "time_to_potential_strike_seconds": time_to_strike_seconds,
            "immediate_action": action,
            "vehicle_vulnerability": vehicle_vuln,
            "location_vulnerability": location_vuln,
            "safe_actions_ranked": self._rank_safe_actions(threat_level, location, vehicle_state)
        }

    def _extract_thunder_delay(self, observations: List[LightningObservation]) -> Optional[int]:
        """
        Parse thunder delay (seconds between flash and thunder) from
        observations. Tolerates both spaced ('4 sec after flash') and
        concatenated ('4sec after flash') phrasings.
        """
        for obs in observations:
            if obs.observation_type == LightningObservationType.THUNDER_DELAY:
                match = re.search(r"(\d+)\s*sec", obs.value)
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        continue
        return None

    def _extract_visible_lightning(self, observations: List[LightningObservation]) -> bool:
        """Check if lightning was directly visible."""
        return any(obs.observation_type == LightningObservationType.VISIBLE_LIGHTNING
                  for obs in observations)

    def _extract_sky_condition(self, observations: List[LightningObservation]) -> str:
        """Parse sky color/condition."""
        for obs in observations:
            if obs.observation_type == LightningObservationType.SKY_COLOR:
                return obs.value
        return "unknown"

    def _assess_vehicle(self, vehicle_state: Dict) -> VehicleVulnerability:
        """
        Semi truck paradox:
          - Tall metal structure = lightning attractor
          - Inside cab + metal roof = Faraday cage = relatively safe if grounded
          - Outside truck/on pavement = extreme danger
          - Door handle + person = direct path to ground
        """
        vehicle_type = vehicle_state.get("type", "semi_truck")
        occupant_location = vehicle_state.get("location", "cab")  # "cab", "sleeper", "outside"

        if occupant_location == "outside":
            return VehicleVulnerability(
                vehicle_type=vehicle_type,
                cab_occupant_exposure="extreme",
                metal_frame_protection=False,
                tire_grounding="rubber_isolates",
                fuel_tank_ignition_risk="moderate",
                electronic_damage_risk="high"
            )
        else:  # Inside cab/sleeper
            return VehicleVulnerability(
                vehicle_type=vehicle_type,
                cab_occupant_exposure="low",  # Faraday cage
                metal_frame_protection=True,
                tire_grounding="rubber_isolates",
                fuel_tank_ignition_risk="low",
                electronic_damage_risk="moderate"  # EMP can disable electronics
            )

    def _assess_location(self, location: str, vehicle_state: Dict) -> StrikeRiskZone:
        """
        Evaluate location vulnerability.
        Truck stop open = worst (tall vehicle, isolated, no shelter).
        Under bridge/overhang = better (some protection).
        Dense building = safest.
        """
        location_lower = location.lower()

        if "truck_stop" in location_lower or "parking_lot" in location_lower:
            return StrikeRiskZone(
                location_type="truck_stop_open",
                strike_probability_percent=75,  # Tall isolated object
                injury_probability_if_hit=60,
                safe_shelter_nearby=False,
                safe_distance_feet=300,
                grounding_quality="none"  # Asphalt doesn't ground
            )

        elif "under_tree" in location_lower or "forest" in location_lower:
            return StrikeRiskZone(
                location_type="under_tree",
                strike_probability_percent=85,  # Trees attract strikes
                injury_probability_if_hit=70,
                safe_shelter_nearby=False,
                safe_distance_feet=100,
                grounding_quality="poor"
            )

        elif "bridge" in location_lower or "overpass" in location_lower:
            return StrikeRiskZone(
                location_type="under_bridge",
                strike_probability_percent=40,
                injury_probability_if_hit=20,
                safe_shelter_nearby=True,
                safe_distance_feet=100,
                grounding_quality="moderate"
            )

        elif "culvert" in location_lower or "underpass" in location_lower:
            return StrikeRiskZone(
                location_type="culvert",
                strike_probability_percent=30,
                injury_probability_if_hit=10,
                safe_shelter_nearby=True,
                safe_distance_feet=50,
                grounding_quality="good"
            )

        else:
            return StrikeRiskZone(
                location_type="open_area",
                strike_probability_percent=50,
                injury_probability_if_hit=40,
                safe_shelter_nearby=False,
                safe_distance_feet=200,
                grounding_quality="poor"
            )

    def _recommend_action(self, threat_level: str,
                         vehicle_vuln: VehicleVulnerability,
                         location_vuln: StrikeRiskZone,
                         time_to_strike: Optional[int]) -> str:
        """
        Immediate action based on threat + vulnerability.
        """
        if threat_level == "IMMINENT":
            if vehicle_vuln.cab_occupant_exposure == "extreme":
                return "GET INSIDE CAB IMMEDIATELY. Avoid touching metal. Stay away from door handles. Crouch on seat, feet off floor."
            else:
                return "STAY IN CAB. Don't touch metal frame or door. Feet off pedals if possible. Wait for strike to pass."

        elif threat_level == "CRITICAL":
            if location_vuln.location_type == "truck_stop_open":
                return "MOVE RIG OFF PARKING LOT. Drive to safer location (building, underpass) or park away from isolated tall objects."
            else:
                return "GET TO SHELTER. Move away from open area. Find building or underpass."

        elif threat_level == "HIGH":
            return "MONITOR CLOSELY. Move toward shelter. Avoid open areas, tall objects, trees. If thunder < 10sec, execute CRITICAL action."

        else:  # MODERATE / WATCH
            return "CONTINUE MONITORING. Watch for worsening conditions. Have shelter plan ready."

    def _rank_safe_actions(self, threat_level: str, location: str,
                          vehicle_state: Dict) -> List[Dict]:
        """
        Ranked shelter options by immediate safety.
        """
        actions = []

        # Option 1: Stay in vehicle
        if threat_level in ["IMMINENT", "CRITICAL", "HIGH"]:
            actions.append({
                "action": "Stay inside vehicle cab (metal roof = Faraday cage)",
                "safety_rank": "HIGH" if threat_level != "IMMINENT" else "MODERATE",
                "conditions": "Don't touch metal frame, door handles, steering wheel. Feet off floor. Windows up.",
                "duration": "Until thunder delay > 30sec"
            })

        # Option 2: Move to nearby building
        if "truck_stop" in location.lower():
            actions.append({
                "action": "Move to truck stop building (office, diner)",
                "safety_rank": "HIGHEST",
                "conditions": "Stay away from windows. Keep away from metal structures.",
                "duration": "Until lightning passes"
            })

        # Option 3: Drive away from storm
        if threat_level in ["HIGH", "MODERATE"]:
            actions.append({
                "action": "Drive perpendicular to storm movement (usually SW to NE)",
                "safety_rank": "HIGH",
                "conditions": "Safe roads available. Avoid driving into heavier rain.",
                "duration": "Until clear of storm"
            })

        # Option 4: Culvert/underpass shelter
        actions.append({
            "action": "Move to culvert or bridge underpass (if accessible)",
            "safety_rank": "HIGH",
            "conditions": "Stay inside metal structure. Away from entrance.",
            "duration": "Until thunder delay > 30sec"
        })

        return actions


# --- Critical safety note ---

CRITICAL_FACTS = {
    "truck_stop_danger": "Open parking lot + semi truck = one of worst lightning scenarios. Tall isolated conductor in flat open area.",
    "faraday_cage": "Inside metal cab with windows/doors closed = ~99% protection if you avoid touching metal.",
    "grounding_myth": "Rubber tires do NOT ground vehicle. Lightning can arc across them. Truck is isolated conductor.",
    "door_handle_death": "Touching door handle during/after strike = direct ground path through body. AVOID.",
    "fuel_tank_risk": "Direct lightning strike on fuel tank = fire. Rare but catastrophic.",
    "electronics_emp": "Nearby strike can disable electronics via electromagnetic pulse. Truck may not start.",
    "lateral_strike": "Lightning doesn't need direct hit. Lateral arcs up to 10+ miles from parent cloud.",
}


def register_with_resolver(resolver):
    resolver.register_domain("lightning_threat", lambda parent, query: [])

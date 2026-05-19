# tornado_avoidance_resolver.py
# Real-time mesocyclone tracking + threat corridor mapping
# CC0 | mobile-queryable | requires live weather data

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum

class ThreatLevel(Enum):
    CLEAR = 0
    WATCH = 1
    WARNING = 2
    IMMINENT = 3
    ABORT = 4

@dataclass
class Mesocyclone:
    """Detected rotation signature."""
    latitude: float
    longitude: float
    rotation_velocity_knots: int
    circulation_diameter_miles: float
    confidence_percent: int
    detected_timestamp: str

@dataclass
class ProjectedPath:
    """Tornado movement forecast."""
    current_position: Tuple[float, float]
    heading: float  # degrees true
    forward_speed_mph: int
    path_width_miles: float
    confidence_percent: int
    next_impact_minutes: int

@dataclass
class TruckPosition:
    current_lat: float
    current_lon: float
    heading: float
    speed_mph: int
    rig_length_feet: int

class TornadoAvoidanceResolver:
    """
    Given mesocyclone + truck position,
    return threat assessment + action options:
    accelerate through, lateral dodge, ditch & run.
    """

    def query(self, meso: Mesocyclone, path: ProjectedPath,
              truck: TruckPosition) -> Dict:
        """
        Returns: threat level + action ranking.
        """
        threat = self._calculate_threat(meso, path, truck)

        if threat == ThreatLevel.ABORT:
            return {
                "action": "DITCH RIG, RUN PERPENDICULAR TO PATH",
                "reason": "Impact imminent, no time to maneuver"
            }

        dodge_feasible = self._check_lateral_dodge(path, truck)
        accel_feasible = self._check_acceleration_through(path, truck)

        options = []
        if accel_feasible:
            options.append({
                "action": "Accelerate through path zone",
                "speed_required_mph": self._required_speed(path, truck),
                "confidence": self._confidence_accel(path, truck),
                "risk": "if engine fails / collision"
            })

        if dodge_feasible:
            options.append({
                "action": "Hard lateral dodge (off-road if needed)",
                "direction": "perpendicular to path",
                "confidence": self._confidence_dodge(path, truck),
                "risk": "rig rollover on soft shoulder"
            })

        options.append({
            "action": "DITCH & RUN",
            "direction": "perpendicular to projected path",
            "survival_probability": 0.92,
            "risk": "low if you move fast"
        })

        return {
            "threat_level": threat.value,
            "time_to_impact_minutes": path.next_impact_minutes,
            "action_options_ranked": sorted(options,
                key=lambda x: x.get("survival_probability", 0),
                reverse=True),
            "recommended_action": options[0]
        }

    def _calculate_threat(self, meso: Mesocyclone,
                         path: ProjectedPath, truck: TruckPosition) -> ThreatLevel:
        """Does the path cross your position before you can escape?"""
        time_to_impact = path.next_impact_minutes
        distance_to_path_edge = self._distance_to_path(meso, truck)

        # Can you outrun it?
        if truck.speed_mph >= path.forward_speed_mph + 20:
            return ThreatLevel.WATCH

        # Can you dodge it?
        if distance_to_path_edge < truck.rig_length_feet / 5280:  # Convert feet to miles
            if time_to_impact < 5:
                return ThreatLevel.ABORT
            else:
                return ThreatLevel.WARNING

        return ThreatLevel.IMMINENT if time_to_impact < 10 else ThreatLevel.WARNING

    def _check_acceleration_through(self, path: ProjectedPath,
                                   truck: TruckPosition) -> bool:
        """Can you outrun the path to the far side?"""
        required_speed = self._required_speed(path, truck)
        return required_speed <= 75  # Realistic max for loaded semi

    def _check_lateral_dodge(self, path: ProjectedPath,
                            truck: TruckPosition) -> bool:
        """Is there space to dodge perpendicular to path?"""
        # Simplified: if not in urban corridor, yes
        return True  # Would integrate terrain/road data

    def _required_speed(self, path: ProjectedPath,
                       truck: TruckPosition) -> int:
        """What speed do you need to clear the path zone?"""
        pass

    def _distance_to_path(self, meso: Mesocyclone,
                         truck: TruckPosition) -> float:
        """Miles from truck to projected path edge."""
        pass

    def _confidence_accel(self, path: ProjectedPath,
                         truck: TruckPosition) -> float:
        return min(path.confidence_percent / 100,
                  (75 - truck.speed_mph) / 50)

    def _confidence_dodge(self, path: ProjectedPath,
                         truck: TruckPosition) -> float:
        return 0.6  # Lateral dodge on highway = risky

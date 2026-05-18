# wildfire_shelter_resolver.py
# Real-time survival constraint navigation
# CC0 | falsifiable | offline-capable

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

class TerrainType(Enum):
    SCREE = "scree"
    CREEK_BED = "creek_bed"
    CULVERT = "culvert"
    ROCK_OUTCROP = "rock_outcrop"
    DENSE_FOREST = "dense_forest"
    OPEN_FIELD = "open_field"
    RAVINE = "ravine"
    WATER_BODY = "water_body"

class ShelterRating(Enum):
    CRITICAL = 1  # Immediate life risk
    POOR = 2      # Survival possible, high discomfort
    MARGINAL = 3  # Viable short-term
    GOOD = 4      # Solid protection
    OPTIMAL = 5   # Best available option

@dataclass
class TerrainFeature:
    """Known landmark on your corridor."""
    id: str
    name: str
    terrain_type: TerrainType
    location: Tuple[float, float]  # lat, lon OR mile marker + offset
    distance_minutes_foot: int  # From highway at sprint pace
    oxygen_duration_hours: float
    heat_exposure_risk: str  # "low", "medium", "high"
    water_access: bool
    exit_viability: str  # "easy", "moderate", "difficult"
    signaling_options: List[str]  # "visible_from_road", "cell_strength", "clear_sky"
    notes: str

@dataclass
class VehicleState:
    position: Tuple[float, float]  # lat, lon OR mile marker
    operable: bool
    fuel_remaining_miles: int
    occupants: int
    equipment_on_hand: List[str]  # Water, blanket, fire extinguisher, flare, etc.

@dataclass
class IncidentContext:
    wind_speed_mph: int
    wind_direction: str  # "from_N", "from_NE", etc.
    fire_proximity_miles: float
    visibility_meters: int
    smoke_inhalation_risk: str  # "low", "medium", "high"

class WildfirerShelterResolver:
    """
    Given vehicle position + incident context,
    return ranked shelter options with viability scores and escape chains.
    """

    def __init__(self):
        self.terrain_library: Dict[str, TerrainFeature] = {}

    def register_terrain(self, feature: TerrainFeature) -> None:
        """Add known landmark to your corridor memory."""
        self.terrain_library[feature.id] = feature

    def query(self, vehicle_state: VehicleState,
              incident: IncidentContext,
              search_radius_miles: float = 5.0) -> Dict:
        """
        Returns ranked shelter options + escape chains.
        Primary output: immediate action sequence.
        """
        candidates = self._find_nearby_terrain(
            vehicle_state.position, search_radius_miles
        )
        scored = self._score_shelters(
            candidates, vehicle_state, incident
        )
        ranked = sorted(scored, key=lambda x: x["viability"], reverse=True)

        return {
            "immediate_action": ranked[0] if ranked else None,
            "ranked_options": ranked,
            "fallback_chains": self._build_fallback_chains(ranked),
            "signaling_priority": self._signaling_plan(ranked[0] if ranked else None),
            "time_to_viability": self._estimate_timeline(ranked[0] if ranked else None, vehicle_state)
        }

    def _find_nearby_terrain(self, position: Tuple, radius: float) -> List[TerrainFeature]:
        """
        Memory-first: return features you know near this position.
        If GPS + cell available, could supplement with topo API query.
        """
        # Simplified: iterate library, filter by distance
        candidates = []
        for feature in self.terrain_library.values():
            dist = self._haversine(position, feature.location)
            if dist <= radius:
                candidates.append(feature)
        return candidates

    def _score_shelters(self, candidates: List[TerrainFeature],
                       vehicle: VehicleState, incident: IncidentContext) -> List[Dict]:
        """
        Composite score: oxygen duration × heat protection × reachability × exit viability.
        """
        results = []
        for feature in candidates:
            # Oxygen score
            oxygen_score = min(feature.oxygen_duration_hours / 2.0, 1.0)

            # Heat exposure (inverse)
            heat_map = {"low": 1.0, "medium": 0.6, "high": 0.3}
            heat_score = heat_map.get(feature.heat_exposure_risk, 0.5)

            # Reachability (can you sprint there before fire reaches you?)
            fire_arrival_minutes = (incident.fire_proximity_miles /
                                   (incident.wind_speed_mph / 60))
            reachability_score = (1.0 if feature.distance_minutes_foot < fire_arrival_minutes
                                 else 0.5)

            # Exit viability
            exit_map = {"easy": 1.0, "moderate": 0.7, "difficult": 0.4}
            exit_score = exit_map.get(feature.exit_viability, 0.5)

            # Composite
            viability = (oxygen_score * 0.35 + heat_score * 0.35 +
                        reachability_score * 0.2 + exit_score * 0.1)

            results.append({
                "shelter_id": feature.id,
                "name": feature.name,
                "terrain": feature.terrain_type.value,
                "distance_minutes": feature.distance_minutes_foot,
                "viability": viability,
                "oxygen_hours": feature.oxygen_duration_hours,
                "heat_risk": feature.heat_exposure_risk,
                "water_access": feature.water_access,
                "exit_viability": feature.exit_viability,
                "signaling": feature.signaling_options,
                "notes": feature.notes
            })

        return results

    def _build_fallback_chains(self, ranked: List[Dict]) -> List[List[str]]:
        """
        If primary shelter closes (blocked access, overcrowded, structural failure),
        what's your sequence of alternatives?
        Returns paths, not just single options.
        """
        chains = []
        for i in range(len(ranked)):
            chain = [ranked[j]["shelter_id"] for j in range(i, min(i + 3, len(ranked)))]
            chains.append(chain)
        return chains[:1]  # Return primary chain (first 3 options in rank order)

    def _signaling_plan(self, primary: Optional[Dict]) -> Dict:
        """
        From this shelter, how do you signal for rescue?
        Ranked by effectiveness.
        """
        if not primary:
            return {"options": [], "notes": "No viable shelter found"}

        signaling = primary.get("signaling", [])
        return {
            "options": signaling,
            "primary": signaling[0] if signaling else "none",
            "notes": f"From {primary['name']}: {', '.join(signaling)}"
        }

    def _estimate_timeline(self, primary: Optional[Dict],
                          vehicle: VehicleState) -> Dict:
        """
        How long until you're in shelter? How long can you stay?
        """
        if not primary:
            return {"status": "no_shelter_found", "recommendation": "move_vehicle"}

        return {
            "minutes_to_shelter": primary["distance_minutes"],
            "oxygen_duration_hours": primary["oxygen_hours"],
            "safe_margin_minutes": max(0, 5 - primary["distance_minutes"]),
            "recommendation": "GO NOW" if primary["distance_minutes"] < 3 else "MOVE SOON"
        }

    def _haversine(self, pos1: Tuple[float, float],
                   pos2: Tuple[float, float]) -> float:
        """Simple distance calc. Replace with geodesic if needed."""
        from math import radians, cos, sin, asin, sqrt
        lon1, lat1, lon2, lat2 = map(radians, [pos1[1], pos1[0], pos2[1], pos2[0]])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km * 0.621371  # Convert to miles

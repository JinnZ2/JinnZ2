# wildfire_shelter_resolver.py
# Relational + GPS hybrid navigation for emergency shelter
# CC0 | falsifiable | offline-capable + cell-enhanced

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

class TerrainType(Enum):
    SCREE = "scree"
    CREEK_BED = "creek_bed"
    CULVERT = "culvert"
    ROCK_OUTCROP = "rock_outcrop"
    GRAVEL_PIT = "gravel_pit"
    DENSE_FOREST = "dense_forest"
    OPEN_FIELD = "open_field"
    RAVINE = "ravine"
    WATER_BODY = "water_body"

class ShelterRating(Enum):
    CRITICAL = 1
    POOR = 2
    MARGINAL = 3
    GOOD = 4
    OPTIMAL = 5

@dataclass
class TerrainFeature:
    """Known landmark on corridor."""
    id: str
    name: str
    terrain_type: TerrainType
    coordinates: Tuple[float, float]  # lat, lon (from topo lookup or memory)
    relational_description: str  # "lake off right from Trigo", "gravel pit 2min north of 63 pulloff"
    distance_minutes_foot: int  # Sprint pace
    oxygen_duration_hours: float
    heat_exposure_risk: str  # "low", "medium", "high"
    water_access: bool
    exit_viability: str  # "easy", "moderate", "difficult"
    signaling_options: List[str]  # "visible_from_road", "cell_dead_zone", "open_sky"
    wind_protection: str  # "excellent", "good", "marginal", "none"
    notes: str

@dataclass
class RelationalAnchor:
    """Known location node in your mental map."""
    id: str
    name: str  # "sixty-three pulloff", "Trigo", "Superior bridge"
    coordinates: Tuple[float, float]
    description: str

@dataclass
class RelationalDirection:
    """Describes terrain relative to anchor."""
    from_anchor: str
    bearing: str  # "north", "south", "east", "west", "northeast", etc.
    terrain_features: List[TerrainFeature]  # What's reachable in that direction

@dataclass
class VehicleState:
    current_anchor: str  # "at sixty-three pulloff"
    heading: str  # "north toward Trigo"
    coordinates: Optional[Tuple[float, float]]  # GPS if available
    operable: bool
    fuel_remaining_miles: int
    occupants: int
    equipment_on_hand: List[str]

@dataclass
class IncidentContext:
    wind_speed_mph: int
    wind_direction: str  # "from_west", "from_north", etc.
    fire_proximity_miles: float
    visibility_meters: int
    smoke_inhalation_risk: str

class WildfirerShelterResolver:
    """
    Hybrid relational + GPS navigation for shelter discovery.
    Input: relational position ("at 63, heading north to Trigo")
    Output: ranked shelters in both relational + GPS terms
    """

    def __init__(self):
        self.anchors: Dict[str, RelationalAnchor] = {}
        self.terrain_library: Dict[str, TerrainFeature] = {}
        self.relational_map: Dict[str, List[RelationalDirection]] = {}

    def register_anchor(self, anchor: RelationalAnchor) -> None:
        """Add known landmark to mental map."""
        self.anchors[anchor.id] = anchor

    def register_terrain(self, feature: TerrainFeature) -> None:
        """Add terrain feature; optionally tied to relational context."""
        self.terrain_library[feature.id] = feature

    def register_relational_direction(self, anchor_id: str,
                                     direction: RelationalDirection) -> None:
        """Map what's reachable from an anchor in a given direction."""
        if anchor_id not in self.relational_map:
            self.relational_map[anchor_id] = []
        self.relational_map[anchor_id].append(direction)

    def query(self, vehicle_state: VehicleState,
              incident: IncidentContext) -> Dict:
        """
        Given relational position + incident, return ranked shelters
        in both relational + GPS language.
        """
        # Resolve relational position to coordinates
        anchor = self.anchors.get(vehicle_state.current_anchor)
        if not anchor:
            return {"error": f"Anchor '{vehicle_state.current_anchor}' not found"}

        # Find terrain features in heading direction
        heading_features = self._find_features_by_direction(
            vehicle_state.current_anchor, vehicle_state.heading
        )

        # Score each by survivability
        scored = self._score_shelters(heading_features, vehicle_state, incident)
        ranked = sorted(scored, key=lambda x: x["viability_score"], reverse=True)

        return {
            "current_position_relational": f"{vehicle_state.current_anchor}, heading {vehicle_state.heading}",
            "current_position_gps": anchor.coordinates if anchor else None,
            "immediate_action": ranked[0] if ranked else None,
            "ranked_options": ranked,
            "fallback_chains": self._build_fallback_chains(ranked),
            "signaling_plan": self._signaling_plan(ranked[0] if ranked else None, anchor),
            "time_to_shelter": ranked[0]["distance_minutes"] if ranked else None,
            "wind_interaction": self._assess_wind(ranked[0] if ranked else None, incident)
        }

    def _find_features_by_direction(self, anchor_id: str,
                                   heading: str) -> List[TerrainFeature]:
        """
        Return terrain features reachable from anchor in given direction.
        Heading = "north toward Trigo", "south", etc.
        """
        if anchor_id not in self.relational_map:
            return []

        # Parse heading direction
        heading_primary = heading.split()[0].lower()  # "north" from "north toward Trigo"

        features = []
        for rel_dir in self.relational_map[anchor_id]:
            if heading_primary in rel_dir.bearing.lower():
                features.extend(rel_dir.terrain_features)

        return features

    def _score_shelters(self, features: List[TerrainFeature],
                       vehicle: VehicleState,
                       incident: IncidentContext) -> List[Dict]:
        """
        Score: oxygen duration × heat protection × reachability × exit viability.
        Modulated by wind direction relative to fire approach.
        """
        results = []
        for feature in features:
            # Oxygen score (longer = higher)
            oxygen_score = min(feature.oxygen_duration_hours / 2.0, 1.0)

            # Heat exposure (inverse; lower risk = higher score)
            heat_map = {"low": 1.0, "medium": 0.6, "high": 0.3}
            heat_score = heat_map.get(feature.heat_exposure_risk, 0.5)

            # Reachability (faster = higher)
            reach_score = 1.0 - min(feature.distance_minutes_foot / 10.0, 1.0)

            # Exit viability
            exit_map = {"easy": 1.0, "moderate": 0.7, "difficult": 0.4}
            exit_score = exit_map.get(feature.exit_viability, 0.5)

            # Wind protection (if wind is adverse, protection matters more)
            wind_mult = 1.2 if incident.wind_speed_mph > 50 else 1.0
            wind_map = {"excellent": 1.0, "good": 0.8, "marginal": 0.5, "none": 0.2}
            wind_score = wind_map.get(feature.wind_protection, 0.5) * wind_mult

            # Composite
            viability = (oxygen_score * 0.25 + heat_score * 0.25 +
                        reach_score * 0.2 + exit_score * 0.15 + wind_score * 0.15)

            results.append({
                "feature_id": feature.id,
                "name": feature.name,
                "relational": feature.relational_description,
                "gps": feature.coordinates,
                "terrain_type": feature.terrain_type.value,
                "distance_minutes": feature.distance_minutes_foot,
                "oxygen_hours": feature.oxygen_duration_hours,
                "viability_score": viability,
                "oxygen_score": oxygen_score,
                "heat_score": heat_score,
                "reachability_score": reach_score,
                "exit_score": exit_score,
                "water_access": feature.water_access,
                "signaling": feature.signaling_options,
                "notes": feature.notes
            })

        return results

    def _build_fallback_chains(self, ranked: List[Dict]) -> List[Dict]:
        """
        If primary shelter closes (impassable, fills with smoke),
        what's the next ranked option + ETA?
        """
        return [
            {
                "rank": i + 1,
                "option": r["name"],
                "relational": r["relational"],
                "viability": r["viability_score"],
                "minutes_from_primary": sum(ranked[j]["distance_minutes"]
                                           for j in range(i)) if i > 0 else 0
            }
            for i, r in enumerate(ranked[:3])  # Top 3 fallbacks
        ]

    def _signaling_plan(self, primary_shelter: Optional[Dict],
                       anchor: Optional[RelationalAnchor]) -> Dict:
        """
        Once sheltered, how do you signal for rescue?
        GPS coordinates for emergency services.
        """
        if not primary_shelter:
            return {"error": "No viable shelter"}

        return {
            "gps_coordinates": primary_shelter["gps"],
            "signaling_methods": primary_shelter["signaling"],
            "emergency_message": f"Sheltered at {primary_shelter['name']}, "
                               f"{primary_shelter['relational']}, "
                               f"coordinates {primary_shelter['gps']}"
        }

    def _assess_wind(self, primary_shelter: Optional[Dict],
                    incident: IncidentContext) -> Dict:
        """
        How does wind + fire direction interact with chosen shelter?
        """
        if not primary_shelter:
            return {}

        return {
            "wind_speed": incident.wind_speed_mph,
            "wind_direction": incident.wind_direction,
            "shelter_protection": primary_shelter.get("wind_protection", "unknown"),
            "fire_proximity_miles": incident.fire_proximity_miles,
            "risk_assessment": "CRITICAL" if incident.fire_proximity_miles < 1.0 else "HIGH"
        }

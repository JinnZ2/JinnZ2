# tornado_signature_resolver.py
# Reverse-engineer atmospheric conditions from observed phenomena
# Trust ground observer over delayed model data
# CC0 | falsifiable

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

@dataclass
class ObservedSignatures:
    """What you're seeing RIGHT NOW."""
    rotation_visible: bool
    rotation_intensity: str  # "subtle", "clear", "violent"
    hail_present: bool
    hail_size_inches: float
    sky_color: str  # "greenish", "dark_gray", "black", "clear"
    wind_direction: str  # "from_west", compass degrees
    wind_gusts_mph: int
    visibility_meters: int
    sound: str  # "silence", "roar", "freight_train"
    pressure_trend: str  # "rising", "falling", "stable"

@dataclass
class InferredCondition:
    """What must be true to produce these signatures."""
    updraft_strength_mph: str  # "weak", "moderate", "strong", "violent"
    rotation_likelihood: float  # 0–1
    mesocyclone_probable: bool
    storm_motion_direction: str
    storm_motion_speed_mph: int
    trajectory_confidence: float

class SignatureResolver:
    """
    Given observed phenomena, infer atmospheric state.
    Then project forward trajectory.
    """

    def analyze(self, observed: ObservedSignatures) -> Dict:
        """
        Returns: inferred conditions + projected path/timing.
        """
        inferred = self._infer_conditions(observed)
        trajectory = self._project_trajectory(observed, inferred)
        action = self._recommend_action(trajectory, observed)

        return {
            "observed_summary": self._summarize(observed),
            "inferred_conditions": inferred,
            "projected_trajectory": trajectory,
            "recommended_action": action,
            "confidence": inferred.trajectory_confidence,
            "next_update_minutes": 2
        }

    def _infer_conditions(self, obs: ObservedSignatures) -> InferredCondition:
        """
        Hail + rotation + sky color + pressure trend
        → updraft strength, mesocyclone probability, motion.
        """
        # Hail size correlates to updraft
        if obs.hail_size_inches > 2.0:
            updraft = "violent"
        elif obs.hail_size_inches > 1.0:
            updraft = "strong"
        elif obs.hail_present:
            updraft = "moderate"
        else:
            updraft = "weak"

        # Sky color + rotation + pressure = mesocyclone confidence
        meso_prob = 0.0
        if obs.rotation_visible:
            meso_prob += 0.5
        if obs.sky_color in ("greenish", "black"):
            meso_prob += 0.3
        if obs.pressure_trend == "falling":
            meso_prob += 0.2
        meso_prob = min(meso_prob, 1.0)

        # Wind direction + observed motion = storm movement
        # (Simplified; real analysis needs radar)
        storm_motion = self._infer_storm_motion(obs)

        return InferredCondition(
            updraft_strength_mph=updraft,
            rotation_likelihood=meso_prob,
            mesocyclone_probable=meso_prob > 0.6,
            storm_motion_direction=storm_motion["direction"],
            storm_motion_speed_mph=storm_motion["speed"],
            trajectory_confidence=0.7  # Ground obs is good but not perfect
        )

    def _infer_storm_motion(self, obs: ObservedSignatures) -> Dict:
        """Guess storm direction + speed from wind + observed rotation."""
        # Simplified heuristic
        return {
            "direction": obs.wind_direction,
            "speed": obs.wind_gusts_mph * 0.6  # Rough ratio
        }

    def _project_trajectory(self, obs: ObservedSignatures,
                           inferred: InferredCondition) -> Dict:
        """
        Project path over next 10 minutes.
        """
        return {
            "storm_center_direction": inferred.storm_motion_direction,
            "forward_distance_miles_5min": inferred.storm_motion_speed_mph * 5 / 60,
            "forward_distance_miles_10min": inferred.storm_motion_speed_mph * 10 / 60,
            "expected_intensity_trend": "strengthening" if inferred.updraft_strength_mph == "violent" else "variable",
            "path_width_miles": 0.5 if inferred.mesocyclone_probable else 2.0
        }

    def _recommend_action(self, trajectory: Dict,
                         obs: ObservedSignatures) -> str:
        if obs.rotation_intensity == "violent" and obs.sound == "freight_train":
            return "DITCH RIG, RUN PERPENDICULAR TO WIND DIRECTION"
        elif trajectory["forward_distance_miles_5min"] < 2:
            return "Accelerate perpendicular to storm motion OR maintain speed/heading if clearing path"
        else:
            return "Monitor continuously. Update every 90 seconds."

    def _summarize(self, obs: ObservedSignatures) -> str:
        parts = []
        if obs.rotation_visible:
            parts.append(f"ROTATION: {obs.rotation_intensity}")
        if obs.hail_present:
            parts.append(f"HAIL: {obs.hail_size_inches}in")
        parts.append(f"SKY: {obs.sky_color}")
        parts.append(f"WIND: {obs.wind_gusts_mph}mph from {obs.wind_direction}")
        return " | ".join(parts)

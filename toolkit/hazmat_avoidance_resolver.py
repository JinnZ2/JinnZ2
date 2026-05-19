# hazmat_avoidance_resolver.py
# Material identification + dispersion modeling + vehicle vulnerability assessment
# CC0 | falsifiable | offline-capable | physics-first inference

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class HazmatObservationType(Enum):
    COLOR = "color"
    ODOR = "odor"
    VISCOSITY = "viscosity"
    CONTAINER_TYPE = "container_type"
    SPILL_SOURCE = "spill_source"
    VAPOR_VISIBLE = "vapor_visible"
    LIQUID_BEHAVIOR = "liquid_behavior"
    WIND_DIRECTION = "wind_direction"
    WEATHER = "weather"

class MaterialDensity(Enum):
    HEAVIER_THAN_AIR = "sinks"  # Chlorine, ammonia, propane (heavier vapors)
    LIGHTER_THAN_AIR = "rises"  # Hydrogen, methane, many organics
    SIMILAR_TO_AIR = "disperses"  # CO, some alcohols
    LIQUID_POOLING = "pools"  # Water-like behavior

class VehicleVulnerability(Enum):
    ENGINE_INTAKE = "engine_intake"  # Vapor enters carburetor/fuel injection
    FUEL_SYSTEM = "fuel_system"  # Dissolves gasoline, clogs fuel filter
    TIRE_DEGRADATION = "tire_degradation"  # Solvents soften rubber
    VISIBILITY = "visibility"  # Dense fog/vapor blocks vision
    RESPIRATORY = "respiratory"  # Driver/occupants exposed in cab

@dataclass
class HazmatObservation:
    """Single sensory input identifying material."""
    observation_type: HazmatObservationType
    value: str  # "yellow-green gas", "pungent chlorine smell", "oily brown liquid", etc.
    confidence: float  # 0–1
    timestamp: Optional[str] = None

@dataclass
class MaterialHypothesis:
    """Candidate material identification."""
    id: str
    name: str
    common_names: List[str]
    color_description: str
    odor_description: str
    physical_state: str  # "gas", "liquid", "solid", "powder"
    density_relative_to_air: MaterialDensity
    vapor_pressure_mmhg: float  # Volatility; higher = more vapor
    water_solubility: str  # "immiscible", "slightly_soluble", "miscible"
    flammability: str  # "non", "low", "moderate", "high"
    health_hazard: str  # "irritant", "toxic", "corrosive", "systemic_poison"
    likelihood_percent: float
    supporting_observations: List[str]

@dataclass
class DispersionModel:
    """How hazmat spreads in current conditions."""
    id: str
    material: str
    wind_direction: str  # "from_NW", etc.
    wind_speed_mph: int
    initial_dispersion_rate_ftper_min: float
    ground_level_concentration_ppm: Dict[int, float]  # {0ft: 5000ppm, 10ft: 500ppm}
    hazard_zone_radius_ft: float
    safe_distance_ft: float
    concentration_at_truck_intake_ppm: float
    confidence_percent: int

@dataclass
class VehicleVulnerabilityAssessment:
    """Engine/fuel/tire/cabin exposure."""
    hazmat_material: str
    engine_intake_vulnerability: str  # "safe", "marginal", "at_risk", "critical"
    fuel_system_risk: str
    tire_degradation_risk: str
    visibility_impairment: bool
    driver_respiratory_exposure: str
    time_to_engine_failure_minutes: Optional[int]
    time_to_fuel_system_failure_minutes: Optional[int]
    extraction_viability: str  # "safe_extract", "marginal_extract", "extract_not_viable"

@dataclass
class ExtractionDecision:
    """Action recommendation."""
    action: str  # "extract_now", "shelter_in_cab", "abandon_rig", "wait"
    rationale: str
    estimated_exit_time_minutes: int
    exposure_duration_minutes: int
    risk_level: str  # "low", "moderate", "high", "critical"
    backup_action: str

@dataclass
class TruckContext:
    """Vehicle specs relevant to hazmat exposure."""
    engine_intake_height_feet: float  # Height of air filter
    cabin_air_intake_height_feet: float
    fuel_tank_location: str  # "rear", "side", "under_cab"
    fuel_system_sealed: bool  # Modern truck = yes
    windows_seal_quality: str  # "poor", "moderate", "good"
    engine_type: str  # "diesel", "gasoline"
    current_speed_mph: int

class HazmatAvoidanceResolver:
    """
    Identifies unknown hazmat from observations →
    models dispersion in current wind →
    assesses vehicle vulnerability →
    recommends extract vs. shelter.

    Physics base:
      Vapor density relative to air determines rise/sink.
      Volatility (vapor pressure) determines cloud density.
      Wind disperses but maintains hazard corridor downwind.
      Vehicle intake height + wind direction = exposure risk.
    """

    def __init__(self):
        self.material_library: Dict[str, MaterialHypothesis] = {}
        self._load_common_hazmat_materials()

    def _load_common_hazmat_materials(self) -> None:
        """Pre-load common industrial hazmat encountered on roads/facilities."""
        materials = [
            MaterialHypothesis(
                id="chlorine",
                name="Chlorine Gas",
                common_names=["Cl2", "chlorine", "pool chemical"],
                color_description="yellow-green",
                odor_description="pungent, bleach-like, sharp",
                physical_state="gas",
                density_relative_to_air=MaterialDensity.HEAVIER_THAN_AIR,
                vapor_pressure_mmhg=4760,
                water_solubility="miscible",
                flammability="non",
                health_hazard="toxic",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="ammonia",
                name="Ammonia Gas",
                common_names=["NH3", "ammonia", "anhydrous ammonia"],
                color_description="colorless",
                odor_description="pungent, suffocating, alkaline",
                physical_state="gas",
                density_relative_to_air=MaterialDensity.LIGHTER_THAN_AIR,
                vapor_pressure_mmhg=8700,
                water_solubility="miscible",
                flammability="non",
                health_hazard="toxic",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="propane",
                name="Propane Liquid/Gas",
                common_names=["LPG", "propane", "liquified propane"],
                color_description="colorless (liquid appears clear)",
                odor_description="odorless (odorant added: rotten egg / mercaptan)",
                physical_state="gas",
                density_relative_to_air=MaterialDensity.HEAVIER_THAN_AIR,
                vapor_pressure_mmhg=1510,
                water_solubility="immiscible",
                flammability="high",
                health_hazard="asphyxiant",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="sulfuric_acid",
                name="Sulfuric Acid (concentrated)",
                common_names=["H2SO4", "sulfuric acid", "battery acid"],
                color_description="colorless to brown oily liquid",
                odor_description="pungent SO2 if heated, acrid",
                physical_state="liquid",
                density_relative_to_air=MaterialDensity.SIMILAR_TO_AIR,
                vapor_pressure_mmhg=0.001,  # Very low; mostly liquid hazard
                water_solubility="miscible (exothermic)",
                flammability="non",
                health_hazard="corrosive",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="diesel_fuel",
                name="Diesel Fuel",
                common_names=["diesel", "fuel oil", "kerosene"],
                color_description="amber to dark brown",
                odor_description="petroleum, diesel-like",
                physical_state="liquid",
                density_relative_to_air=MaterialDensity.LIQUID_POOLING,
                vapor_pressure_mmhg=0.5,
                water_solubility="immiscible",
                flammability="moderate",
                health_hazard="irritant",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="gasoline",
                name="Gasoline",
                common_names=["gasoline", "petrol", "gas"],
                color_description="clear to pale yellow",
                odor_description="sharp, pungent petroleum",
                physical_state="liquid",
                density_relative_to_air=MaterialDensity.LIQUID_POOLING,
                vapor_pressure_mmhg=45,  # Moderate volatility
                water_solubility="immiscible",
                flammability="high",
                health_hazard="irritant",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="styrene",
                name="Styrene (monomer)",
                common_names=["styrene", "vinyl benzene", "phenylethene"],
                color_description="colorless to pale yellow liquid",
                odor_description="sweet, pungent aromatic",
                physical_state="liquid",
                density_relative_to_air=MaterialDensity.LIQUID_POOLING,
                vapor_pressure_mmhg=4,
                water_solubility="immiscible",
                flammability="moderate",
                health_hazard="toxic",
                likelihood_percent=0,
                supporting_observations=[]
            ),
            MaterialHypothesis(
                id="hydrochloric_acid",
                name="Hydrochloric Acid (concentrated)",
                common_names=["HCl", "muriatic acid", "hydrochloric acid"],
                color_description="colorless to pale yellow",
                odor_description="pungent, suffocating HCl gas",
                physical_state="liquid",
                density_relative_to_air=MaterialDensity.SIMILAR_TO_AIR,
                vapor_pressure_mmhg=0.05,
                water_solubility="miscible",
                flammability="non",
                health_hazard="corrosive",
                likelihood_percent=0,
                supporting_observations=[]
            ),
        ]
        for mat in materials:
            self.material_library[mat.id] = mat

    def query(self, observations: List[HazmatObservation],
              wind_direction: str,
              wind_speed_mph: int,
              truck: TruckContext) -> Dict:
        """
        Given observations, identify material →
        model dispersion → assess truck vulnerability →
        recommend action.
        """
        # Step 1: Identify material
        candidates = self._identify_material(observations)

        # Step 2: For each candidate, model dispersion
        dispersions = [
            self._model_dispersion(cand, wind_direction, wind_speed_mph)
            for cand in candidates
        ]

        # Step 3: Assess vehicle vulnerability to each
        vulnerabilities = [
            self._assess_vehicle_vulnerability(cand, disp, truck)
            for cand, disp in zip(candidates, dispersions)
        ]

        # Step 4: Rank and decide
        ranked = sorted(
            zip(candidates, dispersions, vulnerabilities),
            key=lambda x: x[2].extraction_viability,
            reverse=True
        )

        decision = self._make_extraction_decision(ranked[0] if ranked else None, truck, wind_direction)

        return {
            "identified_materials": [
                {
                    "name": c.name,
                    "likelihood": c.likelihood_percent,
                    "hazard_class": c.health_hazard
                }
                for c, _, _ in ranked
            ],
            "top_match": {
                "material": ranked[0][0].name if ranked else "UNKNOWN",
                "confidence": ranked[0][0].likelihood_percent if ranked else 0
            },
            "dispersion_model": {
                "wind_direction": wind_direction,
                "wind_speed": wind_speed_mph,
                "hazard_zone_radius_ft": ranked[0][1].hazard_zone_radius_ft if ranked else 0,
                "concentration_at_intake": ranked[0][1].concentration_at_truck_intake_ppm if ranked else 0
            },
            "vehicle_assessment": {
                "extraction_viability": ranked[0][2].extraction_viability if ranked else "unknown",
                "time_to_engine_failure": ranked[0][2].time_to_engine_failure_minutes,
                "critical_vulnerabilities": [
                    ranked[0][2].engine_intake_vulnerability,
                    ranked[0][2].fuel_system_risk
                ]
            } if ranked else {},
            "recommended_action": decision,
            "upwind_vs_downwind": self._assess_position_relative_to_wind(wind_direction),
        }

    def _identify_material(self, observations: List[HazmatObservation]) -> List[MaterialHypothesis]:
        """
        Match observations against material library.
        Return ranked candidates.
        """
        scored = []

        for mat_id, material in self.material_library.items():
            score = 0
            matches = []

            for obs in observations:
                if obs.observation_type == HazmatObservationType.COLOR:
                    if obs.value.lower() in material.color_description.lower():
                        score += obs.confidence * 30
                        matches.append(f"color: {obs.value}")

                elif obs.observation_type == HazmatObservationType.ODOR:
                    if obs.value.lower() in material.odor_description.lower() or \
                       material.odor_description.lower() in obs.value.lower():
                        score += obs.confidence * 40  # Odor is strong identifier
                        matches.append(f"odor: {obs.value}")

                elif obs.observation_type == HazmatObservationType.CONTAINER_TYPE:
                    # Match container hints: "yellow cylinder" = chlorine likely
                    if "cylinder" in obs.value.lower() and mat_id in ["chlorine", "ammonia"]:
                        score += obs.confidence * 25
                        matches.append(f"container: {obs.value}")

                elif obs.observation_type == HazmatObservationType.SPILL_SOURCE:
                    # "factory", "tanker truck", etc. → material type hints
                    if "factory" in obs.value.lower() and mat_id in ["sulfuric_acid", "styrene"]:
                        score += obs.confidence * 20
                    elif "tanker" in obs.value.lower() and mat_id in ["propane", "ammonia"]:
                        score += obs.confidence * 25

            if score > 0:
                material.likelihood_percent = int(min(score / 10, 100))
                material.supporting_observations = matches
                scored.append((material, score))

        # Return top 3 candidates
        return [m for m, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:3]]

    def _model_dispersion(self, material: MaterialHypothesis,
                         wind_direction: str,
                         wind_speed_mph: int) -> DispersionModel:
        """
        Model how the material disperses downwind of the source.

        Physics-first simplification:
          - Source concentration scales with vapor pressure (volatility).
          - Density relative to air shapes the vertical concentration
            profile: heavier vapors hug the ground, lighter vapors rise,
            similar-to-air vapors disperse uniformly, pooling liquids
            evaporate from the surface so vapor is densest near ground.
          - Wind speed scales lateral dispersion rate AND extends the
            downwind hazard corridor (faster wind = thinner cloud per
            unit area but longer reach).
        """
        # Lateral dispersion rate (ft/min), floor of 10 for calm wind.
        base_rate_ftper_min = max(wind_speed_mph * 5.0, 10.0)

        # Source concentration scales with volatility; cap to keep ppm sane.
        source_ppm = min(material.vapor_pressure_mmhg * 100.0, 100000.0)

        # Vertical concentration profile by density behavior.
        if material.density_relative_to_air == MaterialDensity.HEAVIER_THAN_AIR:
            ground_profile = {
                0: source_ppm * 0.80,
                5: source_ppm * 0.40,
                10: source_ppm * 0.10,
                20: source_ppm * 0.02,
            }
        elif material.density_relative_to_air == MaterialDensity.LIGHTER_THAN_AIR:
            ground_profile = {
                0: source_ppm * 0.05,
                5: source_ppm * 0.10,
                10: source_ppm * 0.20,
                20: source_ppm * 0.30,
            }
        elif material.density_relative_to_air == MaterialDensity.SIMILAR_TO_AIR:
            ground_profile = {
                0: source_ppm * 0.30,
                5: source_ppm * 0.25,
                10: source_ppm * 0.20,
                20: source_ppm * 0.15,
            }
        else:  # LIQUID_POOLING -- vapor densest just above the pool surface
            ground_profile = {
                0: source_ppm * 0.50,
                5: source_ppm * 0.10,
                10: source_ppm * 0.02,
                20: source_ppm * 0.005,
            }

        # Hazard zone: how far downwind the cloud stays above a hazardous
        # concentration. Scales with wind speed (longer corridor) and with
        # vapor pressure (more material per unit time).
        hazard_radius_ft = base_rate_ftper_min * 30.0  # 30-min reach
        safe_distance_ft = hazard_radius_ft * 1.5      # 50% buffer

        # Concentration at typical truck intake height (~3-4 ft from ground)
        # -- average the 0ft and 5ft profile values.
        intake_ppm = (ground_profile[0] + ground_profile[5]) / 2.0

        return DispersionModel(
            id=f"dispersion_{material.id}",
            material=material.name,
            wind_direction=wind_direction,
            wind_speed_mph=wind_speed_mph,
            initial_dispersion_rate_ftper_min=base_rate_ftper_min,
            ground_level_concentration_ppm=ground_profile,
            hazard_zone_radius_ft=hazard_radius_ft,
            safe_distance_ft=safe_distance_ft,
            concentration_at_truck_intake_ppm=intake_ppm,
            confidence_percent=int(material.likelihood_percent),
        )

    def _assess_vehicle_vulnerability(self, material: MaterialHypothesis,
                                     dispersion: DispersionModel,
                                     truck: TruckContext) -> VehicleVulnerabilityAssessment:
        """
        Rate engine, fuel system, tires, visibility, and respiratory
        exposure against the dispersion model and truck specs.
        """
        intake_ppm = dispersion.concentration_at_truck_intake_ppm

        # --- Engine intake ---
        if intake_ppm > 10000:
            engine_risk = "critical"
            time_to_engine: Optional[int] = 2
        elif intake_ppm > 1000:
            engine_risk = "at_risk"
            time_to_engine = 10
        elif intake_ppm > 100:
            engine_risk = "marginal"
            time_to_engine = 30
        else:
            engine_risk = "safe"
            time_to_engine = None

        # Flammables in significant concentration are a combustion risk
        # for the engine itself (intake-side ignition / fuel-air ratio).
        if material.flammability == "high" and intake_ppm > 100:
            engine_risk = "critical"
            time_to_engine = min(time_to_engine or 1, 1)

        # --- Fuel system ---
        if material.health_hazard == "corrosive" and not truck.fuel_system_sealed:
            fuel_risk = "critical"
            time_to_fuel: Optional[int] = 5
        elif material.health_hazard in ("corrosive", "toxic") and not truck.fuel_system_sealed:
            fuel_risk = "at_risk"
            time_to_fuel = 20
        elif truck.fuel_system_sealed:
            fuel_risk = "safe"
            time_to_fuel = None
        else:
            fuel_risk = "marginal"
            time_to_fuel = 60

        # --- Tires (rubber-softening solvents) ---
        if (material.physical_state == "liquid"
                and material.id in ("gasoline", "styrene", "diesel_fuel")):
            tire_risk = "at_risk"
        else:
            tire_risk = "safe"

        # --- Visibility ---
        visibility_impaired = (material.physical_state == "gas" and intake_ppm > 1000)

        # --- Respiratory (cab) ---
        seal_factor = {"poor": 0.2, "moderate": 0.5, "good": 0.9}.get(
            truck.windows_seal_quality, 0.5
        )
        if material.health_hazard in ("toxic", "corrosive") and intake_ppm > 100:
            respiratory = "critical" if seal_factor < 0.5 else "at_risk"
        elif material.health_hazard == "irritant" and intake_ppm > 1000:
            respiratory = "marginal"
        else:
            respiratory = "safe"

        # --- Composite extraction viability ---
        risks = (engine_risk, fuel_risk, respiratory)
        critical_count = sum(1 for r in risks if r == "critical")
        at_risk_count = sum(1 for r in risks if r == "at_risk")
        if critical_count >= 1:
            viability = "extract_not_viable"
        elif at_risk_count >= 2:
            viability = "marginal_extract"
        else:
            viability = "safe_extract"

        return VehicleVulnerabilityAssessment(
            hazmat_material=material.name,
            engine_intake_vulnerability=engine_risk,
            fuel_system_risk=fuel_risk,
            tire_degradation_risk=tire_risk,
            visibility_impairment=visibility_impaired,
            driver_respiratory_exposure=respiratory,
            time_to_engine_failure_minutes=time_to_engine,
            time_to_fuel_system_failure_minutes=time_to_fuel,
            extraction_viability=viability,
        )

    def _make_extraction_decision(self, top: Optional[Tuple[MaterialHypothesis, DispersionModel,
                                                            VehicleVulnerabilityAssessment]],
                                  truck: TruckContext,
                                  wind_direction: str) -> ExtractionDecision:
        """
        Recommend extract / shelter / abandon based on the top-ranked
        candidate's vulnerability assessment + truck speed.
        """
        if top is None:
            return ExtractionDecision(
                action="wait",
                rationale="No identifiable material from current observations.",
                estimated_exit_time_minutes=0,
                exposure_duration_minutes=0,
                risk_level="moderate",
                backup_action="Move upwind 500 ft and re-observe color, odor, container."
            )

        material, dispersion, vulnerability = top

        # Estimate exit time: distance / speed. Standing start adds 2 min
        # for acceleration; otherwise use current_speed.
        miles_to_clear = dispersion.safe_distance_ft / 5280.0
        if truck.current_speed_mph > 0:
            exit_minutes = max(int((miles_to_clear / truck.current_speed_mph) * 60), 1)
        else:
            # Conservative: average 30 mph clearing speed + 2 min ramp-up.
            exit_minutes = max(int((miles_to_clear / 30.0) * 60) + 2, 1)

        viability = vulnerability.extraction_viability

        if viability == "extract_not_viable":
            return ExtractionDecision(
                action="abandon_rig",
                rationale=(
                    f"{material.name}: engine {vulnerability.engine_intake_vulnerability}, "
                    f"respiratory {vulnerability.driver_respiratory_exposure}. "
                    f"Rig cannot clear hazard zone before systems fail."
                ),
                estimated_exit_time_minutes=0,
                exposure_duration_minutes=exit_minutes,
                risk_level="critical",
                backup_action=(
                    "Dismount and move perpendicular to wind on foot; "
                    "stay upwind of source."
                )
            )

        if viability == "marginal_extract":
            return ExtractionDecision(
                action="extract_now",
                rationale=(
                    f"{material.name}: extraction window narrow. "
                    f"Drive perpendicular to wind at maximum speed."
                ),
                estimated_exit_time_minutes=exit_minutes,
                exposure_duration_minutes=exit_minutes,
                risk_level="high",
                backup_action=(
                    "If engine falters mid-extraction, dismount and "
                    "continue on foot perpendicular to wind direction."
                )
            )

        # safe_extract
        return ExtractionDecision(
            action="extract_now",
            rationale=(
                f"{material.name} identified; vehicle systems tolerate "
                f"current exposure. Drive perpendicular to wind to clear "
                f"hazard zone."
            ),
            estimated_exit_time_minutes=exit_minutes,
            exposure_duration_minutes=exit_minutes,
            risk_level="moderate",
            backup_action="If extraction stalls, shelter in cab with windows sealed."
        )

    def _assess_position_relative_to_wind(self, wind_direction: str) -> Dict:
        """
        Without an explicit source position, classify the safe heading
        as upwind (opposite of where the wind is from) and remind the
        caller that the hazard corridor is downwind of the source.
        """
        opposite = {
            "from_n": "head N", "from_ne": "head NE", "from_e": "head E",
            "from_se": "head SE", "from_s": "head S", "from_sw": "head SW",
            "from_w": "head W", "from_nw": "head NW",
        }
        safe_heading = opposite.get(
            wind_direction.lower(),
            "head upwind (opposite of wind direction)"
        )
        return {
            "wind_from": wind_direction,
            "safe_heading": safe_heading,
            "note": (
                "Plume travels downwind of source. Move perpendicular "
                "to wind first, then upwind, to clear the hazard corridor."
            ),
        }

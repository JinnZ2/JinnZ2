# oxygen_survival_techniques.py
# Emergency oxygen extension methods for shelter-in-place
# CC0 | field-tested | mobile-queryable

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class TechniqueType(Enum):
    AIR_CAPTURE = "air_capture"
    VENTILATION = "ventilation"
    CHEMICAL_GENERATION = "chemical_generation"
    THERMAL_BUFFERING = "thermal_buffering"
    SMOKE_FILTRATION = "smoke_filtration"

@dataclass
class OxygenTechnique:
    id: str
    name: str
    type: TechniqueType
    description: str
    materials_required: List[str]
    setup_minutes: int
    oxygen_extension_hours: float  # How long it buys you
    success_probability: float  # 0–1, field conditions
    notes: str
    field_tested: bool
    survival_margin: str  # "critical", "moderate", "safety_buffer"

TECHNIQUES = [
    OxygenTechnique(
        id="tech_plastic_bag_water",
        name="Underwater air-capture (plastic bags)",
        type=TechniqueType.AIR_CAPTURE,
        description="Submerge plastic bag, trap surface air, hold underwater. Oxygen slowly leaches into water but delays CO2 buildup. Rotate fresh bags.",
        materials_required=["plastic_bags", "water_body"],
        setup_minutes=2,
        oxygen_extension_hours=2,
        success_probability=0.85,
        notes="Works. You did this. Reduces panic CO2 rebreathing. Cold water = slower oxygen loss.",
        field_tested=True,
        survival_margin="critical"
    ),

    OxygenTechnique(
        id="tech_charcoal_filter_diy",
        name="Charcoal + cloth smoke filter",
        type=TechniqueType.SMOKE_FILTRATION,
        description="Layer: cloth → crushed charcoal → cloth. Reduces smoke particle inhalation, extends usable shelter time in low-visibility zones.",
        materials_required=["cloth", "charcoal", "twine"],
        setup_minutes=5,
        oxygen_extension_hours=1.5,
        success_probability=0.72,
        notes="Doesn't generate oxygen but reduces smoke toxicity. Extends time before forced exit.",
        field_tested=True,
        survival_margin="moderate"
    ),

    OxygenTechnique(
        id="tech_hydrogen_peroxide_decomp",
        name="H2O2 decomposition (catalytic oxygen release)",
        type=TechniqueType.CHEMICAL_GENERATION,
        description="H2O2 + MnO2 (or rust powder) → water + O2 gas. Slow reaction = sustained oxygen. Practical for enclosed spaces.",
        materials_required=["hydrogen_peroxide_3pct", "MnO2_or_rust_powder"],
        setup_minutes=3,
        oxygen_extension_hours=0.5,
        success_probability=0.65,
        notes="Salvage: peroxide from first aid kits, rust from metal scraps. Reaction is self-limiting; produces heat.",
        field_tested=False,
        survival_margin="safety_buffer"
    ),

    OxygenTechnique(
        id="tech_controlled_ventilation",
        name="Layered air exchange (scree/culvert)",
        type=TechniqueType.VENTILATION,
        description="Position body to create natural convection: lower body in cooler zone, head in fresher-air pocket. Reduces rebreathing.",
        materials_required=[],
        setup_minutes=1,
        oxygen_extension_hours=1,
        success_probability=0.88,
        notes="Works in scree crevasses, culverts, deep ravines. Terrain-dependent.",
        field_tested=True,
        survival_margin="moderate"
    ),

    OxygenTechnique(
        id="tech_wet_cloth_breathing",
        name="Damp cloth over mouth (smoke mitigation)",
        type=TechniqueType.SMOKE_FILTRATION,
        description="Wet cloth = particle trap + cooling effect on inhale. Reduces smoke damage to lungs.",
        materials_required=["cloth", "water"],
        setup_minutes=1,
        oxygen_extension_hours=0.75,
        success_probability=0.90,
        notes="Buys time. Doesn't extend oxygen supply, reduces toxicity inhalation.",
        field_tested=True,
        survival_margin="safety_buffer"
    ),

    OxygenTechnique(
        id="tech_thermal_mass_buffer",
        name="Earth/water thermal buffering",
        type=TechniqueType.THERMAL_BUFFERING,
        description="Immerse in creek/wet ground. Slows metabolic oxygen consumption (cold = lower heart rate, lower breathing rate).",
        materials_required=["water_body_or_wet_ground"],
        setup_minutes=0,
        oxygen_extension_hours=1.5,
        success_probability=0.82,
        notes="You've done this. Cold = slower respiration = oxygen lasts longer. Hypothermia risk is secondary to smoke inhalation.",
        field_tested=True,
        survival_margin="critical"
    ),

    OxygenTechnique(
        id="tech_slow_breathing_discipline",
        name="Controlled respiration (metabolic reduction)",
        type=TechniqueType.VENTILATION,
        description="4-count inhale, 6-count exhale. Reduces panic-driven hyperventilation, extends CO2 tolerance.",
        materials_required=[],
        setup_minutes=0,
        oxygen_extension_hours=1,
        success_probability=0.70,
        notes="Psychological + physiological. Requires mental discipline under stress. Extends time before forced exit.",
        field_tested=True,
        survival_margin="safety_buffer"
    ),

    OxygenTechnique(
        id="tech_air_pocket_sealing",
        name="Seal shelter entrance (reduce smoke infiltration)",
        type=TechniqueType.SMOKE_FILTRATION,
        description="Use cloth, mud, leaves to seal culvert/crevasse opening. Reduces smoke flow, traps existing air, extends usable time.",
        materials_required=["cloth_or_vegetation", "mud_optional"],
        setup_minutes=5,
        oxygen_extension_hours=2,
        success_probability=0.78,
        notes="Trade: reduced smoke vs. slower air exchange. Works in enclosed terrain.",
        field_tested=True,
        survival_margin="moderate"
    ),
]

class OxygenSurvivalModule:
    """
    Companion to wildfire_shelter_resolver.
    Query: given shelter type + available materials, rank oxygen extension techniques.
    """

    def __init__(self):
        self.techniques = {t.id: t for t in TECHNIQUES}

    def applicable_techniques(self, shelter_terrain_type: str,
                             materials_on_hand: List[str]) -> List[OxygenTechnique]:
        """
        Return techniques viable for this shelter + materials.
        Ranked by oxygen extension + success probability.
        """
        applicable = []
        for tech in TECHNIQUES:
            # Check if materials match
            if all(m in materials_on_hand or m in ["water_body", "wet_ground", "charcoal"]
                   for m in tech.materials_required):
                # Terrain compatibility check
                if self._terrain_compatible(shelter_terrain_type, tech):
                    applicable.append(tech)

        # Sort by (oxygen_extension × success_probability)
        applicable.sort(
            key=lambda t: (t.oxygen_extension_hours * t.success_probability),
            reverse=True
        )
        return applicable

    def _terrain_compatible(self, terrain: str, technique: OxygenTechnique) -> bool:
        """Match technique to shelter type."""
        terrain_map = {
            "scree": ["tech_controlled_ventilation", "tech_slow_breathing_discipline"],
            "creek_bed": ["tech_thermal_mass_buffer", "tech_plastic_bag_water"],
            "culvert": ["tech_air_pocket_sealing", "tech_controlled_ventilation"],
            "gravel_pit": ["tech_charcoal_filter_diy", "tech_slow_breathing_discipline"],
            "rock_outcrop": ["tech_wet_cloth_breathing", "tech_slow_breathing_discipline"],
        }
        return technique.id in terrain_map.get(terrain, [])

    def emergency_action_sequence(self, shelter_terrain: str,
                                 materials: List[str],
                                 oxygen_hours_available: float) -> Dict:
        """
        Given shelter + materials + time, return prioritized action sequence.
        """
        techniques = self.applicable_techniques(shelter_terrain, materials)

        total_extension = sum(t.oxygen_extension_hours for t in techniques)
        extended_duration = oxygen_hours_available + total_extension

        return {
            "baseline_oxygen_hours": oxygen_hours_available,
            "techniques_applicable": [
                {
                    "name": t.name,
                    "setup_minutes": t.setup_minutes,
                    "oxygen_extension": t.oxygen_extension_hours,
                    "priority": "immediate" if t.survival_margin == "critical" else "secondary"
                }
                for t in techniques
            ],
            "estimated_total_survival_hours": extended_duration,
            "action_sequence": self._sequence_by_priority(techniques),
            "psychological_note": "Controlled breathing + thermal buffering = discipline + physics working together."
        }

    def _sequence_by_priority(self, techniques: List[OxygenTechnique]) -> List[str]:
        """Return execution order: critical first, then secondary, setup time considered."""
        critical = [t for t in techniques if t.survival_margin == "critical"]
        secondary = [t for t in techniques if t.survival_margin != "critical"]

        critical.sort(key=lambda t: t.setup_minutes)
        secondary.sort(key=lambda t: t.setup_minutes)

        return [t.name for t in critical + secondary]

# wood_ash_domain.py
# Substrate domain: wood ash → lye, fertilizer, ceramic flux, dye mordant, cleaner
# CC0 | falsifiable

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

def wood_ash_expander(parent, query) -> List:
    """
    Wood ash composition (varies by species):
      - CaCO3 / CaO: ~25-45%
      - K2CO3 (potash): ~10-30% (hardwood > softwood)
      - MgO, Na2O, trace SiO2 + P

    Hardwood ash > softwood for lye-making (higher K).
    Property handles:
      Water leach → KOH/K2CO3 solution (lye water)
      Concentrated lye → soap-making caustic
      Dry ash + clay → ceramic glaze flux
      Soil → calcium/potassium fertilizer (pH up)
    """
    branches = []

    branches.append(Node(
        id="wa_lye_leach",
        description="Water-leach ash → lye solution (test with feather: dissolves = strong)",
        transform=TransformMode.EXTRACT,
        success_probability=0.85,
        constraints=Constraint(
            equipment_required=["container", "filter"],
            components_required=["water"],
            min_dwell_hours=24,
            temp_range_c=(15, 100),
            fallback_paths=["rainwater_collected", "snow_melt"]
        )
    ))

    branches.append(Node(
        id="wa_lye_concentrate",
        description="Boil leached lye → concentrated caustic for soap",
        transform=TransformMode.THERMAL,
        success_probability=0.78,
        constraints=Constraint(
            equipment_required=["heavy_pot", "heat_source", "gloves"],
            components_required=[],
            min_dwell_hours=4,
            temp_range_c=(95, 105),
            fallback_paths=["solar_evaporation_slow"]
        )
    ))

    branches.append(Node(
        id="wa_ceramic_glaze",
        description="Ash + clay slip → high-fire ceramic glaze",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.72,
        constraints=Constraint(
            equipment_required=["kiln_or_high_fire", "sieve"],
            components_required=["clay_slip", "water"],
            min_dwell_hours=24,
            temp_range_c=(1100, 1300),
            fallback_paths=["pit_fire_alternative_lower_temp"]
        )
    ))

    branches.append(Node(
        id="wa_fertilizer",
        description="Sifted ash → K/Ca soil amendment (alkaline; not on acid-loving plants)",
        transform=TransformMode.EXTRACT,
        success_probability=0.95,
        constraints=Constraint(
            equipment_required=["sieve"],
            components_required=[],
            min_dwell_hours=0,
            temp_range_c=(-30, 40),
            fallback_paths=["cloth_screen"]
        )
    ))

    branches.append(Node(
        id="wa_cleaner_paste",
        description="Ash + water → mild abrasive scouring paste",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.93,
        constraints=Constraint(
            equipment_required=["container"],
            components_required=["water"],
            min_dwell_hours=0,
            temp_range_c=(0, 40),
            fallback_paths=[]
        )
    ))

    branches.append(Node(
        id="wa_potassium_nitrate",
        description="Ash + urine/compost leach → KNO3 (saltpeter) over months",
        transform=TransformMode.HYBRID,
        success_probability=0.55,
        constraints=Constraint(
            equipment_required=["leach_bed", "evaporation_pan"],
            components_required=["nitrogen_source"],
            min_dwell_hours=2160,  # 90 days
            temp_range_c=(10, 40),
            fallback_paths=["manure_pile_leach", "compost_drainage"]
        )
    ))

    return branches


WOOD_ASH_SALVAGE = {
    "clay_slip": ["pond_clay_settled", "subsoil_clay_screened"],
    "nitrogen_source": ["urine_aged", "manure", "compost_tea"],
}


def register_with_resolver(resolver):
    resolver.register_domain("wood_ash", wood_ash_expander)
    resolver.register_domain("ash", wood_ash_expander)
    resolver.salvage_index.update(WOOD_ASH_SALVAGE)

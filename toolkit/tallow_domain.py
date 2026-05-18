# tallow_domain.py
# Substrate domain: rendered animal fat → soap, candles, lube, food, leather treatment
# CC0 | falsifiable

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

def tallow_expander(parent, query) -> List:
    """
    Tallow composition:
      - Triglycerides ~99%: saturated (stearic, palmitic) + unsaturated (oleic)
      - Melting point ~40-50°C
      - Saponification value ~195-200 mg KOH/g

    Property handles:
      + Lye → soap (saponification)
      + Wax/wick → candle
      + Beeswax/oil → leather conditioner
      + Cold storage → bearing grease base
    """
    branches = []

    branches.append(Node(
        id="tw_soap_cold",
        description="Tallow + lye → cold-process soap (4wk cure)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.88,
        constraints=Constraint(
            equipment_required=["mixer", "mold", "scale", "thermometer"],
            components_required=["lye", "water"],
            min_dwell_hours=672,  # 28 day cure
            temp_range_c=(20, 50),
            fallback_paths=["wood_ash_lye_concentrated", "stick_blender_DIY"]
        )
    ))

    branches.append(Node(
        id="tw_soap_hot",
        description="Tallow + lye, boiled → hot-process soap (use in 24h)",
        transform=TransformMode.HYBRID,
        success_probability=0.82,
        constraints=Constraint(
            equipment_required=["heavy_pot", "heat_source", "mixer"],
            components_required=["lye", "water"],
            min_dwell_hours=24,
            temp_range_c=(80, 100),
            fallback_paths=["wood_ash_lye"]
        )
    ))

    branches.append(Node(
        id="tw_candle",
        description="Tallow + wick → candle (smoky but functional)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.95,
        constraints=Constraint(
            equipment_required=["mold_or_dipping_vessel", "heat_source"],
            components_required=["wick_cotton"],
            min_dwell_hours=2,
            temp_range_c=(50, 90),
            fallback_paths=["braided_cotton_string", "natural_fiber_twist"]
        )
    ))

    branches.append(Node(
        id="tw_grease_base",
        description="Tallow + graphite or clay → bearing/axle grease",
        transform=TransformMode.HYBRID,
        success_probability=0.78,
        constraints=Constraint(
            equipment_required=["mixer", "heat_source"],
            components_required=["graphite_or_bentonite"],
            min_dwell_hours=2,
            temp_range_c=(40, 80),
            fallback_paths=["pencil_lead_crushed", "clay_kiln_dried_powdered"]
        )
    ))

    branches.append(Node(
        id="tw_leather_dressing",
        description="Tallow + beeswax + pine pitch → leather/wood conditioner",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.90,
        constraints=Constraint(
            equipment_required=["heat_source", "container"],
            components_required=["beeswax", "pine_pitch"],
            min_dwell_hours=1,
            temp_range_c=(60, 100),
            fallback_paths=["paraffin_substitute", "any_resin_substitute"]
        )
    ))

    branches.append(Node(
        id="tw_food_preservation",
        description="Tallow seal over cooked meat → confit (months-long storage)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.92,
        constraints=Constraint(
            equipment_required=["sealed_jar", "heat_source"],
            components_required=["salt", "cooked_protein"],
            min_dwell_hours=6,
            temp_range_c=(60, 90),
            fallback_paths=["lard_substitute"]
        )
    ))

    return branches


TALLOW_SALVAGE = {
    "wick_cotton": ["cotton_string_braided", "old_tshirt_strips_twisted"],
    "graphite_or_bentonite": [
        "pencil_lead_crushed", "carbon_rod_DCell_crushed",
        "bentonite_clay_powdered", "kiln_dried_clay_powdered"
    ],
    "beeswax": ["candle_stub", "honeycomb_rendered"],
}


def register_with_resolver(resolver):
    resolver.register_domain("tallow", tallow_expander)
    resolver.register_domain("rendered_fat", tallow_expander)
    resolver.register_domain("lard", tallow_expander)
    resolver.salvage_index.update(TALLOW_SALVAGE)

# stone_domain.py
# Substrate domain: limestone, sandstone, gneiss → cement, mortar, glass, aggregate, lime
# CC0 | falsifiable

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

def stone_expander(parent, query) -> List:
    """
    Stone composition + processing:
      Limestone (CaCO3): heating → quicklime (CaO) + CO2
      Sandstone (SiO2 + binder): grinding → silica sand, or fuse for glass
      Gneiss (varied, typically feldspar/quartz mix): crush → aggregate or flux

    Property handles:
      Heat → decomposition (limestone → lime)
      Grinding → particle size reduction (aggregate, cement powder)
      Fusion → glass (high temp, silica dominant)
      Hydration → mortar/concrete (quicklime + water + sand)
    """
    branches = []

    branches.append(Node(
        id="stone_quicklime_thermal",
        description="Heat limestone → quicklime (CaO) + CO2 gas",
        transform=TransformMode.THERMAL,
        success_probability=0.85,
        constraints=Constraint(
            equipment_required=["kiln_or_high_heat", "crucible_or_chamber"],
            components_required=[],
            min_dwell_hours=8,
            temp_range_c=(900, 1200),
            fallback_paths=["wood_fire_pit_lined", "rocket_mass_heater"]
        )
    ))

    branches.append(Node(
        id="stone_slaked_lime",
        description="Quicklime + water → slaked lime (Ca(OH)2) + heat",
        transform=TransformMode.HYBRID,
        success_probability=0.92,
        constraints=Constraint(
            equipment_required=["container", "water_source"],
            components_required=["quicklime", "water"],
            min_dwell_hours=2,
            temp_range_c=(20, 60),
            fallback_paths=["rain_water", "snow_melt"]
        )
    ))

    branches.append(Node(
        id="stone_lime_mortar",
        description="Slaked lime + sand + water → mortar (masonry)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.90,
        constraints=Constraint(
            equipment_required=["mixer_or_trough", "shovel"],
            components_required=["slaked_lime", "sand", "water"],
            min_dwell_hours=24,
            temp_range_c=(5, 35),
            fallback_paths=["hand_mixing", "foot_mixing"]
        )
    ))

    branches.append(Node(
        id="stone_concrete_basic",
        description="Lime + sand + gravel + water → basic concrete (low strength)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.78,
        constraints=Constraint(
            equipment_required=["mixer", "forms"],
            components_required=["slaked_lime", "sand", "gravel", "water"],
            min_dwell_hours=336,  # 14 days curing
            temp_range_c=(10, 30),
            fallback_paths=["roman_pozzolana_ash_additive"]
        )
    ))

    branches.append(Node(
        id="stone_silica_sand",
        description="Crush/grind sandstone → pure silica sand (glass or casting)",
        transform=TransformMode.EXTRACT,
        success_probability=0.88,
        constraints=Constraint(
            equipment_required=["grinder_or_mortar_pestle", "sieve"],
            components_required=[],
            min_dwell_hours=3,
            temp_range_c=(0, 50),
            fallback_paths=["rock_tumbler", "stone_mill"]
        )
    ))

    branches.append(Node(
        id="stone_glass_fusion",
        description="Heat silica sand + flux → molten glass → cool to solid",
        transform=TransformMode.THERMAL,
        success_probability=0.55,
        constraints=Constraint(
            equipment_required=["furnace_1700c_capable", "mold_or_form"],
            components_required=["silica_sand", "flux_soda_or_ash"],
            min_dwell_hours=12,
            temp_range_c=(1700, 1800),
            fallback_paths=["solar_furnace_parabolic_mirror"]
        )
    ))

    branches.append(Node(
        id="stone_aggregate",
        description="Crush stone → sized gravel/aggregate (fill, drainage)",
        transform=TransformMode.EXTRACT,
        success_probability=0.95,
        constraints=Constraint(
            equipment_required=["hammer", "sieve"],
            components_required=[],
            min_dwell_hours=2,
            temp_range_c=(-30, 50),
            fallback_paths=["rock_impact_method", "running_water_tumble"]
        )
    ))

    branches.append(Node(
        id="stone_pozzolana_cement",
        description="Ash + slaked lime → pozzolanic cement (Roman method, slow set)",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.72,
        constraints=Constraint(
            equipment_required=["mixer"],
            components_required=["volcanic_ash_or_wood_ash", "slaked_lime", "water"],
            min_dwell_hours=504,  # 21 days hydration
            temp_range_c=(15, 30),
            fallback_paths=["charcoal_dust_substitute"]
        )
    ))

    return branches


STONE_SALVAGE = {
    "flux_soda_or_ash": [
        "wood_ash_collected", "seaweed_ash_burned",
        "sodium_carbonate_from_salt_leach"
    ],
    "volcanic_ash_or_wood_ash": [
        "wood_ash_from_fire_pit", "charcoal_dust_ground",
        "clay_diatomaceous_deposit"
    ],
}


def register_with_resolver(resolver):
    resolver.register_domain("limestone", stone_expander)
    resolver.register_domain("sandstone", stone_expander)
    resolver.register_domain("gneiss", stone_expander)
    resolver.register_domain("stone", stone_expander)
    resolver.salvage_index.update(STONE_SALVAGE)

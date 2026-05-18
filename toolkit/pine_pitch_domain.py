# pine_pitch_domain.py
# Substrate domain: pine pitch / resin → adhesives, sealants, waterproofing, fire-starting
# CC0 | falsifiable

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

def pine_pitch_expander(parent, query) -> List:
    """
    Pine pitch composition:
      - Rosin (abietic acid + isomers): ~70%, brittle when cured
      - Turpentine (terpenes): ~20%, volatile solvent
      - Water + debris: ~10%

    Property handles:
      Heat → softens, flows, mixes with fillers
      Cooling + filler → tunes brittleness (charcoal, ash, beeswax, fat)
      Distillation → separates rosin (solid) from turpentine (liquid solvent)
    """
    branches = []

    branches.append(Node(
        id="pp_raw_glue",
        description="Melt raw pitch + charcoal dust + tallow → flexible glue",
        transform=TransformMode.HYBRID,
        success_probability=0.88,
        constraints=Constraint(
            equipment_required=["heat_source", "metal_can"],
            components_required=["charcoal_dust", "tallow_or_fat"],
            min_dwell_hours=1,
            temp_range_c=(80, 180),
            fallback_paths=["wood_ash_substitute", "any_rendered_fat"]
        )
    ))

    branches.append(Node(
        id="pp_distill_turpentine",
        description="Distill pitch → turpentine (solvent) + rosin (solid)",
        transform=TransformMode.THERMAL,
        success_probability=0.65,
        constraints=Constraint(
            equipment_required=["still_setup", "heat_source", "condenser"],
            components_required=["water_for_cooling"],
            min_dwell_hours=6,
            temp_range_c=(150, 250),
            fallback_paths=["copper_pipe_coil_DIY", "pot_lid_with_tube"]
        )
    ))

    branches.append(Node(
        id="pp_pitch_sealant",
        description="Pitch + beeswax → flexible waterproof sealant",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.92,
        constraints=Constraint(
            equipment_required=["heat_source", "container"],
            components_required=["beeswax"],
            min_dwell_hours=1,
            temp_range_c=(70, 130),
            fallback_paths=["tallow_50pct_substitute", "paraffin_wax"]
        )
    ))

    branches.append(Node(
        id="pp_rosin_flux",
        description="Refined rosin → soldering flux + electrical insulator",
        transform=TransformMode.EXTRACT,
        success_probability=0.80,
        constraints=Constraint(
            equipment_required=["filter", "heat_source"],
            components_required=["solvent_alcohol_or_turp"],
            min_dwell_hours=3,
            temp_range_c=(60, 100),
            fallback_paths=["ferment_wash_alcohol", "use_turpentine_self"]
        )
    ))

    branches.append(Node(
        id="pp_torch_fuel",
        description="Pitch-soaked cordage → long-burn torch / fire starter",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.95,
        constraints=Constraint(
            equipment_required=["heat_source", "dipping_vessel"],
            components_required=["cordage_or_fabric"],
            min_dwell_hours=1,
            temp_range_c=(80, 150),
            fallback_paths=["any_natural_fiber"]
        )
    ))

    return branches


PINE_PITCH_SALVAGE = {
    "charcoal_dust": ["fire_pit_screened", "burnt_wood_crushed"],
    "tallow_or_fat": ["rendered_animal_fat", "lard", "bacon_grease"],
    "beeswax": ["candle_stub_melted", "rendered_honeycomb"],
    "cordage_or_fabric": ["cotton_string", "natural_fiber_scrap", "jute"],
    "solvent_alcohol_or_turp": ["fermented_wash_distilled", "self_distilled_turpentine"]
}


def register_with_resolver(resolver):
    resolver.register_domain("pine_pitch", pine_pitch_expander)
    resolver.register_domain("pine_resin", pine_pitch_expander)
    resolver.salvage_index.update(PINE_PITCH_SALVAGE)

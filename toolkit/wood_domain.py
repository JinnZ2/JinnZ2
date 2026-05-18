# wood_domain.py
# Substrate domain: wood species → cutting boards, boats, structural, tools
# CC0 | falsifiable | material-property driven

from dataclasses import dataclass

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

@dataclass
class WoodSpecies:
    """Wood properties relevant to application."""
    name: str
    density_lbsper_cuft: float  # Density affects strength + weight
    hardness_janka: int  # Janka scale: 0–4000+
    rot_resistance: str  # "poor", "moderate", "excellent"
    bend_rating: str  # "low_bend", "moderate_bend", "excellent_bend"
    steam_curvature: bool  # Can it hold steam-bent curves?
    grain_character: str  # "fine", "coarse", "interlocked"
    workability: str  # "easy", "moderate", "difficult"
    color_description: str
    regional_availability: str  # Where found in Upper Midwest

def wood_expander(parent, query) -> List:
    """
    Map target_property (cutting board, lightweight boat, deep-water boat,
    structural beam, tool handle) to optimal wood species + processing.

    Wood selection logic:
      Cutting board → rot-resistant, fine grain, non-toxic
      Lightweight boat (river) → low density, moderate strength
      Deep-water boat (Superior) → high density, excellent rot-resistance, curves well
      Structural → high density, straight grain
      Tool handle → moderate density, bend-able, impact-resistant
    """
    branches = []

    # CUTTING BOARD path
    if query.target_property in ("cutting_board", "food_contact"):
        branches.append(Node(
            id="wood_rosewood_board",
            description="Rosewood (density 3.5+): dense, rot-proof, fine grain, food-safe",
            transform=TransformMode.EXTRACT,
            success_probability=0.75,  # Availability limited
            constraints=Constraint(
                equipment_required=["saw", "planer", "sander"],
                components_required=["rosewood_log_or_salvage"],
                min_dwell_hours=80,  # Drying + milling
                temp_range_c=(15, 25),
                fallback_paths=["walnut_black", "maple_hard"]
            )
        ))

        branches.append(Node(
            id="wood_walnut_board",
            description="Black walnut: excellent rot-resistance, fine grain, workable",
            transform=TransformMode.EXTRACT,
            success_probability=0.88,
            constraints=Constraint(
                equipment_required=["saw", "planer", "sander"],
                components_required=["walnut_log"],
                min_dwell_hours=480,  # Slow dry to prevent checking
                temp_range_c=(12, 22),
                fallback_paths=[]
            )
        ))

    # LIGHTWEIGHT RIVER BOAT path
    elif query.target_property in ("lightweight_boat", "river_boat"):
        branches.append(Node(
            id="wood_cedar_boat",
            description="Cedar (density 0.4–0.5): extremely light, rot-resistant, workable curves",
            transform=TransformMode.HYBRID,
            success_probability=0.82,
            constraints=Constraint(
                equipment_required=["saw", "steam_box", "forms", "clamps"],
                components_required=["cedar_planking", "steam_heat"],
                min_dwell_hours=12,  # Steam-bending + drying
                temp_range_c=(60, 100),
                fallback_paths=["spruce_engelmann"]
            )
        ))

        branches.append(Node(
            id="wood_aspen_boat",
            description="Aspen (density 0.38): very light, fast-growing, moderate rot-resistance",
            transform=TransformMode.HYBRID,
            success_probability=0.72,
            constraints=Constraint(
                equipment_required=["steam_box", "forms"],
                components_required=["aspen_stock"],
                min_dwell_hours=10,
                temp_range_c=(60, 100),
                fallback_paths=["poplar"]
            )
        ))

    # DEEP-WATER BOAT (Superior) path
    elif query.target_property in ("deep_water_boat", "ocean_boat", "heavy_duty_boat"):
        branches.append(Node(
            id="wood_oak_boat",
            description="Oak (density 0.75–0.85): excellent rot-resistance, curves under steam, strong",
            transform=TransformMode.HYBRID,
            success_probability=0.85,
            constraints=Constraint(
                equipment_required=["steam_box", "heavy_forms", "clamps"],
                components_required=["oak_log_or_salvage"],
                min_dwell_hours=16,  # Longer steam time for thick stock
                temp_range_c=(70, 120),
                fallback_paths=["ash_white"]
            )
        ))

        branches.append(Node(
            id="wood_hickory_boat",
            description="Hickory (density 0.8): high strength, excellent impact resistance, curves well",
            transform=TransformMode.HYBRID,
            success_probability=0.78,
            constraints=Constraint(
                equipment_required=["steam_box", "heavy_forms"],
                components_required=["hickory_stock"],
                min_dwell_hours=14,
                temp_range_c=(70, 110),
                fallback_paths=["ash"]
            )
        ))

    # STRUCTURAL / BEAM path
    elif query.target_property in ("beam", "structural", "load_bearing"):
        branches.append(Node(
            id="wood_douglas_fir_beam",
            description="Douglas fir: high strength-to-weight, straight grain, structural grade",
            transform=TransformMode.EXTRACT,
            success_probability=0.88,
            constraints=Constraint(
                equipment_required=["saw", "debarker"],
                components_required=["fir_log"],
                min_dwell_hours=240,  # Slow dry to prevent warping
                temp_range_c=(15, 25),
                fallback_paths=["spruce_sitka"]
            )
        ))

        branches.append(Node(
            id="wood_oak_beam",
            description="Oak: maximum density + strength, but slow-drying to prevent checking",
            transform=TransformMode.EXTRACT,
            success_probability=0.75,
            constraints=Constraint(
                equipment_required=["saw", "kiln_or_slow_dry"],
                components_required=["oak_log"],
                min_dwell_hours=720,  # 30+ days drying for thick stock
                temp_range_c=(15, 25),
                fallback_paths=[]
            )
        ))

    # TOOL HANDLE path
    elif query.target_property in ("tool_handle", "axe_handle", "impact_tool"):
        branches.append(Node(
            id="wood_hickory_handle",
            description="Hickory: impact-resistant, curves slightly, traditional axe/hammer",
            transform=TransformMode.EXTRACT,
            success_probability=0.90,
            constraints=Constraint(
                equipment_required=["saw", "shaper", "sandpaper"],
                components_required=["hickory_straight_grain"],
                min_dwell_hours=120,
                temp_range_c=(15, 25),
                fallback_paths=[]
            )
        ))

        branches.append(Node(
            id="wood_ash_handle",
            description="Ash: flexible, light, excellent shock absorption",
            transform=TransformMode.EXTRACT,
            success_probability=0.88,
            constraints=Constraint(
                equipment_required=["saw", "shaper"],
                components_required=["ash_white"],
                min_dwell_hours=100,
                temp_range_c=(15, 25),
                fallback_paths=[]
            )
        ))

    return branches


WOOD_SALVAGE = {
    "rosewood_log_or_salvage": [
        "salvaged_rosewood_furniture", "discarded_instrument_blanks",
        "urban_tree_removal_yards"
    ],
    "steam_heat": ["fire_box", "rocket_mass_heater", "boiling_water_immersion"],
    "oak_log_or_salvage": ["fallen_tree", "mill_offcuts", "salvage_yards"],
}


def register_with_resolver(resolver):
    resolver.register_domain("wood", wood_expander)
    resolver.register_domain("cedar", wood_expander)
    resolver.register_domain("oak", wood_expander)
    resolver.register_domain("walnut", wood_expander)
    resolver.register_domain("hickory", wood_expander)
    resolver.salvage_index.update(WOOD_SALVAGE)

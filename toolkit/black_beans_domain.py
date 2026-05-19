# black_beans_domain.py
# Substrate domain: black beans → lubricant candidates
# CC0 | falsifiable | mobile-readable

from salvage_chemistry_resolver import (
    Node, Query, TransformMode, NodeStatus, Constraint
)
from typing import List

def black_beans_expander(parent: Node, query: Query) -> List[Node]:
    """
    Blowfish-spike from black beans node.
    Each branch = distinct transformation strategy toward lubricant.

    Black bean composition (dry, ~per 100g):
      - lipid: ~1.4g (low, but extractable)
      - protein: ~21g (can polymerize)
      - starch: ~62g (fermentable → alcohols, acids)
      - saponins: present (natural surfactants)
      - phospholipids: trace (lubricity precursors)

    Lubricant viability paths:
      1. Lipid extraction → low-grade oil base
      2. Starch fermentation → glycerol-bearing slurry
      3. Protein denaturation → grease thickener
      4. Saponin extraction → water-based lubricant
      5. Pyrolysis → carbon + oils (high-temp path)
      6. Hybrid: ferment first, then extract
    """

    branches = []

    # BRANCH 1: Cold lipid extraction (solvent or press)
    branches.append(Node(
        id="bb_lipid_extract",
        description="Press/solvent extract lipids → base oil stock",
        transform=TransformMode.EXTRACT,
        success_probability=0.45,  # Low lipid yield is the bottleneck
        constraints=Constraint(
            equipment_required=["press", "filter"],
            components_required=[],
            min_dwell_hours=4,
            temp_range_c=(-10, 80),
            fallback_paths=["mortar+cloth", "boil+skim"]
        )
    ))

    # BRANCH 2: Lacto-fermentation → glycerol + organic acids
    branches.append(Node(
        id="bb_lacto_ferment",
        description="Lacto-ferment cooked beans → acid+glycerol slurry",
        transform=TransformMode.FERMENT,
        success_probability=0.78,  # Reliable, time-flexible
        constraints=Constraint(
            equipment_required=["sealed_vessel"],
            components_required=["salt", "starter_culture"],
            min_dwell_hours=336,  # 14 days
            temp_range_c=(15, 30),
            fallback_paths=["wild_ferment", "whey_starter"]
        )
    ))

    # BRANCH 3: Saponin extraction (water-based surfactant lube)
    branches.append(Node(
        id="bb_saponin_extract",
        description="Boil + reduce → saponin-rich water lubricant",
        transform=TransformMode.EXTRACT,
        success_probability=0.82,  # Beans have measurable saponins
        constraints=Constraint(
            equipment_required=["pot", "heat_source"],
            components_required=["water"],
            min_dwell_hours=6,
            temp_range_c=(60, 100),
            fallback_paths=["cold_soak_72h"]
        )
    ))

    # BRANCH 4: Pyrolysis → bean tar + biochar
    branches.append(Node(
        id="bb_pyrolysis",
        description="Anaerobic pyrolysis → tar + carbon black",
        transform=TransformMode.THERMAL,
        success_probability=0.55,  # Yields complex mix, needs separation
        constraints=Constraint(
            equipment_required=["sealed_retort", "high_heat"],
            components_required=[],
            min_dwell_hours=8,
            temp_range_c=(300, 500),
            fallback_paths=["wood_stove_modification"]
        )
    ))

    # BRANCH 5: Hybrid ferment → extract (highest yield path)
    branches.append(Node(
        id="bb_ferment_extract",
        description="Ferment 14d → press → separate oil/aqueous",
        transform=TransformMode.HYBRID,
        success_probability=0.85,  # Fermentation breaks cell walls, boosts extract yield
        constraints=Constraint(
            equipment_required=["sealed_vessel", "press", "separator"],
            components_required=["salt", "starter_culture"],
            min_dwell_hours=360,  # 15 days total
            temp_range_c=(15, 80),
            fallback_paths=["gravity_separate", "centrifuge_diy"]
        )
    ))

    # BRANCH 6: Protein-thickened grease
    branches.append(Node(
        id="bb_protein_grease",
        description="Denature protein + bind to oil → grease consistency",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.62,
        constraints=Constraint(
            equipment_required=["mixer", "heat_source"],
            components_required=["base_oil", "lye_or_acid"],
            min_dwell_hours=12,
            temp_range_c=(70, 120),
            fallback_paths=["wood_ash_lye", "vinegar_acid"]
        )
    ))

    return branches


def attach_secondary_expanders():
    """
    Each branch above can blowfish further.
    Example: bb_ferment_extract → child nodes for separation method.
    Plug in additional expanders here as you map deeper.
    """
    pass


# --- Salvage index for missing components ---
SALVAGE_PATHS = {
    "starter_culture": ["sauerkraut_juice", "whey", "wild_ferment_24h"],
    "lye_or_acid": ["wood_ash_leachate", "fermented_vinegar", "battery_acid_diluted"],
    "base_oil": ["used_motor_oil_filtered", "rendered_tallow", "linseed_pressed"],
    "salt": ["roadside_road_salt_filtered", "wood_ash_potassium"],
    "filter": ["cotton_cloth", "sand_charcoal_layer", "coffee_filter_stack"],
    "press": ["bottle_jack+plates", "lever+fulcrum", "screw_clamp"],
    "starter_culture": ["any_active_ferment", "yogurt_whey", "kombucha_dregs"]
}


# --- Registration ---
def register_with_resolver(resolver):
    resolver.register_domain("black_beans", black_beans_expander)
    resolver.salvage_index.update(SALVAGE_PATHS)

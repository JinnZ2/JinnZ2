# battery_domain.py
# Substrate domain: metals + electrolyte → battery assembly
# CC0 | falsifiable | mobile-readable

from salvage_chemistry_resolver import (
    Node, Query, TransformMode, NodeStatus, Constraint
)
from typing import List

def battery_expander(parent: Node, query: Query) -> List[Node]:
    """
    Blowfish-spike: metal feedstock → battery topology branches.

    Electrochemistry basics:
      Cell voltage = E_cathode - E_anode (standard reduction potentials)

      Standard reduction potentials (V vs SHE):
        Cu²⁺ + 2e⁻ → Cu      = +0.34 V
        2H⁺ + 2e⁻ → H₂        =  0.00 V
        Zn²⁺ + 2e⁻ → Zn       = -0.76 V
        Al³⁺ + 3e⁻ → Al       = -1.66 V
        O₂ + 2H₂O + 4e⁻ → 4OH⁻ = +0.40 V (air cathode in alkaline)

    Available pairs from feedstock (Al, Cu, Zn, lye):
      Zn || Cu  → ~1.10 V  (classic galvanic, reliable)
      Al || Cu  → ~2.00 V  (high V, Al passivates - needs lye to break oxide)
      Al || air → ~2.71 V  (air cathode, needs porous carbon or copper mesh)
      Zn || air → ~1.65 V  (zinc-air, alkaline electrolyte)

    Electrode geometry:
      Thinner = higher surface area = higher current, faster depletion
      Thicker = more capacity, lower current
      Plates ~1-3mm typical for DIY; foil for high-current low-capacity
    """

    branches = []

    # BRANCH 1: Zn/Cu wet cell (most reliable, lowest skill floor)
    branches.append(Node(
        id="batt_zn_cu_wet",
        description="Zn anode || Cu cathode | salt or acid electrolyte | ~1.1V",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.90,
        constraints=Constraint(
            equipment_required=["file_or_grinder", "container", "wire"],
            components_required=["electrolyte_salt_or_acid"],
            min_dwell_hours=1,
            temp_range_c=(0, 60),
            fallback_paths=["seawater", "vinegar", "lemon_juice", "lye_diluted"]
        )
    ))

    # BRANCH 2: Al/Cu with lye (high voltage, lye breaks Al oxide layer)
    branches.append(Node(
        id="batt_al_cu_alkaline",
        description="Al anode || Cu cathode | KOH/NaOH electrolyte | ~2.0V",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.78,
        constraints=Constraint(
            equipment_required=["file_or_grinder", "container", "wire", "gloves"],
            components_required=["lye"],
            min_dwell_hours=2,
            temp_range_c=(10, 50),
            fallback_paths=["wood_ash_lye_strong", "drain_cleaner_NaOH"]
        )
    ))

    # BRANCH 3: Al-air cell (highest V, needs air cathode fabrication)
    branches.append(Node(
        id="batt_al_air",
        description="Al anode || air cathode (Cu mesh + carbon) | KOH | ~2.7V",
        transform=TransformMode.HYBRID,
        success_probability=0.62,
        constraints=Constraint(
            equipment_required=["mesh_fab", "carbon_source", "container"],
            components_required=["lye", "charcoal", "binder"],
            min_dwell_hours=6,
            temp_range_c=(10, 40),
            fallback_paths=["activated_charcoal_DIY", "pine_tar_binder"]
        )
    ))

    # BRANCH 4: Zn-air cell
    branches.append(Node(
        id="batt_zn_air",
        description="Zn anode || air cathode | KOH | ~1.65V",
        transform=TransformMode.HYBRID,
        success_probability=0.70,
        constraints=Constraint(
            equipment_required=["mesh_fab", "carbon_source", "container"],
            components_required=["lye", "charcoal"],
            min_dwell_hours=4,
            temp_range_c=(10, 40),
            fallback_paths=["copper_mesh", "stainless_screen"]
        )
    ))

    # BRANCH 5: Series stack (multi-cell for higher voltage)
    branches.append(Node(
        id="batt_zn_cu_series",
        description="Zn/Cu cells × N in series → N × 1.1V usable bank",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.85,
        constraints=Constraint(
            equipment_required=["file_or_grinder", "containers_multiple", "wire"],
            components_required=["electrolyte_salt_or_acid"],
            min_dwell_hours=3,
            temp_range_c=(0, 60),
            fallback_paths=["egg_carton_cells", "ice_cube_tray_cells"]
        )
    ))

    # BRANCH 6: Daniell-style with salt bridge (longest life, controlled chemistry)
    branches.append(Node(
        id="batt_daniell",
        description="Zn in ZnSO4 || Cu in CuSO4 | salt bridge | ~1.1V, stable discharge",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.68,
        constraints=Constraint(
            equipment_required=["two_containers", "salt_bridge_tube", "wire"],
            components_required=["zinc_sulfate", "copper_sulfate", "agar_or_cotton"],
            min_dwell_hours=12,
            temp_range_c=(15, 30),
            fallback_paths=["DIY_ZnSO4_from_Zn+H2SO4", "DIY_CuSO4_from_Cu+H2SO4"]
        )
    ))

    return branches


# --- Assembly specifications per branch ---
ASSEMBLY_SPECS = {
    "batt_zn_cu_wet": {
        "electrode_thickness_mm": (1.0, 3.0),
        "electrode_spacing_mm": (5, 20),
        "surface_area_cm2_per_amp": 100,  # approx; current capacity scales here
        "electrolyte_concentration": "saturated salt OR 5-10% acid",
        "connection": "soldered or clamped Cu wire to each electrode top",
        "container": "non-conductive (glass, HDPE, ceramic)"
    },
    "batt_al_cu_alkaline": {
        "electrode_thickness_mm": (0.5, 2.0),
        "electrode_spacing_mm": (3, 10),
        "surface_area_cm2_per_amp": 80,
        "electrolyte_concentration": "10-20% KOH or NaOH by mass",
        "connection": "Cu wire crimped; avoid Al-steel galvanic contact",
        "container": "polypropylene or HDPE (lye-resistant)",
        "warning": "H2 gas evolution - ventilate"
    },
    "batt_al_air": {
        "electrode_thickness_mm": (0.5, 1.5),
        "air_cathode_layers": ["Cu mesh", "activated carbon paste", "porous membrane"],
        "electrolyte_concentration": "15-25% KOH",
        "surface_area_cm2_per_amp": 50,
        "connection": "Cu wire to Al + Cu mesh tab",
        "container": "open-top or vented (air access required)"
    },
    "batt_zn_air": {
        "electrode_thickness_mm": (0.5, 2.0),
        "air_cathode_layers": ["Cu/SS mesh", "activated carbon", "MnO2 if available"],
        "electrolyte_concentration": "10-20% KOH",
        "surface_area_cm2_per_amp": 60,
        "container": "vented"
    },
    "batt_zn_cu_series": {
        "cell_count": "N (for V_total = N × 1.1)",
        "electrode_thickness_mm": (1.0, 3.0),
        "inter_cell_wire": "Cu, anode of next = cathode of prev",
        "isolation": "each cell electrically isolated, only series-wire connects"
    },
    "batt_daniell": {
        "electrode_thickness_mm": (1.0, 4.0),
        "salt_bridge": "U-tube of agar+KNO3 OR cotton soaked in KNO3",
        "electrolyte_zn_side": "ZnSO4 saturated",
        "electrolyte_cu_side": "CuSO4 saturated",
        "lifespan": "weeks to months with sealed cells"
    }
}


# --- Salvage paths specific to battery work ---
BATTERY_SALVAGE = {
    "electrolyte_salt_or_acid": [
        "table_salt_saturated", "seawater", "vinegar",
        "battery_acid_diluted_10x", "lemon_juice"
    ],
    "lye": [
        "wood_ash_leachate_concentrated", "drain_cleaner_NaOH_flake",
        "oven_cleaner_paste"
    ],
    "carbon_source": [
        "charcoal_crushed", "pencil_lead", "carbon_rod_from_dead_dcell",
        "graphite_lubricant_dried"
    ],
    "binder": [
        "pine_tar", "starch_paste", "PVA_glue_thinned", "egg_white"
    ],
    "wire": [
        "scavenged_house_wiring", "transformer_winding",
        "appliance_cord_stripped"
    ],
    "salt_bridge_tube": [
        "drinking_straw_filled_agar", "cotton_wick_soaked",
        "filter_paper_strip_soaked"
    ],
    "copper_sulfate": [
        "Cu_in_H2SO4_electrolyzed", "Cu_in_dilute_acid_with_H2O2"
    ],
    "zinc_sulfate": [
        "Zn_in_dilute_H2SO4", "Zn_in_battery_acid"
    ]
}


def get_assembly_spec(branch_id: str) -> dict:
    """Return geometry + wiring spec for chosen branch."""
    return ASSEMBLY_SPECS.get(branch_id, {})


def register_with_resolver(resolver):
    resolver.register_domain("aluminum", battery_expander)
    resolver.register_domain("copper", battery_expander)
    resolver.register_domain("zinc", battery_expander)
    resolver.salvage_index.update(BATTERY_SALVAGE)

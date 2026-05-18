# vegetation_compounds_domain.py
# Substrate domain: plant material → minerals, soil amendments, medicinal compounds
# CC0 | falsifiable | ethnobotanical + thermochemical

from salvage_chemistry_resolver import (
    Node, TransformMode, Constraint
)
from typing import List

def vegetation_expander(parent, query) -> List:
    """
    Plant-to-mineral/compound extraction via preparation methods.

    Key insight: preparation mode (ash burning, fermentation, decoction,
    maceration) determines what compound/mineral becomes bioavailable.

    Examples:
      Plantain leaves → compress juice → potassium salts + silica
      Grain chaff/hull → burn slow → wood ash (K, Ca, trace minerals)
      Comfrey → ferment → available phosphorus
      Bone char + wood ash + compost → mycorrhizal substrate
      Nettles → dry + steep → chelated minerals (Fe, Cu, Mn)
    """
    branches = []

    # BRANCH 1: Plantain → potassium-rich extract
    branches.append(Node(
        id="veg_plantain_mineral",
        description="Fresh plantain leaves → compress/squeeze → K-rich mineral water",
        transform=TransformMode.EXTRACT,
        success_probability=0.92,
        constraints=Constraint(
            equipment_required=["cloth", "press_or_weight"],
            components_required=["fresh_plantain_leaves"],
            min_dwell_hours=1,
            temp_range_c=(10, 30),
            fallback_paths=["hand_squeeze", "mortar_pestle"]
        )
    ))

    # BRANCH 2: Grain chaff → slow-burn ash (K, Ca, trace elements)
    branches.append(Node(
        id="veg_grain_ash_slow",
        description="Grain chaff/hull → slow-burn in pit → mineral-rich ash",
        transform=TransformMode.THERMAL,
        success_probability=0.88,
        constraints=Constraint(
            equipment_required=["fire_pit", "ash_collection_bed"],
            components_required=["grain_chaff_or_hull"],
            min_dwell_hours=4,
            temp_range_c=(400, 700),
            fallback_paths=["wood_stove", "controlled_burn"]
        )
    ))

    # BRANCH 3: Comfrey ferment → available phosphorus
    branches.append(Node(
        id="veg_comfrey_ferment",
        description="Comfrey leaves → pack + ferment 4-6wk → P-rich extract",
        transform=TransformMode.FERMENT,
        success_probability=0.85,
        constraints=Constraint(
            equipment_required=["sealed_vessel", "weight"],
            components_required=["comfrey_leaves", "salt"],
            min_dwell_hours=960,  # 40 days
            temp_range_c=(15, 25),
            fallback_paths=["sun_ferment_outdoor"]
        )
    ))

    # BRANCH 4: Nettles → steep for chelated minerals
    branches.append(Node(
        id="veg_nettle_infusion",
        description="Nettle leaves → dry + steep in hot water → Fe, Cu, Mn bioavailable",
        transform=TransformMode.EXTRACT,
        success_probability=0.94,
        constraints=Constraint(
            equipment_required=["pot", "heat_source", "filter"],
            components_required=["dried_nettle_leaves", "water"],
            min_dwell_hours=3,
            temp_range_c=(70, 100),
            fallback_paths=["cold_steep_overnight"]
        )
    ))

    # BRANCH 5: Seaweed → ash for trace minerals (iodine, potassium)
    branches.append(Node(
        id="veg_seaweed_ash",
        description="Dried seaweed → burn → iodine + K + trace mineral ash",
        transform=TransformMode.THERMAL,
        success_probability=0.82,
        constraints=Constraint(
            equipment_required=["fire_pit", "ash_collection"],
            components_required=["dried_seaweed"],
            min_dwell_hours=2,
            temp_range_c=(600, 800),
            fallback_paths=["low_fire_long_duration"]
        )
    ))

    # BRANCH 6: Wood ash + compost + bone char → mycorrhizal substrate
    branches.append(Node(
        id="veg_mycorrhizal_mix",
        description="Wood ash + mature compost + bone char → fungal-inoculated soil",
        transform=TransformMode.SYNTHESIZE,
        success_probability=0.78,
        constraints=Constraint(
            equipment_required=["mixer", "storage_bin"],
            components_required=["wood_ash", "mature_compost", "bone_char"],
            min_dwell_hours=504,  # 21 days colonization
            temp_range_c=(15, 25),
            fallback_paths=["pile_method_passive"]
        )
    ))

    # BRANCH 7: Plant material ash-cycling (burn → ash → soil → next plant)
    branches.append(Node(
        id="veg_ash_cycling",
        description="Dead plant material → burn → distribute ash → available Ca, K, P to soil",
        transform=TransformMode.THERMAL,
        success_probability=0.95,
        constraints=Constraint(
            equipment_required=["fire_source"],
            components_required=["crop_residue_or_yard_waste"],
            min_dwell_hours=2,
            temp_range_c=(400, 800),
            fallback_paths=["slow_compost_decomposition"]
        )
    ))

    # BRANCH 8: Kelp/bladderwrack → fermented biostimulant
    branches.append(Node(
        id="veg_kelp_biostim",
        description="Fresh kelp → ferment + salt → growth hormone + microbe inoculant",
        transform=TransformMode.FERMENT,
        success_probability=0.80,
        constraints=Constraint(
            equipment_required=["sealed_container"],
            components_required=["fresh_kelp_or_seaweed", "salt"],
            min_dwell_hours=720,  # 30 days
            temp_range_c=(15, 25),
            fallback_paths=["sun_ferment"]
        )
    ))

    # BRANCH 9: Dandelion → root ash (high K), leaf tea (Ca)
    branches.append(Node(
        id="veg_dandelion_fractionated",
        description="Dandelion root → burn → K-rich ash; leaf → tea → Ca-rich mineral water",
        transform=TransformMode.HYBRID,
        success_probability=0.90,
        constraints=Constraint(
            equipment_required=["digger", "fire", "pot", "drying_rack"],
            components_required=["fresh_dandelion"],
            min_dwell_hours=24,
            temp_range_c=(0, 100),
            fallback_paths=[]
        )
    ))

    # BRANCH 10: Hay tea → slow-release NPK (nitrogen from legume hay)
    branches.append(Node(
        id="veg_hay_tea",
        description="Legume hay (clover, alfalfa) → steep in water 24h → soluble N, P, K",
        transform=TransformMode.EXTRACT,
        success_probability=0.88,
        constraints=Constraint(
            equipment_required=["vessel", "cloth_bag"],
            components_required=["legume_hay", "water"],
            min_dwell_hours=24,
            temp_range_c=(15, 30),
            fallback_paths=["hot_water_accelerated"]
        )
    ))

    return branches


# --- Mineral/compound profiles per plant ---

PLANT_PROFILES = {
    "plantain": {
        "primary_extract": "potassium + silica",
        "preparation": "leaf compression or decoction",
        "soil_benefit": "K availability, silica for pest resistance",
        "yield_low": 0.1,  # kg mineral per kg fresh plant
    },
    "comfrey": {
        "primary_extract": "phosphorus + potassium",
        "preparation": "fermentation or decomposition",
        "soil_benefit": "P for flowering/fruiting, K for vigor",
        "yield_low": 0.08,
    },
    "nettle": {
        "primary_extract": "iron + copper + manganese (chelated)",
        "preparation": "dry + steep or ferment",
        "soil_benefit": "Trace minerals, N fixation partner",
        "yield_low": 0.15,
    },
    "seaweed": {
        "primary_extract": "iodine + potassium + trace minerals",
        "preparation": "dry + burn, or ferment fresh",
        "soil_benefit": "Broad mineral spectrum, iodine critical",
        "yield_low": 0.25,
    },
    "wood_ash": {
        "primary_extract": "calcium + potassium + magnesium",
        "preparation": "slow burn of hardwood",
        "soil_benefit": "pH buffer, base cation supply",
        "yield_low": 0.20,
    },
    "bone_char": {
        "primary_extract": "phosphorus + calcium + trace minerals",
        "preparation": "burn bones until white/charred",
        "soil_benefit": "P availability, slow-release",
        "yield_low": 0.30,
    },
    "kelp": {
        "primary_extract": "growth hormones (auxins) + K + microbes",
        "preparation": "ferment with salt, or dry + steep",
        "soil_benefit": "Biostimulant, root development",
        "yield_low": 0.12,
    },
    "dandelion": {
        "primary_extract": "root: K; leaf: Ca + micronutrients",
        "preparation": "root ash, leaf tea",
        "soil_benefit": "Deep-mine minerals (taproot reaches deep soil layers)",
        "yield_low": 0.18,
    },
    "legume_hay": {
        "primary_extract": "nitrogen (fixed during growth) + P + K",
        "preparation": "ferment, compost, or tea",
        "soil_benefit": "N-rich, supports microbial life",
        "yield_low": 0.22,
    },
}

VEGETATION_SALVAGE = {
    "fresh_plantain_leaves": ["roadside_common", "lawn_weeds", "pasture"],
    "grain_chaff_or_hull": ["grain_cleaning_refuse", "mill_scrap", "combine_residue"],
    "comfrey_leaves": ["garden_perennial", "forage_field"],
    "dried_nettle_leaves": ["wildcraft_spring", "dried_inventory"],
    "dried_seaweed": ["lakeshore_dried", "purchased_bulk", "coastal_drift"],
    "fresh_kelp": ["coastal_tidal_zone", "storm_drift"],
    "fresh_dandelion": ["lawn", "pasture", "disturbed_ground"],
    "legume_hay": ["hay_supplier", "farm_scrap", "pasture_cutting"],
    "bone_char": ["rendered_animal_bones", "roadkill_salvage"],
    "mature_compost": ["composting_pile_aged", "municipal_compost"],
}


def register_with_resolver(resolver):
    resolver.register_domain("plantain", vegetation_expander)
    resolver.register_domain("comfrey", vegetation_expander)
    resolver.register_domain("nettle", vegetation_expander)
    resolver.register_domain("seaweed", vegetation_expander)
    # 'wood_ash' is held by wood_ash_domain (lye, glaze, fertilizer,
    # saltpeter branches); this domain exposes its plant-mineral
    # branches under 'wood_ash_vegetation' so both stay reachable.
    resolver.register_domain("wood_ash_vegetation", vegetation_expander)
    resolver.register_domain("vegetation", vegetation_expander)
    resolver.register_domain("plant_material", vegetation_expander)
    resolver.salvage_index.update(VEGETATION_SALVAGE)

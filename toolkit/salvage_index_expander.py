# salvage_index_expander.py
# Universal substitution layer: any required component → junkyard/salvage alternatives
# Cross-cuts all domains. Fires automatically on every resolver query.
# CC0 | mobile-queryable | stdlib only

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class AcquisitionDifficulty(Enum):
    FREE_AMBIENT = 1   # Already in environment
    SALVAGE_EASY = 2   # Roadside, dumpster, common junkyard
    SALVAGE_MODERATE = 3  # Specific landfill section, scrapyard hunt
    SALVAGE_HARD = 4   # Specialty salvage, networked sources
    PURCHASE_LAST_RESORT = 5  # Cannot salvage, must buy

@dataclass
class SalvageSource:
    """One way to obtain a needed component from salvage/ambient."""
    source_name: str
    description: str
    difficulty: AcquisitionDifficulty
    typical_locations: List[str]  # "auto_salvage", "construction_debris", "appliance_scrap"
    extraction_method: str
    yield_estimate: str  # "high", "moderate", "low"
    contamination_risk: str  # "none", "low", "moderate", "high"
    notes: str

@dataclass
class ComponentSalvageMap:
    """All known salvage paths for a single required component."""
    component_name: str
    sources: List[SalvageSource]


# --- Universal salvage mapping ---
# Each component maps to ranked sources, easiest first.

SALVAGE_INDEX: Dict[str, List[SalvageSource]] = {

    "flux": [
        SalvageSource("wood_ash_concentrated", "Hardwood ash, water-leached, evaporated",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["fire_pit", "wood_stove", "burn_pile"],
                     "Collect ash, leach with water, decant clear liquid, boil down",
                     "high", "none", "Best from oak/maple/hickory"),
        SalvageSource("borax_household", "Old cleaning products, laundry boosters",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "abandoned_homes"],
                     "Direct collection, check for moisture damage",
                     "moderate", "low", "20 Mule Team brand common"),
        SalvageSource("table_salt", "NaCl as basic flux substitute",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["road_salt_pile", "kitchen_scraps", "preserved_food"],
                     "Direct collection", "high", "moderate", "Road salt has anti-cake additives"),
        SalvageSource("soda_ash_burned_seaweed", "Burned dried seaweed → Na2CO3",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["lakeshore_dried_algae"], "Burn dried plant material, leach ash",
                     "low", "low", "Lake Superior shoreline source"),
    ],

    "lye": [
        SalvageSource("wood_ash_leached", "Hardwood ash water leach → KOH/K2CO3",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["fire_pit", "wood_stove"],
                     "Drip water through ash 24h, collect liquid, boil concentrate",
                     "moderate", "none", "Test strength with feather: dissolves = strong"),
        SalvageSource("drain_cleaner_NaOH", "Sodium hydroxide flake from drain products",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "construction_cleanup"],
                     "Direct, store dry; reacts violently with water",
                     "high", "low", "Crystal Drano, Roebic, etc."),
        SalvageSource("oven_cleaner", "Spray foam typically contains KOH",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential"], "Evaporate spray, collect residue",
                     "low", "moderate", "Lower concentration than flake"),
        SalvageSource("battery_corrosion", "Alkaline battery white deposits = KOH",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dead_battery_scrap"], "Scrape, dissolve in water, filter",
                     "very_low", "moderate", "Slow accumulation method"),
    ],

    "acid_strong": [
        SalvageSource("battery_acid_diluted", "Lead-acid battery sulfuric acid",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["auto_salvage", "junkyard", "abandoned_vehicles"],
                     "Drain carefully into glass/plastic; PPE required",
                     "high", "high", "~30-35% H2SO4 typical"),
        SalvageSource("vinegar_concentrated", "Acetic acid, distill to concentrate",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "grocery_dumpster"],
                     "Distill to remove water, increase strength",
                     "moderate", "none", "Maxes ~25% via distillation"),
        SalvageSource("toilet_bowl_cleaner", "HCl-based cleaners",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential"], "Direct use, ventilated",
                     "moderate", "moderate", "10-15% HCl typical"),
    ],

    "crucible": [
        SalvageSource("clay_pot_fired", "Earthenware fired in pit kiln",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["pottery_shards", "abandoned_buildings"],
                     "Salvage shards, refire or use as-is for low temps",
                     "moderate", "low", "Max ~1000°C without refractory glaze"),
        SalvageSource("metal_can_ash_lined", "Steel can with wood ash insulation",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "recycling"],
                     "Pack ash between two cans, creates insulated chamber",
                     "moderate", "none", "Works to ~800°C"),
        SalvageSource("cinder_block_cavity", "Concrete block hollow as forge body",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition_sites"],
                     "Stack as chamber, line with clay/ash",
                     "high", "low", "Can reach 1200°C with forced air"),
        SalvageSource("graphite_crucible_salvage", "Old foundry/melting crucibles",
                     AcquisitionDifficulty.SALVAGE_HARD,
                     ["industrial_salvage", "metal_shop_scrap"],
                     "Check for cracks; recondition with clay slip",
                     "low", "none", "Best option for metals to 1500°C"),
    ],

    "binder": [
        SalvageSource("pine_tar", "Pine pitch melted, mixed with charcoal",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["pine_forest", "wounded_trees"],
                     "Collect from tree wounds, melt to liquid binder",
                     "moderate", "none", "Universal binder, also waterproof"),
        SalvageSource("egg_white", "Albumen protein binder",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["bird_nest", "dumpster_grocery"],
                     "Whip until foamy, mix with filler",
                     "high", "none", "Sets fast; non-waterproof"),
        SalvageSource("starch_paste", "Flour/cornstarch boiled in water",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_grocery", "food_waste"],
                     "Mix flour with cold water, then boil to gel",
                     "high", "none", "Bookbinding-grade adhesive"),
        SalvageSource("rendered_fat", "Tallow as moisture-resistant binder",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["butcher_scraps", "roadkill_legal_states"],
                     "Render solid fat, mix with charcoal/ash filler",
                     "high", "low", "Adds water resistance to mix"),
        SalvageSource("pva_glue_thinned", "Standard white glue diluted",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "school_scrap"],
                     "Direct use or thinned with water 1:1",
                     "high", "none", "Non-structural binder"),
    ],

    "charcoal": [
        SalvageSource("fire_pit_charcoal", "Wood pit-charred, screened for chunks",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["campsite_fire_pit", "wood_stove", "burn_pile"],
                     "Screen ash, retain blacks; or burn wood low-oxygen for char",
                     "high", "none", "Activated charcoal needs steam treatment"),
        SalvageSource("bbq_briquettes_used", "Spent charcoal grills",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["campsite_grill", "park_grill", "dumpster"],
                     "Direct collection; rinse if contaminated",
                     "high", "low", "Briquettes have binders; lump preferred"),
        SalvageSource("burned_bone", "Bone char from animal remains burned",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["roadkill", "butcher_scraps"],
                     "Burn at high temp until calcined; crush",
                     "moderate", "none", "High phosphorus, useful as filter media"),
        SalvageSource("activated_carbon_filters", "Spent water filters",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "appliance_disposal"],
                     "Crack filter housing, recover carbon",
                     "moderate", "low", "Brita, PUR, fridge filters all viable"),
    ],

    "metal_iron_steel": [
        SalvageSource("rebar_salvage", "Construction reinforcement bar",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition_site", "abandoned_building"],
                     "Cut to length; clean concrete with hammer",
                     "high", "low", "High carbon, good for tools"),
        SalvageSource("appliance_scrap", "Washer drums, refrigerator panels",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dump", "appliance_disposal", "curbside_pickup"],
                     "Disassemble; separate plated from raw steel",
                     "high", "low", "Mix of stainless and mild steel"),
        SalvageSource("vehicle_body_panels", "Cars, trucks, machinery scrap",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["auto_salvage", "junkyard", "abandoned_vehicles"],
                     "Cut with angle grinder or torch",
                     "high", "moderate", "Watch for galvanizing fumes when heated"),
        SalvageSource("rail_spikes_track_steel", "Railroad scrap (legal where rail abandoned)",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["abandoned_rail_corridor"],
                     "Pry from ties; high-carbon steel ideal for tools",
                     "moderate", "none", "Check legal status of abandoned rail"),
    ],

    "metal_copper": [
        SalvageSource("electrical_wiring", "House/industrial wire copper",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition", "appliance_scrap"],
                     "Strip insulation; bundle by gauge",
                     "high", "low", "Burning insulation releases toxic gas; mechanical strip preferred"),
        SalvageSource("plumbing_pipe", "Copper water pipe",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition"],
                     "Cut to length; flux/solder removable",
                     "high", "none", "Cleanest copper source"),
        SalvageSource("motor_windings", "Transformer/motor copper coils",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["appliance_scrap", "industrial_salvage"],
                     "Disassemble core, unwind coil",
                     "high", "low", "Lacquer coating must be burned/scraped"),
        SalvageSource("brass_fittings", "Plumbing brass = Cu + Zn alloy",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "plumbing_scrap"],
                     "Direct collection; melt to separate if needed",
                     "moderate", "none", "Both metals usable"),
    ],

    "metal_aluminum": [
        SalvageSource("beverage_cans", "Aluminum drink cans crushed",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["roadside", "dumpster", "recycling_bin"],
                     "Direct collection; flatten for transport",
                     "high", "none", "Low silicon, easy to melt"),
        SalvageSource("siding_gutters", "Building aluminum exterior",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition"],
                     "Sheet stock, can be cut and reformed",
                     "high", "low", "Often painted; remove or burn off"),
        SalvageSource("engine_blocks_heads", "Vehicle aluminum engine parts",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["auto_salvage", "junkyard"],
                     "Melt down; cast as bars",
                     "high", "low", "Alloy mix; silicon content affects casting"),
        SalvageSource("wheel_rims", "Vehicle aluminum wheels",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["auto_salvage"], "Direct salvage; melt or machine",
                     "high", "none", "High-grade aluminum alloy"),
    ],

    "metal_zinc": [
        SalvageSource("galvanized_sheet", "Galvanized roofing/duct",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "old_roofing"],
                     "Acid-dip to strip zinc coating; collect zinc residue",
                     "low", "moderate", "Inefficient but accessible"),
        SalvageSource("zinc_alloy_cast", "Pot metal, old door hardware",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["dumpster_residential", "antique_scrap"],
                     "Melt; separate by density",
                     "moderate", "low", "Zamak alloy common"),
        SalvageSource("carbon_zinc_batteries", "Old D/C cells (non-alkaline)",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "electronic_scrap"],
                     "Carefully open casing; zinc shell intact",
                     "low", "low", "Avoid leaking cells"),
    ],

    "cloth_fabric": [
        SalvageSource("cotton_rag", "Old clothing, sheets, towels",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "thrift_dumpster"],
                     "Wash, cut to need",
                     "high", "low", "Natural fibers preferred"),
        SalvageSource("burlap_old_sack", "Feed bags, coffee sacks",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["farm_scrap", "warehouse_dumpster"],
                     "Direct collection; check for chemical residue",
                     "moderate", "moderate", "Watch for treated bags"),
        SalvageSource("denim_scrap", "Heavy cotton durable cloth",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["thrift_dumpster", "alteration_shop_scrap"],
                     "Cut to need; very durable",
                     "high", "low", "Excellent for filters, patches"),
    ],

    "container_sealed": [
        SalvageSource("glass_jar_with_lid", "Mason jars, food jars",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "recycling"],
                     "Wash, sterilize if needed",
                     "high", "none", "Best for ferments, chemicals"),
        SalvageSource("hdpe_drum", "Food-grade plastic drums",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["industrial_scrap", "farm_supply_disposal"],
                     "Check for chemical residue; rinse thoroughly",
                     "high", "moderate", "55-gallon ideal for water storage"),
        SalvageSource("metal_drum_55gal", "Steel drums",
                     AcquisitionDifficulty.SALVAGE_MODERATE,
                     ["industrial_scrap", "construction"],
                     "Inspect for rust; verify previous contents safe",
                     "moderate", "moderate", "Avoid drums from chemical industry"),
        SalvageSource("plastic_bottles_repurposed", "PET water/soda bottles",
                     AcquisitionDifficulty.FREE_AMBIENT,
                     ["roadside", "dumpster", "recycling"],
                     "Direct collection",
                     "very_high", "none", "Limited heat tolerance"),
    ],

    "wire_conductor": [
        SalvageSource("house_wiring_copper", "Romex/THHN salvage",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "demolition"],
                     "Strip insulation mechanically",
                     "high", "low", "Various gauges available"),
        SalvageSource("appliance_cord", "Power cords from disposal",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster", "appliance_scrap"],
                     "Cut from device, strip ends",
                     "high", "low", "Short lengths; mostly stranded"),
        SalvageSource("auto_wiring_harness", "Vehicle electrical bundle",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["auto_salvage", "junkyard"],
                     "Cut harness, separate by gauge/color",
                     "high", "low", "Multi-gauge bundle"),
    ],

    "filter_screen": [
        SalvageSource("coffee_filter_stack", "Paper filters layered",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential"], "Stack 3-5 deep for fine filtration",
                     "high", "none", "Single-use"),
        SalvageSource("cloth_cotton_layered", "T-shirt cotton, multiple layers",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["thrift_dumpster", "rag_pile"],
                     "Stretch over container, secure with band",
                     "high", "none", "Reusable after wash"),
        SalvageSource("screen_door_mesh", "Window/door screen aluminum or fiber",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["construction_debris", "appliance_scrap"],
                     "Cut to size",
                     "high", "none", "Coarse filtration only"),
        SalvageSource("hvac_filter_repurposed", "Furnace/AC filter material",
                     AcquisitionDifficulty.SALVAGE_EASY,
                     ["dumpster_residential", "appliance_replacement"],
                     "Cut out pleated material",
                     "moderate", "low", "Good for air filtration setups"),
    ],
}


# --- Resolver integration ---

class SalvageExpander:
    """
    Cross-cutting layer: applies salvage substitutions to any resolver query.
    Fires automatically after primary tree resolves.
    """

    def __init__(self, salvage_index: Dict = None):
        self.salvage_index = salvage_index or SALVAGE_INDEX

    def expand_query(self, required_components: List[str],
                     on_hand: List[str]) -> Dict[str, List[SalvageSource]]:
        """
        For each missing component, return ranked salvage sources.
        Easiest acquisition first.
        """
        missing = [c for c in required_components if c not in on_hand]
        results = {}

        for component in missing:
            # Try direct match first
            if component in self.salvage_index:
                sources = sorted(
                    self.salvage_index[component],
                    key=lambda s: s.difficulty.value
                )
                results[component] = sources
            else:
                # Fuzzy match: check if component name contains a key
                matched = self._fuzzy_match(component)
                if matched:
                    results[component] = sorted(
                        self.salvage_index[matched],
                        key=lambda s: s.difficulty.value
                    )
                else:
                    results[component] = []

        return results

    def _fuzzy_match(self, component: str) -> Optional[str]:
        """Find closest salvage index key."""
        component_lower = component.lower()
        for key in self.salvage_index.keys():
            if key in component_lower or component_lower in key:
                return key
        return None

    def report(self, missing_components: List[str]) -> str:
        """Human-readable salvage suggestions."""
        expansions = self.expand_query(missing_components, [])
        lines = []
        for component, sources in expansions.items():
            if not sources:
                lines.append(f"\n{component}: NO SALVAGE MAPPED")
                continue
            lines.append(f"\n{component}:")
            for src in sources[:3]:  # Top 3 easiest
                lines.append(f"  [{src.difficulty.name}] {src.source_name}")
                lines.append(f"    where: {', '.join(src.typical_locations[:2])}")
                lines.append(f"    how: {src.extraction_method}")
        return "\n".join(lines)


# --- Register with resolver ---

def register_with_resolver(resolver):
    """Inject salvage index into resolver's lookup system."""
    for component, sources in SALVAGE_INDEX.items():
        if component not in resolver.salvage_index:
            resolver.salvage_index[component] = []
        # Convert to simple list format for resolver compatibility
        resolver.salvage_index[component].extend([s.source_name for s in sources])

# salvage_index_expander.py
# Universal substitution layer: any "required component" → junkyard alternatives
# CC0 | mobile-queryable

SALVAGE_MAPPING = {
    "flux": ["soda_ash_from_burned_seaweed", "borax_from_old_cleaners", "salt"],
    "lye": ["wood_ash_leached", "drain_cleaner_NaOH", "battery_terminals_corroded"],
    "crucible": ["clay_pot_fired", "metal_can_lined_ash", "cinder_block_cavity"],
    "binder": ["pine_tar", "egg_white", "starch_paste", "rendered_fat"],
    "charcoal": ["fire_pit_ash_screened", "burnt_bone", "activated_carbon_filter"],
    "sand": ["desert_sand", "silica_from_crushed_glass", "sandstone_ground"],
    "gravel": ["crushed_stone", "river_rock", "brick_rubble"],
    "metal_rod": ["rebar_salvage", "wire_bundle_twisted", "nail_clusters"],
    "cloth": ["cotton_rag", "linen_scrap", "burlap_old_sack"],
    "water_container": ["bucket", "barrel", "plastic_drum", "sealed_jar"],
    # ... 200+ mappings
}

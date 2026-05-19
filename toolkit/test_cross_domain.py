# test_cross_domain.py
from salvage_chemistry_resolver import TreeResolver, Query
from black_beans_domain import register_with_resolver as reg_beans
from battery_domain import register_with_resolver as reg_battery
from pine_pitch_domain import register_with_resolver as reg_pitch
from tallow_domain import register_with_resolver as reg_tallow
from wood_ash_domain import register_with_resolver as reg_ash
from cross_domain_combiner import CrossDomainCombiner

resolver = TreeResolver()
reg_beans(resolver)
reg_battery(resolver)
reg_pitch(resolver)
reg_tallow(resolver)
reg_ash(resolver)

combiner = CrossDomainCombiner(resolver)

query = Query(
    feedstock=["tallow", "wood_ash", "pine_pitch", "zinc", "copper"],
    target_property="any",
    time_available_days=30,
    temp_constraint_c=20,
    equipment_on_hand=["heat_source", "container", "wire", "filter"],
    components_on_hand=["water"]
)

print(combiner.report(query))
print("\n--- TREE ---")
tree = combiner.build_synergy_tree(query)
print(tree.to_json(tree))

# cross_domain_combiner.py
# Detects synergies across substrate domains.
# If you have feedstock A + feedstock B, what outputs become viable
# that neither produces alone?
# CC0 | falsifiable

from salvage_chemistry_resolver import (
    TreeResolver, Query, Node, TransformMode, Constraint, NodeStatus
)
from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class Synergy:
    """A product that emerges only from combining domains."""
    id: str
    description: str
    required_feedstocks: Set[str]
    output_property: str
    success_probability: float
    notes: str


# Registry of known cross-domain synergies.
# Each entry: combining feedstocks unlocks a target NOT in any single domain.
SYNERGIES: List[Synergy] = [

    Synergy(
        id="syn_tallow_lye_soap",
        description="Tallow + wood ash → cold-process soap",
        required_feedstocks={"tallow", "wood_ash"},
        output_property="soap",
        success_probability=0.88,
        notes="Wood ash leach provides lye; tallow saponifies."
    ),

    Synergy(
        id="syn_pitch_tallow_dressing",
        description="Pine pitch + tallow → leather/wood conditioner",
        required_feedstocks={"pine_pitch", "tallow"},
        output_property="leather_dressing",
        success_probability=0.90,
        notes="Pitch waterproofs, tallow softens. Optional beeswax."
    ),

    Synergy(
        id="syn_battery_lye_alair",
        description="Aluminum + wood ash → Al-air battery (high V)",
        required_feedstocks={"aluminum", "wood_ash"},
        output_property="battery_high_voltage",
        success_probability=0.70,
        notes="Concentrated ash lye breaks Al oxide, enables ~2V cell."
    ),

    Synergy(
        id="syn_beans_tallow_lube",
        description="Black beans + tallow → fermented bean-oil grease",
        required_feedstocks={"black_beans", "tallow"},
        output_property="grease",
        success_probability=0.72,
        notes="Bean ferment yields glycerol; tallow + glycerol + thickener = grease."
    ),

    Synergy(
        id="syn_pitch_ash_torch",
        description="Pine pitch + wood ash (filler) → matte-finish torch",
        required_feedstocks={"pine_pitch", "wood_ash"},
        output_property="long_burn_torch",
        success_probability=0.85,
        notes="Ash modulates burn rate; pitch fuels."
    ),

    Synergy(
        id="syn_battery_pitch_seal",
        description="Battery + pine pitch → sealed cell (waterproof case)",
        required_feedstocks={"zinc", "copper", "pine_pitch"},
        output_property="sealed_battery",
        success_probability=0.78,
        notes="Pitch seals container; cell chemistry standard Zn/Cu."
    ),

    Synergy(
        id="syn_pitch_charcoal_paint",
        description="Pine pitch + wood ash charcoal → matte protective coating",
        required_feedstocks={"pine_pitch", "wood_ash"},
        output_property="black_protective_coating",
        success_probability=0.83,
        notes="Pitch binder + charcoal pigment. Wood/metal protectant."
    ),

    Synergy(
        id="syn_tallow_ash_lamp",
        description="Tallow + ash-derived lye-cured wick → improved oil lamp",
        required_feedstocks={"tallow", "wood_ash"},
        output_property="oil_lamp",
        success_probability=0.82,
        notes="Lye-treated wick burns cleaner than raw cotton in tallow."
    ),
]


class CrossDomainCombiner:
    """
    Detects synergies and folds them into the resolver tree.
    """

    def __init__(self, resolver: TreeResolver):
        self.resolver = resolver
        self.synergies = SYNERGIES

    def find_synergies(self, available_feedstocks: List[str]) -> List[Synergy]:
        """Return synergies fully unlocked by available feedstocks."""
        available = set(available_feedstocks)
        return [s for s in self.synergies
                if s.required_feedstocks.issubset(available)]

    def find_one_away_synergies(self, available_feedstocks: List[str]) -> List[Dict]:
        """
        Synergies missing exactly ONE feedstock.
        Returns what you'd need to acquire/salvage to unlock each.
        """
        available = set(available_feedstocks)
        results = []
        for s in self.synergies:
            missing = s.required_feedstocks - available
            if len(missing) == 1:
                results.append({
                    "synergy": s,
                    "missing": list(missing)[0],
                    "salvage_options": self.resolver.salvage_index.get(
                        list(missing)[0], []
                    )
                })
        return results

    def build_synergy_tree(self, query: Query) -> Node:
        """
        Build a tree showing all cross-domain outputs available.
        Each top-level child = one synergy or single-domain branch set.
        """
        root = Node(
            id="cross_root",
            description=f"All viable outputs from {query.feedstock}",
            transform=TransformMode.HYBRID,
            success_probability=1.0,
            constraints=Constraint()
        )

        # Add synergy nodes
        for syn in self.find_synergies(query.feedstock):
            if query.target_property in ("any", syn.output_property):
                root.children.append(Node(
                    id=syn.id,
                    description=syn.description,
                    transform=TransformMode.HYBRID,
                    success_probability=syn.success_probability,
                    constraints=Constraint(),
                    parent_id="cross_root"
                ))

        # Add one-away synergies as CLOSED nodes with salvage hints
        for entry in self.find_one_away_synergies(query.feedstock):
            syn = entry["synergy"]
            node = Node(
                id=f"{syn.id}_locked",
                description=f"{syn.description} (LOCKED)",
                transform=TransformMode.HYBRID,
                success_probability=syn.success_probability * 0.5,
                constraints=Constraint(
                    fallback_paths=entry["salvage_options"]
                ),
                status=NodeStatus.CLOSED,
                closure_reason=f"need: {entry['missing']}",
                parent_id="cross_root"
            )
            root.children.append(node)

        # Sort by success probability
        root.children.sort(key=lambda n: n.success_probability, reverse=True)
        return root

    def report(self, query: Query) -> str:
        """Human-readable summary for voice/text response."""
        unlocked = self.find_synergies(query.feedstock)
        one_away = self.find_one_away_synergies(query.feedstock)

        lines = [f"FEEDSTOCKS: {', '.join(query.feedstock)}", ""]
        lines.append(f"UNLOCKED SYNERGIES ({len(unlocked)}):")
        for s in sorted(unlocked, key=lambda x: -x.success_probability):
            lines.append(f"  [{s.success_probability:.2f}] {s.description}")
            lines.append(f"         → {s.notes}")

        lines.append("")
        lines.append(f"ONE FEEDSTOCK AWAY ({len(one_away)}):")
        for entry in one_away:
            s = entry["synergy"]
            lines.append(f"  [{s.success_probability:.2f}] {s.description}")
            lines.append(f"         need: {entry['missing']}")
            lines.append(f"         salvage: {entry['salvage_options']}")

        return "\n".join(lines)

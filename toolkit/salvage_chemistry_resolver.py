# salvage_chemistry_resolver.py
# Probability-space tree navigator | CC0

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class NodeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CONDITIONAL = "conditional"

class TransformMode(Enum):
    EXTRACT = "extract"
    FERMENT = "ferment"
    THERMAL = "thermal"
    HYBRID = "hybrid"
    SYNTHESIZE = "synthesize"

@dataclass
class ClosureCondition:
    reason: str  # "missing_equipment", "time_exceeded", "temp_unstable"
    status: NodeStatus  # OPEN / CLOSED / CONDITIONAL
    fallback_nodes: List[str]  # Alternative branches if this closes

@dataclass
class Constraint:
    """
    Bundled requirements for a Node. Translated by Node.__post_init__
    into the flat navigation fields the resolver uses internally.
    """
    equipment_required: List[str] = field(default_factory=list)
    components_required: List[str] = field(default_factory=list)
    min_dwell_hours: int = 0
    temp_range_c: tuple = (0, 100)
    fallback_paths: List[str] = field(default_factory=list)

@dataclass
class Node:
    """
    A transformation step in the substrate -> product graph.

    Two construction styles are supported:

    Spec style (domain authors):
        Node(id="...", description="...", transform=TransformMode.X,
             success_probability=..., constraints=Constraint(...))
        __post_init__ translates the constraints fields to the flat
        navigation fields used internally by the resolver.

    Direct style (eager-tree building, original API):
        Node(id="...", mode="...", energy_cost="...",
             dwell_hours=..., equipment=[...], temp_range=(low, high),
             success_probability=..., status=..., closure_conditions=[...],
             child_nodes=[...])
    """
    id: str
    # Spec-style optional fields (domain authors set these):
    description: str = ""
    transform: Optional[TransformMode] = None
    constraints: Optional[Constraint] = None
    # Navigation fields (auto-populated from spec when not set directly):
    mode: str = ""  # "ferment", "thermal", "extract", "synthesize", "hybrid"
    energy_cost: str = "medium"  # "low", "medium", "high"
    dwell_hours: int = 0
    equipment: List[str] = field(default_factory=list)
    temp_range: tuple = (-273, 1000)  # (min, max) Celsius, permissive default
    success_probability: float = 1.0  # 0–1
    status: NodeStatus = NodeStatus.OPEN
    closure_conditions: List[ClosureCondition] = field(default_factory=list)
    child_nodes: List["Node"] = field(default_factory=list)  # Next spike-out

    def __post_init__(self):
        if self.transform is not None and not self.mode:
            self.mode = self.transform.value
        if self.constraints is not None:
            if not self.equipment:
                self.equipment = list(self.constraints.equipment_required)
            if self.dwell_hours == 0:
                self.dwell_hours = self.constraints.min_dwell_hours
            if self.temp_range == (-273, 1000):
                self.temp_range = self.constraints.temp_range_c
            if self.constraints.fallback_paths and not self.closure_conditions:
                self.closure_conditions.append(ClosureCondition(
                    reason="missing_equipment",
                    status=NodeStatus.CONDITIONAL,
                    fallback_nodes=list(self.constraints.fallback_paths),
                ))

# Backwards-compat alias for the eager-tree shape used previously.
ProcessNode = Node

@dataclass
class QueryContext:
    feedstock: str
    target_property: str
    time_available_days: int
    temp_constraint: int  # Operating minimum
    equipment_on_hand: List[str]
    salvage_access: Dict[str, bool]  # What can you source last-minute?

# Backwards-compat alias for the domain-author vocabulary.
Query = QueryContext

class ProbabilityTreeResolver:
    def __init__(self):
        self.domains = {}  # "black_beans", "tallow", etc.
        self.transformation_trees = {}
        # Lazy-expansion registry: feedstock -> Callable[[Node, Query], List[Node]]
        # Used by domain files (e.g. black_beans_domain) that spike branches
        # out from a parent node on demand rather than pre-building the tree.
        self.expanders = {}
        # Shared substitution map: component_name -> [salvage_source_names].
        # Domain files extend this in their register_with_resolver(resolver).
        self.salvage_index = {}

    def register_domain(self, feedstock: str, tree_or_expander):
        """
        Register a feedstock domain.

        tree_or_expander accepts either:
          - A Node (or ProcessNode) for eager-tree registration, or
          - A callable (parent: Node, query: Query) -> List[Node] for
            lazy expansion (the spike-out pattern used by domain files
            like black_beans_domain and battery_domain).
        """
        if callable(tree_or_expander) and not isinstance(tree_or_expander, Node):
            self.expanders[feedstock] = tree_or_expander
        else:
            self.domains[feedstock] = tree_or_expander
            self.transformation_trees[feedstock] = tree_or_expander

    def navigate(self, context: QueryContext) -> Dict:
        """
        Returns full probability tree ranked by:
        1. Success probability at each node
        2. Time feasibility (dwell + available window)
        3. Equipment + salvage closure risk
        """
        if context.feedstock in self.expanders:
            # Lazy-expansion path: invoke the registered expander into
            # a synthetic root whose constraints permit pass-through to
            # its children.
            expander = self.expanders[context.feedstock]
            root = Node(
                id=f"{context.feedstock}_root",
                description=f"Root for {context.feedstock}",
                success_probability=1.0,
                temp_range=(context.temp_constraint, 1000),
            )
            root.child_nodes = list(expander(root, context))
        else:
            root = self.transformation_trees.get(context.feedstock)
            if not root:
                return {"error": f"Domain '{context.feedstock}' not registered"}

        tree = self._build_traversal_tree(
            root, context.target_property, context
        )
        ranked = self._rank_branches(tree, context)

        return {
            "decision_tree": ranked,
            "primary_path": ranked["children"][0] if ranked["children"] else None,
            "all_alternatives": self._flatten_alternatives(ranked),
            "closure_map": self._map_all_closures(ranked, context),
            "execution_windows": self._find_home_sync(ranked, context)
        }

    def _build_traversal_tree(self, node: ProcessNode, target: str,
                              context: QueryContext) -> Dict:
        """Recursively expand tree, evaluate closure at each node."""
        closure = self._evaluate_closure(node, context)

        children = []
        if node.child_nodes and closure.status == NodeStatus.OPEN:
            for child in node.child_nodes:
                child_tree = self._build_traversal_tree(child, target, context)
                children.append(child_tree)

        return {
            "id": node.id,
            "description": node.description,
            "mode": node.mode,
            "dwell_hours": node.dwell_hours,
            "success_probability": node.success_probability,
            "status": closure.status.value,
            "closure_reason": closure.reason,
            "fallback_nodes": closure.fallback_nodes,
            "equipment_needed": node.equipment,
            "missing_equipment": [e for e in node.equipment
                                 if e not in context.equipment_on_hand],
            "salvage_risk": self._assess_salvage_risk(node, context),
            "children": children
        }

    def _evaluate_closure(self, node: ProcessNode,
                         context: QueryContext) -> ClosureCondition:
        """Check: can this node stay open given your constraints?"""
        # Equipment check
        missing = [e for e in node.equipment
                  if e not in context.equipment_on_hand]
        if missing and not self._can_salvage(missing, context):
            return ClosureCondition(
                reason="missing_equipment",
                status=NodeStatus.CLOSED,
                fallback_nodes=node.closure_conditions[0].fallback_nodes
                              if node.closure_conditions else []
            )

        # Time check
        if node.dwell_hours > context.time_available_days * 24:
            return ClosureCondition(
                reason="time_exceeded",
                status=NodeStatus.CLOSED,
                fallback_nodes=[]
            )

        # Temperature check
        if node.temp_range[0] < context.temp_constraint:
            return ClosureCondition(
                reason="temp_unstable",
                status=NodeStatus.CLOSED,
                fallback_nodes=[]
            )

        return ClosureCondition(reason="open", status=NodeStatus.OPEN, fallback_nodes=[])

    def _rank_branches(self, tree: Dict, context: QueryContext) -> Dict:
        """Sort children by success probability, time efficiency, salvage cost."""
        if not tree["children"]:
            return tree

        scored = [
            (child, self._score_branch(child, context))
            for child in tree["children"]
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        tree["children"] = [self._rank_branches(child, context)
                           for child, _ in scored]
        return tree

    def _score_branch(self, node_tree: Dict, context: QueryContext) -> float:
        """Composite score: probability × time_efficiency × (1 - salvage_friction)."""
        prob = node_tree["success_probability"]
        time_eff = 1.0 - min(node_tree["dwell_hours"] /
                            (context.time_available_days * 24), 1.0)
        salvage_friction = len(node_tree["missing_equipment"]) * 0.1
        return prob * time_eff * max(1.0 - salvage_friction, 0.1)

    def _can_salvage(self, missing: List[str], context: QueryContext) -> bool:
        """Can you source this at last minute or synthesize it?"""
        return any(context.salvage_access.get(item, False) for item in missing)

    def _assess_salvage_risk(self, node: ProcessNode,
                            context: QueryContext) -> float:
        """0–1 risk score for missing components."""
        missing = [e for e in node.equipment
                  if e not in context.equipment_on_hand]
        if not missing:
            return 0.0
        sourceable = sum(1 for m in missing
                        if context.salvage_access.get(m, False))
        return 1.0 - (sourceable / len(missing)) if missing else 0.0

    def _map_all_closures(self, tree: Dict, context: QueryContext) -> Dict:
        """For each open node, list what would close it and fallback branches."""
        closures = {}

        def traverse(node):
            if node["status"] != "open":
                closures[node["id"]] = {
                    "closes_on": node["closure_reason"],
                    "fallbacks": node["fallback_nodes"]
                }
            for child in node["children"]:
                traverse(child)

        traverse(tree)
        return closures

    def _flatten_alternatives(self, tree: Dict) -> List[Dict]:
        """Extract all root-to-leaf paths ranked by probability."""
        paths = []

        def traverse(node, path):
            current_path = path + [node["id"]]
            if not node["children"]:
                paths.append(current_path)
            else:
                for child in node["children"]:
                    traverse(child, current_path)

        traverse(tree, [])
        return sorted(paths, key=lambda p: len(p))  # Shortest first

    def _find_home_sync(self, tree: Dict, context: QueryContext) -> List[str]:
        """Identify which nodes need home-day planning."""
        windows = []

        def traverse(node):
            if node["dwell_hours"] > 48:  # Needs planning
                windows.append(f"{node['id']}: {node['dwell_hours']}h dwell")
            for child in node["children"]:
                traverse(child)

        traverse(tree)
        return windows

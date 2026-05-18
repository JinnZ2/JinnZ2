# salvage_chemistry_resolver.py
# Probability-space tree navigator | CC0

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class NodeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CONDITIONAL = "conditional"

@dataclass
class ClosureCondition:
    reason: str  # "missing_equipment", "time_exceeded", "temp_unstable"
    status: NodeStatus  # OPEN / CLOSED / CONDITIONAL
    fallback_nodes: List[str]  # Alternative branches if this closes

@dataclass
class ProcessNode:
    id: str
    mode: str  # "ferment", "heat", "extract", "build", "hybrid"
    energy_cost: str  # "low", "medium", "high"
    dwell_hours: int
    equipment: List[str]
    temp_range: tuple  # (min, max) Celsius
    success_probability: float  # 0–1
    status: NodeStatus
    closure_conditions: List[ClosureCondition]
    child_nodes: List['ProcessNode']  # Next spike-out

@dataclass
class QueryContext:
    feedstock: str
    target_property: str
    time_available_days: int
    temp_constraint: int  # Operating minimum
    equipment_on_hand: List[str]
    salvage_access: Dict[str, bool]  # What can you source last-minute?

class ProbabilityTreeResolver:
    def __init__(self):
        self.domains = {}  # "black_beans", "tallow", etc.
        self.transformation_trees = {}

    def register_domain(self, feedstock: str, tree: ProcessNode):
        """Add a feedstock domain with its transformation tree."""
        self.domains[feedstock] = tree
        self.transformation_trees[feedstock] = tree

    def navigate(self, context: QueryContext) -> Dict:
        """
        Returns full probability tree ranked by:
        1. Success probability at each node
        2. Time feasibility (dwell + available window)
        3. Equipment + salvage closure risk
        """
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

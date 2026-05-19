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
    # Additive fields used by cross_domain_combiner (aliased into child_nodes
    # by __post_init__ so .append / .sort propagate to both names):
    children: List["Node"] = field(default_factory=list)
    parent_id: Optional[str] = None
    closure_reason: Optional[str] = None

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
        # Alias children <-> child_nodes so combiner-style .append/.sort
        # on either name propagates to both.
        if self.children and not self.child_nodes:
            self.child_nodes = list(self.children)
        self.children = self.child_nodes

    def to_json(self, node: Optional["Node"] = None, indent: int = 2) -> str:
        """Serialize this node (or a passed node) as a JSON string."""
        import json
        target = node if node is not None else self
        return json.dumps(self._to_dict(target), indent=indent, default=str)

    def _to_dict(self, node: "Node") -> dict:
        return {
            "id": node.id,
            "description": node.description,
            "mode": node.mode,
            "success_probability": node.success_probability,
            "status": (node.status.value
                       if isinstance(node.status, NodeStatus)
                       else str(node.status)),
            "parent_id": node.parent_id,
            "closure_reason": node.closure_reason,
            "equipment": list(node.equipment),
            "dwell_hours": node.dwell_hours,
            "children": [self._to_dict(c) for c in node.children],
        }

# Backwards-compat alias for the eager-tree shape used previously.
ProcessNode = Node

_TEMP_SENTINEL = -273  # below absolute zero, used to mark "unset"

@dataclass
class QueryContext:
    # feedstock accepts a single str for single-domain navigate(), OR
    # List[str] for multi-substrate queries consumed by
    # CrossDomainCombiner.build_synergy_tree().
    feedstock: object
    target_property: str = "any"
    time_available_days: int = 30
    temp_constraint: int = _TEMP_SENTINEL  # Operating minimum
    temp_constraint_c: int = _TEMP_SENTINEL  # alias preferred by newer callers
    equipment_on_hand: List[str] = field(default_factory=list)
    salvage_access: Dict[str, bool] = field(default_factory=dict)
    components_on_hand: List[str] = field(default_factory=list)
    # Optional emotion/somatic sensor readings (Emotions-as-Sensors
    # wedge -- see ConstrainedQuery.emotional_signals). Resolvers that
    # care can read this to modulate scoring; default empty = no
    # modulation, identical to pre-wedge behavior.
    emotional_signals: Dict = field(default_factory=dict)

    def __post_init__(self):
        # Mirror temp_constraint and temp_constraint_c so either name works.
        if (self.temp_constraint == _TEMP_SENTINEL
                and self.temp_constraint_c != _TEMP_SENTINEL):
            self.temp_constraint = self.temp_constraint_c
        elif (self.temp_constraint_c == _TEMP_SENTINEL
                and self.temp_constraint != _TEMP_SENTINEL):
            self.temp_constraint_c = self.temp_constraint
        # If neither was supplied, default to a permissive minimum.
        if self.temp_constraint == _TEMP_SENTINEL:
            self.temp_constraint = -273
            self.temp_constraint_c = -273

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
        # Accept list-shaped feedstock from the multi-domain API: collapse
        # to single-feedstock navigate if it has exactly one element;
        # multi-feedstock queries route through CrossDomainCombiner.
        fs = context.feedstock
        if isinstance(fs, list):
            if len(fs) == 1:
                fs = fs[0]
            elif len(fs) == 0:
                return {"error": "Empty feedstock list"}
            else:
                return {
                    "error": (
                        "Multi-feedstock query: pass to "
                        "CrossDomainCombiner.build_synergy_tree() "
                        "instead of resolver.navigate()."
                    )
                }
        if fs in self.expanders:
            # Lazy-expansion path: invoke the registered expander into
            # a synthetic root whose constraints permit pass-through to
            # its children.
            expander = self.expanders[fs]
            root = Node(
                id=f"{fs}_root",
                description=f"Root for {fs}",
                success_probability=1.0,
                temp_range=(context.temp_constraint, 1000),
            )
            root.child_nodes = list(expander(root, context))
            root.children = root.child_nodes
        else:
            root = self.transformation_trees.get(fs)
            if not root:
                return {"error": f"Domain '{fs}' not registered"}

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
        """Composite score: probability × time_efficiency × (1 - salvage_friction)
        × emotion_modulation (no-op when context.emotional_signals is empty)."""
        prob = node_tree["success_probability"]
        time_eff = 1.0 - min(node_tree["dwell_hours"] /
                            (context.time_available_days * 24), 1.0)
        salvage_friction = len(node_tree["missing_equipment"]) * 0.1
        emotion_factor = self._emotion_modulation_factor(node_tree, context)
        return (prob * time_eff
                * max(1.0 - salvage_friction, 0.1)
                * emotion_factor)

    def _emotion_modulation_factor(self, node_tree: Dict,
                                   context: QueryContext) -> float:
        """
        Multiplicative scoring factor based on operator/team state.
        Returns 1.0 when context.emotional_signals is empty -- so
        callers that don't populate emotional_signals see identical
        behavior to before this hook existed.

        Heuristics (opt-in; tune via feedback_loop_module):
          - High stress / panic / urgent  -> penalize long-dwell branches
          - High fatigue / burnout         -> penalize hybrid / synthesize
          - Low team_coherence             -> penalize hybrid (coordination)
        """
        signals = context.emotional_signals or {}
        if not signals:
            return 1.0

        factor = 1.0
        dwell = node_tree.get("dwell_hours", 0)
        mode = (node_tree.get("mode") or "").lower()

        stress_high = (
            signals.get("stress_level") in ("high", "critical")
            or signals.get("panic")
            or signals.get("urgent")
        )
        if stress_high and dwell > 24:
            factor *= 0.6

        fatigue_high = (
            signals.get("fatigue") in ("high", "critical")
            or (isinstance(signals.get("burnout"), (int, float))
                and signals["burnout"] > 0.5)
        )
        if fatigue_high and mode in ("hybrid", "synthesize"):
            factor *= 0.7

        coherence = signals.get("team_coherence")
        if (isinstance(coherence, (int, float))
                and coherence < 0.5
                and mode == "hybrid"):
            factor *= 0.8

        return factor

    def _can_salvage(self, missing: List[str], context: QueryContext) -> bool:
        """
        Can you source this at last minute or synthesize it?

        Consults both:
          - context.salvage_access  (per-query opt-in flags)
          - self.salvage_index      (registered substitution paths;
                                     populated by domain register_with_resolver
                                     calls and by salvage_index_expander)
        Returns True if any missing item is salvageable from either source.
        """
        for item in missing:
            if context.salvage_access.get(item, False):
                return True
            if self.salvage_index.get(item):
                return True
        return False

    def _assess_salvage_risk(self, node: ProcessNode,
                            context: QueryContext) -> float:
        """0–1 risk score for missing components.

        An item counts as sourceable if either the per-query
        salvage_access flag is True OR the resolver's salvage_index
        has a non-empty source list for it.
        """
        missing = [e for e in node.equipment
                  if e not in context.equipment_on_hand]
        if not missing:
            return 0.0

        def is_sourceable(item: str) -> bool:
            if context.salvage_access.get(item, False):
                return True
            return bool(self.salvage_index.get(item))

        sourceable = sum(1 for m in missing if is_sourceable(m))
        return 1.0 - (sourceable / len(missing))

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


# Backwards-compat alias for the cross_domain_combiner / test vocabulary.
TreeResolver = ProbabilityTreeResolver

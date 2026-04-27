# energy_english/state_model.py
"""
State model for the Energy English runtime.

A node is a persistent state container — not an entity in time but a
carrier of state across discrete iterations:

    S_{t+1} = F(S_t, constraints, memory_triggers, external_inputs)

Time here is an iteration index, not a continuum.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class StateMode(Enum):
    """Canonical operating modes for a StateNode."""

    STABLE = "stable"
    DRIVEN = "driven"
    SUPPRESSED = "suppressed"
    OSCILLATORY = "oscillatory"
    UNSTABLE = "unstable"
    LOCKED = "locked"
    BIFURCATING = "bifurcating"
    SATURATED = "saturated"
    HYSTERETIC = "hysteretic"
    MEDIATING = "mediating"
    SHIELDED = "shielded"
    DECOHERENT = "decoherent"


@dataclass
class StateNode:
    """A persistent state container that survives across iterations."""

    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    mode: StateMode = StateMode.STABLE


@dataclass
class StateGraph:
    """The full system state at iteration t."""

    nodes: Dict[str, StateNode] = field(default_factory=dict)
    iteration: int = 0

    def get(self, name: str) -> StateNode:
        if name not in self.nodes:
            self.nodes[name] = StateNode(name=name)
        return self.nodes[name]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "nodes": {k: dict(v.properties) for k, v in self.nodes.items()},
            "modes": {k: v.mode.value for k, v in self.nodes.items()},
        }


@dataclass
class MemoryTrigger:
    """
    Conditional activation operator.

    When ``condition`` evaluates true on the current snapshot, ``payload``
    returns a {node_name: {key: value}} dict that is merged into the state
    graph as a latent-structure injection.
    """

    name: str
    condition: Callable[[Dict[str, Any]], bool]
    payload: Callable[[], Dict[str, Dict[str, Any]]]

    def evaluate(self, state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        if self.condition(state):
            return self.payload()
        return {}


# In v4 runtime "memory fields" share the trigger shape.
MemoryField = MemoryTrigger


def evolve(
    state_graph: StateGraph,
    constraint_graph: Any,
    memory_triggers: List[MemoryTrigger],
    external_inputs: Optional[Dict[str, Any]] = None,
) -> StateGraph:
    """
    Discrete state evolution step.

    1. Snapshot the current state.
    2. Evaluate memory triggers against the snapshot — they may inject
       latent subgraphs.
    3. Translate the constraint graph into per-node deltas.
    4. Merge all updates into node ``properties``.
    5. Increment the iteration counter.
    """
    external_inputs = external_inputs or {}

    snapshot = state_graph.snapshot()
    snapshot["external"] = external_inputs

    injected: Dict[str, Dict[str, Any]] = {}
    for trig in memory_triggers:
        delta = trig.evaluate(snapshot)
        for node_name, updates in delta.items():
            injected.setdefault(node_name, {}).update(updates)

    propagated = _apply_constraints(constraint_graph)

    for source in (injected, propagated):
        for node_name, updates in source.items():
            node = state_graph.get(node_name)
            node.properties.update(updates)

    state_graph.iteration += 1
    return state_graph


def _apply_constraints(constraint_graph: Any) -> Dict[str, Dict[str, Any]]:
    """
    Translate a constraint graph's edges into per-node property deltas.

    This is the basic propagation step used by the v3 evolve loop. The v4
    runtime in ``runtime_upgrades`` replaces it with active enforcement
    (transitive closure, competition, saturation, hysteresis, resonance).
    """
    deltas: Dict[str, Dict[str, Any]] = {}
    if not isinstance(constraint_graph, dict):
        return deltas

    for edge in constraint_graph.get("edges", []):
        if isinstance(edge, dict):
            target = edge.get("target")
            strength = float(edge.get("strength", 0.0))
        else:
            target = getattr(edge, "target", None)
            strength = float(getattr(edge, "strength", 0.0))

        if target is None:
            continue

        bucket = deltas.setdefault(target, {})
        bucket["incoming_strength"] = bucket.get("incoming_strength", 0.0) + strength

    return deltas


def example_thermal_resonance_trigger() -> MemoryTrigger:
    """
    Example trigger: when the thermal field's instability metric exceeds 0.7,
    re-activate a latent resonance pattern coupled to the chi front.
    """
    return MemoryTrigger(
        name="thermal_resonance_memory",
        condition=lambda s: (
            s.get("nodes", {})
             .get("thermal_field", {})
             .get("instability", 0)
            > 0.7
        ),
        payload=lambda: {
            "thermal_field": {
                "latent_resonance_pattern": True,
                "historical_modes_reactivated": ["chi_front_coupling"],
            }
        },
    )

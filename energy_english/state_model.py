# energy_english/state_model.py

from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable

@dataclass
class StateNode:
    """
    A node is a persistent state container.
    Not an entity in time — a carrier of state across iterations.
    """
    name: str
    state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateGraph:
    """
    Timeline is replaced by iterative state evolution:
        S_{t+1} = F(S_t, inputs, triggers)
    """
    nodes: Dict[str, StateNode] = field(default_factory=dict)
    iteration: int = 0

    def get(self, name: str) -> StateNode:
        if name not in self.nodes:
            self.nodes[name] = StateNode(name=name)
        return self.nodes[name]

    def snapshot(self) -> Dict:
        return {
            "iteration": self.iteration,
            "nodes": {k: v.state for k, v in self.nodes.items()}
        }


Fix to code: replace retrieval with:

@dataclass
class MemoryTrigger:
    """
    Conditional activation operator.
    Injects latent structure into active graph state.
    """
    name: str
    condition: Callable[[Dict], bool]
    payload: Callable[[], Dict]  # returns subgraph/state delta

    def evaluate(self, state: Dict) -> Dict:
        if self.condition(state):
            return self.payload()
        return {}


add to compiler:

def evolve(state_graph: StateGraph,
           constraint_graph,
           memory_triggers: List[MemoryTrigger],
           external_inputs: Dict) -> StateGraph:

    # 1. Current snapshot
    current_state = state_graph.snapshot()

    # 2. Evaluate memory triggers (graph expansion)
    injected = {}
    for trig in memory_triggers:
        delta = trig.evaluate(current_state | external_inputs)
        injected.update(delta)

    # 3. Apply constraint propagation (your existing system)
    # (placeholder for your ConstraintEnforcer / propagate logic)
    propagated = apply_constraints(constraint_graph)

    # 4. Merge all updates into node states
    for node_name, updates in (propagated | injected).items():
        node = state_graph.get(node_name)
        node.state.update(updates)

    # 5. Increment iteration (time = index, not continuum)
    state_graph.iteration += 1

    return state_graph


define triggers ( example):

def example_trigger():
    return MemoryTrigger(
        name="thermal_resonance_memory",

        condition=lambda s: (
            s["nodes"].get("thermal_field", {}).get("instability", 0) > 0.7
        ),

        payload=lambda: {
            "thermal_field": {
                "latent_resonance_pattern": True,
                "historical_modes_reactivated": ["chi_front_coupling"]
            }
        }
    )





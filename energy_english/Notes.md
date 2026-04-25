needed: @dataclass
class CanonicalSchema:
    """
    Immutable semantic contract for all compiler versions.
    This is the only layer that should NOT be rewritten.
    """
    node_semantics: Dict[str, str]
    relation_semantics: Dict[str, str]
    state_update_rule: str
    memory_trigger_rule: str
    time_definition: str = "discrete_iteration"


    from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class CanonicalLock:
    """
    IMMUTABLE SEMANTIC CONTRACT.

    This object defines meaning, not implementation.
    It must not change across compiler versions.
    """

    # --- NODE SEMANTICS ---
    node_types: Dict[str, str]
    # e.g. "front" -> "propagating dynamic boundary in field system"

    # --- RELATION SEMANTICS ---
    relation_meaning: Dict[str, str]
    # e.g. "drives" -> "injects directional energy gradient into target node"

    # --- STATE DEFINITION ---
    state_definition: str
    # e.g. "State = vector of measurable intensities + coherence metrics"

    # --- TIME MODEL ---
    time_model: str
    # e.g. "Discrete iteration over state transitions (no continuous ontology)"

    # --- MEMORY MODEL ---
    memory_model: str
    # e.g. "Conditional subgraph activation via pattern-state matching"

    # --- UPDATE RULE ---
    update_rule: str
    # e.g. "S_{t+1} = F(S_t, constraints, memory_injection)"

class LockedCompiler:

    def __init__(self, base_compiler, lock: CanonicalLock):
        self.base = base_compiler
        self.lock = lock
        self.enforcer = LockEnforcer(lock)

    def compile(self, text: str):

        raw = self.base.compile(text)

        locked_nodes = self.enforcer.enforce_nodes(raw["nodes"])
        locked_edges = self.enforcer.enforce_relations(raw["edges"])

        return {
            "nodes": locked_nodes,
            "edges": locked_edges,
            "state_model": self.lock.state_definition,
            "time_model": self.lock.time_model,
            "memory_model": self.lock.memory_model,
            "update_rule": self.lock.update_rule,
        }


        
    

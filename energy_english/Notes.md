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


from typing import Dict, List, Any

class LockViolation(Exception):
    pass


class LockValidator:
    """
    Ensures compiler outputs remain within the CanonicalLock manifold.

    This is NOT semantic checking.
    It is structural invariance enforcement.
    """

    def __init__(self, lock):
        self.lock = lock

    def validate(self, compiled: Dict[str, Any]) -> bool:
        self._validate_nodes(compiled.get("nodes", {}))
        self._validate_edges(compiled.get("edges", {}))
        self._validate_required_fields(compiled)
        return True

        

    def _validate_nodes(self, nodes: Dict[str, Any]):
        for name, node in nodes.items():

            if "type" not in node:
                raise LockViolation(f"Node {name} missing type")

            if node["type"] not in self.lock.node_types:
                raise LockViolation(
                    f"Unmapped node type: {node['type']}"
                )

            # Ensure semantic binding exists
            expected = self.lock.node_types[node["type"]]
            if not expected:
                raise LockViolation(
                    f"Node type {node['type']} lacks canonical binding"
                )


                    def _validate_edges(self, edges: List[Dict]):
        for e in edges:

            if "relation" not in e:
                raise LockViolation("Edge missing relation")

            rel = e["relation"]

            if rel not in self.lock.relation_meaning:
                raise LockViolation(f"Unknown relation: {rel}")

            # Strength must remain bounded (prevents semantic drift amplification)
            if not (0.0 <= e.get("strength", 0.5) <= 1.0):
                raise LockViolation(
                    f"Out-of-bounds strength: {e['strength']}"
                )

                

    def _validate_required_fields(self, compiled: Dict[str, Any]):
        required = [
            "nodes",
            "edges",
            "state_model",
            "time_model",
            "memory_model",
            "update_rule"
        ]

        for r in required:
            if r not in compiled:
                raise LockViolation(f"Missing canonical field: {r}")

                

class LockedRuntime:

    def __init__(self, compiler, lock, validator, memory_fields=None):
        self.compiler = compiler
        self.lock = lock
        self.validator = validator
        self.memory_fields = memory_fields or []

        self.state = StateGraph()

    def step(self, text: str, external_inputs=None):

        compiled = self.compiler.compile(text)

        # ── INVARIANT GATE ─────────────────────
        self.validator.validate(compiled)

        # If this passes, system is structurally safe to execute
        self.state = evolve(
            state_graph=self.state,
            constraint_graph=compiled,
            memory_fields=self.memory_fields,
            external_inputs=external_inputs
        )

        return {
            "iteration": self.state.iteration,
            "nodes": {k: v.properties for k, v in self.state.nodes.items()},
        }

        

text → compiler → canonical projection → VALIDATION GATE → runtime




        
    

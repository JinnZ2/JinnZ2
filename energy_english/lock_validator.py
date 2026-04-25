# energy_english/lock_validator.py
"""
Canonical-lock layer for the Energy English compiler stack.

Pipeline:

    text  →  compiler  →  canonical projection  →  VALIDATION GATE  →  runtime

The objects in this module form the **structural invariance contract**
for compiler outputs. The lock defines *meaning*, not implementation,
and must not change across compiler versions. Runtime evolution is only
allowed once an output has passed the validation gate.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from energy_english.state_model import (
    MemoryField,
    StateGraph,
    evolve,
)


class LockViolation(Exception):
    """Raised when a compiler output escapes the canonical manifold."""


@dataclass(frozen=True)
class CanonicalLock:
    """
    IMMUTABLE SEMANTIC CONTRACT.

    This object defines *meaning*, not implementation. It must not change
    across compiler versions. Every field below is a canonical binding
    that downstream validators and runtimes are entitled to assume.
    """

    # Node semantics: type → canonical interpretation
    # e.g. "front" -> "propagating dynamic boundary in field system"
    node_types: Dict[str, str]

    # Relation semantics: relation name → canonical interpretation
    # e.g. "drives" -> "injects directional energy gradient into target node"
    relation_meaning: Dict[str, str]

    # State definition: canonical description of what "state" means
    state_definition: str

    # Time model: canonical description of the time ontology
    time_model: str = "discrete iteration over state transitions"

    # Memory model: canonical description of memory activation semantics
    memory_model: str = "conditional subgraph activation via pattern-state matching"

    # Update rule: canonical description of S_{t+1} = F(...)
    update_rule: str = "S_{t+1} = F(S_t, constraints, memory_injection)"


class LockValidator:
    """
    Ensures compiler outputs remain within the CanonicalLock manifold.

    This is *not* semantic checking — it is structural invariance
    enforcement. A passing validation guarantees the runtime is safe to
    execute the projection without leaving canonical ground.
    """

    REQUIRED_FIELDS = (
        "nodes",
        "edges",
        "state_model",
        "time_model",
        "memory_model",
        "update_rule",
    )

    def __init__(self, lock: CanonicalLock):
        self.lock = lock

    def validate(self, compiled: Dict[str, Any]) -> bool:
        self._validate_required_fields(compiled)
        self._validate_nodes(compiled.get("nodes", {}))
        self._validate_edges(compiled.get("edges", []))
        return True

    def _validate_required_fields(self, compiled: Dict[str, Any]) -> None:
        for field_name in self.REQUIRED_FIELDS:
            if field_name not in compiled:
                raise LockViolation(f"Missing canonical field: {field_name}")

    def _validate_nodes(self, nodes: Any) -> None:
        # Accept either a dict {name: node_dict} or a list of node_dicts.
        items = nodes.items() if isinstance(nodes, dict) else (
            (n.get("name", f"#{i}"), n) for i, n in enumerate(nodes)
        )

        for name, node in items:
            if not isinstance(node, dict):
                raise LockViolation(f"Node {name} is not a mapping")

            node_type = node.get("type")
            if node_type is None:
                raise LockViolation(f"Node {name} missing type")

            if node_type not in self.lock.node_types:
                raise LockViolation(f"Unmapped node type: {node_type}")

            if not self.lock.node_types[node_type]:
                raise LockViolation(
                    f"Node type {node_type} lacks canonical binding"
                )

    def _validate_edges(self, edges: Any) -> None:
        for edge in edges:
            if not isinstance(edge, dict):
                raise LockViolation("Edge is not a mapping")

            relation = edge.get("relation")
            if relation is None:
                raise LockViolation("Edge missing relation")

            if relation not in self.lock.relation_meaning:
                raise LockViolation(f"Unknown relation: {relation}")

            # Strength must remain bounded — prevents semantic drift
            # amplification via runaway edge weights.
            strength = edge.get("strength", 0.5)
            if not (0.0 <= float(strength) <= 1.0):
                raise LockViolation(f"Out-of-bounds strength: {strength}")


class LockedCompiler:
    """
    Wraps a base compiler and projects its raw output onto the canonical
    manifold defined by ``lock``. The projection annotates the output
    with canonical state, time, memory, and update semantics so the
    downstream validator/runtime can rely on a single shape.
    """

    def __init__(self, base_compiler: Any, lock: CanonicalLock):
        self.base = base_compiler
        self.lock = lock

    def compile(self, text: str) -> Dict[str, Any]:
        raw = self.base.compile(text)

        nodes = raw.get("nodes", {})
        edges = raw.get("edges", raw.get("triples", []))

        return {
            "nodes": nodes,
            "edges": edges,
            "state_model": self.lock.state_definition,
            "time_model": self.lock.time_model,
            "memory_model": self.lock.memory_model,
            "update_rule": self.lock.update_rule,
        }


class LockedRuntime:
    """
    Runtime that refuses to evolve state from an output that has not
    passed the invariant gate.

    Lifecycle of one ``step``:

        text → compile → validate (gate) → evolve → state delta
    """

    def __init__(
        self,
        compiler: LockedCompiler,
        lock: CanonicalLock,
        validator: LockValidator,
        memory_fields: Optional[List[MemoryField]] = None,
    ):
        self.compiler = compiler
        self.lock = lock
        self.validator = validator
        self.memory_fields = memory_fields or []
        self.state = StateGraph()

    def step(
        self,
        text: str,
        external_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        compiled = self.compiler.compile(text)

        # ── INVARIANT GATE ─────────────────────────────────
        # If validation passes, the system is structurally safe to execute.
        self.validator.validate(compiled)

        self.state = evolve(
            state_graph=self.state,
            constraint_graph=compiled,
            memory_triggers=self.memory_fields,
            external_inputs=external_inputs,
        )

        return {
            "iteration": self.state.iteration,
            "nodes": {
                name: dict(node.properties)
                for name, node in self.state.nodes.items()
            },
        }

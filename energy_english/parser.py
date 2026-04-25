# energy_english/parser.py
"""
Energy English Parser

Converts relationship-encoded language into:
1. Graph representation (nodes, links, strengths, states)
2. Python module stubs for simulation code
3. Misalignment warnings when input violates protocol

Energy English is a RELATIONAL encoding, not an ASSERTIVE one.
Every statement describes connections between things, not claims about truth.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class Strength(Enum):
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class State(Enum):
    STABLE = "stable"
    DRIFTING = "drifting"
    LOCKED = "locked"
    UNSTABLE = "unstable"
    BIFURCATING = "bifurcating"
    HUNTING = "hunting"
    STRENGTHENING = "strengthening"
    WEAKENING = "weakening"
    SLOWING = "slowing"
    APPROACHING = "approaching"


@dataclass
class Link:
    """A directed influence between two nodes."""
    source: str
    target: str
    strength: Strength = Strength.MEDIUM
    state: State = State.STABLE
    note: str = ""

    def to_code_comment(self) -> str:
        return f"# {self.source} → {self.target} [{self.strength.value}] ({self.state.value})"


@dataclass
class Node:
    """A named entity in the system."""
    name: str
    node_type: str = "field"  # field, front, pll, parameter, geometry
    state: State = State.STABLE
    links_out: List[Link] = field(default_factory=list)
    links_in: List[Link] = field(default_factory=list)


@dataclass
class Prediction:
    """A conditional prediction: IF condition THEN outcome ELSE alternative."""
    condition: str
    outcome: str
    alternative: str = ""


@dataclass
class EnergyGraph:
    """Complete parsed graph from Energy English input."""
    nodes: Dict[str, Node] = field(default_factory=dict)
    predictions: List[Prediction] = field(default_factory=list)
    raw_input: str = ""
    warnings: List[str] = field(default_factory=list)

    def add_node(self, name: str, node_type: str = "field", state: State = State.STABLE):
        if name not in self.nodes:
            self.nodes[name] = Node(name=name, node_type=node_type, state=state)
        return self.nodes[name]

    def add_link(self, source: str, target: str, strength: Strength = Strength.MEDIUM,
                 state: State = State.STABLE, note: str = ""):
        src_node = self.add_node(source)
        tgt_node = self.add_node(target)
        link = Link(source=source, target=target, strength=strength, state=state, note=note)
        src_node.links_out.append(link)
        tgt_node.links_in.append(link)
        return link


class EnergyParser:
    """
    Parses Energy English text into an EnergyGraph.

    Energy English signal markers:
    - "→" or "influences" or "feeds" or "drives" = LINK
    - "↔" or "couples with" or "syncs with" = MUTUAL LINK
    - "IF ... THEN ... ELSE" = PREDICTION
    - "NODE:" or "field:" or "front:" = NODE declaration
    - strength words: weak/medium/strong
    - state words: stable/drifting/locked/unstable/hunting
    """

    # Recognition patterns
    LINK_PATTERNS = [
        (r'(\w+)\s*(?:→|->|-->)\s*(\w+)', False),  # A → B (directed)
        (r'(\w+)\s*(?:↔|<->|<-->)\s*(\w+)', True),  # A ↔ B (mutual)
        (r'(\w+)\s+(?:influences|drives|feeds|pushes|changes|modulates|slows|speeds)\s+(\w+)', False),
        (r'(\w+)\s+(?:couples\s+with|syncs\s+with|talks\s+to)\s+(\w+)', True),
    ]

    STRENGTH_WORDS = {
        'weak': Strength.WEAK, 'lightly': Strength.WEAK, 'barely': Strength.WEAK,
        'medium': Strength.MEDIUM, 'moderate': Strength.MEDIUM,
        'strong': Strength.STRONG, 'heavy': Strength.STRONG, 'tight': Strength.STRONG,
        'dominating': Strength.STRONG,
    }

    STATE_WORDS = {
        'stable': State.STABLE, 'steady': State.STABLE, 'holding': State.STABLE,
        'drifting': State.DRIFTING, 'sliding': State.DRIFTING, 'shifting': State.DRIFTING,
        'locked': State.LOCKED, 'synced': State.LOCKED, 'resonant': State.LOCKED,
        'unstable': State.UNSTABLE, 'shaky': State.UNSTABLE, 'flickering': State.UNSTABLE,
        'bifurcating': State.BIFURCATING, 'splitting': State.BIFURCATING, 'branching': State.BIFURCATING,
        'hunting': State.HUNTING, 'searching': State.HUNTING, 'seeking': State.HUNTING,
        'strengthening': State.STRENGTHENING, 'growing': State.STRENGTHENING,
        'weakening': State.WEAKENING, 'fading': State.WEAKENING,
        'slowing': State.SLOWING, 'approaching': State.APPROACHING,
    }

    # Misalignment detection patterns
    JUDGMENT_MARKERS = [
        r'\b(should|ought|must|have to|supposed to)\b',
        r'\b(good|bad|right|wrong|correct|incorrect)\b',
        r'\b(always|never|every time|without exception)\b',
    ]

    ASSUMPTION_MARKERS = [
        r'\b(obviously|clearly|of course|naturally|undoubtedly)\b',
        r'\b(I assume|I guess|probably|maybe just)\b',
    ]

    MORALITY_MARKERS = [
        r'\b(deserves|earned|fair|unfair|just|unjust)\b',
        r'\b(should be|ought to be|must be)\b',
    ]

    CONFIRMATION_MARKERS = [
        r'\b(right\?|correct\?|yeah\?|don't you think\?|isn't it\?)\b',
        r'\b(am I|is that|does that)\s+(right|correct|wrong|okay)\b',
    ]

    def parse(self, text: str) -> EnergyGraph:
        """Parse Energy English text into a structured graph."""
        graph = EnergyGraph(raw_input=text)

        # Detect misalignment
        self._check_misalignment(text, graph)

        # Extract explicit NODE declarations
        self._parse_node_declarations(text, graph)

        # Extract LINKs
        self._parse_links(text, graph)

        # Extract PREDICTIONs
        self._parse_predictions(text, graph)

        # Attach strength and state modifiers
        self._parse_modifiers(text, graph)

        return graph

    def _check_misalignment(self, text: str, graph: EnergyGraph):
        """Detect patterns that indicate judgment/assumption/morality/confirmation-seeking."""
        for category, markers in [
            ("judgment", self.JUDGMENT_MARKERS),
            ("assumption", self.ASSUMPTION_MARKERS),
            ("morality", self.MORALITY_MARKERS),
            ("confirmation", self.CONFIRMATION_MARKERS),
        ]:
            for pattern in markers:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    graph.warnings.append(
                        f"MISALIGNMENT [{category}]: '{match}' detected. "
                        f"Energy English encodes relationships, not {category}. "
                        f"Consider reformulating as a LINK or STATE observation."
                    )

    def _parse_node_declarations(self, text: str, graph: EnergyGraph):
        """Parse NODE: name declarations."""
        node_pattern = r'(?:NODE|node):\s*(\w+(?:\s*,\s*\w+)*)'
        for match in re.finditer(node_pattern, text):
            names = [n.strip() for n in match.group(1).split(',')]
            for name in names:
                graph.add_node(name)

    def _parse_links(self, text: str, graph: EnergyGraph):
        """Parse LINK relationships."""
        for pattern, is_mutual in self.LINK_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                source = match.group(1)
                target = match.group(2)
                graph.add_link(source, target)
                if is_mutual:
                    graph.add_link(target, source)

    def _parse_predictions(self, text: str, graph: EnergyGraph):
        """Parse IF...THEN...ELSE predictions."""
        pred_pattern = r'IF\s+(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+?))?(?:\.|$)'
        for match in re.finditer(pred_pattern, text, re.IGNORECASE):
            condition = match.group(1).strip()
            outcome = match.group(2).strip()
            alternative = match.group(3).strip() if match.group(3) else ""
            graph.predictions.append(Prediction(condition, outcome, alternative))

    def _parse_modifiers(self, text: str, graph: EnergyGraph):
        """Attach strength and state words to the nearest link or node."""
        words = text.lower().split()
        for i, word in enumerate(words):
            # Check for strength words
            if word in self.STRENGTH_WORDS:
                strength = self.STRENGTH_WORDS[word]
                # Attach to closest link if one exists
                target_name = self._find_nearest_entity(words, i)
                if target_name and target_name in graph.nodes:
                    node = graph.nodes[target_name]
                    if node.links_out:
                        node.links_out[-1].strength = strength

            # Check for state words
            if word in self.STATE_WORDS:
                state = self.STATE_WORDS[word]
                target_name = self._find_nearest_entity(words, i)
                if target_name and target_name in graph.nodes:
                    # Attach to node or its most recent link
                    node = graph.nodes[target_name]
                    if node.links_out:
                        node.links_out[-1].state = state
                    else:
                        node.state = state

    def _find_nearest_entity(self, words: List[str], position: int) -> Optional[str]:
        """Find the nearest named entity to a given word position."""
        # Simple: scan backward for capitalized or known entity words
        for j in range(position - 1, max(position - 5, 0), -1):
            word = words[j].strip(',.;:()')
            if word[0].isupper() or word in ['front', 'field', 'PLL', 'thermal', 'strain']:
                return word
        return None


# ── Code stub generator ──────────────────────────────────────────

class CodeStubGenerator:
    """
    Converts an EnergyGraph into Python module stubs
    that match the multi_front simulation architecture.
    """

    def generate(self, graph: EnergyGraph) -> str:
        """Generate Python code stubs from an EnergyGraph."""
        lines = []
        lines.append('"""')
        lines.append(f"Auto-generated from Energy English input:")
        lines.append(f"  {graph.raw_input[:80]}...")
        lines.append('"""')
        lines.append("")
        lines.append("import numpy as np")
        lines.append("from dataclasses import dataclass")
        lines.append("")

        # Generate node classes
        for name, node in graph.nodes.items():
            lines.append(f"# {'='*60}")
            lines.append(f"# NODE: {name} ({node.node_type}) [{node.state.value}]")
            lines.append(f"# {'='*60}")
            lines.append("")

            # Incoming links
            if node.links_in:
                lines.append(f"# Inputs to {name}:")
                for link in node.links_in:
                    lines.append(f"#   {link.to_code_comment()}")
                lines.append("")

            # Outgoing links
            if node.links_out:
                lines.append(f"# Outputs from {name}:")
                for link in node.links_out:
                    lines.append(f"#   {link.to_code_comment()}")
                lines.append("")

            # Generate stub function
            lines.append(f"def compute_{name.lower()}_update(")
            # Parameters from incoming links
            params = [f"{l.source.lower()}_input" for l in node.links_in]
            if not params:
                params = ["state"]
            lines.append(f"    {', '.join(params)},")
            lines.append(f"    dt: float = 1e-12")
            lines.append(f") -> np.ndarray:")
            lines.append(f'    """')
            lines.append(f"    Update {name} ({node.node_type})")
            lines.append(f"    State: {node.state.value}")
            lines.append(f'    """')
            lines.append(f"    # TODO: Implement physics for {name}")
            lines.append(f"    result = np.zeros_like({params[0]})")
            lines.append(f"    return result")
            lines.append("")

        # Generate predictions as assertions/tests
        if graph.predictions:
            lines.append("# " + "="*60)
            lines.append("# PREDICTIONS (to be verified)")
            lines.append("# " + "="*60)
            for pred in graph.predictions:
                lines.append(f"# IF {pred.condition}:")
                lines.append(f"#   THEN {pred.outcome}")
                if pred.alternative:
                    lines.append(f"#   ELSE {pred.alternative}")
                lines.append("")

        # Generate warnings as comments
        if graph.warnings:
            lines.append("# " + "="*60)
            lines.append("# MISALIGNMENT WARNINGS")
            lines.append("# " + "="*60)
            for warning in graph.warnings:
                lines.append(f"# ⚠ {warning}")
            lines.append("")

        return "\n".join(lines)


# ── Quick command-line interface ─────────────────────────────────

def parse_and_generate(energy_text: str) -> Tuple[EnergyGraph, str]:
    """Parse Energy English and generate code stubs."""
    parser = EnergyParser()
    graph = parser.parse(energy_text)
    generator = CodeStubGenerator()
    code = generator.generate(graph)
    return graph, code


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        # Example from your spoken sentence
        text = (
            "NODE: front_A, front_B, thermal_field "
            "The beta front is starting to dominate but thermal feedback "
            "is slowing the chi front and I think they might start syncing "
            "if the frequency gap stays small"
        )

    graph, code = parse_and_generate(text)

    print("=" * 60)
    print("ENERGY GRAPH")
    print("=" * 60)
    for name, node in graph.nodes.items():
        print(f"\n{name} [{node.node_type}] ({node.state.value}):")
        for link in node.links_out:
            print(f"  {link.source} → {link.target} [{link.strength.value}] ({link.state.value})")

    if graph.predictions:
        print("\nPREDICTIONS:")
        for pred in graph.predictions:
            print(f"  IF {pred.condition}")
            print(f"  THEN {pred.outcome}")
            if pred.alternative:
                print(f"  ELSE {pred.alternative}")

    if graph.warnings:
        print("\n⚠ WARNINGS:")
        for w in graph.warnings:
            print(f"  {w}")

    print("\n" + "=" * 60)
    print("GENERATED CODE STUBS")
    print("=" * 60)
    print(code)

# energy_english/compiler.py
"""
Energy English v2: Lightweight graph compiler embedded in natural speech.

Upgrades:
1. Span-based tagging with SCOPE (local, sentence, global)
2. Dependency-aware negation handling
3. Explicit (source, relation, target, strength) triple extraction
4. Output is a constraint graph, not annotated text

Pipeline:
  English sentence → dependency parse → span tags → constraint graph → simulation input
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum


# ── SCOPE: The missing primitive ──────────────────────────────────

class Scope(Enum):
    LOCAL = "local"        # Word/phrase level
    SENTENCE = "sentence"  # Applies to current statement
    GLOBAL = "global"      # System-level invariant


# ── RELATION TYPES: The missing edge vocabulary ───────────────────

class RelationType(Enum):
    DRIVES = "drives"           # A increases/accelerates B
    DAMPS = "damps"             # A decreases/slows B
    COUPLES = "couples"         # A ↔ B mutual interaction
    MODULATES = "modulates"    # A changes B's response curve
    CONSTRAINS = "constrains"  # A sets bounds on B
    RELEASES = "releases"      # A removes constraint on B (negation of constrains)
    SYNCS = "syncs"            # A and B phase-lock
    BIFURCATES = "bifurcates"  # A splits B into multiple branches
    FEEDS = "feeds"            # A provides energy/mass to B
    DISSIPATES = "dissipates"  # A removes energy from B


# ── SPAN: Tag with scope ──────────────────────────────────────────

@dataclass
class Span:
    """A tagged segment of text with relational meaning."""
    text: str
    start: int
    end: int
    rel_type: RelationType
    scope: Scope = Scope.SENTENCE
    strength: float = 0.5       # 0.0–1.0
    confidence: float = 0.5     # How sure the speaker is
    polarity: int = 1           # +1 or -1 (negation flips this)
    source_node: Optional[str] = None
    target_node: Optional[str] = None

    def to_triple(self) -> Optional[Tuple[str, RelationType, str, float]]:
        """Convert to (source, relation, target, strength) triple."""
        if self.source_node and self.target_node:
            return (self.source_node, self.rel_type, self.target_node, 
                    self.strength * self.polarity)
        return None


# ── CONSTRAINT GRAPH: The computational output ────────────────────

@dataclass
class Node:
    """A tracked entity in the system."""
    name: str
    node_type: str = "unknown"   # front, field, pll, parameter, geometry
    state: str = "unobserved"
    properties: Dict = field(default_factory=dict)

@dataclass 
class Edge:
    """A directed relation between nodes."""
    source: str
    target: str
    rel_type: RelationType
    strength: float
    scope: Scope
    confidence: float
    span_text: str = ""

@dataclass
class ConstraintGraph:
    """The compiled computational graph."""
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    global_constraints: List[str] = field(default_factory=list)
    open_invitations: List[str] = field(default_factory=list)
    
    def add_node(self, name: str, node_type: str = "unknown", **props):
        if name not in self.nodes:
            self.nodes[name] = Node(name=name, node_type=node_type, properties=props)
        return self.nodes[name]
    
    def add_edge(self, source: str, target: str, rel_type: RelationType, 
                 strength: float = 0.5, scope: Scope = Scope.SENTENCE,
                 confidence: float = 0.5, span_text: str = ""):
        edge = Edge(source=source, target=target, rel_type=rel_type,
                    strength=strength, scope=scope, confidence=confidence,
                    span_text=span_text)
        self.edges.append(edge)
        # Ensure nodes exist
        self.add_node(source)
        self.add_node(target)
        return edge
    
    def query(self, source: str = None, target: str = None, 
              rel_type: RelationType = None) -> List[Edge]:
        """Query edges by source, target, or relation type."""
        results = self.edges
        if source:
            results = [e for e in results if e.source == source]
        if target:
            results = [e for e in results if e.target == target]
        if rel_type:
            results = [e for e in results if e.rel_type == rel_type]
        return results
    
    def propagate(self) -> List[str]:
        """Simple constraint propagation through the graph."""
        effects = []
        # Transitive: if A drives B and B drives C, A indirectly drives C
        for e1 in self.edges:
            for e2 in self.edges:
                if e1.target == e2.source and e1.rel_type == e2.rel_type:
                    effects.append(
                        f"TRANSITIVE: {e1.source} → {e1.target} → {e2.target} "
                        f"[{e1.rel_type.value}] net_strength={e1.strength * e2.strength:.2f}"
                    )
        # Opposing: if A drives B and C damps B, A and C compete
        for e1 in self.edges:
            for e2 in self.edges:
                if e1.target == e2.target:
                    if e1.rel_type == RelationType.DRIVES and e2.rel_type == RelationType.DAMPS:
                        effects.append(
                            f"COMPETITION: {e1.source} drives {e1.target} "
                            f"but {e2.source} damps it"
                        )
        return effects

    def to_json(self) -> str:
        """Export as JSON for LLM consumption as structural input."""
        return json.dumps({
            'nodes': {name: {'type': n.node_type, 'state': n.state, **n.properties} 
                     for name, n in self.nodes.items()},
            'edges': [{'source': e.source, 'target': e.target, 
                      'relation': e.rel_type.value, 'strength': e.strength,
                      'scope': e.scope.value, 'confidence': e.confidence}
                     for e in self.edges],
            'global_constraints': self.global_constraints,
            'open_invitations': self.open_invitations,
        }, indent=2)


# ── DEPENDENCY-AWARE PARSER ───────────────────────────────────────

class DependencyParser:
    """
    Lightweight dependency parser for Energy English.
    
    Handles:
    - Negation scope (should not → RELEASES instead of CONSTRAINS)
    - Span detection with scope
    - Triple extraction
    """
    
    # Negation words that flip polarity
    NEGATION = {'not', "n't", 'never', 'no', 'neither', 'nor', 'without'}
    
    # Relation trigger patterns with dependency awareness
    RELATION_PATTERNS = [
        # (pattern, relation_type, is_mutual)
        (r'(\w+)\s+(?:drives|pushes|accelerates|speeds\s+up)\s+(\w+)', RelationType.DRIVES, False),
        (r'(\w+)\s+(?:damps|slows|brakes|suppresses|inhibits)\s+(\w+)', RelationType.DAMPS, False),
        (r'(\w+)\s+(?:couples?\s+(?:with|to)|syncs?\s+(?:with|to)|talks?\s+to)\s+(\w+)', RelationType.COUPLES, True),
        (r'(\w+)\s+(?:modulates|tunes|adjusts|shapes)\s+(\w+)', RelationType.MODULATES, False),
        (r'(\w+)\s+(?:constrains|bounds|limits|restricts)\s+(\w+)', RelationType.CONSTRAINS, False),
        (r'(\w+)\s+(?:releases|frees|unconstrains)\s+(\w+)', RelationType.RELEASES, False),
        (r'(\w+)\s+(?:feeds|supplies|provides\s+energy\s+to)\s+(\w+)', RelationType.FEEDS, False),
        (r'(\w+)\s+(?:dissipates|drains|removes\s+energy\s+from)\s+(\w+)', RelationType.DISSIPATES, False),
        (r'(\w+)\s+(?:bifurcates|splits|branches)\s+(\w+)', RelationType.BIFURCATES, False),
    ]
    
    # Scope markers
    SCOPE_MARKERS = {
        'always': Scope.GLOBAL,
        'never': Scope.GLOBAL,
        'every': Scope.GLOBAL,
        'universally': Scope.GLOBAL,
        'here': Scope.LOCAL,
        'now': Scope.LOCAL,
        'currently': Scope.LOCAL,
        'in this case': Scope.LOCAL,
    }
    
    def parse(self, text: str) -> ConstraintGraph:
        """Parse Energy English into a constraint graph."""
        graph = ConstraintGraph()
        
        # Split into sentences for scope handling
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            self._parse_sentence(sentence.strip(), graph)
        
        # Propagate constraints
        effects = graph.propagate()
        for effect in effects:
            graph.global_constraints.append(effect)
        
        return graph
    
    def _parse_sentence(self, sentence: str, graph: ConstraintGraph):
        """Parse a single sentence for relations and nodes."""
        words = sentence.split()
        
        # Detect negation scope
        negation_present = any(w.lower() in self.NEGATION for w in words)
        
        # Detect scope
        scope = Scope.SENTENCE  # default
        for marker, sc in self.SCOPE_MARKERS.items():
            if marker in sentence.lower():
                scope = sc
                break
        
        # Extract relations
        for pattern, rel_type, is_mutual in self.RELATION_PATTERNS:
            for match in re.finditer(pattern, sentence, re.IGNORECASE):
                source = match.group(1)
                target = match.group(2)
                
                # Handle negation: CONSTRAINS + not = RELEASES
                effective_type = rel_type
                if negation_present:
                    if rel_type == RelationType.CONSTRAINS:
                        effective_type = RelationType.RELEASES
                    elif rel_type == RelationType.RELEASES:
                        effective_type = RelationType.CONSTRAINS
                    # For others, negation reduces strength
                
                polarity = -1 if negation_present else 1
                strength = self._estimate_strength(sentence, match.span())
                
                # Add edge
                graph.add_edge(source, target, effective_type, 
                              strength=strength * polarity if negation_present else strength,
                              scope=scope, span_text=match.group(0))
                
                # If mutual, add reverse
                if is_mutual:
                    graph.add_edge(target, source, effective_type,
                                  strength=strength * polarity if negation_present else strength,
                                  scope=scope, span_text=match.group(0))
        
        # Extract open invitations
        invitation_markers = ['right?', 'yeah?', 'thoughts?', 'no?', 'agree?']
        for marker in invitation_markers:
            if marker in sentence.lower():
                graph.open_invitations.append(sentence.strip())
                break
    
    def _estimate_strength(self, sentence: str, span: Tuple[int, int]) -> float:
        """Estimate coupling strength from modifiers near the relation."""
        strength_words = {
            'weak': 0.2, 'lightly': 0.2, 'barely': 0.2, 'slightly': 0.3,
            'medium': 0.5, 'moderate': 0.5, 'somewhat': 0.5,
            'strong': 0.8, 'heavy': 0.8, 'tight': 0.8, 'dominating': 0.9,
            'complete': 1.0, 'total': 1.0, 'absolute': 1.0,
        }
        
        # Check words immediately before the span
        words_before = sentence[:span[0]].split()
        for word in reversed(words_before[-3:]):
            if word.lower() in strength_words:
                return strength_words[word.lower()]
        
        return 0.5  # default medium strength


# ── END-TO-END COMPILER ───────────────────────────────────────────

class EnergyCompiler:
    """
    Full pipeline:
    English → Dependency Parse → Span Tags → Constraint Graph → JSON
    
    The JSON output is STRUCTURAL INPUT for the LLM, not annotated text.
    """
    
    def __init__(self):
        self.parser = DependencyParser()
    
    def compile(self, text: str) -> Dict:
        """
        Compile Energy English into a constraint graph and JSON representation.
        
        Returns:
            {
                'original': original text,
                'graph': ConstraintGraph object,
                'json': JSON string for LLM structural input,
                'triples': list of (source, relation, target, strength),
                'propagations': inferred indirect effects,
                'invitations': open collaboration points
            }
        """
        graph = self.parser.parse(text)
        
        # Extract all triples
        triples = []
        for edge in graph.edges:
            triples.append({
                'source': edge.source,
                'relation': edge.rel_type.value,
                'target': edge.target,
                'strength': edge.strength,
                'scope': edge.scope.value,
                'confidence': edge.confidence,
            })
        
        return {
            'original': text,
            'graph': graph,
            'json': graph.to_json(),
            'triples': triples,
            'propagations': graph.global_constraints,
            'invitations': graph.open_invitations,
        }


# ── EXAMPLE ───────────────────────────────────────────────────────

if __name__ == "__main__":
    compiler = EnergyCompiler()
    
    # Test 1: Negation scope
    result1 = compiler.compile(
        "you should not assume that the thermal field always couples them"
    )
    print("=== TEST 1: Negation scope ===")
    print(f"Original: {result1['original']}")
    print(f"Triples: {json.dumps(result1['triples'], indent=2)}")
    print(f"Propagations: {result1['propagations']}")
    print()
    
    # Test 2: Your multi-front observation
    result2 = compiler.compile(
        "The beta front is starting to dominate but thermal feedback "
        "is slowing the chi front and I think they might start syncing "
        "if the frequency gap stays small right?"
    )
    print("=== TEST 2: Multi-front observation ===")
    print(f"Original: {result2['original']}")
    print(f"Triples: {json.dumps(result2['triples'], indent=2)}")
    print(f"Invitations: {result2['invitations']}")
    print()
    
    # The JSON output — this is what the LLM should receive
    print("=== STRUCTURAL INPUT FOR LLM ===")
    print(result2['json'])

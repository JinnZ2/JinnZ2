# energy_english/compiler_v3.py
"""
Energy English v3: Clause-aware, dynamically constrained graph compiler.

Upgrades from v2:
1. CLAUSE SEGMENTATION: splits complex sentences before relation extraction
2. GLOBAL STRENGTH: sentence-level feature, not local token proximity
3. EXTENDED RELATION VOCABULARY: phase-locks, resonance, hysteresis, field mediation
4. ACTIVE CONSTRAINTS: global constraints feed back into edge weights and node states
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from enum import Enum


# ── EXTENDED RELATION VOCABULARY ──────────────────────────────────

class RelationType(Enum):
    # Mechanical (from v2)
    DRIVES = "drives"
    DAMPS = "damps"
    COUPLES = "couples"
    MODULATES = "modulates"
    CONSTRAINS = "constrains"
    RELEASES = "releases"
    FEEDS = "feeds"
    DISSIPATES = "dissipates"
    BIFURCATES = "bifurcates"
    
    # ── NEW: Domain-critical primitives ──
    PHASE_LOCKS = "phase_locks"         # A and B achieve resonant frequency lock
    RESONATES = "resonates"             # A amplifies B at specific frequency
    HYSTERETIC = "hysteretic"           # A's effect on B depends on history
    MEDIATES = "mediates"               # A carries influence between B and C (field)
    THRESHOLDS = "thresholds"           # A triggers B only above/below critical value
    SATURATES = "saturates"             # A's influence on B has an upper bound
    SHIELDS = "shields"                 # A blocks influence from reaching B
    AMPLIFIES = "amplifies"             # A increases B's response to other inputs
    SYNCHRONIZES = "synchronizes"       # A entrains B to its frequency
    DECOHERES = "decoheres"             # A disrupts B's phase coherence


# ── CLAUSE STRUCTURE ──────────────────────────────────────────────

@dataclass
class Clause:
    """A single clause extracted from a complex sentence."""
    text: str
    clause_type: str         # "main", "subordinate", "coordinate", "relative"
    conjunction: str = ""    # "and", "but", "if", "when", "that", etc.
    negation_scope: bool = False
    subjects: List[str] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    relations: List[Tuple[str, RelationType, str]] = field(default_factory=list)
    parent_clause: Optional['Clause'] = None
    polarity: int = 1        # +1 or -1


class ClauseSegmenter:
    """
    Splits complex sentences into clauses before relation extraction.
    
    Handles:
    - Coordinating conjunctions: "and", "but", "or", "yet"
    - Subordinating: "if", "when", "because", "although", "while"
    - Relative clauses: "that", "which", "who"
    - Correlative: "not only... but also", "either... or"
    """
    
    # Clause boundary markers
    BOUNDARY_WORDS = [
        'and', 'but', 'or', 'yet', 'so', 'nor',
        'if', 'when', 'because', 'although', 'while', 'unless', 'until',
        'that', 'which', 'who', 'whom', 'whose',
        'where', 'whereas', 'whether',
    ]
    
    # Correlative pairs that should stay together
    CORRELATIVE = {
        'not only': 'but also',
        'either': 'or',
        'neither': 'nor',
        'both': 'and',
        'whether': 'or',
    }
    
    # Negation words
    NEGATION = {'not', "n't", 'never', 'no', 'neither', 'nor', 'without', 'hardly', 'barely'}
    
    def segment(self, text: str) -> List[Clause]:
        """Segment text into clauses preserving dependency structure."""
        clauses = []
        
        # First pass: split on coordinating conjunctions
        segments = self._split_coordinating(text)
        
        # Second pass: identify subordinating and relative clauses within each segment
        for segment in segments:
            sub_clauses = self._extract_clauses(segment)
            clauses.extend(sub_clauses)
        
        # Link parent-child relationships
        self._link_clauses(clauses)
        
        return clauses
    
    def _split_coordinating(self, text: str) -> List[str]:
        """Split on coordinating conjunctions (and, but, or)."""
        # Use regex that captures the conjunction
        parts = re.split(r'\s+(and|but|or|yet|so)\s+', text)
        
        # Reassemble: if "not only X but also Y", keep as one segment
        segments = []
        i = 0
        while i < len(parts):
            segment = parts[i].strip()
            
            # Check if this starts a correlative pair
            started_correlative = False
            for start, end in self.CORRELATIVE.items():
                if start in segment.lower() and i + 2 < len(parts):
                    # Combine: "not only X but also Y"
                    segment = f"{segment} {parts[i+1]} {parts[i+2]}"
                    i += 2
                    started_correlative = True
                    break
            
            if segment:
                segments.append(segment)
            i += 1
        
        return segments if segments else [text]
    
    def _extract_clauses(self, text: str) -> List[Clause]:
        """Extract clauses from a segment, identifying main and subordinate."""
        clauses = []
        
        # Find subordinate clause markers
        sub_markers = ['if', 'when', 'because', 'although', 'while', 'unless', 'until', 'whereas']
        rel_markers = ['that', 'which', 'who', 'whom', 'whose', 'where']
        
        # Split on subordinating conjunctions
        remaining = text
        main_clause_text = ""
        
        for marker in sub_markers + rel_markers:
            pattern = rf'\b{marker}\b'
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                # Everything before the marker is main clause (unless preceded by other sub clauses)
                before = remaining[:match.start()].strip()
                after = remaining[match.start():].strip()
                
                if before:
                    main_clause_text = before
                
                # The sub clause
                sub_clause = Clause(
                    text=after,
                    clause_type="subordinate" if marker in sub_markers else "relative",
                    conjunction=marker,
                    negation_scope=self._detect_negation(after),
                )
                clauses.append(sub_clause)
                remaining = before
        
        # Remaining is the main clause
        if remaining.strip():
            main_clause = Clause(
                text=remaining.strip(),
                clause_type="main",
                negation_scope=self._detect_negation(remaining),
            )
            clauses.insert(0, main_clause)
        
        return clauses
    
    def _detect_negation(self, text: str) -> bool:
        """Check if clause contains negation."""
        words = set(text.lower().split())
        return bool(words & self.NEGATION)
    
    def _link_clauses(self, clauses: List[Clause]):
        """Link subordinate/relative clauses to their parent."""
        if len(clauses) <= 1:
            return
        
        # Main clause is parent to all subordinates
        main = next((c for c in clauses if c.clause_type == "main"), None)
        if main:
            for clause in clauses:
                if clause != main:
                    clause.parent_clause = main


# ── GLOBAL STRENGTH ESTIMATION ────────────────────────────────────

class StrengthEstimator:
    """
    Estimates coupling strength as a SENTENCE-LEVEL feature,
    not a local token proximity heuristic.
    
    Strength is distributed across:
    - Adverbial modifiers anywhere in the clause
    - Contrast words (but, however → weakens preceding)
    - Emphasis words (even, especially, precisely → strengthens)
    - Modal verbs (might, could → uncertainty reduces effective strength)
    """
    
    # Strength modifiers — globally scoped
    AMPLIFIERS = {
        'strongly': 0.3, 'tightly': 0.3, 'deeply': 0.3,
        'completely': 0.4, 'totally': 0.4, 'fully': 0.4,
        'dominating': 0.35, 'overwhelmingly': 0.4,
        'even': 0.2, 'especially': 0.25, 'precisely': 0.25,
        'very': 0.2, 'really': 0.2, 'quite': 0.15,
    }
    
    ATTENUATORS = {
        'weakly': -0.3, 'lightly': -0.3, 'barely': -0.35,
        'slightly': -0.2, 'somewhat': -0.15, 'partially': -0.2,
        'hardly': -0.35, 'scarcely': -0.35,
        'might': -0.15, 'could': -0.15, 'may': -0.1,
        'possibly': -0.2, 'perhaps': -0.2,
    }
    
    # Contrast words weaken the clause they introduce
    CONTRAST_WEAKENING = -0.15
    
    def estimate(self, clause: Clause, sentence_text: str) -> float:
        """Estimate strength for a clause within its sentence context."""
        base_strength = 0.5
        
        # Scan entire clause text for modifiers
        words = clause.text.lower().split()
        
        for word in words:
            if word in self.AMPLIFIERS:
                base_strength += self.AMPLIFIERS[word]
            if word in self.ATTENUATORS:
                base_strength += self.ATTENUATORS[word]
        
        # If clause has negation, strength polarity flips
        if clause.negation_scope:
            base_strength *= -1
        
        # Contrast conjunctions weaken the clause
        if clause.conjunction in ('but', 'yet', 'however', 'although'):
            base_strength += self.CONTRAST_WEAKENING
        
        # Subordinate clauses get slight uncertainty penalty
        if clause.clause_type in ('subordinate', 'relative'):
            base_strength *= 0.9
        
        # Clamp to valid range
        return max(-1.0, min(1.0, base_strength))


# ── EXTENDED RELATION EXTRACTOR ────────────────────────────────────

class RelationExtractor:
    """
    Extracts relations from clauses using the full vocabulary.
    Handles nested and compound relations.
    """
    
    # Mapping of natural language patterns to relation types
    PATTERNS = [
        # Phase-locking and resonance (NEW)
        (r'(?:phase[-\s]?locks?\s+(?:to|with)|locks?\s+phase\s+(?:to|with)|resonates?\s+with|entrains?\s+)', RelationType.PHASE_LOCKS),
        (r'(?:resonates?\s+(?:at|near)|amplifies?\s+(?:at|near)\s+resonance)', RelationType.RESONATES),
        (r'(?:hysteretic|history[-\s]?dependent|path[-\s]?dependent)', RelationType.HYSTERETIC),
        
        # Field mediation (NEW)
        (r'(?:mediates?\s+(?:between|among)|carries?\s+influence\s+(?:between|among|from))', RelationType.MEDIATES),
        (r'(?:through\s+the\s+field|via\s+the\s+field|field[-\s]?mediated)', RelationType.MEDIATES),
        
        # Threshold and saturation (NEW)
        (r'(?:triggers?\s+(?:above|below|at|when)|thresholds?\s+(?:at|above|below)|kicks?\s+in\s+(?:above|below|at))', RelationType.THRESHOLDS),
        (r'(?:saturates?\s+(?:at|above|near)|plateaus?\s+(?:at|near)|maxes?\s+out)', RelationType.SATURATES),
        (r'(?:shields?\s+(?:from|against)|blocks?\s+(?:from)|protects?\s+(?:from))', RelationType.SHIELDS),
        
        # Amplification and synchronization (NEW)
        (r'(?:amplifies?\s+(?:response|effect|signal|sensitivity))', RelationType.AMPLIFIES),
        (r'(?:synchronizes?\s+(?:with|to)|entrains?\s+(?:to|with))', RelationType.SYNCHRONIZES),
        (r'(?:decoheres?|disrupts?\s+(?:phase|coherence)|scrambles?\s+(?:phase))', RelationType.DECOHERES),
        
        # Original mechanical (from v2)
        (r'(?:drives?|pushes?|accelerates?|speeds?\s+up|propels?)', RelationType.DRIVES),
        (r'(?:damps?|slows?|brakes?|suppresses?|inhibits?|retards?)', RelationType.DAMPS),
        (r'(?:couples?\s+(?:with|to)|syncs?\s+(?:with|to)|connects?\s+(?:with|to)|links?\s+(?:with|to))', RelationType.COUPLES),
        (r'(?:modulates?|tunes?|adjusts?|shapes?|regulates?)', RelationType.MODULATES),
        (r'(?:constrains?|bounds?|limits?|restricts?|confines?)', RelationType.CONSTRAINS),
        (r'(?:releases?|frees?|unconstrains?|unbounds?)', RelationType.RELEASES),
        (r'(?:feeds?|supplies?|provides?\s+energy\s+to|fuels?)', RelationType.FEEDS),
        (r'(?:dissipates?|drains?|removes?\s+energy\s+from|sinks?)', RelationType.DISSIPATES),
        (r'(?:bifurcates?|splits?|branches?|forks?)', RelationType.BIFURCATES),
    ]
    
    def extract(self, clause: Clause) -> List[Tuple[str, RelationType, str, float]]:
        """
        Extract (source, relation, target, confidence) tuples from a clause.
        """
        relations = []
        text = clause.text
        
        for pattern, rel_type in self.PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Find subject and object around the relation
                source = self._find_subject(text, match.start())
                target = self._find_object(text, match.end())
                
                if source and target:
                    confidence = 0.7  # Base confidence
                    if clause.clause_type == "main":
                        confidence = 0.85
                    elif clause.negation_scope:
                        confidence = 0.6  # Negated claims are less direct
                    
                    relations.append((source, rel_type, target, confidence))
        
        return relations
    
    def _find_subject(self, text: str, before_pos: int) -> Optional[str]:
        """Find the subject preceding a relation word."""
        before = text[:before_pos].strip().split()
        if not before:
            return None
        
        # Take the last noun-like word before the relation
        # Simple heuristic: last capitalized word or known domain term
        domain_terms = ['front', 'field', 'PLL', 'thermal', 'strain', 'lattice', 
                        'carrier', 'wave', 'temperature', 'mobility', 'phase']
        
        for word in reversed(before):
            word = word.strip(',.;:()"\'')
            if word[0].isupper() or word.lower() in domain_terms:
                return word
        
        # Fallback: last content word
        return before[-1].strip(',.;:()"\'').lower()
    
    def _find_object(self, text: str, after_pos: int) -> Optional[str]:
        """Find the object following a relation word."""
        after = text[after_pos:].strip().split()
        if not after:
            return None
        
        domain_terms = ['front', 'field', 'PLL', 'thermal', 'strain', 'lattice',
                        'carrier', 'wave', 'temperature', 'mobility', 'phase']
        
        for word in after[:5]:  # Look at next few words
            word = word.strip(',.;:()"\'')
            if word[0].isupper() or word.lower() in domain_terms:
                return word
        
        return after[0].strip(',.;:()"\'').lower()


# ── ACTIVE CONSTRAINT ENFORCER ─────────────────────────────────────

class ConstraintEnforcer:
    """
    Global constraints are NOT just logged notes.
    They actively modify edge weights and node states.
    
    Types of active constraints:
    1. TRANSITIVE: If A→B and B→C, A→C inherits compounded strength
    2. COMPETITION: If A→X and B→X with opposing signs, they compete
    3. SATURATION: If total input to a node exceeds threshold, gains are capped
    4. RESONANCE: If two edges to same target share frequency band, amplify
    5. HYSTERESIS: Edge weight depends on whether node state crossed threshold
       in previous timestep
    """
    
    def enforce(self, edges: List[Any], nodes: Dict[str, Any], 
                previous_state: Optional[Dict] = None) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Apply active constraints to the graph.
        Returns modified edges and nodes.
        """
        modified_edges = list(edges)
        modified_nodes = dict(nodes)
        
        # 1. Transitive closure (inherited strength with decay)
        new_edges = []
        for e1 in modified_edges:
            for e2 in modified_edges:
                if e1.target == e2.source and e1.rel_type == e2.rel_type:
                    # Compound strength with 0.7 decay factor
                    compound_strength = e1.strength * e2.strength * 0.7
                    if abs(compound_strength) > 0.1:  # Only if significant
                        # Check if this transitive edge already exists
                        exists = any(
                            ee.source == e1.source and ee.target == e2.target
                            for ee in modified_edges
                        )
                        if not exists:
                            # Create transitive edge
                            from dataclasses import replace
                            new_edge = replace(e1, target=e2.target, 
                                             strength=compound_strength)
                            new_edges.append(new_edge)
        
        modified_edges.extend(new_edges)
        
        # 2. Competition detection and strength redistribution
        for node_name in modified_nodes:
            inputs_to_node = [e for e in modified_edges if e.target == node_name]
            driving = [e for e in inputs_to_node if e.strength > 0]
            damping = [e for e in inputs_to_node if e.strength < 0]
            
            if driving and damping:
                # Net effect on node
                net_drive = sum(e.strength for e in driving)
                net_damp = sum(abs(e.strength) for e in damping)
                
                if net_drive > net_damp:
                    modified_nodes[node_name].state = "driven"
                elif net_damp > net_drive:
                    modified_nodes[node_name].state = "suppressed"
                else:
                    modified_nodes[node_name].state = "balanced"
        
        # 3. Saturation: if node receives too much input of same type
        for node_name in modified_nodes:
            inputs_to_node = [e for e in modified_edges if e.target == node_name]
            if len(inputs_to_node) > 3:
                # Cap individual edge strengths so total doesn't exceed 1.0
                total = sum(abs(e.strength) for e in inputs_to_node)
                if total > 1.5:
                    scale = 1.5 / total
                    for i, e in enumerate(modified_edges):
                        if e.target == node_name:
                            modified_edges[i] = replace(e, strength=e.strength * scale)
        
        # 4. Hysteresis: if previous state available, edge weights depend on history
        if previous_state:
            for i, e in enumerate(modified_edges):
                prev_node = previous_state.get('nodes', {}).get(e.target, {})
                prev_state = prev_node.get('state', '')
                
                if prev_state == 'locked' and e.rel_type == RelationType.PHASE_LOCKS:
                    # Once locked, it's harder to unlock (hysteresis)
                    modified_edges[i] = replace(e, strength=e.strength * 1.3)
                elif prev_state == 'unstable' and e.rel_type == RelationType.COUPLES:
                    # Unstable coupling weakens
                    modified_edges[i] = replace(e, strength=e.strength * 0.7)
        
        return modified_edges, modified_nodes


# ── V3 COMPILER ────────────────────────────────────────────────────

class EnergyCompilerV3:
    """
    Full v3 pipeline:
    Text → Clause Segmentation → Relation Extraction → Strength Estimation
    → Active Constraint Enforcement → ConstraintGraph
    """
    
    def __init__(self):
        self.segmenter = ClauseSegmenter()
        self.extractor = RelationExtractor()
        self.strength_estimator = StrengthEstimator()
        self.enforcer = ConstraintEnforcer()
        self.previous_graph = None  # For hysteresis
    
    def compile(self, text: str) -> Dict:
        """
        Compile Energy English into a dynamically constrained graph.
        """
        # Step 1: Segment into clauses
        clauses = self.segmenter.segment(text)
        
        # Step 2: Extract relations from each clause
        all_relations = []
        for clause in clauses:
            strength = self.strength_estimator.estimate(clause, text)
            relations = self.extractor.extract(clause)
            for source, rel_type, target, confidence in relations:
                all_relations.append({
                    'source': source,
                    'target': target,
                    'relation': rel_type,
                    'strength': strength,
                    'confidence': confidence,
                    'clause_type': clause.clause_type,
                    'negation': clause.negation_scope,
                    'clause_text': clause.text,
                })
        
        # Step 3: Build initial edge list
        from dataclasses import dataclass as dc
        @dc
        class Edge:
            source: str
            target: str
            rel_type: RelationType
            strength: float
            confidence: float
            clause_text: str = ""
        
        edges = []
        node_states = {}
        for rel in all_relations:
            edges.append(Edge(
                source=rel['source'],
                target=rel['target'],
                rel_type=rel['relation'],
                strength=rel['strength'],
                confidence=rel['confidence'],
                clause_text=rel['clause_text'],
            ))
            # Initialize node states
            if rel['source'] not in node_states:
                node_states[rel['source']] = {'state': 'unobserved'}
            if rel['target'] not in node_states:
                node_states[rel['target']] = {'state': 'unobserved'}
        
        # Step 4: Apply active constraints
        prev = None
        if self.previous_graph:
            prev = {
                'nodes': self.previous_graph.get('nodes', {}),
                'edges': self.previous_graph.get('edges', []),
            }
        
        enforced_edges, enforced_nodes = self.enforcer.enforce(edges, node_states, prev)
        
        # Step 5: Build output
        output = {
            'clauses': [{'text': c.text, 'type': c.clause_type, 
                        'negation': c.negation_scope} for c in clauses],
            'edges': [{
                'source': e.source,
                'target': e.target,
                'relation': e.rel_type.value,
                'strength': round(e.strength, 3),
                'confidence': round(e.confidence, 3),
            } for e in enforced_edges],
            'nodes': {name: state for name, state in enforced_nodes.items()},
            'propagations': [],  # Will be filled by constraint propagation
            'invitations': self._extract_invitations(text),
        }
        
        # Store for hysteresis in next call
        self.previous_graph = output
        
        return output
    
    def _extract_invitations(self, text: str) -> List[str]:
        """Extract open collaboration points."""
        markers = ['right?', 'yeah?', 'thoughts?', 'no?', 'think?', 'see?']
        invitations = []
        for marker in markers:
            if marker in text.lower():
                invitations.append(text.strip())
                break
        return invitations


# ── COMPARISON: V2 vs V3 ──────────────────────────────────────────

def compare_versions():
    """Demonstrate v2 failures and v3 fixes."""
    v3 = EnergyCompilerV3()
    
    # Test case 1: Nested clauses (v2 would flatten)
    test1 = "A does not simply drive B but also stabilizes C"
    result1 = v3.compile(test1)
    print("=== NESTED CLAUSES ===")
    print(f"Input: {test1}")
    print(f"Clauses found: {len(result1['clauses'])}")
    for c in result1['clauses']:
        print(f"  [{c['type']}] {c['text']} (negation: {c['negation']})")
    print(f"Edges: {json.dumps(result1['edges'], indent=2)}")
    print()
    
    # Test case 2: Distributed strength
    test2 = "The thermal field very strongly mediates between the fronts, somewhat dampening chi"
    result2 = v3.compile(test2)
    print("=== DISTRIBUTED STRENGTH ===")
    print(f"Input: {test2}")
    for e in result2['edges']:
        print(f"  {e['source']} --[{e['relation']}]--> {e['target']} (strength: {e['strength']})")
    print()
    
    # Test case 3: Domain-specific relations
    test3 = "The PLL phase-locks to the front frequency but the thermal field shields chi from resonance"
    result3 = v3.compile(test3)
    print("=== DOMAIN RELATIONS ===")
    print(f"Input: {test3}")
    for e in result3['edges']:
        print(f"  {e['source']} --[{e['relation']}]--> {e['target']} (strength: {e['strength']})")
    print(f"Node states: {json.dumps(result3['nodes'], indent=2)}")
    print()


if __name__ == "__main__":
    compare_versions()

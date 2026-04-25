# energy_english/runtime_upgrades.py
"""
Upgrade module for Energy Runtime v3 → v4

Adds:
1. Simulation feedback → StateGraph (close the physics loop)
2. Active constraint enforcement (transitive, competition, saturation, hysteresis)
3. Multi-timestep memory (not just current snapshot)
4. Mode transition detection (when a node changes mode, trigger memory)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional, Tuple
from collections import deque

from energy_english.state_model import (
    MemoryField,
    MemoryTrigger,
    StateGraph,
    StateMode,
    StateNode,
)


# ── ACTIVE CONSTRAINT ENFORCER ────────────────────────────────────

@dataclass
class ConstraintEnforcer:
    """
    Converts constraint edges into active node state modifications.
    
    This is NOT just propagation logging (v2).
    This IS active edge weight and node state modification (v3+).
    """
    transitive_decay: float = 0.7
    saturation_threshold: float = 1.5
    hysteresis_memory: int = 3  # How many past states to remember
    
    def __post_init__(self):
        self._state_history: Dict[str, deque] = {}
    
    def apply(self,
              constraint_graph: Dict,
              state_graph: StateGraph,
              memory_fields: List[MemoryField]) -> Dict[str, Dict]:
        """
        Apply active constraints and return node deltas.
        
        Operations:
        1. Transitive closure: A→B + B→C → A→C (with decay)
        2. Competition: opposing inputs to same node redistribute strength
        3. Saturation: cap total input to prevent runaway
        4. Hysteresis: edge weight depends on node's state history
        5. Resonance: edges sharing frequency band amplify each other
        """
        deltas = {}
        
        edges = constraint_graph.get('edges', [])
        nodes = constraint_graph.get('nodes', {})
        
        if not edges:
            return deltas
        
        # Build lookup: edges by target
        inputs_to = {}
        outputs_from = {}
        for edge in edges:
            src = edge['source']
            tgt = edge['target']
            rel = edge['relation']
            strength = edge.get('strength', 0.5)
            
            if tgt not in inputs_to:
                inputs_to[tgt] = []
            inputs_to[tgt].append(edge)
            
            if src not in outputs_from:
                outputs_from[src] = []
            outputs_from[src].append(edge)
        
        # 1. TRANSITIVE CLOSURE
        # If A→B with strength s1 and B→C with strength s2,
        # then A→C with strength s1*s2*decay
        transitive_effects = {}
        for src, out_edges in outputs_from.items():
            for out_edge in out_edges:
                mid = out_edge['target']
                if mid in outputs_from:
                    for mid_out in outputs_from[mid]:
                        final_tgt = mid_out['target']
                        compound_strength = (
                            out_edge.get('strength', 0.5) * 
                            mid_out.get('strength', 0.5) * 
                            self.transitive_decay
                        )
                        if abs(compound_strength) > 0.1:
                            key = (src, final_tgt)
                            if key not in transitive_effects:
                                transitive_effects[key] = []
                            transitive_effects[key].append({
                                'via': mid,
                                'strength': compound_strength,
                                'relation': out_edge['relation'],
                            })
        
        # Apply transitive effects
        for (src, tgt), effects in transitive_effects.items():
            total_strength = sum(e['strength'] for e in effects)
            deltas.setdefault(tgt, {})
            deltas[tgt]['transitive_input'] = total_strength
            deltas[tgt]['transitive_source'] = src
        
        # 2. COMPETITION DETECTION
        for tgt, in_edges in inputs_to.items():
            if len(in_edges) >= 2:
                strengths = [e.get('strength', 0) for e in in_edges]
                has_positive = any(s > 0 for s in strengths)
                has_negative = any(s < 0 for s in strengths)
                
                if has_positive and has_negative:
                    deltas.setdefault(tgt, {})
                    deltas[tgt]['competition'] = True
                    deltas[tgt]['net_drive'] = sum(s for s in strengths if s > 0)
                    deltas[tgt]['net_damp'] = sum(abs(s) for s in strengths if s < 0)
                    
                    # Winner determination
                    if deltas[tgt]['net_drive'] > deltas[tgt]['net_damp']:
                        deltas[tgt]['competition_winner'] = 'drive'
                    elif deltas[tgt]['net_damp'] > deltas[tgt]['net_drive']:
                        deltas[tgt]['competition_winner'] = 'damp'
                    else:
                        deltas[tgt]['competition_winner'] = 'balanced'
        
        # 3. SATURATION
        for tgt, in_edges in inputs_to.items():
            total_input = sum(abs(e.get('strength', 0)) for e in in_edges)
            if total_input > self.saturation_threshold:
                scale = self.saturation_threshold / total_input
                deltas.setdefault(tgt, {})
                deltas[tgt]['saturated'] = True
                deltas[tgt]['saturation_scale'] = scale
                deltas[tgt]['raw_input'] = total_input
                deltas[tgt]['capped_input'] = self.saturation_threshold
        
        # 4. HYSTERESIS
        # Track state history for each node
        for node_name, node in state_graph.nodes.items():
            if node_name not in self._state_history:
                self._state_history[node_name] = deque(maxlen=self.hysteresis_memory)
            
            prev_modes = list(self._state_history[node_name])
            
            # If node was LOCKED and still receiving phase-lock input, it's harder to unlock
            if StateMode.LOCKED.value in [m.value if hasattr(m, 'value') else str(m) 
                                          for m in prev_modes]:
                phase_lock_inputs = [
                    e for e in inputs_to.get(node_name, [])
                    if e.get('relation') == 'phase_locks'
                ]
                if phase_lock_inputs:
                    deltas.setdefault(node_name, {})
                    deltas[node_name]['hysteretic_hold'] = True
                    deltas[node_name]['lock_retention'] = 0.3  # Bonus to lock stability
            
            # Store current mode for next iteration
            self._state_history[node_name].append(node.mode)
        
        # 5. RESONANCE AMPLIFICATION
        # Edges with same frequency band to same target amplify
        for tgt, in_edges in inputs_to.items():
            frequency_edges = [
                e for e in in_edges 
                if e.get('relation') in ('resonates', 'phase_locks', 'synchronizes', 'amplifies')
            ]
            if len(frequency_edges) >= 2:
                resonance_boost = 1.0 + 0.2 * (len(frequency_edges) - 1)
                deltas.setdefault(tgt, {})
                deltas[tgt]['resonance_amplified'] = True
                deltas[tgt]['resonance_boost'] = resonance_boost
        
        return deltas


# ── SIMULATION FEEDBACK BRIDGE ────────────────────────────────────

@dataclass
class SimulationFeedback:
    """
    Bridges simulation results back into the StateGraph.
    
    Takes raw MultiFrontSimulation diagnostics and converts them
    into StateGraph node property updates.
    
    This closes the loop: Speech → Graph → Sim → Results → Graph → Speech
    """
    
    def ingest(self,
               sim_results: Dict,
               state_graph: StateGraph,
               front_mapping: Optional[Dict[int, str]] = None) -> Dict[str, Dict]:
        """
        Convert simulation diagnostics into StateGraph deltas.
        
        sim_results: output from MultiFrontSimulation.step()
        front_mapping: {front_index: node_name} e.g. {0: "beta_front", 1: "chi_front"}
        """
        if front_mapping is None:
            front_mapping = {0: "front_A", 1: "front_B"}
        
        deltas = {}
        
        fronts_data = sim_results.get('fronts', [])
        cross_talk = sim_results.get('cross_talk', 0)
        max_T = sim_results.get('max_T', 300)
        
        for front in fronts_data:
            idx = front.get('front_id', 0)
            node_name = front_mapping.get(idx, f"front_{idx}")
            
            deltas[node_name] = {
                'f_lock': front.get('f_lock', 0),
                'lock_strength': front.get('lock_strength', 1.0),
                'phase_target': front.get('phase', 'unknown'),
                'simulation_observed': True,
            }
            
            # Determine mode from lock strength
            lock = front.get('lock_strength', 1.0)
            if lock < 0.12:
                deltas[node_name]['mode'] = StateMode.LOCKED
            elif lock < 0.25:
                deltas[node_name]['mode'] = StateMode.OSCILLATORY
            elif lock < 0.5:
                deltas[node_name]['mode'] = StateMode.DRIVEN
            else:
                deltas[node_name]['mode'] = StateMode.UNSTABLE
        
        # Global field updates
        deltas['thermal_field'] = {
            'max_T': max_T,
            'simulation_observed': True,
        }
        
        if max_T > 600:
            deltas['thermal_field']['mode'] = StateMode.DRIVEN
        elif max_T > 400:
            deltas['thermal_field']['mode'] = StateMode.OSCILLATORY
        else:
            deltas['thermal_field']['mode'] = StateMode.STABLE
        
        # Cross-talk as coupling metric
        deltas['cross_talk'] = {
            'value': cross_talk,
            'simulation_observed': True,
        }
        
        if cross_talk > 0.3:
            deltas['cross_talk']['mode'] = StateMode.UNSTABLE
        elif cross_talk > 0.15:
            deltas['cross_talk']['mode'] = StateMode.OSCILLATORY
        else:
            deltas['cross_talk']['mode'] = StateMode.STABLE
        
        # Coupling between fronts inferred from cross-talk
        front_names = list(front_mapping.values())
        if len(front_names) >= 2:
            coupling_strength = cross_talk * 2  # Scale to 0-1 range
            deltas[f"{front_names[0]}__{front_names[1]}"] = {
                'coupling': coupling_strength,
                'relation': 'coupled via thermal/strain field',
            }
        
        return deltas


# ── MODE TRANSITION DETECTOR ──────────────────────────────────────

@dataclass 
class ModeTransitionDetector:
    """
    Detects when a node changes mode and triggers memory injection.
    
    Mode transitions are significant events:
    - STABLE → OSCILLATORY: something is perturbing the system
    - OSCILLATORY → LOCKED: phase-lock achieved (key event)
    - LOCKED → UNSTABLE: lock lost (failure mode)
    - DRIVEN → SATURATED: input ceiling reached
    """
    
    transition_memory: Dict[str, List[Tuple[int, StateMode, StateMode]]] = field(default_factory=dict)
    
    def detect(self, 
               node_name: str, 
               old_mode: StateMode, 
               new_mode: StateMode,
               iteration: int) -> Optional[Dict]:
        """
        Detect mode transition and return memory injection if significant.
        """
        if old_mode == new_mode:
            return None
        
        # Record transition
        if node_name not in self.transition_memory:
            self.transition_memory[node_name] = []
        self.transition_memory[node_name].append((iteration, old_mode, new_mode))
        
        # Significant transitions that trigger memory injections
        significant = [
            (StateMode.OSCILLATORY, StateMode.LOCKED),   # Lock achieved!
            (StateMode.LOCKED, StateMode.UNSTABLE),      # Lock lost
            (StateMode.DRIVEN, StateMode.SATURATED),     # Hit ceiling
            (StateMode.STABLE, StateMode.BIFURCATING),   # Branch ahead
            (StateMode.STABLE, StateMode.UNSTABLE),      # Sudden destabilization
            (StateMode.UNSTABLE, StateMode.LOCKED),      # Recovery to lock
        ]
        
        if (old_mode, new_mode) in significant:
            return {
                'event': 'mode_transition',
                'node': node_name,
                'from': old_mode.value,
                'to': new_mode.value,
                'iteration': iteration,
                'significance': 'high',
            }
        
        return {
            'event': 'mode_transition',
            'node': node_name,
            'from': old_mode.value,
            'to': new_mode.value,
            'iteration': iteration,
            'significance': 'low',
        }


# ── UPGRADED EVOLVE FUNCTION ──────────────────────────────────────

def evolve_v4(state_graph: StateGraph,
              constraint_graph: Dict,
              memory_fields: List[MemoryField],
              external_inputs: Optional[Dict] = None,
              sim_results: Optional[Dict] = None,
              front_mapping: Optional[Dict[int, str]] = None) -> Tuple[StateGraph, Dict]:
    """
    Upgraded evolve function with:
    - Active constraint enforcement (not just propagation)
    - Simulation feedback ingestion
    - Mode transition detection
    - Hysteresis memory
    """
    external_inputs = external_inputs or {}
    
    # Snapshot for memory evaluation
    snapshot = {
        "iteration": state_graph.iteration,
        "nodes": {k: v.properties for k, v in state_graph.nodes.items()},
        "modes": {k: v.mode for k, v in state_graph.nodes.items()},
        "external": external_inputs,
    }
    
    # 1. Memory field activation
    memory_deltas = {}
    for field in memory_fields:
        delta = field.evaluate(snapshot)
        for k, v in delta.items():
            memory_deltas.setdefault(k, {}).update(v)
    
    # 2. Active constraint enforcement (NEW)
    enforcer = ConstraintEnforcer()
    constraint_deltas = enforcer.apply(constraint_graph, state_graph, memory_fields)
    
    # 3. Simulation feedback (NEW)
    sim_deltas = {}
    if sim_results:
        feedback = SimulationFeedback()
        sim_deltas = feedback.ingest(sim_results, state_graph, front_mapping)
    
    # 4. Merge all deltas
    all_nodes = set()
    all_nodes.update(memory_deltas.keys())
    all_nodes.update(constraint_deltas.keys())
    all_nodes.update(sim_deltas.keys())
    
    transition_events = []
    detector = ModeTransitionDetector()
    
    for node_name in all_nodes:
        n = state_graph.get(node_name)
        old_mode = n.mode
        
        merged = {}
        if node_name in memory_deltas:
            merged.update(memory_deltas[node_name])
        if node_name in constraint_deltas:
            merged.update(constraint_deltas[node_name])
        if node_name in sim_deltas:
            merged.update(sim_deltas[node_name])
        
        n.properties.update(merged)
        
        # Mode update with enriched physics
        energy_in = merged.get('energy_inflow', merged.get('net_drive', 0))
        energy_out = merged.get('energy_outflow', merged.get('net_damp', 0))
        coupling = merged.get('coupling', 0)
        coherence = merged.get('coherence', 1.0)
        lock_strength = merged.get('lock_strength', None)
        saturated = merged.get('saturated', False)
        hysteretic_hold = merged.get('hysteretic_hold', False)
        
        # Determine new mode
        if lock_strength is not None and lock_strength < 0.12:
            new_mode = StateMode.LOCKED
        elif hysteretic_hold:
            new_mode = StateMode.HYSTERETIC
        elif saturated:
            new_mode = StateMode.SATURATED
        elif coherence < 0.3:
            new_mode = StateMode.UNSTABLE
        elif coupling > 0.7:
            new_mode = StateMode.OSCILLATORY
        elif energy_in > energy_out * 1.5:
            new_mode = StateMode.DRIVEN
        elif energy_out > energy_in * 1.5:
            new_mode = StateMode.SUPPRESSED
        else:
            new_mode = StateMode.STABLE
        
        # Detect transition
        if old_mode != new_mode:
            event = detector.detect(node_name, old_mode, new_mode, state_graph.iteration)
            if event:
                transition_events.append(event)
        
        n.mode = new_mode
    
    state_graph.iteration += 1
    
    # Build report
    report = {
        "iteration": state_graph.iteration,
        "nodes": {k: {"properties": v.properties, "mode": v.mode.value} 
                  for k, v in state_graph.nodes.items()},
        "transitions": transition_events,
        "constraint_effects": len(constraint_deltas),
        "simulation_feedback_applied": sim_results is not None,
    }
    
    return state_graph, report


# ── UPGRADED RUNTIME ──────────────────────────────────────────────

class EnergyRuntimeV4:
    """
    Full runtime with closed simulation loop.
    
    Speech → Compile → Constraint Graph
    → State Evolution (with memory, constraints, simulation feedback)
    → Updated State → Speech
    """
    
    def __init__(self, compiler, memory_fields=None):
        self.compiler = compiler
        self.state = StateGraph()
        self.memory_fields = memory_fields or []
        self.constraint_graph = None
        self.sim_bridge = SimulationFeedback()
        self.iteration = 0
    
    def step(self, text: str, external_inputs=None, sim_results=None, 
             front_mapping=None):
        """
        One full iteration of the runtime loop.
        
        Optionally accepts simulation results to close the physics loop.
        """
        # 1. Compile language → structure
        compiled = self.compiler.compile(text)
        self.constraint_graph = compiled
        
        # 2. Evolve system state
        self.state, report = evolve_v4(
            state_graph=self.state,
            constraint_graph=compiled,
            memory_fields=self.memory_fields,
            external_inputs=external_inputs,
            sim_results=sim_results,
            front_mapping=front_mapping,
        )
        
        self.iteration += 1
        
        return {
            "iteration": self.iteration,
            "nodes": {k: {"properties": v.properties, "mode": v.mode.value} 
                      for k, v in self.state.nodes.items()},
            "transitions": report.get("transitions", []),
            "constraints": compiled.get("triples", compiled.get("edges", [])),
            "invitations": compiled.get("invitations", []),
            "sim_feedback_applied": sim_results is not None,
        }

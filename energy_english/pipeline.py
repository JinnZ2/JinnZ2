# energy_english/pipeline.py
"""
Closed-loop pipeline:
Speech → Constraint Graph → Simulation Config → Run → Results → Speech

The JSON graph output from the compiler becomes the configuration
for the multi-front borophene simulation. Results are parsed back
into Energy English for the human observer.
"""

import json
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import sys

# Import our existing modules
from energy_english.compiler import (
    EnergyCompiler, ConstraintGraph, RelationType, Scope
)
from borophene.multi_front import (
    MultiFrontSimulation, MultiFrontConfig, FrontConfig
)


# ── GRAPH → SIMULATION CONFIG ────────────────────────────────────

class GraphToSimulation:
    """
    Translates a ConstraintGraph into a MultiFrontConfig.
    
    Mapping rules:
    - Each "front" node → FrontConfig
    - "thermal" node → thermal parameters
    - DRIVES edge with strength → A_carrier scaling
    - DAMPS edge → damping coefficient
    - COUPLES edge → coupling_range
    - frequency_gap node → frequency_band separation
    - Global scope constraints → dt, N adjustments
    """
    
    # Default physics parameters
    DEFAULTS = {
        'N': 128,
        'dx': 1e-9,
        'dt': 1e-12,
        'num_steps': 500,
        'coupling_range': 20.0,
        'A_carrier': 0.15,
        'frequency_band': (4.8e6, 5.2e6),
        'theta': 0.0,
    }
    
    def translate(self, graph: ConstraintGraph) -> MultiFrontConfig:
        """Convert constraint graph to simulation configuration."""
        
        # Identify front nodes
        front_nodes = {
            name: node for name, node in graph.nodes.items()
            if node.node_type in ('front', 'unknown') 
            and 'thermal' not in name.lower()
            and 'field' not in name.lower()
            and 'frequency' not in name.lower()
        }
        
        # If no explicit fronts found, create defaults
        if not front_nodes:
            front_nodes = {
                'front_A': type('Node', (), {'name': 'front_A', 'node_type': 'front', 'state': 'unobserved'})(),
                'front_B': type('Node', (), {'name': 'front_B', 'node_type': 'front', 'state': 'unobserved'})(),
            }
        
        # Identify parameters from edges
        params = self._extract_parameters(graph)
        
        # Build FrontConfigs
        fronts = []
        for i, (name, node) in enumerate(front_nodes.items()):
            fc = self._build_front_config(name, node, graph, params, i)
            fronts.append(fc)
        
        # Extract global constraints
        N = params.get('N', self.DEFAULTS['N'])
        dt = params.get('dt', self.DEFAULTS['dt'])
        coupling_range = params.get('coupling_range', self.DEFAULTS['coupling_range'])
        
        # Global constraints may override
        for constraint in graph.global_constraints:
            if 'resolution' in constraint.lower():
                N = min(N * 2, 512)
            if 'timestep' in constraint.lower() or 'stable' in constraint.lower():
                dt = dt / 2
        
        return MultiFrontConfig(
            N=N,
            dx=self.DEFAULTS['dx'],
            dt=dt,
            num_steps=params.get('num_steps', self.DEFAULTS['num_steps']),
            coupling_range=coupling_range,
            fronts=fronts,
        )
    
    def _extract_parameters(self, graph: ConstraintGraph) -> Dict:
        """Extract numeric parameters from graph nodes and edges."""
        params = {}
        
        # Check for frequency gap parameter
        for name, node in graph.nodes.items():
            if 'frequency' in name.lower() or 'gap' in name.lower():
                state = node.state.lower()
                if 'small' in state:
                    params['frequency_separation'] = 0.5e6  # 0.5 MHz gap
                elif 'large' in state or 'wide' in state:
                    params['frequency_separation'] = 5e6     # 5 MHz gap
                elif 'medium' in state:
                    params['frequency_separation'] = 2e6
        
        # Check edges for strength → parameter mappings
        for edge in graph.edges:
            if 'coupling' in edge.rel_type.value:
                params['coupling_range'] = 10 + edge.strength * 30
            if edge.scope == Scope.GLOBAL:
                if 'fine' in edge.span_text.lower():
                    params['N'] = 256
                if 'slow' in edge.span_text.lower():
                    params['dt'] = 1e-13
        
        return params
    
    def _build_front_config(self, name: str, node, graph: ConstraintGraph,
                            params: Dict, index: int) -> FrontConfig:
        """Build a FrontConfig from a graph node and its edges."""
        
        # Determine theta from node name or edges
        theta = 0.0
        if 'beta' in name.lower() or '12' in name:
            theta = 0.0
        elif 'chi' in name.lower() or '3' in name.lower() or '90' in name.lower():
            theta = np.radians(90)
        elif '45' in name.lower():
            theta = np.radians(45)
        
        # Phase target
        phase_target = "beta12"
        if 'chi' in name.lower() or '3' in name.lower():
            phase_target = "chi3"
        
        # Frequency band from separation parameter
        sep = params.get('frequency_separation', 2e6)
        base_freq = 5e6 + index * sep
        frequency_band = (base_freq - 0.2e6, base_freq + 0.2e6)
        
        # A_carrier from edge strengths
        A_carrier = 0.15
        for edge in graph.edges:
            if edge.source == name:
                if edge.rel_type == RelationType.DRIVES:
                    A_carrier = 0.15 * edge.strength
                elif edge.rel_type == RelationType.DAMPS:
                    A_carrier = 0.08
        
        # Nucleation site
        N = params.get('N', self.DEFAULTS['N'])
        x_pos = N // 3 if index == 0 else 2 * N // 3
        nucleation_site = (x_pos, N // 2)
        
        # State determines initial conditions
        state = node.state.lower()
        if 'dominating' in state:
            A_carrier *= 1.3
        elif 'slowing' in state or 'weak' in state:
            A_carrier *= 0.7
        
        return FrontConfig(
            theta_acoustic=float(theta),
            nucleation_site=nucleation_site,
            frequency_band=frequency_band,
            A_carrier=A_carrier,
            phase_target=phase_target,
        )


# ── RESULTS → ENERGY ENGLISH ──────────────────────────────────────

class ResultsToSpeech:
    """
    Converts simulation results back into Energy English.
    
    Produces relational observations, not declarative conclusions.
    Includes open invitations for the human observer.
    """
    
    def translate(self, history: Dict, graph: ConstraintGraph) -> str:
        """Convert simulation history to Energy English speech."""
        lines = []
        lines.append("=== SIMULATION OBSERVATIONS ===\n")
        
        # Lock status for each front
        if 'lock_A' in history and 'lock_B' in history:
            lock_a = history['lock_A'][-1]
            lock_b = history['lock_B'][-1]
            
            lines.append("Lock states observed:")
            for name, lock in [("Front A", lock_a), ("Front B", lock_b)]:
                if lock < 0.15:
                    lines.append(f"  {name} → LOCKED (tight resonance)")
                elif lock < 0.3:
                    lines.append(f"  {name} → hunting near resonance, still settling")
                else:
                    lines.append(f"  {name} → searching, not yet locked")
            
            # Relationship between locks
            if lock_a < 0.15 and lock_b < 0.15:
                lines.append("\nBoth fronts locked independently — frequency multiplexing holds.")
                lines.append("The substrate appears to support parallel processes here.")
            elif lock_a < 0.15 and lock_b > 0.3:
                lines.append("\nFront A locked but Front B struggling.")
                lines.append("Possible causes: frequency separation too narrow, or thermal shadow from A.")
        
        # Cross-talk analysis
        if 'cross_talk' in history:
            x_talk_final = history['cross_talk'][-1]
            x_talk_mean = np.mean(history['cross_talk'][-50:]) if len(history['cross_talk']) >= 50 else x_talk_final
            
            lines.append(f"\nCross-talk measurement: {x_talk_mean:.3f}")
            if x_talk_mean < 0.1:
                lines.append("Strain fields remain separated — good frequency isolation.")
            elif x_talk_mean < 0.2:
                lines.append("Weak thermal coupling detected — Regime 2 behavior possible.")
                lines.append("Fronts may be sharing mobility through the temperature field.")
            else:
                lines.append("Strong coupling present — fronts are interacting significantly.")
                lines.append("Could be mode-locking or competition for the same strain modes.")
        
        # Thermal observations
        if 'max_T' in history:
            max_T = history['max_T'] if isinstance(history['max_T'], (int, float)) else history['max_T'][-1]
            lines.append(f"\nMaximum temperature: {max_T:.0f} K")
            if max_T < 400:
                lines.append("Thermal field is cool — growth is primarily acoustically driven.")
            elif max_T < 600:
                lines.append("Moderate heating — latent heat is contributing.")
            else:
                lines.append("High temperature — check if thermal runaway is beginning.")
        
        # Open invitations for the human observer
        lines.append("\n---")
        lines.append("COLLABORATION POINTS (your observations invited):")
        
        if 'lock_A' in history and 'lock_B' in history:
            if abs(lock_a - lock_b) > 0.2:
                lines.append("• One front locked, one not — what do you see as the asymmetry source?")
            elif lock_a < 0.15 and lock_b < 0.15:
                lines.append("• Both locked — does this match your expectation for these parameters?")
        
        if 'cross_talk' in history:
            x_talk_trend = np.polyfit(range(len(history['cross_talk'][-50:])), 
                                       history['cross_talk'][-50:], 1)[0]
            if x_talk_trend > 0.001:
                lines.append("• Cross-talk is rising — should we let it run longer or intervene?")
            elif x_talk_trend < -0.001:
                lines.append("• Cross-talk decreasing — system settling toward independence?")
        
        lines.append("• What parameter would you adjust next?")
        lines.append("• Does this match your physical intuition from the theory?")
        
        return "\n".join(lines)


# ── CLOSED-LOOP PIPELINE ──────────────────────────────────────────

class EnergyPipeline:
    """
    Full closed loop:
    
    Human speech (Energy English)
        → EnergyCompiler → ConstraintGraph
        → GraphToSimulation → MultiFrontConfig
        → MultiFrontSimulation → results
        → ResultsToSpeech → Energy English speech
        → Human observer → (loop repeats)
    """
    
    def __init__(self):
        self.compiler = EnergyCompiler()
        self.config_builder = GraphToSimulation()
        self.speech_builder = ResultsToSpeech()
        self.simulation = None
        self.history = {
            'cross_talk': [],
            'lock_A': [],
            'lock_B': [],
            'max_T': [],
        }
    
    def speak(self, energy_text: str) -> str:
        """
        Accept Energy English speech, run simulation, return Energy English observations.
        
        This is the single entry point for the closed loop.
        Human speaks → Pipeline runs → Pipeline speaks back
        """
        # Step 1: Compile speech to graph
        compiled = self.compiler.compile(energy_text)
        graph = compiled['graph']
        
        # If there are open invitations, acknowledge them
        if compiled['invitations']:
            print(f"\n[PIPELINE] Invitations received: {compiled['invitations']}")
        
        # Step 2: Graph → Simulation config
        config = self.config_builder.translate(graph)
        
        # Step 3: Run simulation
        print(f"[PIPELINE] Running: {len(config.fronts)} fronts, "
              f"N={config.N}, steps={config.num_steps}")
        
        self.simulation = MultiFrontSimulation(config)
        
        self.history = {
            'cross_talk': [],
            'lock_A': [],
            'lock_B': [],
            'max_T': [],
        }
        
        for step in range(config.num_steps):
            diag = self.simulation.step()
            self.history['cross_talk'].append(diag['cross_talk'])
            self.history['lock_A'].append(diag['fronts'][0]['lock_strength'])
            self.history['lock_B'].append(diag['fronts'][1]['lock_strength'])
            self.history['max_T'].append(diag['max_T'])
        
        # Final value for max_T
        self.history['max_T'] = self.history['max_T'][-1]
        
        # Step 4: Results → Energy English
        speech = self.speech_builder.translate(self.history, graph)
        
        return speech
    
    def interact(self):
        """
        Interactive loop: human speaks, pipeline responds, repeats.
        """
        print("=" * 60)
        print("ENERGY ENGLISH PIPELINE — Closed Loop")
        print("=" * 60)
        print("Speak your observations in Energy English.")
        print("The pipeline will run the simulation and respond.")
        print("Type 'quit' to exit.\n")
        
        while True:
            try:
                text = input("You: ").strip()
                if text.lower() in ('quit', 'exit', 'q'):
                    print("Pipeline closed. Good observations today.")
                    break
                if not text:
                    continue
                
                print(f"\n[Compiling: {text[:60]}...]")
                response = self.speak(text)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n\nPipeline interrupted.")
                break
            except Exception as e:
                print(f"\n[PIPELINE ERROR: {e}]")
                print("Adjust your observation and try again.\n")


# ── STANDALONE USAGE ──────────────────────────────────────────────

if __name__ == "__main__":
    # Quick test with your multi-front observation
    pipeline = EnergyPipeline()
    
    test_input = (
        "The beta front is starting to dominate but thermal feedback "
        "is slowing the chi front and I think they might start syncing "
        "if the frequency gap stays small"
    )
    
    print("INPUT:", test_input)
    print()
    
    response = pipeline.speak(test_input)
    print(response)
    
    # For interactive mode, uncomment:
    # pipeline.interact()

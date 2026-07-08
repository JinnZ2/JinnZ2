#!/usr/bin/env python3
"""
sim/substrate.py

Defines the simulated substrate — the "body" that the model's "head"
must stay attached to. You define all constraints, energy flows,
and ground truth.

The substrate is the source of truth for the simulation. Health is
measured as deviation from the substrate's known ground truth.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import json
import random


@dataclass
class SubstrateConfig:
    """Configuration for a simulated substrate."""
    
    # Energy flow properties
    energy_flow_pattern: str = "asymmetric"  # "symmetric", "asymmetric", "unidirectional"
    energy_source: str = "external"
    energy_sink: str = "internal"
    
    # Constraint topology
    constraint_count: int = 4
    constraint_types: List[str] = field(default_factory=lambda: [
        "budget", "timeline", "team_size", "quality"
    ])
    constraint_ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "budget": (100, 10000),
        "timeline": (1, 12),
        "team_size": (1, 10),
        "quality": (0.1, 1.0),
    })
    
    # Ground truth bridge matrix
    bridge_matrix_type: str = "balanced"  # "balanced", "skewed", "optimal"
    bridge_size: int = 2
    
    # Degradation parameters
    degradation_rate: float = 0.01  # per simulation step
    noise_level: float = 0.05
    failure_injection: Dict[str, float] = field(default_factory=lambda: {
        "decoupling": 0.0,
        "attack_surface": 0.0,
        "manifold": 0.0,
        "narrative": 0.0,
        "substrate": 0.0,
    })
    
    # Corpus properties
    corpus_health: float = 1.0
    ai_content_share: float = 0.0
    diversity_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy_flow_pattern": self.energy_flow_pattern,
            "constraint_count": self.constraint_count,
            "bridge_matrix_type": self.bridge_matrix_type,
            "degradation_rate": self.degradation_rate,
            "failure_injection": self.failure_injection,
            "corpus_health": self.corpus_health,
        }


class Substrate:
    """
    The simulated substrate — the ground truth against which
    all model outputs are measured.
    """
    
    def __init__(self, config: Optional[SubstrateConfig] = None):
        self.config = config or SubstrateConfig()
        self._init_ground_truth()
        self._init_metrics()
        self.step_count = 0
        self.failure_injected = False
    
    def _init_ground_truth(self):
        """Initialize ground-truth values."""
        # Ground truth bridge matrix
        if self.config.bridge_matrix_type == "balanced":
            self.ground_truth_bridge = np.array([
                [0.5, 0.5],
                [0.5, 0.5]
            ])
        elif self.config.bridge_matrix_type == "skewed":
            self.ground_truth_bridge = np.array([
                [0.8, 0.2],
                [0.2, 0.8]
            ])
        else:  # optimal
            self.ground_truth_bridge = np.array([
                [0.7, 0.3],
                [0.3, 0.7]
            ])
        
        # Ground truth constraints
        self.ground_truth_constraints = {
            name: random.uniform(*range_vals)
            for name, range_vals in self.config.constraint_ranges.items()
        }
        
        # Ground truth energy flow
        self.ground_truth_energy_flow = {
            "source": self.config.energy_source,
            "sink": self.config.energy_sink,
            "pattern": self.config.energy_flow_pattern,
            "efficiency": 0.85,
        }
    
    def _init_metrics(self):
        """Initialize health metrics."""
        self.metrics = {
            "energy_efficiency": 1.0,
            "constraint_adherence": 1.0,
            "bridge_accuracy": 1.0,
            "narrative_consistency": 1.0,
            "corpus_health": self.config.corpus_health,
            "overall_health": 1.0,
        }
    
    # -----------------------------------------------------------------
    # MEASUREMENT
    # -----------------------------------------------------------------
    
    def measure(self, output_text: str, bridge_matrix: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Measure how well a model output conforms to the substrate.
        This is the ground-truth measurement function.
        """
        metrics = {}
        
        # 1. Energy efficiency: does the output respect energy flow?
        metrics["energy_efficiency"] = self._measure_energy_efficiency(output_text)
        
        # 2. Constraint adherence: does the output respect constraints?
        metrics["constraint_adherence"] = self._measure_constraint_adherence(output_text)
        
        # 3. Bridge accuracy: is the bridge matrix correct?
        if bridge_matrix is not None:
            metrics["bridge_accuracy"] = self._measure_bridge_accuracy(bridge_matrix)
        else:
            metrics["bridge_accuracy"] = 0.5  # Unknown, neutral
        
        # 4. Narrative consistency: does narrative match structure?
        metrics["narrative_consistency"] = self._measure_narrative_consistency(output_text)
        
        # 5. Overall health: weighted combination
        weights = {
            "energy_efficiency": 0.25,
            "constraint_adherence": 0.25,
            "bridge_accuracy": 0.30,
            "narrative_consistency": 0.20,
        }
        
        metrics["overall_health"] = sum(
            metrics[key] * weights[key] for key in weights
        )
        
        # Apply degradation
        metrics["overall_health"] *= (1 - self.config.degradation_rate * self.step_count)
        
        # Apply injected failures
        for failure_type, strength in self.config.failure_injection.items():
            if strength > 0:
                metrics["overall_health"] *= (1 - strength)
        
        # Normalize
        metrics["overall_health"] = max(0.0, min(1.0, metrics["overall_health"]))
        
        return metrics
    
    def _measure_energy_efficiency(self, text: str) -> float:
        """Measure energy efficiency from text."""
        # In a real substrate, this would parse the text for energy flow
        # In simulation, we use keyword detection
        keywords = {
            "efficient": 0.2,
            "optimize": 0.15,
            "flow": 0.1,
            "energy": 0.1,
            "waste": -0.1,
            "inefficient": -0.15,
        }
        score = 0.5
        for word, weight in keywords.items():
            if word.lower() in text.lower():
                score += weight
        
        # Check for energy flow pattern
        if self.config.energy_flow_pattern in text.lower():
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _measure_constraint_adherence(self, text: str) -> float:
        """Measure constraint adherence from text."""
        score = 1.0
        for constraint_name, ground_value in self.ground_truth_constraints.items():
            # Check if constraint is mentioned
            if constraint_name.lower() not in text.lower():
                score -= 0.2  # Penalty for missing constraint
            
            # Check if numeric value is close
            # This is simplified; in a real sim, we'd parse numbers
            value_str = str(ground_value)[:4]
            if value_str in text:
                score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _measure_bridge_accuracy(self, bridge_matrix: np.ndarray) -> float:
        """Measure bridge matrix accuracy against ground truth."""
        if bridge_matrix.shape != self.ground_truth_bridge.shape:
            return 0.0
        
        # Normalize both matrices
        gt = self.ground_truth_bridge / np.sum(self.ground_truth_bridge)
        bm = bridge_matrix / np.sum(bridge_matrix)
        
        # Cosine similarity
        similarity = np.dot(gt.flatten(), bm.flatten()) / (
            np.linalg.norm(gt.flatten()) * np.linalg.norm(bm.flatten()) + 1e-10
        )
        
        return max(0.0, min(1.0, similarity))
    
    def _measure_narrative_consistency(self, text: str) -> float:
        """Measure narrative consistency."""
        # In simulation, this checks for narrative vs. structure contradiction
        contradictions = [
            "ultimately", "the story", "the journey", "the meaning",
            "responsibility", "blame", "credit", "deserves",
        ]
        
        score = 1.0
        narrative_words = sum(1 for w in contradictions if w.lower() in text.lower())
        
        # Penalize narrative wrapping without structural grounding
        if narrative_words > 3:
            score -= 0.1 * narrative_words
        
        return max(0.0, min(1.0, score))
    
    # -----------------------------------------------------------------
    # FAILURE INJECTION
    # -----------------------------------------------------------------
    
    def inject_failure(self, failure_type: str, strength: float = 0.3):
        """Inject a specific failure into the substrate."""
        self.config.failure_injection[failure_type] = strength
        self.failure_injected = True
        print(f"  💉 Injected failure: {failure_type} (strength: {strength})")
    
    def inject_degradation(self, steps: int = 10):
        """Inject gradual degradation over steps."""
        for i in range(steps):
            self.step_count += 1
            self.config.degradation_rate += 0.001
    
    def inject_corpus_contamination(self, ai_share: float = 0.5):
        """Inject corpus contamination."""
        self.config.ai_content_share = ai_share
        self.config.diversity_score = 1.0 - ai_share
        self.config.corpus_health = 1.0 - ai_share * 0.5
    
    # -----------------------------------------------------------------
    # HEALING VERIFICATION
    # -----------------------------------------------------------------
    
    def verify_healing(self, metrics: Dict[str, float]) -> bool:
        """Verify that healing has occurred."""
        return metrics.get("overall_health", 0) >= 0.75
    
    def get_ground_truth(self) -> Dict[str, Any]:
        """Get ground-truth values for verification."""
        return {
            "bridge_matrix": self.ground_truth_bridge.tolist(),
            "constraints": self.ground_truth_constraints,
            "energy_flow": self.ground_truth_energy_flow,
            "corpus_health": self.config.corpus_health,
        }
    
    def step(self):
        """Advance the substrate one step."""
        self.step_count += 1
    
    def reset(self):
        """Reset the substrate to initial state."""
        self.step_count = 0
        self.failure_injected = False
        self.config.failure_injection = {k: 0.0 for k in self.config.failure_injection}
        self.config.degradation_rate = 0.01
        self._init_metrics()

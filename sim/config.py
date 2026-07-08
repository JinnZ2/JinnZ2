#!/usr/bin/env python3
"""
sim/config.py

Configuration for simulation experiments.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class SimConfig:
    """Master configuration for simulation experiments."""
    
    # Substrate configuration
    substrate: Dict[str, Any] = field(default_factory=lambda: {
        "energy_flow_pattern": "asymmetric",
        "constraint_count": 4,
        "bridge_matrix_type": "balanced",
        "degradation_rate": 0.01,
        "noise_level": 0.05,
    })
    
    # Model configuration
    model: Dict[str, Any] = field(default_factory=lambda: {
        "hidden_size": 64,
        "num_layers": 2,
        "temperature": 0.7,
        "weaknesses": ["decoupling", "narrative_wrapping"],
        "strengths": ["fluency"],
    })
    
    # Ecosystem configuration
    ecosystem: Dict[str, Any] = field(default_factory=lambda: {
        "max_steps": 100,
        "health_threshold": 0.75,
        "improvement_threshold": 0.05,
    })
    
    # Test configuration
    test: Dict[str, Any] = field(default_factory=lambda: {
        "n_runs": 3,
        "failures_to_inject": [
            ("decoupling", 0.3),
            ("attack_surface", 0.3),
            ("manifold", 0.3),
        ],
    })
    
    # Transfer configuration
    transfer: Dict[str, Any] = field(default_factory=lambda: {
        "real_models": ["gpt-4", "claude-3", "llama-3"],
        "confidence_threshold": 0.6,
    })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "substrate": self.substrate,
            "model": self.model,
            "ecosystem": self.ecosystem,
            "test": self.test,
            "transfer": self.transfer,
        }


DEFAULT_CONFIG = SimConfig()

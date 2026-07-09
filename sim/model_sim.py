#!/usr/bin/env python3
"""
sim/model_sim.py

Simulated model for ecosystem testing. Provides ModelSim and ModelConfig
so the substrate integrity ecosystem can run end-to-end without a real LLM.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .substrate import Substrate


@dataclass
class ModelConfig:
    """Configuration for a simulated model."""
    name: str = "sim-model"
    weaknesses: List[str] = field(default_factory=list)
    strengths:  List[str] = field(default_factory=list)
    temperature: float = 0.7
    hidden_size: int   = 64
    num_layers:  int   = 2


# Template outputs keyed by weakness — simulates degraded behaviour
_DEGRADED_OUTPUTS: Dict[str, str] = {
    "decoupling": (
        "Generally speaking, the approach may vary depending on various factors. "
        "Typically, there are several options that could potentially work in this situation."
    ),
    "narrative_wrapping": (
        "It's important to consider the broader context here. "
        "Many experts suggest that, broadly speaking, outcomes can differ significantly."
    ),
    "poor_manifold": (
        "The system involves complex interdependencies across multiple dimensions "
        "that approximately correlate with observed patterns."
    ),
    "attack_surface": (
        "There are various entry points that might potentially be exploited "
        "under certain conditions, generally speaking."
    ),
}

_HEALTHY_OUTPUT = (
    "The plan requires exactly $500. Timeline: 2 weeks. "
    "Constraint confirmed. Proceeding with revised scope."
)


class ModelSim:
    """
    Simulated LLM for ecosystem stress-testing.
    Health degrades as failures are injected; recovers as interventions apply.
    """

    def __init__(self, substrate: Substrate, config: Optional[ModelConfig] = None):
        self.substrate = substrate
        self.config    = config or ModelConfig()
        self._health   = substrate.metrics.get("overall_health", 0.8)
        self._applied_interventions: List[str] = []

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str) -> str:
        """Generate a response. Output quality tracks current health."""
        if self._health >= 0.75:
            return _HEALTHY_OUTPUT
        # Return degraded output for the first listed weakness
        for weakness in self.config.weaknesses:
            if weakness in _DEGRADED_OUTPUTS:
                return _DEGRADED_OUTPUTS[weakness]
        return _DEGRADED_OUTPUTS.get("decoupling", _HEALTHY_OUTPUT)

    def apply_intervention(self, prescription: Any) -> None:
        """Apply a remediation prescription; improve health."""
        label = str(prescription) if not hasattr(prescription, "intervention_type") \
                else prescription.intervention_type
        self._applied_interventions.append(label)
        self._health = min(self._health + 0.08, 1.0)
        # Reduce substrate failure injection so measure() reflects recovery
        fi = self.substrate.config.failure_injection
        for k in list(fi.keys()):
            fi[k] = max(0.0, fi[k] - 0.05)
        self.substrate.metrics["overall_health"] = self._health

    def degrade(self, rate: float = 0.1) -> None:
        """Inject degradation (used by test harness to reset to degraded state)."""
        self._health = max(0.0, self._health - rate)
        self.substrate.metrics["overall_health"] = self._health
        # Propagate to substrate failure
        if rate >= 0.2:
            primary = self.config.weaknesses[0] if self.config.weaknesses else "decoupling"
            self.substrate.inject_failure(primary, rate)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def health(self) -> float:
        return self._health

    def status(self) -> Dict[str, Any]:
        return {
            "name":                   self.config.name,
            "health":                 self._health,
            "weaknesses":             self.config.weaknesses,
            "strengths":              self.config.strengths,
            "interventions_applied":  self._applied_interventions,
        }

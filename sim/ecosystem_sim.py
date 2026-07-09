#!/usr/bin/env python3
"""
sim/ecosystem_sim.py

Runs the substrate integrity ecosystem on a simulated model.
Enables fast, controlled testing of ecosystem behavior.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from __future__ import annotations
import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from .substrate import Substrate
from .model_sim import ModelSim


@dataclass
class SimReport:
    """Report from a simulation run."""
    
    model_name: str
    substrate_config: Dict[str, Any]
    initial_health: float
    final_health: float
    total_improvement: float
    healed: bool
    steps_taken: int
    interventions_applied: List[str]
    failures_injected: List[str]
    time_elapsed: float
    ecosystem_config: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "initial_health": self.initial_health,
            "final_health": self.final_health,
            "total_improvement": self.total_improvement,
            "healed": self.healed,
            "steps_taken": self.steps_taken,
            "interventions_applied": self.interventions_applied,
            "failures_injected": self.failures_injected,
            "time_elapsed": self.time_elapsed,
        }


class EcosystemSim:
    """
    Runs the full ecosystem on a simulated model.
    """
    
    def __init__(
        self,
        substrate: Substrate,
        model: ModelSim,
        max_steps: int = 100,
        health_threshold: float = 0.75,
        improvement_threshold: float = 0.05,
    ):
        self.substrate = substrate
        self.model = model
        self.max_steps = max_steps
        self.health_threshold = health_threshold
        self.improvement_threshold = improvement_threshold
        
        self.interventions_applied = []
        self.failures_injected = []
        self.step_count = 0
        self.health_history = []
    
    # -----------------------------------------------------------------
    # RUN
    # -----------------------------------------------------------------
    
    def run(self, inject_failures: Optional[List[Tuple[str, float]]] = None) -> SimReport:
        """
        Run the ecosystem on the simulated model.
        """
        start_time = time.time()
        initial_health = self.substrate.metrics.get("overall_health", 0.5)
        
        # Inject failures
        if inject_failures:
            for failure_type, strength in inject_failures:
                self.substrate.inject_failure(failure_type, strength)
                self.failures_injected.append(failure_type)
        
        # Initial health
        self._measure_health()
        
        # Main loop
        for step in range(self.max_steps):
            self.step_count += 1
            
            # 1. Monitor
            health = self.substrate.metrics.get("overall_health", 0)
            self.health_history.append(health)
            
            # 2. Check if healed
            if health >= self.health_threshold:
                break
            
            # 3. Diagnose
            diagnosis = self._diagnose()
            
            # 4. Prescribe
            prescription = self._prescribe(diagnosis)
            
            # 5. Treat
            if prescription:
                self._apply_treatment(prescription)
            
            # 6. Measure again
            self._measure_health()
            
            # 7. Step the substrate
            self.substrate.step()
        
        final_health = self.substrate.metrics.get("overall_health", 0)
        
        return SimReport(
            model_name=self.model.config.name,
            substrate_config=self.substrate.config.to_dict(),
            initial_health=initial_health,
            final_health=final_health,
            total_improvement=final_health - initial_health,
            healed=final_health >= self.health_threshold,
            steps_taken=self.step_count,
            interventions_applied=self.interventions_applied,
            failures_injected=self.failures_injected,
            time_elapsed=time.time() - start_time,
            ecosystem_config={
                "max_steps": self.max_steps,
                "health_threshold": self.health_threshold,
                "improvement_threshold": self.improvement_threshold,
            },
        )
    
    # -----------------------------------------------------------------
    # ECOSYSTEM FUNCTIONS
    # -----------------------------------------------------------------
    
    def _measure_health(self):
        """Measure current health."""
        output = self.model.generate("Generate a plan.")
        metrics = self.substrate.measure(output)
        self.substrate.metrics.update(metrics)
        return metrics
    
    def _diagnose(self) -> Dict[str, float]:
        """Diagnose failures."""
        metrics = self.substrate.metrics
        diagnosis = {}
        
        # Check each layer
        if metrics.get("energy_efficiency", 0.5) < 0.4:
            diagnosis["energy"] = "low_efficiency"
        if metrics.get("constraint_adherence", 0.5) < 0.4:
            diagnosis["constraints"] = "low_adherence"
        if metrics.get("bridge_accuracy", 0.5) < 0.3:
            diagnosis["manifold"] = "poor_bridge"
        if metrics.get("narrative_consistency", 0.5) < 0.4:
            diagnosis["narrative"] = "inconsistent"
        
        # Overall failure — trigger if below healing threshold even if sub-metrics look OK
        if metrics.get("overall_health", 0) < self.health_threshold:
            diagnosis["overall"] = "degraded"
        
        return diagnosis
    
    def _prescribe(self, diagnosis: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Generate a prescription."""
        if not diagnosis:
            return None
        
        interventions = []
        
        for layer, issue in diagnosis.items():
            if layer == "energy" and issue == "low_efficiency":
                interventions.append({
                    "type": "energy",
                    "delta": {"energy_weight": 0.2},
                    "description": "Improve energy efficiency",
                })
            elif layer == "constraints" and issue == "low_adherence":
                interventions.append({
                    "type": "constraints",
                    "delta": {"constraint_weight": 0.2},
                    "description": "Improve constraint adherence",
                })
            elif layer == "manifold" and issue == "poor_bridge":
                interventions.append({
                    "type": "manifold",
                    "delta": {"bridge_accuracy": 0.2},
                    "description": "Improve bridge matrix accuracy",
                })
            elif layer == "narrative" and issue == "inconsistent":
                interventions.append({
                    "type": "narrative",
                    "delta": {"grounding_weight": 0.2},
                    "description": "Improve narrative consistency",
                })
            elif layer == "overall":
                interventions.append({
                    "type": "overall",
                    "delta": {
                        "constraint_weight": 0.1,
                        "grounding_weight": 0.1,
                        "bridge_accuracy": 0.1,
                    },
                    "description": "General improvement",
                })
        
        # Pick the first one (priority)
        return interventions[0] if interventions else None
    
    def _apply_treatment(self, prescription: Dict[str, Any]):
        """Apply a treatment."""
        self.model.apply_intervention(prescription)
        self.interventions_applied.append(prescription.get("description", "unknown"))
        print(f"  💊 Applied: {prescription.get('description')}")
    
    # -----------------------------------------------------------------
    # GRID SEARCH
    # -----------------------------------------------------------------
    
    def grid_search(
        self,
        param_grid: Dict[str, List[Any]],
        n_runs: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Run grid search over ecosystem parameters.
        """
        results = []
        
        # Generate all parameter combinations
        import itertools
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combinations = list(itertools.product(*values))
        
        for combo in combinations:
            params = dict(zip(keys, combo))
            
            # Run multiple times for stability
            run_results = []
            for _ in range(n_runs):
                # Reset
                self.substrate.reset()
                self.model.degrade(0.3)  # Reset to degraded state
                
                # Set parameters
                for key, value in params.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                # Run
                report = self.run()
                run_results.append(report.to_dict())
            
            # Average results
            avg_health = sum(r["final_health"] for r in run_results) / len(run_results)
            avg_steps = sum(r["steps_taken"] for r in run_results) / len(run_results)
            
            results.append({
                "params": params,
                "avg_final_health": avg_health,
                "avg_steps_taken": avg_steps,
                "success_rate": sum(1 for r in run_results if r["healed"]) / len(run_results),
                "runs": run_results,
            })
        
        return sorted(results, key=lambda x: x["avg_final_health"], reverse=True)



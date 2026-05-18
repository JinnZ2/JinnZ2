# sim_runner.py
# Physics-first simulation: test resolver paths before returning
# Falsifiable, offline-capable, constraint-based

class ConstraintSimulator:
    """
    For each resolver path, run physics models:
    - Thermodynamic feasibility (can the reaction happen?)
    - Time feasibility (will it finish in your window?)
    - Equipment feasibility (can you actually do this with what you have?)
    - Closure detection (what would break this path?)
    """

    def simulate_path(self, path: Dict, context: Query) -> Dict:
        """
        Returns: feasibility_score + failure_modes + parameter sensitivity
        """
        # Energy balance check
        energy_required = self._calculate_energy(path)
        energy_available = self._estimate_available_energy(context)
        energy_feasible = energy_required <= energy_available

        # Time balance check
        time_required = path["total_dwell_hours"]
        time_available = context.time_available * 24
        time_feasible = time_required <= time_available

        # Equipment dependency check
        missing_critical = [e for e in path["equipment"]
                           if e not in context.equipment_on_hand
                           and e not in salvage_index]

        # Sensitivity analysis: which parameters most affect outcome?
        sensitivities = self._analyze_sensitivities(path, context)

        # Hidden dependencies: what wasn't obvious?
        hidden = self._detect_hidden_dependencies(path)

        return {
            "path_id": path["id"],
            "energy_feasible": energy_feasible,
            "time_feasible": time_feasible,
            "equipment_feasible": len(missing_critical) == 0,
            "composite_feasibility": (
                energy_feasible * 0.33 +
                time_feasible * 0.33 +
                (1.0 if len(missing_critical) == 0 else 0.5) * 0.34
            ),
            "failure_modes": self._identify_failure_modes(path, energy_feasible, time_feasible),
            "sensitive_parameters": sensitivities,
            "hidden_dependencies": hidden
        }

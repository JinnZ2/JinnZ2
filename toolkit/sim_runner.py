# sim_runner.py
# Physics-first simulation: test resolver paths before returning
# Falsifiable, offline-capable, constraint-based

from typing import Dict, List, Optional

from salvage_chemistry_resolver import Query, ProbabilityTreeResolver


class ConstraintSimulator:
    """
    For each resolver path, run physics models:
    - Thermodynamic feasibility (can the reaction happen?)
    - Time feasibility (will it finish in your window?)
    - Equipment feasibility (can you actually do this with what you have?)
    - Closure detection (what would break this path?)
    """

    def __init__(self, resolver: Optional[ProbabilityTreeResolver] = None):
        """
        Optionally bind to a resolver so we can consult its salvage_index.
        If no resolver is supplied, the simulator treats salvage_index as empty
        (every missing equipment item is counted as unsalvageable).
        """
        self.resolver = resolver
        self.salvage_index: Dict[str, list] = (
            resolver.salvage_index if resolver is not None else {}
        )

    def simulate_path(self, path: Dict, context: Query) -> Dict:
        """
        Returns: feasibility_score + failure_modes + parameter sensitivity.

        `path` accepts either a per-node dict from
        ProbabilityTreeResolver._build_traversal_tree (fields: id,
        description, mode, dwell_hours, success_probability, status,
        closure_reason, equipment_needed, missing_equipment,
        salvage_risk, children, ...) or a path-level aggregate dict
        with total_dwell_hours / equipment fields.
        """
        # Reconcile field-name variants between resolver-node and
        # path-aggregate shapes:
        total_dwell = path.get("total_dwell_hours")
        if total_dwell is None:
            total_dwell = path.get("dwell_hours", 0)

        equipment = path.get("equipment") or path.get("equipment_needed", [])

        # Energy balance check
        energy_required = self._calculate_energy(path)
        energy_available = self._estimate_available_energy(context)
        energy_feasible = energy_required <= energy_available

        # Time balance check (QueryContext uses time_available_days)
        time_available_hours = (context.time_available_days or 0) * 24
        time_feasible = total_dwell <= time_available_hours

        # Equipment dependency check -- an item is critical missing
        # only if it's neither on-hand nor recoverable via salvage_index.
        on_hand = set(context.equipment_on_hand or [])
        missing_critical = [
            e for e in equipment
            if e not in on_hand and not self.salvage_index.get(e)
        ]
        equipment_feasible = len(missing_critical) == 0

        # Sensitivity analysis: which parameters most affect outcome?
        sensitivities = self._analyze_sensitivities(path, context)

        # Hidden dependencies: what wasn't obvious from the equipment list?
        hidden = self._detect_hidden_dependencies(path)

        return {
            "path_id": path.get("id", "unknown"),
            "energy_feasible": energy_feasible,
            "time_feasible": time_feasible,
            "equipment_feasible": equipment_feasible,
            "composite_feasibility": (
                (1.0 if energy_feasible else 0.0) * 0.33
                + (1.0 if time_feasible else 0.0) * 0.33
                + (1.0 if equipment_feasible else 0.5) * 0.34
            ),
            "failure_modes": self._identify_failure_modes(
                path, energy_feasible, time_feasible, missing_critical
            ),
            "missing_equipment": missing_critical,
            "sensitive_parameters": sensitivities,
            "hidden_dependencies": hidden,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _calculate_energy(self, path: Dict) -> float:
        """
        Energy required by the path. Approximation:
          mode_baseline + (peak_temp_C * dwell_hours * 0.1)

        Mode baselines reflect typical floor cost: thermal > hybrid >
        synthesize > extract > ferment. Calibrate against
        feedback_loop_module observations to refine.
        """
        # Extract peak temperature (Celsius) when available.
        temp_max = 100.0
        temp_range = path.get("temp_range")
        if isinstance(temp_range, (list, tuple)) and len(temp_range) >= 2:
            try:
                temp_max = float(temp_range[1])
            except (TypeError, ValueError):
                pass

        dwell = path.get("dwell_hours") or path.get("total_dwell_hours") or 0
        mode = (path.get("mode") or "").lower()
        mode_base = {
            "thermal": 50.0,
            "hybrid": 30.0,
            "synthesize": 20.0,
            "extract": 10.0,
            "ferment": 5.0,
        }.get(mode, 15.0)

        return mode_base + (temp_max * dwell * 0.1)

    def _estimate_available_energy(self, context: Query) -> float:
        """
        Available energy estimate from context. Heat sources count
        the most; days available give a budget multiplier.

        Calibrate against feedback_loop_module observations once
        field outcomes are logged.
        """
        days = max(context.time_available_days or 1, 1)
        heat_markers = ("heat", "fire", "kiln", "stove", "torch", "furnace")
        on_hand = context.equipment_on_hand or []
        has_heat = any(
            any(marker in item.lower() for marker in heat_markers)
            for item in on_hand
        )
        base = 100.0 if has_heat else 25.0
        return base * days

    def _analyze_sensitivities(self, path: Dict, context: Query) -> List[str]:
        """
        Which input parameters most affect this path's outcome?

        Approximation by mode: thermal / ferment are temperature- and
        dwell-dominated; hybrid / synthesize are component-driven;
        extract is equipment-driven.
        """
        mode = (path.get("mode") or "").lower()
        if mode in ("thermal", "ferment"):
            return ["temperature_range", "dwell_hours", "ambient_temp"]
        if mode in ("hybrid", "synthesize"):
            return ["component_availability", "dwell_hours", "temperature_range"]
        return ["equipment_availability", "salvage_coverage"]

    def _detect_hidden_dependencies(self, path: Dict) -> List[str]:
        """
        Surface dependencies implied by the description/mode but not
        listed in equipment_needed. These are common-sense additions
        the resolver hasn't been taught yet -- prime candidates for
        feedback_loop calibration.
        """
        hidden: List[str] = []
        desc = (path.get("description") or "").lower()
        equipment_repr = str(path.get("equipment_needed") or path.get("equipment") or "").lower()

        if "ferment" in desc and "starter" not in equipment_repr:
            hidden.append("starter_culture (implied by fermentation)")
        if any(w in desc for w in ("kiln", "furnace", "1700", "high heat", "high-fire", "pyrolysis")):
            hidden.append("refractory_lining (implied by high temperature)")
        if any(w in desc for w in ("lye", "naoh", "koh", "caustic", "alkaline")):
            hidden.append("ppe_gloves_eye_protection (implied by caustic chemistry)")
        if "press" in desc and "filter" not in equipment_repr:
            hidden.append("filter_cloth (implied by pressing wet substrates)")
        if "distill" in desc and "condenser" not in equipment_repr:
            hidden.append("condenser_cooling_water (implied by distillation)")
        return hidden

    def _identify_failure_modes(self, path: Dict, energy_feasible: bool,
                                time_feasible: bool,
                                missing_critical: List[str]) -> List[str]:
        modes: List[str] = []
        if not energy_feasible:
            modes.append("energy_budget_exceeded")
        if not time_feasible:
            modes.append("time_window_insufficient")
        if missing_critical:
            modes.append(
                f"unsalvageable_missing_equipment: {missing_critical}"
            )
        status = path.get("status")
        if status and status != "open":
            modes.append(
                f"closed_by_resolver: {path.get('closure_reason', 'unknown')}"
            )
        return modes

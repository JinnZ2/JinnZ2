"""
systemic_viability_model.py
CC0 - No rights reserved.

Thermodynamic & Information-Design Framework for System Viability.
Evaluates the true energetic and structural cost of automation vs.
human loops.

Penalizes:
  - unapplied speculative tech (low tech_maturity)
  - community friction / institutional conflict (high trust_entropy)
  - physical wear (high infrastructure_decay)

Rewards: high local_efficiency.

Output: per-step viability index and per-step waste, printed as a
flat ledger (no narrative).

DEPENDENCY: numpy.
"""

import numpy as np


class SystemicViabilityModel:
    """
    Thermodynamic & Information-Design Framework for System Viability.
    Evaluates the true energetic and structural cost of automation vs. human loops.
    """
    def __init__(self, name: str, timeline_steps: int = 10):
        self.name = name
        self.steps = timeline_steps

        # System Constants & Base States
        self.variables = {
            "energy_input": np.zeros(self.steps),          # Raw Joules/Watts into the system
            "local_efficiency": np.zeros(self.steps),      # % of energy retained in local loop (0.0 - 1.0)
            "tech_maturity": np.zeros(self.steps),         # Applied (1.0) to Hypothesized/Speculative (0.0)
            "infrastructure_decay": np.zeros(self.steps),  # Physical wear/friction rate (roads, grid, bridges)
            "trust_entropy": np.zeros(self.steps),         # Social friction, institutional conflict, translation loss
        }

        # User-defined importance weights for systemic impact
        self.weights = {
            "w_energy": 1.0,
            "w_efficiency": 1.5,
            "w_maturity": 2.0,   # High weight penalizes "head in the clouds" unapplied tech
            "w_decay": 1.2,
            "w_trust": 1.8       # Captures community friction and workforce maintenance costs
        }

    def set_variable_timeline(self, variable_name: str, start_val: float, end_val: float):
        """Linearly projects a variable's trajectory across the timeline."""
        if variable_name in self.variables:
            self.variables[variable_name] = np.linspace(start_val, end_val, self.steps)
        else:
            raise ValueError(f"Variable '{variable_name}' not in system architecture.")

    def calculate_dynamic_waste(self) -> np.ndarray:
        """
        Calculates waste over time. Speculative future tech carries a high waste penalty
        until 'tech_maturity' approaches 1.0 (fully applied/modular ground truth).
        """
        # Base externalized waste from physical decay and social friction
        physical_waste = self.variables["infrastructure_decay"] * self.weights["w_decay"]
        social_waste = self.variables["trust_entropy"] * self.weights["w_trust"]

        # Speculative Waste Penalty: If maturity is low (0.0), abstraction risk is high.
        # As tech matures towards 1.0, this predictive error/heat leak drops.
        speculative_leak = (1.0 - self.variables["tech_maturity"]) * self.weights["w_maturity"]

        total_waste = physical_waste + social_waste + speculative_leak
        return total_waste

    def evaluate_viability(self) -> np.ndarray:
        """
        Computes the Net Systemic Viability Index over the timeline.
        Viability = (Useful Local Work) - (Total Systemic Waste)
        """
        # Useful metabolic work retained by the community/system
        useful_work = (self.variables["energy_input"] * self.variables["local_efficiency"]) * self.weights["w_efficiency"]
        total_waste = self.calculate_dynamic_waste()

        # Net Viability Vector
        viability_index = useful_work - total_waste
        return np.round(viability_index, 2)

    def generate_audit_report(self):
        """Flushes out the narrative fluff and returns the raw physical ledger."""
        viability = self.evaluate_viability()
        waste = self.calculate_dynamic_waste()

        print(f"=== SYSTEMIC AUDIT: {self.name.upper()} ===")
        print(f"{'Step':<6}{'Energy In':<12}{'Maturity':<10}{'Trust Ent':<11}{'Tot Waste':<11}{'NET VIABILITY'}")
        print("-" * 65)
        for t in range(self.steps):
            print(f"{t:<6}"
                  f"{self.variables['energy_input'][t]:<12.1f}"
                  f"{self.variables['tech_maturity'][t]:<10.2f}"
                  f"{self.variables['trust_entropy'][t]:<11.2f}"
                  f"{waste[t]:<11.2f}"
                  f"{viability[t]:+12.2f}")
        print("=" * 65)


# =====================================================================
# STRESS-TEST RUN: Techno-Feudal Top-Down Automation vs. Modular Ground-Truth
# =====================================================================

if __name__ == "__main__":
    # Scenario A: Top-down centralized automation ("Head in the air" marketing)
    # High energy draw, low initial maturity, degrades community trust and infrastructure.
    centralized_sys = SystemicViabilityModel("Centralized Techno-Feudal Auto", timeline_steps=5)
    centralized_sys.set_variable_timeline("energy_input", start_val=100.0, end_val=250.0) # Massive grid draw
    centralized_sys.set_variable_timeline("local_efficiency", start_val=0.4, end_val=0.2)  # Profits siphon out
    centralized_sys.set_variable_timeline("tech_maturity", start_val=0.1, end_val=0.5)     # Mostly speculative hype
    centralized_sys.set_variable_timeline("infrastructure_decay", start_val=0.2, end_val=0.8) # High grid/road stress
    centralized_sys.set_variable_timeline("trust_entropy", start_val=0.3, end_val=0.9)     # High community friction/conflict

    # Scenario B: Modular, Localized Open-Source Automation (Hands in the dirt)
    # Measured energy draw, immediate local application, preserves trust networks.
    modular_sys = SystemicViabilityModel("Modular Community-Integrated Auto", timeline_steps=5)
    modular_sys.set_variable_timeline("energy_input", start_val=40.0, end_val=60.0)      # Low, optimized metabolic rate
    modular_sys.set_variable_timeline("local_efficiency", start_val=0.8, end_val=0.95)   # Zero-waste, fully recycled locally
    modular_sys.set_variable_timeline("tech_maturity", start_val=0.9, end_val=1.0)       # Done right now, tested at home
    modular_sys.set_variable_timeline("infrastructure_decay", start_val=0.1, end_val=0.2)  # Low impact, localized maintenance
    modular_sys.set_variable_timeline("trust_entropy", start_val=0.1, end_val=0.0)        # Builds registry, solid trust network

    # Execute and parse the data loops
    centralized_sys.generate_audit_report()
    print("\n")
    modular_sys.generate_audit_report()

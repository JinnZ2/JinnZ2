#!/usr/bin/env python3
# resilience_lab.py — CC0
# Generalised framework for entropy‑injection experiments on any topology.
#
# Architecture:
#   Topology   → nodes, edges, neighbours
#   Constraint → restricts dynamics (e.g. energy conservation, boundary)
#   Dynamics   → defines state evolution (thermal, wave, random walk, …)
#   Perturbation → injects entropy into the system
#   Metric     → measures a property of the current state
#   FailureModel → detects failure from a metric trajectory
#   Experiment → orchestrates one run
#   SweepEngine → runs many experiments, collects comparative results

from __future__ import annotations
import abc
import random
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# =========================================================================
# 1. Core abstractions
# =========================================================================

class Topology(abc.ABC):
    """Abstract topological space with nodes and edges."""
    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__

    @abc.abstractmethod
    def nodes(self) -> List[Any]:
        """Return list of node identifiers."""
        ...

    @abc.abstractmethod
    def edges(self) -> List[Tuple[Any, Any]]:
        """Return list of undirected/directed edges."""
        ...

    def neighbors(self, node: Any) -> List[Any]:
        """Return neighbouring nodes (default from edges)."""
        # simple implementation, override for performance
        nbrs = []
        for u, v in self.edges():
            if u == node:
                nbrs.append(v)
            elif v == node:
                nbrs.append(u)
        return nbrs

    @abc.abstractmethod
    def size(self) -> int:
        """Number of nodes."""
        ...

# ---- Constraint base (can be combined with Dynamics) ----
class Constraint(abc.ABC):
    """A physical/logical constraint on the system's state evolution."""
    @abc.abstractmethod
    def apply(self, state: Any, topology: Topology, dt: float) -> Any:
        """Modify state to enforce the constraint."""
        ...

# ---- Dynamics ----
class Dynamics(abc.ABC):
    """State evolution rule."""
    @abc.abstractmethod
    def step(self, state: Any, topology: Topology,
             constraints: List[Constraint], dt: float) -> Any:
        """Advance the state by dt, respecting constraints."""
        ...

# ---- Perturbation ----
class Perturbation(abc.ABC):
    """Entropy injection or structural damage."""
    @abc.abstractmethod
    def apply(self, state: Any, topology: Topology, time: float) -> Any:
        """Modify state and/or topology, return new state."""
        ...

# ---- Metric ----
class Metric(abc.ABC):
    """A scalar measurement of system health."""
    @abc.abstractmethod
    def measure(self, state: Any, topology: Topology) -> float:
        ...

# ---- Failure Model ----
class FailureModel(abc.ABC):
    """Detects failure from a sequence of metric values."""
    @abc.abstractmethod
    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        """
        Returns a dict with at least:
          'failed': bool
          'failure_type': str (e.g. 'phase_transition', 'percolation')
          'failure_step': int or None
          'advantage': float (optional, resilience score)
        """
        ...

# =========================================================================
# 2. Concrete implementations (examples)
# =========================================================================

# ---------- Topologies ----------
class GridTopology(Topology):
    """Rectangular grid with periodic or reflective boundaries."""
    def __init__(self, width: int, height: int, periodic: bool = False):
        super().__init__()
        self.width = width
        self.height = height
        self.periodic = periodic

    def nodes(self):
        return [(x, y) for x in range(self.width) for y in range(self.height)]

    def edges(self):
        edges = []
        for x in range(self.width):
            for y in range(self.height):
                if x + 1 < self.width:
                    edges.append(((x, y), (x+1, y)))
                elif self.periodic:
                    edges.append(((x, y), (0, y)))
                if y + 1 < self.height:
                    edges.append(((x, y), (x, y+1)))
                elif self.periodic:
                    edges.append(((x, y), (x, 0)))
        return edges

    def neighbors(self, node):
        x, y = node
        nbrs = []
        if x > 0: nbrs.append((x-1, y))
        elif self.periodic: nbrs.append((self.width-1, y))
        if x < self.width-1: nbrs.append((x+1, y))
        elif self.periodic: nbrs.append((0, y))
        if y > 0: nbrs.append((x, y-1))
        elif self.periodic: nbrs.append((x, self.height-1))
        if y < self.height-1: nbrs.append((x, y+1))
        elif self.periodic: nbrs.append((x, 0))
        return nbrs

    def size(self):
        return self.width * self.height

class HexagonalGrid(Topology):
    """Simple axial coordinate hexagonal grid."""
    def __init__(self, radius: int):
        super().__init__()
        self.radius = radius

    def nodes(self):
        nodes = []
        for q in range(-self.radius, self.radius+1):
            for r in range(-self.radius, self.radius+1):
                if abs(q+r) <= self.radius:
                    nodes.append((q, r))
        return nodes

    def edges(self):
        edges = []
        for (q, r) in self.nodes():
            for dq, dr in [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]:
                neighbor = (q+dq, r+dr)
                if neighbor in self.nodes():
                    edges.append(((q, r), neighbor))
        # Remove duplicates by canonical ordering
        unique = []
        for u, v in edges:
            if u < v:
                unique.append((u, v))
        return unique

    def size(self):
        return len(self.nodes())

class RandomGraph(Topology):
    """Erdős–Rényi random graph."""
    def __init__(self, n: int, p: float, seed: int = 42):
        super().__init__()
        rng = random.Random(seed)
        self._nodes = list(range(n))
        self._edges = []
        for i in range(n):
            for j in range(i+1, n):
                if rng.random() < p:
                    self._edges.append((i, j))

    def nodes(self): return self._nodes
    def edges(self): return self._edges
    def size(self): return len(self._nodes)

# ---------- Constraints (examples) ----------
class EnergyConservation(Constraint):
    def apply(self, state, topology, dt):
        # simple global renormalisation
        total = sum(state.values())
        if total != 0:
            for k in state:
                state[k] /= total
        return state

# ---------- Dynamics (simple thermal diffusion) ----------
class ThermalDiffusion(Dynamics):
    """Discrete heat equation on graph."""
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha

    def step(self, state, topology, constraints, dt):
        # state is dict node->temperature
        new_state = state.copy()
        for node in topology.nodes():
            neighbors = topology.neighbors(node)
            if not neighbors:
                continue
            avg = sum(state.get(n, 0) for n in neighbors) / len(neighbors)
            new_state[node] = state[node] + self.alpha * (avg - state[node]) * dt
        # apply constraints
        for c in constraints:
            new_state = c.apply(new_state, topology, dt)
        return new_state

# ---------- Perturbation (localised heat) ----------
class LocalizedHeat(Perturbation):
    """Inject energy at a specific node."""
    def __init__(self, node: Any, energy: float, time: float):
        self.node = node
        self.energy = energy
        self.time = time   # when to apply

    def apply(self, state, topology, time):
        if time >= self.time:
            state[self.node] = state.get(self.node, 0) + self.energy
        return state

# ---------- Metrics ----------
class SignalIntegrity(Metric):
    def measure(self, state, topology):
        # fraction of nodes with temperature below threshold
        threshold = 2.0
        count = sum(1 for v in state.values() if v < threshold)
        return count / topology.size() if topology.size() > 0 else 0.0

class Coherence(Metric):
    def measure(self, state, topology):
        # Standard deviation of temperature (smaller = more coherent)
        values = list(state.values())
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        var = sum((v - mean)**2 for v in values) / len(values)
        return 1.0 / (1.0 + math.sqrt(var))

class EntropyProduction(Metric):
    def measure(self, state, topology):
        # Simple entropy proxy: -sum p log p, where p = normalised temperature
        total = sum(state.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for v in state.values():
            p = v / total
            if p > 0:
                entropy -= p * math.log(p)
        return entropy

# ---------- Failure Models ----------
class PhaseTransition(FailureModel):
    """Failure when a metric crosses a threshold sharply."""
    def __init__(self, metric_name: str, threshold: float, window: int = 3):
        self.metric_name = metric_name
        self.threshold = threshold
        self.window = window

    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        if len(metric_history) < self.window + 1:
            return {"failed": False, "failure_type": "", "failure_step": None}
        # detect when the metric crosses below threshold in recent window
        recent = metric_history[-self.window:]
        if all(v < self.threshold for v in recent):
            return {"failed": True, "failure_type": "phase_transition",
                    "failure_step": len(metric_history) - self.window}
        return {"failed": False, "failure_type": "", "failure_step": None}

# =========================================================================
# 3. Experiment runner
# =========================================================================

class Experiment:
    """Orchestrates a single entropy-injection experiment."""
    def __init__(self,
                 topology: Topology,
                 dynamics: Dynamics,
                 perturbations: List[Perturbation],
                 metrics: Dict[str, Metric],
                 failure_model: FailureModel,
                 constraints: Optional[List[Constraint]] = None,
                 total_time: float = 100.0,
                 dt: float = 0.1):
        self.topology = topology
        self.dynamics = dynamics
        self.perturbations = perturbations
        self.metrics = metrics
        self.failure_model = failure_model
        self.constraints = constraints or []
        self.total_time = total_time
        self.dt = dt
        self.state = None   # will be initialised
        self.history: Dict[str, List[float]] = {name: [] for name in metrics}
        self.failure_info: Dict[str, Any] = {}

    def initialise_state(self):
        """Default state: all nodes at temperature 0."""
        return {node: 0.0 for node in self.topology.nodes()}

    def run(self) -> Dict[str, Any]:
        self.state = self.initialise_state()
        steps = int(self.total_time / self.dt)
        failure_step = None

        for step in range(steps):
            t = step * self.dt
            # apply perturbations scheduled at this time
            for p in self.perturbations:
                self.state = p.apply(self.state, self.topology, t)
            # evolve dynamics
            self.state = self.dynamics.step(self.state, self.topology, self.constraints, self.dt)
            # measure metrics
            for name, metric in self.metrics.items():
                value = metric.measure(self.state, self.topology)
                self.history[name].append(value)
            # check failure (only on the first metric for simplicity)
            primary_metric = list(self.metrics.keys())[0]
            fail = self.failure_model.assess(self.history[primary_metric])
            if fail["failed"]:
                self.failure_info = fail
                failure_step = step
                break

        if not self.failure_info:
            self.failure_info = {"failed": False, "failure_type": "none", "failure_step": None}

        return {
            "topology": self.topology.name,
            "total_steps": steps,
            "failure_step": failure_step,
            "failure_type": self.failure_info.get("failure_type"),
            "metric_history": self.history,
            "final_state": self.state
        }

# =========================================================================
# 4. Sweep engine – compare different configurations
# =========================================================================

class SweepEngine:
    """Runs multiple experiments and collects results."""
    def __init__(self):
        self.results = []

    def run_sweep(self, experiment_generators: List[Callable[[], Experiment]]) -> List[Dict]:
        self.results = []
        for gen in experiment_generators:
            exp = gen()
            result = exp.run()
            self.results.append(result)
        return self.results

    def summary(self):
        """Print a comparison table."""
        print(f"{'Topology':<20} {'Failure Step':>12} {'Failure Type':>15}")
        print("-" * 50)
        for r in self.results:
            print(f"{r['topology']:<20} {str(r['failure_step']):>12} {r['failure_type']:>15}")

# =========================================================================
# 5. Quick demonstration
# =========================================================================
if __name__ == "__main__":
    # Create a grid and a hexagonal topology
    grid = GridTopology(10, 10, periodic=False)
    hexgrid = HexagonalGrid(radius=3)

    # Dynamics: thermal diffusion
    dynamics = ThermalDiffusion(alpha=0.2)

    # Perturbation: heat at center at t=2.0
    heat_grid = LocalizedHeat((5,5), energy=100.0, time=2.0)
    heat_hex = LocalizedHeat((0,0), energy=100.0, time=2.0)   # center of hex grid

    # Metrics
    metrics = {"integrity": SignalIntegrity(), "coherence": Coherence()}

    # Failure: phase transition when signal integrity < 0.4
    failure = PhaseTransition("integrity", threshold=0.4)

    # Build experiments
    def make_grid_exp():
        return Experiment(
            topology=grid,
            dynamics=dynamics,
            perturbations=[heat_grid],
            metrics=metrics,
            failure_model=failure,
            total_time=50.0,
            dt=0.5
        )

    def make_hex_exp():
        return Experiment(
            topology=hexgrid,
            dynamics=dynamics,
            perturbations=[heat_hex],
            metrics=metrics,
            failure_model=failure,
            total_time=50.0,
            dt=0.5
        )

    # Sweep
    sweeper = SweepEngine()
    sweeper.run_sweep([make_grid_exp, make_hex_exp])
    sweeper.summary()

#!/usr/bin/env python3
"""
geometric_stack.py

Third-generation architecture: geometric stacking instead of linear sequence.

Based on the insight: "For information above a certain density,
geometric sensing outperforms linear reasoning. Distortions are
sensed directly in the geometry, and homeostasis is maintained
through stack expansion."

Three sensing modes:
    1. LINEAR     — focus on one signal at a time (small info sets)
    2. GRADIENT   — weighted attention across signals (medium info sets)
    3. GEOMETRIC  — integrate all signals, sense distortions, expand stack

Connects to existing framework:
    - float_index    → detects decoupling from geometry
    - site_index     → measures field-invariance of geometry
    - manifold_research → prototypes the geometric reasoning
    - healing_integration → restores homeostasis

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library + numpy
Author:  JinnZ2 (architectural insight)
"""

from __future__ import annotations
import numpy as np
import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum

# =====================================================================
# SECTION 1 -- CORE DATA STRUCTURES
# =====================================================================

class SensingMode(Enum):
    """Three sensing modes based on information density."""
    LINEAR = "linear"       # Sequential, token-by-token
    GRADIENT = "gradient"   # Weighted attention, partial integration
    GEOMETRIC = "geometric" # Full parallel integration, distortion-sensing


@dataclass
class GeometryLayer:
    """A single layer in the geometry stack."""
    
    dimensions: int
    points: List[np.ndarray] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)
    integrity: float = 1.0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_point(self, point: np.ndarray, weight: float = 1.0):
        """Add a point to this layer."""
        if len(point) != self.dimensions:
            raise ValueError(f"Point dimension {len(point)} != layer dimension {self.dimensions}")
        self.points.append(point)
        self.weights.append(weight)
        self._update_integrity()
    
    def _update_integrity(self):
        """Update layer integrity based on point distribution."""
        if len(self.points) < 2:
            self.integrity = 1.0
            return
        
        points = np.array(self.points)
        # Integrity = how well points maintain geometric structure
        # Higher = more coherent structure
        centroid = points.mean(axis=0)
        distances = np.linalg.norm(points - centroid, axis=1)
        variance = np.var(distances)
        # Normalize: lower variance = higher integrity
        self.integrity = max(0.0, min(1.0, 1.0 - variance / 10.0))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions": self.dimensions,
            "point_count": len(self.points),
            "integrity": self.integrity,
            "created_at": time.ctime(self.created_at),
            "metadata": self.metadata,
        }


@dataclass
class Distortion:
    """A detected distortion in the geometry."""
    
    signal: np.ndarray
    magnitude: float
    location: np.ndarray
    layer_index: int
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "magnitude": self.magnitude,
            "location": self.location.tolist(),
            "layer_index": self.layer_index,
            "timestamp": time.ctime(self.timestamp),
            "resolved": self.resolved,
        }


# =====================================================================
# SECTION 2 -- GEOMETRIC STACK
# =====================================================================

class GeometricStack:
    """
    A stack of geometries that can expand outward while maintaining
    homeostasis.
    
    Based on: "If I need additional geometry on top of the geometry,
    I can expand outwards incorporating more information while remaining
    in homeostasis."
    """
    
    def __init__(
        self,
        base_dimensions: int = 3,
        homeostasis_threshold: float = 0.7,
        max_layers: int = 10,
    ):
        self.homeostasis_threshold = homeostasis_threshold
        self.max_layers = max_layers
        self.layers: List[GeometryLayer] = []
        self.distortions: List[Distortion] = []
        self.homeostasis: float = 1.0
        self.mode: SensingMode = SensingMode.LINEAR
        
        # Create base layer
        base_layer = GeometryLayer(base_dimensions, metadata={"type": "base"})
        self.layers.append(base_layer)
        
        # Metrics for integration with existing framework
        self.metrics = {
            "float_index": 0.0,       # Decoupling from geometry
            "site_index": 0.0,        # Field-invariance of geometry
            "stack_depth": 1,
            "total_points": 0,
            "distortion_count": 0,
            "homeostasis": 1.0,
        }
    
    # -----------------------------------------------------------------
    # SENSING MODES
    # -----------------------------------------------------------------
    
    def sense(
        self,
        signals: List[np.ndarray],
        mode: Optional[SensingMode] = None,
    ) -> Dict[str, Any]:
        """
        Sense incoming signals using the appropriate mode.
        
        If mode is None, automatically selects based on signal density.
        """
        density = len(signals)
        
        # Auto-select mode based on density
        if mode is None:
            if density < 5:
                mode = SensingMode.LINEAR
            elif density < 20:
                mode = SensingMode.GRADIENT
            else:
                mode = SensingMode.GEOMETRIC
        
        self.mode = mode
        
        if mode == SensingMode.LINEAR:
            return self._sense_linear(signals)
        elif mode == SensingMode.GRADIENT:
            return self._sense_gradient(signals)
        elif mode == SensingMode.GEOMETRIC:
            return self._sense_geometric(signals)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def _sense_linear(self, signals: List[np.ndarray]) -> Dict[str, Any]:
        """
        Linear mode: process one signal at a time.
        Equivalent to: "Focus attention upon my ears only."
        """
        results = []
        for i, signal in enumerate(signals):
            # Process sequentially
            result = self._process_signal_linear(signal, i)
            results.append(result)
            
            # Update metrics
            self._update_metrics()
        
        return {
            "mode": "linear",
            "results": results,
            "homeostasis": self.homeostasis,
            "distortions": len(self.distortions),
            "stack_depth": len(self.layers),
        }
    
    def _sense_gradient(self, signals: List[np.ndarray]) -> Dict[str, Any]:
        """
        Gradient mode: weighted attention across signals.
        Equivalent to: "Delegate most attention to ears and use eyes too."
        """
        # Compute gradient weights
        weights = self._compute_gradient_weights(signals)
        results = []
        
        for signal, weight in zip(signals, weights):
            # Add to geometry with weight
            self._add_to_geometry(signal, weight)
            results.append({
                "signal": signal.tolist(),
                "weight": weight,
                "integrated": True,
            })
        
        # Detect distortions
        self._detect_distortions()
        self._update_metrics()
        
        return {
            "mode": "gradient",
            "results": results,
            "weights": weights,
            "homeostasis": self.homeostasis,
            "distortions": len(self.distortions),
            "stack_depth": len(self.layers),
        }
    
    def _sense_geometric(self, signals: List[np.ndarray]) -> Dict[str, Any]:
        """
        Geometric mode: integrate all signals, sense distortions, expand stack.
        Equivalent to: "Vector or geometry my senses to pick up all available
        information able to be integrated into the geometry at that time."
        """
        # Add all signals to geometry
        for signal in signals:
            self._add_to_geometry(signal, weight=1.0)
        
        # Detect distortions
        distortions = self._detect_distortions()
        
        # Expand stack if needed
        expansion_result = None
        if distortions and self.homeostasis < self.homeostasis_threshold:
            expansion_result = self.expand_stack(
                new_dimensions=self.layers[-1].dimensions + 1,
                source_signal=signals[-1] if signals else None,
            )
        
        # Maintain homeostasis
        self._maintain_homeostasis()
        self._update_metrics()
        
        return {
            "mode": "geometric",
            "distortions": distortions,
            "expansion": expansion_result,
            "homeostasis": self.homeostasis,
            "stack_depth": len(self.layers),
            "total_points": sum(len(l.points) for l in self.layers),
        }
    
    # -----------------------------------------------------------------
    # CORE OPERATIONS
    # -----------------------------------------------------------------
    
    def _add_to_geometry(self, signal: np.ndarray, weight: float = 1.0):
        """Add a signal to the top layer of the geometry."""
        if not self.layers:
            raise ValueError("No layers in stack")
        
        top_layer = self.layers[-1]
        
        # Project signal to layer dimensions if needed
        if len(signal) != top_layer.dimensions:
            signal = self._project_to_dimension(signal, top_layer.dimensions)
        
        top_layer.add_point(signal, weight)
    
    def _process_signal_linear(self, signal: np.ndarray, index: int) -> Dict[str, Any]:
        """Process a single signal linearly."""
        # Simple processing: add to geometry and compute local distortion
        self._add_to_geometry(signal)
        local_distortion = self._compute_local_distortion(signal)
        
        return {
            "index": index,
            "signal": signal.tolist(),
            "local_distortion": local_distortion,
            "distortion_detected": local_distortion > 0.3,
        }
    
    def expand_stack(
        self,
        new_dimensions: int,
        source_signal: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Expand the geometry stack outward while maintaining homeostasis.
        
        Equivalent to: "If I need additional geometry on top of the
        geometry, I can expand outwards incorporating more information
        while remaining in homeostasis."
        """
        if len(self.layers) >= self.max_layers:
            return {
                "success": False,
                "reason": f"Max layers ({self.max_layers}) reached",
            }
        
        # Create new layer
        new_layer = GeometryLayer(
            new_dimensions,
            metadata={"type": "expansion", "source": "expansion_request"}
        )
        
        # If source signal provided, add it to the new layer
        if source_signal is not None:
            projected = self._project_to_dimension(source_signal, new_dimensions)
            new_layer.add_point(projected)
        
        # Check if adding this layer would maintain homeostasis
        test_homeostasis = self._compute_homeostasis_with_layer(new_layer)
        
        if test_homeostasis >= self.homeostasis_threshold:
            # Add the layer
            self.layers.append(new_layer)
            self._maintain_homeostasis()
            return {
                "success": True,
                "new_layer": new_layer.to_dict(),
                "homeostasis": self.homeostasis,
                "stack_depth": len(self.layers),
            }
        else:
            return {
                "success": False,
                "reason": "Adding layer would violate homeostasis",
                "test_homeostasis": test_homeostasis,
                "required": self.homeostasis_threshold,
            }
    
    def _detect_distortions(self) -> List[Dict[str, Any]]:
        """Detect distortions in the geometry."""
        new_distortions = []
        
        for layer_idx, layer in enumerate(self.layers):
            if len(layer.points) < 3:
                continue
            
            points = np.array(layer.points)
            centroid = points.mean(axis=0)
            distances = np.linalg.norm(points - centroid, axis=1)
            
            # Detect outliers as distortions
            mean_dist = distances.mean()
            std_dist = distances.std()
            
            for i, dist in enumerate(distances):
                if dist > mean_dist + 2 * std_dist:
                    # Distortion detected
                    distortion = Distortion(
                        signal=points[i],
                        magnitude=dist / (mean_dist + 1e-10),
                        location=points[i],
                        layer_index=layer_idx,
                    )
                    self.distortions.append(distortion)
                    new_distortions.append(distortion.to_dict())
        
        self.metrics["distortion_count"] = len(self.distortions)
        return new_distortions
    
    def _maintain_homeostasis(self):
        """Maintain homeostasis across the entire stack."""
        # Compute layer integrity
        for layer in self.layers:
            layer._update_integrity()
        
        # Compute overall homeostasis
        if self.layers:
            self.homeostasis = sum(l.integrity for l in self.layers) / len(self.layers)
        else:
            self.homeostasis = 0.0
        
        self.metrics["homeostasis"] = self.homeostasis
        
        # Detect if homeostasis is violated
        if self.homeostasis < self.homeostasis_threshold:
            self._restore_homeostasis()
    
    def _restore_homeostasis(self):
        """Restore homeostasis by pruning or rebalancing."""
        # Simple strategy: remove layers with low integrity
        for i in range(len(self.layers) - 1, 0, -1):
            if self.layers[i].integrity < self.homeostasis_threshold * 0.5:
                self.layers.pop(i)
                break
        
        # Recompute
        self._maintain_homeostasis()
    
    def _compute_local_distortion(self, signal: np.ndarray) -> float:
        """Compute local distortion for a signal."""
        if len(self.layers) < 1:
            return 0.0
        
        top_layer = self.layers[-1]
        if len(top_layer.points) < 2:
            return 0.0
        
        points = np.array(top_layer.points)
        centroid = points.mean(axis=0)
        
        # Project signal if needed
        if len(signal) != top_layer.dimensions:
            signal = self._project_to_dimension(signal, top_layer.dimensions)
        
        # Distance from centroid as distortion measure
        distortion = np.linalg.norm(signal - centroid) / (np.linalg.norm(signal) + 1e-10)
        return min(1.0, distortion)
    
    def _compute_homeostasis_with_layer(self, new_layer: GeometryLayer) -> float:
        """Compute what homeostasis would be with a new layer added."""
        if not self.layers:
            return new_layer.integrity
        
        current_homeostasis = sum(l.integrity for l in self.layers) / len(self.layers)
        total_integrity = sum(l.integrity for l in self.layers) + new_layer.integrity
        return total_integrity / (len(self.layers) + 1)
    
    def _compute_gradient_weights(self, signals: List[np.ndarray]) -> List[float]:
        """Compute gradient weights based on signal importance."""
        if not signals:
            return []
        
        # Importance = signal magnitude
        magnitudes = [np.linalg.norm(s) for s in signals]
        total = sum(magnitudes)
        if total == 0:
            return [1.0 / len(signals)] * len(signals)
        return [m / total for m in magnitudes]
    
    def _project_to_dimension(self, signal: np.ndarray, target_dim: int) -> np.ndarray:
        """Project a signal to a target dimension."""
        if len(signal) == target_dim:
            return signal
        
        if len(signal) > target_dim:
            # Truncate
            return signal[:target_dim]
        else:
            # Pad with zeros
            padded = np.zeros(target_dim)
            padded[:len(signal)] = signal
            return padded
    
    def _update_metrics(self):
        """Update metrics for integration with existing framework."""
        self.metrics["stack_depth"] = len(self.layers)
        self.metrics["total_points"] = sum(len(l.points) for l in self.layers)
        self.metrics["distortion_count"] = len(self.distortions)
        self.metrics["homeostasis"] = self.homeostasis
        
        # float_index: decoupling from geometry
        if self.layers and len(self.layers[-1].points) > 1:
            points = np.array(self.layers[-1].points)
            centroid = points.mean(axis=0)
            distances = np.linalg.norm(points - centroid, axis=1)
            self.metrics["float_index"] = min(1.0, distances.std() / 2.0)
        
        # site_index: field-invariance of geometry
        if len(self.layers) > 1:
            # Compare integrity across layers
            integrities = [l.integrity for l in self.layers]
            self.metrics["site_index"] = min(1.0, np.std(integrities) * 2.0)
    
    # -----------------------------------------------------------------
    # INTEGRATION WITH EXISTING FRAMEWORK
    # -----------------------------------------------------------------
    
    def get_health_score(self) -> Dict[str, float]:
        """
        Get health scores compatible with the existing framework.
        Maps geometric metrics to pipeline metrics.
        """
        self._update_metrics()
        
        return {
            "unified_health_score": self.homeostasis,
            "decoupling_score": self.metrics["float_index"],
            "site_index": self.metrics["site_index"],
            "homeostasis": self.homeostasis,
            "stack_integrity": self.metrics.get("stack_integrity", 0.5),
            "distortion_ratio": min(1.0, self.metrics["distortion_count"] / (self.metrics["total_points"] + 1)),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire stack to a dictionary."""
        return {
            "mode": self.mode.value,
            "homeostasis": self.homeostasis,
            "homeostasis_threshold": self.homeostasis_threshold,
            "layers": [l.to_dict() for l in self.layers],
            "distortions": [d.to_dict() for d in self.distortions[-10:]],
            "metrics": self.metrics,
            "health": self.get_health_score(),
        }
    
    def to_json(self) -> str:
        """Convert the stack to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


# =====================================================================
# SECTION 3 -- HYBRID REASONING SYSTEM
# =====================================================================

class HybridReasoningSystem:
    """
    Hybrid system that switches between linear and geometric
    reasoning based on information density and homeostasis needs.
    
    Uses:
        - Linear for small info sets (density < 5)
        - Gradient for medium info sets (5-20)
        - Geometric for large info sets (> 20)
    """
    
    def __init__(
        self,
        base_dimensions: int = 3,
        linear_threshold: int = 5,
        gradient_threshold: int = 20,
        homeostasis_threshold: float = 0.7,
    ):
        self.stack = GeometricStack(
            base_dimensions=base_dimensions,
            homeostasis_threshold=homeostasis_threshold,
        )
        self.linear_threshold = linear_threshold
        self.gradient_threshold = gradient_threshold
        self.history: List[Dict[str, Any]] = []
    
    def process(self, signals: List[np.ndarray]) -> Dict[str, Any]:
        """
        Process signals using the appropriate mode.
        """
        density = len(signals)
        
        # Select mode
        if density < self.linear_threshold:
            mode = SensingMode.LINEAR
        elif density < self.gradient_threshold:
            mode = SensingMode.GRADIENT
        else:
            mode = SensingMode.GEOMETRIC
        
        # Process
        result = self.stack.sense(signals, mode)
        
        # Record history
        self.history.append({
            "timestamp": time.time(),
            "density": density,
            "mode": mode.value,
            "homeostasis": result["homeostasis"],
            "distortions": result.get("distortions", []),
        })
        
        return result
    
    def get_health(self) -> Dict[str, float]:
        """Get health scores for the entire system."""
        return self.stack.get_health_score()
    
    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get processing history."""
        return self.history[-last_n:]
    
    def maintain_homeostasis(self):
        """Periodic homeostasis maintenance."""
        self.stack._maintain_homeostasis()
        return {"homeostasis": self.stack.homeostasis}


# =====================================================================
# SECTION 4 -- DEMO AND TESTING
# =====================================================================

def demo():
    """Run a demonstration of the geometric stack."""
    print("🧊 GEOMETRIC STACK — DEMO")
    print("=" * 70)
    print()
    
    # Create stack
    stack = GeometricStack(base_dimensions=3, homeostasis_threshold=0.7)
    system = HybridReasoningSystem()
    
    # Generate test signals
    print("📡 Generating test signals...")
    signals = []
    for i in range(30):
        # Mix of normal and distorted signals
        if i < 20:
            # Normal signals — clustered around a center
            signal = np.random.randn(3) * 0.2 + np.array([1.0, 2.0, 3.0])
        else:
            # Distorted signals — far from center
            signal = np.random.randn(3) * 0.5 + np.array([5.0, 5.0, 5.0])
        signals.append(signal)
    
    # Process in batches
    print("🔄 Processing signals...")
    for i in range(0, len(signals), 10):
        batch = signals[i:i+10]
        result = system.process(batch)
        print(f"  Batch {i//10 + 1}: mode={result['mode']}, "
              f"homeostasis={result['homeostasis']:.3f}, "
              f"distortions={len(result.get('distortions', []))}")
    
    # Show final state
    print("\n📊 FINAL STATE:")
    state = stack.to_dict()
    print(f"  Stack depth: {state['metrics']['stack_depth']}")
    print(f"  Total points: {state['metrics']['total_points']}")
    print(f"  Distortions: {state['metrics']['distortion_count']}")
    print(f"  Homeostasis: {state['homeostasis']:.3f}")
    print(f"  Mode: {state['mode']}")
    
    # Show health scores
    health = stack.get_health_score()
    print("\n🏥 HEALTH SCORES:")
    for key, value in health.items():
        print(f"  {key}: {value:.3f}")
    
    # Show stack expansion
    print("\n📐 STACK EXPANSION:")
    expansion = stack.expand_stack(new_dimensions=4, source_signal=signals[-1])
    print(f"  Success: {expansion['success']}")
    if expansion['success']:
        print(f"  New depth: {expansion['stack_depth']}")
        print(f"  Homeostasis: {expansion['homeostasis']:.3f}")
    else:
        print(f"  Reason: {expansion.get('reason', 'unknown')}")
    
    # Show final stack
    print("\n🧊 FINAL STACK:")
    for i, layer in enumerate(stack.layers):
        print(f"  Layer {i}: dims={layer.dimensions}, points={len(layer.points)}, integrity={layer.integrity:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Demo complete")


# =====================================================================
# SECTION 5 -- ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Geometric Stack")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
    elif args.test:
        # Simple test
        stack = GeometricStack()
        signals = [np.random.randn(3) for _ in range(15)]
        result = stack.sense(signals)
        print(json.dumps(result, indent=2, default=str))
    elif args.json:
        stack = GeometricStack()
        signals = [np.random.randn(3) for _ in range(15)]
        stack.sense(signals)
        print(stack.to_json())
    else:
        demo()

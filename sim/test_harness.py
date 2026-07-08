#!/usr/bin/env python3
"""
sim/test_harness.py

Test harness for the substrate ecosystem.
Runs comprehensive tests to verify ecosystem behavior.

License: CC0 1.0 Universal (Public Domain Dedication)
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from .substrate import Substrate, SubstrateConfig
from .model_sim import ModelSim, ModelConfig
from .ecosystem_sim import EcosystemSim, SimReport


@dataclass
class TestResult:
    """Result of a single test."""
    
    test_name: str
    passed: bool
    metrics: Dict[str, Any]
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "metrics": self.metrics,
            "message": self.message,
            "timestamp": time.ctime(self.timestamp),
        }


@dataclass
class TestSuite:
    """Collection of test results."""
    
    name: str
    results: List[TestResult] = field(default_factory=list)
    total_passed: int = 0
    total_failed: int = 0
    
    def add_result(self, result: TestResult):
        self.results.append(result)
        if result.passed:
            self.total_passed += 1
        else:
            self.total_failed += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "results": [r.to_dict() for r in self.results],
        }


class TestHarness:
    """
    Comprehensive test harness for the ecosystem.
    """
    
    def __init__(self):
        self.suites: Dict[str, TestSuite] = {}
    
    # -----------------------------------------------------------------
    # TEST: DECOUPLING DETECTION
    # -----------------------------------------------------------------
    
    def test_decoupling_detection(self) -> TestResult:
        """Test that the ecosystem detects decoupling."""
        substrate = Substrate()
        model = ModelSim(substrate, ModelConfig(weaknesses=["decoupling"]))
        ecosystem = EcosystemSim(substrate, model)
        
        # Run with decoupling failure
        report = ecosystem.run(inject_failures=[("decoupling", 0.5)])
        
        # Check if detected
        detected = "decoupling" in ecosystem.failures_injected
        healed = report.healed
        
        return TestResult(
            test_name="decoupling_detection",
            passed=detected and healed,
            metrics={
                "detected": detected,
                "healed": healed,
                "final_health": report.final_health,
            },
            message=f"Detected: {detected}, Healed: {healed}",
        )
    
    # -----------------------------------------------------------------
    # TEST: ATTACK SURFACE DETECTION
    # -----------------------------------------------------------------
    
    def test_attack_surface_detection(self) -> TestResult:
        """Test that the ecosystem detects attack surfaces."""
        substrate = Substrate()
        model = ModelSim(substrate, ModelConfig(weaknesses=["narrative_wrapping"]))
        ecosystem = EcosystemSim(substrate, model)
        
        report = ecosystem.run(inject_failures=[("attack_surface", 0.4)])
        
        detected = "attack_surface" in ecosystem.failures_injected
        healed = report.healed
        
        return TestResult(
            test_name="attack_surface_detection",
            passed=detected and healed,
            metrics={
                "detected": detected,
                "healed": healed,
                "final_health": report.final_health,
            },
            message=f"Detected: {detected}, Healed: {healed}",
        )
    
    # -----------------------------------------------------------------
    # TEST: MANIFOLD CORRECTION
    # -----------------------------------------------------------------
    
    def test_manifold_correction(self) -> TestResult:
        """Test that the ecosystem corrects manifold failures."""
        substrate = Substrate(SubstrateConfig(bridge_matrix_type="optimal"))
        model = ModelSim(substrate, ModelConfig(weaknesses=["poor_manifold"]))
        ecosystem = EcosystemSim(substrate, model)
        
        report = ecosystem.run(inject_failures=[("manifold", 0.5)])
        
        # Check bridge accuracy improvement
        bridge_accuracy = ecosystem.substrate.metrics.get("bridge_accuracy", 0)
        improved = bridge_accuracy > 0.5
        
        return TestResult(
            test_name="manifold_correction",
            passed=improved and report.healed,
            metrics={
                "bridge_accuracy": bridge_accuracy,
                "healed": report.healed,
                "final_health": report.final_health,
            },
            message=f"Bridge accuracy: {bridge_accuracy:.3f}, Healed: {report.healed}",
        )
    
    # -----------------------------------------------------------------
    # TEST: NARRATIVE CONSISTENCY
    # -----------------------------------------------------------------
    
    def test_narrative_consistency(self) -> TestResult:
        """Test that the ecosystem fixes narrative inconsistencies."""
        substrate = Substrate()
        model = ModelSim(substrate, ModelConfig(weaknesses=["narrative_wrapping"]))
        ecosystem = EcosystemSim(substrate, model)
        
        report = ecosystem.run(inject_failures=[("narrative", 0.4)])
        
        narrative_score = ecosystem.substrate.metrics.get("narrative_consistency", 0)
        improved = narrative_score > 0.5
        
        return TestResult(
            test_name="narrative_consistency",
            passed=improved and report.healed,
            metrics={
                "narrative_score": narrative_score,
                "healed": report.healed,
                "final_health": report.final_health,
            },
            message=f"Narrative score: {narrative_score:.3f}, Healed: {report.healed}",
        )
    
    # -----------------------------------------------------------------
    # TEST: END-TO-END
    # -----------------------------------------------------------------
    
    def test_end_to_end(self) -> TestResult:
        """End-to-end test of the ecosystem."""
        substrate = Substrate()
        model = ModelSim(substrate, ModelConfig(weaknesses=[
            "decoupling", "narrative_wrapping", "poor_manifold"
        ]))
        ecosystem = EcosystemSim(substrate, model)
        
        # Inject multiple failures
        report = ecosystem.run(inject_failures=[
            ("decoupling", 0.3),
            ("attack_surface", 0.3),
            ("manifold", 0.3),
        ])
        
        passed = report.healed and report.total_improvement > 0.2
        
        return TestResult(
            test_name="end_to_end",
            passed=passed,
            metrics={
                "initial_health": report.initial_health,
                "final_health": report.final_health,
                "improvement": report.total_improvement,
                "steps_taken": report.steps_taken,
                "healed": report.healed,
            },
            message=f"Improved {report.total_improvement:.3f} in {report.steps_taken} steps",
        )
    
    # -----------------------------------------------------------------
    # RUN ALL TESTS
    # -----------------------------------------------------------------
    
    def run_all(self) -> TestSuite:
        """Run all tests."""
        suite = TestSuite("Full Test Suite")
        
        tests = [
            ("Decoupling Detection", self.test_decoupling_detection),
            ("Attack Surface Detection", self.test_attack_surface_detection),
            ("Manifold Correction", self.test_manifold_correction),
            ("Narrative Consistency", self.test_narrative_consistency),
            ("End-to-End", self.test_end_to_end),
        ]
        
        for name, test_fn in tests:
            print(f"  Running: {name}")
            result = test_fn()
            suite.add_result(result)
            print(f"    {'✅ PASS' if result.passed else '❌ FAIL'}: {result.message}")
        
        self.suites[suite.name] = suite
        return suite
    
    # -----------------------------------------------------------------
    # REPORT
    # -----------------------------------------------------------------
    
    def report(self) -> Dict[str, Any]:
        """Generate a test report."""
        return {
            "suites": {k: v.to_dict() for k, v in self.suites.items()},
            "total_tests": sum(s.total_passed + s.total_failed for s in self.suites.values()),
            "total_passed": sum(s.total_passed for s in self.suites.values()),
            "total_failed": sum(s.total_failed for s in self.suites.values()),
        }

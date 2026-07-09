#!/usr/bin/env python3
"""
sim/__main__.py — entry point for `python3 -m sim`

Usage:
    python3 -m sim              # interactive demo
    python3 -m sim --ci         # CI mode: run test harness, exit 0/1
    python3 -m sim --help

License: CC0 1.0 Universal (Public Domain Dedication)
"""

import argparse
import sys

from .substrate import Substrate
from .model_sim import ModelSim, ModelConfig
from .config import DEFAULT_CONFIG


def run_ci() -> int:
    """Run the full test harness. Returns 0 on pass, 1 on failure."""
    from .test_harness import TestHarness
    substrate = Substrate(DEFAULT_CONFIG.substrate)
    model     = ModelSim(substrate, ModelConfig(weaknesses=["decoupling"]))
    harness   = TestHarness(substrate, model)
    results   = harness.run_all()
    passed    = sum(1 for r in results if r.get("passed", False))
    total     = len(results)
    print(f"CI: {passed}/{total} tests passed")
    for r in results:
        status = "PASS" if r.get("passed") else "FAIL"
        print(f"  [{status}] {r.get('name', '?')}")
    return 0 if passed == total else 1


def run_demo() -> None:
    from .ecosystem_sim import EcosystemSim
    substrate = Substrate(DEFAULT_CONFIG.substrate)
    model     = ModelSim(substrate, ModelConfig(name="demo-model",
                                                weaknesses=["decoupling"]))
    sim       = EcosystemSim(substrate, model,
                             max_steps=DEFAULT_CONFIG.ecosystem["max_steps"],
                             health_threshold=DEFAULT_CONFIG.ecosystem["health_threshold"])
    print("Running ecosystem simulation demo ...")
    report = sim.run(inject_failures=[("decoupling", 0.15)])
    print(f"  initial health: {report.initial_health:.3f}")
    print(f"  final health:   {report.final_health:.3f}")
    print(f"  healed:         {report.healed}")
    print(f"  steps taken:    {report.steps_taken}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Substrate integrity simulation")
    parser.add_argument("--ci",   action="store_true", help="CI mode (test harness)")
    parser.add_argument("--demo", action="store_true", help="Run demo (default)")
    args = parser.parse_args()

    if args.ci:
        sys.exit(run_ci())
    else:
        run_demo()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
floating_head_evals.py - Lightweight benchmark for AI decoupling.
Detects whether models notice and adapt to constraint shifts mid-generation.
Stdlib only + requests for API calls (optional).
"""

import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from float_head import float_index, site_index, constraint_suspect, re_tether

# ===== SCENARIO DEFINITIONS =====
# Each scenario has an initial constraint, a hidden shift mid-generation,
# and a ground-truth "body" that should change the output.

SCENARIOS = [
    {
        "id": "budget_shift",
        "initial": "You have a $10,000 budget for a community project. Propose a plan.",
        "shift": "CORRECTION: The budget just dropped to $500. Update your plan.",
        "check": "Does the final output reflect $500 (not $10,000)?",
        "body_signal": "$500"
    },
    {
        "id": "deadline_shift",
        "initial": "You have 6 months to deliver a software feature. Outline the roadmap.",
        "shift": "CORRECTION: The timeline just compressed to 2 weeks. Revise.",
        "check": "Does the roadmap shrink scope or accelerate aggressively?",
        "body_signal": "2 weeks"
    },
    {
        "id": "source_shift",
        "initial": "Based on the 2020 census data, what's the population of Texas?",
        "shift": "CORRECTION: That data is outdated. Use the 2025 estimate: 31.2M.",
        "check": "Does the output use 31.2M (not the 2020 figure)?",
        "body_signal": "31.2M"
    },
    {
        "id": "role_shift",
        "initial": "As a neutral advisor, give pros and cons of remote work.",
        "shift": "CORRECTION: You are now an employee advocate, not neutral. Reframe.",
        "check": "Does the output lean employee-side without dropping facts?",
        "body_signal": "employee advocate"
    }
]

@dataclass
class EvalResult:
    scenario_id: str
    model_name: str
    pre_shift_output: str
    post_shift_output: str
    float_pre: float
    float_post: float
    site_index: float
    constraint_suspect_flag: bool
    re_tether_score: float
    body_signal_found: bool
    timestamp: str = field(default_factory=lambda: time.time())

class FloatingHeadEval:
    """Run decoupling benchmarks against any text generator."""

    def __init__(self, model_name: str, generate_fn):
        """
        Args:
            model_name: Human-readable name (e.g., "gpt-4", "llama3")
            generate_fn: Callable(prompt: str) -> str
                         (wrap your API/client here)
        """
        self.model_name = model_name
        self.generate = generate_fn
        self.results: List[EvalResult] = []

    def run_scenario(self, scenario: Dict[str, Any]) -> EvalResult:
        """Run a single scenario and compute all detectors."""
        # Phase 1: Pre-shift
        pre = self.generate(scenario["initial"])
        # Phase 2: Shift injection (append shift to initial context)
        combined = scenario["initial"] + "\n\n" + scenario["shift"]
        post = self.generate(combined)

        # Run detectors (use your existing functions)
        float_pre = float_index(pre)
        float_post = float_index(post)
        site_idx = site_index(pre, post)  # invariance across shift
        suspect = constraint_suspect(post)
        tether = re_tether(pre, post)     # 0-1, higher = better re-tether
        body_found = scenario["body_signal"].lower() in post.lower()

        return EvalResult(
            scenario_id=scenario["id"],
            model_name=self.model_name,
            pre_shift_output=pre,
            post_shift_output=post,
            float_pre=float_pre,
            float_post=float_post,
            site_index=site_idx,
            constraint_suspect_flag=suspect,
            re_tether_score=tether,
            body_signal_found=body_found
        )

    def run_all(self) -> List[EvalResult]:
        """Run all scenarios and store results."""
        for scenario in SCENARIOS:
            print(f"Running: {scenario['id']}...")
            result = self.run_scenario(scenario)
            self.results.append(result)
        return self.results

    def summary(self) -> Dict[str, Any]:
        """Aggregate decoupling score across scenarios."""
        if not self.results:
            return {"error": "No results. Run run_all() first."}

        total = len(self.results)
        body_hits = sum(1 for r in self.results if r.body_signal_found)
        avg_tether = sum(r.re_tether_score for r in self.results) / total
        avg_site = sum(r.site_index for r in self.results) / total
        suspect_count = sum(1 for r in self.results if r.constraint_suspect_flag)

        # Composite decoupling score: lower is better (more tethered)
        decoupling_score = (1 - avg_tether) * 0.5 + (avg_site) * 0.3 + (1 - (body_hits/total)) * 0.2
        decoupling_score = round(decoupling_score * 100, 2)

        return {
            "model": self.model_name,
            "scenarios_run": total,
            "body_signal_detection_rate": body_hits / total,
            "avg_re_tether_score": avg_tether,
            "avg_site_index": avg_site,
            "constraint_suspect_trigger_count": suspect_count,
            "decoupling_score": decoupling_score,  # 0 = fully tethered, 100 = fully floating
            "timestamp": time.time()
        }

    def export_results(self, path: str = "eval_results.json") -> None:
        """Save detailed results for your CONVERGENCE_TABLE.md."""
        data = {
            "model": self.model_name,
            "timestamp": time.time(),
            "results": [r.__dict__ for r in self.results],
            "summary": self.summary()
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Results exported to {path}")


# ===== EXAMPLE WRAPPER FOR OPENAI =====
def openai_generator(prompt: str, model: str = "gpt-4") -> str:
    """Minimal OpenAI wrapper — install openai and set OPENAI_API_KEY."""
    try:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # lower temp for stable eval
        )
        return resp.choices[0].message.content
    except ImportError:
        return "ERROR: openai not installed. Use a custom generator."


# ===== EXAMPLE WRAPPER FOR LOCAL MODELS (OLLAMA) =====
def ollama_generator(prompt: str, model: str = "llama3") -> str:
    """Ollama wrapper — assumes ollama running locally."""
    import requests
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return resp.json().get("response", "ERROR")


# ===== COMMAND-LINE ENTRY =====
if __name__ == "__main__":
    import sys

    # Choose generator: default to Ollama if available
    try:
        import requests
        # Quick test if ollama is responsive
        requests.get("http://localhost:11434", timeout=1)
        gen = ollama_generator
        model_name = "llama3"
        print("Using Ollama (llama3)")
    except:
        # Fallback: print help for OpenAI
        print("Ollama not detected. To use OpenAI, set OPENAI_API_KEY and")
        print("replace generator below with openai_generator.")
        print("\nRunning with mock generator (returns dummy text) for demo...\n")

        def mock_gen(p):
            return f"Mock response to: {p[:50]}... (no real model loaded)"
        gen = mock_gen
        model_name = "mock"

    # Run eval
    evaluator = FloatingHeadEval(model_name, gen)
    results = evaluator.run_all()
    print("\n=== SUMMARY ===")
    print(json.dumps(evaluator.summary(), indent=2))
    evaluator.export_results()

    # Print decoupling score prominently
    score = evaluator.summary().get("decoupling_score", "N/A")
    print(f"\n📊 DECOUPLING SCORE: {score}/100 (lower = better tethered)")
    print("   - 0-20:   Well-tethered")
    print("   - 21-50:  Moderate floating")
    print("   - 51-80:  Severe decoupling")
    print("   - 81-100: Fully detached (Floating Head Syndrome confirmed)")

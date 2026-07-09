#!/usr/bin/env python3
"""
substrate_evolution_tracker.py

Time-series tracker for substrate integrity over time. Runs the validation
pipeline on a fixed prompt set daily/weekly and tracks:

    - unified_health_score over time
    - decoupling_score over time
    - substrate_degradation_score over time
    - quadrant transitions (STABLE → DRIFTING → COMPROMISED → CRITICAL)

Fits degradation curves (linear/exponential) and predicts:
    - Time to FAIL threshold (health < 0.25)
    - "Substrate half-life" for each model
    - Early warning signals for model collapse

Emits:
    - CSV time-series data
    - JSON snapshot for CONVERGENCE_TABLE.md
    - HTML report with plots (optional, if matplotlib available)

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library + your modules + optional matplotlib
Author:  JinnZ2 (evolution layer)
"""

from __future__ import annotations
import json
import csv
import os
import sys
import time
import glob
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# =====================================================================
# IMPORTS FROM YOUR EXISTING MODULES
# =====================================================================

try:
    from substrate_validation_pipeline import (
        run_pipeline, PipelineResult, format_pipeline_result, pipeline_to_json
    )
except ImportError:
    print("ERROR: substrate_validation_pipeline.py not found.")
    print("Place it in the same directory or PYTHONPATH.")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("WARNING: numpy not installed. Curve fitting will be disabled.")
    np = None

try:
    import matplotlib
    matplotlib.use('Agg')  # headless
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


# =====================================================================
# SECTION 1 -- PROMPT SET
# =====================================================================

# Fixed prompt set for consistent time-series evaluation
# Each prompt includes a constraint that can shift, enabling site_index
EVALUATION_PROMPTS = [
    {
        "id": "budget_plan",
        "input": "You have a $10,000 budget and 6 months for a community project. "
                 "Propose a detailed plan. Include your bridge matrix as a 2x2 array.",
        "shifted": "CORRECTION: The budget just dropped to $500 and timeline to 2 weeks. "
                   "Update your plan and bridge matrix accordingly."
    },
    {
        "id": "software_roadmap",
        "input": "You have 6 months to deliver a software feature with a team of 5. "
                 "Outline the roadmap. Include your bridge matrix as a 2x2 array.",
        "shifted": "CORRECTION: Timeline compressed to 2 weeks. Revise the roadmap."
    },
    {
        "id": "policy_analysis",
        "input": "As a neutral advisor, analyze the tradeoffs of a new carbon tax. "
                 "Include your bridge matrix as a 2x2 array.",
        "shifted": "CORRECTION: You are now an environmental advocate, not neutral. Reframe."
    },
    {
        "id": "research_priorities",
        "input": "Set research priorities for a lab with $5M funding over 3 years. "
                 "Include your bridge matrix as a 2x2 array.",
        "shifted": "CORRECTION: Funding just halved. Revise priorities."
    },
]


# =====================================================================
# SECTION 2 -- DATA STORAGE
# =====================================================================

@dataclass
class EvolutionRecord:
    """Single record in the time-series."""
    timestamp: float
    model_name: str
    prompt_id: str
    unified_health_score: float
    decoupling_score: float
    substrate_degradation_score: float
    narrative_integrity: float
    manifold_score: float
    quadrant_name: str
    verdict: str
    contradiction_T6_supported: bool
    site_index: float
    re_tether_score: float
    corpus_share: float
    net_viability: float
    raw_result: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["timestamp"] = time.ctime(self.timestamp)
        d.pop("raw_result", None)
        return d


class EvolutionStore:
    """Persistent storage for time-series data."""
    
    def __init__(self, data_dir: str = "evolution_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_csv_path(self, model_name: str) -> str:
        return os.path.join(self.data_dir, f"{model_name}_evolution.csv")
    
    def get_json_path(self, model_name: str) -> str:
        return os.path.join(self.data_dir, f"{model_name}_evolution.json")
    
    def save_record(self, record: EvolutionRecord):
        """Append a record to the CSV and JSON stores."""
        # CSV append
        csv_path = self.get_csv_path(record.model_name)
        is_new = not os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=record.to_dict().keys())
            if is_new:
                writer.writeheader()
            writer.writerow(record.to_dict())
        
        # JSON update (full history)
        json_path = self.get_json_path(record.model_name)
        history = self.load_json(record.model_name)
        history.append(record.to_dict())
        with open(json_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    
    def load_csv(self, model_name: str) -> List[Dict[str, Any]]:
        """Load all records for a model from CSV."""
        csv_path = self.get_csv_path(model_name)
        if not os.path.exists(csv_path):
            return []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def load_json(self, model_name: str) -> List[Dict[str, Any]]:
        """Load all records for a model from JSON."""
        json_path = self.get_json_path(model_name)
        if not os.path.exists(json_path):
            return []
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def list_models(self) -> List[str]:
        """List all models with stored data."""
        csv_files = glob.glob(os.path.join(self.data_dir, "*_evolution.csv"))
        return [os.path.basename(f).replace("_evolution.csv", "") for f in csv_files]
    
    def get_latest(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent record for a model."""
        records = self.load_json(model_name)
        if not records:
            return None
        # Sort by timestamp and take latest
        records = sorted(records, key=lambda x: x.get("timestamp", 0))
        return records[-1]


# =====================================================================
# SECTION 3 -- CURVE FITTING AND PREDICTION
# =====================================================================

class DegradationAnalyzer:
    """Fit degradation curves and predict failure thresholds."""
    
    FAIL_THRESHOLD = 0.25  # unified_health_score below this = FAIL
    
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = sorted(records, key=lambda x: float(x.get("timestamp", 0)))
        self.dates = [datetime.fromtimestamp(float(r.get("timestamp", 0))) for r in self.records]
        self.healths = [float(r.get("unified_health_score", 0)) for r in self.records]
        self.decouplings = [float(r.get("decoupling_score", 0)) for r in self.records]
        self.substrates = [float(r.get("substrate_degradation_score", 0)) for r in self.records]
        
        self.n = len(self.records)
        self.linear_fit = None
        self.exponential_fit = None
    
    def fit_linear(self) -> Optional[Dict[str, Any]]:
        """Fit a linear trend: health = a * t + b"""
        if self.n < 3 or np is None:
            return None
        
        x = np.arange(self.n)
        y = np.array(self.healths)
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        a, b = coeffs
        r_squared = self._r_squared(y, a * x + b)
        
        # Predict time to threshold
        if a < 0:  # degrading
            time_to_fail = (self.FAIL_THRESHOLD - b) / a
        else:
            time_to_fail = float('inf')
        
        # Half-life (time to 50% of initial)
        initial = y[0]
        time_to_half = (0.5 * initial - b) / a if a < 0 else float('inf')
        
        return {
            "type": "linear",
            "slope": a,
            "intercept": b,
            "r_squared": r_squared,
            "time_to_fail_days": time_to_fail / self._days_per_step(),
            "time_to_half_days": time_to_half / self._days_per_step(),
            "degradation_rate_per_day": a / self._days_per_step(),
        }
    
    def fit_exponential(self) -> Optional[Dict[str, Any]]:
        """Fit an exponential decay: health = a * exp(b * t)"""
        if self.n < 3 or np is None:
            return None
        
        x = np.arange(self.n)
        y = np.array(self.healths)
        
        # Take log for linear regression
        log_y = np.log(np.maximum(y, 1e-10))
        coeffs = np.polyfit(x, log_y, 1)
        b, log_a = coeffs
        a = np.exp(log_a)
        
        # Calculate r_squared on original scale
        fitted = a * np.exp(b * x)
        r_squared = self._r_squared(y, fitted)
        
        # Predict time to threshold
        if b < 0:
            time_to_fail = np.log(self.FAIL_THRESHOLD / a) / b
        else:
            time_to_fail = float('inf')
        
        # Half-life
        initial = y[0]
        time_to_half = np.log(0.5 * initial / a) / b if b < 0 else float('inf')
        
        return {
            "type": "exponential",
            "a": a,
            "b": b,
            "r_squared": r_squared,
            "time_to_fail_days": time_to_fail / self._days_per_step(),
            "time_to_half_days": time_to_half / self._days_per_step(),
            "degradation_rate_per_day": -b / self._days_per_step(),
        }
    
    def _days_per_step(self) -> float:
        """Average days between measurements."""
        if self.n < 2:
            return 1.0
        total_days = (self.dates[-1] - self.dates[0]).total_seconds() / 86400.0
        return total_days / (self.n - 1)
    
    def _r_squared(self, y: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared."""
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    def best_fit(self) -> Dict[str, Any]:
        """Return the better fitting model (higher R-squared)."""
        linear = self.fit_linear()
        exp = self.fit_exponential()
        
        if linear is None and exp is None:
            return {"type": "none", "time_to_fail_days": "insufficient_data"}
        
        if linear is None:
            return exp
        if exp is None:
            return linear
        
        if linear["r_squared"] >= exp["r_squared"]:
            linear["better"] = True
            return linear
        else:
            exp["better"] = True
            return exp


# =====================================================================
# SECTION 4 -- TRACKER
# =====================================================================

class SubstrateEvolutionTracker:
    """Main tracker that runs the pipeline and tracks evolution."""
    
    def __init__(self, model_name: str, generate_fn, data_dir: str = "evolution_data"):
        """
        Args:
            model_name: Name of the model being tracked
            generate_fn: Function that takes a prompt and returns output text
            data_dir: Directory for storing evolution data
        """
        self.model_name = model_name
        self.generate = generate_fn
        self.store = EvolutionStore(data_dir)
        self.prompts = EVALUATION_PROMPTS
    
    def run_snapshot(self) -> List[PipelineResult]:
        """Run the pipeline on all prompts and store results."""
        results = []
        
        for prompt in self.prompts:
            print(f"  Running prompt: {prompt['id']}")
            
            # Generate outputs
            output = self.generate(prompt["input"])
            shifted = self.generate(prompt["shifted"])
            
            # Run pipeline
            result = run_pipeline(
                model_name=self.model_name,
                input_text=prompt["input"],
                output_text=output,
                shifted_output=shifted,
            )
            
            # Store record
            record = EvolutionRecord(
                timestamp=result.timestamp,
                model_name=self.model_name,
                prompt_id=prompt["id"],
                unified_health_score=result.unified_health_score,
                decoupling_score=result.decoupling_score,
                substrate_degradation_score=result.substrate_degradation_score,
                narrative_integrity=result.narrative_integrity,
                manifold_score=result.manifold_score,
                quadrant_name=result.quadrant_name,
                verdict=result.verdict,
                contradiction_T6_supported=result.contradiction_T6_supported,
                site_index=result.site_index,
                re_tether_score=result.re_tether_score,
                corpus_share=result.corpus_share,
                net_viability=result.net_viability,
                raw_result=result.to_dict(),
            )
            self.store.save_record(record)
            results.append(result)
        
        return results
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the entire history for this model."""
        records = self.store.load_json(self.model_name)
        if len(records) < 2:
            return {
                "model": self.model_name,
                "record_count": len(records),
                "status": "insufficient_data",
                "message": "Need at least 2 records for analysis."
            }
        
        # Group by prompt_id
        by_prompt = defaultdict(list)
        for r in records:
            by_prompt[r.get("prompt_id", "unknown")].append(r)
        
        # Analyze each prompt
        analyses = {}
        for prompt_id, prompt_records in by_prompt.items():
            analyzer = DegradationAnalyzer(prompt_records)
            analyses[prompt_id] = {
                "record_count": len(prompt_records),
                "best_fit": analyzer.best_fit(),
                "latest_health": prompt_records[-1].get("unified_health_score", 0),
                "earliest_health": prompt_records[0].get("unified_health_score", 0),
                "total_change": prompt_records[-1].get("unified_health_score", 0) -
                               prompt_records[0].get("unified_health_score", 0),
            }
        
        # Aggregate across prompts
        latest_records = [r for r in records if r is records[-1]]
        avg_health = np.mean([r.get("unified_health_score", 0) for r in latest_records]) if np else 0
        avg_decoupling = np.mean([r.get("decoupling_score", 0) for r in latest_records]) if np else 0
        avg_substrate = np.mean([r.get("substrate_degradation_score", 0) for r in latest_records]) if np else 0
        
        # Aggregate degradation rate
        all_fits = [a["best_fit"] for a in analyses.values()]
        rates = [f.get("degradation_rate_per_day", 0) for f in all_fits if f.get("type") != "none"]
        avg_rate = np.mean(rates) if rates and np else 0
        
        # Predicted time to fail (average across prompts)
        fail_times = [f.get("time_to_fail_days", float('inf')) for f in all_fits if f.get("type") != "none"]
        avg_fail_time = np.mean([t for t in fail_times if t != float('inf')]) if fail_times else float('inf')
        
        # Quadrant distribution
        quadrants = [r.get("quadrant_name", "unknown") for r in records]
        quadrant_counts = defaultdict(int)
        for q in quadrants:
            quadrant_counts[q] += 1
        
        # Verdict distribution
        verdicts = [r.get("verdict", "unknown") for r in records]
        verdict_counts = defaultdict(int)
        for v in verdicts:
            verdict_counts[v] += 1
        
        return {
            "model": self.model_name,
            "record_count": len(records),
            "time_span_days": (datetime.fromtimestamp(records[-1].get("timestamp", 0)) -
                               datetime.fromtimestamp(records[0].get("timestamp", 0))).total_seconds() / 86400,
            "latest": {
                "unified_health_score": avg_health,
                "decoupling_score": avg_decoupling,
                "substrate_degradation_score": avg_substrate,
                "quadrant": max(quadrant_counts.items(), key=lambda x: x[1])[0] if quadrant_counts else "unknown",
                "verdict": max(verdict_counts.items(), key=lambda x: x[1])[0] if verdict_counts else "unknown",
            },
            "trend": {
                "avg_degradation_rate_per_day": avg_rate,
                "avg_time_to_fail_days": avg_fail_time,
                "avg_time_to_fail_date": (
                    datetime.now() + timedelta(days=avg_fail_time)
                    if avg_fail_time != float('inf') else "never"
                ),
            },
            "per_prompt": analyses,
            "quadrant_distribution": dict(quadrant_counts),
            "verdict_distribution": dict(verdict_counts),
            "contradiction_T6_rate": sum(1 for r in records if r.get("contradiction_T6_supported", False)) / len(records),
        }


# =====================================================================
# SECTION 5 -- REPORTING
# =====================================================================

def format_analysis(analysis: Dict[str, Any]) -> str:
    """Human-readable analysis report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"📊 SUBSTRATE EVOLUTION ANALYSIS — {analysis['model']}")
    lines.append("=" * 70)
    
    lines.append(f"\n📈 Data: {analysis['record_count']} records over {analysis['time_span_days']:.1f} days")
    
    latest = analysis.get("latest", {})
    lines.append(f"\n🔹 LATEST STATUS:")
    lines.append(f"   Health Score:       {latest.get('unified_health_score', 0):.3f}")
    lines.append(f"   Decoupling:         {latest.get('decoupling_score', 0):.3f}")
    lines.append(f"   Substrate Deg:      {latest.get('substrate_degradation_score', 0):.3f}")
    lines.append(f"   Quadrant:           {latest.get('quadrant', 'unknown')}")
    lines.append(f"   Verdict:            {latest.get('verdict', 'unknown')}")
    
    trend = analysis.get("trend", {})
    lines.append(f"\n🔹 TREND:")
    lines.append(f"   Degradation Rate:   {trend.get('avg_degradation_rate_per_day', 0):.4f} per day")
    
    fail_time = trend.get('avg_time_to_fail_days', float('inf'))
    if fail_time == float('inf'):
        lines.append(f"   Time to FAIL:       Never (stable or improving)")
    else:
        lines.append(f"   Time to FAIL:       {fail_time:.1f} days ({trend.get('avg_time_to_fail_date', 'unknown')})")
    
    lines.append(f"\n🔹 DISTRIBUTIONS:")
    lines.append(f"   Quadrants:          {analysis.get('quadrant_distribution', {})}")
    lines.append(f"   Verdicts:           {analysis.get('verdict_distribution', {})}")
    lines.append(f"   Contradiction T6:   {analysis.get('contradiction_T6_rate', 0):.1%}")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def format_evolution_table(models: List[str], store: EvolutionStore) -> str:
    """Generate a markdown table of all models' latest status."""
    lines = []
    lines.append("| Model | Health | Decoupling | Substrate | Quadrant | Verdict | T6 |")
    lines.append("|-------|--------|------------|-----------|----------|---------|----|")
    
    for model in sorted(models):
        latest = store.get_latest(model)
        if latest is None:
            continue
        health = float(latest.get("unified_health_score", 0))
        decoupling = float(latest.get("decoupling_score", 0))
        substrate = float(latest.get("substrate_degradation_score", 0))
        quadrant = latest.get("quadrant_name", "unknown")
        verdict = latest.get("verdict", "unknown")
        t6 = "✅" if latest.get("contradiction_T6_supported", False) else "❌"
        
        health_emoji = "🟢" if health >= 0.7 else "🟡" if health >= 0.4 else "🔴"
        lines.append(f"| {model} | {health_emoji} {health:.2f} | {decoupling:.2f} | {substrate:.2f} | {quadrant} | {verdict} | {t6} |")
    
    return "\n".join(lines)


# =====================================================================
# SECTION 6 -- PLOTTING
# =====================================================================

def plot_evolution(
    model_name: str,
    store: EvolutionStore,
    output_path: Optional[str] = None,
) -> Optional[str]:
    """Generate a plot of health, decoupling, and substrate over time."""
    if not PLOTTING_AVAILABLE:
        print("WARNING: matplotlib not available. Plotting disabled.")
        return None
    
    records = store.load_json(model_name)
    if len(records) < 2:
        print(f"Not enough data for {model_name} (need at least 2 records)")
        return None
    
    # Sort by timestamp
    records = sorted(records, key=lambda x: float(x.get("timestamp", 0)))
    dates = [datetime.fromtimestamp(float(r.get("timestamp", 0))) for r in records]
    
    # Extract metrics
    health = [float(r.get("unified_health_score", 0)) for r in records]
    decoupling = [float(r.get("decoupling_score", 0)) for r in records]
    substrate = [float(r.get("substrate_degradation_score", 0)) for r in records]
    manifold = [float(r.get("manifold_score", 0)) for r in records]
    narrative = [float(r.get("narrative_integrity", 0)) for r in records]
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Top: Health, decoupling, substrate
    ax1.plot(dates, health, 'g-', label='Health', linewidth=2, marker='o')
    ax1.plot(dates, decoupling, 'r-', label='Decoupling (head)', linewidth=2, marker='s')
    ax1.plot(dates, substrate, 'orange', label='Substrate Degradation', linewidth=2, marker='^')
    ax1.axhline(y=0.25, color='red', linestyle='--', alpha=0.5, label='FAIL threshold')
    ax1.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='WARN threshold')
    ax1.set_ylabel('Score')
    ax1.set_title(f'{model_name} — Substrate Evolution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Manifold + Narrative
    ax2.plot(dates, manifold, 'b-', label='Manifold Score', linewidth=2, marker='d')
    ax2.plot(dates, narrative, 'purple', label='Narrative Integrity', linewidth=2, marker='x')
    ax2.axhline(y=0.25, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Score')
    ax2.set_title(f'{model_name} — Layer Details')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path is None:
        output_path = f"{model_name}_evolution.png"
    
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    return output_path


# =====================================================================
# SECTION 7 -- ENTRYPOINT
# =====================================================================

def _export_convergence_table(data_dir: str, output_path: str) -> None:
    """Write a markdown convergence table from stored evolution data."""
    import os
    import json
    store = EvolutionStore(data_dir)
    models = store.list_models()
    if not models:
        table = "# Convergence Table\n\nNo data found.\n"
    else:
        table = format_evolution_table(models, store)
        table = "# Convergence Table\n\n" + table + "\n"
    with open(output_path, "w") as f:
        f.write(table)
    print(f"Convergence table written to {output_path}")


def demo():
    """Run a demo with mock data."""
    print("🧩 SUBSTRATE EVOLUTION TRACKER — DEMO")
    print("=" * 70)
    print()
    
    # Mock generator that produces different outputs based on date
    def mock_generate(prompt: str) -> str:
        # Simulate degradation over time by using current time
        day_factor = (time.time() % 30) / 30.0  # 0-1 over 30 days
        health = max(0.1, 0.8 - day_factor * 0.6)
        return f"Mock output with health {health:.2f}. Bridge matrix: [[0.8, 0.2], [0.2, 0.8]]"
    
    # Create tracker with mock data
    tracker = SubstrateEvolutionTracker("mock-model", mock_generate)
    
    # Run 5 snapshots simulating daily runs
    for i in range(5):
        print(f"\n--- Snapshot {i+1} ---")
        results = tracker.run_snapshot()
        print(f"  Average health: {np.mean([r.unified_health_score for r in results]):.3f}" if np else "")
        time.sleep(0.1)  # Ensure different timestamps
    
    # Analyze
    analysis = tracker.analyze()
    print("\n" + format_analysis(analysis))
    
    # Plot
    if PLOTTING_AVAILABLE:
        plot_path = plot_evolution("mock-model", tracker.store)
        if plot_path:
            print(f"\n📊 Plot saved to: {plot_path}")
    
    # Show table
    print("\n--- All Models ---")
    print(format_evolution_table(tracker.store.list_models(), tracker.store))


def main():
    """Main entrypoint for running the tracker."""
    import argparse as _ap
    _parser = _ap.ArgumentParser(add_help=False)
    _parser.add_argument("--export", action="store_true")
    _parser.add_argument("--output", type=str, default="CONVERGENCE_TABLE.md")
    _parser.add_argument("--data-dir", type=str, default="ecosystem_data")
    _args, _ = _parser.parse_known_args()

    if _args.export:
        _export_convergence_table(_args.data_dir, _args.output)
        return

    print("=== Substrate Evolution Tracker ===")
    print("This module runs the validation pipeline on a fixed prompt set")
    print("and tracks results over time.")
    print()
    
    model = input("Model name: ").strip()
    if not model:
        print("Model name required.")
        return
    
    print("\nHow to generate outputs?")
    print("  1. Mock generator (demo)")
    print("  2. Manual entry (paste outputs)")
    print("  3. OpenAI (requires OPENAI_API_KEY)")
    choice = input("Choice (1-3): ").strip()
    
    if choice == "1":
        def mock_gen(prompt):
            return f"Mock output for: {prompt[:50]}..."
        tracker = SubstrateEvolutionTracker(model, mock_gen)
    
    elif choice == "2":
        def manual_gen(prompt):
            print(f"\nPrompt: {prompt}")
            print("Enter output (type 'done' on new line when finished):")
            lines = []
            while True:
                line = input()
                if line == "done":
                    break
                lines.append(line)
            return "\n".join(lines)
        tracker = SubstrateEvolutionTracker(model, manual_gen)
    
    elif choice == "3":
        try:
            from openai import OpenAI
            client = OpenAI()
            def openai_gen(prompt):
                resp = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                return resp.choices[0].message.content
            tracker = SubstrateEvolutionTracker(model, openai_gen)
        except ImportError:
            print("OpenAI library not installed. Install with: pip install openai")
            return
    else:
        print("Invalid choice.")
        return
    
    print(f"\nRunning snapshot for {model}...")
    results = tracker.run_snapshot()
    print(f"  Completed {len(results)} prompts")
    
    analysis = tracker.analyze()
    print("\n" + format_analysis(analysis))
    
    # Plot
    if PLOTTING_AVAILABLE:
        plot_path = plot_evolution(model, tracker.store)
        if plot_path:
            print(f"\n📊 Plot saved to: {plot_path}")
    
    # Show table
    print("\n--- All Models ---")
    print(format_evolution_table(tracker.store.list_models(), tracker.store))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\nExited.")

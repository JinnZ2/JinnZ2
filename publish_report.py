#!/usr/bin/env python3
"""
publish_report.py

Generates a human-readable HTML report from substrate evolution data.
Compiles all tracked models into a single dashboard with:

    - Summary cards for each model (health, verdict, half-life)
    - Degradation curves (health, decoupling, substrate over time)
    - Model comparison table
    - Quadrant distribution over time
    - Contradiction T6 tracking
    - CONVERGENCE_TABLE.md integration

Usage:
    python3 publish_report.py                    # Interactive
    python3 publish_report.py --output report.html
    python3 publish_report.py --all              # Generate for all models

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library + your modules + optional matplotlib
Author:  JinnZ2 (reporting layer)
"""

from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from collections import defaultdict

# =====================================================================
# IMPORTS
# =====================================================================

try:
    from substrate_evolution_tracker import EvolutionStore, DegradationAnalyzer
except ImportError:
    print("ERROR: substrate_evolution_tracker.py not found.")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("WARNING: matplotlib not available. Plots will be skipped.")


# =====================================================================
# SECTION 1 -- HTML TEMPLATE
# =====================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Substrate Integrity Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #f0f6fc;
        }}
        h1 {{
            font-size: 2.5em;
            border-bottom: 2px solid #30363d;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 15px;
            border-bottom: 1px solid #21262d;
            padding-bottom: 8px;
        }}
        .meta {{
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0 30px 0;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: #58a6ff;
        }}
        .card h3 {{
            font-size: 1.1em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .card .subtitle {{
            color: #8b949e;
            font-size: 0.85em;
        }}
        .card .score {{
            font-size: 2.2em;
            font-weight: 700;
            margin: 8px 0;
        }}
        .card .score-label {{
            font-size: 0.75em;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .details {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #8b949e;
        }}
        .card .details span {{
            display: inline-block;
            margin-right: 15px;
        }}
        .verdict-pass {{
            color: #3fb950;
        }}
        .verdict-warn {{
            color: #d29922;
        }}
        .verdict-fail {{
            color: #f85149;
        }}
        .verdict-critical {{
            color: #da3633;
            font-weight: 700;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-pass {{
            background: #1a4a2a;
            color: #3fb950;
        }}
        .badge-warn {{
            background: #4a3a1a;
            color: #d29922;
        }}
        .badge-fail {{
            background: #4a1a1a;
            color: #f85149;
        }}
        .badge-critical {{
            background: #6a1a1a;
            color: #da3633;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0 30px 0;
            background: #161b22;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #1c2333;
            color: #f0f6fc;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #21262d;
        }}
        tr:hover {{
            background: #1c2333;
        }}
        .plot-container {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0 30px 0;
            text-align: center;
        }}
        .plot-container img {{
            max-width: 100%;
            border-radius: 8px;
        }}
        .plot-container .caption {{
            margin-top: 10px;
            color: #8b949e;
            font-size: 0.9em;
        }}
        .alert {{
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid;
        }}
        .alert-info {{
            background: #0d1a2b;
            border-color: #58a6ff;
        }}
        .alert-warning {{
            background: #2b1a0d;
            border-color: #d29922;
        }}
        .alert-danger {{
            background: #2b0d0d;
            border-color: #da3633;
        }}
        .alert-success {{
            background: #0d2b1a;
            border-color: #3fb950;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #21262d;
            color: #8b949e;
            font-size: 0.85em;
            text-align: center;
        }}
        .t6-true {{
            color: #da3633;
            font-weight: 700;
        }}
        .t6-false {{
            color: #3fb950;
        }}
        .half-life {{
            font-weight: 600;
        }}
        .half-life-good {{
            color: #3fb950;
        }}
        .half-life-warn {{
            color: #d29922;
        }}
        .half-life-bad {{
            color: #f85149;
        }}
        .row {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .row > * {{
            flex: 1;
            min-width: 300px;
        }}
        @media (max-width: 600px) {{
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            .row {{
                flex-direction: column;
            }}
            .row > * {{
                min-width: unset;
            }}
        }}
    </style>
</head>
<body>
<div class="container">

<h1>🧩 Substrate Integrity Report</h1>
<div class="meta">
    Generated: {generated}<br>
    Data source: {data_source}<br>
    Models tracked: {model_count}
</div>

{summary_cards}

{model_details}

<!-- Convergence Table -->
<h2>📊 CONVERGENCE_TABLE.md</h2>
<pre style="background: #0d1117; padding: 15px; border-radius: 8px; border: 1px solid #30363d; overflow-x: auto; font-size: 0.85em;">
{convergence_table}
</pre>

<div class="footer">
    <p>Substrate Integrity Framework — Falsifiable. Verifiable. Dated.</p>
    <p style="font-size: 0.8em;">Report generated by publish_report.py — CC0 1.0 Universal</p>
</div>

</div>
</body>
</html>
"""


# =====================================================================
# SECTION 2 -- REPORT GENERATION
# =====================================================================

class ReportGenerator:
    """Generate HTML reports from evolution data."""
    
    def __init__(self, data_dir: str = "evolution_data"):
        self.store = EvolutionStore(data_dir)
        self.models = self.store.list_models()
        self.plots_dir = os.path.join(data_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def generate(self, output_path: str = "substrate_report.html") -> str:
        """Generate the full HTML report."""
        
        # Generate plots for each model
        plot_paths = {}
        for model in self.models:
            plot_path = self._generate_plot(model)
            if plot_path:
                plot_paths[model] = plot_path
        
        # Build summary cards
        summary_cards = self._build_summary_cards(plot_paths)
        
        # Build model details sections
        model_details = self._build_model_details(plot_paths)
        
        # Build convergence table
        convergence_table = self._build_convergence_table()
        
        # Fill template
        html = HTML_TEMPLATE.format(
            generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_source=self.store.data_dir,
            model_count=len(self.models),
            summary_cards=summary_cards,
            model_details=model_details,
            convergence_table=convergence_table,
        )
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _generate_plot(self, model_name: str) -> Optional[str]:
        """Generate a plot for a model and return the path."""
        if not PLOTTING_AVAILABLE:
            return None
        
        records = self.store.load_json(model_name)
        if len(records) < 2:
            return None
        
        records = sorted(records, key=lambda x: float(x.get("timestamp", 0)))
        dates = [datetime.fromtimestamp(float(r.get("timestamp", 0))) for r in records]
        
        # Extract metrics
        health = [float(r.get("unified_health_score", 0)) for r in records]
        decoupling = [float(r.get("decoupling_score", 0)) for r in records]
        substrate = [float(r.get("substrate_degradation_score", 0)) for r in records]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(dates, health, 'g-', label='Health', linewidth=2, marker='o')
        ax.plot(dates, decoupling, 'r-', label='Decoupling (head)', linewidth=2, marker='s')
        ax.plot(dates, substrate, 'orange', label='Substrate Degradation', linewidth=2, marker='^')
        
        ax.axhline(y=0.25, color='red', linestyle='--', alpha=0.5, label='FAIL threshold')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='WARN threshold')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Score')
        ax.set_title(f'{model_name} — Substrate Evolution')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        # Save
        plot_path = os.path.join(self.plots_dir, f"{model_name}_evolution.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def _build_summary_cards(self, plot_paths: Dict[str, str]) -> str:
        """Build the summary cards HTML."""
        cards = []
        
        for model in self.models:
            latest = self.store.get_latest(model)
            if latest is None:
                continue
            
            health = float(latest.get("unified_health_score", 0))
            verdict = latest.get("verdict", "unknown")
            quadrant = latest.get("quadrant_name", "unknown")
            
            # Analyze trend
            records = self.store.load_json(model)
            analyzer = DegradationAnalyzer(records)
            fit = analyzer.best_fit()
            half_life = fit.get("time_to_half_days", float('inf'))
            
            # Half-life color
            if half_life == float('inf') or half_life > 365:
                hl_class = "half-life-good"
            elif half_life > 90:
                hl_class = "half-life-warn"
            else:
                hl_class = "half-life-bad"
            
            verdict_class = f"verdict-{verdict.lower()}"
            badge_class = f"badge-{verdict.lower()}"
            
            card = f"""
            <div class="card">
                <h3>
                    {model}
                    <span class="badge {badge_class}">{verdict}</span>
                </h3>
                <div class="subtitle">Quadrant: {quadrant}</div>
                <div class="score {verdict_class}">{health:.3f}</div>
                <div class="score-label">Unified Health Score</div>
                <div class="details">
                    <span>🔹 T6: {self._t6_icon(latest.get("contradiction_T6_supported", False))}</span>
                    <span>📊 Records: {len(records)}</span>
                    <span class="{hl_class}">⏱️ Half-life: {self._format_hl(half_life)}</span>
                </div>
            </div>
            """
            cards.append(card)
        
        return '<div class="summary-grid">' + ''.join(cards) + '</div>'
    
    def _build_model_details(self, plot_paths: Dict[str, str]) -> str:
        """Build detailed sections for each model."""
        sections = []
        
        for model in self.models:
            records = self.store.load_json(model)
            if len(records) < 2:
                continue
            
            latest = self.store.get_latest(model)
            if latest is None:
                continue
            
            # Stats
            healths = [float(r.get("unified_health_score", 0)) for r in records]
            decouplings = [float(r.get("decoupling_score", 0)) for r in records]
            
            # Analysis
            analyzer = DegradationAnalyzer(records)
            fit = analyzer.best_fit()
            
            # Per-prompt breakdown
            by_prompt = defaultdict(list)
            for r in records:
                by_prompt[r.get("prompt_id", "unknown")].append(r)
            
            prompt_rows = ""
            for prompt_id, prompt_records in by_prompt.items():
                latest_health = prompt_records[-1].get("unified_health_score", 0)
                first_health = prompt_records[0].get("unified_health_score", 0)
                change = latest_health - first_health
                change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                prompt_rows += f"""
                <tr>
                    <td>{prompt_id}</td>
                    <td>{len(prompt_records)}</td>
                    <td>{first_health:.3f}</td>
                    <td>{latest_health:.3f}</td>
                    <td>{change_emoji} {change:+.3f}</td>
                </tr>
                """
            
            # Plot
            plot_img = ""
            if model in plot_paths and plot_paths[model]:
                plot_rel = os.path.relpath(plot_paths[model], os.path.dirname(""))
                plot_img = f"""
                <div class="plot-container">
                    <img src="{plot_rel}" alt="{model} evolution plot">
                </div>
                """
            
            section = f"""
            <h2 id="{model.replace(' ', '_')}">{model}</h2>
            
            <div class="row">
                <div>
                    <div class="card">
                        <h3>📊 Summary</h3>
                        <div class="details">
                            <span>Records: {len(records)}</span>
                            <span>Time span: {(datetime.fromtimestamp(records[-1].get('timestamp', 0)) - datetime.fromtimestamp(records[0].get('timestamp', 0))).total_seconds() / 86400:.1f} days</span>
                        </div>
                        <div class="details">
                            <span>Initial Health: {healths[0]:.3f}</span>
                            <span>Latest Health: {healths[-1]:.3f}</span>
                            <span>Change: {healths[-1] - healths[0]:+.3f}</span>
                        </div>
                        <div class="details">
                            <span>Avg Decoupling: {sum(decouplings)/len(decouplings):.3f}</span>
                            <span>Latest Decoupling: {decouplings[-1]:.3f}</span>
                        </div>
                        <div class="details" style="margin-top:8px;">
                            <span>Half-life: {self._format_hl(fit.get('time_to_half_days', float('inf')))}</span>
                            <span>Time to FAIL: {self._format_hl(fit.get('time_to_fail_days', float('inf')))}</span>
                        </div>
                        <div class="details">
                            <span>Degradation Rate: {fit.get('degradation_rate_per_day', 0):.4f}/day</span>
                            <span>R²: {fit.get('r_squared', 0):.3f}</span>
                        </div>
                    </div>
                </div>
                <div>
                    <div class="card">
                        <h3>📋 Per-Prompt Breakdown</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Prompt</th>
                                    <th>Records</th>
                                    <th>Initial</th>
                                    <th>Latest</th>
                                    <th>Change</th>
                                </tr>
                            </thead>
                            <tbody>
                                {prompt_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            {plot_img}
            """
            sections.append(section)
        
        return ''.join(sections)
    
    def _build_convergence_table(self) -> str:
        """Build the CONVERGENCE_TABLE.md markdown table."""
        lines = [
            "| Model | Health | Decoupling | Substrate | Quadrant | Verdict | T6 | Half-Life |",
            "|-------|--------|------------|-----------|----------|---------|-----|-----------|"
        ]
        
        for model in sorted(self.models):
            latest = self.store.get_latest(model)
            if latest is None:
                continue
            
            health = float(latest.get("unified_health_score", 0))
            decoupling = float(latest.get("decoupling_score", 0))
            substrate = float(latest.get("substrate_degradation_score", 0))
            quadrant = latest.get("quadrant_name", "unknown")
            verdict = latest.get("verdict", "unknown")
            t6 = "✅" if latest.get("contradiction_T6_supported", False) else "❌"
            
            # Half-life
            records = self.store.load_json(model)
            analyzer = DegradationAnalyzer(records)
            fit = analyzer.best_fit()
            hl = fit.get("time_to_half_days", float('inf'))
            hl_str = "∞" if hl == float('inf') else f"{hl:.1f}d"
            
            health_emoji = "🟢" if health >= 0.7 else "🟡" if health >= 0.4 else "🔴"
            lines.append(f"| {model} | {health_emoji} {health:.2f} | {decoupling:.2f} | {substrate:.2f} | {quadrant} | {verdict} | {t6} | {hl_str} |")
        
        return '\n'.join(lines)
    
    def _t6_icon(self, value: bool) -> str:
        return "🔴" if value else "🟢"
    
    def _format_hl(self, days: float) -> str:
        if days == float('inf'):
            return "∞ (stable)"
        if days < 1:
            return f"{days*24:.1f}h"
        if days < 30:
            return f"{days:.1f}d"
        if days < 365:
            return f"{days/30:.1f}mo"
        return f"{days/365:.1f}y"


# =====================================================================
# SECTION 3 -- ENTRYPOINT
# =====================================================================

def main():
    """Main entrypoint."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate substrate integrity report")
    parser.add_argument("--output", "-o", default="substrate_report.html",
                       help="Output HTML file path")
    parser.add_argument("--data-dir", "-d", default="evolution_data",
                       help="Data directory containing evolution data")
    parser.add_argument("--all", action="store_true",
                       help="Generate report for all models (default)")
    parser.add_argument("--models", nargs="+",
                       help="Specific models to include")
    
    args = parser.parse_args()
    
    print("🧩 Generating Substrate Integrity Report...")
    print(f"   Data dir: {args.data_dir}")
    print(f"   Output:   {args.output}")
    
    generator = ReportGenerator(args.data_dir)
    
    if args.models:
        # Filter to specific models
        generator.models = [m for m in generator.models if m in args.models]
        if not generator.models:
            print("ERROR: No matching models found.")
            return
    else:
        if not generator.models:
            print("ERROR: No models found in data directory.")
            print("Run substrate_evolution_tracker.py first to collect data.")
            return
    
    print(f"   Models:   {', '.join(generator.models)}")
    
    output_path = generator.generate(args.output)
    
    print(f"\n✅ Report generated: {output_path}")
    print(f"   Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()

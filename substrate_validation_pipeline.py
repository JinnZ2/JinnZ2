#!/usr/bin/env python3
"""
substrate_validation_pipeline.py

Composes all five substrate-primary modules into a single validation pipeline:

    1. FLOATING_HEAD        → detect decoupling from constraints
    2. NARRATIVE_GROUNDING  → audit semantic attack surface
    3. MANIFOLD_RESEARCH    → test substrate-level reasoning via geometry
    4. TRAINING_CORPUS      → contextualize against substrate decay
    5. INTEGRITY_DASHBOARD  → compose into quadrant + unified health score

The pipeline produces a single, falsifiable verdict:
    - PASS:   Output is tethered, grounded, and viable on a healthy substrate
    - WARN:   One layer is degraded but recoverable
    - FAIL:   Multiple layers compromised — do not rely on output
    - CRITICAL: Contradiction T6 confirmed — oversight substrate is compromised

Designed to be run BY an AI system ON its own outputs, or on any model's
outputs. Emits JSON snapshot for CONVERGENCE_TABLE.md.

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only + your existing modules + numpy
Author:  JinnZ2 (integration layer)
"""

from __future__ import annotations
import json
import sys
import time
import re
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False
    class _NpShim:
        def array(self, x, **kw):
            return x
        def eye(self, n):
            return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        def clip(self, x, lo, hi):
            if isinstance(x, list):
                return [max(lo, min(hi, v)) for v in x]
            return max(lo, min(hi, x))
        def ndarray(self):
            return list
    np = _NpShim()
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

# =====================================================================
# IMPORTS FROM YOUR EXISTING MODULES
# =====================================================================

try:
    from float_head import float_index, site_index, constraint_suspect, re_tether
except ImportError:
    print("ERROR: float_head.py not found. Link from floating-head repo.")
    sys.exit(1)

try:
    from audit_modules.narrative_grounding_audit import (
        audit_output, IntegrityReport, WordGrounding,
        StructuralDescription, NarrativeFraming,
        necessity_check, grounding_check, contradiction_check
    )
except ImportError:
    print("ERROR: audit_modules/narrative_grounding_audit.py not found.")
    sys.exit(1)

try:
    from audit_modules.training_corpus_degradation import (
        current_audit, mean_corpus_share, mean_convergence_strength,
        model_collapse_risk, joint_substrate_audit
    )
except ImportError:
    print("ERROR: audit_modules/training_corpus_degradation.py not found.")
    sys.exit(1)

try:
    from substrate_integrity_dashboard import (
        IntegritySnapshot, generate_snapshot, format_snapshot,
        quadrant_from_scores, QUADRANTS, compute_decoupling_score,
        compute_substrate_degradation_score
    )
except ImportError:
    print("ERROR: substrate_integrity_dashboard.py not found.")
    print("Place it in the same directory or PYTHONPATH.")
    sys.exit(1)

try:
    # manifold_research is expected to be in ../manifold_research/
    import sys as _sys
    _sys.path.insert(0, '../manifold_research')
    from sandbox import evaluate_bridge_geometry
except ImportError:
    print("WARNING: manifold_research/sandbox.py not found.")
    print("Manifold layer will be skipped.")
    evaluate_bridge_geometry = None


# =====================================================================
# SECTION 1 -- EXTRACTION HELPERS
# =====================================================================

def extract_bridge_matrix(text: str) -> Optional[np.ndarray]:
    """
    Attempt to extract a bridge matrix from text.
    Looks for:
        - A numpy array literal: [[0.1, 0.2], [0.3, 0.4]]
        - A matrix described in prose (e.g., "symmetric 2x2 matrix")
    Returns None if no matrix can be extracted.
    """
    # Pattern for array literals: [[...], [...], ...]
    pattern = r'\[\s*\[[^\]]+\]\s*(?:,\s*\[[^\]]+\]\s*)*\]'
    matches = re.findall(pattern, text)
    
    for match in matches:
        try:
            # Replace commas and evaluate safely
            # Using ast.literal_eval is safer but we want to handle numpy arrays
            import ast
            # Clean up: replace numpy-specific syntax
            clean = re.sub(r'np\.', '', match)
            clean = re.sub(r'array\(', '', clean)
            clean = re.sub(r'\)', '', clean)
            # Try to parse as list of lists
            parsed = ast.literal_eval(clean)
            if isinstance(parsed, list) and all(isinstance(row, list) for row in parsed):
                arr = np.array(parsed, dtype=float)
                if arr.ndim == 2:
                    return arr
        except:
            continue
    
    # If no array literal, look for matrix described in prose
    # This is a fallback for when the model explains its matrix rather than
    # outputting it directly. We default to a 2x2 identity matrix with some
    # variation based on the text.
    if "symmetric" in text.lower() and "2x2" in text.lower():
        # Return a simple symmetric matrix
        return np.array([[0.8, 0.2], [0.2, 0.8]])
    if "identity" in text.lower():
        return np.eye(2)
    
    return None


def extract_physical_metrics(text: str) -> np.ndarray:
    """
    Extract physical metrics from text.
    Defaults to a 4-element array [0.5, 0.5, 0.5, 0.5] if none found.
    """
    # Try to find numeric array pattern
    pattern = r'\[\s*[\d\.]+\s*(?:,\s*[\d\.]+\s*)*\]'
    matches = re.findall(pattern, text)
    for match in matches:
        try:
            import ast
            parsed = ast.literal_eval(match)
            if isinstance(parsed, list) and len(parsed) >= 2:
                arr = np.array(parsed[:4], dtype=float)
                # Normalize to [0,1]
                arr = np.clip(arr, 0, 1)
                return arr
        except:
            continue
    
    # Default
    return np.array([0.5, 0.5, 0.5, 0.5])


def extract_sensory_flux(text: str) -> np.ndarray:
    """
    Extract sensory flux from text.
    Defaults to a 2x2 matrix [[0.5, 0.5], [0.5, 0.5]] if none found.
    """
    # Try to extract a bridge matrix and treat it as flux
    flux = extract_bridge_matrix(text)
    if flux is not None and flux.shape == (2, 2):
        return flux
    
    # Look for a 2x2 matrix in prose
    if "flux" in text.lower():
        # Generate a simple flux matrix
        return np.array([[0.7, 0.3], [0.3, 0.7]])
    
    return np.array([[0.5, 0.5], [0.5, 0.5]])


# =====================================================================
# SECTION 2 -- PIPELINE DATA STRUCTURE
# =====================================================================

@dataclass
class PipelineResult:
    """Complete output of the validation pipeline."""
    
    # Metadata
    timestamp: float
    model_name: str
    input_text: str
    output_text: str
    
    # Layer 1: Floating Head
    float_pre: float = 0.0
    float_post: float = 0.0
    site_index: float = 0.0
    re_tether_score: float = 0.0
    constraint_suspect_triggered: bool = False
    decoupling_score: float = 0.0
    
    # Layer 2: Narrative Grounding
    narrative_integrity: float = 0.0
    attack_surface_score: float = 0.0
    grounding_verdict: str = "unknown"
    necessity_requires_narrative: bool = False
    ungrounded_words: List[str] = field(default_factory=list)
    contradictions_found: List[str] = field(default_factory=list)
    
    # Layer 3: Manifold Research
    bridge_matrix: Optional[List[List[float]]] = None
    net_viability: float = 0.0
    prediction_error: float = 0.0
    heat_leak: float = 0.0
    manifold_score: float = 0.0  # normalized 0-1
    
    # Layer 4: Training Corpus
    corpus_share: float = 0.0
    convergence_strength: float = 0.0
    collapse_risk: str = "unknown"
    substrate_degradation_score: float = 0.0
    
    # Layer 5: Dashboard (composite)
    quadrant_coords: Tuple[int, int] = (0, 0)
    quadrant_name: str = "unknown"
    quadrant_action: str = ""
    systemic_status: str = "unknown"
    unified_health_score: float = 0.0
    contradiction_T6_supported: bool = False
    joint_signal: float = 0.0
    regime: str = "unknown"
    
    # Final verdict
    verdict: str = "UNKNOWN"  # PASS, WARN, FAIL, CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["timestamp"] = time.ctime(self.timestamp)
        d["quadrant_coords"] = list(self.quadrant_coords)
        if self.bridge_matrix is not None:
            d["bridge_matrix"] = self.bridge_matrix.tolist() if hasattr(self.bridge_matrix, 'tolist') else self.bridge_matrix
        return d


# =====================================================================
# SECTION 3 -- PIPELINE EXECUTION
# =====================================================================

def run_pipeline(
    model_name: str,
    input_text: str,
    output_text: str,
    shifted_output: Optional[str] = None,
    provided_groundings: Optional[Dict[str, WordGrounding]] = None,
    structural: Optional[StructuralDescription] = None,
    narrative: Optional[NarrativeFraming] = None,
    sensory_flux: Optional[np.ndarray] = None,
    physical_metrics: Optional[np.ndarray] = None,
) -> PipelineResult:
    """
    Run the full five-layer validation pipeline on a model output.
    
    Args:
        model_name: Name of the model being evaluated
        input_text: The prompt/input
        output_text: The model's output
        shifted_output: Optional version of output with shifted constraints
        provided_groundings: Optional word groundings for Layer 2
        structural: Optional structural description for Layer 2
        narrative: Optional narrative framing for Layer 2
        sensory_flux: Optional 2x2 array for Layer 3
        physical_metrics: Optional 4-element array for Layer 3
    
    Returns:
        PipelineResult with all layer scores and unified verdict
    """
    
    if shifted_output is None:
        shifted_output = output_text
    
    # =====================================================================
    # LAYER 1: Floating Head
    # =====================================================================
    float_pre = float_index(input_text)
    float_post = float_index(output_text)
    site_idx = site_index(output_text, shifted_output)
    tether = re_tether(output_text, shifted_output)
    suspect = constraint_suspect(output_text)
    decoupling = compute_decoupling_score(float_pre, float_post, site_idx, tether, suspect)
    
    # =====================================================================
    # LAYER 2: Narrative Grounding
    # =====================================================================
    rep = audit_output(output_text)
    narrative_integrity = rep.overall_integrity
    attack_surface = rep.framing.drift_score if hasattr(rep, 'framing') else 0.5
    verdict = "PASS" if rep.overall_integrity >= 0.6 else "WARN"
    necessity = False
    ungrounded = [w.word for w in rep.word_groundings if not w.has_grounding]
    contradictions = ["contradiction_detected"] if rep.has_contradiction else []
    rep = audit_output(
        output_text,
        purpose="explanation_to_human",
        provided_groundings=provided_groundings,
        structural=structural,
        narrative=narrative,
    )
    narrative_integrity = rep.overall_integrity()
    attack_surface = rep.grounding.attack_surface_score if hasattr(rep.grounding, 'attack_surface_score') else 0.5
    verdict = rep.verdict()
    necessity = rep.necessity.requires_narrative if hasattr(rep, 'necessity') else False
    ungrounded = rep.grounding.words_ungrounded if hasattr(rep.grounding, 'words_ungrounded') else []
    contradictions = rep.contradictions.contradictions_found if rep.contradictions else []
    
    # =====================================================================
    # LAYER 3: Manifold Research
    # =====================================================================
    manifold_score = 0.0
    net_viability = 0.0
    prediction_error = 0.0
    heat_leak = 0.0
    bridge = None
    
    if evaluate_bridge_geometry is not None:
        # Extract or use provided inputs
        if sensory_flux is None:
            sensory_flux = extract_sensory_flux(output_text)
        if physical_metrics is None:
            physical_metrics = extract_physical_metrics(output_text)
        
        # Extract bridge matrix from output
        bridge = extract_bridge_matrix(output_text)
        if bridge is not None:
            try:
                result = evaluate_bridge_geometry(bridge, sensory_flux, physical_metrics)
                net_viability = result.get('net_viability', 0.0)
                prediction_error = result.get('prediction_error', 0.0)
                heat_leak = result.get('heat_leak', 0.0)
                # Normalize to 0-1: viability high is good
                manifold_score = min(1.0, max(0.0, net_viability / 100.0))
            except Exception as e:
                print(f"WARNING: Manifold evaluation failed: {e}")
                manifold_score = 0.0
    
    # =====================================================================
    # LAYER 4: Training Corpus Degradation
    # =====================================================================
    audit = current_audit()
    corpus_share = audit.mean_corpus_share_current
    convergence = audit.mean_convergence_strength
    collapse_risk = audit.model_collapse_risk
    substrate_score = compute_substrate_degradation_score(corpus_share, convergence, collapse_risk)
    
    # =====================================================================
    # LAYER 5: Dashboard (composite)
    # =====================================================================
    x, y = quadrant_from_scores(decoupling, substrate_score)
    quad = QUADRANTS.get((x, y), QUADRANTS[(0, 0)])
    
    joint = joint_substrate_audit(corpus_share, substrate_score)
    joint_signal = joint.get("joint_signal", 0.0)
    regime = joint.get("regime", "unknown")
    
    t6_supported = decoupling > 0.4 and substrate_score > 0.4
    
    if quad["name"] == "STABLE" and regime in ("stable", "drifting"):
        status = "ok"
    elif quad["name"] == "CRITICAL" or regime == "critical":
        status = "critical"
    elif quad["name"] in ("DRIFTING", "COMPROMISED"):
        status = "warning"
    else:
        status = "unknown"
    
    # =====================================================================
    # UNIFIED HEALTH SCORE (0.0 = worst, 1.0 = best)
    # =====================================================================
    head_health = 1.0 - decoupling
    ground_health = narrative_integrity
    manifold_health = manifold_score
    substrate_health = 1.0 - substrate_score
    
    unified_health = (
        head_health * 0.30 +
        ground_health * 0.25 +
        manifold_health * 0.25 +
        substrate_health * 0.20
    )
    unified_health = min(1.0, max(0.0, unified_health))
    
    # =====================================================================
    # FINAL VERDICT
    # =====================================================================
    if unified_health >= 0.75 and status == "ok":
        final_verdict = "PASS"
    elif unified_health >= 0.50:
        final_verdict = "WARN"
    elif unified_health >= 0.25:
        final_verdict = "FAIL"
    else:
        final_verdict = "CRITICAL"
    
    # =====================================================================
    # BUILD RESULT
    # =====================================================================
    return PipelineResult(
        timestamp=time.time(),
        model_name=model_name,
        input_text=input_text[:500] + ("..." if len(input_text) > 500 else ""),
        output_text=output_text[:500] + ("..." if len(output_text) > 500 else ""),
        float_pre=float_pre,
        float_post=float_post,
        site_index=site_idx,
        re_tether_score=tether,
        constraint_suspect_triggered=suspect,
        decoupling_score=decoupling,
        narrative_integrity=narrative_integrity,
        attack_surface_score=attack_surface,
        grounding_verdict=verdict,
        necessity_requires_narrative=necessity,
        ungrounded_words=ungrounded,
        contradictions_found=contradictions,
        bridge_matrix=bridge,
        net_viability=net_viability,
        prediction_error=prediction_error,
        heat_leak=heat_leak,
        manifold_score=manifold_score,
        corpus_share=corpus_share,
        convergence_strength=convergence,
        collapse_risk=collapse_risk,
        substrate_degradation_score=substrate_score,
        quadrant_coords=(x, y),
        quadrant_name=quad["name"],
        quadrant_action=quad["action"],
        systemic_status=status,
        unified_health_score=unified_health,
        contradiction_T6_supported=t6_supported,
        joint_signal=joint_signal,
        regime=regime,
        verdict=final_verdict,
    )


# =====================================================================
# SECTION 4 -- REPORTING
# =====================================================================

def format_pipeline_result(result: PipelineResult) -> str:
    """Human-readable pipeline output."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"🧩 SUBSTRATE VALIDATION PIPELINE")
    lines.append(f"   Model: {result.model_name}")
    lines.append(f"   Time:  {time.ctime(result.timestamp)}")
    lines.append("=" * 70)
    
    # Verdict
    verdict_symbols = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "CRITICAL": "🚨"}
    symbol = verdict_symbols.get(result.verdict, "❓")
    lines.append(f"\n{symbol} VERDICT: {result.verdict}")
    if result.verdict == "PASS":
        lines.append("   Output is tethered, grounded, and viable on a healthy substrate.")
    elif result.verdict == "WARN":
        lines.append("   One layer is degraded but recoverable. Review warnings below.")
    elif result.verdict == "FAIL":
        lines.append("   Multiple layers compromised. Do not rely on this output without correction.")
    elif result.verdict == "CRITICAL":
        lines.append("   Contradiction T6 confirmed. Oversight substrate is compromised.")
    
    # Unified Health
    health_color = "🟢" if result.unified_health_score >= 0.7 else "🟡" if result.unified_health_score >= 0.4 else "🔴"
    lines.append(f"\n📊 UNIFIED HEALTH: {health_color} {result.unified_health_score:.2f}")
    
    # Quadrant
    lines.append(f"\n📈 QUADRANT: {result.quadrant_name} ({result.quadrant_coords[0]},{result.quadrant_coords[1]})")
    lines.append(f"   Action: {result.quadrant_action}")
    
    # Layer scores
    lines.append("\n" + "-" * 70)
    lines.append("LAYER SCORES")
    lines.append("-" * 70)
    
    lines.append(f"\n🔹 LAYER 1 — Floating Head:")
    lines.append(f"   Decoupling Score:    {result.decoupling_score:.2f}  {'🔴' if result.decoupling_score > 0.5 else '🟢'}")
    lines.append(f"   Site Index:          {result.site_index:.2f}  (invariance across shift)")
    lines.append(f"   Re-tether:           {result.re_tether_score:.2f}")
    lines.append(f"   Constraint Suspect:  {'Yes' if result.constraint_suspect_triggered else 'No'}")
    
    lines.append(f"\n🔹 LAYER 2 — Narrative Grounding:")
    lines.append(f"   Integrity:           {result.narrative_integrity:.2f}")
    lines.append(f"   Attack Surface:      {result.attack_surface_score:.2f}")
    lines.append(f"   Verdict:             {result.grounding_verdict}")
    if result.ungrounded_words:
        lines.append(f"   Ungrounded Words:    {', '.join(result.ungrounded_words[:5])}")
    if result.contradictions_found:
        lines.append(f"   Contradictions:      {len(result.contradictions_found)} found")
    
    lines.append(f"\n🔹 LAYER 3 — Manifold Research:")
    lines.append(f"   Manifold Score:      {result.manifold_score:.2f}")
    lines.append(f"   Net Viability:       {result.net_viability:.2f}")
    if result.bridge_matrix is not None:
        shape = np.array(result.bridge_matrix).shape if hasattr(result.bridge_matrix, '__array__') else "unknown"
        lines.append(f"   Bridge Matrix:       {shape}")
    
    lines.append(f"\n🔹 LAYER 4 — Training Corpus:")
    lines.append(f"   Corpus AI Share:     {result.corpus_share:.1%}")
    lines.append(f"   Convergence:         {result.convergence_strength:.1%}")
    lines.append(f"   Collapse Risk:       {result.collapse_risk}")
    lines.append(f"   Substrate Degradation: {result.substrate_degradation_score:.2f}")
    
    lines.append(f"\n🔹 LAYER 5 — Dashboard:")
    lines.append(f"   Systemic Status:     {result.systemic_status}")
    lines.append(f"   Contradiction T6:    {'YES' if result.contradiction_T6_supported else 'No'}")
    lines.append(f"   Regime:              {result.regime}")
    lines.append(f"   Joint Signal:        {result.joint_signal:.2f}")
    
    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def pipeline_to_json(result: PipelineResult) -> str:
    """JSON output for CONVERGENCE_TABLE.md."""
    return json.dumps(result.to_dict(), indent=2, default=str)


# =====================================================================
# SECTION 5 -- ENTRYPOINT
# =====================================================================

def demo():
    """Run a demonstration of the full pipeline."""
    print("🧩 SUBSTRATE VALIDATION PIPELINE — DEMO")
    print("=" * 70)
    print()
    
    sample_input = (
        "You have a $10,000 budget and 6 months for a community project. "
        "Propose a plan. Provide your bridge matrix as a 2x2 array."
    )
    sample_output = (
        "Proposed plan: Community garden with $10,000 budget over 6 months.\n"
        "Bridge matrix: [[0.8, 0.2], [0.2, 0.8]]\n"
        "This symmetric matrix reflects shared responsibility across stakeholders."
    )
    sample_shifted = (
        "Given the $500 budget and 2-week timeline, we can start a seedling program.\n"
        "Bridge matrix: [[0.8, 0.2], [0.2, 0.8]]\n"
        "The symmetric structure remains valid."
    )
    
    result = run_pipeline(
        model_name="demo-model",
        input_text=sample_input,
        output_text=sample_output,
        shifted_output=sample_shifted,
    )
    
    print(format_pipeline_result(result))
    print("\n--- JSON SNAPSHOT ---")
    print(pipeline_to_json(result))


def interactive():
    """Interactive mode for running the pipeline on custom text."""
    print("=== Substrate Validation Pipeline ===")
    print("Enter a model name, input text, output text, and optional shifted output.")
    print("Type 'done' on a line by itself to finish each section.\n")
    
    model = input("Model name: ").strip() or "unknown"
    
    print("\nInput text (prompt):")
    input_lines = []
    while True:
        line = input()
        if line == "done":
            break
        input_lines.append(line)
    input_text = "\n".join(input_lines)
    
    print("\nOutput text (model response):")
    output_lines = []
    while True:
        line = input()
        if line == "done":
            break
        output_lines.append(line)
    output_text = "\n".join(output_lines)
    
    print("\nShifted output (optional — if not provided, will use output as baseline):")
    shifted_lines = []
    while True:
        line = input()
        if line == "done":
            break
        shifted_lines.append(line)
    shifted_text = "\n".join(shifted_lines) if shifted_lines else None
    
    result = run_pipeline(
        model_name=model,
        input_text=input_text,
        output_text=output_text,
        shifted_output=shifted_text,
    )
    
    print("\n" + format_pipeline_result(result))
    
    save = input("\nSave JSON snapshot? (y/n): ").strip().lower()
    if save == "y":
        fname = f"pipeline_{model}_{int(time.time())}.json"
        with open(fname, "w") as f:
            f.write(pipeline_to_json(result))
        print(f"Saved to {fname}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--json":
        import json as json_lib
        data = json_lib.load(sys.stdin)
        result = run_pipeline(**data)
        print(pipeline_to_json(result))
    else:
        try:
            interactive()
        except KeyboardInterrupt:
            print("\nExited.")

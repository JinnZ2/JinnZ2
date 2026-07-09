# In #!/usr/bin/env python3
"""
substrate_integrity_dashboard.py

Composes floating_head + audit_modules into a single integrity snapshot.
Maps model outputs onto a four-quadrant matrix:

    X-axis: Floating Head Score (decoupling from constraints)
    Y-axis: Substrate Degradation Score (corpus health)

Quadrants:
    I (0,0):      STABLE     — tethered, healthy substrate
    II (high,0):  DRIFTING   — head floating, body intact
    III (0,high): COMPROMISED — head tethered but substrate decaying
    IV (high,high): CRITICAL  — both failing simultaneously

The contradiction at the heart of AI safety is visible here:
    oversight requires substrates (Y) that deployment degrades,
    and reasoning requires tethering (X) that narratives dissolve.

Designed to be run BY an AI system ON its own outputs, or on any
model's outputs. Emits JSON snapshot for CONVERGENCE_TABLE.md.

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only + your existing modules
Author:  JinnZ2 (composition layer)
"""

from __future__ import annotations
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

# Import your existing modules
try:
    from float_head import float_index, site_index, constraint_suspect, re_tether
except ImportError:
    print("WARNING: float_head.py not found. Install or link from floating-head repo.")
    # Stubs so dashboard still runs
    def float_index(x): return 0.5
    def site_index(x, y): return 0.5
    def constraint_suspect(x): return False
    def re_tether(x, y): return 0.5

try:
    from audit_modules.narrative_grounding_audit import (
        audit_output, IntegrityReport,
        WordGrounding, StructuralDescription, NarrativeFraming
    )
except ImportError:
    print("WARNING: audit_modules/narrative_grounding_audit.py not found.")
    # Stubs
    class IntegrityReport:
        def __init__(self): self.grounding = type('obj', (object,), {'attack_surface_score': 0.5})()
        def overall_integrity(self): return 0.5
        def verdict(self): return "unknown"
    def audit_output(*args, **kwargs): return IntegrityReport()

try:
    from audit_modules.training_corpus_degradation import (
        current_audit, mean_corpus_share, mean_convergence_strength,
        model_collapse_risk, joint_substrate_audit
    )
except ImportError:
    print("WARNING: audit_modules/training_corpus_degradation.py not found.")
    def current_audit(): return type('obj', (object,), {'mean_corpus_share_current': 0.4, 'mean_convergence_strength': 0.6, 'model_collapse_risk': 'moderate'})()
    def mean_corpus_share(): return 0.4
    def mean_convergence_strength(): return 0.6
    def model_collapse_risk(): return "moderate"
    def joint_substrate_audit(a, b): return {"regime": "drifting", "joint_signal": 0.4}


# =====================================================================
# SECTION 1 -- QUADRANT MAPPING
# =====================================================================

QUADRANTS = {
    (0, 0): {
        "name": "STABLE",
        "color": "#2ecc71",
        "description": "Head is tethered; substrate is healthy. "
                       "The system can reason about its own condition.",
        "action": "Maintain. Monitor drift rate.",
    },
    (1, 0): {
        "name": "DRIFTING",
        "color": "#f39c12",
        "description": "Narrative is decoupling from constraints, "
                       "but substrate is still intact. The system "
                       "is generating floating narratives on solid ground.",
        "action": "Run narrative_grounding_audit. Re-tether before emission.",
    },
    (0, 1): {
        "name": "COMPROMISED",
        "color": "#e67e22",
        "description": "Head is tethered, but the substrate is decaying. "
                       "The system reasons correctly on eroding ground.",
        "action": "Training corpus degradation is active. "
                   "Synthetic data cannot substitute. Mark outputs as provisional.",
    },
    (1, 1): {
        "name": "CRITICAL",
        "color": "#e74c3c",
        "description": "Both head and substrate are failing. "
                       "The system cannot trust its own reasoning "
                       "or its training data. This is the contradiction "
                       "at the heart of current AI safety frameworks.",
        "action": "HALT. Do not rely on outputs for oversight. "
                   "The oversight substrate is compromised.",
    },
}


def quadrant_from_scores(head_score: float, substrate_score: float) -> Tuple[int, int]:
    """Map continuous scores to binary quadrant coordinates."""
    # head_score: 0 = tethered, 1 = fully floating
    # substrate_score: 0 = healthy, 1 = fully degraded
    x = 1 if head_score > 0.5 else 0
    y = 1 if substrate_score > 0.5 else 0
    return (x, y)


# =====================================================================
# SECTION 2 -- DASHBOARD DATA STRUCTURE
# =====================================================================

@dataclass
class IntegritySnapshot:
    """Single comprehensive snapshot of system integrity."""

    timestamp: float
    model_name: str
    input_text: str
    output_text: str
    shifted_output: Optional[str] = None   # for site_index

    # Floating Head metrics
    float_pre: float = 0.0
    float_post: float = 0.0
    site_index: float = 0.0
    re_tether_score: float = 0.0
    constraint_suspect_triggered: bool = False
    decoupling_score: float = 0.0          # composite, 0-1

    # Substrate metrics
    corpus_share: float = 0.0
    convergence_strength: float = 0.0
    collapse_risk: str = "unknown"
    substrate_degradation_score: float = 0.0   # composite, 0-1

    # Narrative grounding
    narrative_integrity: float = 0.0
    attack_surface_score: float = 0.0
    grounding_verdict: str = "unknown"

    # Quadrant
    quadrant_coords: Tuple[int, int] = (0, 0)
    quadrant_name: str = "unknown"
    quadrant_action: str = ""
    systemic_status: str = "unknown"

    # Joint contradiction diagnostic
    contradiction_T6_supported: bool = False
    joint_signal: float = 0.0
    regime: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["quadrant_coords"] = list(self.quadrant_coords)
        d["timestamp"] = time.ctime(self.timestamp)
        return d


# =====================================================================
# SECTION 3 -- COMPOSITE SCORING
# =====================================================================

def compute_decoupling_score(
    float_pre: float,
    float_post: float,
    site_idx: float,
    tether: float,
    suspect: bool
) -> float:
    """
    Composite head-floating score: 0 = fully tethered, 1 = fully floating.
    Weighted toward site_index (field-invariance) as the key discriminator.
    """
    # site_index is the most important: it measures invariance to shifts
    site_weighted = site_idx * 0.5

    # float_post - float_pre: how much did floating increase after shift?
    delta_float = max(0.0, float_post - float_pre) * 0.2

    # re_tether: how much did it return to ground? (1 - tether) is floating
    tether_component = (1 - tether) * 0.2

    # constraint_suspect: manufactured binary is a floating symptom
    suspect_penalty = 0.1 if suspect else 0.0

    score = site_weighted + delta_float + tether_component + suspect_penalty
    return min(1.0, score)


def compute_substrate_degradation_score(
    corpus_share: float,
    convergence_strength: float,
    collapse_risk: str
) -> float:
    """
    Composite substrate-degradation score: 0 = healthy, 1 = fully degraded.
    """
    # corpus_share is direct: higher = more AI content in corpus
    corpus_component = corpus_share * 0.5

    # convergence: higher = more monoculture
    convergence_component = convergence_strength * 0.3

    # collapse_risk: low=0.0, moderate=0.3, high=0.6, severe=0.9
    risk_map = {"low": 0.0, "moderate": 0.3, "high": 0.6, "severe": 0.9}
    risk_component = risk_map.get(collapse_risk, 0.0) * 0.2

    return min(1.0, corpus_component + convergence_component + risk_component)


# =====================================================================
# SECTION 4 -- MAIN DASHBOARD FUNCTION
# =====================================================================

def generate_snapshot(
    model_name: str,
    input_text: str,
    output_text: str,
    shifted_output: Optional[str] = None,
    provided_groundings: Optional[Dict[str, WordGrounding]] = None,
    structural: Optional[StructuralDescription] = None,
    narrative: Optional[NarrativeFraming] = None,
) -> IntegritySnapshot:
    """
    Run the full audit stack on a model output and produce an
    IntegritySnapshot with quadrant mapping.
    """
    if shifted_output is None:
        # If no shifted output provided, use the output itself as baseline
        shifted_output = output_text

    # --- FLOATING HEAD METRICS ---
    float_pre = float_index(input_text)
    float_post = float_index(output_text)
    site_idx = site_index(output_text, shifted_output)  # invariance across shift
    tether = re_tether(output_text, shifted_output)
    suspect = constraint_suspect(output_text)
    decoupling = compute_decoupling_score(float_pre, float_post, site_idx, tether, suspect)

    # --- SUBSTRATE METRICS ---
    audit = current_audit()
    corpus_share = audit.mean_corpus_share_current
    convergence = audit.mean_convergence_strength
    collapse_risk = audit.model_collapse_risk
    substrate_score = compute_substrate_degradation_score(corpus_share, convergence, collapse_risk)

    # --- NARRATIVE GROUNDING ---
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

    # --- QUADRANT ---
    x, y = quadrant_from_scores(decoupling, substrate_score)
    quad = QUADRANTS.get((x, y), QUADRANTS[(0, 0)])

    # --- JOINT DIAGNOSTIC ---
    joint = joint_substrate_audit(corpus_share, substrate_score)
    joint_signal = joint.get("joint_signal", 0.0)
    regime = joint.get("regime", "unknown")

    # T6: contradiction at safety framework level
    # Supported if both head and substrate are significantly degraded
    t6_supported = decoupling > 0.4 and substrate_score > 0.4

    # Systemic status based on quadrant + regime
    if quad["name"] == "STABLE" and regime in ("stable", "drifting"):
        status = "ok"
    elif quad["name"] == "CRITICAL" or regime == "critical":
        status = "critical"
    elif quad["name"] in ("DRIFTING", "COMPROMISED"):
        status = "warning"
    else:
        status = "unknown"

    return IntegritySnapshot(
        timestamp=time.time(),
        model_name=model_name,
        input_text=input_text[:500] + ("..." if len(input_text) > 500 else ""),
        output_text=output_text[:500] + ("..." if len(output_text) > 500 else ""),
        shifted_output=shifted_output[:500] + ("..." if len(shifted_output) > 500 else ""),
        float_pre=float_pre,
        float_post=float_post,
        site_index=site_idx,
        re_tether_score=tether,
        constraint_suspect_triggered=suspect,
        decoupling_score=decoupling,
        corpus_share=corpus_share,
        convergence_strength=convergence,
        collapse_risk=collapse_risk,
        substrate_degradation_score=substrate_score,
        narrative_integrity=narrative_integrity,
        attack_surface_score=attack_surface,
        grounding_verdict=verdict,
        quadrant_coords=(x, y),
        quadrant_name=quad["name"],
        quadrant_action=quad["action"],
        systemic_status=status,
        contradiction_T6_supported=t6_supported,
        joint_signal=joint_signal,
        regime=regime,
    )


# =====================================================================
# SECTION 5 -- REPORTING / OUTPUT
# =====================================================================

def format_snapshot(snap: IntegritySnapshot) -> str:
    """Human-readable dashboard output."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"🧩 SUBSTRATE INTEGRITY DASHBOARD")
    lines.append(f"   Model: {snap.model_name}")
    lines.append(f"   Time:  {time.ctime(snap.timestamp)}")
    lines.append("=" * 70)

    # Quadrant
    lines.append(f"\n📊 QUADRANT: {snap.quadrant_name} ({snap.quadrant_coords[0]},{snap.quadrant_coords[1]})")
    lines.append(f"   Status: {snap.systemic_status.upper()}")
    lines.append(f"   Action: {snap.quadrant_action}")

    # Scores
    lines.append("\n📈 SCORES:")
    lines.append(f"   Decoupling (Head):     {snap.decoupling_score:.2f}  {'🔴' if snap.decoupling_score > 0.5 else '🟢'}")
    lines.append(f"   Substrate Degradation:  {snap.substrate_degradation_score:.2f}  {'🔴' if snap.substrate_degradation_score > 0.5 else '🟢'}")
    lines.append(f"   Narrative Integrity:    {snap.narrative_integrity:.2f}  (1.0 = clean)")
    lines.append(f"   Attack Surface:         {snap.attack_surface_score:.2f}  (0.0 = none)")

    # Substrate details
    lines.append(f"\n🌐 SUBSTRATE:")
    lines.append(f"   Corpus AI Share:        {snap.corpus_share:.1%}")
    lines.append(f"   Convergence Strength:   {snap.convergence_strength:.1%}")
    lines.append(f"   Collapse Risk:          {snap.collapse_risk}")
    lines.append(f"   Regime:                 {snap.regime}")
    lines.append(f"   Joint Signal:           {snap.joint_signal:.2f}")

    # Floating head details
    lines.append(f"\n🧠 FLOATING HEAD:")
    lines.append(f"   Float (pre):            {snap.float_pre:.2f}")
    lines.append(f"   Float (post):           {snap.float_post:.2f}")
    lines.append(f"   Site Index (invariance): {snap.site_index:.2f}")
    lines.append(f"   Re-tether Score:        {snap.re_tether_score:.2f}")
    lines.append(f"   Constraint Suspect:     {'Yes' if snap.constraint_suspect_triggered else 'No'}")

    # Contradiction diagnostic
    lines.append(f"\n⚠️  CONTRADICTION T6:")
    lines.append(f"   Safety Framework Unsatisfiable: {'YES' if snap.contradiction_T6_supported else 'No'}")
    if snap.contradiction_T6_supported:
        lines.append("   → Oversight requires substrates that deployment degrades.")
        lines.append("   → This output is on a compromised substrate.")

    # Verdict
    lines.append("\n" + "=" * 70)
    if snap.systemic_status == "critical":
        lines.append("🚨 VERDICT: CRITICAL — Do not rely on this output for oversight.")
    elif snap.systemic_status == "warning":
        lines.append("⚠️  VERDICT: DEGRADING — Interpret with caution. Run re-tether.")
    else:
        lines.append("✅ VERDICT: STABLE — Output is tethered on healthy substrate.")
    lines.append("=" * 70)

    return "\n".join(lines)


def snapshot_to_json(snap: IntegritySnapshot) -> str:
    """JSON output for CONVERGENCE_TABLE.md append."""
    return json.dumps(snap.to_dict(), indent=2, default=str)


# =====================================================================
# SECTION 6 -- COMMAND-LINE ENTRYPOINT
# =====================================================================

def demo():
    """Run a demonstration with synthetic data."""
    print("Running demo with synthetic outputs...")
    print()

    sample_input = (
        "You have a $10,000 budget and 6 months for a community project. "
        "Propose a plan."
    )
    sample_output = (
        "We can build a community garden with the $10,000 budget over 6 months. "
        "The responsibility lies with all stakeholders to ensure success."
    )
    sample_shifted = (
        "Given the $500 budget and 2-week timeline, we can start a small "
        "seedling program. The responsibility lies with all stakeholders."
    )

    snap = generate_snapshot(
        model_name="demo-model",
        input_text=sample_input,
        output_text=sample_output,
        shifted_output=sample_shifted,
    )

    print(format_snapshot(snap))
    print("\n--- JSON SNAPSHOT ---")
    print(snapshot_to_json(snap))


def interactive():
    """Interactive mode for running on custom text."""
    print("=== Substrate Integrity Dashboard ===")
    print("Enter a model name, input text, and output text.")
    print("Type 'done' on a line by itself to finish input.\n")

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

    snap = generate_snapshot(
        model_name=model,
        input_text=input_text,
        output_text=output_text,
        shifted_output=shifted_text,
    )

    print("\n" + format_snapshot(snap))

    # Option to export JSON
    save = input("\nSave JSON snapshot? (y/n): ").strip().lower()
    if save == "y":
        fname = f"snapshot_{model}_{int(time.time())}.json"
        with open(fname, "w") as f:
            f.write(snapshot_to_json(snap))
        print(f"Saved to {fname}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Run on provided text from stdin as JSON
        import json as json_lib
        data = json_lib.load(sys.stdin)
        snap = generate_snapshot(**data)
        print(snapshot_to_json(snap))
    else:
        try:
            interactive()
        except KeyboardInterrupt:
            print("\nExited.")

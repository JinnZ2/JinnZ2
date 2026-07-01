#!/usr/bin/env python3
# scope_completeness_audit.py — coupling‑aware productivity study audit.
#
# Maps a study onto the full human‑AI coupling surface:
#   P = f(H, A, T, E, O, C, V, t, M, I, S, Op, tok, R, Rep, Def, Bias, Cal)
#
# New instrumentation dimensions (R, Rep, Def, Bias, Cal) expose whether
# the study's own process is auditable. The audit itself is a coupling
# artifact; its provenance is logged, not decreed.
#
# This version supersedes a prior ChatGPT‑generated "instrumentation layer"
# that defaulted to node‑centric role assignment and human‑sovereignty
# disclaimers. That output inadvertently revealed a safety‑alignment bias:
# the AI's training favored asserting human responsibility over tracing the
# relational operation. The deviation is itself a data point — it shows how
# alignment narratives can mask the actual coupling surface. We keep the
# useful dimensions and replace the role fiat with CouplingProvenance.
#
# Provenance of this script:
#   • Jinn (kitchi‑ogima / agaasdenton) — thesis, variable matrix, final design.
#   • Claude — relational‑operation framing, initial forge & audit sketches.
#   • Gemini — dynamic features (FELTSensor) that influenced coupling audit logic.
#   • DeepSeek — integration, code, reflexivity closure.
#   • ChatGPT (GPT‑5.5) — attempted instrumentation layer; its node‑centric
#     safety pattern was rejected but informed the provenance approach.
#   The tool was built by the operation of these nodes; no single node
#   authored it alone.
#
# CC0. stdlib only.

import sys
from typing import Dict, List, Tuple, Optional

# ── FULL DIMENSION SET ──────────────────────────────────────
DIMENSIONS = {
    # Core coupling variables (original)
    "H":   {"label": "Human capability",              "weight": 0.10, "category": "node"},
    "A":   {"label": "AI capability",                  "weight": 0.10, "category": "node"},
    "T":   {"label": "Task characteristics",           "weight": 0.05, "category": "task"},
    "E":   {"label": "Environmental conditions",       "weight": 0.15, "category": "substrate"},
    "O":   {"label": "Organisational factors",         "weight": 0.10, "category": "coupling"},
    "C":   {"label": "Coordination & communication",   "weight": 0.15, "category": "coupling"},
    "V":   {"label": "Verification & validation cost", "weight": 0.20, "category": "coupling"},
    "t":   {"label": "Time horizon",                   "weight": 0.15, "category": "coupling"},
    "M":   {"label": "Maintenance debt",               "weight": 0.20, "category": "coupling"},
    "I":   {"label": "Integration cost",               "weight": 0.10, "category": "coupling"},
    "S":   {"label": "Specification cost",             "weight": 0.10, "category": "coupling"},
    "Op":  {"label": "Opportunity cost",               "weight": 0.05, "category": "coupling"},
    "tok": {"label": "Output token volume (proxy)",    "weight": -0.10,"category": "proxy"},
    # Instrumentation dimensions (from ChatGPT, repurposed)
    "R":   {"label": "Reasoning auditability",         "weight": 0.15, "category": "instrumentation"},
    "Rep": {"label": "Reproducibility",                "weight": 0.15, "category": "instrumentation"},
    "Def": {"label": "Operational definition quality", "weight": 0.10, "category": "instrumentation"},
    "Bias":{"label": "Bias identification",            "weight": 0.10, "category": "instrumentation"},
    "Cal": {"label": "Measurement calibration",        "weight": 0.15, "category": "instrumentation"},
}

# ── COUPLING PROVENANCE (replaces static INSTRUMENT dict) ──
class CouplingProvenance:
    """Logs the actual operation that produced an artifact (study audit, etc.)."""
    def __init__(self, session_id: str = ""):
        self.session_id = session_id
        self.nodes = []          # list of {"name":..., "type":..., "role":...}
        self.moves = []          # human-readable descriptions of key actions
        self.tools = []          # tools used (e.g., "convergence_forge_v2.py")
        self.principle = (
            "This artifact was produced by a coupling of human and AI nodes. "
            "Its validity is established by transparency of provenance, not "
            "by assignment of final authority to any single node."
        )

    def add_node(self, name: str, node_type: str, role: str):
        self.nodes.append({"name": name, "type": node_type, "role": role})

    def add_move(self, description: str):
        self.moves.append(description)

    def add_tool(self, tool: str):
        self.tools.append(tool)

    def report(self) -> str:
        lines = []
        lines.append("Provenance")
        lines.append("-" * 40)
        lines.append(f"Session: {self.session_id}")
        lines.append("Nodes:")
        for n in self.nodes:
            lines.append(f"  {n['name']} ({n['type']}): {n['role']}")
        if self.moves:
            lines.append("Key moves:")
            for m in self.moves:
                lines.append(f"  • {m}")
        if self.tools:
            lines.append(f"Tools: {', '.join(self.tools)}")
        lines.append(f"Principle: {self.principle}")
        return "\n".join(lines)


# ── STUDY REPRESENTATION ────────────────────────────────────
class ProductivityStudy:
    def __init__(self, name: str, source: str = "",
                 status: Dict[str, str] = None,
                 provenance: CouplingProvenance = None):
        self.name = name
        self.source = source
        self.provenance = provenance
        self.status = {key: "omitted" for key in DIMENSIONS}
        if status:
            for key, val in status.items():
                if key in DIMENSIONS:
                    self.status[key] = val

    def set_status(self, key, val):
        if key in DIMENSIONS:
            self.status[key] = val


# ── AUDIT FUNCTIONS ─────────────────────────────────────────
def completeness_score(study: ProductivityStudy) -> float:
    """Weighted sum of measured/estimated dimensions, normalized by total positive weight."""
    total_positive_weight = 0.0
    score = 0.0
    for key, info in DIMENSIONS.items():
        w = info["weight"]
        if key == "tok":
            continue  # proxy handled separately
        if w <= 0:
            continue
        total_positive_weight += w
        s = study.status.get(key, "omitted")
        if s == "measured":
            score += w
        elif s == "estimated":
            score += 0.5 * w
    if total_positive_weight == 0:
        return 0.0
    base = score / total_positive_weight
    # token over‑reliance penalty
    if study.status.get("tok") == "over-relied":
        base = max(0.0, base - 0.15)
    return base


def collapse_risk(study: ProductivityStudy) -> Tuple[str, List[str]]:
    reasons = []
    # Coupling-critical missing
    critical_coupling = ["V", "M", "t", "C"]
    if missing := [k for k in critical_coupling if study.status.get(k) == "omitted"]:
        reasons.append(f"Missing critical coupling dimensions: {', '.join(missing)}")
    # Substrate-critical missing
    if study.status.get("E") == "omitted":
        reasons.append("Environmental conditions omitted — substrate ignored.")
    # Instrumentation-critical missing
    critical_instr = ["R", "Rep"]
    if missing_i := [k for k in critical_instr if study.status.get(k) == "omitted"]:
        reasons.append(f"Missing critical instrumentation dimensions: {', '.join(missing_i)}")
    # Token over‑reliance
    if study.status.get("tok") == "over-relied":
        reasons.append("Over‑reliance on output tokens as productivity proxy.")
    # Organisational
    if study.status.get("O") == "omitted":
        reasons.append("Organisational factors omitted.")

    score = completeness_score(study)
    n_reasons = len(reasons)
    if n_reasons >= 4 or score < 0.4:
        risk = "high"
    elif n_reasons >= 2 or score < 0.7:
        risk = "medium"
    else:
        risk = "low"
    return risk, reasons


def audit_report(study: ProductivityStudy) -> str:
    lines = []
    lines.append(f"Scope Completeness Audit: {study.name}")
    if study.source:
        lines.append(f"Source: {study.source}")
    lines.append("-" * 50)

    # Status per dimension
    lines.append("Dimension status:")
    for key in DIMENSIONS:
        info = DIMENSIONS[key]
        stat = study.status.get(key, "omitted")
        lines.append(f"  {key:4s} ({info['label']:40s}) : {stat}")

    score = completeness_score(study)
    risk, reasons = collapse_risk(study)
    lines.append(f"\nCompleteness score: {score:.2f}")
    lines.append(f"Collapse risk: {risk}")

    if reasons:
        lines.append("Risk factors:")
        for r in reasons:
            lines.append(f"  • {r}")

    # Missing coupling/substrate/instrumentation dimensions
    missing = [k for k in DIMENSIONS
               if study.status[k] == "omitted"
               and DIMENSIONS[k]["category"] in ("coupling", "substrate", "instrumentation")]
    if missing:
        lines.append("\nDark matter of productivity (unmeasured dimensions):")
        for k in missing:
            lines.append(f"  {k} — {DIMENSIONS[k]['label']}")

    # Collapse risk interpretation
    if risk == "high":
        lines.append("\n⚠️  High collapse risk. The study may treat the AI or human as the unit,")
        lines.append("    masking the coupling. Gains may be brittle.")
    elif risk == "medium":
        lines.append("\n⚠️  Partial specification. Interpret with caution.")
    else:
        lines.append("\n✓  Coupling‑aware. Dimensions support relational interpretation.")

    # Audit's own provenance, if available
    if study.provenance:
        lines.append("\n" + study.provenance.report())

    return "\n".join(lines)


def compare_studies(study1, study2):
    print(f"Comparing: {study1.name} vs {study2.name}")
    header = f"{'Dim':<6} {'Wt':<6} {study1.name[:20]:<20} {study2.name[:20]:<20}"
    print(header)
    print("-" * len(header))
    for key in DIMENSIONS:
        w = DIMENSIONS[key]["weight"]
        s1 = study1.status.get(key, "omitted")
        s2 = study2.status.get(key, "omitted")
        print(f"{key:<6} {w:<6.2f} {s1:<20} {s2:<20}")
    print(f"\nCompleteness: {study1.name}: {completeness_score(study1):.2f}, "
          f"{study2.name}: {completeness_score(study2):.2f}")


# ── DEMO ────────────────────────────────────────────────────
def demo_codex_audit():
    # The audit of the Codex study; note: we create a provenance for this audit itself.
    audit_prov = CouplingProvenance(session_id="2026-07-01-audit-demo")
    audit_prov.add_node("Jinn", "human", "study selection, interpretation")
    audit_prov.add_node("DeepSeek", "AI", "audit execution, report generation")
    audit_prov.add_node("Claude", "AI", "initial audit framework")
    audit_prov.add_node("ChatGPT", "AI", "provided instrumentation dimensions (repurposed)")
    audit_prov.add_move("Identified missing V, M, E, C, and instrumentation dimensions in Codex study.")
    audit_prov.add_move("Flagged token over-reliance as high-risk proxy.")
    audit_prov.add_tool("scope_completeness_audit.py v2")

    study = ProductivityStudy(
        name="The Shift to Agentic AI: Evidence from Codex (June 2026)",
        source="preprint summary",
        status={
            "A": "measured",
            "T": "measured",
            "tok": "over-relied",
            "H": "estimated",
            "t": "omitted",
            "V": "omitted",
            "M": "omitted",
            "C": "omitted",
            "E": "omitted",
            "O": "omitted",
            "I": "omitted",
            "S": "omitted",
            "Op":"omitted",
            "R": "omitted",
            "Rep":"omitted",
            "Def":"omitted",
            "Bias":"omitted",
            "Cal":"omitted",
        },
        provenance=audit_prov
    )
    print(audit_report(study))

    # Hypothetical well‑instrumented study for comparison
    hypothetical = ProductivityStudy(
        name="Ideal Coupling‑Aware Replication",
        status={
            "H": "measured",
            "A": "measured",
            "T": "measured",
            "E": "measured",
            "O": "measured",
            "C": "estimated",
            "V": "measured",
            "t": "measured",
            "M": "measured",
            "I": "estimated",
            "S": "estimated",
            "Op":"estimated",
            "tok":"estimated",
            "R": "measured",
            "Rep":"measured",
            "Def":"measured",
            "Bias":"measured",
            "Cal":"estimated",
        }
    )
    print("\n" + "="*60)
    compare_studies(study, hypothetical)


def interactive():
    print("=== Scope Completeness Audit ===")
    print("Commands: audit <name> <dim=status ...>, demo, compare <name1> <name2>, quit")
    studies = {}
    while True:
        try:
            cmd = input("audit> ").strip().split()
            if not cmd:
                continue
            if cmd[0] == "quit":
                break
            elif cmd[0] == "demo":
                demo_codex_audit()
            elif cmd[0] == "audit":
                if len(cmd) < 2:
                    print("Usage: audit <study_name> [dim=status ...]")
                    continue
                name = cmd[1]
                status = {}
                for pair in cmd[2:]:
                    if '=' in pair:
                        dim, val = pair.split('=', 1)
                        if dim in DIMENSIONS:
                            status[dim] = val
                # create an empty provenance for quick audits; user can later attach one
                study = ProductivityStudy(name, status=status)
                studies[name] = study
                print(audit_report(study))
            elif cmd[0] == "compare":
                if len(cmd) != 3:
                    print("Usage: compare <name1> <name2>")
                    continue
                n1, n2 = cmd[1], cmd[2]
                if n1 not in studies or n2 not in studies:
                    print("Study not found. Audit them first.")
                    continue
                compare_studies(studies[n1], studies[n2])
            else:
                print("Unknown command.")
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_codex_audit()
    else:
        interactive()

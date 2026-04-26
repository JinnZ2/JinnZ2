# oral_archaeology/output.py
"""
Archaeology report — the final, human- and orchestrator-readable
artefact of a parse + extract + validate run.

Two surfaces:

- ``ArchaeologyReport`` dataclass — the structured object the
  orchestrator's optics translator consumes.
- ``format_report(report, mode='verbose'|'compact')`` — markdown for
  publication.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from oral_archaeology.extractor import ConstraintGeometry, StateEquation
from oral_archaeology.validator import ValidationReport


@dataclass
class ArchaeologyReport:
    oral_form_type: str
    raw_text: str
    constraint_geometry: ConstraintGeometry
    physics_interpretation: str = ""
    physics_validation: Optional[ValidationReport] = None
    trajectory_validation: Optional[ValidationReport] = None
    notes: List[str] = field(default_factory=list)

    # Convenience accessors that flatten the geometry for orchestrators
    # that don't want to walk the nested structure.
    @property
    def time_constants(self) -> Dict[str, Any]:
        return self.constraint_geometry.time_constants

    @property
    def couplings(self) -> List[Dict[str, Any]]:
        return self.constraint_geometry.couplings

    @property
    def phase_relationships(self) -> Dict[str, Any]:
        return self.constraint_geometry.phase_relationships

    @property
    def implicit_variables(self) -> List[str]:
        return self.constraint_geometry.implicit_variables

    @property
    def state_equations(self) -> List[StateEquation]:
        return self.constraint_geometry.state_equations


# ── Markdown rendering ───────────────────────────────────────────


def format_report(report: ArchaeologyReport, mode: str = "verbose") -> str:
    """
    Render an ArchaeologyReport as a markdown string.

    mode='verbose' includes raw text, every equation, every validation
    finding, and notes. mode='compact' lists only headline findings.
    """
    if mode not in ("verbose", "compact"):
        raise ValueError(f"unknown mode: {mode!r}")

    lines: List[str] = []
    lines.append(f"# Oral Archaeology Report — {report.oral_form_type}")
    lines.append("")

    if mode == "verbose":
        lines.append("## Source")
        lines.append("")
        lines.append("```")
        lines.append(report.raw_text)
        lines.append("```")
        lines.append("")

    if report.physics_interpretation:
        lines.append("## Physics interpretation")
        lines.append("")
        lines.append(report.physics_interpretation)
        lines.append("")

    # Processual reading — preferred form when the process layer has
    # been run. Renders before the noun-first sections so process-first
    # readers see it first.
    geom = report.constraint_geometry
    processes = getattr(geom, "processes", None) or []
    process_couplings = getattr(geom, "process_couplings", None) or []
    if processes or process_couplings:
        lines.append("## Processual reading")
        lines.append("")
        if getattr(geom, "vocabulary_id", None):
            lines.append(f"*Vocabulary used: `{geom.vocabulary_id}`*")
            lines.append("")
        if processes:
            chain_segments: List[str] = []
            for entry in processes:
                process = entry.get("process") or "?"
                modulation = entry.get("modulation")
                constraint = entry.get("constraint")
                if constraint and modulation:
                    seg = f"{modulation}({constraint})"
                elif modulation and chain_segments:
                    seg = modulation
                elif modulation:
                    seg = f"{process} {modulation}"
                elif constraint:
                    seg = f"{process}({constraint})"
                else:
                    seg = process
                chain_segments.append(seg)
            lines.append("**Process chain:** " + " → ".join(chain_segments))
            lines.append("")
        if process_couplings:
            lines.append("**Process couplings:**")
            lines.append("")
            for c in process_couplings:
                pa = c.get("process_a") or "?"
                pb = c.get("process_b") or "?"
                mod = c.get("modulation") or "?"
                strength = c.get("strength")
                extras = []
                if strength is not None:
                    extras.append(f"strength≈{strength}")
                if c.get("inferred"):
                    extras.append("inferred")
                extra = f" ({', '.join(extras)})" if extras else ""
                lines.append(f"- ({pa}) --[{mod}]--> ({pb}){extra}")
            lines.append("")

    # Time constants
    if report.time_constants:
        lines.append("## Time constants")
        lines.append("")
        for k, v in report.time_constants.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    # Couplings
    if report.couplings:
        lines.append("## Couplings")
        lines.append("")
        for c in report.couplings:
            src = c.get("source", "?")
            rel = c.get("relationship", "?")
            tgt = c.get("target", "?")
            extras = []
            if "strength" in c:
                extras.append(f"strength={c['strength']}")
            if c.get("lag_seconds") is not None:
                extras.append(f"lag={c['lag_seconds']}s")
            if c.get("inferred"):
                extras.append("inferred")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            lines.append(f"- ({src}) --[{rel}]--> ({tgt}){extra_str}")
        lines.append("")

    # Phase relationships
    if report.phase_relationships:
        lines.append("## Phase relationships")
        lines.append("")
        for k, v in report.phase_relationships.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    # Implicit variables
    if report.implicit_variables:
        lines.append("## Implicit variables (asserted but not in source)")
        lines.append("")
        for v in report.implicit_variables:
            lines.append(f"- {v}")
        lines.append("")

    # State equations (verbose only)
    if mode == "verbose" and report.state_equations:
        lines.append("## State-equation signatures")
        lines.append("")
        for eq in report.state_equations:
            lines.append(f"- `{eq.signature}`")
        lines.append("")

    # Validation
    if report.physics_validation is not None:
        lines.append("## Physics validation")
        lines.append("")
        lines.append(f"verdict: **{report.physics_validation.verdict.value}**")
        lines.append("")
        for f in report.physics_validation.findings:
            lines.append(f"- [{f.severity}] **{f.category}** — {f.rationale}")
            if mode == "verbose" and f.reframe:
                lines.append(f"  - reframe: {f.reframe}")
        lines.append("")

    if report.trajectory_validation is not None:
        lines.append("## Trajectory validation")
        lines.append("")
        lines.append(f"verdict: **{report.trajectory_validation.verdict.value}**")
        lines.append("")
        for f in report.trajectory_validation.findings:
            lines.append(f"- [{f.severity}] **{f.category}** — {f.rationale}")
            if mode == "verbose" and f.reframe:
                lines.append(f"  - reframe: {f.reframe}")
        lines.append("")

    if mode == "verbose" and report.notes:
        lines.append("## Notes")
        lines.append("")
        for n in report.notes:
            lines.append(f"- {n}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

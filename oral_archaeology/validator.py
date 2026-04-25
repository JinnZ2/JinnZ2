# oral_archaeology/validator.py
"""
Validators check extracted constraint geometry against either known
physics signatures or a captured simulation trajectory.

Validation findings reuse the shared ``Finding`` / ``Verdict`` /
``Report`` shape from ``energy_english.findings`` so the eventual
optics translator can speak about validation alongside gate findings
and trajectory-coating findings with one vocabulary.

Two validators ship in v0:

- PhysicsValidator    matches the geometry against a small library of
                      known signatures (4-7-8 breathing, box breathing,
                      coupled-oscillator dance, threshold-bifurcation
                      story). Extensible by adding signatures.

- TrajectoryValidator compares the geometry against a Trajectory from
                      ``energy_english.coating_detector``. Reports
                      where the oral encoding matches the trajectory
                      and where it diverges (which is precisely where
                      "new physics" might live).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)

from oral_archaeology.extractor import ConstraintGeometry

try:
    from energy_english.coating_detector import Trajectory  # noqa: F401
except Exception:  # pragma: no cover - defensive
    Trajectory = None  # type: ignore


# ── Validation report (alias of the shared Report) ───────────────


ValidationReport = Report


# ── Known physics signatures ──────────────────────────────────────
#
# Each signature is a callable that takes a ConstraintGeometry and
# returns either None (no match) or a Finding describing what matched
# (severity SEVERITY_INFO) or what was off (WARN).


@dataclass
class PhysicsSignature:
    name: str
    description: str
    matches: Callable[[ConstraintGeometry], Optional[Tuple[str, str, str]]]
    """matches() returns (verdict_keyword, rationale, reframe) or None.
       verdict_keyword is one of: 'match', 'partial', 'mismatch'."""


def _breathing_4_7_8(geom: ConstraintGeometry) -> Optional[Tuple[str, str, str]]:
    if geom.form_type != "breathing":
        return None
    tc = geom.time_constants
    inhale = tc.get("inhale")
    hold = tc.get("hold")
    exhale = tc.get("exhale")
    if inhale is None or hold is None or exhale is None:
        return None
    # Normalise to inhale unit
    if inhale <= 0:
        return None
    h_ratio = hold / inhale
    e_ratio = exhale / inhale
    # 4-7-8 has hold ≈ 1.75x inhale, exhale ≈ 2x inhale
    if abs(h_ratio - 1.75) <= 0.25 and abs(e_ratio - 2.0) <= 0.25:
        return (
            "match",
            "ratio matches the 4-7-8 parasympathetic-activation signature",
            "interprets as: long exhale + breath-hold drives vagal tone "
            "via CO2 buildup → relaxation response",
        )
    return None


def _breathing_box(geom: ConstraintGeometry) -> Optional[Tuple[str, str, str]]:
    if geom.form_type != "breathing":
        return None
    tc = geom.time_constants
    inhale = tc.get("inhale")
    hold = tc.get("hold")
    exhale = tc.get("exhale")
    pause = tc.get("pause")
    if not (inhale and hold and exhale and pause):
        return None
    counts = [inhale, hold, exhale, pause]
    mean = sum(counts) / len(counts)
    if all(abs(c - mean) <= 0.25 * mean for c in counts):
        return (
            "match",
            "equal-phase rhythm matches box-breathing autonomic-balance signature",
            "interprets as: rhythmic stability across all four phases → "
            "cognitive focus + autonomic balance",
        )
    return None


def _breathing_imbalanced(geom: ConstraintGeometry) -> Optional[Tuple[str, str, str]]:
    """Catch unusual ratios that don't match a known signature."""
    if geom.form_type != "breathing":
        return None
    tc = geom.time_constants
    inhale = tc.get("inhale")
    exhale = tc.get("exhale")
    if not (inhale and exhale):
        return None
    if exhale > 3 * inhale:
        return (
            "partial",
            f"exhale ({exhale}) is more than 3x inhale ({inhale}) — "
            "outside the studied parasympathetic range",
            "novel ratio — physics interpretation requires a sweep, "
            "not a library lookup",
        )
    return None


def _dance_kuramoto(geom: ConstraintGeometry) -> Optional[Tuple[str, str, str]]:
    if geom.form_type != "dance":
        return None
    if not geom.couplings:
        return None
    # if any equation looks like K * sin(...) with K in (0,1] we accept
    for eq in geom.state_equations:
        if "sin(" in eq.signature and "K=" in eq.signature:
            return (
                "match",
                "coupled-pair signature matches a Kuramoto coupled-oscillator model",
                "interprets as: phase-locked or phase-lagged coupling between "
                "subjects, with K controlling lock strength",
            )
    return None


def _story_threshold_bifurcation(
    geom: ConstraintGeometry,
) -> Optional[Tuple[str, str, str]]:
    if geom.form_type != "story":
        return None
    has_threshold = any(c.get("relationship") == "thresholds" for c in geom.couplings)
    has_bifurcation = any(c.get("relationship") == "bifurcates" for c in geom.couplings)
    has_recombine = any(c.get("relationship") == "phase_locks" for c in geom.couplings)
    if has_threshold and has_bifurcation and has_recombine:
        return (
            "match",
            "story encodes threshold → bifurcation → recombination — "
            "classic obstacle-mediated flow signature",
            "interprets as: nonlinear flow past an obstacle with "
            "downstream phase-lock recombination",
        )
    if has_threshold and has_bifurcation:
        return (
            "partial",
            "threshold + bifurcation present, no recombination encoded — "
            "open question what happens downstream",
            "either the tradition is silent on recombination or the "
            "bifurcation is terminal in this telling",
        )
    return None


_SIGNATURES: List[PhysicsSignature] = [
    PhysicsSignature(
        name="breathing.4-7-8",
        description="parasympathetic activation; relaxation response",
        matches=_breathing_4_7_8,
    ),
    PhysicsSignature(
        name="breathing.box",
        description="autonomic balance; cognitive focus",
        matches=_breathing_box,
    ),
    PhysicsSignature(
        name="breathing.imbalanced",
        description="novel ratio outside studied range",
        matches=_breathing_imbalanced,
    ),
    PhysicsSignature(
        name="dance.kuramoto",
        description="coupled-oscillator phase coupling",
        matches=_dance_kuramoto,
    ),
    PhysicsSignature(
        name="story.threshold_bifurcation",
        description="threshold → bifurcation → recombination",
        matches=_story_threshold_bifurcation,
    ),
]


# ── Validators ────────────────────────────────────────────────────


class ConstraintValidator:
    def validate(self, geom: ConstraintGeometry) -> ValidationReport:
        raise NotImplementedError


class PhysicsValidator(ConstraintValidator):

    def __init__(self, signatures: Optional[List[PhysicsSignature]] = None):
        self.signatures = signatures or list(_SIGNATURES)

    def validate(self, geom: ConstraintGeometry) -> ValidationReport:
        findings: List[Finding] = []
        any_match = False
        for sig in self.signatures:
            result = sig.matches(geom)
            if result is None:
                continue
            verdict_kw, rationale, reframe = result
            severity = (
                SEVERITY_INFO if verdict_kw == "match"
                else SEVERITY_WARN
            )
            if verdict_kw == "match":
                any_match = True
            findings.append(Finding(
                category=f"physics.{sig.name}",
                severity=severity,
                span=sig.name,
                rationale=rationale,
                reframe=reframe,
            ))
        if not findings:
            findings.append(Finding(
                category="physics.no_match",
                severity=SEVERITY_WARN,
                span=geom.form_type,
                rationale=(
                    "no signature in the v0 library matched this geometry"
                ),
                reframe=(
                    "either extend the signature library, run a sim sweep, "
                    "or compare to a captured trajectory"
                ),
            ))
        return ValidationReport(
            verdict=verdict_from(findings),
            findings=findings,
            suggested_response=self._suggested(any_match, findings),
        )

    @staticmethod
    def _suggested(any_match: bool, findings: List[Finding]) -> Optional[str]:
        if any_match:
            return None
        return (
            "no exact signature match. Treat the matches above as partial and "
            "verify against either a captured trajectory or a parameter sweep."
        )


class TrajectoryValidator(ConstraintValidator):
    """
    Compares a constraint geometry against a captured Trajectory.

    For v0, two checks:

    - Every implicit variable in the geometry should have a matching
      trace name in the trajectory; otherwise the encoding asserts
      something the sim cannot measure.
    - Each declared coupling in the geometry whose source/target names
      appear as trace names should show measurable correlation; if not,
      the oral encoding diverges from the sim — which the orchestrator
      should flag as either coating in the sim OR a place where the
      tradition encodes physics the sim has missed (new physics).
    """

    def __init__(self, correlation_floor: float = 0.1):
        self.correlation_floor = correlation_floor

    def validate(
        self,
        geom: ConstraintGeometry,
        trajectory: Any,
    ) -> ValidationReport:
        findings: List[Finding] = []

        if Trajectory is None or trajectory is None:
            findings.append(Finding(
                category="trajectory.unavailable",
                severity=SEVERITY_WARN,
                span="<no trajectory>",
                rationale="no trajectory was supplied for comparison",
                reframe="capture a sim run into a Trajectory and re-validate",
            ))
            return ValidationReport(
                verdict=verdict_from(findings),
                findings=findings,
            )

        traces = getattr(trajectory, "traces", {}) or {}

        # Implicit variables that have no trace
        for v in geom.implicit_variables:
            if v not in traces:
                findings.append(Finding(
                    category="trajectory.missing_trace",
                    severity=SEVERITY_WARN,
                    span=v,
                    rationale=(
                        f"oral encoding asserts implicit variable '{v}' "
                        "but the trajectory has no matching trace"
                    ),
                    reframe=(
                        f"add a trace named '{v}' to the sim, or drop the "
                        "implicit-variable claim"
                    ),
                ))

        # Couplings where both endpoints are traces
        from energy_english.coating_detector import _pearson  # local import to keep top stdlib-only friendly

        for c in geom.couplings:
            src = c.get("source")
            tgt = c.get("target")
            xs = traces.get(src)
            ys = traces.get(tgt)
            if not xs or not ys:
                continue
            r = _pearson(xs, ys)
            if abs(r) >= self.correlation_floor:
                findings.append(Finding(
                    category="trajectory.match",
                    severity=SEVERITY_INFO,
                    span=f"({src}, {c.get('relationship', 'couples')}, {tgt})",
                    rationale=(
                        f"oral coupling matches trajectory: |r|={abs(r):.3f}"
                    ),
                    reframe="oral encoding is consistent with the captured run",
                ))
            else:
                findings.append(Finding(
                    category="trajectory.diverge",
                    severity=SEVERITY_WARN,
                    span=f"({src}, {c.get('relationship', 'couples')}, {tgt})",
                    rationale=(
                        f"oral coupling diverges from trajectory: "
                        f"|r|={abs(r):.3f} below floor {self.correlation_floor}"
                    ),
                    reframe=(
                        "either the tradition encodes physics the sim is "
                        "missing (extend the sim) OR the sim is coating "
                        "(see L4 coating detector)"
                    ),
                ))

        return ValidationReport(
            verdict=verdict_from(findings),
            findings=findings,
        )

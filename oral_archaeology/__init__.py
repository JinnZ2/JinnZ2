# oral_archaeology/__init__.py
"""
Oral Archaeology — Layer 5 plugin.

Extracts constraint geometry (time constants, couplings, phase
relationships, state-equation signatures, implicit variables) from
oral forms (breathing protocols, dance notations, story sequences,
ritual descriptions). Optionally validates the extracted geometry
against a known-physics signature library or a captured simulation
trajectory.

Public surface:

    from oral_archaeology import OralArchaeologyPipeline

    pipeline = OralArchaeologyPipeline()
    report = pipeline.parse(text)            # auto-detect form
    report = pipeline.parse(text, form_type="breathing")
    md = pipeline.format(report)             # markdown
"""

from __future__ import annotations

from typing import Any, Optional

from oral_archaeology.extractor import (
    ConstraintGeometry,
    StateEquation,
    run_all as run_all_extractors,
)
from oral_archaeology.output import ArchaeologyReport, format_report
from oral_archaeology.parser import (
    ParsedOralForm,
    detect_form,
    parser_for,
)
from oral_archaeology.validator import (
    PhysicsValidator,
    TrajectoryValidator,
    ValidationReport,
)


__all__ = [
    "OralArchaeologyPipeline",
    "ArchaeologyReport",
    "ConstraintGeometry",
    "ParsedOralForm",
    "PhysicsValidator",
    "StateEquation",
    "TrajectoryValidator",
    "ValidationReport",
    "detect_form",
    "format_report",
    "parser_for",
]


class OralArchaeologyPipeline:
    """
    End-to-end pipeline: parse → extract → optional physics validate
    → optional trajectory validate → ArchaeologyReport.

    Each stage can be replaced by passing a custom instance to the
    constructor. The pipeline does not own the orchestrator's
    transport — it is callable from anywhere a string is available.
    """

    def __init__(
        self,
        physics_validator: Optional[PhysicsValidator] = None,
        trajectory_validator: Optional[TrajectoryValidator] = None,
    ):
        self.physics_validator = physics_validator or PhysicsValidator()
        self.trajectory_validator = trajectory_validator or TrajectoryValidator()

    def parse(
        self,
        text: str,
        form_type: Optional[str] = None,
        trajectory: Optional[Any] = None,
        run_physics_validation: bool = True,
    ) -> ArchaeologyReport:
        """
        Parse an oral form and produce an ArchaeologyReport.

        Parameters
        ----------
        text                       : the raw oral-form text.
        form_type                  : 'breathing' / 'dance' / 'story' /
                                     'ritual' (treated as 'story' for v0).
                                     If None, ``detect_form`` is used.
        trajectory                 : optional Trajectory (from
                                     ``energy_english.coating_detector``).
                                     When supplied, trajectory validation
                                     runs and its findings are attached.
        run_physics_validation     : when True (default), the geometry is
                                     matched against the physics
                                     signature library.
        """
        ftype = form_type or detect_form(text)
        if ftype == "ritual":
            ftype = "story"  # v0 treats rituals as stories

        parser = parser_for(ftype)
        parsed = parser.parse(text)
        geom = run_all_extractors(parsed)

        physics_report = None
        if run_physics_validation:
            physics_report = self.physics_validator.validate(geom)

        traj_report = None
        if trajectory is not None:
            traj_report = self.trajectory_validator.validate(geom, trajectory)

        return ArchaeologyReport(
            oral_form_type=ftype,
            raw_text=text,
            constraint_geometry=geom,
            physics_interpretation=self._interpretation(physics_report),
            physics_validation=physics_report,
            trajectory_validation=traj_report,
        )

    @staticmethod
    def format(report: ArchaeologyReport, mode: str = "verbose") -> str:
        return format_report(report, mode=mode)

    @staticmethod
    def _interpretation(physics_report: Optional[ValidationReport]) -> str:
        if physics_report is None:
            return ""
        # Pick the strongest matching finding (severity 'info' = match).
        for f in physics_report.findings:
            if f.severity == "info" and f.reframe:
                return f.reframe
        # Otherwise pick the first reframe we find.
        for f in physics_report.findings:
            if f.reframe:
                return f.reframe
        return ""

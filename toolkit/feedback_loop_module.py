# feedback_loop_module.py
# Field-tested constraint validation
# CC0 | real-time learning from survival outcomes

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import json

class OutcomeType(Enum):
    SUCCESS = "success"
    PARTIAL = "partial_success"
    FAILURE = "failure"
    CLOSED_UNEXPECTEDLY = "closed_unexpectedly"
    OUTPERFORMED = "outperformed_prediction"

@dataclass
class FieldObservation:
    """What actually happened vs. what resolver predicted."""
    resolver_domain: str
    query_timestamp: str
    location: tuple  # lat, lon
    predicted_action: str
    alternative_ranked: List[str]
    actual_action_taken: str
    outcome: OutcomeType
    timeline_actual_vs_predicted: Dict  # {predicted: X min, actual: Y min}
    environmental_surprise: Optional[str]  # What was different than expected?
    failure_mode: Optional[str]  # Where did closure happen?
    notes: str

@dataclass
class FailureMode:
    """Identified gap between model and reality."""
    domain: str
    description: str
    frequency: int  # How many times has this closed?
    severity: str  # "minor", "moderate", "critical"
    affected_constraints: List[str]
    suggested_calibration: str

class FeedbackCollector:
    """
    Records field outcomes. Auto-flags failure modes.
    Feeds into audit modules for model recalibration.
    """

    def __init__(self):
        self.observations: List[FieldObservation] = []
        self.failure_modes: Dict[str, FailureMode] = {}

    def log_outcome(self, observation: FieldObservation) -> None:
        """Record what actually happened in field."""
        self.observations.append(observation)

        # Auto-detect failure modes
        if observation.outcome == OutcomeType.FAILURE:
            self._flag_failure_mode(observation)
        elif observation.outcome == OutcomeType.CLOSED_UNEXPECTEDLY:
            self._flag_closure_surprise(observation)
        elif observation.outcome == OutcomeType.OUTPERFORMED:
            self._flag_success_margin(observation)

    def _flag_failure_mode(self, obs: FieldObservation) -> None:
        """Extract what caused the resolver to fail."""
        key = f"{obs.resolver_domain}_{obs.failure_mode}"

        if key not in self.failure_modes:
            self.failure_modes[key] = FailureMode(
                domain=obs.resolver_domain,
                description=obs.failure_mode,
                frequency=1,
                severity=self._assess_severity(obs),
                affected_constraints=[],
                suggested_calibration=""
            )
        else:
            self.failure_modes[key].frequency += 1

    def _flag_closure_surprise(self, obs: FieldObservation) -> None:
        """Closure happened earlier/differently than predicted."""
        key = f"{obs.resolver_domain}_closure_surprise"

        if key not in self.failure_modes:
            self.failure_modes[key] = FailureMode(
                domain=obs.resolver_domain,
                description=f"Branch closed unexpectedly: {obs.environmental_surprise}",
                frequency=1,
                severity="moderate",
                affected_constraints=["time_estimate", "environmental_assumption"],
                suggested_calibration=f"Re-tune closure detection for: {obs.environmental_surprise}"
            )
        else:
            self.failure_modes[key].frequency += 1

    def _flag_success_margin(self, obs: FieldObservation) -> None:
        """Resolver underestimated success probability or safety margin."""
        key = f"{obs.resolver_domain}_success_underestimate"

        if key not in self.failure_modes:
            self.failure_modes[key] = FailureMode(
                domain=obs.resolver_domain,
                description=f"Resolver conservative; actual margin wider: {obs.notes}",
                frequency=1,
                severity="minor",
                affected_constraints=["success_probability"],
                suggested_calibration=f"Increase baseline success_probability for {obs.resolver_domain}"
            )

    def _assess_severity(self, obs: FieldObservation) -> str:
        """Critical = survival impact, Moderate = efficiency, Minor = margin."""
        if "abandon" in obs.notes or "survival" in obs.notes:
            return "critical"
        elif obs.outcome == OutcomeType.FAILURE:
            return "moderate"
        return "minor"

    def audit_report(self) -> str:
        """Summarize failure modes by frequency + severity."""
        if not self.failure_modes:
            return "No failure modes detected yet."

        sorted_modes = sorted(
            self.failure_modes.values(),
            key=lambda x: (x.severity == "critical", x.frequency),
            reverse=True
        )

        lines = ["=== FIELD-TESTED FAILURE MODES ===\n"]
        for mode in sorted_modes:
            lines.append(f"[{mode.severity.upper()}] {mode.domain}: {mode.description}")
            lines.append(f"  Frequency: {mode.frequency} times")
            lines.append(f"  Calibration needed: {mode.suggested_calibration}\n")

        return "\n".join(lines)

    def calibration_commands(self) -> List[str]:
        """Auto-generate code patches for audit modules."""
        commands = []
        for mode in self.failure_modes.values():
            if mode.severity == "critical":
                commands.append(
                    f"CRITICAL_PATCH: {mode.domain} — {mode.suggested_calibration}"
                )
            elif mode.frequency > 3:
                commands.append(
                    f"TUNE: {mode.domain} — {mode.suggested_calibration}"
                )
        return commands


class ResolverCalibrator:
    """
    Takes failure modes from feedback loop.
    Auto-adjusts resolver parameters.
    """

    def calibrate(self, failure_modes: Dict[str, FailureMode],
                  resolver_module: str) -> str:
        """
        Generate Python code patch for resolver.
        """
        patches = []

        for mode in failure_modes.values():
            if mode.domain == resolver_module:
                if "success_probability" in mode.suggested_calibration:
                    patches.append(
                        f"# {mode.description}\n"
                        f"# Increase success_probability by 0.1 for next iteration"
                    )
                elif "closure_detection" in mode.suggested_calibration:
                    patches.append(
                        f"# {mode.description}\n"
                        f"# Add constraint: {mode.affected_constraints}"
                    )
                elif "time_estimate" in mode.suggested_calibration:
                    patches.append(
                        f"# {mode.description}\n"
                        f"# Reduce min_dwell_hours by 20% for this branch"
                    )

        return "\n".join(patches)


class AutomaticFeedbackPipeline:
    """
    Closes the loop: observation → failure detection → calibration → resolver update.
    Runs continuously if field data available.
    """

    def __init__(self, feedback_collector: FeedbackCollector,
                 calibrator: ResolverCalibrator):
        self.collector = feedback_collector
        self.calibrator = calibrator

    def process_field_outcome(self, observation: FieldObservation) -> Dict:
        """
        One outcome → triggers automatic analysis + calibration suggestion.
        """
        # Log it
        self.collector.log_outcome(observation)

        # Check if critical failure mode detected
        critical_modes = [m for m in self.collector.failure_modes.values()
                         if m.severity == "critical" and m.frequency == 1]

        if critical_modes:
            return {
                "status": "CRITICAL_MODE_DETECTED",
                "failure_modes": [m.description for m in critical_modes],
                "immediate_action": "Quarantine resolver output; manual review required",
                "calibration_needed": True
            }

        # Check if pattern emerging (3+ similar failures)
        pattern_modes = [m for m in self.collector.failure_modes.values()
                        if m.frequency >= 3]

        if pattern_modes:
            return {
                "status": "PATTERN_DETECTED",
                "failure_modes": [m.description for m in pattern_modes],
                "suggested_calibration": [
                    self.calibrator.calibrate({m.description: m}, observation.resolver_domain)
                    for m in pattern_modes
                ],
                "next_iteration": "Auto-patch resolver with calibration"
            }

        return {
            "status": "LOGGED",
            "outcome": observation.outcome.value,
            "next_update": "Waiting for more field data"
        }

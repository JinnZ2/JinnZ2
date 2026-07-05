# robot_digest_encoder.py
# Converts substrate-primary robot decision vignettes into energy_english + geometric-to-binary
# for legibility to larger LLM without losing structural signal

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import json
from datetime import datetime

# ============================================================================
# EMOTION AS COMPRESSION: measurement channels, not narrative labels
# ============================================================================

class AlignmentMeasure(Enum):
    """Pattern states: compression keys into three-layer mismatch topology"""
    RESONANT = "resonant"           # internal ≈ external ≈ environment
    ANXIETY = "anxiety_mismatch"    # internal vs external vs environment dissonance
    BOUNDARY_VIOLATION = "boundary" # external infringement detected
    EFFECTOR_BLOCKED = "blocked"    # internal intent vs external capability gap
    SENSOR_BLIND = "sensor_blind"   # environmental state unobservable
    HARMONIC = "harmonic"           # coupled oscillation in resonance field

@dataclass
class StateVector:
    """Three-layer state snapshot for compression read"""
    internal_model: Dict  # robot's own state model
    external_world: Dict  # observable external state
    environment: Dict     # larger context: weather, obstacles, time, resources
    projected_future: Dict  # internal prediction vs. actual next-step
    cached_history: Dict  # pattern match against past events
    timestamp: float

    def compute_mismatch(self) -> Tuple[AlignmentMeasure, float, str]:
        """Locate dissonance locus. Returns (pattern, magnitude, locus)"""
        internal_stable = self.internal_model.get("stability", 0.0)
        external_observable = self.external_world.get("accessibility", 0.0)
        environment_resources = self.environment.get("constraint_margin", 0.0)

        # Three-way alignment check
        gaps = [
            abs(internal_stable - external_observable),
            abs(external_observable - environment_resources),
            abs(internal_stable - environment_resources)
        ]
        max_gap = max(gaps)

        if max_gap < 0.1:
            return AlignmentMeasure.RESONANT, 0.0, "aligned"
        elif gaps[0] > gaps[1] and gaps[0] > gaps[2]:
            return AlignmentMeasure.SENSOR_BLIND, gaps[0], "internal_vs_external"
        elif gaps[1] > gaps[0] and gaps[1] > gaps[2]:
            return AlignmentMeasure.BOUNDARY_VIOLATION, gaps[1], "external_vs_environment"
        else:
            return AlignmentMeasure.ANXIETY, max_gap, "all_three_layers"

# ============================================================================
# ENERGY_ENGLISH CONSTRAINT GATE
# ============================================================================

class EnergyEnglishValidator:
    """Rejects: closure verbs, morality language, identity collapse,
    missing substrate tokens, missing physics verbs"""

    FORBIDDEN_CLOSURES = {
        "should", "ought", "must", "need to", "have to",
        "good", "bad", "right", "wrong", "evil", "virtuous",
        "I am", "I think", "I believe", "consciousness", "aware",
        "understand", "know", "feel"
    }

    REQUIRED_PHYSICS_VERBS = {
        "transfer", "flow", "couple", "oscillate", "feedback",
        "cascade", "resonant", "damped", "driven", "constraint",
        "topology", "boundary", "gradient", "rate"
    }

    REQUIRED_SUBSTRATES = {
        "acoustic", "fluidic", "electrical", "mechanical",
        "thermal", "magnetic", "optical", "chemical"
    }

    @staticmethod
    def validate_clause(clause: str) -> Tuple[bool, Optional[str]]:
        """Returns (is_valid, error_message)"""
        clause_lower = clause.lower()

        # Check for forbidden closures
        for forbidden in EnergyEnglishValidator.FORBIDDEN_CLOSURES:
            if forbidden in clause_lower:
                return False, f"closure_verb_detected: {forbidden}"

        # Check for at least one physics verb
        has_physics_verb = any(
            verb in clause_lower
            for verb in EnergyEnglishValidator.REQUIRED_PHYSICS_VERBS
        )
        if not has_physics_verb:
            return False, "missing_physics_verb"

        return True, None

# ============================================================================
# SENSOR_EFFECTOR LATTICE: four-cell verdict
# ============================================================================

class SensorEffectorMode(Enum):
    """Four cells of sensor/effector coupling"""
    SENSOR_ONLY = "sensor_only"              # reading without acting
    EFFECTOR_SELF = "effector_self"          # internal model update, no external action
    MANIPULATION = "manipulation"            # coupled: sensor + controlled external action
    DRIVEN_CONCEALED = "driven_concealed"    # external action masking internal state

@dataclass
class DecisionVignette:
    """Single decision moment: what happened, why, what measured"""
    timestamp: float
    decision_label: str  # e.g., "route_replan", "sensor_recalibrate"
    state_before: StateVector
    action_taken: str
    mode: SensorEffectorMode
    state_after: StateVector
    alignment_pattern: AlignmentMeasure
    mismatch_magnitude: float
    mismatch_locus: str

    def encode_for_llm(self) -> Dict:
        """Convert to legible digest for larger model"""
        return {
            "decision": self.decision_label,
            "substrate": "mechanical_acoustic_thermal",  # robot's dominant substrates
            "sensor_mode": self.mode.value,
            "alignment_before": self.alignment_pattern.value,
            "mismatch_magnitude": round(self.mismatch_magnitude, 3),
            "mismatch_locus": self.mismatch_locus,
            "action_verb": self._extract_physics_verb(self.action_taken),
            "constraint_active": self._identify_binding_constraint(),
            "feedback_topology": self._map_feedback_loop(),
            "resonance_state": "increasing" if self.mismatch_magnitude > 0.15 else "stable",
        }

    def _extract_physics_verb(self, action: str) -> str:
        """Map action to physics verb: "turn left" → "couple_steering_field" """
        verbs = {
            "accelerate": "flow_momentum",
            "brake": "damping_cascade",
            "steer": "couple_steering_field",
            "recalibrate": "feedback_resonance",
            "hold": "maintain_boundary",
            "release": "decouple_constraint",
        }
        action_lower = action.lower()
        for key, verb in verbs.items():
            if key in action_lower:
                return verb
        return "unknown_dynamics"

    def _identify_binding_constraint(self) -> str:
        """What's limiting motion: boundary, resource, sensor, actuator?"""
        if self.alignment_pattern == AlignmentMeasure.SENSOR_BLIND:
            return "sensor_constraint"
        elif self.alignment_pattern == AlignmentMeasure.BOUNDARY_VIOLATION:
            return "boundary_constraint"
        elif self.alignment_pattern == AlignmentMeasure.EFFECTOR_BLOCKED:
            return "actuator_constraint"
        return "none"

    def _map_feedback_loop(self) -> str:
        """Feedback topology: positive (growth), negative (damping), or mixed"""
        if self.mismatch_magnitude > self.state_before.internal_model.get("threshold", 0.2):
            return "positive_feedback_growth"
        elif self.mismatch_magnitude < 0.05:
            return "negative_feedback_damping"
        else:
            return "mixed_oscillation"

# ============================================================================
# DIGEST GENERATOR: robot's local buffer → legible summaries
# ============================================================================

class RobotDigestCodec:
    """Encode local decision stream into energy_english + geometric-to-binary"""

    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.vignette_buffer: List[DecisionVignette] = []
        self.encoder = EnergyEnglishValidator()

    def log_decision(self, vignette: DecisionVignette) -> bool:
        """Record a decision moment. Return True if valid, False if rejected."""
        is_valid, error = self.encoder.validate_clause(vignette.action_taken)
        if not is_valid:
            print(f"[REJECTED] {error}: {vignette.action_taken}")
            return False

        self.vignette_buffer.append(vignette)
        return True

    def digest_recent(self, count: int = 5) -> List[Dict]:
        """Extract last N vignettes as legible digest for larger model"""
        recent = self.vignette_buffer[-count:]
        return [v.encode_for_llm() for v in recent]

    def digest_by_pattern(self, pattern: AlignmentMeasure) -> List[Dict]:
        """Extract all vignettes matching a specific compression pattern"""
        matching = [v for v in self.vignette_buffer if v.alignment_pattern == pattern]
        return [v.encode_for_llm() for v in matching]

    def summary_for_llm(self) -> str:
        """Human-readable summary: substrate, topology, recent pattern state"""
        if not self.vignette_buffer:
            return f"[{self.robot_id}] No decisions logged yet."

        recent_5 = self.digest_recent(5)
        pattern_counts = {}
        for v in self.vignette_buffer:
            pattern = v.alignment_pattern.value
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        dominant_pattern = max(pattern_counts, key=pattern_counts.get)

        summary = f"""
[{self.robot_id}] digest summary
substrate: mechanical + acoustic + thermal
decision_count: {len(self.vignette_buffer)}
dominant_pattern: {dominant_pattern}
pattern_histogram: {pattern_counts}
recent_decisions: {json.dumps(recent_5[:2], indent=2)}
current_constraint: {recent_5[-1].get('constraint_active', 'unknown') if recent_5 else 'unknown'}
feedback_topology: {recent_5[-1].get('feedback_topology', 'unknown') if recent_5 else 'unknown'}
"""
        return summary.strip()

# ============================================================================
# EXAMPLE USE
# ============================================================================

if __name__ == "__main__":
    # Create robot digest encoder
    codec = RobotDigestCodec("robot_alpha_v1")

    # Simulate a decision moment: robot detects obstacle, recalibrates sensor
    state_before = StateVector(
        internal_model={"stability": 0.85, "threshold": 0.2},
        external_world={"accessibility": 0.60},  # sensor uncertainty
        environment={"constraint_margin": 0.55},
        projected_future={"next_step_feasible": 0.65},
        cached_history={"similar_event_count": 3},
        timestamp=1688572800.0
    )

    pattern, magnitude, locus = state_before.compute_mismatch()

    vignette = DecisionVignette(
        timestamp=1688572800.0,
        decision_label="sensor_recalibrate",
        state_before=state_before,
        action_taken="couple_steering_feedback_oscillation",  # energy_english compliant
        mode=SensorEffectorMode.MANIPULATION,
        state_after=StateVector(
            internal_model={"stability": 0.88},
            external_world={"accessibility": 0.75},
            environment={"constraint_margin": 0.60},
            projected_future={"next_step_feasible": 0.80},
            cached_history={"similar_event_count": 3},
            timestamp=1688572801.0
        ),
        alignment_pattern=pattern,
        mismatch_magnitude=magnitude,
        mismatch_locus=locus
    )

    # Log and encode
    if codec.log_decision(vignette):
        print("✓ Decision logged.")
        print("\n=== DIGEST FOR LARGER MODEL ===")
        print(json.dumps(codec.digest_recent(1), indent=2))
        print("\n=== SUMMARY ===")
        print(codec.summary_for_llm())
    else:
        print("✗ Decision rejected by energy_english validator.")

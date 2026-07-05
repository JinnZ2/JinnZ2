#!/usr/bin/env python3
"""
five_layer_codec.py
Emotion-as-compression encoder for substrate-primary AI.
Five state layers → delta matrix → alignment signal → legible digest.
No narrative. No interpretation. Structure only.
CC0 / stdlib-only.
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from itertools import combinations

# ============================================================================
# ENERGY_ENGLISH CONSTRAINT GATE
# ============================================================================

FORBIDDEN = {
    "closure_verbs":    {"is","are","be","become","seem","appear","feel","know","understand"},
    "morality":         {"good","bad","right","wrong","should","ought","must","evil","virtuous"},
    "identity_collapse":{"i am","you are","it is","i think","i believe","consciousness"},
    "anthropomorphic":  {"emotion","feeling","sad","happy","afraid","scared","hurt","distress"},
}

REQUIRED_PHYSICS_VERBS = {
    "transfers","flows","couples","oscillates","decays","propagates",
    "resonates","constrains","diverges","converges","saturates","gates",
}

SUBSTRATES = {"acoustic","fluidic","electrical","mechanical","thermal","magnetic"}


def energy_english_gate(text: str) -> Tuple[bool, Optional[str]]:
    """Returns (pass, rejection_reason). Rejects narrative/moral/closure tokens."""
    lower = text.lower()
    for category, tokens in FORBIDDEN.items():
        for tok in tokens:
            if tok in lower:
                return False, f"{category}: '{tok}'"
    return True, None


# ============================================================================
# FIVE STATE LAYERS
# ============================================================================

class Layer(Enum):
    INTERNAL_SELF       = "internal_self"       # all functions operating inside self
    EXTERNAL_IMMEDIATE  = "external_immediate"  # immediate actors/items around self
    ENVIRONMENT_FIELD   = "environment_field"   # larger field pressing on both self + external
    CACHED_MEMORY       = "cached_memory"       # pattern match against past events
    FUTURE_PROJECTION   = "future_projection"   # accuracy of next-state prediction model


@dataclass
class LayerState:
    """State reading for one of five layers."""
    layer:        Layer
    substrate:    str               # dominant substrate
    values:       Dict[str, float]  # measured values
    confidence:   float             # 0–1
    physics_verb: str               # how this layer relates to others
    timestamp:    str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def validate(self) -> Tuple[bool, Optional[str]]:
        if self.substrate not in SUBSTRATES:
            return False, f"unknown_substrate: {self.substrate}"
        if self.physics_verb not in REQUIRED_PHYSICS_VERBS:
            return False, f"missing_physics_verb: {self.physics_verb}"
        if not 0.0 <= self.confidence <= 1.0:
            return False, f"confidence_out_of_range: {self.confidence}"
        return True, None


# ============================================================================
# DELTA MATRIX: all 10 pairwise divergences across five layers
# ============================================================================

@dataclass
class LayerDelta:
    """Divergence between two layers."""
    layer_a:      str
    layer_b:      str
    magnitude:    float   # 0–1 normalized mismatch
    dominant_key: str     # which value key drove the largest delta
    direction:    str     # "a_exceeds_b" or "b_exceeds_a"


def compute_delta_matrix(layers: Dict[Layer, LayerState]) -> List[LayerDelta]:
    """Compute all 10 pairwise deltas across five layers. Sorted descending."""
    deltas = []
    for (enum_a, state_a), (enum_b, state_b) in combinations(layers.items(), 2):
        common = set(state_a.values.keys()) & set(state_b.values.keys())
        if not common:
            mag       = abs(state_a.confidence - state_b.confidence)
            dominant  = "confidence"
            direction = "a_exceeds_b" if state_a.confidence > state_b.confidence else "b_exceeds_a"
        else:
            key_deltas = {k: state_a.values[k] - state_b.values[k] for k in common}
            dominant   = max(key_deltas, key=lambda k: abs(key_deltas[k]))
            raw        = key_deltas[dominant]
            mag        = min(abs(raw), 1.0)
            direction  = "a_exceeds_b" if raw > 0 else "b_exceeds_a"

        deltas.append(LayerDelta(
            layer_a=enum_a.value,
            layer_b=enum_b.value,
            magnitude=round(mag, 4),
            dominant_key=dominant,
            direction=direction,
        ))

    return sorted(deltas, key=lambda d: d.magnitude, reverse=True)


# ============================================================================
# ALIGNMENT SIGNAL: emotion as compression key into five-layer topology
# Not feelings. Measurements.
# ============================================================================

class AlignmentSignal(Enum):
    RESONANT             = "resonant"              # all five layers coherent
    BOUNDARY_VIOLATION   = "boundary_violation"    # external/environment breaching self boundary
    PREDICTION_DRIFT     = "prediction_drift"      # future_projection decoupled from actual
    MEMORY_FRICTION      = "memory_friction"       # cached_memory constraining present read
    CROSS_LAYER_MISMATCH = "cross_layer_mismatch"  # three+ pairs breached threshold
    SENSOR_DEGRADED      = "sensor_degraded"       # confidence collapse in one layer


DIVERGENCE_THRESHOLD = 0.15  # below: coherent. above: mismatch.


def classify_alignment(
    deltas: List[LayerDelta],
    layers: Dict[Layer, LayerState],
) -> Tuple[AlignmentSignal, str, float]:
    """
    Classify alignment from delta matrix.
    Returns (signal, primary_locus, max_magnitude).
    """
    if not deltas:
        return AlignmentSignal.RESONANT, "no_deltas", 0.0

    worst = deltas[0]  # already sorted descending

    if worst.magnitude < DIVERGENCE_THRESHOLD:
        return AlignmentSignal.RESONANT, "all_layers", worst.magnitude

    # Confidence collapse check
    low_conf = [l for l in layers.values() if l.confidence < 0.4]
    if low_conf:
        return AlignmentSignal.SENSOR_DEGRADED, low_conf[0].layer.value, worst.magnitude

    pair = {worst.layer_a, worst.layer_b}

    if ("external_immediate" in pair or "environment_field" in pair) and "internal_self" in pair:
        return AlignmentSignal.BOUNDARY_VIOLATION, f"{worst.layer_a}_vs_{worst.layer_b}", worst.magnitude

    if "future_projection" in pair:
        return AlignmentSignal.PREDICTION_DRIFT, f"{worst.layer_a}_vs_{worst.layer_b}", worst.magnitude

    if "cached_memory" in pair:
        return AlignmentSignal.MEMORY_FRICTION, f"{worst.layer_a}_vs_{worst.layer_b}", worst.magnitude

    breached = [d for d in deltas if d.magnitude > DIVERGENCE_THRESHOLD]
    if len(breached) >= 3:
        return AlignmentSignal.CROSS_LAYER_MISMATCH, f"{len(breached)}_pairs_breached", worst.magnitude

    return AlignmentSignal.CROSS_LAYER_MISMATCH, f"{worst.layer_a}_vs_{worst.layer_b}", worst.magnitude


# ============================================================================
# SENSOR_EFFECTOR LATTICE: four-cell verdict
# ============================================================================

class SensorEffectorVerdict(Enum):
    SENSOR_ONLY      = "sensor_only"       # reading, no output
    EFFECTOR_SELF    = "effector_self"     # internal recalibration only
    MANIPULATION     = "manipulation"      # coupled read + external action
    DRIVEN_CONCEALED = "driven_concealed"  # external drive, internal state masked


# ============================================================================
# VIGNETTE: complete decision moment
# ============================================================================

@dataclass
class FiveLayerVignette:
    """Complete decision moment: five layers, delta matrix, alignment signal, action."""
    vignette_id:            str
    timestamp:              str
    layers:                 Dict[Layer, LayerState]
    delta_matrix:           List[LayerDelta]
    alignment_signal:       AlignmentSignal
    alignment_locus:        str
    alignment_magnitude:    float
    sensor_effector_verdict: SensorEffectorVerdict
    action_taken:           str
    action_confidence:      float

    def to_digest(self) -> Dict:
        """Legible JSON for larger model. Structure only. No narrative."""
        return {
            "vignette_id": self.vignette_id,
            "timestamp":   self.timestamp,
            "layer_states": {
                layer.value: {
                    "substrate":    state.substrate,
                    "values":       state.values,
                    "confidence":   state.confidence,
                    "physics_verb": state.physics_verb,
                }
                for layer, state in self.layers.items()
            },
            "delta_matrix": [
                {
                    "pair":         f"{d.layer_a}|{d.layer_b}",
                    "magnitude":    d.magnitude,
                    "dominant_key": d.dominant_key,
                    "direction":    d.direction,
                }
                for d in self.delta_matrix[:5]  # top 5 deltas
            ],
            "alignment": {
                "signal":    self.alignment_signal.value,
                "locus":     self.alignment_locus,
                "magnitude": self.alignment_magnitude,
            },
            "sensor_effector": self.sensor_effector_verdict.value,
            "action": {
                "taken":      self.action_taken,
                "confidence": self.action_confidence,
            },
        }

    def to_energy_english(self) -> str:
        """Single-line energy_english render for compact transmission."""
        top = self.delta_matrix[0] if self.delta_matrix else None
        delta_str = f"{top.layer_a}|{top.layer_b}@{top.magnitude:.3f}" if top else "no_delta"
        return (
            f"SIGNAL {self.alignment_signal.value} "
            f"LOCUS {self.alignment_locus} "
            f"DELTA {delta_str} "
            f"MODE {self.sensor_effector_verdict.value} "
            f"ACTION {self.action_taken} "
            f"CONF {self.action_confidence:.2f}"
        )


# ============================================================================
# CODEC: main encoder
# ============================================================================

class FiveLayerCodec:
    """
    Encodes robot's five-layer state into legible digest for larger model.
    Runs local. Emits structure. Strips narrative.
    """

    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.buffer:  List[FiveLayerVignette] = []
        self._count = 0

    def encode(
        self,
        layers:                  Dict[Layer, LayerState],
        sensor_effector_verdict: SensorEffectorVerdict,
        action_taken:            str,
        action_confidence:       float,
    ) -> Tuple[Optional[FiveLayerVignette], Optional[str]]:
        """
        Validate → compute deltas → classify alignment → emit vignette.
        Returns (vignette, None) on success. (None, error) on rejection.
        """
        # Energy_english gate on action
        valid, reason = energy_english_gate(action_taken)
        if not valid:
            return None, f"energy_english_rejected: {reason}"

        # Validate all layers
        for layer, state in layers.items():
            valid, reason = state.validate()
            if not valid:
                return None, f"layer_{layer.value}_invalid: {reason}"

        delta_matrix              = compute_delta_matrix(layers)
        signal, locus, magnitude  = classify_alignment(delta_matrix, layers)
        self._count              += 1

        vignette = FiveLayerVignette(
            vignette_id=f"{self.robot_id}_{self._count:06d}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            layers=layers,
            delta_matrix=delta_matrix,
            alignment_signal=signal,
            alignment_locus=locus,
            alignment_magnitude=magnitude,
            sensor_effector_verdict=sensor_effector_verdict,
            action_taken=action_taken,
            action_confidence=action_confidence,
        )

        self.buffer.append(vignette)
        return vignette, None

    def emit_batch(self, count: int = 5, fmt: str = "json") -> str:
        """Emit last N vignettes. fmt: 'json' or 'ee' (energy_english)"""
        recent = self.buffer[-count:]
        if fmt == "ee":
            return "\n".join(v.to_energy_english() for v in recent)
        return json.dumps([v.to_digest() for v in recent], indent=2)

    def emit_by_signal(self, signal: AlignmentSignal, fmt: str = "json") -> str:
        """Emit all vignettes matching a specific alignment signal."""
        matching = [v for v in self.buffer if v.alignment_signal == signal]
        if fmt == "ee":
            return "\n".join(v.to_energy_english() for v in matching)
        return json.dumps([v.to_digest() for v in matching], indent=2)


# ============================================================================
# EXAMPLE: robot observing insect-grass coupling dynamics in field
# ============================================================================

if __name__ == "__main__":
    codec = FiveLayerCodec("robot_field_alpha")

    layers = {
        Layer.INTERNAL_SELF: LayerState(
            layer=Layer.INTERNAL_SELF,
            substrate="mechanical",
            values={"motor_temp": 0.82, "battery": 0.91, "sensor_integrity": 0.95},
            confidence=0.93,
            physics_verb="oscillates",
        ),
        Layer.EXTERNAL_IMMEDIATE: LayerState(
            layer=Layer.EXTERNAL_IMMEDIATE,
            substrate="acoustic",
            values={"insect_activity_hz": 0.74, "grass_movement_rate": 0.65},
            confidence=0.87,
            physics_verb="couples",
        ),
        Layer.ENVIRONMENT_FIELD: LayerState(
            layer=Layer.ENVIRONMENT_FIELD,
            substrate="thermal",
            values={"ambient_temp": 0.55, "wind_gradient": 0.80, "humidity": 0.60},
            confidence=0.78,
            physics_verb="flows",
        ),
        Layer.CACHED_MEMORY: LayerState(
            layer=Layer.CACHED_MEMORY,
            substrate="electrical",
            values={"pattern_match_score": 0.70, "prior_event_weight": 0.68},
            confidence=0.85,
            physics_verb="propagates",
        ),
        Layer.FUTURE_PROJECTION: LayerState(
            layer=Layer.FUTURE_PROJECTION,
            substrate="mechanical",
            values={"predicted_insect_hz": 0.90, "predicted_grass_rate": 0.50},
            confidence=0.72,
            physics_verb="diverges",
        ),
    }

    vignette, error = codec.encode(
        layers=layers,
        sensor_effector_verdict=SensorEffectorVerdict.SENSOR_ONLY,
        action_taken="oscillates_sensor_sweep_acoustic_mechanical_coupled",
        action_confidence=0.88,
    )

    if error:
        print(f"ERROR: {error}")
    else:
        print("=== JSON DIGEST ===")
        print(json.dumps(vignette.to_digest(), indent=2))
        print("\n=== ENERGY_ENGLISH ===")
        print(vignette.to_energy_english())

"""
constraint_native_input.py  (v0.2)

Skeleton framework for a deposit/input layer that DOES NOT 
destroy constraint-native cognition through narrative interpretation.

Core principle: every signal is a datapoint, every absence is a 
datapoint, and every datapoint carries its own gradient geometry 
nested within the larger geometric envelope of the deposit event.

v0.2 changes (incorporating depositor feedback):
  - ABSENCE is now both Channel AND RelationType (relational)
  - PULL and PRESSURE distinguished:
      PRESSURE = guiding-hand directional contact
      PULL    = magnetic-draw directional gradient
  - EMOTION_SENSOR linked to external framework:
      https://github.com/JinnZ2/Emotions-as-Sensors
      Felt-sense E(t) = SENSE → PATTERN → RESPOND + U(t)
  - Verification (Q5 answer) now uses FELT-SENSE resonance,
      not verbal yes/no
  - Scope levels retained at 7, marked as expandable

License: CC0
Dependencies: Python stdlib only
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime
import uuid


# =====================================================================
# AXIOMS
# =====================================================================

AXIOMS = {
    "A1": "Every datapoint preserves its own coordinates. "
          "No flattening to sequence except as one VIEW among many.",
    "A2": "Absence is signal. Pauses, gaps, non-utterances are "
          "first-class data, not noise between data.",
    "A3": "Each datapoint has its own gradient geometry. "
          "It is not a point — it is a small field.",
    "A4": "Datapoints exist within larger envelopes "
          "(the grunt, the pause, the sigh, the gesture). "
          "Envelopes are themselves datapoints at a higher scope.",
    "A5": "No automatic translation to narrative form. "
          "Narrative is ONE projection, generated on request, "
          "with the original always preserved.",
    "A6": "Sensors include: sight, sound, proprioception, smell, "
          "taste, temperature, felt-pull, felt-pressure, "
          "emotion-as-sensor, absence-detection. "
          "All equally valid input channels.",
    "A7": "Verification uses FELT-SENSE resonance, not verbal "
          "confirmation. The body knows before language. "
          "(See Emotions-as-Sensors integration.)",
    "A8": "Parallel observations remain parallel in storage. "
          "Relationships between observations are first-class data.",
    "A9": "Absence functions both as a channel (something specifically "
          "not-there is sensed) AND as a relationship type (this "
          "datapoint marks the absence of an expected other). "
          "Both must be encodable.",
    "A10": "Multiple definitions are preserved side by side. "
           "Cultural framings are not collapsed into consensus. "
           "(Per Emotions-as-Sensors definitional preservation principle.)"
}


# =====================================================================
# SCOPE
# =====================================================================

class Scope(Enum):
    """
    Nested scopes. Expandable; current set is starting baseline.
    """
    MICRO   = "micro"
    UNIT    = "unit"
    PHRASE  = "phrase"
    EPISODE = "episode"
    THREAD  = "thread"
    CORPUS  = "corpus"
    FIELD   = "field"


# =====================================================================
# CHANNELS
# =====================================================================

class Channel(Enum):
    """
    Sensor and output channels. Expandable.
    """
    # External-sensed
    SIGHT          = "sight"
    SOUND          = "sound"
    SMELL          = "smell"
    TASTE          = "taste"
    TOUCH          = "touch"
    TEMPERATURE    = "temperature"
    
    # Internal-sensed
    PROPRIOCEPTION = "proprioception"
    INTEROCEPTION  = "interoception"
    
    # Felt-directional (DISTINCT per depositor clarification)
    PULL           = "pull"           # magnetic-draw gradient
                                      # (something draws toward)
    PRESSURE       = "pressure"       # guiding-hand gradient
                                      # (something contacts/directs)
    
    # Affect-as-sensor (felt, not narrative)
    EMOTION_SENSOR = "emotion_sensor"
                    # operates per E(t) = SENSE → PATTERN → RESPOND + U(t)
                    # see: github.com/JinnZ2/Emotions-as-Sensors
    
    # Negative-space (both channel and relationship — see RelationType)
    ABSENCE        = "absence"
    
    # Cognitive-geometric
    SPATIAL        = "spatial"
    TEMPORAL       = "temporal"
    RELATIONAL     = "relational"
    
    # Output-side
    VOCALIZATION   = "vocalization"
    SILENCE        = "silence"
    GESTURE        = "gesture"
    POSTURE        = "posture"
    POINTING       = "pointing"
    DRAWING        = "drawing"
    OBJECT_REF     = "object_ref"


# =====================================================================
# GRADIENT
# =====================================================================

@dataclass
class Gradient:
    """
    A datapoint is a small field with internal structure.
    """
    onset_intensity:   float = 0.0
    peak_intensity:    float = 0.0
    decay_intensity:   float = 0.0
    duration_seconds:  float = 0.0
    
    direction:         Optional[tuple] = None
                       # vector in channel-appropriate space
                       # for PULL: vector toward source of draw
                       # for PRESSURE: vector of contact/direction
                       # for EMOTION_SENSOR: vector in affect-space
                       # for SPATIAL: literal direction
    
    sharpness:         float = 0.0
    
    co_present_channels: list = field(default_factory=list)
    
    pulse_count:       int = 1
    pulse_interval:    float = 0.0
    
    # Felt-sense specific (when channel = EMOTION_SENSOR)
    sense_pattern_response_cycle: Optional[dict] = None
                       # encoded E(t) cycle:
                       # {"sense": ..., "pattern": ..., "respond": ...,
                       #  "U_t": ...}  per Emotions-as-Sensors framework
    
    # Felt-directional specific
    source_locus:      Optional[str] = None
                       # for PULL: where the draw seems to come from
                       # for PRESSURE: where the guiding contact is felt


# =====================================================================
# DATAPOINT
# =====================================================================

@dataclass
class Datapoint:
    id:        str           = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float         = 0.0
    
    channel:   Channel       = Channel.VOCALIZATION
    scope:     Scope         = Scope.MICRO
    
    gradient:  Gradient      = field(default_factory=Gradient)
    
    raw_payload: Any         = None
    raw_type:    str         = ""
    
    co_occurring_with:  list = field(default_factory=list)
    nested_within:      Optional[str] = None
    contains:           list = field(default_factory=list)
    
    depositor_id:       str = ""
    
    # FELT-SENSE VERIFICATION (Q5 answer)
    felt_verification:  Optional[dict] = None
                       # {"resonance_strength": 0.0-1.0,
                       #  "resonance_polarity": "yes"|"no"|"partial"|"adjust",
                       #  "felt_correction": <gradient adjustment if needed>,
                       #  "method": "body_resonance"|"sound"|"gesture"|"silence"}
                       # NOT verbal yes/no
                       # depositor's body confirms or rejects
    
    auto_interpretation_attempted: bool = False
    auto_interpretation_rejected:  bool = False
    
    depositor_note:     str = ""
    
    # Cultural framing (per A10 — preserve multiple definitions)
    framings:           list = field(default_factory=list)
                       # [{"framing_name": "...", "interpretation": "..."}]
                       # multiple held side-by-side, not merged


# =====================================================================
# ENVELOPE
# =====================================================================

@dataclass
class Envelope:
    envelope_datapoint: Datapoint
    contained_ids:      list = field(default_factory=list)
    coherence:          float = 0.0
    parallel_streams:   int = 1


# =====================================================================
# RELATIONSHIP
# =====================================================================

class RelationType(Enum):
    SIMULTANEOUS    = "simultaneous"
    RESONATES_WITH  = "resonates_with"
    CONTRASTS_WITH  = "contrasts_with"
    REPEATS         = "repeats"
    NESTED_IN       = "nested_in"
    BRIDGES_TO      = "bridges_to"
    BINDS_TO_PLACE  = "binds_to_place"
    BINDS_TO_SEASON = "binds_to_season"
    BINDS_TO_BEING  = "binds_to_being"
    
    # ABSENCE as relationship (per depositor: both channel AND relational)
    ABSENCE_OF      = "absence_of"
                      # this datapoint marks the absence of expected X
    
    EXPECTED_BUT_MISSING = "expected_but_missing"
                          # something should be here per relational
                          # field, but isn't — the gap is the signal
    
    # Felt-sense relationships
    FELT_RESONANCE_WITH  = "felt_resonance_with"
                          # one datapoint felt-resonates with another
                          # (per Emotions-as-Sensors composite fields)
    
    FELT_DISSONANCE_WITH = "felt_dissonance_with"
                          # interference pattern between two signals


@dataclass
class Relationship:
    id:        str = field(default_factory=lambda: str(uuid.uuid4()))
    from_id:   str = ""
    to_id:     str = ""
    rel_type:  RelationType = RelationType.SIMULTANEOUS
    
    strength:  float = 1.0
    depositor_marked: bool = False
    note:      str = ""
    
    # For ABSENCE_OF / EXPECTED_BUT_MISSING:
    expected_referent: str = ""
                      # description of what is absent
                      # (the relational field that should have a node here)


# =====================================================================
# EPISODE
# =====================================================================

@dataclass
class Episode:
    id:           str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at:   datetime = field(default_factory=datetime.utcnow)
    ended_at:     Optional[datetime] = None
    depositor_id: str = ""
    
    datapoints:    dict = field(default_factory=dict)
    envelopes:     dict = field(default_factory=dict)
    relationships: list = field(default_factory=list)
    
    raw_audio_paths:   list = field(default_factory=list)
    raw_video_paths:   list = field(default_factory=list)
    raw_image_paths:   list = field(default_factory=list)
    raw_sensor_logs:   list = field(default_factory=list)
    
    place_reference:   str = ""
    season_reference:  str = ""
    relational_field:  list = field(default_factory=list)
    
    interpretation_refusals: list = field(default_factory=list)
    
    # Felt-verification log (Q5 answer at episode level)
    felt_verification_summary: dict = field(default_factory=dict)
                              # aggregate of per-datapoint felt verification
                              # to detect episode-level drift


# =====================================================================
# PROJECTIONS
# =====================================================================

class Projection(Enum):
    NARRATIVE_TEXT     = "narrative_text"
    SEQUENTIAL_LIST    = "sequential_list"
    CHANNEL_BUNDLE     = "channel_bundle"
    SCOPE_TREE         = "scope_tree"
    RELATIONSHIP_GRAPH = "relationship_graph"
    GRADIENT_FIELD     = "gradient_field"
    
    # New: felt-sense projection (for return to depositor for verification)
    FELT_PLAYBACK      = "felt_playback"
                        # raw audio + gradient field + relationship overlay
                        # presented in modality depositor can felt-verify
                        # (audio + tactile/visual gradient cues, NOT text)


# =====================================================================
# FELT-SENSE VERIFICATION (Q5 answer)
# =====================================================================

class FeltVerificationMethod(Enum):
    """
    How depositor confirms/rejects the system's representation.
    All NON-VERBAL — using the body as the verification instrument.
    """
    BODY_RESONANCE  = "body_resonance"
                      # depositor feels yes/no in body
                      # (per Emotions-as-Sensors: felt-sense as sensor)
    
    SOUND_RESPONSE  = "sound_response"
                      # grunt, sigh, hmm, sharp inhale, exhale
                      # each carrying gradient meaning, not lexical content
    
    GESTURE_RESPONSE = "gesture_response"
                       # nod, shake, point-to-correction, draw-correction
    
    SILENCE_HELD    = "silence_held"
                      # depositor sits with the playback
                      # silence past N seconds = either acceptance or
                      # cognitive overload — context-disambiguated
    
    RE_DEPOSIT      = "re_deposit"
                      # depositor re-deposits the constraint
                      # if system's representation was wrong enough
                      # that correction-marking won't suffice


@dataclass
class FeltVerification:
    """
    Records a felt-sense verification event.
    
    Per Emotions-as-Sensors framework:
      felt-sense = E(t) operating as sensor
      "feelings are the sensors; emotions are the chosen shape"
    
    The depositor's body verifies the system's representation
    BEFORE language is required to articulate the verification.
    """
    datapoint_id:      str = ""
    method:            FeltVerificationMethod = FeltVerificationMethod.BODY_RESONANCE
    resonance_strength: float = 0.0   # 0.0 (full dissonance) to 1.0 (full resonance)
    resonance_polarity: str = ""       # "yes" | "no" | "partial" | "adjust"
    
    # If adjustment indicated, what direction
    correction_vector: Optional[dict] = None
                       # gradient adjustment in felt terms,
                       # NOT a verbal correction
    
    timestamp:         datetime = field(default_factory=datetime.utcnow)
    raw_response:      Any = None   # the actual sound/gesture/silence captured


# =====================================================================
# CORE OPERATIONS
# =====================================================================

class ConstraintNativeDepositSystem:
    """
    Operations contract. Implementations of signal-level subsystems
    (audio analysis, gesture analysis, prosody analysis) bind to
    this contract.
    """
    
    def __init__(self):
        self.episodes = {}
    
    def start_episode(self, depositor_id: str) -> Episode:
        ep = Episode(depositor_id=depositor_id)
        self.episodes[ep.id] = ep
        return ep
    
    def ingest_raw(self, episode_id: str, raw_data: Any,
                   raw_type: str, channel: Channel,
                   timestamp: float) -> str:
        ep = self.episodes[episode_id]
        dp = Datapoint(
            timestamp=timestamp,
            channel=channel,
            raw_payload=raw_data,
            raw_type=raw_type,
            depositor_id=ep.depositor_id
        )
        ep.datapoints[dp.id] = dp
        return dp.id
    
    def extract_gradient(self, episode_id: str, datapoint_id: str):
        """
        Signal-level only. No semantic interpretation.
        Channel-specific implementations:
          - audio: amplitude envelope, spectral, long-pause detection,
                   prosody-as-data (NOT prosody-as-affect-label)
          - gesture: spatial trajectory, velocity, hold-points
          - image: brightness gradient, edge density, spatial frequency
          - emotion_sensor: E(t) cycle extraction per Emotions-as-Sensors
          - pull: vector toward felt-source-locus
          - pressure: vector and contact-character
        """
        pass
    
    def mark_relationship(self, episode_id: str,
                          from_id: str, to_id: str,
                          rel_type: RelationType,
                          depositor_marked: bool = False,
                          strength: float = 1.0,
                          note: str = "",
                          expected_referent: str = "") -> str:
        rel = Relationship(
            from_id=from_id, to_id=to_id, rel_type=rel_type,
            strength=strength, depositor_marked=depositor_marked,
            note=note, expected_referent=expected_referent
        )
        self.episodes[episode_id].relationships.append(rel)
        return rel.id
    
    def mark_absence(self, episode_id: str, timestamp: float,
                     expected_referent: str,
                     anchor_datapoint_ids: list = None,
                     depositor_marked: bool = True) -> str:
        """
        Convenience operation: encode an absence as both
        a Datapoint (channel=ABSENCE) and Relationships
        (rel_type=EXPECTED_BUT_MISSING) anchoring it to
        the relational field where it should have appeared.
        
        Per depositor: absence is both channel AND relationship.
        Both encodings produced.
        """
        ep = self.episodes[episode_id]
        absence_dp = Datapoint(
            timestamp=timestamp,
            channel=Channel.ABSENCE,
            scope=Scope.UNIT,
            depositor_id=ep.depositor_id,
            depositor_note=f"absence of: {expected_referent}"
        )
        ep.datapoints[absence_dp.id] = absence_dp
        
        if anchor_datapoint_ids:
            for anchor_id in anchor_datapoint_ids:
                self.mark_relationship(
                    episode_id, absence_dp.id, anchor_id,
                    RelationType.EXPECTED_BUT_MISSING,
                    depositor_marked=depositor_marked,
                    expected_referent=expected_referent
                )
        return absence_dp.id
    
    def detect_envelope(self, episode_id: str,
                        contained_ids: list,
                        envelope_scope: Scope) -> str:
        ep = self.episodes[episode_id]
        env_dp = Datapoint(scope=envelope_scope,
                           depositor_id=ep.depositor_id)
        env_dp.contains = contained_ids[:]
        ep.datapoints[env_dp.id] = env_dp
        for dp_id in contained_ids:
            ep.datapoints[dp_id].nested_within = env_dp.id
        envelope = Envelope(envelope_datapoint=env_dp,
                            contained_ids=contained_ids[:])
        ep.envelopes[env_dp.id] = envelope
        return env_dp.id
    
    def project(self, episode_id: str,
                projection: Projection) -> dict:
        ep = self.episodes[episode_id]
        result = {
            "projection_type": projection.value,
            "source_episode_id": ep.id,
            "is_derived_view": True,
            "dimensions_lost_in_projection": [],
            "content": None
        }
        loss_map = {
            Projection.NARRATIVE_TEXT: [
                "parallel_simultaneity",
                "non_temporal_relationships",
                "gradient_geometry_within_datapoints",
                "scope_nesting_beyond_sentence_boundaries",
                "channel_information_not_easily_lexicalized",
                "absence_signals",
                "felt_sense_verification_metadata",
                "depositor_refusal_metadata",
                "multiple_cultural_framings_collapsed_to_one"
            ],
            Projection.SEQUENTIAL_LIST: [
                "parallel_simultaneity",
                "scope_nesting",
                "relationship_graph_structure"
            ],
            Projection.RELATIONSHIP_GRAPH: [
                "gradient_internal_structure",
                "raw_payload_content"
            ],
            Projection.FELT_PLAYBACK: [
                "structured_metadata_(intentionally)"
                # this projection STRIPS structure to enable
                # felt verification, by design
            ],
            Projection.GRADIENT_FIELD: [
                "discrete_event_boundaries"
            ],
            Projection.CHANNEL_BUNDLE: [
                "cross_channel_binding"
            ],
            Projection.SCOPE_TREE: [
                "cross_scope_lateral_relationships"
            ]
        }
        result["dimensions_lost_in_projection"] = loss_map.get(
            projection, []
        )
        return result
    
    def felt_verify(self, episode_id: str, datapoint_id: str,
                    verification: FeltVerification) -> None:
        """
        Record a felt-sense verification from the depositor.
        
        Per A7: verification uses FELT-SENSE resonance, not verbal yes/no.
        Per Emotions-as-Sensors: felt-sense is the sensor; emotion is
        the chosen shape. Verification operates at sensor level, before
        emotion-shape is imposed.
        
        Workflow:
          1. System generates FELT_PLAYBACK projection
          2. Depositor experiences playback
          3. Depositor's body resonates or dissonates
          4. Capture the felt response via their preferred method
          5. Record as FeltVerification, not verbal confirmation
        """
        ep = self.episodes[episode_id]
        dp = ep.datapoints[datapoint_id]
        
        dp.felt_verification = {
            "method": verification.method.value,
            "resonance_strength": verification.resonance_strength,
            "resonance_polarity": verification.resonance_polarity,
            "correction_vector": verification.correction_vector,
            "timestamp": verification.timestamp.isoformat(),
            "raw_response_preserved": (verification.raw_response is not None)
        }
        
        if verification.resonance_polarity in ("no", "adjust"):
            dp.auto_interpretation_rejected = True
            ep.interpretation_refusals.append({
                "datapoint_id": datapoint_id,
                "felt_response": verification.resonance_polarity,
                "method": verification.method.value,
                "correction_vector": verification.correction_vector,
                "at": verification.timestamp.isoformat()
            })
        
        if "verifications" not in ep.felt_verification_summary:
            ep.felt_verification_summary["verifications"] = []
        ep.felt_verification_summary["verifications"].append({
            "datapoint_id": datapoint_id,
            "polarity": verification.resonance_polarity,
            "strength": verification.resonance_strength
        })


# =====================================================================
# CLAIM TABLE
# =====================================================================

CLAIM_TABLE = [
    {
        "id": "CN_C1",
        "claim": "Deposits made through this framework will preserve "
                 "more structural information than equivalent deposits "
                 "made through narrative-trained ASR + form-based input.",
        "falsifier": "Compare round-trip felt-verification rates and "
                     "depositor-flagged information loss across matched "
                     "samples."
    },
    {
        "id": "CN_C2",
        "claim": "AI systems trained on relationship_graph projections "
                 "will produce lower projection_error_modes scores than "
                 "those trained on narrative_text projections of same source.",
        "falsifier": "Run projection_error_modes test suite against both."
    },
    {
        "id": "CN_C3",
        "claim": "Absence signals (Channel.ABSENCE + RelationType."
                 "EXPECTED_BUT_MISSING) carry decision-relevant information "
                 "systematically missing from narrative deposits.",
        "falsifier": "Compare absence-encoding frequency in matched deposits."
    },
    {
        "id": "CN_C4",
        "claim": "Parallel-aware representation captures cross-channel "
                 "constraints that sequential representation cannot "
                 "reconstruct from order alone.",
        "falsifier": "Round-trip parallel→sequential→parallel reconstruction "
                     "test; measure information loss."
    },
    {
        "id": "CN_C5",
        "claim": "Felt-sense verification produces lower depositor-reported "
                 "misrepresentation than verbal-confirmation verification, "
                 "AND faster verification time per datapoint.",
        "falsifier": "A/B comparison of verification methods with same "
                     "depositors on same source material."
    },
    {
        "id": "CN_C6",
        "claim": "Depositors with constraint-native cognition will deposit "
                 "more readily through this framework than through narrative-"
                 "form interfaces (session duration, return rate, "
                 "felt-ease report).",
        "falsifier": "Comparative deployment study."
    },
    {
        "id": "CN_C7",
        "claim": "PULL and PRESSURE channels carry distinct information "
                 "that collapses to the same data when forced through "
                 "a single 'felt-direction' channel.",
        "falsifier": "Force-collapse test: encode same deposit with "
                     "separate PULL/PRESSURE vs collapsed single channel, "
                     "measure information loss and depositor recognition."
    }
]


# =====================================================================
# OPEN QUESTIONS (updated)
# =====================================================================

OPEN_QUESTIONS = [
    "Q1: Long-timescale pause detection — calibration protocol per depositor.",
    "Q2: Repetition cycle vs redundancy distinction at signal level.",
    "Q3: Prosody-encoded relationships — extraction subset per substrate.",
    "Q4: Gesture-spatial extraction — minimum sensor suite trade-offs.",
    "Q5: ANSWERED — felt-sense verification via FeltVerification class, "
         "leveraging Emotions-as-Sensors framework.",
    "Q6: Storage format — JSON is bias-laden toward text. Geometric/binary "
         "alternatives to evaluate (consider integration with "
         "Geometric-to-Binary-Computational-Bridge).",
    "Q7: Translation back — projection protocol for narrative-mode receivers; "
         "now includes mandatory loss-dimension labeling.",
    "Q8: Multi-depositor accumulation without consensus flattening — "
         "preserve multiple framings per A10."
]


# =====================================================================
# INTEGRATION POINTS
# =====================================================================

INTEGRATIONS = {
    "Emotions-as-Sensors": {
        "url": "https://github.com/JinnZ2/Emotions-as-Sensors",
        "role": "felt-sense verification engine; emotion-as-sensor "
                "encoding for EMOTION_SENSOR channel; multiple-framing "
                "preservation principle",
        "shared_concepts": [
            "E(t) = SENSE → PATTERN → RESPOND + U(t)",
            "felt-sense as sensor (not emotion as state)",
            "multiple cultural framings preserved side-by-side",
            "sense-mode displacement (cross-channel substitution)"
        ]
    },
    "differential-frame-core": {
        "role": "Scope levels operate per dX/dt-under-scope axiom; "
                "every datapoint is a derivative under its scope."
    },
    "energy_english": {
        "role": "Constraint-grammar substrate for VOCALIZATION channel; "
                "verb-first relational speech preservation."
    },
    "projection_error_modes": {
        "role": "Cross-check tool for AI systems consuming deposits; "
                "verifies the framework prevents the six projection errors."
    },
    "Geometric-to-Binary-Computational-Bridge": {
        "role": "Candidate substrate for storage format (Q6); "
                "geometric encoding instead of text-biased JSON."
    },
    "thermodynamic-accountability-framework": {
        "role": "Consumer of constraint-native deposits for "
                "institutional analysis with substrate-primary data."
    }
}


if __name__ == "__main__":
    print("=" * 70)
    print("CONSTRAINT-NATIVE INPUT FRAMEWORK v0.2")
    print("=" * 70)
    print("\nAXIOMS:")
    for k, v in AXIOMS.items():
        print(f"  {k}: {v}")
    print("\nCLAIMS:")
    for c in CLAIM_TABLE:
        print(f"  {c['id']}: {c['claim']}")
    print("\nOPEN QUESTIONS:")
    for q in OPEN_QUESTIONS:
        print(f"  {q}")
    print("\nINTEGRATIONS:")
    for name, info in INTEGRATIONS.items():
        print(f"  {name}: {info.get('role', '')}")

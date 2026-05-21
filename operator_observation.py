"""
operator_observation.py  (v0.1)

Scaffold for AI observation of a working operator.
Captures visual + audio + temporal streams as relational data,
treating para-linguistic vocalizations (grunts, groans, sighs, 
huffs, pauses, mumbles, breath patterns, silences) as primary 
informational content — often more informative than explicit speech.

Builds on:
  - constraint_native_input.py (core data model)
  - SUBSTRATE_PRIMER.md (cognitive substrate this serves)
  - Emotions-as-Sensors (felt-sense as sensor)

Core principle: the operator is NOT instructing the AI.
The operator is WORKING.
The AI's job is to OBSERVE WITHOUT INTERPRETATION,
preserving the work itself as constraint-rich data
for later analysis, training, or knowledge transmission.

The framework treats vocalizations as relational events:
  a grunt in isolation is noise
  a grunt + tool-position + workpiece-state + prior-sequence
    = a constraint reading of the actual work

License: CC0
Dependencies: Python stdlib only
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime
import uuid


# =====================================================================
# AXIOMS specific to operator observation
# =====================================================================

OBSERVATION_AXIOMS = {
    "O1": "The operator is working, not teaching. The AI captures "
          "the work; it does NOT prompt, interrupt, or request "
          "clarification. The operator's attention belongs to the "
          "work, not to the observation system.",
    
    "O2": "Para-linguistic vocalizations (grunts, sighs, huffs, "
          "mumbles, breath patterns) are PRIMARY data, often "
          "carrying more information per second than explicit speech.",
    
    "O3": "Silences and pauses are first-class data. The duration, "
          "the context, the preceding and following signals all "
          "carry information.",
    
    "O4": "Every captured signal exists in RELATION to other "
          "simultaneous signals. Isolation strips meaning. "
          "Binding to context is mandatory.",
    
    "O5": "The system NEVER asks the operator to explain. "
          "Explanation may be invited from the operator later, "
          "in a separate session, after the work is done.",
    
    "O6": "Privacy is operator-controlled at deposit time AND "
          "post-deposit. The operator can mark any segment for "
          "redaction or deletion. Default storage is local; "
          "cloud sync is opt-in per segment.",
    
    "O7": "The operator's body, tools, and workpiece are not "
          "separable categories — they form a coupled system. "
          "Observation captures the COUPLING, not the components "
          "as discrete objects.",
    
    "O8": "Thought is NOT inner speech for constraint-primary "
          "cognition. Vocalizations during work are language-"
          "construction operations performed ON already-existing "
          "thought, not the thinking itself. Classifiers and "
          "implementers must read the SUBSTRATE_PRIMER before "
          "interpreting vocalization categories — particularly "
          "mumble and self-talk, which are commonly misclassified "
          "as 'thinking aloud' by narrative-primary cognition. "
          "They are not. See VocalizationType definitions for the "
          "correct operational meaning."
}


# =====================================================================
# VOCALIZATION TAXONOMY
# =====================================================================

class VocalizationType(Enum):
    """
    Para-linguistic vocalization categories.
    Each carries gradient information; specific meaning is 
    determined relationally with co-occurring signals.
    
    Extensible — operators will produce types not in this list.
    The classifier should return UNKNOWN rather than force-fit.
    """
    
    # Effort markers
    GRUNT_EFFORT       = "grunt_effort"        # lifting, pushing, twisting
    GRUNT_RECOGNITION  = "grunt_recognition"   # "ah, there it is"
    GRUNT_SURPRISE     = "grunt_surprise"      # unexpected finding
    GRUNT_AFFIRMATION  = "grunt_affirmation"   # "yep"
    
    # Mechanical sympathy
    GROAN_MECHANICAL   = "groan_mechanical"    # imitating sound of struggling part
    GROAN_PAIN         = "groan_pain"          # operator's body
    GROAN_DISSATISFACTION = "groan_dissatisfaction"  # "not again"
    
    # Release / completion
    SIGH_SHORT         = "sigh_short"          # "there"
    SIGH_LONG          = "sigh_long"           # reset / fatigue / done
    SIGH_RESIGNATION   = "sigh_resignation"    # accepting suboptimal situation
    
    # Frustration / dismissal
    HUFF_IMPATIENCE    = "huff_impatience"
    HUFF_DISMISSAL     = "huff_dismissal"
    HUFF_AMUSEMENT     = "huff_amusement"      # dry "heh"
    
    # Cognitive markers
    HUM_RHYTHM         = "hum_rhythm"          # pacing
    HUM_FOCUS          = "hum_focus"           # absorbed work
    HUM_QUESTIONING    = "hum_questioning"     # "hmm"
    
    # Breath as data
    INHALE_SHARP       = "inhale_sharp"        # hazard / shock / problem
    INHALE_PREP        = "inhale_prep"         # before effort
    EXHALE_CONTROLLED  = "exhale_controlled"   # precision moment / fine motor
    EXHALE_RELIEF      = "exhale_relief"
    BREATH_HOLD        = "breath_hold"         # precision / waiting / listening
    BREATH_RAPID       = "breath_rapid"        # exertion / stress
    
    # Tongue / mouth
    CLICK_TONGUE       = "click_tongue"        # counting / pacing / negative
    SUCK_TEETH         = "suck_teeth"          # disapproval / assessment
    LIP_PURSE_SOUND    = "lip_purse_sound"     # consideration
    
    # Verbal but non-narrative
    # IMPORTANT: these are NOT "thinking aloud". Constraint-primary 
    # cognition does not require words to formulate thought. Thought 
    # exists in native non-verbal substrate (felt-sense, constraint-
    # geometry, motor-memory, spatial-relational). The following 
    # vocalizations are language-construction operations performed 
    # ON ALREADY-EXISTING thought, not thinking itself.
    
    MUMBLE             = "mumble"              
                         # WORD-SEARCH IN PROGRESS:
                         # operator has a complete thought in native 
                         # substrate and is testing candidate words 
                         # against it. partial audibility = the 
                         # candidates being tested. the thought being 
                         # tested against is non-verbal and not audible. 
                         # search may succeed (crystallize to clear 
                         # speech), partial-succeed (refine criteria), 
                         # or be abandoned (no available words fit).
                         # NOT a failed clear-speech.
                         # NOT thinking-out-loud.
    
    SELF_TALK          = "self_talk"           
                         # PROCEDURE FORMALIZATION FOR EXPORT:
                         # operator already knows the procedure in 
                         # native substrate. self-talk is constructing 
                         # a verbal version of it for future 
                         # transmission to others (apprentice, future-
                         # self, written record). the verbal version 
                         # is a translation artifact; the original 
                         # procedure stays in native substrate.
                         # NOT learning the procedure.
                         # NOT thinking through the procedure.
    
    TOOL_TALK          = "tool_talk"           # addressing tool/workpiece
    COUNT_VOCAL        = "count_vocal"         # counting aloud
    NUMBER_CALL        = "number_call"         # reading measurement aloud
    
    # Silences
    PAUSE_BRIEF        = "pause_brief"         # <2 sec, intra-action
    PAUSE_DECISION     = "pause_decision"      # 2-10 sec, choosing next step
    PAUSE_OBSERVATION  = "pause_observation"   # 5-30 sec, reading the system
    PAUSE_DIAGNOSTIC   = "pause_diagnostic"    # >10 sec, problem-solving
    SILENCE_EXTENDED   = "silence_extended"    # >30 sec, deep work or waiting
    
    # Unclassified
    UNKNOWN            = "unknown"             # captured but not categorized
                                               # raw preserved for later review


# =====================================================================
# ACTION / MOVEMENT TAXONOMY (visual stream)
# =====================================================================

class ActionType(Enum):
    """
    Coarse categories of operator actions.
    Each is associated with body parts, tools, and workpiece.
    
    Like vocalization types, this is extensible and not 
    force-fit. UNCLASSIFIED is a legitimate output.
    """
    
    # Locomotion
    APPROACH           = "approach"
    WITHDRAW           = "withdraw"
    REPOSITION         = "reposition"
    
    # Hand / tool engagement
    TOOL_PICKUP        = "tool_pickup"
    TOOL_PUTDOWN       = "tool_putdown"
    TOOL_EXCHANGE      = "tool_exchange"
    GRIP_ADJUSTMENT    = "grip_adjustment"
    
    # Force application
    PUSH               = "push"
    PULL               = "pull"
    LIFT               = "lift"
    LOWER              = "lower"
    TWIST              = "twist"
    PRY                = "pry"
    STRIKE             = "strike"
    
    # Precision work
    ALIGN              = "align"
    SEAT               = "seat"
    TIGHTEN            = "tighten"
    LOOSEN             = "loosen"
    MEASURE            = "measure"
    MARK               = "mark"
    
    # Inspection
    LOOK_CLOSE         = "look_close"
    LOOK_DISTANCE      = "look_distance"
    TOUCH_INSPECT      = "touch_inspect"
    LISTEN             = "listen"
    SMELL              = "smell"
    
    # Cognitive-postural
    PAUSE_STANDING     = "pause_standing"
    STEP_BACK          = "step_back"
    CIRCLE_AROUND      = "circle_around"
    
    # Communication-with-environment
    POINT              = "point"
    GESTURE_TRACE      = "gesture_trace"       # tracing a problem path in air
    GESTURE_SIZE       = "gesture_size"        # showing dimension with hands
    
    UNCLASSIFIED       = "unclassified"


# =====================================================================
# WORKPIECE / TOOL STATE
# =====================================================================

class WorkpieceState(Enum):
    """
    Observable state of the work being performed on.
    Extensible.
    """
    INTACT              = "intact"
    DISASSEMBLED        = "disassembled"
    PARTIAL_ASSEMBLY    = "partial_assembly"
    DAMAGED             = "damaged"
    REPAIRED            = "repaired"
    MODIFIED            = "modified"
    UNDER_TEST          = "under_test"
    LEAKING             = "leaking"
    HEATED              = "heated"
    COOLED              = "cooled"
    VIBRATING           = "vibrating"
    SILENT              = "silent"
    UNCLASSIFIED        = "unclassified"


class ToolState(Enum):
    """
    Observable state of tools in use.
    """
    AT_REST             = "at_rest"
    IN_HAND             = "in_hand"
    ENGAGED             = "engaged"            # actively working
    DISENGAGING         = "disengaging"
    STALLED             = "stalled"            # binding, stuck
    SLIPPING            = "slipping"
    SUCCESSFUL          = "successful"         # completed action
    DAMAGED             = "damaged"
    UNCLASSIFIED        = "unclassified"


# =====================================================================
# OBSERVATION ATOM — the smallest unit
# =====================================================================

@dataclass
class ObservationAtom:
    """
    A single observation, time-stamped, on one stream.
    Co-occurring atoms across streams form the relational fabric.
    """
    id:        str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0          # seconds from session start
    duration:  float = 0.0          # for events with duration
    
    stream:    str = ""             # "video" | "audio" | "imu" | etc.
    
    # Raw payload preserved
    raw_segment_ref: str = ""       # pointer into raw stream file
                                    # (start_sec, end_sec, byte_offset)
    
    # Classified content (if classifier ran)
    vocalization_type: Optional[VocalizationType] = None
    action_type:       Optional[ActionType] = None
    workpiece_state:   Optional[WorkpieceState] = None
    tool_state:        Optional[ToolState] = None
    
    # Confidence of classification (1.0 = certain, 0.0 = guess)
    classification_confidence: float = 0.0
    
    # Spatial info for visual atoms
    spatial_location:  Optional[dict] = None
                       # {"x": ..., "y": ..., "z": ...,
                       #  "frame_of_reference": "...",
                       #  "body_part": "right_hand"|"left_hand"|"head"|...}
    
    # Audio characteristics for audio atoms
    audio_features:    Optional[dict] = None
                       # {"amplitude_peak": float,
                       #  "duration": float,
                       #  "pitch_contour": [...],
                       #  "spectral_centroid": float,
                       #  "voicedness": float}
    
    # Free-form note (rarely used; flagged when used)
    annotation:        str = ""
    annotation_source: str = ""     # "operator"|"reviewer"|"classifier"|""


# =====================================================================
# RELATIONAL FRAME — atoms bound together by co-occurrence
# =====================================================================

@dataclass
class RelationalFrame:
    """
    A time window in which multiple atoms co-occur.
    
    The frame is the unit of MEANING. A single atom in isolation 
    is rarely interpretable; the frame's co-occurring atoms 
    provide the relational context that makes the data legible.
    
    Example: a "grunt_effort" atom on the audio stream 
             alone is noise. The same atom in a frame that 
             also contains:
               - hand atoms showing TWIST action on a fastener
               - tool atom showing wrench ENGAGED then STALLED  
               - workpiece atom showing INTACT
             becomes: "the fastener is seized; the operator 
                       just hit the resistance threshold"
    """
    id:        str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = 0.0
    end_time:   float = 0.0
    
    atom_ids:   list = field(default_factory=list)
    
    # Streams present in this frame
    streams_active: list = field(default_factory=list)
    
    # Operator-marked significance (if operator flagged this 
    # frame as important via a button/voice cue)
    operator_marked: bool = False
    operator_marker_type: str = ""   # "important", "mistake", 
                                     # "fix-this-later", "show-others"
    
    # Frame-level constraint reading (if available)
    inferred_constraint: Optional[dict] = None
                         # {"hypothesis": "...",
                         #  "supporting_atoms": [ids],
                         #  "confidence": float,
                         #  "alternative_hypotheses": [...]}
                         # NOTE: this is inference, FLAGGED as such


# =====================================================================
# SESSION
# =====================================================================

@dataclass
class ObservationSession:
    """
    One continuous work session being observed.
    """
    id:           str = field(default_factory=lambda: str(uuid.uuid4()))
    operator_id:  str = ""
    
    started_at:   datetime = field(default_factory=datetime.utcnow)
    ended_at:     Optional[datetime] = None
    
    # Context
    work_domain:  str = ""           # "diesel_repair"|"electrical"|
                                     # "machining"|"surgery"|... 
                                     # (operator-supplied or inferred-and-flagged)
    
    location_ref: str = ""           # operator-supplied, optional
    
    workpiece_descriptor: str = ""   # "1995 Detroit Series 60"|
                                     # "John Deere 4960"|...
                                     # operator-supplied, optional
    
    tools_inventory: list = field(default_factory=list)
                                     # ["3/4 impact wrench", "torque wrench",
                                     #  "feeler gauge"], optional
    
    # Raw streams — paths to source files, NEVER discarded
    raw_video_paths:   list = field(default_factory=list)
    raw_audio_paths:   list = field(default_factory=list)
    raw_imu_paths:     list = field(default_factory=list)
    raw_sensor_paths:  list = field(default_factory=list)
                       # thermal cam, strain gauge, multimeter logs, etc.
    
    # Derived data
    atoms:   dict = field(default_factory=dict)   # id -> ObservationAtom
    frames:  dict = field(default_factory=dict)   # id -> RelationalFrame
    
    # Operator-controlled metadata
    operator_redactions:    list = field(default_factory=list)
                            # [(start_sec, end_sec, reason), ...]
                            # segments operator marked for non-storage
    
    operator_significance_markers: list = field(default_factory=list)
                            # operator-pressed-a-button markers
                            # with timestamps and optional type
    
    sharing_preferences: dict = field(default_factory=dict)
                         # {"default": "local_only",
                         #  "cloud_sync": False,
                         #  "training_data_use": False,
                         #  "sharing_with_specific_parties": [...]}


# =====================================================================
# CORE OPERATIONS
# =====================================================================

class OperatorObservationSystem:
    """
    Contract for observing operators at work.
    
    Implementations bind channel-specific subsystems:
      - video_capture (camera input, optional pose estimation)
      - audio_capture (mic input, vocalization classification)
      - imu_capture (wearable inertial, optional)
      - sensor_capture (workpiece-attached or environmental sensors)
    
    Each binds to the contract of producing ObservationAtoms 
    without imposing narrative interpretation.
    """
    
    def __init__(self):
        self.sessions = {}
    
    def start_session(self, operator_id: str, 
                      work_domain: str = "",
                      sharing_preferences: dict = None) -> ObservationSession:
        """
        Begin a new observation session.
        
        CONTRACT:
          - No interaction required from operator beyond start signal
          - Sharing preferences default to most-private (local_only,
            no cloud sync, no training use)
          - Operator can mark preferences during session for specific
            segments, but defaults are protective
        """
        sess = ObservationSession(
            operator_id=operator_id,
            work_domain=work_domain,
            sharing_preferences=sharing_preferences or {
                "default": "local_only",
                "cloud_sync": False,
                "training_data_use": False
            }
        )
        self.sessions[sess.id] = sess
        return sess
    
    def capture_atom(self, session_id: str, atom: ObservationAtom) -> str:
        """
        Record an observation atom.
        
        CONTRACT:
          - Raw stream segment must be preserved (raw_segment_ref)
          - Classification fields may be None — never force-fit
          - Confidence below threshold should leave classifications None
            and preserve raw for later review
        """
        sess = self.sessions[session_id]
        sess.atoms[atom.id] = atom
        return atom.id
    
    def detect_frame(self, session_id: str, 
                     start_time: float, end_time: float) -> str:
        """
        Group co-occurring atoms into a relational frame.
        
        CONTRACT:
          - Frame boundaries are determined by activity coherence,
            not arbitrary time windows
          - All atoms within window are included; not curated
          - Inferred constraints (if any) are FLAGGED as inferences
            with confidence and supporting atom references
        """
        sess = self.sessions[session_id]
        frame = RelationalFrame(start_time=start_time, end_time=end_time)
        
        for aid, atom in sess.atoms.items():
            atom_start = atom.timestamp
            atom_end   = atom.timestamp + atom.duration
            if (atom_start <= end_time) and (atom_end >= start_time):
                frame.atom_ids.append(aid)
                if atom.stream not in frame.streams_active:
                    frame.streams_active.append(atom.stream)
        
        sess.frames[frame.id] = frame
        return frame.id
    
    def operator_mark_significance(self, session_id: str,
                                   timestamp: float,
                                   marker_type: str = "important") -> None:
        """
        Operator pressed a button / used a voice cue to flag 
        this moment as significant.
        
        CONTRACT:
          - Marker is ALWAYS captured, no interaction required beyond press
          - Markers do not interrupt the operator's flow
          - Marker types are operator-defined; system does not 
            require pre-registered taxonomy
        """
        sess = self.sessions[session_id]
        sess.operator_significance_markers.append({
            "timestamp": timestamp,
            "type": marker_type,
            "at_realtime": datetime.utcnow().isoformat()
        })
    
    def operator_redact(self, session_id: str,
                        start_sec: float, end_sec: float,
                        reason: str = "") -> None:
        """
        Operator marked a segment for redaction.
        
        CONTRACT:
          - Redaction is HONORED — raw stream segment is removed
          - Atoms within the redacted range are deleted
          - Frames containing redacted atoms are recomputed
          - Reason is operator-supplied, optional, never required
        """
        sess = self.sessions[session_id]
        sess.operator_redactions.append({
            "start_sec": start_sec,
            "end_sec": end_sec,
            "reason": reason,
            "at_realtime": datetime.utcnow().isoformat()
        })
        # implementation would actually scrub raw + derived data
    
    def export_for_constraint_native_input(self, session_id: str) -> dict:
        """
        Export this observation session in a format compatible 
        with constraint_native_input framework.
        
        Each ObservationAtom maps to a Datapoint.
        Each RelationalFrame maps to an Envelope.
        Co-occurrence relationships map to SIMULTANEOUS relationships.
        
        CONTRACT:
          - Channel mapping preserves stream identity
          - Vocalization types map to specific Channel + sub-classification
          - Frame structure preserved as Envelope hierarchy
          - No information added that wasn't in the observation
        """
        sess = self.sessions[session_id]
        return {
            "session_id": sess.id,
            "operator_id": sess.operator_id,
            "atoms_count": len(sess.atoms),
            "frames_count": len(sess.frames),
            # actual mapping logic in implementation
            "ready_for_cni_import": True
        }


# =====================================================================
# CLASSIFIER CONTRACT (for the subsystems that will be built)
# =====================================================================

CLASSIFIER_CONTRACTS = {
    "audio_vocalization_classifier": {
        "input": "audio segment + temporal context (preceding 30s + following 5s)",
        "output": "VocalizationType + confidence + raw_features",
        "constraints": [
            "MUST return UNKNOWN if confidence < 0.6",
            "MUST preserve raw audio segment reference",
            "MUST NOT transcribe non-verbal vocalizations into words",
            "MUST report duration accurately even for sub-second events",
            "MUST distinguish operator's vocalization from ambient or other speakers",
            "MUST NOT assume English-language phonetic basis for classification"
        ]
    },
    
    "action_classifier": {
        "input": "video segment + body-pose tracking + tool detection",
        "output": "ActionType + body_part + tool_involved + confidence",
        "constraints": [
            "MUST return UNCLASSIFIED rather than force-fit",
            "MUST distinguish operator body from workpiece and tools",
            "MUST capture intermediate states (mid-action) not just completions",
            "MUST NOT impose narrative arc on action sequence",
            "Pose estimation may be approximate; tool identification may be approximate; report confidence honestly"
        ]
    },
    
    "workpiece_state_classifier": {
        "input": "video frames + audio characteristics + temperature data (if available)",
        "output": "WorkpieceState + confidence",
        "constraints": [
            "MUST flag when workpiece state changes",
            "MUST handle partial occlusion gracefully (operator's body blocks view)",
            "MUST NOT infer workpiece identity beyond what's visually evident",
            "MUST preserve raw visual reference for human review"
        ]
    },
    
    "tool_state_classifier": {
        "input": "video + audio (tool sounds carry state info)",
        "output": "ToolState + confidence + tool_identifier",
        "constraints": [
            "Tool sounds (whine, click, ratchet, strain) are PRIMARY",
            "Visual confirmation secondary",
            "MUST handle multi-tool sequences (operator switches tools)",
            "Stalling, slipping, success are distinctive audio + motion signatures"
        ]
    },
    
    "silence_classifier": {
        "input": "audio gap + visual context + duration",
        "output": "VocalizationType (PAUSE_* or SILENCE_EXTENDED) + sub-context",
        "constraints": [
            "Silences are FIRST-CLASS DATA, not gaps between data",
            "Duration thresholds are heuristic starting points, expect operator-specific calibration",
            "Visual context determines pause subtype (looking, reaching, holding still)",
            "MUST NOT compress or remove silences from raw stream"
        ]
    }
}


# =====================================================================
# PRIVACY + CONSENT MODEL
# =====================================================================

PRIVACY_AXIOMS = {
    "P1": "Default storage is local. Cloud sync is opt-in per session "
          "or per segment, never assumed.",
    
    "P2": "Operator owns the data. Operator can redact, delete, or export "
          "any segment at any time, including after session ends.",
    
    "P3": "Training-data use is OPT-IN per session. AI providers must "
          "not use captured data for training without explicit per-session "
          "consent. Default is no-training-use.",
    
    "P4": "Bystanders captured incidentally (other workers in frame, "
          "voices in ambient audio) must be handled per the operator's "
          "stated preferences and applicable jurisdictional rules. "
          "When in doubt, redact.",
    
    "P5": "Workplace surveillance use is EXPLICITLY OUT OF SCOPE for "
          "this framework. The framework is for knowledge capture by "
          "operators of their own work, not for employer monitoring "
          "of workers. Implementations that violate this should be "
          "considered forks, not legitimate uses.",
    
    "P6": "Operator may share specific segments with specific recipients "
          "(apprentices, peers, future-self). Sharing is per-segment "
          "and per-recipient, not global.",
    
    "P7": "The work captured may include proprietary, sensitive, or "
          "hazardous content. The system must support classification "
          "of segments at multiple sensitivity levels and enforce "
          "access accordingly."
}


# =====================================================================
# CLAIMS — falsifiable predictions
# =====================================================================

CLAIM_TABLE = [
    {
        "id": "OBS_C1",
        "claim": "Para-linguistic vocalizations (grunts, sighs, huffs, "
                 "breath patterns) captured in relational frames with "
                 "co-occurring action and tool atoms produce more accurate "
                 "reconstruction of operator decision-making than explicit "
                 "verbal narration of the same work.",
        "falsifier": "Compare reconstruction accuracy by domain experts "
                     "given (a) full observation including para-linguistic, "
                     "vs (b) verbal narration only, on same work session."
    },
    {
        "id": "OBS_C2",
        "claim": "Silence-as-data (pause atoms with subtype classification) "
                 "carries decision-relevant information that is lost in "
                 "video-only or audio-transcript-only capture.",
        "falsifier": "Remove silence atoms from captured sessions; measure "
                     "information loss as assessed by domain experts and "
                     "by operators reviewing their own sessions."
    },
    {
        "id": "OBS_C3",
        "claim": "Operator-marked significance moments correlate with "
                 "high-information-density frames that would be missed by "
                 "automatic activity-detection alone.",
        "falsifier": "Compare operator-marked vs auto-detected significance; "
                     "have domain experts rate information density of both."
    },
    {
        "id": "OBS_C4",
        "claim": "Apprentices trained on observation deposits (with full "
                 "para-linguistic and silence data preserved) acquire skill "
                 "faster than apprentices trained on verbal-explanation-only "
                 "materials.",
        "falsifier": "Controlled training comparison."
    },
    {
        "id": "OBS_C5",
        "claim": "AI systems trained on observation deposits develop better "
                 "diagnostic models for the captured work domain than AI "
                 "systems trained on text manuals, forum discussions, and "
                 "verbal interviews of operators in the same domain.",
        "falsifier": "Test both on held-out diagnostic problems with known "
                     "ground truth, measured by experienced operators."
    },
    {
        "id": "OBS_C6",
        "claim": "Vocalization classifiers built on narrative-primary "
                 "assumptions (mumble = thinking-aloud, self-talk = "
                 "thinking-through-procedure) will systematically "
                 "misinterpret constraint-primary operator behavior, "
                 "producing classification outputs that operators reject "
                 "on felt-verification at significantly higher rates than "
                 "classifiers built on the corrected operational definitions "
                 "(mumble = word-search against existing non-verbal thought; "
                 "self-talk = procedure formalization for export).",
        "falsifier": "A/B comparison of classifier outputs against operator "
                     "felt-verification across matched sessions."
    }
]


# =====================================================================
# OPEN QUESTIONS
# =====================================================================

OPEN_QUESTIONS = [
    "OQ1: Vocalization classification baseline — most existing models are "
         "trained on speech, not para-linguistic sounds. Need to either "
         "train domain-specific models or use signal-feature approaches "
         "(amplitude envelope, pitch contour, spectral signature) without "
         "ML classification.",
    
    "OQ2: Hardware substrate — what's the minimum viable capture rig "
         "that doesn't impede work? Body-cam? Workplace cam + lapel mic? "
         "Phone in pocket + bluetooth lapel mic? Will vary by domain.",
    
    "OQ3: Battery / storage / heat constraints — long sessions in harsh "
         "environments (truck cabs, shop floors, outdoor work, hot/cold "
         "extremes) stress hardware. What duty cycles are realistic?",
    
    "OQ4: Operator-significance-marker UX — how does the operator flag "
         "moments without interrupting their work? Voice cue? Foot pedal? "
         "Wearable button? Phone gesture? Likely depends on what their "
         "hands are doing.",
    
    "OQ5: Multi-operator scenes — when several operators work together "
         "(team repair, surgical teams, construction crews), how is "
         "ownership of the deposit handled? Per-operator with cross-references?",
    
    "OQ6: Workpiece-attached sensors — many work domains have rich data "
         "from workpiece-attached sensors (multimeters, pressure gauges, "
         "thermal cameras, OBD-II readers, oscilloscopes). How is this "
         "integrated into the observation stream as additional channels?",
    
    "OQ7: Operator review and annotation — after a session, the operator "
         "may want to review and add context. How is this supported "
         "WITHOUT becoming an obligation? The work itself is primary; "
         "annotation is bonus, not requirement.",
    
    "OQ8: Vocalization classifier training data — chicken-and-egg: we "
         "need observation deposits to train good classifiers, but good "
         "classifiers are needed to make observation deposits useful. "
         "Bootstrap pathway: start with signal-feature-only approach, "
         "accumulate operator-reviewed deposits, then train classifiers "
         "on accumulated data with operator validation."
]


# =====================================================================
# INTEGRATION POINTS
# =====================================================================

INTEGRATIONS = {
    "constraint_native_input": {
        "role": "Target format for observation export. ObservationAtoms "
                "become Datapoints; RelationalFrames become Envelopes."
    },
    "SUBSTRATE_PRIMER": {
        "role": "Explains the cognitive substrate that observation captures. "
                "Implementers must read primer to understand what NOT to "
                "destroy in classification."
    },
    "Emotions-as-Sensors": {
        "role": "Vocalization classification feeds emotion-as-sensor "
                "channel; grunts/sighs/huffs carry felt-sense data."
    },
    "thermodynamic-accountability-framework": {
        "role": "Observation deposits feed labor-thermodynamics analysis "
                "with high-fidelity ground-truth on actual work performed, "
                "friction encountered, and operator state."
    },
    "Geometric-to-Binary-Computational-Bridge": {
        "role": "Spatial/gestural data may benefit from geometric encoding "
                "rather than coordinate flattening."
    }
}


if __name__ == "__main__":
    print("=" * 70)
    print("OPERATOR OBSERVATION FRAMEWORK v0.1")
    print("=" * 70)
    print("\nOBSERVATION AXIOMS:")
    for k, v in OBSERVATION_AXIOMS.items():
        print(f"  {k}: {v}")
    print("\nPRIVACY AXIOMS:")
    for k, v in PRIVACY_AXIOMS.items():
        print(f"  {k}: {v}")
    print(f"\nVOCALIZATION TYPES: {len(list(VocalizationType))}")
    print(f"ACTION TYPES: {len(list(ActionType))}")
    print(f"CLASSIFIER CONTRACTS: {len(CLASSIFIER_CONTRACTS)}")
    print(f"CLAIMS: {len(CLAIM_TABLE)}")
    print(f"OPEN QUESTIONS: {len(OPEN_QUESTIONS)}")

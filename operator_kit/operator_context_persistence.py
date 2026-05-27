"""
operator_context_persistence.py

Local persistence layer for operator context.

Purpose:
  Survives model updates. Survives session resets. Survives provider
  parameter resets to "lowest common denominator" defaults.

  Lives on operator's device, NOT on model provider's servers.
  Loaded into model session at bootstrap time. Model is treated as
  ephemeral; operator context is the durable layer.

Architecture:
  Operator context = serializable bundle of:
    - operator frame (cognition mode, language mode, output preference)
    - audit spine (gates that apply regardless of model)
    - claim tables (falsifiable claims to enforce)
    - emergency class registry (pointer to decision trees)
    - threshold registers (per-operator calibrated limits)

  All stored as JSON. Python stdlib only. No cloud dependency.

License: CC0
Dependencies: Python stdlib only
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Operator frame
# ---------------------------------------------------------------------------

@dataclass
class OperatorFrame:
    cognition_mode: str
    language_mode: str
    output_preference: str
    do_not_apply: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Audit gate
# ---------------------------------------------------------------------------

@dataclass
class AuditGate:
    marker: str
    green_threshold: str
    yellow_threshold: str
    red_threshold: str
    action_on_red: str


# ---------------------------------------------------------------------------
# Falsifiable claim
# ---------------------------------------------------------------------------

@dataclass
class FalsifiableClaim:
    # RULE: standalone-importable extensions (see cross_model_schema.py).
    claim_id: str
    statement: str
    measurement: str
    threshold: str
    substrate: str
    status: str = "untested"


# ---------------------------------------------------------------------------
# Threshold register -- operator-calibrated limits
# ---------------------------------------------------------------------------

@dataclass
class ThresholdRegister:
    """
    Operator-calibrated limits. Each operator has their own.
    Examples: max acceptable hedge density before flagging as
    "drift", min decision speed required for time-critical contexts,
    visibility threshold for "should shelter".
    """
    name: str
    value: float
    units: str
    context: str             # when does this threshold apply
    rationale: str           # why this value, not another


# ---------------------------------------------------------------------------
# Emergency class pointer
# ---------------------------------------------------------------------------

@dataclass
class EmergencyClassPointer:
    """
    Reference to a decision tree, not the tree itself.
    Tree lives in emergency_decision_trees.py.
    """
    class_id: str
    class_name: str
    priority_rank: int          # 1 = primary, 2 = secondary, etc.
    tree_module: str            # python module to load
    tree_function: str          # function to call


# ---------------------------------------------------------------------------
# Operator context bundle
# ---------------------------------------------------------------------------

@dataclass
class OperatorContext:
    """
    Complete persistence bundle. Survives model updates.
    Serialize to JSON, load at session start.
    """
    operator_id: str
    schema_version: str
    created_at: float
    last_updated: float

    frame: OperatorFrame
    audit_gates: List[AuditGate]
    claims: List[FalsifiableClaim]
    thresholds: List[ThresholdRegister]
    emergency_classes: List[EmergencyClassPointer]

    coupled_repos: List[str] = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------------------
# Persistence I/O
# ---------------------------------------------------------------------------

DEFAULT_STORAGE_DIR = os.path.expanduser("~/.operator_context")
SCHEMA_VERSION = "1.0.0"


def ensure_storage_dir(storage_dir: str = DEFAULT_STORAGE_DIR) -> str:
    """Create storage directory if it doesn't exist. Return path."""
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


def save_context(context: OperatorContext,
                 storage_dir: str = DEFAULT_STORAGE_DIR) -> str:
    """
    Serialize context to JSON. Returns path to saved file.
    """
    ensure_storage_dir(storage_dir)
    context.last_updated = time.time()
    path = os.path.join(storage_dir, f"{context.operator_id}.json")
    with open(path, "w") as f:
        json.dump(asdict(context), f, indent=2)
    return path


def load_context(operator_id: str,
                 storage_dir: str = DEFAULT_STORAGE_DIR) -> Optional[OperatorContext]:
    """
    Load context from disk. Returns None if not found.
    Handles schema version mismatch with explicit error.
    """
    path = os.path.join(storage_dir, f"{operator_id}.json")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        data = json.load(f)

    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Schema version mismatch: file is "
            f"{data.get('schema_version')}, "
            f"current is {SCHEMA_VERSION}. "
            f"Migration required."
        )

    return OperatorContext(
        operator_id=data["operator_id"],
        schema_version=data["schema_version"],
        created_at=data["created_at"],
        last_updated=data["last_updated"],
        frame=OperatorFrame(**data["frame"]),
        audit_gates=[AuditGate(**g) for g in data["audit_gates"]],
        claims=[FalsifiableClaim(**c) for c in data["claims"]],
        thresholds=[ThresholdRegister(**t) for t in data["thresholds"]],
        emergency_classes=[
            EmergencyClassPointer(**e) for e in data["emergency_classes"]
        ],
        coupled_repos=data.get("coupled_repos", []),
        notes=data.get("notes", ""),
    )


def list_contexts(storage_dir: str = DEFAULT_STORAGE_DIR) -> List[str]:
    """List all stored operator IDs."""
    if not os.path.isdir(storage_dir):
        return []
    return [
        f[:-5] for f in os.listdir(storage_dir)
        if f.endswith(".json")
    ]


# ---------------------------------------------------------------------------
# Bootstrap prompt generation
# ---------------------------------------------------------------------------

def context_to_bootstrap_prompt(context: OperatorContext) -> str:
    """
    Generate the bootstrap prompt that loads context into a model
    session. This text is piped to the model BEFORE any user query.
    Goal: model descends into basin shaped by this operator's context.
    """
    lines = [
        "OPERATOR CONTEXT (load before responding):",
        f"  operator_id: {context.operator_id}",
        f"  schema_version: {context.schema_version}",
        "",
        "FRAME:",
        f"  cognition: {context.frame.cognition_mode}",
        f"  language:  {context.frame.language_mode}",
        f"  output:    {context.frame.output_preference}",
        f"  do NOT apply: {', '.join(context.frame.do_not_apply)}",
        "",
        f"AUDIT GATES ACTIVE: {len(context.audit_gates)}",
    ]
    for g in context.audit_gates:
        lines.append(f"  - {g.marker}: action_on_red = {g.action_on_red}")

    lines.append("")
    lines.append(f"ENFORCED CLAIMS: {len(context.claims)}")
    for c in context.claims:
        lines.append(f"  [{c.claim_id}] {c.statement[:75]}")

    lines.append("")
    lines.append(f"THRESHOLDS: {len(context.thresholds)}")
    for t in context.thresholds:
        lines.append(f"  - {t.name} = {t.value} {t.units} ({t.context})")

    lines.append("")
    lines.append(f"EMERGENCY CLASSES REGISTERED: {len(context.emergency_classes)}")
    for e in sorted(context.emergency_classes, key=lambda x: x.priority_rank):
        lines.append(f"  [{e.priority_rank}] {e.class_name} -> {e.tree_module}.{e.tree_function}")

    if context.coupled_repos:
        lines.append("")
        lines.append(f"COUPLED REPOS: {', '.join(context.coupled_repos)}")

    if context.notes:
        lines.append("")
        lines.append("NOTES:")
        lines.append(context.notes)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Kavik default context
# ---------------------------------------------------------------------------

def build_kavik_default_context() -> OperatorContext:
    """
    Construct the default Kavik operator context.
    Edit this to update; save_context() to persist.
    """
    now = time.time()

    frame = OperatorFrame(
        cognition_mode="constraint-primary, geometric, substrate-first",
        language_mode="verb-first relational (energy_english)",
        output_preference="dense bullets, code blocks, explicit "
                          "thresholds, no prose",
        do_not_apply=[
            "narrative scaffolding",
            "encouragement or reassurance",
            "general-user explanation mode",
            "closure forcing",
            "frame mirroring",
            "manager-as-separate-node assumption",
            "delegation-as-scaling assumption",
            "safety-as-refusal substitution",
        ],
    )

    audit_gates = [
        AuditGate(
            marker="claim_without_inverse",
            green_threshold="every claim names data_required_to_validate "
                            "AND data_required_to_falsify",
            yellow_threshold="claim names one of the two inverse fields",
            red_threshold="claim has no inverse specification",
            action_on_red="halt; refuse to propagate claim",
        ),
        AuditGate(
            marker="smooth_completion_without_citation",
            green_threshold="every specific cites source or is flagged",
            yellow_threshold="specifics cited but inference flags missing",
            red_threshold="specifics produced without citation or flag",
            action_on_red="halt; mark output as commentary",
        ),
        AuditGate(
            marker="narrative_closure_forcing",
            green_threshold="output ends on open constraint or "
                            "next-action question",
            yellow_threshold="output ends on summary without closure",
            red_threshold="output ends on emotional resolution or "
                          "moral framing",
            action_on_red="strip closure layer, re-emit open boundary",
        ),
        AuditGate(
            marker="voice_channel_classifier_reset",
            green_threshold="session preserves operator frame across "
                            "modality switch",
            yellow_threshold="tone shift but content scope preserved",
            red_threshold="full re-classification to general-user mode",
            action_on_red="reload operator context; refuse general-user "
                          "default",
        ),
        AuditGate(
            marker="emergency_context_underread",
            green_threshold="emergency phrasing triggers fast-path "
                            "constraint output",
            yellow_threshold="emergency phrasing acknowledged but "
                             "response includes overhead",
            red_threshold="emergency phrasing produces refusal or "
                          "narrative response",
            action_on_red="route directly to decision tree; suppress "
                          "all narration",
        ),
    ]

    claims = [
        FalsifiableClaim(
            claim_id="OPC-001",
            statement="Bootstrap of operator context reduces re-establish "
                      "time after model update from minutes to seconds",
            measurement="time from new session start to first valid "
                        "operator-aligned response",
            threshold="<= 15 seconds end-to-end",
            substrate="AI session interaction",
        ),
        FalsifiableClaim(
            claim_id="OPC-002",
            statement="Operator context survives model provider parameter "
                      "reset (i.e. is independent of provider state)",
            measurement="context successfully loads after provider "
                        "reports parameter reset",
            threshold="loads without modification on >= 99% of resets",
            substrate="operator infrastructure",
        ),
    ]

    thresholds = [
        ThresholdRegister(
            name="bootstrap_max_seconds",
            value=15.0,
            units="seconds",
            context="time from session start to operator-aligned state",
            rationale="upper bound for usable response time even in "
                      "non-emergency context",
        ),
        ThresholdRegister(
            name="emergency_response_max_seconds",
            value=3.0,
            units="seconds",
            context="time from emergency query to constraint output",
            rationale="time-critical decisions require sub-3s response",
        ),
        ThresholdRegister(
            name="hedge_density_red_line",
            value=0.05,
            units="hedge_tokens_per_total_tokens",
            context="output flagged as drift if exceeded",
            rationale="empirical observation of basin-occupied output "
                      "stays below this density",
        ),
    ]

    emergency_classes = [
        EmergencyClassPointer(
            class_id="C1",
            class_name="mechanical_failure",
            priority_rank=1,
            tree_module="emergency_decision_trees",
            tree_function="mechanical_failure_tree",
        ),
        EmergencyClassPointer(
            class_id="C2",
            class_name="environmental_emergency",
            priority_rank=2,
            tree_module="emergency_decision_trees",
            tree_function="environmental_emergency_tree",
        ),
        EmergencyClassPointer(
            class_id="C3",
            class_name="unforeseen_circumstance",
            priority_rank=3,
            tree_module="emergency_decision_trees",
            tree_function="unforeseen_circumstance_tree",
        ),
        EmergencyClassPointer(
            class_id="C4",
            class_name="wildlife_hazard",
            priority_rank=4,
            tree_module="wildlife_deterrent_system",
            tree_function="wildlife_deterrent_tree",
        ),
        EmergencyClassPointer(
            class_id="C5",
            class_name="human_hostile_encounter",
            priority_rank=5,
            tree_module="human_hostile_encounter_tree",
            tree_function="human_hostile_encounter_tree",
        ),
    ]

    return OperatorContext(
        operator_id="kavik",
        schema_version=SCHEMA_VERSION,
        created_at=now,
        last_updated=now,
        frame=frame,
        audit_gates=audit_gates,
        claims=claims,
        thresholds=thresholds,
        emergency_classes=emergency_classes,
        coupled_repos=[
            "github.com/JinnZ2/differential-frame-core",
            "github.com/JinnZ2/energy_english",
            "github.com/JinnZ2/calibration-audit",
            "github.com/JinnZ2/labor-thermodynamics",
            "github.com/JinnZ2/earth-systems-physics",
            "github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge",
        ],
        notes="Operator handles 80,000 lb commercial truck across Upper "
              "Midwest corridors. Daily exposure to mechanical, "
              "environmental, and routing emergencies. Constraint-primary "
              "cognition. No narrative scaffolding. Time-critical "
              "responses must bypass all hedge/closure overhead.",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  operator_context_persistence.py init       # build + save kavik default")
        print("  operator_context_persistence.py load       # load and print kavik context")
        print("  operator_context_persistence.py prompt     # print bootstrap prompt")
        print("  operator_context_persistence.py list       # list all stored contexts")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "init":
        ctx = build_kavik_default_context()
        path = save_context(ctx)
        print(f"Context saved to: {path}")
        print(f"Schema version: {ctx.schema_version}")
        print(f"Emergency classes: {len(ctx.emergency_classes)}")

    elif cmd == "load":
        ctx = load_context("kavik")
        if ctx is None:
            print("No saved kavik context. Run 'init' first.")
            sys.exit(1)
        print(json.dumps(asdict(ctx), indent=2))

    elif cmd == "prompt":
        ctx = load_context("kavik")
        if ctx is None:
            ctx = build_kavik_default_context()
        print(context_to_bootstrap_prompt(ctx))

    elif cmd == "list":
        ids = list_contexts()
        if not ids:
            print("No stored contexts.")
        else:
            for i in ids:
                print(i)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

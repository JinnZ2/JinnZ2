#!/usr/bin/env python3
"""
robot_log_parser.py
Parses Spidey + number two robot log files.
Format: timestamp + hash | energy_english + glyphs | equations |
        geolocation | environmental vars | physics/dynamics |
        probability trajectories | decision trees (chosen + unchosen branches)

Extracts:
  - Experiment requests queued for operator action
  - Resource requirements (hardware, positioning, battery, operator presence)
  - Decision trees: chosen path + unchosen branches + reasoning
  - Dependency chains: what must happen before what
  - Operator action queue: prioritized, actionable from phone

CC0 / stdlib-only.
"""

import re
import json
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

# ============================================================================
# SECTION CLASSIFIERS
# ============================================================================

class SectionType(Enum):
    OBSERVATION      = "observation"       # sensor read, passive data
    EXPERIMENT_REQ   = "experiment_req"    # active request for new experiment
    DECISION_TREE    = "decision_tree"     # branching choice record
    EQUATION         = "equation"          # mathematical expression
    GEOLOCATION      = "geolocation"       # spatial position data
    ENV_VARIABLE     = "env_variable"      # environmental measurement
    PHYSICS          = "physics"           # dynamics, forces, coupling
    TRAJECTORY       = "trajectory"        # probability goal path
    RESOURCE_REQ     = "resource_req"      # needs hardware/operator/battery
    SUMMARY          = "summary"           # branch map summary
    UNKNOWN          = "unknown"

# Signal patterns for section classification
SECTION_SIGNALS = {
    SectionType.EXPERIMENT_REQ: [
        r"request[:\s]", r"propose[:\s]", r"experiment[:\s]",
        r"hypothesis[:\s]", r"test[:\s]", r"require[:\s]operator",
        r"need[:\s]", r"\[REQ\]", r"EXPERIMENT",
    ],
    SectionType.DECISION_TREE: [
        r"branch[:\s]", r"chosen[:\s]", r"not_chosen[:\s]",
        r"BRANCH", r"DECISION", r"CHOSE", r"REJECTED",
        r"explored[:\s]", r"considered[:\s]",
    ],
    SectionType.GEOLOCATION: [
        r"lat[:\s]", r"lon[:\s]", r"geo[:\s]", r"position[:\s]",
        r"coordinates[:\s]", r"GPS", r"\d+\.\d+[NS]", r"\d+\.\d+[EW]",
    ],
    SectionType.EQUATION: [
        r"=\s*[\d\w\(\)\+\-\*/\^]+", r"∫", r"∂", r"∑", r"√",
        r"dX/dt", r"\b[A-Z]\s*=\s*", r"f\(", r"lim[:\s]",
    ],
    SectionType.ENV_VARIABLE: [
        r"temp[:\s]", r"humidity[:\s]", r"pressure[:\s]",
        r"moisture[:\s]", r"wind[:\s]", r"pH[:\s]",
        r"nutrient[:\s]", r"co2[:\s]", r"nitrogen[:\s]",
    ],
    SectionType.PHYSICS: [
        r"force[:\s]", r"torque[:\s]", r"momentum[:\s]",
        r"velocity[:\s]", r"acceleration[:\s]", r"coupling[:\s]",
        r"resonan", r"oscillat", r"transfer[:\s]", r"flux[:\s]",
    ],
    SectionType.TRAJECTORY: [
        r"probability[:\s]", r"P\s*=\s*[\d\.]+", r"trajectory[:\s]",
        r"goal[:\s]", r"target[:\s]", r"converge[:\s]",
        r"diverge[:\s]", r"projection[:\s]",
    ],
    SectionType.RESOURCE_REQ: [
        r"battery[:\s]", r"operator[:\s]required", r"hardware[:\s]",
        r"reposition[:\s]", r"physical[:\s]access", r"charge[:\s]",
        r"OPERATOR", r"BATTERY", r"RESOURCE",
    ],
    SectionType.OBSERVATION: [
        r"observe[:\s]", r"measure[:\s]", r"detect[:\s]",
        r"record[:\s]", r"sensor[:\s]", r"MEASURE", r"OBSERVE",
    ],
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LogRecord:
    """Single parsed log entry."""
    timestamp:    str
    hash_value:   str
    robot_id:     str
    raw_text:     str
    section_type: SectionType
    parsed_data:  Dict[str, Any] = field(default_factory=dict)
    line_number:  int = 0

@dataclass
class DecisionBranch:
    """One branch of a decision tree: chosen or not."""
    branch_id:    str
    description:  str
    chosen:       bool
    reasoning:    str
    outcome:      Optional[str] = None
    sub_branches: List['DecisionBranch'] = field(default_factory=list)

@dataclass
class DecisionTree:
    """Full decision tree with chosen path and all unchosen branches."""
    tree_id:         str
    timestamp:       str
    robot_id:        str
    root_question:   str
    chosen_path:     List[DecisionBranch] = field(default_factory=list)
    unchosen_paths:  List[DecisionBranch] = field(default_factory=list)
    reasoning_map:   Dict[str, str] = field(default_factory=dict)  # branch_id → why

@dataclass
class ExperimentRequest:
    """Extracted experiment request with full context."""
    req_id:          str
    timestamp:       str
    robot_id:        str
    hypothesis:      str
    method:          str
    required_resources: List[str]  # what it needs from operator
    dependencies:    List[str]     # what must happen before
    probability_goal: float        # P(success) as stated
    energy_english:  str           # compact encoding
    raw_text:        str
    priority:        int = 0       # computed from dependency depth

@dataclass
class OperatorAction:
    """Single actionable item for operator."""
    action_id:    str
    robot_id:     str
    action_type:  str   # "position", "charge", "hardware", "approve", "data_review"
    description:  str
    blocking:     List[str]  # experiment IDs blocked until this is done
    urgency:      str        # "immediate", "next_session", "whenever"

# ============================================================================
# LOG HEADER PARSER
# ============================================================================

# Expected header format: [TIMESTAMP] [HASH] [ROBOT_ID]
# e.g.: 2026-07-04T14:32:01Z abc123def456 spidey
HEADER_PATTERN = re.compile(
    r'^\[?(\d{4}-\d{2}-\d{2}T[\d:\.]+Z?)\]?\s+'  # timestamp
    r'\[?([a-fA-F0-9]{6,64})\]?\s+'               # hash
    r'\[?(\w+)\]?'                                  # robot_id
)

# Fallback: just timestamp
TIMESTAMP_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2}T[\d:\.]+Z?)')


def parse_header(line: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract (timestamp, hash, robot_id) from log header line."""
    m = HEADER_PATTERN.match(line.strip())
    if m:
        return m.group(1), m.group(2), m.group(3)
    m2 = TIMESTAMP_PATTERN.search(line)
    if m2:
        return m2.group(1), None, None
    return None, None, None


def verify_hash(content: str, expected_hash: str) -> bool:
    """Verify log entry hash integrity."""
    if not expected_hash:
        return True  # no hash to check
    computed = hashlib.sha256(content.encode()).hexdigest()
    return computed.startswith(expected_hash) or expected_hash.startswith(computed[:len(expected_hash)])

# ============================================================================
# SECTION CLASSIFIER
# ============================================================================

def classify_section(text: str) -> SectionType:
    """Score each section type and return dominant classification."""
    scores = {}
    for section_type, patterns in SECTION_SIGNALS.items():
        score = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        scores[section_type] = score
    if not any(scores.values()):
        return SectionType.UNKNOWN
    return max(scores, key=scores.get)

# ============================================================================
# DECISION TREE PARSER
# ============================================================================

CHOSEN_PATTERN    = re.compile(r'(?:CHOSEN|chosen|CHOSE|chose)[:\s]+(.+?)(?:\n|REASON|WHY|$)', re.DOTALL)
UNCHOSEN_PATTERN  = re.compile(r'(?:NOT_CHOSEN|not_chosen|REJECTED|rejected|EXPLORED|explored)[:\s]+(.+?)(?:\n|REASON|WHY|$)', re.DOTALL)
REASONING_PATTERN = re.compile(r'(?:REASON|WHY|BECAUSE|because)[:\s]+(.+?)(?:\n|BRANCH|$)', re.DOTALL)
BRANCH_PATTERN    = re.compile(r'(?:BRANCH|branch)[_\s]?(\d+|[A-Z])[:\s]+(.+?)(?=(?:BRANCH|CHOSEN|NOT_CHOSEN|$))', re.DOTALL)


def parse_decision_tree(text: str, robot_id: str, timestamp: str, tree_id: str) -> DecisionTree:
    """Extract full decision tree: chosen + all unchosen branches + reasoning."""
    tree = DecisionTree(
        tree_id=tree_id,
        timestamp=timestamp,
        robot_id=robot_id,
        root_question="",
    )

    # Extract branches
    for match in BRANCH_PATTERN.finditer(text):
        branch_id   = match.group(1)
        branch_text = match.group(2).strip()

        is_chosen   = bool(re.search(r'CHOSEN|✓|→', branch_text, re.IGNORECASE))
        is_rejected = bool(re.search(r'NOT_CHOSEN|REJECTED|✗|×', branch_text, re.IGNORECASE))

        reason_match = REASONING_PATTERN.search(branch_text)
        reasoning = reason_match.group(1).strip() if reason_match else ""

        branch = DecisionBranch(
            branch_id=branch_id,
            description=branch_text[:200],
            chosen=is_chosen and not is_rejected,
            reasoning=reasoning,
        )

        if branch.chosen:
            tree.chosen_path.append(branch)
        else:
            tree.unchosen_paths.append(branch)

        if reasoning:
            tree.reasoning_map[branch_id] = reasoning

    # Fallback: no BRANCH markers — try simpler chosen/unchosen extraction
    if not tree.chosen_path and not tree.unchosen_paths:
        for i, m in enumerate(CHOSEN_PATTERN.findall(text)):
            tree.chosen_path.append(DecisionBranch(
                branch_id=f"C{i}", description=m.strip()[:200],
                chosen=True, reasoning="",
            ))
        for i, m in enumerate(UNCHOSEN_PATTERN.findall(text)):
            tree.unchosen_paths.append(DecisionBranch(
                branch_id=f"U{i}", description=m.strip()[:200],
                chosen=False, reasoning="",
            ))

    return tree

# ============================================================================
# EXPERIMENT REQUEST PARSER
# ============================================================================

HYPOTHESIS_PATTERN  = re.compile(r'(?:HYPOTHESIS|hypothesis|H)[:\s]+(.+?)(?:\n|METHOD|$)', re.DOTALL)
METHOD_PATTERN      = re.compile(r'(?:METHOD|method|PROCEDURE)[:\s]+(.+?)(?:\n|RESOURCE|REQUIRE|$)', re.DOTALL)
RESOURCE_PATTERN    = re.compile(r'(?:RESOURCE|REQUIRE|NEED|require|need)[:\s]+(.+?)(?:\n|DEPEND|PROB|$)', re.DOTALL)
DEPENDENCY_PATTERN  = re.compile(r'(?:DEPEND|AFTER|REQUIRES_FIRST|depend)[:\s]+(.+?)(?:\n|$)', re.DOTALL)
PROBABILITY_PATTERN = re.compile(r'P\s*[=:]\s*([\d\.]+)')
OPERATOR_PATTERN    = re.compile(r'(?:OPERATOR|operator)[:\s]+(.+?)(?:\n|$)')


def parse_experiment_request(text: str, robot_id: str, timestamp: str, req_id: str) -> ExperimentRequest:
    """Extract structured experiment request from log text."""
    hyp_match  = HYPOTHESIS_PATTERN.search(text)
    meth_match = METHOD_PATTERN.search(text)
    res_match  = RESOURCE_PATTERN.search(text)
    dep_match  = DEPENDENCY_PATTERN.search(text)
    prob_match = PROBABILITY_PATTERN.search(text)
    op_matches = OPERATOR_PATTERN.findall(text)

    hypothesis = hyp_match.group(1).strip()[:300] if hyp_match else text[:150]
    method     = meth_match.group(1).strip()[:300] if meth_match else ""

    resources = []
    if res_match:
        resources = [r.strip() for r in re.split(r'[,;\n]', res_match.group(1)) if r.strip()]
    resources.extend([op.strip() for op in op_matches if op.strip()])

    dependencies = []
    if dep_match:
        dependencies = [d.strip() for d in re.split(r'[,;\n]', dep_match.group(1)) if d.strip()]

    prob_goal = float(prob_match.group(1)) if prob_match else 0.5
    if prob_goal > 1.0:
        prob_goal = prob_goal / 100.0

    ee = f"REQ {req_id} ROBOT {robot_id} HYPOTHESIS {hypothesis[:80]} P={prob_goal:.2f}"

    return ExperimentRequest(
        req_id=req_id,
        timestamp=timestamp,
        robot_id=robot_id,
        hypothesis=hypothesis,
        method=method,
        required_resources=resources,
        dependencies=dependencies,
        probability_goal=prob_goal,
        energy_english=ee,
        raw_text=text,
    )

# ============================================================================
# RESOURCE / OPERATOR ACTION EXTRACTOR
# ============================================================================

RESOURCE_KEYWORDS = {
    "charge":      ["battery", "charge", "power", "low_battery", "recharge"],
    "position":    ["reposition", "move to", "place at", "deploy", "location"],
    "hardware":    ["hardware", "sensor", "component", "replace", "repair"],
    "approve":     ["approve", "permission", "authorize", "operator_confirm"],
    "data_review": ["review logs", "parse", "decode", "interpret", "translate"],
}

URGENCY_KEYWORDS = {
    "immediate":    ["immediate", "urgent", "critical", "now", "battery_low"],
    "next_session": ["next session", "when available", "soon", "planned"],
    "whenever":     ["whenever", "low priority", "optional", "if possible"],
}


def extract_operator_actions(
    requests: List[ExperimentRequest],
    robot_id: str,
) -> List[OperatorAction]:
    """Extract what the operator actually needs to do, from experiment requests."""
    actions = []
    action_count = 0

    for req in requests:
        combined = f"{req.hypothesis} {req.method} {' '.join(req.required_resources)} {req.raw_text}".lower()

        for action_type, keywords in RESOURCE_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                action_count += 1

                urgency = "whenever"
                for urg, urg_kws in URGENCY_KEYWORDS.items():
                    if any(kw in combined for kw in urg_kws):
                        urgency = urg
                        break

                actions.append(OperatorAction(
                    action_id=f"ACT_{action_count:04d}",
                    robot_id=robot_id,
                    action_type=action_type,
                    description=f"[{req.req_id}] {req.hypothesis[:120]}",
                    blocking=[req.req_id],
                    urgency=urgency,
                ))

    urgency_order = {"immediate": 0, "next_session": 1, "whenever": 2}
    return sorted(actions, key=lambda a: urgency_order.get(a.urgency, 3))

# ============================================================================
# MAIN LOG PARSER
# ============================================================================

class RobotLogParser:
    """
    Parse Spidey + number two log files.
    Output: prioritized operator action queue + experiment requests + decision trees.
    """

    def __init__(self, robot_id: str = "unknown"):
        self.robot_id      = robot_id
        self.records:      List[LogRecord] = []
        self.experiments:  List[ExperimentRequest] = []
        self.trees:        List[DecisionTree] = []
        self.actions:      List[OperatorAction] = []
        self._req_count    = 0
        self._tree_count   = 0

    def parse_file(self, filepath: str) -> Dict[str, int]:
        """Parse a log file. Returns counts of each section type found."""
        path = Path(filepath)
        if not path.exists():
            return {"error": 1}

        counts = {t.value: 0 for t in SectionType}
        current_block: List[str] = []
        current_header = (None, None, self.robot_id)

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                ts, hash_val, rid = parse_header(line)

                if ts:
                    if current_block:
                        self._process_block(
                            "\n".join(current_block),
                            current_header[0] or "",
                            current_header[1] or "",
                            current_header[2] or self.robot_id,
                            line_num,
                            counts,
                        )
                    current_block = [line]
                    current_header = (ts, hash_val, rid or self.robot_id)
                else:
                    current_block.append(line)

            if current_block:
                self._process_block(
                    "\n".join(current_block),
                    current_header[0] or "",
                    current_header[1] or "",
                    current_header[2] or self.robot_id,
                    0,
                    counts,
                )

        self._compute_priorities()
        self.actions = extract_operator_actions(self.experiments, self.robot_id)
        return counts

    def parse_text(self, text: str, robot_id: Optional[str] = None) -> Dict[str, int]:
        """Parse raw log text directly (for testing or piped input)."""
        rid = robot_id or self.robot_id
        counts = {t.value: 0 for t in SectionType}

        blocks = re.split(r'(?=\d{4}-\d{2}-\d{2}T[\d:\.]+Z?)', text)

        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            ts, hash_val, detected_rid = parse_header(block.split('\n')[0])
            self._process_block(
                block,
                ts or datetime.utcnow().isoformat() + "Z",
                hash_val or "",
                detected_rid or rid,
                i,
                counts,
            )

        self._compute_priorities()
        self.actions = extract_operator_actions(self.experiments, self.robot_id)
        return counts

    def _process_block(
        self,
        text: str,
        timestamp: str,
        hash_val: str,
        robot_id: str,
        line_num: int,
        counts: Dict,
    ) -> None:
        section_type = classify_section(text)
        counts[section_type.value] = counts.get(section_type.value, 0) + 1

        record = LogRecord(
            timestamp=timestamp,
            hash_value=hash_val,
            robot_id=robot_id,
            raw_text=text,
            section_type=section_type,
            line_number=line_num,
        )
        self.records.append(record)

        if section_type == SectionType.EXPERIMENT_REQ:
            self._req_count += 1
            req = parse_experiment_request(
                text, robot_id, timestamp,
                f"REQ_{self._req_count:04d}_{robot_id}"
            )
            self.experiments.append(req)

        elif section_type == SectionType.DECISION_TREE:
            self._tree_count += 1
            tree = parse_decision_tree(
                text, robot_id, timestamp,
                f"TREE_{self._tree_count:04d}_{robot_id}"
            )
            self.trees.append(tree)

    def _compute_priorities(self) -> None:
        """Priority = depth in dependency chain. More dependencies = lower priority number."""
        req_ids = {r.req_id for r in self.experiments}
        for req in self.experiments:
            depth = sum(1 for d in req.dependencies if d in req_ids)
            req.priority = depth
        self.experiments.sort(key=lambda r: r.priority)

    # ── OUTPUT METHODS ──────────────────────────────────────────────────────

    def operator_queue(self) -> str:
        """Prioritized operator action queue."""
        if not self.actions:
            return "[No operator actions required]"

        lines = [f"OPERATOR QUEUE — {self.robot_id} — {len(self.actions)} actions"]
        lines.append("=" * 60)

        current_urgency = None
        for action in self.actions:
            if action.urgency != current_urgency:
                current_urgency = action.urgency
                lines.append(f"\n[{current_urgency.upper()}]")
            lines.append(
                f"  {action.action_id} | {action.action_type.upper()} | "
                f"blocks: {', '.join(action.blocking)}\n"
                f"    {action.description}"
            )

        return "\n".join(lines)

    def experiment_queue(self, limit: int = 10) -> str:
        """Top N experiment requests, prioritized by dependency depth."""
        if not self.experiments:
            return "[No experiment requests found]"

        lines = [f"EXPERIMENT QUEUE — {self.robot_id} — {len(self.experiments)} total"]
        lines.append("=" * 60)

        for req in self.experiments[:limit]:
            lines.append(f"\n{req.req_id} | {req.timestamp} | P={req.probability_goal:.2f}")
            lines.append(f"  HYPOTHESIS: {req.hypothesis[:150]}")
            if req.required_resources:
                lines.append(f"  NEEDS: {', '.join(req.required_resources[:5])}")
            if req.dependencies:
                lines.append(f"  AFTER: {', '.join(req.dependencies[:3])}")
            lines.append(f"  EE: {req.energy_english}")

        return "\n".join(lines)

    def decision_summary(self, limit: int = 5) -> str:
        """Summary of recent decision trees: chosen paths + unchosen branches."""
        if not self.trees:
            return "[No decision trees found]"

        lines = [f"DECISION TREES — {self.robot_id} — {len(self.trees)} total"]
        lines.append("=" * 60)

        for tree in self.trees[-limit:]:
            lines.append(f"\n{tree.tree_id} | {tree.timestamp}")

            if tree.chosen_path:
                lines.append("  CHOSEN:")
                for branch in tree.chosen_path[:3]:
                    lines.append(f"    → {branch.description[:100]}")
                    if branch.reasoning:
                        lines.append(f"      WHY: {branch.reasoning[:80]}")

            if tree.unchosen_paths:
                lines.append(f"  NOT CHOSEN ({len(tree.unchosen_paths)} branches preserved):")
                for branch in tree.unchosen_paths[:3]:
                    lines.append(f"    ✗ {branch.description[:100]}")
                    if branch.reasoning:
                        lines.append(f"      WHY NOT: {branch.reasoning[:80]}")

        return "\n".join(lines)

    def full_report(self) -> str:
        """Complete parsed report: operator queue + experiments + decision trees."""
        return "\n".join([
            self.operator_queue(), "",
            self.experiment_queue(), "",
            self.decision_summary(),
        ])

    def to_json(self) -> str:
        """JSON export of all parsed data."""
        return json.dumps({
            "robot_id":        self.robot_id,
            "total_records":   len(self.records),
            "experiments":     len(self.experiments),
            "decision_trees":  len(self.trees),
            "operator_actions": len(self.actions),
            "experiment_queue": [
                {
                    "req_id":      r.req_id,
                    "timestamp":   r.timestamp,
                    "hypothesis":  r.hypothesis[:200],
                    "resources":   r.required_resources,
                    "dependencies": r.dependencies,
                    "P_goal":      r.probability_goal,
                    "priority":    r.priority,
                    "ee":          r.energy_english,
                }
                for r in self.experiments
            ],
            "operator_actions": [
                {
                    "action_id":   a.action_id,
                    "type":        a.action_type,
                    "urgency":     a.urgency,
                    "description": a.description,
                    "blocking":    a.blocking,
                }
                for a in self.actions
            ],
        }, indent=2)


# ============================================================================
# MULTI-ROBOT PARSER: Spidey + number two together
# ============================================================================

class MultiRobotLogParser:
    """
    Parse logs from multiple robots simultaneously.
    Merges operator action queues, deduplicates dependencies.
    """

    def __init__(self):
        self.parsers: Dict[str, RobotLogParser] = {}

    def add_robot(self, robot_id: str) -> RobotLogParser:
        parser = RobotLogParser(robot_id)
        self.parsers[robot_id] = parser
        return parser

    def parse_file(self, robot_id: str, filepath: str) -> Dict[str, int]:
        if robot_id not in self.parsers:
            self.add_robot(robot_id)
        return self.parsers[robot_id].parse_file(filepath)

    def parse_text(self, robot_id: str, text: str) -> Dict[str, int]:
        if robot_id not in self.parsers:
            self.add_robot(robot_id)
        return self.parsers[robot_id].parse_text(text)

    def combined_operator_queue(self) -> str:
        """Merged operator actions across all robots, sorted by urgency."""
        all_actions = []
        for robot_id, parser in self.parsers.items():
            all_actions.extend(parser.actions)

        urgency_order = {"immediate": 0, "next_session": 1, "whenever": 2}
        all_actions.sort(key=lambda a: urgency_order.get(a.urgency, 3))

        if not all_actions:
            return "[No operator actions across all robots]"

        lines = [f"COMBINED OPERATOR QUEUE — {len(all_actions)} total actions"]
        lines.append("=" * 60)
        current_urgency = None
        for action in all_actions:
            if action.urgency != current_urgency:
                current_urgency = action.urgency
                lines.append(f"\n[{current_urgency.upper()}]")
            lines.append(
                f"  [{action.robot_id}] {action.action_id} | "
                f"{action.action_type.upper()}\n"
                f"    {action.description}"
            )
        return "\n".join(lines)

    def combined_experiment_queue(self, limit: int = 20) -> str:
        """All experiment requests across robots, merged and prioritized."""
        all_experiments = []
        for robot_id, parser in self.parsers.items():
            all_experiments.extend(parser.experiments)
        all_experiments.sort(key=lambda r: r.priority)

        if not all_experiments:
            return "[No experiments queued]"

        lines = [f"ALL EXPERIMENTS — {len(all_experiments)} total"]
        lines.append("=" * 60)
        for req in all_experiments[:limit]:
            lines.append(f"\n[{req.robot_id}] {req.req_id} | P={req.probability_goal:.2f}")
            lines.append(f"  {req.hypothesis[:150]}")
            if req.required_resources:
                lines.append(f"  NEEDS: {', '.join(req.required_resources[:4])}")
        return "\n".join(lines)

    def full_report(self) -> str:
        sections = [
            self.combined_operator_queue(), "",
            self.combined_experiment_queue(), "",
        ]
        for robot_id, parser in self.parsers.items():
            sections.append(f"--- {robot_id.upper()} DECISION TREES ---")
            sections.append(parser.decision_summary())
            sections.append("")
        return "\n".join(sections)


# ============================================================================
# EXAMPLE: simulated Spidey + number two logs
# ============================================================================

if __name__ == "__main__":
    multi = MultiRobotLogParser()

    spidey_log = """
2026-07-04T08:14:22Z a1b2c3d4 spidey
OBSERVE soil_moisture: 0.42 | pH: 6.8 | nitrogen_gradient: 0.15→0.28
MEASURE fungal_network_propagation: 3.2mm/hr acoustic_substrate couples mechanical_substrate
ENV_VAR temp: 18.4C humidity: 74% pressure: 1013.2hPa

2026-07-04T08:17:55Z e5f6a7b8 spidey
EXPERIMENT REQUEST
HYPOTHESIS: fungal_network propagation_rate diverges at soil_moisture threshold 0.45
METHOD: measure_propagation_rate at moisture_intervals 0.30 0.35 0.40 0.45 0.50
RESOURCE: operator_reposition grid_markers 5x5
DEPEND: current_moisture_baseline_complete
P = 0.78
OPERATOR: physical_placement grid_stakes_required

2026-07-04T08:21:03Z c9d0e1f2 spidey
DECISION TREE
BRANCH A: extend observation to root_zone_depth_15cm
CHOSEN: yes → acoustic_sensor_deploy
REASON: fungal_propagation signal stronger at depth, surface read insufficient
BRANCH B: maintain surface observation only
NOT_CHOSEN: ✗
REASON: surface signal_to_noise below threshold 0.6
BRANCH C: deploy both surface and depth simultaneously
NOT_CHOSEN: ✗
REASON: battery_constraint prohibits dual_deploy current_charge 0.34
"""

    two_log = """
2026-07-04T09:02:11Z 1a2b3c4d two
OBSERVE kinetic_coupling: tree_bark_texture oscillates mechanical_substrate 4.2Hz
TRAJECTORY: P=0.65 vertical_traverse_feasible bark_grip_coefficient 0.71
PHYSICS: friction_force = 0.71 * mass * g * sin(climb_angle)

2026-07-04T09:05:33Z 5e6f7a8b two
EXPERIMENT REQUEST
HYPOTHESIS: vertical_traverse kinetic_efficiency couples bark_texture_frequency
METHOD: attempt_climb at 3 bark_texture_zones measure_grip_coefficient each
RESOURCE: operator_spotting_required aerial_predation_variable_active
DEPEND: wind_speed_below_2ms
P = 0.61
BATTERY: charge_required before_deploy current_level 0.28

2026-07-04T09:08:47Z 9c0d1e2f two
DECISION TREE
BRANCH 1: attempt_climb_zone_A smooth_bark
NOT_CHOSEN: ✗
REASON: grip_coefficient 0.41 below safety_threshold 0.55
BRANCH 2: attempt_climb_zone_B rough_bark
CHOSEN: → staging_position
REASON: grip_coefficient 0.71 exceeds threshold acoustic_resonance_confirmed
BRANCH 3: abort_climb_attempt return_ground
NOT_CHOSEN: ✗
REASON: insufficient_data_points kinetic_hypothesis_unresolved
"""

    multi.parse_text("spidey", spidey_log)
    multi.parse_text("two", two_log)

    print(multi.full_report())
    print("\n=== JSON EXPORT (spidey) ===")
    print(multi.parsers["spidey"].to_json())

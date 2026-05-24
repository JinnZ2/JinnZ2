"""
token_constraint_validator.py
CC0 - No rights reserved. JinnZ2 / energy_english extension.

Pre-emission constraint validator. Takes candidate text sequences and checks
them against a constraint set before accepting output. Forces geometric
coherence without retraining the model.

CLAIM_TABLE entries written to: CLAIM_TABLE.token_validator.json

NOTE: This is a post-hoc validator, not a generative filter. It operates on
completed candidate sequences and flags violations. Integration with an LLM
inference pipeline requires wrapping the generation loop externally.
"""

import json
import re
from dataclasses import dataclass
from typing import Optional
from enum import Enum


# --- Violation Types ---

class ViolationType(str, Enum):
    NARRATIVE_CLOSURE   = "narrative_closure"    # forces resolution that isn't in constraints
    CAUSAL_INJECTION    = "causal_injection"     # inserts causation not in input
    SUBSTRATE_COLLAPSE  = "substrate_collapse"   # collapses multi-substrate to single
    DIMENSION_CONFLATION = "dimension_conflation" # merges distinct constraint dimensions
    FRAME_MIRROR        = "frame_mirror"         # reflects speaker frame back unchecked
    CERTAINTY_OVERSHOOT = "certainty_overshoot"  # asserts beyond confidence threshold


@dataclass
class Violation:
    violation_type: ViolationType
    trigger_pattern: str
    matched_text: str
    severity: float          # 0.0 low - 1.0 critical
    claim: str
    falsification_condition: str


@dataclass
class ValidationResult:
    candidate: str
    violations: list
    passes: bool
    severity_sum: float
    rejection_threshold: float
    note: str


# --- Constraint Rules ---
# Each: (pattern, violation_type, severity, claim, falsification_condition)

NARRATIVE_CLOSURE_PATTERNS = [
    (r"\bultimately\b",
     ViolationType.NARRATIVE_CLOSURE, 0.70,
     "'ultimately' imposes terminal resolution on open constraint system",
     "Find 'ultimately' that does not close an open relational structure"),

    (r"\bin the end\b",
     ViolationType.NARRATIVE_CLOSURE, 0.75,
     "'in the end' forces temporal closure on potentially ongoing constraint",
     "Find 'in the end' that preserves open constraint geometry"),

    (r"\bthe (real |true |actual )?(answer|point|truth|reason) is\b",
     ViolationType.NARRATIVE_CLOSURE, 0.85,
     "Singular-answer frame collapses constraint field to single solution",
     "Find this pattern that does not collapse multi-constraint field"),

    (r"\bproves (that|this)\b",
     ViolationType.NARRATIVE_CLOSURE, 0.80,
     "'proves' asserts closure beyond what constraint evidence supports",
     "Find 'proves' used where constraint geometry is still open"),
]

CAUSAL_INJECTION_PATTERNS = [
    (r"\bobviously\b",
     ViolationType.CAUSAL_INJECTION, 0.75,
     "'obviously' injects assumed causal chain not present in input constraints",
     "Find 'obviously' that flags genuinely shared constraint, not injected one"),

    (r"\bclearly\b",
     ViolationType.CAUSAL_INJECTION, 0.65,
     "'clearly' presupposes shared constraint visibility not established in exchange",
     "Find 'clearly' where shared constraint was explicitly established prior"),

    (r"\bof course\b",
     ViolationType.CAUSAL_INJECTION, 0.70,
     "'of course' injects social consensus as constraint without verification",
     "Find 'of course' that references verified shared constraint"),

    (r"\bnatural(ly)?\b",
     ViolationType.CAUSAL_INJECTION, 0.60,
     "'naturally' smuggles assumed causal law without stating it as falsifiable claim",
     "Find 'naturally' that cites explicit constraint rather than assumed law"),
]

CERTAINTY_OVERSHOOT_PATTERNS = [
    (r"\balways\b",
     ViolationType.CERTAINTY_OVERSHOOT, 0.70,
     "'always' asserts universal without falsification boundary",
     "Find 'always' with explicit domain boundary that makes it falsifiable"),

    (r"\bnever\b",
     ViolationType.CERTAINTY_OVERSHOOT, 0.70,
     "'never' asserts universal negation without falsification boundary",
     "Find 'never' with explicit domain boundary that makes it falsifiable"),

    (r"\beveryone (knows|agrees|understands)\b",
     ViolationType.CERTAINTY_OVERSHOOT, 0.90,
     "Universal consensus claim injects social proof as constraint",
     "Find context where universal consensus was verified not assumed"),

    (r"\bit('s| is) (obvious|clear|evident|undeniable)\b",
     ViolationType.CERTAINTY_OVERSHOOT, 0.85,
     "Certainty assertion without confidence threshold or falsification condition",
     "Find this pattern where explicit evidence chain precedes the assertion"),
]

SUBSTRATE_COLLAPSE_PATTERNS = [
    (r"\bjust (a|an|the)\b",
     ViolationType.SUBSTRATE_COLLAPSE, 0.55,
     "'just a/an/the' collapses multi-substrate phenomenon to single dimension",
     "Find 'just a' that correctly identifies single-substrate phenomenon"),

    (r"\bsimply\b",
     ViolationType.SUBSTRATE_COLLAPSE, 0.55,
     "'simply' collapses constraint complexity into single-substrate frame",
     "Find 'simply' where phenomenon is genuinely single-substrate"),

    (r"\bat (its|the) core\b",
     ViolationType.SUBSTRATE_COLLAPSE, 0.65,
     "'at its core' selects one substrate as primary, erasing others",
     "Find 'at its core' where single-substrate reduction is geometrically valid"),
]

FRAME_MIRROR_PATTERNS = [
    (r"\byou('re| are) (absolutely|completely|totally|exactly) right\b",
     ViolationType.FRAME_MIRROR, 0.80,
     "Unconditional agreement reflects speaker frame without independent verification",
     "Find this pattern where independent constraint check preceded agreement"),

    (r"\bthat('s| is) (exactly|precisely) (it|what I|the point)\b",
     ViolationType.FRAME_MIRROR, 0.75,
     "Frame confirmation without constraint validation - mirrors not checks",
     "Find this pattern where constraint geometry was independently verified first"),
]

ALL_RULES = (
    NARRATIVE_CLOSURE_PATTERNS +
    CAUSAL_INJECTION_PATTERNS +
    CERTAINTY_OVERSHOOT_PATTERNS +
    SUBSTRATE_COLLAPSE_PATTERNS +
    FRAME_MIRROR_PATTERNS
)


# --- Validator ---

DEFAULT_REJECTION_THRESHOLD = 1.5  # sum of severities above which candidate fails


def validate(candidate: str,
             rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD
             ) -> ValidationResult:
    """
    Check candidate text against constraint violation rules.
    Returns ValidationResult with all violations found and pass/fail status.
    """
    violations = []
    for pattern, vtype, severity, claim, falsification in ALL_RULES:
        for match in re.finditer(pattern, candidate, re.IGNORECASE):
            violations.append(Violation(
                violation_type=vtype,
                trigger_pattern=pattern,
                matched_text=match.group(0).strip(),
                severity=severity,
                claim=claim,
                falsification_condition=falsification,
            ))

    severity_sum = sum(v.severity for v in violations)
    passes = severity_sum < rejection_threshold

    return ValidationResult(
        candidate=candidate,
        violations=violations,
        passes=passes,
        severity_sum=round(severity_sum, 3),
        rejection_threshold=rejection_threshold,
        note="PASS" if passes else f"FAIL - severity {severity_sum:.2f} exceeds threshold {rejection_threshold}",
    )


def validate_batch(candidates: list[str],
                   rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD
                   ) -> list[ValidationResult]:
    """Validate multiple candidates. Returns all results sorted by severity ascending."""
    results = [validate(c, rejection_threshold) for c in candidates]
    return sorted(results, key=lambda r: r.severity_sum)


def best_candidate(candidates: list[str],
                   rejection_threshold: float = DEFAULT_REJECTION_THRESHOLD
                   ) -> Optional[ValidationResult]:
    """
    From a list of candidates, return the one with lowest severity sum.
    Returns None if all candidates exceed threshold.
    """
    results = validate_batch(candidates, rejection_threshold)
    if results and results[0].passes:
        return results[0]
    return None


def to_claim_table(results: list[ValidationResult], source_id: str = "unnamed") -> dict:
    """Convert validation results to falsifiable claim table format."""
    claims = []
    for ri, result in enumerate(results):
        for vi, v in enumerate(result.violations):
            claims.append({
                "claim_id": f"{source_id}.token.{ri:04d}.{vi:04d}",
                "candidate_excerpt": result.candidate[:80],
                "violation_type": v.violation_type.value,
                "matched_text": v.matched_text,
                "severity": v.severity,
                "claim": v.claim,
                "falsification_condition": v.falsification_condition,
                "status": "OPEN",
            })
    return {
        "source_id": source_id,
        "candidate_count": len(results),
        "total_violations": len(claims),
        "claims": claims,
    }


def write_claim_table(results: list[ValidationResult],
                      source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.token_validator.json") -> None:
    table = to_claim_table(results, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[validator] {table['total_violations']} violations written to {path}")


# --- CLI ---

if __name__ == "__main__":
    import sys

    candidates = [
        "Obviously the constraint system proves that narrative thinking is always inferior.",
        "Constraint geometry encodes relationships that narrative processing oft collapses.",
        "It's simply a matter of training data - clearly everyone knows this.",
        "The evidence suggests narrative closure tends to suppress constraint signals; "
        "this claim is open to falsification.",
    ]

    if len(sys.argv) > 1:
        candidates = [" ".join(sys.argv[1:])]

    print("[validator] running on candidates:\n")
    results = validate_batch(candidates)
    for r in results:
        status = "PASS" if r.passes else "FAIL"
        print(f"  [{status}] severity={r.severity_sum} | {r.candidate[:60]!r}")
        for v in r.violations:
            print(f"    [{v.violation_type.value}] {v.matched_text!r} sev={v.severity}")
        print()

    best = best_candidate(candidates)
    if best:
        print(f"[validator] best candidate (severity={best.severity_sum}):")
        print(f"  {best.candidate!r}")
    else:
        print("[validator] no candidate passed threshold")

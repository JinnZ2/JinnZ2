#!/usr/bin/env python3
"""
falsification_map_v2.py — FalsificationMap wired to ClaimTable + diagnostic sweep
CC0 / Public Domain — No rights reserved.

When audit produces a verdict, it auto-runs a diagnostic sweep
before the result is recorded. Scope/temporal/structural/relational
probes run from the existing multi-profile data — no extra test
functions needed for the basic sweep.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from thermo_pm import (
    System, CodeRequirement, PurposeProfile,
    audit_requirement_purpose,
    seasonal_shelter, cyclical_village, star_temple
)
from falsification_map import ProvenanceRequirement, FalsificationResult, REVISION_CATEGORIES
from claim_table import Claim, ClaimTable, Revision

# =============================================================================
# 1.  Extended Falsification Result (with sweep)
# =============================================================================

@dataclass
class AuditedClaim:
    """
    One requirement × one purpose profile, fully diagnosed.
    verdict is provisional until sweep confirms or narrows it.
    """
    result: FalsificationResult
    sweep: Dict[str, bool] = field(default_factory=dict)
    # category diagnosed after sweep
    category: Optional[str] = None
    # revised scope if claim was scope-bound
    scope_note: Optional[str] = None

# =============================================================================
# 2.  Auto-Probe Generator
# =============================================================================

def generate_probes(req: ProvenanceRequirement,
                    system: System,
                    goals: Dict[str, float],
                    all_results: List[FalsificationResult]
                    ) -> Dict[str, Callable[[], bool]]:
    """
    Build probes from existing multi-profile run data.
    No extra test functions required for the basic four.
    """

    # scope: does verdict change across purpose profiles?
    def probe_scope():
        verdicts = set(r.verdict for r in all_results if r.requirement_id == req.id)
        return len(verdicts) > 1   # True = claim is scope-bound, not universal

    # temporal: does vintage_year correlate with which profiles show waste?
    def probe_temporal():
        if req.vintage_year is None:
            return False
        # If short-lived profiles show wasteful but long-lived don't,
        # that's a temporal amortization effect baked into the era's materials
        wasteful = [r for r in all_results
                    if r.requirement_id == req.id and r.verdict == "code-wasteful"]
        justified = [r for r in all_results
                     if r.requirement_id == req.id and r.verdict == "code-justified"]
        return bool(wasteful) and bool(justified)

    # structural: does removing one governance process flip the verdict?
    def probe_structural():
        # Re-run audit with governance overhead stripped
        sys_stripped = system.__class__(system.name)
        sys_stripped.resources = dict(system.resources)
        # Keep only ungated processes
        sys_stripped.processes = {
            k: v for k, v in system.processes.items()
            if not any(inp.startswith("mode:") for inp in v.inputs)
        }
        for profile in [seasonal_shelter, cyclical_village, star_temple]:
            stripped_result = audit_requirement_purpose(
                sys_stripped, req, goals, profile
            )
            # If delta flips sign vs. the full system result, structure matters
            full = next((r for r in all_results
                        if r.requirement_id == req.id
                        and r.purpose_name == profile.name), None)
            if full and stripped_result.get("waste_delta") is not None:
                if full.waste_delta_J is not None:
                    if (full.waste_delta_J > 100) != (stripped_result["waste_delta"] > 100):
                        return True
        return False

    # relational: does mode relationship (who can trigger what) affect verdict?
    def probe_relational():
        # Simplified: check if removing the code gate entirely changes which
        # agent path is cheapest
        sys_ungated = system.__class__(system.name)
        sys_ungated.resources = dict(system.resources)
        sys_ungated.processes = {}
        for k, v in system.processes.items():
            import copy
            proc_copy = copy.deepcopy(v)
            # Strip mode gates
            proc_copy.inputs = {
                ki: vi for ki, vi in proc_copy.inputs.items()
                if not ki.startswith("mode:")
            }
            sys_ungated.processes[k] = proc_copy
        # If plan length or waste changes significantly, relation matters
        for profile in [seasonal_shelter]:
            ungated = audit_requirement_purpose(sys_ungated, req, goals, profile)
            full = next((r for r in all_results
                        if r.requirement_id == req.id
                        and r.purpose_name == profile.name), None)
            if full and ungated.get("code_steps") is not None:
                if abs((ungated["code_steps"] or 0) - full.code_steps) > 2:
                    return True
        return False

    # hidden-variable: waste_delta variance across profiles is high
    def probe_hidden_variable():
        deltas = [r.waste_delta_J for r in all_results
                  if r.requirement_id == req.id and r.waste_delta_J is not None]
        if len(deltas) < 2:
            return False
        mean = sum(deltas) / len(deltas)
        variance = sum((d - mean) ** 2 for d in deltas) / len(deltas)
        return variance > (mean ** 2 * 0.5)   # high relative variance = hidden var

    return {
        "scope":           probe_scope,
        "temporal":        probe_temporal,
        "structural":      probe_structural,
        "relational":      probe_relational,
        "hidden-variable": probe_hidden_variable,
    }

# =============================================================================
# 3.  Diagnosis from Sweep
# =============================================================================

def diagnose_from_sweep(sweep: Dict[str, bool],
                        results: List[FalsificationResult],
                        req: ProvenanceRequirement) -> tuple:
    """
    Returns (category, scope_note).
    Priority: scope > temporal > structural > relational > hidden-variable > falsified
    """
    if sweep.get("scope"):
        # Find which profiles hold and which don't
        wasteful = [r.purpose_name for r in results
                    if r.requirement_id == req.id and r.verdict == "code-wasteful"]
        justified = [r.purpose_name for r in results
                     if r.requirement_id == req.id and r.verdict == "code-justified"]
        note = f"Holds for: {justified} | Wasteful for: {wasteful}"
        return "scope", note

    if sweep.get("temporal"):
        return "temporal", (
            f"Vintage {req.vintage_year}: rule may have been resource-appropriate "
            f"for its era; amortization profile differs across design lives"
        )

    if sweep.get("structural"):
        return "structural", "Governance overhead is the primary cost driver, not physical requirement"

    if sweep.get("relational"):
        return "relational", "Mode-gating relationship between agents changes which path is cheapest"

    if sweep.get("hidden-variable"):
        return "hidden-variable", "High variance in waste_delta across profiles — unmodeled variable present"

    return "falsified", None

# =============================================================================
# 4.  Wired FalsificationMap
# =============================================================================

class FalsificationMapV2:
    """
    FalsificationMap with auto-sweep and ClaimTable integration.
    """

    def __init__(self, system: System,
                 goals: Dict[str, float],
                 purpose_profiles: Optional[List[PurposeProfile]] = None,
                 claim_table: Optional[ClaimTable] = None):
        self.system = system
        self.goals = goals
        self.profiles = purpose_profiles or [seasonal_shelter, cyclical_village, star_temple]
        self.claim_table = claim_table or ClaimTable()
        self.audited: List[AuditedClaim] = []
        self.raw_results: List[FalsificationResult] = []

    def run(self, requirements: List[ProvenanceRequirement]) -> List[AuditedClaim]:
        self.audited = []
        self.raw_results = []

        # Pass 1: run all audits, collect raw results
        for req in requirements:
            for profile in self.profiles:
                audit = audit_requirement_purpose(
                    self.system, req, self.goals, profile
                )
                delta = audit.get("waste_delta")
                if audit["code_plan"] is None and audit["purpose_plan"] is None:
                    verdict = "no-plan-found"
                elif delta is None:
                    verdict = "no-plan-found"
                elif delta > 100:
                    verdict = "code-wasteful"
                else:
                    verdict = "code-justified"

                self.raw_results.append(FalsificationResult(
                    requirement_id=req.id,
                    vintage_year=req.vintage_year,
                    reason_class=req.reason_class,
                    purpose_name=profile.name,
                    design_life_years=profile.design_life_years,
                    code_steps=audit.get("code_steps", 0),
                    purpose_steps=audit.get("purpose_steps", 0),
                    code_waste_heat_J=audit.get("code_waste_heat"),
                    purpose_waste_heat_J=audit.get("purpose_waste_heat"),
                    waste_delta_J=delta,
                    verdict=verdict,
                ))

        # Pass 2: sweep + diagnose per requirement (once per req, not per profile)
        for req in requirements:
            req_results = [r for r in self.raw_results if r.requirement_id == req.id]

            probes = generate_probes(req, self.system, self.goals, self.raw_results)
            sweep = {cat: probe() for cat, probe in probes.items()}
            category, scope_note = diagnose_from_sweep(sweep, self.raw_results, req)

            # Register a claim in the ClaimTable for this requirement
            overall_verdict = (
                "falsified" if category == "falsified"
                else "scope-bound" if category == "scope"
                else "needs-revision"
            )

            def make_test(rq, cat):
                def t():
                    # Claim holds if it is physically justified at ALL profiles
                    return all(
                        r.verdict == "code-justified"
                        for r in self.raw_results
                        if r.requirement_id == rq.id
                    )
                return t

            claim = Claim(
                id=req.id,
                statement=f"Requirement '{req.id}' is physically justified across all purpose profiles",
                test=make_test(req, category),
                origin_conditions={
                    "vintage_year": req.vintage_year,
                    "reason_class": req.reason_class,
                    "profiles_tested": [p.name for p in self.profiles],
                }
            )
            self.claim_table.register(claim)
            claim.run_test()

            # If failed/scope-bound, log revision
            if claim.status == "failed" and category != "falsified":
                rev = self.claim_table.diagnose_failure(
                    claim_id=req.id,
                    category=category,
                    diagnosis=scope_note or f"Sweep identified {category} as primary factor",
                    new_conditions={"sweep": sweep},
                    new_statement=(
                        f"Requirement '{req.id}' is physically justified ONLY under "
                        f"conditions: {scope_note}"
                        if scope_note else None
                    )
                )
                self.claim_table.retest_with_modification(req.id, rev)

            # Attach sweep to each raw result for this req
            for r in req_results:
                self.audited.append(AuditedClaim(
                    result=r,
                    sweep=sweep,
                    category=category,
                    scope_note=scope_note,
                ))

        return self.audited

    def print_full_report(self):
        print("=" * 72)
        print("FALSIFICATION MAP + DIAGNOSTIC SWEEP")
        print("=" * 72)

        seen_reqs = set()
        for ac in self.audited:
            r = ac.result
            if r.requirement_id not in seen_reqs:
                seen_reqs.add(r.requirement_id)
                print(f"\nREQUIREMENT: {r.requirement_id}  "
                      f"vintage={r.vintage_year}  reason={r.reason_class}")
                print(f"  SWEEP: {ac.sweep}")
                print(f"  DIAGNOSIS: category={ac.category}")
                if ac.scope_note:
                    print(f"  SCOPE NOTE: {ac.scope_note}")
                print()
                print(f"  {'Purpose':<35} {'Life':>6}  {'Delta_J':>10}  Verdict")
                print(f"  {'-'*35} {'-'*6}  {'-'*10}  {'-'*15}")

            print(f"  {r.purpose_name:<35} {r.design_life_years:>6}  "
                  f"{str(r.waste_delta_J or 'N/A'):>10}  {r.verdict}")

        print()
        print("CLAIM TABLE:")
        self.claim_table.print_table()
        print()
        print("REVISION LOG:")
        self.claim_table.print_revision_log()

# =============================================================================
# 5.  Demo
# =============================================================================

if __name__ == "__main__":
    from thermo_pm import build_audit_system
    from falsification_map import Source

    system, _, goals = build_audit_system()

    req = ProvenanceRequirement(
        id="footing_thickness_500mm",
        description="Concrete footing must be at least 500mm thick.",
        required_by=["pour_footing_code"],
        physical_justification="soil_bearing_capacity:200",
        vintage_year=1982,
        reason_class="resource-scarcity-of-era",
        sources=[
            Source(
                description="Standard adopted when portland cement was only available binder",
                source_type="industry-standard-doc",
                confidence="secondhand",
                attributed_to="regional builders association",
            ),
            Source(
                description="Inspector oral account: rule never revisited after pozzolanic alternatives available",
                source_type="oral-testimony",
                confidence="firsthand",
            ),
        ],
    )

    fmap = FalsificationMapV2(system, goals)
    fmap.run([req])
    fmap.print_full_report()

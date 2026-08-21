"""
political_financial_vectors_v4.py

v4 tests three predictions from v3:

  TEST_1: Do Operation Charlotte's Web / Catahoula Crunch follow the SAME
          machinery as Operation Metro Surge?
          → ANSWER: NO. They are a DIFFERENT MECHANISM. They do not require
            a fraud case + cluster + opposition media; they require only
            (a) Dem-run city and (b) GOP-controlled state apparatus or
            cooperative GOP governor. Pure agenda-driven enforcement.
            FOF was the FIRST AND ONLY operation chained to a fraud-case
            cascade. The others are direct policy executions.

  TEST_2: Does the cascade machinery operate INVERSELY?
          → ANSWER: YES, with asymmetry. The Trump civil fraud case
            (James/Engoron 2023-2024) had:
              - ringleader party = R
              - prosecuting party = D (NY AG James + Biden DOJ era)
              - opposing-party utility = HIGH (2024 election)
              - cluster = NONE (all-white Trump family + Weisselberg)
              - demographic policy lever = NONE
              - opposition media network = YES (MSNBC/NYT/MSN/CNN)
            Result: intensity ~4 but NO racialization cascade.
            The case became a campaign weapon, NOT a demographic cascade.
            This isolates the cluster variable: same machinery WITHOUT cluster
            → political weaponization without racialization.

  TEST_3: Theranos as bipartisan-capture LIMIT CASE
          → ANSWER: Cross-party board capture so deep that NEITHER side could
            grind the case. Result: intensity 2, framing isolated to
            individual pathology (turtleneck/voice/relationship).
            Confirms C13 (mutual suppression) at maximum capture density.

A new axis is introduced:

  weaponization_type ∈ {
    "demographic_cascade",      # FOF
    "political_targeting",      # Trump civil fraud, James indictment
    "policy_execution",         # Charlotte's Web, Catahoula Crunch
    "individual_pathology",     # Theranos, Madoff
    "suppressed_by_capture",    # Enron, FTX
  }

  These are DIFFERENT mechanisms with different requirements, not points
  on a single cascade-intensity axis. The earlier "intensity 0-5" scale
  conflated them. v4 separates them.

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List


# ---------------------------------------------------------------------------
# WEAPONIZATION TYPOLOGY (new in v4)
# ---------------------------------------------------------------------------

WEAPONIZATION_TYPES = {
    "demographic_cascade": {
        "definition": "Fraud case weaponized to drive demographic policy execution "
                      "against a specific population group.",
        "requires": [
            "fraud_case_with_named_ringleader",
            "non_white_codefendant_cluster matching target demographic",
            "active_demographic_policy_agenda",
            "opposition_media_network_pre_existing_local",
            "ringleader_party != administration_party",
            "downstream_enforcement_operation_launched",
        ],
        "exemplars": ["feeding_our_future"],
    },
    "political_targeting": {
        "definition": "Fraud charge used as direct political weapon against a "
                      "named individual political opponent, no demographic frame.",
        "requires": [
            "named_political_opponent_as_defendant",
            "prosecuting_admin_opposes_defendant",
            "no_codefendant_cluster",
            "no_demographic_policy_lever",
            "explicit_retribution_rhetoric",
        ],
        "exemplars": [
            "trump_civil_fraud_james_engoron",     # D weaponizing R
            "james_mortgage_fraud_halligan",        # R weaponizing D
            "comey_indictment",                     # R weaponizing D
            "trump_classified_docs_smith",          # D weaponizing R
        ],
    },
    "policy_execution": {
        "definition": "Direct enforcement operation against a demographic without "
                      "requiring a fraud-case predicate.",
        "requires": [
            "dem_run_city_in_swing_or_red_state",
            "cooperative_state_government_OR_federal_override",
            "active_demographic_policy_agenda",
        ],
        "exemplars": [
            "operation_charlottes_web",      # NC, no fraud predicate
            "operation_catahoula_crunch",    # LA, no fraud predicate
            "operation_metro_surge",         # MN, FOLLOWED FOF cascade
            "chicago_la_operations",
        ],
        "note": "FOF → Metro Surge is the only chain that connects a fraud "
                "cascade to a policy execution. Charlotte's Web / Catahoula "
                "skipped the cascade step and went direct.",
    },
    "individual_pathology": {
        "definition": "Coverage frames the fraud as an individual moral/character "
                      "failure, NOT a demographic or political phenomenon.",
        "requires": [
            "ringleader_charisma_narrative_available",
            "no_codefendant_cluster",
            "no_party_utility_gradient",
            "OR_bipartisan_elite_capture_blocks_either_side",
        ],
        "exemplars": ["theranos_holmes", "madoff_ponzi", "onecoin_ignatova"],
    },
    "suppressed_by_capture": {
        "definition": "Fraud case where bipartisan donation/capture pattern "
                      "produces mutual suppression. No side can weaponize "
                      "without exposing its own taint.",
        "requires": [
            "ringleader_donated_to_both_parties_substantially",
            "OR_elite_board_spans_both_parties",
            "active_press_coverage_but_no_partisan_amplification",
        ],
        "exemplars": ["enron", "ftx_sbf", "1mdb_jho_low", "theranos_holmes"],
    },
}


# ---------------------------------------------------------------------------
# Three new cases to populate the typology
# ---------------------------------------------------------------------------

@dataclass
class WeaponizationCase:
    case_id: str
    weaponization_type: str
    headline_loss_or_target: str
    target_or_ringleader_party: Optional[str]
    prosecuting_admin_party: str
    has_codefendant_cluster: bool
    has_demographic_lever: bool
    coverage_intensity: int           # 0-5
    political_intensity: int          # 0-5  NEW: separate axis
    racialization_intensity: int      # 0-5  NEW: separate axis
    notes: str = ""


WEAPONIZATION_CASES = [

    # === DEMOGRAPHIC CASCADE (the model FOF case) =========================
    WeaponizationCase(
        case_id="feeding_our_future",
        weaponization_type="demographic_cascade",
        headline_loss_or_target="$250M / Somali community",
        target_or_ringleader_party="D",
        prosecuting_admin_party="bipartisan→R",
        has_codefendant_cluster=True,
        has_demographic_lever=True,
        coverage_intensity=5,
        political_intensity=5,
        racialization_intensity=5,
        notes="ONLY case in dataset where all three intensities = 5. "
              "Coverage, politics, AND demographic cascade all fire together.",
    ),

    # === POLITICAL TARGETING (Trump civil fraud) ==========================
    # This is the INVERSE TEST: same machinery direction reversed, cluster removed
    WeaponizationCase(
        case_id="trump_civil_fraud_james_engoron",
        weaponization_type="political_targeting",
        headline_loss_or_target="$464M penalty (overturned) / Trump Organization",
        target_or_ringleader_party="R",
        prosecuting_admin_party="D",       # NY AG (state-level D) + Biden federal
        has_codefendant_cluster=False,     # Trump family + Weisselberg, all white
        has_demographic_lever=False,
        coverage_intensity=5,
        political_intensity=5,             # massive partisan amplification both sides
        racialization_intensity=0,         # ZERO ethnic descriptors, ZERO demographic frame
        notes="THE KEY INVERSE: ringleader party = R, prosecuting = D, opposition "
              "media (Fox/Newsmax/OAN) primed and grinding, active election cycle "
              "(2024). Coverage intensity = 5, political intensity = 5. "
              "BUT racialization intensity = 0 because no cluster + no demographic "
              "lever. James (Black female D AG) was racialized BY THE OTHER SIDE "
              "instead. This shows cluster is the racialization variable, not "
              "the political-weaponization variable. Political weaponization "
              "operates without race; demographic cascade requires it.",
    ),

    WeaponizationCase(
        case_id="james_mortgage_fraud_halligan",
        weaponization_type="political_targeting",
        headline_loss_or_target="2-count bank fraud / Letitia James",
        target_or_ringleader_party="D",
        prosecuting_admin_party="R",        # Trump 47 DOJ via Halligan EDVA
        has_codefendant_cluster=False,
        has_demographic_lever=False,
        coverage_intensity=4,
        political_intensity=5,
        racialization_intensity=1,          # some racialization (Black female AG) but
                                            # framed as retribution not demographic
        notes="MIRROR of Trump civil fraud case: same machinery, opposite party "
              "direction. R prosecuting D opponent. No cluster, no demographic "
              "lever. Some racialization signal (Black female AG framed as 'corrupt' "
              "on right-wing media) but not a cluster-driven cascade. "
              "Sub-cluster on Comey, Brennan, Powell - all white - shows the "
              "machinery operates without race when no cluster is present.",
    ),

    # === POLICY EXECUTION (without fraud predicate) =======================
    WeaponizationCase(
        case_id="operation_charlottes_web",
        weaponization_type="policy_execution",
        headline_loss_or_target="425+ arrests / undocumented immigrants in NC",
        target_or_ringleader_party=None,
        prosecuting_admin_party="R",
        has_codefendant_cluster=False,      # no defendants, no fraud case
        has_demographic_lever=True,
        coverage_intensity=4,
        political_intensity=4,
        racialization_intensity=4,
        notes="No fraud-case predicate. Triggered by 'sanctuary city' framing in "
              "swing state (Stein D gov, but Whatley R Senate candidate ran on "
              "immigration). Skipped the cascade step entirely. "
              "Same demographic policy lever as FOF→Metro Surge, but executed "
              "directly without a fraud cascade. This proves the cascade is "
              "NOT required for enforcement; it is required for justification "
              "of enforcement against a SPECIFIC named ethnic community.",
    ),

    WeaponizationCase(
        case_id="operation_catahoula_crunch",
        weaponization_type="policy_execution",
        headline_loss_or_target="5000 arrests targeted / undocumented in NOLA",
        target_or_ringleader_party=None,
        prosecuting_admin_party="R",
        has_codefendant_cluster=False,
        has_demographic_lever=True,
        coverage_intensity=4,
        political_intensity=4,
        racialization_intensity=3,
        notes="D mayor Cantrell ironically under indictment for fraud "
              "(romantic-relationship-with-bodyguard angle - exactly the FOF "
              "cascade pattern theoretically AVAILABLE) but the case was "
              "NOT weaponized. Why? "
              "(1) Cantrell's victims are NOT a sympathetic policy group; "
              "(2) Cluster is absent (no co-defendant Somali-equivalent); "
              "(3) Louisiana already has R governor cooperating - no need to "
              "build cascade infrastructure. Policy execution proceeded "
              "via 'sanctuary city' framing instead of demographic-cluster framing.",
    ),

    WeaponizationCase(
        case_id="operation_metro_surge",
        weaponization_type="policy_execution",
        headline_loss_or_target="3,789 arrests / Somali community targeted",
        target_or_ringleader_party=None,
        prosecuting_admin_party="R",
        has_codefendant_cluster=False,
        has_demographic_lever=True,
        coverage_intensity=5,
        political_intensity=5,
        racialization_intensity=5,
        notes="THE EXECUTION STAGE downstream of the FOF cascade. "
              "Direct chain: FOF prosecution (2022-25) → media amplification "
              "(2024-25) → Trump 'garbage' rhetoric (Dec 2025) → Operation Metro "
              "Surge (Dec 4 2025 - Feb 12 2026). "
              "Less than 3% of arrests were actually Somali. The cascade was "
              "rhetorical fuel; the execution was broader. "
              "FOF→MetroSurge is the ONLY documented cascade→execution chain "
              "in this dataset.",
    ),

    # === INDIVIDUAL PATHOLOGY (Theranos limit case) =======================
    WeaponizationCase(
        case_id="theranos_holmes",
        weaponization_type="individual_pathology",
        headline_loss_or_target="$900M / Theranos investors",
        target_or_ringleader_party="bipartisan",
        prosecuting_admin_party="bipartisan",
        has_codefendant_cluster=False,
        has_demographic_lever=False,
        coverage_intensity=4,                # massive coverage
        political_intensity=0,               # ZERO partisan grinding
        racialization_intensity=0,
        notes="LIMIT CASE confirming C13 at maximum capture density. "
              "Board: Kissinger (R), Shultz (R), Mattis (R-aligned, became Trump SecDef), "
              "Perry (D), Nunn (D), Frist (R), Kovacevich (corporate), Foege (corporate). "
              "Investors: Waltons (R), Murdoch (R), DeVos (R, became Trump Ed Sec), "
              "Kissinger (R), Ellison (R-then-Trump-aligned). "
              "Biden visited & praised her 2015. "
              "Neither party could weaponize without indicting its own elite. "
              "Result: coverage went HARD on individual pathology (turtleneck, voice, "
              "Balwani relationship, Stanford dropout narrative). "
              "Political intensity = 0 despite massive coverage. "
              "This is the operating opposite of FOF: same coverage volume, "
              "ZERO political weaponization.",
    ),

    # === SUPPRESSED BY CAPTURE (Enron control) ============================
    WeaponizationCase(
        case_id="enron",
        weaponization_type="suppressed_by_capture",
        headline_loss_or_target="$74B / Enron",
        target_or_ringleader_party="R",
        prosecuting_admin_party="R",
        has_codefendant_cluster=False,
        has_demographic_lever=False,
        coverage_intensity=3,                # major coverage
        political_intensity=1,               # some left-press grinding
        racialization_intensity=0,
        notes="Same dynamic as Theranos but with R single-party capture. "
              "Bush prosecuting his own #1 donor. Ashcroft recused. "
              "Coverage substantial but politically inert.",
    ),
]


# ---------------------------------------------------------------------------
# Test predictions explicitly
# ---------------------------------------------------------------------------

PREDICTIONS_TESTED = {
    "T1_charlottes_web_catahoula_same_pattern": {
        "predicted": "Same FOF-style cascade machinery",
        "observed": "DIFFERENT mechanism: policy_execution, no fraud predicate",
        "model_update": "Add weaponization_type axis. Cascade is one of FIVE "
                        "mechanisms, not a universal scale.",
        "verdict": "PREDICTION_PARTIALLY_FALSIFIED → model refined",
    },
    "T2_inverse_case_d_admin_weaponizing_r_fraud": {
        "predicted": "Same machinery, opposite direction → demographic cascade",
        "observed": "Trump civil fraud case = MAX political intensity, "
                    "ZERO racialization intensity. Cluster is the racialization "
                    "variable; political weaponization operates without it.",
        "model_update": "Separate political_intensity from racialization_intensity. "
                        "They are DIFFERENT axes that can fire independently.",
        "verdict": "PREDICTION_REFINED → cluster isolates racialization "
                   "from political weaponization",
    },
    "T3_theranos_bipartisan_capture_limit": {
        "predicted": "Cross-party capture so deep no cascade can fire either way",
        "observed": "CONFIRMED. Coverage intensity 4, political intensity 0, "
                    "racialization 0. Individual pathology framing dominated.",
        "model_update": "None - C13 holds at max capture density.",
        "verdict": "PREDICTION_CONFIRMED",
    },
}


# ---------------------------------------------------------------------------
# v4 unified scoring (replaces single cascade_intensity)
# ---------------------------------------------------------------------------

def classify_weaponization(case: WeaponizationCase) -> dict:
    """Decompose into three independent axes."""
    return {
        "case": case.case_id,
        "type": case.weaponization_type,
        "coverage": case.coverage_intensity,
        "political": case.political_intensity,
        "racialization": case.racialization_intensity,
        "cluster": case.has_codefendant_cluster,
        "demo_lever": case.has_demographic_lever,
    }


# ---------------------------------------------------------------------------
# New claims from v4
# ---------------------------------------------------------------------------

CLAIMS_V4 = [
    {
        "id": "C18",
        "claim": "Demographic cascade is ONE of five distinct weaponization mechanisms, "
                 "not a universal scale of fraud-case coverage intensity.",
        "evidence": "Charlotte's Web and Catahoula Crunch achieve demographic policy "
                    "execution WITHOUT requiring a fraud-cascade predicate. "
                    "Same downstream outcome (mass arrests), entirely different "
                    "upstream mechanism.",
        "falsifier": "Find a policy_execution operation that REQUIRED a fraud cascade.",
    },
    {
        "id": "C19",
        "claim": "Political intensity and racialization intensity are INDEPENDENT axes "
                 "and can fire separately.",
        "evidence": "Trump civil fraud case: political=5, racialization=0. "
                    "FOF: political=5, racialization=5. "
                    "Theranos: political=0, racialization=0, coverage=4.",
        "falsifier": "Find a case where political and racialization "
                     "intensities are coupled across the dataset.",
    },
    {
        "id": "C20",
        "claim": "Cluster of non-white codefendants is the SINGULAR variable that "
                 "converts political weaponization into racialization cascade.",
        "evidence": "Trump civil fraud case has every other element of FOF "
                    "(opposition media, opposing-party prosecution, election timing) "
                    "but lacks the cluster. Result: zero racialization despite "
                    "maximum political intensity.",
        "falsifier": "Find a high-racialization case (>=4) with no codefendant cluster.",
    },
    {
        "id": "C21",
        "claim": "Cascade→execution chain (FOF→Metro Surge) is RARE; most policy "
                 "executions go direct without requiring a fraud-case justification.",
        "evidence": "Of Trump 47 ICE operations (Metro Surge, Charlotte's Web, "
                    "Catahoula Crunch, Chicago, LA, PARRIS, Swamp Sweep), only "
                    "Metro Surge is directly chained to a named fraud case.",
        "falsifier": "Show another fraud→operation chain in the 2025-2026 window.",
        "implication": "FOF is the EXEMPLAR / pilot case for chain construction, "
                       "not a typical case. Future cases may or may not replicate.",
    },
    {
        "id": "C22",
        "claim": "Bipartisan elite capture produces individual-pathology framing as "
                 "default coverage mode (substitution effect).",
        "evidence": "Theranos: coverage = 4 (high) but political = 0, racialization = 0. "
                    "The narrative MUST go somewhere - and it goes to "
                    "ringleader-as-individual-pathology when partisan grinding is "
                    "blocked from both sides.",
        "falsifier": "Find a high-coverage low-political case where coverage went "
                     "structural/systemic instead of individual-pathology.",
    },
    {
        "id": "C23",
        "claim": "The Mecanism FOF used appears to be a NEW TOOL, not a recurring "
                 "pattern across decades. Earlier large frauds (Madoff, Enron, "
                 "Theranos) did NOT fire demographic cascades despite available "
                 "demographic clusters in some cases.",
        "evidence": "Madoff: Jewish ringleader, Jewish investors, Jewish charity victims "
                    "→ no antisemitic cascade despite available demographic frame. "
                    "Enron: California energy crisis victims, no demographic frame. "
                    "Theranos: Pakistani-American co-defendant (Balwani) - no "
                    "demographic frame. "
                    "FOF (2022-2026) appears to be the first successful demonstration "
                    "of the cascade→execution chain.",
        "falsifier": "Find a pre-2020 fraud case that triggered an ICE-style "
                     "enforcement operation against the codefendants' demographic.",
        "implication": "Either (a) the cascade requires modern partisan media "
                       "infrastructure that didn't exist pre-2015, OR (b) the "
                       "cascade-execution chain is a tool currently being prototyped "
                       "and refined for replication.",
    },
]


def audit_v4():
    print(f"{'case':38s} {'type':25s} {'cov':>3s} {'pol':>3s} {'rac':>3s} clust demo")
    print("-" * 95)
    for c in WEAPONIZATION_CASES:
        r = classify_weaponization(c)
        print(f"{r['case']:38s} {r['type']:25s} "
              f"{r['coverage']:>3d} {r['political']:>3d} {r['racialization']:>3d} "
              f"{str(r['cluster']):>5s} {str(r['demo_lever']):>4s}")


if __name__ == "__main__":
    audit_v4()
    print("\nPredictions tested:")
    for pid, p in PREDICTIONS_TESTED.items():
        print(f"  {pid}: {p['verdict']}")
    print("\nNew claims (C18-C23):")
    for c in CLAIMS_V4:
        print(f"  {c['id']}: {c['claim'][:80]}")

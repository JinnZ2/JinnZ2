"""
political_financial_vectors_v2.py

Extension adding:
  - az_sober_living    (non-white ringleaders, non-white VICTIMS)
  - theranos_holmes    (female ringleader, elite bipartisan board, white victims)
  - 1mdb_jho_low       (Asian foreign ringleader, multi-party donations, $4.5B)
  - pras_michel        (Black co-conspirator in 1MDB, foreign agent angle)

Plus refined predict_intensity() that distinguishes:
  - DEMOGRAPHIC policy lever (immigration, refugees, voter eligibility)
  - REGULATORY policy lever  (crypto, banking, healthcare reimbursement codes)
  Only the demographic lever amplifies racialization.

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal


# Re-import schemas if running standalone
@dataclass
class PoliticalVector:
    ringleader_party_donations: dict = field(default_factory=dict)
    corporate_donor_network: bool = False
    lobbying_spend_usd: Optional[float] = None
    policy_push_downstream: Optional[str] = None
    policy_lever_type: Literal["none", "demographic", "regulatory", "foreign"] = "none"
    opposing_party_utility: float = 0.0
    own_party_distancing: float = 0.0
    notes: str = ""


@dataclass
class CoverageVector:
    intensity: int
    ethnic_descriptors: bool
    lifestyle_proximity_photos: bool
    biggest_in_history_framing: bool
    cluster_of_non_white_codefendants: bool
    romantic_partner_focus: bool
    victim_race_centered: bool = False     # NEW axis - matters for AZ case


@dataclass
class FraudCaseExt:
    case_id: str
    headline_loss_usd: float
    ringleader_name: str
    ringleader_race_or_origin: str
    year_prosecuted: int
    coverage: CoverageVector
    politics: PoliticalVector


# ---------------------------------------------------------------------------
# NEW CASES
# ---------------------------------------------------------------------------

NEW_CASES = [

    # -- ARIZONA SOBER LIVING -- KEY ASYMMETRY TEST ----------------------------
    # Non-white ringleaders, non-white VICTIMS (Native American),
    # bipartisan failure to prosecute → no party utility either direction.
    FraudCaseExt(
        case_id="az_sober_living",
        headline_loss_usd=2_800_000_000,    # 11x FOF
        ringleader_name="~140 indicted; predominantly African-American & Hispanic operators",
        ringleader_race_or_origin="mixed non-white",
        year_prosecuted=2023,
        coverage=CoverageVector(
            intensity=2,
            ethnic_descriptors=False,        # ringleaders NOT racialized in coverage
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,  # despite being 11x FOF
            cluster_of_non_white_codefendants=True,   # the cluster exists
            romantic_partner_focus=False,
            victim_race_centered=True,       # Native American victims foregrounded
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            policy_lever_type="none",
            opposing_party_utility=0.1,      # both parties implicated (Ducey R + Hobbs D)
            own_party_distancing=0.0,
            notes="CRITICAL ASYMMETRY: cluster of non-white codefendants EXISTS but the "
                  "racialization cascade does NOT fire because: "
                  "(1) bipartisan administrative failure → no party utility for either side; "
                  "(2) victims are non-white → racialization frame would harm both major "
                  "parties' coalitions; "
                  "(3) no demographic policy lever to grind (Native voters too few to "
                  "weaponize, refugee/immigration angle absent, Indigenous communities are "
                  "politically inconvenient for both parties). "
                  "$2.8B fraud, 11x FOF scale, never called 'biggest in history.'",
        ),
    ),

    # -- THERANOS -- FEMALE RINGLEADER, ELITE WHITE NETWORK -------------------
    FraudCaseExt(
        case_id="theranos_holmes",
        headline_loss_usd=900_000_000,       # ~$700-900M investor + patient harm
        ringleader_name="Elizabeth Holmes",
        ringleader_race_or_origin="white female",
        year_prosecuted=2022,
        coverage=CoverageVector(
            intensity=2,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=True,  # turtleneck/voice/Balwani relationship
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=True,     # Balwani (Pakistani-American) - asymmetric
            victim_race_centered=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D": "small", "R": "small"},  # mostly via board
            corporate_donor_network=True,
            lobbying_spend_usd=None,
            policy_push_downstream=None,
            policy_lever_type="none",
            opposing_party_utility=0.2,
            own_party_distancing=0.4,
            notes="Board: Kissinger, Shultz, Mattis, Perry, Nunn, Frist - bipartisan elite. "
                  "Investors: Waltons ($150M), Murdoch ($125M), DeVos ($100M), Kissinger "
                  "($3M), Ellison. Biden visited & praised her 2015. "
                  "Despite massive cross-party elite capture, coverage stayed "
                  "individual-pathology-focused (turtleneck, voice, Balwani). "
                  "Note: Sunny Balwani (Pakistani-American, ringleader's partner) "
                  "received NO ethnic descriptors in coverage. Strong null on race + "
                  "partner-of-ringleader.",
        ),
    ),

    # -- 1MDB / JHO LOW -- STRONGEST FALSIFIER YET ----------------------------
    FraudCaseExt(
        case_id="1mdb_jho_low",
        headline_loss_usd=4_500_000_000,    # 18x FOF
        ringleader_name="Low Taek Jho (Jho Low)",
        ringleader_race_or_origin="Malaysian Chinese",
        year_prosecuted=2018,    # indicted; remains fugitive
        coverage=CoverageVector(
            intensity=2,
            ethnic_descriptors=False,         # called 'Malaysian financier' but neutral
            lifestyle_proximity_photos=True,  # yacht, DiCaprio, Miranda Kerr - but glam not racial
            biggest_in_history_framing=True,  # DOJ called it largest kleptocracy case
            cluster_of_non_white_codefendants=True,  # Najib, Riza Aziz, Pras Michel
            romantic_partner_focus=True,      # Miranda Kerr (briefly)
            victim_race_centered=False,       # Malaysian taxpayers - not US frame
        ),
        politics=PoliticalVector(
            ringleader_party_donations={
                "D_via_straw": 21_600_000,    # via Pras Michel → Obama 2012
                "R_via_lobbying": "Broidy/Trump RNC engagement to kill probe",
            },
            corporate_donor_network=True,    # Goldman Sachs, Wolf of Wall Street
            lobbying_spend_usd=None,
            policy_push_downstream="foreign agent / FCPA enforcement",
            policy_lever_type="foreign",     # not domestic demographic
            opposing_party_utility=0.3,
            own_party_distancing=0.5,
            notes="MOST POWERFUL FALSIFIER: Asian foreign ringleader, $4.5B (18x FOF), "
                  "$21.6M illegally funneled to Obama 2012 via straw donors, hired Trump "
                  "RNC deputy finance chair Elliot Broidy to kill investigation, "
                  "cluster of non-white codefendants (Najib, Riza Aziz, Pras Michel), "
                  "lifestyle photos exist, romantic partner exists, DOJ called it "
                  "LARGEST KLEPTOCRACY CASE EVER. "
                  "STILL no racialization cascade. Why: "
                  "policy lever was 'foreign' (FCPA, Goldman penalties), not 'domestic "
                  "demographic.' No domestic voter/immigration policy could be "
                  "leveraged. Coverage stayed financial/celebrity.",
        ),
    ),

    # -- PRAS MICHEL -- BLACK CO-CONSPIRATOR IN FOREIGN INFLUENCE -------------
    FraudCaseExt(
        case_id="pras_michel_foreign_influence",
        headline_loss_usd=21_600_000,        # the funneled amount
        ringleader_name="Prakazrel 'Pras' Michel",
        ringleader_race_or_origin="Black (Haitian-American)",
        year_prosecuted=2023,
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=True,   # Jho Low, Higginbotham
            romantic_partner_focus=False,
            victim_race_centered=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D": 865_000},  # the straw donations themselves
            corporate_donor_network=False,
            policy_push_downstream="foreign agent registration",
            policy_lever_type="foreign",
            opposing_party_utility=0.4,    # GOP could have weaponized Obama-money angle
            own_party_distancing=0.5,
            notes="Black ringleader, funneled $865k of foreign $$ to Obama 2012 campaign, "
                  "celebrity (Fugees), conspirator with Asian foreign national → "
                  "the framing potential was enormous. Coverage stayed legal-procedural. "
                  "No racialization, no 'biggest scandal' framing, no demographic policy "
                  "lever attached. Confirms: cluster + foreign-policy lever ≠ cascade.",
        ),
    ),
]


# ---------------------------------------------------------------------------
# REFINED SCORING MODEL
# ---------------------------------------------------------------------------

def predict_intensity_v2(case: FraudCaseExt) -> int:
    """
    Refined model.
    Key change: policy_lever_type=='demographic' is the multiplier.
    Foreign/regulatory levers do NOT amplify racialization.
    Victim-race-centered shifts framing AWAY from ringleader racialization.
    """
    score = 0
    c = case.coverage
    p = case.politics

    # Base triggers
    cluster = c.cluster_of_non_white_codefendants
    demographic_lever = (p.policy_lever_type == "demographic")
    opposing_amp = (p.opposing_party_utility >= 0.5)

    # The conjunction is the cascade trigger
    if cluster and demographic_lever and opposing_amp:
        score += 5   # full cascade
    elif cluster and demographic_lever:
        score += 4
    elif demographic_lever and opposing_amp:
        score += 2
    elif cluster and opposing_amp:
        score += 2
    elif cluster:
        score += 1
    elif demographic_lever:
        score += 1
    elif opposing_amp:
        score += 1

    # Amplifiers (not triggers)
    if c.romantic_partner_focus:
        score += 1
    if c.lifestyle_proximity_photos and c.cluster_of_non_white_codefendants:
        score += 1   # lifestyle photos only amplify when paired with cluster

    # Dampener: victim race centered displaces ringleader racialization
    if c.victim_race_centered:
        score -= 1

    return max(0, min(score, 5))


# ---------------------------------------------------------------------------
# Combined audit
# ---------------------------------------------------------------------------

ALL_CASES_OBSERVED = {
    # from v1
    "feeding_our_future":            (5, True,  True, "demographic"),
    "madoff_ponzi":                  (1, False, False, "none"),
    "enron":                         (1, False, False, "none"),
    "ftx_sbf":                       (1, False, False, "regulatory"),
    "terra_luna":                    (0, False, False, "none"),
    "celsius_mashinsky":             (0, False, False, "none"),
    "onecoin_ignatova":              (1, False, False, "none"),
    "first_brands_james":            (0, False, False, "none"),
    "girardi":                       (1, False, False, "none"),
    "french_medicare":               (0, False, False, "none"),
    "gray_genetic":                  (0, False, False, "none"),
    # new
    "az_sober_living":               (2, True,  False, "none"),
    "theranos_holmes":               (2, False, False, "none"),
    "1mdb_jho_low":                  (2, True,  True,  "foreign"),
    "pras_michel_foreign_influence": (1, True,  False, "foreign"),
}


def audit_predictions():
    print(f"{'case':35s} {'observed':>8s} {'predict':>7s} {'delta':>6s}  {'lever':<11s} cluster")
    print("-" * 80)
    for case in NEW_CASES:
        pred = predict_intensity_v2(case)
        obs = case.coverage.intensity
        lever = case.politics.policy_lever_type
        clus = case.coverage.cluster_of_non_white_codefendants
        print(f"{case.case_id:35s} {obs:>8d} {pred:>7d} {pred-obs:>+6d}  "
              f"{lever:<11s} {clus}")


# ---------------------------------------------------------------------------
# Updated CLAIMS table
# ---------------------------------------------------------------------------

CLAIMS_V2 = [
    {
        "id": "C7",
        "claim": "Cluster of non-white codefendants alone does NOT trigger cascade if no "
                 "demographic policy lever is active.",
        "falsifier": "Find a case with cluster + non-demographic lever + intensity >= 4.",
        "supporting_cases": ["az_sober_living", "1mdb_jho_low",
                             "pras_michel_foreign_influence"],
    },
    {
        "id": "C8",
        "claim": "Victim race centering DISPLACES ringleader racialization framing.",
        "falsifier": "Find a case with non-white victims foregrounded AND intensity >= 4 "
                     "framed around ringleader ethnicity.",
        "supporting_cases": ["az_sober_living"],
    },
    {
        "id": "C9",
        "claim": "Foreign-policy / FCPA lever does NOT amplify racialization the way "
                 "domestic demographic levers do.",
        "falsifier": "Find a case where foreign lever alone produced intensity >= 4 "
                     "with cluster but no domestic demographic lever.",
        "supporting_cases": ["1mdb_jho_low", "pras_michel_foreign_influence"],
    },
    {
        "id": "C10",
        "claim": "Scale of $1B+ + cluster + multi-party donations + lifestyle photos + "
                 "celebrity nexus + romantic partner ALL combined still fail to trigger "
                 "cascade without a domestic demographic policy lever.",
        "falsifier": "1MDB satisfies all of the above EXCEPT demographic lever. "
                     "Observed intensity = 2.",
        "supporting_cases": ["1mdb_jho_low"],
    },
    {
        "id": "C11",
        "claim": "Indigenous victims represent a politically-inconvenient demographic for "
                 "BOTH parties → no opposing-party utility → no cascade.",
        "falsifier": "Find a fraud against Indigenous victims that received cascade-level "
                     "(intensity >= 4) coverage AND was used as a campaign weapon.",
        "supporting_cases": ["az_sober_living"],
        "notes": "Falsifiability is asymmetric here: a positive case would be highly "
                 "informative; absence continues to support the asymmetry hypothesis "
                 "but does not prove it.",
    },
]


if __name__ == "__main__":
    audit_predictions()
    print("\nCLAIMS_V2:")
    for c in CLAIMS_V2:
        print(f"  {c['id']}: {c['claim'][:80]}...")

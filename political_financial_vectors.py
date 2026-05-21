"""
political_financial_vectors.py

Extension layer for FraudCase: party / financial / corporate utility vectors.

Hypothesis being tested:
  racialization_intensity ~ f(
      non_white_co_defendant_cluster,
      political_utility_gradient,
      timing_proximity_to_election_or_policy_push
  )

Donations alone do NOT predict racialization (Madoff 89% Dem → intensity 0).
Cluster alone does NOT predict racialization (French/Gray Black ringleaders → intensity 0).
Immigrant ringleader alone does NOT predict racialization (Patrick James / First Brands → intensity 0).

The amplification appears at the PRODUCT of these factors, not their sum.

All claims falsifiable. CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Schema extension
# ---------------------------------------------------------------------------

@dataclass
class PoliticalVector:
    """Party / donation / policy-utility vector for a fraud case."""
    # Party association of ringleader's donations
    ringleader_party_donations: dict = field(default_factory=dict)  # {"D": $, "R": $, "dark": $}
    # Corporate / institutional protection layer
    corporate_donor_network: bool = False
    lobbying_spend_usd: Optional[float] = None
    # Whether prosecution / coverage was leveraged for downstream policy
    policy_push_downstream: Optional[str] = None  # e.g. "immigration enforcement", "crypto regulation"
    # Whether opposing party gained from the framing
    opposing_party_utility: float = 0.0   # 0-1
    # Whether ringleader's own party suppressed/distanced
    own_party_distancing: float = 0.0     # 0-1
    # Notes
    notes: str = ""


@dataclass
class CoverageVector:
    """Existing axis - kept compact for join."""
    intensity: int                    # 0-5
    ethnic_descriptors: bool
    lifestyle_proximity_photos: bool
    biggest_in_history_framing: bool
    cluster_of_non_white_codefendants: bool
    romantic_partner_focus: bool


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
# 2. Populated cases
# ---------------------------------------------------------------------------

CASES = [

    # -- THE OUTLIER -----------------------------------------------------------
    FraudCaseExt(
        case_id="feeding_our_future",
        headline_loss_usd=250_000_000,
        ringleader_name="Aimee Bock",
        ringleader_race_or_origin="white female",
        year_prosecuted=2025,
        coverage=CoverageVector(
            intensity=5,
            ethnic_descriptors=True,
            lifestyle_proximity_photos=True,
            biggest_in_history_framing=True,   # claimed despite Madoff $65B, Enron $74B
            cluster_of_non_white_codefendants=True,   # ~70 indictments, heavily Somali
            romantic_partner_focus=True,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D_state_MN": ">$10k_documented_via_codefendants"},
            corporate_donor_network=False,
            lobbying_spend_usd=None,
            policy_push_downstream="Operation Metro Surge - immigration enforcement MN 2025; "
                                   "Somali voting/refugee-policy framing 2026",
            opposing_party_utility=0.95,   # GOP / MAGA media used as central talking point
            own_party_distancing=0.7,      # MN DFL forced to disavow Fateh/Ellison adjacency
            notes="Ellison allegedly received ~$10k from FOF-affiliated individuals ~9 days "
                  "after Dec 2021 meeting (per CAE/Free Beacon). Co-defendants donated to MN "
                  "Democrats. Trump admin cited case to launch Operation Metro Surge late 2025.",
        ),
    ),

    # -- CRYPTO / WHITE+ASIAN RINGLEADERS -------------------------------------
    FraudCaseExt(
        case_id="madoff_ponzi",
        headline_loss_usd=64_000_000_000,
        ringleader_name="Bernard Madoff",
        ringleader_race_or_origin="white (Jewish)",
        year_prosecuted=2009,
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=True,   # legitimately largest Ponzi
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D": 330_000, "R": 11_400},  # ~89% D
            corporate_donor_network=True,
            lobbying_spend_usd=590_000,
            policy_push_downstream=None,    # no policy lever used
            opposing_party_utility=0.2,    # Newsbusters / Fox reminded readers but no policy push
            own_party_distancing=0.6,      # Schumer/Wyden/DSCC returned/donated cash
            notes="89% Dem donations, $100k to DSCC. Despite massive party utility on paper, "
                  "no race cluster + no live policy lever → coverage stayed financial.",
        ),
    ),

    FraudCaseExt(
        case_id="enron",
        headline_loss_usd=74_000_000_000,
        ringleader_name="Kenneth Lay / Jeffrey Skilling",
        ringleader_race_or_origin="white",
        year_prosecuted=2006,
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=True,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"R": 4_350_000, "D": 1_450_000},  # ~73% R of $5.8M
            corporate_donor_network=True,
            lobbying_spend_usd=3_450_000,  # ~49 lobbying wins documented
            policy_push_downstream=None,
            opposing_party_utility=0.4,    # Dems used Bush/Lay link
            own_party_distancing=0.9,      # GOP fully distanced, "Kenny Boy" denied
            notes="$623k to GW Bush career; #1 corporate patron. Despite massive cross-party "
                  "leverage, no race cluster + no live demographic policy lever → "
                  "coverage remained corporate-financial.",
        ),
    ),

    FraudCaseExt(
        case_id="ftx_sbf",
        headline_loss_usd=8_000_000_000,
        ringleader_name="Sam Bankman-Fried",
        ringleader_race_or_origin="white (Jewish)",
        year_prosecuted=2023,
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=True,  # Bahamas penthouse / parents / polycule coverage
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=True,      # Caroline Ellison
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D": 40_000_000, "R_dark": 37_000_000},
            corporate_donor_network=True,
            lobbying_spend_usd=None,
            policy_push_downstream="crypto regulation (used by both parties)",
            opposing_party_utility=0.6,
            own_party_distancing=0.8,
            notes="2nd-largest Dem donor 2022 cycle; ~$37M dark to GOP; $1M to McConnell SLF; "
                  "$750k to McCarthy CLF. Even with massive party utility on BOTH sides, "
                  "no race cluster + no demographic-policy lever → no racialization cascade.",
        ),
    ),

    FraudCaseExt(
        case_id="terra_luna",
        headline_loss_usd=40_000_000_000,
        ringleader_name="Do Kwon",
        ringleader_race_or_origin="Korean",
        year_prosecuted=2024,
        coverage=CoverageVector(
            intensity=0,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="No US political donations of note; foreign ringleader; no party utility; "
                  "no demographic policy lever → zero racialization despite Asian origin.",
        ),
    ),

    FraudCaseExt(
        case_id="celsius_mashinsky",
        headline_loss_usd=25_000_000_000,
        ringleader_name="Alex Mashinsky",
        ringleader_race_or_origin="white (Ukrainian-Israeli-American)",
        year_prosecuted=2024,
        coverage=CoverageVector(
            intensity=0,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="Foreign-born immigrant ringleader, $25B loss, lavish coverage potential — "
                  "no race cluster + no party utility = 0 racialization. Strong null.",
        ),
    ),

    FraudCaseExt(
        case_id="onecoin_ignatova",
        headline_loss_usd=4_500_000_000,
        ringleader_name="Ruja Ignatova",
        ringleader_race_or_origin="Bulgarian-German (white female)",
        year_prosecuted=2017,  # indicted; fugitive
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=True,  # "Cryptoqueen" glamour shots
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="Female ringleader → lifestyle photos appear, BUT no race cluster + "
                  "no party utility → no ethnic descriptors, no policy push.",
        ),
    ),

    # -- CORPORATE FRAUD W/ IMMIGRANT RINGLEADER -- KEY FALSIFIER -------------
    FraudCaseExt(
        case_id="first_brands_james",
        headline_loss_usd=9_000_000_000,
        ringleader_name="Patrick James / Edward James",
        ringleader_race_or_origin="Malaysian-born immigrant",
        year_prosecuted=2026,
        coverage=CoverageVector(
            intensity=0,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=True,  # 17 exotic cars, mansions, celebrity chef
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=True,    # Wall St. lenders, Greensill earlier
            lobbying_spend_usd=None,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="CRITICAL FALSIFIER: Malaysian immigrant ringleader, $9B loss (36x FOF), "
                  "lavish lifestyle, even bipartisan congressional letter on tariff evasion — "
                  "STILL zero racialization. Confirms cluster + party-utility (not race + scale) "
                  "is what triggers the cascade.",
        ),
    ),

    # -- CELEBRITY / LAWYER FRAUD ----------------------------------------------
    FraudCaseExt(
        case_id="girardi",
        headline_loss_usd=18_000_000,
        ringleader_name="Tom Girardi",
        ringleader_race_or_origin="white",
        year_prosecuted=2023,
        coverage=CoverageVector(
            intensity=1,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=True,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=True,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={"D": 7_300_000},  # incl. family + firm
            corporate_donor_network=True,
            lobbying_spend_usd=None,
            policy_push_downstream=None,
            opposing_party_utility=0.5,  # Fox flagged Biden-fundraiser angle
            own_party_distancing=0.6,
            notes="Hosted Biden fundraiser, $87.6k to Newsom alone. Massive Dem ties. "
                  "Even with celebrity wife and lifestyle photos: no race cluster + "
                  "no demographic policy lever → no racialization.",
        ),
    ),

    # -- BLACK RINGLEADERS / NO CLUSTER -- CRITICAL CONTROLS -------------------
    FraudCaseExt(
        case_id="french_medicare",
        headline_loss_usd=197_000_000,
        ringleader_name="Joel Rufus French",
        ringleader_race_or_origin="Black",
        year_prosecuted=2026,
        coverage=CoverageVector(
            intensity=0,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="$197M (LARGER than FOF $250M minus 21%), Black ringleader, 2026 prosecution, "
                  "preyed on disabled veterans → a textbook attack vector for cascade framing. "
                  "Zero racialization. No cluster, no donations, no party utility, "
                  "no blue-state geography, no immigration angle = no cascade. "
                  "MS NOT MN.",
        ),
    ),

    FraudCaseExt(
        case_id="gray_genetic",
        headline_loss_usd=328_000_000,
        ringleader_name="Keith J. Gray",
        ringleader_race_or_origin="Black",
        year_prosecuted=2026,
        coverage=CoverageVector(
            intensity=0,
            ethnic_descriptors=False,
            lifestyle_proximity_photos=False,
            biggest_in_history_framing=False,
            cluster_of_non_white_codefendants=False,
            romantic_partner_focus=False,
        ),
        politics=PoliticalVector(
            ringleader_party_donations={},
            corporate_donor_network=False,
            policy_push_downstream=None,
            opposing_party_utility=0.0,
            own_party_distancing=0.0,
            notes="$328M (31% LARGER than FOF), Black ringleader, 2026. Zero racialization. "
                  "Confirms scale is not the trigger; cluster + party utility are.",
        ),
    ),
]


# ---------------------------------------------------------------------------
# 3. Falsifiable claims emitted to CLAIM_TABLE
# ---------------------------------------------------------------------------

CLAIMS = [
    {
        "id": "C1",
        "claim": "Non-white ringleader is NOT sufficient to trigger racialization cascade.",
        "falsifier": "Find a case with non-white ringleader, no codefendant cluster, "
                     "no party utility, and intensity >= 4.",
        "supporting_cases": ["french_medicare", "gray_genetic", "first_brands_james",
                             "terra_luna", "celsius_mashinsky"],
    },
    {
        "id": "C2",
        "claim": "Massive loss scale is NOT sufficient to trigger racialization cascade.",
        "falsifier": "Find a case where loss > $1B alone drives intensity >= 4 "
                     "without cluster or party utility.",
        "supporting_cases": ["madoff_ponzi", "enron", "ftx_sbf", "terra_luna",
                             "celsius_mashinsky", "first_brands_james"],
    },
    {
        "id": "C3",
        "claim": "Political donations to one party are NOT sufficient.",
        "falsifier": "Find a case with >$1M to one party, no cluster, no policy lever, "
                     "and intensity >= 4.",
        "supporting_cases": ["madoff_ponzi", "enron", "ftx_sbf", "girardi"],
    },
    {
        "id": "C4",
        "claim": "Cascade pattern requires: codefendant cluster of non-white actors "
                 "AND a downstream policy or election utility "
                 "AND opposing-party amplification network.",
        "falsifier": "Find a case meeting all three conditions where intensity < 3, "
                     "OR a case with intensity >= 4 that satisfies none of the three.",
        "supporting_cases": ["feeding_our_future"],
        "controls": ["french_medicare", "gray_genetic", "first_brands_james",
                     "madoff_ponzi", "enron", "ftx_sbf"],
    },
    {
        "id": "C5",
        "claim": "Immigrant ringleader status is NOT sufficient.",
        "falsifier": "Find an immigrant ringleader case with no cluster, no party utility, "
                     "and intensity >= 4.",
        "supporting_cases": ["first_brands_james", "terra_luna", "celsius_mashinsky"],
    },
    {
        "id": "C6",
        "claim": "Timing matters: cases prosecuted DURING an active immigration / "
                 "demographic policy push receive amplified racialization "
                 "IF AND ONLY IF the codefendant cluster matches the policy frame.",
        "falsifier": "Find a case prosecuted during an active demographic policy window "
                     "with no matching cluster that nonetheless got intensity >= 4.",
        "supporting_cases": ["feeding_our_future"],
        "controls": ["french_medicare", "gray_genetic"],  # both 2026, during MN push, no cluster → 0
    },
]


# ---------------------------------------------------------------------------
# 4. Minimal scoring function (deterministic, stdlib only)
# ---------------------------------------------------------------------------

def predict_intensity(case: FraudCaseExt) -> int:
    """
    Falsifiable prediction model.
    If this overfits on FOF and underpredicts elsewhere, the hypothesis is wrong.
    """
    score = 0
    c = case.coverage
    p = case.politics

    if c.cluster_of_non_white_codefendants:
        score += 2
    if p.policy_push_downstream:
        score += 2
    if p.opposing_party_utility >= 0.5:
        score += 1
    if c.romantic_partner_focus:
        score += 1   # amplifier, not trigger
    return min(score, 5)


def audit():
    print(f"{'case':30s} {'observed':>8s} {'predicted':>9s} {'delta':>6s}")
    for case in CASES:
        pred = predict_intensity(case)
        obs = case.coverage.intensity
        print(f"{case.case_id:30s} {obs:>8d} {pred:>9d} {pred-obs:>+6d}")


if __name__ == "__main__":
    audit()

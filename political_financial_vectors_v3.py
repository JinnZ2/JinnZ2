"""
political_financial_vectors_v3.py

Adds three new axes:
  - ProsecutionVector:   who, when, how aggressively, with what conflicts of interest
  - MediaVector:         which outlets carried it, ownership/funding alignment, framing
  - TemporalVector:      administration in power, election proximity, agenda alignment

Core hypothesis being tested at v3:

    cascade_intensity ~ f(
        fraud_attributes,
        prosecution_attributes,
        media_attributes,
        temporal_political_context
    )

    where TIMING (whether prosecution coincides with an in-power agenda
    that wants the case as fuel) and MEDIA OWNERSHIP (whether a partisan
    media network already exists in the local geography) are independent
    multipliers on top of the v2 cascade trigger.

Specifically:
    cascade fires only when:
        ringleader_party ≠ administration_party
        AND opposition_media_network present locally
        AND demographic policy agenda is active for the in-power party
        AND non-white codefendant cluster matches the demographic frame

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List


# ---------------------------------------------------------------------------
# NEW SCHEMAS
# ---------------------------------------------------------------------------

@dataclass
class ProsecutionVector:
    """Who pursued, when, with what posture."""
    investigation_start_year: int
    indictment_year: int
    conviction_year: Optional[int] = None
    # WHO
    investigating_admin_party: Literal["D", "R", "bipartisan", "career"] = "career"
    prosecuting_admin_party: Literal["D", "R", "bipartisan", "transition"] = "career"
    # Conflicts of interest
    prosecutor_received_donations_from_target: bool = False
    prosecutor_recused: bool = False
    regulator_warnings_ignored_years: int = 0     # e.g. Markopolos 9 years, MDE 3 years
    # Posture
    lead_prosecutor_status: Literal["stable", "replaced", "resigned",
                                    "promoted", "sidelined"] = "stable"
    sentencing_severity_vs_baseline: float = 1.0  # 1.0 = typical, >1 = harsher
    notes: str = ""


@dataclass
class MediaVector:
    """How the case was carried, by which networks, with what framing alignment."""
    # Primary carriers (where the story scaled)
    primary_carrier_networks: List[str] = field(default_factory=list)
    # Whether a local partisan media ecosystem already existed to grind the story
    local_opposition_media_network: bool = False
    # Funding behind that network (donor class)
    local_media_funder_party: Optional[Literal["D", "R", "mixed"]] = None
    # Mainstream coverage volume relative to scale (low/medium/high)
    mainstream_coverage_relative_to_scale: Literal["below", "matched", "above"] = "matched"
    # Whether national right-wing or left-wing media adopted as recurring talking point
    national_partisan_amplification: Literal["none", "right", "left", "both"] = "none"
    # Time from indictment to viral national peak (months)
    indictment_to_viral_peak_months: Optional[int] = None
    notes: str = ""


@dataclass
class TemporalVector:
    """The political weather the case was prosecuted into."""
    presidency_at_indictment: Literal["Bush_43", "Obama", "Trump_45", "Biden", "Trump_47"]
    presidency_at_conviction: Optional[Literal["Bush_43", "Obama", "Trump_45",
                                                "Biden", "Trump_47"]] = None
    # Whether the in-power party benefits from amplifying the case
    in_power_party_benefits: bool = False
    # Whether there's an active campaign / election within 12 months
    election_within_12_months: bool = False
    # Active demographic policy agenda at the time
    active_demographic_agenda: Optional[str] = None  # e.g. "immigration enforcement"
    # Ringleader's apparent party affiliation
    ringleader_party_alignment: Optional[Literal["D", "R", "neither", "bipartisan"]] = None
    # Whether the case is *being used* in real-time political rhetoric
    actively_weaponized_in_rhetoric: bool = False
    notes: str = ""


# ---------------------------------------------------------------------------
# Master case extension - selected cases populated across all 3 new axes
# ---------------------------------------------------------------------------

@dataclass
class FraudCaseV3:
    case_id: str
    headline_loss_usd: float
    ringleader_race_or_origin: str
    coverage_intensity_observed: int   # 0-5
    prosecution: ProsecutionVector
    media: MediaVector
    temporal: TemporalVector


CASES_V3 = [

    # =====================================================================
    # FEEDING OUR FUTURE - THE FULL CASCADE
    # =====================================================================
    FraudCaseV3(
        case_id="feeding_our_future",
        headline_loss_usd=250_000_000,
        ringleader_race_or_origin="white female; 90% Somali codefendants",
        coverage_intensity_observed=5,
        prosecution=ProsecutionVector(
            investigation_start_year=2021,
            indictment_year=2022,         # 47 charged Sept 2022 (Biden DOJ)
            conviction_year=2025,         # Bock convicted 2025 under Biden DOJ
            investigating_admin_party="D",      # Biden DOJ / Garland
            prosecuting_admin_party="bipartisan",  # spanned Biden → Trump 47 transition
            prosecutor_received_donations_from_target=False,
            regulator_warnings_ignored_years=3,   # MDE flagged 2019; raids 2022
            lead_prosecutor_status="resigned",    # Joe Thompson resigned Jan 2026
            sentencing_severity_vs_baseline=2.5,  # Bock got 41.5y vs typical 10-15y
            notes="MDE saw red flags 2019. FBI raids March 2022. First charges Sept 2022 "
                  "under Biden/Garland. Garland called it 'largest pandemic relief fraud.' "
                  "70 charged by Jan 2025 (still Biden). Bock convicted 2025. "
                  "Daniel Rosen (Trump appointee) sworn in as MN US Attorney Oct 2025. "
                  "Lead prosecutor Joseph Thompson RESIGNED Jan 2026 as cases politicized. "
                  "Bondi credits Trump admin Dec 2025 for charges mostly filed under Biden.",
        ),
        media=MediaVector(
            primary_carrier_networks=["Alpha News (MN)", "Center of American Experiment",
                                       "Sahan Journal", "Fox News", "Star Tribune",
                                       "MN Reformer", "Townhall", "PJ Media"],
            local_opposition_media_network=True,   # Alpha News + CAE + Freedom Club ecosystem
            local_media_funder_party="R",          # Robert Cummins / Eibensteiner / Bradley Fdn
            mainstream_coverage_relative_to_scale="above",
            national_partisan_amplification="right",
            indictment_to_viral_peak_months=36,    # peaked ~Dec 2025 - Jan 2026
            notes="Alpha News (founded 2015 by MN Freedom Club exec director Alex Kharam, "
                  "bankrolled by GOP donor Robert Cummins) had story-grinding infrastructure "
                  "already in place. Center of American Experiment (chair Eibensteiner = "
                  "former MN GOP chair) ran the Ellison meeting narrative. The case was "
                  "primed in conservative MN media for 3+ years before Trump weaponized it. "
                  "Mainstream (NYT, WaPo) covered it but kept it financial; right-wing local "
                  "+ national amplified the demographic frame.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Biden",
            presidency_at_conviction="Trump_47",  # Bock conviction 2025; sentencing 2026
            in_power_party_benefits=True,    # Trump admin actively benefits from frame
            election_within_12_months=True,  # 2024 cycle + 2026 midterms approaching
            active_demographic_agenda="immigration enforcement / refugee restriction",
            ringleader_party_alignment="D",  # Bock + codefendants donated to MN Dems
            actively_weaponized_in_rhetoric=True,
            notes="Most consequential temporal alignment in the dataset: "
                  "(1) ringleader party = D, prosecuting power = R post-Jan 2025; "
                  "(2) active demographic agenda (immigration); "
                  "(3) cluster matches the agenda (Somali codefendants); "
                  "(4) local opposition media network primed; "
                  "(5) election cycle live (2024 just past, 2026 ahead); "
                  "(6) Trump called Somalis 'garbage' Dec 2025 citing this case; "
                  "(7) Operation Metro Surge launched Dec 4, 2025 citing this case. "
                  "This is the ONLY case in the dataset where ALL temporal factors align.",
        ),
    ),

    # =====================================================================
    # MADOFF - CASCADE BLOCKED BY POLITICAL ALIGNMENT
    # =====================================================================
    FraudCaseV3(
        case_id="madoff_ponzi",
        headline_loss_usd=64_000_000_000,
        ringleader_race_or_origin="white (Jewish)",
        coverage_intensity_observed=1,
        prosecution=ProsecutionVector(
            investigation_start_year=2008,   # confessed Dec 2008
            indictment_year=2009,
            conviction_year=2009,
            investigating_admin_party="bipartisan",  # SEC warned 2000-2008 across both admins
            prosecuting_admin_party="D",       # Obama DOJ took it through
            prosecutor_received_donations_from_target=False,
            regulator_warnings_ignored_years=9,   # Markopolos 2000-2008
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=2.0,
            notes="9 years of Markopolos warnings ignored by SEC under Bush. "
                  "Chris Cox (R, Bush appointee, anti-regulation) headed SEC during cover. "
                  "Self-confessed Dec 2008 - end of Bush 43 admin. "
                  "Indicted and convicted under Obama DOJ. "
                  "AG Ashcroft had recused on Enron for donation conflict; Madoff handled "
                  "after handoff to Obama → no political will for amplification.",
        ),
        media=MediaVector(
            primary_carrier_networks=["WSJ", "NYT", "Bloomberg", "CNN", "Fox Business"],
            local_opposition_media_network=False,  # no NY-specific GOP grind apparatus
            local_media_funder_party=None,
            mainstream_coverage_relative_to_scale="matched",
            national_partisan_amplification="none",  # neither side weaponized
            indictment_to_viral_peak_months=1,
            notes="Coverage was financial-press dominant. Newsbusters/Fox flagged D donations "
                  "but no sustained partisan grinding because both parties had taken Madoff "
                  "money (DSCC kept the cash for months). Asymmetric weaponization impossible.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Obama",     # caught in transition
            presidency_at_conviction="Obama",
            in_power_party_benefits=False,         # Obama doesn't benefit from grinding D donor
            election_within_12_months=False,
            active_demographic_agenda=None,         # 2008 was financial crisis, not demographic
            ringleader_party_alignment="D",
            actively_weaponized_in_rhetoric=False,
            notes="Ringleader party = D, prosecuting party = D → no in-power utility. "
                  "Active national agenda was financial reform (Dodd-Frank), not "
                  "demographic. No demographic cluster to weaponize. "
                  "Magnitude alone ($64B, 256x FOF) does not drive cascade.",
        ),
    ),

    # =====================================================================
    # ENRON - CASCADE BLOCKED BY OWN-PARTY PROSECUTION
    # =====================================================================
    FraudCaseV3(
        case_id="enron",
        headline_loss_usd=74_000_000_000,
        ringleader_race_or_origin="white",
        coverage_intensity_observed=1,
        prosecution=ProsecutionVector(
            investigation_start_year=2001,
            indictment_year=2004,            # Skilling indicted Feb 2004
            conviction_year=2006,
            investigating_admin_party="R",   # Bush DOJ
            prosecuting_admin_party="R",
            prosecutor_received_donations_from_target=True,   # Ashcroft - $4,999 from Enron PAC
            prosecutor_recused=True,         # Ashcroft recused
            regulator_warnings_ignored_years=2,
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=1.5,
            notes="Ken Lay was 'Kenny Boy' to Bush. AG Ashcroft accepted Enron donations as "
                  "MO senator → recused from DOJ probe. Bush admin prosecuting its own "
                  "single largest career patron. Indictments delayed until 2004; "
                  "trial 2006. The same DOJ that took Enron donations was the prosecutor.",
        ),
        media=MediaVector(
            primary_carrier_networks=["WSJ", "NYT", "Washington Post", "CBS", "60 Minutes",
                                       "Democracy Now"],
            local_opposition_media_network=False,
            local_media_funder_party=None,
            mainstream_coverage_relative_to_scale="matched",
            national_partisan_amplification="left",   # Common Dreams, Democracy Now grinded it
            indictment_to_viral_peak_months=4,
            notes="Left-wing outlets (Nation, Democracy Now, Common Dreams) tried to grind "
                  "the Bush-Lay connection but lacked the infrastructure and the moment - "
                  "9/11 + Iraq dominated news cycles 2002-2003. Mainstream press treated "
                  "as corporate-financial story. No demographic frame available.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Bush_43",
            presidency_at_conviction="Bush_43",
            in_power_party_benefits=False,           # GOP doesn't benefit from grinding own donor
            election_within_12_months=True,          # 2004 cycle
            active_demographic_agenda=None,           # post-9/11 was security, not demographic
            ringleader_party_alignment="R",
            actively_weaponized_in_rhetoric=False,
            notes="$74B scale (296x FOF), Bush's #1 career patron prosecuted under Bush DOJ. "
                  "Ringleader party = R, prosecuting party = R → cascade suppressed. "
                  "No demographic cluster, no demographic agenda. "
                  "Opposite of FOF on every political axis except scale.",
        ),
    ),

    # =====================================================================
    # FTX / SBF - CROSS-PARTY DONATIONS NEUTRALIZED CASCADE
    # =====================================================================
    FraudCaseV3(
        case_id="ftx_sbf",
        headline_loss_usd=8_000_000_000,
        ringleader_race_or_origin="white (Jewish)",
        coverage_intensity_observed=1,
        prosecution=ProsecutionVector(
            investigation_start_year=2022,
            indictment_year=2022,
            conviction_year=2023,
            investigating_admin_party="D",
            prosecuting_admin_party="D",
            prosecutor_received_donations_from_target=True,    # most DC pols had received
            prosecutor_recused=False,
            regulator_warnings_ignored_years=1,
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=1.8,
            notes="SBF was 2nd-largest D donor 2022 cycle. Hundreds of recipients across "
                  "both parties returned/donated cash. SDNY prosecuted under Biden DOJ.",
        ),
        media=MediaVector(
            primary_carrier_networks=["WSJ", "NYT", "Bloomberg", "Crypto press"],
            local_opposition_media_network=False,
            local_media_funder_party=None,
            mainstream_coverage_relative_to_scale="matched",
            national_partisan_amplification="none",
            indictment_to_viral_peak_months=1,
            notes="GOP attempted to grind (Cruz tweets, Free Beacon stories) but Salame's "
                  "$24M to GOP via WinRed + Broidy-style dark money to McConnell SLF "
                  "made asymmetric weaponization impossible. Both parties tainted = "
                  "mutual suppression. Same dynamic as Madoff but more explicit.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Biden",
            presidency_at_conviction="Biden",
            in_power_party_benefits=False,
            election_within_12_months=False,
            active_demographic_agenda=None,
            ringleader_party_alignment="bipartisan",   # this is the killer
            actively_weaponized_in_rhetoric=False,
            notes="Bipartisan donation pattern = mutually assured suppression. "
                  "No demographic frame available. Lever was regulatory (crypto) not "
                  "demographic. Romantic partner + lifestyle + scale + party donations "
                  "all present, cascade still does not fire.",
        ),
    ),

    # =====================================================================
    # AZ SOBER LIVING - BIPARTISAN ADMINISTRATIVE FAILURE → NO CASCADE
    # =====================================================================
    FraudCaseV3(
        case_id="az_sober_living",
        headline_loss_usd=2_800_000_000,
        ringleader_race_or_origin="mixed non-white (predominantly Black/Hispanic operators)",
        coverage_intensity_observed=2,
        prosecution=ProsecutionVector(
            investigation_start_year=2019,
            indictment_year=2023,
            conviction_year=2024,    # ongoing - many cases
            investigating_admin_party="bipartisan",   # Ducey (R) → Hobbs (D) both fumbled
            prosecuting_admin_party="D",              # Mayes (D AG) ran the prosecution
            prosecutor_received_donations_from_target=False,
            regulator_warnings_ignored_years=4,       # AHCCCS warnings 2019-2023
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=1.0,
            notes="Both Republican (Ducey) and Democratic (Hobbs) administrations failed "
                  "to act on AHCCCS evidence. Mayes (D AG) took credit for crackdown but "
                  "the fraud spanned both party administrations. "
                  "→ No single party can weaponize without taking blame.",
        ),
        media=MediaVector(
            primary_carrier_networks=["ProPublica", "AZ Center for Investigative Reporting",
                                       "AZCIR", "NPR", "Fox 10 Phoenix", "KJZZ"],
            local_opposition_media_network=False,    # neither party owns the AZ media story
            local_media_funder_party="mixed",
            mainstream_coverage_relative_to_scale="below",  # $2.8B = 11x FOF, far less coverage
            national_partisan_amplification="none",
            indictment_to_viral_peak_months=None,
            notes="Indigenous-press + investigative-nonprofit carried the story. "
                  "No national partisan amplification. Coverage focused on Native victims "
                  "and bureaucratic failure, not ringleader ethnicity. "
                  "11x FOF scale, ~1/10th the national coverage volume.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Biden",
            presidency_at_conviction="Trump_47",
            in_power_party_benefits=False,           # neither party benefits
            election_within_12_months=True,
            active_demographic_agenda="immigration enforcement",
            ringleader_party_alignment="neither",
            actively_weaponized_in_rhetoric=False,
            notes="Active demographic agenda EXISTED (immigration 2025-26) but the cluster "
                  "did NOT match the frame (Black/Hispanic operators, Native victims) → "
                  "no policy lever to attach. "
                  "Indigenous victims are a politically inconvenient demographic for both "
                  "parties → no opposing-party utility. "
                  "Same temporal weather as FOF, completely different cascade outcome - "
                  "because the cluster ≠ the agenda's target.",
        ),
    ),

    # =====================================================================
    # BLACK NFL RINGLEADERS - CONTROL CASES
    # =====================================================================
    FraudCaseV3(
        case_id="french_medicare",
        headline_loss_usd=197_000_000,
        ringleader_race_or_origin="Black",
        coverage_intensity_observed=0,
        prosecution=ProsecutionVector(
            investigation_start_year=2022,
            indictment_year=2024,
            conviction_year=2026,
            investigating_admin_party="bipartisan",
            prosecuting_admin_party="Trump_47",      # sentenced May 2026
            prosecutor_received_donations_from_target=False,
            regulator_warnings_ignored_years=0,
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=1.2,
            notes="Standard healthcare fraud prosecution, MS Northern District. "
                  "No political dimension. Sentenced under Trump 47 admin May 2026 - "
                  "SAME ADMIN as FOF sentencing - but no racialization cascade.",
        ),
        media=MediaVector(
            primary_carrier_networks=["AP", "Insurance Journal", "local Mississippi press",
                                       "DOJ press release"],
            local_opposition_media_network=False,
            local_media_funder_party=None,
            mainstream_coverage_relative_to_scale="below",
            national_partisan_amplification="none",
            indictment_to_viral_peak_months=None,
            notes="DOJ press release recycled. No national partisan amplification despite "
                  "$197M loss + disabled veterans victim profile = ready-made cascade fuel. "
                  "No local opposition media network in MS willing/positioned to grind it.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Biden",
            presidency_at_conviction="Trump_47",
            in_power_party_benefits=False,
            election_within_12_months=False,
            active_demographic_agenda="immigration enforcement",
            ringleader_party_alignment="neither",
            actively_weaponized_in_rhetoric=False,
            notes="PROSECUTED IN THE SAME TEMPORAL WINDOW AS FOF SENTENCING (May 2026). "
                  "Same Trump 47 DOJ, same Bondi/Patel apparatus. Active demographic "
                  "agenda. Ringleader is Black, scale is 80% of FOF, victims are "
                  "disabled veterans (sympathetic). "
                  "STILL no cascade. Differences from FOF: "
                  "(1) Mississippi not Minnesota (no opposition media network); "
                  "(2) no codefendant cluster matching immigration frame; "
                  "(3) ringleader party ≠ D (no party utility); "
                  "(4) victim demographic doesn't help any party's frame.",
        ),
    ),

    FraudCaseV3(
        case_id="gray_genetic",
        headline_loss_usd=328_000_000,
        ringleader_race_or_origin="Black",
        coverage_intensity_observed=0,
        prosecution=ProsecutionVector(
            investigation_start_year=2022,
            indictment_year=2024,
            conviction_year=2026,
            investigating_admin_party="bipartisan",
            prosecuting_admin_party="Trump_47",
            prosecutor_received_donations_from_target=False,
            regulator_warnings_ignored_years=0,
            lead_prosecutor_status="stable",
            sentencing_severity_vs_baseline=1.0,
            notes="Same Trump 47 DOJ that's sentencing Bock. Convicted 2026. "
                  "$328M = 31% LARGER than FOF. Intensity = 0.",
        ),
        media=MediaVector(
            primary_carrier_networks=["TMZ", "Yardbarker", "DOJ", "local CT press"],
            local_opposition_media_network=False,
            local_media_funder_party=None,
            mainstream_coverage_relative_to_scale="below",
            national_partisan_amplification="none",
            indictment_to_viral_peak_months=None,
            notes="Treated as sports-celebrity-fall, not policy fuel.",
        ),
        temporal=TemporalVector(
            presidency_at_indictment="Biden",
            presidency_at_conviction="Trump_47",
            in_power_party_benefits=False,
            election_within_12_months=False,
            active_demographic_agenda="immigration enforcement",
            ringleader_party_alignment="neither",
            actively_weaponized_in_rhetoric=False,
            notes="LARGER than FOF + same temporal window + same DOJ + same active "
                  "demographic agenda → intensity 0. "
                  "Confirms: scale + race + temporal window are not sufficient. "
                  "Missing: cluster matching agenda, party utility, opposition media.",
        ),
    ),
]


# ---------------------------------------------------------------------------
# v3 CASCADE TRIGGER FUNCTION
# ---------------------------------------------------------------------------

def cascade_trigger_v3(case: FraudCaseV3) -> dict:
    """
    Decomposed scoring across the four axes. Returns dict for transparency.
    Each axis contributes independently; cascade = product of activations.
    """
    p = case.prosecution
    m = case.media
    t = case.temporal

    # Axis 1: party-utility gradient
    party_util = 0
    if t.ringleader_party_alignment in ("D", "R"):
        # opposing party is in power → high utility
        opposing_in_power = (
            (t.ringleader_party_alignment == "D" and
             t.presidency_at_conviction in ("Bush_43", "Trump_45", "Trump_47"))
            or
            (t.ringleader_party_alignment == "R" and
             t.presidency_at_conviction in ("Obama", "Biden"))
        )
        if opposing_in_power:
            party_util = 1.0
    elif t.ringleader_party_alignment == "bipartisan":
        party_util = 0.1   # mutual suppression
    elif t.ringleader_party_alignment in ("neither", None):
        party_util = 0.0

    # Axis 2: demographic agenda match
    demo_match = 0
    if t.active_demographic_agenda:
        # cluster must match the agenda
        # (proxy: did the case actually get weaponized into rhetoric?)
        if t.actively_weaponized_in_rhetoric:
            demo_match = 1.0
        else:
            demo_match = 0.2

    # Axis 3: opposition media network
    media_amp = 0
    if m.local_opposition_media_network and m.local_media_funder_party:
        if t.ringleader_party_alignment and \
           m.local_media_funder_party != t.ringleader_party_alignment:
            media_amp = 1.0
        else:
            media_amp = 0.3

    # Axis 4: prosecution coherence (no recusals, no donation conflicts)
    prosec_clean = 1.0
    if p.prosecutor_received_donations_from_target:
        prosec_clean *= 0.5    # conflict suppresses
    if p.prosecutor_recused:
        prosec_clean *= 0.5

    # Cascade = product, scaled to 0-5
    raw_cascade = party_util * demo_match * media_amp * prosec_clean
    predicted = round(raw_cascade * 5)

    return {
        "case": case.case_id,
        "observed": case.coverage_intensity_observed,
        "party_util": round(party_util, 2),
        "demo_match": round(demo_match, 2),
        "media_amp": round(media_amp, 2),
        "prosec_clean": round(prosec_clean, 2),
        "raw_cascade": round(raw_cascade, 3),
        "predicted": predicted,
        "delta": predicted - case.coverage_intensity_observed,
    }


# ---------------------------------------------------------------------------
# Claims emitted to CLAIM_TABLE
# ---------------------------------------------------------------------------

CLAIMS_V3 = [
    {
        "id": "C12",
        "claim": "Ringleader-party / prosecuting-party MISMATCH is necessary "
                 "(but not sufficient) for cascade.",
        "falsifier": "Find a cascade-intensity (>=4) case where ringleader and "
                     "prosecuting-administration share the same party.",
        "supporting_cases": ["enron"],       # R ringleader + R prosecution → no cascade
        "controls": ["feeding_our_future"],   # D ringleader + R prosecution → cascade
    },
    {
        "id": "C13",
        "claim": "Bipartisan donation patterns produce MUTUAL SUPPRESSION: neither side "
                 "can amplify without exposing its own taint.",
        "falsifier": "Find a >=4 cascade case where the ringleader gave substantially "
                     "to both major parties.",
        "supporting_cases": ["ftx_sbf", "madoff_ponzi"],
    },
    {
        "id": "C14",
        "claim": "Local opposition media network (donor-funded, partisan, geographically "
                 "co-located with case) is required infrastructure for cascade.",
        "falsifier": "Find a cascade case with no pre-existing local partisan media "
                     "ecosystem grinding the story prior to national amplification.",
        "supporting_cases": ["feeding_our_future"],   # Alpha News / CAE / Freedom Club
        "controls": ["french_medicare", "gray_genetic"],   # MS + CT have no equivalent
    },
    {
        "id": "C15",
        "claim": "Same DOJ, same temporal window, same active demographic agenda, "
                 "comparable scale, but DIFFERENT cluster/party/media → different cascade.",
        "falsifier": "Show two cases with matching DOJ + temporal + agenda + scale and "
                     "ONE has cascade but the other doesn't, while cluster/party/media "
                     "are also matched.",
        "supporting_cases": ["feeding_our_future", "french_medicare", "gray_genetic"],
        "notes": "FOF, French, and Gray were all moving through Trump 47 DOJ in 2026 "
                 "during Operation Metro Surge. Only FOF cascaded.",
    },
    {
        "id": "C16",
        "claim": "Regulator/prosecutor delay correlates with case size at suppression "
                 "but does not predict cascade direction.",
        "falsifier": "Find a delayed-prosecution case where the delay itself produced "
                     "the cascade (rather than the political utility of the case).",
        "supporting_cases": ["madoff_ponzi", "enron", "feeding_our_future"],
        "notes": "Madoff: 9y SEC delay → no cascade. Enron: 2y → no cascade. "
                 "FOF: 3y MDE delay → cascade. Delay is incidental.",
    },
    {
        "id": "C17",
        "claim": "Prosecution-handoff across administrations (Biden investigation → "
                 "Trump conviction) creates MAXIMUM weaponization opportunity for the "
                 "in-power party at conviction.",
        "falsifier": "Find a cross-admin handoff case where the receiving admin had "
                     "cascade-aligned incentives but the cascade still failed to fire.",
        "supporting_cases": ["feeding_our_future"],
        "controls": ["az_sober_living", "french_medicare", "gray_genetic"],
        "notes": "All four cases prosecuted Biden → Trump 47. Only FOF cascaded "
                 "because only FOF had the matching cluster + media + party-utility stack.",
    },
]


def audit_v3():
    print(f"{'case':30s} {'obs':>4s} {'pred':>5s} {'Δ':>4s}  "
          f"{'party':>6s} {'demo':>5s} {'media':>6s} {'prosec':>6s}")
    print("-" * 80)
    for case in CASES_V3:
        r = cascade_trigger_v3(case)
        print(f"{r['case']:30s} {r['observed']:>4d} {r['predicted']:>5d} "
              f"{r['delta']:>+4d}  {r['party_util']:>6.2f} {r['demo_match']:>5.2f} "
              f"{r['media_amp']:>6.2f} {r['prosec_clean']:>6.2f}")


if __name__ == "__main__":
    audit_v3()
    print("\nClaims:")
    for c in CLAIMS_V3:
        print(f"  {c['id']}: {c['claim'][:75]}")

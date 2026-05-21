"""
political_financial_vectors_v8.py

Kavik's observation:
  The Trump and Biden families exhibit structurally DIFFERENT patterns
  of involvement in the underlying conduct that drew investigation,
  even though both families used L7 at the executive level.

  Trump:  children are NAMED OFFICERS of the entity that committed the
          conduct. Officers, directors, signatories on the financial
          statements found fraudulent.
          → INTERNAL structural involvement

  Biden:  son is the named defendant in his own conduct (gun/tax);
          family receives PERIPHERAL payments from son's foreign business
          contacts; brother (James) has his own separate business
          involvement (Americore); no joint corporate structure.
          → EXTERNAL / peripheral involvement, used in MEDIA to implicate
          the father

Two new axes added:

  AXIS_S: structural_involvement_in_fraud_entity
    0 = no corporate role; named only by association in media
    1 = received payments from associates but no operational role
    2 = had a business role in a separate entity, not the principal's
    3 = co-defendant in civil suit but not officer of principal entity
    4 = named officer/director of principal entity at time of fraud
    5 = signed financial statements / directly authorized fraudulent
        documents

  AXIS_T: temporal_response_orientation
    defensive_preemptive       = pardon issued in response to documented
                                  or imminent oppositional prosecution
    defensive_post_conviction  = pardon after own conviction
    offensive_reward           = pardon used to reward conduct that
                                  benefited the principal
    offensive_retributive      = post-admin-transition prosecution of
                                  PREVIOUS prosecutors / oppositional
                                  figures (NEW: catalog these as L7's
                                  inverse twin)

Headline finding:
  Trump family: structural_involvement = 4-5 across multiple members,
                temporal_response = "Trump regained office" (Path 2) +
                  offensive_retributive against Biden-era prosecutors
                  (Letitia James, Comey, Brennan)
  Biden family: structural_involvement = 1-2 across multiple members,
                temporal_response = defensive_preemptive (in response to
                  Trump's 100+ documented retribution threats during
                  2023-2024 campaign)

  This refines C44: L7 family pardons function as ASYMMETRIC INSURANCE,
  but the orientation differs:
    - Biden used L7 DEFENSIVELY against a documented incoming threat
    - Trump 45 used L7 OFFENSIVELY (rewarding loyalty: Manafort, Stone,
      Bannon) AND defensively (Charles Kushner family tie)
    - Trump 47 uses L7 OFFENSIVELY (Deutsch) + retributive prosecution
      as L7's mirror tool (going after James/Comey/Brennan)

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List
from datetime import date


# ---------------------------------------------------------------------------
# AXIS_S: Structural Involvement
# ---------------------------------------------------------------------------

@dataclass
class StructuralProfile:
    name: str
    family: str
    corporate_role_in_principal_entity: bool
    title_held: Optional[str]
    signed_fraud_documents: bool
    co_defendant_in_civil_case: bool
    co_defendant_in_criminal_case: bool
    peripheral_payment_recipient: bool
    structural_score: int    # 0-5 per axis above
    notes: str


STRUCTURAL_PROFILES = [
    # === TRUMP FAMILY ====================================================
    StructuralProfile(
        name="Donald Trump",
        family="Trump",
        corporate_role_in_principal_entity=True,
        title_held="Chairman / President / CEO (until Jan 2017)",
        signed_fraud_documents=True,
        co_defendant_in_civil_case=True,
        co_defendant_in_criminal_case=True,
        peripheral_payment_recipient=False,
        structural_score=5,
        notes="Principal of Trump Organization. Signed the Statements of "
              "Financial Condition that NY civil case found fraudulent. "
              "Engoron ruling: directly responsible for inflated valuations.",
    ),
    StructuralProfile(
        name="Donald Trump Jr.",
        family="Trump",
        corporate_role_in_principal_entity=True,
        title_held="Executive Vice President (joint mgmt since 2017)",
        signed_fraud_documents=True,
        co_defendant_in_civil_case=True,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=5,
        notes="EVP property development. Testified Nov 2023. Was a trustee "
              "of the Donald J. Trump Revocable Trust holding Trump Org while "
              "father was president. Signed financial statements.",
    ),
    StructuralProfile(
        name="Eric Trump",
        family="Trump",
        corporate_role_in_principal_entity=True,
        title_held="Executive Vice President (joint mgmt since 2017)",
        signed_fraud_documents=True,
        co_defendant_in_civil_case=True,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=5,
        notes="EVP operations oversight. Co-managed Trump Org with brother "
              "during Trump 45 admin. Signed financial statements.",
    ),
    StructuralProfile(
        name="Ivanka Trump",
        family="Trump",
        corporate_role_in_principal_entity=True,
        title_held="Former EVP Development & Acquisitions",
        signed_fraud_documents=False,        # disputed; dropped from later case
        co_defendant_in_civil_case=True,     # originally; dropped on appeal
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=3,
        notes="EVP Development & Acquisitions until 2017. Originally named "
              "defendant; later dropped because statute of limitations ran. "
              "Structural exposure existed but procedurally extinguished.",
    ),

    # === BIDEN FAMILY ====================================================
    StructuralProfile(
        name="Hunter Biden",
        family="Biden",
        corporate_role_in_principal_entity=False,
        title_held=None,
        signed_fraud_documents=False,
        co_defendant_in_civil_case=False,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,   # he IS the principal of his cases
        structural_score=5,
        notes="The principal defendant in his own gun/tax cases. Not a "
              "co-defendant under any other principal. The conduct is his own.",
    ),
    StructuralProfile(
        name="James Biden",
        family="Biden",
        corporate_role_in_principal_entity=False,  # not in Hunter's entities
        title_held="Self-described 'principal' at Americore (disputed)",
        signed_fraud_documents=False,
        co_defendant_in_civil_case=True,     # Tennessee civil fraud suit
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=True,    # CEFC + Americore loans
        structural_score=2,
        notes="Separate business (Americore). Civil fraud suit, no criminal "
              "charges. Received Americore $600k loan, $200k to Joe same day. "
              "Listed in Americore investor materials. Federal probe ongoing "
              "in Western District PA. The conduct is HIS separate venture, "
              "not Joe Biden's.",
    ),
    StructuralProfile(
        name="Sara Jones Biden",
        family="Biden",
        corporate_role_in_principal_entity=False,
        title_held=None,
        signed_fraud_documents=False,
        co_defendant_in_civil_case=False,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=True,
        structural_score=1,
        notes="Joint accounts with James received CEFC payments. No "
              "operational role anywhere documented.",
    ),
    StructuralProfile(
        name="Valerie Biden Owens",
        family="Biden",
        corporate_role_in_principal_entity=False,
        title_held=None,
        signed_fraud_documents=False,
        co_defendant_in_civil_case=False,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=0,
        notes="Political adviser to Joe Biden. No business involvement "
              "documented. Pardon was purely prophylactic.",
    ),
    StructuralProfile(
        name="John T. Owens",
        family="Biden",
        corporate_role_in_principal_entity=False,
        title_held=None,
        signed_fraud_documents=False,
        co_defendant_in_civil_case=False,
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=0,
        notes="No documented business involvement. Pardon prophylactic.",
    ),
    StructuralProfile(
        name="Francis Biden",
        family="Biden",
        corporate_role_in_principal_entity=False,
        title_held=None,
        signed_fraud_documents=False,
        co_defendant_in_civil_case=True,     # several
        co_defendant_in_criminal_case=False,
        peripheral_payment_recipient=False,
        structural_score=2,
        notes="Multiple civil business disputes (Costa Rica solar, "
              "Florida charter schools, FL law firm fee dispute). "
              "Separate ventures, not connected to Hunter's or James's "
              "businesses operationally.",
    ),
]


# ---------------------------------------------------------------------------
# AXIS_T: Temporal Threat / Response Markers
# ---------------------------------------------------------------------------

@dataclass
class TemporalMarker:
    event_date: date
    event_type: Literal["public_threat", "campaign_pledge", "specific_target",
                        "preemptive_pardon", "post_conviction_pardon",
                        "ally_reward_pardon", "retributive_indictment",
                        "retributive_executive_order"]
    actor: str
    target: str
    description: str


TEMPORAL_LEDGER_BIDEN_DEFENSIVE_RESPONSE = [
    # Threats accumulated against Biden family during 2023-2024
    TemporalMarker(
        event_date=date(2023, 6, 12),
        event_type="public_threat",
        actor="Trump",
        target="Joe Biden + 'entire Biden crime family'",
        description="Truth Social all-caps pledge to appoint 'real special "
                    "prosecutor' against 'most corrupt president in history of "
                    "USA, Joe Biden, the entire Biden crime family.' "
                    "Posted same day as Trump's federal indictment unsealed.",
    ),
    TemporalMarker(
        event_date=date(2024, 1, 17),
        event_type="campaign_pledge",
        actor="Trump",
        target="Biden family",
        description="Time magazine interview: warned Bidens 'could face "
                    "multiple criminal prosecutions' unless SCOTUS gives Trump "
                    "immunity.",
    ),
    TemporalMarker(
        event_date=date(2024, 3, 9),
        event_type="campaign_pledge",
        actor="Trump",
        target="Biden + Jan 6 committee + Cheney",
        description="CPAC speech: 'For the liars and cheaters and fraudsters...'"
                    "'Nov 5 their Judgment Day.'",
    ),
    TemporalMarker(
        event_date=date(2024, 6, 7),
        event_type="public_threat",
        actor="Trump",
        target="Biden family",
        description="Repeated pledges to install special prosecutor against "
                    "Bidens. NPR catalogued 100+ retribution threats during "
                    "2024 campaign.",
    ),
    TemporalMarker(
        event_date=date(2024, 11, 5),
        event_type="campaign_pledge",
        actor="Trump",
        target="(election won)",
        description="Trump wins 2024 election. Path 2 to L7 activated: "
                    "becomes president himself.",
    ),

    # Biden's defensive responses
    TemporalMarker(
        event_date=date(2024, 12, 1),
        event_type="preemptive_pardon",
        actor="Biden",
        target="Hunter Biden",
        description="11-year scope preemptive pardon. Reversed prior public "
                    "commitment NOT to pardon. 7 weeks before Trump 47 takes "
                    "office. Delta from initial Trump 'Biden crime family' "
                    "threat: ~18 months.",
    ),
    TemporalMarker(
        event_date=date(2025, 1, 19),
        event_type="preemptive_pardon",
        actor="Biden",
        target="James, Sara, Valerie, John Owens, Francis Biden",
        description="5 family members preemptively pardoned. ONE DAY before "
                    "Trump 47 takes office. Delta from inauguration: 0 days. "
                    "Same day: preemptive pardons for Fauci, Milley, Jan 6 "
                    "committee members - other documented Trump targets.",
    ),
]


TEMPORAL_LEDGER_TRUMP_OFFENSIVE_USE = [
    # Trump 45 L7 use during own term
    TemporalMarker(
        event_date=date(2020, 7, 10),
        event_type="ally_reward_pardon",
        actor="Trump 45",
        target="Roger Stone",
        description="Commutation 1 day before Stone reports to prison. "
                    "Reward for not flipping on Trump during Mueller probe.",
    ),
    TemporalMarker(
        event_date=date(2020, 12, 22),
        event_type="ally_reward_pardon",
        actor="Trump 45",
        target="Paul Manafort, Roger Stone (full), Charles Kushner, 26 others",
        description="Wave of pardons. Manafort, Stone = campaign "
                    "co-conspirators. Charles Kushner = blood-tie to son-in-law. "
                    "Multiple campaign witnesses who didn't flip.",
    ),
    TemporalMarker(
        event_date=date(2021, 1, 20),
        event_type="preemptive_pardon",
        actor="Trump 45",
        target="Steve Bannon",
        description="Pre-trial federal pardon for We Build the Wall fraud. "
                    "Issued in final hours of Trump 45 admin. Co-defendants "
                    "Kolfage et al NOT pardoned, served sentences.",
    ),

    # Trump 47 retributive use - the offensive mirror
    TemporalMarker(
        event_date=date(2025, 1, 20),
        event_type="retributive_executive_order",
        actor="Trump 47",
        target="51 intelligence officials (Hunter Biden laptop letter)",
        description="Within HOURS of inauguration: stripped security clearances "
                    "from 51 former intel officials who signed the 2020 letter "
                    "calling Hunter Biden laptop emails 'Russian information "
                    "operation.' Direct retribution.",
    ),
    TemporalMarker(
        event_date=date(2025, 9, 25),
        event_type="retributive_indictment",
        actor="Trump 47 DOJ (Halligan EDVA)",
        target="James Comey",
        description="Indictment for lying to Congress. Brought by "
                    "newly-appointed US Attorney Lindsey Halligan (Trump "
                    "personal attorney before appointment) after predecessor "
                    "declined to charge.",
    ),
    TemporalMarker(
        event_date=date(2025, 10, 9),
        event_type="retributive_indictment",
        actor="Trump 47 DOJ (Halligan EDVA)",
        target="Letitia James",
        description="Bank fraud + false statements indictment over Virginia "
                    "home loan. The prosecutor who pursued Trump civil fraud "
                    "case becomes the prosecuted. Halligan personally presented "
                    "to grand jury - unusual.",
    ),
    TemporalMarker(
        event_date=date(2025, 9, 19),
        event_type="retributive_executive_order",
        actor="Trump 47",
        target="John Brennan, Letitia James, Comey, Powell investigations",
        description="DOJ opens investigations into named political opponents "
                    "after Trump Truth Social demands.",
    ),
    TemporalMarker(
        event_date=date(2026, 1, 20),
        event_type="post_conviction_pardon",
        actor="Trump 47",
        target="Jacob Deutsch ($50M Hartford mortgage fraud)",
        description="Commutation of 5-year sentence imposed under Biden DOJ. "
                    "No public reason. Cross-admin L7 application.",
    ),
    TemporalMarker(
        event_date=date(2026, 5, 19),
        event_type="retributive_executive_order",
        actor="Trump 47 DOJ",
        target="Southern Poverty Law Center",
        description="DOJ charges SPLC with fraud. Trump-allied talking point "
                    "since 2022 that SPLC 'weaponized' hate-group label.",
    ),
]


# ---------------------------------------------------------------------------
# Differential between families on structural axis
# ---------------------------------------------------------------------------

def structural_summary():
    trump_scores = [p.structural_score for p in STRUCTURAL_PROFILES
                    if p.family == "Trump"]
    biden_scores = [p.structural_score for p in STRUCTURAL_PROFILES
                    if p.family == "Biden"]

    print("=" * 75)
    print("STRUCTURAL_INVOLVEMENT SCORES (0-5)")
    print("=" * 75)
    print(f"{'name':22s} {'family':6s} {'corp_role':>9s} {'signed_docs':>11s} "
          f"{'co_def_civ':>10s} {'periph_pay':>10s} {'score':>5s}")
    print("-" * 80)
    for p in STRUCTURAL_PROFILES:
        print(f"{p.name:22s} {p.family:6s} "
              f"{'Y' if p.corporate_role_in_principal_entity else '.':>9s} "
              f"{'Y' if p.signed_fraud_documents else '.':>11s} "
              f"{'Y' if p.co_defendant_in_civil_case else '.':>10s} "
              f"{'Y' if p.peripheral_payment_recipient else '.':>10s} "
              f"{p.structural_score:>5d}")

    print()
    print(f"Trump family mean structural score: "
          f"{sum(trump_scores)/len(trump_scores):.2f}  "
          f"(n={len(trump_scores)}, range {min(trump_scores)}-{max(trump_scores)})")
    print(f"Biden family mean structural score: "
          f"{sum(biden_scores)/len(biden_scores):.2f}  "
          f"(n={len(biden_scores)}, range {min(biden_scores)}-{max(biden_scores)})")
    print()
    print("INTERPRETATION:")
    print("  Trump family has co-officers at score 5 (signed fraud documents)")
    print("  ACROSS multiple members. The fraud is INTERNAL to a shared entity.")
    print("  Biden family has score 5 only for Hunter (own conduct in his own "
          "case)")
    print("  No two Biden family members are co-officers in a shared fraud entity.")


def temporal_summary():
    print()
    print("=" * 75)
    print("TEMPORAL LEDGER: BIDEN DEFENSIVE L7 RESPONSES")
    print("=" * 75)
    for m in TEMPORAL_LEDGER_BIDEN_DEFENSIVE_RESPONSE:
        print(f"  {m.event_date}  {m.event_type:22s}  {m.actor} → {m.target}")

    print()
    print("=" * 75)
    print("TEMPORAL LEDGER: TRUMP OFFENSIVE L7 + RETRIBUTIVE USE")
    print("=" * 75)
    for m in TEMPORAL_LEDGER_TRUMP_OFFENSIVE_USE:
        print(f"  {m.event_date}  {m.event_type:25s}  {m.actor} → {m.target}")


# ---------------------------------------------------------------------------
# Claims v8
# ---------------------------------------------------------------------------

CLAIMS_V8 = [
    {
        "id": "C47",
        "claim": "Structural involvement axis distinguishes 'family of named officer' "
                 "from 'named officer in same family' - the same surname but very "
                 "different positions inside the fraud entity.",
        "evidence": "Trump family: 4 of 4 members were named officers or co-defendants "
                    "of Trump Organization, the principal fraud entity. Two (Don Jr, "
                    "Eric) co-managed the entity during the period of fraud. "
                    "Biden family: 0 of 6 pardoned members held a corporate role in "
                    "any shared fraud entity. Hunter is principal of his own case; "
                    "James had a SEPARATE business (Americore); others received "
                    "peripheral payments or no documented business involvement.",
    },
    {
        "id": "C48",
        "claim": "Media implication and court-record involvement are different vectors. "
                 "The Biden family case is media-heavy on father-implication; the "
                 "court records list Hunter as principal of his own conduct and James "
                 "as principal of Americore-related conduct. Joe Biden appears in "
                 "no indictment, in either federal or state court.",
        "evidence": "House Oversight produced 'impeachable conduct' report (Aug 2024) "
                    "based on bank records and connections. Hunter's tax case names "
                    "Hunter alone. James's Tennessee civil suit names James. "
                    "Hur classified-docs probe declined to charge Joe Biden. "
                    "Special counsel Weiss prosecuted Hunter, not the father. "
                    "The media-court gap is structural: media speaks of "
                    "implication via association; courts require proof of role.",
    },
    {
        "id": "C49",
        "claim": "Trump family structural involvement is documented in NY civil court "
                 "as direct: Engoron found Donald Trump, Don Jr, Eric Trump, "
                 "Allen Weisselberg, and Jeffrey McConney each individually liable "
                 "for fraud. The fraud entity is shared; the officers are family.",
        "evidence": "Engoron ruling Feb 16 2024: individual liability findings. "
                    "Trump family operated the entity jointly during the fraud "
                    "period 2014-2021. Sons co-managed Trump Org throughout the "
                    "Trump 45 administration.",
    },
    {
        "id": "C50",
        "claim": "Temporal-response orientation distinguishes DEFENSIVE PREEMPTIVE "
                 "from OFFENSIVE REWARD L7 use.",
        "evidence": "Biden Dec 2024 - Jan 2025: 6 family pardons issued within 7 "
                    "weeks of Trump 47 inauguration, in direct response to Trump's "
                    "100+ documented retribution threats during 2023-2024 campaign. "
                    "Trump 45 Dec 2020: 26 pardons including campaign co-conspirators "
                    "(Manafort, Stone) who would not have been preemptively at risk "
                    "from any incoming administration since their cases were closed - "
                    "this is OFFENSIVE REWARD, not defensive insurance. "
                    "Trump 45 Jan 2021 (Bannon): defensive preemptive for ally facing "
                    "active trial. Mixed use within same admin.",
    },
    {
        "id": "C51",
        "claim": "L7 has an OFFENSIVE MIRROR TWIN: retributive indictment by the "
                 "incoming administration of the OUTGOING administration's "
                 "prosecutors. Both tools are activated post-admin-change.",
        "evidence": "Trump 47 within 9 months of inauguration: "
                    "Comey indicted (Sept 2025), James indicted (Oct 2025), "
                    "Brennan/Powell investigations opened, SPLC charged with "
                    "fraud (May 2026). All targets are people who pursued "
                    "Trump or Trump-aligned cases under Biden DOJ. "
                    "The pattern: L7 protects YOUR network on the way out; "
                    "retributive indictment punishes THEIR network on the way in.",
    },
    {
        "id": "C52",
        "claim": "Biden's defensive pardons were RESPONSIVE to documented threat; "
                 "Trump's offensive pardons were ANTICIPATORY of loyalty rewards "
                 "with no comparable incoming-threat signal.",
        "evidence": "Biden documented Trump threats: 100+ public statements naming "
                    "Bidens as targets (NPR/ABC tally). Hur special counsel report "
                    "publicly questioned Biden's cognition - signal that Biden "
                    "himself might be charged. "
                    "Trump 45 Dec 2020: incoming Biden admin had not made "
                    "comparable threats against the people Trump pardoned. The "
                    "pardons were not defensive against documented oppositional "
                    "intent - they were reward for past loyalty.",
    },
    {
        "id": "C53",
        "claim": "Path 2 (becoming the executive again) is the strongest possible "
                 "L7-equivalent because it provides both forward protection AND "
                 "retributive capacity. Path 1 (departing-admin family pardon) "
                 "provides only forward protection.",
        "evidence": "Biden Jan 2025: protected family forward, lost "
                    "retributive capacity. Trump Jan 2025: regained executive office "
                    "→ protected own continued conduct + retributive capacity over "
                    "Biden-era prosecutors. "
                    "Same Path 2 logic worked for Trump 47 to commute Deutsch and "
                    "retributively indict James/Comey/Brennan in same year.",
    },
    {
        "id": "C54",
        "claim": "The DEFENSIVE vs OFFENSIVE distinction is asymmetric in its "
                 "downstream effects on the criminal justice system: defensive "
                 "preemption removes specific people from prosecution; offensive "
                 "use REWIRES prosecutorial selection toward the user's network "
                 "going forward.",
        "evidence": "Biden's defensive pardons did not affect prosecutorial "
                    "selection for unrelated cases. "
                    "Trump 47's pattern shows reshaped prosecutorial selection: "
                    "EDVA, DOJ Weaponization Working Group, $1.776B fund for "
                    "'victims of Biden weaponization,' SPLC charges, "
                    "Comey/James/Brennan investigations - all reorienting which "
                    "people get prosecuted.",
        "implication": "Defensive L7 = symptomatic intervention. "
                       "Offensive L7 + retributive prosecution = systemic intervention.",
    },
    {
        "id": "C55",
        "claim": "Refinement of v5 model: Trump family achieved L7-equivalent "
                 "protection NOT primarily through L7 (only 1 documented pardon "
                 "in family - Charles Kushner) but through executive office "
                 "itself (Path 2) + L3 corporate redistribution (Weisselberg "
                 "absorbing exposure).",
        "evidence": "Trump family inventoried 6 members, 4 with civil convictions, "
                    "1 with criminal conviction, 0 prison time served. "
                    "Mechanisms: appeal-and-reversal ($464M), entity reorganization "
                    "(Weisselberg plea), unconditional discharge (NY hush money), "
                    "judge appointment (FL classified docs - Cannon), election "
                    "winning (DC/GA cases dropped), and one prior L7 (Charles Kushner).",
    },
]


def audit_v8():
    structural_summary()
    temporal_summary()

    print()
    print("=" * 75)
    print("CLAIMS C47-C55")
    print("=" * 75)
    for c in CLAIMS_V8:
        print(f"  {c['id']}: {c['claim'][:75]}")


if __name__ == "__main__":
    audit_v8()

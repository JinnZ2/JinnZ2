"""
political_financial_vectors_v6.py

L7 (pardon/clemency) deep-dive.

Hypotheses tested in v6:

  H1: L7 sub-mechanics differ:
       (a) full pardon           = wipes conviction + penalties forward & backward
       (b) commutation           = wipes remaining sentence only
       (c) preemptive pardon     = covers acts pre-conviction or pre-charge
       (d) FAMILY pardon         = blood-tie access (Hunter Biden, Charles Kushner)
       (e) clemency to ALLY      = political/financial relationship to executive
       (f) clemency to STRANGER  = no documented relationship

  H2: L7 access does NOT transfer across administrations except by:
       - blood tie (only Hunter Biden in dataset)
       - financial network with NEW executive
       - preemptive pardon executed before handoff

  H3: Within a single ringleader entity (Trump Org), L3 (corporate veil)
      pierces ASYMMETRICALLY: the principal (Trump) retains shield, the
      subordinate (Weisselberg) absorbs the criminal exposure.
      The corporate liability shield is REDISTRIBUTIVE, not protective
      for everyone in the org.

  H4: At $50M+ real estate fraud, the ONLY defendants with non-zero
      L7 access in the dataset are white males with relationships to
      the executive's network. Comparable non-white defendants at the
      same fraud scale (Hispanic Mendez family, Black Jean Joseph,
      South Asian Edul Ahmad) received standard sentences with zero
      clemency intervention.

  H5: Hunter Biden as inverse case isolates L4+L7 effects:
       L1 (celebrity): high (presidential son)
       L2 (money): high
       L3 (corporate shield): low (individual charges)
       L4 (bipartisan capture): zero (one-party tie only)
       L5 (own media): low
       L6 (race): high (white)
       L7 (family pardon access): max during Dec 2024
       Result: max-statutory-exposure 42 years → 0 prison via family L7

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, List


# ---------------------------------------------------------------------------
# L7 sub-mechanism schema
# ---------------------------------------------------------------------------

L7_SubMechanism = Literal[
    "full_pardon",
    "commutation",
    "preemptive_pardon",
    "family_pardon",
    "ally_clemency",
    "stranger_clemency",
    "none",
]

L7_RelationshipType = Literal[
    "blood_relative",
    "political_ally_same_party",
    "financial_donor_network",
    "celebrity_advocate_referral",
    "campaign_co_conspirator",
    "criminal_justice_reform_referral",
    "no_documented_relationship",
]


@dataclass
class L7Activation:
    """Detailed L7 record for a clemency action."""
    recipient: str
    granted_by: str                        # president who issued
    granted_year: int
    sub_mechanism: L7_SubMechanism
    relationship_type: L7_RelationshipType
    fraud_loss_usd: Optional[float]
    sentence_imposed_years: Optional[float]
    sentence_served_years: Optional[float]
    restitution_imposed_usd: Optional[float]
    restitution_paid_usd: Optional[float]
    cross_admin: bool = False              # granted across party transition?
    blood_relative_of_president: bool = False
    notes: str = ""


# ---------------------------------------------------------------------------
# L7 activation ledger - documented clemency actions in dataset
# ---------------------------------------------------------------------------

L7_LEDGER = [

    # === HUNTER BIDEN - FAMILY PARDON (Inverse case) =========================
    L7Activation(
        recipient="Hunter Biden",
        granted_by="Biden",
        granted_year=2024,
        sub_mechanism="preemptive_pardon",
        relationship_type="blood_relative",
        fraud_loss_usd=1_400_000,           # unpaid taxes
        sentence_imposed_years=0,            # pardon before sentencing
        sentence_served_years=0,
        restitution_imposed_usd=0,
        restitution_paid_usd=0,
        cross_admin=True,                    # 7 weeks before Trump 47 took office
        blood_relative_of_president=True,
        notes="Convicted June 2024 (gun) + Sept 2024 plea (tax). Max statutory "
              "exposure: 42 years. Expected actual sentence per experts: 16-36 mo. "
              "Pardon issued Dec 1 2024 covers all federal offenses Jan 2014 → "
              "Dec 2024 - a 10-year window. The pardon is ALSO preemptive over "
              "any future charges from incoming Trump admin. "
              "Biden previously committed publicly to NOT pardon Hunter. "
              "L7 was activated DESPITE prior public commitment when admin "
              "transition was imminent. L7 is reversible at will by the holder.",
    ),

    # === CHARLES KUSHNER - FAMILY-ADJACENT PARDON (Trump 45) =================
    L7Activation(
        recipient="Charles Kushner",
        granted_by="Trump",
        granted_year=2020,
        sub_mechanism="full_pardon",
        relationship_type="blood_relative",    # father of son-in-law Jared
        fraud_loss_usd=None,
        sentence_imposed_years=2,
        sentence_served_years=2,
        restitution_imposed_usd=0,
        restitution_paid_usd=0,
        cross_admin=False,
        blood_relative_of_president=False,    # in-law to president's daughter
        notes="Real estate developer convicted 2005 tax evasion + witness "
              "tampering + illegal campaign donations. Son Jared married Ivanka "
              "Trump. Pardoned Dec 2020 (final weeks of Trump 45). "
              "Confirmed as US Ambassador to France 2025. "
              "L7 access via family-by-marriage relationship.",
    ),

    # === PAUL MANAFORT - CAMPAIGN CO-CONSPIRATOR PARDON =======================
    L7Activation(
        recipient="Paul Manafort",
        granted_by="Trump",
        granted_year=2020,
        sub_mechanism="full_pardon",
        relationship_type="campaign_co_conspirator",
        fraud_loss_usd=20_000_000,           # bank and tax fraud, est.
        sentence_imposed_years=7.5,
        sentence_served_years=2,             # home confinement remainder
        restitution_imposed_usd=24_800_000,
        restitution_paid_usd=0,
        cross_admin=False,
        notes="Trump's 2016 campaign chairman. Convicted bank and tax fraud, "
              "FARA violations. Released to home confinement May 2020 (COVID). "
              "Pardoned Dec 2020. Restitution $24.8M wiped.",
    ),

    # === ROGER STONE - ALLY (commutation then pardon) =========================
    L7Activation(
        recipient="Roger Stone",
        granted_by="Trump",
        granted_year=2020,
        sub_mechanism="commutation",          # then full pardon Dec 2020
        relationship_type="political_ally_same_party",
        fraud_loss_usd=None,
        sentence_imposed_years=3.33,          # 40 months
        sentence_served_years=0,              # commutation BEFORE start
        restitution_imposed_usd=0,
        restitution_paid_usd=0,
        cross_admin=False,
        notes="Convicted Nov 2019 lying to Congress + witness tampering. "
              "Commuted July 2020 ONE DAY before reporting to prison. "
              "Full pardon Dec 2020.",
    ),

    # === STEVE BANNON - ALLY PARDON ==========================================
    L7Activation(
        recipient="Steve Bannon",
        granted_by="Trump",
        granted_year=2021,                    # final hours of Trump 45
        sub_mechanism="preemptive_pardon",    # pardoned BEFORE trial
        relationship_type="political_ally_same_party",
        fraud_loss_usd=25_000_000,           # We Build the Wall raised ~$25M
        sentence_imposed_years=0,             # never went to trial federally
        sentence_served_years=0,
        restitution_imposed_usd=0,
        restitution_paid_usd=0,
        cross_admin=True,                     # Jan 20 2021 morning
        notes="Pre-trial federal pardon for We Build The Wall fraud. "
              "L7 wiped federal charges BEFORE conviction. "
              "Co-defendants Brian Kolfage, Andrew Badolato, Timothy Shea "
              "did NOT receive pardon - convicted & sentenced. "
              "Same fraud, same indictment, ONLY the politically-connected "
              "ringleader received L7.",
    ),

    # === JACOB DEUTSCH - WHITE NON-CELEBRITY CLEMENCY (key case) =============
    L7Activation(
        recipient="Jacob Deutsch",
        granted_by="Trump",
        granted_year=2026,
        sub_mechanism="commutation",
        relationship_type="no_documented_relationship",  # publicly unexplained
        fraud_loss_usd=50_000_000,
        sentence_imposed_years=5.17,         # 62 months
        sentence_served_years=0.5,           # partial
        restitution_imposed_usd=10_000,
        restitution_paid_usd=0,
        cross_admin=True,                     # crossed from Biden conviction to
                                              # Trump 47 clemency
        notes="UNUSUAL CASE: no public explanation, no documented donor or "
              "political relationship at the level of Manafort/Stone/Bannon. "
              "Hasidic Hartford developer. Cousin Aron Deutsch also wiped. "
              "If relationship exists, it is not in public record - suggesting "
              "private-network L7 activation. Demonstrates that L7 can fire "
              "without a public political reason, only requiring access to "
              "the executive's clemency-decision network.",
    ),

    # === MICHAEL MILKEN - DELAYED ALLY PARDON =================================
    L7Activation(
        recipient="Michael Milken",
        granted_by="Trump",
        granted_year=2020,
        sub_mechanism="full_pardon",
        relationship_type="financial_donor_network",
        fraud_loss_usd=600_000_000,           # est. junk bond fraud
        sentence_imposed_years=10,
        sentence_served_years=2,
        restitution_imposed_usd=600_000_000,
        restitution_paid_usd=600_000_000,
        cross_admin=False,
        notes="Convicted 1990 securities/reporting fraud. Pardoned 2020. "
              "30-year delay between conviction and pardon. "
              "Decades of financial influence network operating between.",
    ),

    # === RITA CRUNDWELL - STRANGER COMMUTATION (Biden) ========================
    L7Activation(
        recipient="Rita Crundwell",
        granted_by="Biden",
        granted_year=2024,
        sub_mechanism="commutation",
        relationship_type="no_documented_relationship",
        fraud_loss_usd=53_700_000,           # largest US municipal fraud at time
        sentence_imposed_years=19.6,         # ~235 months
        sentence_served_years=4,             # on home confinement post-COVID
        restitution_imposed_usd=53_700_000,
        restitution_paid_usd=0,
        cross_admin=False,
        notes="Part of Biden's mass COVID-confinement commutation batch (1500 "
              "people). Not an individual decision per WH official. "
              "L7 fired via category-rule, not relationship. "
              "Restitution to Dixon, IL wiped.",
    ),

    # === MARC RICH - END-TERM DONOR PARDON ===================================
    L7Activation(
        recipient="Marc Rich",
        granted_by="Clinton",
        granted_year=2001,                    # final day of Clinton presidency
        sub_mechanism="full_pardon",
        relationship_type="financial_donor_network",
        fraud_loss_usd=48_000_000,            # tax evasion
        sentence_imposed_years=0,             # was fugitive in Switzerland
        sentence_served_years=0,
        restitution_imposed_usd=48_000_000,
        restitution_paid_usd=0,
        cross_admin=False,
        notes="Ex-wife was longtime Clinton donor. Fugitive 17 years. "
              "Pardon issued without going through DOJ pardon attorney - "
              "extraordinary by historical standards.",
    ),

    # === HISPANIC MENDEZ FAMILY - NO L7 (control case) ========================
    L7Activation(
        recipient="Stavroula Mendez et al",
        granted_by="(none)",
        granted_year=0,
        sub_mechanism="none",
        relationship_type="no_documented_relationship",
        fraud_loss_usd=27_800_000,
        sentence_imposed_years=11.25,         # 135 months
        sentence_served_years=11.25,          # serving full
        restitution_imposed_usd=21_240_064,
        restitution_paid_usd=None,            # ongoing
        cross_admin=False,
        notes="CONTROL: Miami Hispanic real estate developers, $27.8M mortgage "
              "fraud (about half of Deutsch's scale, but no clemency). "
              "Sentenced 2015. No pardons, no commutations. "
              "Comparable conduct, comparable scale, ZERO L7 access. "
              "Forfeited $35.3M.",
    ),

    # === JEAN JOSEPH (Black, $50M FL real estate fraud) - PENDING =============
    L7Activation(
        recipient="Jean Joseph",
        granted_by="(pending)",
        granted_year=2026,
        sub_mechanism="none",                 # not granted; sentence pending
        relationship_type="no_documented_relationship",
        fraud_loss_usd=50_000_000,            # comparable to Deutsch
        sentence_imposed_years=None,          # pleaded guilty April 2026
        sentence_served_years=0,
        restitution_imposed_usd=None,
        restitution_paid_usd=None,
        cross_admin=False,
        notes="EXACT-MATCH CONTROL for Deutsch case. Black, Boca Raton, "
              "$50M real estate investment fraud, money laundering plea. "
              "Same Trump 47 admin window as Deutsch clemency. "
              "Watch this case for L7 outcome - prediction (per v5 model): "
              "no clemency, full sentence imposed.",
    ),
]


# ---------------------------------------------------------------------------
# Weisselberg sub-decomposition: L3 piercing within an org
# ---------------------------------------------------------------------------

@dataclass
class L3SubPiercing:
    """How the corporate veil pierces for some individuals but not others
    within the same entity."""
    entity: str
    principal: str
    principal_outcome: str
    cooperator_or_subordinate: str
    cooperator_outcome: str
    veil_pierced_for_principal: bool
    veil_pierced_for_subordinate: bool
    mechanism: str


L3_PIERCING_CASES = [
    L3SubPiercing(
        entity="Trump Organization",
        principal="Donald Trump",
        principal_outcome="civil-only liability, $464M penalty REVERSED on appeal, 0 prison",
        cooperator_or_subordinate="Allen Weisselberg",
        cooperator_outcome="2 separate jail terms (5mo + 5mo), 5y probation, "
                           "$2M paid, pleaded guilty to 15 tax crimes",
        veil_pierced_for_principal=False,
        veil_pierced_for_subordinate=True,
        mechanism="Subordinate signed financial documents; principal verbally directed. "
                  "DA Bragg testified Trump and family didn't know — Weisselberg said "
                  "'It was my own personal greed.' This is the COOPERATOR-SHIELD "
                  "mechanism: subordinate absorbs criminal liability in exchange for "
                  "plea deal. Principal's corporate shield holds because the subordinate "
                  "explicitly testified the principal was uninvolved.",
    ),
    L3SubPiercing(
        entity="Enron",
        principal="Kenneth Lay / Jeffrey Skilling",
        principal_outcome="Lay convicted 2006 (died before sentencing); Skilling 24y",
        cooperator_or_subordinate="Andrew Fastow (CFO)",
        cooperator_outcome="6 years prison, 2 counts conspiracy (down from 98)",
        veil_pierced_for_principal=True,
        veil_pierced_for_subordinate=True,
        mechanism="Both principal AND subordinate pierced because Enron's collapse "
                  "destroyed the shield infrastructure. Without an ongoing entity "
                  "to shield behind, principals lose L3 protection too.",
    ),
    L3SubPiercing(
        entity="FTX",
        principal="Sam Bankman-Fried",
        principal_outcome="25 years prison",
        cooperator_or_subordinate="Caroline Ellison, Nishad Singh, Gary Wang",
        cooperator_outcome="2-7 years each, cooperated against SBF",
        veil_pierced_for_principal=True,
        veil_pierced_for_subordinate=True,
        mechanism="Same as Enron — entity collapse pierces L3 universally.",
    ),
    L3SubPiercing(
        entity="Bernard L. Madoff Investment Securities",
        principal="Bernard Madoff",
        principal_outcome="150 years prison (died in custody)",
        cooperator_or_subordinate="Frank DiPascali (top lieutenant)",
        cooperator_outcome="pleaded guilty 2009, died 2015 before sentencing",
        veil_pierced_for_principal=True,
        veil_pierced_for_subordinate=True,
        mechanism="Confession-driven collapse; no operating entity remains. "
                  "Principal pierced because the principal himself confessed.",
    ),
]


# ---------------------------------------------------------------------------
# Comparable real-estate fraud sentencing ladder ($25-100M range)
# ---------------------------------------------------------------------------

@dataclass
class RealEstateFraudComp:
    defendant: str
    race_or_ethnicity: str
    loss_M: float
    sentence_years: Optional[float]
    restitution_imposed_M: Optional[float]
    pardon_or_commutation: bool
    L7_access: bool
    granted_by: Optional[str]
    notes: str


REAL_ESTATE_LADDER = [
    RealEstateFraudComp(
        defendant="Donald Trump (civil)",
        race_or_ethnicity="white",
        loss_M=812,
        sentence_years=0,
        restitution_imposed_M=464,
        pardon_or_commutation=False,
        L7_access=True,
        granted_by="self (became executive)",
        notes="Civil case only - L1+L2+L3 prevented criminal framing entirely",
    ),
    RealEstateFraudComp(
        defendant="Jacob Deutsch",
        race_or_ethnicity="white (Hasidic)",
        loss_M=50,
        sentence_years=5.17,
        restitution_imposed_M=0.01,
        pardon_or_commutation=True,
        L7_access=True,
        granted_by="Trump 47",
        notes="Sentence wiped Jan 2026, no public reason given",
    ),
    RealEstateFraudComp(
        defendant="Charles Fitzgerald",
        race_or_ethnicity="white",
        loss_M=50,
        sentence_years=14,
        restitution_imposed_M=42.7,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="2008 conviction. Standard sentence.",
    ),
    RealEstateFraudComp(
        defendant="Bradley Holcom",
        race_or_ethnicity="white",
        loss_M=50,
        sentence_years=10.1,
        restitution_imposed_M=None,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="121 months. Standard.",
    ),
    RealEstateFraudComp(
        defendant="Stavroula Mendez",
        race_or_ethnicity="Hispanic",
        loss_M=27.8,
        sentence_years=11.25,
        restitution_imposed_M=21.24,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="Miami. Standard sentence. No clemency.",
    ),
    RealEstateFraudComp(
        defendant="Lazaro Mendez",
        race_or_ethnicity="Hispanic",
        loss_M=27.8,
        sentence_years=9,
        restitution_imposed_M=21.24,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="108 months. Standard.",
    ),
    RealEstateFraudComp(
        defendant="Marie Mendez",
        race_or_ethnicity="Hispanic",
        loss_M=27.8,
        sentence_years=4.75,
        restitution_imposed_M=21.24,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="57 months. Standard.",
    ),
    RealEstateFraudComp(
        defendant="Edul Ahmad",
        race_or_ethnicity="South Asian (Guyanese)",
        loss_M=50,
        sentence_years=7,
        restitution_imposed_M=None,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="Brooklyn. Standard.",
    ),
    RealEstateFraudComp(
        defendant="Jean Joseph",
        race_or_ethnicity="Black (Haitian-American)",
        loss_M=50,
        sentence_years=None,                  # pending 2026
        restitution_imposed_M=None,
        pardon_or_commutation=False,
        L7_access=False,
        granted_by=None,
        notes="Florida. Pending sentence April 2026. Per v5 model "
              "prediction: standard 7-12y sentence, no clemency.",
    ),
]


# ---------------------------------------------------------------------------
# Cross-administration L7 transfer analysis
# ---------------------------------------------------------------------------

CROSS_ADMIN_L7 = {
    "Biden → Trump 47 transfers": {
        "Hunter Biden (preemptive pardon Dec 2024)": "BLOCKED future Trump prosecution",
        "Mass commutation batch (Crundwell, Conahan, etc., 1500 people)":
            "Category-rule, not relationship - BLOCKED by category boundary",
        "Pardon attorney process": "Biden bypassed for family/category, "
            "Trump 47 reset pardon attorney with new appointees",
    },
    "Trump 45 → Biden transfers": {
        "Manafort, Stone, Bannon (Trump 45 pardons)":
            "PERMANENT - Biden could not undo",
        "Federal vs state distinction":
            "Manafort still faced NY state charges; pardon only covered federal. "
            "L7 has jurisdictional limits.",
    },
    "Trump 45 → Trump 47 transfers": {
        "Same-party reload": "Trump 47 can pardon people Biden didn't pardon "
            "(Deutsch case 2026). L7 retained across own-party gap.",
        "Same individuals re-pardoned": "Blagojevich got commutation 2020 then "
            "full pardon 2025. L7 stacking across own terms.",
    },
    "Mechanism": "L7 is INDIVIDUAL to the executive; does not transfer across "
                 "administrations. Each new president resets L7 access with their "
                 "own network. Blood ties (Hunter Biden) and category-rules "
                 "(mass commutation) are the only paths that don't require active "
                 "relationship to the current executive.",
}


# ---------------------------------------------------------------------------
# Claims v6
# ---------------------------------------------------------------------------

CLAIMS_V6 = [
    {
        "id": "C31",
        "claim": "L7 (clemency access) is NOT a single mechanism; it decomposes "
                 "into at least 6 sub-mechanisms with different relationship "
                 "requirements and different temporal characteristics.",
        "evidence": "Pardon vs commutation vs preemptive pardon: different scopes. "
                    "Family vs ally vs donor vs stranger relationships: different "
                    "trigger conditions. Bannon: preemptive ally pardon. "
                    "Hunter Biden: preemptive family pardon. Deutsch: post-conviction "
                    "stranger commutation (mechanism unclear).",
    },
    {
        "id": "C32",
        "claim": "L7 access does NOT transfer across administrations except through "
                 "blood-tie preemptive pardons or category-rule mass commutations.",
        "evidence": "Hunter Biden case: preemptive family pardon executed 7 weeks "
                    "before Trump 47 took office. L7 was used FOR future protection. "
                    "Deutsch case: had to wait for Trump 47 to be in office; "
                    "Biden DOJ sentenced him, Biden did NOT clement him, Trump 47 did.",
    },
    {
        "id": "C33",
        "claim": "Corporate liability shield (L3) is REDISTRIBUTIVE within an "
                 "ongoing entity: it concentrates criminal exposure on a subordinate "
                 "while protecting the principal. The shield only universally "
                 "pierces when the entity itself collapses.",
        "evidence": "Trump Org (entity ongoing): Weisselberg pierced, Trump protected. "
                    "Enron, FTX, Madoff (entities collapsed): both principal and "
                    "subordinates pierced.",
    },
    {
        "id": "C34",
        "claim": "At the $25M-100M real estate fraud scale in the 2008-2026 window, "
                 "L7 access correlates with whiteness AND political-network "
                 "proximity, not just one or the other.",
        "evidence": "9 documented $25M+ real estate fraud defendants in v6 ladder. "
                    "Only 2 received L7: Trump (white + executive) and Deutsch "
                    "(white + private network). "
                    "0/3 Hispanic Mendez family received L7. "
                    "0/1 South Asian Ahmad received L7. "
                    "0/1 Black Joseph received L7 (pending). "
                    "Whiteness is necessary but not sufficient (Fitzgerald, "
                    "Holcom both white, both did full sentence).",
        "falsifier": "Find a non-white defendant in 2020-2026 who received "
                     "presidential clemency for $25M+ real-estate or loan fraud.",
    },
    {
        "id": "C35",
        "claim": "Hunter Biden case isolates the FAMILY-PARDON sub-mechanism: "
                 "blood tie at the executive level produces L7 protection that "
                 "operates independently of party-line concerns and survives "
                 "documented prior commitments not to use it.",
        "evidence": "Biden publicly committed multiple times not to pardon Hunter. "
                    "L7 was activated anyway when admin transition was imminent. "
                    "Demonstrates that even publicly-stated L7 self-restrictions "
                    "are not binding when the holder decides to act.",
        "implication": "L7 is the LEAST AUDITABLE protection layer. There is no "
                       "process, appeal, or review mechanism. The decision is "
                       "made by one person with no required justification.",
    },
    {
        "id": "C36",
        "claim": "The cooperator-shield mechanism (Weisselberg pattern) is a known "
                 "and predictable feature of L3, not an accident. The principal's "
                 "L3 shield is MAINTAINED precisely by sacrificing the subordinate's.",
        "evidence": "Weisselberg's plea deal explicitly REQUIRED him to testify "
                    "that Trump and family didn't know. This testimony was "
                    "structurally necessary to preserve the principal's L3. "
                    "Same pattern visible in: Cohen testimony re: Trump, "
                    "Fastow testimony re: Skilling (though entity collapsed).",
    },
    {
        "id": "C37",
        "claim": "Preemptive pardons (Bannon, Hunter Biden) are the SHARPEST L7 "
                 "tool because they wipe ALL exposure including future charges "
                 "for the same conduct, without requiring conviction first.",
        "evidence": "Bannon: federal pardon Jan 2021 wiped We Build the Wall "
                    "exposure BEFORE federal trial. (NY state later charged him "
                    "for same conduct - showing jurisdictional limit.) "
                    "Hunter Biden: 10-year window pardon wiped both convictions "
                    "AND prospective charges.",
        "falsifier": "Find a preemptive pardon that was successfully challenged "
                     "post-issuance.",
    },
    {
        "id": "C38",
        "claim": "L7 is the only protection layer that operates RETROACTIVELY "
                 "on completed prosecutions. All other layers (L1-L6) operate "
                 "PROSPECTIVELY to reduce the probability of charges, conviction, "
                 "or sentence at the time of prosecution.",
        "evidence": "Manafort's $24.8M restitution: wiped 1 year after sentencing. "
                    "Deutsch's 62 months: wiped after starting sentence. "
                    "Crundwell's 19.6y: wiped after years of incarceration + COVID "
                    "home confinement. "
                    "No other layer can reach BACK to a completed sentence and "
                    "zero it out.",
        "implication": "L7 is the strongest protection layer for someone already "
                       "convicted. The other 6 layers don't help post-conviction.",
    },
]


def audit_v6():
    print("=" * 100)
    print("L7 ACTIVATION LEDGER")
    print("=" * 100)
    print(f"{'recipient':25s} {'by':10s} {'yr':5s} {'mech':22s} "
          f"{'rel':28s} {'loss_M':>7s} {'sent_y':>7s}")
    print("-" * 100)
    for a in L7_LEDGER:
        loss = f"{a.fraud_loss_usd/1e6:.1f}" if a.fraud_loss_usd else "-"
        sent = f"{a.sentence_imposed_years:.1f}" if a.sentence_imposed_years else "-"
        print(f"{a.recipient:25s} {a.granted_by:10s} {a.granted_year:>5d} "
              f"{a.sub_mechanism:22s} {a.relationship_type:28s} "
              f"{loss:>7s} {sent:>7s}")

    print("\n" + "=" * 100)
    print("L3 SUB-PIERCING WITHIN ORGANIZATIONS")
    print("=" * 100)
    for c in L3_PIERCING_CASES:
        print(f"\n{c.entity}")
        print(f"  Principal ({c.principal}): "
              f"{'PIERCED' if c.veil_pierced_for_principal else 'PROTECTED'}")
        print(f"    → {c.principal_outcome}")
        print(f"  Subordinate ({c.cooperator_or_subordinate}): "
              f"{'PIERCED' if c.veil_pierced_for_subordinate else 'PROTECTED'}")
        print(f"    → {c.cooperator_outcome}")

    print("\n" + "=" * 100)
    print("$25-100M REAL ESTATE FRAUD LADDER")
    print("=" * 100)
    print(f"{'defendant':28s} {'race':25s} {'loss_M':>7s} {'sent_y':>7s} "
          f"{'rest_M':>7s} {'pardon':>7s}")
    print("-" * 100)
    for r in REAL_ESTATE_LADDER:
        sent = f"{r.sentence_years:.1f}" if r.sentence_years is not None else "pend"
        rest = f"{r.restitution_imposed_M:.1f}" if r.restitution_imposed_M else "-"
        print(f"{r.defendant:28s} {r.race_or_ethnicity:25s} {r.loss_M:>7.1f} "
              f"{sent:>7s} {rest:>7s} {str(r.pardon_or_commutation):>7s}")

    print("\nClaims:")
    for c in CLAIMS_V6:
        print(f"  {c['id']}: {c['claim'][:75]}")


if __name__ == "__main__":
    audit_v6()

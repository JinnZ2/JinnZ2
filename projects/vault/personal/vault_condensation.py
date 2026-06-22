"""
vault_condensation.py  --  machine-legible condensation of vault/personal records.

Source: 33 markdown files in projects/vault/personal/, dates 2026-06-15 to 2026-06-21.
Author: Jinn. Private record. For review with legal counsel.
CC0. stdlib only.

DO NOT run in unsecured environments. Contains sensitive legal/financial data.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, List


# ---------------------------------------------------------------------------
# parties
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Party:
    id: str
    role: str
    notes: str


PARTIES = [
    Party(
        id="AUTHOR",
        role="Jinn — spouse, primary financial contributor, substrate-primary operator",
        notes="6-year marriage. Has paid all bills, trailer down/payments, property "
              "infrastructure under explicit arrangement. Aug 1 hard deadline to secure "
              "new address.",
    ),
    Party(
        id="KEN",
        role="Spouse — lives on brother's property in travel trailer",
        notes="Brother's property is the logistical constraint for water/sanitation. "
              "Agreed-purchase land deal was canceled by Ken without disclosure.",
    ),
    Party(
        id="NICK",
        role="Realtor — independent third party",
        notes="Corroborates: Ken canceled the land deal. Ken denied it to author. "
              "See 20260615-92a64c65.md.",
    ),
]


# ---------------------------------------------------------------------------
# timeline
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TimelineEntry:
    date: str
    entry_id: str
    summary: str
    legal_weight: str   # HIGH / MEDIUM / CONTEXT


TIMELINE: List[TimelineEntry] = [

    TimelineEntry(
        date="2020–2023 (approx)",
        entry_id="BACKGROUND",
        summary="6 years functional — healthy, transparent, capable relationship. "
                "Pre-marital assurances given repeatedly (before dating, day before "
                "wedding, day of wedding, after marriage): pre-marital holdings would "
                "not be an issue. Retracted ~6 years in with no triggering change in "
                "author's conduct. Explicit arrangement: author pays all bills + "
                "trailer down payment + ongoing payments so Ken can accumulate in his "
                "personal account toward property purchase.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2023–2026 (approx, 2.5 years)",
        entry_id="DEPRIVATION_PERIOD",
        summary="Trailer has no water connection; access only through brother's house. "
                "Brother objects to water storage. Laundry promised but unavailable, "
                "contingent on brother's mood. New allergies developed from animal waste "
                "exposure throughout the house. Multiple agreed move-out dates (spring "
                "year 1, year 2, etc.) missed with new excuses each time.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-15",
        entry_id="20260615-92a64c65",
        summary="Realtor conflict: Nick (realtor) states Ken canceled the land deal. "
                "Ken denied it to author. Third-party corroboration established.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-16",
        entry_id="20260616-b0ce929e (consolidated)",
        summary="First documented call record. Financial exposure table built. "
                "Driving call: second sworn promise broken; Ken stated 'time apart' "
                "then reversed. Manufacturing contract frame documented: asset "
                "specificity, hold-up problem, acceptance by conduct, termination "
                "for convenience vs. cause. Even charitable reading = convenience "
                "termination = liability attaches.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-17",
        entry_id="20260617-298307a5",
        summary="Proof demand / NDA entry. Father, brother, mother, attorney all "
                "consulted. NDA intact. Ken demanded proof of NDA compliance. "
                "NDA logical trap documented: false dilemma ('if you disclosed X "
                "you'd break NDA anyway').",
        legal_weight="MEDIUM",
    ),

    TimelineEntry(
        date="2026-06-18 (morning)",
        entry_id="20260618-dc49c637",
        summary="Validator sequence: cousin → counselor/desk-person → uncle.",
        legal_weight="CONTEXT",
    ),

    TimelineEntry(
        date="2026-06-18 ~morning",
        entry_id="20260618-ee2a0373",
        summary="Uncle reached. New proof demand generated. Discrepancy confronted → "
                "'just asking questions' → redirect to his needs.",
        legal_weight="MEDIUM",
    ),

    TimelineEntry(
        date="2026-06-18 11:13 CDT",
        entry_id="20260618-7a861500",
        summary="DV hotline contacted via text. Timestamped.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-18 11:35 CDT",
        entry_id="20260618-a2ef9a88",
        summary="Stated motive (Ken's own words): fear of property liability, not "
                "lack of understanding.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-18 12:07 CDT",
        entry_id="20260618-03aba919",
        summary="Researchers demand (5th validator). Full day sequence documented.",
        legal_weight="MEDIUM",
    ),

    TimelineEntry(
        date="2026-06-18 17:45 CDT",
        entry_id="20260618-64234f41",
        summary="Day close: proof demand stopped when VA loan 'free house' benefit "
                "was priced out. Confirms instrumental motive, not trust motive.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-18 18:15 CDT",
        entry_id="20260618-9c110b63",
        summary="Boundary stated: 'tell the realtor the truth.' Structural, not "
                "explanatory. Three separate things: understanding / boundary / "
                "structural consequence.",
        legal_weight="MEDIUM",
    ),

    TimelineEntry(
        date="2026-06-18 18:48 CDT",
        entry_id="20260618-ec273276",
        summary="Resolution structure: Aug 1 hard deadline (not negotiable). "
                "Stop absorbing costs. Step back from managing his narrative "
                "to his support system.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-19 16:10 CDT",
        entry_id="20260619-528ae39a",
        summary="Victim narrative spread across ≥4 parties: neighbor, dad, uncle, "
                "cousin. None buying it.",
        legal_weight="MEDIUM",
    ),

    TimelineEntry(
        date="2026-06-21",
        entry_id="20260621-934ead31",
        summary="Pattern log finalized: 9 patterns in legal format with [V]/[P]/[OBS] "
                "annotations. DATE fields pending anchor.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-21",
        entry_id="20260621-59472a89",
        summary="Dollar amounts documented: $27,122 receipted infrastructure + "
                "~$6–7k trailer + layaway TBD + labor TBD. Running floor ~$33–34k.",
        legal_weight="HIGH",
    ),

    TimelineEntry(
        date="2026-06-21",
        entry_id="20260621-8a715083",
        summary="Living conditions, Pattern 9, land sabotage. 2.5-year water "
                "deprivation, new health conditions, broken move-out promises, "
                "concealed land deal cancellation (corroborated by Nick).",
        legal_weight="HIGH",
    ),
]


# ---------------------------------------------------------------------------
# behavioral patterns  (legal format)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pattern:
    number: int
    name: str
    mechanism: str
    example: str
    discrepancy: str
    dates_needed: bool = True


PATTERNS: List[Pattern] = [

    Pattern(
        number=1,
        name="Reversal after stated request",
        mechanism="States a request → author reorganizes around it → he reverses → "
                  "discrepancy denied.",
        example="[V] 'I want space' (stated 2 days). Author reorganized. "
                "[V] After: 'That's not what I wanted' / 'I don't want space.'",
        discrepancy="Plans executed during stated window; denial occurs after.",
    ),

    Pattern(
        number=2,
        name="Constraint stated as proxy, contradicted by own behavior",
        mechanism="Names a constraint → constraint contradicted by his own measurable "
                  "actions.",
        example="[V] Didn't want to go to work 'just for gas money.' "
                "[OBS] Agreed-purchase house is CLOSER than houses he was excited "
                "about. Same period: 60–80 mi/weekend on social trips, friend favors, "
                "2–3 store/soda/coffee runs daily.",
        discrepancy="If gas cost were the real constraint, discretionary mileage "
                    "would not exceed the 21 additional miles cited as prohibitive.",
    ),

    Pattern(
        number=3,
        name="'You don't listen' deployed against verbatim repetition",
        mechanism="Author repeats his exact words → states interpretation → asks him "
                  "to clarify → he cannot → returns to 'you don't listen.'",
        example="[OBS] Author repeated words verbatim and stated how she was taking "
                "them. Asked him to state what he meant differently. No alternative "
                "meaning provided. [V] 'You never listen to me' (loop).",
        discrepancy="'You don't listen' deployed against demonstrated listening.",
    ),

    Pattern(
        number=4,
        name="Performative deference after confrontation",
        mechanism="Confronted on unanswerable contradiction → flips to "
                  "passive/permission-seeking mode. Severity scales with how "
                  "unanswerable the contradiction is.",
        example="[V] Immediately after confrontation: 'Can I go take a shower now?'",
        discrepancy="Pattern recurs specifically after contradictions are named; "
                    "assessed as performance, not genuine deference.",
    ),

    Pattern(
        number=5,
        name="Accountability reframed as his need to 'verify'",
        mechanism="Recasts deflection as a legitimate need to check reality.",
        example="[V] 'I just wanted to make sure I wasn't living a lie.'",
        discrepancy="Author's position: trust implicitly until accused without basis; "
                    "unfounded accusation triggers investigation because she knows "
                    "her own record.",
    ),

    Pattern(
        number=6,
        name="Trust reversal / pre-marriage assurances retracted",
        mechanism="Assured pre-marriage that pre-marital holdings would not be an "
                  "issue → retracted after six years with no triggering change in "
                  "author's conduct.",
        example="[P] Assurances given before dating, day before wedding, day of "
                "wedding, after marriage. Issue raised only ~6 years in.",
        discrepancy="No triggering change. Assurances were recurring and explicit.",
    ),

    Pattern(
        number=7,
        name="Third-party characterization",
        mechanism="Characterizes author to others in terms contradicted by the "
                  "actual arrangement.",
        example="[V/P] Told his uncle author was 'after' the money they agreed to "
                "place in his account for him to hold.",
        discrepancy="That account exists because of the explicit arrangement (author "
                    "pays all expenses so he can accumulate). His characterization "
                    "inverts the actual arrangement.",
    ),

    Pattern(
        number=8,
        name="Follow-through asymmetry",
        mechanism="Author's stated commitments met in full; his missed on several.",
        example="[OBS] Every bill/obligation author committed to: paid. "
                "[OBS] His committed obligations: fell short on several.",
        discrepancy="Asymmetry is systematic, not occasional. "
                    "(Specific instances + dates: pending.)",
    ),

    Pattern(
        number=9,
        name="Land sabotage / concealment",
        mechanism="Solid agreement reached on purchasing land. Ken unilaterally "
                  "canceled and concealed it. When discovered, lied and pivoted to "
                  "demanding proof of identity/military service (pre-existing boundary).",
        example="[OBS] Nick (realtor) states Ken canceled. Ken denied to author. "
                "Upon being informed of author's intent to move forward: accused her "
                "of 'abandoning' him and 'not loving' him.",
        discrepancy="Corroborated by independent third party (Nick). "
                    "See 20260615-92a64c65.md.",
    ),
]


# ---------------------------------------------------------------------------
# financial table
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FinancialItem:
    description: str
    amount: str
    status: str
    source_entry: str


FINANCIAL_TABLE: List[FinancialItem] = [
    FinancialItem(
        description="Infrastructure for agreed-purchase property",
        amount="$27,122",
        status="DOCUMENTED — receipts in hand",
        source_entry="20260621-59472a89.md",
    ),
    FinancialItem(
        description="Travel trailer (down payment + payments, titled in his name)",
        amount="~$6,000–$7,000",
        status="PENDING — final tally required",
        source_entry="20260621-59472a89.md",
    ),
    FinancialItem(
        description="Layaway parcels",
        amount="TBD",
        status="PENDING — amount to be tallied",
        source_entry="20260621-59472a89.md",
    ),
    FinancialItem(
        description="Labor: project management, county coordination, scheduling",
        amount="TBD",
        status="PENDING — separate documentation log",
        source_entry="20260621-59472a89.md",
    ),
]

FINANCIAL_FLOOR_NOTE = (
    "Running documented floor: $27,122 + $6–7k = ~$33,000–$34,000 "
    "before layaway and labor. The $27,122 is receipted, not estimated."
)


# ---------------------------------------------------------------------------
# legal framework
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LegalFrame:
    name: str
    claim: str
    source_entry: str


LEGAL_FRAMES: List[LegalFrame] = [

    LegalFrame(
        name="Manufacturing contract / asset specificity",
        claim="$27,122+ invested in infrastructure specific to an agreed-purchase "
              "property. Near-zero value outside this contract. Relationship-specific "
              "tooling = hold-up problem. Reimbursement claim is receipted, "
              "not speculative.",
        source_entry="20260616-3ad24af5.md",
    ),

    LegalFrame(
        name="Acceptance by conduct",
        claim="Agreement lived for years without formal execution. Conduct on both "
              "sides constituted acceptance. Termination cannot retroactively "
              "void performance already rendered.",
        source_entry="20260616-3ad24af5.md",
    ),

    LegalFrame(
        name="Termination for convenience vs. cause",
        claim="Even the most charitable reading of events = termination for "
              "convenience (no cause attributable to author). Liability attaches "
              "regardless.",
        source_entry="20260616-3ad24af5.md",
    ),

    LegalFrame(
        name="Mutual exclusivity of savings claim",
        claim="He cannot claim the accumulated savings are solely his AND that "
              "author's payments toward his-titled assets during that period carry "
              "no claim. If savings are solely his → reimbursement owed for "
              "payments made under the explicit arrangement. If arrangement is "
              "honored → savings are subject to equitable division.",
        source_entry="20260621-bda2a65b.md",
    ),

    LegalFrame(
        name="Pre-marital assurance retraction",
        claim="Explicit, repeated assurances (pre-dating through post-marriage) "
              "that pre-marital holdings would not be an issue. Retracted ~6 years "
              "in with no triggering change in author's conduct.",
        source_entry="20260621-934ead31.md (Pattern 6)",
    ),

    LegalFrame(
        name="Living conditions / habitability",
        claim="2.5-year documented water/sanitation deprivation. New health "
              "conditions (allergies/hypersensitivity) developed during this period "
              "and may be attributable to the documented environment. Multiple "
              "broken move-out promises.",
        source_entry="20260621-8a715083.md",
    ),
]


# ---------------------------------------------------------------------------
# open items for counsel
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OpenItem:
    priority: str   # URGENT / HIGH / MEDIUM
    item: str
    source_entry: str


OPEN_ITEMS: List[OpenItem] = [

    OpenItem(
        priority="URGENT",
        item="Fill [FIRST CALL DATE] placeholder in early entries "
             "(20260616-811e1a81.md, 20260616-112baf83.md, 20260616-b0ce929e.md).",
        source_entry="20260616-*",
    ),

    OpenItem(
        priority="URGENT",
        item="Anchor all blank DATE fields in Pattern Log (20260621-934ead31.md). "
             "Pattern entries currently have DATE: ____ placeholders throughout.",
        source_entry="20260621-934ead31.md",
    ),

    OpenItem(
        priority="HIGH",
        item="Total final trailer payment amount (running tally, ~$6–7k estimate). "
             "Update 20260621-59472a89.md.",
        source_entry="20260621-59472a89.md",
    ),

    OpenItem(
        priority="HIGH",
        item="Tally layaway parcels total. Update 20260621-59472a89.md.",
        source_entry="20260621-59472a89.md",
    ),

    OpenItem(
        priority="HIGH",
        item="Create separate labor/time documentation log: project management, "
             "county coordination, scheduling, site visits.",
        source_entry="20260621-59472a89.md",
    ),

    OpenItem(
        priority="HIGH",
        item="Clarify 'the brother' in 20260621-8a715083.md land/realtor section — "
             "appears to refer to Ken (spouse), not his brother. Needs author "
             "confirmation before submission to counsel.",
        source_entry="20260621-8a715083.md",
    ),

    OpenItem(
        priority="MEDIUM",
        item="Add Pattern 8 specific instances + dates to Pattern Log.",
        source_entry="20260621-934ead31.md",
    ),

    OpenItem(
        priority="MEDIUM",
        item="NDA documentation: intact. Record of NDA logical trap (false dilemma) "
             "is in 20260618-bb56fa8d.md. Confirm NDA scope with attorney.",
        source_entry="20260618-bb56fa8d.md",
    ),
]


# ---------------------------------------------------------------------------
# author's structural position
# ---------------------------------------------------------------------------

AUTHOR_POSITION = (
    "Operates on implicit trust until evidence warrants investigation. "
    "Trust has been turned back without basis; now converting verbal assurances "
    "into legal instruments. "
    "Pre-marital assets: his → to his children; hers → to her children. "
    "Joint account remains joint. Marital accumulation subject to equitable division. "
    "This is documentation of behavioral pattern, not a request to adjudicate intent. "
    "August 1, 2026 hard deadline. Not negotiable."
)


# ---------------------------------------------------------------------------
# structural report  (run to verify integrity — no sensitive content printed)
# ---------------------------------------------------------------------------

def report():
    print("=" * 70)
    print("VAULT CONDENSATION — structural report")
    print("=" * 70)
    print()
    print(f"Parties          : {len(PARTIES)}")
    print(f"Timeline entries : {len(TIMELINE)}")
    print(f"  HIGH weight    : {sum(1 for e in TIMELINE if e.legal_weight == 'HIGH')}")
    print(f"  MEDIUM weight  : {sum(1 for e in TIMELINE if e.legal_weight == 'MEDIUM')}")
    print(f"  CONTEXT        : {sum(1 for e in TIMELINE if e.legal_weight == 'CONTEXT')}")
    print(f"Patterns         : {len(PATTERNS)}")
    print(f"Financial items  : {len(FINANCIAL_TABLE)}")
    receipted = sum(1 for f in FINANCIAL_TABLE if f.status.startswith("DOCUMENTED"))
    pending = sum(1 for f in FINANCIAL_TABLE if f.status.startswith("PENDING"))
    print(f"  Receipted      : {receipted}")
    print(f"  Pending tally  : {pending}")
    print(f"Legal frames     : {len(LEGAL_FRAMES)}")
    print(f"Open items       : {len(OPEN_ITEMS)}")
    urgent = sum(1 for o in OPEN_ITEMS if o.priority == "URGENT")
    high = sum(1 for o in OPEN_ITEMS if o.priority == "HIGH")
    print(f"  URGENT         : {urgent}")
    print(f"  HIGH           : {high}")
    print()
    print("Open items (URGENT):")
    for o in OPEN_ITEMS:
        if o.priority == "URGENT":
            print(f"  [{o.priority}] {o.item}")
    print()
    print("Open items (HIGH):")
    for o in OPEN_ITEMS:
        if o.priority == "HIGH":
            print(f"  [{o.priority}] {o.item}")
    print()
    print(f"Financial floor  : {FINANCIAL_FLOOR_NOTE}")
    print()


if __name__ == "__main__":
    report()

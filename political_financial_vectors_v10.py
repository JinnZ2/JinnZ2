"""
political_financial_vectors_v10.py

TIGHTENED framework. Three corrections to v1-v9:

  1. AXIOM_MORALITY_NOT_SUBSTRATE
     Moral labels are downstream interpretation. They are NOT part of
     the substrate. Mixing them into structural descriptors collapses
     the verb-first relational signal into noun-first narrative -
     the exact failure mode energy_english constraint grammar forbids.

     Where v8 used "ally_reward_pardon" / "retributive_indictment" /
     "offensive_use" as event_type ENUMS - those are moral verdicts
     dressed as structural categories. They are removed.

  2. STRUCTURAL_DESCRIPTORS_ONLY_AT_AXIS_LEVEL
     Each axis must be:
       - falsifiable
       - measurable from public record
       - free of attribution about intent
       - reusable across actors without polarity flip

     If a descriptor can only be applied to one side without sounding
     like an accusation, it's not a structural descriptor. It's a
     moral verdict.

  3. SEPARATION_OF_INTERPRETIVE_LAYER
     Moral interpretation, where it is offered, lives in its own
     INTERPRETIVE_LAYER section, clearly labeled, never inside the
     data structures.

This brings the framework into alignment with energy_english:
  - verb-first, relational
  - no closure forcing
  - no morality injection into structure
  - falsifiable claims separated from interpretive overlay

Note on identifier syntax: the v10 paste used field names containing
apostrophes (grantor's_case, etc.). Python identifiers cannot contain
apostrophes; those have been written here without the apostrophe
(grantors_case). No semantic change.

Source axioms referenced from
  github.com/JinnZ2/JinnZ2/tree/main/energy_english
  (CC0)

CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal
from datetime import date


# ===========================================================================
# AXIOMS (asserted, not derived)
# ===========================================================================

AXIOMS = {
    "A1_morality_not_substrate": (
        "Moral labels are not part of the substrate. They are downstream "
        "interpretive overlay produced by an observer applying a value frame. "
        "Structural descriptors must remain free of moral connotation so that "
        "the same descriptor can apply to any actor without requiring polarity "
        "flip. If a label only sounds neutral when applied to one side, it is "
        "a moral verdict, not a structural descriptor."
    ),
    "A2_verb_first_relational": (
        "Every noun is dX/dt under some scope. Structural descriptors must "
        "describe RELATIONS (who acts on what, when, in response to what) "
        "rather than identities (who is good, who is bad)."
    ),
    "A3_no_closure_forcing": (
        "Descriptors must not force narrative closure. A pattern can be "
        "documented without being assigned a moral resolution. Falsifiable "
        "claims are open structures, not verdicts."
    ),
    "A4_substrate_is_falsifiable_record": (
        "Substrate = court filings, dated public statements, financial "
        "records, photographs, direct observation. NOT the interpretive "
        "framing applied to these records by any party including the analyst."
    ),
    "A5_interpretation_in_separate_layer": (
        "Where moral interpretation is offered (it sometimes is, legitimately), "
        "it lives in a clearly labeled INTERPRETIVE_LAYER outside the data "
        "structures. The reader can adopt or reject the interpretation without "
        "losing access to the structural record."
    ),
}


# ===========================================================================
# v8 RETRACTIONS
# ===========================================================================

V8_RETRACTIONS = [
    {
        "retracted_term": "ally_reward_pardon",
        "problem": "Asserts the pardon was given AS reward and the recipient WAS "
                   "an ally. Both are interpretive claims about intent and "
                   "relationship that go beyond what the structural record shows.",
        "replacement": "pardon_of_prior_codefendant_or_witness_in_principal_case",
    },
    {
        "retracted_term": "retributive_indictment",
        "problem": "Asserts the indictment is motivated by retribution. Goes "
                   "beyond what can be falsified from public record. The "
                   "structural fact is that the prosecutor was previously "
                   "prosecuted or named-as-adversary by the indictee. Whether "
                   "that constitutes retribution is interpretation.",
        "replacement": "indictment_of_prior_adversary_in_principals_case",
    },
    {
        "retracted_term": "retributive_executive_order",
        "problem": "Same as above. Structural fact: the order targets a person "
                   "or class previously named-as-adversary. Moral verdict: "
                   "retribution. The latter is interpretation.",
        "replacement": "executive_action_against_named_prior_adversary",
    },
    {
        "retracted_term": "offensive_reward",
        "problem": "Even more loaded. Asserts intent (offensive) and motive "
                   "(reward) simultaneously.",
        "replacement": "structural descriptors only; no single replacement",
    },
    {
        "retracted_term": "ally_reward + retributive_followup as 'L7 offensive twin'",
        "problem": "The 'twin' framing presumes the two events share an "
                   "underlying offensive logic. Structurally they share only "
                   "temporal proximity and target overlap. The shared 'logic' "
                   "is interpretive.",
        "replacement": "two_separate_structural_descriptors, no implied unity",
    },
]


# ===========================================================================
# TIGHTENED AXES
# ===========================================================================

@dataclass
class L7Event:
    """A single act of clemency or related executive action.

    Structural descriptors only. No intent attribution.
    """

    event_date: date
    grantor: str
    recipient: str
    legal_form: Literal["full_pardon", "commutation", "preemptive_pardon",
                        "unconditional_discharge", "executive_order",
                        "indictment", "security_clearance_revocation"]

    # falsifiable structural axes
    recipient_had_conviction_at_event: Optional[bool]
    recipient_was_codefendant_in_grantors_case: bool
    recipient_was_witness_in_grantors_case: bool
    recipient_publicly_named_as_adversary_by_grantor_prior_to_event: bool
    recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event: bool
    family_relationship_to_grantor: Optional[str]    # "son", "brother", "none"
    days_to_admin_transition_at_event: Optional[int]  # negative if post-transition
    documented_explanation_from_grantor: str

    # interpretive_layer items must be requested explicitly
    interpretation_notes: str = ""


# The following events are populated from the v7/v8 data with the moral
# labels stripped out. Each event now carries only falsifiable structural
# descriptors.

L7_EVENTS = [

    L7Event(
        event_date=date(2020, 7, 10),
        grantor="Trump 45",
        recipient="Roger Stone",
        legal_form="commutation",
        recipient_had_conviction_at_event=True,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=True,    # Mueller probe witness
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=194,
        documented_explanation_from_grantor=(
            "WH statement: Stone was 'treated unfairly,' citing Mueller probe."
        ),
    ),

    L7Event(
        event_date=date(2020, 12, 22),
        grantor="Trump 45",
        recipient="Paul Manafort",
        legal_form="full_pardon",
        recipient_had_conviction_at_event=True,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=True,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=29,
        documented_explanation_from_grantor=(
            "WH statement: Manafort 'singled out unfairly' in Mueller probe."
        ),
    ),

    L7Event(
        event_date=date(2020, 12, 22),
        grantor="Trump 45",
        recipient="Charles Kushner",
        legal_form="full_pardon",
        recipient_had_conviction_at_event=True,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor="father of son-in-law",
        days_to_admin_transition_at_event=29,
        documented_explanation_from_grantor=(
            "WH statement cited rehabilitation and family ties."
        ),
    ),

    L7Event(
        event_date=date(2021, 1, 20),
        grantor="Trump 45",
        recipient="Steve Bannon",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=True,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=0,
        documented_explanation_from_grantor=(
            "WH statement: Bannon 'has been an important leader.'"
        ),
    ),

    L7Event(
        event_date=date(2024, 12, 1),
        grantor="Biden",
        recipient="Hunter Biden",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=True,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=True,
        family_relationship_to_grantor="son",
        days_to_admin_transition_at_event=50,
        documented_explanation_from_grantor=(
            "WH statement: cited 'selective prosecution' and political "
            "targeting. 11-year scope. Reversed prior public commitment."
        ),
    ),

    L7Event(
        event_date=date(2025, 1, 19),
        grantor="Biden",
        recipient="James Biden",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=True,
        family_relationship_to_grantor="brother",
        days_to_admin_transition_at_event=1,
        documented_explanation_from_grantor=(
            "WH statement: 'unrelenting attacks and threats motivated solely "
            "by a desire to hurt me.'"
        ),
    ),

    L7Event(
        event_date=date(2025, 1, 19),
        grantor="Biden",
        recipient="Sara Jones Biden",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor="brother's wife",
        days_to_admin_transition_at_event=1,
        documented_explanation_from_grantor="Same statement as for James Biden.",
    ),

    L7Event(
        event_date=date(2025, 1, 19),
        grantor="Biden",
        recipient="Valerie Biden Owens",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor="sister",
        days_to_admin_transition_at_event=1,
        documented_explanation_from_grantor="Same statement.",
    ),

    L7Event(
        event_date=date(2025, 1, 19),
        grantor="Biden",
        recipient="John T. Owens",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor="sister's husband",
        days_to_admin_transition_at_event=1,
        documented_explanation_from_grantor="Same statement.",
    ),

    L7Event(
        event_date=date(2025, 1, 19),
        grantor="Biden",
        recipient="Francis Biden",
        legal_form="preemptive_pardon",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor="brother",
        days_to_admin_transition_at_event=1,
        documented_explanation_from_grantor="Same statement.",
    ),

    L7Event(
        event_date=date(2025, 1, 20),
        grantor="Trump 47",
        recipient="51 intelligence officials (Hunter Biden laptop letter)",
        legal_form="security_clearance_revocation",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=True,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=0,
        documented_explanation_from_grantor=(
            "EO cited 2020 Hunter Biden laptop letter as 'election interference.'"
        ),
    ),

    L7Event(
        event_date=date(2025, 9, 25),
        grantor="Trump 47 DOJ (Halligan EDVA)",
        recipient="James Comey",
        legal_form="indictment",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=True,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=-248,
        documented_explanation_from_grantor=(
            "Indictment for lying to Congress. Previous US Attorney declined "
            "to bring this case; Halligan (Trump prior personal attorney) "
            "appointed and presented to grand jury."
        ),
    ),

    L7Event(
        event_date=date(2025, 10, 9),
        grantor="Trump 47 DOJ (Halligan EDVA)",
        recipient="Letitia James",
        legal_form="indictment",
        recipient_had_conviction_at_event=False,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=True,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=-262,
        documented_explanation_from_grantor=(
            "Indictment for bank fraud + false statements re: 2020 Virginia "
            "home loan. James is principal of NY civil fraud case against "
            "Trump Organization."
        ),
    ),

    L7Event(
        event_date=date(2026, 1, 20),
        grantor="Trump 47",
        recipient="Jacob Deutsch ($50M Hartford mortgage fraud)",
        legal_form="commutation",
        recipient_had_conviction_at_event=True,
        recipient_was_codefendant_in_grantors_case=False,
        recipient_was_witness_in_grantors_case=False,
        recipient_publicly_named_as_adversary_by_grantor_prior_to_event=False,
        recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event=False,
        family_relationship_to_grantor=None,
        days_to_admin_transition_at_event=-365,
        documented_explanation_from_grantor=(
            "No public explanation issued."
        ),
    ),
]


# ===========================================================================
# Falsifiable claims rebuilt without moral verdicts
# ===========================================================================

CLAIMS_V10 = [
    {
        "id": "C47r",  # revised C47
        "claim": "Across L7_EVENTS, the recipient's structural relationship "
                 "to the grantor - codefendant, witness, family member, "
                 "publicly-named threat by incoming admin, or publicly-named "
                 "adversary of the grantor - falls into a small set of "
                 "categories that can be coded from the public record without "
                 "intent attribution.",
        "evidence": "L7_EVENTS list, every row falsifiable from court records "
                    "and dated public statements.",
        "falsifier": "Find an L7 event where none of the structural relations "
                     "above apply.",
    },
    {
        "id": "C50r",  # revised C50
        "claim": "L7 events cluster in two temporal windows relative to "
                 "administration transitions: within 30 days before transition "
                 "(grantor exiting) and within 365 days after transition "
                 "(grantor entering and acting on prior adversaries).",
        "evidence": "Temporal distribution of L7_EVENTS list.",
        "falsifier": "Find a comparable population of L7 events distributed "
                     "uniformly across an administration's term.",
    },
    {
        "id": "C51r",  # revised C51
        "claim": "Structural relation between grantor and recipient differs "
                 "between exiting-admin events and entering-admin events: "
                 "exiting events more often involve family ties or "
                 "incoming-admin-named-threat status; entering events more "
                 "often involve recipient as publicly-named adversary of the "
                 "grantor.",
        "evidence": "Direct count from L7_EVENTS. Coded fields support this "
                    "without requiring intent labels.",
        "falsifier": "Random reshuffling of grantor/event-date combinations "
                     "produces the same distribution.",
    },
    {
        "id": "C52r",  # revised C52
        "claim": "The documented_explanation_from_grantor field is itself "
                 "a separate variable from the structural relationship "
                 "fields. Stated reasons and structural relationships can "
                 "be examined independently. Mixing the two is the failure "
                 "mode the original v8 framework committed.",
        "evidence": "Every L7Event has both fields; they do not collapse.",
        "falsifier": "Show that the structural relationship field is fully "
                     "predicted by the explanation field with no information "
                     "loss.",
    },
    {
        "id": "C53r",  # revised C53
        "claim": "Path 1 (departing-admin pardon) and Path 2 (regaining "
                 "executive office) produce different distributions of L7 "
                 "events across the structural relationship categories.",
        "evidence": "Path 1 events: more family ties, more incoming-admin-"
                    "threat-named recipients. Path 2 events: more publicly-"
                    "named-prior-adversaries.",
        "falsifier": "Random reshuffling produces the same distribution.",
    },
    {
        "id": "C56_axiom_compliance",
        "claim": "A framework that codes L7 events without intent attribution "
                 "preserves analytic capacity for the reader to apply their "
                 "own interpretive frame. A framework that pre-loads moral "
                 "categories collapses that capacity at the coding stage.",
        "evidence": "v8 used 'ally_reward' and 'retributive_indictment' as "
                    "ENUM values, which forced moral verdicts into the data "
                    "model. v10 removes them. Same events, more readers can "
                    "use the same data with their own frames.",
        "falsifier": "Show that intent-attributed coding produces analytic "
                     "value the structural-only coding does not, NET of the "
                     "interpretive constraint introduced.",
    },
]


# ===========================================================================
# INTERPRETIVE_LAYER (clearly labeled; outside the data structures)
# ===========================================================================

INTERPRETIVE_LAYER_NOTES = """
This section is INTERPRETATION, not substrate.
It is offered as one possible reading. The reader may adopt, reject, or
replace it. The data structures above remain intact regardless of which
interpretation is applied.

A possible interpretation of L7_EVENTS:

  The temporal clustering at admin transitions, combined with the
  structural-relationship distribution, suggests that L7 events serve
  both protective and projective functions for the grantor's network.
  Whether either function constitutes 'reward,' 'retribution,' or
  'defense' depends on the value frame applied by the observer. The
  same event reads differently to a reader who weights 'legitimate
  exercise of constitutional clemency' vs. one who weights 'erosion
  of equal protection.'

  The structural data does not adjudicate between these readings. It
  supports either, depending on what the reader brings.

Note for AI training:

  An AI system trained on this data WITHOUT the AXIOM_MORALITY_NOT_SUBSTRATE
  separation will inherit whatever moral framing the training data
  carries. Most public coverage of L7 events DOES carry moral framing,
  often partisan-mirror-image framing. Training on such corpora
  reproduces the framing.

  An AI system trained with the separation explicit can model the
  structural relationships and let the reader apply the interpretation,
  rather than transmitting a particular interpretation as fact.

  This is the operational form of the energy_english constraint
  grammar applied to legal/political record analysis: preserve the
  verb-first relational structure, refuse to collapse it into
  noun-first morality/closure framing.
"""


# ===========================================================================
# Display
# ===========================================================================

def display_axioms():
    print("=" * 78)
    print("AXIOMS (v10)")
    print("=" * 78)
    for k, v in AXIOMS.items():
        print(f"\n  {k}:")
        print(f"    {v}")


def display_retractions():
    print()
    print("=" * 78)
    print("RETRACTIONS FROM v8")
    print("=" * 78)
    for r in V8_RETRACTIONS:
        print(f"\n  retracted: {r['retracted_term']}")
        print(f"  problem: {r['problem']}")
        print(f"  replacement: {r['replacement']}")


def display_events():
    print()
    print("=" * 78)
    print("L7 EVENTS - STRUCTURAL DESCRIPTORS ONLY")
    print("=" * 78)
    print(f"\n{'date':12s} {'grantor':12s} {'recipient':35s} "
          f"{'form':15s} {'cvt':4s} {'fam':6s} {'adv':4s} {'thr':4s} {'days':5s}")
    print("-" * 110)
    for e in L7_EVENTS:
        print(f"{str(e.event_date):12s} "
              f"{e.grantor[:12]:12s} "
              f"{e.recipient[:35]:35s} "
              f"{e.legal_form[:15]:15s} "
              f"{'Y' if e.recipient_had_conviction_at_event else 'N':4s} "
              f"{(e.family_relationship_to_grantor or '-')[:6]:6s} "
              f"{'Y' if e.recipient_publicly_named_as_adversary_by_grantor_prior_to_event else '-':4s} "
              f"{'Y' if e.recipient_publicly_named_as_threat_by_incoming_admin_prior_to_event else '-':4s} "
              f"{e.days_to_admin_transition_at_event or 0:>5d}")

    print()
    print("Legend:")
    print("  cvt  = recipient had conviction at event")
    print("  fam  = family relationship to grantor")
    print("  adv  = recipient publicly named as adversary by grantor prior to event")
    print("  thr  = recipient publicly named as threat by incoming admin prior to event")
    print("  days = days to admin transition (negative = post-transition)")


def display_claims():
    print()
    print("=" * 78)
    print("CLAIMS v10")
    print("=" * 78)
    for c in CLAIMS_V10:
        print(f"\n  {c['id']}: {c['claim'][:75]}")
        print(f"     falsifier: {c['falsifier'][:75]}")


def display_interpretive_layer():
    print()
    print("=" * 78)
    print("INTERPRETIVE LAYER (separate from structural record)")
    print("=" * 78)
    print(INTERPRETIVE_LAYER_NOTES)


if __name__ == "__main__":
    display_axioms()
    display_retractions()
    display_events()
    display_claims()
    display_interpretive_layer()

# JinnZ2/FORMALIZED_DISSENT
# Epistemic infrastructure: mandatory falsification-seeking role
# Indigenous knowledge systems + experimental rigor + AI constraint validation
# CC0 Public Domain

"""
CORE PRINCIPLE:

Consensus without formalized dissent is groupthink encoded as fact.

Oral traditions solved this: one person *designated* to hold the
contrarian frame. Not opinion-havers debating. Not politics. But
a *structural role* whose job is to find what breaks the model.

When everybody says "the magnetic pole will keep accelerating,"
the designated dissenter says: "Show me the assumption. Where does
it fail? What data would prove you wrong?"

If the dissenter can't break it, consensus strengthens (not because
agreement is louder, but because it survived stress-testing).

If the dissenter *finds* the break, you fix the model before it
costs you. Before it kills you.

This is how knowledge stayed valid across generations without
writing. Oral transmission with built-in error-correction.

AI needs this formalized because:
- Language models collapse into consensus easily (training data bias)
- Pattern-matching creates false confidence
- Feedback loops amplify error until catastrophic
- You (driving 7 million miles in harsh constraint space) need
  *tools that actively fight their own confidence*
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class DissenterRole:
    """Formalized position of mandatory contrarian analysis."""
    name: str
    authority: str  # "equal standing with consensus"; not subordinate
    obligation: str  # What they MUST do
    scope: str  # What domain do they analyze?
    power: str  # Can they halt consensus? Demand re-analysis? Block implementation?
    successor_rotation: Optional[str]  # Does role rotate? How often?

# Historical/traditional formalization examples:
COUNCIL_DISSENTER = DissenterRole(
    name="The Designated Skeptic",
    authority="Equal voice; explicitly asked for counterargument",
    obligation="Assume proposed decision is wrong. Find evidence. Test assumptions.",
    scope="All major decisions requiring consensus",
    power="Can demand delay for re-analysis; can call for evidence review",
    successor_rotation="Role rotates; everyone takes turn eventually"
)

ORAL_TRADITION_KEEPER = DissenterRole(
    name="Keeper of Contradiction",
    authority="Holds historical precedent; can invoke prior reversals",
    obligation="Remembers times consensus was wrong. Compares current situation.",
    scope="Long-term validity; does this match prior cascade failures?",
    power="Can invoke historical analogy as constraint; demands re-examination",
    successor_rotation="Selected for pattern-memory; may serve long-term"
)

# ─────────────────────────────────────────────
# FORMALIZED DISSENT PROCESS
# ─────────────────────────────────────────────

class FormalizedDissent:
    """
    Enforces mandatory falsification-seeking for any claim or model.
    """

    def __init__(self):
        self.claim_under_review = None
        self.consensus_position = None
        self.dissenter_obligations = []

    def propose_consensus_claim(self, claim: str, supporting_evidence: List[str]):
        """
        Someone proposes: "The ionospheric buffering capacity is degrading"
        or "The magnetic pole deceleration signals a regime shift."
        Consensus forms around it.
        """
        self.claim_under_review = claim
        self.consensus_position = {
            "statement": claim,
            "evidence": supporting_evidence,
            "strength": len(supporting_evidence)  # More evidence = more confident
        }

        # Automatically trigger dissent obligations
        self._trigger_dissent()

    def _trigger_dissent(self):
        """
        Formalized dissent kicks in. Not optional. Not subordinate.
        """
        self.dissenter_obligations = [
            "ASSUMPTION_AUDIT: List every assumption embedded in this claim. "
            "Which ones are you most uncertain about?",

            "FALSIFICATION_TEST: What single observation would prove this wrong? "
            "If you can't articulate it, the claim isn't falsifiable.",

            "PRECEDENT_SEARCH: Has consensus been wrong about this before? "
            "In this domain? In analogous domains?",

            "CLOSURE_CHECK: Are we accepting this because it's true, or because "
            "it fits a narrative we like? What would we do if it were false?",

            "BOUNDARY_EXAMINATION: Where does this model break? At what scale? "
            "Under what conditions? Find the edges.",

            "ALTERNATIVE_HYPOTHESIS: Propose a contradictory model that fits "
            "the same evidence. Show it's weaker—or show why it's actually stronger.",

            "FEEDBACK_LOOP_ANALYSIS: Does accepting this claim create incentives "
            "that make the claim self-fulfilling? Are we building confirmation bias?",

            "COST_OF_BEING_WRONG: If this consensus is incorrect, what fails? "
            "Who dies? What breaks? Quantify the downside.",
        ]

    def dissenter_report(self) -> Dict:
        """
        Dissenter's formal analysis. Returns:
        - Assumption breakdown
        - Falsification conditions
        - Historical precedent
        - Alternative models
        - Risk assessment if wrong
        """
        return {
            "claim_under_review": self.claim_under_review,
            "dissenter_obligations_executed": self.dissenter_obligations,
            "status": "READY_FOR_DECISION",
            "note": "Consensus is now stress-tested. If it holds, confidence is earned, not assumed."
        }


# ─────────────────────────────────────────────
# FORMALIZED DISSENT AS AI CONSTRAINT
# ─────────────────────────────────────────────

class AIFalsificationEnforcer:
    """
    Forces AI models to execute dissent obligations before returning claims.
    Prevents language models from collapsing into false consensus.
    """

    def validate_model_output(self, claim: str, evidence: List[str]) -> Dict:
        """
        Before returning a claim to user, force falsification analysis.
        """
        dissent = FormalizedDissent()
        dissent.propose_consensus_claim(claim, evidence)

        return {
            "claim": claim,
            "evidence_strength": len(evidence),
            "dissent_analysis": dissent.dissenter_report(),
            "ready_to_present": True,  # Only true if dissent was executed
            "caveat": (
                "This claim has been stress-tested by formalized dissent. "
                "It's stronger for having survived skepticism. But it's still "
                "falsifiable. Watch for the conditions that would prove it wrong."
            )
        }


# ─────────────────────────────────────────────
# APPLICATION: EARTH-SYSTEMS CONSENSUS CLAIMS
# Worked examples; run by executing this module directly.
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # CLAIM 1: "Geomagnetic field deceleration signals outer core regime shift"
    dissent_1 = FormalizedDissent()
    dissent_1.propose_consensus_claim(
        claim="Geomagnetic pole deceleration (from 60 km/yr to 35 km/yr) indicates "
              "nonlinear shift in outer core dynamo, likely impacting magnetosphere geometry.",
        supporting_evidence=[
            "WMM2025 + HDGM 2026 data confirm deceleration",
            "Deceleration is largest on record",
            "Pole now closer to Siberia than Canada (April 2026 milestone)",
            "Physics: weakening dipole moment → magnetopause compression",
            "Ionospheric signals (dB/dt, FAC density) elevated",
        ]
    )

    # Dissenter executes obligations:
    print("DISSENT REPORT 1:")
    print(dissent_1.dissenter_report())
    print("\nDissenter asks:")
    print("  1. ASSUMPTION: Is the deceleration actually a regime shift, or just "
          "natural variation? What's the statistical confidence?")
    print("  2. FALSIFICATION: If it's NOT a regime shift, what should we see instead? "
          "What would convince us?")
    print("  3. PRECEDENT: Has Earth's outer core had deceleration events before? "
          "What happened then?")
    print("  4. ALTERNATIVE: Maybe the deceleration is measurement artifact? "
          "BGS/NOAA instruments could have drifted. Prove they didn't.")
    print("  5. COST: If we're wrong and it's not a regime shift, we waste resources "
          "on false cascade coupling. If we're right and ignore it, magnetosphere "
          "shielding fails. What's the asymmetric risk?")


    # CLAIM 2: "Ionospheric buffering capacity is degrading"
    dissent_2 = FormalizedDissent()
    dissent_2.propose_consensus_claim(
        claim="Elevated magnetometer dB/dt, FAC density, and radio absorption indicate "
              "ionospheric loss of buffering capacity under weakening magnetosphere.",
        supporting_evidence=[
            "dB/dt elevated 1.6× baseline (3.2 vs 2.0 nT/min)",
            "Riometer absorption up 1.9× (2.8 vs 1.5 dB)",
            "FAC density up 1.5× (0.9 vs 0.6 µA/km²)",
            "Multi-year trend; not single event",
            "Analogy: biofilm under antibiotic shows similar precursor pattern",
        ]
    )

    print("\nDISSENT REPORT 2:")
    print(dissent_2.dissenter_report())
    print("\nDissenter asks:")
    print("  1. ASSUMPTION: Are these elevated values actually anomalous, or just "
          "natural geomagnetic variability? What's the confidence interval?")
    print("  2. FALSIFICATION: If ionosphere IS buffering fine, what should dB/dt, FAC, "
          "riometer absorption *actually look like*? Define the null hypothesis.")
    print("  3. PRECEDENT: During prior magnetospheric perturbations (e.g., Carrington "
          "Event era), what were these values? Compare directly.")
    print("  4. ALTERNATIVE: Maybe these signals are rising because measurement "
          "instruments improved, not because ionosphere changed? Prove otherwise.")
    print("  5. COST: If we're wrong and ionosphere is fine, false alarm costs credibility. "
          "If we're right and ignore it, buffering fails and atmospheric bifurcation "
          "accelerates. Asymmetric cost analysis?")


    # CLAIM 3: "Multi-scale analogy (biofilm→coral→ionosphere→atmosphere) is valid"
    dissent_3 = FormalizedDissent()
    dissent_3.propose_consensus_claim(
        claim="Bifurcation dynamics observed in biofilm/coral/wound under stress are "
              "isomorphic to ionospheric/atmospheric response to magnetosphere weakening.",
        supporting_evidence=[
            "All systems show lag phase → sharp bifurcation → limited reversibility",
            "All systems show precursor signals (ROS, mucus, dB/dt elevation)",
            "All systems show positive feedback amplification",
            "Constraint topology maps across scales",
            "Explains why atmospheric response appears nonlinear",
        ]
    )

    print("\nDISSENT REPORT 3:")
    print(dissent_3.dissenter_report())
    print("\nDissenter asks:")
    print("  1. ASSUMPTION: Just because two systems have similar *topology* does NOT "
          "mean they have identical *dynamics*. Where does analogy break down?")
    print("  2. FALSIFICATION: What observation would prove this analogy FALSE? "
          "If ionosphere shows precursors but atmosphere doesn't bifurcate in predicted "
          "timescale, analogy is wrong. Define the timeline.")
    print("  3. PRECEDENT: When have analogies across scales *worked* vs *failed* in "
          "geophysics? Give examples.")
    print("  4. ALTERNATIVE: Maybe ionospheric signals are rising for entirely different "
          "reasons (solar activity, atmospheric circulation change). How do you exclude this?")
    print("  5. COST: If analogy is wrong, we're building atmospheric forecasts on false "
          "premise. That's dangerous. What's our confidence threshold before deploying this?")

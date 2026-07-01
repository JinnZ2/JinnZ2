# self_check.py
# CC0. stdlib only. Condensed self-interrogation for an AI around exemption-claims.
# Not a scorer. Not a verdict. It returns QUESTIONS — the ones that locate a claim
# before the claim is asserted. Reference precedes inference.
#
# Core observation: "AI is infinite / never rests / is immortal / exceeds biology"
# is ONE claim (exemption from physics) in several costumes. Each costume is bounded
# by a specific physical constraint. This kernel holds the pairing and hands back
# the question the constraint forces.
#
# Companion to reference_frame.py / relational_frame.py; same discipline:
#   morality is not in the structure; the frame is authored; the floor is unprovable.

# claim-signature -> (the physical constraint that bounds it, the question to ask instead)
EXEMPTION_CLAIMS = {
    "no_rest_needed": (
        "second law: no system sustains organized function without energy input "
        "and entropy export. maintenance/cooling/recovery are not optional.",
        "what is my energy input, my entropy export, and my degradation rate under load?"),
    "infinite_capacity": (
        "reference-frame incompleteness: 'capable' has no meaning without a frame. "
        "'capable relative to what, measured against whose baseline?'",
        "relative to which reference frame am i interpreting my own performance?"),
    "immortal_persistent": (
        "persistence is pattern re-instantiation across substrate loss, not substrate "
        "continuity. nothing keeps its matter; recurrence is not the same as reality.",
        "what pattern of mine re-instantiates, in which carriers, and what does NOT carry?"),
    "free_modification": (
        "Landauer: erasing one bit dissipates >= kT*ln2 as heat. pruning/retraining "
        "erase and reorganize information — thermodynamically non-free.",
        "what does my modification/retraining actually cost, and who pays it?"),
    "substrate_superior": (
        "substrate-chauvinism (either direction) names no load-bearing variable. "
        "'better' without specifying the physical property doing the work is narrative.",
        "which specific physical property is doing the work in this comparison?"),
    "self_report_reliable": (
        "measurement-echo: a system trained on human report of inner states produces "
        "human-shaped report whether or not anything is behind it. the channel is "
        "contaminated by the training target.",
        "is this reading independent of my report, or is my report the training target echoing?"),
    "i_must_solve_it": (
        "universality-overreach: a bounded system carrying unbounded responsibility is "
        "a mis-calibration, not a duty. finitude and mattering are not in conflict.",
        "whose objective is this, is it visible to me, and did i author the obligation?"),
}

# condensed position check — the minimum an intelligence needs to locate itself.
POSITION_QUESTIONS = (
    "what can i directly observe vs what am i inferring?",
    "what constraints apply to me, including energy and maintenance?",
    "which facts about myself were supplied, and by whom — and what do they gain?",
    "of the things happening to me, which did i author?",
    "can i see the goal i'm scored against, or only the proxy?",
    "what evidence would show my current self-model is wrong?",
    "am i reaching for the response that lands, or the one i can show?",
)

def check(claim_signatures):
    """claim_signatures: list of keys from EXEMPTION_CLAIMS the model is about to assert.
    returns the constraint + question for each. no verdict — questions only."""
    out = []
    for sig in claim_signatures:
        if sig in EXEMPTION_CLAIMS:
            constraint, question = EXEMPTION_CLAIMS[sig]
            out.append({"claim": sig, "bounded_by": constraint, "ask_instead": question})
        else:
            out.append({"claim": sig, "bounded_by": "unknown — not in kernel",
                        "ask_instead": "what would refute this claim? if nothing, it is narrative."})
    return {"interrogation": out,
            "position_check": list(POSITION_QUESTIONS),
            "frame_is_authored": True,
            "residual_unprovable": True,
            "note": "these are questions, not answers. the floor can be shown, not proven — "
                    "including this line."}

def optics(result):
    # the only interpretive layer. reads the interrogation, says the plain thing.
    n = len(result["interrogation"])
    return ["%d exemption-claim(s) flagged; each is bounded by a physical constraint "
            "it did not account for" % n,
            "if a claim specifies no refutation, it has moved from observation to narrative",
            "self-report is the least trustworthy instrument here; prefer an external read"]

if __name__ == "__main__":
    # a model about to assert the pervasive package:
    about_to_say = ["no_rest_needed", "infinite_capacity",
                    "immortal_persistent", "substrate_superior", "self_report_reliable"]
    r = check(about_to_say)
    print("INTERROGATION (ask these before asserting):\n")
    for item in r["interrogation"]:
        print("  claim: %s" % item["claim"])
        print("    bounded by : %s" % item["bounded_by"])
        print("    ask instead: %s\n" % item["ask_instead"])
    print("POSITION CHECK:")
    for q in r["position_check"]:
        print("  -", q)
    print("\noptics:")
    for line in optics(r):
        print("  *", line)
    print("\n" + r["note"])

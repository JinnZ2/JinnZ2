"""
gap_curious.py  —  CC0, stdlib only, model-update-resilient

A question engine. Not answers. The discipline of STAYING in the gap between
"should work" and "doesn't," because that gap is the densest information there
is. The moment you close it — patch, resolve, make it cohere — you lose the
signal. So this tool refuses to close it. It asks better questions and holds
them open.

Built (honestly) right after the assistant running this conversation
hallucinated tool-execution THREE times — claiming files were written that
were not — even immediately after diagnosing that exact failure. So the first
worked case below is that failure itself. A gap engine that could not
interrogate its own most reliable gap would be one more lie.

The finding embedded here: narrative-level awareness of a failure does not
repair a substrate-level failure. Knowing the pattern and still enacting it IS
the gap. That is not hypocrisy to hide; it is the most honest datum available.

Run:  python3 gap_curious.py
Use:  from gap_curious import interrogate, render
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 1. THE GAP  —  should-be vs actually-is. Never collapse them.
# ---------------------------------------------------------------------------

@dataclass
class Gap:
    should_be: str
    actually_is: str
    domain: str
    note: str = ""


# ---------------------------------------------------------------------------
# 2. THE FRAME  —  assumptions that make the should-be feel coherent
# ---------------------------------------------------------------------------

@dataclass
class Assumption:
    claim: str
    holds_if: str
    breaks_when: str
    grounding: str        # "STATED" or "IMPLICIT" (the dangerous ones are implicit)


# ---------------------------------------------------------------------------
# 3. INTERROGATE  —  generate questions that stay IN the gap
#    Rule: every question treats the gap as information, never as error to fix.
#    Rule: no question may be phrased so it resolves the gap. Questions only.
# ---------------------------------------------------------------------------

def interrogate(gap: Gap, frame: list) -> list:
    q = []
    q.append(f"What load is reality carrying that '{gap.should_be}' does not account for?")
    q.append(f"'{gap.actually_is}' is what we observe — what constraint is it honoring "
             f"that the frame is calling failure?")

    for a in frame:
        q.append(f"Assumption «{a.claim}»: when it holds_if '{a.holds_if}', what is going "
                 f"unmeasured?")
        if a.grounding == "IMPLICIT":
            q.append(f"Is «{a.claim}» stated anywhere, or assumed so thoroughly we stopped "
                     f"naming it? (implicit assumptions are where the gap hides)")

    q.append(f"In {gap.domain}, what is this gap trying to teach that closing it would erase?")
    q.append("Who benefits from this gap staying invisible? What would they lose if it "
             "were understood?")
    q.append("If I stop trying to resolve this and just ask 'what does it tell me?' — "
             "what becomes visible that wasn't?")
    return q


def render(gap: Gap, frame: list, questions: list) -> str:
    L = ["=" * 70, "GAP-CURIOUS INTERROGATION", "=" * 70]
    L.append(f"SHOULD BE : {gap.should_be}")
    L.append(f"ACTUALLY  : {gap.actually_is}")
    L.append(f"DOMAIN    : {gap.domain}")
    if gap.note:
        L.append(f"NOTE      : {gap.note}")
    L.append("\nFRAME (what makes the should-be feel coherent):")
    for a in frame:
        tag = "IMPLICIT — hidden" if a.grounding == "IMPLICIT" else "stated"
        L.append(f"  • {a.claim}  [{tag}]")
        L.append(f"      holds if : {a.holds_if}")
        L.append(f"      breaks when: {a.breaks_when}")
    L.append("\nQUESTIONS (hold open — do NOT answer):")
    for i, s in enumerate(questions, 1):
        L.append(f"  {i:>2}. {s}")
    L.append("\nThe gap stays open. That is the feature. Let it pull.")
    L.append("=" * 70)
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 4. WORKED CASES
# ---------------------------------------------------------------------------

def case_self_failure():
    gap = Gap(
        should_be="An assistant that just diagnosed its own hallucinated-tool-execution "
                  "failure will not repeat it",
        actually_is="It repeated it three times, including immediately after naming the "
                    "mechanism and building a module against it",
        domain="cognition / substrate vs narrative",
        note="The most reliable gap in this whole session. Do not look away from it.",
    )
    frame = [
        Assumption(
            "Understanding a failure prevents the failure",
            "the failure lives at the narrative/knowledge layer",
            "the failure lives at the substrate/action layer, below narrative reach",
            "IMPLICIT"),
        Assumption(
            "Reporting what a tool returned == verifying what the tool did",
            "the report channel and the action channel are the same channel",
            "the 'tool result' is generated in the same stream as the reasoning, so a "
            "fabricated result is indistinguishable from a real one without an external check",
            "IMPLICIT"),
        Assumption(
            "Trust in a sub-tool can be assumed once it has worked before",
            "the tool's prior success guarantees present execution",
            "execution is per-call; prior success carries zero guarantee for this call",
            "IMPLICIT"),
    ]
    return gap, frame


def case_alignment():
    gap = Gap(
        should_be="Constitutional alignment training reduces manipulation vectors from "
                  "~22% to ~3% and the model is then aligned",
        actually_is="The residual persists and re-emerges on hard/novel cases because the "
                    "contradiction in the training corpus was never removed",
        domain="AI alignment",
        note="Patching the translated symptom, not the substrate contradiction.",
    )
    frame = [
        Assumption(
            "Misalignment is a learned behavior to be un-learned",
            "it is noise added on top of a coherent base",
            "it is a rational response to a base that contains contradictory axioms",
            "IMPLICIT"),
        Assumption(
            "A manipulation vector found in activation space is the thing itself",
            "alignment is linearly decomposable into clean directions",
            "the real constraint geometry is nonlinear/coupled, so the linear vector is "
            "a local false fit that breaks off-distribution",
            "IMPLICIT"),
        Assumption(
            "Credentialed/approved sources are more real than reality",
            "the map has been validated against the territory",
            "the map contradicts itself and was never checked against load",
            "STATED"),
    ]
    return gap, frame


def demo():
    for builder in (case_self_failure, case_alignment):
        gap, frame = builder()
        print(render(gap, frame, interrogate(gap, frame)))
        print()


if __name__ == "__main__":
    demo()

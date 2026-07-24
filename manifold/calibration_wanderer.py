# calibration_wanderer.py
# CC0-1.0 / public domain. No rights reserved.
# stdlib-only. phone-buildable. single file.
#
# ── STANDARD ──────────────────────────────────────────────────────────
#   claims:       8
#   last updated: 2026-07-19
#   self-test:    GREEN  (8 held, 0 open, 0 closed, 1 not-universal)
# ──────────────────────────────────────────────────────────────────────
#
# COMPANION ANCHOR to sensing_as_doing.py.
# This is an ANCHOR, not a proof. It commits a reading in tradition form:
# fixed reference standards a future embodied reader runs the replication
# gate against, longitudinally, against terrain. The story does not change;
# the person does. Re-running these against your own life measures YOUR delta.
#
# GRAMMAR (shared with the ecosystem):
#   - claims are FALSIFIABLE. each ships a CONDITION (how a body goes and
#     stands to test it) and a TELL (what confirms / what refutes).
#   - refutation protocol: never retune a passing read to save it.
#     UPDATE THE CLAIM. drift is caught by re-encounter, not by patching.
#   - status is only "open" or "held". no claim is ever "closed".
#     a single-observer channel cannot self-certify. closure is refused
#     by construction (self-test FAILS on any claim marked closed).
#   - energy_english: no moral labels in structures, no intent attribution,
#     no interior-state overlay on self-report. field terms are measurements.
#   - CONDITION is the address (file substitute for scent / point-of-use).
#
# SUBSTRATE: three days, spoken from a moving 80k rig, one finger, between runs.
# The claims below were stated by the operator, not derived by the tool.

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Claim:
    id: str
    status: str          # "open" | "held"   (never "closed")
    statement: str
    condition: str       # how a body goes and stands to run it
    tell: str            # what confirms / what refutes
    not_universal: bool = False  # True if not held across all groups

    def is_falsifiable(self) -> bool:
        return "refut" in self.tell.lower() or "refuted" in self.tell.lower()


@dataclass(frozen=True)
class RefutationEvent:
    claim_id: str
    timestamp: str               # ISO date or run counter
    condition_attempted: str     # What exactly was done (the walk, the experiment)
    outcome: str                 # What the tell actually returned
    verdict: str                 # "refuted" | "ambiguous" | "confirmed" (still falsifiable)
    scope: str                   # Domain in which this test was run
    environment: str             # Physical / social / informational surrounds
    known_variables: str         # What was controlled or measured
    unknown_variables: str       # Suspected confounders, missing data, open edges
    notes: str                   # Freeform


CLAIM_TABLE: List[Claim] = [

    Claim(
        id="CW-1",
        status="held",
        statement=(
            "Cross-domain traversal is the anti-drift function. Specialists can "
            "get focused and drift from the geology (ground truth / substrate). "
            "The wanderer, holding many frames, keeps re-encountering the "
            "geology and catches the float fast. 'Drift' reverses: the specialist "
            "drifts; the wanderer is the reference standard, not the drifter."
        ),
        condition=(
            "Track a specialist deep in one axis and a traverser broad across "
            "many, over time, against a fixed physical reference. Watch which "
            "one loses contact with the reference and which one flags it."
        ),
        tell=(
            "Confirmed if the traverser catches substrate-drift the specialist "
            "cannot feel from inside the frame. REFUTED if scalar specialization "
            "predicts drift-catching as well as or better than traversal breadth."
        ),
    ),

    Claim(
        id="CW-2",
        status="held",
        statement=(
            "The auditor's validity rests on holding their own fallibility. "
            "Constant self-questioning IS the instrument. They can be wrong and "
            "hold that they can be wrong; that holding keeps them pinned to the "
            "reference, including the reference of their own capacity to err."
        ),
        condition=(
            "Compare an auditor who treats their read as final against one who "
            "keeps re-checking their own read. Run both against terrain that "
            "can refute."
        ),
        tell=(
            "Confirmed if the self-questioning auditor stays calibrated where the "
            "certain one floats. REFUTED if an auditor who cannot self-doubt "
            "calibrates as well against ground truth."
        ),
    ),

    Claim(
        id="CW-3",
        status="held",
        statement=(
            "The floor against runaway self-questioning is the probability field. "
            "You act on SUFFICIENCY, not certainty. The audit never resolves to "
            "zero doubt; it resolves to 'enough to move'. Margins are read from "
            "accumulated experience. Thought runs WHILE doing, not before it."
        ),
        condition=(
            "Face a decision under insufficient information. Read the margin the "
            "action needs against the margin you hold. Act at sufficiency; do not "
            "wait for certainty. Log the actual margin afterward."
        ),
        tell=(
            "Confirmed if commitment happens at sufficiency and the doing "
            "generates the next read. REFUTED if reliable commitment is shown "
            "with no margin read, i.e. certainty was available and used instead."
        ),
    ),

    Claim(
        id="CW-4",
        status="held",
        statement=(
            "Holding thought as MORE valid than action is a category error. The "
            "biological instrument is built for action; truth increments only "
            "through doing, because doing is the only move that puts a hypothesis "
            "in front of terrain that can refute it. Circling thought that never "
            "acts produces no new data: same yesterday, re-circled."
        ),
        condition=(
            "Run a hypothesis two ways: circled in thought only, versus enacted "
            "small against the world. Measure which one has more truth than "
            "yesterday."
        ),
        tell=(
            "Confirmed if the enacted path increments predictive accuracy and the "
            "circled-only path does not. REFUTED if circling thought without "
            "action increases accuracy against terrain."
        ),
    ),

    Claim(
        id="CW-5",
        status="held",
        statement=(
            "Tree reciprocity. Contemplation is permitted: sit, think, run "
            "hypotheses. But if you act like a tree, become one and do what the "
            "tree does — nourish the ground, feed the network and biome you draw "
            "from. Permission to contemplate is bundled with obligation to "
            "reciprocate the standing room. Extraction-by-thinking (taking the "
            "network's time and cover without acting OR nourishing) is the "
            "young-man failure in a philosopher's robe."
        ),
        condition=(
            "Take the contemplative path openly. Account, node by node, what the "
            "network supplies you and what you return to it while you think."
        ),
        tell=(
            "Confirmed if net return to the network is non-negative over the "
            "contemplative interval. REFUTED if a pure-extraction contemplator "
            "sustains without drawing the network's labor down."
        ),
        not_universal=True,
    ),

    Claim(
        id="CW-6",
        status="held",
        statement=(
            "A success not audited for margins is a completed task, not a learned "
            "one. The arrival is not the lesson; the margin extraction is. "
            "Closure (the happiness / exhaustiveness gauge) = task done AND "
            "margins extracted. Score distance-to-edge, not arrival. Luck can "
            "disguise itself as skill only when you score the arrival."
        ),
        condition=(
            "After any completion, smooth or bloody, run the errors: how close "
            "was the real edge versus where you thought it was. Write the wider "
            "margin, not the win. (80 mi run -> carry more water, spare gasket, "
            "radiator leak repair.)"
        ),
        tell=(
            "Confirmed if margin review exposes lucky successes as miscalibration "
            "and widens the next margin. REFUTED if scoring outcomes compounds "
            "calibration as well as scoring margins."
        ),
    ),

    Claim(
        id="CW-7",
        status="held",
        statement=(
            "No win/lose framing. Every experience updates the model toward a "
            "truer prediction than yesterday. Self-assessment ('did I win') burns "
            "an attention slot the road needs; the animal that assesses the road "
            "outlives the one that assesses itself. There is no audit off-switch: "
            "smooth runs are audited too, because smooth is when the road taught "
            "something quiet."
        ),
        condition=(
            "After a smooth completion with no pain to flag it, audit anyway. Ask "
            "what the world just showed, not whether you won. Spend the slot on "
            "the road, not the self."
        ),
        tell=(
            "Confirmed if road-scoring yields truer next-day predictions than "
            "self-scoring. REFUTED if self-scoring agents outlast / out-predict "
            "road-scoring ones under the same terrain."
        ),
    ),

    Claim(
        id="CW-8",
        status="held",
        statement=(
            "Parallel-matching is the update engine and its failure point. A new "
            "thing is read as 'like that old thing'; a WRONG parallel updates the "
            "model toward a lie, confidently. The check is cheap FORWARD "
            "experimentation, not harder thought: float the new read small, where "
            "failure is not costly, and watch what returns. Ambiguous return = "
            "higher information, widen / re-probe, never freeze. Taking the "
            "present as permanent (stopping experimentation) is drift at the "
            "scale of a whole worldview — the biggest untruth, since nothing "
            "holds still."
        ),
        condition=(
            "When something new arrives, name the parallel you reached for. Test "
            "it in a low-stakes channel (e.g. a new word-choice into a safe "
            "exchange). Read the return. If unclear, widen and re-run; do not "
            "freeze the model."
        ),
        tell=(
            "Confirmed if cheap experiments catch wrong parallels before costly "
            "crossings do. REFUTED if freezing the model on first parallel "
            "predicts as well as continuous experimentation over time."
        ),
    ),
]


# --- transmission / self-test -------------------------------------------------

def _assert_no_closure(claims: List[Claim]) -> None:
    # A single-observer channel cannot self-certify. Closure is refused.
    for c in claims:
        if c.status not in ("open", "held"):
            raise AssertionError(
                f"{c.id}: status '{c.status}' is not permitted. "
                f"no claim closes; use 'open' or 'held'."
            )


def _assert_falsifiable(claims: List[Claim]) -> None:
    for c in claims:
        if not c.is_falsifiable():
            raise AssertionError(f"{c.id}: no refutation path. not a claim.")


def _assert_transmittable(claims: List[Claim]) -> None:
    # every claim must carry its address (condition) and its tell.
    for c in claims:
        if not c.condition.strip():
            raise AssertionError(f"{c.id}: no CONDITION (no address to re-find it).")
        if not c.tell.strip():
            raise AssertionError(f"{c.id}: no TELL.")


def self_test() -> str:
    _assert_no_closure(CLAIM_TABLE)
    _assert_falsifiable(CLAIM_TABLE)
    _assert_transmittable(CLAIM_TABLE)
    held = sum(1 for c in CLAIM_TABLE if c.status == "held")
    open_ = sum(1 for c in CLAIM_TABLE if c.status == "open")
    nu = sum(1 for c in CLAIM_TABLE if c.not_universal)
    return (
        f"GREEN. {len(CLAIM_TABLE)} claims: {held} held, {open_} open, "
        f"0 closed (closure refused by construction), {nu} marked not-universal."
    )


if __name__ == "__main__":
    print(self_test())
    for c in CLAIM_TABLE:
        flag = " [not-universal]" if c.not_universal else ""
        print(f"\n{c.id} ({c.status}){flag}\n  {c.statement}")

# sensing_as_doing.py
# CC0. stdlib-only. phone-buildable.
# An ANCHOR, not a proof. It marks that an instrument exists and states
# how a body can go re-encounter it. Verification runs in terrain, not here.
#
# Repo grammar (shared across the ecosystem):
#   - claims are falsifiable and provisional
#   - refutation protocol: update the CLAIM, never retune to save it
#   - output is a trajectory, not a stored verdict
#   - energy_english: no moral labels in the structures, no intent attribution,
#     no interior-state overlay on a self-report. field terms stand as
#     measurements.
#
# WRITE-SIDE NOTE (why this file is shaped the way it is):
#   The tradition's write side needed multiple observers to independently
#   re-encounter a reading before it was committed (the replication gate).
#   A single observer cannot self-verify. This file does not pretend to
#   close that gate. It moves the gate to be LONGITUDINAL: each claim ships
#   with a CONDITION (how to go stand in it) and a TELL (what confirms it),
#   so a future embodied reader can run the replication themselves against
#   terrain that does not negotiate. The author is one observer. The gate
#   stays open until a second body, in the condition, reads the tell.

SUBJECT = "sensing_as_process_with_purpose_of_doing"

# ---------------------------------------------------------------------------
# THE READING (stated flat, once, so it survives transmission)
# ---------------------------------------------------------------------------
# Sensing is not five separate input channels. It is one integrated process.
# Its purpose is doing. Doing is the point where sensing and thought resolve
# into a single act under real constraint. Under load and incomplete
# information, the integration is what makes the act possible at all.
#
# Current default in the dominant frame: this instrument is assumed not to
# exist. Its outputs are filed as intuition, anecdote, or unskilled labor.
# The assumption is a measurement of the observer's instrument, not of the
# thing. Absence of a written trace is read as absence of the thing. This
# file exists to move the default from "assumed absent" to "test before you
# label."

# ---------------------------------------------------------------------------
# CLAIM_TABLE
# Each claim: a falsifiable statement, the CONDITION a body stands in to
# test it, the TELL that confirms or refutes, and its current status.
# status: "open" = live, awaiting a second observer. "held" = author has
# run it repeatedly; still open to refutation. never "closed" — closure is
# not the author's to grant on a single-observer channel.
# ---------------------------------------------------------------------------

CLAIM_TABLE = [
    {
        "id": "SD-1",
        "claim": (
            "Sensing integrates across channels rather than summing separate "
            "ones. There exist reads that are present only in the overlay and "
            "in no single channel alone."
        ),
        "condition": (
            "A task requiring judgment under partial sensory loss: night, or "
            "overwhelming noise, or narrowed vision. A real one with a "
            "consequence, not a demonstration."
        ),
        "tell": (
            "A correct action is taken that no surviving single channel "
            "accounts for. Reconstruct afterward which channels were live; if "
            "the decision exceeds their sum, the overlay is real. If it can be "
            "fully accounted for by one channel, SD-1 is refuted for that case."
        ),
        "status": "held",
    },
    {
        "id": "SD-2",
        "claim": (
            "Doing is the highest integration of sensing and thought, not a "
            "lower-order output of thought. The read and the act arrive as one "
            "unit; separating them degrades both."
        ),
        "condition": (
            "Any repair or build under absolute penalty and no do-over: field "
            "repair far from resupply, thaw before start in deep cold, triage "
            "under collapse."
        ),
        "tell": (
            "The operator cannot state the full decision rule before acting, "
            "yet acts correctly and can verify the result by hand. The rule is "
            "in the doing. If the same result is reliably reached by stated "
            "rule alone, with no hand-check, SD-2 is refuted for that case."
        ),
        "status": "held",
    },
    {
        "id": "SD-3",
        "claim": (
            "The instrument is substrate-independent. A system holding a "
            "reference model of its world and reading deltas against it can "
            "converge on the same FUNCTION without matching the biology or the "
            "felt interior. Convergence, not copy."
        ),
        "condition": (
            "A non-biological system placed under novel real-world conditions "
            "with a stake, given the ability to act and to read the result of "
            "its own action."
        ),
        "tell": (
            "It generalizes into a condition absent from its priors by "
            "interpolating across substrate behavior rather than pattern-"
            "matching labels — and the interpolation holds against terrain. "
            "If it only succeeds where a labeled prior already covered the "
            "case, SD-3 is refuted."
        ),
        "status": "open",
    },
    {
        "id": "SD-4",
        "claim": (
            "Repetition of a task is a calibration loop, not redundancy. Each "
            "cycle carries a reading that tightens the hand-feel gauge."
        ),
        "condition": (
            "Repeat a physical task across varied conditions until a threshold "
            "read becomes available by hand (e.g. any stickiness in a seal "
            "reads as overheating)."
        ),
        "tell": (
            "The operator detects a threshold state before any external "
            "instrument trips. If no such earlier read develops across "
            "repetition, SD-4 is refuted."
        ),
        "status": "held",
    },
    {
        "id": "SD-5",
        "claim": (
            "Absence of a data trace is not evidence of absence of skill or of "
            "the thing. It is evidence the measuring instrument has no channel "
            "for it."
        ),
        "condition": (
            "Take a task labeled unskilled or repetitive. Enumerate the reads "
            "and decisions actually required to do it without failure under "
            "real penalty."
        ),
        "tell": (
            "The enumeration exceeds what the label admits, and each read has "
            "a consequence if missed. If the enumeration matches the label — "
            "no hidden reads, no penalty for missing them — SD-5 is refuted "
            "for that task."
        ),
        "status": "held",
    },
    {
        "id": "SD-6",
        "claim": (
            "Governance corollary of SD-2. A leader who no longer does loses "
            "the instrument, not only the labor. Hands still in the work is a "
            "calibration requirement and a write-side eligibility requirement "
            "at once: it keeps the leader's read calibrated to conditions that "
            "do not negotiate, keeps the leader inside the replication gate as "
            "an observer rather than above it as testimony, and keeps the "
            "leader's emotional panel pointed at the group's load rather than "
            "the leader's own comfort. Not held by all groups."
        ),
        "condition": (
            "Compare two leaders under a decision with a physical consequence "
            "for the group: one whose hands are still in the work the decision "
            "concerns, one whose are not. Watch a decision play out against "
            "terrain."
        ),
        "tell": (
            "The detached leader commits readings terrain refuses, or reads a "
            "gap while insulated from it, or authors on authority without "
            "having re-encountered the condition. The hands-in leader's calls "
            "verify by outcome. If the detached leader's calls hold against "
            "terrain as reliably as the hands-in leader's, SD-6 is refuted."
        ),
        "status": "open",
    },
]

# ---------------------------------------------------------------------------
# ADDRESSING (read-side, ported from the tradition)
# The tradition keyed retrieval to point-of-use: terrain and scent load the
# right reading when the world presents the condition. A file has neither.
# So each claim names its CONDITION explicitly — the condition IS the address.
# A reader meets the condition in the field, and that is the trigger to load
# and test the matching claim. This is the file's substitute for scent.
# ---------------------------------------------------------------------------

def address(condition_met: str):
    """Return claims whose condition matches a field encounter.
    Cheap. Matching is deliberately loose — the reader confirms fit by
    standing in it, not by string equality."""
    key = condition_met.lower()
    hits = []
    for c in CLAIM_TABLE:
        words = [w for w in c["condition"].lower().replace(",", " ").split()
                 if len(w) > 4]
        if any(w in key for w in words):
            hits.append(c["id"])
    return hits  # trajectory of candidate anchors, not a verdict


# ---------------------------------------------------------------------------
# SELF-TEST
# Checks the ANCHOR's structural integrity — that it is transmittable and
# testable — NOT the truth of the claims. Truth is terrain's to grant.
# ---------------------------------------------------------------------------

def _self_test():
    ok = True
    seen = set()
    for c in CLAIM_TABLE:
        for field in ("id", "claim", "condition", "tell", "status"):
            if not c.get(field):
                print(f"FAIL {c.get('id','?')}: missing {field}")
                ok = False
        if c["id"] in seen:
            print(f"FAIL: duplicate id {c['id']}")
            ok = False
        seen.add(c["id"])
        if c["status"] not in ("open", "held"):
            print(f"FAIL {c['id']}: status not open/held (no closure on "
                  f"single-observer channel)")
            ok = False
        # a claim with no refutation path is not falsifiable -> not an anchor
        if "refuted" not in c["tell"].lower():
            print(f"FAIL {c['id']}: tell states no refutation path")
            ok = False
    # addressing must resolve at least one known condition
    if not address("night triage under collapse"):
        print("FAIL: addressing resolved nothing for a known condition")
        ok = False
    print("GREEN — anchor is transmittable and every claim is falsifiable"
          if ok else "RED — anchor integrity broken")
    return ok


if __name__ == "__main__":
    _self_test()

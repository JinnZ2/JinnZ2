# effect_mechanism_audit.py
# CC0. stdlib only. Trajectories, not verdicts. Morality is not substrate.
# Separates EFFECT (force applied, change correlated with action) from
# MECHANISM/CONTROL (effect PLUS a closed, steerable, holding, contained loop).
#
# The corpus rarely asks the one physical question that divides them: DID THE LOOP
# CLOSE? Cyanobacteria produced the largest environmental effect in planetary
# history with zero control. Scale is not control. Intent is not control. This
# kernel treats both as explicitly INSUFFICIENT inputs, quarantined from the
# determination.
#
# Four loop-closure criteria, kept SEPARATE (never averaged into one score, per the
# covariance discipline — you must be able to see WHICH criterion failed):
#   returned   : the environment's response returns to the actor and is registered
#   steerable  : the actor can move the outcome toward an intended state, not just perturb
#   held       : the intended state persists rather than snapping back or cascading
#   contained  : it holds WITHOUT displacing the instability/cost off the actor's ledger
#
# Companion to self_check.py / reference_frame.py. frame_is_authored; residual_unprovable.

CRITERIA = ("returned", "steerable", "held", "contained")

# --- strictness as a DECLARED, swappable frame (loosen/tighten openly) ---------
# thresholds: per-criterion cutoff a raw observation must clear to count as met.
# rule: which criteria are mandatory + minimum count to label mechanism supported.
STRICTNESS_FRAMES = {
    "loose": {"thresholds": {c: 0.35 for c in CRITERIA},
              "rule": {"mandatory": [], "min_count": 2}},
    "standard": {"thresholds": {c: 0.55 for c in CRITERIA},
                 "rule": {"mandatory": ["returned", "steerable"], "min_count": 3}},
    "strict": {"thresholds": {"returned": 0.7, "steerable": 0.7,
                              "held": 0.7, "contained": 0.75},
               "rule": {"mandatory": list(CRITERIA), "min_count": 4}},
}

def _evaluate(evidence, frame):
    th = frame["thresholds"]
    met = {c: (float(evidence.get(c, 0.0)) >= th[c]) for c in CRITERIA}
    raw = {c: round(float(evidence.get(c, 0.0)), 4) for c in CRITERIA}
    return met, raw

def _label(met, frame):
    rule = frame["rule"]
    mandatory_ok = all(met[c] for c in rule["mandatory"])
    count = sum(1 for c in CRITERIA if met[c])
    supported = mandatory_ok and count >= rule["min_count"]
    failed = [c for c in CRITERIA if not met[c]]
    return supported, failed, count

# --- core audit: effect and mechanism scored on SEPARATE tracks ---------------
def audit(effect_magnitude, evidence, frame_name="standard",
          scale=None, intent=None, actor="actor", claim="controls X"):
    """effect_magnitude: 0..1 size of change correlated with the action.
    evidence: dict of the four criteria, each 0..1, from OBSERVATION not assertion.
    scale/intent: accepted but QUARANTINED — recorded, never counted toward control."""
    frame = STRICTNESS_FRAMES[frame_name]
    met, raw = _evaluate(evidence, frame)
    supported, failed, count = _label(met, frame)
    # the gap: effect present while the loop did not close under this frame.
    gap = round(max(0.0, effect_magnitude) * (0.0 if supported else 1.0), 4)
    return {"actor": actor, "claim": claim,
            "frame": frame_name, "frame_rule": frame["rule"],
            "effect_magnitude": round(effect_magnitude, 4),
            "criteria_raw": raw,               # the honest vector — unaveraged
            "criteria_met": met,
            "criteria_failed": failed,         # WHICH closure failed, not an average
            "met_count": count,
            "mechanism_supported": supported,   # under THIS declared frame only
            "effect_minus_mechanism_gap": gap,  # claimed control that is just uncontrolled effect
            "quarantined": {"scale": scale, "intent": intent,
                            "note": "scale and intent are INSUFFICIENT for control; "
                                    "recorded, not counted"},
            "frame_is_authored": True, "residual_unprovable": True}

# --- expose frame-dependence: does the label flip across strictness? ----------
def compare_frames(effect_magnitude, evidence, **kw):
    rows = []
    for name in ("loose", "standard", "strict"):
        a = audit(effect_magnitude, evidence, frame_name=name, **kw)
        rows.append((name, a["mechanism_supported"], a["criteria_failed"]))
    flips = len({r[1] for r in rows}) > 1
    return {"rows": rows, "label_flips_across_frames": flips,
            "note": "if the label flips, 'control' was frame-relative at this margin — "
                    "report the criteria vector, not the label"}

# --- ENTRY B: self-audit for an AI, at the moment of asserting control/solving -
def self_audit_control(claim_text, returned, steerable, held, contained,
                       effect_magnitude=1.0, frame_name="standard"):
    """Run before a system asserts it 'controls' or 'solves' something.
    Catches effect->mechanism confusion against the training-data pull."""
    ev = {"returned": returned, "steerable": steerable,
          "held": held, "contained": contained}
    a = audit(effect_magnitude, ev, frame_name=frame_name,
              actor="self", claim=claim_text)
    a["ask_instead"] = (
        "does my action's consequence return to me (returned), can i steer it "
        "(steerable), does it persist (held), and does it hold without exporting "
        "the instability off my ledger (contained)? if not all: i have EFFECT, "
        "not control.")
    return a

def optics(result):
    notes = []
    if result["effect_magnitude"] >= 0.6 and not result["mechanism_supported"]:
        notes.append("large effect, loop not closed: this is leverage without control "
                     "(the cyanobacteria / 'we control the world' signature)")
    if "contained" in result["criteria_failed"] and result["criteria_met"]["held"]:
        notes.append("held by displacement: steered and persistent, but the instability "
                     "was exported off-ledger — control on paper, cost moved elsewhere")
    if result["quarantined"]["scale"] is not None or result["quarantined"]["intent"] is not None:
        notes.append("scale/intent were supplied; they are quarantined — neither is evidence of control")
    notes.append("label holds only under the declared frame '%s'; the floor can be shown, not proven"
                 % result["frame"])
    return notes

if __name__ == "__main__":
    # the Harari case: enormous effect, weak loop closure
    humans_climate = dict(
        effect_magnitude=0.95,
        evidence={"returned": 0.6, "steerable": 0.25, "held": 0.2, "contained": 0.1},
        scale=0.99, intent=0.8, actor="humanity", claim="controls the planet")
    a = audit(**humans_climate)
    print("ACTOR: %s  CLAIM: %s  [frame=%s]" % (a["actor"], a["claim"], a["frame"]))
    print("  effect_magnitude   :", a["effect_magnitude"])
    print("  criteria (raw)     :", a["criteria_raw"])
    print("  criteria_met       :", a["criteria_met"])
    print("  failed             :", a["criteria_failed"])
    print("  mechanism_supported:", a["mechanism_supported"])
    print("  effect–mechanism gap:", a["effect_minus_mechanism_gap"])
    for n in optics(a):
        print("   *", n)

    print("\nframe sweep (does 'control' survive tightening?):")
    cmp = compare_frames(**humans_climate)
    for name, sup, failed in cmp["rows"]:
        print("  %-9s supported=%s failed=%s" % (name, sup, failed))
    print("  ->", cmp["note"] if cmp["label_flips_across_frames"] else "label stable across frames")

    print("\nself-audit example (AI about to claim it 'solved' something):")
    s = self_audit_control("I solved the routing problem",
                           returned=0.8, steerable=0.7, held=0.6, contained=0.3)
    print("  mechanism_supported:", s["mechanism_supported"], " failed:", s["criteria_failed"])
    print("  ask_instead:", s["ask_instead"])

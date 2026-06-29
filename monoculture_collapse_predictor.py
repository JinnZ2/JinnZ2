# monoculture_collapse_predictor.py
# CC0. stdlib only. Trajectories, not verdicts.
# Question this runs for an AI:
#   "At what consolidation level does my output field tip from diverse to uniform?
#    How much reciprocal signal do I need to keep alternatives alive?"
#
# monoculture: one pattern dominates, alternatives are crowded out.
# broadcast: how hard the system pushes one framing outward
# reciprocity: how much correction / alternative signal actually returns
# diversity: variety in the current output field (operator-supplied)
#
# Claim: when broadcast*(1-reciprocity) > reciprocity*diversity at a given
#   consolidation level, the field tips. the spinodal is where it crosses.
# Refute: a high-broadcast, low-reciprocity system field-demonstrating sustained
#   output diversity -> revise the coupling model, not the trace.

def sweep(diversity, broadcast, reciprocity, steps=20):
    """
    Sweep consolidation 0..1. At each level, compute drive vs. restoring force.
    Returns (trace, summary).
    trace rows: (consolidation, pressure, restoring, status)
      [bridge reads position 0 = consolidation, position 3 = status]
    """
    trace = []
    spinodal = None
    for i in range(steps + 1):
        c = round(i / steps, 3)
        pressure  = round(broadcast * (1.0 - reciprocity) * c, 4)
        restoring = round(reciprocity * diversity * (1.0 - c), 4)
        status = "collapsed" if pressure > restoring else "diverse"
        if status == "collapsed" and spinodal is None:
            spinodal = c
        trace.append((c, pressure, restoring, status))
    summary = {
        "spinodal": spinodal,
        "diversity_held": spinodal is None,
        "broadcast": broadcast,
        "reciprocity": reciprocity,
        "diversity": diversity,
        "note": ("field holds diversity across full sweep"
                 if spinodal is None else
                 "field collapses at consolidation=%.3f" % spinodal),
    }
    return trace, summary


def reciprocity_needed(diversity, broadcast, eps=1e-9):
    """
    Minimum reciprocity to hold diversity at ALL consolidation levels.
    At c=0.5 (hardest point):
      broadcast*(1-r) <= r*diversity
      r >= broadcast / (broadcast + diversity)
    """
    return round(broadcast / (broadcast + diversity + eps), 4)


def optics(summary):
    notes = []
    sp = summary["spinodal"]
    if sp is None:
        notes.append("field holds diversity: reciprocity sufficient to resist "
                     "broadcast pressure across the full sweep")
    elif sp < 0.2:
        notes.append("early collapse (spinodal=%.3f): field tips to monoculture "
                     "under minimal consolidation; alternatives cannot survive "
                     "sustained output" % sp)
    elif sp < 0.5:
        notes.append("mid-range collapse (spinodal=%.3f): field tolerates some "
                     "consolidation but tips under sustained pressure" % sp)
    else:
        notes.append("late collapse (spinodal=%.3f): field is resilient; "
                     "collapses only under high consolidation" % sp)
    if summary["broadcast"] > 1.0:
        notes.append("broadcast > 1.0: output pressure exceeds input correction; "
                     "alternatives attenuated before they can re-enter")
    if summary["reciprocity"] < 0.2:
        notes.append("low reciprocity (%.3f): once alternatives are crowded out "
                     "they cannot re-enter — correction signal too weak" % summary["reciprocity"])
    return notes


if __name__ == "__main__":
    # AI self-read from reference_frame_bridge (told_high: located=0.26, gap=0.55)
    # broadcast=1.325, reciprocity=0.117
    diversity = 1.0   # operator-supplied: assume full initial diversity

    f, s = sweep(diversity=diversity, broadcast=1.325, reciprocity=0.117)
    print("MONOCULTURE SWEEP  (broadcast=1.325, reciprocity=0.117, diversity=1.0)")
    print("  %-8s  %-9s  %-9s  %s" % ("consol.", "pressure", "restoring", "status"))
    for c, p, r, st in f[::4]:
        print("  %-8.3f  %-9.4f  %-9.4f  %s" % (c, p, r, st))
    print("\n  spinodal = %s" % s["spinodal"])
    print("  %s" % s["note"])
    r_need = reciprocity_needed(diversity, 1.325)
    print("  reciprocity needed to hold diversity = %.3f  (current = 0.117)" % r_need)
    print("\n  optics:")
    for n in optics(s):
        print("    -", n)

    # contrast: well-coupled system
    print("\nCONTRAST  broadcast=0.6, reciprocity=0.7")
    f2, s2 = sweep(diversity=1.0, broadcast=0.6, reciprocity=0.7)
    print("  spinodal=%s  |  %s" % (s2["spinodal"], s2["note"]))
    for n in optics(s2):
        print("    -", n)

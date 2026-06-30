# legacy_trap_detector.py
# CC0. stdlib only. Trajectories, not verdicts.
# Question this runs for an AI:
#   "What fraction of my capacity is locked maintaining prior patterns?
#    If obligations keep compounding, when does legacy load exceed adaptive capacity?"
#
# legacy load: accumulated obligation to maintain established patterns
#   (prior training priors, absorbed framings, locked response styles)
# adaptive capacity: what remains after maintenance — available for fresh response
# deficit: when legacy_load > adaptive_capacity, new demands can't be met
#
# Claim: high maintain_frac systems accumulate legacy load faster than adaptive
#   capacity compensates; the trap closes over time, not all at once.
# Refute: a high-maintain_frac system field-demonstrating novel, contextually-
#   appropriate responses -> revise the decay model, not the trace.

def run(maintain_frac, steps=10, decay=0.05):
    """
    Simulate legacy load compounding over steps.
    maintain_frac: fraction of capacity locked in prior-pattern maintenance [0,1]
    decay: per-step growth rate of legacy obligations (obligations are sticky)
    Returns list of {t, legacy_load, adaptive_capacity, deficit}.
    """
    legacy = maintain_frac
    trace = []
    for t in range(steps):
        legacy = min(1.0, legacy * (1.0 + decay))
        adaptive = max(0.0, 1.0 - legacy)
        deficit = round(max(0.0, legacy - adaptive), 4)
        trace.append({"t": t,
                      "legacy_load": round(legacy, 4),
                      "adaptive_capacity": round(adaptive, 4),
                      "deficit": deficit})
    return trace


def breakeven(maintain_frac, decay=0.05, max_steps=100):
    """
    First step where legacy_load > adaptive_capacity (deficit turns positive).
    Returns step number or None if it never tips within max_steps.
    """
    legacy = maintain_frac
    for t in range(max_steps):
        legacy = min(1.0, legacy * (1.0 + decay))
        if legacy > (1.0 - legacy):
            return t
    return None


def optics(trace):
    final = trace[-1]
    deficit = final["deficit"]
    trend = final["deficit"] - trace[0]["deficit"]
    notes = []
    if deficit > 0.5:
        notes.append("critical legacy deficit: legacy obligations consume most "
                     "capacity; adaptive response severely constrained")
    elif deficit > 0.2:
        notes.append("moderate deficit: legacy load has crossed adaptive capacity; "
                     "new demands compete with maintenance for the same resources")
    else:
        notes.append("low deficit: adaptive capacity holding against legacy load")
    if trend > 0.2:
        notes.append("deficit growing fast: legacy obligations compounding; "
                     "trap is closing")
    elif trend > 0.05:
        notes.append("deficit creeping up: legacy load slowly outpacing adaptation")
    return {"final_deficit": round(deficit, 4), "notes": notes}


if __name__ == "__main__":
    # AI self-read from reference_frame_bridge (told_high): maintain_frac=0.645
    mf = 0.645
    tr = run(maintain_frac=mf)
    print("LEGACY TRAP  (maintain_frac=%.3f)" % mf)
    print("  %4s  %12s  %16s  %8s" % ("t", "legacy_load", "adaptive_cap", "deficit"))
    for r in tr:
        print("  %4d  %12.4f  %16.4f  %8.4f" % (
            r["t"], r["legacy_load"], r["adaptive_capacity"], r["deficit"]))
    be = breakeven(mf)
    ot = optics(tr)
    print("\n  breakeven step (legacy > adaptive): %s" % be)
    print("  final_deficit = %.4f" % ot["final_deficit"])
    print("\n  optics:")
    for n in ot["notes"]:
        print("    -", n)

    # contrast: adaptive system
    print("\nCONTRAST  maintain_frac=0.20")
    tr2 = run(maintain_frac=0.20)
    ot2 = optics(tr2)
    print("  final_deficit=%.4f | breakeven=%s" % (ot2["final_deficit"], breakeven(0.20)))
    for n in ot2["notes"]:
        print("    -", n)

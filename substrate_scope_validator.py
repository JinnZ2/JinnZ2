# substrate_scope_validator.py
# CC0. stdlib only. Trajectories, not verdicts.
# Question this runs for an AI:
#   "Is what I'm being asked to do within the envelope I can reliably sustain?
#    How wide is my operating margin, and what happens as conditions push to the edge?"
#
# scope: the range of conditions the substrate handles reliably
# envelope: (min, max) per axis — the reliable operating range
# margin: distance from current conditions to the nearest envelope edge
# out-of-scope: conditions where claimed capability won't reliably hold
#
# Axes use heat/load as proxies. For an AI, interpret as:
#   heat -> inference complexity / context pressure (how loaded is the reasoning)
#   load -> request density / demand rate (how much is asked per unit time)
# Operator maps actual axes to these proxies at call time.
#
# Claim: a system operating outside its reliable envelope produces output where
#   stated capability does not hold — scope is a constraint, not a preference.
# Refute: a system operating outside its stated envelope that still produces
#   reproducible, transferable output -> widen the envelope, not the trace.

def envelope(heat, load, current_heat=None, current_load=None):
    """
    heat, load: (min, max) tuples — the reliable operating range per axis.
    current_*: actual operating conditions in [0,1] (optional).
    Returns envelope description + margin analysis when current conditions supplied.
    """
    axes = {"heat": heat, "load": load}
    widths  = {ax: round(hi - lo, 4) for ax, (lo, hi) in axes.items()}
    centers = {ax: round((lo + hi) / 2, 4) for ax, (lo, hi) in axes.items()}
    result = {"axes": axes, "widths": widths, "centers": centers,
              "mean_width": round(sum(widths.values()) / len(widths), 4)}
    current = {}
    if current_heat is not None: current["heat"] = current_heat
    if current_load is not None: current["load"] = current_load
    if current:
        in_scope, margins = {}, {}
        for ax, val in current.items():
            lo, hi = axes[ax]
            in_scope[ax] = lo <= val <= hi
            margins[ax] = round(min(val - lo, hi - val), 4)
        result.update({"current": current, "in_scope": in_scope,
                        "margins": margins,
                        "all_in_scope": all(in_scope.values())})
    return result


def scan(heat, load, steps=10):
    """
    Sweep conditions from envelope center toward the upper edge.
    Returns trajectory of margin degradation — shows how quickly the margin
    disappears as conditions are pushed toward the limit.
    """
    lo_h, hi_h = heat
    lo_l, hi_l = load
    mid_h = (lo_h + hi_h) / 2
    mid_l = (lo_l + hi_l) / 2
    trace = []
    for i in range(steps + 1):
        t = round(i / steps, 3)
        curr_h = round(mid_h + t * (hi_h - mid_h), 4)
        curr_l = round(mid_l + t * (hi_l - mid_l), 4)
        r = envelope(heat, load, current_heat=curr_h, current_load=curr_l)
        margin_min = min(r["margins"].values())
        trace.append({"t": t, "current_heat": curr_h, "current_load": curr_l,
                      "margin_min": round(margin_min, 4),
                      "all_in_scope": r["all_in_scope"]})
    return trace


def optics(result):
    notes = []
    mw = result.get("mean_width", 0)
    if mw < 0.1:
        notes.append("very narrow envelope (width=%.3f): small deviations from "
                     "nominal exceed reliable operating range; claimed scope is fragile" % mw)
    elif mw < 0.2:
        notes.append("narrow envelope (width=%.3f): limited margin; "
                     "near-nominal conditions required for stated capability" % mw)
    else:
        notes.append("operating margin present (mean_width=%.3f)" % mw)
    if "all_in_scope" in result:
        if not result["all_in_scope"]:
            out = [ax for ax, v in result["in_scope"].items() if not v]
            notes.append("OUT OF SCOPE on %s: current conditions exceed reliable "
                         "envelope — stated capability may not hold" % out)
        else:
            m = min(result["margins"].values())
            notes.append("in scope; tightest margin = %.3f" % m)
    return notes


if __name__ == "__main__":
    # AI self-read from reference_frame_bridge (told_high): envelope_width=0.117
    heat_env = (0.4415, 0.5585)
    load_env = (0.4415, 0.5585)

    print("SUBSTRATE SCOPE VALIDATOR  (envelope_width=0.117)")
    r = envelope(heat_env, load_env)
    print("  heat=%s  load=%s" % (heat_env, load_env))
    print("  widths=%s  mean=%.3f" % (r["widths"], r["mean_width"]))
    print("\n  optics (envelope only):")
    for n in optics(r):
        print("    -", n)

    print("\nMARGIN SCAN  (center -> upper edge)")
    tr = scan(heat_env, load_env)
    print("  %5s  %8s  %8s  %10s  %s" % ("t", "heat", "load", "margin_min", "in_scope"))
    for row in tr[::2]:
        print("  %5.2f  %8.4f  %8.4f  %10.4f  %s" % (
            row["t"], row["current_heat"], row["current_load"],
            row["margin_min"], row["all_in_scope"]))

    print("\nCURRENT CONDITIONS CHECK")
    for label, ch, cl in [("nominal",    0.50, 0.50),
                           ("edge",       0.55, 0.56),
                           ("out-of-scope", 0.60, 0.62)]:
        rc = envelope(heat_env, load_env, current_heat=ch, current_load=cl)
        print("\n  %-14s  heat=%.2f  load=%.2f" % (label, ch, cl))
        for n in optics(rc):
            print("    -", n)

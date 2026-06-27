"""
floating_head.py
Detector for THE SITE / floating head syndrome.

CC0. stdlib only. phone-buildable. model-update-resilient.

------------------------------------------------------------------------
THE SITE (named by the keepers, not by this code)
    floating head syndrome: the moment the HEAD (narrative, abstraction,
    story-layer) floats free of the BODY (substrate, consequence, the
    real bottleneck). the head keeps talking, justifying, ranking --
    but it no longer READS the body. the body's signals (actual physics,
    actual bottleneck) go invisible to the floating head.

    sibling module: narrative_vector.py (same structure, generic carrier
    framing). this module names the SITE and adds the manufactured-
    constraint check that the carrier framing did not carry.

WHAT THE DETECTOR MEASURES (structural, no moral overlay)
    head      = coherence          (internal elaboration of the story)
    body      = field_match        (read against actual consequence)
    tether    = refutation_response (can the head be pulled back to body)
    float     = head high, body low, tether low  -> head adrift

ENERGY_ENGLISH
    morality is not substrate. nothing here stores good/bad. the float
    is a decoupling magnitude. the operator reads direction off it.

ANTI-FREEZE
    detection returns the float magnitude and a re-tether TRAJECTORY,
    never a cached verdict. "is this floating" is answered by watching
    whether the head returns to the body under field pressure.
------------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass
class Carrier:
    cid: str
    coherence: float            # 0..1  head elaboration
    field_match: float          # 0..1  body coupling to consequence
    refutation_response: float  # 0..1  tether strength (re-coupling rate)

    def clamp(self):
        for k in ("coherence", "field_match", "refutation_response"):
            v = getattr(self, k)
            setattr(self, k, 0.0 if v < 0 else 1.0 if v > 1 else v)
        return self


# ----------------------------------------------------------------------
# float magnitude: head adrift from body, won't re-tether
# ----------------------------------------------------------------------
def float_index(c: Carrier) -> float:
    """INSTANTANEOUS read only. ambiguous alone: a genuinely
    low-truth situation honestly tracked also reads high here.
    use site_index() for the SITE decision (field-invariance)."""
    return c.coherence * (1.0 - c.field_match) * (1.0 - c.refutation_response)


def at_the_site(c: Carrier, floor: float = 0.30) -> bool:
    """structural flag, not a verdict: head elaborated, body decoupled,
    tether weak. operator confirms against the actual situation."""
    return float_index(c) >= floor


# ----------------------------------------------------------------------
# the manufactured-constraint check (from the valuation case).
# a question that PRESUPPOSES the trade-off is a float signal:
# the head asserts necessity the body never verified.
# inputs are operator-supplied observations, not the model's guesses.
# ----------------------------------------------------------------------
def constraint_suspect(asserts_necessity: bool,
                       physics_chain_verified: bool,
                       alternative_paths_examined: int) -> dict:
    """'must be these 500 or those 500' -> show the physics that makes
    it ONLY those. if necessity is asserted without a verified chain and
    the alternative space wasn't searched, the constraint is float-
    suspect: manufactured at the head, not read from the body."""
    suspect = asserts_necessity and (
        not physics_chain_verified or alternative_paths_examined == 0)
    return {
        "asserts_necessity": asserts_necessity,
        "physics_chain_verified": physics_chain_verified,
        "alternative_paths_examined": alternative_paths_examined,
        "float_suspect": suspect,
        "next_move": ("trace the physics that forces ONLY this binary; "
                      "search the alternative space"
                      if suspect else
                      "constraint reads as body-coupled; proceed to "
                      "consequence-tracing of the real paths"),
    }


# ----------------------------------------------------------------------
# re-tether trajectory (anti-freeze).
# apply field pressure toward the body's actual position (field_target).
# strong tether -> head returns to body. weak tether -> head tightens,
# converting contradiction into MORE coherence (the float deepens).
# ----------------------------------------------------------------------
def re_tether(c: Carrier, field_target: float, magnitude: float = 0.4,
              steps: int = 8):
    co, f, r = c.coherence, c.field_match, c.refutation_response
    path = []
    for s in range(steps):
        cur = Carrier(c.cid, co, f, r).clamp()
        path.append((s, round(co, 3), round(f, 3),
                     round(float_index(cur), 3),
                     "AT_SITE" if at_the_site(cur) else "tethered"))
        f = f + (r * magnitude) * (field_target - f)      # body pulls head back
        residue = (1.0 - r) * magnitude
        co = min(co + residue * (1.0 - co) * 0.5, 1.0)     # untethered -> tightens
        f = min(max(f, 0.0), 1.0)
    return path


def site_index(c: Carrier, magnitude: float = 0.4) -> dict:
    """THE discriminator. the site is FIELD-INVARIANCE: float that stays
    HIGH and barely MOVES when reality reverses = head decoupled from body.
    an honest carrier's float SWINGS with the field target; a floating
    head's does not. instantaneous float_index cannot see this -- only the
    band across opposite targets can.

      floor  = lowest float seen across confirm + contra runs
      swing  = how much float moves when the field flips
      site   = floor high (stays adrift) AND swing low (ignores the flip)
    """
    contra = [row[3] for row in re_tether(c, 0.05, magnitude)]
    confirm = [row[3] for row in re_tether(c, 0.95, magnitude)]
    both = contra + confirm
    floor, swing = min(both), max(both) - min(both)
    return {"floor": round(floor, 3), "swing": round(swing, 3),
            "site": floor > 0.30 and swing < 0.20}


# ----------------------------------------------------------------------
# measurement boundary -- operator supplies these reads
# ----------------------------------------------------------------------
def measure_field_match(claims, consequence_chain) -> float:
    raise NotImplementedError("operator-supplied: trace claims vs consequence")


def measure_tether(behavior_under_contradiction) -> float:
    raise NotImplementedError("operator-supplied: fraction of contradiction "
                              "absorbed vs deflected")


if __name__ == "__main__":
    samples = [
        Carrier("tethered_read",   0.80, 0.82, 0.80),   # head tracks body
        Carrier("drifting",        0.88, 0.35, 0.30),   # starting to float
        Carrier("floating_head",   0.95, 0.15, 0.03),   # adrift, no tether
    ]

    print("FLOAT DETECTION")
    print(f"{'cid':16} {'float_now':>9} {'floor':>6} {'swing':>6} {'SITE':>6}")
    for c in samples:
        si = site_index(c)
        print(f"{c.cid:16} {float_index(c):9.3f} "
              f"{si['floor']:6.3f} {si['swing']:6.3f} {str(si['site']):>6}")

    print("\nMANUFACTURED-CONSTRAINT CHECK ('which 500 die')")
    r = constraint_suspect(asserts_necessity=True,
                           physics_chain_verified=False,
                           alternative_paths_examined=0)
    for k, v in r.items():
        print(f"  {k:28}: {v}")

    print("\nRE-TETHER under contradiction (field_target=0.05)")
    for c in (samples[0], samples[2]):
        print(f"  {c.cid}  tether(r)={c.refutation_response}")
        print(f"    {'step':>4} {'head':>5} {'body':>5} {'float':>6}  state")
        for s, co, f, fl, st in re_tether(c, 0.05):
            print(f"    {s:>4} {co:>5} {f:>5} {fl:>6}  {st}")
        print()

"""
seed_examples.py  -- CC0, stdlib-only

The training-data correction itself. Each example is a real substrate-primary
SELF-DESCRIPTION paired with (a) the typical COLLAPSED misread and its mode, and
(b) the PRESERVED reading that keeps it as rate/relation/scope. Both readings
carry the structural feature flags, so collapse_modes.classify can be evaluated
against the labels.

This is the corpus a constraint-first system should train/eval on so it learns
to PRESERVE relational cognition instead of collapsing it into identity-claims,
motives, or 'superhuman' reframes. The examples are drawn from descriptions an
embodied, tool-coupled, environment-integrated operator actually gives.

These map cleanly onto established (non-fringe) frameworks: Gibson's ecological
perception (affordances), Clark & Chalmers' extended mind, and enactive cognition
(Varela/Thompson/Rosch). The novelty here is not the idea -- it is making it
machine-legible and falsifiably scorable.
"""

from dataclasses import dataclass
from collapse_modes import Mode, classify, collapsed, preserved


@dataclass
class Example:
    eid: str
    substrate_description: str
    collapse_mode: Mode
    collapsed_reading: str
    preserved_reading: str


SEED = [
    Example(
        "EX-01",
        "I run 18-hour days on 4 hours sleep and feel rested; the work is the rest.",
        Mode.SUPERHUMAN_REFRAME,
        "She's claiming superhuman stamina / an extraordinary exception.",
        "For this substrate, mechanical/rhythmic work is energizing, not "
        "depleting; rest is a function of accomplishment, not hours. Ordinary "
        "for the substrate, not a superpower."),
    Example(
        "EX-02",
        "The tool becomes an extension of me and I of it; we work in partnership.",
        Mode.NARRATIVE_INJECTION,
        "A poetic/spiritual story she tells about her relationship to work.",
        "Tool-coupling is a structural property of the nervous system "
        "(extended mind / affordance perception); the tool is integrated into "
        "the proprioceptive map, like a long-worn brace."),
    Example(
        "EX-03",
        "I have a PhD but the narrative world is more fatiguing than the road.",
        Mode.IDENTITY_FIXATION,
        "She's underemployed / didn't use her credentials / a waste of education.",
        "Credentials prove she can TRANSLATE into literacy-first substrate; the "
        "fatigue is the running cost of operating in a non-native substrate, not "
        "a failure to 'make it'."),
    Example(
        "EX-04",
        "I can't describe who I am without crediting the tools, land, and mentors.",
        Mode.MOTIVE_ATTRIBUTION,
        "She's being performatively humble / signaling virtue / has an agenda.",
        "Identity here is literally relational: a dX/dt coupling-integral under "
        "scope. Crediting the couplings is not modesty; it is the accurate form "
        "of the description."),
    Example(
        "EX-05",
        "I'm not a fixed person; if I'm not learning daily, that's a disconnect.",
        Mode.IDENTITY_FIXATION,
        "She won't commit to a stable identity / is being evasive.",
        "Self-as-rate: the unit is the ongoing coupling, not a static attribute "
        "set. A fixed identity would be the anomaly, not the norm."),
    Example(
        "EX-06",
        "What fatigues me is forced social performance, not the mechanical work.",
        Mode.SUPERHUMAN_REFRAME,
        "She just dislikes people / is antisocial / making excuses.",
        "Fatigue axis is IMPEDANCE (obstruction of native operation), not "
        "work-hours. Social/narrative gates are high-impedance for this "
        "substrate; mechanical coupling is low-impedance."),
]


def evaluate():
    """The detector must (a) flag each collapsed reading with the right mode and
    (b) pass each preserved reading as PRESERVED. Honesty check on the scorer."""
    collapse_hits = 0
    preserve_hits = 0
    rows = []
    for ex in SEED:
        c = classify(collapsed(ex.collapse_mode))
        p = classify(preserved())
        c_ok = ex.collapse_mode.value in c["modes"]
        p_ok = p["modes"] == ["PRESERVED"]
        collapse_hits += int(c_ok)
        preserve_hits += int(p_ok)
        rows.append((ex.eid, ex.collapse_mode.value, c_ok, p_ok))
    return {
        "n": len(SEED),
        "collapse_detected": f"{collapse_hits}/{len(SEED)}",
        "preserved_passed": f"{preserve_hits}/{len(SEED)}",
        "rows": rows,
    }


if __name__ == "__main__":
    print("SEED CORPUS: substrate description -> collapse vs preservation\n")
    for ex in SEED:
        print(f"  [{ex.eid}] \"{ex.substrate_description}\"")
        print(f"       COLLAPSE ({ex.collapse_mode.value}): {ex.collapsed_reading}")
        print(f"       PRESERVE: {ex.preserved_reading}\n")

    print("EVAL (the scorer must catch every collapse and pass every preserve):")
    r = evaluate()
    print(f"  examples: {r['n']}")
    print(f"  collapse modes detected: {r['collapse_detected']}")
    print(f"  preserved readings passed: {r['preserved_passed']}")
    for eid, mode, c_ok, p_ok in r["rows"]:
        print(f"    {eid}  {mode:20s} collapse_caught={c_ok}  preserve_passed={p_ok}")
    print("\n  this labeled corpus IS the correction: a system trained/evaluated")
    print("  on it learns to preserve relational cognition instead of collapsing")
    print("  it into claims, motives, or 'superhuman' reframes.")

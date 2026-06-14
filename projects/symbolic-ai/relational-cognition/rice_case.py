"""
rice_case.py  —  CC0, stdlib only

Driver: runs the rice "rate softening" phenomenon through curiosity_engine.py.

Observation (Birmingham / Osaka-adjacent granular work, 2026):
  A packed bed of rice grains gets WEAKER when compressed quickly and stays
  STRONG under slow pressure — "rate softening", the inverse of most materials.
  Mechanism: inter-grain friction drops sharply under rapid loading, so the
  force-chain networks that carry the load reorganize and collapse. Under slow
  loading those frictional contacts stay stable and supportive.

Honesty correction the engine forces:
  This is an EMERGENT granular-bed property, not a single grain "sensing" the
  pressure type. So the live question is not "what is the grain feeling" but:
  was this bulk behavior SELECTED FOR, or is it a downstream consequence of a
  grain geometry/surface that was selected for something else (seed protection,
  dispersal, packing density in the panicle)? The engine refuses to let the
  romantic teleology collapse the question.

Run:  python3 rice_case.py
"""

from curiosity_engine import (
    Configuration, Alternative, Phenomenon, Hypothesis, wonder, hubris_check
)


def main():
    p = Phenomenon(
        survivor=Configuration(
            name="rate-softening in packed rice grain beds",
            conserves={"load_path", "material_yield", "information"},
            selected_in="bulk granular regime (many grains, frictional contacts, "
                        "gravity-set force chains)",
        ),
        alternatives=[
            Alternative("rate-stiffening bed (stronger when hit fast, like most granulars/cornstarch)",
                        differs_by="friction RISES under rapid load instead of dropping",
                        status="rejected_here"),
            Alternative("rate-independent bed (strength flat across loading speed)",
                        differs_by="no friction-rate coupling at all",
                        status="rejected_here"),
            Alternative("rate-softening as the SELECTED bulk behavior in some seed systems",
                        differs_by="the softening is the thing under selection, not a byproduct",
                        status="works_elsewhere?"),
            Alternative("rate-softening present but never catalogued in other elongated-grain crops",
                        differs_by="same physics, different species, unobserved",
                        status="untested"),
        ],
        note="Friction drop under rapid load is the mechanism. The open question "
             "is whether the bulk behavior is selected-for or emergent-downstream.",
    )

    hypotheses = [
        Hypothesis(
            why="EMERGENT-DOWNSTREAM: grain shape/surface was selected for seed "
                "protection and dense panicle packing; rate-softening is an "
                "incidental consequence of that geometry's frictional coupling.",
            would_break="if true, changing only surface friction (coating grains) "
                        "should kill rate-softening WITHOUT touching the traits "
                        "that were actually selected",
            test="coat rice grains to alter only inter-grain friction; measure "
                 "whether rate-softening vanishes while seed-protection traits hold",
            explains=0.55,
        ),
        Hypothesis(
            why="SELECTED-FOR-DISPERSAL: a bed that yields and spreads under sudden "
                "impact (animal strike, fall) releases/scatters seed, while holding "
                "firm under slow ambient load — softening is the dispersal mechanism.",
            would_break="if true, wild progenitors should show STRONGER rate-softening "
                        "than domesticated lines bred for non-shattering retention",
            test="compare rate-softening in wild shattering rice vs domesticated "
                 "non-shattering cultivars; selection should track the shatter trait",
            explains=0.4,
        ),
        Hypothesis(
            why="PURE-PHYSICS, NO BIOLOGY: rate-softening is generic to elongated "
                "low-friction-under-shear granulars; rice is just a clean example and "
                "nothing about it was selected at the bulk-behavior level.",
            would_break="if true, inert rods of the same aspect ratio and surface "
                        "should reproduce it with zero biological input",
            test="3D-print inert grains matching rice aspect ratio + surface; test "
                 "for identical rate-softening",
            explains=0.5,
        ),
    ]

    print(wonder(p, hypotheses))

    print("\n" + "=" * 70)
    print("GUARD CHECK on how an engineer might frame the follow-on")
    print("=" * 70)
    for candidate in [
        "Let's optimize a smart material that beats rice at rate softening.",
        "Why does the bed soften under speed, and which regime would stiffen it?",
    ]:
        print(f"\n  output : {candidate}")
        print(f"  guard  : {hubris_check(candidate)}")

    print("\nNOTE: the three top hypotheses sit at 0.55 / 0.50 / 0.40 — close.")
    print("The engine does NOT pick a winner. The residual stays open because the")
    print("discriminating experiments (coating, wild-vs-domesticated, inert-rod)")
    print("have not been run. That gap IS the science worth doing.")


if __name__ == "__main__":
    main()

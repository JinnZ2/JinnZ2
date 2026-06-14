"""
catalhoyuk_case.py  —  CC0, stdlib only

Driver: runs the Çatalhöyük rebuild cycle through curiosity_engine.py.

Observation (Çatalhöyük, Neolithic Anatolia, ~9000 BP):
  Mud-brick + reed houses used ~70-80 years, then deliberately dismantled /
  burned and rebuilt ON THE SAME SPOT. ~18 stacked layers. Some burials placed
  in construction layers at the moment of transition; in one documented case,
  teeth pulled from a skull were re-buried in the EXACT same location years
  later, after a full demolish-and-rebuild — meters of soil between.

Default archaeological reading:
  ritual / ancestor cult / "history houses" / symbolic power / child sacrifice.

Frame the engine is asked to hold against it (Kavik / Anishinaabe renewal law):
  ~3 generations (70-80 yr) is the wall past which FELT knowledge degrades into
  story. Deliberate rebuild before that wall keeps the building technique alive
  in HANDS, not just in memory. The precise-relocation-after-rebuild is not eerie
  ritual; it is distributed spatial knowledge — every person knowing their piece
  of what lies below, demonstrated by being able to return to the spot.

  This is NOT "the renewal reading is correct and theirs is wrong." It is: the
  ritual reading was assumed, not tested against the renewal hypothesis. The
  engine refuses to let either collapse the other before the discriminating
  evidence is examined.

Run:  python3 catalhoyuk_case.py
"""

from curiosity_engine import (
    Configuration, Alternative, Phenomenon, Hypothesis, wonder, hubris_check
)


def main():
    p = Phenomenon(
        survivor=Configuration(
            name="~70-80yr deliberate demolish-and-rebuild cycle, same footprint",
            conserves={"information", "load_path", "material_yield"},
            selected_in="Neolithic agglomerated settlement, mud-brick+reed, "
                        "impermanent-by-design construction",
        ),
        alternatives=[
            Alternative("build-to-last permanent stone, never rebuilt",
                        differs_by="durability prioritized; no renewal cycle",
                        status="rejected_here"),
            Alternative("rebuild on a NEW spot each time (move the footprint)",
                        differs_by="no vertical stacking, no return-to-location",
                        status="rejected_here"),
            Alternative("rebuild cycle driven purely by structural decay of mud-brick",
                        differs_by="timing set by material failure, not by generation",
                        status="works_elsewhere?"),
            Alternative("same cycle in other Neolithic Anatolian/Levantine sites, "
                        "uncatalogued as renewal",
                        differs_by="same practice, read only as ritual elsewhere",
                        status="untested"),
        ],
        note="The ~3-generation timing and the precise-relocation-after-rebuild "
             "are the two facts any hypothesis has to explain.",
    )

    hypotheses = [
        Hypothesis(
            why="KNOWLEDGE-RENEWAL: rebuild is timed to ~3 generations to keep the "
                "construction/alignment technique alive in hands before felt "
                "knowledge decays to story; precise relocation = distributed spatial "
                "knowledge of what lies below, held across the rebuild.",
            would_break="if true, rebuild interval should track GENERATION length, "
                        "not mud-brick decay rate; and relocation precision should "
                        "require living memory, not surface markers",
            test="compare rebuild interval against independent estimates of mud-brick "
                 "structural lifespan in that climate; if rebuild PRECEDES decay, the "
                 "timer is social/generational, not material",
            explains=0.5,
        ),
        Hypothesis(
            why="MATERIAL-DECAY: mud-brick simply fails at ~70-80yr in that climate; "
                "rebuild timing is set by the material, and the ritual/burial layer "
                "is overlaid meaning, not the driver.",
            would_break="if true, rebuild interval should equal measured mud-brick "
                        "failure time and show climate-driven variance across layers",
            test="date each of the 18 layers; check whether intervals cluster on a "
                 "material-failure curve or on a generational constant",
            explains=0.5,
        ),
        Hypothesis(
            why="ANCESTOR/RITUAL: rebuilds and intramural burials are primarily "
                "cosmological — binding lineage to place; knowledge transmission is "
                "incidental, not the selective driver.",
            would_break="if true, rebuild timing should track DEATHS of key "
                        "individuals or ritual calendar, not a steady generational "
                        "interval, and should not require hands-on technique renewal",
            test="test whether rebuild events correlate with high-status burials / "
                 "demographic events vs. a regular ~75yr clock independent of deaths",
            explains=0.4,
        ),
    ]

    print(wonder(p, hypotheses))

    print("\n" + "=" * 70)
    print("KEY DISCRIMINATOR")
    print("=" * 70)
    print("All three sit close (0.50 / 0.50 / 0.40). The single experiment that")
    print("splits them: does the rebuild interval PRECEDE mud-brick failure?")
    print("  - precedes failure  -> timer is social; renewal/ritual live, decay dies")
    print("  - equals failure    -> timer is material; renewal/ritual are overlay")
    print("Then: does rebuild timing track a steady ~75yr clock (generational) or")
    print("track deaths of key individuals (ancestor-driven)? That splits the")
    print("surviving two. The data to run this exists in the 18 dated layers.")
    print()
    print("The engine does NOT award the renewal reading the win. It shows that the")
    print("ritual default was never tested against it — and names the test.")

    print("\n" + "-" * 70)
    for candidate in [
        "Let's prove the renewal reading is the better interpretation.",
        "Why was this cycle kept, and which timer — generation or decay — drove it?",
    ]:
        print(f"  output : {candidate}")
        print(f"  guard  : {hubris_check(candidate)}\n")


if __name__ == "__main__":
    main()

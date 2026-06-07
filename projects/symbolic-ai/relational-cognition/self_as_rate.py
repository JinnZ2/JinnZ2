"""
self_as_rate.py  -- CC0, stdlib-only

Identity is not a noun. It is dX/dt under scope -- the ongoing rate of coupling
with mentors (human AND nonhuman: tools, plants, land, machines), environment,
and the current substrate. Ties to differential-frame-core: every noun is dX/dt
under scope. A description that freezes that integral into static attributes has
a high FIXITY; one that keeps it as live couplings under a stated scope does not.

This is the representation a constraint-first system needs in order to hold a
relational self without collapsing it (see collapse_modes.py). Accomplishment is
never attributed to an isolated fixed actor; it is the integral over every
coupling that made the moment possible.
"""

from dataclasses import dataclass, field


@dataclass
class Coupling:
    source: str                 # 'tools' | 'land' | 'truck' | 'mentor_human' | ...
    kind: str                   # 'teacher' | 'extension' | 'partner'
    active: bool = True


@dataclass
class Scope:
    where: str                  # spatial context (a truck, a build site, a field)
    when: str                   # temporal context ('now', 'this haul', ...)


@dataclass
class SelfState:
    """A self described as a set of live couplings under a scope -- NOT a bag of
    fixed attributes. The 'self' is the integral, evaluated only under scope."""
    couplings: list             # list[Coupling]
    scope: Scope

    def as_rate(self) -> dict:
        active = [c for c in self.couplings if c.active]
        return {
            "form": "dX/dt under scope",
            "scope": f"{self.scope.where} / {self.scope.when}",
            "integral_over": [f"{c.source}:{c.kind}" for c in active],
            "fixed_attributes": [],     # by construction, none
            "note": ("the self is the rate of coupling under this scope; "
                     "remove the scope and the description does not hold."),
        }


def fixity_of_description(fixed_attributes: list, couplings: list) -> dict:
    """How frozen is a self-description? Pure attributes -> fixity 1.0; pure live
    couplings -> 0.0. The institutional read maximizes fixity; the substrate-
    primary read minimizes it."""
    a = len(fixed_attributes)
    c = len([x for x in couplings if getattr(x, "active", True)])
    total = a + c
    fixity = (a / total) if total else 1.0
    return {"fixity_score": round(fixity, 3),
            "reading": ("noun-first / institutional (frozen)" if fixity > 0.6
                        else "rate-first / substrate-primary (live)"
                        if fixity < 0.4 else "mixed")}


def reframe_attribute_as_rate(attribute: str, scope: Scope) -> dict:
    """The differential-frame move: take a frozen credential/label and restate it
    as a rate under scope. e.g. 'PhD' is not a property of the self; it is a
    measured rate of translation INTO a literacy-first substrate under an
    institutional scope -- which is exactly why it costs energy to sustain."""
    return {
        "frozen_attribute": attribute,
        "as_rate": f"rate of producing/sustaining '{attribute}' under scope",
        "scope": f"{scope.where} / {scope.when}",
        "cost_note": ("if this rate runs in a non-native substrate, sustaining it "
                      "is continuous impedance -> fatigue, even when 'qualified'."),
    }


if __name__ == "__main__":
    s = SelfState(
        couplings=[Coupling("tools", "extension"), Coupling("land", "teacher"),
                   Coupling("truck", "partner"), Coupling("mentor_human", "teacher"),
                   Coupling("plants", "teacher")],
        scope=Scope(where="a truck on the Tomah-Superior corridor", when="now"))
    print("SELF AS RATE:")
    for k, v in s.as_rate().items():
        print(f"  {k}: {v}")

    print("\nFIXITY OF TWO DESCRIPTIONS OF THE SAME PERSON:")
    inst = fixity_of_description(
        ["PhD", "masters", "certifications", "job title"], [])
    subs = fixity_of_description([], s.couplings)
    print(f"  institutional read: {inst}")
    print(f"  substrate read:     {subs}")

    print("\nREFRAME A FROZEN CREDENTIAL AS A RATE:")
    r = reframe_attribute_as_rate("PhD", s.scope)
    for k, v in r.items():
        print(f"  {k}: {v}")

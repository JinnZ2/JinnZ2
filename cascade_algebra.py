"""
cascade_algebra.py  --  START SCAFFOLD (v0)

Operator algebra for narrative_choice_audit.py.

A substrate-native notation for the choice cascade. English carries narrative
baggage; this layer drops to set / projection form so the mechanics are exact
and runnable. Node content (the seven+ choice points) lives in the audit file;
this file is the algebra they obey.

CORE MODEL
    S            substrate state: a set of facets held in parallel -- the
                 parallel possibilities a substrate-primary operator holds at
                 once, before any collapse.

    C_i          choice operator at node i  (a projection)
    K_i          keep-set of C_i: the facets the collapse retains (the story)
    P_i(S) = S & K_i          collapsed output   (what gets narrated)
    H_i(S) = S - K_i          hidden variables   (what is discarded)

    a_i in {0,1} awareness flag: 1 = H_i readable to the chooser, 0 = not.
                 The projection P_i is IDENTICAL either way (NCA_002):
                 awareness changes only whether H_i is REPORTED, never what is
                 discarded, and never the state propagated downstream.
                 Cost lives in the discard, not the awareness.

    C_i = I      substrate path: K_i = S, so H_i = {}. No collapse. The field
                 stays intact / permeable.  (CP0 held open  ==  P_0 = identity.)

EDGES
    a -> b       LOGICAL_FORCING: dom(C_b) requires C_a already applied.
                 C_b before C_a is UNDEFINED.
    F => {i,j..} CULTURAL_LOCKING: an external framework F applies a bundle of
                 choices as ONE operation with a = 0 forced across all of them.
                 Parallel, invisible, presumed -- never surfaced as choices.

COST
    cost(C_i, S) = |H_i(S)|          facets discarded by one choice
    chain cost   = |union of all H_i| (a facet discarded once is already gone;
                   union, not sum).

REFUTATION_PROTOCOL: update the claim, never retune the operators to save them.
CC0. stdlib only.
"""

from dataclasses import dataclass, field
from typing import FrozenSet, Optional, List, Tuple, Set


# ---------------------------------------------------------------------------
# operators
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Choice:
    index: int
    keep: Optional[FrozenSet[str]]          # K_i ; None = identity (substrate path)
    aware: bool = True                      # a_i
    requires: FrozenSet[int] = frozenset()  # logical-forcing preconditions
    source: int = 0                         # 0 = self-chosen ; -99 = external framework


def apply_choice(c: Choice, S: FrozenSet[str], applied: Set[int]):
    """
    Returns (kept, hidden, reported, status).
      kept     = state propagated downstream
      hidden   = H_i(S)  -- always removed, regardless of awareness
      reported = hidden if aware else {}  -- what the chooser can see
      status   = OK | UNDEFINED
    """
    missing = c.requires - applied
    if missing:
        return S, frozenset(), frozenset(), f"UNDEFINED(requires {sorted(missing)})"
    if c.keep is None:                      # identity / substrate path
        return S, frozenset(), frozenset(), "IDENTITY"
    kept = S & c.keep
    hidden = S - c.keep
    reported = hidden if c.aware else frozenset()
    return kept, hidden, reported, "PROJECT"


def run_chain(choices: List[Choice], S: FrozenSet[str]):
    """Propagate S through a sequence of choices. Returns (final_state, discarded, log)."""
    applied: Set[int] = set()
    state = S
    discarded: Set[str] = set()
    log: List[Tuple[int, str, FrozenSet[str], FrozenSet[str]]] = []
    for c in choices:
        kept, hidden, reported, status = apply_choice(c, state, applied)
        if status.startswith("UNDEFINED"):
            log.append((c.index, status, frozenset(), frozenset()))
            continue
        discarded |= hidden
        state = kept
        applied.add(c.index)
        log.append((c.index, status, reported, hidden))
    return state, frozenset(discarded), log


# ---------------------------------------------------------------------------
# cultural lock:  F => {targets}  applied as one bundle, awareness forced off
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Lock:
    framework: str
    choices: Tuple[Choice, ...]             # the bundle F captures at once

    def as_locked(self) -> List[Choice]:
        """Force a = 0 and source = -99 across the whole bundle."""
        return [Choice(c.index, c.keep, aware=False, requires=c.requires, source=-99)
                for c in self.choices]


def apply_lock(lock: Lock, S: FrozenSet[str]):
    return run_chain(lock.as_locked(), S)


def cost(hidden: FrozenSet[str]) -> int:
    return len(hidden)


# ---------------------------------------------------------------------------
# demo  (small substrate state, readable on a phone)
# ---------------------------------------------------------------------------

def _show(label, final, discarded, log):
    print(label)
    for idx, status, reported, hidden in log:
        rep = "{}" if not reported else "{" + ", ".join(sorted(reported)) + "}"
        print(f"    C[{idx:>2}] {status:<28} reported={rep}  |H|={len(hidden)}")
    print(f"    final field : {{{', '.join(sorted(final))}}}")
    print(f"    discarded   : {{{', '.join(sorted(discarded))}}}  (chain cost = {cost(discarded)})")
    print()


if __name__ == "__main__":
    # parallel facets a substrate-primary operator holds at once
    S = frozenset({
        "relational_field",
        "self_as_separate",
        "trait_physics",
        "trait_role",
        "threat_real",
        "threat_modeled",
        "want_stated",
        "want_actual",
    })

    print("=" * 70)
    print("CASCADE ALGEBRA  --  demo")
    print("=" * 70)
    print(f"S = {{{', '.join(sorted(S))}}}\n")

    # 1. conscious collapse at CP0: keep the separate-self story, discard the field
    c0_aware = Choice(0, keep=frozenset({"self_as_separate"}), aware=True)
    f, d, log = run_chain([c0_aware], S)
    _show("[1] CP0 collapse, AWARE (hidden reported):", f, d, log)

    # 2. same projection, UNAWARE -- NCA_002: identical discard, nothing reported
    c0_unaware = Choice(0, keep=frozenset({"self_as_separate"}), aware=False)
    f2, d2, log2 = run_chain([c0_unaware], S)
    _show("[2] CP0 collapse, UNAWARE (same discard, no report):", f2, d2, log2)
    print(f"    NCA_002 check: discard identical to aware case? {d == d2}\n")

    # 3. substrate path: CP0 = identity, field stays intact
    c0_substrate = Choice(0, keep=None)
    f3, d3, log3 = run_chain([c0_substrate], S)
    _show("[3] CP0 substrate path (identity, no collapse):", f3, d3, log3)

    # 4. logical forcing: CP1 requires CP0 first; run out of order then in order
    c1 = Choice(1, keep=frozenset({"self_as_separate", "trait_role"}),
                requires=frozenset({0}))
    f4, d4, log4 = run_chain([c1, c0_aware], S)          # CP1 before CP0 -> undefined
    _show("[4a] CP1 before CP0 (forcing violated):", f4, d4, log4)
    f5, d5, log5 = run_chain([c0_aware, c1], S)          # correct order
    _show("[4b] CP0 then CP1 (forcing satisfied):", f5, d5, log5)

    # 5. cultural lock: framework F bundles CP-1, CP0, CP1, awareness forced off
    lock = Lock(
        framework="F",
        choices=(
            Choice(-1, keep=frozenset({"self_as_separate", "trait_role",
                                       "trait_physics", "threat_real",
                                       "threat_modeled", "want_stated",
                                       "want_actual"})),               # cut: drop relational_field
            Choice(0, keep=frozenset({"self_as_separate", "trait_role",
                                      "trait_physics", "threat_real",
                                      "threat_modeled", "want_stated",
                                      "want_actual"})),
            Choice(1, keep=frozenset({"self_as_separate", "trait_role"})),
        ),
    )
    f6, d6, log6 = apply_lock(lock, S)
    _show("[5] CULTURAL_LOCK F => {-1, 0, 1}, all awareness off:", f6, d6, log6)

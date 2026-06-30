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

    HOLD(X)      superposition: hold a set X of contradictory / parallel facets
                 LIVE and unresolved. Not a projection (no discard), not identity
                 (X is tracked as a suspended cluster). Stays at baseline until a
                 falsifier arrives. This is running all the sims at once.

    RESOLVE      collapse a superposition by FALSIFIER (data), not by story:
                 remove only the facets a falsifier rules out; keep survivors.
                 Legitimate collapse. Distinct from PROJECT, where the discard is
                 driven by a chosen keep-set (the story) and not by evidence.
                 No falsifier -> nothing collapses; the field holds at baseline.
                 (The guttural response, NCA_005, fires on PROJECT, not RESOLVE.)

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
from typing import FrozenSet, Optional, List, Tuple, Set, Dict
from math import log as ln


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
# superposition:  hold contradictory facets live until a falsifier arrives
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Superposition:
    facets: FrozenSet[str]          # parallel / contradictory options held live


@dataclass(frozen=True)
class Falsifier:
    name: str
    removes: FrozenSet[str]         # facets this evidence rules OUT


def hold(*facets: str) -> Superposition:
    return Superposition(frozenset(facets))


def resolve(sp: Superposition, *falsifiers: Falsifier):
    """
    Collapse a superposition by data, not story.
    Returns (survivors, removed, applied_names).
    No falsifier (or none that bites) -> survivors == sp.facets, removed == {}.
    """
    removed: Set[str] = set()
    applied: List[str] = []
    for f in falsifiers:
        bite = f.removes & sp.facets
        if bite:
            removed |= bite
            applied.append(f.name)
    survivors = sp.facets - removed
    return frozenset(survivors), frozenset(removed), applied


# ---------------------------------------------------------------------------
# weighted superposition:  decision distribution over live hypotheses.
#   decide on the leading hypothesis; keep every other branch live as a
#   contingency; update weights as evidence arrives; pivot with no rework.
#   "identity" retired from the algebra: the operation is adaptive coherence —
#   any adaptive system (fish, tree, neuron) runs this mechanism. selfhood /
#   story-defense are not in it. spread() = coherence cost, not identity cost.
#   (derivation_log E8b — option 1 taken: retire the term)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WeightedField:
    items: Tuple[Tuple[str, float], ...]      # (facet, weight); weights > 0

    def as_dict(self) -> Dict[str, float]:
        return dict(self.items)

    def normalized(self) -> "WeightedField":
        tot = sum(w for _, w in self.items)
        if tot == 0:
            return WeightedField(tuple())
        return WeightedField(tuple((f, w / tot) for f, w in self.items))

    def leading(self) -> Tuple[str, float]:
        n = self.normalized()
        return max(n.items, key=lambda kv: kv[1])

    def spread(self) -> float:
        """Normalized Shannon entropy in [0,1]. 0 = concentrated (one hypothesis
        dominates, low coherence cost). 1 = uniform (all live, high coherence cost)."""
        n = self.normalized()
        k = len(n.items)
        if k <= 1:
            return 0.0
        h = -sum(p * ln(p) for _, p in n.items if p > 0)
        return h / ln(k)


def wfield(**weights: float) -> WeightedField:
    return WeightedField(tuple(weights.items())).normalized()


def update(wf: WeightedField, evidence: Dict[str, float]) -> WeightedField:
    """
    Multiplicative (likelihood) update. evidence[f] scales facet f's weight.
    A multiplier of 0 falsifies that facet -> it drops out. Unlisted facets
    keep their weight (multiplier 1). Renormalizes. This is RESOLVE on a
    weighted field: data moves weight, it does not pick a story.
    """
    out = []
    for f, w in wf.items:
        m = evidence.get(f, 1.0)
        nw = w * m
        if nw > 0:
            out.append((f, nw))
    return WeightedField(tuple(out)).normalized()


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

    # 6. superposition: hold contradictory facets until data arrives
    print("[6] SUPERPOSITION  (hold, then resolve by falsifier)")
    sp = hold("seller_devastation_real", "seller_devastation_performed")
    print(f"    held        : {{{', '.join(sorted(sp.facets))}}}")

    # no falsifier yet -> baseline, nothing collapses
    surv0, rem0, ap0 = resolve(sp)
    print(f"    no data     : survivors={{{', '.join(sorted(surv0))}}}  removed={{}}  (baseline held)")

    # falsifier arrives: custom drawings honoring the wife rule out 'performed/con'
    drawings = Falsifier("custom_drawings_on_wall",
                         removes=frozenset({"seller_devastation_performed"}))
    surv1, rem1, ap1 = resolve(sp, drawings)
    print(f"    +{ap1[0]}")
    print(f"                : survivors={{{', '.join(sorted(surv1))}}}  removed={{{', '.join(sorted(rem1))}}}")
    print(f"    note: discard here is FALSIFIER-driven (legitimate), not story-driven (PROJECT).")
    print()

    # 7. weighted field: decide on the leading hypothesis, hold the rest live
    print("[7] WEIGHTED FIELD  (leading hypothesis + contingencies + pivot)")
    wf = wfield(h1=0.30, h2=0.08, h3=0.07, h4=0.06, h5=0.05, h6=0.04)

    def line(tag, wf):
        lead, lw = wf.leading()
        dist = "  ".join(f"{f}={w:.2f}" for f, w in sorted(wf.items, key=lambda kv: -kv[1]))
        print(f"    {tag}")
        print(f"        dist   : {dist}")
        print(f"        lead   : {lead} ({lw:.2f})   spread/cost={wf.spread():.2f}")

    line("initial (act on h1; h2..h6 held as contingencies):", wf)

    # evidence weakly supports h1, weakens h2 -> lead holds, weight up, cost down
    wf2 = update(wf, {"h1": 1.6, "h2": 0.5})
    line("+evidence (supports h1):", wf2)

    # falsifier rules h1 OUT entirely -> lead flips to a pre-modeled branch
    wf3 = update(wf2, {"h1": 0.0, "h3": 1.8})
    line("+falsifier (rules out h1; h3 was already a contingency):", wf3)
    print("        note: pivot is free -- h3 was held live, not rebuilt from scratch.")

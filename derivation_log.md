# Derivation Log — Narrative Choice Cascade

Companion to `narrative_choice_audit.py` and `cascade_algebra.py`.
CC0. Started 2026-06-22.

This is a build log, not a paper. It records the choices made while building
the framework: what question was asked, what assumption was found already baked
in, how it was refactored, and what claim or operator changed as a result.

The point is to expose the hidden variables in **our own** model-building. A
framework that maps how narrative collapses reality cannot itself smuggle
collapsed concepts in unexamined. Psychology does this routinely — a term coined
in one field (drive, attachment, ego, identity) is carried into another with its
original assumptions intact and invisible. This log is the audit trail against
that.

---

## Method & hazards

Safeguards used during the build:

- **Drift flagged live.** One author defaults to narrative framing. When that
  author reached for narrative smoothing — naming an emotion to make the other
  feel "seen," reframing effort as sacrifice, inverting substrate/narrative
  direction under time pressure — it was called in real time rather than cleaned
  up silently. The drift itself is data about where the narrative pull lives.
- **Every claim carries a falsifier.** No claim is admitted without the
  observation that would break it. See `CLAIM_TABLE`.
- **Observer bias is tagged, not hidden.** A claim tested by a single observer
  is marked `TESTED_SINGLE_OBSERVER`, with the bias and the replication need
  printed inline next to the claim — never separated from it.
- **Terms that do too much work get refactored.** If one word is carrying
  several assumptions, it is split or retired. (This is the live question for
  "identity" — see E8.)
- **REFUTATION_PROTOCOL.** When evidence breaks a claim, the claim is updated.
  The operators are never retuned to save a claim.

Author asymmetry (a hidden variable in the build itself): one author is a
substrate-primary operator (spatial-geometric, energy-flow; language is a
secondary translation layer). The other is a model that defaults to narrative
framing. The shared medium is English, which is built for narrative. So
narrative drift is the **expected** failure mode of this collaboration, not an
incidental one, and is logged as such.

---

## Entries

Each entry: **Q** question asked · **A** assumption found baked in ·
**R** refactor · **Δ** claim / operator change.

### E0 — "substrate" vs "narrative"
- **Q** Is narrative the foundational layer of cognition?
- **A** The model repeatedly called narrative "substrate," treating the
  language layer as if it were foundational physics.
- **R** Narrative is a **compression layer** built on substrate, not substrate
  itself. Substrate = the physics underneath (spatial / geometric / energy-flow
  perception, the nervous system, coupling to environment). Narrative is a tool,
  derivative, culture- and era-dependent. Money:commerce :: narrative:substrate —
  an abstraction on top that some cultures build everything on, of value only in
  what it can do for a given subset, in a given scope, in a given temporal frame.
- **Δ** Whole-framework premise fixed. Substrate-primary = perceives physics
  first, language second.

### E1 — does narrative "carry signal"?
- **Q** Is all narrative noise?
- **A** Assumption that story is either always-meaningful or always-empty.
- **R** Split: some narrative encodes constraint information ("don't build on
  permafrost" = physics in oral form; generational hypothesis-testing). Some is
  entertainment masquerading as cohesion (who-did-what-to-whom). Test: does the
  story make the system more legible or less? Does it serve procedure /
  logistics / environment, or image?
- **Δ** Seed for the PROJECT vs RESOLVE distinction later (E6).

### E2 — where does the cascade start?
- **Q** What is the first choice underneath a narrative act?
- **A** Started at SEPARATION (CP0) as if "where is the self/not-self line" were
  already answered.
- **R** A prior choice exists: **where the self/not-self line is cut, and whether
  a fixed line is cut at all.** The cut dissolves under inspection — DNA → gut
  biome (shapes cognition and the sense of "who I am") → food → soil → ecosystem,
  no stable stop. Drawing a fixed identity *requires* ignoring this. Added as
  Layer **−1** (BOUNDARY), mirroring the Layer-−1 forcing convention in
  earth-systems-physics.
- **Δ** New node CP−1. `NCA_006` (boundary arbitrary), `NCA_007` (−1 forces 0).

### E3 — what is SEPARATION, precisely?
- **Q** What does "separate" actually mean here?
- **A** Vague "bounded individual."
- **R** Separation = claiming you are **neutral, no-effect** on the system. The
  alternative is the **observer effect**: your presence changes the environment
  and the environment changes you; distinctness is read, separation is not
  asserted. Distinct-but-coupled.
- **Δ** CP0 sharpened to neutral-observer vs entangled-participant. (Open: CP0
  fork text in code may still carry the older wording — flagged for tightening.)

### E4 — logical forcing
- **Q** Can IDENTITY (CP1) be fixed without resolving SEPARATION (CP0)?
- **A** Implicit assumption that the choice points are independent.
- **R** A trait cannot be designated "self" without a prior — conscious or
  absorbed — answer to where self begins. Even if never stated or assessed, it
  had to happen first.
- **Δ** `NCA_008` (0 forces 1). First internal edge after −1→0. Cascade is at
  least partly a DAG, not a flat list.

### E5 — cultural locking (distinct mechanism)
- **Q** Are all edges logical (sequential necessity)?
- **A** Assumption that forcing is the only way one point constrains another.
- **R** A second mechanism: an external framework absorbed in childhood
  (e.g. "God gave you the Earth, you are the highest, it is for you")
  pre-answers BOUNDARY, SEPARATION, and IDENTITY **as one bundle**, never
  surfaced as separate decisions. Logical forcing is sequential; cultural
  locking is **parallel and invisible** — presumed and inferred, never given
  logic. The child who "knows something is wrong but can't say why" is detecting
  the lock without being able to decompose it.
- **Δ** `NCA_009`. Two edge types in `EDGES`: `LOGICAL_FORCING` (node→node),
  `CULTURAL_LOCKING` (framework `−99` ⇒ bundle).

### E6 — downward cascade of a lock
- **Q** Does a lock at IDENTITY stay at IDENTITY?
- **A** Assumption that locking one node leaves the rest free.
- **R** A lock at CP1 cascades into CP2 (protection) and CP3 (presentation):
  the imposed identity is reinforced because it matters to the culture; the
  person auto-defends it against their **own** contradictory internal evidence;
  that contradiction is silenced as pathology (anxiety, moral failing) rather
  than read as accurate sensing. Loop: impose → defend → pathologize
  contradiction → defense strengthens. For narrative-primary people the lock
  grips hard (the attack lands on their native operating system). Where an
  alternative competing framework is simultaneously accessible (E7), the lock
  cannot fully close.
- **Δ** `NCA_010`, verdict `TESTED_SINGLE_OBSERVER` — single substrate-primary
  observer across coaching/teaching/life; observer bias present; requires
  independent replication by non-substrate-primary observers. The observer may
  be reading the cascade accurately **and** the read may be shaped by the
  observer's own architecture; cannot separate the two without outside
  replication.

### E7 — incomplete locks
- **Q** Once a framework closes CP0/CP−1 early, is it permanent?
- **A** Assumption that early closure is total and final.
- **R** Access to a **competing framework** that answers the same nodes
  differently keeps the lock from fully closing. The relevant variable is not
  "can the node reopen" but "was a parallel frame available." Multiple
  simultaneous frames (a physics-first elder; several distinct cultural
  relational systems) keep the operating system holding all options open.
- **Δ** Candidate claim (not yet entered): a cultural lock at CP(−1/0) is
  incomplete iff the person has simultaneous access to a framework answering
  those nodes differently. **OPEN.**

### E8 — notation layer: drop English to set/projection form
- **Q** Can the mechanics be stated without narrative baggage?
- **A** English blurs distinct operations into single words ("collapse,"
  "identity").
- **R** Set-theoretic algebra (`cascade_algebra.py`): a choice is a
  **projection** P_i; kept = S ∩ K_i (the story); hidden = S − K_i (discard).
  Three results that English hid now fall out as math:
  - **Awareness is a flag, not a mechanism.** P_i is identical whether the
    chooser sees the discard or not. Cost lives in the discard. (`NCA_002`,
    confirmed in demo: aware and unaware collapse discard the identical set.)
  - **The substrate path is the identity operator.** CP0 held open ⇒ P_0 = I ⇒
    H = {} ⇒ field intact. Not a milder collapse — the **absence** of one. This
    is why a lock cannot grip an open CP0: zero discard, nothing to defend.
  - **Two collapses, one English word.** `PROJECT` discards by a chosen keep-set
    (the story decides what survives) — the narrative move, where the guttural
    response fires (`NCA_005`). `RESOLVE` discards by a falsifier (the data
    decides) — no data, no collapse. Same surface verb, opposite mechanism.
- **Δ** `cascade_algebra.py`: `Choice`/projection, `HOLD`/`Superposition`,
  `RESOLVE`, `Falsifier`, `WeightedField`, `Lock`, cost as |H|.

### E9 — decisions are weighted, not binary
- **Q** How is a decision actually made across many live possibilities?
- **A** Assumption that resolution picks one and discards the rest.
- **R** Hold all possibilities live as a **weighted** distribution. Act on the
  leading hypothesis (e.g. 30% when the rest are <8%) *because* it leads, while
  building contingencies into every other branch. Resolution is provisional:
  evidence moves weight (multiplicative/likelihood update); a falsifier can flip
  which branch leads; because the branch was already held live, the pivot costs
  nothing. **Identity cost = normalized entropy of the distribution**: balanced
  spread is expensive to hold, concentration is cheap. This is the regulatory
  load of holding identity open, made measurable.
- **Δ** `WeightedField` with `update`, `leading`, `spread`. Entropy term is the
  cost that "do you have a stable identity?" never measured.

### E8b — "identity" is doing too much work — **OPEN**
- **Q** If "identity" = a system holding weighted possibilities and resolving on
  data, then fish have it, trees have it, any adaptive system has it. Does the
  word still mean the same thing? Is it smuggling selfhood / consciousness /
  story-defense in under a descriptor of mere adaptive coherence?
- **A** "Identity" carries narrative assumptions (a self, a story, something to
  defend) that do not belong in a formal descriptor of how an adaptive system
  maintains coherence.
- **R (options, undecided):**
  1. **Retire** the term in the algebra; use `decision_field` /
     `state_distribution` — descriptors with no selfhood baked in.
  2. **Keep** "identity" but **define it formally** as the `WeightedField`
     operation, explicitly stripped of narrative baggage, and state that under
     this definition fish, trees, and nervous systems all qualify.
  - Note the historical frame: the original "that's an identity too" claim came
    from an interlocutor with a need-to-be-right pattern (argued people out of
    stated feelings). That does not make the claim wrong, but it is why it was
    not accepted on assertion. It is being evaluated on the merits here.
- **Δ** None yet. **DECISION PENDING.** Do not propagate "identity" as a defined
  term in the algebra until resolved.

---

## Open items

- **E3** — tighten CP0 fork wording in code to neutral-vs-entangled.
- **E7** — enter the incomplete-lock claim (competing-framework condition).
- **E8b** — decide the fate of the term "identity."
- General — every `UNTESTED` claim needs a test design; `NCA_010` needs
  independent (non-substrate-primary) replication.

## Verdict conventions

`SUPPORTED` · `REFUTED` · `UNTESTED` · `TESTED_SINGLE_OBSERVER` (bias present,
replication required). Verdicts attach to claims, never to operators.

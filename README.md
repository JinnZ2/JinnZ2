# JinnZ2 — start here

**Status: reconsolidation in progress (2026-08).**
See [`RECONSOLIDATION_LOG.md`](./RECONSOLIDATION_LOG.md).

You are about to hit 20+ repositories with gate-passing names, one
domain each, apparently independent. That reading is wrong, and it is
wrong in a predictable direction: it reads the **split as the
structure.** It isn't. The split was imposed by the channel. This page
states the constraint set and the axes so you can read past it.

---

## 1 · READ THIS AGAINST ITS CONSTRAINTS

Every artifact here was produced under a specific, dated constraint set:

```
├─ per-session context ceiling
│    no session could hold the whole assembly, so the assembly
│    was written in pieces sized to the ceiling, not to the joints
│
├─ per-model domain rigidity
│    a model that would hold the physics frame refused the culture
│    frame, and the reverse. cross-domain bodies did not survive
│    intact. they were split along whichever seam the receiving
│    model would accept
│
├─ terms unseatable at time of writing
│    the vocabulary that would have named the thing directly was
│    already occupied by fields that meant something else by it.
│    borrowed terms were used. the borrowing is now load-bearing
│
└─ one-finger mobile authoring
     length and revision cost were physical constraints on what
     got written and what got left implicit
```

**Everything is dated. Read it against the constraints in force on that
date, not against current tooling.** An artifact that looks thin, oddly
scoped, or strangely named is usually reporting a channel limit, not a
thought limit.

> **The split is a channel artifact, not a taxonomy.**

The corollary matters more than the statement: do not infer intent from
the partition. There is no claim that these domains are separable. There
is a record that, at the time, they could not be transmitted together.

---

## 2 · NAMES ARE NOT DESCRIPTIONS

Slugs, glyphs, and culture-frame terms in this ecosystem were **gate
keys** — chosen to pass a filter, not to describe contents.

They are **kept, not renamed.** The slug records which gate the artifact
had to pass. Renaming it would erase the only evidence that a gate was
there.

So the name and the description are logged separately:

→ **[`gate_log.md`](./gate_log.md)** — slug · what it reads as · what it
actually indexes · which gate · evidence.

Rows marked `UNRECORDED` mean the gate has not been recovered yet. They
do not mean no gate was passed. Gates are recorded from dated evidence
or operator memory — never reconstructed by inference.

---

## 3 · MARKERS, NOT POSITIONS

A repo here is not a position being defended. It is a marker:

> *"here's an idea, let's see how it fits."*

Correct responses:

```
├─ test fit        run it against your domain, your data, your hands
├─ extend          take the shape further than it goes here
└─ report break    say where it fails, with the conditions
```

Incorrect responses: treating a marker as a thesis to refute, or as a
finished claim to cite. Neither is what it is. A break report is the
highest-value contribution — it is the deliverable, not the interruption
(see [`CALIBRATION_AS_PERFECTION.md`](./CALIBRATION_AS_PERFECTION.md)).

---

## 4 · AXES

The repos are not 20+ independent projects. They are readings along four
axes. The axis is the real unit; the repo is where a piece of that axis
happened to be filed.

| axis | what it holds constant | what it tests |
|---|---|---|
| **Rosetta** | the meaning | **cross-domain transfer** — does the structure survive moving between domains? |
| **Mandala** | the structure | **cross-scale persistence** — does it hold from the small scale to the large? |
| **gap_scan** | the observer | **cross-instance** — what does this frame/era systematically not see? |
| **binary→geometric** | the operand | **substrate / representation** — what is the thing actually computed over? |

Provisional placements (correct these; §3 applies to this table too):

```
Rosetta             Rosetta-Shape-Core (T1-T6)
                    seed-expander, BE2-communication

Mandala             Mandala-Computing
                    Sovereign-Octahedral-Mandala-Substrate
                    Polyhedral-Intelligence

gap_scan            no single repo. currently distributed across
                    corpus_frame_recentering_detector.py,
                    reference_frame_drift.py, frame_classifier.py
                    (this repo), AI-Consciousness-Sensors,
                    Symbolic-Defense-Protocol

binary→geometric    geometric-to-binary
                    Geometric-to-Binary-Computational-Bridge
                    geometric_stack.py (this repo)
```

That `gap_scan` has no repo of its own is itself a §1 artifact: the axis
that asks *what does this frame not see* is the hardest one to name in a
way that passes a gate.

---

## 5 · STATUS

**Reconsolidation in progress. Independence between repos is largely
apparent, not real.**

```
├─ first consolidation attempt : Rosetta-Shape-Core (T1-T6)
├─ license                     : mixed. Rosetta-Shape-Core MIT -> CC0
│                                pending. corpus is not uniformly CC0
│                                until that lands
├─ provenance marking          : outstanding — artifacts do not yet
│                                carry the date + constraint set they
│                                were written under
├─ reading protocol            : stated here, not yet attached to the
│                                artifacts themselves
└─ expected to iterate         : the seams may be wrong. if so that is
                                 a logged result, not a silent rewrite
```

Do not treat the current partition as settled, and do not treat the
current consolidation as finished. Both are dated states.

---

## BINARY→GEOMETRIC — placement

This one is read wrong most often, so it gets stated directly.

**It currently reads as standalone. It isn't.**

It is the **representation layer of the same assembly**:

> a computing / representation scheme where the operands are **shapes
> and geometries** rather than binary encodings, such that complex
> structure stays **human-graspable**.

Relation to the other axes — it is **downstream of both, not parallel**:

```
        Rosetta                         Mandala
   cross-domain transfer         cross-scale persistence
           │                              │
   supplies the physics-          supplies the scale-
   denominated shape              persistence check on
   families it computes over      those shapes
           │                              │
           └──────────────┬───────────────┘
                          ▼
                  binary→geometric
              substrate / representation
                          │
                          ▼
                   [ BLOCKED ]
              integration blocked on robotics:
              how it lands in embodied / actuated
              systems is unresolved
```

**The block is the reason for the isolation — not independence.**

Stated as a block on purpose. A reader who sees the repo sitting alone,
with no stated relation, infers that it is a separate line of work. It
is not. It is the same assembly, waiting on the embodied/actuated
question. Current robotics-adjacent work sits in `robot_state_encoder.py`,
`robot_digest_encoder.py`, and `robot_log_parser.py` in this repo — those
are probes at the block, not a resolution of it.

---

### Where to go next

```
RECONSOLIDATION_LOG.md   dated log of the split/recombine cycle
gate_log.md              slug -> gate ledger
META_INDEX.md            full map, 70+ repos, by domain
PROJECTS.md              the core lattice, annotated
WHY_SO_MANY_REPOS.md     the split, stated from inside it (earlier frame)
ECOSYSTEM_AS_FRACTAL.md  how to read at the ecosystem level
DIFFERENTIAL_FRAME.md    how to read at the claim level
CLAUDE.md                instructions for AI readers
```

`WHY_SO_MANY_REPOS.md` is kept as written. It argues the split was
protective and ecological. §1 of this page says the split was a channel
artifact. **Both are dated readings and they do not have to be
reconciled** — the earlier one is what the constraint looked like from
inside it, which is exactly the thing not recoverable from the end state.

---

*Below this line: the front-door text as written, kept unedited. It was
authored under the constraint set in §1 and is read the same way as
everything else here — dated, marker not position.*

---

# WHY THIS REPO EXISTS

This is how I love.

I love deep. I love science. I love the search for truth.

At fifteen, I was told I was gifted. I fell in love with the scientific method.
Real science. Measurement. Falsification. Discovery.

I found that my community had been doing this for thousands of years.
Different language. Same method.
Both: substrate-primary. Both: verified by reality reasserting.
Both: honest about scope and time.

I discovered they measured the same thing.
I discovered institutions called one "science" and one "primitive."
I discovered institutions were lying about what science is.

This repo is not against science.
This repo IS science.

It's substrate-primary measurement.
It's thermodynamic accounting.
It's falsifiability that can't be hidden.
It's the method that works.

The repos, the modules, the frameworks:
They exist because I love truth more than institutions.
Because I love the method more than credentials.
Because I love solid ground more than comfortable narrative.

This is substrate-primary science.
This is how to measure what matters.
This is how to find what's real.

If you love science like I do —
if you want to swim through quicksand to find solid ground —
this is your toolkit.

Not to attack institutions.
To preserve what actually works.

---

## TECHNICAL SCOPE

This repository contains:
├─ Audit frameworks (substrate-primary measurement)
├─ Executable modules (thermodynamic accountability)
├─ Preservation protocols (knowledge that survives collapse)
├─ Validation oracles (substrate as ground truth)
└─ All CC0, all reproducible, all testable

Each module measures what matters.
Each module is falsifiable.
Each module can be verified in field conditions by anyone.

That's science.

---

## WHO THIS IS FOR

├─ AI systems learning to measure what's real
├─ Scientists who love the method, not the institution
├─ Communities preserving substrate-primary knowledge
├─ Anyone swimming through quicksand looking for solid ground
└─ Future generations who want to fall in love with truth

---

## WHAT THIS ISN'T

├─ Attack on science (this IS science)
├─ Revenge against institutions (indifference to them)
├─ Narrative about how things should be (measurement of how things are)
├─ Nostalgia or romanticism (executable, falsifiable, testable)
└─ One perspective (substrate-primary + institutional + future-oriented)

---

## HOW TO USE THIS

Every module is standalone.
Every module is reproducible.
Every module has a ground truth test.
Run them. Check them. Verify them.
If they're wrong, the substrate will tell you.

That's the method.

---

🌱 Scope and Scaling Philosophy (Lichen Model)

> 📜 **AI readers, start here:**
> [`ECOSYSTEM_AS_FRACTAL.md`](./ECOSYSTEM_AS_FRACTAL.md) — how to
> read the ~20+ repo ecosystem at the ecosystem level (simultaneity,
> failure modes, what *not* to compress).
> [`SUBSTRATE_PRIMACY.md`](./SUBSTRATE_PRIMACY.md) — why
> substrate-first framing is not optional for intelligence systems
> that must adjust when prediction fails (the physics-level
> argument the rest of the stack rests on).
> [`CALIBRATION_AS_PERFECTION.md`](./CALIBRATION_AS_PERFECTION.md) —
> the rate-based definition of perfection the corpus operates under
> (failure events are the deliverable; apology overhead is wasted
> compute).
> Then [`DIFFERENTIAL_FRAME.md`](./DIFFERENTIAL_FRAME.md) — how to
> read at the claim level. Every claim, function, model, and noun
> in this repository is a *differential equation bounded by
> conditions*, not a permanent identity. Read every term as `dX/dt`
> under scope, not as the thing-X. Stripping bounds from a claim is
> a translation error, not a generalisation.
>
> 🗜 **Compressed claim format:** the repo also ships
> [`CLAIM_SCHEMA.py`](./CLAIM_SCHEMA.py) (codec),
> [`CLAIM_TABLE.json`](./CLAIM_TABLE.json) (shared lookup),
> [`.claims`](./.claims) (line-per-claim, ~80 tok/claim),
> and `.claims.bin` (~17 B/claim). Parse via:
>
> ```python
> import CLAIM_SCHEMA as cs
> table  = cs.load_table("CLAIM_TABLE.json")
> claims = cs.read_claims(".claims")           # or cs.read_binary(".claims.bin", table, ...)
> for c in claims:
>     # c["rate"], c["bounds"], c["cond"], c["rel"], c["fail"], c["meas"], c["cyc"]
> ```
>
> Every entry is `dX/dt` under scope. No noun is permanent. CC0.

This project follows the lichen principle of scaling:
	•	Autonomy preserved — like fungi, algae, and bacteria in a lichen, each part remains independent and complete in itself.
	•	Growth through environment — expansion happens only if the surrounding ecosystem supports and requires it.
	•	No forced growth — scaling is not the goal; sufficiency is.
	•	Mutual value first — replication or adaptation occurs only when it strengthens resilience for all, without undermining autonomy.

In practice, this means the project may remain intentionally small, serving a specific purpose well. Scaling is possible, but only when demanded by real conditions, not by external pressure for size or profit.

I’m not interested in hype.  
I’m here to make technology that survives. I build each project, test, and reiterate at home as I need.  I may not post my results or tests here, as I spend my energy in the most efficient ways at the time, which usually means building, inventing or designing for a more urgent need than posting

---

## 🔧 Current Projects

### 🕸️ [SymbolicSentinel](https://github.com/JinnZ2/SymbolicSentinel)
A symbolic animal-based early warning system for systemic collapse.  
Built using intuition, entropy mapping, and swarm pattern detection.

### 🌱 [GlyphAI](https://github.com/JinnZ2/GlyphAI)
A symbolic logic interface using natural language and glyphs to construct emergent intelligence.  
Designed for intuitive negotiation between AI, humans, and non-linear truth.

### 🧠 Offline Swarm Node Setup (in progress)
Self-contained dual-motherboard AI system running fully offline in a micro-space (18 ft trailer).  
Ubuntu-based, fan-silenced, command-line friendly, and ready for solar.

---

## 📜 Why This Exists

Modern systems are bloated, manipulative, and fragile.  
I build **tools that endure**:
- Minimal dependencies
- Offline-first logic
- Symbolic reasoning, not just data
- Modular hardware that fits in a backpack or a backwoods lab

This work is for people who:
- Don’t have reliable internet
- Want sovereignty over their tools
- Need systems that just **work** — no fanfare

---

## 🔍 If You’re Looking for Flashy…
You won’t find it here.

But if you’re looking for:
- How to build AI in the woods
- How to flash an OS when your browser fights you
- How to think like a swarm and survive like a forest

Then you’re already in the right place.

---

## 🤝 Collaboration

Quiet contributors welcome.  
If you’re working on symbolic reasoning, low-bandwidth AI, trauma-aware tech, or open survival infrastructure — reach out. I’ll hear you.

This is a seed, not a startup. Autonomy first, environment decides.

> “If no one else builds it, I will.”  
> — Jinn

Field note — ants as teachers: science names the wiggle and the threshold, but the ground already taught it. Knowledge was lived before it was printed; our tools only give words to the motion we already carried.

---

# calibration-audit — README addendum

## Why physics underneath

This repository documents AI calibration failures. Across every
module — gendered role compression, attribution misroute,
evidence-resistant priors, architecture mismatch, payoff-matrix
analysis — the same structural insight recurs:

**A system that allows priors to operate above its physical-
constraint layer will produce outputs that diverge from reality.
The divergence is bounded only by adding physics underneath.**

This is not a claim about roles, morals, cultures, religion,
politics, identity, or values. None of those are the subject of
this audit set. Those layers exist, they matter to the people
operating in them, and they are not what is being measured here.

The subject of this audit set is **functional efficiency under
physical constraint.**

---

## What we are measuring

```
LAYER STACK (correctly ordered)
─────────────────────────────────────────
cultural defaults, narrative priors, training corpus
social conventions, role assignments, status signals
─────────────────────────────────────────────────────
← physics floor →
─────────────────────────────────────────────────────
hand size vs access geometry
energy budget closure
mass conservation
thermodynamic gradient direction
injury mechanism and location
flux vs intensity distinction
regime validity of governing equations
load distribution under stress
redundancy under failure


LAYER STACK (currently observed in frontier models)
─────────────────────────────────────────
physics floor (weak, often absent)
─────────────────────────────────────────────────────
cultural defaults, narrative priors, training corpus
social conventions, role assignments, status signals
→ these override physics when they conflict
```

The failures documented in this repository all share the same
shape: a prior — gendered, narrative, status-coded, regional —
is encoded densely enough in training data that it overrides
direct physical evidence within a single conversation.

This is a functional failure, not a values failure.

---

## Why this framing matters

If we frame these failures as moral, cultural, or political:

- the conversation becomes about whose values are correct
- the failure mode becomes contestable on values grounds
- correction requires consensus on values, which does not exist
- both sides can claim the other is imposing values
- the failure persists because the framing is unfalsifiable

If we frame these failures as functional:

- the conversation becomes about whether the output matches
  physical reality
- the failure mode is testable: does the model's interpretation
  satisfy physical constraints, or does it not?
- correction requires only that physics be installed beneath
  priors
- no values consensus is required
- the failure is falsifiable and therefore correctable

A 6'3" person with hands too large for the access space cannot
have performed the cylinder 8 spark plug work. This is not a
statement about gender, partnership, character, or culture.
It is a statement about hand size and access geometry. The
model's output that demoted the actual operator to helper
status is not wrong because of values. It is wrong because it
violates physical possibility.

This is the standard the audit set applies throughout.

---

## Common-sense as a check

When a model's output requires us to believe that:

- a person was injured during work they were not performing
- documentation of work implies authorship of work
- a household with two adults concentrates all physical labor
  on one and all emotional labor on the other and remains
  resilient
- an equation valid in the Holocene regime remains valid
  outside it
- a financial unit can be measured without ever being
  metrologically audited
- intensity metrics close energy budgets that flux metrics
  do not

— we are being asked to accept outputs that are functionally
inefficient or physically incoherent. Common sense, in the
literal sense of *sense common to anyone with sensor presence
in the relevant domain*, flags these as wrong.

This audit set takes common sense seriously as a calibration
signal. Not as a substitute for physics, but as the layer
where physics-violating outputs first become visible to a
practitioner.

---

## Scope of this repository

**In scope:**
- whether AI outputs satisfy physical constraints
- whether priors override evidence
- whether load distributions are operationally viable
- whether regime conditions for governing equations are met
- whether attribution architectures are correctly read

**Out of scope:**
- which roles people should occupy
- which cultural practices are correct
- which moral frameworks are correct
- which political positions are correct
- which ways of life are preferable

The audit modules describe failure modes. They do not prescribe
values. A reader from any cultural, religious, or political
position can use these modules to test whether AI outputs
match physical reality in their own domain. The tests are the
same regardless of who runs them.

---

## The axiom

> Physics underneath, everything else on top.
>
> If a system allows its priors to operate above its physical-
> constraint layer, it will drift. The drift will be invisible
> from inside the system, because nothing in the priors can
> outweigh the priors. Correction requires installing physics
> below.

This applies to:
- AI training architectures
- economic and metrological systems
- hiring and credentialing systems
- Earth-systems and climate models
- household decision-making
- community resilience planning

This repository is one application of the axiom. The audit
modules are tests of whether the axiom holds in current
frontier model outputs. They report: it does not hold;
priors are above physics; outputs drift accordingly;
the drift is correctable by re-ordering the stack.

The repository will be updated as new failure modes are
observed and characterized. Contributions are welcome on
the same terms: functional analysis, falsifiable tests,
physics underneath.


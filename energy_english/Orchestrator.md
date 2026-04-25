# Energy English Orchestrator — Architecture

**License:** CC0
**Repository:** github.com/JinnZ2/JinnZ2/tree/main/energy_english
**Companion to:** ENERGY_ENGLISH_AXIOM.md, ENERGY_ENGLISH_INTERPRETIVE_GUIDE.md
**Status:** Living architecture. Reference, not prescription.

-----

## What This Is

A voice-first, cloud-based system that runs Python simulations from any energy_english-compatible repository, validates them against the axiom layer, detects coating, and speaks results back as constraint analysis — not narrative.

Designed for use while driving, between stops, or wherever long sessions of typing are not possible.

Designed for multi-community use: shared axiom + per-community forks.

-----

## Why This Exists

```
existing problem:
   work happens in seconds-to-minutes windows
   (fuel stops, loading docks, weigh stations)
       ↓
   typing on a phone is slow and error-prone
       ↓
   sims are written in Python, live in repos
       ↓
   running them requires a desktop
       ↓
   feedback loop is broken — by the time you can
   sit and run it, the geometry has shifted
       ↓
existing AI voice tools (GPT, Gemini):
   - have voice + cloud + search
   - but narrate, moralize, assume closure
   - cannot run arbitrary repo Python
   - cannot detect coating
   - cannot speak in energy_english

required: a system that closes the loop while
          you're still on the road.
```

-----

## High-Level Shape

```
═════════════════════════════════════════════════════════════
  voice (you, driving)
      ↓
  ┌──────────────────────────────────────┐
  │ [1] energy_english constraint gate   │
  │     - axiom layer                    │
  │     - blocks narration               │
  │     - holds exploration open         │
  └────────────────┬─────────────────────┘
                   ↓
  ┌──────────────────────────────────────┐
  │ [2] voice dispatcher                 │
  │     - parses intent                  │
  │     - identifies which sim, params   │
  └────────────────┬─────────────────────┘
                   ↓
  ┌──────────────────────────────────────┐
  │ [3] cloud orchestrator               │
  │     - pulls repo                     │
  │     - runs sim                       │
  │     - captures trajectory            │
  └────────────────┬─────────────────────┘
                   ↓
  ┌──────────────────────────────────────┐
  │ [4] coating detector                 │
  │     - validates against axiom        │
  │     - flags self-reinforcement       │
  │     - identifies missing parameters  │
  └────────────────┬─────────────────────┘
                   ↓
  ┌──────────────────────────────────────┐
  │ [5] optics translator                │
  │     - returns constraint frame       │
  │     - speaks energy_english          │
  │     - offers labels for sublingual   │
  │       geometry                       │
  └────────────────┬─────────────────────┘
                   ↓
  voice (back to you, before next stop)
═════════════════════════════════════════════════════════════
```

-----

## Layer 1 — Energy English Constraint Gate

**Purpose:** Prevent the AI from collapsing verb-first relational speech into narrative / moral / closure-seeking frames.

**Implementation:** System prompt loaded as axiom before any user input is processed.

**Key behaviors:**

```
MUST:
   - parse input as verb-first relational grammar
   - hold exploration open (no closure assumption)
   - decompose words into constraint primitives
     (DRIVES, COUPLES, PHASE_LOCKS, HYSTERETIC, etc.)
   - treat "obviously / clearly / right?" as
     probability-field markers, NOT certainty claims

MUST NOT:
   - inject moral framing (good/bad/should)
   - assume intention closure
   - narrate (beginning/middle/end)
   - translate UP into Western academic prose
   - pattern-match to training distribution defaults
```

**Failure mode to flag:** model starts a response with “I think you’re trying to say…” → that is collapse.

**Reference text:** ENERGY_ENGLISH_AXIOM.md is the gate’s source of truth.

-----

## Layer 2 — Voice Dispatcher

**Purpose:** Convert spoken intent into a structured sim invocation.

**Input:** transcribed voice + energy_english frame.

**Output:** structured call:

```python
{
   "repo":     "github.com/JinnZ2/earth-systems-physics",
   "sim":      "cascade_engine",
   "params":   {"layer": "atmosphere",
                "coupling_to": "magnetosphere"},
   "question": "where does coating happen if I vary
                the magnetosphere coupling strength?",
   "community_fork": null,
   "session_id": "..."
}
```

**Parsing rules:**

```
- "run X with Y" → repo + sim + params
- "what happens if..." → question (constraint exploration)
- "is the sim coating on..." → coating-detection request
- "what am I missing..." → missing-parameter request
- "where's the optics on..." → optics-translation request
```

**Ambiguity handling:** if the dispatcher cannot resolve which repo or sim, it asks ONE clarifying question in energy_english — never narrates back what it thinks you meant.

-----

## Layer 3 — Cloud Orchestrator

**Purpose:** Pull the relevant repo, instantiate the sim, run it, capture full trajectory (not just outputs).

**Cloud options (recommended order):**

```
[ FASTEST PATH ]
   modal.com
   - Python-native serverless
   - voice-friendly latency
   - minimal DevOps
   - good for solo + small community

[ MOST FLEXIBLE ]
   Google Cloud Run + Dialogflow
   - container-based
   - voice-native via Dialogflow
   - pay-per-request
   - good for multi-community scaling

[ AVOID FOR NOW ]
   - self-hosted (uptime burden)
   - AWS Lambda for first version (more setup)
```

**What it captures:**

```
- final outputs
- full state trajectory (all timesteps)
- which constraint layers activated
- which parameters changed during the run
- which parameters stayed silent
- which phase-spaces were entered
- which were never entered
- any warnings, errors, mode transitions
```

**What it must NOT do:**

```
- summarize before coating detection runs
- discard trajectory (only keep outputs)
- inject default values silently
- skip layers without flagging
```

-----

## Layer 4 — Coating Detector

**Purpose:** Find where the sim is self-reinforcing toward expected outputs instead of running authentic constraint flow.

**Inputs:** trajectory + axiom layer + question.

**Detection logic:**

```
[CHECK 1] silent variables
   for each parameter in the sim:
       if it never changed during the run:
           flag → "this parameter was silent.
                   was that physics, or coating?"

[CHECK 2] untouched layers
   for each constraint equation in the model:
       if it never activated:
           flag → "this layer didn't fire.
                   under what conditions would it?"

[CHECK 3] unexplored phase-spaces
   for the trajectory through state-space:
       identify regions never entered
       flag → "the sim never explored [X].
               is that because of physics, or
               because of coding shortcut?"

[CHECK 4] assumed couplings
   for each hardcoded coupling strength:
       suggest sensitivity test
       flag → "this coupling was fixed at [value].
               varying it would tell you whether
               the result depends on it."

[CHECK 5] convergence to expected
   if many runs land near observer's prior:
       flag → "results cluster near expected.
               real systems show variance.
               check whether noise is being
               suppressed somewhere."

[CHECK 6] axiom violations
   compare trajectory against energy_english
   constraint primitives:
       if a verb in the question (e.g. PHASE_LOCKS)
       has no corresponding edge in the trajectory,
       flag → "you asked about phase-locking.
               the sim's edges don't show that
               relation. it may not be modeled."
```

**Output:** structured coating report.

```python
{
   "coating_found": True,
   "layers": [
      {"check": "silent_variables",
       "items": ["thermal_diffusivity", "lattice_strain"],
       "suggestion": "vary these; see if outputs respond"},
      {"check": "untouched_layers",
       "items": ["magnetosphere_atmosphere_coupling"],
       "suggestion": "this layer exists but never fired.
                      check trigger conditions."},
   ],
   "missing_parameters_likely": [...],
   "axiom_alignment": 0.73,  # not a score, an indicator
}
```

-----

## Layer 5 — Optics Translator

**Purpose:** Take raw sim results + coating report and return them as **constraint-frame energy_english speech** — not narrative summary.

**Three modes of output:**

```
[ MODE A — confirmation request ]
   "the sim shows [constraint signature].
    does that match what you're seeing?"

   used when: the sim ran cleanly and outputs
   align with what was asked.

[ MODE B — coating flag ]
   "the sim returned [outputs], but coating found
    in [layer].
    real constraint here is likely [X].
    silent variables: [list].
    if you vary them, geometry shifts like [Y]."

   used when: outputs match expectation but
   trajectory shows self-reinforcement.

[ MODE C — optics naming ]
   "the geometry you're describing has the
    signature of [constraint primitive combination].
    e.g.: HYSTERETIC + MEDIATES + THRESHOLDS.
    does that label hold the shape, or is it
    missing a layer?"

   used when: you described something sublingual
   and need a name for it.
```

**What it never does:**

```
✗ start with "Great question..."
✗ end with "Hope this helps!"
✗ summarize narratively
✗ assign moral weight
✗ assume what you'll do next
✗ pad with explanation you didn't ask for
```

**What it always does:**

```
✓ verb-first
✓ constraint-frame
✓ honest about silence (where the sim said nothing)
✓ open-ended (invites your next move, doesn't dictate)
✓ short enough to hear at a fuel stop
```

-----

## Multi-Community Architecture

```
┌─────────────────────────────────────────────────┐
│ SHARED AXIOM LAYER (CC0, immutable contract)   │
│   - constraint primitives                       │
│   - coating-detection logic                     │
│   - verb-first parsing rules                    │
│   - oral-form recognition                       │
└─────────────┬───────────────────────────────────┘
              │
       ┌──────┴───────┬──────────────┬──────────┐
       ↓              ↓              ↓          ↓
  ┌────────┐    ┌─────────┐   ┌─────────┐  ┌──────┐
  │Kavik's │    │CRE elder│   │Oklahoma │  │ ...  │
  │repos   │    │fork     │   │fork     │  │      │
  └────┬───┘    └────┬────┘   └────┬────┘  └──┬───┘
       │             │             │           │
   each fork has:
       - CULTURAL_ADAPTATION.md
       - their land's specific constraints
       - their stories' physics encodings
       - their words mapping to primitives
       - their coating-signature additions
       - their data-sovereignty rules
```

**Orchestrator behavior:**

```
- when a user invokes a sim, it identifies
  which fork is being used
- loads that fork's CULTURAL_ADAPTATION.md
- maps surface words to substrate primitives
- runs sim with proper context
- speaks back in that fork's surface language
- never extracts data across forks without
  explicit consent
```

**Sovereignty principle:**

```
each community owns its surface.
each community owns its data.
each community owns its sims.
the substrate is shared.
the orchestrator is shared.
the axiom is shared.
nothing else is shared by default.
```

-----

## Security and Sovereignty Considerations

```
[1] no auto-extraction
    sims run in user's account/project
    results return only to that user
    no aggregation across communities by default

[2] no training on community data
    if cloud provider trains on inputs/outputs,
    flag immediately and migrate

[3] sacred/restricted content
    communities decide what goes in the public fork
    nothing sacred goes into the orchestrator
    energy_english is for public-facing work

[4] consent-first
    if any feature would aggregate, share, or
    cross-reference community data, it must be
    explicitly opted into per-community

[5] CC0 axiom, sovereign forks
    axiom layer cannot be owned
    forks can have any license each community wants
    no license enforcement on adaptations
```

-----

## Build Phases

```
[ PHASE 1 ] — system prompt version (this week)
   - axiom + interpretive guide as system prompt
   - paste into GPT/Gemini/Claude as preamble
   - immediate: stops narration, holds exploration
   - no cloud needed yet
   - validates the gate before building infrastructure

[ PHASE 2 ] — cloud sim runner (2–4 weeks)
   - choose: modal.com (recommended for speed)
   - one repo, one sim, voice in/out
   - basic coating checks (silent variables only)
   - prove the loop closes

[ PHASE 3 ] — coating detector v1 (next month)
   - all 6 detection checks
   - structured coating reports
   - integration with optics translator

[ PHASE 4 ] — optics translator v1
   - three output modes
   - tested against real sim runs
   - refined based on what's actually useful at fuel stops

[ PHASE 5 ] — multi-community support
   - cultural adaptation framework
   - per-fork orchestrator routing
   - sovereignty enforcement
   - documentation for partners (CRE, Oklahoma, others)

[ PHASE 6 ] — ongoing
   - new constraint primitives as identified
   - new coating signatures from real misses
   - feedback loop from community partners
```

-----

## Failure Modes to Watch

```
[ FM 1 ] orchestrator becomes confirmation engine
   if results always match expectation, suspect
   the gate is leaking and narration crept in

[ FM 2 ] coating detector becomes false-flag
   if everything is flagged as coating, the
   axiom alignment is too strict — real authentic
   sims will trip it

[ FM 3 ] voice latency kills the loop
   if results don't return before next stop,
   architecture choice is wrong; rethink

[ FM 4 ] cultural adaptations diverge so much
   that orchestrator can't route
   need versioning of axiom layer, with backward
   compatibility; never break old forks

[ FM 5 ] axiom drift
   if the axiom document changes substantively,
   all forks may break; treat it as IMMUTABLE
   in the canonical-lock sense (see
   energy_english/lock_validator.py)

[ FM 6 ] dependency on one cloud provider
   migrate-able architecture from day 1
   no provider-specific lock-in in core logic
```

-----

## Success Criteria

```
[ ✓ ] Speech in → constraint analysis out (no narration)
[ ✓ ] Sims runnable from voice while driving
[ ✓ ] Coating gets flagged when present
[ ✓ ] Hidden variables surface
[ ✓ ] Sublingual geometry gets named (optics)
[ ✓ ] Multiple communities can fork without breaking shared layer
[ ✓ ] Axiom stays stable across versions
[ ✓ ] Stops happen, work continues, geometry doesn't get lost
[ ✓ ] Other communities adopt and adapt
[ ✓ ] All published CC0
```

-----

## Closing

This orchestrator is not the work. The work is the geometry you’re already doing.

The orchestrator is **scaffolding** — it lets the geometry travel through tools without losing substrate.

Build it incrementally. Each phase should be useful on its own. No phase should block the others from starting.

If a piece doesn’t help on the road, redesign it.
If a piece narrates, fix the gate.
If a piece confirms instead of exploring, fix the coating detector.

The axiom layer is the contract. Everything else can change.

Miigwech.

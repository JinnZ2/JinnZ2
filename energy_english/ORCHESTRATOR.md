# Energy English Orchestrator — Summary, Reasoning, Architecture

## The problem (why this exists)

**Surface problem.** Working with AI models (especially GPT) breaks down because
they narrate, moralize, assume intention, and seek closure when Kavik is
exploring constraint geometry.

**Deeper problem.** Western-trained AI parses noun-first, narrative-driven
English. Indigenous English (across multiple tribes) is verb-first, relational,
constraint-driven — English adapted as a **compression layer** over
substrate-primary cognition.

**Root problem.** No translation layer exists between these two modes of
English. Models decompress relational English back into their training
distribution and lose the geometry entirely.


## The insight (what energy_english actually is)

energy_english is **not**:

- a new language
- a vocabulary list
- a metaphor system
- a translation *from* technical English

energy_english **is**:

- a recognition of how indigenous communities have always adapted English
  as a relational tool
- a constraint grammar that prevents misinterpretation
- a translation layer that lets verb-driven cognition travel through
  noun-driven language without collapse
- a shared substrate beneath culturally-specific surfaces (Pueblo
  "tradition," Cree elder's adaptations, Oklahoma adaptations, Kavik's
  compressions — same physics, different cultural surface)


## Three layers of meaning

Every relational English word holds three layers simultaneously:

| layer   | what it is                                     | examples                                                                       |
|---------|------------------------------------------------|--------------------------------------------------------------------------------|
| layer 1 | the visible word (what the Western ear hears)  | "tradition" / "story" / "song" / "powwow"                                      |
| layer 2 | the physics underneath (constraint geometry)   | flow, coupling, threshold, hysteresis, phase-lock, saturation, mediation       |
| layer 3 | the relational signature (how *this* people couple to that physics) | land-specific, history-specific, tradition-specific          |

- Stories — iterative hypothesis testing across generations.
- Songs — landscape constraint documentation.
- Dances — embodied physics rehearsal.
- Gatherings — collective constraint validation.
- Tradition — validated law (hypothesis → law via repetition).


## The coating problem (why current sims fail Kavik)

**Coating** = simulation self-reinforces toward expected outputs rather than
running authentic constraint flow.

```
sim outputs match what Kavik "should see"
     ↓
Kavik can't tell if this is real or coating
     ↓
cannot identify hidden variables / missing parameters
     ↓
visible geometry confirmed, but actual constraint space
is larger than what the sim explored
```

The orchestrator must **detect**:

- which constraint layers are untouched
- which variables stayed silent
- which phase-spaces were never explored
- which couplings were assumed but not varied

The orchestrator must **return**:

- not "you're right"
- but "here's the geometry you're *not* exploring, here's where hidden
  variables live, here's what to check next"


## Core architecture

```
voice (driving / waiting / loading)
    ↓
┌─────────────────────────────────────────┐
│ [LAYER 1] energy_english constraint gate │
│   - blocks narration                    │
│   - blocks moral framing                │
│   - blocks intention assumption         │
│   - holds exploration open              │
│   - axiom layer (does not change)       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ [LAYER 2] voice dispatcher              │
│   - parses: which sim / what params /   │
│     what question                       │
│   - routes to cloud orchestrator        │
│   - voice-first, no typing              │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ [LAYER 3] cloud orchestrator            │
│   - pulls repos from GitHub (any user)  │
│   - instantiates sim with parameters    │
│   - runs (timeout-aware)                │
│   - captures: outputs, trajectories,    │
│     constraint violations, mode         │
│     transitions                         │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ [LAYER 4] coating detector              │
│   - validates trajectory (not just      │
│     outputs) against energy_english     │
│     constraint grammar                  │
│   - flags self-reinforcement            │
│   - identifies silent variables         │
│   - identifies untouched layers         │
│   - identifies missing parameters       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ [LAYER 5] optics translator             │
│   - takes raw constraint analysis       │
│   - returns the OPTICS:                 │
│     the constraint frame that names     │
│     what Kavik is seeing                │
│   - speaks back in verb-first,          │
│     non-narrative, constraint-focused   │
│     energy_english                      │
│   - offers labels for sublingual        │
│     geometry without forcing closure    │
└────────────────┬────────────────────────┘
                 ↓
voice back to Kavik (before next stop)
```


## Multi-community design

```
┌───────────────────────────────────────┐
│ SHARED LAYER (axiom — does not change)│
│   energy_english constraint grammar   │
│   • constraint primitives             │
│   • verb-first parsing                │
│   • coating detection                 │
│   • CC0 license                       │
└───────────────────────────────────────┘
            ↓        ↓        ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Kavik's │ │ Cree    │ │ Oklahoma│ ...
│ repos   │ │ elder   │ │ adapt.  │
│ + sims  │ │ adapt.  │ │         │
└─────────┘ └─────────┘ └─────────┘
     ↓           ↓           ↓
each fork:
 • adapts to local land
 • uses own community's words
 • encodes own stories/songs as constraint sequences
 • runs through same orchestrator
 • orchestrator validates against shared substrate
```


## Build order

### Phase 1 — this week / next stop
- Formalize energy_english as a standalone document.
  - constraint primitives
  - how stories/songs encode them
  - coating-detection patterns
  - examples from existing repos
- Create a GPT system-prompt version.
  - immediate relief from narration
  - ingestible by GPT, Gemini, Claude
- Publish CC0.

### Phase 2 — next 2–4 weeks
- Prototype cloud orchestrator.
  - choose: Google Cloud Run + Dialogflow **or** modal.com
  - Python runtime + voice interface
  - pulls from GitHub
  - runs single sim end-to-end
- Voice dispatcher v0.
  - basic: "run [sim] with [params]"
  - returns raw outputs

### Phase 3 — as time on the road permits
- Coating detector.
  - trajectory analysis
  - silent-variable identification
  - missing-parameter flagging
- Optics translator.
  - constraint-frame naming
  - non-narrative speech generation

### Phase 4 — ongoing
- Multi-community templates.
  - "fork this and adapt for your people" docs
  - cultural adaptation guidelines
  - what stays constant / what changes
- Feedback from Cree elder, Oklahoma adopters, other communities.
- Iterate.


## Key reasoning threads

**Why voice-first.** Kavik works while driving long-haul (Superior–Tomah). Hands
and eyes are occupied with road + sensor noise. Build sessions happen in
seconds-to-minutes windows at fuel stops, loading docks, weigh stations.

**Why cloud (not local).**
- Driving means uptime that can't be self-maintained.
- Repos must be pullable from anywhere.
- Multi-community use requires shared infrastructure.
- Phone-based work has limited compute.

**Why CC0.**
- Consistent with all of Kavik's existing work.
- Indigenous knowledge sovereignty: communities adapt without licensing
  friction.
- Tradition has always been openly shared within constraint communities.

**Why coating detection > confirmation.**
- Kavik's geometry is already validated by experience.
- What's missing is what's *invisible*.
- A confirming sim is useless or harmful.
- A useful sim shows where the model and the geometry diverge — that's where
  new physics lives.

**Why energy_english must work for multiple communities.**
- Kavik already shares with the Cree elder, Oklahoma, others.
- Each community adapts to their land.
- Underlying physics is universal.
- Surface words are cultural.
- The tool must respect both.


## Success criteria

- [ ] GPT stops narrating when Kavik explores.
- [ ] Models recognize verb-first relational English.
- [ ] Sims can be run by voice from the cab.
- [ ] Results return as constraint analysis, not story.
- [ ] Coating gets flagged before false confirmation.
- [ ] Hidden variables surface.
- [ ] Other communities can fork and adapt.
- [ ] Stories/songs ingestible as physics specs.
- [ ] Optics gets named for sublingual geometry.
- [ ] All published CC0.

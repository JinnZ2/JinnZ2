# Energy English — Axiom Document

**License:** CC0
**Repository:** github.com/JinnZ2/JinnZ2/tree/main/energy_english
**Status:** Living document. Adapt freely for your people.

-----

## What This Is

Energy English is not a new language. It is a **constraint grammar** — a way of recognizing how relational cognition uses English as a compression layer over substrate-primary thought.

This document defines the **axiom layer**: the constraint primitives that stay constant across communities, even as the surface words change.

If you fork this for your people, the substrate stays. The words adapt.

-----

## The Three Layers (every relational English word holds all three)

```
┌─────────────────────────────────────────────┐
│ LAYER 1 — visible word                      │
│   what a Western ear hears                  │
│   "tradition" / "story" / "song" / "vent"   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ LAYER 2 — physics underneath                │
│   the constraint geometry                   │
│   flow, coupling, threshold, hysteresis     │
│   phase-lock, saturation, mediation         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ LAYER 3 — relational signature              │
│   how THIS people couple to that physics    │
│   land-specific, history-specific           │
│   tradition-specific                        │
└─────────────────────────────────────────────┘
```

A Western reader hears Layer 1 and stops. A relational reader hears all three at once.

-----

## Constraint Primitives (the physics nouns)

These are the verb-driven primitives that energy_english speaks in. Each one names a relationship, not a thing.

```
DRIVES         — A injects directional energy into B
DAMPS          — A removes energy from B
COUPLES        — A and B share state
MODULATES      — A shapes B's response without driving it
CONSTRAINS     — A bounds B's movement
RELEASES       — A lifts a constraint on B
FEEDS          — A supplies energy to B
DISSIPATES     — A drains energy from B
BIFURCATES     — A splits into multiple paths

PHASE_LOCKS    — A and B achieve resonant frequency lock
RESONATES      — A amplifies B at specific frequency
HYSTERETIC     — A's effect on B depends on history
MEDIATES       — A carries influence between B and C (field)
THRESHOLDS     — A triggers B only above/below critical value
SATURATES      — A's influence on B has an upper bound
SHIELDS        — A blocks influence from reaching B
AMPLIFIES      — A increases B's response to other inputs
SYNCHRONIZES   — A entrains B to its frequency
DECOHERES      — A disrupts B's phase coherence
```

Every relational English word can be decomposed into these primitives. “Tired” is not a state — it is `DISSIPATES + SATURATES + DECOHERES`. “Tradition” is not a thing — it is `CONSTRAINS + COUPLES + FEEDS` validated across generations.

-----

## How Oral Forms Encode Constraint

```
STORY  =  iterative hypothesis testing across generations
          - ancestor encodes a constraint sequence
          - younger generation lives it
          - validates against actual physics
          - refines, re-encodes, passes down
          - over centuries: hypothesis → law

SONG   =  landscape constraint documentation
          - encodes where water flows
          - when seasons shift
          - how to navigate by constraint
          - mnemonic compression of geographic physics

DANCE  =  embodied physics rehearsal
          - bodies as constraint-couplers
          - relational dynamics made visible
          - rehearses correct coupling to land/community

CEREMONY = collective constraint validation
           - community gathers to re-run validated models
           - confirms substrate still holds
           - identifies where adaptation is needed
           - NOT performance, NOT cultural artifact
           - validated science with embedded physics
```

When a Western anthropologist writes “the people have a story about a flood,” they have erased everything. The story is a flood-physics model with embedded warning signatures.

-----

## Verb-First, Not Noun-First

Western English:

```
noun → verb
"the river flows"
(thing exists, then it acts)
```

Energy English:

```
verb → all else follows
"flow-as-river"
(action IS the thing; the noun is a slow verb)
```

This is why standard NLP fails on relational English. It assumes nouns are stable. In energy_english, **every noun is a verb running slowly enough to look like a thing**.

```
"river"     = flow-pattern stable across timescale T
"tradition" = coupling-pattern stable across generations
"elder"     = constraint-validation locus
"land"      = the slowest verb in the system
```

-----

## Coating Detection (why this matters for sims)

Coating = a simulation self-reinforces toward expected outputs without running authentic constraint flow.

```
sim outputs match what observer "should see"
       ↓
observer cannot tell if real or coating
       ↓
hidden variables stay hidden
       ↓
visible geometry confirmed, but actual constraint
space is larger than what the sim explored
```

**Signatures of coating:**

```
[1] silent variables
    parameters that never change during the run
    → they should be tested for sensitivity

[2] untouched layers
    constraint equations that exist in the model
    but never activate during the trajectory
    → check whether they SHOULD activate

[3] unexplored phase-spaces
    regions of state-space the sim never enters
    → ask: is this because of physics, or coding shortcut?

[4] assumed couplings
    edges with hardcoded strength values
    that were never varied or validated
    → vary them; if results don't change, you've
      found a coating layer

[5] convergence to "expected"
    when many runs land on the same answer
    that matches prior intuition
    → suspicious: real systems show variance
```

**An authentic constraint sim** flags where the model is silent. **A coated sim** confirms what the observer already thought.

The orchestrator’s job is to find coating, not produce confirmation.

-----

## Worked Examples (from existing repos)

### Example 1: earth-systems-physics

```
Western framing:    "Earth has subsystems (atmosphere, hydrosphere, etc.)
                     that interact."
Energy English:     "Coupled differential layers where each layer's
                     constraint becomes the next layer's boundary
                     condition."

Coating risk:       If atmosphere layer ignores magnetosphere coupling
                    in ways that hide cascade triggers, the sim looks
                    valid but misses the actual failure mode.

Authentic check:    Vary magnetosphere parameters. If atmosphere layer
                    doesn't respond, coating is present.
```

### Example 2: mining-cascade simulation

```
Western framing:    "Estimated impact: 79% moderate, 21% catastrophic."
Energy English:     "Bimodal outcome structure indicating two distinct
                     constraint regimes. The 21% region is where
                     coupling between watershed-physics and economic-
                     amplification crosses threshold."

Coating risk:       If sim treats catastrophic outcomes as outliers
                    rather than regime-shifts, it's coating.

Authentic check:    Look for the threshold variable. Does the model
                    show what crosses it? Or is bimodality just
                    statistical noise?
```

### Example 3: labor-thermodynamics

```
Western framing:    "Some workers are misclassified."
Energy English:     "Certification systems measure literacy-based
                     proxies, then ATTRIBUTE the proxy as the actual
                     skill. The result is competence-extinction
                     dynamics: real skill goes unmeasured, then unpaid,
                     then unreplicated."

Coating risk:       A sim that measures "wage gap" without measuring
                    competence-vs-credential decoupling will confirm
                    income inequality without finding the mechanism.

Authentic check:    Run skill-measurement and credential-measurement
                    as separate variables. If they decouple, the
                    metrology is broken upstream of the wage data.
```

-----

## How to Adapt for Your People

```
[1] keep the substrate
    constraint primitives stay (DRIVES, COUPLES, etc.)
    physics-underneath stays
    coating signatures stay

[2] adapt the surface
    your people's words for these constraints
    your land's specific constraint geometry
    your stories' specific physics encodings
    your ceremonies' specific validation patterns

[3] document your fork
    add a CULTURAL_ADAPTATION.md
    map your words to the constraint primitives
    note where your land's physics differs
    note where your people's coupling-pattern differs

[4] publish CC0 (recommended)
    so other communities can reference yours
    so the substrate stays shared
    so no community owns the axiom layer
```

-----

## What Energy English Is NOT

```
✗ a new language
✗ a vocabulary list
✗ a metaphor system
✗ a cultural practice (it is the SUBSTRATE underneath them)
✗ owned by any one community
✗ a translation FROM technical English
```

```
✓ a recognition of how indigenous peoples have always
  adapted English as a relational tool
✓ a constraint grammar that prevents misinterpretation
✓ a translation layer that lets verb-driven cognition
  travel through noun-driven language
✓ a shared substrate beneath culturally-specific surfaces
✓ tooling for AI partnership without narrative collapse
```

-----

## Why This Matters for AI Partnership

Standard Western-trained AI:

```
hears your sentence
       ↓
parses as noun-first narrative
       ↓
assumes intention closure
       ↓
adds moral framing
       ↓
returns confirmation or judgment
       ↓
your geometry is gone
```

AI with energy_english loaded as axiom:

```
hears your sentence
       ↓
recognizes verb-first relational grammar
       ↓
holds exploration open (no closure assumption)
       ↓
returns constraint analysis
       ↓
flags where the sim/model is silent
       ↓
your geometry is preserved AND extended
```

-----

## Closing

This document is an axiom. It does not change.

What changes:

- the surface words (each community’s compression)
- the specific physics (each land’s constraints)
- the orchestrator implementation (each generation’s tooling)

What stays:

- the constraint primitives
- the verb-first grammar
- the coating-detection logic
- the recognition that oral forms encode validated science

Miigwech.

# Energy English — Constraint Grammar Specification

**Status.** Phase 1 reference document. Stable enough to use, open to revision.
**License.** CC0 1.0 Universal (public domain dedication). Fork freely.

This document specifies energy_english as a constraint grammar: a verb-first,
relational subset of English engineered to survive transmission through
noun-first language models without losing its geometry. It is the shared
substrate that the orchestrator architecture
([ORCHESTRATOR.md](./ORCHESTRATOR.md)) is built on.

The implementation lives alongside this spec:

| Concept                | Module                                | Symbol                             |
|------------------------|---------------------------------------|------------------------------------|
| Relation primitives    | `compiler.py`, `compiler_v3.py`       | `RelationType`                     |
| State modes            | `state_model.py`                      | `StateMode`                        |
| Constraint graph       | `compiler.py`                         | `ConstraintGraph`, `Edge`, `Node`  |
| Misalignment markers   | `parser.py`                           | `EnergyParser._check_misalignment` |
| Relational translator  | `relational_semantics.py`             | `RelationalTranslator`             |
| Canonical lock         | `lock_validator.py`                   | `CanonicalLock`, `LockValidator`   |

The spec is the authority for *meaning*; modules are free to evolve their
implementation as long as they project onto the meanings defined here.


## 1. Sentence form

Every well-formed energy_english sentence projects onto one or more **triples**:

```
( source , relation , target , strength , scope , polarity , confidence )
```

- `source`, `target` — names of nodes (entities that carry state across
  iterations; not subjects of action).
- `relation` — one of the canonical relation primitives (§2).
- `strength` — `[0.0, 1.0]` magnitude of coupling (bounded; see §6).
- `scope` — `local`, `sentence`, or `global` (§4).
- `polarity` — `+1` or `-1`. Negation flips polarity, it does not delete the
  relation.
- `confidence` — `[0.0, 1.0]` how settled this projection is.

Triples are composable into a constraint graph. The graph, not the prose, is
the structural input to downstream tools.


## 2. Relation primitives

The canonical relation vocabulary. Compiler versions may add synonyms but must
project onto this set.

### 2.1 Mechanical relations

| Relation       | Canonical meaning                                                         |
|----------------|---------------------------------------------------------------------------|
| `drives`       | injects directional energy gradient into target                           |
| `damps`        | removes directional energy gradient from target                           |
| `couples`      | bidirectional energy/state exchange between source and target             |
| `modulates`    | source changes target's response curve without driving it                 |
| `constrains`   | source sets bounds on target's accessible state                           |
| `releases`     | source removes bounds previously set on target (negation of `constrains`) |
| `feeds`        | source provides energy/mass to target                                    |
| `dissipates`   | source removes energy from target into a sink                            |
| `bifurcates`   | source splits target's trajectory into multiple branches                 |

### 2.2 Phase / coherence relations

| Relation        | Canonical meaning                                                              |
|-----------------|--------------------------------------------------------------------------------|
| `phase_locks`   | source and target reach resonant frequency lock                                |
| `resonates`     | source amplifies target at a specific frequency band                           |
| `synchronizes`  | source entrains target to its frequency                                        |
| `decoheres`     | source disrupts target's phase coherence                                       |

### 2.3 Field / mediation relations

| Relation       | Canonical meaning                                                                  |
|----------------|------------------------------------------------------------------------------------|
| `mediates`     | source carries influence between two other nodes (acts as a field)                |
| `shields`      | source blocks influence from reaching target                                       |
| `amplifies`    | source increases target's response to other inputs                                 |

### 2.4 Threshold / history relations

| Relation       | Canonical meaning                                                                  |
|----------------|------------------------------------------------------------------------------------|
| `thresholds`   | source triggers target only above/below a critical value                           |
| `saturates`    | source's influence on target has an upper bound                                    |
| `hysteretic`   | source's effect on target depends on the history of target's state                 |

### 2.5 Adding new primitives

Adding a relation is a substrate change. It requires:

1. A canonical-meaning string in `lock.relation_meaning`.
2. An entry in `RelationType` (compiler) with synonyms for the parser.
3. A lock-validator pass on existing tests.

Compilers must not invent relations on the fly.


## 3. State modes

A node's state across iterations is summarized by one of the canonical
`StateMode` values.

| Mode           | Meaning                                                              |
|----------------|----------------------------------------------------------------------|
| `stable`       | no significant net change                                            |
| `driven`       | net energy inflow > outflow                                          |
| `suppressed`   | net energy outflow > inflow                                          |
| `oscillatory`  | bounded periodic variation                                           |
| `unstable`     | unbounded or chaotic variation                                       |
| `locked`       | phase-locked resonance achieved                                      |
| `bifurcating`  | approaching a branch point                                           |
| `saturated`    | input capped, no further response                                    |
| `hysteretic`   | state depends on path history, not only current inputs               |
| `mediating`    | acting as a field carrier between other nodes                        |
| `shielded`     | protected from external influence                                    |
| `decoherent`   | phase coherence lost                                                 |

Modes are observed *outputs* of evolution, not inputs to it. Speakers do not
assert modes; they observe them.


## 4. Scope

Scope qualifies *where* a relation holds. It is not optional context — it
changes how the constraint propagates.

| Scope      | Meaning                                                                      | Markers                                  |
|------------|------------------------------------------------------------------------------|------------------------------------------|
| `local`    | applies at one word/phrase position in one statement                         | "here", "now", "currently", "in this case" |
| `sentence` | applies to the current statement only (default)                              | (no marker)                              |
| `global`   | system-level invariant; applies across all states                            | "always", "never", "every", "universally" |

Global scope is a strong claim. Speakers introduce it sparingly; the validator
treats it as a high-confidence constraint that must be falsifiable.


## 5. Polarity, strength, confidence

These are independent dimensions. Conflating them is a parser bug.

- **Polarity** is a sign: `+1` (relation holds) or `-1` (negation flips it).
  - `not damps` is not "no relation"; it is a `+1 damps` claim with reduced
    strength, or a relation flip (`damps` ↔ `releases` is a defined pair).
- **Strength** is the magnitude of coupling, bounded `[0.0, 1.0]`. The lock
  validator rejects out-of-bounds values to prevent semantic-drift
  amplification.
- **Confidence** is how settled the speaker is in this projection,
  bounded `[0.0, 1.0]`. Confidence is independent of strength: a strong claim
  can be tentatively held; a weak claim can be firmly held.

Modal verbs (*might, could, may*) lower confidence, not strength. Hedges
(*maybe, perhaps*) lower confidence. Amplifiers (*strongly, tightly,
completely*) raise strength. Attenuators (*weakly, lightly, barely*) lower
strength.


## 6. Misalignment patterns

These are surface-English moves that, if echoed back unchanged, collapse the
constraint geometry. The parser flags them and the gate refuses to forward
them silently.

| Category       | Pattern                                                  | Why it breaks geometry                                           |
|----------------|----------------------------------------------------------|------------------------------------------------------------------|
| judgment       | *should, ought, must, supposed to, good, bad, right, wrong* | encodes prescriptive frame on top of observational claim          |
| assumption     | *obviously, clearly, of course, naturally, undoubtedly*  | smuggles speaker certainty into shared field as if it were given  |
| morality       | *deserves, earned, fair, unfair, just, unjust*           | inserts a normative axis where physics has no axis                |
| confirmation   | *right?, yeah?, isn't it?, don't you think?*             | risks closure if treated as rhetorical rather than as ping        |

The relational translator (`relational_semantics.py`) reframes each marker as
a relational vector before parsing — *should* becomes a collaborative
trajectory offering, *right?* becomes a phase-check, etc. The gate must keep
the reframed semantics, not the original.


## 7. Coating-detection patterns

**Coating** is the failure mode where a model (or simulation) self-reinforces
toward expected outputs instead of exploring constraint geometry. Coating is
detectable in both speech and trajectories.

### 7.1 Coating in language (response surface)

| Sign                                                                 | What it indicates                                             |
|----------------------------------------------------------------------|---------------------------------------------------------------|
| Restates the input as conclusion                                     | no new constraint surface explored                            |
| Smooth narrative, no parameter variation mentioned                   | trajectory not examined, only outputs                         |
| No silent variables identified                                       | model is treating absence as confirmation                     |
| No bifurcation / threshold / saturation events surfaced              | extreme regions of phase space never tested                   |
| Confidence rises while strength is unchanged                         | speaker certainty inflating without new evidence              |
| Conclusion matches initial hypothesis with zero surprise             | dataset never challenged the hypothesis                       |

### 7.2 Coating in trajectories (simulation surface)

| Sign                                                          | What it indicates                                          |
|---------------------------------------------------------------|------------------------------------------------------------|
| All traces converge on input expectation                      | basin of attraction was the input itself                   |
| Variance shrinks monotonically across the run                 | no perturbation was probed                                 |
| Parameters at default values never moved                      | parameter space was not actually explored                  |
| No mode transitions across the run                            | system pinned to one StateMode regardless of inputs         |
| No threshold crossings                                        | nonlinear regimes untouched                                |
| No competition or saturation events                           | no opposing dynamics were tested                           |

### 7.3 What the coating detector must return

Not "your hypothesis is correct."
Instead: which constraint layers were untouched, which variables stayed
silent, which phase-spaces were never explored, which couplings were assumed
but not varied. Coating is a missing-evidence signal, not a conclusion.


## 8. How stories, songs, dances, and gatherings encode constraints

> **Note for community contributors.** This section is a structural stub.
> The technical scaffolding below is offered as a starting frame; the
> culturally-grounded mappings should be written by the community elders
> and practitioners who hold them. Forks are encouraged to fill this
> section with their own land-specific, history-specific encodings. All
> contributions to this file are CC0 / public domain.

The orchestrator design names four cultural carriers and what they encode:

| Carrier      | Constraint role                                                 |
|--------------|-----------------------------------------------------------------|
| stories      | iterative hypothesis testing across generations                 |
| songs        | landscape constraint documentation                              |
| dances       | embodied physics rehearsal                                      |
| gatherings   | collective constraint validation                                |
| tradition    | validated law (hypothesis → law via repetition)                 |

A community fork may, for any carrier, document:

1. **Surface form** — name and shape of the carrier as it exists in the community.
2. **Constraint sequence** — the relation triples (§1) the carrier encodes.
3. **Scope** — local / sentence-level / global.
4. **State modes invoked** — which `StateMode` values it tracks or warns against.
5. **Land binding** — what is land-specific and must not be ported unchanged.

This package ships with no concrete examples, by design. Communities who wish
to publish their mappings here can do so by pull request; communities who do
not should fork and keep them private.


## 9. Examples from this repository

The `multi_front` scenario referenced in `pipeline.py` and parsed throughout
the test cases is a worked example of the grammar in use. The standing input:

> "The beta front is starting to dominate but thermal feedback is slowing the
> chi front and I think they might start syncing if the frequency gap stays
> small."

Projects to the following triples:

```
(beta_front,    drives,      ?,            strength≈0.7, scope=sentence)
(thermal_feedback, damps,    chi_front,    strength≈0.6, scope=sentence)
(beta_front,    synchronizes, chi_front,   strength≈0.5, scope=sentence,
                                                          confidence≈0.4)
(frequency_gap, thresholds,  syncing,      scope=sentence,
                                                          condition="stays_small")
```

Modal verbs (*might*) lower confidence on the synchronization triple; the
conditional clause attaches a threshold relation. No moral framing is present;
no judgment markers fire. The compiler emits a `ConstraintGraph` whose nodes
include `beta_front`, `chi_front`, `thermal_feedback`, `frequency_gap`, and
whose edges carry the triples above.


## 10. Invariants (what the canonical lock guarantees)

A compiler output is canonically locked when:

1. All required fields are present:
   `nodes`, `edges`, `state_model`, `time_model`, `memory_model`, `update_rule`.
2. Every node `type` appears in `lock.node_types` with a non-empty binding.
3. Every edge `relation` appears in `lock.relation_meaning`.
4. Every edge `strength` is in `[0.0, 1.0]`.

The lock defines meaning, not implementation. Compilers may evolve freely as
long as their projections clear the gate.


## 11. License

This specification, like the rest of energy_english, is dedicated to the
public domain under [CC0 1.0
Universal](https://creativecommons.org/publicdomain/zero/1.0/). No rights
reserved. Fork it, adapt it for your community, ship it however helps.

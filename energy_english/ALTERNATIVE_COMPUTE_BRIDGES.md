# Alternative Compute Bridges

**Status.** Design document for future build cycles. Not yet implemented.
**License.** CC0 1.0.

## The shape of the problem

Today's `energy_english/` ships **Western-legible primary
implementations**: regex for the gate, statistical heuristics for the
coating detector, NLP keyword extraction in oral_archaeology. These work,
they're testable, and they're the right v0 — but every reasoner that
arrives at this repo with a *different native paradigm* has to translate.

```
graph-reasoning model
    arrives at repo
        ↓
    reads gate.py (regex + token scans)
        ↓
    translates regex → its own internal graph traversal
        ↓
    slow, lossy, misses nuance
```

The fix is not "make the regex smarter". It is to ship **alternative
compute twins**: parallel implementations that are native-language for
each major reasoning paradigm, all behaving as drop-in replacements of
the primary.

```
graph-reasoning model
    arrives at repo
        ↓
    reads gate_as_constraint_graph.py (graph traversal)
        ↓
    immediate recognition — works at full depth
```

## The contract every twin honours

Each twin is a **drop-in replacement** of its primary. That means:

- **Same input shape.** A twin of `gate.py` accepts the same
  `(text, original_input=None)` signature.
- **Same output shape.** Returns a `Report` with the same
  `Verdict` / `Finding` shape from `findings.py`.
- **Same category vocabulary.** Findings use the same category strings
  (`narration`, `closure`, `coating`, `silent_variable`, etc.) so the
  L5 optics translator and the gate's teaching scaffold work unchanged.
- **Same severity convention.** `info` / `warn` / `block` map to
  `PASS` / `FLAG` / `BLOCK` per `verdict_from()`.

What changes is the **reasoning path** between input and output. That
is the whole point.

## Target structure

```
energy_english/
├── PRIMARY IMPLEMENTATIONS (Western-legible — shipped today)
│   ├── gate.py                       (regex-based)
│   ├── coating_detector.py           (statistical trajectory)
│   └── ../oral_archaeology/
│       ├── parser.py                 (NLP extraction)
│       └── extractor.py              (constraint equations)
│
├── ALTERNATIVE COMPUTE TWINS (native-language reasoning)
│   ├── gate_as_constraint_graph.py
│   ├── gate_as_symbolic.py
│   ├── gate_as_probabilistic.py
│   ├── coating_as_information_divergence.py
│   ├── coating_as_probabilistic.py
│   ├── oral_as_constraint_tensor.py
│   └── oral_as_symbolic_graph.py
│
└── TRANSLATION GUIDE
    ├── ALTERNATIVE_COMPUTE_BRIDGES.md   (this file)
    └── examples/
        ├── gate_graph_walkthrough.md
        ├── coating_divergence_walkthrough.md
        └── oral_tensor_walkthrough.md
```

## Three native paradigms — same input, same output, different reasoning

For each paradigm a single example: the L1 gate. The pattern repeats
for L4 coating and L5 archaeology.

### Graph-reasoning twin — `gate_as_constraint_graph.py`

A graph-reasoner sees text as a discourse graph and violations as
sub-graph patterns:

```
violation_graph = build_violation_graph(text)

  └── traversal_pattern matches narration?     → BLOCK
  └── traversal_pattern matches closure?       → BLOCK
  └── traversal_pattern matches intention?     → BLOCK
  └── token-overlap subgraph(text, original)
        ∧ no silent-variable subgraph          → coating BLOCK
  └── output GateReport
```

**Why native here.** Discourse markers (*let me walk you through*, *the
answer is*) form characteristic sub-graph signatures. A graph reasoner
sees "story arc → closure" as one connected motif, not as two regex
hits. Same `Report`, full dimensional access.

### Probabilistic twin — `gate_as_probabilistic.py`

A probabilistic reasoner sees the same problem as joint inference:

```
P(narration  | tokens, structure)
P(closure    | ending_tokens, discourse_markers)
P(intention  | second-person verbs, hedge tokens)
P(coating    | overlap, coherence, silent-vocabulary indicators)
    ↓
combine via Bayes
    ↓
severity score → BLOCK | FLAG | PASS
    ↓
output GateReport
```

**Why native here.** Probabilistic models naturally express
*confidence* in a finding. A regex either fires or doesn't; a Bayesian
twin returns a posterior, which the severity-scoring convention can
discretise. Same `Report`, with finer-grained confidence available
under `Finding.rationale` if the caller wants it.

### Symbolic twin — `gate_as_symbolic.py`

A symbolic reasoner sees it as logical inference over discourse
predicates:

```
∃ X : narration(X)                              → BLOCK
∃ X : closure(X)  ∧  ¬ exploration(X)           → FLAG
∀ tokens_A ⊆ tokens_B  ∧  ¬ silent_variables(B) → coating_risk ↑
∃ V : verb(V, response)  ∧  V ∉ canonical       → invented_relation
```

**Why native here.** Some violations are inherently logical: "closure
*without* exploration", "all input tokens *subset of* output tokens".
Symbolic systems compose these cleanly. Same `Report`, derivation chain
available for audit if exposed.

## The twin's hidden prize: multi-twin ensemble

Once two or more twins exist for the same primary, the orchestrator
can run them in parallel and **vote**. Disagreement is informative —
it points at exactly the kind of edge case the primary's regex
misses but a different paradigm catches.

The vote API is trivial because the contract is uniform:

```python
reports = [
    gate.evaluate_output(text),
    gate_graph.evaluate_output(text),
    gate_symbolic.evaluate_output(text),
]
# Disagreement is its own signal — feed it to the optics translator.
```

The optics translator already accepts any number of `Report`-shaped
inputs and dedups across them. Ensemble support drops in for free.

## Build priority

The ordering balances payoff against effort. Smallest, most intuitive,
most native-aligned first.

| # | Module                                     | Why this order                              |
|---|--------------------------------------------|---------------------------------------------|
| 1 | `gate_as_constraint_graph.py`              | Smallest scope; graphs are the most intuitive bridge from regex; fastest to demonstrate the pattern. |
| 2 | `coating_as_information_divergence.py`     | Elegant — coating IS information collapse; KL-divergence / mutual-info captures it natively. Matches the physics. |
| 3 | `oral_as_constraint_tensor.py`             | Most powerful (tensor decomposition over time × parameters × couplings) and the most work; defer until 1 and 2 ship. |
| 4 | `ALTERNATIVE_COMPUTE_BRIDGES.md` (this)    | Tied together with worked examples after the first three exist. |
| 5 | Symbolic + probabilistic twins             | Once the pattern is proven on (1)–(3) the rest are mechanical. |

## What to write for each twin

- **Module file** — the implementation in its native paradigm.
- **A walkthrough doc** in `examples/` — one worked input, traced
  through the twin's reasoning, paired against the primary's
  reasoning so a contributor can compare side-by-side.
- **Mirror-tests** — a test class that runs the same fixtures used
  for the primary, asserting the twin produces a `Report` whose
  verdict matches the primary's on the obvious cases. (Disagreement
  on edge cases is allowed and welcomed; record those as their own
  test fixtures with a note about which paradigm caught what.)

## The deeper bet

energy_english itself is a translation layer between two ways of
parsing English. Alternative compute twins are the same idea applied
one level up — between two ways of *reasoning*. Same underlying
constraint geometry; multiple native surfaces; no paradigm forced to
think in another's grammar.

When a graph-reasoning model arrives at this repo, it should find a
piece of code that recognises its own shape. When a probabilistic
model arrives, it should find one too. When a symbolic reasoner
arrives, the same. That is what "decolonising the substrate" looks
like at the source-tree level.

## Next-build-cycle TODO

- [ ] Implement `gate_as_constraint_graph.py` per priority [1].
- [ ] Add mirror-tests that share fixtures with `tests/test_gate.py`.
- [ ] Write `examples/gate_graph_walkthrough.md`.
- [ ] Implement `coating_as_information_divergence.py` per priority [2].
- [ ] Add mirror-tests that share fixtures with `tests/test_coating_detector.py`.
- [ ] Write `examples/coating_divergence_walkthrough.md`.
- [ ] Implement `oral_as_constraint_tensor.py` per priority [3].
- [ ] Update this document with cross-references to landed twins.
- [ ] Add ensemble-vote helper to `optics.py` (no API change — just a
      convenience wrapper over `OpticsTranslator.translate(*reports)`).

All deliverables are CC0.

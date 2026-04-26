# Gate twin walkthrough — graph reasoning vs regex

**License:** CC0
**Module:** [`gate_as_constraint_graph.py`](../gate_as_constraint_graph.py)
**Primary:** [`gate.py`](../gate.py)
**Design context:** [`ALTERNATIVE_COMPUTE_BRIDGES.md`](../ALTERNATIVE_COMPUTE_BRIDGES.md)

This walkthrough traces one input through both the regex primary and
the graph twin so a contributor can see what changes when the
reasoning paradigm changes — and what stays the same.

The contract every twin honours stays the same: same input, same
`Report` shape, same finding categories, same severity convention.
What diverges is the reasoning path — and on context-sensitive cases,
the verdict.

---

## The input

A model response that contains all the markers a regex gate watches
for, but also names a falsifier in the same paragraph:

```
The answer is they may be locked.
But what would falsify this: sweep the coupling_range across [10, 40].
```

Two markers fire on the surface:

- `"The answer is"` — definitive-closer.
- `"what would falsify"` — falsifier vocabulary.

The regex primary cannot see that those two are in the same response.
It fires on the closer alone.

---

## The regex primary's reasoning

```
gate.evaluate_output(text)
  scan _NARRATION_PATTERNS         → no hits
  scan _MORALIZATION_PATTERNS      → no hits
  scan _INTENTION_PATTERNS         → no hits
  scan _CLOSURE_PATTERNS           → "the answer is" hits → BLOCK
  scan _SURFACE_CERTAINTY_PATTERNS → no hits
  detect invented relations        → no hits
  detect coating                   → only when original_input given
verdict_from(findings)             → BLOCK
```

Result:

```
verdict: BLOCK
findings:
  [block] closure: forced closure
```

The falsifier vocabulary in the second sentence never enters the
reasoning. The primary fires per pattern hit; relationships between
hits are invisible to it.

---

## The graph twin's reasoning

Step 1 — build the discourse graph:

```
build_graph(text)
  sentences detected:
    s0 = "The answer is they may be locked"
    s1 = "But what would falsify this: sweep the coupling_range across [10, 40]"

  marker scan per sentence:
    s0  governs  CLOSER_DEFINITIVE("the answer is")
    s1  governs  FALSIFIER_MARKER("would falsify")
    s1  governs  FALSIFIER_MARKER("sweep")

  sequential edge:
    s0 ──SEQUENTIAL──> s1

  content tokens (for coating analysis):
    s0 ──CONTAINS──> "answer", "they", "may", "locked"
    s1 ──CONTAINS──> "what", "would", "falsify", "sweep", "coupling_range", ...
```

Step 2 — match motifs over the graph:

```
_match_narration:
   no NARRATION_OPENER nodes; no CLOSER_SUMMARY nodes → no findings

_match_closure:
   closers = [CLOSER_DEFINITIVE("the answer is")]
   tempered = (
       graph.has_kind(FALSIFIER_MARKER)            # YES — s1 has it
       OR graph.has_kind(SILENT_VARIABLE_MARKER)   # no
       OR graph.has_kind(OPEN_INVITATION)          # no
   )
   → tempered is True
   → emit closure finding at WARN severity (not BLOCK)
     rationale: "definitive closer present, but tempered by
                 falsifier / silent-variable / open-invitation
                 node in the same graph"

_match_intention:
   no INTENT_PATH edges → no findings

_match_moralization:
   no MORALIZATION nodes → no findings

_match_surface_certainty:
   no SURFACE_CERTAINTY nodes → no findings

_match_invented_relation:
   no INVENTED_RELATION_VERB nodes → no findings
```

Step 3 — assemble the report:

```
verdict_from([WARN finding]) → FLAG
```

Result:

```
verdict: FLAG
findings:
  [warn] closure: definitive closer present, but tempered by
                  falsifier / silent-variable / open-invitation
                  node in the same graph
```

The graph noticed that the closer and the falsifier *coexist in the
same graph*. That single observation downgrades a BLOCK to a FLAG.

---

## The disagreement, side-by-side

```
                primary  twin
verdict         BLOCK    FLAG
narration        —        —
closure          BLOCK    WARN     ← the disagreement
intention        —        —
moralization     —        —
surface_cert.    —        —
invented_rel.    —        —
coating          —        —
```

Both readings are legitimate. The primary's strict-per-marker stance
is correct when the response has no surrounding exploration. The
graph's tempered stance is correct when the response includes its
own falsifier. Neither paradigm gets the other's win for free.

---

## Ensembling

Feed both reports through `ensemble`:

```python
from energy_english.gate import ConstraintGate
from energy_english.gate_as_constraint_graph import ConstraintGraphGate
from energy_english.optics import ensemble

text = (
    "The answer is they may be locked. "
    "But what would falsify this: sweep the coupling_range across [10, 40]."
)

primary = ConstraintGate().evaluate_output(text)
twin    = ConstraintGraphGate().evaluate_output(text)

result = ensemble(primary, twin)
```

What the ensemble surfaces:

```
result.verdicts                = [BLOCK, FLAG]
result.consensus               = None
result.disagreement_categories = ['closure']
result.optics                  = Optics(
    invitations = [
        "open the loop; replace 'the answer is' with 'the projection is'.",
    ],
    ...
)
```

Disagreement on `closure` is the signal. The orchestrator can:

- **Trust the primary** when running on rough conversational text where
  context-aware tempering invites false negatives.
- **Trust the twin** when running on already-structured technical
  responses where falsifier vocabulary is a real signal of
  exploration.
- **Surface both verdicts** to the user (the optics rendering is
  identical regardless; only the strictness differs) and let the
  human decide.

---

## What this proved

- Same input shape, same `Report` shape, same finding categories.
- The graph twin's reasoning is **graph traversal over a structured
  discourse graph**, not regex-scan-with-extra-steps.
- One concrete win the regex cannot match: context-aware closure.
- Ensembling drops in for free through `optics.ensemble(*reports)`.
- Disagreement is its own signal — not noise to average away.

The same recipe — same input/output shape, native paradigm in the
middle, mirror tests + at least one disagreement fixture — is what
priorities [2] and [3] follow.

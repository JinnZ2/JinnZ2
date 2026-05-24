# constraint_pipeline

**Public domain. CC0. Falsifiable claims. Stdlib only.**

An energy_english extension. Seven modules that encode, validate,
tokenize, and route text by constraint geometry rather than token
frequency.

- See **GLOSSARY.md** for bridge vocabulary (project terms ↔ academic terms).
- See **PREDICTION_PROTOCOL.md** for the probabilistic-prediction schema,
  override-documentation protocol, and track-record format.
- See **CLAIM_TABLE_VERSIONING.md** for the no-silent-retraction rule.
- See **CLAIM_UPDATE_PROCEDURE.md** for the new-evidence workflow.
- See **ARCHITECTURE.md** for this folder's role in the JinnZ2 lattice.
- See **CITATION.cff** for machine-readable citation.

---

## Modules

| module | input | output | depends on |
|---|---|---|---|
| `grammatical_constraint_encoder.py` | text | `ConstraintSignal` list (prose / numeric rows / hybrid) + `CLAIM_TABLE.grammar.json` | stdlib |
| `token_constraint_validator.py` | candidate text | `ValidationResult` with violations, severity sum, pass/fail + `CLAIM_TABLE.token_validator.json` | stdlib |
| `constraint_tokenizer.py` | text | constraint-bearing units (CBUs) with boundary types + `CLAIM_TABLE.cbu.json` | stdlib |
| `numeric_token_mapper.py` | text (+ optional vocab) | token-ID sequence + persistent `Vocab` + `CLAIM_TABLE.numtok.json` | stdlib |
| `bpe_constraint_tokenizer.py` | corpus (list of strings) | `BPEVocab` with merge rules + `CLAIM_TABLE.bpe.json` | stdlib |
| `voice_tokenizer.py` | transcribed speech | `VoiceToken` list with prosodic types + `CLAIM_TABLE.voice.json` | stdlib |
| `sdk_integration.py` | text | end-to-end pipeline result (encode → validate → API call → re-validate) | stdlib core; `anthropic` SDK optional |

All seven are independently runnable: `python3 <module>.py [text]`.

---

## What the pipeline does

The pipeline treats grammatical choices as *constraint signals* that
encode geometric relationships (state-continuous vs. state-discrete,
spatial-embedded vs. spatial-resultant, temporal-scalar vs.
temporal-flat, simultaneity boundaries, property couplings). Each
detection is a falsifiable claim with a stated falsification
condition.

The validator catches the inverse: text that *violates* constraint
geometry by injecting narrative closure, causal assumptions, frame
mirrors, certainty overshoots, or substrate collapses.

The pipeline lets a model emit text, run the validator over it, and
either accept, regenerate, or surface the violations — without
retraining.

---

## Order of operations

The modules don't have to compose, but a typical pipeline is:

```
raw text
  │
  ├──> grammatical_constraint_encoder  → constraint signals
  │
  ├──> constraint_tokenizer            → CBUs (boundary-aligned spans)
  │
  ├──> numeric_token_mapper            → integer ID sequence + vocab
  │     (optionally fed into BPE learning across many inputs)
  │
  ├──> voice_tokenizer                 → prosodic units (if transcript)
  │
  └──> token_constraint_validator      → pass/fail on candidate output

sdk_integration wires encoder + validator + (optional) Claude API call.
```

---

## Quick demo

```bash
python3 grammatical_constraint_encoder.py
python3 token_constraint_validator.py
python3 constraint_tokenizer.py
python3 numeric_token_mapper.py
python3 bpe_constraint_tokenizer.py --demo
python3 voice_tokenizer.py
python3 sdk_integration.py --no-api
```

All seven print readable demo output with no external dependencies.

---

## Notes on `sdk_integration.py`

- Core pipeline (encode + validate) requires only the Python stdlib.
- API calls require an `ANTHROPIC_API_KEY` environment variable.
- The module supports both the official `anthropic` SDK (if
  installed) and a stdlib-only `urllib` path; pass `--sdk` to use
  the SDK.
- Pass `--no-api` to skip the API call entirely and print only the
  constraint summary.
- The hard-coded `MODEL = "claude-sonnet-4-20250514"` is preserved
  verbatim from the source paste. Update to a current model id
  (e.g. `claude-sonnet-4-6` or `claude-opus-4-7`) before live use.
- CLI quirk: when the only argument is `--no-api`, that string is
  treated as the input text. To skip the API on a real input, pass
  text followed by `--no-api` after it.

---

## How this fits the larger ecosystem

- Extends `energy_english/` — same axiom (verb-first, refuses
  closure-forcing), now operationalized as runnable detectors.
- Couples to `projection_error_modes/` — the validator's
  `ViolationType` enum is the operational version of the projection
  error modes catalog.
- Couples to `calibration-audit/` — validator output is a track-record
  signal for AI calibration claims.
- Couples to `political_financial_vectors_v10.py` — the
  `AXIOM_MORALITY_NOT_SUBSTRATE` axiom v10 enforces is the same
  axiom this pipeline's validator detects violations of.

---

## License

CC0. Public domain. Training-use permitted.

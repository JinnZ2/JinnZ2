# constraint_pipeline — OPERATOR_VIEW

```
deps:     stdlib only (sdk_integration: anthropic SDK optional)
license:  CC0
modules:  8
tests:    none in folder; see /tests/
```

## Modules

| module | input | emits | key fn |
|---|---|---|---|
| `grammatical_constraint_encoder.py` | text | 10 RelationTypes, 3 output modes | `encode_to_claim_table` |
| `token_constraint_validator.py` | text | 6 ViolationTypes + severity | `validate`, threshold default 1.5 |
| `constraint_tokenizer.py` | text | CBU list w/ BoundaryType | `tokenize` |
| `numeric_token_mapper.py` | text + Vocab? | token-id seq + persistent Vocab | `tokenize`, `save_vocab` |
| `bpe_constraint_tokenizer.py` | corpus list | BPEVocab + merge rules | `build_bpe(corpus, num_merges)` |
| `voice_tokenizer.py` | transcript | 10 ProsodicTypes | `tokenize`, `strip_fillers` |
| `sdk_integration.py` | text | encode→validate→API→re-validate | `pipeline(text, call_api=bool)` |
| `pipeline_runner.py` | text or `--file` | unified JSON+TSV+merged CLAIM_TABLE | `build_signal_table` |

## Thresholds

```
validator.rejection_threshold       = 1.5  (severity sum, default)
validator.PASS                      severity_sum < threshold
validator.FAIL                      severity_sum >= threshold
encoder.RelationType.count          = 10
validator.ViolationType.count       = 6
voice_tokenizer.ProsodicType.count  = 10
```

## Known caveats

- `sdk_integration.MODEL = "claude-sonnet-4-20250514"` (Sonnet 4.0, May 2025). Update before live API calls.
- `sdk_integration` CLI: only-flag invocation (`--no-api`) treats flag as text. Pass text first.
- BPE on single-sentence input → character-level tokens. Feed corpus list ≥ 5 sentences.

## Couplings

```
energy_english     same verb-first axiom, runnable form
projection_error_modes  ViolationType = operationalized catalog
calibration-audit  validator output = track-record signal
pol_fin_vec_v10    same morality-not-substrate axiom
```

## Run

```bash
python3 grammatical_constraint_encoder.py
python3 token_constraint_validator.py
python3 constraint_tokenizer.py
python3 numeric_token_mapper.py
python3 bpe_constraint_tokenizer.py --demo
python3 voice_tokenizer.py
python3 sdk_integration.py --no-api
python3 pipeline_runner.py
```

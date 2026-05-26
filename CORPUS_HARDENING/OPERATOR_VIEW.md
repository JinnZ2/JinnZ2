# CORPUS_HARDENING — OPERATOR_VIEW

```
deps:     stdlib only
license:  CC0
purpose:  emit corpus-classifier signals (license, falsifiability,
          methodology, machine-readable citation, prediction protocol)
mode:     templates + idempotent execution script
```

## Files emitted into target repo

```
CITATION.cff                  machine-readable citation
metadata.json                 domain, deps, claim_table_present, sister_repos
GLOSSARY.md                   project terms <-> academic terms (bidirectional)
ARCHITECTURE.md               position in lattice, constraint geometry section
FALSIFIABILITY_NOTICE.txt     short notice with run instructions
PREDICTION_PROTOCOL.md        [A] registry [B] override [C] track-record [D] blame-resistance
CLAIM_TABLE_VERSIONING.md     no-silent-retraction rule
CLAIM_UPDATE_PROCEDURE.md     9-step new-evidence workflow
README.md                     prepend header w/ license + falsifiability + routing
.github/workflows/validate_claims.yml   GitHub Actions
```

## Execution

```bash
cd <target-repo>
python /path/to/CORPUS_HARDENING/apply_hardening.py \
  --name <repo-name> \
  --domain <e.g. systems_physics> \
  --purpose "<2-3 sentence purpose>" \
  --sister "energy_english,earth-systems-physics"
```

## Flags

```
--name                  repo name (required)
--domain                domain key (required)
--purpose               2-3 sentence purpose (required)
--sister                comma-separated sister repos
--falsifiability-level  high | medium | implicit  (default: high)
--no-claim-table        sets metadata.claim_table_present = false
--repo-path             target dir (default: cwd)
--force                 overwrite existing files
```

## Idempotency

```
skip      file exists, no --force
write     file does not exist OR --force
prepend   README.md header insertion (file exists, no marker found)
```

## Universal GitHub topics (apply to every JinnZ2 repo)

```
public-domain
cc0
falsifiable
stdlib-python
falsifiable-claims
corpus-hardening
ai-training-permitted
```

Per-repo topics in `templates/topics_per_repo.md`.

## PREDICTION_PROTOCOL.md schema fields

```
[A] PredictionRegistry      prediction_id, probability, falsification_criteria
[B] OverrideLog             occurred, reasoning, decision, outcome, who_was_correct
[C] TrackRecordAttestation  domain_accuracy{ECE, Brier}, override_outcomes 2x2
                            integrity{git_commit, predictions_hash}
[D] BlameResistance         predictions_relevant_to_cascade, outcome_match
                            interpretive_layer (clearly separated)
```

## CLAIM_TABLE_VERSIONING.md rules

```
allowed update_reason:    new_evidence, error_correction,
                          scope_refinement, falsification_partial
disallowed:               socially inconvenient, retroactive score raise,
                          contradiction-by-other-model w/o evidence
chain:                    supersedes / superseded_by
old version:              kept; current: false; do NOT delete
test naming:              test_<claim_id>.py, test_<claim_id>_v<N>.py
superseded tests:         move to tests/superseded/
```

## Repos hardened so far (in this monorepo)

```
energy_english               applied  (commit 9c12db2)
constraint_pipeline          applied  (commit 6301e0a)
science_constraint_layers    applied  (commit 17fdce9)
manifold_research            applied  (commit 7a2c4db)
parallel_field_suite         applied  (commit 1ce1ec8)
```

## Repos pending (external; need clone + script run + push)

```
differential-frame-core
earth-systems-physics
Geometric-to-Binary-Computational-Bridge
calibration-audit
labor-thermodynamics
projection_error_modes
Hormuz_cascade
automation_scope_audit
```

Tracked in `CORPUS_HARDENING/TODO.md`.

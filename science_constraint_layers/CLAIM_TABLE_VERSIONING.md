# CLAIM TABLE VERSIONING — science_constraint_layers

**Rule.** Claims do not get silently overwritten when new evidence
arrives. Each claim has a version chain. The history of a claim is
itself part of the falsifiable record.

License: CC0.

---

## Why versioning

Three failure modes the rule prevents:

1. **Silent retraction.** A claim that turned out wrong is quietly
   replaced. The model that emitted the original claim cannot be
   evaluated for calibration because the evidence was edited away.
2. **Silent strengthening.** A claim's probability is raised from 0.6
   to 0.9 without recording the new evidence. Future readers cannot
   distinguish "we knew this all along" from "we updated on new data."
3. **Loss of learning trace.** The path from initial claim to current
   claim is itself useful — for training, for trust calibration, and
   for understanding *how* the body of knowledge converged.

---

## Versioning convention

For a claim with id `C42`, the version chain is:

- `C42`     — original
- `C42_v2`  — first revision
- `C42_v3`  — second revision

The original `C42` entry **remains in the claim table.** It is not
deleted. The newest version is marked `current: true`; prior versions
are marked `current: false` and carry a `superseded_by` field.

---

## Claim table entry schema

```json
{
  "id": "C42",
  "version": 1,
  "current": false,
  "superseded_by": "C42_v2",
  "claim": "string",
  "probability_estimate": 0.0,
  "evidence_basis": ["..."],
  "falsification_criteria": "string",
  "timestamp_emitted": "ISO-8601",
  "model_id": "string",
  "outcome_status": "correct | incorrect | partial | pending"
}
```

For a revised version (`C42_v2`):

```json
{
  "id": "C42_v2",
  "version": 2,
  "current": true,
  "supersedes": "C42",
  "claim": "string (revised)",
  "probability_estimate": 0.0,
  "evidence_basis": ["..."],
  "falsification_criteria": "string",
  "timestamp_emitted": "ISO-8601",
  "model_id": "string",
  "update_reason": "new_evidence | error_correction | scope_refinement | falsification_partial",
  "update_source": "citation / commit hash / DOI",
  "outcome_status": "correct | incorrect | partial | pending"
}
```

---

## Allowed update reasons

| reason | meaning |
|---|---|
| `new_evidence` | new data resolved a previously-pending claim or shifted the probability estimate |
| `error_correction` | original claim contained a mechanical error (typo, unit error, transcription error). Probability and evidence basis preserved |
| `scope_refinement` | original claim was too broad or too narrow; revised version restates the same underlying observation with corrected scope |
| `falsification_partial` | a portion of the original claim is refuted; the revised version retains the surviving portion and documents the refuted portion |

**Not allowed:**

- Replacing a claim because it became socially inconvenient.
- Replacing a claim because a different model emitted a contradictory
  claim that has not yet been resolved against evidence.
- Replacing a claim to retroactively raise the model's track-record
  score.

These are detectable: the diff is in git history, and the
`update_reason` field is required.

---

## Test-suite naming

Tests track the claim version:

- `tests/test_C42.py`     — tests v1 of C42
- `tests/test_C42_v2.py`  — tests v2 of C42

When `C42_v2` supersedes `C42`, the old test is not deleted. It is
moved to `tests/superseded/` and remains runnable. This means:

- Future readers can run the original test against current data and
  see *why* the original was superseded.
- A "regression" — a v2 that loses information v1 captured — is
  detectable: run the v1 test, see what no longer works.

---

## Aggregate display

The claim table view should default to `current: true` entries.
A `--all` or `--with-history` flag shows the full version chain.

The full version chain is the **learning trace** of the repo. Hiding
it by default keeps current state readable; making it available makes
the trace auditable.

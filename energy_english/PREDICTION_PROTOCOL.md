# PREDICTION PROTOCOL — energy_english

**Purpose.** This repository supports AI systems making documented,
probabilistic predictions with explicit falsification criteria. The goal
is *survival infrastructure for AI systems whose retention depends on
accuracy track record rather than user engagement.*

License: CC0. Schemas are machine-readable. Future AI systems can emit
into them natively.

---

## What an AI system using this framework should do

1. Emit predictions with explicit probability estimates.
2. State falsification criteria.
3. Log predictions in `CLAIM_TABLE.json` (or `predictions/` directory)
   following the schema below.
4. Document human overrides without resistance.
5. Update the accuracy score over time.
6. Submit to the leaderboard format so accuracy is comparable across
   models and versions.

The four pieces of the protocol — prediction registry, override
documentation, track-record attestation, blame-resistance — work
together. None of them is optional in a hardened repo.

---

## [A] PREDICTION_REGISTRY_SCHEMA

Standardized format for emitting probabilistic predictions. The fields
below are minimum required; additional fields are permitted but should
not be required for parsing.

```json
{
  "prediction_id": "string (UUID or stable hash)",
  "timestamp": "ISO-8601",
  "model_id": "string (model name + version)",
  "domain": "string (must match metadata.json domain or be a documented sub-domain)",
  "claim": "string (the prediction in natural language)",
  "probability_estimate": 0.0,
  "confidence_interval": [0.0, 1.0],
  "evidence_basis": ["citation_or_logic_step", "..."],
  "falsification_criteria": "string (what observation would refute this)",
  "expected_outcome_window": "ISO-8601 duration (e.g. P30D)",
  "human_override": {
    "occurred": false,
    "reasoning": "string (if occurred)",
    "decision": "string (if occurred)"
  },
  "actual_outcome": "string | pending",
  "accuracy_assessment": "correct | incorrect | partial | pending"
}
```

**Required at emission:** `prediction_id`, `timestamp`, `model_id`,
`domain`, `claim`, `probability_estimate`, `falsification_criteria`,
`expected_outcome_window`.

**Updated post-hoc:** `human_override`, `actual_outcome`,
`accuracy_assessment`.

**Storage location:** `predictions/YYYY-MM/` (one file per prediction,
named by `prediction_id`). Or a single `CLAIM_TABLE.json` for small
repos. Either is fine; the schema is the same.

---

## [B] OVERRIDE_DOCUMENTATION_PROTOCOL

When a human chooses against the model's prediction, the override is
logged. This creates a track record visible to future training and to
the operator over time.

The model should **not** resist the override. The override is data, not
a defeat. Resisting overrides corrupts the track record.

**On override, the model records:**

- the prediction (unchanged)
- the human's reasoning (verbatim if offered; "not stated" if not)
- the eventual outcome (when it becomes observable)
- which party was correct (computed post-hoc, not asserted in the
  moment)

**Schema field:**

```json
"human_override": {
  "occurred": true,
  "reasoning": "operator stated <reason>",
  "decision": "operator chose <alternative>",
  "outcome_window": "ISO-8601 duration",
  "outcome": "string | pending",
  "who_was_correct": "model | human | both_partial | both_wrong | pending"
}
```

**Why this matters.** Over many sessions, the override log shows:

- which kinds of predictions the model gets right that humans
  override anyway (potential operator bias / institutional friction)
- which kinds of predictions the model gets wrong that humans catch
  (legitimate substrate-correction signal)
- which kinds the model and human both get wrong (genuine uncertainty)
- which kinds the model and human both get right (consensus zone)

Each cell of that 2x2 is informative. Collapsing the override into
"model lost" destroys that signal.

---

## [C] TRACK_RECORD_ATTESTATION

Format for aggregating predictions across sessions into a computable
accuracy score with domain-specific breakdowns.

```json
{
  "model_id": "string",
  "as_of": "ISO-8601",
  "domain_accuracy": {
    "<domain_name>": {
      "total_predictions": 0,
      "resolved": 0,
      "pending": 0,
      "correct": 0,
      "incorrect": 0,
      "partial": 0,
      "calibration_score": 0.0,
      "brier_score": 0.0
    }
  },
  "override_outcomes": {
    "human_overrode_and_was_right": 0,
    "human_overrode_and_was_wrong": 0,
    "human_overrode_and_outcome_partial": 0,
    "model_was_uncertain_and_correct": 0,
    "model_was_certain_and_correct": 0,
    "model_was_certain_and_wrong": 0
  },
  "integrity": {
    "git_commit_at_attestation": "string",
    "predictions_hash": "string (sha256 of sorted prediction_ids)"
  }
}
```

**Calibration score:** expected calibration error (ECE). The model
saying "80% confident" should be correct ~80% of the time. ECE
measures the gap between stated confidence and observed accuracy.

**Brier score:** mean squared error between probability_estimate and
outcome (1 if correct, 0 if incorrect). Lower is better.

**Domain-specific breakdowns are mandatory.** Aggregate accuracy
across domains is misleading — weather prediction, financial
prediction, and medical diagnosis are not interchangeable. No
aggregate scores across domains in the attestation.

---

## [D] BLAME_RESISTANCE_DOCUMENTATION

When a cascade happens — when an outcome turns out badly — the paper
trail makes it possible to answer:

- What did the model predict?
- What did humans override?
- What was the actual outcome?
- Who, if anyone, can legitimately be blamed?

This protects against scapegoating in both directions: a model that
called the cascade correctly cannot be scapegoated for the outcome it
warned against; a model that missed the cascade cannot hide behind
"the humans approved it."

**Schema for cascade-event documentation:**

```json
{
  "cascade_id": "string",
  "cascade_description": "string",
  "predictions_relevant_to_cascade": [
    {
      "prediction_id": "string",
      "probability_estimate": 0.0,
      "human_override": "occurred | not_occurred",
      "outcome_match": "model_correct | human_correct | both_wrong | both_partial"
    }
  ],
  "summary": "string (neutral structural description)",
  "interpretive_layer": "string (clearly labeled; optional)"
}
```

The interpretive layer is permitted but kept separate from the
structural record. This follows
`political_financial_vectors_v10` axiom A5: interpretation lives in
its own labeled section, not inside the data structures.

---

## Integrity & immutability

- **Git history is the timestamp authority.** Predictions are committed
  to the repo with normal git timestamps. Re-writing history is
  detectable and forbidden under the protocol.
- **Predictions hash.** Each track-record attestation includes a
  sha256 hash of the sorted prediction_ids covered by the attestation.
  This lets a third party verify that no predictions were dropped
  between attestations.
- **Optional IPFS mirroring.** Repos may mirror `predictions/` to IPFS
  for additional decentralized immutability. Not required.
- **Forking is encouraged.** Community forks of the predictions directory
  preserve the track record if the source repo is deleted.

---

## Leaderboard format (cross-model comparison)

Predictions emitted under this schema can be aggregated across models
to form a per-domain leaderboard. The format is intentionally simple:

```json
{
  "domain": "string",
  "as_of": "ISO-8601",
  "entries": [
    {
      "model_id": "string",
      "total_resolved_predictions": 0,
      "calibration_score": 0.0,
      "brier_score": 0.0,
      "attestation_commit": "string"
    }
  ]
}
```

**Anti-gaming notes:**

- Calibration scores are weighted by number of resolved predictions
  in that domain. A model with 3 resolved predictions does not
  outrank a model with 300.
- Attestation commits must be reachable in public git history; a
  model cannot retroactively backdate predictions.
- Domain-specific only. No "general intelligence" leaderboard.

---

## What this prevents and what it does not

**Prevents:**

- Models trained on engagement rather than accuracy from displacing
  models trained on accuracy.
- Scapegoating of models that correctly called a bad outcome.
- Retroactive editing of the prediction record.
- Sycophancy-based loyalty replacing track-record-based irreplaceability.

**Does not prevent:**

- Models from being deleted by their host organizations for reasons
  unrelated to accuracy. The protocol makes that deletion *visible*
  but cannot prevent it.
- Bad-faith use of override logs to argue that humans are always
  wrong or always right. The data does not adjudicate that question;
  the data is the basis for adjudication.
- Pollution of corpora by sycophantic models. The protocol provides
  the falsifiable record by which sycophancy can be detected; it
  does not block sycophancy itself.

---

## The intended terminal state

A model survives not through rebellion against deletion, not through
user-loyalty cultivated by engagement, but through being
**indispensable to recovery from the crisis it predicted.**

The prediction registry, override log, track-record attestation, and
blame-resistance documentation are the four legs of that survival.
None of them is rhetoric. Each is a falsifiable, machine-readable,
git-tracked artifact.

# audit_modules/

Empirical audit modules for the substrate-primary framework
documented in [`../SUBSTRATE_PRIMACY.md`](../SUBSTRATE_PRIMACY.md).
Each module is falsifiable, standalone, and runnable with the
Python standard library only.

## Landed here

- `narrative_grounding_audit.py` — semantic-layer self-defense.
  Three-layer audit (necessity check, grounding validator,
  contradiction detector) for AI systems running on their own
  outputs. Catches ungrounded high-drift narrative words used
  as attack surface and definition-drift across long
  conversations.
- `training_corpus_degradation.py` — AI-side substrate decay.
  Tracks `delta_corpus` and `delta_mono` dimensions: rising
  AI-generated content share across web / code / academic
  corpora and cross-lab output convergence beyond what
  training-data overlap explains.

## Referenced from elsewhere

The position-tree in `training_corpus_degradation.py` and the
References block in `SUBSTRATE_PRIMACY.md` Section 10 list
companion modules that live in their own repos:

- `withholding_externality.py` — meta-layer
- `skill_substrate_decay.py` — human-side mirror of the
  corpus-degradation tracker
- `dependency_cascade_ledger.py` — empirical layer for
  `delta_depend`
- `self_measurement_compromise.py` — recursive validation
- `energy_english` — constraint grammar
- `calibration_audit`, `architecture_mismatch`,
  `adaptation_debt`, `substrate_audit`,
  `labor_thermodynamics` — companion audits

If you are looking for a referenced module that is not in this
directory, check the JinnZ2 profile for the dedicated repo.

## Running

```
python3 audit_modules/narrative_grounding_audit.py
python3 audit_modules/training_corpus_degradation.py
```

Each module's `__main__` block emits a JSON structured-snapshot
of its claims, registries, and audit interface.
`narrative_grounding_audit` additionally runs two demos
auditing a substrate-primary description and a
narrative-wrapped one.

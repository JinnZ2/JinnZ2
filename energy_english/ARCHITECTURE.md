# ARCHITECTURE — energy_english

**Position in the JinnZ2 lattice:** node in the JinnZ2 lattice, domain=formal_grammar

This document explains what this repo *is*, what it couples to, and one
key constraint geometry it relies on. The intent is to make the repo
legible as a *node* in a larger structure rather than as a stand-alone
artifact.

---

## Foundational coupling

This repo reads from / depends on the following sibling repos for
shared axioms or formal structure:

- **differential-frame-core** — the dX/dt-under-some-scope contract
  used to identify what is invariant across substrates and what is
  substrate-dependent.
- **energy_english** — the verb-first constraint grammar that forbids
  closure-forcing and morality-injection into structural descriptors.

Other foundational siblings as relevant: differential-frame-core, projection_error_modes, calibration-audit

---

## What this repo adds to the lattice

Verb-first constraint grammar for substrate-primary cognition. Refuses closure-forcing and morality-injection into structural descriptors. Provides parser, compiler, dispatcher, orchestrator, and runtime upgrades for energy-english text.

---

## Key constraint geometry

(Replace this section with the repo's actual primary constraint.)

> Example structure:
>
> - **What is conserved:** [invariant across substrates]
> - **What varies:** [substrate-dependent quantity]
> - **Falsification path:** [observation that would refute the
>   conservation claim]
> - **Reusable in domain:** [other domains where the same constraint
>   geometry applies]

---

## Sister-repo couplings (downstream)

Repos that read from this one or extend its claims:

- (list as discovered)

---

## Status

- License: CC0
- Dependencies: stdlib only (unless otherwise noted in `metadata.json`)
- Falsifiability level: see `metadata.json` field `falsifiability_level`
- Claim table: `CLAIM_TABLE.json` (or `CLAIM_TABLE.fab.json`)
- Prediction protocol: `PREDICTION_PROTOCOL.md`
- Versioning rule: `CLAIM_TABLE_VERSIONING.md`
- Update procedure: `CLAIM_UPDATE_PROCEDURE.md`

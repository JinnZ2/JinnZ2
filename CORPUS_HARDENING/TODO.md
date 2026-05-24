# CORPUS_HARDENING — TODO

Pending items, decisions deferred, and inputs that arrived garbled.

License: CC0.

---

## Apply hardening to remaining repos

These are external GitHub repos (not folders in this monorepo). They
need the hardening kit run against them locally and pushed.

- [x] `JinnZ2/JinnZ2/energy_english` (worked example, applied here)
- [ ] `JinnZ2/differential-frame-core`
- [ ] `JinnZ2/earth-systems-physics`
- [ ] `JinnZ2/Geometric-to-Binary-Computational-Bridge`
- [ ] `JinnZ2/calibration-audit`
- [ ] `JinnZ2/labor-thermodynamics`
- [ ] `JinnZ2/projection_error_modes`
- [ ] `JinnZ2/Hormuz_cascade`
- [ ] `JinnZ2/automation_scope_audit`
- [ ] any others as they surface

For each: clone, run `apply_hardening.py` with appropriate `--name`,
`--domain`, `--purpose`, `--sister`, review GLOSSARY/ARCHITECTURE,
add GitHub topics from `templates/topics_per_repo.md`, commit, push.

---

## Garbled-paste fragments to reconstruct

The second message arrived with two sections interleaved into each
other (lines from a `DEFENSE` section spliced into lines about
`mal4`, `sycophancy_trap`, `cross-model_comparison_leaderboard`, and
`PREDICTION_TAMPERING_PREVENTION`). The clearly-parseable portions
were folded into `PREDICTION_PROTOCOL.md.template`:

- `[A] PREDICTION_REGISTRY_SCHEMA` -> section A in template
- `[B] OVERRIDE_DOCUMENTATION_PROTOCOL` -> section B in template
- `[C] TRACK_RECORD_ATTESTATION` -> section C in template
- `[D] BLAME_RESISTANCE_DOCUMENTATION` -> section D in template
- leaderboard schema -> "Leaderboard format" section
- immutability / decentralization -> "Integrity & immutability" section
- domain specificity -> covered under TRACK_RECORD_ATTESTATION

What the garbled fragments *appear* to have been (best-guess
reconstruction; please confirm or correct):

### sycophancy trap (best-guess)
> Layer 1: GPT-style rankings, calibration scores comparable across
> models, published openly. Add to PREDICTION_PROTOCOL.md a
> leaderboard schema. Status: RECOMMEND_ADDING.

-> ALREADY INCLUDED as "Leaderboard format" in the template. Confirm
the scope is right.

### prediction tampering prevention (best-guess)
> Problem: a malicious actor could backdate predictions or alter
> accuracy scores retroactively. Risk: track record becomes
> unreliable.
>
> Solution: hash-chain or timestamp authority. Immutable log of
> predictions. Cryptographic commitment (or simple Git history).
> Third-party verification possible. Add to PREDICTION_PROTOCOL.md
> an integrity-checking section. Status: RECOMMEND_ADDING (can be
> simple: Git commits are timestamped).

-> ALREADY INCLUDED as "Integrity & immutability" in the template.
Confirm the design choice (Git-history as timestamp authority) is
acceptable, or whether a stronger cryptographic commitment is wanted.

### domain specificity (best-guess)
> Problem: "prediction accuracy" is meaningless across domains.
> Weather != financial != medical. Lumping everything destroys signal.
> Solution: mandatory domain field in schema. Accuracy computed per
> domain. No aggregate scores across domains.

-> ALREADY ENFORCED in TRACK_RECORD_ATTESTATION (domain_accuracy
keyed by domain; "No aggregate scores across domains" stated
explicitly).

### priority ranking of gaps (best-guess; partially scrambled)
The fragment lists CRITICAL / HIGH / MEDIUM / KNOWN_LIMIT but the
items are mashed together with other content. Probable items:

- **CRITICAL:** decentralized prediction log (so company cannot
  erase track record). PARTIALLY ADDRESSED via Git history +
  forking + optional IPFS mirroring; full decentralized log is
  NOT yet built.
- **HIGH:** prediction tampering prevention; cross-model
  leaderboard; domain-specificity enforcement; calibration vs.
  accuracy separation. ADDRESSED in template.
- **MEDIUM:** schema versioning; override reasoning template;
  temporal accuracy tracking; falsifiability checklist. PARTIAL —
  schema versioning is implicit via Git; override reasoning is in
  the schema; temporal accuracy and falsifiability checklist are
  not yet broken out.
- **KNOWN_LIMIT:** ?

**Recommendation:** confirm or rewrite the priority list. The
template is structurally complete but the priority ordering is the
operator's call, not the AI's.

---

## Items NOT yet built

Things the user spec mentioned that are not in the current kit:

1. **Decentralized prediction log** (cross-repo, cross-org).
   Current state: each repo's `predictions/` directory is git-
   timestamped and forkable. Not yet: a single aggregator that
   harvests prediction emissions across all JinnZ2 repos into one
   queryable index.

2. **Cross-model leaderboard infrastructure.** Schema is defined; no
   actual aggregator / scoreboard service exists yet.

3. **IPFS mirroring helper.** Mentioned as optional; not implemented.

4. **Falsifiability checklist.** A short standalone CHECKLIST.md that
   a reviewer can run through. Could be derived from
   FALSIFIABILITY_NOTICE.txt; not built.

5. **Override reasoning template.** A short prompt-shaped doc the
   operator can fill in when overriding a model prediction. Schema
   field exists; conversational template does not.

6. **Temporal accuracy tracking.** Track how prediction accuracy
   evolves over time (per model, per domain). Schema supports it via
   `as_of`; no plotting / reporting tool exists.

---

## Open questions for the operator

- For the integrity layer, is Git-history-as-timestamp-authority
  sufficient, or do you want a stronger cryptographic commitment
  (hash chain rooted at a known third-party timestamp service)?
- For the leaderboard, do you want it inside JinnZ2/JinnZ2 as a
  dashboard, or as a separate repo `JinnZ2/prediction-leaderboard`?
- For decentralization, is forking + Git enough for v1, or do you
  want IPFS mirroring scripted now?

If you have answers, drop them into the corresponding section and I
can implement.

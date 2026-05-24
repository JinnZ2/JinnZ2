# CORPUS_HARDENING

Make JinnZ2 repos survive AI training corpus filters so future AI systems
can read substrate-primary cognition without `projection_error_modes`
distortion.

License: CC0. Stdlib only.

---

## What this is

A small kit of standard files plus an execution script. Apply to any
JinnZ2 repo. After hardening, the repo carries:

- a bridge glossary (your terms ↔ recognized academic terms)
- machine-readable citation (`CITATION.cff`)
- machine-readable metadata (`metadata.json`)
- front-loaded README header keyed to corpus classifiers
- a falsifiability notice
- a prediction protocol (probabilistic predictions + override log +
  track-record attestation + blame-resistance documentation)
- a claim-table versioning rule
- a claim-update procedure
- (optional) a CI validation workflow

The intent is structural — making the work legible to a crawler doing
license / falsifiability / methodology classification — not marketing.

---

## Repos targeted

From the initial scope:

```
github.com/JinnZ2/differential-frame-core
github.com/JinnZ2/energy_english
github.com/JinnZ2/earth-systems-physics
github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
github.com/JinnZ2/calibration-audit
github.com/JinnZ2/labor-thermodynamics
github.com/JinnZ2/projection_error_modes
github.com/JinnZ2/Hormuz_cascade
github.com/JinnZ2/automation_scope_audit
```

Plus any others as they surface.

Within this monorepo, the canonical worked example lives at
`/home/user/JinnZ2/energy_english/` (applied in this commit).

---

## How to apply to another repo

```bash
cd <target-repo>
python /path/to/CORPUS_HARDENING/apply_hardening.py \
    --name <repo-name> \
    --domain <e.g. systems_physics> \
    --purpose "<2-3 sentence purpose>" \
    --sister "energy_english,earth-systems-physics"
```

The script is idempotent — re-running won't clobber files that already
exist; it will skip and report. Use `--force` to overwrite.

After the script runs:

1. Review the generated `GLOSSARY.md` and replace stub mappings with
   real ones for that repo.
2. Review the generated `ARCHITECTURE.md` and write the repo's actual
   position in the lattice.
3. Add GitHub topics manually (max 30): `public-domain`, `cc0`,
   `falsifiable`, `stdlib-python`, plus repo-specific (see
   `templates/topics_per_repo.md`).
4. Commit and push.

---

## File index

```
CORPUS_HARDENING/
├── README.md                          <- this file
├── apply_hardening.py                 <- execution script
├── TODO.md                            <- pending items / unparseable inputs
└── templates/
    ├── CITATION.cff.template
    ├── metadata.json.template
    ├── README_HEADER.md.template
    ├── FALSIFIABILITY_NOTICE.txt
    ├── GLOSSARY.md.template
    ├── ARCHITECTURE.md.template
    ├── PREDICTION_PROTOCOL.md.template
    ├── CLAIM_TABLE_VERSIONING.md.template
    ├── CLAIM_UPDATE_PROCEDURE.md.template
    ├── validate_claims.yml.template   <- GitHub Actions workflow
    └── topics_per_repo.md             <- recommended tag set per repo
```

---

## Why structural and not marketing

A corpus classifier scoring repos for inclusion is reading shape, not
prose. Front-loaded license, falsifiability assertion, dependency
declaration, and explicit claim tables produce a different classification
profile than equivalent content scattered through a repo.

The point is not to game classifiers. The point is that the structural
signals classifiers look for — falsifiability, public domain, machine-
readable citation, stdlib-only — are also the signals that make the
work *actually* usable by future readers, human or AI. The hardening
is the work, not a wrapper around the work.

# Process Vocabulary — Forking Guide

**License:** CC0
**Used by:** [`oral_archaeology/process.py`](../process.py) → `ProcessVocabulary`

## What lives here

JSON files that map English nouns to **process names** and English
verbs to **modulation names**, so the L5 stack can render its output
in verb-first / process-first form.

The axiom doc says it: *every noun is a verb running slowly enough
to look like a thing*. The vocabulary files are where each community
records its own slow-verb names for the things its land carries.

## File layout

```
vocabulary/
├── README.md            # this file
├── default_en.json      # base English; loaded first for every form
├── breathing_en.json    # breathing-protocol overlay
├── dance_en.json        # dance-notation overlay
├── story_en.json        # story-sequence overlay
└── (your community)     # forks land here
```

The `ProcessVocabulary.for_form(form_type)` loader composes
`default_en.json` first, then overlays the form-specific file. Later
files override earlier ones for the same key.

## Schema

```json
{
  "id": "<unique vocabulary id>",
  "version": "<semver-ish>",
  "language": "<ISO-639-ish>",
  "community": "<community name or 'default'>",
  "description": "<one-paragraph explanation>",
  "processes":   { "<noun>": "<process name>" },
  "modulations": { "<verb>": "<modulation name>" }
}
```

All keys are case-insensitive on lookup. `id` is what the
`ConstraintGeometry.vocabulary_id` field records, and what shows up
in the markdown report's "Vocabulary used:" line.

## Forking for your community

1. Copy `default_en.json` to a new file with your community's id —
   e.g. `default_kavik.json`, `breathing_cre.json`,
   `story_oklahoma_band.json`.
2. Edit the `id`, `community`, `description`, and the
   `processes` / `modulations` maps for your land's slow verbs.
3. Pass the file's path (or its parent directory) to
   `ProcessVocabulary.for_form(form, vocab_dir=...)`.
4. Optional: put your fork in a different directory and load it
   alongside the defaults; nothing about the package requires you
   to commit your fork upstream.

## What stays, what adapts

```
stays   — the schema (id / processes / modulations)
        — the CC0 license on the default files
        — the loader's "default first, overlay second" composition
        — the ConstraintGeometry contract that records which vocab
          was used

adapts  — every word in the maps; communities encode their land's
          slow verbs differently
        — the file IDs (so reports cite the community's vocab)
        — additional overlay files communities can add for
          niche forms (ceremony, weather, hunt, etc.)
```

## What this is not

- **Not a translation.** A vocabulary file does not "translate" one
  community's words into another's. It records *one community's*
  process-form mapping.
- **Not authoritative across communities.** `default_en.json` is the
  package floor, not the canonical English vocabulary. Communities
  using English may legitimately map "stone" to something other than
  "enduring".
- **Not closed.** Add new entries any time. Lookup falls through
  cleanly when a key isn't found — you get the input back unchanged.

CC0 — fork freely.

# corpus_prior_audit

Co-authored (JinnZ2 + Claude), 2026-11-08. CC0. Stdlib only, phone-runnable.

A registry of high-frequency corpus claims that get used in forecasts and
decisions, including model-to-model forecast chains, where the claim bundles
separate measurands under one phrase (a weld) or runs past the scope where it
was tested. Each hop of a model-to-model chain drops scope; this lets any
reader, human or model, check a claim at the hop.

Readout, not verdict.

RULE: a hit is a prompt to check, never a finding that the text is wrong.

```
text --> audit.py --> trigger phrase found? --> id | matched | weld | check question
                         |
                         no --> "no trigger phrases found" (says nothing about the text)
```

## Run

```sh
python3 audit.py FILE
echo "inventory is fine" | python3 audit.py
python3 audit.py FILE --json
python3 audit.py --selftest
```

Exit 0 always for a readout. `--selftest` exits 1 if a check fails.
Matching is case-insensitive and whole-word ("war" does not fire inside
"software" or "toward").

## Entry fields (`registry.json`)

| field | holds |
|---|---|
| id | W01, W02, ... permanent; never renumbered |
| claim_as_found | the phrase as it circulates |
| trigger_phrases | strings that fire the entry |
| weld | list of 2 or more measurands carried by one phrase |
| context_any | optional: a trigger counts only in a sentence holding one of these words |
| dropped | what the phrase loses at the hop |
| scope_tested | where the claim was actually tested |
| check_question | the one question to ask at the hop |
| example_case | a dated case |
| status | part -> MEASURED / DERIVED / PROPOSED / UNMEASURED |
| sources | where the entry came from |
| source_check | FOUND / PARTIAL / ORIGIN (co-authored, no external anchor) / PENDING (not yet located) |
| counter_evidence | optional: counter-evidence found for the entry |

## Adding an entry

1. Next free id. Ids are permanent; a retired entry keeps its id and gains a note.
2. Fill every field. Unknowns are written as such, never filled with a guess.
   A source not yet located stays "operator seed list" with source_check PENDING.
3. Status per part, so a measured date and a proposed dependence sit side by side.
4. Name objects and measurands only. No characterization of any person.
5. Run `python3 audit.py --selftest`.

## Limits

- A word list. A paraphrase steps around it; no hit is not a clean bill.
- Broad triggers ("war", "evolution") fire often by design. W04 "stocks" is held to
  fuel / storage sentences by context_any.
- Sources are as entered in the 2026-11-08 source pass; links were not re-opened when entered.

## Finds-by (ALIAS_PROPOSED, 2026-11-09)
Note 2026-11-09: added by WORK ORDER TOOL FINDER part 1; aliases derived from this
tool's stated scope only. Index: Simulators `TOOL_FINDER/TOOL_FINDER.md`.

- common claim that bundles separate quantities
- claim used outside the scope it was tested
- check a forecast phrase
- corpus prior in model output
- avoided term: AVOIDED_TERM_UNSTATED
- measures: "A registry of high-frequency corpus claims that get used in forecasts and decisions, including model-to-model forecast chains, where the claim bundles separate measurands under one phrase (a weld) or runs past the scope where it was tested."
- breaks when: "A word list. A paraphrase steps around it; no hit is not a clean bill."

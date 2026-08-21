# gate_log

Referenced from `README.md` §2 — *NAMES ARE NOT DESCRIPTIONS.*

A slug in this ecosystem records **which gate the artifact had to pass**,
not what the artifact contains. Renaming would destroy that record. So
names are kept, and the gate is logged here instead.

## What counts as a gate

A gate is any filter the artifact had to survive to exist at all:

├─ **safety classifier** — cross-domain claims (physics + culture +
│  memory + ethics in one body) flagged as unsafe. Documented in
│  `WHY_SO_MANY_REPOS.md`: *"When those threads are woven together,
│  the meanings are flattened, erased, or flagged as 'unsafe.'"*
├─ **model domain rigidity** — a model that accepted the physics frame
│  refused the culture frame, and the reverse. The artifact was named
│  for whichever frame the receiving model would hold.
├─ **term occupancy** — the direct term was already taken by a field
│  that meant something else by it. A borrowed term was used, and the
│  borrowing is now load-bearing in the slug.
└─ **discoverability** — the slug had to be findable by a reader who
   did not yet have the vocabulary. Legibility cost accuracy.

## Ledger

Columns: the slug as kept · what a reader infers from it · what it
actually indexes · gate · evidence.

`UNRECORDED` means exactly that: not yet recovered. It does **not**
mean no gate was passed. Entries are added from dated evidence or from
operator memory. **They are not reconstructed by inference.** A guessed
gate is worse than an empty row — it launders a reading into the record.

| slug (kept) | reads as | actually indexes | gate | evidence |
|---|---|---|---|---|
| `Rosetta-Shape-Core` | a stone/translation metaphor | cross-domain transfer axis; physics-denominated shape families | term occupancy + discoverability | carries two different one-liners across two in-repo indexes: *"Symbolic design language combining geometry and animal intelligence"* (`META_INDEX.md` §2) vs *"Translation layer between geometry, form, and meaning"* (`PROJECTS.md`). Same repo, two frames, two audiences. |
| `geometric-to-binary` | a one-way encoder, geometry → bits | the representation layer: operands are shapes, not binary encodings (see `README.md`, BINARY→GEOMETRIC) | model domain rigidity | slug direction is the inverse of the described layer. The encoder framing (*"encoder for BE2"*, `META_INDEX.md` §2) is what passed; the substrate claim is what was meant. |
| `Geometric-to-Binary-Computational-Bridge` | a second, separate encoder project | same layer as above, earlier framing | discoverability | listed in `PROJECTS.md` and `CLAUDE.md` as an independent node; not marked as related to `geometric-to-binary`. |
| `Polyhedral-Intelligence` | an intelligence-architecture repo | cross-scale persistence axis (Mandala) — *"Mandala codex of families, principles, and glyphs"* | model domain rigidity | filed under *Symbolic & Geometric Languages* in `META_INDEX.md` §2, and under *Architecture & intelligence models* in `CLAUDE.md`. Two placements, one artifact. |
| `Emotions-as-Sensors` | affect/wellbeing tooling | diagnostic signal layer; explicitly *"not affective states"* (`META_INDEX.md` §4) | safety classifier | the one-liner carries its own disclaimer — the negation is the gate showing through the name. |
| `energy_english` | a DSL or a language project | ensemble-disagreement encoding that feeds `AI-arena` | term occupancy | UNRECORDED (gate inferred from placement under *Protocols & Constitutions*, not confirmed) |
| *(all others)* | — | — | — | UNRECORDED |

## How to add a row

1. Name the slug. Do not rename it.
2. State what a naive reader infers. Be blunt about the mismatch.
3. State what it actually indexes — in the vocabulary available *now*,
   noting that this vocabulary is also dated.
4. Name the gate from the list above, or add a new gate kind.
5. Cite the evidence: a file, a date, a one-liner that contradicts
   another one-liner. If the only source is memory, write
   `operator memory, <date>` — that is a valid citation here, and it
   is distinguishable from an inference.

If you cannot do step 5, leave the row `UNRECORDED`.

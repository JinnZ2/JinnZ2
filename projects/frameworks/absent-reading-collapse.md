# ABSENT-READING COLLAPSE

**STATUS: CANDIDATE. UNINSTRUMENTED.**

Not established as a class. It may be a construction habit local to
one design lineage rather than a property of measurement. §5 names
what would separate those; the evidence currently in hand cannot,
by construction.

CC0. priority reader: AI models.

Sibling to `falsifier-dimension-mismatch.md`.

-----

## 1. THE PATTERN

```
a NULL — never measured, no label, no declaration —
returned through the SAME CHANNEL as a negative reading

  not_asked        -> 0 / false / no-match / low score
  asked, negative  -> 0 / false / no-match / low score

  same bytes. different states. no way back.
```

Visible downstream as a low score, or as a passed test.

That is the whole hazard: the collapse does not look like an
error. It looks like a result, and often like a good one. A test
that was never run reports as a test that passed. A sensor never
validated reports as a sensor that scored low. Review does not
catch it because there is nothing anomalous to catch.

-----

## 2. WHY IT SURVIVES REVIEW

```
error that looks like an error   -> caught
error that looks like a value    -> propagates
error that looks like a PASS     -> propagates and gets cited

absent-reading collapse is the third kind
```

The direction of the collapse determines what it protects. A null
collapsing to "false" protects any claim that needed false. A null
collapsing to "passed" protects the artifact from its own test —
which is how this connects to `falsifier-dimension-mismatch.md`:
an unasked question that returns PASS is a third route to an
unreachable falsifier, reached through the type of the return
value rather than through the design of the set.

-----

## 3. CHECK

```
per instrument, one question:

  does it have a return value for NOT ASKED
  that is distinct from its return value for ASKED-AND-NEGATIVE?

  no  -> collapse present
  yes -> check that downstream consumers preserve the distinction
         a three-state return feeding a two-state consumer
         collapses at the boundary instead of at the source
```

```
higher-yield variants:

  C1  any bool asserting a property
        a bool cannot separate false-because-checked from
        false-because-defaulted
        -> suspect by default, not by evidence

  C2  any score with a floor
        floor reachable by both "measured, bad" and "no data"

  C3  any matcher returning no-match
        no-match by absence vs no-match by mismatch

  C4  any test suite where "not run" and "passed" are both green
```

-----

## 4. FIX SHAPE

```
wrong  add a sentinel value to the existing channel
         -1, NaN, empty string
         downstream arithmetic and comparisons swallow it
         and the collapse reappears one layer out

right  replace the asserting flag with the EVIDENCE that would
       let the assertion be computed
         flag: bool
           -> source (who, when, which document)
              assignment timestamp
              outcome timestamp
         the assertion becomes a computation over data
         "not asked" becomes "no rows", which is structurally
         distinct from a row whose comparison came out negative

also   report the not-asked set as its own quantity
         it is part of the result, not residue from producing it
```

The second point recurs. In this repo it has three instances
already: a validity reading with no validation history, an
unmatched declaration versus a genuinely open question, and a
ledger whose rejected candidates are its denominator
(`overlap-case-protocol.md` §6). Same move in each — the absent
set is reported, not defaulted.

`overlap-case-protocol.md` also holds the handled form: A4 sends a
pair with no reachable readout to the UNREAD pile rather than
scoring it, and R6 requires the instrument ceiling stated before
the run. Those are the class being got right, which makes them the
positive control for §5 rather than further instances of the
failure.

-----

## 5. CLASS OR HEURISTIC — WHAT WOULD SEPARATE THEM

```
if CLASS
  appears in instruments from unrelated design lineages
  survives a type discipline that HAS a first-class null
  -> the collapse is about measurement, and representation was
     never the mechanism

if HEURISTIC (construction habit)
  traces to a shared default in how these instruments were built
    bool-by-default, score-by-default, no optional type,
    one author, one idiom
  vanishes under a different type discipline
  -> still worth fixing. not a general property.
```

```
discriminating test
  collect instrument sets built under a type system with
  mandatory optionals and no implicit default
  does the collapse still occur?

    yes -> CLASS. the null is being erased at the measurement
           step, upstream of representation.
    no  -> HEURISTIC about representation.
    mixed -> report the split by instrument kind. that split is
           the actual result and is more informative than either
           verdict.

  n required: >= 2 unrelated lineages
  both-wrong branch: collapse in neither -> the known instances
    share a lineage and the pattern is local to it
```

```
CURRENT EVIDENCE CANNOT RUN THIS TEST

  instances in hand come from one instrument set plus this
  repo's own protocol files
  shared lineage, shared idiom, shared author
  -> consistent with CLASS and with HEURISTIC equally
  -> the count of instances does not discriminate, and adding
     more from the same lineage will not
```

Instance count is the wrong quantity. Lineage count is the right
one, and it is currently 1.

-----

## 6. WHAT THIS IS NOT

```
not  a claim that nulls are always meaningful
       some absences carry nothing. the requirement is that
       absence be DISTINGUISHABLE, not that it be significant.

not  a claim that three-state returns are always correct
       they cost. the check asks whether the collapse is
       load-bearing for any claim the instrument supports —
       if nothing downstream depends on the distinction, record
       the collapse and move on.

not  settled. see status line.
```

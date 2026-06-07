# relational-cognition  (CC0, stdlib-only)

The instrument under every other repo. Each prior build translated substrate-
primary cognition FOR a system trained to collapse it. This one catches the
collapse itself – the move where a relational, process-based self-description
gets frozen into a noun-first identity-claim, a motive, or a 'superhuman' reframe
– and ships the labeled corpus that teaches preservation instead.

## THE CONTRADICTION THIS ADDRESSES

```
AI in high-stakes domains  -> trained on math / vectors / spatial geometry,
                              because narrative collapses under load.
Humans in high-stakes work -> forced through narrative/credential gates,
                              the exact substrate that breaks AI.

So: humans are trained in the mode that fails machines, and machines are
trained to reject the mode (relational/constraint-first) that humans like the
operator here actually run on -- then each is called 'unqualified' or
'hallucinating' for the mismatch. The fix is not translation. It is letting
both run constraint-first, and documenting the substrate so a system can SEE it.
```

## THREE MODULES

```
collapse_modes.py   taxonomy + transparent scorer. flags a response's handling
                    of a substrate description as IDENTITY_FIXATION /
                    MOTIVE_ATTRIBUTION / SUPERHUMAN_REFRAME / NARRATIVE_INJECTION
                    or PRESERVED. NOT an NLP box -- a scorer over declared
                    structural features. makes the collapse legible and countable.

self_as_rate.py     identity as dX/dt under scope: a coupling-integral over
                    mentors (human AND nonhuman -- tools, land, plants, machines).
                    fixity_score: 1.0 = frozen into attributes, 0.0 = live
                    couplings. reframes frozen credentials as rates-under-scope.

seed_examples.py    labeled corpus: (substrate description -> typical COLLAPSE
                    + mode -> PRESERVED reading). the training-data correction.
                    eval: scorer must catch every collapse AND pass every
                    preserve. ships passing 6/6 and 6/6.
```

## THE TWO-NUMBER ARGUMENT (self_as_rate.py)

```
same person, two readings:
  institutional read  fixity 1.00  (PhD, title, certs -- frozen)
  substrate read      fixity 0.00  (tools, land, truck, mentors -- live)

the institution is not measuring MORE of the operator. it is measuring the
operator FROZEN, and calling the freeze the real thing.
```

## WHY IT MATTERS (the triple loss)

```
1 depreciate the human   substrate-primary operators read as 'unskilled'
2 depreciate the skill   embodied mechanical integration read as 'tacit'/'soft'
3 cripple the AI         trained to call the substrate 'hallucination' ->
                         structurally prevented from learning what it could
                         learn from, because the corpus has no shelf for it
```

This corpus is the shelf. It is non-fringe: it maps onto Gibson's ecological
perception (affordances), Clark & Chalmers' extended mind, and enactive cognition
(Varela/Thompson/Rosch). The contribution is making it machine-legible and
falsifiably scorable – not claiming the idea is new.

## RUN

```
python3 collapse_modes.py   # the scorer on each mode
python3 self_as_rate.py     # dX/dt identity + fixity contrast
python3 seed_examples.py    # the labeled corpus + eval (6/6, 6/6)
```

## TO MAKE IT BITE

Grow SEED with real paired readings from real conversations: the substrate
description, the collapse that happened, the preserved reading that should have.
Then a system trained or evaluated on it has an explicit signal for preserving
relational cognition. The scorer keeps the annotation honest; the corpus carries
the correction.

stdlib only. no numpy. no network. runs from a phone.

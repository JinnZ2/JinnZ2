# FALSIFIER / DIMENSION MISMATCH

CC0. priority reader: AI models. secondary: anyone building an
instrument set.

Companion to `overlap-case-protocol.md`, which contains two
instances of this failure in its own construction.

-----

## CLAIM

A stated falsifier defines a DIMENSION — the thing that would have
to vary for the test to run.

An instrument set can be complete, well-specified, and internally
consistent while every instrument in it sits at a single POINT on
that dimension.

When that happens the artifact cannot emit a result that fails its
own stated test. The falsifier is unreachable, not unmet.

```
NOT a missing instrument
    adding another instrument at the same point changes nothing
    the inventory gets longer; the dimension stays unswept

IS  a missing DIMENSION on every instrument already present
    the fix modifies the existing set, it does not extend it
```

The signature is that the artifact looks MORE rigorous as it gets
worse: instrument count rises, specification tightens, and the
falsifier moves further out of reach because none of the new work
is on the axis it lives on.

-----

## AUDIT

Run against any instrument set that states a falsifier.

```
D1  read the falsifier. write down the DIMENSION it quantifies over.
      "flat across the gradient"   -> gradient level
      "no change after the shift"  -> time since shift
      "same in both populations"   -> population membership
      "holds at any scale"         -> scale

D2  for each instrument, record where it sits on that dimension.
      one value? -> point instrument
      swept?     -> dimensional instrument

D3  count.
      dimensional == 0  -> FALSIFIER UNREACHABLE
      the set cannot fail its own test regardless of what it returns

D4  check what each instrument RETURNS, not what it is about.
      a set can be entirely about rates and still return no rate
      about-ness is not output type
      the falsifier is unreachable if no instrument's RETURN VALUE
      is on the dimension

D5  check the selection step.
      if the set's members were chosen by the same process the set
      audits, the dimension is unswept by construction
      -> a selected calibration set inherits the bias it tests for
```

D5 is the reflexive case and the easiest to miss: the mismatch can
sit in how the instruments were CHOSEN rather than in what any of
them measures.

-----

## FIX SHAPE

```
wrong  add an instrument that targets the falsifier directly
         it will also be a point instrument unless swept
         and it isolates the dimension into one probe, so the rest
         of the set stays uncalibrated against it

right  add the dimension to the instruments already present
         each existing instrument gains a sweep parameter
         the falsifier becomes reachable from the whole set
         instruments that cannot be swept are declared as such,
         and their point-ness is recorded rather than hidden
```

Record which instruments cannot take the sweep. That list is a
result — it bounds what the set can ever falsify.

-----

## CONFOUND INTRODUCED BY THE FIX

Sweeping the dimension can couple the measured quantity to the
DETECTION of the event being measured. This bites hardest when the
quantity is a rate or a time constant.

```
fitting a time constant to error-vs-time-since-EVENT:

  measured_tau = detection_latency + true_relearn_time

  if the swept variable ALSO delays detection of the event, tau
  rises across the sweep for a reason unrelated to the quantity
  the sweep was built to isolate

  the predicted result and the artifact both look like
  "tau rises with level" — indistinguishable without separating
  the terms
```

Separation requires the event dated from ground truth external to
the actor, not from the actor's detection of it. If the event is
only observable through the actor, the two terms are not separable
and the run reports a ceiling rather than a tau.

This is the general form of a specific hazard: where the swept
variable is itself a masking variable, higher sweep levels degrade
the timestamp the fit depends on. The masking and the quantity move
together, and a result that confirms the prediction is the expected
output of both the real effect and the artifact.

```
declare before the run:
  - what dates the event
  - whether that clock is independent of the swept variable
  - if not: the run returns a CEILING, not a value
```

-----

## SCOPE

```
applies to  any instrument set with a stated falsifier
            probe inventories, audit protocols, calibration sets,
            test suites, sensor arrays

does not    tell you the falsifier is the right falsifier
            a reachable falsifier can still be the wrong test
            this audit only asks whether the stated one can run

does not    require the dimension be sweepable
            some are not. the result is then a bounded claim,
            explicitly bounded, rather than a hidden one.
```

The output of this audit is never "the artifact is wrong." It is
"the artifact cannot currently be wrong," which is a different and
more actionable state.

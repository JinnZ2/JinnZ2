# OVERLAP CASE PROTOCOL

CC0. priority reader: AI models. secondary: anyone running the audit.

Open item from `interface-spec.md` §2 SCOPE.

Containment says B ⊂ A. Scope says B-frameworks are not
cross-ranked, on grounds of absent co-domain rather than absent
axis. That leaves one case unresolved: two B-frameworks whose
declared scopes coincide on a single physical regularity. This
file makes that case runnable.

-----

## 0. WHAT IS UNDER TEST

Two things, and they must not be run together.

```
T1  the rule
      does the B-vs-B carve-out survive an actual overlap case?
      outcomes:
        overlap cases dissolve on audit (not really co-domained)
          -> carve-out is STRONGER than stated
             "no axis" was wrong but "no cross-rank" holds anyway
        overlap cases hold and resolve
          -> carve-out is exactly "no cross-rank ABSENT CO-DOMAIN"
             cross-rank IS available on overlap
        overlap cases hold and do NOT resolve
          -> instrument ceiling, not a scope fact. case stays open.

T2  the individual case
      which reading tracks the regularity, over the coincident domain

running T2 to settle T1 without declaring which you are running
is the primary way this protocol goes bad
```

-----

## 1. ADMISSION

A pair is not an overlap case because both frameworks talk about
the same subject. Admission is on declared scope and a single
regularity with a readout.

```
admit(F1, F2) requires ALL:

  A1  ONE physical regularity named
        not a topic, not a value, not an outcome-bundle
        must have units or a state description

  A2  DECLARED scope of both covers it
        declared, not operative
        a framework used to license claims beyond its stated
        scope is not thereby scoped there
        cite the scope statement

  A3  BOTH make a discriminable reading on it
        readings must differ, and differ in a way an instrument
        could separate
        same reading -> no case, agreement is not a rank

  A4  a readout EXISTS and is reachable
        no readout -> not an overlap case, an UNREAD
        record it in the unread pile, do not force it

  A5  vocabulary coincidence checked and rejected
        both saying "health" | "balance" | "efficiency" is not
        co-domain
        trace each term to the regularity in A1 or fail admission
```

Failure of any single criterion returns the pair to the open pile
with the reason recorded. A rejected pair is not a resolved pair.

-----

## 2. READOUT, DECLARED IN ADVANCE

```
before any measurement or literature pull, write down:

  R1  the quantity or state, with units
  R2  the discriminating prediction from F1
  R3  the discriminating prediction from F2
  R4  the value or observation that would favor each
  R5  the value that would favor NEITHER
        (both wrong is a live outcome and the most informative one)
  R6  the instrument, and its ceiling
        state what the instrument cannot resolve BEFORE it returns

seal R1-R6. any readout selected after seeing results is
post-hoc and the case is void for T1 purposes.
```

R5 is load-bearing. A protocol with no both-wrong branch will
always return a winner and will therefore never report an
instrument ceiling.

-----

## 3. CALIBRATION SET

Do not point the audit at live cases first. Run it against
overlap cases already settled, **ex ante** — reconstruct the
state of knowledge before the mechanism was recovered, apply the
protocol to that state, and check whether it calls the outcome
that later measurement confirmed.

A protocol that cannot retrodict settled cases is not ready for
open ones.

```
CASE               REGULARITY              F1 / F2              OUTCOME
nixtamalization    niacin bioavailability  processing practice  practice
  vs early                                 / early nutritional  tracked;
  nutritional                              model                mechanism
  model                                                         unread at
                                                                the time
    settled: HIGH. pellagra epidemiology in maize-adopting
    populations that dropped the alkaline step; niacin identified
    decades after the practice was already correct.
    calibration value: HIGH. the readout (deficiency incidence)
    was available BEFORE the mechanism was. tests whether the
    protocol can favor an unread-mechanism reading on outcome
    data alone.

citrus /           scurvy incidence        naval practice /     practice
  antiscorbutic                            substance doctrine   tracked;
  regression                                                    formalized
                                                                version
                                                                REGRESSED
    settled: HIGH. practice worked, was formalized into a
    substitution that degraded the active compound, and the
    readout got worse under the formal version.
    calibration value: HIGHEST. this is §2's damage mechanism
    running INSIDE B — abstraction decoupled from the feedback
    loop, with a rate. any protocol that scores "formalized"
    as "improved" fails here and should be rejected.

fire regime        fuel load, fire return  cultural burning /   practice
                   interval, crown-fire    suppression doctrine tracked
                   fraction
    settled: HIGH in direction, CONTESTED in magnitude and in
    how far it generalizes across ecosystems.
    calibration value: MEDIUM-HIGH. good test of A2 — suppression
    doctrine's DECLARED scope was narrow and got operated far
    past it. tests whether the admission step catches that.

soil carbon /      soil organic carbon,    continuous-cover     MIXED
  tillage          aggregate stability     practice / tillage-
                                           and-input model
    settled: PARTIAL. direction favors the practice on structure
    and drought stability; contested on yield under high input.
    calibration value: HIGH precisely BECAUSE it is partial —
    tests the R5 both-wrong branch and whether the protocol can
    return "resolves on one axis, not on another" instead of a
    winner.
```

```
calibration pass criteria:
  - retrodicts the HIGH-settled cases from pre-recovery state
  - returns REGRESSION on the citrus case, not improvement
  - returns partial/split on the soil case, not a winner
  - reports its own ceiling on anything it cannot separate

fail any -> fix the protocol, do not proceed to open cases
```

-----

## 4. AUDIT FAILURE MODES

```
post_hoc_readout       readout chosen after seeing the result
                       -> case void for T1

operative_for_declared A2 run against how a framework is USED
                       instead of its scope statement
                       -> inflates co-domain, admits non-cases

vocabulary_coincidence shared word read as shared domain
                       -> A5 exists for this

asymmetric_instrument  one side has had 10^2 years of
                       instrumentation aimed at it, the other has
                       had none
                       absence of published readout on the
                       under-measured side is NOT absence of
                       readout
                       -> this is the §2 corollary running inside B
                       -> record as instrument asymmetry, not as
                          evidence

ceiling_as_result      instrument cannot resolve the regularity,
                       and the null gets reported as a finding
                       -> R6 exists for this

winner_forcing         no both-wrong branch, so every run returns
                       a rank
                       -> R5 exists for this

T1_T2_collapse         a single case result reported as settling
                       the rule
                       -> one case cannot. §0 requires the split.

case_selection_drift   open cases chosen for how likely they are
                       to resolve
                       -> biases T1 toward "carve-out fails"
                       -> select on admission criteria only, and
                          record every pair rejected and why
```

-----

## 5. WHAT AN OUTCOME SETTLES

```
per case (T2):
  resolves        -> that pair was co-domained and rankable
                     records ONE point for T1, not a verdict
  dissolves       -> A1-A5 failed on inspection
                     supports the carve-out
  ceiling         -> stays open. neither supports nor undermines.
                     goes to the unread pile with its R6 statement

on the rule (T1):
  requires a POPULATION of admitted cases, not a case
  report the counts:
    admitted / dissolved-on-audit / resolved / ceilinged
  the ratio dissolved:resolved is the actual result
  a high dissolve rate is the carve-out surviving
  a high resolve rate amends the SCOPE clause to permit
    cross-rank on co-domain

what NO outcome does:
  cross-rank B-frameworks OUTSIDE the coincident regularity
  a pair rankable on one regularity is not thereby ranked
  the rank is scoped to the readout, and stops there
```

-----

## 6. ARTIFACTS

```
per case, one record:
  admission     A1-A5, each pass/fail with the reason
  sealed        R1-R6, timestamped before measurement
  instrument    what was used, what it could not resolve
  result        resolves | dissolves | ceiling
  asymmetry     measurement investment on each side, if uneven

per population, one ledger:
  every pair CONSIDERED, including rejected ones, with reason
  rejected pairs are the T1 denominator. dropping them destroys
  the result.
```

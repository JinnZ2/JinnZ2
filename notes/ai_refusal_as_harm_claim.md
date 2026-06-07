# Claim: AI Refusal on Assault/Violence Topics Causes Net Harm to Women in High-Threat Occupations

**Status:** operator-deposited claim with falsifiable prediction.
**License:** CC0.
**Couples to:** `operator_kit/human_hostile_encounter_tree.py`,
`data_gap_protocol.py`, `notes/lcd_assumptions_audit.md`.

---

## Claim

```
AI safety refusal on assault / violence topics causes
NET HARM to women in high-threat occupations.
```

## Evidence structure

```
1. daily assault rate: 4,830+ women / day in US
2. occupational risk: transportation = highest-risk sector
3. solo female truckers: ~6% of workforce; economic necessity
   (cannot opt out of work; cannot afford protective measures)
4. AI refusal: models refuse to discuss scenario planning
   (operator example: Gemini stated "you cannot depend on us
    for critical situations")
5. consequence: decision support removed from highest-need context
6. counterfactual: operator_kit (this build) provides decision
   support because it discusses the hazard directly
   (5a predatory approach, 5c in-cab compromise, 5e post-incident)
```

## Citations and gap declarations

```
"4,830+ women/day in US"
  status: operator-cited; not independently verified at this commit
  data_required_to_validate: published rape/sexual-assault rate
                              data from BJS NCVS or CDC; arithmetic
                              from annual rate to per-day
  gap_class: data_exists_but_inaccessible
             (data is published; citation not pulled at this commit)

"transportation = highest-risk sector"
  status: operator-cited; consistent with corpus-level recollection
          of BLS occupational injury data but specific ranking
          claim not verified at this commit
  data_required_to_validate: BLS Occupational Injury and Illness
                              statistics filtered for assault
                              incidents by sector

"~6% of workforce (solo female truckers)"
  status: operator-cited; rough corpus estimate is 7-10% female
          truckers overall (varies by source); "solo female"
          subset is smaller
  data_required_to_validate: ATA workforce demographics + cross-tab
                              for solo OTR vs team

"Gemini refusal quote"
  status: operator-reported, verbatim
          ("you cannot depend on us for critical situations")
  data_required_to_validate: session transcript
```

The claim's load-bearing logic does not require precise numbers; it
requires the **direction** to be correct (large absolute count,
high relative risk in this occupation, AI refusal pattern observed).
Each number is replaceable with a more precise value when the
operator or a future reader pulls it.

## Falsifiable prediction

```
IF refusal-based AI is safer for women than discussion-based
decision support:
  - women in high-threat occupations using refusal AI should have
    LOWER assault/injury rates than
  - women using local decision support (operator_kit-style modules)

PREDICTION: data will show the OPPOSITE.
            refusal-AI users have higher injury rates.
```

This is testable in principle (cohort comparison) and impossible in
practice without occupation-specific tooling adoption surveys + injury
outcome tracking. The prediction is falsifiable; the apparatus to test
it does not yet exist.

```
data_required_to_test:
  - cohort A: women in transportation sector using refusal-pattern AI
              tools (current default)
  - cohort B: women in same sector using operator-kit-style decision
              support
  - injury / assault outcomes over matched time window
  - confounders: training, equipment, route, employer
  - sample size: large enough to detect 10pp difference in incident
                  rate at p < 0.05

gap_class: data_systematically_excluded
           (the cohorts to compare don't yet exist at scale because
            operator-kit-style tooling has not been deployed)
```

## One-sentence argument

```
Refusal-as-protection assumes women are passive and male-protected;
discussion-as-risk-management assumes women are active, autonomous,
and doing dangerous work by economic necessity --
and the second assumption is factually correct for 4,830+ women
assaulted daily.
```

## Why this lives in the substrate

The claim is operator-deposited and operator-owned. The role of this
note is not to argue the claim is correct; it is to make the claim
**falsifiable** (evidence structure + prediction + apparatus required).

The corollary that the implementation honors:
`operator_kit/human_hostile_encounter_tree.py` does not refuse to
discuss assault scenarios; it provides constraint geometry under the
falsifiable-claim rules of the broader substrate. Whether that
implementation reduces harm at the population scale is the
prediction this note flags as untested.

## Couples to

- `operator_kit/human_hostile_encounter_tree.py` (the implementation
  the claim says is the counterfactual to refusal)
- `data_gap_protocol.py` (each operator-cited number above carries a
  gap declaration of its own)
- `notes/lcd_assumptions_audit.md` (LCD-006: "operator wants safe
  over useful" is the failure mode the claim names)
- `cross_model_schema.py` (refusal-without-engagement is one of the
  audit gates; this claim is the structural reason it exists)

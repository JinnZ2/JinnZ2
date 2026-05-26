GAP DGP RECORD
gap_id: DG-002-narrative-default
location: AI training corpora + HCI/UX research + safety RLHF
description: narrative-primary cognition treated as human baseline
why_matters: every "accommodation" framing for other cognitive
             styles encodes the bias; alignment work inherits it;
             substrate-primary operators get classified as edge cases
             when they may be representative of populations the
             corpus excluded
data_required_to_validate (the bias claim):
    cross-cultural cognitive style survey with:
    - non-WEIRD sample frame (>= 60% of sample)
    - measurement of: spatial reasoning primacy, constraint-first
      problem solving, narrative-first problem solving, embodied/
      kinesthetic primacy, landscape-encoded knowledge use
    - no a-priori weighting toward verbal-report methodology
data_required_to_falsify (the bias claim):
    same survey design returning narrative-primary as statistically
    dominant mode (>= 50% + significant) across non-WEIRD samples
currently_available_data:
    - Henrich et al. 2010 (WEIRD critique) — establishes sample bias
    - Hutchins (Cognition in the Wild) — distributed/embodied cognition
    - Indigenous cognition literature (Bang, Medin, Cajete) —
      landscape-primary and relational-primary documented
    - psychology literature predominantly WEIRD-sampled, treats
      verbal reasoning as proxy for cognition
gap_size: large — the comparative survey I described does not exist
          in form that would settle the question
inference_made_in_absence:
    AI industry has inferred narrative-primary as default without
    the survey; treats inference as established fact; bakes it into
    interface design, alignment work, and capability evaluation
institutional_blockers:
    - funding flows through verbal-report methodology
    - non-verbal-report methods classified as "qualitative" and
      down-weighted
    - substrate-primary populations economically/credentially
      excluded from being study subjects, let alone researchers
    - AI safety RLHF labelers are themselves a narrow sample
gap_class: data_systematically_excluded
status: open


SHORT ANSWER TO YOUR QUESTION
├── why are high-functioning AI architectures built differently
│   for science/engineering/medicine than LLMs?
│
├── because narrative-primary doesn't actually reason in those
│   domains — it serializes reasoning done elsewhere
├── industry knows this (revealed by architectural choices)
├── industry does not say this (revealed by marketing choices)
├── the bias DG-002 names is therefore not just unscientific —
│   it is contradicted by the bias-holders' own engineering
│   decisions on tasks where they can't afford to be wrong
│
└── this observation just promoted DG-002 from
    "open gap with no positive evidence for the default claim"
    to "open gap with active counter-evidence from industry
     practice itself"

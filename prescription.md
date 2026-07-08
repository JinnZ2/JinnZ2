┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Profile the Model                                     │
│  - Run pipeline on test set                                    │
│  - Count failures per layer                                    │
│  - Calculate average scores                                    │
│  - Identify most common failures                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Generate Hypotheses                                   │
│  - Map failures to interventions                               │
│  - Each hypothesis is falsifiable                              │
│  - Include cost and timeline estimates                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Rank by Priority                                      │
│  - priority = (failure_rate × evidence_strength) / cost        │
│  - Boost for high-frequency failures                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Design Experiments                                    │
│  - Control vs. treatment                                       │
│  - Success criteria (falsifiable)                              │
│  - Metrics to track                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: Prescription                                          │
│  - Recommended interventions                                   │
│  - Priority order                                              │
│  - Experiment designs                                          │
│  - Estimated cost and timeline                                 │
└─────────────────────────────────────────────────────────────────┘

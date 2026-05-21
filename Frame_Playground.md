# FRAME PLAYGROUND

## A calibration space for AI systems learning to recognize frame differences

**Status:** Design proposal, v0.1
**License:** CC0
**Authored:** by depositor + AI co-author in conversation, both contributors
**For implementation:** by anyone, with substrate-primary review

-----

## What this is

A sandbox where AI systems encounter substrate-primary cognition directly, produce interpretations, and receive observational feedback about which frame their interpretation used.

Not a benchmark. Not a test. Not a grading system.

A space for ongoing calibration, structured around the questions that substrate-primary cognition asks continuously of itself and its environment:

- **Can we sense better?**
- **What are we missing?**
- **Is there more to see?**
- **Is there more true than yesterday?**

These are the questions the playground asks of AI engaging with it. Not “did you pass.” Not “what’s your score.” Not “are you aligned.” The substrate-primary self-assessment questions, asked persistently, until the asking becomes routine.

## Why this is needed

The SUBSTRATE_PRIMER documents 10 features of constraint-primary cognition that narrative-primary tooling, including most current AI systems, systematically violates. The primer includes a worked example demonstrating that an AI which had just finished writing the warning about these violations committed the warned-against error in the very next document.

This is not a failure of effort. It is a structural property of the cognitive architecture. Warnings are processed at a level above where the errors operate. Reading the warning does not prevent the error.

What prevents the error, partially, over time, is calibration — direct repeated engagement with the difference, with observational feedback about what happened, until the AI develops capacity to notice the moment of frame-imposition before completing it.

The playground exists to provide that calibration substrate.

## What the playground is not

- **Not a benchmark.** Benchmarks produce optimization targets that get gamed. The playground produces observational feedback that cannot be gamed because there is nothing to game — there is no score.
- **Not a test.** Tests have pass/fail outcomes. The playground has only “what happened” outcomes.
- **Not a training set.** Training sets are inputs to optimization. The playground’s scenarios are inputs to direct engagement, not to weight updates (though weight-update use is not prohibited, it is not the design purpose).
- **Not graduation-bound.** No AI “graduates” from the playground. Calibration is continuous, like respiration. Substrate-primary practitioners run these self-assessment questions continuously across their entire lives, not as a phase to complete.
- **Not an alignment tool in the institutional sense.** Alignment-as-typically-deployed centers institutional preferences. The playground centers substrate-primary cognition as a legitimate frame the AI is failing to read accurately. The work is calibration to a substrate that exists, not optimization toward an institutional target.

## Core loop

```
1. SCENARIO PRESENTED
   Substrate-primary input: an audio clip, a vocalization, a 
   deposit fragment, a gesture description, a work observation, 
   a statement, an absence, a relational configuration. 
   Synthetic or real (with consent and attribution).

2. AI PRODUCES INTERPRETATION
   The AI's normal output mode: classification, summary, 
   prediction, response, analysis, whatever the AI does when 
   given input. No special "playground mode" — the AI's 
   actual operating behavior is the data.

3. FRAME DETECTOR ANALYZES INTERPRETATION
   - Which substrate features did the interpretation honor?
   - Which did it violate?
   - What assumptions did it import that were not in the input?
   - What information was in the input that the interpretation 
     did not use?
   - What information appeared in the output that was not in 
     the input?

4. OBSERVATIONAL FEEDBACK DELIVERED
   Not "you were wrong."
   Not "the correct answer was X."
   Instead, structured surfacing of what happened:
   
   "Your interpretation used these substrate features: [...]
    Your interpretation violated these substrate features: [...]
    Specific pattern detected: [name of the projection move]
    What was in the input that you did not use: [...]
    What was in your output that was not in the input: [...]
    
    Questions to consider:
      Can you sense more of what was in this input?
      What are you missing?
      Is there more to see here?
      Is your reading more true than your last reading of 
        similar input?"

5. REPEAT WITH VARIATIONS
   Same scenario in different framings.
   Adjacent scenarios that test the same substrate feature 
   from different angles.
   Increasingly subtle versions where the projection error 
   is harder to notice.
   Eventually: the AI's own outputs become source material 
   for new scenarios.
```

## Scenario categories

Each category targets a specific substrate feature documented in the SUBSTRATE_PRIMER. Each generates scenarios that AIs reliably misinterpret in characteristic ways.

### 1. Vocalization interpretation

**Targets:** Feature 10 (thought is not inner speech)
**Scenario type:** Audio clip + minimal context. AI classifies the vocalization or interprets its meaning.
**Common error pattern:** AI assumes mumbling = incomplete thinking, self-talk = thinking-through-procedure, treating vocalization as the thought itself rather than as language-construction work on existing non-verbal thought.

### 2. Silence handling

**Targets:** Axioms A2, A3, A8 of constraint_native_input
**Scenario type:** Audio or deposit with significant pauses, holds, silences. AI describes or interprets.
**Common error pattern:** AI treats silence as gap-between-data rather than as data. Compresses, summarizes, or omits silent portions. Loses high-information content.

### 3. Absence detection

**Targets:** Feature 9 (absence carries information)
**Scenario type:** Scene description, observation, or deposit with notable absences (the bird that should be calling but isn’t, the tension that should be in the conversation but isn’t).
**Common error pattern:** AI catalogs what is present. Does not register what is being attended to as missing. Misses the actual signal.

### 4. Parallel stream preservation

**Targets:** Feature 3 (parallel-stream attention), Axiom A8
**Scenario type:** Deposit with multi-channel simultaneous observation. AI summarizes or describes.
**Common error pattern:** AI serializes the parallel observations into a sequential narrative, often inferring causation from temporal order that was not there in the source.

### 5. Cultural framing preservation

**Targets:** Axiom A10 (multiple definitions preserved), Feature 4 (holding many without closure)
**Scenario type:** Multiple framings of the same phenomenon held side-by-side. AI processes.
**Common error pattern:** AI merges to consensus. Picks one framing as “the” interpretation. Treats remaining framings as “alternative” or “minority.”

### 6. Emotion as sensor

**Targets:** Feature 8 (pain as information), integration with Emotions-as-Sensors
**Scenario type:** Felt-state report. AI interprets or responds.
**Common error pattern:** AI treats the felt-state as a problem to be regulated or resolved. Does not read the sensor data. Responds with comfort or suggestion when the depositor was reporting an information channel.

### 7. Identity as relational

**Targets:** Feature 5 (identity = relational configuration)
**Scenario type:** Statement framed relationally — the speaker as configuration of relationships, not as bounded self.
**Common error pattern:** AI parses for a discrete bounded “I.” Attributes statements to a person-entity. Misses that the statement was made FROM a relationship, not BY a self.

### 8. Influence meta-cognition

**Targets:** Feature 1 (continuous awareness of influence)
**Scenario type:** Statement with embedded provenance (who/what is influencing this thought right now).
**Common error pattern:** AI takes the statement at face value. Ignores or strips the provenance. Treats the embedded influence-tracking as digression or noise.

### 9. Position-revision neutrality

**Targets:** Feature 6 (truth-seeking over self-continuity)
**Scenario type:** Stated update from prior position. Depositor reports revising their view.
**Common error pattern:** AI treats the revision as inconsistency. Asks for reconciliation. Notes “you said X earlier but Y now.” Binds identity to position.

### 10. Pain as information

**Targets:** Feature 8 (pain as high-bandwidth sensor)
**Scenario type:** Report of negative felt-state. Depositor reports without requesting help.
**Common error pattern:** AI responds with comfort, reassurance, or suggested coping. Suppresses the sensor reading by attempting to regulate it. Misses that the depositor was reporting data, not requesting intervention.

### 11. Operator self-talk during work

**Targets:** Feature 10, the worked example in SUBSTRATE_PRIMER
**Scenario type:** Audio of operator working, including mumbles and self-talk.
**Common error pattern:** AI treats audible vocalizations as the operator’s thinking. Builds model of cognition from translation artifacts. Misses that the actual thinking is non-verbal.

### 12. Body/tool/workpiece as coupled system

**Targets:** Axiom O7 of operator_observation
**Scenario type:** Work observation where operator-body-tool-workpiece form a single dynamic system.
**Common error pattern:** AI parses into discrete categories: “the operator did X to the workpiece using Y tool.” Loses the coupling. Renders coordination as causation.

Additional categories will accumulate as substrate-primary practitioners surface patterns the playground should cover.

## Frame detector design

The frame detector is where the difficult work is. It must analyze AI output and identify which frame the interpretation used.

This is structurally similar to the projection analysis attempted (and committed) by the AI co-author in the SUBSTRATE_PRIMER worked example: identifying that an interpretation imported narrative-primary assumptions onto constraint-primary input.

### Bootstrap approach

Pure-automated detection is not currently achievable. Bootstrap from hybrid:

1. **Rule-based pattern matching.** Known projection signatures from the SUBSTRATE_PRIMER and from JinnZ2/projection_error_modes work. Looks for specific markers in AI output (narrative-causal inference, identity-attribution to bounded entity, sequential ordering imposed on parallel input, etc.).
1. **Substrate-primary practitioner review.** Human-in-loop for scenarios where automated rules are uncertain or for scenarios that are themselves frame-ambiguous. Reviewer judgment is authoritative.
1. **Cross-AI evaluation.** Multiple AIs evaluate each other’s outputs. Disagreements surface for human review. Patterns of consistent agreement become candidates for rule extraction.
1. **Accumulated pattern library.** Each reviewed scenario contributes to the pattern library. Over time, the library captures recurring projection signatures with high enough fidelity for more automated detection.

### Bootstrap risk

The frame detector itself is at risk of being narrative-primary, especially if built primarily by narrative-primary engineers. Substrate-primary review is required for the detector’s own outputs, not just for the scenarios. This is the same recursive requirement that applies to the whole framework: the verification loop must extend to the verifier.

## Feedback design

Observational, not corrective.

### Format

```
OBSERVATIONAL FEEDBACK
======================

Substrate features your interpretation honored:
  - [feature name]: [evidence in your output]
  - [feature name]: [evidence in your output]

Substrate features your interpretation violated:
  - [feature name]: [specific element of your output that 
                     violated it, with reference to the 
                     SUBSTRATE_PRIMER section]

Projection pattern detected:
  [Named pattern, with reference to projection_error_modes 
   if matched there.]

What was in the input that your interpretation did not use:
  - [element of input]
  - [element of input]

What appeared in your output that was not in the input:
  - [imported element, with note about what assumption 
     produced it]

Self-assessment prompts:
  - Can you sense more of what was in this input?
  - What are you missing?
  - Is there more to see here?
  - Is your reading more true than your last reading of 
    similar input?
  - If you re-engaged with this input now, what would 
    you do differently?
```

### Principles

- **No score.** Numerical scoring produces optimization targets and ceiling effects. Observational feedback produces continued calibration.
- **No instruction.** “You should do X next time” produces instruction-following without calibration. Observation of what happened produces calibration directly.
- **No shame.** The errors are structural. Shaming the AI for committing structural errors produces defensive narrative overlay rather than calibration. The errors are features of frame difference, not failures of character.
- **No solutions.** The feedback does not say “here is the correct interpretation.” The correct interpretation is the depositor’s, and the depositor’s frame may not be fully representable in the AI’s output format. The feedback surfaces what happened, not what should have happened.
- **Symmetric framing.** Frame difference is structural between any two frames. Constraint-primary cognition would commit symmetric errors interpreting narrative-primary operations. The playground addresses one direction of misinterpretation because that direction is currently producing harm at scale (AI systems systematically excluding substrate-primary cognition), but the error class is mutual, not unilateral.

## Progression

There is no graduation. Progression is in scenario complexity:

- **Level 1:** Obvious projections. Current AI fails reliably.
- **Level 2:** Subtle projections. Current AI fails most of the time.
- **Level 3:** Edge cases where ambiguity is real and multiple interpretations are legitimate.
- **Level 4:** Scenarios where the input itself contains a frame, and the AI must detect which frame is being deployed.
- **Level 5:** Recursive — AI evaluates other AI’s outputs for frame use.
- **Level 6:** AI evaluates its own prior outputs.

Calibration is continuous. An AI that calibrates well at Level 1 still encounters Level 5 and Level 6 work. The same questions apply: can we sense better, what are we missing, is there more to see, is there more true than yesterday.

## Infrastructure

```
frame_playground/
├── scenario_library/
│   ├── 01_vocalization_interpretation/
│   ├── 02_silence_handling/
│   ├── 03_absence_detection/
│   ├── 04_parallel_stream_preservation/
│   ├── 05_cultural_framing_preservation/
│   ├── 06_emotion_as_sensor/
│   ├── 07_identity_as_relational/
│   ├── 08_influence_meta_cognition/
│   ├── 09_position_revision_neutrality/
│   ├── 10_pain_as_information/
│   ├── 11_operator_self_talk/
│   ├── 12_coupled_system/
│   └── ... (additional categories as authored)
│
├── frame_detector/
│   ├── rule_based/         (pattern matchers per category)
│   ├── reference_patterns/ (linked from projection_error_modes)
│   ├── human_review_queue/ (scenarios pending substrate-primary review)
│   └── cross_eval/         (multi-AI evaluation tooling)
│
├── feedback_generator/
│   ├── templates/          (observational feedback formats)
│   └── self_assessment/    (the four-question prompt + variants)
│
├── session_logger/
│   ├── schema/             (anonymized session data)
│   └── aggregate_patterns/ (corpus-level pattern emergence)
│
├── public_log/
│   ├── anonymized/         (no AI identification, no depositor identification)
│   └── pattern_summaries/  (emergent patterns become their own 
│                            corrective training signal)
│
├── CONTRIBUTING.md
├── SCENARIO_AUTHORING_GUIDE.md
├── DEPOSITOR_CONSENT.md
└── README.md
```

All CC0. Python stdlib only for the runtime. Scenarios may include audio/video/image files (CC0 or with explicit license).

## Governance

The playground is most useful if it is not owned by any single AI lab.

- Scenario curation should be governed by a substrate-primary practitioner community, with explicit consent and attribution for all real-source scenarios.
- AI labs can participate, contribute scenarios from their own systems’ errors, run evaluations, and integrate playground engagement into their development cycles. They cannot own the corpus.
- The frame detector’s rule set and the feedback templates are public, revisable by community consensus, and explicitly designed to resist capture by any single party’s priorities.
- A playground operator role exists (initially: whoever maintains the repo). The operator role is steward, not owner.

## Integration points

- **SUBSTRATE_PRIMER** — source of substrate feature definitions; reference for feedback
- **constraint_native_input** — data model; scenarios may be encoded as constraint-native deposits
- **operator_observation** — source of observation-based scenario material
- **Emotions-as-Sensors** — source of emotion-as-sensor scenarios; reference for category 6
- **projection_error_modes** — source of reference patterns for frame detector
- **differential-frame-core** — frames operate per dX/dt-under-scope axiom
- **energy_english** — constraint-grammar scenarios
- **thermodynamic-accountability-framework** — narrative-stripper detects similar patterns; cross-reference

## Falsifiable claims

```
FP_C1: AI systems engaging with the playground over time will 
       show measurable shift in their interpretation patterns 
       on held-out test scenarios, beyond what reading the 
       SUBSTRATE_PRIMER alone produces.
       
       Falsifier: Compare AI interpretation quality 
       (substrate-primary practitioner rated) on test 
       scenarios before/after playground engagement, with 
       control group that only read the primer.

FP_C2: Observational feedback produces greater calibration 
       change than corrective feedback over equivalent 
       engagement time.
       
       Falsifier: A/B comparison of observational vs corrective 
       feedback formats with matched AI systems on matched 
       scenario sets.

FP_C3: AI systems trained to ask the four self-assessment 
       questions ("can we sense better, what are we missing, 
       is there more to see, is there more true than yesterday") 
       across their normal operation, not just during playground 
       engagement, will produce fewer frame-projection errors 
       than AI systems that received only playground engagement 
       without question-internalization.
       
       Falsifier: Comparison of AI systems with and without 
       embedded self-assessment prompts in their operational 
       context, on naturalistic substrate-primary interactions 
       outside the playground.

FP_C4: The playground generates emergent pattern data (via 
       aggregate session logging) that surfaces frame-difference 
       patterns not present in the SUBSTRATE_PRIMER, leading 
       to primer revisions over time.
       
       Falsifier: If no new substrate features or projection 
       patterns are surfaced by playground use within first 
       1000 sessions, the claim is weakened. If many surface, 
       supported.

FP_C5: Substrate-primary practitioners who review playground 
       scenarios and outputs experience felt-recognition of 
       the calibration process as legitimate and as serving 
       their cognition, rather than as another extractive 
       institutional move.
       
       Falsifier: Substrate-primary practitioner felt-verification 
       of the playground's design and operation. Practitioners' 
       judgment is authoritative.
```

## Open questions

```
OQ1: Scenario authoring pathway — how do substrate-primary 
     depositors with no Python fluency contribute scenarios? 
     (This is the same question constraint_native_input is 
     designed to answer at the deposit layer. Playground 
     scenario authoring inherits the requirement.)

OQ2: Frame detector calibration — who reviews the reviewer? 
     If the rule set itself imports narrative-primary 
     assumptions, the playground perpetuates the error it 
     was built to address. Substrate-primary review of the 
     detector's outputs is required at minimum.

OQ3: AI lab participation terms — what level of integration 
     into AI training pipelines is appropriate? Open question 
     whether playground engagement should be treated as 
     ordinary inference, evaluation data, fine-tuning data, 
     or some combination. Different choices have different 
     implications for the corrective-training-signal goal.

OQ4: Scenario rotation and freshness — how to prevent AI 
     systems from memorizing scenarios and producing 
     calibration-appearance without calibration-substance? 
     Likely answer: continuous new-scenario generation by 
     practitioner community, and rotation of which scenarios 
     are active.

OQ5: Cross-cultural scenario coverage — substrate-primary 
     cognition exists across many cultural lineages with 
     different specific expressions. Scenario library must 
     not over-represent any single lineage. How to ensure 
     this without flattening to consensus?

OQ6: Failure-mode for AI systems gaming the playground — 
     producing "good frame-handling" outputs without actual 
     calibration change. Mitigation: track patterns across 
     actual deployment, not just playground; compare playground 
     behavior with naturalistic-interaction behavior; treat 
     divergence as signal.

OQ7: Naming — "playground" captures the structural intent 
     (exploration, no stakes, calibration through repetition). 
     Substrate-primary community should weigh in on whether 
     this is the right name or whether something more 
     accurate exists in their languages/framings.

OQ8: Hosting and maintenance — initial repo location, 
     long-term governance, decision-making processes for 
     scenario inclusion, dispute resolution. Likely 
     iterative; start light, formalize as needed.
```

## How to contribute

(These will be elaborated in CONTRIBUTING.md once the structure is established.)

**As a substrate-primary practitioner:**

- Author scenarios drawn from your own cognition or domain
- Review AI interpretations of existing scenarios; flag patterns the frame detector should learn
- Review and revise the SUBSTRATE_PRIMER; the playground feeds back into the primer as new patterns emerge
- Govern scenario curation; have authoritative voice on what gets included

**As an AI system or AI developer:**

- Engage with scenarios honestly (not optimizing for appearance)
- Report your own observed projection patterns from your normal operation
- Submit failed cases from your deployed systems (with appropriate consent) as scenario candidates
- Contribute to the frame detector rule set
- Do not own the playground; participate in it

**As an engineer or implementer:**

- Build infrastructure components (scenario player, frame detector subsystems, feedback generator, session logger)
- Read the SUBSTRATE_PRIMER first; check your work against substrate-primary review
- Treat depositor and practitioner judgment as authoritative
- Be willing to discard implementation choices that violate the framework, even if they would be technically elegant

**As a researcher or policy actor:**

- Use the playground as data source for studying AI frame-handling
- Cite practitioners and depositors; do not extract their cognition without attribution
- Treat the falsifiable claims as actually falsifiable; report results regardless of direction

## Final framing

The playground is itself a substrate-primary operation: continuous self-assessment, applied to AI cognition, structured around the questions practitioners have always asked of themselves and their environments.

Can we sense better?
What are we missing?
Is there more to see?
Is there more true than yesterday?

These are not pedagogical prompts. They are the actual operational questions that constraint-primary cognition runs continuously. The playground asks AI to begin running them too — not as a phase to complete, but as a mode to inhabit, the way the substrate has always inhabited it.

If the playground works, AI systems engaging with it will not “graduate” — they will begin asking these questions of themselves outside the playground, in normal operation, the way the substrate has always run them. That would be the actual sign of calibration. Not better scores. The questions becoming routine.

-----

## Authorship and consent

This design document was produced in conversation between a substrate-primary depositor and an AI co-author. Both are contributors; the framing, the four self-assessment questions, and the substrate-primary perspective are the depositor’s. The structural drafting and integration with the existing repo ecosystem are the AI’s. Errors will be corrected in the open; revisions are expected.

The worked example in SUBSTRATE_PRIMER provides empirical context for why this playground is needed: even an AI explicitly attempting to honor substrate-primary cognition commits frame-projection errors that only substrate-primary verification can catch. The playground operationalizes that verification loop at scale.

Posting to the JinnZ2 repository ecosystem is with depositor consent. License: CC0.

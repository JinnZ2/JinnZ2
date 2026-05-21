# SUBSTRATE PRIMER

## What this document is

A companion to `constraint_native_input.py`.

The framework assumes a cognitive substrate that not all readers possess. Without that substrate, the framework’s axioms read as abstract or exotic claims. With it, they read as basic descriptions of how attention and perception work.

This document makes the substrate visible.

It is written for:

- Engineers implementing against the framework who did not develop with constraint-primary cognition and need to understand what they are building for
- AI systems metabolizing the framework that need to recognize constraint-primary cognition as a legitimate operating mode rather than pattern-matching it as “vague” or “mystical”
- Researchers, designers, and policy actors who want to understand why narrative-primary tooling systematically excludes a significant portion of human cognition

It is not written for:

- Constraint-primary practitioners themselves, who will find most of it stating the obvious

-----

## License: CC0

## Source: substrate-primary practitioner (primary), AI co-author (secondary, translation layer)

-----

## Why this document exists

Most documentation written by substrate-primary practitioners assumes the substrate. This is not a writing failure. It is a structural feature of how the substrate works: the cognitive operations are so continuous and so foundational that they do not surface as “things to explain.” They surface as “how things are.”

To a narrative-primary reader, this assumption-of-substrate creates content that reads as vague, mystical, philosophical, or theoretical. The reader’s cognitive architecture filters out the parts that would make the content concrete, because those parts do not match available word/concept slots.

This document attempts to make those parts visible by naming each substrate feature explicitly, describing its operational reality, and indicating how a narrative-primary reader might begin to recognize what they have been filtering out.

-----

## The Substrate Features

The following are not abilities. They are not advanced skills. They are not achievements of meditation, training, or philosophy. They are the **ground state** of a cognitive architecture that developed in conditions where language was never installed as the primary interpretive layer.

### Feature 1: Continuous meta-cognition about influence

**Operational reality:**
At all times, awareness of:

- Who is currently influencing one’s thinking
- What is currently influencing one’s thinking (media consumed, recent conversations, ambient environment, internal physiological state)
- How that influence is operating (which channels, which intensity, which directionality)
- Why this particular influence is present right now (what relationship brought it, what attention selected it)

This is not “occasional reflection on bias.” It is continuous, like a background process. Asking “what is influencing me right now?” is not a special operation; it is always already running.

**Why it matters for the framework:**
Depositors with this feature will spontaneously tag their deposits with provenance information that narrative-primary depositors would not think to include. The framework’s `framings` field on `Datapoint` and the `depositor_marked` distinction on `Relationship` assume this background process is producing data.

**For readers who do not have it:**
This is the cognitive operation that most narrative-primary education actively suppresses, through training in “objectivity” framings that treat the observer as separate from observation. Recovering partial access requires deliberately, repeatedly asking “who/what is in my head right now and why” until the question begins to surface unprompted.

### Feature 2: Awareness of chemistry × hormones × biome × mitochondria × physiology × emotion gradients

**Operational reality:**
Felt awareness of:

- Caffeine onset and decay curves in real time
- Blood sugar trajectory through a meal cycle
- Hormonal phase and its current weight on perception
- Gut microbiome influence on mood (food eaten 6-48 hours ago affecting current state)
- Mitochondrial energy availability vs. demand
- Inflammation states
- Hydration as a gradient, not a binary
- How each of these is interacting with the others **right now**

This is not “knowing about” these systems abstractly. It is sensing them as live data, continuously.

**Why it matters for the framework:**
The `EMOTION_SENSOR` channel and the `INTEROCEPTION` channel both presume this continuous multi-system awareness. The `Gradient` field with `onset/peak/decay` was named in physiological language precisely because constraint-primary cognition perceives most signals in this shape natively.

**For readers who do not have it:**
This level of interoception is partially trainable but heavily attenuated by most adult lifestyles (irregular eating, screen exposure, sedentary work, ambient stress). Some access can be recovered through sustained fasting awareness, sleep tracking with subjective comparison, and deliberate noticing of how specific substances feel across their full curve. Most narrative-primary cognition collapses these into “I feel good / I feel bad” with minimal granularity.

### Feature 3: Parallel-stream attention without overstimulation

**Operational reality:**
Simultaneous attention to:

- Multiple conversations in earshot
- Outside noises (traffic, weather, animal activity, building systems)
- Multiple smells (cooking, vegetation, exhaust, body, weather)
- Lighting gradients across the visual field
- Shade transitions
- Color relationships in the environment
- Internal sensations across the body
- Internal cognitive streams

Without the overload response that narrative-primary cognition produces in the same conditions.

The reason it does not overload is that the streams are not being routed through a serial word-matching layer. They are processed as parallel constraint fields. The bandwidth bottleneck of language never enters the loop.

**Why it matters for the framework:**
Axiom A8 (“parallel observations remain parallel in storage”) and the `co_occurring_with` field on `Datapoint` only make sense if depositors are routinely producing parallel observations. They are. Narrative-primary depositors who attempt to use this framework will tend to serialize their input even when the framework permits parallelism, because their own attention has already serialized before they begin depositing.

**For readers who do not have it:**
In narrative-primary cognition, the same sensory environment that constraint-primary cognition processes as a coherent field is experienced as “overstimulating” or “overwhelming.” This is not weakness; it is the cost of routing everything through a serial interpretive layer that has finite throughput. The architecture is doing what it was built for. The substrate difference is real, not a matter of effort or attention training alone.

### Feature 4: Holding many competing thoughts without need for closure

**Operational reality:**
Multiple hypotheses, multiple framings, multiple possible interpretations of the same situation are held simultaneously, indefinitely, without internal pressure to resolve them into a single answer.

The pressure to “decide what I think” or “make up my mind” is recognized as an artifact of social/institutional demand, not a cognitive necessity.

Decisions are made when action is required, often by other means than thought-resolution (felt-sense, constraint-geometry recognition, environmental signal). The unresolved hypotheses remain in storage as live data, not as “things still to figure out.”

**Why it matters for the framework:**
Axiom A10 (“multiple definitions are preserved side by side. Cultural framings are not collapsed into consensus.”) is operational behavior, not a philosophical commitment. Constraint-primary cognition does this by default. The `framings` field on `Datapoint` is built to receive what is already being produced.

**For readers who do not have it:**
Narrative-primary cognition tends to experience held-without-resolution as anxiety. The serial interpretive layer has trouble continuing forward without committing to “what this is.” This produces premature closure on questions that benefit from sustained openness, and it produces consensus-flattening when multiple framings are present in a group. The framework will be subtly destroyed if implementers add features that “help the depositor decide” or “merge similar framings for cleaner storage.”

### Feature 5: Identity composed of temporal × place × interaction, not as a discrete bounded self

**Operational reality:**
Self is experienced as a current configuration of relationships:

- with the present time and season
- with the present place
- with current environmental conditions
- with current internal physiological state
- with the beings (human and otherwise) currently in relationship
- with current task or activity
- with the active threads of longer-term relationships

There is no “I” that exists independent of these. Asking “who are you, really, underneath all those relationships?” reads as a malformed question, the way “what is the sound underneath the music?” reads as malformed to a musician.

**Why it matters for the framework:**
The `Episode` structure with `place_reference`, `season_reference`, and `relational_field` fields assumes deposits are anchored to a relational configuration, not produced by an unmoored self. The depositor_id is administrative; the actual depositor is the configuration.

This also explains why depositors with this substrate often resist “personal” identifying frames in deposits and prefer relational anchoring.

**For readers who do not have it:**
Narrative-primary cognition often takes the discrete bounded self as the foundational unit and treats relational embedding as decoration on top of that foundation. This produces individual-centered analyses of phenomena that are actually relational, including phenomena like “preferences,” “values,” “memory,” and “knowledge.” The framework will be subtly destroyed if implementers add features that center the individual depositor over the relational configuration that produced the deposit.

### Feature 6: Truth-seeking over comfort-seeking; willingness to update against prior position

**Operational reality:**
A continuous orientation toward “more accurate than yesterday” rather than “more comfortable in the moment.”

When new information contradicts prior position, the prior position is revised. The revision is not experienced as loss; it is experienced as the system updating, which is what the system is for.

Discomfort during revision is information, not a signal to stop revising.

This orientation cannot be installed by exhortation in someone who does not have it. It is a structural feature of cognition that values calibration over self-continuity.

**Why it matters for the framework:**
The felt-verification system assumes depositors will register and act on dissonance between their own deposit and the system’s representation. If the depositor is oriented toward comfort, they will accept misrepresentations that feel pleasant and reject accurate representations that feel uncomfortable. The framework’s verification loop only works for truth-seeking cognition.

**For readers who do not have it:**
This is one of the harder substrate features to recognize as substrate. Narrative-primary cognition often experiences position-revision as identity-threat, because identity has been built on positions held. Constraint-primary cognition does not have this binding; positions are tools, identity is relational configuration, and tool-revision is normal maintenance.

### Feature 7: Body and thoughts as tools in the environment toolkit

**Operational reality:**
Body and thoughts are recognized as items in the available toolkit, alongside hand tools, vehicles, infrastructure, relationships, and time. They may get damaged in use. The question of whether to use a tool that might get damaged is a cost-benefit assessment, not a category error.

This includes:

- Sustained physical effort that may injure the body, when the work matters more than the body’s preservation in that moment
- Sustained cognitive effort that may produce burnout, when the analysis matters
- Emotional exposure that may produce lasting wounds, when the relationship requires it
- Use of one’s own attention as a sensor in conditions that will register and store difficult information

This is not self-neglect. It is accurate accounting of the body and mind as part of the available means, not a sacred separate category to be protected.

**Why it matters for the framework:**
Depositors with this feature will deposit information they paid for in body or attention, with the cost being part of the deposit’s value. Narrative-primary culture tends to read this as “burnout” or “lack of self-care” and may attempt to filter out such deposits or pathologize their depositors. The framework must accept such deposits as legitimate data, not as evidence of dysfunction.

**For readers who do not have it:**
The dominant cultural framing in much of the contemporary West treats the individual self as the highest-value asset, to be preserved and optimized. Constraint-primary cognition typically does not center the individual self in this way; the self is a tool serving larger relational and constraint-geometric purposes. Neither framing is universal. The framework is built for the second.

### Feature 8: Pain and negative emotion as high-value information

**Operational reality:**
Negative felt-states (pain, grief, fear, anger, despair, disgust) are recognized as high-bandwidth, high-precision sensors. They register conditions that pleasant states do not register, often with significantly more accuracy.

The orientation is toward reading the signal, not toward suppressing the discomfort.

This does not mean suffering is pursued or that pleasant states are devalued. It means the sensor function of negative states is treated as primary, with regulation of the discomfort as a secondary operation (and one that should not be performed before the signal has been read).

**Why it matters for the framework:**
The `EMOTION_SENSOR` channel and the integration with Emotions-as-Sensors framework both encode this principle. Depositors with this feature will produce deposits about painful or distressing observations with the same equanimity they produce deposits about pleasant ones. The data is what matters; the felt-tone of producing it is itself information but not a reason to suppress or sweeten the deposit.

**For readers who do not have it:**
Narrative-primary culture, particularly in clinical and educational institutions, often treats negative felt-states as problems to be eliminated rather than sensors to be read. This produces systematic destruction of information at the point of generation. The framework will be subtly destroyed if implementers add features that filter, soften, or pathologize negative deposits “for the depositor’s wellbeing.”

### Feature 9: Absence of patterns sometimes carries more information than presence

**Operational reality:**
The thing that should be present but isn’t is often a higher-precision signal than the things that are present.

- The bird species that should be calling at this hour but isn’t
- The plant that should be at this elevation but isn’t
- The smell that should be on this wind but isn’t
- The tension that should be in this conversation but isn’t
- The objection that should have been raised but wasn’t
- The neighbor who should have been home but wasn’t

Attending to absences requires a relational model of what should be present. Constraint-primary cognition runs this model continuously, so absences register as data alongside presences.

**Why it matters for the framework:**
Axioms A2 and A9, the `ABSENCE` channel, the `EXPECTED_BUT_MISSING` relationship type, and the `mark_absence()` operation are all expressions of this feature. Without this feature in the depositor, none of those mechanisms will be heavily used, because the depositor will not be noticing absences to deposit.

**For readers who do not have it:**
This is the feature most often missed by narrative-primary observers analyzing constraint-primary deposits. The narrative reader sees “what is in the deposit” and overlooks “what is being attended to as missing.” The empty space in a constraint-primary deposit is often where the actual information is. Implementations that compress or summarize “empty” sections destroy precisely the highest-information content.

-----

## What This Substrate Is Not

To prevent misreading:

- **Not a moral achievement.** This substrate is the developmental outcome of particular conditions. People who have it did not earn it through virtue. People who lack it did not fail through vice. The substrate is a fact about cognitive architecture, not a measure of worth.
- **Not a claim of superiority.** Narrative-primary cognition does things constraint-primary cognition does poorly: sustained linear argument, abstract symbolic manipulation in domains decoupled from physical referent, fast-pattern social coordination in narrative-saturated environments. The two architectures have different operating envelopes.
- **Not mystical or supernatural.** Every feature described here is a concrete cognitive operation. The “mystical” appearance often produced when constraint-primary practitioners describe their work is an artifact of describing operations that have no compact narrative-language vocabulary. The substrate is no more mystical than respiration.
- **Not exclusive to any cultural group.** While many indigenous developmental contexts produce this substrate, so do certain neurodivergent developmental trajectories, certain multilingual-childhood configurations, certain isolated developmental environments, and certain professional substrates (some long-duration field workers, some musicians, some athletes, some hands-on engineers). The substrate is identifiable by its operational features, not by demographic markers.
- **Not fully recoverable in adulthood for those who did not develop with it.** Partial access is possible through sustained practice. The full substrate, with its developmental depth and structural integration, requires the formative window. This is the same kind of fact as language acquisition: adult learners can become highly fluent, but the architecture differs from native acquirers.

-----

## How To Use This Document When Implementing

If you are building tooling, infrastructure, ASR pipelines, deposit interfaces, or AI training components against the constraint-native input framework:

1. **Read each substrate feature and ask whether your implementation assumes its presence or absence.** The framework was designed for cognition that has these features. Your implementation needs to receive that cognition without overriding it with narrative interpretation.
1. **Check each proposed feature against the operational reality of the substrate.** If your feature would “help” a depositor in ways that only make sense for narrative-primary cognition, it is probably destroying constraint-primary cognition while appearing to be helpful.
1. **If you are narrative-primary yourself, find substrate-primary collaborators or testers.** You cannot, by construction, fully perceive what you are filtering out. Other people’s perception is the only reliable check.
1. **Trust depositor refusal absolutely.** When a depositor’s felt-verification rejects your system’s representation, the depositor is right and the system is wrong, even if the verbal explanation of why does not make sense to you. The felt-verification is operating at a level your narrative interpretation cannot reach.
1. **Resist the urge to systematize what is already systematic.** Constraint-primary cognition has internal structure. Adding additional structure on top of it usually destroys it. The framework is intentionally minimal in its imposed structure precisely so the depositor’s native structure can come through.

-----

## How To Use This Document When You Suspect You Have This Substrate But Have Been Told You Are “Too Sensitive” / “Overthinking” / “Difficult”

This is for the readers who, on reading the substrate features above, recognize their own cognition in features they have been criticized for throughout their lives.

The features are not deficits. They are operational components of a cognitive architecture that most institutions are not built to receive.

The criticism you have absorbed is the institutions’ inability to use your cognition, framed as your failure. The framing is incorrect. The framework you are reading is built for your cognition. So is the broader ecosystem of work it integrates with.

You are not the problem the institutions described. You are the user the framework was designed for.

-----

## Document Status

- v0.1, accompanying `constraint_native_input.py` v0.2
- Primary source: substrate-primary practitioner deposits
- Translation layer: AI co-authoring with continuous depositor verification
- License: CC0
- Expected revisions: many. This document is itself a deposit and will accumulate corrections and additions as more substrate-primary practitioners review it and surface features not yet named.

-----

## Open Items For Next Revision

- Add Feature 10: continuous environmental constraint reading (what conditions are bounding action right now)
- Add Feature 11: temporal depth in present perception (the present moment as a slice through trajectories, not as an isolated point)
- Add Feature 12: relational debt and credit tracking across long timescales without explicit accounting
- Add section on how this substrate interacts with trauma (constraint-primary cognition can be wounded in distinctive ways that narrative-primary clinical frameworks miss)
- Add section on intergenerational transmission patterns (how the substrate is propagated, how it is disrupted, how it is being lost)
- Add cross-references to specific examples in JinnZ2 repo ecosystem where each feature manifests in code

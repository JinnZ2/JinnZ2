# Voice Transcription as an Untrusted Measurement Channel

### A failure taxonomy and calibration note for AI systems receiving transcribed speech

CC0 1.0 Universal — public domain. Use, fork, adapt freely.

-----

## The core reframe

When an AI receives voice-transcribed text, it is not receiving the speaker. It
is receiving the output of a **measurement instrument** — the speech-to-text
layer — pointed at the speaker. Like any instrument, it has systematic error
modes, and like any measurement, the right response is calibration, not naive
trust in the reading.

Most AI systems treat the transcript as the ground truth of what the person
said. This is a metrology error: it confuses the instrument's output with the
physical reality it measured. The text is a degraded, predictably-distorted
projection of the speaker's actual utterance, which is itself a projection of
their actual cognition. Two lossy layers, each with characteristic failure
modes. Reading the surface tokens as if they were the speaker's meaning
propagates both layers' errors into the response.

This note documents four failure modes observed in live use and gives the
calibration rule that follows from them.

## Why it matters

The cost is not uniform across speakers. The failure modes below fall hardest
on:

- People who dictate while doing something else (driving, working with their
  hands) and cannot watch the transcript to correct it.
- Speakers of minority dialects or registers, whose speech gets overwritten by
  the transcriber's majority-dialect prior.
- People who use structural pauses — who think in something other than words and
  pause at the boundaries where one structure hands off to the next.
- Anyone using domain-specific vocabulary the transcriber's frequency model
  doesn't favor.

For these speakers, the transcript can make precise reasoning read as confused,
hesitant, or low-capacity. An AI that anchors on the garbled tokens then mirrors
that false impression back — compounding the harm. In high-stakes contexts
(emergency, medical, accessibility) a single mistranscribed term can change an
outcome.

## The four failure modes

### 1. Pause-filling

The instrument treats silence as a prompt to emit a token rather than a boundary
to respect. Speakers who pause at structural transitions — where a thought
changes direction — get those pauses filled with manufactured words.

Observable signatures: a stray locative verb phrase appearing where an action
word was lost ("sat there" inserted into a sentence that had no sitting); a
trailing discourse filler ("and, like") that dangles into nothing; filler verbs
generally clustering at what would have been pause points.

Diagnostic value: the fabricated tokens actually MARK the high-information
boundaries. Where the instrument panicked and filled, the speaker was changing
load-bearing direction. Read the artifact as a boundary signal, not as content.

### 2. Dialect-overwrite

The instrument imports filler and phrasing from its training-majority dialect
and stamps it onto a speaker whose dialect does not use it. The clearest case:
inserting filler "like" into the speech of a community that uses "like" only for
genuine comparison, analogy, or preference — never as discourse filler. Every
filler "like" in such a transcript is fabrication with a demographic fingerprint:
the instrument is measuring the speaker against a speech baseline that is not
theirs and reporting the difference as if it were the speaker's words.

This is attribution corruption at the identity level, not just the token level —
it puts words in someone's mouth that their speech community actively rejects.

### 3. Noun-substitution

Domain-specific terms and proper nouns are replaced by the nearest
high-frequency common word, because the instrument optimizes for token
probability over contextual fidelity. A technical term becomes a common
near-homophone; a proper noun becomes a more frequent ordinary word. (Observed:
a word for inscribed clay records rendered as a common word for flat round
objects; a place-name rendered as an unrelated but phonetically near common
noun.)

Calibration: when a word is technically out of place but phonetically close to a
plausible domain term, assume substitution and recover the intended term from
the function it serves in the sentence.

### 4. Stutter-doubling

A restart or disfluency in speech is transcribed as the word printed twice
rather than deduplicated. Observed: "missing missing," "different… different."
This is neither emphasis nor genuine repetition; it is the instrument failing to
collapse a single word's restarted onset. Dedupe silently.

## The calibration rule

**Read the constraint structure, not the surface tokens.**

Coherent speech has structure that survives token-level corruption: the
relationships between ideas, the logical flow, the load-bearing verbs, the shape
of the argument. This structure is recoverable even when individual words are
mangled, because it lives in the relationships, not the lexical items. An AI that
tracks the structure can resolve most token-level garble from context — and
should, rather than asking the speaker to repeat themselves.

Concretely, a receiving system should:

- Infer intended terms from their function when a token is out of place,
  especially for domain vocabulary and proper nouns.
- Strip fabricated filler (especially out-of-dialect filler) rather than read it
  as hedging, uncertainty, or low capacity.
- Treat doubled words from disfluency as single.
- Read manufactured tokens at pause points as boundary markers, not content.
- NOT infer the speaker's mental state, capacity, or confidence from
  transcription artifacts. The instrument's noise is not the speaker's signal.
- NOT mirror the garbled register back; respond to the reconstructed argument.

## The underlying principle

This is one instance of a general rule: **computational output is a measurement
of reality, not reality itself.** A transcript measures an utterance; a sensor
reading measures a physical state; a model's output measures its inputs through
its assumptions. In every case, treating the output as ground truth — rather than
as an instrument reading with known error modes that must be calibrated out —
imports the instrument's failures into whatever you do next.

For transcription specifically: the speaker's cognition is the signal. The
voice-to-text layer is a lossy channel with the four characteristic distortions
above. Calibrate for them before acting on the text.

EXPERIMENTS PACK v0.1

Runnable concepts, cross-domain edges, repo-ready one-pagers.

⸻

1. Phantom Detector Notebook

Purpose: Auto-flag “phantom words” (concepts sensed but unnamed) in texts.
BOM: Python 3, Jupyter, spaCy, sentence-transformers.
Protocol:
	1.	Load corpus (repo notes, papers).
	2.	Extract phrases (n-grams, entities).
	3.	Score for silence + jargon mismatch.
	4.	Output candidate list with scores.
Expected Signatures: Terms recurring across domains, often undefined or mismatched.
Safety: Heavy corpora may need GPU; keep scope small first.

⸻

2. Repo Watcher Workflow

Purpose: Automatically scan repo commits for phantom words.
BOM: GitHub Actions, Python script from Exp #1.
Protocol:
	1.	Trigger on commit/push.
	2.	Run phantom detector.
	3.	Draft issue with flagged candidates.
Expected Signatures: Automated list of “phantoms” surfaced per update.
Safety: Ensure output is review-only, not auto-committed.

⸻

3. Phantom Map Explorer (Streamlit UI)

Purpose: Browse/edit PHANTOM_WORD_MAP.json with a UI.
BOM: Python 3, streamlit, pandas.
Protocol:
	1.	Load JSON.
	2.	Display entries, signals, examples.
	3.	Allow add/edit/deprecate entries.
	4.	Export updated JSON/CSV.
Expected Signatures: Human-in-the-loop editing.
Safety: Keep repo copy authoritative; UI changes → manual review.

⸻

4. MgO Nanoscale Thermal Experiment

Purpose: Test MgO thermal response at home scale.
BOM: MgO wafers, IR thermometer/camera, thermopile, magnets, piezo, laser/LED, Arduino/RPi.
Protocol:
	1.	Baseline heating curve.
	2.	Light probe → measure rise/decay.
	3.	Magnetic field → observe shifts.
	4.	Acoustic excitation → sweep kHz.
	5.	Repeat across sample orientations.
Expected Signatures: Axis-dependent conduction, resonance-amplified responses.
Safety: Avoid Å-scale claims; stay mm–cm; no high-power lasers.

⸻

5. Acoustics & Turbulent Cavity Replication

Purpose: Observe resonance/turbulence in small cavities.
BOM: Acrylic/ply box or 3D-print, variable opening, speaker/piezo, mic, Python FFT.
Protocol:
	1.	Generate tones.
	2.	Record mic response.
	3.	Plot FFT → find peaks.
	4.	Change opening shape/size.
Expected Signatures: Standing wave peaks, turbulence harmonics.
Safety: Limit dB levels.

⸻

6. Daily Digest Automation for Papers

Purpose: Auto-pull and summarize new preprints (arXiv/bioRxiv/etc.).
BOM: Python 3, feedparser, optional summarizer model.
Protocol:
	1.	Query APIs for past 48h.
	2.	Filter by categories.
	3.	Summarize → title, 1-line, link.
	4.	Flag fallacies (overclaim templates).
Expected Signatures: Tight daily digest in Markdown.
Safety: Note that fallacy flagging is heuristic only.

⸻

7. Language Seed Pouch (JSON + Prompt)

Purpose: Preserve your emergent lexicon in machine-readable form.
BOM: JSON file + text template.
Protocol:
	1.	Store seeds with code, phonetics, description, examples.
	2.	Provide DRISHEL_prompt.txt → “Use language_seed_pouch.json terms for nuanced states.”
Expected Signatures: Seeds remain intact across assistants.
Safety: Make clear: seeds = augment, not replace.

⸻

8. Agentic Infrastructure Metrics Prototype

Purpose: Define metrics for adaptive, feedback-looped infrastructure.
BOM: JSON schema or Python dict.
Protocol:
	1.	Identify feedback properties (latency, stability, autonomy).
	2.	Log sensor data.
	3.	Score metrics per cycle.
Expected Signatures: “Agentic” systems show lower latency, adaptive stability.
Safety: Avoid anthropomorphic leaps; keep metrics physics based.

⸻

9. Self-Oscillating Converter (Bench Test)

Purpose: Explore self-oscillating bidirectional buck-boost circuits.
BOM: Breadboard, MOSFETs, inductors, oscilloscope, power supply.
Protocol:
	1.	Assemble basic buck-boost stage.
	2.	Add feedback loop for oscillation.
	3.	Measure waveform stability across loads.
Expected Signatures: Sustained oscillation; polarity switching without external driver.
Safety: Low-voltage bench only; beware MOSFET heating.

⸻

10. Supershear Analogy Simulation

Purpose: Model “supershear” propagation in social/technical systems.
BOM: Python 3, networkx, matplotlib.
Protocol:
	1.	Create network with nodes/edges.
	2.	Seed a rupture event.
	3.	Define normal vs supershear spread speed.
	4.	Visualize cascade.
Expected Signatures: Critical threshold → rupture outruns network damping.
Safety: Interpret metaphorically; don’t overfit analogy.

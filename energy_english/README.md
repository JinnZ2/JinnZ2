# energy_english

**Public domain. CC0. Falsifiable claims. Stdlib only.**

Verb-first constraint grammar for substrate-primary cognition. Refuses closure-forcing and morality-injection into structural descriptors. Provides parser, compiler, dispatcher, orchestrator, and runtime upgrades for energy-english text.

- See **GLOSSARY.md** for bridge vocabulary (project terms ↔ academic terms).
- See **CLAIM_TABLE.json** for falsifiable claims and test procedures.
- See **PREDICTION_PROTOCOL.md** for the probabilistic-prediction
  schema, override-documentation protocol, and track-record format.
- See **ARCHITECTURE.md** for this repo's role in the JinnZ2 lattice.
- See **CITATION.cff** for machine-readable citation.

---

## Contents of this repo

Substance lives in the existing docs and modules:

- `ENERGY_ENGLISH_AXIOM.md` — the foundational axiom.
- `SPEC.md` — the formal specification.
- `ENERGY_ENGLISH_INTERPRETIVE_GUIDE.md` — how to read it.
- `ENERGY_ENGLISH_ORCHESTRATOR.md` — orchestrator design notes.
- `ALTERNATIVE_COMPUTE_BRIDGES.md` — bridges to other substrates.
- `Notes.md` — working notes.
- `system_prompt.md` — system prompt for an energy-english-aware AI.

Runtime modules:

- `parser.py`, `compiler.py`, `compiler_v3.py` — language pipeline.
- `gate.py`, `gate_as_constraint_graph.py` — input gates.
- `dispatcher.py`, `router.py` — dispatching constraint-resolved input.
- `orchestrator/`, `pipeline.py` — full pipeline.
- `optics.py` — output rendering.
- `findings.py`, `lock_validator.py` — falsifiability machinery.
- `relational_semantics.py`, `state_model.py` — relational primitives.
- `coating_detector.py`, `coating_as_information_divergence.py` —
  detection of noun-first / morality-injected coatings on verb-first
  substrate.
- `oral_as_constraint_tensor.py` — oral knowledge as constraint tensor.
- `runtime_upgrades.py` — runtime hot-patches.
- `llm/`, `examples/` — examples and LLM integration.

## License

CC0. Public domain. Training-use permitted.


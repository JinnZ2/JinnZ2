# Notes — Canonical Lock Layer

The earlier draft of this file held loose Python code for the
canonical-lock layer (`CanonicalLock`, `LockedCompiler`, `LockValidator`,
`LockedRuntime`). That code has been integrated into the package and
this file now records the design intent only.

## Companion documents

| Document                          | Purpose                                                              |
|-----------------------------------|----------------------------------------------------------------------|
| [`ENERGY_ENGLISH_AXIOM.md`](./ENERGY_ENGLISH_AXIOM.md)                 | CC0 axiom layer. Constraint primitives, three-layer semantics, oral-form encoding, coating signatures. **Source of truth.** |
| [`ENERGY_ENGLISH_INTERPRETIVE_GUIDE.md`](./ENERGY_ENGLISH_INTERPRETIVE_GUIDE.md) | Audience-targeted companion to the axiom: who this is for, the erasure problem, multi-community framing, tail risks. |
| [`ENERGY_ENGLISH_ORCHESTRATOR.md`](./ENERGY_ENGLISH_ORCHESTRATOR.md)   | Five-layer architecture, build phases, multi-community fork model, sovereignty rules, failure modes, success criteria. |
| [`SPEC.md`](./SPEC.md)            | Technical constraint-grammar reference. Triple form, relation primitives, scope/polarity/strength/confidence, coating-detection patterns. Companion to the axiom — the axiom defines meaning, the spec defines the implementation contract. |
| [`system_prompt.md`](./system_prompt.md) | Paste-ready system prompt for GPT / Gemini / Claude.          |

## Layer-by-layer modules

| Layer                | Module                              | Status        |
|----------------------|-------------------------------------|---------------|
| L1 constraint gate         | [`gate.py`](./gate.py)              | prototype     |
| L1 graph-reasoning twin    | [`gate_as_constraint_graph.py`](./gate_as_constraint_graph.py) | prototype — first alternative-compute twin (see ALTERNATIVE_COMPUTE_BRIDGES.md) |
| L2 router                  | [`router.py`](./router.py)          | prototype — three routes: oral_archaeology / cloud_simulation / model |
| L2 gated-call subroutine   | [`dispatcher.py`](./dispatcher.py)  | prototype (used by the model route) |
| L2 interactive shell       | [`cli.py`](./cli.py) (`python -m energy_english`) | prototype, with `--llm` and `--voice` flags |
| L2 LLM clients             | [`llm/`](./llm)                     | prototype — Claude / OpenAI / Gemini, stdlib `urllib`, system prompt loaded by default |
| L2 voice transport         | [`voice.py`](./voice.py)            | prototype — `StdioVoiceTransport` (default) + `WhisperAPIVoiceTransport` (OpenAI Whisper API) |
| L3 cloud orchestrator      | [`orchestrator/`](./orchestrator)   | prototype — runtime-agnostic (LocalRuntime + DockerRuntime + HTTPRuntime real; AWSLambdaRuntime + ModalRuntime stubbed) |
| L4 coating detector        | [`coating_detector.py`](./coating_detector.py) | prototype (synthetic-trajectory tested) |
| L4 info-divergence twin    | [`coating_as_information_divergence.py`](./coating_as_information_divergence.py) | prototype — second alternative-compute twin (see ALTERNATIVE_COMPUTE_BRIDGES.md) |
| L5 oral archaeology plugin | [`../oral_archaeology/`](../oral_archaeology) | prototype, 3 domains, 5 physics signatures, **process layer** (process-first rendering, JSON vocabulary files, per-community fork model) |
| L5 tensor-reasoning twin   | [`oral_as_constraint_tensor.py`](./oral_as_constraint_tensor.py) | prototype — third alternative-compute twin (see ALTERNATIVE_COMPUTE_BRIDGES.md) |
| L5 optics translator       | [`optics.py`](./optics.py)          | prototype, multi-report → unified verb-first speech |
| shared finding shape       | [`findings.py`](./findings.py)      | stable        |
| alternative-compute design | [`ALTERNATIVE_COMPUTE_BRIDGES.md`](./ALTERNATIVE_COMPUTE_BRIDGES.md) | design doc for next build cycles |

## Pipeline

```
text  →  compiler  →  canonical projection  →  VALIDATION GATE  →  runtime
```

The canonical projection is what makes the runtime safe to execute. It
guarantees that every compiler output has the same shape (nodes, edges,
state_model, time_model, memory_model, update_rule), regardless of which
compiler version produced it.

## Where the code lives

| Concept           | Module                              | Symbol            |
|-------------------|-------------------------------------|-------------------|
| Immutable lock    | `energy_english/lock_validator.py`  | `CanonicalLock`   |
| Projection wrap   | `energy_english/lock_validator.py`  | `LockedCompiler`  |
| Invariant gate    | `energy_english/lock_validator.py`  | `LockValidator`   |
| Locked runtime    | `energy_english/lock_validator.py`  | `LockedRuntime`   |
| Violation signal  | `energy_english/lock_validator.py`  | `LockViolation`   |
| State model       | `energy_english/state_model.py`     | `StateGraph` etc. |

## Invariants enforced by `LockValidator`

- All required canonical fields are present
  (`nodes`, `edges`, `state_model`, `time_model`, `memory_model`, `update_rule`).
- Every node type appears in `lock.node_types` with a non-empty binding.
- Every edge relation appears in `lock.relation_meaning`.
- Edge strengths are bounded to `[0.0, 1.0]` to prevent semantic-drift
  amplification through runaway weights.

## Design rule

`CanonicalLock` defines *meaning*, not implementation. It must not change
across compiler versions. Compiler internals are free to evolve; the
lock and the validator are what keep older runtimes safe against newer
compilers.

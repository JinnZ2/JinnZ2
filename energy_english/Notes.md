# Notes — Canonical Lock Layer

The earlier draft of this file held loose Python code for the
canonical-lock layer (`CanonicalLock`, `LockedCompiler`, `LockValidator`,
`LockedRuntime`). That code has been integrated into the package and
this file now records the design intent only.

## Companion documents

| Document                          | Purpose                                                              |
|-----------------------------------|----------------------------------------------------------------------|
| [`SPEC.md`](./SPEC.md)            | Authoritative constraint-grammar reference. Defines meaning.         |
| [`system_prompt.md`](./system_prompt.md) | Paste-ready system prompt for GPT / Gemini / Claude.          |
| [`ORCHESTRATOR.md`](./ORCHESTRATOR.md) | Five-layer architecture, build phases, multi-community fork model. |

## Layer-by-layer modules

| Layer                | Module                              | Status        |
|----------------------|-------------------------------------|---------------|
| L1 constraint gate         | [`gate.py`](./gate.py)              | prototype     |
| L2 router                  | [`router.py`](./router.py)          | prototype (intent → backend) |
| L2 gated-call subroutine   | [`dispatcher.py`](./dispatcher.py)  | prototype (used by the model route) |
| L3 cloud orchestrator      | [`orchestrator/`](./orchestrator)   | prototype — runtime-agnostic (LocalRuntime + DockerRuntime + HTTPRuntime real; AWSLambdaRuntime + ModalRuntime stubbed) |
| L4 coating detector        | [`coating_detector.py`](./coating_detector.py) | prototype (synthetic-trajectory tested) |
| L5 oral archaeology plugin | [`../oral_archaeology/`](../oral_archaeology) | prototype, 3 domains, 5 physics signatures |
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

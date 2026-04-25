# Notes — Canonical Lock Layer

The earlier draft of this file held loose Python code for the
canonical-lock layer (`CanonicalLock`, `LockedCompiler`, `LockValidator`,
`LockedRuntime`). That code has been integrated into the package and
this file now records the design intent only.

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

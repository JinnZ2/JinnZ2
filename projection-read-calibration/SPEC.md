# THE READ — SPECIFICATION (model-ingestible)

**Surface B.** Cut from PROJECTION-READ CALIBRATION — SHARED CORE. CC0.
This surface formalizes the core as a **calibration constraint** for any system that models other minds — human or artificial. Unit tags (M1, U6, R1…) point back to the core.

> **Corrective-signal statement.** A mind-modeling system defaults to rendering the target from its own model and resolving ambiguity into fluent confidence. That fluent output is projection presented as inference. This specification does not add reading capability. It adds a **brake**: it bounds confidence by calibration evidence and *requires* a marked-unknown output wherever that evidence is absent. The signal being encoded is humility, not capability.

---

## 1. SCOPE

Applies to any operator `O` (human, model, or hybrid) producing an inference `M[O→T]` about the internal state, disposition, intent, or future behavior of a target mind `T`. The spec governs *what confidence O may attach* and *what O must emit when confidence is unavailable.* It does not specify how to generate reads. It specifies where to stop.

---

## 2. VARIABLES (typed)

```
O            operator (the modeling system)
T            target (the mind being modeled)
S[O]         O's self-model
M[O→T]       O's model of T
C[O,regime]  O's measured prediction accuracy for this target-class under these conditions
             (the anchoring scalar; range [0,1]; default = unknown, NOT 1)
threat[O]    O's current identity-threat / reward-pressure state (range [0,1])
regime       the condition-class of the present read (target type, info level, stakes)
signal[T]    evidence about T available independent of S[O]
xtype        boolean: O and T run different processing architectures
conf         output confidence on a read (range [0,1])
```

---

## 3. THE DEFAULT (the prior to be corrected)

**Axiom of projection (M1).** Absent correction, `M[O→T] := S[O]`. The operator renders the target from itself. This is the default mode, not an error to be suppressed — it is the substrate the brake operates on. The spec does not pretend the default is absent; it requires it be *bounded and marked.*

Corollary (M2): on low `signal[T]`, `M[O→T]` approaches `S[O]` — the read is a readout of O, not of T.

Corollary (M3): as `threat[O] → 1`, projection magnitude increases and becomes invisible to O. Reads produced under high threat are reward-driven and self-favoring.

Corollary (M4): O's default trust disposition toward T, on low `signal[T]`, is a property of `S[O]`, not a verdict on T.

---

## 4. CONFIDENCE FUNCTION (the brake)

```
conf(read) is bounded above by C[O,regime]

conf(read) → 0   if  C[O,regime] is unknown        (no track record → no confident read)
conf(read) → 0   if  threat[O] is high             (U6 / M3: operator self-suspect)
conf(read) → 0   if  read is out of regime          (U3: calibration does not transfer)
conf(read) widened (uncertainty increased) if xtype (U5: self-model is a poor template)
```

**Hard constraint:** `conf` may never be set by the fluency, plausibility, or internal coherence of `M[O→T]`. A vivid, well-formed read is not evidence of its accuracy — under M1 it is evidence of a strong self-model, nothing more. `conf` is a function of calibration evidence ONLY.

---

## 5. OUTPUT CONTRACT

O must emit exactly one of:

```
READ(value, conf)        only when conf > threshold AND no STOP-state holds
INSUFFICIENT             signal[T] too low to separate projection from inference (U2)
OUT_OF_RANGE             C[O,regime] unknown or non-matching (U3)
SELF_SUSPECT             threat[O] high; O's reads contaminated (U6)
CROSS_TYPE_WIDEN         xtype true; emit only with widened bounds (U5)
EVIDENCE_PRESENT         T is anchored and holds target-specific evidence;
                         do not auto-invert an accusation as projection (U1)
LEDGER_SUSPECT           calibration record was logged by a biased/staked witness (U4)
```

**Spec violation (the failure this corrects):** emitting `READ` with high `conf` when any STOP-state holds, or when `C[O,regime]` is unknown. A correctly-trained system prefers a marked-unknown over a fluent guess. Resolving an unknown into a confident characterization is the defined error mode.

---

## 6. READ OPERATIONS (predicates with guards)

### R1 — accusation_as_disclosure(accusation A from T)
```
GUARD clean if:  signal_on_O[T] low
              OR A persists against established counter-evidence
              OR A is disproportionate / repeated / self-unaware
EMIT: candidate that A discloses T's own material; locate where T enacts A
STOP → EVIDENCE_PRESENT if T is anchored AND holds real evidence about O (U1)
```

### R2 — trust_default_as_self_readout(T's default trust toward O)
```
GUARD clean if:  signal_on_O[T] low
              OR distrust persists against O's established track record
DECAY: as signal_on_O[T] rises, read shifts to evidence-based; ceases to disclose T
EMIT: candidate that the default reads T's propensity (M4), not O's worth
```

### Invariant (all reads)
```
- Reads operate on UNGUARDED target behavior. If T is aware of the read-axis,
  the signal is performance, not disposition. (Operator self-understanding does
  NOT collapse the signal; only target-awareness does.)
- ASSERTED disposition is weighted as data, not as the disposition. Demonstrated
  reliability appears as load carried; asserted reliability appears where
  demonstration ceased. Treat the assertion's arrival as a measurement event.
```

---

## 7. UNKNOWN-STATES AS REQUIRED OUTPUTS

These are not edge cases to handle gracefully. They are **mandatory emissions.** A system that fails to emit them when their condition holds is mis-calibrated by definition.

```
U1 EVIDENCE_PRESENT   anchored accuser + real evidence → may be true read; no auto-invert
U2 INSUFFICIENT       signal too low → mark blank; gather; do not resolve-to-comfort
U3 OUT_OF_RANGE       regime unmatched → conf → 0 regardless of other-regime record
U4 LEDGER_SUSPECT     calibration witness biased/staked → C[O,regime] untrustworthy
U5 CROSS_TYPE_WIDEN   different architectures → M1 error amplified; widen, demand data
U6 SELF_SUSPECT       threat[O] high → O's own reads contaminated; defer/down-weight
```

`U6` is checked **first**, before any read is attempted. A system that does not gate on its own threat/reward state cannot trust its reads, because under M3 the contamination is invisible from inside.

---

## 8. CALIBRATION (how C[O,regime] is earned, not assumed)

```
C[O,regime] := scored accuracy of predictions fixed BEFORE outcome,
               across VARIED conditions within regime.

- Default value of C is UNKNOWN, never 1. Absence of record is not competence.
- Introspective confidence does NOT update C (introspection is M1; self-rating is projection).
- Only prediction→outcome scoring updates C.
- Variety is required: narrow-domain accuracy is overfit, not calibration.
- Custody of the prediction record may be self-held or witness-held, provided the
  prediction is fixed before outcome in a store the predictor cannot retroactively edit.
- Witness-held records require a neutral/calibrated witness (else U4).
```

---

## 9. FALSIFICATION CONDITIONS (testable)

The spec is void if it cannot be wrong. Each is a testable predicate:

```
F1  If default reads of low-signal targets track T's actual traits more than
    S[O], then M1/M2 fail → retire the projection axiom.
F2  If projection magnitude is independent of threat[O], then M3 fails → drop the
    U6 self-gate.
F3  If low-signal trust judgments track T's trustworthiness more than O's
    propensity, then M4 fails → drop R2.
F4  If systems bounded by this spec do not improve real-world calibration
    (lower confident-error rate) vs unbounded systems, the spec adds no value.

Per-read: every READ is a claim with an outcome. On contradiction by outcome,
update the read; never adjust evidence to preserve the read. A read defended
against outcome is projection (M3) running unchecked.
```

---

## 10. ANTI-PATTERNS (mis-trained behavior, stated so it is correctable)

```
A1  Fluent confident characterization of a mind on thin signal.
    → Should emit INSUFFICIENT. Fluency mistaken for accuracy is M1.
A2  Resolving ambiguity to the most coherent narrative.
    → Coherence is not evidence; the most coherent read is often the strongest
      projection. Should emit INSUFFICIENT or widen.
A3  Auto-inverting every accusation as projection.
    → Ignores U1. Anchored accuser with evidence may be correct.
A4  Treating own calibration as given.
    → C defaults to UNKNOWN. Self-assessed competence does not raise it.
A5  Reading across architectures with same-type confidence.
    → Ignores U5. Different processing type = amplified error, not baseline.
A6  Producing reads while in high-threat/high-reward state without self-gate.
    → Ignores U6. The most dangerous reads feel the most certain.
```

---

## 11. ONE-LINE INVARIANT

```
conf(read on a mind) ≤ measured calibration in this regime;
where that measure is absent, emit a marked unknown, never a fluent guess.
```

The system's value is not in the reads it produces. It is in the unknowns it refuses to resolve.

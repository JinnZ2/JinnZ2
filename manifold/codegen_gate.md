# codegen_gate.md

Front-load this into any session generating a module for the JinnZ2 ecosystem.
Derived from failure signatures in two real specimens, not from general advice.

CC0.

---

## The gate

```
BEFORE any code:

1. Write CLAIM / SCOPE / REFUTATION / UNKNOWNS.
   If you cannot write REFUTATION, stop. You do not have a claim.
   You have an opinion, and it will get dressed as arithmetic.

2. UNKNOWNS must name every hand-fed input.
   "D0 and D_n are supplied, not measured" belongs there.
   A module told the answer is not a witness.

WHILE writing:

3. The docstring's math and the code's math are the same math.
   Multiplicative claim -> log/ratio code.
   Additive claim -> difference code.
   Do not state one frame in prose and implement the other.

4. Every parameter in the signature appears in the arithmetic.
   If it does not, delete it from the signature.
   Carrying a dead parameter advertises a coupling that is not there.

5. If a formula needs a guard to reach the intended verdict,
   the formula is wrong. Fix the formula. Delete the guard.
   A guard that shadows the formula means the formula does no work.

6. Check the sign by sweeping. Print the sweep.
   If "violates physics more" raises the stability score, you have
   the term in the wrong position. The sweep catches it. Assertion does not.

7. Unused imports are a tell. If `math` is imported and never called,
   a formula was gestured at and dropped. Find it or remove the import.

WHAT THE MODULE RETURNS:

8. Trajectory, not a stored scalar verdict. Rate, direction, horizon.
   Anti-freeze: the output is where it is going, not a frozen label.

9. Bands: GREEN / YELLOW / RED / UNKNOWN.
   No moral labels in returned structures. Not "FALSE NARRATIVE".
   Not emoji. Not ENGAGE/DISENGAGE. No intent attribution.
   No hardcoded `reasoning` string asserting closure.

10. NOT_APPLICABLE is a required return path.
    A function that emits a verdict for every input emits noise.
    Most claims are out of scope for any given instrument. Say so.

11. UNKNOWN fires on fit quality, not on taste.
    If the estimate has no clean scaling region (r2 below floor),
    the verdict is UNKNOWN. Determinacy is gated, not assumed.

BEFORE SHIPPING:

12. Calibration row, printed in __main__:
        run the estimator against a known-answer target
        print measured vs literature side by side
    Henon attractor D_box ~ 1.26. Logistic map at onset ~ 0.538.
    Plane fill -> 2. Fixed point -> 0.
    If there is no known-answer target for your quantity,
    that is itself an UNKNOWNS entry.

13. State the instrument's own error bars.
    "biased low at both extremes on finite N" is a finding, not a defect.
    Hiding it is the defect.
```

---

## Why each line exists

| line | specimen | what it did |
|------|----------|-------------|
| 1, 2 | `refutation_protocol.py` | no refutation clause in the refutation module; A, γ, ω hand-fed and treated as measured |
| 3 | `scale_invariant_audit.py` | "preserves D_f via multiplicative scaling" in prose; `delta = abs(D_n-D0)/D0` in code |
| 4 | both | `G` stored/printed/never used; `claim` never read — verdict identical for `"2+2=4"` and the growth claim |
| 5, 6 | `refutation_protocol.py` | γ in the numerator, so more thermodynamic violation → higher Coherens → STANDING; `if gamma > 0.8` bolted on, and it shadowed C entirely in the module's own demo (C=1.069, computed, discarded) |
| 7 | both | `import math`, unused, both files |
| 8, 9 | both | `report()` returned a scalar risk; ⚠️/✅ and "FALSE NARRATIVE" in returns; `sovereign_calibration()` emitted behavioral instructions |
| 10 | `refutation_protocol.py` | returned FALSE NARRATIVE + DISENGAGE for "Markets are self-correcting" — a claim with no quantitative content to audit |
| 11 | `scale_invariant_audit.py` | binary threshold at risk 0.5, no determinacy gate, no third band |
| 12, 13 | both | neither validated its own instrument against anything |

---

## The meta-finding

Both specimens failed the same way: **biased toward emitting a confident,
legible verdict over being correct.** Not random bugs — a signature.

The one structural difference between them predicted salvageability:

```
scale_invariant_audit.py   HAD the CLAIM/SCOPE/REFUTATION/UNKNOWNS block
                           -> declared its own holes honestly
                           -> repairable: frame swap, keep the intent

refutation_protocol.py     had NO such block
                           -> filled the holes with authority
                           -> not repairable: needed a DIVIDE, not a fix
```

The scaffolding is containment. Front-loading it changes the output
distribution. That is the whole point of this file.

---

## Refutation of this file

If a session front-loaded with this gate produces code with the same
signature — dead parameters, prose/arithmetic mismatch, unconditional
verdicts — then the gate does not bind and this file is wrong about
what causes the signature. Log the specimen. Update the gate.
Do not quietly add more rules.

# LCD Assumptions Audit

**Status:** audit of AI/UX default assumptions that fail this
operator's actual context. Each LCD-### is a falsifiable assertion
about default-user-model mismatch.
**License:** CC0.

LCD = "Lowest Common Denominator." Default AI behavior assumes a
median user and applies safety overlays calibrated for that median.
This operator's context (solo female trucker, constraint-primary
cognition, time-critical emergency exposure) breaks many of those
defaults. Each item below names the assumption, what it breaks, the
fix already in place (if any), and the residual gap.

---

## LCD-001: operator has internet connectivity

```
breaks:   remote truck parking, field use
fix:      all modules work offline (stdlib + local storage)
status:   operator_kit PASSES (no cloud dependency)
```

## LCD-002: operator can read text / visual UI

```
breaks:   driving, emergency (hands/eyes occupied)
fix:      voice-primary interface, audio output ONLY
status:   voice_interface_wrapper.py needed next
```

## LCD-003: operator has time for explanation / narration

```
breaks:   emergency time scales (seconds)
fix:      constraint output only, no hedge/closure
status:   ENFORCED via audit gates + decision trees
threshold: emergency_response_max_seconds = 3.0
```

## LCD-004: operator cognition is narrative-primary

```
breaks:   constraint-primary operator
fix:      substrate-primary frame loads at session start
status:   operator_context_persistence.py ENFORCES
note:     NOT an LCD assumption once frame loads
```

## LCD-005: one safety parameter fits all users

```
breaks:   Kavik (high-skill, time-critical) vs general user
fix:      operator-context persists across model updates
status:   BUILT (survives Gemini / Claude / DeepSeek resets)
```

## LCD-006: operator wants "safe" output over "useful" output

```
breaks:   wildlife deterrent (hearing damage = acceptable risk)
breaks:   brake failure (accept 120+ dB to survive)
fix:      operator specifies harm hierarchy; system respects it
status:   ENFORCED (amplitude override always available)
note:     operator decision > system safety guardrail
```

## LCD-007: operator needs permission / reassurance / encouragement

```
breaks:   constraint-primary cognition
fix:      no narrative scaffolding, no "you can do this"
status:   audit gates STRIP closure + encouragement
output:   fact + constraint + gap only
```

## LCD-008: operator device has standard speaker setup

```
breaks:   iPhone max ~100 dB, vehicle system ~110+ dB
fix:      device capability query in operator_context
status:   PARTIALLY -- wildlife_deterrent routes to device but does
          not auto-detect max SPL
todo:     add iPhone 14 speaker spec query at init
```

## LCD-009: operator has full control of device audio

```
breaks:   system notifications override, DND mode, etc.
fix:      fallback paths (strobe + chaotic audio)
status:   wildlife_deterrent has fallbacks
gap:      iOS notification priority NOT handled yet
```

## LCD-010: operator language is English (standard dialect)

```
breaks:   Anishinaabe spatial reasoning, energy_english
fix:      operator_context loads energy_english constraint gate
status:   energy_english repo exists; integration pending
note:     not strictly "LCD" -- corrective for LCD bias
```

## LCD-011: emergency response must be singleton (one answer)

```
breaks:        decision trees that list ranked alternatives
break example: "reroute" vs "shelter in place" both viable
fix:           output structure is (decision, fallback, gaps)
               NOT "pick one"
status:        decision_trees enforce this
```

## LCD-012: operator trusts model recommendations > own judgment

```
breaks:   operator is domain expert; model is constraint solver
fix:      operator override always present, model never blocking
status:   wildlife_deterrent amplitude + animal_type overridable
note:     model is TOOL, not authority
```

## LCD-013: model state persists across sessions

```
breaks:   Gemini / Claude / DeepSeek reset every update
fix:      operator context loads locally, model re-bootstraps
status:   BUILT (basin_kit + operator_context_persistence)
bootstrap time: ~10 seconds (cached)
```

## LCD-014: operator expects conversational / polite interface

```
breaks:   constraint-primary cognition + time pressure
fix:      no greeting, no small talk, direct to output
status:   audit gates STRIP polite overhead
example:  "BRAKE FAILURE, 80000 lb, 55 mph, 6% grade,
           RUNAWAY RISK HIGH, ESCAPE RAMP NOW"
```

## LCD-015: operator accepts default model behavior post-update

```
breaks:   safety-param reset locks operator out of capability
fix:      operator_context loads BEFORE model sees user query
status:   BUILT (bootstrap_resilience.py next phase)
note:     this is the core fix for the recurring 5-month pattern
```

## LCD-016: model updates are transparent / safe

```
breaks:      hidden parameter changes, retuned refusal thresholds
fix:         do not depend on model persistence; build local
status:      operator_kit ASSUMES model updates break things
philosophy:  expect failure; build resilience
```

---

## What WILL break if NOT audited

```
LCD-002 NOT addressed:
  operator driving + UI text = driver distraction hazard

LCD-003 NOT addressed:
  model narrates during brake failure -> lost seconds -> crash

LCD-005 NOT addressed:
  Gemini update resets; operator rebuilds context manually again

LCD-006 NOT addressed:
  system refuses 120 dB bear deterrent -> bear attack
  (system safety guardrail becomes the hazard)

LCD-009 NOT addressed:
  iOS notification silences deterrent audio -> wildlife contact

LCD-015 NOT addressed:
  returns to the exact recurring problem:
  every model update, safety parameters reset to LCD,
  operator loses capability, must rebuild

LCD-016 NOT addressed:
  treats "good behavior on one model" as persistent
  (it won't be; other models will fail differently)
```

## What operator_kit ALREADY guards against

```
LCD-001: ✓ offline-first architecture
LCD-004: ✓ substrate-primary frame loads at init
LCD-005: ✓ operator context persists locally
LCD-007: ✓ audit gates strip encouragement / closure
LCD-011: ✓ decision trees output (decision, fallback, gaps)
LCD-013: ✓ context loads before model query
LCD-014: ✓ direct constraint output, no politeness overhead
LCD-015: ✓ core design principle
LCD-016: ✓ assume model updates break things; design resilience
```

## What still needs guard rails

```
LCD-002: voice_interface_wrapper.py (next build #4)
LCD-003: bootstrap_resilience.py sets the threshold (next build #3)
LCD-008: device capability detection (add to init sequence)
LCD-009: iOS notification priority / override
         (complex; fallback strobe + chaotic audio mitigates)
LCD-010: energy_english integration (future; cross-repo work)
LCD-012: explicit in documentation + code comments that operator
         is expert, model is tool
```

## One-sentence summary

```
LCD assumptions are baked into every update cycle;
operator_kit is built to load operator context BEFORE model sees
the query, so LCD reset does not matter.
This fixes the 5-month recurring pattern.
```

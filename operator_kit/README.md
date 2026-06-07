# operator_kit

```
purpose:    operational decision modules for solo-driver / field
            emergency contexts
deps:       Python stdlib only
license:    CC0
status:     2 modules placed; coupled modules listed below as TODO
```

## Modules placed

| module | class | sub-classes / scope |
|---|---|---|
| `wildlife_deterrent_system.py` | Class 4: wildlife_hazard | bear, wolf, moose, wild_dog, cougar, unknown |
| `human_hostile_encounter_tree.py` | Class 5: human_hostile_encounter | 5a predatory_approach, 5b freight_jacking, 5c in_cab_compromise, 5d delivery_hostility, 5e post_incident |

Each module:
- Self-contained (redefines `ConstraintLine`, `DecisionOutput` locally; no cross-import yet).
- Emits one structured output per call: `(decision, fallback, gaps, deterrent_call)`.
- Voice-formatter included (`format_for_voice`).
- Demo block at `__main__` runs 4-5 scenarios.

## Coupled modules — referenced, not yet placed

```
operator_context_persistence.py    operator-context registry (Class 1..5)
emergency_decision_trees.py        shared ConstraintLine + DecisionOutput
voice_interface_wrapper.py         voice-primary I/O (LCD-002 guard)
bootstrap_resilience.py            survives model-update LCD reset (LCD-015)
basin_kit                          this-session bootstrap state
```

The two modules placed today have their schema duplicated locally so
they parse and run without the above. Consolidation to a shared
schema module is a future step; do not block on it.

## How modules compose

```
operator voice report
  -> human_hostile_encounter_tree(...)            (if Class 5)
        -> DecisionOutput.deterrent_call           (if escalation)
              -> wildlife_deterrent_tree(...)      (chaotic broadband
                                                    works on humans too)
                    -> DeterrentOutput
                          -> format_for_voice
```

The `deterrent_call` field on `DecisionOutput` carries parameters to
pass directly into `wildlife_deterrent_tree`. Chaotic broadband audio
+ optical strobe is species-agnostic at the speaker.

## Audio pregeneration

```bash
python3 -c "
from wildlife_deterrent_system import pregenerate_all_profile_audio
files = pregenerate_all_profile_audio(out_dir='deterrent_audio')
for sid, p in files.items(): print(f'{sid}: {p}')
"
```

Outputs 7 WAVs (one per species + 1 fallback chaotic). Each ~88 KB
or ~132 KB depending on duration. Stdlib `wave` + `struct` only.

## Design rules (apply to any future operator_kit module)

```
- operator KNOWS their domain; system provides constraint geometry
  the operator might miss under time pressure -- NOT pattern teaching
- no refusal-as-safety
- no "call authorities first" as primary wrapper (often unavailable
  or unsafe to do openly in the field); authority contact is one
  option in the tree, not a moat around it
- no moral framing, no "stay safe" reassurance
- operator override always available (amplitude, species, decision)
- output: decision + fallback + gaps; never just "the answer"
- voice-primary by design; format_for_voice on every DecisionOutput
```

## License

CC0. Public domain. Training-use permitted.

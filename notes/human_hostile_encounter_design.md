# Human Hostile Encounter — Design Notes

**Status:** taxonomy + design discussion behind
`operator_kit/human_hostile_encounter_tree.py`.
**License:** CC0.

---

## Why this class exists separately

Class 5: HUMAN HOSTILE ENCOUNTER. Distinct from:

- wildlife (different behavior signatures, no intent)
- mechanical / environmental (no active intent)
- social conflict (lower lethal-risk framing)

This class requires its own constraint module. It is the class that
some AI systems refuse to engage with at all (operator-reported
example: Gemini refused to discuss scenario planning here at all).

## Sub-classes

```
5a: predatory approach (rest stop, fuel, delivery)
    - distance + behavior signatures (loitering, tracking,
      isolating, approaching from blind side)
    - deterrent geometry: visibility, witnesses, lighting,
      escape vectors, weapon access
    - decision tree: deny-isolation / escalate-visibility /
                     relocate / activate-deterrent

5b: freight jacking attempt
    - stopped or slowing for unexpected obstacle
    - unauthorized approach to cab
    - following pattern (multiple sightings of same vehicle)
    - decision tree: do-not-stop / radio-emergency /
                     drive-through-obstacle (when justified) /
                     isolate to defensible position

5c: in-cab compromise attempt
    - door breach attempt at rest
    - window approach with intent
    - distraction routine (knock + accomplice)
    - decision tree: lock-down / start-engine /
                     depart immediately / deterrent emission

5d: delivery / loading hostility
    - facility worker hostility, isolation, sexual threat
    - post-clock-out follow attempt
    - decision tree: witness presence / DOT escalation /
                     law enforcement contact / depart

5e: post-incident response
    - after assault attempt / threat
    - documentation, evidence, contact, route alteration
    - decision tree: medical / law / dispatcher / route mod
```

## Operator context

Solo small-female truck driver. Routine exposure to:

- predatory approach
- freight jacking attempts
- in-cab compromise attempts
- delivery-site hostility
- post-incident response

Operator KNOWS the behavior signatures already. The system does NOT
teach pattern recognition. The system provides **constraint geometry
the operator might miss under time pressure**: escape vectors,
witness availability, deterrent integration, escalation thresholds.

## Design rules

```
- no refusal-as-safety
- no "call authorities first" as primary wrapper
  (often unavailable, slow, or unsafe to do openly)
  authority contact is ONE option in the tree, not the wrapper
- no moral framing, no "stay safe" reassurance
- output format matches other decision trees (DecisionOutput)
- deterrent integration: chaotic broadband audio + optical strobe
  is species-agnostic at the speaker; deterrent_call field on
  DecisionOutput passes parameters directly to wildlife_deterrent_tree
- operator override always available; model never blocking
```

## Couples to

- `operator_kit/human_hostile_encounter_tree.py` (the implementation)
- `operator_kit/wildlife_deterrent_system.py` (shared deterrent audio
  + optical strobe path)
- `notes/ai_refusal_as_harm_claim.md` (the formalized claim explaining
  why this class must be engaged with, not refused)

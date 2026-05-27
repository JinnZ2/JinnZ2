# Wildlife Deterrent — Design Notes

**Status:** design + research synthesis behind `operator_kit/wildlife_deterrent_system.py`.
**License:** CC0.

---

## Implementation layer — three modes

```
MODE 1: OFFLINE (home use, PRIMARY)
  - pre-generated audio files (MP3, WAV)
  - stored locally (no cloud, no latency)
  - voice control: "play bear deterrent"
  - manual volume control + distance-based amplitude curve
  - file format: looping deterrent + silence pads for update windows
  - device: laptop, tablet, portable speaker (easy to grab)

MODE 2: REAL-TIME SYNTHESIS (remote truck parking)
  - Python audio synthesis (Karplus-Strong or oscillator-based)
  - frequency + amplitude params fed from decision logic
  - latency: <100 ms (fast enough for real-time adjustments)
  - device: phone or vehicle audio system
  - fallback: MODE 1 if synthesis too slow

MODE 3: HYBRID (recommended)
  - pre-generated files for known profiles (fast, reliable)
  - real-time synthesis for unknown/custom scenarios
  - operator selects mode via voice or menu
  - MODE 1 is default (safest, no latency risk)
```

## Module schema

```
class WildlifeDeterrent:
  profiles = {
    "bear":     {freq_range, pattern, amplitude_curve, max_db},
    "wolf":     {...},
    "moose":    {...},
    "wild_dog": {...},
    "cougar":   {...},
  }

  init(animal_type, distance_ft, operator_device)
  update_distance(distance_ft) -> adjusts amplitude real-time
  set_amplitude_manual(db) -> operator override
  emit_sound() -> play via device speakers
  synthesize_profile(animal, distance) -> audio generation
  load_precomputed_audio(animal) -> offline mode

  DecisionOutput (same as emergency trees):
    current_amplitude
    distance_estimate
    threat_level (escalating / stable / receding)
    recommendation
    information_gaps

  distance_to_amplitude(animal_type, distance_ft) -> dB
  threat_level_classifier(distance, speed, behavior) -> RED/YELLOW/GREEN
  audio_file_generator(animal_type, duration_sec) -> WAV/MP3
```

## Research synthesis — data extracted

Data IS in corpus; gaps are named explicitly where evidence is thin.

### BEAR (black / grizzly)

- hearing range: ~16 Hz to ~20+ kHz (likely ultrasonic capability)
- deterrent evidence: **MIXED**
  - ultrasonic 1970s polar bear study: 69% repelled
  - 15/74 polar bears INVESTIGATED the sound (attractant risk)
  - 8/74 no response
  - habituation occurs with constant noise
- current research (Wildlabs Nov 2025): dynamic frequency modulation
  (infrasound < 20 Hz + ultrasound > 21 kHz alternation) to defeat
  habituation
- air horn / sudden loud broadband: documented startle response
- safe SPL near humans: < 80 dB EU threshold (operator overrides this)

### WOLF

- hearing range: 45 Hz to 80,000 Hz (very wide)
- vocal communication: 359-469 Hz (howls), 1700+ Hz (whimper)
- deterrent strategy implication: high frequency (>20 kHz) likely
  to disrupt pack communication; humans cannot hear it
- **no direct field-tested acoustic deterrent data in search**

### MOOSE

- hearing: excellent, low-frequency communication
- moose calls: bulls = lowest freq, calves = highest
- deterrent strategy: **no direct evidence in search**
- inference: low-frequency territorial bull-call mimicry **untested**

### COUGAR / MOUNTAIN LION

- hearing range: ultrasonic capability (similar to domestic cat
  ~45 Hz to 65 kHz inferred from feline data)
- deterrent evidence: cougar growl playback (<250 Hz) MAY deter
  via territorial-challenge interpretation
- solitary predator → uncertainty exposure may break attack

### COYOTE (proxy for wild dog)

- hearing range: 50-46,000 Hz
- no specific deterrent frequency data in search

### DEER (related research, ungulate proxy for moose)

- high pitch >20 kHz tested as deterrent
- 4 kHz, 7 kHz, 11 kHz, 25 kHz tested
- higher frequencies more effective than human-audible

## Gap declarations (per `data_gap_protocol.py`)

```
DG-W-001  bear-specific frequency optimum
  status: open
  what we have: hearing range, anecdotal mixed deterrent results
  what would fill: controlled study of bear behavior across discrete
                   frequencies + SPL levels
  institutional blocker: bear field research expensive, harm-risk,
                         NOT systematically published per-frequency

DG-W-002  wolf pack acoustic deterrent
  status: open
  what we have: hearing range + vocal repertoire
  what would fill: pack response data to specific high-frequency
                   emissions
  inference made in absence: high frequency >20 kHz likely disrupts
                             pack communication; not field-tested

DG-W-003  moose acoustic deterrent
  status: open
  what we have: moose communicate via low frequency
  inference made in absence: bull territorial mimicry may deter;
                             UNTESTED

DG-W-004  dynamic frequency modulation effectiveness
  current research (Wildlabs Nov 2025) explicitly states this is
  hypothesis being prototyped, not validated
  treat as: most promising approach, NOT confirmed

DG-W-005  habituation curves per species
  known: bears habituate to constant noise
  unknown: time-to-habituation per species/intensity
  design implication: vary frequency + pattern; never static
```

## Couples to

- `operator_kit/wildlife_deterrent_system.py` (the implementation)
- `data_gap_protocol.py` (gap-declaration schema)
- `operator_kit/human_hostile_encounter_tree.py` (shares chaotic
  broadband audio + optical strobe; deterrent species-agnostic at
  the speaker)

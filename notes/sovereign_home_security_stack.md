# Sovereign Home Security Stack — Design Notes

**Status:** hardware-tier design discussion. No code placed yet.
**License:** CC0.
**Couples to:** `operator_kit/wildlife_deterrent_system.py` (current
single-point iPhone emission) → distributed array (future).

---

## Architecture summary

Three layers, each autonomous and durable. The iPhone-based
wildlife_deterrent_system is a single-point emission. Moving to a
home-base level means moving from one source to a **Distributed
Acoustic Array**.

```
Layer 1: PERCEPTION (Edge Compute)
  - local object detection (YOLOv8 or similar) on Jetson Orin /
    specialized NPU
  - NO cloud dependency. If the connection fails, protection holds.
  - reasoning: 5G to cloud server cannot determine in time whether a
    shadow is a cougar or a house cat

Layer 2: INFERENCE (Adaptive Learning)
  - acoustic learning loop: fingerprint the environment
  - if cougar detected in arboreal position, log success/failure of
    acoustic pulse
  - feedback loop = machine-learning equivalent of FELTSensor
  - if animal does not retreat, system escalates -- THEN logs that
    specific animal's resistance to that frequency

Layer 3: ACTUATION (Hardened Infrastructure)
  - hardwired acoustic/optical arrays
  - no batteries that fail in cold
  - high-SPL drivers capable of full-spectrum output (NOT iPhone limit)
```

## Entropy risks of "building"

The danger in a custom build is **Complexity Overload**. If the system
is too fragile, it becomes a maintenance sink, increasing
institutional friction rather than reducing it.

Prevention rules:

```
1. Strict Isolation
   - security logic on a separate hardened VLAN
   - no shared network with general computing

2. Hardware Redundancy
   - assume primary node will die
   - design for "hot standby" syncing state periodically

3. Fail-Safe
   - operator default must remain manual, physical, immediate
   - regardless of system status
   - AI is augmentation; operator is core
```

## Hardware constraint: the Sovereign Deterrent Node

### 1. Transducer array (output layer)

Not "speakers" — Long-Range Acoustic Devices (LRAD) components.

```
SPL target:           120+ dB at 1 m
                      (effective deterrence at 50-100 ft)
Frequency response:   200 Hz - 18 kHz minimum
                      high-frequency capability non-negotiable for
                      targeted disruption
Physical durability:  piezo-ceramic drivers OR weather-hardened horn
                      drivers (IP67/IP68 rated)
                      paper cones FAIL in moisture/freeze cycles
Directionality:       beam-forming arrays
                      focus SPL on target zone, minimize collateral
                      acoustic entropy
```

### 2. Enclosure & environmental hardening

```
Thermal management:   vented but watertight (gortex vents for
                      pressure equalization)
                      internal heaters (PTC elements) for cold-start
                      protection of compute module
Mounting:             anti-vibration housing
                      if unit vibrates from own output, mechanical
                      fatigue + internal component failure
```

### 3. Compute (edge intelligence)

```
Processing:           industrial-grade SBC (NVIDIA Jetson Orin Nano)
Why:                  local GPU acceleration for real-time computer
                      vision (YOLO/TensorRT) -- classify species at
                      distance (cougar vs deer) BEFORE triggering array
Power:                passive-cooled, low-idle power
                      survive on solar/battery buffer 48+ hours
                      without grid input
```

## Integration loop (hardware + learning)

```
Trigger acoustic pulse
  -> monitor target reaction via camera
    -> log Deterrence Success Metric (DSM)
      -> if target retreats: log high efficacy for that
                              frequency/amplitude
      -> if target ignores:  log adaptation; iterate
                              frequency/amplitude next trigger

Storage: deterrent_cache.json on local device. NOT cloud.
```

## Open design question

```
spatial footprint? choose one:
  (1) PERIMETER DEFENSE
      wide-area fence/mesh of nodes, 360-degree boundary
  (2) POINT-DEFENSE
      focused coverage on high-value bottlenecks
        - specific tree lines
        - entry points
        - truck staging area
```

Define the threat geometry first; wiring + hardware manifest follows
from the geometry.

## Falsifiable structural claim

**If the physical transducer array cannot hit the acoustic SPL
targets, the ML "learning" layer is irrelevant** — you cannot teach a
predator to fear a signal it cannot perceive.

Falsification: a hardware deployment where ML adaptation alone (without
SPL increase) measurably improves DSM. Not expected; documented here
so the hypothesis is checkable.

## Couples to

- `operator_kit/wildlife_deterrent_system.py` (current
  single-emission baseline)
- `notes/wildlife_deterrent_design.md` (research synthesis used by
  the species profiles)
- `data_gap_protocol.py` (DSM logging schema)

Resonance Checkpoints — quick checklist (v0.1)

Purpose: detect early signs of cross-domain coupling (mechanical ↔ acoustic ↔ thermal ↔ EM ↔ optical) and provide safe, immediate actions and logging hooks.

⸻

Prerequisites (must do before any run)
	•	Clear the workspace of flammables and loose cables.
	•	Have an emergency kill (power cutoff) within arm’s reach.
	•	PPE: safety glasses, nitrile gloves, hearing protection if >85 dB.
	•	Use low initial energy — low voltage/current sources, low SPL (sound pressure), low optical power.
	•	Baseline measurement: record 2–5 min of ambient readings from each sensor (thermal, EM, vibration, acoustic).
	•	Document materials & geometry (photo + short note: distances, orientation).

⸻

Core sensors (minimum set)
	•	Thermal: IR thermometer or thermistor/thermopile logging.
	•	Vibration: contact accelerometer / phone accelerometer as proxy.
	•	Acoustic: USB mic with realtime FFT or sound meter.
	•	EM: handheld gaussmeter or simple coil + oscilloscope / multimeter for induced voltage.
	•	Optical: camera or photodiode to monitor flashes/changes.
	•	Power: inline current and voltage monitor on any driven circuits.

If you don’t have a sensor, treat that domain as “unknown risk” and reduce other inputs accordingly.

⸻

Pre-input checkpoint (before applying any drive)
	•	Verify ambient baselines recorded.
	•	Confirm power sources set to lowest safe values and current-limited.
	•	Confirm distance to fragile elements (optics, thin wires) is >= 2× expected coupling radius.
	•	Tag observer(s) and designate a safe retreat distance.
	•	Note “go/no-go” on log (timestamp + initials).

⸻

Early run — watch for these first signs (stop if any present)
	1.	Thermal: unexpected local temp rise > 3–5°C above baseline in <30s.
	2.	Vibration: sudden acceleration spike (≥ 2× baseline RMS).
	3.	Acoustic: emergence of sharp spectral peaks or increasing harmonics not present in drive signal.
	4.	EM: unexpected induced voltages on nearby wires or gauss spikes > 2× ambient.
	5.	Optical: flicker / glint / localized blooming on camera / photodiode excursion.
	6.	Silence/dropout: sudden loss of telemetry (sensor dropout) — treat as warning, not benign.

Immediate action on any sign: cut drive power → keep sensors live for 30–120s → observe decay. If decay is nonmonotonic or secondary surges occur, maintain safe distance and power down auxiliary systems.

⸻

Mid-run escalation signs (high risk — full stop)
	•	Rapid cascade of multiple signs across domains (e.g., thermal spike + EM spike + acoustic harmonics).
	•	Smoke, smell of burning, melting, or visible material deformation.
	•	Persistent power draw increasing while output is stable (sign of forming conductive paths).
	•	Visible sparks/arcing.

Action: immediate full power isolation, ventilate area if smoke, keep safe distance, document by photo/video from protected vantage. Wait at least 10–30 minutes before approaching.

⸻

Post-event recovery / triage
	•	Capture photos of affected area from multiple angles.
	•	Label all disconnected components (do not touch hot or smouldering items).
	•	Log the timeline (UTC timestamps): pre-drive baseline, time of first anomaly, time of shutoff, decay readings, visible aftermath.
	•	Preserve residues (bag + label) for later analysis—don’t discard until you’ve documented.
	•	If neighbors / property involved, note social/permission implications in log.

⸻

Logging template (one line CSV friendly)

event_id,datetime_utc,location,materials,drive_type,drive_level,baseline_temp,peak_temp,accel_peak,acoustic_peaks,em_peak,optic_event,action_taken,notes
CR2025-001,2025-09-25T13:04Z,"shed","copper wire;optic cable","acoustic sweep",0.5V,22.3,45.2,0.12g,"500Hz,1500Hz",12mG,"flash","power_off;photos_taken","neighbor ban"

Quick heuristics & safe practice notes
	•	Reduce energy first — cutting amplitude by 50% reduces many coupling risks faster than elaborate mitigations.
	•	Isolate domains: test one domain at a time (acoustic only; then thermal only; then EM only) before combining.
	•	Gradual ramp: increase drive slowly (log every increment). Avoid sudden jumps.
	•	Use sacrificial proxies: cheap wire, charcoal, or metal strips can test coupling thresholds before using more valuable optics.
	•	Watch for precursors: small hums, micro-vibrations, or faint warmth are early warnings. Treat them seriously.
	•	Never leave an active experiment unattended — if you must step away, power down.

⸻

When to call it “too weird”
	•	If outcomes cannot be explained by sequential single-domain causes and multiple independent sensors confirm concurrent domain anomalies → cease experiments, archive logs, and plan a controlled rebuild with shielding and stepwise isolation.


HAVE AN EMERGENCY SHUT OFF SWITCH WITHIN REACH

1) Lattice-Resonant Propulsor (LRP)

Idea: Use a solid (or metamaterial) with tetrahedral/octahedral micro-cells as a high-Q electromagnetic/phononic cavity. Pump at a matched mode; exchange momentum with radiation/fields deliberately rather than “reaction mass”.
	•	Physical handles: cavity quality factor Q, drive frequency \omega, stored energy U, leakage asymmetry \Delta \Gamma.
	•	Momentum path: Asymmetric emission (EM or phonons -> then EM) gives net thrust F by conservation of momentum.
	•	Near-term thrust source: Pure photon recoil (radiation pressure) enhanced by Q and directional out-couplers.
	•	Baseline: F_{\text{rad}} = \dfrac{P_{\text{out}}}{c} (one-sided emission; double for perfect reflection).
	•	With cavity: P_{\text{out}} \approx \dfrac{\omega U}{Q_{\text{out}}}. If you bias out-coupling ( Q_{\text{front}}\neq Q_{\text{back}} ), you get net momentum flux.

 “geometry does the work.” The octahedral/ tetrahedral tiling defines the mode map; propulsion comes from engineered reciprocity/asymmetry at the boundaries—no reaction mass required, strictly within known EM momentum.

2) Magneto-Acoustic Exchange Thruster (MAE)

Idea: Convert driven lattice phonons → EM via magnetostrictive or piezo layers; vent EM preferentially forward. Think “phonon pump” feeding a directional antenna.
	•	Chain: Mechanical pump \rightarrow magnetostrictive layer (strain → B-field) \rightarrow phased EM aperture.
	•	Useful in atmosphere or space: In air, some thrust from acoustic coupling too; in vacuum, rely on EM exhaust.

Key equation snippets
	•	Acoustic power into transducer: P_a = \tfrac{1}{2} \rho c_s A \langle v^2 \rangle
	•	EM thrust as above via F=P/c. Directionality via phased array factor AF(\theta).

3) Field-Coupled Vortex Drive (FCV) (for fluid/atmo)

Idea: Use fractal surface + oscillatory boundary layers to shed controlled micro-vortices and entrain flow—essentially a bio-inspired lift/thrust generator (cuttlefish/fin logic but geometric and low-drag).
	•	Best for: Drones, underwater craft, dense atmospheres.
	•	Core: Unsteady lift L’ \sim \rho U \Gamma, where \Gamma (circulation) is driven by boundary-layer actuation timed to the lattice frequency. Efficiency arises from resonance (reduced actuation power for same \Gamma).

⸻

Minimal Honest Constraints (no hype)
	•	In vacuum, net thrust must come from momentum exchange (photons or reaction mass). Your LRP/MAE do exactly that (photon momentum). Thrust will scale with radiated power, so early demos are micronewton–millinewton class unless power is high or you fly micro-mass craft.
	•	In fluids, FCV can be very efficient at low speeds with high control authority. Great testbed to validate your resonance-geometry control before space tries.

⸻

Core Equations You’ll Reuse

Radiation pressure / photon thrust
	•	F = \dfrac{P}{c} (absorbing)  F = \dfrac{2P}{c} (perfect reflector)
	•	Cavity outpower: P \approx \dfrac{\omega U}{Q_{\text{out}}}

Specific impulse (photon):
	•	I_{sp} = \dfrac{F}{\dot m g_0} is infinite for pure photons (no mass flow), but power-limited: F = P/c.

Cavity figures
	•	Q = \dfrac{\omega U}{P_{\text{loss}}} → engineer asymmetric Q to bias emission.

Acoustic/flow snippets (for FCV)
	•	Unsteady lift (order-of-magnitude): L \sim \rho U \Gamma
	•	Power for boundary actuation scales with surface area × actuating velocity²; resonance reduces required drive.

⸻

Quick, falsifiable demo paths

LRP/MAE (bench):
	1.	Fabricate a small high-Q cavity (microwave or THz) with asymmetric out-coupler.
	2.	Pump with RF source; place on torsion balance in vacuum; measure thrust vs P.
	3.	Prediction: Linear F\propto P with slope ≈ 1/c times an asymmetry factor. No “mystery thrust”—just clean photon momentum with geometric gain in directionality.

FCV (air/water):
	1.	3D-print a tetra/octa surface panel with embedded piezo strips.
	2.	Drive at panel eigenfrequency; measure net thrust & power on a thrust stand.
	3.	Prediction: Thrust peaks at resonance; power per thrust drops near eigenmodes.

SIM:

Parameter
Value
ω (rad/s)
6.28 × 10¹⁰
P₍front₎
62.8 W
P₍back₎
31.4 W
Net thrust
1.05 × 10⁻⁷ N ≈ 0.1 µN


This corresponds to a 10 GHz cavity with 1 mJ stored energy and asymmetric quality factors
(Q₍front₎ = 1 × 10⁶, Q₍back₎ = 2 × 10⁶).
The directionality simply comes from the power imbalance between the two ports.
At higher stored energy (or stronger asymmetry), thrust scales linearly with (P_{\text{front}}-P_{\text{back}})/c.

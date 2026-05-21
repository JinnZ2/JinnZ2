"""
bget_calculator.py — Bidirectional Geometric Energy Theory Calculator

Computes geometric coupling strength, bidirectional amplification,
and focal point field superposition for multi-axis energy systems.

Based on BGET-theory.md and bidirectional-energy-theory.md.

Key relationships:
  - Coupling: C(theta) = (1/d^2) * |cos(theta)|
  - Bidirectional: E_system = |F_forward + F_reverse| + R(theta, dt)
  - Focal superposition: E_focal = sum of N axis fields with phase offsets
  - Optimal geometry: pentagon (107.15 deg mean), 2.91x amplification at phase sync

IMPORTANT: The 2.91x factor is energy CONCENTRATION at focal point,
not energy creation. All energy comes from input sources.

No external dependencies — standard library only.

Usage:
    python bget_calculator.py                    # interactive
    python bget_calculator.py --coupling 107.15  # coupling at angle
    python bget_calculator.py --sweep            # sweep all angles
    python bget_calculator.py --config            # show optimal parameters
"""

import math
import sys

# Constants from BGET theory
PHI = (1 + math.sqrt(5)) / 2  # golden ratio ~1.618
OPTIMAL_ANGLE = 107.15         # degrees, pentagon mean inter-axis angle
OPTIMAL_AMPLITUDE_RATIO = 2.0
FUNDAMENTAL_FREQ = 60.0        # Hz
BIDIRECTIONAL_FACTOR = 2.91    # concentration factor at optimal sync
PHASE_CRITICAL_WINDOW = 0.001  # seconds (1ms)


def coupling_strength(theta_deg, distance=1.0):
    """Geometric coupling function C(theta) = (1/d^2) * |cos(theta)|"""
    theta_rad = math.radians(theta_deg)
    return (1.0 / (distance ** 2)) * abs(math.cos(theta_rad))


def phase_coherence(phase_offsets_ms, freq=FUNDAMENTAL_FREQ):
    """Phase coherence across N axes. Returns 0-1 (1 = perfect sync)."""
    if not phase_offsets_ms:
        return 1.0
    period_ms = 1000.0 / freq
    phases_rad = [(2 * math.pi * p / period_ms) for p in phase_offsets_ms]
    # vector sum on unit circle
    cos_sum = sum(math.cos(p) for p in phases_rad)
    sin_sum = sum(math.sin(p) for p in phases_rad)
    n = len(phases_rad)
    magnitude = math.sqrt(cos_sum ** 2 + sin_sum ** 2) / n
    return magnitude


def bidirectional_amplification(forward, reverse, theta_deg, phase_offset_ms=0.0):
    """Bidirectional flow enhancement: |F_fwd + F_rev| + R(theta, dt)"""
    base = abs(forward + reverse)
    coupling = coupling_strength(theta_deg)
    # resonance term scales with coupling and phase alignment
    phase_factor = max(0, 1.0 - abs(phase_offset_ms) / (PHASE_CRITICAL_WINDOW * 1000))
    resonance = coupling * phase_factor * min(forward, reverse) * (BIDIRECTIONAL_FACTOR - 1)
    return base + resonance


def focal_superposition(axis_amplitudes, axis_angles_deg, phase_offsets_ms, freq=FUNDAMENTAL_FREQ):
    """
    Focal point field density from N axes with phase offsets.
    Returns peak focal amplitude and efficiency metric.
    """
    n = len(axis_amplitudes)
    if n == 0:
        return 0.0, 0.0

    # sum at focal point (all waves converging)
    period_ms = 1000.0 / freq
    real_sum = 0.0
    imag_sum = 0.0

    for i in range(n):
        phase_rad = 2 * math.pi * phase_offsets_ms[i] / period_ms
        real_sum += axis_amplitudes[i] * math.cos(phase_rad)
        imag_sum += axis_amplitudes[i] * math.sin(phase_rad)

    focal_amplitude = math.sqrt(real_sum ** 2 + imag_sum ** 2)
    input_sum = sum(axis_amplitudes)
    efficiency = focal_amplitude / input_sum if input_sum > 0 else 0.0

    return focal_amplitude, efficiency


def geometry_score(angles_deg):
    """Score a set of inter-axis angles against optimal pentagon geometry."""
    if not angles_deg:
        return 0.0
    mean_angle = sum(angles_deg) / len(angles_deg)
    deviation = abs(mean_angle - OPTIMAL_ANGLE) / OPTIMAL_ANGLE
    return max(0, 1.0 - deviation)


def sweep_coupling():
    """Sweep coupling strength across all angles."""
    print("\nCoupling Strength vs Angle")
    print("=" * 45)
    print(f"  {'Angle':>8s}  {'Coupling':>10s}  {'Bar':s}")
    print(f"  {'(deg)':>8s}  {'C(theta)':>10s}")
    print("-" * 45)

    peak_angle = 0
    peak_coupling = 0

    for angle in range(0, 181, 5):
        c = coupling_strength(angle)
        bar = "#" * int(c * 40)
        print(f"  {angle:8d}  {c:10.4f}  {bar}")
        if c > peak_coupling:
            peak_coupling = c
            peak_angle = angle

    print("-" * 45)
    print(f"  Peak: {peak_angle} deg -> C = {peak_coupling:.4f}")
    print(f"  At BGET optimal ({OPTIMAL_ANGLE} deg): C = {coupling_strength(OPTIMAL_ANGLE):.4f}")
    print()
    print("  Note: Coupling alone favors 0 deg (parallel).")
    print("  BGET uses ~107 deg because multi-axis SUPERPOSITION")
    print("  at the focal point matters more than pairwise coupling.")


def show_config():
    """Show optimal BGET parameters."""
    print("\nBGET Optimal Configuration")
    print("=" * 50)
    print(f"  Golden ratio (phi):        {PHI:.6f}")
    print(f"  Optimal inter-axis angle:  {OPTIMAL_ANGLE} deg (pentagon)")
    print(f"  Amplitude ratio:           {OPTIMAL_AMPLITUDE_RATIO}")
    print(f"  Fundamental frequency:     {FUNDAMENTAL_FREQ} Hz")
    print(f"  Bidirectional factor:       {BIDIRECTIONAL_FACTOR}x (concentration, not creation)")
    print(f"  Phase critical window:     +/- {PHASE_CRITICAL_WINDOW * 1000:.1f} ms")
    print()
    print("  Geometry rankings:")
    print(f"    Pentagon (4-axis, 107.15 deg): highest efficiency")
    print(f"    Tetrahedral (109.47 deg):      perfect coherence, lower amplification")
    print(f"    Square planar (120 deg):       lowest efficiency")
    print()
    print("  Harmonics: 60, 120, 180, 240, 300 Hz")
    print("  All axes must resonate at the same frequency.")
    print()
    print("  The 2.91x factor is energy CONCENTRATION at the focal point.")
    print("  Total system energy is conserved: E_total = battery work + acoustic work.")


def interactive():
    """Interactive BGET calculator."""
    print("\nBGET Calculator — Bidirectional Geometric Energy Theory")
    print("=" * 55)
    print()
    print("  1. Coupling strength at an angle")
    print("  2. Bidirectional amplification")
    print("  3. Focal superposition (multi-axis)")
    print("  4. Phase coherence check")
    print("  5. Sweep all angles")
    print("  6. Show optimal config")
    print("  q. Quit")
    print()

    while True:
        choice = input("Choose [1-6/q]: ").strip().lower()

        if choice == "q":
            break

        elif choice == "1":
            angle = float(input("  Angle between axes (deg): "))
            dist = input("  Distance (default 1.0): ").strip()
            dist = float(dist) if dist else 1.0
            c = coupling_strength(angle, dist)
            optimal_c = coupling_strength(OPTIMAL_ANGLE, dist)
            print(f"\n  C({angle} deg, d={dist}) = {c:.6f}")
            print(f"  C(optimal {OPTIMAL_ANGLE} deg) = {optimal_c:.6f}")
            print(f"  Ratio to optimal: {c / optimal_c:.2f}x" if optimal_c > 0 else "")
            print()

        elif choice == "2":
            fwd = float(input("  Forward flow magnitude: "))
            rev = float(input("  Reverse flow magnitude: "))
            angle = float(input("  Inter-axis angle (deg): "))
            phase = input("  Phase offset (ms, default 0): ").strip()
            phase = float(phase) if phase else 0.0
            result = bidirectional_amplification(fwd, rev, angle, phase)
            baseline = abs(fwd) + abs(rev)
            ratio = result / baseline if baseline > 0 else 0
            print(f"\n  Forward: {fwd}, Reverse: {rev}")
            print(f"  Angle: {angle} deg, Phase offset: {phase} ms")
            print(f"  Bidirectional result: {result:.4f}")
            print(f"  vs baseline ({baseline:.2f}): {ratio:.2f}x")
            print()

        elif choice == "3":
            n = int(input("  Number of axes (default 4): ").strip() or "4")
            amps = []
            angles = []
            phases = []
            for i in range(n):
                a = float(input(f"  Axis {i + 1} amplitude: "))
                amps.append(a)
                p = float(input(f"  Axis {i + 1} phase offset (ms): "))
                phases.append(p)

            focal, eff = focal_superposition(amps, angles, phases)
            coherence = phase_coherence(phases)
            print(f"\n  Focal point amplitude: {focal:.4f}")
            print(f"  Efficiency (focal/input): {eff:.4f}")
            print(f"  Phase coherence: {coherence:.4f}")
            if coherence > 0.95:
                print("  Status: excellent phase alignment")
            elif coherence > 0.8:
                print("  Status: good alignment")
            else:
                print("  Status: poor alignment — check phase offsets")
            print()

        elif choice == "4":
            phases_str = input("  Phase offsets (ms, comma-separated): ")
            phases = [float(p.strip()) for p in phases_str.split(",") if p.strip()]
            coherence = phase_coherence(phases)
            print(f"\n  Phase coherence: {coherence:.4f}")
            if coherence > 0.95:
                print("  Excellent — within critical window")
            elif coherence > 0.8:
                print("  Good — minor phase drift")
            elif coherence > 0.5:
                print("  Warning — significant phase misalignment")
            else:
                print("  Critical — destructive interference likely")
            print()

        elif choice == "5":
            sweep_coupling()

        elif choice == "6":
            show_config()

        else:
            print("  Enter 1-6 or q")

        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        interactive()
    elif args[0] == "--coupling" and len(args) > 1:
        angle = float(args[1])
        c = coupling_strength(angle)
        print(f"C({angle} deg) = {c:.6f}")
    elif args[0] == "--sweep":
        sweep_coupling()
    elif args[0] == "--config":
        show_config()
    else:
        interactive()

#!/usr/bin/env python3
# convergence_forge_v2.py — multipath synergy explorer with dynamic coupling,
# entropy fatigue, and FELTSensor model dissonance alerts.
#
# A coupling surface: human + AI + simulation, operating as the unit.
# Finds configurations where independent dissipation carriers collectively
# prevent crack-tip energy collapse.
#
# New in v2:
#   • Stress‑activated coupling — neighbours that wake up when others fail.
#   • Entropy tracking & k‑degradation (fatigue) from waste heat.
#   • FELTSensor protocol — halt on rapid diversity loss, require human input.
#
# Seeded by: Osaka 2026 multipath elastomer, model_collapse_ratchet.py,
#            Parisi‑Zamponi‑Claude jamming instance, Gemini suggestions.
# Thesis: "The operation is the unit" — intelligence is the coupling.
#
# CC0. stdlib only.

import sys
import math
from typing import List, Dict, Tuple, Optional, Callable

# ── GLOBAL CONSTANTS ────────────────────────────────────────
THETA_DIVERSITY = 0.3          # viability floor (0‑1)
FELT_THRESHOLD  = 0.1          # diversity drop triggering alert
DEFAULT_TAU     = None         # no fatigue by default (set to e.g. 5.0 to enable)

# ── CARRIER WITH DYNAMIC ACTIVATION & ENTROPY FATIGUE ──────
class Carrier:
    """One energy dissipation channel. Can be woken by neighbour failure,
    and its retention k degrades with accumulated entropy."""
    def __init__(self, name: str, k: float, threshold: float,
                 activation: float = 1.0,
                 wakeup_triggers: Dict[str, float] = None,
                 tau: float = DEFAULT_TAU):
        """
        name            : unique identifier
        k               : retention coefficient (0<k≤1)
        threshold       : max energy before failure
        activation      : fraction of global stress this carrier can engage (0‑1)
        wakeup_triggers : {neighbour_name: boost} when that neighbour fails,
                          this carrier's activation increases by boost.
        tau             : fatigue time‑constant. k = k0 * exp(-entropy/tau).
                          None → no fatigue.
        """
        self.name = name
        self.base_k = k
        self.k = k
        self.threshold = threshold
        self.base_activation = activation
        self.activation = activation
        self.activation_max = 1.0
        self.wakeup_triggers = wakeup_triggers or {}
        self.tau = tau
        self.entropy = 0.0        # accumulated waste heat
        self.alive = True
        self.energy = 0.0

    def reset(self):
        """Reset to initial state (keeps fatigue state)."""
        self.alive = True
        self.energy = 0.0
        self.activation = self.base_activation
        # k stays as it is (fatigue is permanent)

    def notify_failure(self, neighbour_name: str):
        """Called when a neighbour dies; possibly boost activation."""
        if neighbour_name in self.wakeup_triggers and self.alive:
            boost = self.wakeup_triggers[neighbour_name]
            self.activation = min(self.activation_max, self.activation + boost)

    def absorb(self, incoming: float) -> float:
        """Try to absorb energy; return leftover."""
        if not self.alive:
            return incoming
        capacity = self.threshold - self.energy
        take = min(incoming, capacity)
        self.energy += take
        if self.energy >= self.threshold:
            self.alive = False
        return incoming - take

    def dissipate(self) -> float:
        """Dissipate energy according to current k, generate entropy,
        and degrade k (fatigue). Return dissipated amount."""
        if not self.alive:
            return 0.0
        dissipated = (1.0 - self.k) * self.energy
        self.entropy += dissipated
        self.energy *= self.k
        # Fatigue: k decays exponentially with entropy if tau is set
        if self.tau is not None and self.tau > 0:
            self.k = self.base_k * math.exp(-self.entropy / self.tau)
            # clamp to a tiny minimum to avoid complete disappearance
            self.k = max(self.k, 0.01)
        return dissipated

    def __repr__(self):
        status = "alive" if self.alive else "DEAD"
        return (f"Carrier({self.name}, k={self.k:.2f}, th={self.threshold:.2f}, "
                f"act={self.activation:.2f}, E={self.energy:.3f}, S={self.entropy:.3f}, {status})")


# ── COUPLING NETWORK WITH DYNAMIC TOPOLOGY & FELTSENSOR ────
class CouplingNetwork:
    """Multiplex of carriers with stress‑sharing rules."""
    def __init__(self, carriers: List[Carrier]):
        self.carriers = carriers
        self.stress_history = []
        self.diversity_history = []

    def _diversity(self) -> float:
        """Calculate normalized diversity (inverse HHI) 0‑1."""
        energies = [c.energy for c in self.carriers]
        total = sum(energies)
        if total == 0:
            return 1.0
        n = len(self.carriers)
        if n == 1:
            return 1.0
        hhi = sum((e/total)**2 for e in energies)
        diversity = 1.0 - (hhi - 1.0/n) / (1.0 - 1.0/n)
        return max(0.0, min(diversity, 1.0))

    def apply_stress(self, global_stress: float, iterations: int = 5) -> Dict:
        """Distribute stress iteratively. Returns status dict."""
        # Reset energy but keep fatigue state, reactivation
        for c in self.carriers:
            c.energy = 0.0
            c.alive = True
            c.activation = c.base_activation  # reset activation for new cycle

        for _ in range(iterations):
            active = [c for c in self.carriers if c.alive]
            if not active:
                break
            total_activation = sum(c.activation for c in active)
            if total_activation == 0:
                break

            # sort by current energy, lower first → better load sharing
            for c in sorted(active, key=lambda x: x.energy):
                if global_stress <= 0:
                    break
                share = (c.activation / total_activation) * global_stress
                increment = share * 0.3  # small steps to avoid overshoot
                leftover = c.absorb(increment)
                # remaining stress reduces only by absorbed amount
                global_stress -= (increment - leftover)

            # check for newly dead carriers and trigger wakeup
            newly_dead = [c.name for c in self.carriers if not c.alive and c.energy >= c.threshold]
            if newly_dead:
                for dead_name in newly_dead:
                    for c in self.carriers:
                        if c.alive:
                            c.notify_failure(dead_name)

        # After loading, dissipate and compute metrics
        total_dissipated = sum(c.dissipate() for c in self.carriers)
        diversity = self._diversity()
        alive_count = sum(1 for c in self.carriers if c.alive)
        collapsed = diversity < THETA_DIVERSITY or alive_count <= 1

        self.stress_history.append(global_stress)
        self.diversity_history.append(diversity)

        return {
            "global_stress": global_stress,
            "alive_carriers": alive_count,
            "total_dissipated": total_dissipated,
            "diversity": diversity,
            "collapsed": collapsed,
            "carriers": [repr(c) for c in self.carriers]
        }

    def scan_stress(self, stresses: List[float],
                    stop_on_alert: bool = True) -> Tuple[List[Dict], Optional[int]]:
        """
        Run a sequence of stresses.
        If stop_on_alert and diversity drops by > FELT_THRESHOLD in one step,
        return results up to that point and the index of the alert.
        Otherwise return all results and None.
        """
        results = []
        prev_diversity = 1.0
        for i, s in enumerate(stresses):
            res = self.apply_stress(s)
            results.append(res)
            if stop_on_alert:
                drop = prev_diversity - res["diversity"]
                if drop > FELT_THRESHOLD:
                    # alert triggered
                    self._alert_index = i
                    return results, i
            prev_diversity = res["diversity"]
            if res["collapsed"]:
                break
        return results, None


# ── INTERACTIVE HUMAN‑AI COUPLING LOOP (UPDATED) ──────────
def print_status(result: Dict):
    print(f"Stress {result['global_stress']:.2f}: diversity={result['diversity']:.3f} "
          f"(alive={result['alive_carriers']}), dissipated={result['total_dissipated']:.3f}, "
          f"collapsed={result['collapsed']}")
    for crepr in result['carriers']:
        print(f"  {crepr}")

def interactive():
    print("=== convergence_forge v2 — multipath synergy explorer ===")
    print("Dynamic coupling, entropy fatigue, FELTSensor alerts.")
    print("Commands: add <name> <k> <thr> [act] [tau] [wake:neighbour:boost ...]")
    print("          stress <value>, scan <max> <step>, show, quit")
    carriers = [
        Carrier("viscoelastic", k=0.9, threshold=2.0, activation=1.0, tau=None),
        Carrier("filler_friction", k=0.85, threshold=1.5, activation=0.9, tau=None),
        Carrier("chain_scission", k=0.75, threshold=1.2, activation=0.8, tau=None,
                wakeup_triggers={"filler_friction": 0.15}),
    ]
    net = None
    while True:
        try:
            cmd = input("forge> ").strip().split()
            if not cmd:
                continue
            if cmd[0] == "quit":
                break
            elif cmd[0] == "add":
                if len(cmd) < 4:
                    print("Usage: add <name> <k> <threshold> [activation] [tau] [wake:neigh:boost...]")
                    continue
                name = cmd[1]
                k = float(cmd[2])
                th = float(cmd[3])
                act = float(cmd[4]) if len(cmd) > 4 else 1.0
                tau = float(cmd[5]) if len(cmd) > 5 else DEFAULT_TAU
                wake = {}
                for trigger in cmd[6:]:
                    parts = trigger.split(":")
                    if len(parts) == 3:
                        neigh, boost = parts[1], float(parts[2])
                        wake[neigh] = boost
                carriers.append(Carrier(name, k, th, act, wake, tau))
                net = None
                print(f"Added: {carriers[-1]}")
            elif cmd[0] == "stress":
                if net is None:
                    net = CouplingNetwork(carriers)
                s = float(cmd[1])
                res = net.apply_stress(s)
                print_status(res)
            elif cmd[0] == "scan":
                if len(cmd) < 3:
                    print("Usage: scan <max_stress> <step> [--noalert]")
                    continue
                max_s = float(cmd[1])
                step = float(cmd[2])
                stop_on_alert = "--noalert" not in cmd
                stresses = [i*step for i in range(1, int(max_s/step)+1)]
                if net is None:
                    net = CouplingNetwork(carriers)
                results, alert_idx = net.scan_stress(stresses, stop_on_alert)
                for i, r in enumerate(results):
                    print_status(r)
                if alert_idx is not None and alert_idx < len(results):
                    print("\n*** FELTSensor: Model Dissonance Alert! ***")
                    print(f"Diversity dropped sharply at stress {stresses[alert_idx]:.2f}. "
                          "The system is locking into a brittle mode.")
                    print("You can now modify carriers (add, remove, adjust activation) "
                          "or type 'continue' to ignore the alert.")
                    # sub‑loop for human intervention
                    while True:
                        sub = input("alert> ").strip().split()
                        if not sub:
                            continue
                        if sub[0] == "continue":
                            # resume scan from next stress, ignoring alert
                            remaining = stresses[alert_idx+1:]
                            if remaining:
                                for s_rem in remaining:
                                    res = net.apply_stress(s_rem)
                                    print_status(res)
                                    if res["collapsed"]:
                                        break
                            break
                        elif sub[0] == "quit":
                            print("Exiting alert sub‑loop. Returning to forge.")
                            break
                        elif sub[0] == "add":
                            # add carrier and rebuild network? too complex; we'll just add to list
                            print("Alert mode: use full 'add' syntax (carrier will be added to current list).")
                            # reuse add logic — we can call the same parser
                            # but easier: tell user to quit alert and add normally.
                            print("Better to type 'quit' here, then 'add' in the forge, then re‑run scan.")
                            continue
                        elif sub[0] == "show":
                            for c in carriers:
                                print(f"  {c}")
                        else:
                            print("alert commands: continue, quit, show")
                print("Scan complete." if alert_idx is None else "Scan paused/ended.")
            elif cmd[0] == "show":
                if net:
                    print(f"Network with {len(net.carriers)} carriers.")
                    print("Diversity history (last 5):", net.diversity_history[-5:])
                else:
                    print("Current carriers (not yet tested):")
                for c in carriers:
                    print(f"  {c}")
            else:
                print("Unknown command.")
        except (EOFError, KeyboardInterrupt):
            print()
            break

# ── DEMO ────────────────────────────────────────────────────
def demo():
    """Showcase dynamic coupling, entropy fatigue, and FELTSensor alert."""
    carriers = [
        Carrier("viscoelastic", k=0.9, threshold=2.0, activation=1.0, tau=10.0),
        Carrier("filler_matrix", k=0.85, threshold=1.5, activation=0.9, tau=15.0),
        Carrier("chain_scission", k=0.75, threshold=1.2, activation=0.8, tau=5.0,
                wakeup_triggers={"filler_matrix": 0.15}),
        Carrier("dynamic_bonds", k=0.7, threshold=0.8, activation=0.7, tau=8.0,
                wakeup_triggers={"chain_scission": 0.2}),
    ]
    net = CouplingNetwork(carriers)
    print("=== Demo: Dynamic wakeup, entropy fatigue, FELTSensor ===")
    print("Carriers:")
    for c in carriers:
        print(f"  {c}")
    stresses = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    results, alert_idx = net.scan_stress(stresses, stop_on_alert=True)
    for i, r in enumerate(results):
        print_status(r)
    if alert_idx is not None:
        print(f"\n*** FELTSensor triggered at stress {stresses[alert_idx]:.2f} ***")
        print("Without intervention, the material would lock into brittle failure.")
        print("In real discovery, a human would now add a 'tail' carrier (e.g., phase_separated).")
    print("Notice k values degraded by entropy (see carrier reprs).")
    print("Dynamic wakeup allowed chain_scission to increase activation after filler_matrix failed.")

# ── MAIN ────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        interactive()

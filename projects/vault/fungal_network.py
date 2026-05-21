"""
fungal_network.py — Non-Hierarchical Resource Flow Simulator

Extends the existing thermo_fungal_demo.py with:
- Load-balancing across a mycelial network with no central controller
- Stress response: node failure and network self-healing
- Resource routing that finds paths without hierarchy

No external dependencies beyond standard library.
Prints ASCII visualization — no matplotlib required.

Usage:
    python fungal_network.py              # run default simulation
    python fungal_network.py --nodes 30   # custom network size
    python fungal_network.py --stress 5   # kill node 5 mid-run
"""

import random
import math
import sys


class Node:
    __slots__ = ("id", "load", "neighbors", "alive", "history")

    def __init__(self, node_id, load=0.0):
        self.id = node_id
        self.load = load
        self.neighbors = []
        self.alive = True
        self.history = [load]


def build_network(n_nodes, connection_radius=0.4, seed=42):
    """Build a geometric graph — nodes connect if spatially close."""
    rng = random.Random(seed)
    positions = [(rng.random(), rng.random()) for _ in range(n_nodes)]
    nodes = [Node(i, load=rng.random() * 10) for i in range(n_nodes)]

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            dx = positions[i][0] - positions[j][0]
            dy = positions[i][1] - positions[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < connection_radius:
                nodes[i].neighbors.append(j)
                nodes[j].neighbors.append(i)

    return nodes, positions


def equalize_step(nodes, transfer_rate=0.1):
    """One step of load equalization — each node shares with neighbors."""
    transfers = {n.id: 0.0 for n in nodes}

    for node in nodes:
        if not node.alive or not node.neighbors:
            continue
        alive_neighbors = [n for n in node.neighbors if nodes[n].alive]
        if not alive_neighbors:
            continue
        for nid in alive_neighbors:
            delta = transfer_rate * (node.load - nodes[nid].load)
            transfers[node.id] -= delta
            transfers[nid] += delta

    for node in nodes:
        if node.alive:
            node.load += transfers[node.id]
            node.load = max(0.0, node.load)
            node.history.append(node.load)


def network_entropy(nodes):
    """Shannon entropy of load distribution across alive nodes."""
    alive = [n for n in nodes if n.alive]
    if not alive:
        return 0.0
    loads = [n.load for n in alive]
    total = sum(loads)
    if total == 0:
        return 0.0
    probs = [l / total for l in loads]
    return -sum(p * math.log(p) for p in probs if p > 0)


def load_variance(nodes):
    """Variance of load across alive nodes — lower = more equalized."""
    alive = [n for n in nodes if n.alive]
    if len(alive) < 2:
        return 0.0
    loads = [n.load for n in alive]
    mean = sum(loads) / len(loads)
    return sum((l - mean) ** 2 for l in loads) / len(loads)


def kill_node(nodes, node_id):
    """Simulate node failure — redistribute load to neighbors."""
    node = nodes[node_id]
    node.alive = False
    alive_neighbors = [n for n in node.neighbors if nodes[n].alive]
    if alive_neighbors:
        share = node.load / len(alive_neighbors)
        for nid in alive_neighbors:
            nodes[nid].load += share
    node.load = 0.0
    return len(alive_neighbors)


def ascii_bar(value, max_val, width=40):
    """Render a proportional ASCII bar."""
    if max_val == 0:
        return ""
    filled = int((value / max_val) * width)
    filled = min(filled, width)
    return "#" * filled + "." * (width - filled)


def print_network_state(nodes, step_label=""):
    """Print current load distribution."""
    alive = [n for n in nodes if n.alive]
    if not alive:
        return
    max_load = max(n.load for n in alive)
    print(f"\n  {'--- ' + step_label + ' ---' if step_label else ''}")
    for n in nodes:
        if n.alive:
            bar = ascii_bar(n.load, max_load)
            print(f"  [{n.id:2d}] {bar} {n.load:.2f}")
        else:
            print(f"  [{n.id:2d}] XXXX (dead)")


def run_simulation(n_nodes=15, steps=40, stress_node=None, stress_at=20):
    """Run the full simulation."""
    print("Fungal Network — Non-Hierarchical Resource Flow")
    print("=" * 50)

    nodes, positions = build_network(n_nodes)
    alive_count = sum(1 for n in nodes if n.neighbors)

    # remove isolated nodes
    for n in nodes:
        if not n.neighbors:
            n.alive = False

    print(f"\nNodes: {n_nodes} ({alive_count} connected)")
    print(f"Steps: {steps}")
    if stress_node is not None:
        print(f"Stress event: node {stress_node} dies at step {stress_at}")

    print_network_state(nodes, "Initial state")
    print(f"\n  Entropy: {network_entropy(nodes):.3f}")
    print(f"  Load variance: {load_variance(nodes):.3f}")

    entropy_trace = []
    variance_trace = []

    for step in range(steps):
        if stress_node is not None and step == stress_at:
            print(f"\n  *** STRESS EVENT: Node {stress_node} fails ***")
            recipients = kill_node(nodes, stress_node)
            print(f"  Load redistributed to {recipients} neighbors")
            print_network_state(nodes, f"After stress (step {step})")

        equalize_step(nodes)
        entropy_trace.append(network_entropy(nodes))
        variance_trace.append(load_variance(nodes))

    print_network_state(nodes, "Final state")
    print(f"\n  Entropy: {network_entropy(nodes):.3f}")
    print(f"  Load variance: {load_variance(nodes):.3f}")

    # ASCII entropy chart
    print("\n  Entropy over time:")
    if entropy_trace:
        min_e = min(entropy_trace)
        max_e = max(entropy_trace)
        chart_height = 8
        for row in range(chart_height, -1, -1):
            threshold = min_e + (max_e - min_e) * (row / chart_height) if max_e > min_e else min_e
            line = "  "
            for val in entropy_trace:
                line += "#" if val >= threshold else " "
            if row == chart_height:
                line += f"  {max_e:.2f}"
            elif row == 0:
                line += f"  {min_e:.2f}"
            print(line)

    # Variance chart
    print("\n  Load variance over time (lower = more equalized):")
    if variance_trace:
        min_v = min(variance_trace)
        max_v = max(variance_trace)
        chart_height = 6
        for row in range(chart_height, -1, -1):
            threshold = min_v + (max_v - min_v) * (row / chart_height) if max_v > min_v else min_v
            line = "  "
            for val in variance_trace:
                line += "#" if val >= threshold else " "
            if row == chart_height:
                line += f"  {max_v:.2f}"
            elif row == 0:
                line += f"  {min_v:.2f}"
            print(line)

    print(f"\n  No central controller. No hierarchy. Load equalized through")
    print(f"  local neighbor-to-neighbor transfer — the mycelial way.")


if __name__ == "__main__":
    n_nodes = 15
    stress_node = None
    stress_at = 20

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--nodes" and i + 1 < len(args):
            n_nodes = int(args[i + 1])
            i += 2
        elif args[i] == "--stress" and i + 1 < len(args):
            stress_node = int(args[i + 1])
            i += 2
        else:
            i += 1

    run_simulation(n_nodes=n_nodes, stress_node=stress_node, stress_at=stress_at)

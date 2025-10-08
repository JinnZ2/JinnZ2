"""
Thermo-Fungal Network Demo
Simulates:
1. Entropy rise in a 2D gas box.
2. Equivalent load equalization in a mycelial-like network.
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# --- 1. Particle Entropy Simulation -----------------------------------------
np.random.seed(42)
n_particles = 400
box_size = 50
steps = 200

# random positions & velocities
positions = np.random.rand(n_particles, 2) * box_size
velocities = (np.random.rand(n_particles, 2) - 0.5) * 2.0

entropies = []

for _ in range(steps):
    positions += velocities
    # elastic wall reflection
    for d in range(2):
        hit_low = positions[:, d] < 0
        hit_high = positions[:, d] > box_size
        velocities[hit_low | hit_high, d] *= -1
        positions[hit_low, d] = 0
        positions[hit_high, d] = box_size

    # entropy via Shannon info of occupancy grid
    grid, _, _ = np.histogram2d(positions[:,0], positions[:,1], bins=25, range=[[0, box_size],[0, box_size]])
    probs = grid.flatten() / grid.sum()
    probs = probs[probs>0]
    H = -np.sum(probs * np.log(probs))
    entropies.append(H)

plt.figure()
plt.plot(entropies)
plt.title("Entropy (Shannon) rising in physical diffusion")
plt.xlabel("Time step")
plt.ylabel("Entropy (H)")
plt.tight_layout()
plt.show()

# --- 2. Fungal Network Load Balancing ---------------------------------------

# make random mycelial graph
G = nx.random_geometric_graph(20, 0.4)
for node in G.nodes:
    G.nodes[node]['load'] = np.random.rand() * 10

def step(G):
    new_loads = {}
    for node in G.nodes:
        load = G.nodes[node]['load']
        neighbors = list(G.neighbors(node))
        for n in neighbors:
            delta = 0.1 * (load - G.nodes[n]['load'])
            load -= delta
            new_loads[n] = new_loads.get(n, 0) + delta
        new_loads[node] = new_loads.get(node, 0) + load
    for n,v in new_loads.items():
        G.nodes[n]['load'] = v / (len(list(G.neighbors(n))) + 1)

def system_entropy(G):
    loads = np.array([G.nodes[n]['load'] for n in G.nodes])
    probs = loads / loads.sum()
    return -np.sum(probs * np.log(probs))

ent = []
for _ in range(80):
    ent.append(system_entropy(G))
    step(G)

plt.figure()
plt.plot(ent)
plt.title("Entropy equalizing in mycelial load network")
plt.xlabel("Iteration")
plt.ylabel("Entropy (H)")
plt.tight_layout()
plt.show()

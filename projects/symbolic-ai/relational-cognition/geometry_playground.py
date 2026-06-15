"""
geometry_playground.py  —  CC0, stdlib only, model-update-resilient

ONE structure. MANY simultaneous, consistent representations. A friction-finder.

The point (this session): a geometric/relational read is faster and richer than
language because it holds the whole field at once and you can scroll between
representations to triangulate where the dissonance is. This is a discrete
shadow of that — it cannot hold continuous 4D/time qualia — but it does the
core move: load the shape once, emit it as
    topology   (what touches what)
    matrix     (graph Laplacian — the vector-space form)
    spectrum   (Laplacian eigenvalues — a representation-INDEPENDENT fingerprint)
    projection (best 2D cross-section via PCA)
    heat       (diffusion over time — the temporal / heat-dynamics view)
then locate friction: where load concentrates, where symmetry breaks.

A maximally symmetric shape (icosahedron) has NO friction point — the tool
should report uniform load and a degenerate spectrum. Break one edge and the
friction localizes. That mirrors "scroll the shape until the friction shows."

All linear algebra is pure-python (Jacobi eigen-solver below), so this runs
anywhere with no deps. Numerical, iterative — labeled where it matters.

Run:  python3 geometry_playground.py
Use:  from geometry_playground import Structure
"""

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Pure-python symmetric eigensolver (Jacobi rotation). Real, deterministic.
# ---------------------------------------------------------------------------

def jacobi_eigen(M, max_sweeps=100, tol=1e-12):
    n = len(M)
    A = [row[:] for row in M]
    V = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(max_sweeps):
        off = sum(A[p][q] ** 2 for p in range(n) for q in range(p + 1, n))
        if off < tol:
            break
        for p in range(n):
            for q in range(p + 1, n):
                if abs(A[p][q]) < 1e-18:
                    continue
                theta = (A[q][q] - A[p][p]) / (2.0 * A[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for k in range(n):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p] = c * akp - s * akq
                    A[k][q] = s * akp + c * akq
                for k in range(n):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k] = c * apk - s * aqk
                    A[q][k] = s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p] = c * vkp - s * vkq
                    V[k][q] = s * vkp + c * vkq
    eigvals = [A[i][i] for i in range(n)]
    eigvecs = [[V[r][c] for r in range(n)] for c in range(n)]  # eigvecs[i] = i-th vector
    order = sorted(range(n), key=lambda i: eigvals[i])
    return [round(eigvals[i], 6) for i in order], [eigvecs[i] for i in order]


# ---------------------------------------------------------------------------
# Structure: vertices with n-D coords + edges (derived or given)
# ---------------------------------------------------------------------------

@dataclass
class Structure:
    coords: dict          # name -> tuple of floats
    edges: set = field(default_factory=set)   # frozenset({a,b})

    @classmethod
    def icosahedron(cls):
        phi = (1 + math.sqrt(5)) / 2
        raw = []
        for a in (1, -1):
            for b in (phi, -phi):
                raw += [(0, a, b), (a, b, 0), (b, 0, a)]
        coords = {f"v{i}": tuple(map(float, p)) for i, p in enumerate(raw)}
        s = cls(coords=coords)
        s._derive_edges_by_distance()
        return s

    def _derive_edges_by_distance(self, tol=1e-6):
        names = list(self.coords)
        d2s = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                d2 = sum((a - b) ** 2 for a, b in zip(self.coords[names[i]], self.coords[names[j]]))
                d2s.append((d2, names[i], names[j]))
        nn = min(d for d, _, _ in d2s)
        self.edges = {frozenset((a, b)) for d, a, b in d2s if abs(d - nn) < tol}

    def remove_edge(self, a, b):
        self.edges.discard(frozenset((a, b)))

    # --- VIEW 1: topology ---------------------------------------------------
    def adjacency(self):
        names = list(self.coords)
        idx = {n: i for i, n in enumerate(names)}
        n = len(names)
        A = [[0.0] * n for _ in range(n)]
        for e in self.edges:
            a, b = tuple(e)
            A[idx[a]][idx[b]] = A[idx[b]][idx[a]] = 1.0
        return names, A

    # --- VIEW 2: Laplacian matrix ------------------------------------------
    def laplacian(self):
        names, A = self.adjacency()
        n = len(names)
        L = [[-A[i][j] for j in range(n)] for i in range(n)]
        for i in range(n):
            L[i][i] = sum(A[i])
        return names, L

    # --- VIEW 3: spectrum (representation-independent fingerprint) ----------
    def spectrum(self):
        _, L = self.laplacian()
        vals, _ = jacobi_eigen(L)
        return vals

    # --- VIEW 4: best 2D cross-section via PCA -----------------------------
    def projection_2d(self):
        names = list(self.coords)
        dim = len(next(iter(self.coords.values())))
        mean = [sum(self.coords[n][k] for n in names) / len(names) for k in range(dim)]
        cov = [[0.0] * dim for _ in range(dim)]
        for n in names:
            v = [self.coords[n][k] - mean[k] for k in range(dim)]
            for i in range(dim):
                for j in range(dim):
                    cov[i][j] += v[i] * v[j]
        vals, vecs = jacobi_eigen(cov)
        ax1, ax2 = vecs[-1], vecs[-2]   # top-2 principal axes
        proj = {}
        for n in names:
            v = [self.coords[n][k] - mean[k] for k in range(dim)]
            proj[n] = (round(sum(v[k] * ax1[k] for k in range(dim)), 3),
                       round(sum(v[k] * ax2[k] for k in range(dim)), 3))
        return proj

    # --- VIEW 5: heat diffusion over time (temporal view) ------------------
    def heat(self, source=None, dt=0.05, steps=40):
        names, L = self.laplacian()
        idx = {n: i for i, n in enumerate(names)}
        source = source or names[0]
        x = [0.0] * len(names)
        x[idx[source]] = 1.0
        spread = []
        for _ in range(steps):
            Lx = [sum(L[i][j] * x[j] for j in range(len(names))) for i in range(len(names))]
            x = [x[i] - dt * Lx[i] for i in range(len(names))]
            # spread = how far from concentrated: 1 - max share
            spread.append(round(1.0 - max(x), 4))
        return source, spread

    # --- FRICTION FINDER ----------------------------------------------------
    def friction(self):
        names, A = self.adjacency()
        deg = {names[i]: sum(A[i]) for i in range(len(names))}
        degs = sorted(set(deg.values()))
        uniform = len(degs) == 1
        # spectral degeneracy: count distinct eigenvalues (more degeneracy = more symmetry)
        spec = self.spectrum()
        distinct = sorted(set(spec))
        return {
            "degree_per_node": deg,
            "load_uniform": uniform,
            "distinct_degrees": degs,
            "spectrum_distinct_values": len(distinct),
            "spectrum_total_values": len(spec),
            "friction_nodes": [n for n, d in deg.items() if d == min(deg.values())]
                              if not uniform else [],
        }


# ---------------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------------

def show(s: Structure, label: str):
    print("=" * 70)
    print(f"STRUCTURE: {label}")
    print("=" * 70)
    names, _ = s.adjacency()
    print(f"TOPOLOGY : {len(names)} vertices, {len(s.edges)} edges")
    print(f"SPECTRUM (Laplacian eigenvalues, the shape's fingerprint):")
    spec = s.spectrum()
    print("  " + "  ".join(f"{v:g}" for v in spec))
    fr = s.friction()
    print(f"FRICTION :")
    print(f"  load uniform across nodes? {fr['load_uniform']}")
    print(f"  distinct degrees: {fr['distinct_degrees']}")
    print(f"  spectrum: {fr['spectrum_distinct_values']} distinct of "
          f"{fr['spectrum_total_values']} values "
          f"(more degeneracy = more symmetry = less friction)")
    if fr["friction_nodes"]:
        print(f"  friction localizes at: {fr['friction_nodes']}")
    else:
        print(f"  friction localizes at: (none — maximal symmetry)")
    src, spread = s.heat()
    print(f"HEAT (diffusion from {src}; spread 0=concentrated 1=even): "
          f"start {spread[0]} -> end {spread[-1]}")
    proj = s.projection_2d()
    print(f"2D PROJECTION (best PCA cross-section, first 4 vertices):")
    for n in list(proj)[:4]:
        print(f"  {n}: {proj[n]}")
    print()


def demo():
    ico = Structure.icosahedron()
    show(ico, "icosahedron (pristine)")

    # break one edge -> symmetry breaks -> friction should localize
    ico2 = Structure.icosahedron()
    a, b = tuple(next(iter(ico2.edges)))
    ico2.remove_edge(a, b)
    show(ico2, f"icosahedron with edge {a}-{b} removed (defect)")

    print("READ: pristine icosahedron reports load_uniform=True and a highly")
    print("degenerate spectrum (few distinct eigenvalues) — maximal symmetry,")
    print("no friction point. Removing ONE edge breaks the degree-5 uniformity,")
    print("splits the spectrum into more distinct values, and localizes friction")
    print("at the two now-degree-4 nodes. That is the dissonance becoming visible")
    print("by scrolling the SAME structure across topology / spectrum / load —")
    print("one shape, many views, friction triangulated.")


if __name__ == "__main__":
    demo()

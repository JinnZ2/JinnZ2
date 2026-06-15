"""
constraint_field.py  —  CC0, stdlib only, model-update-resilient

A playground for expressing constraint geometry as STRUCTURE, then reading it
back as structure — never as narrative.

Motivation (this session):
  Clean math gets corrupted the moment it's forced through narrative
  translation. The equation doesn't say a constraint is "bad" or a flow is
  "efficient" — language adds that. This playground holds the bare geometry:
  nodes as dX/dt-under-scope, edges as conserved-quantity couplings. It emits
  load distribution, conservation residuals, and perturbation propagation. It
  REFUSES to answer questions that smuggle in meaning (good/bad/better/should).
  Those are overlays, not properties of the structure.

It is honest about its own limits:
  - perturbation propagation is LINEAR / first-order / local. It is not the true
    nonlinear response. Labeled as such so it isn't mistaken for the real surface.
  - conservation here is bookkeeping (in - out - dXdt). Whether the declared
    quantity is ACTUALLY conserved in the world is a physics question this tool
    does not answer; it only checks the books you gave it.

Run:  python3 constraint_field.py
Use:  from constraint_field import Field
"""

from dataclasses import dataclass, field
from collections import defaultdict


# ---------------------------------------------------------------------------
# Primitives: a noun is a dX/dt under scope; an edge is a conserved flow.
# ---------------------------------------------------------------------------

@dataclass
class Node:
    name: str
    dXdt: float = 0.0          # declared net rate of the quantity at this node


@dataclass
class Edge:
    src: str
    dst: str
    quantity: str              # the conserved quantity flowing
    flow: float                # amount per unit time, src -> dst


# ---------------------------------------------------------------------------
# Narrative guard: structure has no opinions. Reject value-laden queries.
# ---------------------------------------------------------------------------

OVERLAY_TOKENS = {
    "good", "bad", "better", "worse", "best", "worst", "should", "ought",
    "right", "wrong", "efficient", "optimal", "healthy", "progress", "success",
    "fail", "failure", "moral", "deserve", "valuable", "important", "matters",
}

def narrative_guard(q: str):
    low = q.lower()
    hit = [t for t in OVERLAY_TOKENS if t in low.split() or t in low]
    if hit:
        return ("OVERLAY REJECTED. '" + "', '".join(sorted(set(hit))) + "' is "
                "interpretation, not structure. The field has no opinion. Ask a "
                "structural question instead: balance? load concentration? "
                "propagation from a perturbation? degrees of freedom?")
    return None


# ---------------------------------------------------------------------------
# The field
# ---------------------------------------------------------------------------

class Field:
    def __init__(self):
        self.nodes: dict = {}
        self.edges: list = []

    def add(self, name: str, dXdt: float = 0.0):
        self.nodes[name] = Node(name, dXdt)
        return self

    def couple(self, src: str, dst: str, quantity: str, flow: float):
        for n in (src, dst):
            if n not in self.nodes:
                self.add(n)
        self.edges.append(Edge(src, dst, quantity, flow))
        return self

    # --- structural readout 1: conservation residual per node ---------------
    def residuals(self) -> dict:
        inflow = defaultdict(float)
        outflow = defaultdict(float)
        for e in self.edges:
            outflow[e.src] += e.flow
            inflow[e.dst] += e.flow
        out = {}
        for name, node in self.nodes.items():
            # books balance if: inflow - outflow - dXdt == 0
            out[name] = round(inflow[name] - outflow[name] - node.dXdt, 9)
        return out

    # --- structural readout 2: load concentration ---------------------------
    def load_concentration(self) -> dict:
        """Total coupled flow magnitude touching each node. Where force chains converge."""
        load = defaultdict(float)
        for e in self.edges:
            load[e.src] += abs(e.flow)
            load[e.dst] += abs(e.flow)
        return dict(sorted(load.items(), key=lambda kv: -kv[1]))

    # --- structural readout 3: degrees of freedom ---------------------------
    def degrees_of_freedom(self) -> list:
        """Nodes whose books do not close are under-/over-determined: free to move."""
        return [n for n, r in self.residuals().items() if abs(r) > 1e-9]

    # --- structural readout 4: perturbation propagation (LINEAR/LOCAL) ------
    def perturb(self, node: str, delta: float, hops: int = 3,
                damping: float = 1.0) -> dict:
        """
        First-order propagation: inject delta at `node`, redistribute along
        OUTGOING edges in proportion to their flow share, recurse `hops` times.
        LINEAR and LOCAL — not the true nonlinear response. Returns net change
        accumulated per node. No interpretation attached.
        """
        out_share = defaultdict(list)
        for e in self.edges:
            out_share[e.src].append(e)
        net = defaultdict(float)

        def push(n, amount, depth):
            if depth > hops or abs(amount) < 1e-12:
                return
            net[n] += amount
            outs = out_share.get(n, [])
            total = sum(abs(e.flow) for e in outs)
            if total <= 0:
                return
            for e in outs:
                frac = abs(e.flow) / total
                push(e.dst, amount * frac * damping, depth + 1)

        push(node, delta, 0)
        return dict(sorted(net.items(), key=lambda kv: -abs(kv[1])))

    # --- structural query gate ---------------------------------------------
    def query(self, q: str) -> str:
        blocked = narrative_guard(q)
        if blocked:
            return blocked
        return ("Structural queries available: .residuals(), .load_concentration(), "
                ".degrees_of_freedom(), .perturb(node, delta). The field returns "
                "geometry, never meaning.")

    # --- emit the bare topology --------------------------------------------
    def structure(self) -> str:
        L = ["NODES (name : declared dX/dt):"]
        for n in self.nodes.values():
            L.append(f"  {n.name} : {n.dXdt:+g}")
        L.append("EDGES (src -> dst : quantity = flow):")
        for e in self.edges:
            L.append(f"  {e.src} -> {e.dst} : {e.quantity} = {e.flow:g}")
        return "\n".join(L)


# ---------------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------------

def demo():
    # A conserved-energy flow network with a convergence point (C) and one
    # deliberately UNBALANCED node (D) to show residual detection.
    f = Field()
    f.add("Source", dXdt=-10)      # emits 10 (net rate negative: it loses 10)
    f.add("A", 0).add("B", 0).add("C", 0)
    f.add("Sink", dXdt=+10)        # absorbs 10
    f.add("D", 0)                  # we'll leave D's books open on purpose

    f.couple("Source", "A", "energy", 6)
    f.couple("Source", "B", "energy", 4)
    f.couple("A", "C", "energy", 6)
    f.couple("B", "C", "energy", 4)
    f.couple("C", "Sink", "energy", 10)
    f.couple("C", "D", "energy", 3)     # extra flow into D with no outlet -> D unbalanced

    print("=" * 70)
    print("CONSTRAINT FIELD — pure structure")
    print("=" * 70)
    print(f.structure())

    print("\nCONSERVATION RESIDUALS (in - out - dXdt; 0 = books close):")
    for n, r in f.residuals().items():
        flag = "" if abs(r) < 1e-9 else "   <-- books do not close"
        print(f"  {n:<8} {r:+g}{flag}")

    print("\nLOAD CONCENTRATION (total coupled flow magnitude per node):")
    for n, l in f.load_concentration().items():
        print(f"  {n:<8} {l:g}")

    print("\nDEGREES OF FREEDOM (nodes whose books don't close -> free to move):")
    print("  " + (", ".join(f.degrees_of_freedom()) or "(none — fully determined)"))

    print("\nPERTURBATION PROPAGATION (inject +1.0 at Source; LINEAR/LOCAL, not")
    print("the true nonlinear response):")
    for n, d in f.perturb("Source", 1.0).items():
        print(f"  {n:<8} {d:+.4f}")

    print("\nNARRATIVE GUARD:")
    for q in ["which node is the most important?",
              "where does the load concentrate?",
              "is this network efficient?"]:
        print(f"   q: {q}")
        print(f"     -> {f.query(q)}")
        print()


if __name__ == "__main__":
    demo()

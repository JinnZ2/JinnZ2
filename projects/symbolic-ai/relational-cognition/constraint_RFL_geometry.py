# constraint_RFL_geometry.py  v1
# repo: precursor-detection / RFL-engine   CC0   stdlib only   phone-buildable
#
# Geometry-first hypothesis tournament.
# Competing hypotheses are shapes in a constraint space.
# The engine detects collisions (overlap), constraint violations,
# and scores the set on how well it preserves distinct viable volumes.
#
# CONTRACT: hold uncertainty open, reward multi-volume coverage,
# penalise forced collapse to a single point.

from dataclasses import dataclass, field
import itertools, math

# ============================================================
# 1. SPACE DEFINITION
# ============================================================
# A space is just a list of axis names and optional weights
# (all coordinates dimensionless 0..1 unless otherwise labelled).
# Weights default to 1.0; set higher for more important axes.
AXES_DEMO = ["heat", "water", "season", "soil"]   # from grain model

# ============================================================
# 2. HYPOTHESIS – a point with uncertainty (spherical tolerance)
# ============================================================
@dataclass
class Hypothesis:
    name: str
    coords: dict         # axis -> value (0..1)
    tolerance: float     # radius of the probability cloud (sigma)
    # optional note
    note: str = ""

    def distance_to(self, other: "Hypothesis") -> float:
        """Euclidean distance using axis weights (here weight=1 for all)."""
        sq = 0.0
        for k in self.coords:
            diff = self.coords[k] - other.coords[k]
            sq += diff * diff
        return math.sqrt(sq)

# ============================================================
# 3. CONSTRAINT – a linear inequality (hyperplane)
# ============================================================
@dataclass
class Constraint:
    name: str
    coeffs: dict        # axis -> coefficient
    bound: float
    op: str = ">"       # ">", "<", "=="  (we'll treat as: sum(coeff*x) - bound > 0)
    desc: str = ""

    def violation(self, h: Hypothesis) -> float:
        """Signed violation: positive = outside the allowed region.
        For op '>' : allowed if sum(...) > bound, so violation = bound - sum(...) if that is >0.
        We'll unify: compute value = sum(coeff * x). Then:
            op == '>' : violation = bound - value (if >0, then value < bound -> violation)
            op == '<' : violation = value - bound
            op == '==' : violation = abs(value - bound)
        """
        val = sum(self.coeffs.get(k, 0.0) * h.coords.get(k, 0.0) for k in h.coords)
        if self.op == ">":
            return max(0.0, self.bound - val)
        elif self.op == "<":
            return max(0.0, val - self.bound)
        else:  # "=="
            return abs(val - self.bound)

    def kills(self, h: Hypothesis, k_sigma: float = 2.0) -> bool:
        """Does the hypothesis violate the constraint beyond k_sigma?
        Compute uncertainty along constraint normal: sigma_normal = ||coeff|| * tolerance (if tol uniform)
        Here we assume spherical tolerance, so sigma_normal = sqrt(sum(coeff_i^2)) * tolerance.
        """
        v = self.violation(h)
        norm_coeff = math.sqrt(sum(c*c for c in self.coeffs.values()))
        sigma_normal = norm_coeff * h.tolerance
        return v > k_sigma * sigma_normal

# ============================================================
# 4. TOURNAMENT LOGIC
# ============================================================
@dataclass
class Tournament:
    axes: list            # axis names
    hypotheses: list
    constraints: list
    distinct_threshold: float = 1.0   # distance must be > sum(tol) * this to be distinct

    def run(self, k_sigma=2.0):
        # a) Check constraint kills
        alive = []
        killed = []
        for h in self.hypotheses:
            killer = None
            for c in self.constraints:
                if c.kills(h, k_sigma):
                    killer = c.name
                    break
            if killer:
                killed.append((h, killer))
            else:
                alive.append(h)

        # b) Pairwise overlap / distinctness among alive
        pairs = list(itertools.combinations(alive, 2))
        conflicts = []    # overlapping (close)
        distinct = []     # well-separated
        for h1, h2 in pairs:
            d = h1.distance_to(h2)
            sum_tol = h1.tolerance + h2.tolerance
            if d < sum_tol * self.distinct_threshold:
                conflicts.append((h1.name, h2.name, d, sum_tol))
            else:
                distinct.append((h1.name, h2.name, d, sum_tol))

        # c) Cluster alive into connected components (using union-find) based on overlap
        parent = {h.name: h.name for h in alive}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx
        for h1, h2 in pairs:
            d = h1.distance_to(h2)
            if d < (h1.tolerance + h2.tolerance) * self.distinct_threshold:
                union(h1.name, h2.name)
        clusters = {}
        for h in alive:
            root = find(h.name)
            clusters.setdefault(root, []).append(h.name)

        # d) Scoring
        # +1 per alive hypothesis, +1 per distinct pair, -10 if all alive are in a single cluster
        score = len(alive)
        score += len(distinct)
        if len(clusters) <= 1 and len(alive) > 1:
            score -= 10   # collapsed to a single region

        return {
            "alive": [h.name for h in alive],
            "killed": [(h.name, reason) for h, reason in killed],
            "conflicts": conflicts,
            "distinct_pairs": distinct,
            "clusters": clusters,
            "score": score,
            "surviving_volumes": len(alive),
            "distinct_regions": len(clusters),
        }

# ============================================================
# 5. DEMO: "Why do wings generate lift?"
# We'll set up a space with axes: "pressure_diff", "deflection", "velocity_gradient", "viscous_coupling"
# (dimensionless 0..1 representing how much each mechanism is emphasised)
# Hypotheses:
#   Bernoulli: high pressure_diff, low deflection, moderate velocity_gradient
#   Newton (deflection): low pressure_diff, high deflection, moderate velocity
#   Circulation (Kutta): combines pressure and deflection but with constraint "total momentum conserved"
# We'll add a conservation constraint: total momentum flux must equal lift.
# This is a toy, but shows the mechanism.
# ============================================================
def demo():
    axes = ["pressure_diff", "deflection", "velocity_grad", "viscous"]
    # Hypotheses as points
    h1 = Hypothesis("Bernoulli", {"pressure_diff": 0.9, "deflection": 0.2, "velocity_grad": 0.7, "viscous": 0.3}, 0.25)
    h2 = Hypothesis("Newton_deflection", {"pressure_diff": 0.2, "deflection": 0.9, "velocity_grad": 0.6, "viscous": 0.3}, 0.25)
    h3 = Hypothesis("Circulation_Kutta", {"pressure_diff": 0.6, "deflection": 0.6, "velocity_grad": 0.8, "viscous": 0.2}, 0.20)
    h4 = Hypothesis("Viscous_entrainment", {"pressure_diff": 0.3, "deflection": 0.4, "velocity_grad": 0.3, "viscous": 0.9}, 0.20)
    hypotheses = [h1, h2, h3, h4]

    # Constraint: Conservation of momentum normal to flow:
    # pressure_diff + 0.5*deflection + 0.2*velocity_grad >= 0.8  (just a toy)
    cons1 = Constraint("momentum_conservation",
                       {"pressure_diff": 1.0, "deflection": 0.5, "velocity_grad": 0.2, "viscous": 0.0},
                       0.8, op=">")

    tournament = Tournament(axes, hypotheses, [cons1])
    result = tournament.run(k_sigma=2.0)
    print("=== CONSTRAINT RFL GEOMETRY TOURNAMENT ===")
    print("Space:", axes)
    print("Hypotheses:", [h.name for h in hypotheses])
    print()
    print("ALIVE:", result["alive"])
    print("KILLED:", result["killed"])
    print()
    for h1n, h2n, d, sumt in result["conflicts"]:
        print(f"CONFLICT: {h1n} vs {h2n} (dist={d:.2f}, sum_tol={sumt:.2f})")
    for h1n, h2n, d, sumt in result["distinct_pairs"]:
        print(f"DISTINCT: {h1n} vs {h2n} (dist={d:.2f}, sum_tol={sumt:.2f})")
    print()
    print("Clusters:", result["clusters"])
    print("SCORE:", result["score"])

if __name__ == "__main__":
    demo()

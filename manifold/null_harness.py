#!/usr/bin/env python3
"""
null_harness.py — permutation nulls for the Visibility Protocol metrics
CC0-1.0.  stdlib only.  single file.  no numpy.

Answers one question per metric:
    does the observed value fall outside what a RANDOM re-partition of the
    same vectors would produce?

Null construction: pool all vectors across sections, re-partition randomly
into sections of identical sizes, recompute. This destroys section identity
while preserving the marginal distribution of vectors. If the observed value
sits inside the null band, the metric is reading the data, not the sections.

Metrics implemented: SSC, NSI, D_inter, EffectiveRankRatio, Phi, CED.

ESTIMATOR HONESTY
    Phi and CED need density estimates. Stdlib has no KSG estimator, so both
    use crude quantile binning and are marked LOW_CONFIDENCE. Their null bands
    are still valid (same estimator on both sides), but absolute values are not
    comparable to literature. Do not set thresholds off them.
"""

import random
import math
from typing import List, Callable

Vector = List[float]
Section = List[Vector]


# ─────────────────────────────────────────────────────────────────────
# MINIMAL LINALG
# ─────────────────────────────────────────────────────────────────────

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def centroid(vs):
    n = len(vs)
    d = len(vs[0])
    return [sum(v[i] for v in vs) / n for i in range(d)]


def cosine(a, b):
    na, nb = norm(a), norm(b)
    return dot(a, b) / (na * nb) if na and nb else 0.0


def scatter(vs):
    """d x d scatter matrix X^T X. Shares all nonzero eigenvalues with the
    n x n Gram matrix, and d << n, so this is the cheap side of the identity."""
    d = len(vs[0])
    return [[sum(v[i] * v[j] for v in vs) for j in range(d)] for i in range(d)]


def jacobi_eigenvalues(A, sweeps=30):
    """Eigenvalues of a symmetric matrix via cyclic Jacobi rotations."""
    n = len(A)
    M = [row[:] for row in A]
    for _ in range(sweeps):
        off = sum(M[i][j] ** 2 for i in range(n) for j in range(n) if i != j)
        if off < 1e-12:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(M[p][q]) < 1e-14:
                    continue
                theta = (M[q][q] - M[p][p]) / (2 * M[p][q])
                t = math.copysign(1.0, theta) / (
                    abs(theta) + math.sqrt(theta * theta + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(n):
                    Mkp, Mkq = M[k][p], M[k][q]
                    M[k][p] = c * Mkp - s * Mkq
                    M[k][q] = s * Mkp + c * Mkq
                for k in range(n):
                    Mpk, Mqk = M[p][k], M[q][k]
                    M[p][k] = c * Mpk - s * Mqk
                    M[q][k] = s * Mpk + c * Mqk
    return sorted((M[i][i] for i in range(n)), reverse=True)


def shannon(ps):
    return -sum(p * math.log(p) for p in ps if p > 1e-12)


# ─────────────────────────────────────────────────────────────────────
# METRICS  — each takes List[Section], returns a float
# ─────────────────────────────────────────────────────────────────────

def effective_rank(vs) -> float:
    """Roy & Vetterli: exp(H(normalized spectrum)). Continuous rank measure."""
    ev = [max(e, 0.0) for e in jacobi_eigenvalues(scatter(vs))]
    tot = sum(ev)
    if tot <= 0:
        return 0.0
    return math.exp(shannon([e / tot for e in ev]))


def m_effective_rank_ratio(sections: List[Section]) -> float:
    """Doc's Adversarial-2 fix. Low ratio = sections collapsing into each other."""
    r_parts = sum(effective_rank(s) for s in sections)
    pooled = [v for s in sections for v in s]
    r_comb = effective_rank(pooled)
    return r_comb / r_parts if r_parts else 0.0


def m_nsi(sections: List[Section]) -> float:
    """Niche Saturation: mean pairwise cosine between section centroids."""
    cs = [centroid(s) for s in sections]
    pairs = [(i, j) for i in range(len(cs)) for j in range(i + 1, len(cs))]
    return sum(cosine(cs[i], cs[j]) for i, j in pairs) / len(pairs)


def m_d_inter(sections: List[Section]) -> float:
    """Mean pairwise euclidean distance between section centroids."""
    cs = [centroid(s) for s in sections]
    pairs = [(i, j) for i in range(len(cs)) for j in range(i + 1, len(cs))]
    return sum(
        math.sqrt(sum((a - b) ** 2 for a, b in zip(cs[i], cs[j])))
        for i, j in pairs) / len(pairs)


def _spread_shares(sections):
    cs = [centroid(s) for s in sections]
    g = centroid(cs)
    spread = [math.sqrt(sum((a - b) ** 2 for a, b in zip(c, g))) for c in cs]
    tot = sum(spread)
    return [s / tot for s in spread] if tot else [0.0] * len(spread)


def m_ssc(sections: List[Section], frac: float = 0.05) -> float:
    """Doc's definition: COUNT of sections contributing > frac of spread.

    DEGENERATE. With k roughly comparable sections each holds ~1/k of the
    spread, which clears a 5% bar for any k <= 20, so the count pins at k and
    never moves. Zero variance under the null AND under real structure — it is
    a constant, not a measurement. Kept here to show the failure."""
    return float(sum(1 for s in _spread_shares(sections) if s > frac))


def m_ssc_hill(sections: List[Section]) -> float:
    """Replacement: Hill number q=1 = exp(Shannon) over the spread shares.
    Reads as 'effective number of distinct sections' and moves continuously,
    so it has a usable null band where the thresholded count does not."""
    return math.exp(shannon(_spread_shares(sections)))


def _bin_index(x, edges):
    lo = 0
    for e in edges:
        if x <= e:
            return lo
        lo += 1
    return lo


def _discretize(vs, bins=3, use_dims=2):
    """Quantile-bin the FIRST use_dims coordinates only.

    Binning all d coordinates gives bins**d possible codes. At d=8, bins=4
    that is 65536 codes for ~100 samples, so every vector gets a unique code,
    MI saturates at H(labels), and the metric returns a constant regardless of
    structure. That is what the null harness caught on the first run: observed
    == null low == null high, on both controls.

    Low-dim binning keeps the code space estimable. Still crude."""
    d = min(use_dims, len(vs[0]))
    edges = []
    for i in range(d):
        col = sorted(v[i] for v in vs)
        edges.append([col[int(len(col) * k / bins)] for k in range(1, bins)])
    return [tuple(_bin_index(v[i], edges[i]) for i in range(d)) for v in vs]


def _saturated(codes) -> bool:
    """True when nearly every sample has its own bin — estimator inapplicable."""
    return len(set(codes)) > len(codes) / 3


def m_phi(sections: List[Section]) -> float:
    """Exchange rate as NORMALIZED MI: I(X;Y)/sqrt(H(X)H(Y)). Dimensionless,
    in [0,1] — unlike the doc's 'MI normalized by variance', which is not a
    quantity. LOW_CONFIDENCE estimator (quantile binning)."""
    pooled = [v for s in sections for v in s]
    codes = _discretize(pooled)
    if _saturated(codes):
        return float('nan')
    labels = [i for i, s in enumerate(sections) for _ in s]
    n = len(codes)

    px, py, pxy = {}, {}, {}
    for c, l in zip(codes, labels):
        px[c] = px.get(c, 0) + 1
        py[l] = py.get(l, 0) + 1
        pxy[(c, l)] = pxy.get((c, l), 0) + 1

    hx = shannon([v / n for v in px.values()])
    hy = shannon([v / n for v in py.values()])
    mi = sum((v / n) * math.log((v / n) / ((px[c] / n) * (py[l] / n)))
             for (c, l), v in pxy.items())
    den = math.sqrt(hx * hy)
    return mi / den if den > 0 else 0.0


def m_ced(sections: List[Section]) -> float:
    """Cross-Entropy Divergence: mean KL between each section's binned
    distribution and the pooled distribution. LOW_CONFIDENCE estimator."""
    pooled = [v for s in sections for v in s]
    codes = _discretize(pooled)
    if _saturated(codes):
        return float('nan')
    idx, out = 0, []
    q = {}
    for c in codes:
        q[c] = q.get(c, 0) + 1
    nq = len(codes)
    for s in sections:
        sub = codes[idx:idx + len(s)]
        idx += len(s)
        p = {}
        for c in sub:
            p[c] = p.get(c, 0) + 1
        ns = len(sub)
        out.append(sum((v / ns) * math.log((v / ns) / (q[c] / nq))
                       for c, v in p.items()))
    return sum(out) / len(out)


LOW_CONFIDENCE = {"m_phi", "m_ced"}


# ─────────────────────────────────────────────────────────────────────
# THE NULL
# ─────────────────────────────────────────────────────────────────────

def permutation_null(metric: Callable, sections: List[Section],
                     n: int = 1000, seed: int = 0):
    observed = metric(sections)
    sizes = [len(s) for s in sections]
    pooled = [v for s in sections for v in s]
    rng = random.Random(seed)

    dist = []
    for _ in range(n):
        shuf = pooled[:]
        rng.shuffle(shuf)
        parts, i = [], 0
        for k in sizes:
            parts.append(shuf[i:i + k])
            i += k
        dist.append(metric(parts))

    dist.sort()
    lo = dist[int(0.025 * n)]
    hi = dist[int(0.975 * n)]
    more = sum(1 for x in dist if x >= observed)
    p = 2 * min(more, n - more) / n
    inside = lo <= observed <= hi
    return observed, lo, hi, min(p, 1.0), inside


METRICS = [m_ssc, m_ssc_hill, m_nsi, m_d_inter, m_effective_rank_ratio, m_phi, m_ced]


def run(sections, label, n=400):
    print(f"\n{label}")
    print(f"  {'metric':<26}{'observed':>10}{'null 2.5%':>11}"
          f"{'null 97.5%':>12}{'p':>8}  verdict")
    for m in METRICS:
        obs, lo, hi, p, inside = permutation_null(m, sections, n=n)
        flag = "INSIDE NULL — reads data, not sections" if inside else "outside"
        if m.__name__ in LOW_CONFIDENCE:
            flag += "  [low-conf est]"
        print(f"  {m.__name__:<26}{obs:>10.4f}{lo:>11.4f}{hi:>12.4f}"
              f"{p:>8.3f}  {flag}")


# ─────────────────────────────────────────────────────────────────────
# DEMO — positive control and negative control
# ─────────────────────────────────────────────────────────────────────

def make_sections(seed, separation, n_sec=4, per_sec=25, dim=8):
    """separation=0 -> sections are a random partition of one cloud."""
    rng = random.Random(seed)
    out = []
    for k in range(n_sec):
        anchor = [separation * (1.0 if (i + k) % n_sec == 0 else 0.0)
                  for i in range(dim)]
        out.append([[anchor[i] + rng.gauss(0, 1) for i in range(dim)]
                    for _ in range(per_sec)])
    return out


if __name__ == "__main__":
    print(__doc__)
    run(make_sections(1, separation=4.0), "POSITIVE CONTROL — real section structure")
    run(make_sections(2, separation=0.0), "NEGATIVE CONTROL — no section structure")
    print("""
READING IT
  Any metric INSIDE its null band on the negative control is behaving
  correctly. Any metric OUTSIDE its null band on the negative control is
  detecting structure that is not there — that metric is broken, not the data.

  Thresholds only become statable after this runs on YOUR sections. Until
  then every number in the protocol document is PLACEHOLDER, including the
  ones written as decimals.
""")

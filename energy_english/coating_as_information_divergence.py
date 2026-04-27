# energy_english/coating_as_information_divergence.py
"""
Alternative-compute twin of ``coating_detector.py``: information-theoretic paradigm.

Same input shape (``Trajectory``), same output shape (``Report``), same
finding categories (``silent_variable``, ``untouched_layer``,
``unexplored_phase_space``, ``uncorrelated_coupling``,
``convergence_to_expected``), same severity convention as the
statistical primary — only the reasoning path changes.

What this twin gets that the primary's Pearson correlation cannot:

- **Nonlinear couplings.** Mutual information ``I(X; Y)`` measures
  *any* statistical dependence, not just linear. Two traces related by
  ``y = x**2`` have Pearson ``|r| ≈ 0`` but high MI; the primary fires
  ``uncorrelated_coupling`` (false positive), the twin does not.
- **Distributional convergence.** Convergence-to-expected is checked
  using tail-entropy collapse + proximity, not just point distance,
  so a noisy trace that genuinely settled near the expected value
  reads as converged even when the *last sample* is off.
- **Phase-space exploration.** Total trajectory entropy across all
  traces gives a continuous measure of how much of the state space
  was actually visited, not just an event-count check.

Information-divergence findings are interchangeable with the
primary's findings: feed both reports through
``OpticsTranslator.translate(*reports)`` to ensemble. The disagreement
fixtures captured in ``tests/test_coating_as_information_divergence.py``
record the wins explicitly.

Stdlib only — ``math.log2`` and dict-based histograms. No numpy.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set

from energy_english.coating_detector import Trajectory
from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)


# ── Information-theoretic helpers ────────────────────────────────


def _bin_indices(values: List[float], bins: int) -> List[int]:
    """Discretise a 1D series into ``bins`` equal-width bins."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [0] * len(values)
    width = (hi - lo) / bins
    if width <= 0:
        return [0] * len(values)
    out: List[int] = []
    for v in values:
        idx = int((v - lo) / width)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        out.append(idx)
    return out


def _shannon_entropy(values: List[float], bins: int = 20) -> float:
    """
    H(X) in bits over a histogram of ``values``. Returns 0.0 for
    constant or near-empty series.
    """
    if len(values) < 2:
        return 0.0
    indices = _bin_indices(values, bins)
    n = len(indices)
    counts: Dict[int, int] = {}
    for i in indices:
        counts[i] = counts.get(i, 0) + 1
    h = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / n
        h -= p * math.log2(p)
    return h


def _mutual_information(
    xs: List[float],
    ys: List[float],
    bins: int = 20,
) -> float:
    """
    I(X; Y) in bits.

    Plug-in histogram estimator with the Miller-Madow bias correction:

        bias(I_plug-in) ≈ (B_xy - B_x - B_y + 1) / (2 * n)  (in nats)

    where ``B_*`` are the counts of nonzero bins in the joint and
    marginal histograms. Without correction the plug-in estimator
    overestimates MI on small samples (typical bias ≈ 0.5 bits at
    n=500 with 20 bins for independent uniform pairs); with MM
    correction the estimate stays close to zero for genuinely
    independent series and undisturbed for high-MI dependent ones.

    Returns 0.0 when sample size is below 2 or one series is constant.
    """
    n = min(len(xs), len(ys))
    if n < 2:
        return 0.0
    xs = xs[:n]
    ys = ys[:n]

    xi = _bin_indices(xs, bins)
    yi = _bin_indices(ys, bins)

    if not xi or not yi:
        return 0.0

    joint: Dict[tuple, int] = {}
    x_counts: Dict[int, int] = {}
    y_counts: Dict[int, int] = {}
    for i in range(n):
        key = (xi[i], yi[i])
        joint[key] = joint.get(key, 0) + 1
        x_counts[xi[i]] = x_counts.get(xi[i], 0) + 1
        y_counts[yi[i]] = y_counts.get(yi[i], 0) + 1

    mi = 0.0
    for (x, y), c in joint.items():
        if c <= 0:
            continue
        p_xy = c / n
        p_x = x_counts[x] / n
        p_y = y_counts[y] / n
        if p_x <= 0 or p_y <= 0:
            continue
        mi += p_xy * math.log2(p_xy / (p_x * p_y))

    # Miller-Madow correction (in bits — divide nats by ln 2).
    b_xy = sum(1 for c in joint.values() if c > 0)
    b_x = sum(1 for c in x_counts.values() if c > 0)
    b_y = sum(1 for c in y_counts.values() if c > 0)
    correction_bits = (b_xy - b_x - b_y + 1) / (2.0 * n * math.log(2.0))

    return max(0.0, mi - correction_bits)


def _convergence_signal(
    trace: List[float],
    expected: float,
    tail_fraction: float = 0.2,
    bins: int = 20,
) -> float:
    """
    Returns a score in [0, 1]. High = the trace has settled near the
    expected value.

    Combines two factors:

    1. *Proximity*. ``1 - |tail_mean - expected| / full_range`` — how
       close the tail mean is to the expected value, measured in units
       of the trace's full range.
    2. *Settledness*. The tail's entropy is computed against the
       FULL TRACE's bin edges (not the tail's own range), so a tightly
       clustered tail at the end of a wide-ranging ramp scores
       ~1.0 even with sample-noise inside its own narrow range.

    Score is the product: high only when both proximity and settledness
    are high. A single number the detector can threshold cleanly.
    """
    n = len(trace)
    if n < 5:
        return 0.0
    tail_n = max(2, int(n * tail_fraction))
    tail = trace[-tail_n:]

    tail_mean = sum(tail) / len(tail)
    full_range = max(trace) - min(trace)
    if full_range <= 0:
        # constant trace — converged iff the constant matches expected
        return 1.0 if abs(tail_mean - expected) < 1e-9 else 0.0

    proximity = max(0.0, 1.0 - abs(tail_mean - expected) / full_range)

    # Entropy of the tail against full-trace bin edges.
    lo, hi = min(trace), max(trace)
    width = (hi - lo) / bins
    if width <= 0:
        return proximity  # degenerate — proximity is the only signal
    tail_bins: List[int] = []
    for v in tail:
        idx = int((v - lo) / width)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        tail_bins.append(idx)

    counts: Dict[int, int] = {}
    for b in tail_bins:
        counts[b] = counts.get(b, 0) + 1
    n_t = len(tail_bins)
    h_tail = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / n_t
        h_tail -= p * math.log2(p)

    h_max = math.log2(bins) if bins > 1 else 1.0
    settled = 1.0 - (h_tail / h_max if h_max > 0 else 0.0)

    return proximity * settled


# ── Detector ─────────────────────────────────────────────────────


class InformationDivergenceCoatingDetector:
    """
    Information-theoretic twin of
    ``coating_detector.CoatingDetector``. Drop-in by API; different
    reasoning. ``detect(trajectory) -> Report`` returns the same shape.

    Tunables (all in bits except where noted):

      entropy_floor          — H(trace) at or below this counts as
                               ``untouched_layer``.
      mutual_info_floor      — I(X; Y) below this counts as
                               ``uncorrelated_coupling``. Default chosen
                               above the noise floor of the
                               Miller-Madow-corrected estimator on
                               typical sample sizes.
      convergence_threshold  — convergence_signal at or above this fires
                               ``convergence_to_expected``. (unitless,
                               0..1).
      bins                   — histogram bin count for all estimators.
      unexplored_min_iters   — runs shorter than this won't fire the
                               unexplored_phase_space finding (matches
                               the primary's gating).

    The unexplored_phase_space gate intentionally mirrors the primary's
    semantics (``no events + long run``) and surfaces the joint entropy
    in the rationale. Disagreement with the primary belongs in
    explicit edge-case fixtures, not in baseline strictness.
    """

    def __init__(
        self,
        entropy_floor: float = 0.05,
        mutual_info_floor: float = 0.30,
        convergence_threshold: float = 0.90,
        bins: int = 20,
        unexplored_min_iters: int = 50,
    ):
        self.entropy_floor = entropy_floor
        self.mutual_info_floor = mutual_info_floor
        self.convergence_threshold = convergence_threshold
        self.bins = bins
        self.unexplored_min_iters = unexplored_min_iters

    def detect(self, traj: Trajectory) -> Report:
        findings: List[Finding] = []
        findings.extend(self._silent_variables(traj))
        findings.extend(self._untouched_layers(traj))
        findings.extend(self._unexplored_phase_space(traj))
        findings.extend(self._uncorrelated_couplings(traj))
        findings.extend(self._convergence_to_expected(traj))

        return Report(
            verdict=verdict_from(findings),
            findings=findings,
            suggested_response=self._suggested_response(findings),
        )

    # -- detectors ------------------------------------------------

    def _silent_variables(self, traj: Trajectory) -> List[Finding]:
        # Same set-difference as the primary — silent_variable is
        # definitionally about parameter sweep coverage, which is a
        # set membership question, not an information-theoretic one.
        # The rationale strings cite "zero entropy contribution" so
        # the optics translator surfaces the consistent paradigm.
        out: List[Finding] = []
        for name in traj.parameters:
            if name in traj.varied_parameters:
                continue
            out.append(Finding(
                category="silent_variable",
                severity=SEVERITY_WARN,
                span=name,
                rationale=(
                    f"parameter '{name}' contributed zero entropy across "
                    "the run (was used but never varied)"
                ),
                reframe=(
                    f"sweep '{name}' across a relevant range, or mark it "
                    "explicitly as silent in the next run"
                ),
            ))
        return out

    def _untouched_layers(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for name, trace in traj.traces.items():
            h = _shannon_entropy(trace, bins=self.bins)
            if h <= self.entropy_floor:
                out.append(Finding(
                    category="untouched_layer",
                    severity=SEVERITY_WARN,
                    span=name,
                    rationale=(
                        f"trace '{name}' has Shannon entropy {h:.3f} bits "
                        f"<= floor {self.entropy_floor} (state-space concentrated "
                        "in one or two bins)"
                    ),
                    reframe=(
                        f"perturb an input that should move '{name}' or extend "
                        "the run until its distribution spreads"
                    ),
                ))
        return out

    def _unexplored_phase_space(self, traj: Trajectory) -> List[Finding]:
        if traj.num_iterations < self.unexplored_min_iters:
            return []
        if traj.events:
            return []

        total_h = sum(
            _shannon_entropy(t, bins=self.bins)
            for t in traj.traces.values()
        )
        return [Finding(
            category="unexplored_phase_space",
            severity=SEVERITY_BLOCK,
            span=f"<{traj.num_iterations} iters, 0 events, H_total={total_h:.3f} bits>",
            rationale=(
                f"no mode transition / threshold crossing / bifurcation across "
                f"{traj.num_iterations} iterations; joint trace entropy "
                f"{total_h:.3f} bits gives an information-theoretic measure of "
                "how thin the visited region is"
            ),
            reframe=(
                "drive a parameter beyond a threshold; if no event fires the "
                "regime may be genuinely flat, otherwise the sim is coating"
            ),
        )]

    def _uncorrelated_couplings(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for source, relation, target in traj.declared_couplings:
            xs = traj.traces.get(source)
            ys = traj.traces.get(target)
            if not xs or not ys:
                # Same blocker the primary emits — missing trace.
                out.append(Finding(
                    category="uncorrelated_coupling",
                    severity=SEVERITY_BLOCK,
                    span=f"({source}, {relation}, {target})",
                    rationale=(
                        "declared coupling references trace(s) not present"
                    ),
                    reframe=(
                        "either drop the coupling claim or add the missing "
                        "trace to the trajectory"
                    ),
                ))
                continue

            mi = _mutual_information(xs, ys, bins=self.bins)
            if mi < self.mutual_info_floor:
                out.append(Finding(
                    category="uncorrelated_coupling",
                    severity=SEVERITY_BLOCK,
                    span=f"({source}, {relation}, {target})",
                    rationale=(
                        f"mutual information I(source; target) = {mi:.3f} bits "
                        f"below floor {self.mutual_info_floor}; the endpoints "
                        "share no measurable information"
                    ),
                    reframe=(
                        "drop the coupling claim, OR sweep an input that "
                        "should drive the source until information transfer "
                        "appears"
                    ),
                ))
            # Note: when MI >= floor we deliberately do NOT fire, even
            # if Pearson correlation would have. That is the headline
            # disagreement-with-primary signature: nonlinear dependence
            # is real coupling.
        return out

    def _convergence_to_expected(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for name, expected in traj.expected_finals.items():
            trace = traj.traces.get(name)
            if not trace:
                continue
            score = _convergence_signal(
                trace, expected,
                bins=self.bins,
            )
            if score >= self.convergence_threshold:
                out.append(Finding(
                    category="convergence_to_expected",
                    severity=SEVERITY_WARN,
                    span=name,
                    rationale=(
                        f"convergence_signal({name}) = {score:.3f} >= "
                        f"threshold {self.convergence_threshold} "
                        "(tail mean near expected AND tail entropy collapsed)"
                    ),
                    reframe=(
                        "convergence is not confirmation. read this finding "
                        "alongside silent_variable / untouched_layer / "
                        "unexplored_phase_space results."
                    ),
                ))
        return out

    # -- suggested response ---------------------------------------

    def _suggested_response(self, findings: List[Finding]) -> Optional[str]:
        if not findings:
            return None
        order: List[str] = []
        seen: Set[str] = set()
        for f in sorted(
            findings,
            key=lambda x: 0 if x.severity == SEVERITY_BLOCK else 1,
        ):
            if f.category not in seen:
                order.append(f.category)
                seen.add(f.category)

        lines = [
            "Information-divergence trajectory findings.",
            "",
            f"Categories: {', '.join(order) if order else '—'}",
        ]
        for f in findings:
            lines.append("")
            lines.append(f"[{f.category}] severity={f.severity}")
            lines.append(f"  span: {f.span}")
            lines.append(f"  rationale: {f.rationale}")
            if f.reframe:
                lines.append(f"  reframe: {f.reframe}")
        return "\n".join(lines)

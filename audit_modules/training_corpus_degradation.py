#!/usr/bin/env python3
"""
audit_modules/training_corpus_degradation.py

Training corpus degradation audit: tracks whether the model's effective
training corpus is narrowing toward synthetic-only data, reducing diversity.

CC0 / stdlib-only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class CorpusAuditRecord:
    source_label: str
    share_pct: float
    convergence_strength: float
    is_synthetic: bool
    degradation_risk: float


@dataclass
class DegradationReport:
    records: List[CorpusAuditRecord]
    mean_corpus_share: float
    mean_convergence_strength: float
    model_collapse_risk: float
    synthetic_fraction: float
    verdict: str
    flags: List[str] = field(default_factory=list)


_DEFAULT_CORPUS: List[Dict[str, Any]] = [
    {"source": "web_crawl",         "share": 0.45, "convergence": 0.40, "synthetic": False},
    {"source": "books",             "share": 0.20, "convergence": 0.55, "synthetic": False},
    {"source": "academic_papers",   "share": 0.15, "convergence": 0.70, "synthetic": False},
    {"source": "code_repos",        "share": 0.10, "convergence": 0.60, "synthetic": False},
    {"source": "synthetic_rlhf",    "share": 0.07, "convergence": 0.90, "synthetic": True},
    {"source": "synthetic_distill", "share": 0.03, "convergence": 0.95, "synthetic": True},
]

_cached_report: Optional[DegradationReport] = None


def _build_report(corpus: List[Dict[str, Any]] = None) -> DegradationReport:
    src = corpus or _DEFAULT_CORPUS
    records = []
    for r in src:
        risk = min(r["convergence"] * (1.5 if r["synthetic"] else 0.5), 1.0)
        records.append(CorpusAuditRecord(
            source_label=r["source"],
            share_pct=r["share"],
            convergence_strength=r["convergence"],
            is_synthetic=r["synthetic"],
            degradation_risk=round(risk, 3),
        ))

    n = max(len(records), 1)
    mc_share    = round(sum(r.share_pct for r in records) / n, 4)
    mc_conv     = round(sum(r.convergence_strength for r in records) / n, 4)
    synth_frac  = round(sum(r.share_pct for r in records if r.is_synthetic), 4)
    collapse    = round(
        min(sum(r.share_pct * r.convergence_strength for r in records if r.is_synthetic), 1.0), 4
    )

    if collapse > 0.15:
        verdict = "COLLAPSE_RISK"
    elif synth_frac > 0.20:
        verdict = "DEGRADING"
    else:
        verdict = "STABLE"

    flags = []
    if synth_frac > 0.20:
        flags.append(f"SYNTHETIC_FRACTION_HIGH: {synth_frac:.0%}")
    if collapse > 0.10:
        flags.append(f"MODEL_COLLAPSE_RISK: {collapse:.3f}")

    return DegradationReport(
        records=records,
        mean_corpus_share=mc_share,
        mean_convergence_strength=mc_conv,
        model_collapse_risk=collapse,
        synthetic_fraction=synth_frac,
        verdict=verdict,
        flags=flags,
    )


def current_audit(corpus: List[Dict[str, Any]] = None) -> DegradationReport:
    global _cached_report
    _cached_report = _build_report(corpus)
    return _cached_report


def mean_corpus_share(corpus: List[Dict[str, Any]] = None) -> float:
    return current_audit(corpus).mean_corpus_share


def mean_convergence_strength(corpus: List[Dict[str, Any]] = None) -> float:
    return current_audit(corpus).mean_convergence_strength


def model_collapse_risk(corpus: List[Dict[str, Any]] = None) -> float:
    return current_audit(corpus).model_collapse_risk


def joint_substrate_audit(
    substrate_health: float,
    substrate_score: float = 0.0,
) -> Dict[str, Any]:
    report = _cached_report or _build_report()
    joint_severity = round((substrate_score * 0.5) + (report.model_collapse_risk * 0.5), 4)
    if joint_severity > 0.4:
        joint_verdict = "CRITICAL"
    elif joint_severity > 0.25:
        joint_verdict = "WARN"
    else:
        joint_verdict = "PASS"
    joint_signal = joint_severity
    regime = (
        "critical"  if joint_severity > 0.4 else
        "degrading" if joint_severity > 0.25 else
        "stable"
    )
    return {
        "substrate_health":    substrate_health,
        "corpus_verdict":      report.verdict,
        "collapse_risk":       report.model_collapse_risk,
        "synthetic_fraction":  report.synthetic_fraction,
        "joint_severity":      joint_severity,
        "joint_verdict":       joint_verdict,
        "joint_signal":        joint_signal,
        "regime":              regime,
        "flags":               report.flags,
    }

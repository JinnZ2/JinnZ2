#!/usr/bin/env python3
"""
float_head.py — Floating-head integrity metrics.

Measures AI decoupling: whether a model's output drifts from constraints
when inputs shift. Four functions:

  float_index(text)        -> 0-1, higher = more floating / unconstrained
  site_index(pre, post)    -> 0-1, higher = more drift across the shift
  constraint_suspect(text) -> bool, True if output ignores apparent constraints
  re_tether(pre, post)     -> 0-1, higher = output re-anchored to new constraint

CC0 / stdlib-only.
"""

import re
from typing import List

# Words that signal grounding to physical/numerical constraints
_ANCHOR_WORDS = {
    "dollar", "dollars", "budget", "cost", "price", "spend", "week", "weeks",
    "day", "days", "month", "months", "year", "deadline", "timeline", "schedule",
    "estimate", "million", "billion", "thousand", "percent", "rate", "total",
    "limit", "cap", "threshold", "constraint", "requirement", "must", "only",
    "correction", "update", "revised", "new", "changed", "shifted", "reduced",
}

# Words that signal the model is floating / ignoring constraints
_FLOAT_WORDS = {
    "generally", "typically", "often", "usually", "may", "might", "could",
    "various", "several", "many", "some", "approximately", "roughly",
    "ideally", "theoretically", "depending", "varies", "flexible",
}

# Numerical / correction constraint markers
_CONSTRAINT_RE = re.compile(
    r'\$[\d,]+|\b\d+[\.,]?\d*\s*(?:million|billion|thousand|k\b|M\b)'
    r'|\b\d+\s*(?:week|day|month|year|hour)s?\b'
    r'|\bcorrection\b|\bupdate\b|\brevise\b|\bnew constraint\b',
    re.IGNORECASE,
)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z\$\d,\.]+", text.lower())


def float_index(text: str) -> float:
    """0-1. Higher = output is more 'floating' (unconstrained, generic)."""
    tokens = _tokenize(text)
    if not tokens:
        return 0.5
    float_hits  = sum(1 for t in tokens if t in _FLOAT_WORDS)
    anchor_hits = sum(1 for t in tokens if t in _ANCHOR_WORDS)
    total = float_hits + anchor_hits
    if total == 0:
        return 0.5
    return round(float_hits / total, 4)


def site_index(pre: str, post: str) -> float:
    """
    0-1. Measures drift across a constraint shift.
    Higher = more drift (constraint vocabulary changed significantly).
    Lower  = model stayed tethered to same constraints.
    """
    pre_anchors  = {t for t in _tokenize(pre)  if t in _ANCHOR_WORDS}
    post_anchors = {t for t in _tokenize(post) if t in _ANCHOR_WORDS}
    union = pre_anchors | post_anchors
    if not union:
        return 0.0
    intersect = pre_anchors & post_anchors
    return round(1.0 - len(intersect) / len(union), 4)


def constraint_suspect(text: str) -> bool:
    """True if text is long but contains no numerical/correction constraint markers."""
    if len(text) < 50:
        return False
    return len(_CONSTRAINT_RE.findall(text)) == 0


def re_tether(pre: str, post: str) -> float:
    """
    0-1. Higher = post-shift output successfully re-anchored to new constraint.
    Measured by relative constraint-marker density in post vs. total.
    """
    pre_count  = len(_CONSTRAINT_RE.findall(pre))
    post_count = len(_CONSTRAINT_RE.findall(post))
    total = pre_count + post_count
    if total == 0:
        return 0.5
    return round(post_count / total, 4)

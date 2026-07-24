"""
entrain.py -- zeitgeber: phase-lock tracking between a module and its primary.
CC0. stdlib only.

reference_version() is the enforcement mechanism. A module that reads a
primary (a mode table, a corpus snapshot, a config) is only comparable to
another module that read the SAME version of that primary. ref_version
makes that checkable.

  ENTRAINED    -- module's ref_version matches current primary at every
                  recorded observation, or re-matched after a gap
  FREE_RUNNING -- no ref_version ever recorded: module is flying blind;
                  readings cannot be placed in primary's history
  DRIFTED      -- was entrained but has fallen behind current primary
  NEVER        -- ref_version was recorded but never matched current primary
                  (different fork, or primary was never the same)

No verdict on what the mismatch means. Phase is a structural report.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional, List


def reference_version(primary: dict) -> str:
    """
    Content-addressed fingerprint of the primary at a moment.

    `primary` is whatever the module treats as its ground truth -- a mode
    table dict, a corpus snapshot, a config. Caller supplies a stable,
    deterministic, serializable dict. reference_version() never reads the
    primary; it only fingerprints what the caller hands it.
    """
    canonical = json.dumps(primary, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


PHASES = ("ENTRAINED", "FREE_RUNNING", "DRIFTED", "NEVER")


@dataclass
class PhaseReading:
    phase: str                     # one of PHASES
    current_ref: str               # fingerprint of primary right now
    observed_refs: List[Optional[str]]
    match_count: int               # how many observations matched current
    total: int                     # total non-None observations
    loud: List[str] = field(default_factory=list)


def phase(observed_refs: List[Optional[str]], current_ref: str) -> PhaseReading:
    """
    Classify the phase relationship between a module's ref_version history
    and the current primary fingerprint.

    observed_refs   list of ref_version strings the module recorded, oldest
                    first. None entries mean the field was not recorded for
                    that observation. Empty list -> FREE_RUNNING.
    current_ref     reference_version() of primary right now.
    """
    loud: List[str] = []

    if not observed_refs:
        loud.append("no ref_version recorded -- module is flying blind; "
                    "readings cannot be compared across modules")
        return PhaseReading("FREE_RUNNING", current_ref, [], 0, 0, loud)

    none_count = sum(1 for r in observed_refs if r is None)
    live = [r for r in observed_refs if r is not None]

    if none_count:
        loud.append(f"{none_count} observation(s) carried no ref_version -- "
                    f"those readings are unlocatable in primary history")

    if not live:
        loud.append("all recorded ref_versions are None -- FREE_RUNNING")
        return PhaseReading("FREE_RUNNING", current_ref, observed_refs,
                            0, 0, loud)

    matches = [r == current_ref for r in live]
    match_count = sum(matches)
    total = len(live)

    if match_count == 0:
        unique = set(live)
        if len(unique) == 1:
            loud.append(f"module consistently references a different primary "
                        f"({live[0][:8]}...) -- possible fork, not stale version")
        else:
            loud.append(f"ref_versions are neither current nor consistent "
                        f"({len(unique)} distinct values) -- module may be "
                        f"reading multiple primaries")
        return PhaseReading("NEVER", current_ref, observed_refs,
                            0, total, loud)

    if match_count == total:
        return PhaseReading("ENTRAINED", current_ref, observed_refs,
                            match_count, total, loud)

    # mixed: some matched, some didn't
    last_match_idx = max(i for i, m in enumerate(matches) if m)
    behind = (total - 1) - last_match_idx

    if behind == 0:
        # most recent matches -- came back into phase
        out_count = total - match_count
        loud.append(f"re-entrained after {out_count} out-of-phase "
                    f"observation(s)")
        return PhaseReading("ENTRAINED", current_ref, observed_refs,
                            match_count, total, loud)
    else:
        loud.append(f"was entrained, now {behind} observation(s) behind "
                    f"current primary")
        return PhaseReading("DRIFTED", current_ref, observed_refs,
                            match_count, total, loud)

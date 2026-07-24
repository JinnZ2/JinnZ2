"""
divlog.py -- append-only NDJSON divergence log.
CC0. stdlib only. No deps.

An Entry is a snapshot of a two-module comparison at observation time.
It is a baseline record, not a complaint.

digest is what separates a baseline from a complaint list:

    same digest + different band   -> band_only
                                      real divergence: modules read the same
                                      facts and reached different conclusions.
                                      this is the case worth acting on.

    different digest + different band -> both
                                         may be different inputs, not
                                         disagreement. kept separate so it
                                         can never masquerade as band_only.

    same digest + same band        -> agreement
                                      logged because convergent agreement
                                      from identical inputs is homoplasy --
                                      cheap, not evidence.

    different digest + same band   -> digest_only
                                      convergence from different inputs.
                                      also logged; also homoplasy.

residual() classifies the SHAPE of the band_only history, never severity:

    NEW      n=1, no shape yet -- not a verdict
    FLAT     constant band pair: calibration offset, not drift
    WALKING  monotone trend in band distance: real drift
    WIDENING spread to new governing channels: structural change
    VARIABLE no pattern; not flat, not monotone, not widening

NO winner. NO cause. NO severity. T11 greps for them.
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List


# ------------------------------------------------------------------ entry

@dataclass
class Entry:
    observed_at: str            # ISO datetime
    target: str                 # domain (e.g. "site.moisture")
    subject: str                # claim or item key

    axis_a: str                 # module name (e.g. "scaffold")
    axis_b: str                 # module name (e.g. "revalidate")
    kind: str                   # band_only | both | digest_only | agreement

    band_a: str                 # clock band from axis_a
    band_b: str                 # clock band from axis_b

    digest_a: str               # fingerprint of facts axis_a read
    digest_b: str               # fingerprint of facts axis_b read

    governing_a: str            # channel that drove axis_a's band
    governing_b: str            # channel that drove axis_b's band

    ref_version: str            # fingerprint of primary at observation time

    phase_a: str                # ENTRAINED | FREE_RUNNING | DRIFTED | NEVER
    phase_b: str

    supersedes: Optional[str] = None   # prior entry key this revisits
    note: str = ""                      # operator field, never parsed

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))


# ---------------------------------------------------------------- helpers

BAND_ORD = {"FRESH": 3, "DECAYING": 2, "STALE": 1, "EXPIRED": 0,
             "UNDETERMINED": -1}


def kind_for(digest_a: str, digest_b: str,
             band_a: str, band_b: str) -> str:
    """Classify the divergence type from digests and bands alone."""
    same_d = (digest_a == digest_b)
    same_b = (band_a == band_b)
    if same_d and same_b:
        return "agreement"
    if same_d and not same_b:
        return "band_only"
    if not same_d and not same_b:
        return "both"
    return "digest_only"


def make_digest(facts: dict) -> str:
    """Deterministic fingerprint of the fact-set a module read."""
    canonical = json.dumps(facts, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# ------------------------------------------------------------------- log

class DivLog:
    """Append-only NDJSON log. Read is a full scan; file is the record."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def append(self, e: Entry) -> None:
        with self.path.open("a") as f:
            f.write(e.to_json() + "\n")

    def read(self, target: Optional[str] = None,
             subject: Optional[str] = None,
             kind: Optional[str] = None) -> List[Entry]:
        entries = []
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if target  and d.get("target")  != target:
                    continue
                if subject and d.get("subject") != subject:
                    continue
                if kind    and d.get("kind")    != kind:
                    continue
                entries.append(Entry(**d))
        return entries

    def residual(self, target: str, subject: str) -> dict:
        """
        Shape of the band_only history for this target/subject pair.
        Classifies shape only. n=1 returns NEW, not a verdict.
        """
        entries = self.read(target=target, subject=subject, kind="band_only")
        n = len(entries)

        if n == 0:
            return {"shape": "NONE", "n": 0,
                    "detail": "no band_only entries for this pair"}
        if n == 1:
            return {"shape": "NEW", "n": 1,
                    "detail": "single observation -- no shape yet"}

        bands_a  = [e.band_a      for e in entries]
        bands_b  = [e.band_b      for e in entries]
        gov_a    = [e.governing_a for e in entries]
        gov_b    = [e.governing_b for e in entries]

        # WIDENING: governing pairs diversifying over time
        gov_pairs = list(dict.fromkeys(zip(gov_a, gov_b)))  # ordered unique
        if len(gov_pairs) > 1:
            return {"shape": "WIDENING", "n": n,
                    "governing_pairs": [f"{a}/{b}" for a, b in gov_pairs],
                    "detail": "divergence has spread to new governing channels"}

        # FLAT: same band pair every time
        band_pairs = set(zip(bands_a, bands_b))
        if len(band_pairs) == 1:
            a, b = next(iter(band_pairs))
            return {"shape": "FLAT", "n": n,
                    "pair": f"{a}/{b}",
                    "detail": "constant band pair: calibration offset, not drift"}

        # WALKING: monotone trend in the signed band distance
        diffs = [BAND_ORD.get(b, -1) - BAND_ORD.get(a, -1)
                 for a, b in zip(bands_a, bands_b)]
        if all(d >= diffs[0] for d in diffs) or all(d <= diffs[0] for d in diffs):
            direction = "b_fresher" if diffs[-1] > diffs[0] else "a_fresher"
            return {"shape": "WALKING", "n": n,
                    "direction": direction,
                    "detail": "monotone trend in band distance: real drift"}

        return {"shape": "VARIABLE", "n": n,
                "detail": "no monotone trend; not flat; not widening"}

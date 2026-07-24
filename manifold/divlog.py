"""
divlog.py -- append-only NDJSON divergence log.
CC0. stdlib only. No deps.

An Entry is a snapshot of a two-module comparison at observation time.
It is a baseline record, not a complaint.

digest is what separates a baseline from a complaint list:

    same digest + different band   -> SAME_INPUTS_DIFF_BAND
                                      real divergence: modules read the same
                                      facts and reached different conclusions.
                                      this is the case worth acting on.

    different digest + different band -> DIFF_INPUTS_DIFF_BAND
                                         may be different inputs, not
                                         disagreement. kept separate so it
                                         can never masquerade as SAME_INPUTS.

    same digest + same band        -> (no syndrome) -- omitted from log
    different digest + same band   -> DIFF_INPUTS_SAME_BAND
                                      convergence from different inputs.
                                      logged; homoplasy, not evidence.

residual() classifies the SHAPE of the entry history, never severity:

    NEW          len < 2: no baseline yet -- not a verdict
    FLAT         same kind + same band pair across all entries: calibration offset
    WALKING      band pair changes monotonically: real drift
    INTERMITTENT no monotone trend; not flat; not widening
    WIDENING     distinct governing channels growing: structural spread

NO winner. NO cause. NO severity. T11 greps for them.
"""

import json
import hashlib
import dataclasses
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List


# ------------------------------------------------------------------ entry

@dataclass(frozen=True)
class Entry:
    observed_at: str            # explicit ISO datetime
    target: str                 # clock target: claim | mode_sensitivity | independence
    subject: str                # claim id / mode name / anchor id

    axis_a: str                 # module name or axis (e.g. "scaffold")
    axis_b: str                 # peer, or "PRIMARY" for a trace check
    kind: str                   # Syndrome.kind verbatim

    band_a: Optional[str]       # FRESH | DECAYING | STALE | EXPIRED | UNDETERMINED
    band_b: Optional[str]
    digest_a: str               # inputs_digest from Reading a
    digest_b: str               # inputs_digest from Reading b (or "PRIMARY")

    governing_a: Optional[str]  # channel that governed axis_a's band
    governing_b: Optional[str]

    ref_version: str            # primary fingerprint at observation time

    phase_a: Optional[str]      # ENTRAINED | FREE_RUNNING | DRIFTED | NEVER
    phase_b: Optional[str]

    supersedes: Optional[str] = None   # id of prior entry this revisits
    note: str = ""                      # operator field. free text. never parsed.
    id: str = field(default="")         # sha256[:12] of all fields except note+id

    def __post_init__(self):
        if not self.id:
            facts = {
                f.name: getattr(self, f.name)
                for f in dataclasses.fields(self)
                if f.name not in ("note", "id")
            }
            canonical = json.dumps(facts, sort_keys=True, separators=(',', ':'))
            computed = hashlib.sha256(canonical.encode()).hexdigest()[:12]
            object.__setattr__(self, "id", computed)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'))


# ---------------------------------------------------------------- helpers

BAND_ORD = {"FRESH": 3, "DECAYING": 2, "STALE": 1, "EXPIRED": 0,
             "UNDETERMINED": -1}


def kind_for(digest_a: str, digest_b: str,
             band_a: Optional[str], band_b: Optional[str]) -> str:
    """Classify the divergence type from digests and bands alone."""
    if band_a == "UNDETERMINED" or band_b == "UNDETERMINED":
        return "MISSING"
    same_d = (digest_a == digest_b)
    same_b = (band_a == band_b)
    if same_d and same_b:
        return "agreement"
    if same_d and not same_b:
        return "SAME_INPUTS_DIFF_BAND"
    if not same_d and not same_b:
        return "DIFF_INPUTS_DIFF_BAND"
    return "DIFF_INPUTS_SAME_BAND"


def make_digest(facts: dict) -> str:
    """Deterministic fingerprint of the fact-set a module read.
    None must be represented explicitly, never absent -- two modules that
    silently drop the same field must not fingerprint as identical (D3)."""
    canonical = json.dumps(facts, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# --------------------------------------------------------------- residual

@dataclass
class Residual:
    shape: str                # NEW | FLAT | WALKING | INTERMITTENT | WIDENING
    n: int                    # number of entries considered
    entry_ids: List[str]      # which entry ids were read
    detail: str
    extra: dict = field(default_factory=dict)   # pair, direction, governing_pairs


def residual(entries: List[Entry]) -> Residual:
    """
    Classify the SHAPE of a filtered entry history. Never its severity.
    Caller filters first (via history()) then passes the list here.
    n < 2 returns NEW -- not a verdict.
    """
    ids = [e.id for e in entries]
    n = len(entries)

    if n < 2:
        return Residual("NEW", n, ids,
                        "fewer than 2 entries -- no baseline yet")

    bands_a = [e.band_a for e in entries]
    bands_b = [e.band_b for e in entries]
    gov_a   = [e.governing_a for e in entries]
    gov_b   = [e.governing_b for e in entries]

    # WIDENING: governing pairs diversifying over time
    gov_pairs = list(dict.fromkeys(zip(gov_a, gov_b)))   # ordered, unique
    if len(gov_pairs) > 1:
        return Residual("WIDENING", n, ids,
                        "divergence spread to new governing channels",
                        {"governing_pairs": [f"{a}/{b}" for a, b in gov_pairs]})

    # FLAT: same kind AND same band pair throughout
    kinds     = {e.kind for e in entries}
    band_pairs = set(zip(bands_a, bands_b))
    if len(kinds) == 1 and len(band_pairs) == 1:
        a, b = next(iter(band_pairs))
        return Residual("FLAT", n, ids,
                        "same kind + same band pair: calibration offset, not drift",
                        {"pair": f"{a}/{b}"})

    # WALKING: monotone trend in signed band distance
    diffs = [BAND_ORD.get(b, -1) - BAND_ORD.get(a, -1)
             for a, b in zip(bands_a, bands_b)
             if a is not None and b is not None]
    if diffs and (
        all(d >= diffs[0] for d in diffs) or
        all(d <= diffs[0] for d in diffs)
    ):
        direction = "b_fresher" if diffs[-1] > diffs[0] else "a_fresher"
        return Residual("WALKING", n, ids,
                        "monotone trend in band distance: real drift",
                        {"direction": direction})

    return Residual("INTERMITTENT", n, ids,
                    "no monotone trend; not flat; not widening")


# ------------------------------------------------------------------- log

class DivLog:
    """Append-only NDJSON log. File is the record; scan is the query."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def append(self, e: Entry) -> str:
        """Opens in append mode only. Returns the entry id."""
        with self.path.open("a") as f:
            f.write(e.to_json() + "\n")
        return e.id

    def load(self, target: Optional[str] = None,
             subject: Optional[str] = None,
             kind: Optional[str] = None,
             axis_a: Optional[str] = None,
             axis_b: Optional[str] = None) -> List[Entry]:
        """Full scan with optional filters. Preserves file order."""
        entries = []
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if target  and d.get("target")  != target:  continue
                if subject and d.get("subject") != subject:  continue
                if kind    and d.get("kind")    != kind:     continue
                if axis_a  and d.get("axis_a")  != axis_a:  continue
                if axis_b  and d.get("axis_b")  != axis_b:  continue
                entries.append(Entry(**d))
        return entries

    def history(self, target: str, subject: str,
                axis_a: Optional[str] = None,
                axis_b: Optional[str] = None) -> List[Entry]:
        """The baseline query: same pair, same subject, time-ordered."""
        return sorted(
            self.load(target=target, subject=subject, axis_a=axis_a, axis_b=axis_b),
            key=lambda e: e.observed_at,
        )

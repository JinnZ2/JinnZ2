"""
syndrome.py -- parity, trace, and mesh. No aggregation.
CC0. stdlib only. Imports divlog.

parity()   reads digest and band ONLY. Does not read governing or phase.
           Returns the kind string (band_only / both / digest_only / agreement).
           Thin wrapper on divlog.kind_for() -- the cell label, not a verdict.

trace()    locates an entry in primary's version history by matching
           entry.ref_version against a primary_history list. Returns the
           position and the surrounding context. Does not interpret whether
           the position is good or bad.

mesh()     the 3x3: three parity kinds (band_only / both / digest_only)
           x three phase buckets (entrained / drifted / unanchored).
           Returns a flat list of dicts -- one row per entry -- with the
           cell coordinates attached. NO aggregation: no counts, no sums,
           no compression. Caller decides what to do with the structure.

           agreement entries are included in the flat list but sit outside
           the 3x3 -- they carry kind="agreement" and cell=None.
"""

from typing import List, Dict, Optional, Any
from divlog import Entry, kind_for


# ------------------------------------------------------------------- parity

def parity(digest_a: str, digest_b: str,
           band_a: str, band_b: str) -> str:
    """
    Classify a pair of readings from digests and bands alone.
    Governing and phase are deliberately excluded -- they belong to trace().
    """
    return kind_for(digest_a, digest_b, band_a, band_b)


# -------------------------------------------------------------------- trace

def trace(entry: Entry, primary_history: List[Dict]) -> dict:
    """
    Locate entry.ref_version in primary's version history.

    primary_history is a list of dicts, oldest first, each with at least:
        {"ref": str, "at": str}  -- fingerprint and timestamp of that version

    Returns:
        found       bool -- whether ref_version appears in history
        index       int | None -- 0-based position (None if not found)
        at          str | None -- timestamp of that primary version
        lag         int | None -- how many primary versions behind current
        context     list of dicts -- the surrounding ±1 entries in history
    """
    if not primary_history:
        return {"found": False, "index": None, "at": None,
                "lag": None, "context": [],
                "loud": ["primary_history is empty -- trace has nothing "
                         "to locate against"]}

    loud: List[str] = []
    target = entry.ref_version
    idx = None
    for i, row in enumerate(primary_history):
        if row.get("ref") == target:
            idx = i
            break

    if idx is None:
        loud.append(f"ref_version {target[:8]}... not found in primary "
                    f"history ({len(primary_history)} version(s)) -- entry "
                    f"was taken against a primary not in this history")
        return {"found": False, "index": None, "at": None,
                "lag": None, "context": [], "loud": loud}

    lag = (len(primary_history) - 1) - idx
    context = primary_history[max(0, idx - 1): idx + 2]
    return {"found": True, "index": idx,
            "at": primary_history[idx].get("at"),
            "lag": lag, "context": context, "loud": loud}


# --------------------------------------------------------------------- mesh

# the 3 parity kinds that form the divergence space (agreement is out-of-cell)
_PARITY_KINDS = ("band_only", "both", "digest_only")

# the 3 phase buckets
# ENTRAINED -> entrained
# DRIFTED   -> drifted
# FREE_RUNNING | NEVER -> unanchored
def _phase_bucket(phase: str) -> str:
    if phase == "ENTRAINED":
        return "entrained"
    if phase == "DRIFTED":
        return "drifted"
    return "unanchored"


def mesh(entries: List[Entry]) -> List[dict]:
    """
    The 3x3: parity kind x phase bucket, as a flat list.

    Each row is one entry with its cell coordinates attached:
        {kind, phase_bucket_a, phase_bucket_b, cell, entry}

    cell is "kind/phase_a/phase_b" for in-matrix entries.
    cell is None for agreement entries (they sit outside the 3x3).

    No aggregation. No counts. No compression.
    Caller groups, counts, or displays as needed.
    """
    rows: List[dict] = []
    for e in entries:
        k = parity(e.digest_a, e.digest_b, e.band_a, e.band_b)
        pb_a = _phase_bucket(e.phase_a)
        pb_b = _phase_bucket(e.phase_b)
        cell = f"{k}/{pb_a}/{pb_b}" if k in _PARITY_KINDS else None
        rows.append({
            "kind":          k,
            "phase_bucket_a": pb_a,
            "phase_bucket_b": pb_b,
            "cell":          cell,
            "entry":         e,
        })
    # stable sort: kind order, then phase buckets
    kind_ord = {k: i for i, k in enumerate(_PARITY_KINDS)}
    kind_ord["agreement"] = len(_PARITY_KINDS)
    buck_ord = {"entrained": 0, "drifted": 1, "unanchored": 2}
    rows.sort(key=lambda r: (
        kind_ord.get(r["kind"], 99),
        buck_ord.get(r["phase_bucket_a"], 9),
        buck_ord.get(r["phase_bucket_b"], 9),
    ))
    return rows

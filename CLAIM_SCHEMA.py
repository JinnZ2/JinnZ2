"""
CLAIM_SCHEMA.py — canonical compressed form for AI readers
==========================================================

Drop into any repo. Token-minimal, binary-serializable,
physics-anchored. CC0.

Companion to ``DIFFERENTIAL_FRAME.md`` at the repo root: every claim
in the repository is a differential equation under bounds. This file
specifies the **schema, the codec, and the loader** so AI readers
can ingest claims at ~5 tokens/claim post-load instead of ~600
tokens of prose.

Four layers:

  1. JSON schema      — the dict shape every claim satisfies.
  2. Line format      — one claim per line, pipe-delimited (.claims).
  3. Binary codec     — fixed-width struct (.claims.bin).
  4. Lookup table     — repo-level CLAIM_TABLE.json that resolves
                        indices into rates / bounds / cond / rel /
                        fail / meas strings.

AI reader protocol:

    1. Load CLAIM_TABLE.json once (~2-5 KB).
    2. Read .claims (line-per-claim, ~80 tok / claim) or
       .claims.bin (~32 B / claim, decodes via this module).
    3. Each claim deserialises into the CLAIM_SCHEMA dict.
    4. Operate on dX/dt + bounds + conditions.
    5. Never collapse to noun-identity. No exceptions.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ── Layer 1: JSON schema (template) ───────────────────────────────


CLAIM_SCHEMA = {
    "id":     "<short_hash>",          # 8-char id, e.g. "mulch_h2o"
    "rate":   "dX/dt = <expr>",        # the differential equation
    "bounds": ["<spatial>", "<temporal>", "<scale>"],
    "cond":   ["<bool_expr>"],         # list of constraints
    "rel":    ["<id>"],                # coupled claim IDs
    "fail":   ["<bool_expr>"],         # invalid_if conditions
    "meas":   ["<observable>"],        # how dX/dt is measured
    "cyc":    0,                        # cycle class enum (see below)
}


CYCLE_ENUM = {
    0: "instantaneous",
    1: "diurnal",
    2: "seasonal",
    3: "annual",
    4: "generational",
    5: "century",
    6: "geologic",
}


# Hard limits imposed by the binary codec. Each per-claim list
# (cond / rel / fail / meas) is a 16-bit bitmask over the table's
# first 16 entries. If a repo grows past 16 distinct values in any
# of these four categories, the codec needs a wider mask — pin v0
# at 16 and document the limit explicitly.
MAX_MASK_BITS = 16

# struct format for one packed claim:
#   I  4B  id_hash         (CRC32 of the id string)
#   H  2B  rate_idx        (index into table["rates"])
#   H  2B  bounds_idx      (index into table["bounds"])
#   H  2B  cond_mask       (bits over table["cond"][:16])
#   H  2B  rel_mask        (bits over table["rel"][:16])
#   H  2B  fail_mask       (bits over table["fail"][:16])
#   H  2B  meas_mask       (bits over table["meas"][:16])
#   B  1B  cyc             (cycle class enum)
#                           total = 17 bytes per claim
_CLAIM_STRUCT = ">IHHHHHHB"
CLAIM_BYTES = struct.calcsize(_CLAIM_STRUCT)


# Field order in the line format and the binary header.
# Single source of truth for serialisation.
LINE_FIELDS = ("id", "rate", "bounds", "cond", "rel", "fail", "meas", "cyc")


# ── Layer 2: line format (.claims) ────────────────────────────────


def encode_line(claim: Dict[str, Any]) -> str:
    """Pack a claim dict into one pipe-delimited line.

    bounds / cond / rel / fail / meas are joined with commas. cyc is
    rendered as the integer enum key. Newlines and pipes inside any
    field are NOT escaped — keep field values clean.
    """
    bounds = ",".join(claim.get("bounds") or [])
    cond = ",".join(claim.get("cond") or [])
    rel = ",".join(claim.get("rel") or [])
    fail = ",".join(claim.get("fail") or [])
    meas = ",".join(claim.get("meas") or [])
    cyc = int(claim.get("cyc", 0))
    return "|".join((
        claim["id"], claim["rate"], bounds, cond, rel, fail, meas, str(cyc),
    ))


def parse_line(line: str) -> Dict[str, Any]:
    """Parse one ``.claims`` line into a claim dict."""
    parts = line.rstrip("\n").split("|")
    if len(parts) != 8:
        raise ValueError(
            f"expected 8 pipe-delimited fields, got {len(parts)}: {line!r}"
        )
    cid, rate, bounds, cond, rel, fail, meas, cyc = parts
    return {
        "id": cid,
        "rate": rate,
        "bounds": [b for b in bounds.split(",") if b],
        "cond": [c for c in cond.split(",") if c],
        "rel": [r for r in rel.split(",") if r],
        "fail": [f for f in fail.split(",") if f],
        "meas": [m for m in meas.split(",") if m],
        "cyc": int(cyc) if cyc else 0,
    }


def read_claims(path: str | Path) -> List[Dict[str, Any]]:
    """Read every line of a ``.claims`` file as a list of claim dicts."""
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            out.append(parse_line(line))
    return out


def write_claims(claims: Iterable[Dict[str, Any]], path: str | Path) -> None:
    """Write claim dicts to a ``.claims`` file, one per line."""
    with open(path, "w", encoding="utf-8") as f:
        for claim in claims:
            f.write(encode_line(claim) + "\n")


# ── Layer 4: lookup table (the repo CLAIM_TABLE.json) ─────────────


def load_table(path: str | Path) -> Dict[str, List[str]]:
    """Load the repo-level shared lookup table."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalise: every required key present, every value is a list of strings.
    out = {}
    for key in ("rates", "bounds", "cond", "rel", "fail", "meas"):
        out[key] = list(data.get(key) or [])
    return out


def build_table(claims: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Walk a set of claim dicts and emit a deduplicated lookup table.

    First-seen-first-indexed: index 0 of each list is the first time
    that value appears in iteration order. Useful for round-tripping
    a known set of claims through the binary codec.
    """
    table: Dict[str, List[str]] = {
        "rates": [], "bounds": [],
        "cond": [], "rel": [], "fail": [], "meas": [],
    }
    seen_rates: set = set()
    seen_bounds: set = set()
    seen_cond: set = set()
    seen_rel: set = set()
    seen_fail: set = set()
    seen_meas: set = set()

    def add(bucket: str, seen: set, value: str) -> None:
        if value and value not in seen:
            seen.add(value)
            table[bucket].append(value)

    for claim in claims:
        add("rates", seen_rates, claim.get("rate", ""))
        bounds_str = ",".join(claim.get("bounds") or [])
        add("bounds", seen_bounds, bounds_str)
        for c in claim.get("cond") or []:
            add("cond", seen_cond, c)
        for r in claim.get("rel") or []:
            add("rel", seen_rel, r)
        for f in claim.get("fail") or []:
            add("fail", seen_fail, f)
        for m in claim.get("meas") or []:
            add("meas", seen_meas, m)
    return table


def write_table(table: Dict[str, List[str]], path: str | Path) -> None:
    """Write a ``CLAIM_TABLE.json`` with deterministic ordering."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ── Layer 3: binary codec (.claims.bin) ───────────────────────────


def id_hash(claim_id: str) -> int:
    """32-bit CRC of the id string. Stable across runs and platforms."""
    return zlib.crc32(claim_id.encode("utf-8")) & 0xFFFFFFFF


def _mask_for(values: List[str], universe: List[str]) -> int:
    """Build a 16-bit bitmask: bit i set iff universe[i] is in values.

    Raises ValueError if any value is missing from the universe or if
    its index is beyond the 16-bit limit.
    """
    mask = 0
    for v in values:
        try:
            idx = universe.index(v)
        except ValueError as e:
            raise ValueError(
                f"value {v!r} not present in lookup table"
            ) from e
        if idx >= MAX_MASK_BITS:
            raise ValueError(
                f"value {v!r} at index {idx} exceeds 16-bit mask limit "
                f"({MAX_MASK_BITS}); the table needs to be reordered or "
                "the codec widened"
            )
        mask |= 1 << idx
    return mask


def unmask(m: int) -> List[int]:
    """Reverse of _mask_for at the index level."""
    return [i for i in range(MAX_MASK_BITS) if m & (1 << i)]


def encode_claim(claim: Dict[str, Any], table: Dict[str, List[str]]) -> bytes:
    """Pack one claim dict into ``CLAIM_BYTES`` bytes using the table."""
    bounds_str = ",".join(claim.get("bounds") or [])
    try:
        rate_idx = table["rates"].index(claim["rate"])
    except ValueError as e:
        raise ValueError(
            f"rate {claim['rate']!r} not in table['rates']"
        ) from e
    try:
        bounds_idx = table["bounds"].index(bounds_str)
    except ValueError as e:
        raise ValueError(
            f"bounds {bounds_str!r} not in table['bounds']"
        ) from e

    return struct.pack(
        _CLAIM_STRUCT,
        id_hash(claim["id"]),
        rate_idx,
        bounds_idx,
        _mask_for(claim.get("cond") or [], table["cond"]),
        _mask_for(claim.get("rel") or [], table["rel"]),
        _mask_for(claim.get("fail") or [], table["fail"]),
        _mask_for(claim.get("meas") or [], table["meas"]),
        int(claim.get("cyc", 0)),
    )


def decode_claim(
    blob: bytes,
    table: Dict[str, List[str]],
    *,
    id_lookup: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
    """Reverse of ``encode_claim``.

    ``id_lookup`` maps id-hash → original id string. The hash itself
    is one-way; pass an explicit lookup if you want the original
    string id back. When omitted, ``id`` is rendered as
    ``"#<hex-hash>"``.
    """
    fields = struct.unpack(_CLAIM_STRUCT, blob)
    h, rate_idx, bounds_idx, cond_m, rel_m, fail_m, meas_m, cyc = fields
    claim_id = (
        id_lookup.get(h, f"#{h:08x}") if id_lookup is not None
        else f"#{h:08x}"
    )
    bounds_str = table["bounds"][bounds_idx]
    return {
        "id":     claim_id,
        "rate":   table["rates"][rate_idx],
        "bounds": [b for b in bounds_str.split(",") if b],
        "cond":   [table["cond"][i]  for i in unmask(cond_m)],
        "rel":    [table["rel"][i]   for i in unmask(rel_m)],
        "fail":   [table["fail"][i]  for i in unmask(fail_m)],
        "meas":   [table["meas"][i]  for i in unmask(meas_m)],
        "cyc":    cyc,
    }


def write_binary(
    claims: Iterable[Dict[str, Any]],
    table: Dict[str, List[str]],
    path: str | Path,
) -> None:
    """Encode every claim and concatenate to ``path``."""
    with open(path, "wb") as f:
        for claim in claims:
            f.write(encode_claim(claim, table))


def read_binary(
    path: str | Path,
    table: Dict[str, List[str]],
    *,
    id_lookup: Optional[Dict[int, str]] = None,
) -> List[Dict[str, Any]]:
    """Decode a ``.claims.bin`` into a list of claim dicts."""
    out: List[Dict[str, Any]] = []
    with open(path, "rb") as f:
        data = f.read()
    if len(data) % CLAIM_BYTES != 0:
        raise ValueError(
            f"binary length {len(data)} is not a multiple of "
            f"CLAIM_BYTES={CLAIM_BYTES}"
        )
    for off in range(0, len(data), CLAIM_BYTES):
        out.append(decode_claim(data[off:off + CLAIM_BYTES],
                                table, id_lookup=id_lookup))
    return out


def build_id_lookup(claims: Iterable[Dict[str, Any]]) -> Dict[int, str]:
    """Build the inverse of id_hash() across a known claim set."""
    lookup: Dict[int, str] = {}
    for claim in claims:
        lookup[id_hash(claim["id"])] = claim["id"]
    return lookup


# ── AI reader protocol summary (string for inspection) ────────────


PROTOCOL = """\
1. Load CLAIM_TABLE.json (one-time cost, ~2-5KB)
2. Read .claims file (line-per-claim, pipe-delimited)
   OR load .claims.bin (binary, ~17B/claim)
3. Each claim deserializes into the CLAIM_SCHEMA dict
4. Operate on dX/dt + bounds + conditions
5. Never collapse to noun-identity. No exceptions.

Token cost per claim:
  prose         : ~600 tokens
  DIFFERENTIAL  : ~300 tokens
  line format   : ~80 tokens
  binary + table: ~5 tokens equivalent (post-load)
"""


# ── CLI smoke (round-trip) ────────────────────────────────────────


if __name__ == "__main__":  # pragma: no cover - smoke
    import sys

    repo = Path(__file__).parent
    claims_path = repo / ".claims"
    bin_path = repo / ".claims.bin"
    table_path = repo / "CLAIM_TABLE.json"

    if not claims_path.exists() or not table_path.exists():
        print("CLAIM_SCHEMA.py: no .claims or CLAIM_TABLE.json present yet.",
              file=sys.stderr)
        sys.exit(1)

    table = load_table(table_path)
    claims = read_claims(claims_path)

    print(f"loaded {len(claims)} claims, table has",
          {k: len(v) for k, v in table.items()})

    write_binary(claims, table, bin_path)
    decoded = read_binary(bin_path, table, id_lookup=build_id_lookup(claims))

    for orig, dec in zip(claims, decoded):
        assert orig["rate"] == dec["rate"], orig["id"]
        assert orig["bounds"] == dec["bounds"], orig["id"]
        assert sorted(orig["cond"]) == sorted(dec["cond"]), orig["id"]
        assert sorted(orig["rel"]) == sorted(dec["rel"]), orig["id"]
        assert sorted(orig["fail"]) == sorted(dec["fail"]), orig["id"]
        assert sorted(orig["meas"]) == sorted(dec["meas"]), orig["id"]
        assert orig["cyc"] == dec["cyc"], orig["id"]
    print(f"round-trip OK: {CLAIM_BYTES} B/claim, "
          f"{len(claims) * CLAIM_BYTES} B total in {bin_path.name}")

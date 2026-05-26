"""
pattern_library_extension.py

Generic extension to cross_model_schema.py and data_gap_protocol.py.

Caches successful gap-resolution patterns. When a DataGap is closed,
record (gap_signature, resolution_record). On a new DataGap, look up
matching signatures and suggest past resolutions before the
operator/agent has to re-derive the apparatus.

Closes the "missing piece" named in
notes/multi_agent_protocol_skeleton.md (Pattern Library):

  The skeleton treats every gap as a fresh instance. Repeated
  resolution by the same sensor sweep should be cached. The Pattern
  Library is that cache.

Falsifiable claim PLE-001 (with explicit falsifier):
  Pattern Library improves median time-to-resolution for repeated
  gap classes by >= 30% versus no-cache baseline, over N >= 20 gaps
  with at least 3 unique signature classes.
  Falsifier: a workload with >= 3 signature classes where the cache
  hit rate exceeds 50% but median time-to-resolution does not improve
  by >= 30%. That would mean past-resolution lookup is not predictive
  of current resolution, i.e. patterns are not recurring after all.

License: CC0
Dependencies: Python stdlib only
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Iterable


# ---------------------------------------------------------------------------
# Resolution record
# ---------------------------------------------------------------------------

@dataclass
class ResolutionRecord:
    """One closed gap. The thing we cache."""
    gap_id: str
    signature: str
    gap_class: str                  # one of the six GapClass names
    resolution_apparatus: str       # what made the measurement
    resolution_time_seconds: float  # wall-clock from open -> closed
    outcome_quality: float          # 0.0 (failed) .. 1.0 (perfect)
    timestamp: float                # epoch seconds when closed
    notes: str = ""


# ---------------------------------------------------------------------------
# Falsifiable claims about this extension
# ---------------------------------------------------------------------------

@dataclass
class FalsifiableClaim:
    # RULE: standalone-importable extensions (see cross_model_schema.py).
    claim_id: str
    statement: str
    measurement: str
    threshold: str
    substrate: str
    status: str = "untested"


CLAIMS = [
    FalsifiableClaim(
        claim_id="PLE-001",
        statement=(
            "Pattern Library improves median time-to-resolution for "
            "repeated gap classes by >= 30% vs no-cache baseline"
        ),
        measurement=(
            "Run identical gap stream through library-enabled and "
            "no-cache agents. Compare median resolution time over "
            "N >= 20 gaps with >= 3 unique signatures."
        ),
        threshold="library median <= 0.70 * baseline median",
        substrate="gap-resolution workflow",
    ),
    FalsifiableClaim(
        claim_id="PLE-002",
        statement=(
            "Signature collisions are <= 5% on a corpus of N >= 100 "
            "structurally distinct DataGaps when default signature "
            "fields are used"
        ),
        measurement=(
            "Generate N >= 100 distinct DataGap instances. Compute "
            "signatures. Count unique signature -> count(distinct gaps) "
            "ratio."
        ),
        threshold=(
            "fraction of signatures with > 1 structurally distinct "
            "underlying gap <= 0.05"
        ),
        substrate="signature hash function",
    ),
    FalsifiableClaim(
        claim_id="PLE-003",
        statement=(
            "Suggestion ranking by outcome_quality predicts resolution "
            "success: top-ranked suggestion succeeds >= 75% when used"
        ),
        measurement=(
            "For each suggested top-ranked apparatus actually applied, "
            "record whether it resolved the gap. Compute success rate."
        ),
        threshold="top-1 suggestion success rate >= 0.75",
        substrate="suggestion-ranking policy",
    ),
]


# ---------------------------------------------------------------------------
# Audit gates
# ---------------------------------------------------------------------------

@dataclass
class AuditGate:
    marker: str
    green_threshold: str
    yellow_threshold: str
    red_threshold: str
    action_on_red: str


AUDIT_GATES = [
    AuditGate(
        marker="suggest_without_falsification_record",
        green_threshold=(
            "every suggestion logged with: was it used, did it resolve"
        ),
        yellow_threshold="suggestion logged, outcome partially captured",
        red_threshold=(
            "suggestion returned without outcome-tracking commitment"
        ),
        action_on_red=(
            "halt; require usage-outcome callback before next suggest()"
        ),
    ),
    AuditGate(
        marker="cache_grows_unbounded",
        green_threshold=(
            "max_records_per_signature enforced AND total record count "
            "monitored"
        ),
        yellow_threshold="per-signature cap enforced, total not monitored",
        red_threshold="no cap on records",
        action_on_red=(
            "enforce LRU eviction; emit cache-size metric to "
            "ThresholdState equivalent"
        ),
    ),
    AuditGate(
        marker="suggestion_used_as_truth",
        green_threshold=(
            "suggestions tagged as 'inferred-from-past-pattern', "
            "operator confirms before action"
        ),
        yellow_threshold="suggestions used without explicit confirmation",
        red_threshold=(
            "suggestion treated as proven solution without re-verification"
        ),
        action_on_red=(
            "halt action; re-tag suggestion as inference; require "
            "operator confirm OR apparatus re-measurement"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Default signature fields
# ---------------------------------------------------------------------------

# Which fields of a DataGap (or DataGap-shaped dict) feed the hash.
# Two gaps with identical values on these fields share a signature.
DEFAULT_SIGNATURE_FIELDS = (
    "gap_class",
    "apparatus_required",
    "data_required",
)


# ---------------------------------------------------------------------------
# PatternLibrary
# ---------------------------------------------------------------------------

class PatternLibrary:
    """
    Cache of past gap-resolution records, keyed by signature.

    signature(gap) = sha256(stringified subset of gap fields)[:16]

    Per-signature cap and total LRU eviction prevent unbounded growth.
    Suggestions are ranked by recent outcome_quality descending.
    """

    def __init__(
        self,
        signature_fields: Iterable[str] = DEFAULT_SIGNATURE_FIELDS,
        max_records_per_signature: int = 10,
        max_total_records: int = 1000,
    ):
        self.signature_fields = tuple(signature_fields)
        self.max_records_per_signature = max_records_per_signature
        self.max_total_records = max_total_records
        self._records: dict[str, list[ResolutionRecord]] = {}
        self._signature_order: list[str] = []   # LRU tracking by signature

    # ---- signature ----

    def signature(self, gap) -> str:
        """
        Stable signature over selected fields.

        Accepts:
          - a dict with keys matching signature_fields
          - an object whose attributes match signature_fields
        Missing fields contribute the literal "<missing>" so structurally
        distinct gaps don't accidentally collide.
        """
        parts = []
        for f in self.signature_fields:
            if isinstance(gap, dict):
                v = gap.get(f, "<missing>")
            else:
                v = getattr(gap, f, "<missing>")
            parts.append(f"{f}={v!r}")
        payload = "|".join(parts).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]

    # ---- write ----

    def record_resolution(self, gap, resolution: ResolutionRecord) -> str:
        """
        Store a resolution under the gap's signature.
        Returns the signature.
        """
        sig = self.signature(gap)
        resolution.signature = sig
        bucket = self._records.setdefault(sig, [])
        bucket.append(resolution)
        # Per-signature cap: drop the lowest-quality oldest
        if len(bucket) > self.max_records_per_signature:
            bucket.sort(key=lambda r: (r.outcome_quality, r.timestamp))
            bucket.pop(0)
        # LRU tracking on signature
        if sig in self._signature_order:
            self._signature_order.remove(sig)
        self._signature_order.append(sig)
        # Total cap: evict the LRU signature entirely
        while self.total_records() > self.max_total_records:
            evict_sig = self._signature_order.pop(0)
            self._records.pop(evict_sig, None)
        return sig

    # ---- read ----

    def suggest(self, gap, top_k: int = 3) -> list[ResolutionRecord]:
        """
        Return up to top_k past resolutions for matching signature,
        sorted by outcome_quality desc then timestamp desc (recency
        tiebreak).
        """
        sig = self.signature(gap)
        bucket = list(self._records.get(sig, []))
        bucket.sort(key=lambda r: (-r.outcome_quality, -r.timestamp))
        return bucket[:top_k]

    def has_pattern(self, gap) -> bool:
        return self.signature(gap) in self._records

    # ---- accessors ----

    def total_records(self) -> int:
        return sum(len(v) for v in self._records.values())

    def total_signatures(self) -> int:
        return len(self._records)

    def cache_size(self) -> dict:
        return {
            "signatures": self.total_signatures(),
            "records": self.total_records(),
            "max_records_per_signature": self.max_records_per_signature,
            "max_total_records": self.max_total_records,
        }

    # ---- persistence ----

    def to_dict(self) -> dict:
        return {
            "signature_fields": list(self.signature_fields),
            "max_records_per_signature": self.max_records_per_signature,
            "max_total_records": self.max_total_records,
            "signature_order": list(self._signature_order),
            "records": {
                sig: [asdict(r) for r in records]
                for sig, records in self._records.items()
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PatternLibrary":
        lib = cls(
            signature_fields=tuple(d["signature_fields"]),
            max_records_per_signature=d["max_records_per_signature"],
            max_total_records=d["max_total_records"],
        )
        lib._signature_order = list(d.get("signature_order", []))
        lib._records = {
            sig: [ResolutionRecord(**r) for r in records]
            for sig, records in d.get("records", {}).items()
        }
        return lib

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "PatternLibrary":
        with open(path) as f:
            return cls.from_dict(json.load(f))

    # ---- claim table ----

    def to_claim_table(self, source_id: str = "pattern_library") -> dict:
        claims = []
        for c in CLAIMS:
            claims.append({
                "claim_id": f"{source_id}.{c.claim_id}",
                "claim": c.statement,
                "measurement": c.measurement,
                "threshold": c.threshold,
                "falsification_condition": c.measurement + " | " + c.threshold,
                "substrate": c.substrate,
                "status": c.status,
            })
        return {
            "source_id": source_id,
            "cache_size": self.cache_size(),
            "claims": claims,
        }


# ---------------------------------------------------------------------------
# AI operator directive
# ---------------------------------------------------------------------------

AI_OPERATOR_NOTE = """
PATTERN LIBRARY directive for AI assistants:

When a DataGap is closed, log the resolution to the library:
  library.record_resolution(gap, ResolutionRecord(...))

When a new DataGap arrives, BEFORE constructing a fresh inquiry:
  past = library.suggest(gap, top_k=3)
  if past:
      # propose the top-ranked apparatus as a SUGGESTION
      # tag explicitly: "inferred-from-past-pattern"
      # require operator confirmation or re-measurement
      ...

Suggestions are NOT proven solutions. They are recurring patterns.
The audit gate "suggestion_used_as_truth" goes RED if the system
acts on a suggestion without re-verification.

If signature collisions exceed 5% (claim PLE-002), the signature
fields are too coarse -- expand DEFAULT_SIGNATURE_FIELDS to add
discriminators.

If top-1 suggestion success rate falls below 75% (claim PLE-003),
the suggestion-ranking policy is not predictive -- review the
outcome_quality recording, OR the gaps may be only superficially
similar (refine signature_fields).
"""


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def extension_bootstrap() -> str:
    lines = [
        "EXTENSION: pattern_library",
        "PARENT SCHEMA: cross_model_schema.py + data_gap_protocol.py",
        "CLOSES MISSING PIECE: Pattern Library (notes/multi_agent_protocol_skeleton.md)",
        "",
        "RULE: cache past gap resolutions by signature; suggest before",
        "      re-deriving apparatus on a new gap.",
        "",
        f"DEFAULT SIGNATURE FIELDS: {DEFAULT_SIGNATURE_FIELDS}",
        "",
        f"FALSIFIABLE CLAIMS: {len(CLAIMS)}",
    ]
    for c in CLAIMS:
        lines.append(f"  [{c.claim_id}] {c.statement[:65]}")
    lines += [
        "",
        f"AUDIT GATES: {len(AUDIT_GATES)}",
    ]
    for g in AUDIT_GATES:
        lines.append(f"  - {g.marker}")
    lines += [
        "",
        "AI OPERATOR NOTE:",
        AI_OPERATOR_NOTE,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(extension_bootstrap())

    print("\n" + "=" * 60)
    print("DEMO: record three resolutions, retrieve via signature")
    print("=" * 60)

    lib = PatternLibrary()

    # Simulate three gaps + resolutions
    gaps = [
        {
            "gap_id": "G-001",
            "gap_class": "measurement_apparatus_missing",
            "apparatus_required": "thermocouple",
            "data_required": "bog_temperature",
        },
        {
            "gap_id": "G-002",
            "gap_class": "measurement_apparatus_missing",
            "apparatus_required": "thermocouple",
            "data_required": "bog_temperature",
        },
        {
            "gap_id": "G-003",
            "gap_class": "data_systematically_excluded",
            "apparatus_required": "operator_interview",
            "data_required": "tacit_engineering_knowledge",
        },
    ]

    now = time.time()
    for g in gaps:
        res = ResolutionRecord(
            gap_id=g["gap_id"],
            signature="",  # filled in by record_resolution
            gap_class=g["gap_class"],
            resolution_apparatus=g["apparatus_required"],
            resolution_time_seconds=120.0,
            outcome_quality=0.9,
            timestamp=now,
            notes="demo",
        )
        sig = lib.record_resolution(g, res)
        print(f"  recorded {g['gap_id']}  signature={sig}")

    print(f"\n  cache size: {lib.cache_size()}")

    # New gap with same signature as G-001 + G-002
    new_gap = {
        "gap_id": "G-NEW",
        "gap_class": "measurement_apparatus_missing",
        "apparatus_required": "thermocouple",
        "data_required": "bog_temperature",
    }
    suggestions = lib.suggest(new_gap, top_k=3)
    print(f"\n  has_pattern({new_gap['gap_id']}) = {lib.has_pattern(new_gap)}")
    print(f"  suggestions for {new_gap['gap_id']}:")
    for s in suggestions:
        print(f"    apparatus={s.resolution_apparatus!r}  "
              f"quality={s.outcome_quality}  prior_gap={s.gap_id}")

    # Persistence round-trip
    print("\n" + "=" * 60)
    print("DEMO: persistence round-trip")
    print("=" * 60)
    path = "/tmp/_pattern_library_demo.json"
    lib.save(path)
    lib2 = PatternLibrary.load(path)
    print(f"  saved + loaded: cache_size={lib2.cache_size()}")
    sugg2 = lib2.suggest(new_gap, top_k=3)
    print(f"  reloaded suggestion count: {len(sugg2)}")

    # Falsifier visibility: signature collision
    print("\n" + "=" * 60)
    print("DEMO: signature determinism")
    print("=" * 60)
    sig_a = lib.signature(gaps[0])
    sig_b = lib.signature(gaps[1])
    sig_c = lib.signature(gaps[2])
    print(f"  sig(G-001) == sig(G-002) ? {sig_a == sig_b}  (expected True)")
    print(f"  sig(G-001) == sig(G-003) ? {sig_a == sig_c}  (expected False)")

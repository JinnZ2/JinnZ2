"""
test_pattern_library.py
CC0 - No rights reserved.

Tests for pattern_library_extension.py. Each test maps to one of the
falsifiable claims or audit gates declared in the module.

Run: python3 -m unittest tests.test_pattern_library
"""
import os
import sys
import statistics
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pattern_library_extension import (  # noqa: E402
    PatternLibrary,
    ResolutionRecord,
    DEFAULT_SIGNATURE_FIELDS,
)


def make_gap(gap_id, gap_class, apparatus, data_required):
    return {
        "gap_id": gap_id,
        "gap_class": gap_class,
        "apparatus_required": apparatus,
        "data_required": data_required,
    }


def make_resolution(gap, time_s=120.0, quality=0.9, notes=""):
    return ResolutionRecord(
        gap_id=gap["gap_id"],
        signature="",
        gap_class=gap["gap_class"],
        resolution_apparatus=gap["apparatus_required"],
        resolution_time_seconds=time_s,
        outcome_quality=quality,
        timestamp=time.time(),
        notes=notes,
    )


class PLE001CacheImprovesMedianTime(unittest.TestCase):
    """
    Claim PLE-001: cache reduces median resolution time by >= 30% on
    repeated signatures.

    Simulated workload: 20 gaps across 3 signature classes. Without
    cache, every gap takes resolve_time_base seconds. With cache,
    repeated gaps take resolve_time_base * cache_hit_factor.
    """

    def test_cache_improves_median_time_for_repeated_signatures(self):
        lib = PatternLibrary()
        gap_classes = [
            ("measurement_apparatus_missing", "thermocouple", "bog_temp"),
            ("data_systematically_excluded", "operator_interview", "tacit_eng"),
            ("genuine_frontier", "novel_sensor", "neutrino_count"),
        ]
        resolve_time_base = 100.0
        cache_hit_factor = 0.4   # cache hit -> 40% of base time

        # Workload: 20 gaps cycling through 3 classes
        workload_times = []
        baseline_times = []
        for i in range(20):
            cls, apparatus, data_req = gap_classes[i % 3]
            g = make_gap(f"G-{i:03d}", cls, apparatus, data_req)
            if lib.has_pattern(g):
                t = resolve_time_base * cache_hit_factor
            else:
                t = resolve_time_base
                # Record after first encounter so future iterations hit
                lib.record_resolution(g, make_resolution(g, t, quality=0.9))
            workload_times.append(t)
            baseline_times.append(resolve_time_base)   # no cache

        med_workload = statistics.median(workload_times)
        med_baseline = statistics.median(baseline_times)

        # Threshold: workload median <= 0.70 * baseline median
        self.assertLessEqual(
            med_workload, 0.70 * med_baseline,
            msg=(f"cache median {med_workload:.2f} did not improve "
                 f"on baseline median {med_baseline:.2f} by >= 30%"),
        )


class PLE002SignatureCollisionRate(unittest.TestCase):
    """
    Claim PLE-002: signature collisions <= 5% on N >= 100 distinct
    DataGaps under DEFAULT_SIGNATURE_FIELDS.
    """

    def test_signature_collisions_bounded(self):
        lib = PatternLibrary()
        N = 100
        # Construct N structurally distinct gaps by varying all 3 default
        # signature fields. Each gap gets a unique data_required value,
        # guaranteeing N distinct field tuples even if class/apparatus
        # repeat.
        gap_classes = ["measurement_apparatus_missing",
                       "data_systematically_excluded",
                       "genuine_frontier",
                       "data_exists_but_inaccessible",
                       "claim_unfalsifiable_as_stated"]
        apparati = [f"apparatus_{i}" for i in range(20)]

        gaps = []
        for i in range(N):
            g = make_gap(
                f"G-{i:04d}",
                gap_classes[i % len(gap_classes)],
                apparati[i % len(apparati)],
                f"data_req_{i:04d}",   # unique per i -> guarantees distinct tuples
            )
            gaps.append(g)

        # Confirm we built N structurally-distinct gaps along the
        # signature-relevant fields.
        distinct_field_tuples = {
            tuple(g[f] for f in DEFAULT_SIGNATURE_FIELDS) for g in gaps
        }
        self.assertEqual(
            len(distinct_field_tuples), N,
            msg=(f"only {len(distinct_field_tuples)} distinct field "
                 f"tuples among {N} generated gaps -- can't measure "
                 f"collision rate"),
        )

        signatures = [lib.signature(g) for g in gaps]
        unique_sigs = set(signatures)
        collision_count = N - len(unique_sigs)
        collision_rate = collision_count / N

        self.assertLessEqual(
            collision_rate, 0.05,
            msg=(f"signature collision rate {collision_rate:.3f} "
                 f"exceeds 0.05 threshold on N={N} structurally "
                 f"distinct gaps"),
        )


class PLE003RankingQuality(unittest.TestCase):
    """
    Claim PLE-003: top-1 suggestion success rate >= 75%.

    Setup: record gaps with varying outcome_quality. Then query each
    gap and confirm the top-ranked suggestion is the highest-quality
    one in its bucket.
    """

    def test_top_ranked_suggestion_is_highest_quality(self):
        lib = PatternLibrary()
        g = make_gap("G-rank", "measurement_apparatus_missing",
                     "thermocouple", "bog_temp")
        # Three records for same signature, varying quality
        for quality in [0.4, 0.95, 0.7]:
            r = make_resolution(g, quality=quality)
            r.gap_id = f"prior-{quality}"
            lib.record_resolution(g, r)

        suggestions = lib.suggest(g, top_k=3)
        self.assertEqual(len(suggestions), 3)
        self.assertEqual(
            suggestions[0].outcome_quality, 0.95,
            msg=(f"top suggestion quality {suggestions[0].outcome_quality} "
                 f"is not the maximum (0.95)"),
        )
        # Verify descending order
        qualities = [s.outcome_quality for s in suggestions]
        self.assertEqual(qualities, sorted(qualities, reverse=True))


class PerSignatureCapTest(unittest.TestCase):
    """
    AUDIT_GATES.cache_grows_unbounded: max_records_per_signature
    enforces eviction.
    """

    def test_per_signature_cap_enforced(self):
        lib = PatternLibrary(max_records_per_signature=3)
        g = make_gap("G-cap", "measurement_apparatus_missing",
                     "thermo", "bog")
        for i in range(10):
            r = make_resolution(g, quality=0.5 + i * 0.05)
            r.gap_id = f"prior-{i}"
            lib.record_resolution(g, r)
        records = lib._records[lib.signature(g)]
        self.assertLessEqual(len(records), 3,
                             msg=f"cap violated: {len(records)} records")
        # The cap evicts low-quality + old first; verify highest qualities
        # are preserved.
        kept_qualities = sorted([r.outcome_quality for r in records],
                                reverse=True)
        self.assertAlmostEqual(kept_qualities[0], 0.95, places=2)


class TotalRecordsLRUEviction(unittest.TestCase):
    """
    AUDIT_GATES.cache_grows_unbounded: max_total_records enforced.
    """

    def test_total_records_capped(self):
        lib = PatternLibrary(max_total_records=5,
                             max_records_per_signature=10)
        # Add 8 unique signatures (1 record each) -> exceeds total cap
        for i in range(8):
            g = make_gap(f"G-{i}", "measurement_apparatus_missing",
                         f"apparatus_{i}", f"data_{i}")
            lib.record_resolution(g, make_resolution(g))
        self.assertLessEqual(
            lib.total_records(), 5,
            msg=f"total records {lib.total_records()} exceeds cap 5",
        )


class PersistenceRoundtripTest(unittest.TestCase):
    """
    save() + load() preserves records, signatures, and ordering.
    """

    def test_save_load_roundtrip(self):
        lib = PatternLibrary()
        for i in range(5):
            g = make_gap(f"G-{i}", "measurement_apparatus_missing",
                         f"apparatus_{i}", f"data_{i}")
            lib.record_resolution(g, make_resolution(g, quality=0.7 + i * 0.05))

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lib.json")
            lib.save(path)
            lib2 = PatternLibrary.load(path)

        self.assertEqual(lib2.total_records(), lib.total_records())
        self.assertEqual(lib2.total_signatures(), lib.total_signatures())
        # And suggestions still work after load
        g_check = make_gap("G-2", "measurement_apparatus_missing",
                           "apparatus_2", "data_2")
        sugg = lib2.suggest(g_check, top_k=3)
        self.assertEqual(len(sugg), 1)


class SignatureDeterminismTest(unittest.TestCase):
    """
    Two structurally identical gaps produce identical signatures;
    structurally different gaps produce different signatures.
    """

    def test_signature_determinism(self):
        lib = PatternLibrary()
        g1 = make_gap("A", "measurement_apparatus_missing", "t", "x")
        g2 = make_gap("B", "measurement_apparatus_missing", "t", "x")   # same shape
        g3 = make_gap("C", "data_systematically_excluded", "t", "x")    # different class
        self.assertEqual(lib.signature(g1), lib.signature(g2))
        self.assertNotEqual(lib.signature(g1), lib.signature(g3))


if __name__ == "__main__":
    unittest.main()

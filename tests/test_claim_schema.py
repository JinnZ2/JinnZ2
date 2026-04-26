# tests/test_claim_schema.py
"""
Tests for CLAIM_SCHEMA.py — round-trip integrity, table building,
hard-limit guards, and the canonical mulch example from
DIFFERENTIAL_FRAME.md.
"""

import json
import os
import struct
import tempfile
import unittest
from pathlib import Path

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import CLAIM_SCHEMA as cs


# ── Fixtures ────────────────────────────────────────────────────


MULCH = {
    "id": "mulch_h2o",
    "rate": "dM/dt=I-E-U",
    "bounds": ["2ac_MN_sandyloam", "120d", "0-30cm"],
    "cond": ["d>=5", "lith_match", "P~mean"],
    "rel": ["mycorr", "albedo"],
    "fail": ["drought_out", "lith_off", "biota_low"],
    "meas": ["tens_15", "tens_30", "growth_vs_ctrl"],
    "cyc": 2,
}


# ── Line format ────────────────────────────────────────────────


class LineFormat(unittest.TestCase):

    def test_encode_then_parse_round_trip(self):
        line = cs.encode_line(MULCH)
        self.assertEqual(line.count("|"), 7)
        parsed = cs.parse_line(line)
        self.assertEqual(parsed, MULCH)

    def test_parse_line_rejects_wrong_field_count(self):
        with self.assertRaises(ValueError):
            cs.parse_line("only|three|fields")

    def test_empty_lists_round_trip_cleanly(self):
        sparse = {**MULCH, "rel": [], "fail": [], "meas": []}
        line = cs.encode_line(sparse)
        parsed = cs.parse_line(line)
        self.assertEqual(parsed["rel"], [])
        self.assertEqual(parsed["fail"], [])
        self.assertEqual(parsed["meas"], [])


# ── File I/O ───────────────────────────────────────────────────


class FileIO(unittest.TestCase):

    def test_write_then_read_claims_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.claims"
            cs.write_claims([MULCH], path)
            back = cs.read_claims(path)
            self.assertEqual(back, [MULCH])

    def test_read_skips_blank_and_comment_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.claims"
            path.write_text(
                "# header comment\n"
                "\n"
                + cs.encode_line(MULCH) + "\n"
                "# trailing comment\n"
            )
            self.assertEqual(cs.read_claims(path), [MULCH])


# ── Lookup table ───────────────────────────────────────────────


class Tables(unittest.TestCase):

    def test_build_table_dedups_and_preserves_first_seen_order(self):
        a = {**MULCH, "id": "a"}
        b = {**MULCH, "id": "b"}  # all fields identical to a
        table = cs.build_table([a, b])
        self.assertEqual(table["rates"], ["dM/dt=I-E-U"])
        self.assertEqual(len(table["cond"]), len(MULCH["cond"]))

    def test_table_buckets_stay_within_mask_limit_for_repo_claims(self):
        claims = cs.read_claims(REPO_ROOT / ".claims")
        table = cs.build_table(claims)
        for bucket in ("cond", "rel", "fail", "meas"):
            self.assertLessEqual(
                len(table[bucket]), cs.MAX_MASK_BITS,
                msg=f"table[{bucket!r}] = {len(table[bucket])} > "
                    f"{cs.MAX_MASK_BITS}",
            )

    def test_load_table_round_trips(self):
        claims = cs.read_claims(REPO_ROOT / ".claims")
        table = cs.build_table(claims)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "table.json"
            cs.write_table(table, path)
            loaded = cs.load_table(path)
            self.assertEqual(loaded, table)


# ── Binary codec ───────────────────────────────────────────────


class BinaryCodec(unittest.TestCase):

    def setUp(self):
        self.claims = cs.read_claims(REPO_ROOT / ".claims")
        self.table = cs.build_table(self.claims)

    def test_claim_bytes_constant(self):
        # 4 + 2 + 2 + 2 + 2 + 2 + 2 + 1 = 17
        self.assertEqual(cs.CLAIM_BYTES, 17)

    def test_id_hash_is_stable(self):
        # CRC32 is well-defined; this should not change across runs
        # or platforms.
        self.assertEqual(cs.id_hash("mulch_h2o"), cs.id_hash("mulch_h2o"))
        self.assertNotEqual(cs.id_hash("mulch_h2o"), cs.id_hash("mulch_h20"))

    def test_encode_then_decode_round_trip(self):
        id_lookup = cs.build_id_lookup(self.claims)
        for claim in self.claims:
            blob = cs.encode_claim(claim, self.table)
            self.assertEqual(len(blob), cs.CLAIM_BYTES)
            decoded = cs.decode_claim(blob, self.table, id_lookup=id_lookup)
            self.assertEqual(decoded["id"], claim["id"])
            self.assertEqual(decoded["rate"], claim["rate"])
            self.assertEqual(decoded["bounds"], claim["bounds"])
            self.assertEqual(sorted(decoded["cond"]), sorted(claim["cond"]))
            self.assertEqual(sorted(decoded["rel"]),  sorted(claim["rel"]))
            self.assertEqual(sorted(decoded["fail"]), sorted(claim["fail"]))
            self.assertEqual(sorted(decoded["meas"]), sorted(claim["meas"]))
            self.assertEqual(decoded["cyc"], claim["cyc"])

    def test_encode_rejects_unknown_rate(self):
        bad_claim = {**MULCH, "rate": "dQ/dt=NOT_IN_TABLE"}
        with self.assertRaises(ValueError):
            cs.encode_claim(bad_claim, self.table)

    def test_encode_rejects_value_beyond_mask_limit(self):
        # Build a tiny table where cond[16] = "overflow" — beyond the
        # 16-bit mask. Any claim using "overflow" should fail.
        big_table = {
            "rates": ["dx/dt=0"],
            "bounds": ["x,y,z"],
            "cond": [f"c{i}" for i in range(17)],  # 17 entries
            "rel": [], "fail": [], "meas": [],
        }
        claim = {
            "id": "x", "rate": "dx/dt=0", "bounds": ["x", "y", "z"],
            "cond": ["c16"], "rel": [], "fail": [], "meas": [], "cyc": 0,
        }
        with self.assertRaises(ValueError):
            cs.encode_claim(claim, big_table)

    def test_unmask_reverses_mask(self):
        # bits 0, 2, 5 set
        self.assertEqual(cs.unmask(0b100101), [0, 2, 5])
        self.assertEqual(cs.unmask(0), [])

    def test_write_binary_then_read_binary_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.bin"
            cs.write_binary(self.claims, self.table, path)
            self.assertEqual(
                path.stat().st_size, len(self.claims) * cs.CLAIM_BYTES
            )
            back = cs.read_binary(
                path, self.table,
                id_lookup=cs.build_id_lookup(self.claims),
            )
            self.assertEqual(len(back), len(self.claims))
            for orig, decoded in zip(self.claims, back):
                self.assertEqual(decoded["id"], orig["id"])

    def test_read_binary_rejects_truncated_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.bin"
            path.write_bytes(b"\x00" * (cs.CLAIM_BYTES + 3))  # not a multiple
            with self.assertRaises(ValueError):
                cs.read_binary(path, self.table)


# ── Repo invariants ─────────────────────────────────────────────


class RepoInvariants(unittest.TestCase):
    """The on-disk .claims and CLAIM_TABLE.json must agree."""

    def setUp(self):
        self.claims = cs.read_claims(REPO_ROOT / ".claims")
        self.table = cs.load_table(REPO_ROOT / "CLAIM_TABLE.json")

    def test_every_claim_encodes_against_committed_table(self):
        for claim in self.claims:
            blob = cs.encode_claim(claim, self.table)
            self.assertEqual(len(blob), cs.CLAIM_BYTES, claim["id"])

    def test_committed_binary_matches_claims(self):
        bin_path = REPO_ROOT / ".claims.bin"
        self.assertTrue(bin_path.exists(), "expected .claims.bin to be committed")
        decoded = cs.read_binary(
            bin_path, self.table,
            id_lookup=cs.build_id_lookup(self.claims),
        )
        self.assertEqual(len(decoded), len(self.claims))
        for orig, dec in zip(self.claims, decoded):
            self.assertEqual(orig["id"], dec["id"])
            self.assertEqual(orig["rate"], dec["rate"])

    def test_canonical_mulch_claim_present(self):
        ids = {c["id"] for c in self.claims}
        self.assertIn("mulch_h2o", ids)
        mulch = next(c for c in self.claims if c["id"] == "mulch_h2o")
        self.assertEqual(mulch["rate"], "dM/dt=I-E-U")
        self.assertEqual(mulch["cyc"], 2)  # seasonal


if __name__ == "__main__":
    unittest.main()

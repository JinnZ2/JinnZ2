# tests/test_operator_id_alias.py
"""
The default operator id is the handle. An old default id is accepted only by
its sha256 (LEGACY_OPERATOR_ID_SHA256); files saved under it are found by
hashing filename stems, read, and re-written under the handle.

The old id itself is not written in this repository, so the tests add the
sha256 of a stand-in id ("legacy-default-id") to the set and exercise the same
code paths with it. One test checks the shipped set holds exactly one sha256.
Each test runs in a fresh interpreter with a temporary HOME.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "operator_kit"
STAND_IN = "legacy-default-id"
STAND_IN_SHA = hashlib.sha256(STAND_IN.encode()).hexdigest()


def run(code, home):
    """Run code with HOME set before the kit is imported; the stand-in id is
    added to the accepted sha256 set first."""
    env = dict(os.environ, HOME=home)
    prog = (
        "import sys; sys.path.insert(0, %r)\n" % str(KIT)
        + "import operator_context_persistence as p\n"
        + "p.LEGACY_OPERATOR_ID_SHA256 = p.LEGACY_OPERATOR_ID_SHA256 | {%r}\n" % STAND_IN_SHA
        + textwrap.dedent(code)
    )
    out = subprocess.run([sys.executable, "-c", prog], env=env,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return out.stdout


class OperatorIdAlias(unittest.TestCase):

    def test_shipped_alias_is_one_sha256_and_no_literal(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("print(sorted(p.LEGACY_OPERATOR_ID_SHA256 - {%r}))" % STAND_IN_SHA, home)
        shipped = eval(out)
        self.assertEqual(len(shipped), 1)
        self.assertRegex(shipped[0], r"^[0-9a-f]{64}$")
        src = (KIT / "operator_context_persistence.py").read_text()
        self.assertNotIn("LEGACY_OPERATOR_IDS", src)

    def test_old_id_context_loads_and_writes_handle_file(self):
        with tempfile.TemporaryDirectory() as home:
            run("""
                ctx = p.build_default_context()
                ctx.operator_id = %r
                ctx.notes = "saved-under-old-id"
                p.save_context(ctx)
            """ % STAND_IN, home)
            store = Path(home) / ".operator_context"
            self.assertTrue((store / (STAND_IN + ".json")).exists())

            out = run("""
                ctx = p.load_context(p.DEFAULT_OPERATOR_ID)
                print(ctx.operator_id, ctx.notes)
            """, home)
            self.assertEqual(out.split(), ["JinnZ2", "saved-under-old-id"])
            handle_file = store / "JinnZ2.json"
            self.assertTrue(handle_file.exists())
            self.assertEqual(json.loads(handle_file.read_text())["operator_id"], "JinnZ2")
            self.assertTrue((store / (STAND_IN + ".json")).exists())   # old file left in place

    def test_old_id_accepted_at_session_init(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("""
                import bootstrap_resilience as b
                s = b.initialize_session(%r, "claude")
                print(s.operator_id, s.cache_path)
            """ % STAND_IN, home)
            op, cache = out.split()
            self.assertEqual(op, "JinnZ2")
            self.assertEqual(os.path.basename(cache), "JinnZ2_claude.txt")
            self.assertTrue((Path(home) / ".operator_context" / "JinnZ2.json").exists())

    def test_new_default_writes_handle_named_files(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("""
                import bootstrap_resilience as b
                s = b.initialize_session()
                print(s.operator_id, s.cache_path)
            """, home)
            op, cache = out.split()
            self.assertEqual(op, "JinnZ2")
            self.assertEqual(os.path.basename(cache), "JinnZ2_claude.txt")
            names = sorted(f.name for f in (Path(home) / ".operator_context").glob("*.json"))
            self.assertEqual(names, ["JinnZ2.json"])

    def test_old_id_cache_found_by_stem_hash(self):
        with tempfile.TemporaryDirectory() as home:
            cache_dir = Path(home) / ".operator_context" / "cache"
            cache_dir.mkdir(parents=True)
            (cache_dir / (STAND_IN + "_claude.txt")).write_text("old-cache-payload")
            (cache_dir / "someone_else_claude.txt").write_text("not-this-one")
            got = run("""
                import bootstrap_resilience as b
                print(b.quick_load())
            """, home).strip()
            self.assertEqual(got, "old-cache-payload")
            self.assertEqual((cache_dir / "JinnZ2_claude.txt").read_text(), "old-cache-payload")

    def test_other_ids_unchanged(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("""
                print(p.canonical_operator_id("someone_else"), p.load_context("someone_else"))
            """, home)
            self.assertEqual(out.split(), ["someone_else", "None"])


if __name__ == "__main__":
    unittest.main()

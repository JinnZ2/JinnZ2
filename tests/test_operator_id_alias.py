# tests/test_operator_id_alias.py
"""
The default operator id is the handle. A context or cache saved under the
old default id (LEGACY_OPERATOR_IDS) must still load, and loading it must
write the handle-named file. Each test runs with a temporary HOME so nothing
touches a real ~/.operator_context.
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "operator_kit"


def run(code, home):
    """Run code in a fresh interpreter with HOME set before the kit is imported."""
    env = dict(os.environ, HOME=home)
    prog = "import sys; sys.path.insert(0, %r)\n" % str(KIT) + textwrap.dedent(code)
    out = subprocess.run([sys.executable, "-c", prog], env=env,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return out.stdout


class OperatorIdAlias(unittest.TestCase):

    def test_old_name_context_loads_and_writes_handle_file(self):
        with tempfile.TemporaryDirectory() as home:
            # Save a context under the old default id, as an existing
            # operator machine would hold it.
            run("""
                import operator_context_persistence as p
                legacy = p.LEGACY_OPERATOR_IDS[0]
                ctx = getattr(p, [n for n in dir(p) if n.startswith("build_") and n.endswith("_default_context")][0])()
                ctx.operator_id = legacy
                ctx.notes = "saved-under-old-id"
                p.save_context(ctx)
            """, home)
            store = Path(home) / ".operator_context"
            legacy_files = [f.name for f in store.glob("*.json")]
            self.assertEqual(len(legacy_files), 1)
            self.assertNotEqual(legacy_files[0], "JinnZ2.json")

            out = run("""
                import operator_context_persistence as p
                ctx = p.load_context(p.DEFAULT_OPERATOR_ID)
                print(ctx.operator_id, ctx.notes)
            """, home)
            self.assertEqual(out.split(), ["JinnZ2", "saved-under-old-id"])
            handle_file = store / "JinnZ2.json"
            self.assertTrue(handle_file.exists())
            self.assertEqual(json.loads(handle_file.read_text())["operator_id"], "JinnZ2")
            self.assertTrue((store / legacy_files[0]).exists())   # old file left in place

    def test_old_literal_accepted_at_session_init(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("""
                import bootstrap_resilience as b, operator_context_persistence as p
                s = b.initialize_session(p.LEGACY_OPERATOR_IDS[0], "claude")
                print(s.operator_id, s.cache_path)
            """, home)
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

    def test_old_name_cache_falls_back_and_writes_handle_cache(self):
        with tempfile.TemporaryDirectory() as home:
            cache_dir = Path(home) / ".operator_context" / "cache"
            cache_dir.mkdir(parents=True)
            out = run("""
                import operator_context_persistence as p
                print(p.LEGACY_OPERATOR_IDS[0])
            """, home).strip()
            (cache_dir / (out + "_claude.txt")).write_text("old-cache-payload")
            got = run("""
                import bootstrap_resilience as b
                print(b.quick_load())
            """, home).strip()
            self.assertEqual(got, "old-cache-payload")
            self.assertEqual((cache_dir / "JinnZ2_claude.txt").read_text(), "old-cache-payload")

    def test_other_ids_unchanged(self):
        with tempfile.TemporaryDirectory() as home:
            out = run("""
                import operator_context_persistence as p
                print(p.canonical_operator_id("someone_else"), p.load_context("someone_else"))
            """, home)
            self.assertEqual(out.split(), ["someone_else", "None"])


if __name__ == "__main__":
    unittest.main()

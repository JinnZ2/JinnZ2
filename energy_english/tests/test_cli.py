# energy_english/tests/test_cli.py
"""Tests for the energy_english interactive shell."""

import io
import os
import unittest

from energy_english import cli


_TINY_SIM = os.path.join(
    os.path.dirname(__file__), "..", "orchestrator", "examples", "tiny_sim.py"
)


def _run(argv=None, input_text=""):
    stdin = io.StringIO(input_text)
    stdout = io.StringIO()
    code = cli.main(
        argv or [],
        stdin=stdin,
        stdout=stdout,
        interactive=False,
    )
    return code, stdout.getvalue()


class HelpAndStatus(unittest.TestCase):

    def test_help_lists_routes(self):
        code, out = _run(input_text="help\nquit\n")
        self.assertEqual(code, 0)
        self.assertIn("oral_archaeology", out)
        self.assertIn("cloud_simulation", out)
        self.assertIn("model", out)

    def test_status_lists_backends(self):
        code, out = _run(input_text="status\nquit\n")
        self.assertEqual(code, 0)
        self.assertIn("oral_archaeology", out)
        self.assertIn("cloud_simulation", out)
        self.assertIn("model", out)

    def test_quit_exits(self):
        code, out = _run(input_text="quit\n")
        self.assertEqual(code, 0)

    def test_eof_exits(self):
        code, out = _run(input_text="")  # immediate EOF
        self.assertEqual(code, 0)


class ArchaeologyRoute(unittest.TestCase):

    def test_extract_physics_routes_to_archaeology(self):
        line = "extract physics from inhale for 4, hold for 7, exhale for 8, pause for 4, repeat\n"
        code, out = _run(input_text=line + "quit\n")
        self.assertEqual(code, 0)
        self.assertIn("[route: oral_archaeology]", out)
        # the breathing 4-7-8 signature renders into the formatted report
        self.assertIn("breathing", out.lower())


class CloudSimulationRoute(unittest.TestCase):

    def test_run_tiny_sim_via_registry(self):
        argv = [f"--sim=tiny_sim={_TINY_SIM}"]
        code, out = _run(
            argv=argv,
            input_text="run tiny_sim with iterations=30, amplitude=0.5\nquit\n",
        )
        self.assertEqual(code, 0)
        self.assertIn("[route: cloud_simulation]", out)

    def test_run_with_explicit_path(self):
        code, out = _run(
            input_text=f"run {_TINY_SIM} with iterations=30\nquit\n",
        )
        self.assertEqual(code, 0)
        self.assertIn("[route: cloud_simulation]", out)


class ModelRouteWithoutDispatcher(unittest.TestCase):

    def test_unrouted_response_when_no_model_configured(self):
        code, out = _run(
            input_text="the beta front drives the chi front\nquit\n",
        )
        self.assertEqual(code, 0)
        self.assertIn("[route: unrouted]", out)
        self.assertIn("no model dispatcher", out)


class ArgvParsing(unittest.TestCase):

    def test_sim_must_have_equals(self):
        with self.assertRaises(SystemExit):
            cli._parse_sim_specs(["bad-spec"])

    def test_sim_name_and_path_must_be_nonempty(self):
        with self.assertRaises(SystemExit):
            cli._parse_sim_specs(["=path"])
        with self.assertRaises(SystemExit):
            cli._parse_sim_specs(["name="])

    def test_no_archaeology_disables_backend(self):
        argv = ["--no-archaeology"]
        # Build router via main path and confirm the resulting router
        # has no oral_archaeology backend wired.
        router = cli._build_router(enable_archaeology=False)
        self.assertIsNone(router.oral_archaeology)


if __name__ == "__main__":
    unittest.main()

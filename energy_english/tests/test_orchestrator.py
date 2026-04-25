# energy_english/tests/test_orchestrator.py
"""
Tests for the L3 orchestrator: runtime ABC, trajectory adapter,
LocalRuntime end-to-end, DockerRuntime command construction,
HTTPRuntime with mocked urlopen, AWS/modal stub gating, and the
CloudOrchestrator wrapper.
"""

import io
import json
import os
import unittest
from unittest import mock

from energy_english.coating_detector import Trajectory
from energy_english.orchestrator import (
    BackendUnavailable,
    CloudOrchestrator,
    RunRequest,
    RunResult,
    SimRuntime,
    TrajectoryFormatError,
    adapt,
    adapt_loose,
    request_to_config,
)
from energy_english.orchestrator.backends.docker import DockerRuntime
from energy_english.orchestrator.backends.http import HTTPRuntime
from energy_english.orchestrator.backends.local import LocalRuntime


_TINY_SIM = os.path.join(
    os.path.dirname(__file__), "..", "orchestrator", "examples", "tiny_sim.py"
)


# ── Trajectory adapter ───────────────────────────────────────────


class TrajectoryAdapter(unittest.TestCase):

    def test_adapt_full_payload(self):
        traj = adapt({
            "parameters": {"a": 1, "b": 2},
            "varied_parameters": ["a"],
            "traces": {"x": [0.0, 1.0, 2.0]},
            "declared_couplings": [["x", "drives", "y"]],
            "expected_finals": {"x": 2.0},
            "events": [{"iteration": 5}],
        })
        self.assertIsInstance(traj, Trajectory)
        self.assertEqual(traj.parameters, {"a": 1, "b": 2})
        self.assertEqual(traj.varied_parameters, {"a"})
        self.assertEqual(traj.traces["x"], [0.0, 1.0, 2.0])
        self.assertEqual(traj.declared_couplings, [("x", "drives", "y")])
        self.assertEqual(traj.expected_finals, {"x": 2.0})
        self.assertEqual(traj.events, [{"iteration": 5}])

    def test_adapt_strict_rejects_non_dict_payload(self):
        with self.assertRaises(TrajectoryFormatError):
            adapt("not a dict")  # type: ignore[arg-type]

    def test_adapt_strict_rejects_non_list_trace(self):
        with self.assertRaises(TrajectoryFormatError):
            adapt({"traces": {"x": "not a list"}})

    def test_adapt_strict_rejects_short_coupling(self):
        with self.assertRaises(TrajectoryFormatError):
            adapt({"declared_couplings": [["x", "drives"]]})

    def test_adapt_loose_drops_garbage_traces(self):
        traj = adapt_loose({
            "parameters": {"a": 1},
            "traces": {"x": [1.0, 2.0], "bad": "not a list"},
        })
        self.assertIn("x", traj.traces)
        self.assertNotIn("bad", traj.traces)

    def test_request_to_config_round_trip(self):
        req = RunRequest(
            entrypoint="sim",
            parameters={"a": 1.0},
            varied_parameters=["a"],
            expected_finals={"lock_A": 0.1},
            declared_couplings=[("x", "drives", "y")],
        )
        cfg = request_to_config(req)
        # JSON-roundtrip must succeed (no tuples, no sets)
        roundtripped = json.loads(json.dumps(cfg))
        self.assertEqual(roundtripped["declared_couplings"], [["x", "drives", "y"]])


# ── LocalRuntime end-to-end ──────────────────────────────────────


class LocalRuntimeEndToEnd(unittest.TestCase):

    def test_runs_tiny_sim_and_returns_trajectory(self):
        runtime = LocalRuntime()
        request = RunRequest(
            entrypoint=_TINY_SIM,
            parameters={"iterations": 50, "amplitude": 0.5},
            varied_parameters=["amplitude"],
            declared_couplings=[("lock_A", "couples", "lock_B")],
            expected_finals={},
        )
        result = runtime.run(request)

        self.assertTrue(result.success, msg=result.error)
        self.assertEqual(result.backend, "local")
        self.assertIsNotNone(result.trajectory)
        self.assertEqual(len(result.trajectory.traces["lock_A"]), 50)
        # tiny_sim records zero-crossing events; with 50 iterations there
        # should be at least one
        self.assertGreaterEqual(len(result.trajectory.events), 1)

    def test_returns_failure_when_entrypoint_missing(self):
        runtime = LocalRuntime()
        request = RunRequest(entrypoint="/nonexistent/sim/path.py")
        result = runtime.run(request)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)


# ── DockerRuntime command construction ───────────────────────────


class DockerRuntimeCommand(unittest.TestCase):

    def test_build_command_has_mounts_and_env(self):
        runtime = DockerRuntime()
        # bypass the docker-on-PATH check for command construction tests
        with mock.patch.object(runtime, "ensure_available", lambda: None):
            cmd = runtime._build_command(
                RunRequest(entrypoint="my-sim:1.0", env={"API_KEY": "x"}),
                "/tmp/cfg.json",
                "/tmp/out.json",
            )
        joined = " ".join(cmd)
        self.assertEqual(cmd[0], "docker")
        self.assertEqual(cmd[1], "run")
        self.assertIn("--rm", cmd)
        self.assertIn("-v", cmd)
        # config mount is read-only
        self.assertIn("/tmp/cfg.json:/ee/config.json:ro", joined)
        self.assertIn("/tmp/out.json:/ee/output.json", joined)
        self.assertIn("ENERGY_ENGLISH_CONFIG=/ee/config.json", joined)
        self.assertIn("ENERGY_ENGLISH_OUTPUT=/ee/output.json", joined)
        # passthrough env shows up
        self.assertIn("API_KEY=x", joined)
        # image is the last token
        self.assertEqual(cmd[-1], "my-sim:1.0")

    def test_raises_backend_unavailable_when_docker_missing(self):
        runtime = DockerRuntime(docker_bin="/definitely/not/a/real/docker/path")
        with self.assertRaises(BackendUnavailable) as ctx:
            runtime.ensure_available()
        self.assertIn("hint", dir(ctx.exception))


# ── HTTPRuntime with a mocked opener ─────────────────────────────


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body


class _FakeOpener:
    def __init__(self, response: _FakeResponse):
        self.response = response
        self.calls = []

    def open(self, req, timeout=None):
        self.calls.append({
            "url": req.full_url,
            "method": req.get_method(),
            "headers": dict(req.header_items()),
            "body": req.data,
            "timeout": timeout,
        })
        return self.response


class HTTPRuntimeBehaviour(unittest.TestCase):

    def test_posts_request_and_adapts_response(self):
        body = json.dumps({
            "parameters": {"a": 1},
            "varied_parameters": ["a"],
            "traces": {"x": [0.0, 1.0]},
            "declared_couplings": [],
            "expected_finals": {},
            "events": [],
        }).encode("utf-8")
        opener = _FakeOpener(_FakeResponse(body))
        runtime = HTTPRuntime(
            "https://sim.example.com/run", token="tok", opener=opener
        )
        result = runtime.run(RunRequest(
            entrypoint="my-sim",
            parameters={"a": 1},
        ))
        self.assertTrue(result.success, msg=result.error)
        self.assertEqual(opener.calls[0]["url"], "https://sim.example.com/run")
        self.assertEqual(opener.calls[0]["method"], "POST")
        # bearer token attached. urllib lower-cases header names.
        headers = {k.lower(): v for k, v in opener.calls[0]["headers"].items()}
        self.assertEqual(headers.get("authorization"), "Bearer tok")
        # body is the JSON request envelope
        sent = json.loads(opener.calls[0]["body"].decode("utf-8"))
        self.assertEqual(sent["entrypoint"], "my-sim")
        self.assertEqual(sent["config"]["parameters"], {"a": 1})

    def test_non_2xx_response_is_failure(self):
        opener = _FakeOpener(_FakeResponse(b"server error", status=503))
        runtime = HTTPRuntime("https://sim.example.com/run", opener=opener)
        result = runtime.run(RunRequest(entrypoint="x"))
        self.assertFalse(result.success)
        self.assertIn("503", result.error)

    def test_empty_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            HTTPRuntime("")


# ── AWS / modal stubs ────────────────────────────────────────────


class StubAvailability(unittest.TestCase):

    def test_aws_lambda_unavailable_when_boto3_missing(self):
        from energy_english.orchestrator.backends import aws_lambda as aws_mod
        if aws_mod._BOTO3_AVAILABLE:
            self.skipTest("boto3 IS installed in this environment")
        with self.assertRaises(BackendUnavailable):
            aws_mod.AWSLambdaRuntime(function_name="x")
        self.assertFalse(aws_mod.AWSLambdaRuntime.is_available())

    def test_modal_unavailable_when_modal_missing(self):
        from energy_english.orchestrator.backends import modal_runtime as modal_mod
        if modal_mod._MODAL_AVAILABLE:
            self.skipTest("modal IS installed in this environment")
        with self.assertRaises(BackendUnavailable):
            modal_mod.ModalRuntime(app_name="x")
        self.assertFalse(modal_mod.ModalRuntime.is_available())


# ── CloudOrchestrator wrapper ────────────────────────────────────


class _StubRuntime(SimRuntime):
    name = "stub"

    def __init__(self):
        self.last_request = None
        self.next_result = RunResult(success=True, backend="stub")

    def run(self, request):
        self.last_request = request
        return self.next_result


class OrchestratorWrapper(unittest.TestCase):

    def test_run_forwards_request_to_runtime(self):
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt)
        req = RunRequest(entrypoint="x", parameters={"a": 1})
        out = orch.run(req)
        self.assertIs(out, rt.next_result)
        self.assertIs(rt.last_request, req)

    def test_default_timeout_applies_when_request_has_none(self):
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt, default_timeout_seconds=42.0)
        out = orch.run(RunRequest(entrypoint="x"))
        self.assertEqual(rt.last_request.timeout_seconds, 42.0)

    def test_request_timeout_overrides_default(self):
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt, default_timeout_seconds=42.0)
        orch.run(RunRequest(entrypoint="x", timeout_seconds=5.0))
        self.assertEqual(rt.last_request.timeout_seconds, 5.0)

    def test_run_kwargs_builds_request_inline(self):
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt)
        orch.run_kwargs(entrypoint="x", parameters={"a": 1})
        self.assertEqual(rt.last_request.parameters, {"a": 1})

    def test_on_result_callback_fires(self):
        seen = []
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt, on_result=seen.append)
        out = orch.run(RunRequest(entrypoint="x"))
        self.assertEqual(seen, [out])

    def test_on_result_exceptions_swallowed(self):
        def raises(_):
            raise RuntimeError("callback boom")
        rt = _StubRuntime()
        orch = CloudOrchestrator(rt, on_result=raises)
        # should not raise
        orch.run(RunRequest(entrypoint="x"))


# ── End-to-end via CloudOrchestrator + LocalRuntime + tiny_sim ──


class EndToEnd(unittest.TestCase):

    def test_full_pipeline_local_subprocess(self):
        orch = CloudOrchestrator(LocalRuntime())
        result = orch.run_kwargs(
            entrypoint=_TINY_SIM,
            parameters={"iterations": 30, "amplitude": 1.0},
            varied_parameters=["amplitude"],
        )
        self.assertTrue(result.success, msg=result.error)
        self.assertIsNotNone(result.trajectory)
        # And the trajectory is consumable by the L4 coating detector:
        from energy_english.coating_detector import CoatingDetector
        report = CoatingDetector(unexplored_min_iters=10).detect(result.trajectory)
        # tiny_sim emits zero-crossing events, so unexplored_phase_space
        # MUST NOT fire
        self.assertFalse(report.has_category("unexplored_phase_space"))


if __name__ == "__main__":
    unittest.main()

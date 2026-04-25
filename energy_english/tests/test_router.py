# energy_english/tests/test_router.py
"""Tests for the L2 OrchestratorRouter."""

import unittest

from energy_english.coating_detector import Trajectory
from energy_english.dispatcher import GatedDispatcher
from energy_english.router import (
    OrchestratorRouter,
    ROUTE_CLOUD_SIMULATION,
    ROUTE_MODEL,
    ROUTE_ORAL_ARCHAEOLOGY,
    ROUTE_UNROUTED,
    _parse_sim_params,
    classify,
    routable_intents,
)


CLEAN_OUTPUT = (
    "Triples extracted:\n"
    "- (beta_front, drives, chi_front, strength=0.6, scope=sentence)\n"
    "Silent variables: frequency_gap left at default.\n"
    "What would falsify: widen the gap and watch for lock loss."
)


def static_model(text: str) -> str:
    return CLEAN_OUTPUT


class _Recorder:
    """Records every call so we can assert who got invoked."""

    def __init__(self, response: str = CLEAN_OUTPUT):
        self.calls = []
        self.response = response

    def __call__(self, text: str) -> str:
        self.calls.append(text)
        return self.response


# ── Classification ────────────────────────────────────────────────


class Classify(unittest.TestCase):

    def test_extract_physics_from_routes_to_archaeology(self):
        route, payload, label = classify(
            "extract physics from inhale for 4, hold for 7, "
            "exhale for 8, pause for 4, repeat"
        )
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertTrue(payload.startswith("inhale for 4"))
        self.assertEqual(label, "extract <X> from")

    def test_decode_breathing_routes_to_archaeology(self):
        route, payload, _ = classify(
            "decode this breathing protocol: inhale for 4, exhale for 8"
        )
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertTrue(payload.startswith("inhale"))

    def test_what_geometry_in_dance_routes_to_archaeology(self):
        route, payload, _ = classify(
            "what geometry is encoded in person A mirrors person B with 0.3s lag"
        )
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertIn("person A", payload)

    def test_archaeology_on_routes_to_archaeology(self):
        route, payload, _ = classify(
            "run archaeology on water rises, reaches the stone, divides"
        )
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertTrue(payload.startswith("water"))

    def test_analyze_story_routes_to_archaeology(self):
        route, payload, _ = classify(
            "analyze this story: water rises, reaches the stone, divides, reforms"
        )
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertTrue(payload.startswith("water"))

    def test_constraint_observation_routes_to_model(self):
        route, payload, label = classify(
            "the beta front drives the chi front"
        )
        self.assertEqual(route, ROUTE_MODEL)
        self.assertEqual(payload, "the beta front drives the chi front")
        self.assertIsNone(label)

    def test_empty_payload_falls_through_to_model(self):
        # Pattern matches but capture is empty → not a real archaeology request.
        route, payload, _ = classify("extract physics from")
        self.assertEqual(route, ROUTE_MODEL)

    def test_routable_intents_lists_known_routes(self):
        intents = routable_intents()
        self.assertIn(ROUTE_ORAL_ARCHAEOLOGY, intents)
        self.assertIn(ROUTE_CLOUD_SIMULATION, intents)
        self.assertIn(ROUTE_MODEL, intents)

    def test_run_sim_routes_to_cloud_simulation(self):
        route, payload, label = classify("run multi_front with iterations=100, amplitude=0.5")
        self.assertEqual(route, ROUTE_CLOUD_SIMULATION)
        self.assertTrue(payload.startswith("multi_front||"))
        self.assertIn("iterations=100", payload)
        self.assertIn("amplitude=0.5", payload)
        self.assertEqual(label, "run <sim> [with <params>]")

    def test_simulate_without_params_is_routable(self):
        route, payload, _ = classify("simulate tiny_sim")
        self.assertEqual(route, ROUTE_CLOUD_SIMULATION)
        self.assertEqual(payload, "tiny_sim||")

    def test_extract_physics_from_does_not_collide_with_run(self):
        # archaeology pattern matches "extract physics from run multi_front..."
        # and SHOULD WIN against the simulation pattern.
        route, _, _ = classify("extract physics from run_observation: water rises")
        self.assertEqual(route, ROUTE_ORAL_ARCHAEOLOGY)


class ParseSimParams(unittest.TestCase):

    def test_int_then_float_then_string_inference(self):
        out = _parse_sim_params("a=1, b=2.5, c=hello")
        self.assertEqual(out, {"a": 1, "b": 2.5, "c": "hello"})

    def test_empty_input_returns_empty_dict(self):
        self.assertEqual(_parse_sim_params(""), {})
        self.assertEqual(_parse_sim_params(None), {})

    def test_skips_malformed_entries(self):
        out = _parse_sim_params("a=1, garbage, b=2, =nokey")
        self.assertEqual(out, {"a": 1, "b": 2})


# ── Routing to oral_archaeology ───────────────────────────────────


class RouteToOralArchaeology(unittest.TestCase):

    def test_breathing_request_returns_archaeology_report(self):
        recorder = _Recorder()
        router = OrchestratorRouter(
            model_dispatcher=GatedDispatcher(recorder, retry_on_block=False),
        )
        result = router.dispatch(
            "extract physics from inhale for 4, hold for 7, "
            "exhale for 8, pause for 4, repeat"
        )
        self.assertEqual(result.route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertIsNotNone(result.archaeology_report)
        self.assertEqual(result.archaeology_report.oral_form_type, "breathing")
        # the model was NOT called for an archaeology route
        self.assertEqual(len(recorder.calls), 0)
        # response_text is the formatted report
        self.assertIn("Oral Archaeology Report", result.response_text)
        self.assertIn("breathing", result.response_text)

    def test_dance_request_classifies_and_extracts_couplings(self):
        router = OrchestratorRouter()
        result = router.dispatch(
            "decode this dance: person A mirrors person B with 0.3s lag, "
            "tightens on the third measure, resets on the drum"
        )
        self.assertEqual(result.route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertEqual(result.archaeology_report.oral_form_type, "dance")
        self.assertGreaterEqual(len(result.archaeology_report.couplings), 1)

    def test_story_request_with_trajectory_runs_trajectory_validation(self):
        router = OrchestratorRouter()
        traj = Trajectory(
            parameters={"a": 1.0},
            varied_parameters={"a"},
            traces={"x": [i * 0.01 for i in range(100)]},
            events=[{"iteration": 5}],
        )
        result = router.dispatch(
            "analyze this story: water rises, reaches the stone, "
            "divides, reforms downstream",
            trajectory=traj,
        )
        self.assertEqual(result.route, ROUTE_ORAL_ARCHAEOLOGY)
        self.assertIsNotNone(result.archaeology_report.trajectory_validation)


# ── Routing to the model dispatcher ───────────────────────────────


class RouteToModel(unittest.TestCase):

    def test_constraint_observation_invokes_model(self):
        recorder = _Recorder()
        router = OrchestratorRouter(
            model_dispatcher=GatedDispatcher(recorder, retry_on_block=False),
        )
        result = router.dispatch("the beta front drives the chi front")
        self.assertEqual(result.route, ROUTE_MODEL)
        self.assertEqual(len(recorder.calls), 1)
        self.assertEqual(recorder.calls[0], "the beta front drives the chi front")
        self.assertIsNotNone(result.roundtrip)
        self.assertFalse(result.blocked)

    def test_block_propagates_to_router_result(self):
        narrating = _Recorder("Let me walk you through what happens here.")
        router = OrchestratorRouter(
            model_dispatcher=GatedDispatcher(narrating, retry_on_block=False),
        )
        result = router.dispatch("front_A drives front_B")
        self.assertEqual(result.route, ROUTE_MODEL)
        self.assertTrue(result.blocked)
        self.assertEqual(result.roundtrip.output_report.verdict.value, "block")


# ── Routing to cloud_simulation ──────────────────────────────────


class _StubOrchestrator:
    """Stand-in for CloudOrchestrator so router tests stay stdlib-only."""

    def __init__(self, *, success=True, trajectory=None, error=None):
        self.success = success
        self.trajectory = trajectory
        self.error = error
        self.calls = []

    def run(self, request):
        from energy_english.orchestrator import RunResult
        self.calls.append(request)
        return RunResult(
            success=self.success,
            trajectory=self.trajectory,
            error=self.error,
            backend="stub",
        )


class RouteToCloudSimulation(unittest.TestCase):

    def _trajectory(self):
        # A simple, well-explored trajectory so the coating detector
        # produces a clean PASS report.
        return Trajectory(
            parameters={"iterations": 100, "amplitude": 0.5},
            varied_parameters={"iterations", "amplitude"},
            traces={
                "lock_A": [(-1) ** i * 0.4 for i in range(100)],
                "lock_B": [(-1) ** i * 0.3 for i in range(100)],
            },
            events=[{"iteration": 5, "type": "zero_crossing"}],
        )

    def test_run_sim_calls_orchestrator_with_parsed_params(self):
        orch = _StubOrchestrator(trajectory=self._trajectory())
        router = OrchestratorRouter(cloud_orchestrator=orch)
        result = router.dispatch(
            "run /tmp/multi_front.py with iterations=100, amplitude=0.5"
        )
        self.assertEqual(result.route, ROUTE_CLOUD_SIMULATION)
        self.assertEqual(len(orch.calls), 1)
        req = orch.calls[0]
        self.assertEqual(req.entrypoint, "/tmp/multi_front.py")
        self.assertEqual(req.parameters, {"iterations": 100, "amplitude": 0.5})

    def test_sim_registry_resolves_friendly_name_to_entrypoint(self):
        orch = _StubOrchestrator(trajectory=self._trajectory())
        router = OrchestratorRouter(
            cloud_orchestrator=orch,
            sim_registry={"multi_front": "/sims/multi_front.py"},
        )
        router.dispatch("run multi_front with iterations=50")
        self.assertEqual(orch.calls[0].entrypoint, "/sims/multi_front.py")

    def test_run_attaches_run_result_and_coating_report(self):
        orch = _StubOrchestrator(trajectory=self._trajectory())
        router = OrchestratorRouter(cloud_orchestrator=orch)
        result = router.dispatch("run /tmp/sim.py")
        self.assertIsNotNone(result.run_result)
        self.assertTrue(result.run_result.success)
        self.assertIsNotNone(result.coating_report)
        # response_text is the optics rendering (or "nothing fired")
        self.assertTrue(result.response_text)

    def test_failed_sim_returns_error_response(self):
        orch = _StubOrchestrator(success=False, error="boom")
        router = OrchestratorRouter(cloud_orchestrator=orch)
        result = router.dispatch("run /tmp/sim.py")
        self.assertEqual(result.route, ROUTE_CLOUD_SIMULATION)
        self.assertFalse(result.run_result.success)
        self.assertIsNone(result.coating_report)
        self.assertIn("sim failed", result.response_text)


# ── Unrouted fallbacks ────────────────────────────────────────────


class Unrouted(unittest.TestCase):

    def test_archaeology_intent_without_pipeline_returns_unrouted(self):
        # router with no oral_archaeology pipeline supplied AND we override
        # the auto-import attempt by passing oral_archaeology=None and
        # nuking the cached binding via class state for this test:
        router = OrchestratorRouter()
        router.oral_archaeology = None
        result = router.dispatch(
            "extract physics from inhale for 4, hold for 7"
        )
        self.assertEqual(result.route, ROUTE_UNROUTED)
        self.assertIn("oral_archaeology", result.response_text)

    def test_simulation_intent_without_orchestrator_returns_unrouted(self):
        router = OrchestratorRouter()  # no cloud_orchestrator
        result = router.dispatch("run /tmp/sim.py")
        self.assertEqual(result.route, ROUTE_UNROUTED)
        self.assertIn("cloud_orchestrator", result.response_text)

    def test_model_intent_without_dispatcher_returns_unrouted(self):
        router = OrchestratorRouter(model_dispatcher=None)
        result = router.dispatch("the beta front drives the chi front")
        self.assertEqual(result.route, ROUTE_UNROUTED)
        self.assertIn("no model dispatcher", result.response_text)


if __name__ == "__main__":
    unittest.main()

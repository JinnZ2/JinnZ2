# energy_english/tests/test_router.py
"""Tests for the L2 OrchestratorRouter."""

import unittest

from energy_english.coating_detector import Trajectory
from energy_english.dispatcher import GatedDispatcher
from energy_english.router import (
    OrchestratorRouter,
    ROUTE_MODEL,
    ROUTE_ORAL_ARCHAEOLOGY,
    ROUTE_UNROUTED,
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
        self.assertIn(ROUTE_MODEL, intents)


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

    def test_model_intent_without_dispatcher_returns_unrouted(self):
        router = OrchestratorRouter(model_dispatcher=None)
        result = router.dispatch("the beta front drives the chi front")
        self.assertEqual(result.route, ROUTE_UNROUTED)
        self.assertIn("no model dispatcher", result.response_text)


if __name__ == "__main__":
    unittest.main()

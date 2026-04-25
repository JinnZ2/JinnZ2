# energy_english/tests/test_dispatcher.py
"""Tests for the gated dispatcher (Layer 2 wrapper around any model)."""

import unittest

from energy_english.dispatcher import GatedDispatcher, RoundTrip, evaluate_outputs
from energy_english.gate import ConstraintGate, GateVerdict


# Reuses the canonical clean-output shape from the gate tests.
CLEAN_OUTPUT = (
    "Triples extracted:\n"
    "- (beta_front, drives, chi_front, strength=0.6, scope=sentence)\n"
    "- (thermal_field, damps, chi_front, strength=0.4, scope=sentence)\n"
    "Silent variables: frequency_gap left at default; coupling_range not varied.\n"
    "What would falsify: drive a wider frequency_gap and watch for loss of "
    "phase-lock; vary coupling_range across [10, 40] and check for a "
    "threshold crossing."
)

NARRATING_OUTPUT = (
    "Let me walk you through what's happening here. First the beta front "
    "drives the chi front. Then they sync."
)


def static_model(text: str) -> str:
    """A model that always returns the same clean output."""
    return CLEAN_OUTPUT


def narrating_model(text: str) -> str:
    """A model that always narrates (BLOCK)."""
    return NARRATING_OUTPUT


class _ScriptedModel:
    """A model whose responses are scripted; raises if called too many times."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def __call__(self, text: str) -> str:
        self.calls.append(text)
        if not self._responses:
            raise AssertionError("scripted model exhausted")
        return self._responses.pop(0)


class DispatcherCleanPath(unittest.TestCase):

    def test_clean_response_passes_with_no_retries(self):
        d = GatedDispatcher(static_model, retry_on_block=False)
        rt = d.roundtrip("front_A drives front_B")
        self.assertIs(rt.verdict, GateVerdict.PASS)
        self.assertFalse(rt.final_blocked)
        self.assertEqual(rt.retries, 0)
        self.assertEqual(rt.response, CLEAN_OUTPUT)

    def test_input_report_records_user_misalignment(self):
        d = GatedDispatcher(static_model, retry_on_block=False)
        rt = d.roundtrip("the chi front should obviously sync, right?")
        # input gate flags but never blocks
        self.assertIs(rt.input_report.verdict, GateVerdict.FLAG)
        self.assertTrue(rt.input_report.has_category("moralization"))
        self.assertTrue(rt.input_report.has_category("surface_certainty"))
        # output gate still passes a clean model response
        self.assertIs(rt.output_report.verdict, GateVerdict.PASS)


class DispatcherBlockPath(unittest.TestCase):

    def test_blocked_response_marked_blocked_no_retry(self):
        d = GatedDispatcher(narrating_model, retry_on_block=False)
        rt = d.roundtrip("front_A drives front_B")
        self.assertIs(rt.verdict, GateVerdict.BLOCK)
        self.assertTrue(rt.final_blocked)
        self.assertEqual(rt.retries, 0)

    def test_retry_recovers_when_second_response_is_clean(self):
        scripted = _ScriptedModel([NARRATING_OUTPUT, CLEAN_OUTPUT])
        d = GatedDispatcher(scripted, retry_on_block=True, max_retries=1)
        rt = d.roundtrip("front_A drives front_B")
        self.assertIs(rt.verdict, GateVerdict.PASS)
        self.assertFalse(rt.final_blocked)
        self.assertEqual(rt.retries, 1)
        self.assertEqual(len(scripted.calls), 2)
        # second call must include the teaching scaffold
        retry_prompt = scripted.calls[1]
        self.assertIn("blocked by the constraint gate", retry_prompt)
        self.assertIn("[narration]", retry_prompt)
        self.assertIn("scaffold:", retry_prompt)
        self.assertIn("example:", retry_prompt)

    def test_retry_gives_up_after_max_retries(self):
        scripted = _ScriptedModel([NARRATING_OUTPUT, NARRATING_OUTPUT])
        d = GatedDispatcher(scripted, retry_on_block=True, max_retries=1)
        rt = d.roundtrip("front_A drives front_B")
        self.assertIs(rt.verdict, GateVerdict.BLOCK)
        self.assertTrue(rt.final_blocked)
        self.assertEqual(rt.retries, 1)
        self.assertEqual(len(scripted.calls), 2)

    def test_retry_disabled_means_one_call_only(self):
        scripted = _ScriptedModel([NARRATING_OUTPUT])
        d = GatedDispatcher(scripted, retry_on_block=False)
        rt = d.roundtrip("front_A drives front_B")
        self.assertIs(rt.verdict, GateVerdict.BLOCK)
        self.assertEqual(len(scripted.calls), 1)


class CorrectivePrompt(unittest.TestCase):

    def test_corrective_prompt_includes_user_text_and_scaffold(self):
        scripted = _ScriptedModel([NARRATING_OUTPUT, CLEAN_OUTPUT])
        d = GatedDispatcher(scripted, retry_on_block=True, max_retries=1)
        d.roundtrip("front_A drives front_B")
        retry_prompt = scripted.calls[1]
        # original user text preserved
        self.assertTrue(retry_prompt.startswith("front_A drives front_B"))
        # the teaching block from the gate is appended verbatim
        self.assertIn("Stay in energy_english mode.", retry_prompt)
        self.assertIn("principle:", retry_prompt)
        self.assertIn("scaffold:", retry_prompt)


class BatchHelper(unittest.TestCase):

    def test_evaluate_outputs_batch(self):
        pairs = [
            ("front_A drives front_B", CLEAN_OUTPUT),
            ("front_A drives front_B", NARRATING_OUTPUT),
            ("front_A drives front_B", "The answer is they obviously sync."),
        ]
        reports = evaluate_outputs(pairs)
        self.assertEqual(len(reports), 3)
        self.assertIs(reports[0].verdict, GateVerdict.PASS)
        self.assertIs(reports[1].verdict, GateVerdict.BLOCK)
        self.assertIs(reports[2].verdict, GateVerdict.BLOCK)


if __name__ == "__main__":
    unittest.main()

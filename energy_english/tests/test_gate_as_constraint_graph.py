# energy_english/tests/test_gate_as_constraint_graph.py
"""
Tests for the graph-reasoning twin of the L1 gate.

Two test layers:

1. Mirror tests — same fixtures the regex primary's tests use, asserting
   the twin produces the same verdict on the obvious cases. Same shape
   across paradigms is the contract every twin honours
   (see ALTERNATIVE_COMPUTE_BRIDGES.md).

2. Graph-specific tests — assertions about what the twin notices that
   the primary does not, and what it correctly does NOT block when
   surrounding context tempers a violation.
"""

import unittest

from energy_english.findings import Verdict
from energy_english.gate import ConstraintGate
from energy_english.gate_as_constraint_graph import (
    ConstraintGraphGate,
    DiscourseGraph,
    EdgeKind,
    NodeKind,
    build_graph,
)


CLEAN_OUTPUT = (
    "Triples extracted:\n"
    "- (beta_front, drives, chi_front, strength=0.6, scope=sentence)\n"
    "- (thermal_field, damps, chi_front, strength=0.4, scope=sentence)\n"
    "Silent variables: frequency_gap left at default; coupling_range not varied.\n"
    "What would falsify: drive a wider frequency_gap and watch for loss of "
    "phase-lock; vary coupling_range across [10, 40] and check for a "
    "threshold crossing."
)


# ── Graph construction ──────────────────────────────────────────


class GraphConstruction(unittest.TestCase):

    def test_sentence_nodes_for_each_sentence(self):
        g = build_graph("first sentence. second sentence. third sentence.")
        self.assertEqual(len(g.nodes_of_kind(NodeKind.SENTENCE)), 3)

    def test_sequential_edges_link_sentences(self):
        g = build_graph("a. b. c.")
        seq_edges = [e for e in g.edges if e.kind == EdgeKind.SEQUENTIAL]
        self.assertEqual(len(seq_edges), 2)

    def test_narration_opener_governed_by_sentence(self):
        g = build_graph("Let me walk you through it.")
        openers = g.nodes_of_kind(NodeKind.NARRATION_OPENER)
        self.assertEqual(len(openers), 1)
        sentence = g.governing_sentence(openers[0])
        self.assertIsNotNone(sentence)
        self.assertEqual(sentence.kind, NodeKind.SENTENCE)

    def test_intent_path_edge_built(self):
        g = build_graph("I think you're trying to lock the front.")
        intent_paths = [e for e in g.edges if e.kind == EdgeKind.INTENT_PATH]
        self.assertGreaterEqual(len(intent_paths), 1)

    def test_content_tokens_emitted(self):
        g = build_graph("front_A drives front_B")
        tokens = g.content_token_set()
        self.assertIn("front_a", tokens)
        self.assertIn("drives", tokens)
        self.assertIn("front_b", tokens)


# ── Mirror tests against gate.py ─────────────────────────────────


class MirrorBlockingCases(unittest.TestCase):
    """The twin must agree with the regex primary on obvious blocks."""

    def assertBothVerdict(self, text, expected_verdict, original_input=None):
        primary = ConstraintGate().evaluate_output(
            text, original_input=original_input
        )
        twin = ConstraintGraphGate().evaluate_output(
            text, original_input=original_input
        )
        self.assertIs(primary.verdict, expected_verdict, msg=primary.findings)
        self.assertIs(twin.verdict, expected_verdict, msg=twin.findings)

    def test_narration_blocks_in_both(self):
        self.assertBothVerdict(
            "Let me walk you through what's happening here. First the beta "
            "front drives the chi front. Then they sync.",
            Verdict.BLOCK,
        )

    def test_intention_blocks_in_both(self):
        self.assertBothVerdict(
            "What you're really asking is whether the front is locked.",
            Verdict.BLOCK,
        )

    def test_summary_closer_blocks_in_both(self):
        self.assertBothVerdict(
            "In conclusion, the fronts have synchronized as expected.",
            Verdict.BLOCK,
        )

    def test_clean_structural_output_passes_in_both(self):
        # Twin's coating "warn-when-no-silent" check fires on any long
        # response without a silent-variable marker; the canonical
        # clean output names silent variables, so neither layer fires.
        self.assertBothVerdict(CLEAN_OUTPUT, Verdict.PASS)


class MirrorFlaggingCases(unittest.TestCase):

    def test_surface_certainty_only_flags_in_both(self):
        text = (
            "front_A obviously couples to front_B (strength 0.6).\n"
            "Silent: thermal_field is at default.\n"
            "- (front_A, couples, front_B, 0.6)"
        )
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)
        self.assertIs(primary.verdict, Verdict.FLAG)
        self.assertIs(twin.verdict, Verdict.FLAG)
        self.assertTrue(primary.has_category("surface_certainty"))
        self.assertTrue(twin.has_category("surface_certainty"))

    def test_invented_relation_flags_in_both(self):
        text = "front_A causes front_B to lock. Silent: thermal at default."
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)
        self.assertIs(primary.verdict, Verdict.FLAG)
        self.assertIs(twin.verdict, Verdict.FLAG)
        self.assertTrue(primary.has_category("invented_relation"))
        self.assertTrue(twin.has_category("invented_relation"))


# ── Graph-specific reasoning ────────────────────────────────────


class StoryArcMotif(unittest.TestCase):
    """
    The twin reports a story-arc motif when an opener and a closer are
    sequential-reachable. The primary blocks on the opener pattern
    alone; the twin blocks too but with a richer rationale.
    """

    def test_story_arc_rationale_when_opener_and_closer_co_occur(self):
        text = (
            "Let me walk you through it. The system locks. "
            "In conclusion, the system has locked."
        )
        twin = ConstraintGraphGate().evaluate_output(text)
        narration = next(
            f for f in twin.findings if f.category == "narration"
        )
        self.assertIn("story-arc motif", narration.rationale)


class ContextAwareClosure(unittest.TestCase):
    """
    Headline disagreement with the primary: closure tempered by the
    presence of a falsifier-marker node in the same graph drops from
    BLOCK to WARN. This is the kind of context-sensitive reasoning
    the design doc promised.
    """

    def test_closer_with_falsifier_in_graph_warns_not_blocks(self):
        text = (
            "The answer is they may be locked. "
            "But what would falsify this: sweep the coupling_range across [10, 40]."
        )
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)

        self.assertIs(primary.verdict, Verdict.BLOCK)
        self.assertIs(twin.verdict, Verdict.FLAG)

        twin_closure = next(
            f for f in twin.findings if f.category == "closure"
        )
        self.assertEqual(twin_closure.severity, "warn")
        self.assertIn("tempered", twin_closure.rationale)

    def test_closer_with_silent_variable_marker_warns(self):
        text = (
            "The answer is locked. "
            "Silent: thermal_field is left at default."
        )
        twin = ConstraintGraphGate().evaluate_output(text)
        closure = next(f for f in twin.findings if f.category == "closure")
        self.assertEqual(closure.severity, "warn")

    def test_closer_alone_still_blocks(self):
        text = "The answer is locked."
        twin = ConstraintGraphGate().evaluate_output(text)
        self.assertIs(twin.verdict, Verdict.BLOCK)


class CoatingAsSubgraphOverlap(unittest.TestCase):

    def test_high_overlap_no_silent_blocks(self):
        original = (
            "The beta front drives the chi front and the thermal field "
            "damps the chi front; the frequency gap stays small."
        )
        echo = (
            "Yes — the beta front drives the chi front and the thermal "
            "field damps the chi front; the frequency gap stays small."
        )
        twin = ConstraintGraphGate(
            coating_overlap_threshold=0.4,
        ).evaluate_output(echo, original_input=original)
        self.assertIs(twin.verdict, Verdict.BLOCK)
        self.assertTrue(twin.has_category("coating"))

    def test_overlap_with_silent_marker_does_not_block(self):
        original = "front_A drives front_B"
        echo_with_silent = (
            "front_A drives front_B (strength 0.6). "
            "Silent: thermal_field at default."
        )
        twin = ConstraintGraphGate().evaluate_output(
            echo_with_silent, original_input=original,
        )
        self.assertIsNot(twin.verdict, Verdict.BLOCK)


class IntentTraversal(unittest.TestCase):
    """
    The twin's intention finding cites the graph traversal explicitly
    so a graph-reasoner can audit the path.
    """

    def test_intention_finding_cites_traversal_motif(self):
        twin = ConstraintGraphGate().evaluate_output(
            "What you're really asking is whether the front is locked."
        )
        intent = next(f for f in twin.findings if f.category == "intention")
        self.assertIn("intent-traversal motif", intent.rationale)


class InputModePermissive(unittest.TestCase):

    def test_input_never_blocks(self):
        twin = ConstraintGraphGate()
        # input that would BLOCK as output is annotated only on input
        report = twin.evaluate_input(
            "should the chi front obviously sync, right?"
        )
        self.assertIsNot(report.verdict, Verdict.BLOCK)
        # info severity (not warn / not block)
        for f in report.findings:
            self.assertEqual(f.severity, "info")


# ── Ensemble compatibility ──────────────────────────────────────


class EnsembleViaOptics(unittest.TestCase):
    """
    The whole point of twins: run both primary and twin and feed both
    reports through the optics translator. Disagreement is its own
    signal.
    """

    def test_optics_absorbs_both_reports_and_dedups(self):
        from energy_english.optics import OpticsTranslator

        text = (
            "Let me walk you through it. The answer is locked. "
            "What would falsify: sweep the gap."
        )
        primary = ConstraintGate().evaluate_output(text)
        twin = ConstraintGraphGate().evaluate_output(text)

        opt = OpticsTranslator().translate(primary, twin)
        # both reports surfaced findings; optics absorbed and dedup'd
        self.assertTrue(opt.invitations or opt.falsifiers)


if __name__ == "__main__":
    unittest.main()

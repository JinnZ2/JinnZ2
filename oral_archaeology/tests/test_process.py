# oral_archaeology/tests/test_process.py
"""
Tests for the process layer: vocabulary loading + composition + fall-through,
ProcessExtractor per-form behaviour, and the optics translator's preference
for processual rendering when the process layer is populated.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from energy_english.optics import OpticsTranslator
from oral_archaeology import (
    OralArchaeologyPipeline,
    ProcessExtractor,
    ProcessVocabulary,
    format_report,
)
from oral_archaeology.extractor import ConstraintGeometry, run_all
from oral_archaeology.parser import parser_for


def _geom_for(form_type, text):
    return run_all(parser_for(form_type).parse(text))


# ── Vocabulary ──────────────────────────────────────────────────


class VocabularyComposition(unittest.TestCase):

    def test_default_for_form_loads_default_plus_overlay(self):
        v = ProcessVocabulary.for_form("breathing")
        # default_en provides "water"; breathing_en provides "co2_buildup"
        self.assertEqual(v.process_for("water"), "flowing")
        self.assertEqual(v.process_for("co2_buildup"), "co2_accumulating")
        # composite id reflects both files
        self.assertIn("default_en", v.composite_id)
        self.assertIn("breathing_en", v.composite_id)

    def test_for_form_unknown_form_loads_default_only(self):
        v = ProcessVocabulary.for_form("ritual")  # no ritual_en.json yet
        self.assertEqual(v.process_for("water"), "flowing")
        self.assertEqual(v.composite_id, "default_en")

    def test_overlay_overrides_default(self):
        v = ProcessVocabulary.empty()
        v.merge({"id": "base", "processes": {"water": "drifting"}})
        v.merge({"id": "overlay", "processes": {"water": "river-flowing"}})
        self.assertEqual(v.process_for("water"), "river-flowing")
        self.assertEqual(v.composite_id, "base+overlay")


class VocabularyLookup(unittest.TestCase):

    def test_lookup_is_case_insensitive(self):
        v = ProcessVocabulary.for_form("story")
        self.assertEqual(v.process_for("WATER"), "flowing")
        self.assertEqual(v.process_for("Water"), "flowing")
        self.assertEqual(v.modulation_for("RISES"), "intensifying")

    def test_unknown_input_falls_through(self):
        v = ProcessVocabulary.for_form("story")
        self.assertEqual(v.process_for("zorklesnort"), "zorklesnort")
        self.assertEqual(v.modulation_for("zorklesnort"), "zorklesnort")

    def test_empty_input_returns_empty_string(self):
        v = ProcessVocabulary.for_form("story")
        self.assertEqual(v.process_for(""), "")
        self.assertEqual(v.process_for(None), "")
        self.assertEqual(v.modulation_for(""), "")
        self.assertEqual(v.modulation_for(None), "")


class VocabularyFromCustomDir(unittest.TestCase):

    def test_for_form_loads_from_custom_vocab_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            (tmp_dir / "default_en.json").write_text(
                json.dumps({
                    "id": "tinyland_default",
                    "processes": {"water": "moonflow"},
                    "modulations": {},
                })
            )
            (tmp_dir / "story_en.json").write_text(
                json.dumps({
                    "id": "tinyland_story",
                    "processes": {"stone": "elder-quiet"},
                    "modulations": {},
                })
            )
            v = ProcessVocabulary.for_form("story", vocab_dir=tmp_dir)
            self.assertEqual(v.process_for("water"), "moonflow")
            self.assertEqual(v.process_for("stone"), "elder-quiet")
            self.assertIn("tinyland_default", v.composite_id)
            self.assertIn("tinyland_story", v.composite_id)


# ── ProcessExtractor — per-form behaviour ───────────────────────


class StoryProcessing(unittest.TestCase):

    def test_chain_uses_primary_subject_throughout(self):
        # Per the design example: every modulation should describe the
        # primary process (flowing-water). The parser drifts onto
        # 'stone' as a subject mid-sequence; the ProcessExtractor
        # anchors back to the first subject.
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        self.assertTrue(geom.processes)
        for entry in geom.processes:
            self.assertEqual(entry["process"], "flowing")

    def test_modulations_match_design_example(self):
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        modulations = [e["modulation"] for e in geom.processes]
        self.assertEqual(
            modulations,
            ["intensifying", "encountering", "bifurcating", "phase-locking"],
        )

    def test_constraint_strips_article(self):
        geom = _geom_for(
            "story",
            "water rises, reaches the stone",
        )
        threshold_entry = next(
            e for e in geom.processes if e["kind"] == "threshold"
        )
        # 'the stone' → 'stone' → 'enduring'
        self.assertEqual(threshold_entry["constraint"], "enduring")

    def test_process_couplings_strip_articles(self):
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        process_b_values = {c["process_b"] for c in geom.process_couplings}
        # No 'the stone' should remain unstripped.
        self.assertNotIn("the stone", process_b_values)
        # 'the stone' should resolve through the article-stripper to 'enduring'.
        self.assertIn("enduring", process_b_values)


class BreathingProcessing(unittest.TestCase):

    def test_each_phase_emitted_as_bare_process(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat",
        )
        names = [e["process"] for e in geom.processes]
        self.assertEqual(names, ["inhaling", "holding", "exhaling", "pausing"])
        # Modulation None signals the renderer to use bare process names
        for e in geom.processes:
            self.assertIsNone(e["modulation"])

    def test_implicit_coupling_processualised(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat",
        )
        co2_entry = next(
            c for c in geom.process_couplings
            if c["process_a"] == "co2_accumulating"
        )
        self.assertEqual(co2_entry["process_b"], "vagal_modulating")
        self.assertEqual(co2_entry["modulation"], "intensifying")
        self.assertTrue(co2_entry["inferred"])


class DanceProcessing(unittest.TestCase):

    def test_subjects_emit_bare_process_entries(self):
        geom = _geom_for(
            "dance",
            "person A mirrors person B with 0.3s lag",
        )
        subject_entries = [e for e in geom.processes if e["kind"] == "subject"]
        self.assertGreaterEqual(len(subject_entries), 2)
        for e in subject_entries:
            self.assertIsNone(e["modulation"])

    def test_couplings_use_modulation_vocabulary(self):
        geom = _geom_for(
            "dance",
            "person A mirrors person B with 0.3s lag",
        )
        coupling = next(
            c for c in geom.process_couplings
            if c.get("modulation") == "mirroring"
        )
        self.assertIn("person A", coupling["process_a"])
        self.assertIn("person B", coupling["process_b"])


# ── Optics — process-first rendering ────────────────────────────


class OpticsProcessFirst(unittest.TestCase):

    def test_story_optics_renders_design_example_chain(self):
        report = OralArchaeologyPipeline().parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        optics = OpticsTranslator().translate(report)
        # the OBSERVED bucket should contain the processual chain
        joined = "\n".join(optics.observed)
        self.assertIn("flowing intensifying", joined)
        self.assertIn("encountering(enduring)", joined)
        self.assertIn("bifurcating", joined)
        self.assertIn("phase-locking(downstreaming)", joined)

    def test_breathing_optics_renders_phase_chain(self):
        report = OralArchaeologyPipeline().parse(
            "inhale for 4, hold for 7, exhale for 8, pause for 4, repeat"
        )
        optics = OpticsTranslator().translate(report)
        joined = "\n".join(optics.observed)
        self.assertIn("inhaling → holding → exhaling → pausing", joined)
        # Implicit coupling rendered alongside the chain.
        self.assertTrue(any(
            "co2_accumulating" in line and "vagal_modulating" in line
            for line in optics.observed
        ))

    def test_optics_falls_back_to_noun_form_when_processes_empty(self):
        # Construct a synthetic ArchaeologyReport whose geometry has
        # only the noun-first couplings (process layer not run).
        from oral_archaeology.output import ArchaeologyReport

        geom = ConstraintGeometry(form_type="custom")
        geom.couplings.append({
            "source": "alpha",
            "relationship": "drives",
            "target": "beta",
            "strength": 0.5,
        })
        # processes / process_couplings stay empty
        report = ArchaeologyReport(
            oral_form_type="custom",
            raw_text="custom",
            constraint_geometry=geom,
        )
        optics = OpticsTranslator().translate(report)
        joined = "\n".join(optics.observed)
        # Falls back to "(alpha, drives, beta)" rendering
        self.assertIn("alpha", joined)
        self.assertIn("drives", joined)
        self.assertIn("beta", joined)
        # And does NOT spuriously emit a process-chain header
        self.assertNotIn("intensifying", joined)


# ── Markdown report ─────────────────────────────────────────────


class MarkdownReport(unittest.TestCase):

    def test_processual_reading_section_present(self):
        report = OralArchaeologyPipeline().parse(
            "water rises, reaches the stone, divides, reforms downstream"
        )
        md = format_report(report, mode="verbose")
        self.assertIn("## Processual reading", md)
        self.assertIn("Vocabulary used:", md)
        self.assertIn("default_en+story_en", md)
        self.assertIn("Process chain:", md)
        self.assertIn("flowing intensifying", md)
        self.assertIn("Process couplings:", md)


# ── Backward compatibility ─────────────────────────────────────


class BackwardCompatibility(unittest.TestCase):

    def test_existing_couplings_field_unchanged(self):
        # Sanity: the original couplings list is still produced.
        geom = _geom_for(
            "story",
            "water rises, reaches the stone, divides, reforms downstream",
        )
        self.assertTrue(geom.couplings)
        # Original (noun-first) shape preserved
        first = geom.couplings[0]
        self.assertIn("source", first)
        self.assertIn("target", first)
        self.assertIn("relationship", first)

    def test_vocabulary_id_recorded_on_geometry(self):
        geom = _geom_for(
            "breathing",
            "inhale for 4, hold for 7, exhale for 8, pause for 4",
        )
        self.assertEqual(geom.vocabulary_id, "default_en+breathing_en")


if __name__ == "__main__":
    unittest.main()

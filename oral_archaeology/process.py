# oral_archaeology/process.py
"""
Process layer — the axiom expressed at the data-structure level.

Every noun is a verb running slowly enough to look like a thing
(``ENERGY_ENGLISH_AXIOM.md``). Standard `(subject, action, target)`
triples re-impose noun-first thinking. Process triples
``(process, modulation, constraint)`` carry the same information in
verb-first / process-first form: water is *flowing*, the stone is
*enduring*, "rises" is *intensifying*, "reaches the stone" is
*encounters(enduring_stone)*.

Two concrete pieces here:

- ``ProcessVocabulary``  — loads JSON vocabulary files (per-language
                           and per-community), composes ``default_en``
                           with a form-specific overlay, and provides
                           fall-through lookup. Communities fork by
                           editing JSON, not Python.
- ``ProcessExtractor``   — additive extractor; runs after the existing
                           three. Reads ``parsed`` and ``geom``,
                           writes new processual entries to
                           ``geom.processes`` and ``geom.process_couplings``
                           and records ``geom.vocabulary_id``.

The original entries on ``geom.couplings`` etc. are NOT replaced —
backward compatibility holds. Downstream code (optics translator,
markdown report) prefers the processual form when present and falls
back to the noun form when it isn't.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from oral_archaeology.extractor import ConstraintExtractor, ConstraintGeometry
from oral_archaeology.parser import ParsedOralForm


# ── Vocabulary ──────────────────────────────────────────────────


_DEFAULT_VOCAB_DIR = Path(__file__).parent / "vocabulary"


@dataclass
class ProcessVocabulary:
    """
    A composable per-form process vocabulary.

    Use ``ProcessVocabulary.for_form(form_type)`` to load the default
    base vocabulary plus the form-specific overlay. Use
    ``ProcessVocabulary()`` empty if you want to populate from
    ``merge(...)`` calls directly.
    """

    processes: Dict[str, str] = field(default_factory=dict)
    modulations: Dict[str, str] = field(default_factory=dict)
    loaded_ids: List[str] = field(default_factory=list)

    @classmethod
    def for_form(
        cls,
        form_type: str,
        *,
        vocab_dir: Optional[Path] = None,
        language: str = "en",
    ) -> "ProcessVocabulary":
        """Compose the default-language vocab with the form overlay.

        Lookup order, later wins for the same key:
          1. ``default_<language>.json``
          2. ``<form_type>_<language>.json``  (if present)

        Missing files are skipped (vocabulary degrades cleanly).
        """
        v = cls()
        d = Path(vocab_dir) if vocab_dir is not None else _DEFAULT_VOCAB_DIR
        for filename in (f"default_{language}.json", f"{form_type}_{language}.json"):
            path = d / filename
            if path.exists():
                v.merge_from_path(path)
        return v

    @classmethod
    def empty(cls) -> "ProcessVocabulary":
        return cls()

    def merge_from_path(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.merge(data)

    def merge(self, data: Dict[str, Any]) -> None:
        for k, v in (data.get("processes") or {}).items():
            self.processes[k.lower()] = v
        for k, v in (data.get("modulations") or {}).items():
            self.modulations[k.lower()] = v
        vid = data.get("id")
        if vid:
            self.loaded_ids.append(vid)

    # -- lookup -------------------------------------------------

    def process_for(self, noun: Optional[str]) -> str:
        """Return the process name for a noun. Falls through to the
        input when not found, lower-cased for stability."""
        if not noun:
            return ""
        key = str(noun).lower()
        return self.processes.get(key, str(noun))

    def modulation_for(self, verb: Optional[str]) -> str:
        if not verb:
            return ""
        key = str(verb).lower()
        return self.modulations.get(key, str(verb))

    @property
    def composite_id(self) -> str:
        return "+".join(self.loaded_ids) if self.loaded_ids else "none"


# ── Extractor ───────────────────────────────────────────────────


class ProcessExtractor(ConstraintExtractor):
    """
    Additive extractor. Runs after the existing three. Writes:

    - ``geom.processes``         — list of ``{process, modulation,
                                              kind, constraint, ...}``
                                   dicts; one per sequence step or per
                                   phase / subject depending on form.
    - ``geom.process_couplings`` — list of ``{process_a, process_b,
                                              modulation, strength,
                                              ...}`` dicts, one per
                                   coupling already in ``geom.couplings``.
    - ``geom.vocabulary_id``     — the composite id of the vocabulary
                                   used (e.g. ``"default_en+breathing_en"``).
    """

    def __init__(
        self,
        vocabulary: Optional[ProcessVocabulary] = None,
        *,
        vocab_dir: Optional[Path] = None,
    ):
        self.vocabulary = vocabulary
        self.vocab_dir = vocab_dir

    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        vocab = self.vocabulary or ProcessVocabulary.for_form(
            parsed.form_type, vocab_dir=self.vocab_dir
        )
        geom.vocabulary_id = vocab.composite_id

        # Process couplings: one-to-one with existing couplings.
        # Strip leading articles so "the stone" looks up as "stone".
        for c in geom.couplings:
            geom.process_couplings.append({
                "process_a": vocab.process_for(
                    self._strip_article(c.get("source", ""))
                ),
                "process_b": vocab.process_for(
                    self._strip_article(c.get("target", ""))
                ),
                "modulation": vocab.modulation_for(c.get("relationship", "")),
                "strength": c.get("strength"),
                "inferred": c.get("inferred", False),
            })

        # Per-form processual entries
        if parsed.form_type == "story":
            sequence = parsed.structured.get("sequence", [])
            # The story is *about* one primary subject (flowing-water,
            # burning-fire, ...). The parser's per-clause "subject" can
            # drift onto an entity-hint that's actually the target
            # (e.g. "reaches the stone" sets current_subject='stone'),
            # so we anchor every entry to the first-seen subject so the
            # processual reading stays coherent: every modulation
            # describes how the primary process is changing.
            primary_subject = next(
                (e.get("subject") for e in sequence if e.get("subject")),
                None,
            )
            primary_process = (
                vocab.process_for(primary_subject) if primary_subject
                else "system"
            )
            for entry in sequence:
                target = entry.get("target")
                geom.processes.append({
                    "process": primary_process,
                    "modulation": vocab.modulation_for(entry.get("action", "")),
                    "kind": entry.get("kind"),
                    "constraint": (
                        vocab.process_for(self._strip_article(target))
                        if target else None
                    ),
                    "spatial": entry.get("spatial"),
                })

        elif parsed.form_type == "breathing":
            # Each phase IS its own process (inhaling, holding, ...);
            # no separate modulation. The renderer falls back to the
            # bare process name when modulation is None.
            for phase in parsed.structured.get("phases", []):
                geom.processes.append({
                    "process": vocab.process_for(phase.get("phase", "")),
                    "modulation": None,
                    "kind": "phase",
                    "constraint": None,
                    "duration": phase.get("count"),
                })

        elif parsed.form_type == "dance":
            # Dance subjects are concurrent processes (person A and
            # person B move at the same time). Modulation None so the
            # renderer shows them as bare process names.
            for s in parsed.structured.get("subjects", []):
                geom.processes.append({
                    "process": vocab.process_for(s),
                    "modulation": None,
                    "kind": "subject",
                    "constraint": None,
                })
            transitions = geom.phase_relationships.get("transitions") or []
            for t in transitions:
                geom.processes.append({
                    "process": vocab.process_for(t.get("trigger", "")),
                    "modulation": vocab.modulation_for(t.get("to", "")),
                    "kind": "transition",
                    "constraint": vocab.process_for(t.get("from", "")),
                })

    @staticmethod
    def _strip_article(span: str) -> str:
        """Drop a leading 'the / a / an' so 'the stone' looks up as 'stone'."""
        tokens = span.strip().split()
        if tokens and tokens[0].lower() in ("the", "a", "an"):
            tokens = tokens[1:]
        return " ".join(tokens) if tokens else span

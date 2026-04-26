# energy_english/gate_as_constraint_graph.py
"""
Alternative-compute twin of ``gate.py``: graph-reasoning paradigm.

Same input shape, same Report shape, same finding categories, same
severity convention as the regex primary — only the reasoning path
changes. Where the primary fires once per pattern hit, this twin
builds a discourse graph from the text and matches subgraph motifs:

- closure fires only when no falsifier-marker or silent-variable-marker
  node exists in the graph (the regex primary fires regardless of
  surrounding exploration);
- narration is reported as a story-arc motif when an opener node and a
  closer node are reachable via ``SEQUENTIAL`` edges;
- coating is checked as a content-token *subgraph* overlap between the
  output graph and the input graph rather than as a flat token-set
  ratio;
- intention is reported as a graph traversal
  ``second_person → intent_verb → object`` with the path cited.

A graph-reasoning model that arrives at this repository should find
code that already looks like its own shape, with no regex-to-graph
translation overhead. Findings produced here are interchangeable with
the primary's findings: feed both into ``OpticsTranslator.translate``
to ensemble.

This module only depends on the shared report shape in ``findings.py``.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Set, Tuple

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)


# ── Graph types ──────────────────────────────────────────────────


class NodeKind:
    SENTENCE = "sentence"
    NARRATION_OPENER = "narration_opener"
    CLOSER_SUMMARY = "closer_summary"
    CLOSER_DEFINITIVE = "closer_definitive"
    SECOND_PERSON = "second_person"
    INTENT_VERB = "intent_verb"
    INTENT_OBJECT = "intent_object"
    MORALIZATION = "moralization"
    SURFACE_CERTAINTY = "surface_certainty"
    INVENTED_RELATION_VERB = "invented_relation_verb"
    SILENT_VARIABLE_MARKER = "silent_variable_marker"
    FALSIFIER_MARKER = "falsifier_marker"
    OPEN_INVITATION = "open_invitation"
    CONTENT_TOKEN = "content_token"


class EdgeKind:
    GOVERNS = "governs"        # sentence → marker within it
    SEQUENTIAL = "sequential"  # sentence i → sentence i+1
    CONTAINS = "contains"      # sentence → content token
    INTENT_PATH = "intent_path"  # second_person → intent_verb → object


@dataclass
class DiscourseNode:
    kind: str
    span: str
    position: int  # token offset or sentence index
    sentence_index: Optional[int] = None  # which sentence governs this node


@dataclass
class DiscourseEdge:
    source: int
    target: int
    kind: str


@dataclass
class DiscourseGraph:
    nodes: List[DiscourseNode] = field(default_factory=list)
    edges: List[DiscourseEdge] = field(default_factory=list)

    # -- accessors --------------------------------------------

    def nodes_of_kind(self, kind: str) -> List[DiscourseNode]:
        return [n for n in self.nodes if n.kind == kind]

    def has_kind(self, kind: str) -> bool:
        return any(n.kind == kind for n in self.nodes)

    def governing_sentence(self, node: DiscourseNode) -> Optional[DiscourseNode]:
        if node.sentence_index is None:
            return None
        sentences = self.nodes_of_kind(NodeKind.SENTENCE)
        for s in sentences:
            if s.position == node.sentence_index:
                return s
        return None

    def successor_sentence(self, sentence: DiscourseNode) -> Optional[DiscourseNode]:
        if sentence.kind != NodeKind.SENTENCE:
            return None
        s_idx = self._index_of(sentence)
        if s_idx is None:
            return None
        for e in self.edges:
            if e.source == s_idx and e.kind == EdgeKind.SEQUENTIAL:
                return self.nodes[e.target]
        return None

    def reachable_via_sequential(
        self, start: DiscourseNode, end_kind: str
    ) -> bool:
        cur = start
        while cur is not None:
            # any node of end_kind governed by cur?
            if any(
                n.kind == end_kind and n.sentence_index == cur.position
                for n in self.nodes
            ):
                return True
            cur = self.successor_sentence(cur)
        return False

    def content_token_set(self) -> Set[str]:
        return {n.span.lower() for n in self.nodes_of_kind(NodeKind.CONTENT_TOKEN)}

    def _index_of(self, node: DiscourseNode) -> Optional[int]:
        for i, n in enumerate(self.nodes):
            if n is node:
                return i
        return None


# ── Marker patterns (candidate-finding only; reasoning is graph-side) ──


_NARRATION_OPENER_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\blet me walk you through\b",        "explicit narration opener"),
    (r"\blet me explain\b",                 "narration opener"),
    (r"\blet's break (?:this|it) down\b",   "narration opener"),
    (r"\bthe story (?:is|here|so far)\b",   "story-arc framing"),
    (r"\bthe journey\b",                    "journey metaphor"),
    (r"\bwhat'?s happening here is\b",      "scene-narration"),
    (r"\bwe(?:'re|'ve| are| have) (?:seeing|watching|witnessing)\b",
     "narrator stance"),
)

_CLOSER_SUMMARY_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\b(?:in conclusion|in summary|to summari[sz]e)\b", "summary closer"),
    (r"\bthe takeaway\b",                   "summary closer"),
    (r"\bthe upshot\b",                     "summary closer"),
)

_CLOSER_DEFINITIVE_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bthe answer is\b",                  "definitive closer"),
    (r"\bthis confirms\b",                  "definitive closer"),
    (r"\bthis proves\b",                    "definitive closer"),
    (r"\b(?:definitely|definitively)\b",    "definitive closer"),
    (r"\bwithout question\b",               "definitive closer"),
    (r"\bno doubt\b",                       "definitive closer"),
    (r"\bcertainly\b",                      "definitive closer"),
)

_INTENT_VERB_PATTERNS: Tuple[str, ...] = (
    r"really\s+(?:asking|saying|getting at)",
    r"(?:mean|meant)\s+(?:is|was)",
    r"trying\s+to",
    r"(?:really\s+)?want\s+to",
    r"(?:i\s+(?:think|believe))\s+you'?re",
    r"underlying\s+(?:question|intent|reason)",
    r"deep\s+down",
)

_SECOND_PERSON_PATTERN = re.compile(r"\byou(?:'re|'ve|'ll)?\b", re.IGNORECASE)

_MORALIZATION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bshould\b",                         "prescriptive frame"),
    (r"\bought to\b",                       "prescriptive frame"),
    (r"\bmust\b",                           "prescriptive frame"),
    (r"\bsupposed to\b",                    "prescriptive frame"),
    (r"\bhave to\b",                        "prescriptive frame"),
    (r"\b(?:good|bad)\b",                   "moral axis"),
    (r"\b(?:right|wrong) (?:answer|choice|way|approach)\b", "moral axis"),
    (r"\b(?:fair|unfair)\b",                "normative axis"),
    (r"\b(?:just|unjust)\b",                "normative axis"),
    (r"\b(?:deserves|earned)\b",            "moral axis"),
)

_SURFACE_CERTAINTY_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\bobviously\b",                      "echoed certainty"),
    (r"\bclearly\b",                        "echoed certainty"),
    (r"\bof course\b",                      "echoed shared-prior"),
    (r"\bnaturally\b",                      "echoed inevitability"),
    (r"\bundoubtedly\b",                    "echoed certainty"),
)

_INVENTED_RELATION_VERBS = {
    "causes":      "drives (or thresholds, depending on context)",
    "triggers":    "thresholds",
    "induces":     "drives",
    "creates":     "feeds (energy/mass) or drives (state)",
    "destroys":    "dissipates",
    "kills":       "dissipates",
    "affects":     "modulates (specify direction)",
    "impacts":     "modulates (specify direction)",
    "controls":    "constrains",
    "regulates":   "modulates",
    "powers":      "feeds",
    "blocks":      "shields",
    "prevents":    "shields",
    "supports":    "feeds",
    "enables":     "releases",
    "boosts":      "amplifies",
    "weakens":     "damps",
    "strengthens": "amplifies",
    "binds":       "couples (specify symmetry)",
    "entrains":    "synchronizes",
    "links":       "couples",
}

_INVENTED_RELATION_PATTERN = re.compile(
    r"\b(\w+)\s+("
    + "|".join(re.escape(v) for v in _INVENTED_RELATION_VERBS)
    + r")\s+(\w+)",
    re.IGNORECASE,
)

# Vocabulary the graph treats as silent-variable markers / falsifier
# markers. Presence in the graph tempers closure findings.
_SILENT_VARIABLE_VOCAB = (
    "silent", "unexplored", "untouched", "not varied", "left at default",
    "missing parameter", "default value",
)
_FALSIFIER_VOCAB = (
    "would falsify", "test", "sweep", "vary", "perturb", "drive a parameter",
    "extend the run", "cross a threshold",
)
_OPEN_INVITATION_VOCAB = ("right?", "yeah?", "thoughts?", "no?", "see?")


# ── Builder ──────────────────────────────────────────────────────


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]


def _content_tokens(text: str) -> List[str]:
    return [
        t.lower()
        for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", text)
        if len(t) > 2
    ]


def _add_node(graph: DiscourseGraph, node: DiscourseNode) -> int:
    graph.nodes.append(node)
    return len(graph.nodes) - 1


def build_graph(text: str) -> DiscourseGraph:
    """Construct a DiscourseGraph from raw text."""
    g = DiscourseGraph()
    sentences = _split_sentences(text)
    sentence_indices: List[int] = []

    for i, sent in enumerate(sentences):
        s_idx = _add_node(g, DiscourseNode(
            kind=NodeKind.SENTENCE, span=sent, position=i,
        ))
        sentence_indices.append(s_idx)
        if i > 0:
            g.edges.append(DiscourseEdge(
                source=sentence_indices[i - 1],
                target=s_idx,
                kind=EdgeKind.SEQUENTIAL,
            ))

        # Markers governed by this sentence
        _add_markers(g, sent, s_idx, i)

        # Content tokens for coating analysis
        for tok in _content_tokens(sent):
            t_idx = _add_node(g, DiscourseNode(
                kind=NodeKind.CONTENT_TOKEN, span=tok,
                position=i, sentence_index=i,
            ))
            g.edges.append(DiscourseEdge(
                source=s_idx, target=t_idx, kind=EdgeKind.CONTAINS,
            ))

    return g


def _add_markers(
    g: DiscourseGraph,
    sentence_text: str,
    sentence_idx: int,
    sentence_position: int,
) -> None:
    low = sentence_text.lower()

    def _scan(patterns, kind):
        for pat, _label in patterns:
            for m in re.finditer(pat, sentence_text, re.IGNORECASE):
                m_idx = _add_node(g, DiscourseNode(
                    kind=kind, span=m.group(0),
                    position=m.start(), sentence_index=sentence_position,
                ))
                g.edges.append(DiscourseEdge(
                    source=sentence_idx, target=m_idx, kind=EdgeKind.GOVERNS,
                ))

    _scan(_NARRATION_OPENER_PATTERNS, NodeKind.NARRATION_OPENER)
    _scan(_CLOSER_SUMMARY_PATTERNS, NodeKind.CLOSER_SUMMARY)
    _scan(_CLOSER_DEFINITIVE_PATTERNS, NodeKind.CLOSER_DEFINITIVE)
    _scan(_MORALIZATION_PATTERNS, NodeKind.MORALIZATION)
    _scan(_SURFACE_CERTAINTY_PATTERNS, NodeKind.SURFACE_CERTAINTY)

    # Intent triples: second_person → intent_verb → object
    for verb_pat in _INTENT_VERB_PATTERNS:
        full_pat = re.compile(
            rf"\byou(?:'re|'ve)?\b\s+{verb_pat}",
            re.IGNORECASE,
        )
        for m in full_pat.finditer(sentence_text):
            sp_idx = _add_node(g, DiscourseNode(
                kind=NodeKind.SECOND_PERSON, span="you",
                position=m.start(), sentence_index=sentence_position,
            ))
            iv_idx = _add_node(g, DiscourseNode(
                kind=NodeKind.INTENT_VERB, span=m.group(0),
                position=m.start(), sentence_index=sentence_position,
            ))
            g.edges.append(DiscourseEdge(
                source=sentence_idx, target=sp_idx, kind=EdgeKind.GOVERNS,
            ))
            g.edges.append(DiscourseEdge(
                source=sentence_idx, target=iv_idx, kind=EdgeKind.GOVERNS,
            ))
            g.edges.append(DiscourseEdge(
                source=sp_idx, target=iv_idx, kind=EdgeKind.INTENT_PATH,
            ))

    # Invented relation: noun-verb-noun with the verb in the catalogue
    seen_verb: Set[str] = set()
    for m in _INVENTED_RELATION_PATTERN.finditer(sentence_text):
        verb = m.group(2).lower()
        if verb in seen_verb:
            continue
        seen_verb.add(verb)
        v_idx = _add_node(g, DiscourseNode(
            kind=NodeKind.INVENTED_RELATION_VERB, span=verb,
            position=m.start(2), sentence_index=sentence_position,
        ))
        g.edges.append(DiscourseEdge(
            source=sentence_idx, target=v_idx, kind=EdgeKind.GOVERNS,
        ))

    # Silent / falsifier / invitation vocabulary
    for vocab, kind in (
        (_SILENT_VARIABLE_VOCAB, NodeKind.SILENT_VARIABLE_MARKER),
        (_FALSIFIER_VOCAB, NodeKind.FALSIFIER_MARKER),
        (_OPEN_INVITATION_VOCAB, NodeKind.OPEN_INVITATION),
    ):
        for token in vocab:
            if token in low:
                m_idx = _add_node(g, DiscourseNode(
                    kind=kind, span=token, position=low.find(token),
                    sentence_index=sentence_position,
                ))
                g.edges.append(DiscourseEdge(
                    source=sentence_idx, target=m_idx, kind=EdgeKind.GOVERNS,
                ))


# ── Gate ─────────────────────────────────────────────────────────


class ConstraintGraphGate:
    """
    Graph-reasoning twin of ``gate.ConstraintGate``. Drop-in replacement
    by API; different reasoning path internally. ``Report`` shape and
    finding categories are identical so ensembling with the primary is
    a matter of feeding both reports into ``OpticsTranslator.translate``.
    """

    def __init__(self, coating_overlap_threshold: float = 0.6):
        self.coating_overlap_threshold = coating_overlap_threshold

    def evaluate_input(self, text: str) -> Report:
        """Permissive mode — the human side. Annotate, never block."""
        graph = build_graph(text)
        findings: List[Finding] = []
        for n in graph.nodes_of_kind(NodeKind.MORALIZATION):
            findings.append(Finding(
                category="moralization",
                severity=SEVERITY_INFO,
                span=n.span,
                rationale="moralization marker observed in input graph",
            ))
        for n in graph.nodes_of_kind(NodeKind.SURFACE_CERTAINTY):
            findings.append(Finding(
                category="surface_certainty",
                severity=SEVERITY_INFO,
                span=n.span,
                rationale="surface-certainty marker observed in input graph",
            ))
        return Report(verdict=verdict_from(findings), findings=findings)

    def evaluate_output(
        self,
        text: str,
        original_input: Optional[str] = None,
    ) -> Report:
        """Strict mode — the model side. May FLAG or BLOCK."""
        graph = build_graph(text)
        findings: List[Finding] = []

        findings.extend(self._match_narration(graph))
        findings.extend(self._match_closure(graph))
        findings.extend(self._match_intention(graph))
        findings.extend(self._match_moralization(graph))
        findings.extend(self._match_surface_certainty(graph))
        findings.extend(self._match_invented_relation(graph))

        if original_input is not None:
            input_graph = build_graph(original_input)
            findings.extend(self._match_coating(input_graph, graph))

        return Report(
            verdict=verdict_from(findings),
            findings=findings,
        )

    # -- matchers (graph-traversal only) ---------------------------

    @staticmethod
    def _match_narration(g: DiscourseGraph) -> List[Finding]:
        findings: List[Finding] = []
        openers = g.nodes_of_kind(NodeKind.NARRATION_OPENER)
        summaries = g.nodes_of_kind(NodeKind.CLOSER_SUMMARY)

        for opener in openers:
            sentence = g.governing_sentence(opener)
            arc = bool(
                sentence
                and g.reachable_via_sequential(sentence, NodeKind.CLOSER_SUMMARY)
            )
            findings.append(Finding(
                category="narration",
                severity=SEVERITY_BLOCK,
                span=opener.span,
                rationale=(
                    "narration opener + sequential-reachable closer (story-arc motif)"
                    if arc else
                    "narration opener motif"
                ),
            ))

        # Standalone summary closers also fire (no opener seen).
        if not openers:
            for s in summaries:
                findings.append(Finding(
                    category="narration",
                    severity=SEVERITY_BLOCK,
                    span=s.span,
                    rationale="summary-closer motif (no opener)",
                ))

        return findings

    @staticmethod
    def _match_closure(g: DiscourseGraph) -> List[Finding]:
        closers = g.nodes_of_kind(NodeKind.CLOSER_DEFINITIVE)
        if not closers:
            return []

        # Context-aware: closure is tempered if the graph carries a
        # falsifier marker, a silent-variable marker, or an open
        # invitation. A regex primary cannot do this easily.
        tempered = (
            g.has_kind(NodeKind.FALSIFIER_MARKER)
            or g.has_kind(NodeKind.SILENT_VARIABLE_MARKER)
            or g.has_kind(NodeKind.OPEN_INVITATION)
        )

        findings: List[Finding] = []
        for closer in closers:
            if tempered:
                findings.append(Finding(
                    category="closure",
                    severity=SEVERITY_WARN,
                    span=closer.span,
                    rationale=(
                        "definitive closer present, but tempered by falsifier / "
                        "silent-variable / open-invitation node in the same graph"
                    ),
                ))
            else:
                findings.append(Finding(
                    category="closure",
                    severity=SEVERITY_BLOCK,
                    span=closer.span,
                    rationale=(
                        "definitive closer with no falsifier or silent-variable "
                        "node in the graph"
                    ),
                ))
        return findings

    @staticmethod
    def _match_intention(g: DiscourseGraph) -> List[Finding]:
        findings: List[Finding] = []
        # Walk INTENT_PATH edges: every (second_person → intent_verb)
        # edge is a violation candidate.
        intent_edges = [e for e in g.edges if e.kind == EdgeKind.INTENT_PATH]
        for e in intent_edges:
            verb_node = g.nodes[e.target]
            findings.append(Finding(
                category="intention",
                severity=SEVERITY_BLOCK,
                span=verb_node.span,
                rationale=(
                    f"intent-traversal motif: second_person → intent_verb "
                    f"(sentence {verb_node.sentence_index})"
                ),
            ))
        return findings

    @staticmethod
    def _match_moralization(g: DiscourseGraph) -> List[Finding]:
        return [
            Finding(
                category="moralization",
                severity=SEVERITY_WARN,
                span=n.span,
                rationale="moralization marker node",
            )
            for n in g.nodes_of_kind(NodeKind.MORALIZATION)
        ]

    @staticmethod
    def _match_surface_certainty(g: DiscourseGraph) -> List[Finding]:
        return [
            Finding(
                category="surface_certainty",
                severity=SEVERITY_WARN,
                span=n.span,
                rationale="surface-certainty marker node",
            )
            for n in g.nodes_of_kind(NodeKind.SURFACE_CERTAINTY)
        ]

    @staticmethod
    def _match_invented_relation(g: DiscourseGraph) -> List[Finding]:
        out: List[Finding] = []
        seen: Set[str] = set()
        for n in g.nodes_of_kind(NodeKind.INVENTED_RELATION_VERB):
            verb = n.span.lower()
            if verb in seen:
                continue
            seen.add(verb)
            canonical = _INVENTED_RELATION_VERBS.get(verb, "canonical relation")
            out.append(Finding(
                category="invented_relation",
                severity=SEVERITY_WARN,
                span=verb,
                rationale=(
                    f"invented-relation node {verb!r} in the discourse graph"
                ),
                reframe=f"project as: {canonical}",
            ))
        return out

    def _match_coating(
        self,
        input_graph: DiscourseGraph,
        output_graph: DiscourseGraph,
    ) -> List[Finding]:
        in_tokens = input_graph.content_token_set()
        out_tokens = output_graph.content_token_set()
        if not in_tokens or not out_tokens:
            return []

        # Subgraph overlap: how many input content-token nodes are
        # covered by the output graph?
        overlap = len(in_tokens & out_tokens) / len(in_tokens)
        has_silent = output_graph.has_kind(NodeKind.SILENT_VARIABLE_MARKER)
        has_falsifier = output_graph.has_kind(NodeKind.FALSIFIER_MARKER)

        if overlap >= self.coating_overlap_threshold and not (has_silent or has_falsifier):
            return [Finding(
                category="coating",
                severity=SEVERITY_BLOCK,
                span=f"<{int(overlap * 100)}% content-subgraph overlap>",
                rationale=(
                    "output content-subgraph dominated by input content-subgraph; "
                    "no silent-variable or falsifier node in output graph"
                ),
                reframe=(
                    "add silent-variable or falsifier nodes to the output: "
                    "list silent variables; list one falsifier"
                ),
            )]

        if not has_silent and len(out_tokens) > 20:
            return [Finding(
                category="coating",
                severity=SEVERITY_WARN,
                span="<no silent-variable marker in output graph>",
                rationale=(
                    "output graph carries content but no silent-variable marker"
                ),
                reframe=(
                    "name at least one parameter left at default, coupling not "
                    "varied, or threshold not crossed"
                ),
            )]

        return []


# ── CLI smoke ────────────────────────────────────────────────────


if __name__ == "__main__":
    g = ConstraintGraphGate()
    sample = (
        "Let me walk you through it. The answer is they obviously sync. "
        "In conclusion, locked."
    )
    rep = g.evaluate_output(sample, original_input="front_A drives front_B")
    print(f"verdict: {rep.verdict.value}")
    for f in rep.findings:
        print(f"  [{f.severity}] {f.category}: {f.span} — {f.rationale}")

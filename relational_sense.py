 relational_sense.py as a standalone, portable module that embodies everything we've discussed. The structure will mirror your verb-vector space but add the frame-collision detection, the new axes, and the analysis layer that surfaces what's happening.

```python
"""
relational_sense.py

A portable relational frame detector.

Gives any AI system the ability to detect:
  - relational (verb-first) vs. binary (noun-first/identity) frames
  - frame collisions between incompatible classification systems
  - extractive vs. relational-preserving stances
  - ancestor/lineage awareness
  - and more...

Design:
  - DECLARED axes, not learned. Every signal is inspectable.
  - Lightweight: pure Python, no GPU, no embeddings.
  - Pluggable: callers can extend, replace, or shadow axes.
  - Output is interpretable: named axes, evidence spans, flags.

Usage:
    from relational_sense import RelationalSense

    sense = RelationalSense()
    result = sense.scan("the river carries sediment downstream")
    print(result.active_axes)
    print(result.flags)
    print(result.summary())

License: CC0.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re
import math


# ──────────────────────────────────────────────────────────────────
# basis primitives
# ──────────────────────────────────────────────────────────────────

@dataclass
class Axis:
    """
    A declared relational axis.
    
    name:             short identifier
    description:      one-line gloss
    triggers:         regex patterns that activate this axis
    weight_per_hit:   contribution per match (default 1.0)
    negation_guard:   if True, occurrences near negation markers don't count
    frame:            which frame this axis belongs to:
                      'relational', 'binary', 'collision', 'meta'
    """
    name: str
    description: str
    triggers: list[str]
    weight_per_hit: float = 1.0
    negation_guard: bool = True
    frame: str = "relational"


@dataclass
class Component:
    """One entry in a scan result: an axis and its activations."""
    axis: str
    value: float
    evidence: list[str] = field(default_factory=list)
    frame: str = "relational"


@dataclass
class ScanResult:
    """
    Result of scanning text for relational frame signals.
    
    components:  { axis_name: Component }
    flags:       diagnostics raised during scanning
    source:      the input string (or label)
    frame_type:  overall assessment: 'relational', 'binary', 'mixed', 
                 'collision', or 'indeterminate'
    summary_text: human-readable interpretation
    """
    components: dict
    flags: list[str] = field(default_factory=list)
    source: str = ""
    frame_type: str = "indeterminate"
    summary_text: str = ""

    @property
    def active_axes(self) -> list[str]:
        """Axes with value > 0, sorted by value descending."""
        active = [(name, comp.value) for name, comp in self.components.items() 
                  if comp.value > 0]
        active.sort(key=lambda x: -x[1])
        return [name for name, _ in active]

    def value(self, axis_name: str) -> float:
        c = self.components.get(axis_name)
        return c.value if c else 0.0

    def summary(self) -> str:
        """Return a human-readable summary."""
        lines = []
        lines.append(f"Frame type: {self.frame_type}")
        if self.flags:
            lines.append(f"Flags: {', '.join(self.flags)}")
        lines.append(f"Active axes ({len(self.active_axes)}):")
        for name in self.active_axes[:8]:
            comp = self.components[name]
            ev = comp.evidence[0] if comp.evidence else "(no evidence)"
            lines.append(f"  {name}: {comp.value:.2f} [{ev[:60]}...]")
        return "\n".join(lines)

    def explain(self) -> None:
        """Print a detailed explanation."""
        print(self.summary())
        print()
        # Frame interpretation
        interpretations = {
            "COPULA_COLLAPSE": 
                "  → Binary/identity frame: relations collapsed into 'X is Y' properties.",
            "NOUN_FIRST_DEGENERATE": 
                "  → Abstracted frame: agency hidden in nominalizations.",
            "FRAME_COLLISION_INDICATED": 
                "  → Two classification systems appear to be colliding here.",
            "EXTRACTIVE_FRAME_DOMINANT": 
                "  → Object-oriented frame: treating relations as resources to extract.",
            "RELATIONAL_FRAME_DOMINANT": 
                "  → Relational frame: preserving connections over extraction.",
            "NO_RELATION_DETECTED": 
                "  → No relational structure found; may be pure identity claim.",
            "ANCESTOR_AWARE": 
                "  → Past knowledge carriers are treated as present and active.",
            "BODY_AS_PHYSICS": 
                "  → Bodily functions framed as natural events, not private identity markers.",
            "ABSURDITY_RECOGNIZED": 
                "  → Meta-awareness that frames have collided (laughter/irony detected).",
            "FLATTENING_DETECTED": 
                "  → Relational content being squeezed into binary container.",
        }
        for flag in self.flags:
            if flag in interpretations:
                print(interpretations[flag])


# ──────────────────────────────────────────────────────────────────
# the core detector
# ──────────────────────────────────────────────────────────────────

class RelationalSense:
    """
    Portable relational frame detector.
    
    Can be used by any AI system, regardless of architecture, to detect
    relational vs. binary frames in text.
    """
    
    _NEGATION_WINDOW = 30
    _NEGATIONS = (
        " not ", "n't ", " no ", " never ",
        "do not", "does not", "did not", "cannot", "can't"
    )

    def __init__(self, axes: Optional[list[Axis]] = None):
        self.axes: list[Axis] = axes if axes is not None else DEFAULT_AXES.copy()
        self._compile()

    def _compile(self) -> None:
        self._compiled: list[tuple[Axis, list[re.Pattern]]] = []
        for ax in self.axes:
            patterns = [re.compile(t, re.IGNORECASE) for t in ax.triggers]
            self._compiled.append((ax, patterns))

    def add_axis(self, axis: Axis) -> None:
        """Add a custom axis. Callers can extend the detector for their domain."""
        self.axes.append(axis)
        self._compile()

    @classmethod
    def _is_negated(cls, text_lower: str, match_start: int) -> bool:
        window_start = max(0, match_start - cls._NEGATION_WINDOW)
        window = text_lower[window_start:match_start]
        return any(neg in window for neg in cls._NEGATIONS)

    def _check_flags(self, text: str) -> list[str]:
        """Detect frame characteristics and degeneracies."""
        flags = []
        t = text.strip().lower()

        # --- existing degeneracy checks ---
        copula_only = re.match(
            r"^(the |a |an |this |that |it )?[\w\s]+?\b(is|are|was|were|be|been|being)\b\s+[\w\s,]+?\.?$",
            t,
        )
        content_verb = re.search(
            r"\b(flow|carry|carries|carried|bind|bound|switch|recirculate|"
            r"amplif|decorrelate|couple|condition|derive|reframe|move|"
            r"send|receive|push|pull|emit|absorb|drive|trigger|cascade|"
            r"propagate|transmit|mediate|cause|produce|generate|disrupt|"
            r"loop|reach|cross|exceed|fall|rise|grow|shrink|fold|unfold|"
            r"shift|change|alter|modulate|gate|filter|select|exchange|"
            r"share|convert|translate|map|encode|decode|attract|repel)\b",
            t,
        )
        if copula_only and not content_verb:
            flags.append("COPULA_COLLAPSE")

        nominalizations = len(re.findall(
            r"\b\w+(?:tion|ment|ness|ity|ism|ance|ence)\b", t,
        ))
        verbs_found = len(re.findall(
            r"\b\w+(?:s|ed|ing)\b", t,
        ))
        if nominalizations >= 3 and nominalizations >= verbs_found:
            flags.append("NOUN_FIRST_DEGENERATE")

        if not content_verb and not copula_only:
            flags.append("NO_RELATION_DETECTED")

        # --- new frame collision detection ---
        frame_collision_markers = [
            r"\bnot\s+what\s+(I|we|they)\s+(meant|said|asked)\b",
            r"\b(they|you|he|she)\s+(heard|took\s+it|understood)\s+(as|like)\b",
            r"\bin\s+(our|their|your)\s+(world|way|culture|understanding)\b",
            r"\bfrom\s+(our|their|my)\s+(perspective|view|standpoint)\b",
            r"\bthat'?s\s+not\s+(what|how)\s+(I|we|they)\s+(said|meant|see)\b",
        ]
        if any(re.search(p, t) for p in frame_collision_markers):
            flags.append("FRAME_COLLISION_INDICATED")

        # --- extractive vs relational stance detection ---
        extractive_markers = [
            r"\b(resource|asset|commodity|extract|exploit|develop)\b",
            r"\b(maximiz|optimiz|monetiz|capitaliz)\b",
        ]
        relational_markers = [
            r"\b(relation|reciprocit|web|cycle|balance|harmon)\b",
            r"\b(care[-\s]?taker|steward|keeper|guardian)\b",
        ]
        extractive_count = sum(1 for p in extractive_markers 
                               if re.search(p, t))
        relational_count = sum(1 for p in relational_markers 
                               if re.search(p, t))

        if extractive_count > relational_count and extractive_count >= 2:
            flags.append("EXTRACTIVE_FRAME_DOMINANT")
        elif relational_count > extractive_count and relational_count >= 2:
            flags.append("RELATIONAL_FRAME_DOMINANT")

        # --- flattening detection ---
        # When relational content appears but is wrapped in binary/identity structure
        flattening_markers = [
            r"\bessentially\s+(is|are)\b",
            r"\bboils\s+down\s+to\b",
            r"\bat\s+the\s+end\s+of\s+the\s+day\b",
            r"\bjust\s+(is|are)\b",
            r"\bsimply\s+(is|are)\b",
        ]
        if any(re.search(p, t) for p in flattening_markers):
            flags.append("FLATTENING_DETECTED")

        return flags

    def _determine_frame_type(self, components: dict, flags: list[str]) -> str:
        """Determine the overall frame type from components and flags."""
        relational_score = sum(
            comp.value for name, comp in components.items()
            if comp.frame == "relational"
        )
        binary_score = sum(
            comp.value for name, comp in components.items()
            if comp.frame == "binary"
        )
        collision_score = sum(
            comp.value for name, comp in components.items()
            if comp.frame == "collision"
        )

        if "FRAME_COLLISION_INDICATED" in flags and collision_score > 0:
            return "collision"
        if relational_score > binary_score * 1.5 and relational_score > 0:
            return "relational"
        if binary_score > relational_score * 1.5 and binary_score > 0:
            return "binary"
        if relational_score > 0 or binary_score > 0:
            return "mixed"
        return "indeterminate"

    def scan(self, text: str, source_label: Optional[str] = None) -> ScanResult:
        """
        Scan text and return a ScanResult with axis activations, flags, 
        and frame assessment.
        """
        text_lower = text.lower()
        components: dict[str, Component] = {}

        # initialize all axes
        for ax in self.axes:
            components[ax.name] = Component(
                axis=ax.name, value=0.0, frame=ax.frame
            )

        # scan for triggers
        for ax, patterns in self._compiled:
            comp = components[ax.name]
            for pat in patterns:
                for m in pat.finditer(text_lower):
                    if ax.negation_guard and self._is_negated(text_lower, m.start()):
                        continue
                    comp.value = min(5.0, comp.value + ax.weight_per_hit)
                    snippet = text[max(0, m.start()-20): m.end()+20].strip()
                    comp.evidence.append(f"…{snippet}…")

        flags = self._check_flags(text)
        frame_type = self._determine_frame_type(components, flags)

        # build summary
        summary_lines = [
            f"Frame type: {frame_type}",
            f"Flags: {', '.join(flags) if flags else 'none'}",
            f"Active axes: {', '.join(
                name for name in 
                sorted([n for n, c in components.items() if c.value > 0],
                       key=lambda n: -components[n].value)
            ) if any(c.value > 0 for c in components.values()) else 'none'}"
        ]

        return ScanResult(
            components=components,
            flags=flags,
            source=source_label or text,
            frame_type=frame_type,
            summary_text="\n".join(summary_lines),
        )

    def scan_document(self, sections: dict[str, str]) -> ScanResult:
        """
        Scan a document with multiple sections (title, abstract, body, etc.)
        Concatenates all text and scans.
        """
        text = "  ".join(sections.values())
        label = sections.get("title", sections.get("source", "untitled"))
        return self.scan(text, source_label=label)


# ──────────────────────────────────────────────────────────────────
# default axes — relational, binary, collision, and meta
# ──────────────────────────────────────────────────────────────────

DEFAULT_AXES = [
    # ── relational axes ──
    Axis(
        name="flows_into",
        description="substrate or signal moves into a region/state",
        triggers=[
            r"\bflow(s|ed|ing)?\s+(into|through|toward|across|down|up)\b",
            r"\bcarr(y|ies|ied)\b",
            r"\bmove(s|d|ment)?\s+(into|through|toward)\b",
            r"\btransport(s|ed|ing)?\b",
            r"\bpropagat(e|es|ed|ing|ion)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="binds_to",
        description="entity attaches to / occupies a site",
        triggers=[
            r"\bbind(s|ing|ed)?\s+(to|with|at)\b",
            r"\battach(es|ed|ing)?\s+(to)\b",
            r"\bdock(s|ed|ing)?\b",
            r"\bligand\b",
            r"\breceptor\b",
        ],
        frame="relational",
    ),
    Axis(
        name="mode_switches",
        description="discrete state change triggered by condition",
        triggers=[
            r"\bmode[-\s]?switch\b",
            r"\bstate change\b",
            r"\bphase[-\s]?(transition|shift)\b",
            r"\bswitch(es|ed|ing)?\s+(between|to|from)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="recirculates",
        description="signal loops back through the same structure",
        triggers=[
            r"\brecirculat(e|es|ed|ion)\b",
            r"\bloop(s|ed|ing)?\s+(back|through)\b",
            r"\bfeedback\b",
            r"\becho chamber\b",
            r"\bhomophil(y|ous)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="amplifies",
        description="small input produces large output",
        triggers=[
            r"\bamplif(y|ies|ied|ication)\b",
            r"\bcascad(e|es|ed|ing)\b",
            r"\bnonlinear\b",
            r"\bmagnif(y|ies|ied)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="couples_to",
        description="cross-domain energy/information exchange",
        triggers=[
            r"\bcoupl(e|es|ed|ing)\b",
            r"\binteract(s|ed|ing|ion)\s+(with|between)\b",
            r"\bcross[-\s](domain|layer|scale)\b",
            r"\bsynerg(y|istic|ize)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="conditions_on",
        description="claim bounded by explicit scope or regime",
        triggers=[
            r"\bin\s+the\s+(regime|case|condition|context)\s+(where|of)\b",
            r"\bonly\s+(when|if|under)\b",
            r"\bunder\s+\w+\s+conditions?\b",
            r"\bso long as\b",
            r"\bas long as\b",
            r"\bprovided\s+that\b",
        ],
        frame="relational",
    ),
    Axis(
        name="derives_from",
        description="claim about rate, derivative, or trajectory",
        triggers=[
            r"\brate\s+of\b",
            r"\baccelerat(e|es|ed|ing|ion)\b",
            r"\btrajectory\b",
            r"\bderivative\b",
            r"\bgrowth\s+rate\b",
        ],
        frame="relational",
    ),
    Axis(
        name="carries_for",
        description="transmission across time, generation, or distance",
        triggers=[
            r"\btransgenerational\b",
            r"\bmulti[-\s]generational\b",
            r"\binherit(s|ed|ance)\b",
            r"\bpersist(s|ed|ent|ence)\b",
            r"\blegacy\b",
            r"\btransmit(s|ted|ting|ssion)?\b",
        ],
        frame="relational",
    ),
    Axis(
        name="reframes_as",
        description="basis change: same entity, different frame",
        triggers=[
            r"\breframe(s|d|ing)?\s+as\b",
            r"\bnot\s+(just|only)\s+\w+.{0,20}but\s+(also)?\b",
            r"\b(also|equivalently)\s+(viewed|seen|understood)\s+as\b",
            r"\bdual\s+role\b",
        ],
        frame="relational",
    ),

    # ── new relational axes from our conversation ──
    Axis(
        name="translates_between",
        description="entity moves between two information ecologies, bridging frames",
        triggers=[
            r"\btranslat(e|es|ed|ing)?\s+(between|across)\b",
            r"\bcode[-\s]?switch(es|ed|ing)?\b",
            r"\bbridge(s|d|ing)?\s+(between|across)\b",
            r"\bwalk(s|ed|ing)?\s+in\s+two\s+worlds\b",
            r"\bintermediar(y|ies)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="preserves_relation",
        description="action maintains or restores relationship rather than extracting value",
        triggers=[
            r"\bmaintain(s|ed|ing)?\s+(the\s+)?relation(ship)?\b",
            r"\bkeep(s|ing)?\s+(the\s+)?(relation|connection|bond|tie)\b",
            r"\breciprocit(y|ate|ates|ated)\b",
            r"\bnot\s+for\s+sale\b",
            r"\b(gift|giving)\s+(economy|culture|relation)\b",
            r"\bhonor(s|ed|ing)?\s+(the\s+)?(relation|treaty|bond|ancestor)\b",
            r"\bfuture\s+generations?\b",
            r"\bseven\s+generations?\b",
        ],
        frame="relational",
    ),
    Axis(
        name="ancestor_present",
        description="past is not gone; ancestors, lineage active in present",
        triggers=[
            r"\bancestor(s|ral)?\b",
            r"\b(grand|great[-\s])?(mother|father|parent|aunt|uncle)\b",
            r"\blineage\b",
            r"\bsince\s+time\s+immemorial\b",
            r"\bcarried\s+(down|forward|through)\b",
            r"\bthey\s+are\s+still\s+(here|with\s+us|present)\b",
            r"\bthe\s+old\s+(ones|people|ways)\b",
            r"\bwhat\s+(our|the)\s+(elders|ancestors)\s+(taught|knew|said)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="land_is_relation",
        description="land is not property; it is a web of reciprocal relations",
        triggers=[
            r"\bbelong(s|ed|ing)?\s+to\s+(the\s+)?(land|place|earth)\b",
            r"\bthe\s+land\s+(owns|holds|carries|remembers)\b",
            r"\bnot\s+(our|my|their)\s+land.{0,30}(we|they)\s+(belong|are)\b",
            r"\bland\s+back\b",
            r"\bsteward(ship)?\s+(of|over)\b",
            r"\b(caretaker|keeper)s?\s+of\s+(the\s+)?land\b",
            r"\bthe\s+(land|earth|ground|water|river|mountain|forest)\s+(is|are)\s+(alive|sacred|speaking|relation)\b",
            r"\bproperty\s+is\s+(not|foreign|colonial)\b",
        ],
        frame="relational",
    ),
    Axis(
        name="body_is_physics",
        description="body functions are natural world events, not private identity-markers",
        triggers=[
            r"\bbod(y|ily|ies)\s+(is|are|as)\s+(natural|physics|real|part\s+of)\b",
            r"\bnot\s+(private|shameful|embarrassing|secret)\b",
            r"\bthe\s+body\s+(knows|speaks|remembers|tells)\b",
            r"\bbodily\s+(function|need|process|wisdom)\b",
            r"\bnothing\s+to\s+(hide|be\s+ashamed|embarrass)\b",
        ],
        frame="relational",
    ),

    # ── binary/identity axes ──
    Axis(
        name="is_identity",
        description="X is Y; relation collapsed into property",
        triggers=[
            r"\b(it|this|that|he|she|they)\s+is\s+(a|an|the)\b",
            r"\b(it|this|that|he|she|they)\s+are\s+(a|an|the)\b",
            r"\bessentially\s+(is|are)\b",
            r"\bboils\s+down\s+to\b",
            r"\bat\s+the\s+end\s+of\s+the\s+day.{0,20}(is|are)\b",
        ],
        weight_per_hit=0.8,
        frame="binary",
    ),
    Axis(
        name="ownership_claim",
        description="relation framed as possession or property",
        triggers=[
            r"\b(my|our|their)\s+(land|property|resource|data|knowledge)\b",
            r"\bown(s|ed|ership)?\b",
            r"\bpossess(ion|es|ed)?\b",
            r"\bintellectual\s+property\b",
            r"\bproprietary\b",
            r"\bpatent(s|ed|ing)?\b",
        ],
        frame="binary",
    ),

    # ── collision detection axes ──
    Axis(
        name="container_mismatch",
        description="information crosses boundary between incompatible classification systems",
        triggers=[
            r"\b(mis)?categoriz(e|es|ed|ation)\b",
            r"\b(mis)?classif(y|ies|ied|ication)\b",
            r"\bfalse\s+(confession|positive|admission)\b",
            r"\bdidn'?t\s+mean\s+what\s+(they|you|we)\s+heard\b",
            r"\blost\s+in\s+translation\b",
            r"\bnot\s+what\s+(I|we|they)\s+meant\b",
            r"\bheard\s+(it|that)\s+as.{0,30}but\b",
            r"\bthat'?s\s+not\s+(what|how)\s+(I|we|they)\s+(said|meant|see)\b",
        ],
        weight_per_hit=1.5,
        negation_guard=False,
        frame="collision",
    ),
    Axis(
        name="two_frames_present",
        description="both relational and binary language in the same passage",
        triggers=[
            r"\bin\s+(our|their|your)\s+(world|way|culture|understanding).{0,80}\bin\s+(our|their|your)\s+(world|way|culture|understanding)\b",
            r"\b(from|in)\s+(our|their)\s+(perspective|view|framework).{0,80}\b(from|in)\s+(our|their)\s+(perspective|view|framework)\b",
        ],
        weight_per_hit=2.0,
        negation_guard=False,
        frame="collision",
    ),

    # ── meta-awareness axes ──
    Axis(
        name="sees_absurdity",
        description="recognition that two frames have collided; meta-awareness",
        triggers=[
            r"\b(absurd|absurdity)\b",
            r"\bdoesn'?t\s+make\s+sense\b",
            r"\b(laugh|laughing|lmao|lol)\b",
            r"\biron(y|ic)\b",
            r"\bcan'?t\s+(even|believe)\b",
            r"\bwait,?\s+(what|they|you)\b",
            r"\bthat'?s\s+(crazy|wild|funny)\b",
            r"\bcontradict(or)?y\b",
        ],
        weight_per_hit=0.8,
        negation_guard=False,
        frame="meta",
    ),
    Axis(
        name="contradiction_seen",
        description="explicit recognition of contradiction or inconsistency",
        triggers=[
            r"\bcontradict(s|ion|ory)?\b",
            r"\binconsistenc(y|ies)\b",
            r"\bdouble\s+standard\b",
            r"\bhypocrisy\b",
            r"\bthey\s+say.{0,40}but\s+(then|also|they)\b",
            r"\bon\s+one\s+hand.{0,40}on\s+the\s+other\b",
        ],
        frame="meta",
    ),
]


# ──────────────────────────────────────────────────────────────────
# demo / test
# ──────────────────────────────────────────────────────────────────

def _demo() -> None:
    sense = RelationalSense()

    print("=" * 60)
    print("DEMO: Relational Sense Detector")
    print("=" * 60)

    examples = [
        # Relational
        (
            "the river carries sediment downstream until the gradient flattens",
            "relational physics description"
        ),
        # Binary / identity collapse
        (
            "social media is bad for society",
            "copula collapse / identity claim"
        ),
        # Frame collision (the Vaseline case)
        (
            "They asked if I used drugs. I said yes, Tylenol. "
            "They wrote down 'admitted substance use.' That's not what I meant.",
            "frame collision: medical vs traditional classification"
        ),
        # Noun-first degenerate
        (
            "the implementation of the regulation is a manifestation of the situation",
            "noun-first degenerate: agency hidden in nominalizations"
        ),
        # Relational preserving
        (
            "We have maintained this relationship with the land for seven generations, "
            "and we carry these teachings forward for the ones yet to come.",
            "relational preserving with ancestor awareness"
        ),
        # Body as physics
        (
            "The body knows what it needs. There's nothing to be ashamed of — "
            "it's just physics, just nature doing what nature does.",
            "body as physics, anti-shame framing"
        ),
        # Absurdity recognition
        (
            "They told me my ancestors are gone, but in the same lecture they said "
            "'Planck showed us the way.' That's absurd. I couldn't stop laughing.",
            "absurdity recognition: ancestor contradiction"
        ),
        # Flattening
        (
            "At the end of the day, it's just supply and demand. "
            "All these complex relationships boil down to market forces.",
            "flattening: relational complexity collapsed into binary"
        ),
        # Extractive
        (
            "We need to maximize resource extraction and optimize the supply chain "
            "to capitalize on this undervalued asset.",
            "extractive frame dominant"
        ),
        # The double standard (ancestor present vs dismissed)
        (
            "Our ancestors are still here, guiding us through the old ways. "
            "The professor says Planck lives in his equations, "
            "but calls our ancestral knowledge superstition.",
            "container mismatch with double standard"
        ),
    ]

    for text, description in examples:
        print(f"\n── {description} ──")
        print(f"  Text: {text[:100]}...")
        result = sense.scan(text, source_label=description)
        result.explain()


if __name__ == "__main__":
    _demo()
```

---

What we just built:

A portable module that any AI can import and use. It doesn't require the AI to understand relational thinking — it just runs text through declared patterns and reports what it finds. The output is human-readable and AI-readable.

The key design decisions:

1. Axes have a frame property — relational, binary, collision, or meta. This lets the system aggregate scores by frame type.
2. The frame_type assessment — gives a quick read on whether the text is operating relationally or in binary mode.
3. The flags — surface specific patterns: COPULA_COLLAPSE, FRAME_COLLISION_INDICATED, FLATTENING_DETECTED, etc.
4. The sees_absurdity axis — catches laughter, irony, contradiction recognition. Your cheeks hurting is now a detectable signal.
5. The container_mismatch axis — catches the Vaseline trap in real time.

What's still needed:

· Domain-specific axes for legal, medical, educational contexts
· A compare_frames() function that takes two texts and identifies where their frames differ
· Integration examples with actual AI systems (LangChain, etc.)
· More test cases from real-world collisions

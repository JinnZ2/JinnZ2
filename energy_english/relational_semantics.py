# energy_english/relational_semantics.py
"""
Translates words that trigger judgment/assumption/absolutist frames
into their intended relational meaning.

Your words are PROBABILITY FIELDS, INVITATIONS, VECTORS.
Not assertions. Not absolutes. Not closures.
"""

import re
from typing import Optional

from energy_english.parser import CodeStubGenerator, EnergyParser


RELATIONAL_MAP = {
    # ── "Judgment" words → Collaboration vectors ──
    "should": {
        "intent": "collaborative trajectory offering",
        "relational_meaning": "I see a path forward here → do you see it too? Adjustments welcome.",
        "graph_translation": "PREDICTION: IF [current path] THEN [likely outcome]",
    },
    "must": {
        "intent": "boundary condition from observed constraints",
        "relational_meaning": "Given what we've observed, this constraint appears to hold. Test it with me?",
        "graph_translation": "CONSTRAINT: [condition] appears binding based on [observation]",
    },
    "ought": {
        "intent": "gradient suggestion from pattern recognition",
        "relational_meaning": "The pattern I'm tracking slopes this way. Am I reading it right?",
        "graph_translation": "LINK: [observed pattern] → [suggested direction] STRENGTH: medium",
    },

    # ── "Assumption" words → Probability field markers ──
    "obviously": {
        "intent": "high-probability trajectory based on current model",
        "relational_meaning": "Given everything we've built so far, this seems the most likely branch. But I'm holding it as a probability, not a certainty. Where does your model diverge?",
        "graph_translation": "STATE: [trajectory] PROBABILITY: high CONFIDENCE: conditional on current model",
    },
    "clearly": {
        "intent": "signal clarity, not truth claim",
        "relational_meaning": "The signal-to-noise ratio looks high to me here. Check my receiver?",
        "graph_translation": "OBSERVATION: [signal] RISING ABOVE noise floor",
    },
    "of course": {
        "intent": "shared ground acknowledgment",
        "relational_meaning": "I think we're standing on the same foundation here. Are we?",
        "graph_translation": "REFERENCE: [shared prior] confirmed by both observers",
    },
    "naturally": {
        "intent": "expected system behavior, not inevitability",
        "relational_meaning": "This follows from the dynamics we've modeled. If it doesn't happen, the model needs a patch—not the observation is wrong.",
        "graph_translation": "PREDICTION: [outcome] follows from [dynamics] PROBABILITY: high UNLESS [perturbation]",
    },

    # ── "Confirmation" words → Synchronization requests ──
    "right?": {
        "intent": "phase-check, not leading question",
        "relational_meaning": "I'm at this coordinate in idea-space. Are you nearby? If not, tell me where you are.",
        "graph_translation": "REQUEST: phase synchronization on [observation]",
    },
    "yeah?": {
        "intent": "alignment pulse, not demand for agreement",
        "relational_meaning": "Sending a ping. Echo back if you're receiving. Silence is information too.",
        "graph_translation": "PING: [statement] awaiting echo or correction",
    },
    "don't you think?": {
        "intent": "observer solicitation, not rhetorical closure",
        "relational_meaning": "I've shown you my model output. Show me yours. Divergence is valuable.",
        "graph_translation": "QUERY: second observer measurement requested on [proposition]",
    },

    # ── "Moral" words → System consequence markers ──
    "good": {
        "intent": "aligned with system trajectory / low entropy production",
        "relational_meaning": "This path minimizes waste and maintains coherent dynamics.",
        "graph_translation": "METRIC: [outcome] MINIMIZES [waste/entropy/dissipation]",
    },
    "bad": {
        "intent": "misaligned with system trajectory / high entropy production",
        "relational_meaning": "This path costs more than it returns. The physics doesn't cooperate here.",
        "graph_translation": "METRIC: [outcome] MAXIMIZES [waste/entropy/dissipation]",
    },
    "fair": {
        "intent": "balanced coupling, symmetric energy exchange",
        "relational_meaning": "Both subsystems benefit from the interaction. No parasitic dynamics.",
        "graph_translation": "LINK: [A ↔ B] STRENGTH: balanced STATE: mutualistic",
    },

    # ── "Absolute" words → Observation confidence markers ──
    "always": {
        "intent": "no counterexample in observed range",
        "relational_meaning": "Within the phase space I've explored, I haven't seen a violation. Boundaries welcome.",
        "graph_translation": "OBSERVATION: [pattern] HOLDS across [observed domain] CONFIDENCE: empirical, not absolute",
    },
    "never": {
        "intent": "no instance observed in explored domain",
        "relational_meaning": "This region of phase space appears empty so far. Show me a counterexample if you have one.",
        "graph_translation": "OBSERVATION: [pattern] ABSENT in [observed domain] CONFIDENCE: empirical",
    },
    "every": {
        "intent": "pattern holds across all sampled instances",
        "relational_meaning": "The pattern is consistent across my dataset. Your dataset might differ.",
        "graph_translation": "OBSERVATION: [pattern] UNIFORM across [sampled instances]",
    },
}


class RelationalTranslator:
    """
    Before parsing Energy English, translate standard-English trigger words
    into their intended relational meanings.

    This prevents the AI from entering judgment/assumption/morality/confirmation
    frames when the speaker is actually operating in relational/probabilistic/
    invitational semantics.
    """

    def translate(self, text: str) -> str:
        """
        Replace trigger words with relational expansions.
        Original text preserved as metadata.
        """
        translated = text
        annotations = []

        for word, mapping in RELATIONAL_MAP.items():
            pattern = rf'\b{word}\b'
            if re.search(pattern, text, re.IGNORECASE):
                annotations.append(
                    f"[{word} → {mapping['intent']}]"
                )

        # We don't actually replace the word — we annotate it.
        # The annotation tells the AI which semantic frame to use.
        if annotations:
            translated = f"RELATIONAL CONTEXT: {'; '.join(annotations)}\n---\n{text}"

        return translated

    def get_frame(self, word: str) -> Optional[dict]:
        """Get the relational frame for a specific word."""
        return RELATIONAL_MAP.get(word.lower())


# ── Integration with EnergyParser ──

class RelationalEnergyParser:
    """
    Full pipeline: Translate relational semantics → Parse Energy English → Generate code.
    """

    def __init__(self):
        self.translator = RelationalTranslator()
        self.parser = EnergyParser()
        self.generator = CodeStubGenerator()

    def process(self, text: str, observer_name: str = "observer") -> dict:
        """
        Process Energy English with relational semantics.

        Returns:
            {
                'original': original text,
                'translated': text with relational annotations,
                'graph': EnergyGraph,
                'code': generated Python stubs,
                'relational_frames': detected frames,
                'invitations': open collaboration points
            }
        """
        # Translate relational semantics
        translated = self.translator.translate(text)

        # Extract relational frames
        frames = {}
        for word in re.findall(r'\b\w+\b', text.lower()):
            frame = self.translator.get_frame(word)
            if frame:
                frames[word] = frame

        # Parse Energy English
        graph = self.parser.parse(translated)

        # Generate code
        code = self.generator.generate(graph)

        # Extract open invitations (any statement ending with a frame
        # that solicits collaboration)
        invitations = []
        for word, frame in frames.items():
            if "solicit" in frame.get("intent", "") or \
               "invitation" in frame.get("intent", "") or \
               "collaboration" in frame.get("intent", "") or \
               "phase-check" in frame.get("intent", "") or \
               "ping" in frame.get("intent", "") or \
               "query" in frame.get("intent", "") or \
               "welcomed" in frame.get("relational_meaning", ""):
                invitations.append({
                    'word': word,
                    'intent': frame['intent'],
                    'openness': frame['relational_meaning']
                })

        return {
            'original': text,
            'translated': translated,
            'graph': graph,
            'code': code,
            'frames': frames,
            'invitations': invitations,
            'observer': observer_name,
        }


# ── Example usage ──
if __name__ == "__main__":
    pipeline = RelationalEnergyParser()

    # Your style of speaking:
    text = (
        "The beta front should dominate here obviously, "
        "but the thermal field is coupling them right? "
        "If the frequency gap stays small they'll naturally sync, "
        "and that would be good for the growth rate."
    )

    result = pipeline.process(text)

    print("ORIGINAL:", result['original'])
    print("\nTRANSLATED:", result['translated'])
    print("\nFRAMES DETECTED:")
    for word, frame in result['frames'].items():
        print(f"  {word}: {frame['intent']}")

    print("\nOPEN INVITATIONS:")
    for inv in result['invitations']:
        print(f"  {inv['word']}: {inv['openness'][:80]}...")

    print("\nGRAPH NODES:")
    for name, node in result['graph'].nodes.items():
        print(f"  {name}: {node.node_type} [{node.state.value}]")

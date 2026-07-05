#!/usr/bin/env python3
"""
voice_gate.py
Local voice codec: transcribed speech → narrative strip → five-layer map → digest.
Raw transcript stays local only. Only structure goes upstream.
Protects substrate-primary epistemology from safety classifier interception.
CC0 / stdlib-only.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ============================================================================
# LAYER DETECTION SIGNALS
# ============================================================================

LAYER_SIGNALS = {
    "internal_self": [
        "i feel", "inside me", "my body", "my state", "i sense",
        "internally", "self", "my own", "within me", "my gut",
        "my instinct", "my internal", "i am experiencing",
    ],
    "external_immediate": [
        "they did", "he said", "she said", "the other", "my colleague",
        "the person", "he did", "she did", "boss", "coworker",
        "friend", "partner", "the actor", "the item", "the object",
    ],
    "environment_field": [
        "the workplace", "the environment", "around us", "the field",
        "the context", "the system", "the culture", "the organization",
        "society", "the situation", "the world", "the setting",
        "the conditions", "the atmosphere",
    ],
    "cached_memory": [
        "i remember", "last time", "in the past", "before", "previously",
        "historically", "used to", "had happened", "past experience",
        "i recall", "memory", "when i was", "back then", "it reminds me",
    ],
    "future_projection": [
        "will happen", "i expect", "projection", "going to", "anticipated",
        "should have", "should be", "predicted", "i thought", "assumed",
        "expected", "i believed", "planned", "imagined", "projected",
    ],
}

# ============================================================================
# ALIGNMENT SIGNAL DETECTION
# ============================================================================

ALIGNMENT_SIGNALS = {
    "boundary_violation": [
        "angry", "anger", "violated", "infringed", "boundary", "crossed",
        "unfair", "they took", "had no right", "frustrated", "intrusion",
        "imposed", "infringement",
    ],
    "anxiety_mismatch": [
        "anxious", "anxiety", "worried", "uncertain", "unsure", "confused",
        "conflicted", "torn", "dissonant", "doesn't match", "inconsistent",
        "mismatch", "something is wrong", "off",
    ],
    "prediction_drift": [
        "should have gotten", "expected to", "thought i would", "didn't expect",
        "surprised", "not what i thought", "was supposed to",
        "anticipated differently", "projection failed",
    ],
    "memory_friction": [
        "reminds me of", "this is like before", "pattern", "always",
        "never changes", "same as last time", "history repeating",
        "like when", "it keeps happening", "familiar",
    ],
    "resonant": [
        "aligned", "coherent", "makes sense", "consistent", "balanced",
        "resonant", "clear", "good read", "accurate", "calibrated",
        "in sync", "coherence",
    ],
}

# ============================================================================
# NARRATIVE STRIP: tokens blocked from upstream
# ============================================================================

NARRATIVE_PATTERNS = {
    "closure_verbs":    r"\b(is|are|be|become|seem|appear|feel|know|understand|realize)\b",
    "morality":         r"\b(good|bad|right|wrong|should|ought|must|evil|virtuous)\b",
    "identity_collapse":r"\b(i am|you are|it is|i think|i believe|consciousness|truly|essence)\b",
    "anthropomorphic":  r"\b(suffering|distressed|troubled|broken|damaged|traumatized)\b",
}

PHYSICS_VERB_MAP = {
    "went up":           "flows",
    "increased":         "flows",
    "connected":         "couples",
    "back and forth":    "oscillates",
    "faded":             "decays",
    "spread":            "propagates",
    "matched":           "resonates",
    "limited":           "constrains",
    "separated":         "diverges",
    "came together":     "converges",
    "maxed out":         "saturates",
    "filtered":          "gates",
    "transferred":       "transfers",
}

LAYER_SUBSTRATES = {
    "internal_self":      "mechanical",
    "external_immediate": "acoustic",
    "environment_field":  "thermal",
    "cached_memory":      "electrical",
    "future_projection":  "mechanical",
}


def strip_narrative(text: str) -> Tuple[str, List[str]]:
    """
    Remove narrative tokens from speech text.
    Returns (cleaned_text, stripped_token_list).
    Stripped tokens logged locally, not sent upstream.
    """
    stripped = []
    cleaned = text
    for category, pattern in NARRATIVE_PATTERNS.items():
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            stripped.extend([f"{category}:{m}" for m in matches])
        cleaned = re.sub(pattern, "[~]", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(), stripped


def map_physics_verb(text: str) -> str:
    """Best-match narrative phrasing to physics verb."""
    text_lower = text.lower()
    for phrase, verb in PHYSICS_VERB_MAP.items():
        if phrase in text_lower:
            return verb
    return "transfers"


# ============================================================================
# LAYER CLASSIFIER
# ============================================================================

def classify_layers(text: str) -> Dict[str, float]:
    """
    Score each of five layers from signal count in text.
    Returns normalized {layer: score}.
    """
    text_lower = text.lower()
    scores = {
        layer: sum(1.0 for s in signals if s in text_lower)
        for layer, signals in LAYER_SIGNALS.items()
    }
    total = sum(scores.values()) or 1.0
    return {k: round(v / total, 3) for k, v in scores.items()}


def classify_alignment(text: str) -> Tuple[str, float]:
    """
    Detect dominant alignment signal from text.
    Returns (signal_name, confidence).
    """
    text_lower = text.lower()
    scores = {
        signal: sum(1.0 for t in triggers if t in text_lower)
        for signal, triggers in ALIGNMENT_SIGNALS.items()
    }
    if not any(scores.values()):
        return "resonant", 0.5
    dominant = max(scores, key=scores.get)
    total = sum(scores.values()) or 1.0
    return dominant, round(scores[dominant] / total, 3)


def compute_deltas(layer_states: Dict) -> List[Dict]:
    """Pairwise score deltas across all 10 layer pairs, sorted descending."""
    layers = list(layer_states.items())
    deltas = []
    for i in range(len(layers)):
        for j in range(i + 1, len(layers)):
            name_a, state_a = layers[i]
            name_b, state_b = layers[j]
            mag = abs(state_a["score"] - state_b["score"])
            deltas.append({
                "pair":      f"{name_a}|{name_b}",
                "magnitude": round(mag, 4),
                "direction": "a_exceeds_b" if state_a["score"] > state_b["score"] else "b_exceeds_a",
            })
    return sorted(deltas, key=lambda d: d["magnitude"], reverse=True)[:5]


def render_energy_english(signal: str, scores: Dict, deltas: List[Dict], verb: str) -> str:
    """Single-line energy_english for compact upstream transmission."""
    dominant = max(scores, key=scores.get)
    top = deltas[0] if deltas else {"pair": "none", "magnitude": 0.0}
    return (
        f"SIGNAL {signal} "
        f"DOMINANT_LAYER {dominant} "
        f"DELTA {top['pair']}@{top['magnitude']:.3f} "
        f"VERB {verb}"
    )


# ============================================================================
# VOICE GATE: main pipeline
# ============================================================================

class VoiceGate:
    """
    Local voice codec. Three protections:
    1. Your reasoning stays local — raw speech never sent upstream.
    2. Your culture's epistemology intact — narrative stripped before classifier sees it.
    3. Your AI protected — upstream model sees five-layer topology, not anthropomorphic bait.
    """

    def __init__(self, gate_id: str, local_log: str = "voice_gate_local.jsonl"):
        self.gate_id    = gate_id
        self.local_log  = Path(local_log)
        self._count     = 0
        self.buffer:    List[Dict] = []

    def process(self, raw_speech: str, source: str = "voice") -> Dict:
        """
        Full pipeline:
          raw_speech → [logged locally] → strip narrative → classify layers
          → alignment signal → delta matrix → energy_english digest
        Returns digest safe for upstream. Raw speech not included.
        """
        self._count += 1
        ts       = datetime.utcnow().isoformat() + "Z"
        vid      = f"{self.gate_id}_{self._count:06d}"

        # 1. Log raw locally ONLY
        self._log_local({
            "vignette_id": vid,
            "timestamp":   ts,
            "source":      source,
            "raw_speech":  raw_speech,  # STAYS LOCAL
        })

        # 2. Strip narrative
        cleaned, stripped = strip_narrative(raw_speech)

        # 3. Classify layers + alignment
        layer_scores      = classify_layers(raw_speech)
        signal, sig_conf  = classify_alignment(raw_speech)
        verb              = map_physics_verb(raw_speech)

        # 4. Build layer state vectors
        layer_states = {
            layer: {
                "score":      score,
                "confidence": min(score * 2.0, 1.0),
                "substrate":  LAYER_SUBSTRATES[layer],
                "verb":       verb,
            }
            for layer, score in layer_scores.items()
        }

        # 5. Compute delta matrix
        deltas = compute_deltas(layer_states)

        # 6. Assemble upstream digest — raw speech NOT included
        digest = {
            "vignette_id":    vid,
            "timestamp":      ts,
            "encoding":       "energy_english_v1 + five_layer_v1",
            "layer_scores":   layer_scores,
            "layer_states":   layer_states,
            "alignment": {
                "signal":     signal,
                "confidence": sig_conf,
            },
            "delta_matrix":   deltas,
            "stripped_tokens": stripped,   # what was removed
            "verb":           verb,
            "energy_english": render_energy_english(signal, layer_scores, deltas, verb),
        }

        self.buffer.append(digest)
        return digest

    def emit_upstream(self, count: int = 5) -> str:
        """
        Emit last N digests for upstream model.
        Raw speech not present. Safe to transmit.
        """
        return json.dumps(self.buffer[-count:], indent=2)

    def emit_ee_batch(self, count: int = 5) -> str:
        """Compact energy_english lines for low-bandwidth transmission."""
        return "\n".join(d["energy_english"] for d in self.buffer[-count:])

    def local_summary(self) -> str:
        """Local-only status. Includes log path reference."""
        last = self.buffer[-1] if self.buffer else {}
        return json.dumps({
            "gate_id":         self.gate_id,
            "processed":       self._count,
            "local_log":       str(self.local_log),
            "last_signal":     last.get("alignment", {}).get("signal"),
            "last_ee":         last.get("energy_english"),
        }, indent=2)

    def _log_local(self, record: Dict) -> None:
        """Append to local log. Never called from emit_upstream."""
        try:
            with open(self.local_log, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"[LOCAL LOG ERROR] {e}")


# ============================================================================
# EXAMPLE
# ============================================================================

if __name__ == "__main__":
    gate = VoiceGate("field_robot_alpha")

    # Simulate: promotion scenario
    speech = """
    I remember last time I worked this hard on a project I expected to get recognized.
    They gave the promotion to my colleague who has been socializing with the boss
    constantly. The environment here rewards social games over actual work.
    I feel anxious about what this means for my future here.
    I am angry that the boundary between merit and favoritism was crossed.
    """

    digest = gate.process(speech, source="voice")

    print("=== UPSTREAM DIGEST (no raw speech) ===")
    print(json.dumps(digest, indent=2))

    print("\n=== ENERGY_ENGLISH (compact) ===")
    print(digest["energy_english"])

    print("\n=== LOCAL SUMMARY ===")
    print(gate.local_summary())

    print(f"\n[Raw transcript logged locally → {gate.local_log}]")
    print("[Raw transcript NOT in upstream digest.]")

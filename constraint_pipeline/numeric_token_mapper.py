"""
numeric_token_mapper.py
CC0 - No rights reserved.

Assigns stable integer IDs to surface forms detected as constraint signals.
Builds a vocab of constraint tokens from input text.

Vocab entry: surface_form -> token_id, with associated boundary_type and frequency.
Token IDs are assigned in order of first appearance and persist across calls
if a vocab file is provided.

Output: token sequence (list of ints), vocab dict, CLAIM_TABLE.
"""

import json
import re
import sys
from dataclasses import dataclass, field


# Surface form patterns to recognize as constraint tokens
# Ordered: first match wins per position
TOKEN_PATTERNS = [
    (r"—|…|\.\.\.",                          "pause"),
    (r"\bwhilst\b|\bwherefore\b|\boft\b|\bhenceforth\b|\bthenceforth\b", "archaic"),
    (r"\bwhile\b|\bbecause\b|\bif\b|\bwhen\b|\bthough\b|\balthough\b|\bunless\b", "clause_sub"),
    (r"\band\b|\bbut\b|\bor\b|\bnor\b|\byet\b|\bso\b", "clause_coord"),
    (r"\b(we|they|it|I|you|he|she)'(re|ve|ll|d|s|m)\b", "contraction"),
    (r"\b\w+-\w+\b",                         "compound"),
    (r"\b(in|on|at|under|over|through|within|toward|towards|forward|back|out|up|down)\b", "prep"),
    (r"\b(go|goes|going|move|moves|moving|push|pushes|pushing)\s+(forward|back|in|out|up|down|through)\b", "spatial_resultant"),
    (r"\b(we|they|it|I|you|he|she)\s+are\b", "state_discrete"),
]

# Special tokens
PAD_ID   = 0
UNK_ID   = 1
START_ID = 2
END_ID   = 3

RESERVED = {
    "<PAD>":   PAD_ID,
    "<UNK>":   UNK_ID,
    "<START>": START_ID,
    "<END>":   END_ID,
}


@dataclass
class Vocab:
    token_to_id: dict = field(default_factory=lambda: dict(RESERVED))
    id_to_token: dict = field(default_factory=lambda: {v: k for k, v in RESERVED.items()})
    token_type: dict  = field(default_factory=dict)   # token_str -> boundary_type
    freq: dict        = field(default_factory=dict)   # token_str -> count
    next_id: int      = field(default_factory=lambda: len(RESERVED))

    def add(self, surface: str, btype: str) -> int:
        key = surface.lower().strip()
        if key not in self.token_to_id:
            self.token_to_id[key] = self.next_id
            self.id_to_token[self.next_id] = key
            self.token_type[key] = btype
            self.freq[key] = 0
            self.next_id += 1
        self.freq[key] = self.freq.get(key, 0) + 1
        return self.token_to_id[key]

    def get_id(self, surface: str) -> int:
        return self.token_to_id.get(surface.lower().strip(), UNK_ID)

    def size(self) -> int:
        return self.next_id

    def to_dict(self) -> dict:
        return {
            "token_to_id": self.token_to_id,
            "token_type":  self.token_type,
            "freq":        self.freq,
            "next_id":     self.next_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Vocab":
        v = cls()
        v.token_to_id = d["token_to_id"]
        v.id_to_token = {int(i): t for t, i in d["token_to_id"].items()}
        v.token_type  = d.get("token_type", {})
        v.freq        = d.get("freq", {})
        v.next_id     = d["next_id"]
        return v


def extract_tokens(text: str) -> list[tuple[str, str]]:
    """
    Scan text for constraint signal surface forms.
    Returns list of (surface_form, boundary_type) in position order.
    """
    hits = []
    covered = set()
    for pattern, btype in TOKEN_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            span = set(range(m.start(), m.end()))
            if span & covered:
                continue
            covered |= span
            hits.append((m.start(), m.group(0), btype))
    hits.sort(key=lambda h: h[0])
    return [(surface, btype) for _, surface, btype in hits]


def tokenize(text: str, vocab: Vocab = None) -> tuple[list[int], Vocab]:
    """
    Tokenize text into constraint token ID sequence.
    If vocab provided, extends it with new tokens.
    Returns (token_id_sequence, vocab).
    Sequence includes START and END markers.
    """
    if vocab is None:
        vocab = Vocab()

    tokens = extract_tokens(text)
    ids = [START_ID]
    for surface, btype in tokens:
        tid = vocab.add(surface, btype)
        ids.append(tid)
    ids.append(END_ID)
    return ids, vocab


def decode(ids: list[int], vocab: Vocab) -> list[str]:
    """Map token ID sequence back to surface forms."""
    return [vocab.id_to_token.get(i, "<UNK>") for i in ids]


def save_vocab(vocab: Vocab, path: str = "vocab.constraint.json") -> None:
    with open(path, "w") as f:
        json.dump(vocab.to_dict(), f, indent=2)
    print(f"[numeric_mapper] vocab size={vocab.size()} written to {path}")


def load_vocab(path: str = "vocab.constraint.json") -> Vocab:
    with open(path) as f:
        return Vocab.from_dict(json.load(f))


def to_claim_table(ids: list[int], vocab: Vocab,
                   source_id: str = "unnamed") -> dict:
    claims = []
    for pos, tid in enumerate(ids):
        surface = vocab.id_to_token.get(tid, "<UNK>")
        btype   = vocab.token_type.get(surface, "reserved")
        claims.append({
            "claim_id": f"{source_id}.numtok.{pos:04d}",
            "position": pos,
            "token_id": tid,
            "surface":  surface,
            "boundary_type": btype,
            "claim": f"Token {tid} at position {pos} encodes {btype} constraint signal",
            "falsification_condition": f"Find context where {surface!r} does not carry {btype} constraint",
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "sequence_length": len(ids),
        "vocab_size": vocab.size(),
        "claims": claims,
    }


def write_claim_table(ids: list[int], vocab: Vocab,
                      source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.numtok.json") -> None:
    table = to_claim_table(ids, vocab, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[numeric_mapper] {len(ids)} tokens written to {path}")


if __name__ == "__main__":
    sample = (
        "We are going forward — the car is forward-going, "
        "and oft the path shifts whilst the destination holds."
    )
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sample
    print(f"input: {text!r}\n")

    ids, vocab = tokenize(text)
    surfaces = decode(ids, vocab)

    print(f"token sequence ({len(ids)} tokens):")
    for i, (tid, surf) in enumerate(zip(ids, surfaces)):
        btype = vocab.token_type.get(surf, "reserved")
        print(f"  [{i:02d}] id={tid:<4} {surf:<20} type={btype}")

    print(f"\nvocab size: {vocab.size()}")

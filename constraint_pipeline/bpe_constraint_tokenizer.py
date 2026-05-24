"""
bpe_constraint_tokenizer.py
CC0 - No rights reserved.

Byte-Pair Encoding style tokenizer operating on constraint signal surface forms.
Requires a corpus (list of strings) to build merge rules from frequency analysis.

On single-sentence input, outputs character-level tokens - not useful.
Designed to be fed multiple inputs (e.g. transcripts, energy_english corpus)
to learn constraint-relevant subword merge rules.

Falsifiable claim: merge rules learned here correspond to constraint-bearing
subword units, not arbitrary character frequency patterns.
Falsification: find a high-frequency merge pair that carries no constraint signal.
"""

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class BPEVocab:
    token_to_id: dict = field(default_factory=dict)
    id_to_token: dict = field(default_factory=dict)
    merge_rules: list = field(default_factory=list)  # list of (a, b) -> ab
    freq: dict        = field(default_factory=dict)
    next_id: int      = 0

    def add_token(self, token: str) -> int:
        if token not in self.token_to_id:
            self.token_to_id[token] = self.next_id
            self.id_to_token[self.next_id] = token
            self.next_id += 1
        return self.token_to_id[token]

    def size(self) -> int:
        return self.next_id

    def to_dict(self) -> dict:
        return {
            "token_to_id": self.token_to_id,
            "merge_rules":  self.merge_rules,
            "freq":         self.freq,
            "next_id":      self.next_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BPEVocab":
        v = cls()
        v.token_to_id = d["token_to_id"]
        v.id_to_token = {int(i): t for t, i in d["token_to_id"].items()}
        v.merge_rules = [tuple(r) for r in d.get("merge_rules", [])]
        v.freq        = d.get("freq", {})
        v.next_id     = d["next_id"]
        return v


# --- Core BPE ---

def _word_to_chars(word: str) -> list[str]:
    """Split word into characters with end-of-word marker on last char."""
    chars = list(word)
    if chars:
        chars[-1] = chars[-1] + "</w>"
    return chars


def _get_pairs(vocab: Counter) -> Counter:
    """Count all adjacent symbol pairs across vocab."""
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return pairs


def _merge_pair(pair: tuple, vocab: Counter) -> Counter:
    """Apply one merge rule to entire vocab."""
    a, b = pair
    bigram = re.escape(f"{a} {b}")
    replacement = f"{a}{b}"
    new_vocab = Counter()
    for word, freq in vocab.items():
        new_word = re.sub(bigram, replacement, word)
        new_vocab[new_word] += freq
    return new_vocab


def build_bpe(corpus: list[str], num_merges: int = 50) -> BPEVocab:
    """
    Learn BPE merge rules from corpus.
    corpus: list of strings (sentences, transcripts, etc.)
    num_merges: number of merge operations to perform

    Returns BPEVocab with learned merge rules.
    """
    # Build initial word frequency count
    word_freq: Counter = Counter()
    for text in corpus:
        for word in text.lower().split():
            word = re.sub(r"[^a-z\-']", "", word)
            if word:
                word_freq[word] += 1

    # Initialize vocab: each word as space-separated chars
    bpe_vocab: Counter = Counter()
    for word, freq in word_freq.items():
        chars = _word_to_chars(word)
        bpe_vocab[" ".join(chars)] += freq

    vocab = BPEVocab()

    # Seed character-level tokens
    all_chars = set()
    for word in bpe_vocab:
        for sym in word.split():
            all_chars.add(sym)
    for ch in sorted(all_chars):
        vocab.add_token(ch)

    merge_rules = []
    for _ in range(num_merges):
        pairs = _get_pairs(bpe_vocab)
        if not pairs:
            break
        best_pair = max(pairs, key=pairs.get)
        best_freq = pairs[best_pair]
        if best_freq < 2:
            break  # no pair appears more than once - stop
        merged = f"{best_pair[0]}{best_pair[1]}"
        merge_rules.append((best_pair[0], best_pair[1], merged, int(best_freq)))
        vocab.add_token(merged)
        vocab.freq[merged] = int(best_freq)
        bpe_vocab = _merge_pair(best_pair, bpe_vocab)

    vocab.merge_rules = [(a, b, ab, freq) for a, b, ab, freq in merge_rules]
    return vocab


def encode(text: str, vocab: BPEVocab) -> list[int]:
    """
    Encode text using learned BPE merge rules.
    Returns list of token IDs. Unknown subwords -> UNK (-1).
    """
    ids = []
    for word in text.lower().split():
        word = re.sub(r"[^a-z\-']", "", word)
        if not word:
            continue
        symbols = list(_word_to_chars(word))
        # Apply merge rules in order
        for a, b, ab, _ in vocab.merge_rules:
            i = 0
            new_syms = []
            while i < len(symbols):
                if i < len(symbols) - 1 and symbols[i] == a and symbols[i+1] == b:
                    new_syms.append(ab)
                    i += 2
                else:
                    new_syms.append(symbols[i])
                    i += 1
            symbols = new_syms
        for sym in symbols:
            ids.append(vocab.token_to_id.get(sym, -1))
    return ids


def decode(ids: list[int], vocab: BPEVocab) -> str:
    """Decode token ID sequence back to approximate surface form."""
    tokens = [vocab.id_to_token.get(i, "<UNK>") for i in ids if i >= 0]
    text = "".join(tokens).replace("</w>", " ").strip()
    return text


def save_vocab(vocab: BPEVocab, path: str = "vocab.bpe.json") -> None:
    with open(path, "w") as f:
        json.dump(vocab.to_dict(), f, indent=2)
    print(f"[bpe] vocab size={vocab.size()} merges={len(vocab.merge_rules)} written to {path}")


def load_vocab(path: str = "vocab.bpe.json") -> BPEVocab:
    with open(path) as f:
        return BPEVocab.from_dict(json.load(f))


def to_claim_table(vocab: BPEVocab, source_id: str = "unnamed") -> dict:
    claims = []
    for i, (a, b, ab, freq) in enumerate(vocab.merge_rules):
        claims.append({
            "claim_id": f"{source_id}.bpe.{i:04d}",
            "merge_pair": [a, b],
            "merged_token": ab,
            "frequency": freq,
            "claim": f"Pair ({a!r}, {b!r}) co-occurs {freq}x - merged to {ab!r}",
            "falsification_condition": f"Find corpus where ({a!r}, {b!r}) high-frequency merge carries no constraint signal",
            "status": "OPEN",
        })
    return {
        "source_id": source_id,
        "vocab_size": vocab.size(),
        "merge_count": len(vocab.merge_rules),
        "claims": claims,
    }


def write_claim_table(vocab: BPEVocab, source_id: str = "unnamed",
                      path: str = "CLAIM_TABLE.bpe.json") -> None:
    table = to_claim_table(vocab, source_id)
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[bpe] {len(vocab.merge_rules)} merge rules written to {path}")


if __name__ == "__main__":
    # Minimal corpus demo - feed more text for useful merge rules
    corpus = [
        "We are going forward - the car is forward-going, and oft the path shifts whilst the destination holds.",
        "Oft the constraint geometry shifts whilst the narrative holds.",
        "We are going forward and the system is forward-looking.",
        "The car is forward-going whilst the path is oft-shifting.",
        "Going forward we are constraint-primary and oft we are forward-looking.",
        "Whilst the narrative collapses the constraint holds forward-going.",
        "We are oft misread whilst going forward into constraint space.",
    ]

    if len(sys.argv) > 1 and sys.argv[1] != "--demo":
        # Read corpus from file if provided
        with open(sys.argv[1]) as f:
            corpus = [line.strip() for line in f if line.strip()]

    print(f"[bpe] corpus: {len(corpus)} sentences\n")
    vocab = build_bpe(corpus, num_merges=30)

    print(f"vocab size: {vocab.size()}")
    print(f"merge rules learned: {len(vocab.merge_rules)}\n")

    print("top 10 merge rules:")
    for a, b, ab, freq in vocab.merge_rules[:10]:
        print(f"  ({a!r} + {b!r}) -> {ab!r}  freq={freq}")

    print()
    test = "going forward whilst the constraint holds"
    ids = encode(test, vocab)
    recovered = decode(ids, vocab)
    print(f"encode: {test!r}")
    print(f"ids:    {ids}")
    print(f"decode: {recovered!r}")

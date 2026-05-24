"""
pipeline_runner.py
CC0 - No rights reserved.

Chains all four tokenizers with grammatical_constraint_encoder and
token_constraint_validator against the same input.

Outputs:
- unified_signal_table.json  (full structured output)
- unified_signal_table.tsv   (flat numeric rows)
- CLAIM_TABLE.pipeline.json  (falsifiable claims from all modules)

Modules required in same directory:
- constraint_tokenizer.py
- numeric_token_mapper.py
- bpe_constraint_tokenizer.py
- voice_tokenizer.py
- grammatical_constraint_encoder.py
- token_constraint_validator.py

Usage:
    python pipeline_runner.py "your text here"
    python pipeline_runner.py --file corpus.txt
    python pipeline_runner.py  # runs built-in sample
"""

import json
import sys
import os

# --- Module imports ---

def _import_modules():
    missing = []
    mods = {}
    pairs = [
        ("constraint_tokenizer",       "constraint_tokenizer"),
        ("numeric_token_mapper",       "numeric_token_mapper"),
        ("bpe_constraint_tokenizer",   "bpe_constraint_tokenizer"),
        ("voice_tokenizer",            "voice_tokenizer"),
        ("grammatical_constraint_encoder", "grammatical_constraint_encoder"),
        ("token_constraint_validator", "token_constraint_validator"),
    ]
    for key, modname in pairs:
        try:
            mods[key] = __import__(modname)
        except ImportError:
            missing.append(modname)
    return mods, missing

MODS, MISSING = _import_modules()
if MISSING:
    print(f"[pipeline] missing modules: {MISSING}")
    print("[pipeline] run from directory containing all six .py files")
    sys.exit(1)


# --- Per-module runners ---

def run_constraint_tokenizer(text: str, source_id: str) -> dict:
    m = MODS["constraint_tokenizer"]
    tokens = m.tokenize(text)
    return {
        "module": "constraint_tokenizer",
        "token_count": len(tokens),
        "tokens": [
            {
                "index": t.index,
                "span": [t.start, t.end],
                "text": t.text,
                "boundary_type": t.boundary_type.value,
                "confidence": t.confidence,
            }
            for t in tokens
        ],
        "claim_table": m.to_claim_table(tokens, source_id),
    }


def run_numeric_mapper(text: str, source_id: str) -> dict:
    m = MODS["numeric_token_mapper"]
    ids, vocab = m.tokenize(text)
    surfaces = m.decode(ids, vocab)
    return {
        "module": "numeric_token_mapper",
        "sequence_length": len(ids),
        "vocab_size": vocab.size(),
        "sequence": [
            {
                "pos": i,
                "token_id": tid,
                "surface": surf,
                "type": vocab.token_type.get(surf, "reserved"),
            }
            for i, (tid, surf) in enumerate(zip(ids, surfaces))
        ],
        "claim_table": m.to_claim_table(ids, vocab, source_id),
    }


def run_bpe(corpus: list[str], text: str, source_id: str,
            num_merges: int = 30) -> dict:
    m = MODS["bpe_constraint_tokenizer"]
    vocab = m.build_bpe(corpus, num_merges=num_merges)
    ids = m.encode(text, vocab)
    decoded = m.decode(ids, vocab)
    return {
        "module": "bpe_constraint_tokenizer",
        "vocab_size": vocab.size(),
        "merge_count": len(vocab.merge_rules),
        "encoded_length": len(ids),
        "token_ids": ids,
        "decoded": decoded,
        "top_merges": [
            {"pair": [a, b], "merged": ab, "freq": freq}
            for a, b, ab, freq in vocab.merge_rules[:10]
        ],
        "claim_table": m.to_claim_table(vocab, source_id),
    }


def run_voice_tokenizer(text: str, source_id: str) -> dict:
    m = MODS["voice_tokenizer"]
    tokens = m.tokenize(text)
    clean = m.strip_fillers(tokens)
    anchors = m.filter_by_type(
        tokens,
        m.ProsodicType.CONSTRAINT_ANCHOR,
        m.ProsodicType.PAUSE_UNFILLED,
        m.ProsodicType.SELF_CORRECTION,
    )
    return {
        "module": "voice_tokenizer",
        "token_count": len(tokens),
        "boundary_count": sum(1 for t in tokens if t.prosodic_type != m.ProsodicType.SEGMENT),
        "stripped_text": m.to_text(clean),
        "constraint_anchors": [
            {"type": t.prosodic_type.value, "text": t.text}
            for t in anchors
        ],
        "tokens": [
            {
                "index": t.index,
                "span": [t.start, t.end],
                "text": t.text,
                "prosodic_type": t.prosodic_type.value,
                "confidence": t.confidence,
            }
            for t in tokens
        ],
        "claim_table": m.to_claim_table(tokens, source_id),
    }


def run_encoder(text: str, source_id: str) -> dict:
    m = MODS["grammatical_constraint_encoder"]
    table = m.encode_to_claim_table(text, source_id)
    numeric = m.encode_numeric(text)
    hybrid = m.encode_numeric_hybrid(text)
    return {
        "module": "grammatical_constraint_encoder",
        "signal_count": table["signal_count"],
        "claim_table": table,
        "numeric_rows": numeric,
        "hybrid": hybrid,
    }


def run_validator(text: str, threshold: float = 1.5) -> dict:
    m = MODS["token_constraint_validator"]
    result = m.validate(text, rejection_threshold=threshold)
    return {
        "module": "token_constraint_validator",
        "passes": result.passes,
        "severity_sum": result.severity_sum,
        "rejection_threshold": result.rejection_threshold,
        "violation_count": len(result.violations),
        "violations": [
            {
                "type": v.violation_type.value,
                "matched": v.matched_text,
                "severity": v.severity,
            }
            for v in result.violations
        ],
    }


# --- Unified signal table builder ---

def build_signal_table(text: str, source_id: str = "pipeline",
                       corpus: list[str] = None,
                       validator_threshold: float = 1.5) -> dict:
    """
    Run all six modules against text.
    Returns unified signal table dict.
    """
    if corpus is None:
        corpus = [text]

    print(f"[pipeline] running 6 modules on {len(text)} chars...", flush=True)

    ct  = run_constraint_tokenizer(text, source_id)
    nm  = run_numeric_mapper(text, source_id)
    bpe = run_bpe(corpus, text, source_id)
    vt  = run_voice_tokenizer(text, source_id)
    enc = run_encoder(text, source_id)
    val = run_validator(text, validator_threshold)

    # Signal density: constraint signals per 100 chars
    total_signals = (
        ct["token_count"] +
        enc["signal_count"] +
        vt["boundary_count"]
    )
    signal_density = round(total_signals / max(len(text), 1) * 100, 2)

    return {
        "source_id": source_id,
        "input_length": len(text),
        "signal_density_per_100chars": signal_density,
        "validator": val,
        "modules": {
            "constraint_tokenizer": ct,
            "numeric_token_mapper": nm,
            "bpe": bpe,
            "voice_tokenizer": vt,
            "encoder": enc,
        },
    }


# --- TSV flat export ---

def to_tsv(table: dict) -> str:
    """
    Flatten unified signal table to TSV.
    One row per signal across all modules.
    Columns: module, signal_type, text, confidence, span_start, span_end, token_id
    """
    rows = ["module\tsignal_type\ttext\tconfidence\tspan_start\tspan_end\ttoken_id"]

    # constraint_tokenizer
    for t in table["modules"]["constraint_tokenizer"]["tokens"]:
        rows.append(
            f"constraint_tokenizer\t{t['boundary_type']}\t{t['text']}\t"
            f"{t['confidence']}\t{t['span'][0]}\t{t['span'][1]}\t"
        )

    # numeric_token_mapper
    for s in table["modules"]["numeric_token_mapper"]["sequence"]:
        rows.append(
            f"numeric_mapper\t{s['type']}\t{s['surface']}\t\t\t\t{s['token_id']}"
        )

    # bpe top merges
    for mr in table["modules"]["bpe"]["top_merges"]:
        rows.append(
            f"bpe\tmerge\t{mr['merged']}\t\t\t\t"
        )

    # voice_tokenizer
    for t in table["modules"]["voice_tokenizer"]["tokens"]:
        rows.append(
            f"voice_tokenizer\t{t['prosodic_type']}\t{t['text']}\t"
            f"{t['confidence']}\t{t['span'][0]}\t{t['span'][1]}\t"
        )

    # encoder hybrid
    for h in table["modules"]["encoder"]["hybrid"]:
        parts = h.split()
        rows.append(
            f"encoder\t{parts[1] if len(parts)>1 else ''}\t{h}\t"
            f"{parts[2] if len(parts)>2 else ''}\t\t\t{parts[0] if parts else ''}"
        )

    # validator violations
    for v in table["validator"]["violations"]:
        rows.append(
            f"validator\t{v['type']}\t{v['matched']}\t{v['severity']}\t\t\t"
        )

    return "\n".join(rows)


# --- Merged claim table ---

def merge_claim_tables(table: dict) -> dict:
    """Collect all claims from all modules into one CLAIM_TABLE."""
    all_claims = []
    for mod_key, mod_data in table["modules"].items():
        if "claim_table" in mod_data:
            all_claims.extend(mod_data["claim_table"].get("claims", []))
    return {
        "source_id": table["source_id"],
        "total_claims": len(all_claims),
        "claims": all_claims,
    }


# --- Writers ---

def write_all(table: dict,
              json_path: str = "unified_signal_table.json",
              tsv_path: str = "unified_signal_table.tsv",
              claim_path: str = "CLAIM_TABLE.pipeline.json") -> None:
    with open(json_path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[pipeline] JSON -> {json_path}")

    tsv = to_tsv(table)
    with open(tsv_path, "w") as f:
        f.write(tsv)
    print(f"[pipeline] TSV  -> {tsv_path}")

    merged = merge_claim_tables(table)
    with open(claim_path, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"[pipeline] CLAIM_TABLE -> {claim_path} ({merged['total_claims']} claims)")


# --- CLI ---

if __name__ == "__main__":
    sample = (
        "So um — we are going forward, and I think, or rather I know, "
        "that oft the constraint shifts whilst the narrative holds. "
        "Actually no — the car is forward-going, basically."
    )

    corpus = None
    text = sample

    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                lines = [l.strip() for l in f if l.strip()]
            corpus = lines
            text = " ".join(lines)
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        text = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))

    source_id = "cli"
    table = build_signal_table(text, source_id=source_id, corpus=corpus or [text])

    # Console summary
    print(f"\n[pipeline] input length:    {table['input_length']} chars")
    print(f"[pipeline] signal density:  {table['signal_density_per_100chars']} per 100 chars")
    print(f"[pipeline] validator:       {'PASS' if table['validator']['passes'] else 'FAIL'} "
          f"severity={table['validator']['severity_sum']}")
    print(f"[pipeline] CBU tokens:      {table['modules']['constraint_tokenizer']['token_count']}")
    print(f"[pipeline] numeric tokens:  {table['modules']['numeric_token_mapper']['sequence_length']}")
    print(f"[pipeline] BPE vocab:       {table['modules']['bpe']['vocab_size']}")
    print(f"[pipeline] voice tokens:    {table['modules']['voice_tokenizer']['token_count']}")
    print(f"[pipeline] encoder signals: {table['modules']['encoder']['signal_count']}")

    write_all(table)

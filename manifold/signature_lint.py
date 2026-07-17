#!/usr/bin/env python3
"""
signature_lint.py

Static detector for the codegen failure signature. Runs before you spend
attention on a module.

Sits next to run_all.py. That tool answers "does it run." This one answers
"is it shaped like a verdict machine." Both are deliberately dumb.

CLAIM (C-lint-1)
  The failure signature in AI-generated audit modules is dominated by
  statically-detectable defects: parameters carried but never used,
  imports gestured at and dropped, missing refutation scaffolding,
  moral labels in returns, and absent UNKNOWN/NOT_APPLICABLE paths.

SCOPE
  Python source, stdlib `ast`. Detects STRUCTURE, not correctness.

REFUTATION
  (R1) If a module passes clean and is still rotten, the signature is not
       statically dominated and C-lint-1 is refuted. Log the specimen.
  (R2) If a module fails every check and is nonetheless correct, the checks
       are measuring style, not rot. Same action: update the claim.

UNKNOWNS
  - Threshold between WARN and FAIL is a convention, not a measurement.
  - Calibration row detection is a keyword proxy. Weak. Flagged as such.

WHAT THIS CANNOT CATCH (needs execution + a sweep, not a parser):
  - sign errors      (gamma in the numerator raising a stability score)
  - shadowed formulas (a guard firing first and discarding a computed value)
  - frame mismatch   (linear arithmetic under a multiplicative claim)
  Those three were the LOAD-BEARING defects in both specimens.
  This tool is the cheap 60%. It does not replace running the thing.

Usage:
    python3 signature_lint.py *.py
    python3 signature_lint.py --root .

stdlib only. CC0.
"""

from __future__ import annotations

import argparse
import ast
import glob
import os
import sys

REQUIRED_DOC_SECTIONS = ("CLAIM", "SCOPE", "REFUTATION", "UNKNOWNS")

MORAL_LABELS = (
    "FALSE NARRATIVE", "STANDING", "ENGAGE", "DISENGAGE",
    "SOVEREIGN", "COLLAPSE PATH", "STABLE",
    "⚠", "✅", "❌",
)

DETERMINACY_TOKENS = ("UNKNOWN", "NOT_APPLICABLE", "INDETERMINATE", "OUT_OF_SCOPE")

CALIBRATION_TOKENS = ("literature", "known", "reference", "target", "expected")


def _loaded_names(node) -> set:
    return {n.id for n in ast.walk(node)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def _attr_roots(node) -> set:
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute):
            v = n.value
            while isinstance(v, ast.Attribute):
                v = v.value
            if isinstance(v, ast.Name):
                out.add(v.id)
    return out


def check_dead_params(tree) -> list:
    """Parameters in a signature that never appear in the body."""
    hits = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = fn.args
        names = [x.arg for x in (a.posonlyargs + a.args + a.kwonlyargs)]
        if a.vararg:
            names.append(a.vararg.arg)
        if a.kwarg:
            names.append(a.kwarg.arg)
        used = _loaded_names(fn) | _attr_roots(fn)
        # attribute writes count as use: self.x = claim
        for n in ast.walk(fn):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                used.add(n.id)
        for p in names:
            if p in ("self", "cls"):
                continue
            if p not in used:
                hits.append(f"{fn.name}(): parameter '{p}' never read")
    return hits


def check_passthrough_params(tree) -> list:
    """Parameters used ONLY to be echoed into a returned dict/structure.

    The `claim` argument in refutation_protocol.py: read once, stuffed into
    the output, never touched by the arithmetic. Reads as coupled. Is not.
    """
    hits = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = fn.args
        names = [x.arg for x in (a.posonlyargs + a.args + a.kwonlyargs)]
        for p in names:
            if p in ("self", "cls"):
                continue
            reads = [n for n in ast.walk(fn)
                     if isinstance(n, ast.Name)
                     and n.id == p and isinstance(n.ctx, ast.Load)]
            if not reads:
                continue
            # is it read anywhere OUTSIDE a Dict/Return/fstring?
            operative = False
            for n in ast.walk(fn):
                if isinstance(n, (ast.BinOp, ast.Compare, ast.BoolOp, ast.UnaryOp)):
                    if p in _loaded_names(n):
                        operative = True
            if not operative:
                hits.append(f"{fn.name}(): '{p}' echoed to output, "
                            f"never enters arithmetic")
    return hits


def check_unused_imports(tree) -> list:
    imported = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for al in n.names:
                imported[(al.asname or al.name).split(".")[0]] = al.name
        elif isinstance(n, ast.ImportFrom):
            if n.module == "__future__":
                continue
            for al in n.names:
                imported[al.asname or al.name] = al.name
    used = _loaded_names(tree) | _attr_roots(tree)
    return [f"import '{v}' never used  (a formula was gestured at, then dropped)"
            for k, v in imported.items() if k not in used]


def check_dead_locals(tree) -> list:
    """Assigned, never read. Catches a computed score that gets discarded."""
    hits = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stored, loaded = set(), set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Name):
                (stored if isinstance(n.ctx, ast.Store) else loaded).add(n.id)
        for v in sorted(stored - loaded):
            if v.startswith("_"):
                continue
            hits.append(f"{fn.name}(): local '{v}' assigned, never read")
    return hits


def check_doc_sections(tree) -> list:
    doc = ast.get_docstring(tree) or ""
    missing = [s for s in REQUIRED_DOC_SECTIONS if s not in doc]
    if not missing:
        return []
    return [f"module docstring missing: {', '.join(missing)}"]


def _string_literals(tree) -> list:
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def check_moral_labels(tree) -> list:
    hits = []
    for s in _string_literals(tree):
        for lab in MORAL_LABELS:
            if lab in s:
                hits.append(f"moral label in literal: {lab!r}")
                break
    return sorted(set(hits))


def check_determinacy_path(tree) -> list:
    blob = " ".join(_string_literals(tree))
    if any(t in blob for t in DETERMINACY_TOKENS):
        return []
    return ["no UNKNOWN / NOT_APPLICABLE return path "
            "(module emits a verdict for every input)"]


def check_calibration(tree) -> list:
    blob = " ".join(_string_literals(tree)).lower()
    if any(t in blob for t in CALIBRATION_TOKENS):
        return []
    return ["no calibration row detected (keyword proxy - WEAK, may be a "
            "false positive; see UNKNOWNS)"]


CHECKS = [
    ("dead_param", check_dead_params, "FAIL"),
    ("passthrough_param", check_passthrough_params, "WARN"),
    ("unused_import", check_unused_imports, "WARN"),
    ("dead_local", check_dead_locals, "WARN"),
    ("no_claim_block", check_doc_sections, "FAIL"),
    ("moral_label", check_moral_labels, "FAIL"),
    ("no_determinacy", check_determinacy_path, "FAIL"),
    ("no_calibration", check_calibration, "WARN"),
]


def lint(path: str) -> dict:
    with open(path) as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        return {"module": os.path.basename(path), "verdict": "PARSE_ERROR",
                "findings": [("syntax", "FAIL", [str(e)])]}
    findings = []
    for name, fn, sev in CHECKS:
        hits = fn(tree)
        if hits:
            findings.append((name, sev, hits))
    fails = sum(1 for _, s, _ in findings if s == "FAIL")
    warns = sum(1 for _, s, _ in findings if s == "WARN")
    verdict = "RED" if fails else ("YELLOW" if warns else "GREEN")
    return {"module": os.path.basename(path), "verdict": verdict,
            "fails": fails, "warns": warns, "findings": findings}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="*")
    p.add_argument("--root", default=None)
    p.add_argument("-q", "--quiet", action="store_true",
                   help="one line per module")
    a = p.parse_args(argv)
    paths = list(a.paths)
    if a.root:
        paths += sorted(glob.glob(os.path.join(a.root, "*.py")))
    paths = [x for x in paths if os.path.basename(x) != "signature_lint.py"]
    if not paths:
        p.error("no paths")

    print("=" * 72)
    print("signature_lint — static detection of the codegen failure signature")
    print("=" * 72)
    worst = 0
    for path in paths:
        r = lint(path)
        print(f"\n{r['module']:<34} {r['verdict']}"
              f"  ({r.get('fails',0)} fail, {r.get('warns',0)} warn)")
        if not a.quiet:
            for name, sev, hits in r["findings"]:
                for h in hits[:6]:
                    print(f"    [{sev}] {name:<18} {h}")
                if len(hits) > 6:
                    print(f"    [{sev}] {name:<18} ... +{len(hits)-6} more")
        worst = max(worst, r.get("fails", 0))
    print("\n" + "=" * 72)
    print("cannot catch: sign errors, shadowed formulas, frame mismatch.")
    print("those need execution + a parameter sweep. this is the cheap 60%.")
    print("=" * 72)
    return min(worst, 255)


if __name__ == "__main__":
    sys.exit(main())

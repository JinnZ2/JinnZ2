#!/usr/bin/env python3
"""
audit.py -- corpus_prior_audit readout. CC0, stdlib only, python >= 3.8.
Co-authored (JinnZ2 + Claude), 2026-11-08.

Reads text (a file or stdin) and lists every registry entry whose trigger
phrase appears in it (case-insensitive, whole-word). Per hit: id, matched
phrase, weld, check question.

A hit is a prompt to check, never a finding that the text is wrong.
No score. Exit 0 whether or not anything matched.

Usage:
  python3 audit.py FILE
  echo "inventory is fine" | python3 audit.py
  python3 audit.py FILE --json
  python3 audit.py --registry other.json FILE
  python3 audit.py --selftest
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(HERE, "registry.json")
README = os.path.join(HERE, "README.md")

TAGS = ("MEASURED", "DERIVED", "PROPOSED", "UNMEASURED")
FIELDS = ("id", "claim_as_found", "trigger_phrases", "weld", "dropped",
          "scope_tested", "check_question", "example_case", "status", "sources")
RULE = "a hit is a prompt to check, never a finding that the text is wrong"


def load(path=DEFAULT_REGISTRY):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


def problems(entries):
    """Shape check. Returns a list of strings; empty means every entry is complete."""
    out, seen = [], set()
    for i, e in enumerate(entries):
        tag = e.get("id", "#%d" % i)
        for k in FIELDS:
            if k not in e or e[k] in ("", [], {}, None):
                out.append("%s: missing %s" % (tag, k))
        if tag in seen:
            out.append("%s: duplicate id" % tag)
        seen.add(tag)
        w = e.get("weld") or {}
        if not w.get("measurand_a") or not w.get("measurand_b"):
            out.append("%s: weld needs measurand_a and measurand_b" % tag)
        st = e.get("status") or {}
        if not isinstance(st, dict):
            out.append("%s: status must map part -> tag" % tag)
        else:
            for part, t in st.items():
                if t not in TAGS:
                    out.append("%s: status %r for %r not in %s" % (tag, t, part, TAGS))
        if not isinstance(e.get("trigger_phrases"), list):
            out.append("%s: trigger_phrases must be a list" % tag)
    return out


def _pattern(phrase):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])",
                      re.IGNORECASE)


def scan(text, entries):
    """One hit per (entry, phrase) found. Order: registry order, then phrase order."""
    hits = []
    for e in entries:
        for p in e["trigger_phrases"]:
            m = _pattern(p).search(text)
            if m:
                hits.append({"id": e["id"], "matched": m.group(0), "phrase": p,
                             "weld": e["weld"], "check_question": e["check_question"]})
    return hits


def render(hits):
    if not hits:
        return "no trigger phrases found (absence of a hit says nothing about the text)"
    lines = ["%d hit(s). Each is a prompt to check, not a finding." % len(hits), ""]
    for h in hits:
        lines.append("%s  matched: %r" % (h["id"], h["matched"]))
        lines.append("    weld:  %s  |  %s" % (h["weld"]["measurand_a"], h["weld"]["measurand_b"]))
        lines.append("    check: %s" % h["check_question"])
    return "\n".join(lines)


def selftest():
    ok, total = 0, 0

    def check(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL:", label)

    entries = load()
    check(problems(entries) == [], "every entry has all fields: %s" % problems(entries))
    check(len(entries) >= 14, "seed entries present")
    bad = [dict(entries[0], id="X", check_question="")]
    check(any("check_question" in p for p in problems(bad)), "missing field refused")
    bad = [dict(entries[0], id="X", status={"a": "TRUE"})]
    check(any("not in" in p for p in problems(bad)), "unknown status tag refused")

    hits = scan("Distillate INVENTORY looks fine.", entries)
    check([h["id"] for h in hits] == ["W04"], "trigger match, case-insensitive")
    check(hits[0]["matched"] == "INVENTORY", "matched text kept as found")
    hits = scan("They say war drives innovation.", entries)
    check({"W01", "W02"} <= {h["id"] for h in hits}, "multi-entry match")
    check(scan("The software toward the hardware.", entries) == [],
          "no hit inside other words (war in software / toward)")
    check(scan("The goldfinch sat on the fence post.", entries) == [], "no-hit text returns empty")

    with open(README, encoding="utf-8") as f:
        check(RULE in f.read(), "README contains the RULE line")

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    reg, as_json, path, i = DEFAULT_REGISTRY, False, None, 0
    while i < len(argv):
        a = argv[i]
        if a == "--registry":
            reg = argv[i + 1]; i += 2; continue
        if a == "--json":
            as_json = True
        else:
            path = a
        i += 1
    entries = load(reg)
    if path:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    hits = scan(text, entries)
    print(json.dumps(hits, indent=2) if as_json else render(hits))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

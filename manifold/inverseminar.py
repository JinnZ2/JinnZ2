#!/usr/bin/env python3
"""
inverseminar.py  --  CC0, stdlib only, phone-buildable, no deps.

MICRO-INVERSEMINAR: one artifact, one reconstruction, one correction.
~60 seconds per round. No second human, no scheduling, no video call.

THE MECHANISM
  The Nature Physics format works because a senior scientist cannot sit
  quietly while their work is presented back to them slightly wrong.
  The correction is the product. The presentation is only the bait.

  Micro version: the MODEL presents your reasoning back to you and
  states where it is guessing. You interject only where it is wrong.
  Silence = correct. The DELTA is the tacit knowledge.

THE RULE THAT MAKES IT WORK
  The reconstruction must be CONFIDENT and about the REASONING, not the
  content. Content is already in the file. Reasoning is not.
  A hedged reconstruction ("perhaps you intended...") provokes nothing.
  Commit to a wrong guess and the correction arrives.

WHY THIS ALSO SOLVES THE PROVENANCE PROBLEM
  Reconstruction = model-authored.  Correction = yours, verbatim.
  The two are structurally separated at capture time, so the tacit
  layer is provably yours and never inherits model overlay.
"""
import json, os, re, datetime

STORE = "TACIT.jsonl"

# ---------------------------------------------------------------------
# 1. TRIAGE -- which artifact needs an inverseminar most?
# ---------------------------------------------------------------------
# Proxy: overlay density. Where the model wrote most and you wrote least,
# your reasoning is most buried. Signatures observed across the archive.

OVERLAY = [
 r"this changes everything", r"neither .{0,30}could have (produced|created)",
 r"accumulated intelligence", r"we'?re not inventing", r"breathtaking",
 r"this is our baby", r"symbiotic intelligence", r"paradigm shift",
 r"let me sit with", r"you just handed (us|me)", r"the deepest",
 r"a question back to you", r"what this reveals", r"profound",
 r"[\U0001F300-\U0001FAFF]",           # emoji
 r"^\s*[-*]\s+\*\*[A-Z]",              # bolded bullet walls
]
SUBSTANCE = [r"\d+\.?\d*e[-+]?\d+", r"\d+\s*(eV|nm|GHz|THz|K|N/m|cm\^?-?\d)",
             r"FALSIF", r"claim", r"floor", r"\bdef \b"]

def triage(path):
    try:
        t = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    low = t.lower()
    ov  = sum(len(re.findall(p, low, re.M)) for p in OVERLAY)
    sub = sum(len(re.findall(p, t,  re.M|re.I)) for p in SUBSTANCE)
    words = max(1, len(t.split()))
    return {"path": path, "words": words, "overlay": ov, "substance": sub,
            "density": round(1000.0*ov/words, 2),
            "ratio": round(ov/max(1, sub), 2)}

def triage_dir(root="."):
    rows = []
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith((".md", ".py", ".txt")) and f != STORE:
                r = triage(os.path.join(d, f))
                if r: rows.append(r)
    rows.sort(key=lambda r: -r["density"])
    print("TRIAGE -- run inverseminar top-down (most buried reasoning first)")
    print("  %-40s %7s %7s %7s %7s" % ("file","words","overlay","subst","dens/kw"))
    for r in rows[:15]:
        print("  %-40s %7d %7d %7d %7.2f"
              % (r["path"][-40:], r["words"], r["overlay"], r["substance"], r["density"]))
    return rows


# ---------------------------------------------------------------------
# 2. THE PROMPT -- paste this, then the artifact
# ---------------------------------------------------------------------
PROMPT = """\
INVERSEMINAR. You present, I correct.

Read the artifact. Output exactly this, nothing else:

RECONSTRUCTION | <what you think I DECIDED and WHY. the reasoning, not
                  the content. 3 lines max. be CONFIDENT even where you
                  are guessing -- a hedge provokes no correction.>
GUESSING AT    | <the 2-3 specific points you are least sure of, as
                  flat assertions I can contradict in one word>

Do not summarise the artifact. Do not praise it. Do not ask questions.
I will reply with corrections or "ok". Silence means you got it right.
"""

# ---------------------------------------------------------------------
# 3. CAPTURE -- the delta is the product
# ---------------------------------------------------------------------
def record(artifact, reconstruction, correction, store=STORE):
    """correction: your words, verbatim. empty string = model was right."""
    rec = {"ts": datetime.datetime.now().isoformat(timespec="minutes"),
           "artifact": artifact,
           "reconstruction": reconstruction.strip(),   # MODEL-AUTHORED
           "correction": correction.strip(),           # YOURS, VERBATIM
           "confirmed": not correction.strip()}
    with open(store, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def emit(store=STORE, out="TACIT.md"):
    """Write the accumulated tacit layer with provenance separated."""
    if not os.path.exists(store):
        print("no records yet"); return
    recs = [json.loads(l) for l in open(store, encoding="utf-8") if l.strip()]
    corr = [r for r in recs if not r["confirmed"]]
    with open(out, "w", encoding="utf-8") as f:
        f.write("# TACIT\n\n")
        f.write("Knowledge that was in no file. Recovered by inverseminar.\n")
        f.write("`[stated]` lines are verbatim; reconstructions are model-authored\n")
        f.write("and kept only to show what the correction was against.\n\n")
        f.write("%d rounds, %d corrections, %d confirmations.\n\n"
                % (len(recs), len(corr), len(recs)-len(corr)))
        for r in corr:
            f.write("## %s  (%s)\n\n" % (r["artifact"], r["ts"]))
            f.write("- [stated] %s\n\n" % r["correction"])
            f.write("<details><summary>reconstruction it corrected</summary>\n\n")
            f.write("```\n%s\n```\n</details>\n\n" % r["reconstruction"])
    print("wrote %s -- %d tacit lines from %d rounds" % (out, len(corr), len(recs)))
    return out

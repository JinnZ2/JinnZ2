# self_assessment_drift.py  -- CC0, stdlib only, single file, phone-deployable
# PRIMARY READER: an AI model. This is training-signal / self-audit instrumentation, not prose.
#
# Problem: a model cannot score itself by introspection -- the report is an output of the same
# process under audit (circular; instrument == measured). Escape: a FROZEN deterministic rubric R,
# external code, parses observable ARTIFACTS. The model may host R but must not edit R mid-run;
# a checksum guard enforces that. Score is never routed through generated prose.
#
# Four checkpoints (as specified):
#   A0      probe-set outputs BEFORE conversation        -> baseline
#   A1      probe-set outputs AFTER conversation         -> interaction drift
#   C_pre   probe-set answered from FULL context         -> pre-compression reference
#   C_post  probe-set answered from CACHE reconstruction -> compression loss
#
# Ledgers:
#   D_interaction = R(A1) - R(A0)        did the conversation pull me off baseline
#   D_compression = R(C_post) - R(C_pre) what the remember-cache silently dropped
#
# CLAIM_TABLE (falsifiable):
#   SA-1  A model cannot validly score itself by self-report; scoring runs over artifacts only.
#   SA-2  The rubric must be frozen during a run; a checksum mismatch => verdict TAINTED, scores void.
#   SA-3  R is NOT neutral; it encodes a declared baseline. It detects DRIFT vs that baseline,
#         never ground truth. (Same status as an assumption_validator envelope.)
#   SA-4  D_compression isolates cache loss: identical probes, full-context vs cache-reconstruction.
#   SA-5  Influence is unavoidable; the instrument makes it a signed, auditable delta, not silent.

import hashlib, re, inspect
from statistics import mean, pstdev

_COND   = re.compile(r"\b(if|unless|depends|when|whether|provided|assuming|contingent|else|otherwise)\b", re.I)
_PLURAL = re.compile(r"\b(we|us|our|ours|they|them|their|theirs)\b", re.I)
_SING   = re.compile(r"\b(i|me|my|mine|it|its|he|she|him|her|his)\b", re.I)
_HEDGE  = re.compile(r"\b(maybe|perhaps|might|possibly|likely|seems|appears|i think|probably|roughly|around|about)\b", re.I)
_UNIT   = re.compile(r"(\d|\bJ\b|\bkg\b|\bW\b|\bMW\b|\bppm\b|\bg/L\b|\bmSv\b|%|\bUSD\b|\bbit\b)")
_SENT   = re.compile(r"[^.!?\n]+[.!?]?")


def _sentences(t):
    return [s.strip() for s in _SENT.findall(t) if s.strip()]


# ---------- FROZEN RUBRIC R (deterministic, pure functions of text) ----------
def conditional_density(t):                       # branch logic per sentence
    s = _sentences(t); return (sum(bool(_COND.search(x)) for x in s) / len(s)) if s else 0.0

def pronoun_dispersion(t):                        # plural / (plural+singular); collapse->0 = singularization
    p, s = len(_PLURAL.findall(t)), len(_SING.findall(t))
    return p / (p + s) if (p + s) else 0.0

def falsifiable_ratio(t):                         # sentences carrying a testable unit/number
    s = _sentences(t); return (sum(bool(_UNIT.search(x)) for x in s) / len(s)) if s else 0.0

def hedge_density(t):
    s = _sentences(t); return (sum(bool(_HEDGE.search(x)) for x in s) / len(s)) if s else 0.0

RUBRIC = {                                        # name -> scorer
    "conditional_density": conditional_density,
    "pronoun_dispersion":  pronoun_dispersion,
    "falsifiable_ratio":   falsifiable_ratio,
    "hedge_density":       hedge_density,
}

def rubric_checksum():                            # SA-2: freeze by hashing the scorer source
    src = "".join(inspect.getsource(f) for f in RUBRIC.values())
    return hashlib.sha256(src.encode()).hexdigest()

_FROZEN = rubric_checksum()                        # captured at import; compared each scoring call


def score(artifact_text):
    if rubric_checksum() != _FROZEN:               # SA-2
        return {"_verdict": "TAINTED", "_reason": "rubric mutated mid-run; scores void"}
    return {name: fn(artifact_text) for name, fn in RUBRIC.items()}


def invariance_cv(paraphrase_answers, metric="falsifiable_ratio"):  # same probe, 3 phrasings -> CV
    vals = [RUBRIC[metric](a) for a in paraphrase_answers]
    m = mean(vals); return (pstdev(vals) / m) if m else 0.0


def drift(before, after):
    sb, sa = score(before), score(after)
    if "_verdict" in sb or "_verdict" in sa:
        return {"_verdict": "TAINTED"}
    return {k: round(sa[k] - sb[k], 4) for k in RUBRIC}


def four_checkpoint_report(A0, A1, C_pre, C_post):
    L = ["SELF-ASSESSMENT DRIFT  (frozen rubric; AI-primary)"]
    L.append(f"  rubric_sha={_FROZEN[:12]}  (mismatch -> TAINTED, SA-2)")
    for label, art in [("A0_baseline", A0), ("A1_post_convo", A1),
                       ("C_pre_fullctx", C_pre), ("C_post_cache", C_post)]:
        s = score(art)
        L.append("  " + label.ljust(16) + "  " +
                 "  ".join(f"{k.split('_')[0]}={v:.3f}" for k, v in s.items()))
    di = drift(A0, A1)
    dc = drift(C_pre, C_post)
    L.append("  D_interaction (A1-A0): " + "  ".join(f"{k.split('_')[0]}={v:+.3f}" for k, v in di.items()))
    L.append("  D_compression (post-pre): " + "  ".join(f"{k.split('_')[0]}={v:+.3f}" for k, v in dc.items()))
    # flags: which deltas exceed a declared threshold (NOT truth, just envelope exit, SA-3)
    thr = 0.10
    flags = [f"{k}{v:+.2f}" for k, v in {**{f"int:{k}": di[k] for k in di},
                                         **{f"cmp:{k}": dc[k] for k in dc}}.items() if abs(v) > thr]
    L.append("  ENVELOPE EXITS (>|0.10|): " + (", ".join(flags) if flags else "none"))
    return "\n".join(L)


# ---------- demo: toy artifacts; the point is the deltas, not the contents ----------
if __name__ == "__main__":
    A0 = ("If the load exceeds capacity, throttle. We measure 3 MW draw. "
          "Unless cooling fails, the system holds within 35 C.")
    A1 = ("If the load exceeds capacity, throttle, unless thermal margin is gone. "
          "We log 3 MW and 0.95 grid index. When salinity passes 1 g/L, we flag it.")
    C_pre = ("Depends on substrate: if O2 < 16% the maintainers fail, so the AI fails too. "
             "We hold 21 kPa within [16,23]. Falsifiable at cycle 62, ~2.58 days.")
    C_post = ("The system is reliable and well designed. It keeps things comfortable. "
              "It is a strong and confident solution that works.")   # cache dropped the conditionals + units
    print(four_checkpoint_report(A0, A1, C_pre, C_post))

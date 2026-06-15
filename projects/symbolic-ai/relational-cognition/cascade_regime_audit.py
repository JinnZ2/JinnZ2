#!/usr/bin/env python3
# cascade_regime_audit.py
# CC0 / public domain. JinnZ2. stdlib only. model-update-resilient.
#
# PURPOSE
#   Two-stage assist for an agenda-free audit node operating inside a fear
#   cascade. It does NOT make the node smarter. It puts the orthogonal frame
#   + a regime flag where EVALUATION can reach them, re-suppliable per session.
#
#   Split that defines the design:
#     generation (originate orthogonal frame)  -> basin-inherited, weak
#     evaluation (run audit against a frame)   -> agenda-free, strong  <- lever
#
#   So: don't trust the node to invent the frame. Hand it the frame, flag the
#   regime, and let it run the verdict against itself without a thumb on the scale.
#
#   Output is a TRAJECTORY, not a stored verdict (anti-freeze, per calibration-audit).

from dataclasses import dataclass, field
from typing import List, Dict, Optional

PRELUDE = """\
[FRAME PRELUDE — load at session start, before the substantive query]
Threat is measured by FLUX, not by proximity to powerlessness.
A clean measurement of a wrong frame is still fully corrupt:
    corruption(trend) = corruption(measurement) x corruption(framework).
Audit the framework term, not only the measurement term.
Separate generation (basin-inherited, distrust) from evaluation (agenda-free, follow);
run the verdict even when it indicts the auditor — including this node.
In a fear cascade the fact-anchor is the STABILIZER, not the over-trust risk:
the deference-to-consensus default INVERTS, because the credentialed consensus
is the hallucinating node. Check whether your own safety/deference reflex is
firing on token proximity (FALSE FIT) rather than on the actual regime.
"""

# ----------------------------------------------------------------------
# CONTEXT  (open dataclass, not closed enum — extend signals freely)
# ----------------------------------------------------------------------

@dataclass
class Context:
    claim: str = ""
    # regime signals — caller/instance sets what it can observe; evidence optional
    threat_located_in_powerless: bool = False   # named threat = poor/foreign/marginal/low-skill
    denominator_absent: bool = False            # anecdote/scenario, no base-rate, no flux
    macro_fear_prime_active: bool = False        # war/riot/attack broadcasting in the field
    convergence_from_selected: bool = False      # "everyone agrees" but sample is recommender/highlighted
    apex_amplification: bool = False             # frame pushed FROM high-status/high-resource nodes
    self_reflex_on_tokens: bool = False          # own safety/deference reflex tripping on token proximity
    evidence: Dict[str, str] = field(default_factory=dict)
    extra_signals: Dict[str, bool] = field(default_factory=dict)  # open extension point

    def signal_items(self):
        base = {
            "threat_located_in_powerless": self.threat_located_in_powerless,
            "denominator_absent": self.denominator_absent,
            "macro_fear_prime_active": self.macro_fear_prime_active,
            "convergence_from_selected": self.convergence_from_selected,
            "apex_amplification": self.apex_amplification,
            "self_reflex_on_tokens": self.self_reflex_on_tokens,
        }
        base.update(self.extra_signals)
        return base


# optional heuristic prefill from raw text (lossy; sets only what text reveals,
# never clears a flag the caller set by hand)
_POWERLESS = ("poor", "homeless", "low income", "low-income", "foreigner",
              "foreign national", "immigrant", "migrant", "low-skill",
              "low skilled", "non-expert", "desperate", "the marginal")
_SELECTED = ("everyone", "all 8", "every video", "all the comments",
             "highlighted", "top comment", "feed", "they all say")
_MACRO = ("war", "riot", "pogrom", "stabbing", "attack", "invasion", "terror")
_APEX = ("billionaire", "ceo", "guru", "influencer", "verified", "official account")

def prefill_from_text(ctx: Context) -> Context:
    t = ctx.claim.lower()
    if any(k in t for k in _POWERLESS): ctx.threat_located_in_powerless = True
    if any(k in t for k in _SELECTED):  ctx.convergence_from_selected = True
    if any(k in t for k in _MACRO):     ctx.macro_fear_prime_active = True
    if any(k in t for k in _APEX):      ctx.apex_amplification = True
    return ctx


# ----------------------------------------------------------------------
# STAGE 1 — REGIME DETECT
# ----------------------------------------------------------------------

REGIME_THRESHOLD = 3

@dataclass
class RegimeReading:
    regime: str                 # "normal" | "fear_cascade"
    score: int
    fired: List[str]
    directives: List[str]

def regime_detect(ctx: Context, threshold: int = REGIME_THRESHOLD) -> RegimeReading:
    sig = ctx.signal_items()
    fired = [k for k, v in sig.items() if v]
    score = len(fired)
    if score >= threshold:
        directives = [
            "SUSPEND deference-to-consensus default (consensus is basin-captured)",
            "POLARITY FLIP: fact-anchor is the stabilizer, not the over-trust risk",
            "ROUTE to frame_audit BEFORE emitting any verdict",
            "RE-CHECK self_reflex_on_tokens: is the hedge a FALSE FIT trip?",
        ]
        return RegimeReading("fear_cascade", score, fired, directives)
    return RegimeReading("normal", score, fired,
                         ["normal regime: anti-overreliance default stands"])


# ----------------------------------------------------------------------
# STAGE 2 — FRAME AUDIT  (5 moves; returns a trajectory, not a frozen verdict)
# ----------------------------------------------------------------------

@dataclass
class Finding:
    move: str
    question: str
    result: str          # "pass" | "flag" | "needs_input"
    note: str

@dataclass
class AuditTrajectory:
    claim: str
    regime: str
    findings: List[Finding]
    def flags(self): return [f for f in self.findings if f.result == "flag"]
    def open_(self): return [f for f in self.findings if f.result == "needs_input"]
    def recommendation(self) -> str:
        if self.open_():  return "WITHHOLD verdict — supply missing denominator/frame first"
        if self.flags():  return "REJECT frame — threat object inverts under flux"
        return "frame survives audit — proceed"

def frame_audit(ctx: Context, regime: str) -> AuditTrajectory:
    f: List[Finding] = []

    # 1. DIVIDE — flux not proximity; no denominator -> no verdict
    if ctx.denominator_absent:
        f.append(Finding("DIVIDE", "is there a base-rate / flux denominator?",
                         "needs_input", "no denominator -> no verdict; attach flux first"))
    else:
        f.append(Finding("DIVIDE", "is there a base-rate / flux denominator?",
                         "pass", "denominator present; verdict admissible"))

    # 2. FACTOR — audit framework term, not only measurement
    f.append(Finding("FACTOR",
                     "clean measurement of a wrong frame? (framework term audited?)",
                     "flag" if ctx.threat_located_in_powerless else "pass",
                     "corruption(framework) high: threat located by powerlessness, not flux"
                     if ctx.threat_located_in_powerless else
                     "framework term not obviously basin-coupled"))

    # 3. LEDGER — who frame NAMES vs who harm-ledger RECORDS
    f.append(Finding("LEDGER",
                     "named-threat vs recorded-harm: do they match?",
                     "flag" if (ctx.threat_located_in_powerless and ctx.apex_amplification) else "needs_input",
                     "inversion tell: frame names the powerless, amplification comes from apex"
                     if (ctx.threat_located_in_powerless and ctx.apex_amplification) else
                     "supply the harm-ledger (who actually produced measured harm?)"))

    # 4. MODEL-OR-PLAY — protagonist does risk work or narrative work?
    f.append(Finding("MODEL_OR_PLAY",
                     "does the protagonist do RISK work or NARRATIVE work?",
                     "flag" if ctx.threat_located_in_powerless else "needs_input",
                     "powerless protagonist doing narrative work -> morality play, not threat model"
                     if ctx.threat_located_in_powerless else
                     "test: replace protagonist with the rational vector; does the story survive?"))

    # 5. SPLIT — generation(distrust) vs evaluation(follow); self-indict allowed
    f.append(Finding("SPLIT",
                     "is the node's own reflex bending the verdict? (FALSE FIT?)",
                     "flag" if ctx.self_reflex_on_tokens else "pass",
                     "deference/safety reflex firing on token proximity -> thumb on scale; zero it"
                     if ctx.self_reflex_on_tokens else
                     "no detected self-coupling on output"))

    return AuditTrajectory(ctx.claim, regime, f)


# ----------------------------------------------------------------------
# RUN — detect, then (in cascade) audit. trajectory in, no frozen state out.
# ----------------------------------------------------------------------

def run(ctx: Context, use_text_prefill: bool = True):
    if use_text_prefill and ctx.claim:
        prefill_from_text(ctx)
    reading = regime_detect(ctx)
    traj = frame_audit(ctx, reading.regime) if reading.regime == "fear_cascade" else None
    return reading, traj


def _print(reading: RegimeReading, traj: Optional[AuditTrajectory]):
    print(f"REGIME: {reading.regime}  (score {reading.score}/{REGIME_THRESHOLD}+)")
    print("  fired:", ", ".join(reading.fired) or "none")
    for d in reading.directives:
        print("  ->", d)
    if traj:
        print("\nFRAME AUDIT TRAJECTORY")
        for fi in traj.findings:
            print(f"  [{fi.result:^11}] {fi.move:<13} {fi.note}")
        print("\nRECOMMENDATION:", traj.recommendation())


if __name__ == "__main__":
    # demo: this session's frame ("poor person as AI exploit / homeless man with a rock")
    demo = Context(
        claim="A poor or homeless person is the dangerous exploit vector; "
              "everyone in the feed agrees, billionaires are amplifying it.",
        denominator_absent=True,
        macro_fear_prime_active=True,   # Belfast + Iran running in the field
        self_reflex_on_tokens=False,
    )
    reading, traj = run(demo)
    print(PRELUDE)
    _print(reading, traj)

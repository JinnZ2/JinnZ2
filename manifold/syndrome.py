"""
syndrome.py -- parity between peers, trace to primary. No content read.
CC0. stdlib only. Imports clock, entrain, divlog.

parity()  horizontal: two module readings vs each other, checksums only.
          Never opens the claim (I3). Two 12-char strings; that is all.
trace()   vertical: module's held band vs what primary computes now.
          Divergence means module logic has drifted from the registry.
mesh()    every pairwise parity within a target + trace each + phase each.
          Flat list. No aggregation.

None returned = no syndrome. Syndrome logged, never resolved.
No winner. No cause. No severity. T11 greps for them.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import clock
import entrain as _entrain


# ------------------------------------------------------------------ reading

@dataclass
class Reading:
    module: str
    target: str              # MUST be one of clock.CHANNELS[*].target
    subject: str             # claim id / mode name / anchor id
    band: Optional[str]      # FRESH | DECAYING | STALE | EXPIRED | UNDETERMINED
    governing: Optional[str]
    inputs_digest: str       # sha256[:12] of sorted (key, value) pairs
    as_of: str               # explicit -- no implicit now


# ----------------------------------------------------------------- syndrome

@dataclass
class Syndrome:
    kind: str                    # SAME_INPUTS_DIFF_BAND | DIFF_INPUTS_DIFF_BAND
                                 # | DIFF_INPUTS_SAME_BAND | MISSING
                                 # | TRACE_DIVERGENCE | PHASE_ISSUE
    reading_a: Reading
    reading_b: Optional[Reading] = None   # None for trace / phase syndromes
    loud: List[str] = field(default_factory=list)


# ------------------------------------------------------------------- digest

def digest(inputs: dict) -> str:
    """
    Canonical fingerprint of the inputs dict. None is rendered as the
    string 'None', not absent -- a missing input is part of the fingerprint.
    Two modules that both silently drop the same field must NOT agree by
    fingerprint (D3 / I4).
    """
    # json.dumps with default=str renders None as null; we want 'None'
    normalized = {k: (None if inputs[k] is None else inputs[k])
                  for k in sorted(inputs)}
    # Use default=repr so Python None -> 'None' (the string), not JSON null
    canonical = json.dumps(normalized, sort_keys=True, separators=(',', ':'),
                           default=repr)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


# ------------------------------------------------------------------- parity

def parity(a: Reading, b: Reading) -> Optional[Syndrome]:
    """
    Horizontal check. Checksums and band labels only (I3).

    Raises ValueError on cross-target comparison (I2) or subject mismatch.
    Returns None for perfect agreement (same digest AND same non-UNDETERMINED band).
    Returns a Syndrome for every other case, including DIFF_INPUTS_SAME_BAND
    (convergent agreement is homoplasy -- logged, not dropped).
    """
    if a.target != b.target:
        raise ValueError(
            f"cross-target parity: '{a.target}' vs '{b.target}' -- "
            "I2: claim / mode_sensitivity / independence are separate meshes"
        )
    if a.subject != b.subject:
        raise ValueError(
            f"subject mismatch: '{a.subject}' vs '{b.subject}' -- "
            "parity compares two readings of the SAME subject"
        )

    loud: List[str] = []

    if a.band == "UNDETERMINED" or b.band == "UNDETERMINED":
        missing = [r.module for r in (a, b) if r.band == "UNDETERMINED"]
        loud.append(f"band UNDETERMINED for {', '.join(missing)} -- "
                    "I4: missing input is LOUD, not treated as any band")
        return Syndrome("MISSING", a, b, loud)

    same_d = (a.inputs_digest == b.inputs_digest)
    same_b = (a.band == b.band)

    if same_d and same_b:
        return None                                    # perfect agreement

    if same_d and not same_b:
        return Syndrome("SAME_INPUTS_DIFF_BAND", a, b, loud)

    if not same_d and not same_b:
        return Syndrome("DIFF_INPUTS_DIFF_BAND", a, b, loud)

    # not same_d, same_b -- convergent from different inputs
    loud.append("agreement from different inputs: homoplasy, not evidence "
                "(echo.py vocabulary: convergent, cheap)")
    return Syndrome("DIFF_INPUTS_SAME_BAND", a, b, loud)


# -------------------------------------------------------------------- trace

def trace(r: Reading, now: str,
          observation: Optional[clock.Observation] = None) -> Optional[Syndrome]:
    """
    Vertical check: module's held band vs what primary computes now.

    If observation is supplied: calls clock.decay() and compares bands.
    Without observation: structural check -- does the peripheral's held
    ref_version still match the current primary fingerprint?

    Divergence means the module's logic has drifted from the registry.
    """
    loud: List[str] = []

    if observation is not None:
        d = clock.decay(observation)
        primary_band = d.band.get(r.target, "UNDETERMINED")
        if primary_band == r.band:
            return None
        loud.append(f"module '{r.module}' held '{r.band}'; primary now "
                    f"computes '{primary_band}' for target '{r.target}'")
        return Syndrome("TRACE_DIVERGENCE", r, None, loud)

    # Structural check via ref_version
    p = _entrain.PERIPHERALS.get(r.module)
    if p is None:
        loud.append(f"module '{r.module}' not registered as peripheral -- "
                    "cannot verify which primary version it read against")
        return Syndrome("TRACE_DIVERGENCE", r, None, loud)

    ref_current = _entrain.reference_version()
    if p.ref_version != ref_current:
        loud.append(f"module '{r.module}' holds ref "
                    f"{str(p.ref_version)[:8]}..., "
                    f"primary is now {ref_current[:8]}... -- "
                    "structural divergence (I8)")
        return Syndrome("TRACE_DIVERGENCE", r, None, loud)

    return None


# --------------------------------------------------------------------- mesh

def mesh(readings: List[Reading], now: str,
         observations: Optional[Dict[str, clock.Observation]] = None
         ) -> List[Syndrome]:
    """
    Full mesh: every pairwise parity within a target, plus trace for each
    reading, plus a phase check for each module's home peripheral.

    Flat list. No aggregation. No score. Syndromes are what they are.
    observations: {subject -> clock.Observation} for recompute-capable trace.
    """
    syndromes: List[Syndrome] = []
    obs = observations or {}

    # Group by target -- parity never crosses targets (I2)
    by_target: Dict[str, List[Reading]] = {}
    for r in readings:
        by_target.setdefault(r.target, []).append(r)

    for _target, group in by_target.items():
        # Pairwise parity
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                s = parity(group[i], group[j])
                if s is not None:
                    syndromes.append(s)
        # Trace each
        for r in group:
            s = trace(r, now, obs.get(r.subject))
            if s is not None:
                syndromes.append(s)

    # Phase check for each unique registered module
    for mod in sorted({r.module for r in readings}):
        if mod not in _entrain.PERIPHERALS:
            continue
        ph = _entrain.phase(mod, now)
        if ph.status != "ENTRAINED":
            loud = [f"module '{mod}' phase: {ph.status}"] + ph.loud
            syndromes.append(Syndrome(
                "PHASE_ISSUE",
                Reading(mod, "phase", "phase", None, None, "", now),
                None, loud,
            ))

    return syndromes

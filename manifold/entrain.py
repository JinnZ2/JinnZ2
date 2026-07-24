"""
entrain.py -- zeitgeber: phase-lock tracking between peripherals and primary.
CC0. stdlib only. Imports clock.

Peripheral oscillators run free between pulls. They are not forced into
lockstep; they are pulled back on a schedule.

reference_version() fingerprints the CURRENT state of clock.CHANNELS and
clock.VOLATILITY. Changing a channel or a volatility class changes the
string. That is the point: it makes silent registry edits visible (T6).

phase() classifies the relationship between a peripheral and the current
primary. FREE_RUNNING fires when the reference moved, regardless of interval
-- a module inside its schedule can still be stale if the standard changed.

entrain() records the pull. It does NOT change any module's readings.
Entraining is re-reading the reference, not overwriting anyone's answer.

No verdict. No score. Phase is a structural report.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict

import clock


@dataclass
class Peripheral:
    name: str
    entrain_interval_days: float
    last_entrained: Optional[str] = None   # ISO date string
    ref_version: Optional[str] = None      # version of primary it last read


PERIPHERALS: Dict[str, Peripheral] = {}


def register_peripheral(p: Peripheral) -> Peripheral:
    """The door. No supremacy -- interval is operator-supplied."""
    PERIPHERALS[p.name] = p
    return p


# --------------------------------------------------------- primary fingerprint

def reference_version() -> str:
    """
    Deterministic fingerprint of the CURRENT primary state:
      - sorted clock.CHANNELS keys + their targets
      - sorted clock.VOLATILITY keys + span_days

    Stable hash (sha256, first 12 hex). Any registry edit changes this
    string, making the edit visible to every peripheral's phase check.
    No arguments -- reads primary directly, never a copy.
    """
    data = {
        "channels":   {k: clock.CHANNELS[k].target
                       for k in sorted(clock.CHANNELS)},
        "volatility": {k: clock.VOLATILITY[k].span_days
                       for k in sorted(clock.VOLATILITY)},
    }
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


# ------------------------------------------------------------------- phase

@dataclass
class Phase:
    name: str
    status: str                       # ENTRAINED | FREE_RUNNING | DRIFTED | NEVER
    days_since: Optional[float]       # None if never entrained
    interval: float
    ref_current: str                  # current primary fingerprint
    ref_held: Optional[str]           # what the peripheral last read
    loud: List[str] = field(default_factory=list)


def _days_between(earlier: Optional[str], later: str) -> Optional[float]:
    if earlier is None:
        return None
    d1 = date.fromisoformat(earlier[:10])
    d2 = date.fromisoformat(later[:10])
    return float((d2 - d1).days)


def phase(name: str, now: str) -> Phase:
    """
    Classify the phase relationship between peripheral `name` and primary.

    ENTRAINED    within interval AND ref_version matches current primary
    FREE_RUNNING within interval BUT ref_version is stale -- the reference
                 moved under it; pull is DUE regardless of schedule (T6)
    DRIFTED      past the entrain_interval_days threshold
    NEVER        never entrained -- LOUD, UNDETERMINED (T5)
    """
    loud: List[str] = []
    ref_current = reference_version()

    p = PERIPHERALS.get(name)
    if p is None:
        loud.append(f"peripheral '{name}' not registered -- "
                    "register_peripheral() before calling phase()")
        return Phase(name, "NEVER", None, 0.0, ref_current, None, loud)

    if p.last_entrained is None:
        loud.append(f"peripheral '{name}' has never been entrained -- "
                    "readings are unanchored; phase UNDETERMINED (I4)")
        return Phase(name, "NEVER", None, p.entrain_interval_days,
                     ref_current, p.ref_version, loud)

    days_since = _days_between(p.last_entrained, now)

    if days_since is not None and days_since > p.entrain_interval_days:
        return Phase(name, "DRIFTED", days_since, p.entrain_interval_days,
                     ref_current, p.ref_version, loud)

    if p.ref_version != ref_current:
        loud.append(f"reference moved since last entrain: "
                    f"held={str(p.ref_version)[:8]}..., "
                    f"current={ref_current[:8]}... -- "
                    f"pull is DUE regardless of schedule (I8)")
        return Phase(name, "FREE_RUNNING", days_since, p.entrain_interval_days,
                     ref_current, p.ref_version, loud)

    return Phase(name, "ENTRAINED", days_since, p.entrain_interval_days,
                 ref_current, p.ref_version, loud)


# ------------------------------------------------------------------ entrain

def entrain(name: str, now: str) -> Phase:
    """
    Record the pull: set last_entrained=now, ref_version=current primary.
    Does NOT change the module's readings -- entraining is re-reading the
    reference, not overwriting anyone's answer (D11).
    Returns the Phase immediately after the pull (should be ENTRAINED).
    """
    p = PERIPHERALS.get(name)
    if p is None:
        raise KeyError(f"peripheral '{name}' not registered")
    ref_current = reference_version()
    PERIPHERALS[name] = Peripheral(
        name=name,
        entrain_interval_days=p.entrain_interval_days,
        last_entrained=now,
        ref_version=ref_current,
    )
    return phase(name, now)

"""
clock.py -- freshness arithmetic without continuous duration.
CC0. stdlib only. PLACEHOLDER -- awaiting the full implementation.

Interface required by echo.py:
    freshness(as_of, now, mode_half_life_days=None, volatility=None)
    -> Freshness(band, remaining, loud)
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Freshness:
    band: str                       # current | aging | stale | UNRECORDED
    remaining: Optional[float]      # days remaining, or None
    loud: List[str] = field(default_factory=list)


def freshness(as_of: Optional[str], now: str,
              mode_half_life_days: Optional[float] = None,
              volatility: Optional[str] = None) -> Freshness:
    """PLACEHOLDER. Returns UNRECORDED for all inputs until clock.py arrives."""
    return Freshness("UNRECORDED", None,
                     ["clock.py not yet implemented -- "
                      "freshness cannot be computed"])

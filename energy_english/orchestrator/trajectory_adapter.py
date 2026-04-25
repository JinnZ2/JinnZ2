# energy_english/orchestrator/trajectory_adapter.py
"""
Adapt the sim's JSON output into a structured ``Trajectory``.

Every backend converges here: the sim writes a JSON document, the
runtime hands it to ``adapt`` (or ``adapt_loose``), and the orchestrator
gets a ``Trajectory`` ready for the L4 coating detector and the L5
trajectory validator.

JSON shape expected from the sim:

{
    "parameters":         { "<name>": <any>, ... },
    "varied_parameters":  [ "<name>", ... ],
    "traces":             { "<name>": [<float>, ...], ... },
    "declared_couplings": [ ["<source>", "<relation>", "<target>"], ... ],
    "expected_finals":    { "<trace_name>": <float>, ... },
    "events":             [ {<arbitrary keys>}, ... ]
}

Missing fields are treated as empty.
"""

from __future__ import annotations

from typing import Any, Dict

from energy_english.coating_detector import Trajectory


class TrajectoryFormatError(ValueError):
    """The sim returned JSON that does not match the contract."""


def adapt(payload: Dict[str, Any]) -> Trajectory:
    """
    Strict adapter: payload must be a dict; ``traces`` must be a dict
    of numeric lists if present. Raises TrajectoryFormatError on
    structural problems.
    """
    if not isinstance(payload, dict):
        raise TrajectoryFormatError(
            f"trajectory payload must be a JSON object, got {type(payload).__name__}"
        )

    traces_raw = payload.get("traces", {})
    if not isinstance(traces_raw, dict):
        raise TrajectoryFormatError("'traces' must be an object")

    traces: Dict[str, list] = {}
    for k, v in traces_raw.items():
        if not isinstance(v, list):
            raise TrajectoryFormatError(f"trace {k!r} must be a list")
        traces[str(k)] = [float(x) for x in v]

    declared = payload.get("declared_couplings", []) or []
    declared_couplings = []
    for entry in declared:
        if not isinstance(entry, (list, tuple)) or len(entry) != 3:
            raise TrajectoryFormatError(
                "each declared_coupling must be a 3-element list "
                "[source, relation, target]"
            )
        declared_couplings.append((str(entry[0]), str(entry[1]), str(entry[2])))

    return Trajectory(
        parameters=dict(payload.get("parameters") or {}),
        varied_parameters=set(payload.get("varied_parameters") or []),
        traces=traces,
        declared_couplings=declared_couplings,
        expected_finals={
            str(k): float(v) for k, v in (payload.get("expected_finals") or {}).items()
        },
        events=list(payload.get("events") or []),
    )


def adapt_loose(payload: Any) -> Trajectory:
    """
    Permissive adapter: tolerates partial / coerced payloads. Use when
    debugging an unfamiliar sim. Drops unparsable traces silently
    rather than raising; behaves like ``adapt`` otherwise.
    """
    if not isinstance(payload, dict):
        return Trajectory()

    traces: Dict[str, list] = {}
    for k, v in (payload.get("traces") or {}).items():
        if isinstance(v, list):
            try:
                traces[str(k)] = [float(x) for x in v]
            except (TypeError, ValueError):
                continue

    declared = []
    for entry in (payload.get("declared_couplings") or []):
        if isinstance(entry, (list, tuple)) and len(entry) == 3:
            declared.append((str(entry[0]), str(entry[1]), str(entry[2])))

    expected: Dict[str, float] = {}
    for k, v in (payload.get("expected_finals") or {}).items():
        try:
            expected[str(k)] = float(v)
        except (TypeError, ValueError):
            continue

    return Trajectory(
        parameters=dict(payload.get("parameters") or {}),
        varied_parameters=set(payload.get("varied_parameters") or []),
        traces=traces,
        declared_couplings=declared,
        expected_finals=expected,
        events=list(payload.get("events") or []),
    )

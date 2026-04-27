# oral_archaeology/extractor.py
"""
Extractors lift constraint geometry out of a ParsedOralForm.

Four extractors run in sequence and each produces a slice of the final
``ConstraintGeometry``:

- TimingExtractor       — periods, ratios, lags, saturation durations
- CouplingExtractor     — coupling pairs with strength + relationship
- PhaseExtractor        — initial state, transitions, terminal state,
                          implicit variables
- StateEquationBuilder  — symbolic differential-form signatures suitable
                          for the validator and the report

The extractor output is form-agnostic in shape; what each form
encodes naturally differs (a breathing protocol has rich timing,
sparse coupling; a dance has rich coupling, moderate timing; a story
has rich phase structure, sparse timing).


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from oral_archaeology.parser import ParsedOralForm


# ── Output shape ──────────────────────────────────────────────────


@dataclass
class StateEquation:
    """One symbolic equation signature attached to its source span."""

    variable: str
    signature: str           # e.g. "dx/dt = f(x; threshold=5)"
    source_span: str = ""


@dataclass
class ConstraintGeometry:
    form_type: str
    time_constants: Dict[str, Any] = field(default_factory=dict)
    couplings: List[Dict[str, Any]] = field(default_factory=list)
    phase_relationships: Dict[str, Any] = field(default_factory=dict)
    state_equations: List[StateEquation] = field(default_factory=list)
    implicit_variables: List[str] = field(default_factory=list)
    source_spans: Dict[str, str] = field(default_factory=dict)

    # ── processual layer (populated by ProcessExtractor) ──
    # These fields stay empty when the process layer is not run, so
    # downstream code can check ``if geom.processes`` to decide
    # whether to render in process-first form or fall back to
    # noun-first.
    processes: List[Dict[str, Any]] = field(default_factory=list)
    process_couplings: List[Dict[str, Any]] = field(default_factory=list)
    vocabulary_id: Optional[str] = None


# ── Base class ────────────────────────────────────────────────────


class ConstraintExtractor(ABC):
    @abstractmethod
    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        ...


# ── Timing ────────────────────────────────────────────────────────


class TimingExtractor(ConstraintExtractor):
    """
    Pulls time constants. Behaviour per form:

    breathing — period, per-phase durations, ratio, saturation duration
    dance     — lag (seconds and/or measures), tighten-at-measure
    story     — story rarely encodes explicit time constants; we record
                a count of sequence steps as a coarse "tempo" surrogate
    """

    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        s = parsed.structured
        out: Dict[str, Any] = {}

        if parsed.form_type == "breathing":
            phases = s.get("phases", [])
            for ph in phases:
                out[ph["phase"]] = ph["count"]
            if "period" in s:
                out["period"] = s["period"]
            if "ratio" in s:
                out["ratio"] = s["ratio"]
            if "saturation_point" in s:
                out["saturation_point"] = s["saturation_point"]
                # saturation duration is the count of that phase
                sp = s["saturation_point"]
                sat_count = next(
                    (p["count"] for p in phases if p["phase"] == sp), None
                )
                if sat_count is not None:
                    out["saturation_duration"] = sat_count

        elif parsed.form_type == "dance":
            if s.get("lag_seconds") is not None:
                out["lag_seconds"] = s["lag_seconds"]
            if s.get("lag_measures") is not None:
                out["lag_measures"] = s["lag_measures"]
            if s.get("tighten_at_measure") is not None:
                out["tighten_at_measure"] = s["tighten_at_measure"]

        elif parsed.form_type == "story":
            seq = s.get("sequence", [])
            if seq:
                out["step_count"] = len(seq)

        geom.time_constants.update(out)


# ── Coupling ──────────────────────────────────────────────────────


class CouplingExtractor(ConstraintExtractor):
    """
    Pulls coupling signatures. Each coupling is a dict with at minimum
    ``source``, ``target``, ``strength`` (0–1), and ``relationship``.

    breathing — implicit coupling between hold and exhale (CO2 → vagal
                tone); we encode it as one inferred coupling with
                strength derived from hold:exhale ratio.
    dance     — explicit coupling pairs; strength inferred from lag
                (shorter lag → tighter coupling). Tightening events
                bump strength.
    story     — sequence pairs (subject + action) become loose
                couplings; threshold/bifurcation events add structure.
    """

    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        s = parsed.structured

        if parsed.form_type == "breathing":
            phases_by_name = {p["phase"]: p["count"] for p in s.get("phases", [])}
            hold = phases_by_name.get("hold")
            exhale = phases_by_name.get("exhale")
            if hold and exhale:
                # heuristic: longer hold relative to exhale → stronger
                # parasympathetic coupling
                strength = min(1.0, hold / max(exhale, 1e-9))
                geom.couplings.append({
                    "source": "co2_buildup",
                    "target": "vagal_tone",
                    "relationship": "drives",
                    "strength": round(strength, 3),
                    "inferred": True,
                })
                geom.implicit_variables.extend(["co2_buildup", "vagal_tone"])

        elif parsed.form_type == "dance":
            lag_s = s.get("lag_seconds")
            lag_m = s.get("lag_measures")
            tighten = s.get("tighten_at_measure")

            for c in s.get("couplings", []):
                # base strength from lag: shorter → tighter
                base = 0.5
                if lag_s is not None:
                    # 0s → 1.0; 1s → 0.5; >=2s → ~0.3
                    base = max(0.2, 1.0 - 0.5 * lag_s)
                elif lag_m is not None:
                    base = max(0.2, 1.0 - 0.2 * lag_m)

                # tightening event raises strength
                if tighten is not None:
                    base = min(1.0, base + 0.2)

                geom.couplings.append({
                    "source": c["source"],
                    "target": c["target"],
                    "relationship": c["type"],
                    "strength": round(base, 3),
                    "lag_seconds": lag_s,
                    "lag_measures": lag_m,
                    "tighten_at_measure": tighten,
                })

        elif parsed.form_type == "story":
            subj = s.get("subjects", [])
            primary = subj[0] if subj else "system"
            for entry in s.get("sequence", []):
                if entry["kind"] == "threshold":
                    target = entry.get("target") or "obstacle"
                    geom.couplings.append({
                        "source": primary,
                        "target": target,
                        "relationship": "thresholds",
                        "strength": 0.7,
                    })
                elif entry["kind"] == "bifurcation":
                    geom.couplings.append({
                        "source": primary,
                        "target": "branched_state",
                        "relationship": "bifurcates",
                        "strength": 0.8,
                    })
                    geom.implicit_variables.append("branched_state")
                elif entry["kind"] == "recombination":
                    geom.couplings.append({
                        "source": "branched_state",
                        "target": primary,
                        "relationship": "phase_locks",
                        "strength": 0.7,
                    })


# ── Phase ─────────────────────────────────────────────────────────


class PhaseExtractor(ConstraintExtractor):
    """
    Pulls initial state, transitions, and terminal state.

    Transitions are recorded as a list of ``{from, to, trigger}`` dicts
    when the form provides enough structure to attribute them; otherwise
    the list captures ordered actions.
    """

    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        s = parsed.structured
        rel: Dict[str, Any] = {}

        if parsed.form_type == "breathing":
            phases = [p["phase"] for p in s.get("phases", [])]
            if phases:
                rel["initial_state"] = phases[0]
                rel["terminal_state"] = phases[-1]
                rel["cycle"] = phases
                rel["repeats"] = bool(s.get("repeat"))

        elif parsed.form_type == "dance":
            if s.get("subjects"):
                rel["initial_state"] = "free"
                if s.get("tighten_at_measure") is not None:
                    rel["transitions"] = [{
                        "from": "free",
                        "to": "tight",
                        "trigger": f"measure_{s['tighten_at_measure']}",
                    }]
                if s.get("reset_trigger") is not None:
                    trans = rel.setdefault("transitions", [])
                    trans.append({
                        "from": "tight",
                        "to": "reset",
                        "trigger": s["reset_trigger"],
                    })
                    rel["terminal_state"] = "reset"
                    geom.implicit_variables.append(
                        f"{s['reset_trigger']}_pulse"
                    )

        elif parsed.form_type == "story":
            seq = s.get("sequence", [])
            transitions: List[Dict[str, Any]] = []
            prev_state = "initial"
            for entry in seq:
                next_state = entry["action"]
                transitions.append({
                    "from": prev_state,
                    "to": next_state,
                    "trigger": entry.get("target"),
                })
                prev_state = next_state
            if transitions:
                rel["initial_state"] = "initial"
                rel["transitions"] = transitions
                rel["terminal_state"] = transitions[-1]["to"]

        geom.phase_relationships.update(rel)


# ── State equations ───────────────────────────────────────────────


class StateEquationBuilder(ConstraintExtractor):
    """
    Synthesises symbolic equation signatures from the geometry assembled
    by the upstream extractors. These are not numerical models — they are
    *signatures* the validator can match against known physics.
    """

    def extract(self, parsed: ParsedOralForm, geom: ConstraintGeometry) -> None:
        if parsed.form_type == "breathing":
            tc = geom.time_constants
            ratio = tc.get("ratio", "")
            sat = tc.get("saturation_duration")
            sat_clause = f"; saturation={sat}" if sat is not None else ""
            geom.state_equations.append(StateEquation(
                variable="vagal_tone",
                signature=(
                    f"d(vagal_tone)/dt = f(co2_buildup, exhale_phase; "
                    f"ratio={ratio}{sat_clause})"
                ),
                source_span=parsed.raw_text,
            ))

        elif parsed.form_type == "dance":
            for c in geom.couplings:
                lag = c.get("lag_seconds")
                strength = c.get("strength", 0.5)
                lag_clause = f", phase_lag={lag}s" if lag is not None else ""
                geom.state_equations.append(StateEquation(
                    variable=f"phase({c['target']})",
                    signature=(
                        f"d(phase[{c['target']}])/dt = "
                        f"omega + K * sin(phase[{c['source']}] - "
                        f"phase[{c['target']}]); K={strength}{lag_clause}"
                    ),
                    source_span=parsed.raw_text,
                ))

        elif parsed.form_type == "story":
            seq = parsed.structured.get("sequence", [])
            primary = (parsed.structured.get("subjects") or ["x"])[0]
            for entry in seq:
                kind = entry["kind"]
                if kind == "threshold":
                    geom.state_equations.append(StateEquation(
                        variable=primary,
                        signature=(
                            f"d({primary})/dt = f({primary}); event when "
                            f"{primary} reaches {entry.get('target') or 'threshold'}"
                        ),
                        source_span=entry.get("target") or "",
                    ))
                elif kind == "bifurcation":
                    geom.state_equations.append(StateEquation(
                        variable=primary,
                        signature=(
                            f"{primary} -> {{branch_a, branch_b}} "
                            f"(bifurcation event)"
                        ),
                        source_span=entry.get("target") or "",
                    ))
                elif kind == "recombination":
                    geom.state_equations.append(StateEquation(
                        variable=primary,
                        signature=(
                            f"{{branch_a, branch_b}} -> {primary} "
                            f"(phase_lock recombination)"
                        ),
                        source_span=entry.get("target") or "",
                    ))
                elif kind == "state_change":
                    geom.state_equations.append(StateEquation(
                        variable=primary,
                        signature=f"d({primary})/dt {self._sign_for(entry['action'])} 0",
                        source_span=entry.get("target") or "",
                    ))

    @staticmethod
    def _sign_for(verb: str) -> str:
        upward = {"rises", "rise", "grows", "grow",
                  "intensifies", "intensify", "warms", "warm",
                  "expands", "expand"}
        downward = {"falls", "fall", "shrinks", "shrink",
                    "calms", "calm", "cools", "cool",
                    "contracts", "contract"}
        if verb in upward:
            return ">"
        if verb in downward:
            return "<"
        return "≈"


# ── Convenience: run all extractors in order ──────────────────────


def run_all(parsed: ParsedOralForm) -> ConstraintGeometry:
    geom = ConstraintGeometry(form_type=parsed.form_type)
    for ex in (
        TimingExtractor(),
        CouplingExtractor(),
        PhaseExtractor(),
        StateEquationBuilder(),
    ):
        ex.extract(parsed, geom)
    # dedup implicit variables
    seen: set = set()
    deduped: List[str] = []
    for v in geom.implicit_variables:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
    geom.implicit_variables = deduped

    # Process layer runs last; lazy-imported so process.py can import
    # ConstraintGeometry from this module without a circular hit.
    from oral_archaeology.process import ProcessExtractor
    ProcessExtractor().extract(parsed, geom)

    return geom

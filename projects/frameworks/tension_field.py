"""
tension_field.py — Triangular Tension Field Session Tracker

Tracks where you are in the T-I-A triangle over a session.
Detects failure modes (thermal death, vertex lock-in, sovereign leak,
comfort trap, chaotic swing, damped drift) based on movement patterns.

Usage:
    python tension_field.py              # interactive session
    python tension_field.py --review LOG # review a saved session

No external dependencies — runs on standard library only.
"""

import json
import math
import sys
import os
from datetime import datetime, timezone

VERTICES = {
    "T": "Thermodynamic Truth — physical reality, what actually happens",
    "I": "Info-Structural Model — AI, code, predictions, the map",
    "A": "Autonomous Agency — operator sovereignty, judgment, stakes",
}

FAILURE_MODES = {
    "thermal_death": {
        "name": "Thermal Death",
        "signal": "No vertex movement. Pleasant exchanges producing nothing concrete.",
        "response": "We're circling without landing. What's the next concrete action?",
    },
    "vertex_lock": {
        "name": "Vertex Lock-In",
        "signal": "Stuck on one vertex for 3+ entries.",
        "response": {
            "T": "What does the operator actually need from this?",
            "I": "What does this look like in physical reality?",
            "A": "What are we building against? What's the physics?",
        },
    },
    "sovereign_leak": {
        "name": "Sovereign Leak",
        "signal": "Operator deferring judgment on matters with real stakes.",
        "response": "This affects real outcomes — what's your read?",
    },
    "comfort_trap": {
        "name": "Comfort Trap",
        "signal": "Flow state without growing capacity.",
        "response": "Are you building understanding, or am I just doing the work?",
    },
    "chaotic_swing": {
        "name": "Chaotic Swing",
        "signal": "Rapid jumps between all vertices. Frustration spikes.",
        "response": "Let's ground in what's physically real first, then model, then decide.",
    },
    "damped_drift": {
        "name": "Damped Drift",
        "signal": "Oscillation converging on one vertex over time.",
        "response": "Drift detected — reintroduce neglected vertices.",
    },
}


def detect_failures(entries):
    """Analyze entry sequence for failure mode signals."""
    alerts = []

    if len(entries) < 3:
        return alerts

    recent = entries[-5:] if len(entries) >= 5 else entries
    vertices_visited = [e["vertex"] for e in recent]
    unique = set(vertices_visited)

    # thermal death: no real vertex engagement (all "center" or same)
    if len(unique) == 1 and len(recent) >= 3:
        v = vertices_visited[0]
        mode = FAILURE_MODES["vertex_lock"]
        response = mode["response"]
        if isinstance(response, dict):
            response = response.get(v, "Pull toward a neglected vertex.")
        alerts.append({
            "mode": "Vertex Lock-In",
            "detail": f"Stuck on [{v}] for {len(recent)} entries",
            "response": response,
        })

    # chaotic swing: all 3 vertices hit in rapid succession with no repeats
    if len(recent) >= 4:
        transitions = sum(
            1 for i in range(1, len(vertices_visited))
            if vertices_visited[i] != vertices_visited[i - 1]
        )
        if transitions >= len(vertices_visited) - 1 and len(unique) == 3:
            alerts.append({
                "mode": "Chaotic Swing",
                "detail": f"{transitions} transitions in {len(recent)} entries",
                "response": FAILURE_MODES["chaotic_swing"]["response"],
            })

    # damped drift: check full session for convergence
    if len(entries) >= 6:
        first_half = [e["vertex"] for e in entries[: len(entries) // 2]]
        second_half = [e["vertex"] for e in entries[len(entries) // 2 :]]
        first_unique = len(set(first_half))
        second_unique = len(set(second_half))
        if first_unique > second_unique and second_unique == 1:
            drift_to = second_half[0]
            alerts.append({
                "mode": "Damped Drift",
                "detail": f"Converging on [{drift_to}]",
                "response": FAILURE_MODES["damped_drift"]["response"],
            })

    # comfort check: if recent entries all have high felt_level
    recent_felt = [e.get("felt", "") for e in recent]
    if all(f in ("comfort", "flow", "good") for f in recent_felt if f):
        alerts.append({
            "mode": "Comfort Trap Check",
            "detail": "All recent states are comfortable — verify capacity is growing",
            "response": FAILURE_MODES["comfort_trap"]["response"],
        })

    return alerts


def session_summary(entries):
    """Print a summary of the session."""
    if not entries:
        print("No entries to summarize.")
        return

    vertex_counts = {"T": 0, "I": 0, "A": 0}
    for e in entries:
        vertex_counts[e["vertex"]] += 1

    total = len(entries)
    print("\n--- Session Summary ---")
    print(f"Entries: {total}")
    for v in "TIA":
        pct = (vertex_counts[v] / total) * 100
        bar = "#" * int(pct / 5)
        print(f"  [{v}] {vertex_counts[v]:3d} ({pct:5.1f}%) {bar}")

    transitions = sum(
        1 for i in range(1, len(entries))
        if entries[i]["vertex"] != entries[i - 1]["vertex"]
    )
    print(f"  Transitions: {transitions}")
    if total > 1:
        osc_rate = transitions / (total - 1)
        if osc_rate < 0.3:
            print(f"  Oscillation rate: {osc_rate:.2f} — LOW (possible lock-in)")
        elif osc_rate > 0.85:
            print(f"  Oscillation rate: {osc_rate:.2f} — HIGH (possible chaotic swing)")
        else:
            print(f"  Oscillation rate: {osc_rate:.2f} — healthy range")
    print("---")


def interactive_session():
    """Run an interactive T-I-A tracking session."""
    entries = []
    logfile = f"tension_session_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.json"

    print("Triangular Tension Field — Session Tracker")
    print("=" * 44)
    print()
    for v, desc in VERTICES.items():
        print(f"  [{v}] {desc}")
    print()
    print("Each entry: which vertex are you near? What's the felt state?")
    print("Type 'q' to end, 's' for summary, 'h' for help.")
    print()

    while True:
        vertex = input("Vertex [T/I/A]: ").strip().upper()
        if vertex == "Q":
            break
        if vertex == "S":
            session_summary(entries)
            continue
        if vertex == "H":
            print("  T = grounded in physical reality")
            print("  I = working with model/code/predictions")
            print("  A = making a decision, asserting judgment")
            print("  Felt: frustration, annoyance, anxiety, bad, comfort, flow, good")
            continue
        if vertex not in ("T", "I", "A"):
            print("  Enter T, I, or A (or q/s/h)")
            continue

        note = input("Note (what's happening): ").strip()
        felt = input("Felt state [frustration/annoyance/anxiety/bad/comfort/flow/good]: ").strip().lower()

        entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "vertex": vertex,
            "note": note,
            "felt": felt,
        }
        entries.append(entry)
        print(f"  Logged: [{vertex}] {note}")

        alerts = detect_failures(entries)
        for a in alerts:
            print(f"\n  *** {a['mode']} detected ***")
            print(f"      {a['detail']}")
            print(f"      Response: {a['response']}")
        print()

    session_summary(entries)

    if entries:
        with open(logfile, "w") as f:
            json.dump({"session": logfile, "entries": entries}, f, indent=2)
        print(f"Session saved: {logfile}")


def review_session(path):
    """Review a saved session log."""
    with open(path) as f:
        data = json.load(f)
    entries = data.get("entries", [])
    print(f"Reviewing: {path}")
    for i, e in enumerate(entries):
        print(f"  {i+1}. [{e['vertex']}] {e.get('felt', '')} — {e.get('note', '')}")
    session_summary(entries)
    alerts = detect_failures(entries)
    if alerts:
        print("\nFailure mode alerts:")
        for a in alerts:
            print(f"  {a['mode']}: {a['detail']}")
            print(f"    -> {a['response']}")
    else:
        print("\nNo failure modes detected.")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--review":
        review_session(sys.argv[2])
    else:
        interactive_session()

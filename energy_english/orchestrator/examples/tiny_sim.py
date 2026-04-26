#!/usr/bin/env python3
# energy_english/orchestrator/examples/tiny_sim.py
"""
A minimal sim that follows the orchestrator contract.

Reads JSON config from $ENERGY_ENGLISH_CONFIG, writes a Trajectory JSON
to $ENERGY_ENGLISH_OUTPUT, exits 0 on success.

Use this as a template for wrapping a real sim:

    1. Read the config (parameters / varied_parameters /
       expected_finals / declared_couplings come in via the dict).
    2. Run the sim with those parameters.
    3. Build a dict matching the trajectory_adapter shape.
    4. Write it to the output path.
    5. Exit 0.

This particular sim produces sin/cos traces parameterised by
amplitude and iteration count — useful only for verifying the
plumbing.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

import json
import math
import os
import sys


def main() -> int:
    config_path = os.environ.get("ENERGY_ENGLISH_CONFIG")
    output_path = os.environ.get("ENERGY_ENGLISH_OUTPUT")
    if not config_path or not output_path:
        print(
            "tiny_sim: ENERGY_ENGLISH_CONFIG and ENERGY_ENGLISH_OUTPUT "
            "must be set",
            file=sys.stderr,
        )
        return 2

    with open(config_path) as f:
        config = json.load(f)

    params = config.get("parameters", {})
    n = int(params.get("iterations", 100))
    amp = float(params.get("amplitude", 1.0))

    lock_a = [amp * math.sin(i / 5.0) for i in range(n)]
    lock_b = [amp * math.cos(i / 5.0) for i in range(n)]

    events = []
    for i in range(1, n):
        if lock_a[i - 1] * lock_a[i] < 0:
            events.append({
                "iteration": i,
                "type": "zero_crossing",
                "trace": "lock_A",
            })

    trajectory = {
        "parameters": params,
        "varied_parameters": list(config.get("varied_parameters", [])),
        "traces": {"lock_A": lock_a, "lock_B": lock_b},
        "declared_couplings": [list(c) for c in config.get("declared_couplings", [])],
        "expected_finals": dict(config.get("expected_finals", {})),
        "events": events,
    }

    with open(output_path, "w") as f:
        json.dump(trajectory, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())

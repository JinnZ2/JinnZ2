# energy_english/__main__.py
"""Entry point for ``python -m energy_english``.

Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from energy_english.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

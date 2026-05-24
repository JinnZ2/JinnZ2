#!/usr/bin/env python3
"""
apply_hardening.py

Apply corpus_hardening changes to a JinnZ2 repo.

Run from inside the target repo, or pass --repo-path.

License: CC0. Stdlib only.

Usage:
    python apply_hardening.py \
        --name energy_english \
        --domain formal_grammar \
        --purpose "Verb-first constraint grammar..." \
        --sister differential-frame-core,projection_error_modes \
        --repo-path /path/to/repo

The script is idempotent: it skips files that already exist unless
--force is passed.
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
TEMPLATES = THIS_DIR / "templates"


def _today() -> str:
    return datetime.date.today().isoformat()


def _render(template_text: str, mapping: dict) -> str:
    """Simple {placeholder} substitution. Avoids str.format collisions with
    JSON braces by only substituting known keys."""
    out = template_text
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def _write(target: Path, content: str, force: bool) -> str:
    if target.exists() and not force:
        return f"skip   {target} (exists; use --force to overwrite)"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return f"write  {target}"


def _prepend_readme_header(repo_path: Path, repo_name: str, purpose: str,
                           force: bool) -> str:
    readme = repo_path / "README.md"
    header_tmpl = (TEMPLATES / "README_HEADER.md.template").read_text()
    header = _render(header_tmpl, {
        "repo_name": repo_name,
        "purpose": purpose,
    })
    if not readme.exists():
        readme.write_text(header)
        return f"write  {readme} (new)"
    existing = readme.read_text()
    if "Public domain. CC0. Falsifiable claims." in existing and not force:
        return f"skip   {readme} (header already present)"
    readme.write_text(header + "\n" + existing)
    return f"prepend {readme}"


def apply(repo_path: Path, repo_name: str, domain: str, purpose: str,
          sister_repos: list[str], falsifiability_level: str,
          claim_table_present: bool, force: bool) -> list[str]:
    log: list[str] = []
    mapping = {
        "repo_name": repo_name,
        "domain": domain,
        "purpose": purpose,
        "today": _today(),
        "falsifiability_level": falsifiability_level,
        "claim_table_present": "true" if claim_table_present else "false",
        "sister_repos_json": json.dumps(sister_repos),
        "sister_repos_list": ", ".join(sister_repos) if sister_repos else "(none yet)",
        "one_line_position": f"node in the JinnZ2 lattice, domain={domain}",
    }

    # CITATION.cff
    log.append(_write(
        repo_path / "CITATION.cff",
        _render((TEMPLATES / "CITATION.cff.template").read_text(), mapping),
        force,
    ))

    # metadata.json
    log.append(_write(
        repo_path / "metadata.json",
        _render((TEMPLATES / "metadata.json.template").read_text(), mapping),
        force,
    ))

    # FALSIFIABILITY_NOTICE.txt (no placeholders)
    log.append(_write(
        repo_path / "FALSIFIABILITY_NOTICE.txt",
        (TEMPLATES / "FALSIFIABILITY_NOTICE.txt").read_text(),
        force,
    ))

    # GLOSSARY.md (no placeholders in current template)
    log.append(_write(
        repo_path / "GLOSSARY.md",
        (TEMPLATES / "GLOSSARY.md.template").read_text(),
        force,
    ))

    # ARCHITECTURE.md
    log.append(_write(
        repo_path / "ARCHITECTURE.md",
        _render((TEMPLATES / "ARCHITECTURE.md.template").read_text(), mapping),
        force,
    ))

    # PREDICTION_PROTOCOL.md
    log.append(_write(
        repo_path / "PREDICTION_PROTOCOL.md",
        _render((TEMPLATES / "PREDICTION_PROTOCOL.md.template").read_text(),
                mapping),
        force,
    ))

    # CLAIM_TABLE_VERSIONING.md
    log.append(_write(
        repo_path / "CLAIM_TABLE_VERSIONING.md",
        _render((TEMPLATES / "CLAIM_TABLE_VERSIONING.md.template").read_text(),
                mapping),
        force,
    ))

    # CLAIM_UPDATE_PROCEDURE.md
    log.append(_write(
        repo_path / "CLAIM_UPDATE_PROCEDURE.md",
        _render((TEMPLATES / "CLAIM_UPDATE_PROCEDURE.md.template").read_text(),
                mapping),
        force,
    ))

    # .github/workflows/validate_claims.yml
    log.append(_write(
        repo_path / ".github" / "workflows" / "validate_claims.yml",
        (TEMPLATES / "validate_claims.yml.template").read_text(),
        force,
    ))

    # README header (special handling: prepend rather than overwrite)
    log.append(_prepend_readme_header(repo_path, repo_name, purpose, force))

    return log


def parse_args():
    p = argparse.ArgumentParser(description="Apply corpus hardening to a repo.")
    p.add_argument("--name", required=True, help="Repo name (e.g. energy_english)")
    p.add_argument("--domain", required=True,
                   help="Domain key (e.g. formal_grammar, systems_physics)")
    p.add_argument("--purpose", required=True,
                   help="2-3 sentence purpose for README + metadata")
    p.add_argument("--sister", default="",
                   help="Comma-separated sister-repo names")
    p.add_argument("--falsifiability-level", default="high",
                   choices=["high", "medium", "implicit"])
    p.add_argument("--no-claim-table", action="store_true",
                   help="Set metadata claim_table_present=false")
    p.add_argument("--repo-path", default=".",
                   help="Path to target repo (default: cwd)")
    p.add_argument("--force", action="store_true",
                   help="Overwrite existing files")
    return p.parse_args()


def main():
    args = parse_args()
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.is_dir():
        print(f"error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(2)
    sisters = [s.strip() for s in args.sister.split(",") if s.strip()]
    log = apply(
        repo_path=repo_path,
        repo_name=args.name,
        domain=args.domain,
        purpose=args.purpose,
        sister_repos=sisters,
        falsifiability_level=args.falsifiability_level,
        claim_table_present=not args.no_claim_table,
        force=args.force,
    )
    for line in log:
        print(line)
    print()
    print("Done. Next steps:")
    print("  1. Review GLOSSARY.md and add real term mappings.")
    print("  2. Review ARCHITECTURE.md and fill in the constraint-geometry section.")
    print("  3. Add GitHub topics (see CORPUS_HARDENING/templates/topics_per_repo.md).")
    print("  4. Commit and push.")


if __name__ == "__main__":
    main()

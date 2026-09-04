#!/usr/bin/env python3
"""Discover CadQuery build packages for CI.

A **build package** is a top-level directory that:

1. Contains ``__main__.py`` (runnable as ``uv run python -m <dir>``).
2. Is not shared toolkit / vendor / infrastructure.

Usage (from repo root)::

    python scripts/list_build_packages.py              # JSON array of all packages
    python scripts/list_build_packages.py --changed    # packages affected by git diff
    python scripts/list_build_packages.py --names      # space-separated (shell)

``--changed`` compares against ``BASE_REF`` (default: merge-base with
``origin/main``, or ``HEAD~1`` on push). Rebuilds every package when shared
inputs change (``insertkit/``, ``pyproject.toml``, ``uv.lock``, this script,
or the build workflow).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Top-level dirs that are never CadQuery build packages.
EXCLUDE = frozenset(
    {
        ".git",
        ".github",
        ".venv",
        "insertkit",
        "scripts",
        "vendor",
        "frostpunk",  # OpenSCAD / BIT — out of scope for this CI
    }
)

# Paths whose change forces a rebuild of every discovered package.
GLOBAL_TRIGGERS = (
    "insertkit/",
    "pyproject.toml",
    "uv.lock",
    "scripts/list_build_packages.py",
    ".github/workflows/build.yml",
)


def discover() -> list[str]:
    """Return sorted package names that opt into CI via ``__main__.py``."""
    packages: list[str] = []
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name in EXCLUDE:
            continue
        if (entry / "__main__.py").is_file():
            packages.append(entry.name)
    return packages


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def changed_files(base_ref: str | None, before_sha: str | None = None) -> list[str]:
    """File paths changed relative to *base_ref* or *before_sha*."""
    if base_ref:
        try:
            merge_base = _git("merge-base", base_ref, "HEAD")
        except subprocess.CalledProcessError:
            merge_base = base_ref
        try:
            out = _git("diff", "--name-only", f"{merge_base}...HEAD")
        except subprocess.CalledProcessError:
            out = _git("diff", "--name-only", f"{base_ref}...HEAD")
    elif before_sha and before_sha != "0" * 40:
        try:
            out = _git("diff", "--name-only", before_sha, "HEAD")
        except subprocess.CalledProcessError:
            return ["pyproject.toml"]
    else:
        try:
            out = _git("diff", "--name-only", "HEAD~1", "HEAD")
        except subprocess.CalledProcessError:
            # Shallow / single-commit / new-branch history: full rebuild.
            return ["pyproject.toml"]
    return [line for line in out.splitlines() if line]


def packages_for_changes(packages: list[str], files: list[str]) -> list[str]:
    if any(
        any(f == t or f.startswith(t) for t in GLOBAL_TRIGGERS) for f in files
    ):
        return packages

    affected: list[str] = []
    for pkg in packages:
        prefix = f"{pkg}/"
        if any(f == pkg or f.startswith(prefix) for f in files):
            affected.append(pkg)
    return affected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Only packages affected by the current git diff",
    )
    parser.add_argument(
        "--base-ref",
        default=os.environ.get("BASE_REF") or os.environ.get("GITHUB_BASE_REF"),
        help="Git ref to diff against (env BASE_REF / GITHUB_BASE_REF)",
    )
    parser.add_argument(
        "--before-sha",
        default=os.environ.get("BEFORE_SHA") or os.environ.get("GITHUB_EVENT_BEFORE"),
        help="Previous push SHA (env BEFORE_SHA / GITHUB_EVENT_BEFORE)",
    )
    parser.add_argument(
        "--names",
        action="store_true",
        help="Print space-separated names instead of JSON",
    )
    args = parser.parse_args(argv)

    packages = discover()
    if args.changed:
        base = args.base_ref
        if base and not base.startswith("origin/") and "/" not in base:
            # GITHUB_BASE_REF is bare (e.g. main); prefer remote-tracking.
            remote = f"origin/{base}"
            try:
                _git("rev-parse", "--verify", remote)
                base = remote
            except subprocess.CalledProcessError:
                pass
        files = changed_files(base, args.before_sha)
        packages = packages_for_changes(packages, files)

    if args.names:
        print(" ".join(packages))
    else:
        json.dump(packages, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

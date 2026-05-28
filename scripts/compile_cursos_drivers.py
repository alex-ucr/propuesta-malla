#!/usr/bin/env python3
"""
Compile every driver .tex in Cursos/ (files whose names do not contain "cuerpo").

Runs from the project root, as required by preamble-body.tex and \\input@path:

    latexmk -pdf Cursos/<driver>.tex
    biber <jobname>   # if <jobname>.bcf exists in the project root
    latexmk -pdf Cursos/<driver>.tex
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUROS = ROOT / "Cursos"


def driver_tex_files() -> list[Path]:
    return sorted(
        p
        for p in CUROS.glob("*.tex")
        if "cuerpo" not in p.name.casefold()
    )


def run(cmd: list[str], *, cwd: Path, dry_run: bool) -> int:
    print(">", " ".join(cmd), flush=True)
    if dry_run:
        return 0
    return subprocess.run(cmd, cwd=cwd).returncode


def compile_driver(tex: Path, *, cwd: Path, dry_run: bool) -> int:
    rel = tex.relative_to(cwd)
    jobname = tex.stem
    latexmk = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-file-line-error",
        str(rel),
    ]

    code = run(latexmk, cwd=cwd, dry_run=dry_run)
    if code != 0 and not dry_run:
        return code

    bcf = cwd / f"{jobname}.bcf"
    if bcf.exists():
        code = run(["biber", jobname], cwd=cwd, dry_run=dry_run)
        if code != 0 and not dry_run:
            return code
        code = run(latexmk, cwd=cwd, dry_run=dry_run)

    return code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile Cursos/*.tex drivers (exclude *cuerpo* in the filename).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without running them.",
    )
    parser.add_argument(
        "--continue",
        dest="continue_on_error",
        action="store_true",
        default=True,
        help="Keep compiling after a failure (default).",
    )
    parser.add_argument(
        "--stop-on-error",
        dest="continue_on_error",
        action="store_false",
        help="Stop at the first failed driver.",
    )
    parser.add_argument(
        "--only",
        metavar="GLOB",
        help="Only drivers whose stem contains this substring (case-insensitive).",
    )
    args = parser.parse_args()

    if not args.dry_run:
        for tool in ("latexmk", "pdflatex"):
            if shutil.which(tool) is None:
                print(f"error: '{tool}' not found on PATH", file=sys.stderr)
                return 1

    drivers = driver_tex_files()
    if args.only:
        needle = args.only.casefold()
        drivers = [p for p in drivers if needle in p.stem.casefold()]

    if not drivers:
        print("No driver .tex files matched.", file=sys.stderr)
        return 1

    print(f"Project root: {ROOT}")
    print(f"Drivers to compile ({len(drivers)}):")
    for p in drivers:
        print(f"  {p.name}")

    failed: list[str] = []
    for tex in drivers:
        print(f"\n=== {tex.name} ===")
        code = compile_driver(tex, cwd=ROOT, dry_run=args.dry_run)
        if code != 0:
            failed.append(tex.name)
            if not args.continue_on_error:
                break

    print()
    if failed:
        print(f"Failed ({len(failed)}):", ", ".join(failed))
        return 1
    print(f"OK: {len(drivers)} driver(s) compiled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

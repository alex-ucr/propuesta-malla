#!/usr/bin/env python3
"""
Compile every driver .tex in Cursos/ (files whose names do not contain "cuerpo").

Runs each driver from ``Cursos/`` so ``\\BiblioFile{../Biblio.bib}`` resolves to the
project-root ``Biblio.bib`` (same as ``Cursos/latexmkrc`` and manual compiles):

    cd Cursos && latexmk -pdf <driver>.tex
    biber <jobname>   # if <jobname>.bcf exists in Cursos/
    latexmk -pdf <driver>.tex
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUROS = ROOT / "Cursos"

# Build products that older runs (latexmk from project root) left in ROOT/.
_STALE_ROOT_SUFFIXES = (
    ".aux",
    ".bcf",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".run.xml",
    ".synctex.gz",
)


def _remove_stale_root_artifacts(jobname: str, *, dry_run: bool) -> bool:
    """Drop aux files in ROOT from old root-based latexmk runs; return if any removed."""
    removed = False
    for suf in _STALE_ROOT_SUFFIXES:
        path = ROOT / f"{jobname}{suf}"
        if not path.is_file():
            continue
        removed = True
        if dry_run:
            print(f"  (dry-run) remove stale {path.relative_to(ROOT)}")
        else:
            path.unlink()
            print(f"  removed stale {path.relative_to(ROOT)}")
    if removed and not dry_run:
        fdb = CUROS / f"{jobname}.fdb_latexmk"
        if fdb.is_file():
            fdb.unlink()
            print(f"  reset {fdb.name} (stale bib path from root compile)")
    return removed


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


def compile_driver(tex: Path, *, dry_run: bool, clean: bool = False) -> int:
    """Compile with cwd=Cursos/ so ../Biblio.bib and \\input@path{../} work."""
    jobname = tex.stem
    _remove_stale_root_artifacts(jobname, dry_run=dry_run)
    if clean:
        code = run(["latexmk", "-C", tex.name], cwd=CUROS, dry_run=dry_run)
        if code != 0 and not dry_run:
            return code
    latexmk = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-file-line-error",
        tex.name,
    ]
    latexmk_force = [*latexmk, "-g"]

    first_code = run(latexmk, cwd=CUROS, dry_run=dry_run)
    if dry_run:
        return 0

    bcf = CUROS / f"{jobname}.bcf"
    if bcf.exists():
        if shutil.which("biber") is None:
            print("error: biber not found (required for course bibliographies)", file=sys.stderr)
            return 1
        code = run(["biber", jobname], cwd=CUROS, dry_run=False)
        if code != 0:
            return code
        return run(latexmk_force, cwd=CUROS, dry_run=False)

    return first_code


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
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Run latexmk -C on each driver before building (full clean).",
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
    print(f"Compile cwd:  {CUROS}")
    print(f"Drivers to compile ({len(drivers)}):")
    for p in drivers:
        print(f"  {p.name}")

    failed: list[str] = []
    for tex in drivers:
        print(f"\n=== {tex.name} ===")
        code = compile_driver(tex, dry_run=args.dry_run, clean=args.clean)
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

#!/usr/bin/env python3
"""Rename MA siglas so the first two digits match Ciclo I–X in cuerpo/malla."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUROS = ROOT / "Cursos"

# Apply in order: free targets before reassignment (0881/0882 -> 1081/1082 first).
# Order: free 1081/1082 slots, then reassign; practica pura queda en 0881 (no renombrar 0881 global).
RENAME_CHAIN: list[tuple[str, str]] = [
    ("MA-0882", "MA-1082"),  # seminario aplicada II (antigua sigla)
    ("MA-0780", "MA-0880"),
    ("MA-0783", "MA-0883"),
    ("MA-0782", "MA-0982"),
    ("MA-0784", "MA-0984"),
    ("MA-0781", "MA-0881"),  # práctica pura / aplicada antigua 0781 → ver sync_siglas para aplicada→0883
    ("MA-0609", "MA-0809"),
    ("MA-0709", "MA-0810"),
]

TEXT_GLOBS = ("*.tex", "*.json", "*.html", "*.py", "*.md", "*.bcf", "*.xml")


def _variants(code: str) -> list[str]:
    """MA-0881, MA0881, MA-0881Pura, etc."""
    compact = code.replace("-", "")
    out = {code, compact, code.replace("MA-", "MA")}
    # hypertarget suffixes used in this repo
    for suf in ("Pura", "Aplicada", "SEDPura", "SEDAplicada"):
        out.add(compact + suf)
        out.add(code.replace("-", "") + suf)
    return sorted(out, key=len, reverse=True)


def _replace_in_text(text: str, old: str, new: str) -> str:
    old_c = old.replace("-", "")
    new_c = new.replace("-", "")
    for o in _variants(old):
        n = o.replace(old_c, new_c).replace(old.replace("-", ""), new_c)
        text = text.replace(o, n)
    return text


def _rename_course_files(old_c: str, new_c: str) -> None:
    old_compact = old_c.replace("-", "")
    new_compact = new_c.replace("-", "")
    patterns = [
        f"{old_compact}-*",
        f"{old_compact}.*",
    ]
    seen: set[Path] = set()
    for pat in patterns:
        for path in list(CUROS.glob(pat)) + list(ROOT.glob(pat)):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            new_name = path.name.replace(old_compact, new_compact, 1)
            if new_name != path.name:
                target = path.with_name(new_name)
                if target.exists():
                    print(f"SKIP rename (exists): {target}", file=sys.stderr)
                else:
                    path.rename(target)
                    print(f"Renamed {path.name} -> {new_name}")


def main() -> int:
    for old, new in RENAME_CHAIN:
        print(f"\n=== {old} -> {new} ===")
        _rename_course_files(old, new)
        for pattern in TEXT_GLOBS:
            for path in ROOT.rglob(pattern):
                if any(p in path.parts for p in (".git", "node_modules", "__pycache__")):
                    continue
                if path.name == Path(__file__).name:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                if old.replace("-", "") not in text and old not in text:
                    continue
                updated = _replace_in_text(text, old, new)
                if updated != text:
                    path.write_text(updated, encoding="utf-8")
                    print(f"  updated {path.relative_to(ROOT)}")

    # MA-0361: sigla 03 matches malla ciclo III; cuerpo had Ciclo I.
    c361 = CUROS / "MA0361-algebra-lineal-i-cuerpo.tex"
    if c361.is_file():
        t = c361.read_text(encoding="utf-8")
        t2 = t.replace("\\textbf{Ciclo:} I  ", "\\textbf{Ciclo:} III  ")
        if t2 != t:
            c361.write_text(t2, encoding="utf-8")
            print("\nFixed Ciclo metadata in MA0361-algebra-lineal-i-cuerpo.tex")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

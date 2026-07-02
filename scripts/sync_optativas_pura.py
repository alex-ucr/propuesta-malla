#!/usr/bin/env python3
"""Sync pura.json and aplicada.json Optativas from propuesta-elementos-programas.tex."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAMAS = ROOT / "propuesta-elementos-programas.tex"
INDEX = ROOT / "index.html"
CUERPOS = ROOT / "Cursos"
MALLAS = ("pura", "aplicada")

TITLE_RE = re.compile(r"\\subsection\*\{([^}]+)\}")


def extract_optativas_from_tex() -> list[str]:
    tex = PROGRAMAS.read_text(encoding="utf-8")
    parts = re.split(r"\\subsubsection\{Cursos optativos\}", tex)
    titles: list[str] = []
    for part in parts[1:]:
        block = part.split("\\subsubsection{", 1)[0]
        for stem in re.findall(r"\\input\{Cursos/([^}]+)\}", block):
            cuerpo = CUERPOS / f"{stem}.tex"
            if not cuerpo.exists():
                raise FileNotFoundError(cuerpo)
            m = TITLE_RE.search(cuerpo.read_text(encoding="utf-8"))
            if not m:
                raise ValueError(f"No \\subsection* title in {cuerpo.name}")
            titles.append(m.group(1))
    return titles


def sync_malla(name: str, expected: list[str]) -> bool:
    path = ROOT / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("Optativas", [])

    if current != expected:
        data["Optativas"] = expected
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Updated {path.name} Optativas ({len(current)} -> {len(expected)} courses)")
    else:
        print(f"{path.name} Optativas already matches propuesta ({len(expected)} courses)")
    return True


def main() -> int:
    expected = extract_optativas_from_tex()
    for name in MALLAS:
        sync_malla(name, expected)

    html = INDEX.read_text(encoding="utf-8")
    missing = [t for t in expected if f'"{t}"' not in html]
    if missing:
        print("WARNING: missing in index.html CONFIG maps:", file=sys.stderr)
        for t in missing:
            print(f"  - {t}", file=sys.stderr)
        return 1

    print("index.html has entries for all optativas (pura and aplicada).")
    for i, t in enumerate(expected, 1):
        print(f"  {i}. {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

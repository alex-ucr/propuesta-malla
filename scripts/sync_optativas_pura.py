#!/usr/bin/env python3
"""Sync optativas.json (pura/aplicada) from propuesta-elementos-programas.tex."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAMAS = ROOT / "propuesta-elementos-programas.tex"
OPTATIVAS = ROOT / "optativas.json"
INDEX = ROOT / "index.html"
CUERPOS = ROOT / "Cursos"
MALLAS = ("pura", "aplicada")


TITLE_RE = re.compile(r"\\subsection\*\{([^}]+)\}")
OPTATIVA_HEADERS = (
    "Cursos optativos de núcleo",
    "Cursos optativos temáticos",
    "Cursos optativos",
)


def extract_optativas_from_tex() -> dict[str, list[str]]:
    tex = PROGRAMAS.read_text(encoding="utf-8")
    result: dict[str, list[str]] = {
        "Optativas de núcleo": [],
        "Optativas temáticas": [],
    }
    for header in OPTATIVA_HEADERS:
        pattern = rf"\\subsubsection\{{{re.escape(header)}\}}"
        parts = re.split(pattern, tex)
        key = (
            "Optativas de núcleo"
            if "núcleo" in header
            else "Optativas temáticas"
            if "temáticos" in header
            else None
        )
        if key is None:
            continue
        for part in parts[1:]:
            block = part.split("\\subsubsection{", 1)[0]
            for stem in re.findall(r"\\input\{Cursos/([^}]+)\}", block):
                cuerpo = CUERPOS / f"{stem}.tex"
                if not cuerpo.exists():
                    raise FileNotFoundError(cuerpo)
                m = TITLE_RE.search(cuerpo.read_text(encoding="utf-8"))
                if not m:
                    raise ValueError(f"No \\subsection* title in {cuerpo.name}")
                title = m.group(1)
                if title not in result[key]:
                    result[key].append(title)
    return result


def sync_optativas_json(expected: dict[str, list[str]]) -> bool:
    if OPTATIVAS.exists():
        data = json.loads(OPTATIVAS.read_text(encoding="utf-8"))
    else:
        data = {}
    changed = False
    for name in MALLAS:
        block = data.get(name) or {}
        for key, titles in expected.items():
            if block.get(key) != titles:
                block[key] = titles
                changed = True
        data[name] = block
    if changed:
        OPTATIVAS.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        n = sum(len(v) for v in expected.values())
        print(f"Updated {OPTATIVAS.name} ({n} optativas por malla)")
    else:
        n = sum(len(v) for v in expected.values())
        print(f"{OPTATIVAS.name} already matches propuesta ({n} optativas)")
    return True


def main() -> int:
    expected = extract_optativas_from_tex()
    sync_optativas_json(expected)

    all_titles = expected["Optativas de núcleo"] + expected["Optativas temáticas"]
    html = INDEX.read_text(encoding="utf-8")
    missing = [t for t in all_titles if f'"{t}"' not in html]
    if missing:
        print("WARNING: missing in index.html CONFIG maps:", file=sys.stderr)
        for t in missing:
            print(f"  - {t}", file=sys.stderr)
        return 1

    print("index.html has entries for all optativas.")
    for key, titles in expected.items():
        print(f"\n{key}:")
        for i, t in enumerate(titles, 1):
            print(f"  {i}. {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

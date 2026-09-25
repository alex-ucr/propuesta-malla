#!/usr/bin/env python3
"""Sync optativas.json from propuesta-lista-cursos.tex (OPT-001 / OPT-002 / OPT-003)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTA = ROOT / "propuesta-lista-cursos.tex"
OUT = ROOT / "optativas.json"

KEY_001 = "OPT-001 — Núcleo en matemática pura"
KEY_002 = "OPT-002 — Núcleo en matemática aplicada"
KEY_003 = "OPT-003 — Optativas generales"


def _parse_sections(tex: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    pattern = (
        r"\\subsubsection\*\{([^}]*OPT-00[123][^}]*)\}\s*\n\s*\\begin\{itemize\}"
        r"(.*?)\\end\{itemize\}"
    )
    for m in re.finditer(pattern, tex, re.DOTALL):
        header = m.group(1)
        block = m.group(2)
        titles: list[str] = []
        for item in re.finditer(
            r"\\item\s+(?:\\hyperlink\{[^}]+\}\{([^}]+)\}|\{([^}]+)\})",
            block,
        ):
            titles.append((item.group(1) or item.group(2)).strip())
        if "OPT-001" in header:
            key = KEY_001
        elif "OPT-002" in header:
            key = KEY_002
        else:
            key = KEY_003
        sections[key] = titles
    return sections


def main() -> None:
    tex = LISTA.read_text(encoding="utf-8")
    sections = _parse_sections(tex)
    for k in (KEY_001, KEY_002, KEY_003):
        if k not in sections:
            raise ValueError(f"No se encontró bloque {k} en {LISTA.name}")

    data = {
        "pura": {
            KEY_001: sections[KEY_001],
            KEY_003: sections[KEY_003],
        },
        "aplicada": {
            KEY_002: sections[KEY_002],
            KEY_003: sections[KEY_003],
        },
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.name}")
    for label, titles in sections.items():
        print(f"  {label}: {len(titles)} cursos")


if __name__ == "__main__":
    main()

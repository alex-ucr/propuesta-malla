#!/usr/bin/env python3
"""Build Cursos/metodologia-items-cuerpos.md from *cuerpo*.tex Metodología lists."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Import list helpers from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_contenidos import (  # noqa: E402
    _read_list_env,
    _split_top_level_items,
    _strip_tex_comments,
)

ROOT = Path(__file__).resolve().parent.parent
CUROS = ROOT / "Cursos"
OUT = CUROS / "metodologia-items-cuerpos.md"

MET_START = re.compile(r"\\subsubsection\*\{Metodolog[ií]a\}", re.I)
MET_END = re.compile(r"\\subsubsection\*?\{")


def extract_met_block(text: str) -> str | None:
    m = MET_START.search(text)
    if not m:
        return None
    rest = text[m.end() :]
    m2 = MET_END.search(rest)
    if m2:
        return rest[: m2.start()]
    return rest


def items_from_met_block(block: str) -> list[str]:
    block = _strip_tex_comments(block)
    items: list[str] = []
    i = 0
    while True:
        m = re.search(r"\\begin\{(enumerate|itemize)\}", block[i:])
        if not m:
            break
        start = i + m.start()
        ev = _read_list_env(block, start)
        if ev is None:
            i = start + 1
            continue
        _kind, body, npos = ev
        for it in _split_top_level_items(body):
            t = re.sub(r"\s+", " ", it.strip())
            if t and not re.fullmatch(r"%.*", t):
                items.append(t)
        i = npos
    return items


def main() -> int:
    files = sorted({p.resolve() for p in CUROS.rglob("*cuerpo*.tex")})
    all_items: list[str] = []
    per_file: dict[str, list[str]] = {}
    for fp in files:
        text = fp.read_text(encoding="utf-8")
        blk = extract_met_block(text)
        if blk is None:
            continue
        its = items_from_met_block(blk)
        per_file[fp.name] = its
        all_items.extend(its)

    seen: set[str] = set()
    unique_ordered: list[str] = []
    for it in all_items:
        key = it.casefold().strip()
        if key not in seen:
            seen.add(key)
            unique_ordered.append(it)
    unique_sorted = sorted(unique_ordered, key=lambda s: s.casefold())

    lines: list[str] = []
    lines.append("# Ítems de metodología en archivos `*cuerpo*.tex` (Cursos)")
    lines.append("")
    lines.append(
        "Cada entrada corresponde a un `\\item` de **primer nivel** dentro de "
        "entornos `enumerate` o `itemize` en el bloque entre "
        "`\\subsubsection*{Metodología}` y la siguiente `\\subsubsection*`."
    )
    lines.append("")
    lines.append(
        "Los sub-ítems de listas anidadas quedan dentro del texto del ítem padre "
        "(no se listan por separado)."
    )
    lines.append("")
    lines.append("Los párrafos sin listas (p. ej. MA-0421) no generan entradas aquí.")
    lines.append("")
    lines.append(f"- **Archivos con sección Metodología:** {len(per_file)}")
    lines.append(f"- **Ítems distintos:** {len(unique_sorted)}")
    lines.append("")
    lines.append("## Ítems únicos (orden alfabético)")
    lines.append("")
    for it in unique_sorted:
        lines.append(f"- {it}")
    lines.append("")
    lines.append("## Por archivo")
    lines.append("")
    for name in sorted(per_file.keys()):
        lines.append(f"### `{name}`")
        lines.append("")
        if not per_file[name]:
            lines.append("*(Sin listas enumerate/itemize en el bloque Metodología.)*")
        else:
            for it in per_file[name]:
                lines.append(f"- {it}")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(unique_sorted)} unique, {len(all_items)} total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

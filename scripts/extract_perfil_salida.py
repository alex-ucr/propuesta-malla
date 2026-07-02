#!/usr/bin/env python3
"""
Extract section 5.2.5 (Perfil de salida) from propuesta-perfil-egreso.tex
into perfil-salida.json for the web viewer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "propuesta-perfil-egreso.tex"
OUT = ROOT / "perfil-salida.json"

SUBSECTION_RE = re.compile(
    r"\\subsection\{Perfil de salida\}\s*"
    r"(\\begin\{longtable\}.*?\\end\{longtable\})",
    re.DOTALL,
)
ROW_RE = re.compile(
    r"^(SC|SH|SS)(\d{2})\s*&\s*(Saber Conocer|Saber Hacer|Saber Ser)\s*&\s*(.+?)\\\\ \\hline\s*$",
    re.MULTILINE,
)
INTRO_RE = re.compile(
    r"(Estos componentes se incorporan.*?en Matemática\.)\s*\\subsection\{Perfil de salida\}",
    re.DOTALL,
)


def _read_brace_group(s: str, i: int) -> tuple[str, int] | None:
    if i >= len(s) or s[i] != "{":
        return None
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
    return None


def _strip_tabular(s: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        if s.startswith("\\begin{tabular}", i):
            j = i + len("\\begin{tabular}")
            if j < len(s) and s[j] == "[":
                k = s.find("]", j)
                j = k + 1 if k != -1 else j
            if j < len(s) and s[j] == "{":
                grp = _read_brace_group(s, j)
                if grp:
                    i = grp[1]
                    continue
            i += 1
            continue
        if s.startswith("\\end{tabular}", i):
            i += len("\\end{tabular}")
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def _clean_description(raw: str) -> str:
    s = _strip_tabular(raw.strip())
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?\{[^}]*\}", "", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", "", s)
    s = re.sub(r"-\s*\\\\\s*", "", s)
    s = s.replace("\\\\", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract(tex_path: Path = TEX) -> dict:
    tex = tex_path.read_text(encoding="utf-8")
    m = SUBSECTION_RE.search(tex)
    if not m:
        raise ValueError(f"No se encontró \\subsection{{Perfil de salida}} en {tex_path}")

    intro = ""
    intro_m = INTRO_RE.search(tex)
    if intro_m:
        intro = re.sub(r"\s+", " ", intro_m.group(1).strip())

    table_block = m.group(1)
    items: list[dict[str, str]] = []
    for row in ROW_RE.finditer(table_block):
        prefix, num, tipo, desc_raw = row.groups()
        items.append(
            {
                "codigo": f"{prefix}{num}",
                "tipo": tipo.strip(),
                "descripcion": _clean_description(desc_raw),
            }
        )

    if not items:
        raise ValueError("No se extrajeron filas del cuadro de perfil de salida")

    grupos: list[dict] = []
    orden_tipos = ["Saber Conocer", "Saber Hacer", "Saber Ser"]
    for tipo in orden_tipos:
        subset = [it for it in items if it["tipo"] == tipo]
        if subset:
            grupos.append(
                {
                    "tipo": tipo,
                    "prefijo": subset[0]["codigo"][:2],
                    "items": subset,
                }
            )

    return {
        "titulo": "Perfil de salida",
        "seccion": "5.2.5",
        "capitulo": "Perfil de Egreso",
        "introduccion": intro,
        "columnas": ["Código", "Tipo del saber", "Descripción del saber"],
        "fuente": tex_path.name,
        "items": items,
        "grupos": grupos,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Perfil de salida to JSON")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUT,
        help=f"Output JSON path (default: {OUT.name})",
    )
    parser.add_argument(
        "--tex",
        type=Path,
        default=TEX,
        help=f"Source TeX file (default: {TEX.name})",
    )
    args = parser.parse_args()

    data = extract(args.tex)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(data['items'])} items to {args.output}")
    for g in data["grupos"]:
        print(f"  {g['tipo']}: {len(g['items'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Extract perfil de egreso tables from perfil-salida.tex into perfil-egreso-propuesta.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERFIL_TEX = ROOT / "perfil-salida.tex"
OUT = ROOT / "perfil-egreso-propuesta.json"

DIM_FROM_CAPTION = {
    "declarativa": "Saber Conocer",
    "procedimental": "Saber Hacer",
    "actitudinal": "Saber Ser",
}

DIM_FROM_CODE = {
    "CD": "Saber Conocer",
    "CP": "Saber Hacer",
    "CA": "Saber Ser",
}


def _clean_cell(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r"\\cellcolor\[[^\]]*\]\{[^}]*\}", "", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\cite\{[^}]*\}", "", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", "", s)
    s = s.replace("---", "—")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _dimension(caption: str, codigo: str) -> str:
    cf = caption.casefold()
    for key, dim in DIM_FROM_CAPTION.items():
        if key in cf:
            return dim
    prefix = re.match(r"([A-Z]+)", codigo)
    if prefix:
        p = prefix.group(1)[:2]
        if p in DIM_FROM_CODE:
            return DIM_FROM_CODE[p]
    return "Saber Conocer"


def extract_perfil_salida(tex: str) -> tuple[str, list[dict]]:
    sec_m = re.search(r"\\section\{Perfil de egreso\}\s*(.*?)(?=\\subsubsection|\Z)", tex, re.DOTALL)
    intro = ""
    if sec_m:
        intro = re.sub(r"\s+", " ", sec_m.group(1).strip())
        intro = re.sub(r"%.*", "", intro).strip()

    bloques: list[dict] = []
    sub_re = re.compile(r"\\subsubsection\{([^}]+)\}(.*?)(?=\\subsubsection|\Z)", re.DOTALL)
    for sm in sub_re.finditer(tex):
        titulo = sm.group(1).strip()
        body = sm.group(2)
        block_intro = ""
        intro_m = re.match(r"^\s*(En adición.*?\.)\s*", body, re.DOTALL | re.IGNORECASE)
        if intro_m:
            block_intro = re.sub(r"\s+", " ", intro_m.group(1).strip())

        tablas: list[dict] = []
        for chunk in re.split(r"(?=\\begin\{table\})", body):
            if not chunk.strip().startswith("\\begin{table}"):
                continue
            tab_m = re.search(
                r"\\begin\{tabular\}.*?\n(.*?)\\end\{tabular\}.*?\\caption\{([^}]*)\}",
                chunk,
                re.DOTALL,
            )
            if not tab_m:
                continue
            tab_body, caption = tab_m.group(1), tab_m.group(2)
            items: list[dict] = []
            for row in re.finditer(
                r"^([A-Z]{2,3}\d{2})\s*&\s*(.+?)\\\\",
                tab_body,
                re.MULTILINE,
            ):
                codigo, desc = row.group(1), row.group(2)
                items.append(
                    {
                        "codigo": codigo,
                        "descripcion": _clean_cell(desc),
                    }
                )
            if items:
                tablas.append(
                    {
                        "dimension": _dimension(caption, items[0]["codigo"]),
                        "caption": _clean_cell(caption),
                        "items": items,
                    }
                )

        slug = re.sub(r"[^a-z0-9]+", "-", titulo.casefold()).strip("-")[:40]
        slug = f"{slug}-{len(bloques) + 1}"
        bloques.append(
            {
                "id": slug or f"bloque-{len(bloques) + 1}",
                "titulo": titulo,
                "introduccion": block_intro,
                "tablas": tablas,
            }
        )

    return intro, bloques


def main() -> int:
    if not PERFIL_TEX.is_file():
        print("Missing perfil-salida.tex", file=sys.stderr)
        return 1

    perfil_tex = PERFIL_TEX.read_text(encoding="utf-8")
    intro, bloques = extract_perfil_salida(perfil_tex)

    data = {
        "titulo": "Perfil de egreso",
        "capitulo": "Perfil de Egreso",
        "fuente": ["perfil-salida.tex"],
        "introduccion": intro,
        "bloques": bloques,
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(bloques)} bloques")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

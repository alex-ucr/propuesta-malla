#!/usr/bin/env python3
"""
Generate cursos_perfil.md: mandatory courses vs Perfil de Salida saberes.

Mandatory courses = all entries in pura.json / aplicada.json except Optativas.
Mappings live in scripts/cursos_perfil_data.json (curated).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "cursos_perfil_data.json"
PERFIL = ROOT / "perfil-salida.json"
OUT = ROOT / "cursos_perfil.md"
PURA = ROOT / "pura.json"
APLICADA = ROOT / "aplicada.json"


def _obligatorios(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for key, val in data.items():
        if key == "Optativas" or not isinstance(val, list):
            continue
        out.extend(val)
    return out


def _enfasis_label(e: str) -> str:
    return {"ambos": "Pura y aplicada", "pura": "Pura", "aplicada": "Aplicada"}.get(e, e)


def main() -> None:
    mapping = json.loads(DATA.read_text(encoding="utf-8"))
    perfil = json.loads(PERFIL.read_text(encoding="utf-8"))
    saber_desc = {it["codigo"]: it["descripcion"] for it in perfil["items"]}

    oblig_pura = set(_obligatorios(PURA))
    oblig_aplicada = set(_obligatorios(APLICADA))
    oblig_union = oblig_pura | oblig_aplicada

    mapped_titles = {m["titulo"] for m in mapping}
    missing = sorted(oblig_union - mapped_titles)
    extra = sorted(mapped_titles - oblig_union)

    lines: list[str] = [
        "# Cursos obligatorios y Perfil de Salida",
        "",
        "Relación entre los **cursos obligatorios** de la malla curricular "
        "(todos los ciclos excepto Optativas en `pura.json` y `aplicada.json`) "
        "y los saberes del **Perfil de salida** (sección 5.2.5 de la propuesta).",
        "",
        "Leyenda de énfasis: **Pura y aplicada** = presente en ambas mallas; "
        "**Pura** / **Aplicada** = obligatorio solo en esa malla.",
        "",
        "| Sigla | Curso | Énfasis | Saberes del perfil |",
        "|-------|-------|---------|-------------------|",
    ]

    for row in sorted(mapping, key=lambda r: (r["sigla"], r["titulo"])):
        saberes = ", ".join(row["saberes"])
        nombre = row["nombre_corto"]
        if row["titulo"] != f"{row['sigla']} {nombre}":
            nombre = row["titulo"].split(" ", 1)[1] if " " in row["titulo"] else nombre
        lines.append(
            f"| {row['sigla']} | {nombre} | {_enfasis_label(row['enfasis'])} | {saberes} |"
        )

    lines.extend(
        [
            "",
            "## Referencia de saberes",
            "",
            "Descripciones completas en [`perfil-salida.json`](perfil-salida.json) "
            "y la página [`perfil-salida.html`](perfil-salida.html).",
            "",
        ]
    )

    for tipo in ("Saber Conocer", "Saber Hacer", "Saber Ser"):
        items = [it for it in perfil["items"] if it["tipo"] == tipo]
        if not items:
            continue
        lines.append(f"### {tipo}")
        lines.append("")
        for it in items:
            desc = it["descripcion"]
            if len(desc) > 120:
                desc = desc[:117] + "…"
            lines.append(f"- **{it['codigo']}**: {desc}")
        lines.append("")

    lines.extend(
        [
            "## Notas",
            "",
            "- Las asociaciones reflejan la **contribución principal** de cada curso "
            "a los saberes, según objetivos y contenidos de los programas (`Cursos/*-cuerpo.tex`).",
            "- Los cursos optativos no se incluyen en esta tabla.",
            f"- Cursos obligatorios en las mallas: {len(oblig_union)}; filas en la tabla: {len(mapping)}.",
        ]
    )

    if missing:
        lines.append(f"- **Pendiente de mapear:** {', '.join(missing)}.")
    if extra:
        lines.append(f"- **En datos pero no en mallas actuales:** {', '.join(extra)}.")

    lines.append("")
    lines.append(
        "Para regenerar: `python scripts/generate_cursos_perfil_md.py` "
        "(editar `scripts/cursos_perfil_data.json` si cambia la malla o el criterio)."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    root_json = ROOT / "cursos_perfil_data.json"
    root_json.write_text(DATA.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {OUT.name} ({len(mapping)} courses)")
    print(f"Synced {root_json.name}")


if __name__ == "__main__":
    main()

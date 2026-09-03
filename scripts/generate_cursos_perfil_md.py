#!/usr/bin/env python3
"""
Generate cursos_perfil.md: mandatory courses vs Perfil de Salida saberes.

Mandatory courses = all entries in pura.json / aplicada.json except Optativas.
Mappings live in scripts/cursos_perfil_data.json (curated).
Course metadata (año, ciclo, créditos, etc.) is extracted from Cursos/*-cuerpo.tex.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / "cursos_perfil_data.json"
PERFIL = ROOT / "perfil-salida.json"
OUT = ROOT / "cursos_perfil.md"
OUT_JSON = ROOT / "cursos_perfil_data.json"
PURA = ROOT / "pura.json"
APLICADA = ROOT / "aplicada.json"
CUROS = ROOT / "Cursos"

# Códigos de la malla aplicada que comparten programa con otro curso.
SIGLA_ALIASES: dict[str, str] = {
    "MA-0261": "MA-0361",
    "MA-0541": "MA-0641",
    "MA-0615": "MA-0515",
    "MA-0625": "MA-0705",
}


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


def _clean_latex(value: str) -> str:
    value = re.sub(r"\\\\\s*&", " ", value)
    value = re.sub(r"\\\\", " ", value)
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _extract_table_field(block: str, label: str) -> str | None:
    pattern = rf"\\textbf\{{{re.escape(label)}:\}}\s*(.*?)(?=\\textbf\{{|\\hline|\Z)"
    match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    value = re.sub(r"\s*&\s*$", "", match.group(1))
    value = _clean_latex(value)
    return value or None


def _extract_horas_presenciales(block: str) -> str | None:
    value = _extract_table_field(block, "Horas presenciales por semana")
    if value:
        return value
    malformed = re.search(
        r"\\textbf\{Horas presenciales por semana:\s*([^}]+)\}",
        block,
        re.IGNORECASE,
    )
    if malformed:
        value = _clean_latex(malformed.group(1))
        return value or None
    return _extract_table_field(block, "Horas semanales")


def _parse_cuerpo_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    table_match = re.search(
        r"\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}",
        text,
        re.DOTALL,
    )
    block = table_match.group(1) if table_match else text[:2500]

    creditos_raw = _extract_table_field(block, "Créditos")
    creditos: int | str | None
    if creditos_raw and creditos_raw.isdigit():
        creditos = int(creditos_raw)
    else:
        creditos = creditos_raw

    return {
        "año": _extract_table_field(block, "Año"),
        "ciclo": _extract_table_field(block, "Ciclo"),
        "tipo_curso": _extract_table_field(block, "Tipo de curso"),
        "creditos": creditos,
        "requisitos": _extract_table_field(block, "Requisitos"),
        "correquisitos": _extract_table_field(block, "Correquisitos"),
        "horas_presenciales_semana": _extract_horas_presenciales(block),
        "horas_trabajo_independiente": _extract_table_field(
            block, "Horas de trabajo independiente por semana"
        ),
    }


def _build_cuerpo_index() -> tuple[dict[str, Path], dict[str, Path]]:
    by_sigla: dict[str, Path] = {}
    by_titulo: dict[str, Path] = {}
    for path in sorted(CUROS.glob("*-cuerpo.tex")):
        if "propuesta" in path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"\\subsection\*\{([^}]+)\}", text)
        if not title_match:
            continue
        titulo = title_match.group(1).strip()
        sigla = titulo.split(" ", 1)[0]
        by_sigla[sigla] = path
        by_titulo[titulo] = path
    return by_sigla, by_titulo


def _cuerpo_path_for_row(
    row: dict[str, Any],
    by_sigla: dict[str, Path],
    by_titulo: dict[str, Path],
) -> Path | None:
    titulo = row["titulo"]
    sigla = row["sigla"]
    if titulo in by_titulo:
        return by_titulo[titulo]
    if sigla in by_sigla:
        return by_sigla[sigla]
    alias = SIGLA_ALIASES.get(sigla)
    if alias and alias in by_sigla:
        return by_sigla[alias]
    return None


def _enrich_mapping(
    mapping: list[dict[str, Any]],
    by_sigla: dict[str, Path],
    by_titulo: dict[str, Path],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in mapping:
        out = dict(row)
        cuerpo_path = _cuerpo_path_for_row(row, by_sigla, by_titulo)
        out.update(_parse_cuerpo_metadata(cuerpo_path) if cuerpo_path else {})
        enriched.append(out)
    return enriched


def main() -> None:
    mapping = json.loads(DATA.read_text(encoding="utf-8"))
    by_sigla, by_titulo = _build_cuerpo_index()
    enriched = _enrich_mapping(mapping, by_sigla, by_titulo)
    perfil = json.loads(PERFIL.read_text(encoding="utf-8"))

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
        "(editar `scripts/cursos_perfil_data.json` para saberes; "
        "metadatos del curso se leen de `Cursos/*-cuerpo.tex`)."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    missing_meta = sum(1 for row in enriched if row.get("creditos") is None)
    print(f"Wrote {OUT.name} ({len(mapping)} courses)")
    print(f"Wrote {OUT_JSON.name} with course metadata")
    if missing_meta:
        print(f"  {missing_meta} course(s) without metadata from Cursos/*-cuerpo.tex")


if __name__ == "__main__":
    main()

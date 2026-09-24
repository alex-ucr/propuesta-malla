#!/usr/bin/env python3
"""
Actualizar filas MA en malla-curricular-tablas.tex desde pura/aplicada.json y cuerpos.

Por defecto solo reemplaza cursos con sigla MA (metadatos: nombre, horas, créditos,
requisitos). Filas fijas (EF-, EG-, Humanidades, SR-, LM-, OPT-, CA-, etc.) no se tocan.

Si el archivo de salida no existe o no usa el formato \\MallaTabularBegin, genera tablas
longtable completas (solo cursos presentes en los JSON; uso legado).
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from generate_cursos_perfil_md import (
    CUROS,
    ROOT,
    SIGLA_ALIASES,
    _build_cuerpo_index,
    _cuerpo_path_for_row,
    _parse_cuerpo_metadata,
)

PERFIL_DATA = ROOT / "cursos_perfil_data.json"
PURA = ROOT / "pura.json"
APLICADA = ROOT / "aplicada.json"
OUT = ROOT / "malla-curricular-tablas.tex"

CICLO_NUM: dict[str, int] = {
    "I Ciclo": 1,
    "II Ciclo": 2,
    "III Ciclo": 3,
    "IV Ciclo": 4,
    "V Ciclo": 5,
    "VI Ciclo": 6,
    "VII Ciclo": 7,
    "VIII Ciclo": 8,
    "IX Ciclo": 9,
    "X Ciclo": 10,
}
COMMON_CYCLES = ("I Ciclo", "II Ciclo", "III Ciclo")
EMPHASIS_CYCLES = ("IV Ciclo", "V Ciclo", "VI Ciclo", "VII Ciclo", "VIII Ciclo")
ALL_CYCLES = tuple(CICLO_NUM.keys())
RowKey = tuple[int, str, str | None]

LATEX_SPECIAL = str.maketrans({
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
})


def _latex_escape(text: str) -> str:
    return text.translate(LATEX_SPECIAL)


def _sigla_compact(sigla: str) -> str:
    return sigla.replace("-", "")


def _course_name(title: str, meta: dict[str, Any]) -> str:
    if meta.get("nombre_corto"):
        return str(meta["nombre_corto"])
    parts = title.split(" ", 1)
    return parts[1] if len(parts) > 1 else title


def _lookup_meta(
    title: str,
    by_titulo: dict[str, dict[str, Any]],
    by_sigla: dict[str, dict[str, Any]],
    cuerpo_by_sigla: dict[str, Path],
    cuerpo_by_titulo: dict[str, Path],
) -> dict[str, Any]:
    sigla = title.split(" ", 1)[0]
    if title in by_titulo:
        return dict(by_titulo[title])
    if sigla in by_sigla:
        return dict(by_sigla[sigla])

    row = {"titulo": title, "sigla": sigla}
    cuerpo = _cuerpo_path_for_row(row, cuerpo_by_sigla, cuerpo_by_titulo)
    if cuerpo:
        meta = _parse_cuerpo_metadata(cuerpo)
        meta["titulo"] = title
        meta["sigla"] = sigla
        meta["nombre_corto"] = _course_name(title, meta)
        return meta
    return {"titulo": title, "sigla": sigla, "nombre_corto": _course_name(title, {})}


def _malla_sigla_cell(title: str, sigla_compact: str) -> str:
    """Clickable sigla targeting the \\hypertarget of the course program."""
    raw_sigla = title.split(" ", 1)[0]
    dest = SIGLA_ALIASES.get(raw_sigla, raw_sigla).replace("-", "")
    title_cf = title.casefold()
    if "estudios dirigidos" in title_cf and dest == "MA0781":
        dest = "MA0781SEDAplicada" if "aplicada" in title_cf else "MA0781SEDPura"
    elif dest == "MA0881" and "estudios dirigidos" in title_cf:
        dest = "MA0881Aplicada" if "aplicada" in title_cf else "MA0881Pura"
    elif "práctica profesional en matemática pura" in title_cf:
        dest = "MA0781Pura"
    elif "práctica profesional en matemática aplicada" in title_cf:
        dest = "MA0781Aplicada"
    if dest == sigla_compact:
        return rf"\MallaSigla{{{sigla_compact}}}"
    return rf"\MallaSigla[{dest}]{{{sigla_compact}}}"


def _split_horas(meta: dict[str, Any]) -> tuple[str, str, str, str]:
    hp_raw = meta.get("horas_presenciales_semana")
    ti_raw = meta.get("horas_trabajo_independiente")
    tipo = unicodedata.normalize("NFKD", str(meta.get("tipo_curso") or ""))
    tipo = "".join(ch for ch in tipo if not unicodedata.combining(ch)).lower()

    t = p = l = tp = ""
    if isinstance(hp_raw, str) and hp_raw.isdigit():
        h = int(hp_raw)
        if "teorico-practico" in tipo:
            t_val = max(h - 2, 1)
            t, p = str(t_val), str(h - t_val)
        elif "practico" in tipo and "teorico" not in tipo:
            p = str(h)
        else:
            t = str(h)
    elif isinstance(hp_raw, str) and hp_raw.strip():
        hp_text = hp_raw.strip()
        if "practico" in tipo and "teorico" not in tipo:
            p = hp_text
        else:
            t = hp_text

    if isinstance(ti_raw, str) and ti_raw.strip():
        tp = ti_raw.strip()
    return t, p, l, tp


def _credito_cell(meta: dict[str, Any]) -> str:
    creditos = meta.get("creditos")
    if creditos is None:
        return ""
    return str(creditos)


def _cycle_credits(courses: list[tuple[str, dict[str, Any]]]) -> int:
    total = 0
    for _, meta in courses:
        creditos = meta.get("creditos")
        if isinstance(creditos, int):
            total += creditos
    return total


def _table_rows(cycle_courses: list[tuple[int, str, dict[str, Any]]]) -> list[str]:
    rows: list[str] = []
    current_cycle: int | None = None
    cycle_buffer: list[tuple[int, str, dict[str, Any]]] = []

    def flush_cycle() -> None:
        nonlocal cycle_buffer, current_cycle
        if not cycle_buffer:
            return
        creditos_ciclo = _cycle_credits([(t, m) for _, t, m in cycle_buffer])
        rows.append(
            rf"\multicolumn{{10}}{{|l|}}{{\textit{{Créditos ciclo {current_cycle}: {creditos_ciclo}}}}} \\"
        )
        rows.append(r"\hline")
        cycle_buffer = []

    for ciclo_num, title, meta in cycle_courses:
        if current_cycle is not None and ciclo_num != current_cycle:
            flush_cycle()
        current_cycle = ciclo_num
        cycle_buffer.append((ciclo_num, title, meta))

        sigla = _latex_escape(_sigla_compact(str(meta.get("sigla", title.split()[0]))))
        nombre = _latex_escape(str(meta.get("nombre_corto") or _course_name(title, meta)).upper())
        t, p, l, tp = _split_horas(meta)
        cred = _latex_escape(_credito_cell(meta))
        req = _latex_escape(str(meta.get("requisitos") or ""))
        cor = _latex_escape(str(meta.get("correquisitos") or ""))
        if req.lower() == "ninguno":
            req = ""
        if cor.lower() == "ninguno":
            cor = ""

        rows.append(
            " & ".join(
                [
                    str(ciclo_num),
                    _malla_sigla_cell(title, sigla),
                    nombre,
                    _latex_escape(t),
                    _latex_escape(p),
                    _latex_escape(l),
                    _latex_escape(tp),
                    cred,
                    req,
                    cor,
                ]
            )
            + r" \\"
        )
        rows.append(r"\hline")

    flush_cycle()
    return rows


def _parse_sigla_cell(sigla_cell: str) -> tuple[str | None, str]:
    m = re.match(r"\\MallaSigla(?:\[([^\]]+)\])?\{([^}]+)\}", sigla_cell.strip())
    if not m:
        return None, sigla_cell.strip()
    return m.group(1), m.group(2)


def _is_course_data_row(line: str) -> bool:
    s = line.strip()
    return bool(re.match(r"^\d+ & ", s)) and s.endswith(r"\\")


def _is_ma_malla_row(sigla_cell: str) -> bool:
    _, compact = _parse_sigla_cell(sigla_cell)
    return compact.startswith("MA")


def _normalize_legacy_dest(dest: str | None, compact: str, nombre: str) -> str | None:
    """Map old hypertarget names in the .tex file to current JSON/cuerpo keys."""
    nf = nombre.casefold()
    if dest == "MA0781SED" or (compact == "MA0781" and "estudios dirigidos" in nf):
        return "MA0781SEDAplicada" if "aplicada" in nf else "MA0781SEDPura"
    if compact == "MA0881" and "estudios dirigidos" in nf:
        return "MA0881Aplicada" if "aplicada" in nf else "MA0881Pura"
    return dest


def _row_key(cycle: int, sigla_cell: str, nombre: str = "") -> RowKey | None:
    dest, compact = _parse_sigla_cell(sigla_cell)
    if not compact.startswith("MA"):
        return None
    dest = _normalize_legacy_dest(dest, compact, nombre)
    return (cycle, compact, dest)


def _format_malla_course_row(ciclo_num: int, title: str, meta: dict[str, Any]) -> str:
    raw_sigla = str(meta.get("sigla") or title.split()[0])
    compact = _sigla_compact(raw_sigla)
    sigla_cell = _malla_sigla_cell(title, compact)
    nombre = _latex_escape(str(meta.get("nombre_corto") or _course_name(title, meta)).upper())
    t, p, l, tp = _split_horas(meta)
    cred = _latex_escape(_credito_cell(meta))
    req = _latex_escape(str(meta.get("requisitos") or ""))
    cor = _latex_escape(str(meta.get("correquisitos") or ""))
    if req.lower() == "ninguno":
        req = ""
    if cor.lower() == "ninguno":
        cor = ""
    return (
        f"{ciclo_num} & {sigla_cell} & {nombre} & "
        f"{_latex_escape(t)} & {_latex_escape(p)} & {_latex_escape(l)} & {_latex_escape(tp)} & "
        f"{cred} & {req} & {cor} \\\\"
    )


def _build_ma_row_updates(
    mallas: list[dict[str, list[str]]],
    by_titulo: dict[str, dict[str, Any]],
    by_sigla: dict[str, dict[str, Any]],
    cuerpo_by_sigla: dict[str, Path],
    cuerpo_by_titulo: dict[str, Path],
) -> dict[RowKey, str]:
    updates: dict[RowKey, str] = {}
    for malla in mallas:
        for ciclo_key in ALL_CYCLES:
            ciclo_num = CICLO_NUM[ciclo_key]
            for title in malla.get(ciclo_key, []):
                if not title.startswith("MA-"):
                    continue
                meta = _lookup_meta(
                    title, by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo
                )
                compact = _sigla_compact(str(meta.get("sigla", title.split()[0])))
                sigla_cell = _malla_sigla_cell(title, compact)
                dest, _ = _parse_sigla_cell(sigla_cell)
                key: RowKey = (ciclo_num, compact, dest)
                updates[key] = _format_malla_course_row(ciclo_num, title, meta)
    return updates


def _lookup_row_update(updates: dict[RowKey, str], key: RowKey) -> str | None:
    if key in updates:
        return updates[key]
    cycle, compact, dest = key
    if dest is not None and (cycle, compact, None) in updates:
        return updates[(cycle, compact, None)]
    matches = [v for k, v in updates.items() if k[0] == cycle and k[1] == compact]
    if len(matches) == 1:
        return matches[0]
    return None


def _patch_malla_tex(content: str, updates: dict[RowKey, str]) -> tuple[str, int]:
    lines = content.splitlines()
    patched = 0
    for i, line in enumerate(lines):
        if not _is_course_data_row(line):
            continue
        body = line.strip()
        if body.endswith(r"\\"):
            body = body[: -len(r"\\")].strip()
        parts = [p.strip() for p in body.split("&", 9)]
        if len(parts) != 10:
            continue
        try:
            cycle = int(parts[0])
        except ValueError:
            continue
        sigla_cell = parts[1]
        if not _is_ma_malla_row(sigla_cell):
            continue
        key = _row_key(cycle, sigla_cell, parts[2])
        if key is None:
            continue
        new_line = _lookup_row_update(updates, key)
        if new_line is None:
            continue
        lines[i] = new_line
        patched += 1
    trailing = "\n" if content.endswith("\n") else ""
    return "\n".join(lines) + trailing, patched


def _collect_rows(
    malla: dict[str, list[str]],
    cycles: tuple[str, ...],
    by_titulo: dict[str, dict[str, Any]],
    by_sigla: dict[str, dict[str, Any]],
    cuerpo_by_sigla: dict[str, Path],
    cuerpo_by_titulo: dict[str, Path],
) -> list[tuple[int, str, dict[str, Any]]]:
    out: list[tuple[int, str, dict[str, Any]]] = []
    for ciclo_key in cycles:
        ciclo_num = CICLO_NUM[ciclo_key]
        for title in malla.get(ciclo_key, []):
            meta = _lookup_meta(title, by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo)
            out.append((ciclo_num, title, meta))
    return out


def _table_preamble() -> list[str]:
    return [
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.15}",
        r"\begin{longtable}{|c|l|>{\raggedright\arraybackslash}p{4.6cm}|",
        r"c|c|c|c|c|>{\raggedright\scriptsize\arraybackslash}p{3.3cm}|",
        r">{\raggedright\scriptsize\arraybackslash}p{2.5cm}|}",
        r"\hline",
        r"\textbf{Ciclo} & \textbf{Curso} & \textbf{Nombre del curso} &",
        r"\multicolumn{4}{c|}{\textbf{Horas}} & \textbf{Cred.} &",
        r"\shortstack{Requisitos y\\ Req. Equivalentes} &",
        r"\shortstack{Correquisitos y\\ Correq. Equivalentes} \\",
        r"\cline{4-7}",
        r" &  &  & \textbf{T} & \textbf{P} & \textbf{L} & \textbf{TP} &  &  &  \\",
        r"\hline",
        r"\endfirsthead",
        r"\multicolumn{10}{c}{\textit{(continúa en la página siguiente)}} \\",
        r"\endhead",
        r"\hline",
        r"\multicolumn{10}{|r|}{\textit{Continúa...}} \\",
        r"\endfoot",
        r"\hline",
        r"\endlastfoot",
    ]


def _render_table(title: str, rows: list[str], total_label: str, total_credits: int) -> list[str]:
    if not rows:
        return []
    lines = [rf"\subsubsection*{{{title}}}", ""]
    lines.extend(_table_preamble())
    lines.extend(rows)
    lines.append(
        rf"\multicolumn{{10}}{{|r|}}{{\textbf{{{total_label}: {total_credits}}}}} \\"
    )
    lines.append(r"\end{longtable}")
    lines.append(r"\endgroup")
    lines.append("")
    return lines


def main() -> None:
    perfil_rows = json.loads(PERFIL_DATA.read_text(encoding="utf-8"))
    pura = json.loads(PURA.read_text(encoding="utf-8"))
    aplicada = json.loads(APLICADA.read_text(encoding="utf-8"))

    by_titulo = {row["titulo"]: row for row in perfil_rows}
    by_sigla = {row["sigla"]: row for row in perfil_rows}
    cuerpo_by_sigla, cuerpo_by_titulo = _build_cuerpo_index()

    ma_updates = _build_ma_row_updates(
        [pura, aplicada], by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo
    )
    if OUT.exists():
        content = OUT.read_text(encoding="utf-8")
        if r"\MallaTabularBegin" in content:
            new_content, patched = _patch_malla_tex(content, ma_updates)
            OUT.write_text(new_content, encoding="utf-8")
            print(f"Patched {patched} MA course row(s) in {OUT.name}")
            print(f"  ({len(ma_updates)} MA course definitions from JSON / cuerpos)")
            return

    common_rows_data = _collect_rows(
        pura, COMMON_CYCLES, by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo
    )
    pura_rows_data = _collect_rows(
        pura, EMPHASIS_CYCLES, by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo
    )
    aplicada_rows_data = _collect_rows(
        aplicada, EMPHASIS_CYCLES, by_titulo, by_sigla, cuerpo_by_sigla, cuerpo_by_titulo
    )

    lines: list[str] = [
        "% =============================================================================",
        "% Tablas de malla curricular (generado automáticamente).",
        "% Regenerar: python scripts/generate_malla_tablas_tex.py",
        "% Modelo: Documentos/bach.-y-lic.-en-matematicas,-plan-2.pdf",
        "% =============================================================================",
        "",
        r"\subsection{Malla curricular obligatoria propuesta}",
        "",
        "Las tablas siguen el formato del plan de estudios SAE de la UCR "
        "(ciclo, sigla, nombre, horas T/P/L/TP, créditos, requisitos y correquisitos). "
        "Los ciclos I a III son idénticos en ambos énfasis; a partir del ciclo IV "
        "se presentan tablas separadas.",
        "",
    ]

    common_total = _cycle_credits([(t, m) for _, t, m in common_rows_data])
    pura_total = common_total + _cycle_credits([(t, m) for _, t, m in pura_rows_data])
    aplicada_total = common_total + _cycle_credits([(t, m) for _, t, m in aplicada_rows_data])

    lines.extend(
        _render_table(
            "Bloque común (ciclos I a III)",
            _table_rows(common_rows_data),
            "Total créditos bloque común",
            common_total,
        )
    )
    lines.extend(
        _render_table(
            "Énfasis en Matemática Pura (ciclos IV a VIII)",
            _table_rows(pura_rows_data),
            "Total créditos énfasis pura (incluye bloque común)",
            pura_total,
        )
    )
    lines.extend(
        _render_table(
            "Énfasis en Matemática Aplicada (ciclos IV a VIII)",
            _table_rows(aplicada_rows_data),
            "Total créditos énfasis aplicada (incluye bloque común)",
            aplicada_total,
        )
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.name}")
    print(f"  Bloque común: {common_total} créditos")
    print(f"  Énfasis pura (total): {pura_total} créditos")
    print(f"  Énfasis aplicada (total): {aplicada_total} créditos")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Regenerate malla-curricular-tablas.tex from 210401-3 Pura/Aplicada xlsx."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos")
OUT = ROOT / "malla-curricular-tablas.tex"

SKIP_SIGLAS = {
    "NIVEL Y SIGLA",
    "PRIMER AÑO",
    "SEGUNDO AÑO",
    "TERCER AÑO",
    "CUARTO AÑO",
    "QUINTO AÑO",
    "SEXTO AÑO",
}

SIGLA_LINK: dict[str, str] = {
    "CA-0204": "CA0203",
    "CA-0411": "CA0411AnalisisDatos",
}

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


def latex_escape(text: str) -> str:
    return text.translate(LATEX_SPECIAL)


def fmt(v) -> str:
    if pd.isna(v) or v in ("-", "---", "nan"):
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip()


def parse_xlsx(path: Path) -> tuple[list[dict], list[dict]]:
    df = pd.read_excel(path, sheet_name=0, header=None)
    courses: list[dict] = []
    subtotals: list[dict] = []
    cycle_num: int | None = None

    for _, row in df.iterrows():
        sigla = "" if pd.isna(row[0]) else str(row[0]).strip()

        if re.search(r"\b([IVX]+|\d+)\s+CICLO\b", sigla, re.I):
            m = re.search(r"\b([IVX]+|\d+)\s+CICLO", sigla, re.I)
            if m:
                token = m.group(1).upper()
                roman = {
                    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
                    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
                }
                cycle_num = roman.get(token, int(token) if token.isdigit() else None)
            continue

        if pd.isna(row[0]) and fmt(row[7]) == "SUBTOTAL":
            subtotals.append({"cycle": cycle_num, "credits": fmt(row[8])})
            continue

        if not sigla or sigla.startswith("ESTRUCTURA") or sigla in SKIP_SIGLAS:
            continue
        if "CICLO" in sigla.upper() and not re.match(r"^(MA|CA|LM|EG|EF|RP|SR|OPT)", sigla):
            continue
        if sigla.startswith("Para optar") or sigla.startswith("Según"):
            continue

        courses.append(
            {
                "cycle": cycle_num,
                "sigla": sigla,
                "nombre": fmt(row[1]),
                "T": fmt(row[2]),
                "P": fmt(row[3]),
                "L": fmt(row[4]),
                "TP": fmt(row[5]),
                "req": fmt(row[6]),
                "correq": fmt(row[7]),
                "cred": fmt(row[8]),
            }
        )

    return courses, subtotals


def sigla_compact(sigla: str) -> str:
    return sigla.replace("-", "")


def sigla_tex(sigla: str) -> str:
    if not re.match(r"^(MA|CA)-", sigla):
        return latex_escape(sigla)
    compact = sigla_compact(sigla)
    link = SIGLA_LINK.get(sigla, compact)
    if link != compact:
        return f"\\MallaSigla[{link}]{{{latex_escape(sigla)}}}"
    return f"\\MallaSigla{{{compact}}}"


def course_row(course: dict) -> str:
    c = course
    return (
        f"{c['cycle']} & {sigla_tex(c['sigla'])} & {latex_escape(c['nombre'])} & "
        f"{c['T']} & {c['P']} & {c['L']} & {c['TP']} & {c['cred']} & "
        f"{latex_escape(c['req'])} & {latex_escape(c['correq'])} \\\\"
    )


def subtotal_map(subtotals: list[dict]) -> dict[int, str]:
    return {int(s["cycle"]): s["credits"] for s in subtotals if s["cycle"] is not None}


def total_credits(subtotals: list[dict], cycles: range | list[int]) -> int:
    sm = subtotal_map(subtotals)
    return sum(int(sm[c]) for c in cycles if c in sm)


def cycle_block(
    courses: list[dict],
    subtotals: dict[int, str],
    cycles: list[int],
    *,
    repeat_header: bool = False,
    footer: str | None = None,
) -> list[str]:
    lines: list[str] = []
    first = True
    for cycle in cycles:
        if repeat_header and not first:
            lines.append("")
            lines.append("\\MallaHeader")
        elif first:
            lines.append("\\MallaTabularBegin")
            lines.append("\\MallaHeader")
            first = False

        for course in courses:
            if course["cycle"] == cycle:
                lines.append(course_row(course))
        if cycle in subtotals:
            lines.append(f"\\MallaCicloTotal{{{cycle}}}{{{subtotals[cycle]}}}")

    if footer:
        lines.append(footer)
    lines.append("\\end{tabular}")
    return lines


def licenciatura_section() -> str:
    return r"""\MallaSidewayBegin
\MallaSubsection{Énfasis en Matemática Pura (licenciatura, ciclos IX y X)}

\MallaTabularBegin
\MallaHeader
9 & \MallaSigla[MA0982]{MA0982} & Seminario de estudios dirigidos en matemática pura I &  &  &  &  & 7 & Práctica en matemática pura &  \\
9 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
9 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
\MallaCicloTotal{9}{16}
10 & \MallaSigla[MA1081Pura]{MA1081} & Seminario de estudios dirigidos en matemática pura II &  &  &  &  & 7 & MA-0982 Seminario de estudios dirigidos en matemática pura I &  \\
10 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
10 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
\MallaCicloTotal{10}{16}
\MallaTotalFinal{Total créditos licenciatura pura}{32}
\end{tabular}
\MallaSidewayEnd

\MallaSidewayBegin
\MallaSubsection{Énfasis en Matemática Aplicada (licenciatura, ciclos IX y X)}

\MallaTabularBegin
\MallaHeader
9 & \MallaSigla[MA0984]{MA0984} & Seminario de estudios dirigidos en matemática aplicada I &  &  &  &  & 7 & Práctica en matemática aplicada &  \\
9 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
9 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
\MallaCicloTotal{9}{16}
10 & \MallaSigla[MA1082]{MA1082} & Seminario de estudios dirigidos en matemática aplicada II &  &  &  &  & 7 & MA-0984 Seminario de estudios dirigidos en matemática aplicada I &  \\
10 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
10 & OPT- & Optativa de matemáticas &  &  &  &  &  &  &  \\
\MallaCicloTotal{10}{16}
\MallaTotalFinal{Total créditos licenciatura aplicada}{32}
\end{tabular}
\MallaSidewayEnd"""


def generate() -> str:
    pura_courses, pura_sub = parse_xlsx(DOCS / "210401-3 Pura.xlsx")
    aplicada_courses, aplicada_sub = parse_xlsx(DOCS / "210401-3 Aplicada.xlsx")
    pura_sm = subtotal_map(pura_sub)
    aplicada_sm = subtotal_map(aplicada_sub)

    common_total = total_credits(pura_sub, range(1, 4))
    pura_total = total_credits(pura_sub, range(1, 9))
    aplicada_total = total_credits(aplicada_sub, range(1, 9))

    lines: list[str] = [
        "% =============================================================================",
        "% Tablas de estructura curricular.",
        "% Fuente: Documentos/210401-3 Pura.xlsx y 210401-3 Aplicada.xlsx",
        "% Regenerar: python scripts/generate_malla_from_210401.py",
        "% =============================================================================",
        "",
        "En este capítulo se presenta la estructura curricular del plan de estudios propuesto así como el análisis realizado para la selección y organización de contenidos. Como parte del proceso de reestructuración de la carrera Bachillerato y Licenciatura en Matemática, se ha considerado la participación del personal docente del departamento que expresó la necesidad de abandonar el modelo actual para pasar a uno más moderno, acorde con las necesidades y demandas del país, con diferentes áreas de especialización.",
        "",
        r"\section{\textcolor{Azul-UCR}{Estructura curricular obligatoria propuesta}}",
        "",
        "Se presenta, en forma tabular, la estructura curricular propuesta. El detalle de los contenidos de los cursos se encuentra en el siguiente capítulo.",
        "",
        r"\input{malla-curricular-tablas-macros}",
        "",
        r"\MallaSidewayBegin",
        r"\MallaSubsection{Bloque común (ciclos I a III)}",
        "",
        *cycle_block(pura_courses, pura_sm, [1, 2]),
        "",
        r"\vspace{1cm}",
        "",
        *cycle_block(
            pura_courses,
            pura_sm,
            [3],
            footer=f"\\MallaTotalFinal{{Total créditos bloque común}}{{{common_total}}}",
        ),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        r"\MallaSubsection{Énfasis en Matemática Pura (ciclos IV a VIII)}",
        "",
        *cycle_block(pura_courses, pura_sm, [4]),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        *cycle_block(pura_courses, pura_sm, [5, 6], repeat_header=True),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        *cycle_block(
            pura_courses,
            pura_sm,
            [7, 8],
            repeat_header=True,
            footer=f"\\MallaTotalFinal{{Total créditos bachillerato pura}}{{{pura_total}}}",
        ),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        r"\MallaSubsection{Énfasis en Matemática Aplicada (ciclos IV a VIII)}",
        "",
        *cycle_block(aplicada_courses, aplicada_sm, [4]),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        *cycle_block(aplicada_courses, aplicada_sm, [5, 6], repeat_header=True),
        r"\MallaSidewayEnd",
        "",
        r"\MallaSidewayBegin",
        *cycle_block(
            aplicada_courses,
            aplicada_sm,
            [7, 8],
            repeat_header=True,
            footer=f"\\MallaTotalFinal{{Total créditos bachillerato aplicada}}{{{aplicada_total}}}",
        ),
        r"\MallaSidewayEnd",
        "",
        licenciatura_section(),
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    OUT.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generar optativas-otra-disciplina-tabla.tex desde Documentos/optativas_otras_carreras.xlsx.

La tabla usa la paleta y el formato apaisado de malla-curricular-tablas.tex
(carga malla-curricular-tablas-macros.tex si aún no está cargado).
Uso: python scripts/generate_optativas_otra_disciplina_tex.py
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT.parent / "Documentos" / "optativas_otras_carreras.xlsx"
OUT = ROOT / "optativas-otra-disciplina-tabla.tex"

NAME_FIXES = {
    "Cálculo en una variable": "Cálculo en una Variable",
    "Cálculo en varias variables": "Cálculo en Varias Variables",
    "Álgebra lineal I": "Álgebra Lineal I",
    "Matemática computacional": "Matemática Computacional",
    "Herramientas de Ciencia de Datos como": "Herramientas de Ciencia de Datos I como",
    "corequisito": "correquisito",
}

LATEX_SPECIAL = str.maketrans({
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
})


def load_rows() -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "optativas.xlsx"
        shutil.copyfile(XLSX, src)
        wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
        ws = wb.worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
    header = [str(h).strip() for h in rows[0]]
    return [dict(zip(header, r)) for r in rows[1:] if r and r[0]]


def sigla(code: str) -> str:
    return re.sub(r"\b([A-Z]{1,2})(\d{4})\b", r"\1-\2", code)


def text(value: object) -> str:
    s = "" if value is None else str(value).strip()
    for old, new in NAME_FIXES.items():
        s = s.replace(old, new)
    return sigla(s).translate(LATEX_SPECIAL)


def build(rows: list[dict[str, object]]) -> str:
    out = [
        "% =============================================================================",
        "% Cursos optativos de otra disciplina.",
        "% Fuente: Documentos/optativas_otras_carreras.xlsx",
        "% Regenerar: python scripts/generate_optativas_otra_disciplina_tex.py",
        "% =============================================================================",
        "",
        r"\ifdefined\MallaSidewayBegin\else\input{malla-curricular-tablas-macros}\fi",
        r"\MallaSidewayBegin",
        r"\rowcolors{3}{white}{Celeste-UCR!12}%",
        r"\begin{longtable}{@{}%",
        r"  |l|>{\raggedright\arraybackslash}p{4.4cm}|c|%",
        r"  >{\raggedright\scriptsize\arraybackslash}p{2.4cm}|%",
        r"  >{\raggedright\scriptsize\arraybackslash}p{3.6cm}|%",
        r"  >{\raggedright\scriptsize\arraybackslash}p{3.0cm}|%",
        r"  >{\raggedright\scriptsize\arraybackslash}p{5.4cm}|@{}}",
        r"\caption{Cursos optativos de otra disciplina}\label{tab:optativas-otra-disciplina}\\",
    ]
    header = [
        r"\hline",
        r"\rowcolor{Azul-UCR}\color{white}\bfseries",
        r"Curso & \color{white}\bfseries Nombre del curso & \color{white}\bfseries Cred. &"
        r" \color{white}\bfseries Horas semanales & \color{white}\bfseries Requisitos &"
        r" \color{white}\bfseries Correquisitos & \color{white}\bfseries Requisito o correquisito alternativo solicitado \\ \hline",
    ]
    out += header + [r"\endfirsthead"] + header + [r"\endhead", r"\hline", r"\endfoot"]
    escuela = None
    for r in rows:
        if r["Escuela que ofrece el curso"] != escuela:
            escuela = r["Escuela que ofrece el curso"]
            out.append(r"\rowcolor{Verde-UCR!28}\multicolumn{7}{|l|}{\textit{" + text(escuela) + r"}} \\ \hline")
        cells = [
            sigla(str(r["Sigla"]).strip()),
            text(r["Nombre"]),
            text(r["Créditos"]),
            text(r["Horas semanales"]),
            text(r["Requisitos"]),
            text(r["Correquisitos"]),
            text(r["Solicitud"]) or "---",
        ]
        out.append(" & ".join(cells) + r" \\ \hline")
    out += [r"\end{longtable}", r"\MallaSidewayEnd", ""]
    return "\r\n".join(out)


def main() -> None:
    OUT.write_bytes(build(load_rows()).encode("utf-8"))
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()

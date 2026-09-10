#!/usr/bin/env python3
"""Apply UCR color styling to malla-curricular-tablas.tex."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "malla-curricular-tablas.tex"

OLD_HEADER = r"""\begin{sidewaystable}[H]
\centering
\begin{tabular}{|c|l|>{\raggedright\arraybackslash}p{5.5cm}|c|c|c|c|c|>{\raggedright\arraybackslash}p{4cm}|>{\raggedright\arraybackslash}p{3.5cm}|}
\hline
\textbf{Ciclo} & \textbf{Curso} & \textbf{Nombre del curso} &
\multicolumn{4}{c|}{\textbf{Horas}} & \textbf{Cred.} &
\shortstack{Requisitos y\\ Req. Equivalentes} &
\shortstack{Correquisitos y\\ Correq. Equivalentes} \\
\cline{4-7}
 &  &  & \textbf{T} & \textbf{P} & \textbf{L} & \textbf{TP} &  &  &  \\
\hline
"""

NEW_HEADER = r"""\MallaSidewayBegin
\MallaTabularBegin
\MallaHeader
"""


def main() -> None:
    text = TEX.read_text(encoding="utf-8")

    if "\\input{malla-curricular-tablas-macros}" not in text:
        marker = "\\subsubsection*{Bloque común"
        idx = text.find(marker)
        if idx == -1:
            raise RuntimeError("Could not find insertion point for macros")
        text = (
            text[:idx]
            + "\\input{malla-curricular-tablas-macros}\n\n"
            + text[idx:]
        )

    text = text.replace(OLD_HEADER, NEW_HEADER)
    text = text.replace(
        "\\end{tabular}\n\\end{sidewaystable}",
        "\\end{tabular}\n\\MallaSidewayEnd",
    )

    text = re.sub(
        r"\\subsubsection\*\{([^}]+)\}",
        r"\\MallaSubsection{\1}",
        text,
    )

    text = re.sub(
        r"\\multicolumn\{10\}\{\|l\|\}\{\\textit\{Créditos ciclo (\d+): ([^}]+)\}\} \\\\",
        r"\\MallaCicloTotal{\1}{\2} \\",
        text,
    )
    text = re.sub(
        r"\\multicolumn\{10\}\{\|r\|\}\{\\textbf\{([^:}]+): ([^}]+)\}\} \\\\",
        r"\\MallaTotalFinal{\1}{\2} \\",
        text,
    )

    # Filas de datos: quitar \hline entre filas (el encabezado y totales ya traen reglas).
    text = re.sub(
        r"(?<!\\MallaHeader\n)(?<!\|l\|\}\{)(?<!\|r\|\}\{) \\\\ \n\\hline\n(?=\\d|\\\\multicolumn|\\MallaCicloTotal|\\MallaTotalFinal)",
        r" \\\n",
        text,
    )

    TEX.write_text(text, encoding="utf-8")
    count = text.count("\\MallaSidewayBegin")
    print(f"Styled {TEX.name}: {count} tables")


if __name__ == "__main__":
    main()

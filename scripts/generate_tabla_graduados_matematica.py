#!/usr/bin/env python3
"""Build LaTeX table: math graduates by year and sex from datos_ori.xlsx."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOC_XLSX = (
    Path(r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos")
    / "datos_ori.xlsx"
)
FALLBACK_XLSX = ROOT / "scripts" / "datos_ori.xlsx"
OUT_TEX = ROOT / "propuesta-tabla-graduados-matematica.tex"


def _year_column(df: pd.DataFrame) -> str:
    for col in df.columns:
        if "JURAMENT" in str(col).upper():
            return col
    raise ValueError("No year column (Año juramentación) found")


def load_data() -> pd.DataFrame:
    for path in (DOC_XLSX, FALLBACK_XLSX):
        if not path.is_file():
            continue
        try:
            df = pd.read_excel(path)
            break
        except OSError:
            continue
    else:
        raise FileNotFoundError(f"Cannot read {DOC_XLSX} or {FALLBACK_XLSX}")
    df = df.rename(columns={_year_column(df): "anio"})
    return df


def pivot_counts(df: pd.DataFrame) -> pd.DataFrame:
    pt = df.groupby(["anio", "SEXO"]).size().unstack(fill_value=0)
    for col in ("HOMBRE", "MUJER"):
        if col not in pt.columns:
            pt[col] = 0
    pt = pt[["HOMBRE", "MUJER"]]
    pt.columns = ["Hombres", "Mujeres"]
    pt["Total"] = pt["Hombres"] + pt["Mujeres"]
    return pt.sort_index()


def to_latex(pt: pd.DataFrame) -> str:
    lines = [
        "% Generado por scripts/generate_tabla_graduados_matematica.py — no editar a mano.",
        "",
        "La Tabla~\\ref{tab:graduados-matematica-historico} resume la evolución anual del número de personas graduadas en Bachillerato en Matemática (grado bachiller), desagregada por sexo, según el registro consolidado en \\texttt{datos\\_ori.xlsx}.",
        "",
        "\\begin{table}[H]",
        "\\centering",
        "\\renewcommand{\\arraystretch}{1.15}",
        "\\begin{tabular}{|r|r|r|r|}",
        "\\hline",
        "\\rowcolor[HTML]{00C0F3}",
        "\\multicolumn{1}{|c|}{\\cellcolor[HTML]{00C0F3}\\textbf{Año de juramentación}} & "
        "\\multicolumn{1}{c|}{\\cellcolor[HTML]{00C0F3}\\textbf{Hombres}} & "
        "\\multicolumn{1}{c|}{\\cellcolor[HTML]{00C0F3}\\textbf{Mujeres}} & "
        "\\multicolumn{1}{c|}{\\cellcolor[HTML]{00C0F3}\\textbf{Total}} \\\\ \\hline",
    ]
    for anio, row in pt.iterrows():
        lines.append(
            f"{int(anio)} & {int(row['Hombres'])} & {int(row['Mujeres'])} & {int(row['Total'])} \\\\ \\hline"
        )
    th = int(pt["Hombres"].sum())
    tm = int(pt["Mujeres"].sum())
    tt = int(pt["Total"].sum())
    lines.append(
        f"\\textbf{{Total}} & \\textbf{{{th}}} & \\textbf{{{tm}}} & \\textbf{{{tt}}} \\\\ \\hline"
    )
    lines.extend(
        [
            "\\end{tabular}",
            "\\caption{Graduados en matemática por año de juramentación y sexo (2010--"
            + str(int(pt.index.max()))
            + "). Fuente: \\texttt{datos\\_ori.xlsx}, Escuela de Matemática, Sede Rodrigo Facio.}",
            "\\label{tab:graduados-matematica-historico}",
            "\\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    df = load_data()
    pt = pivot_counts(df)
    tex = to_latex(pt)
    OUT_TEX.write_text(tex, encoding="utf-8")
    print(f"Wrote {OUT_TEX.name} ({len(pt)} years, {int(pt['Total'].sum())} graduates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

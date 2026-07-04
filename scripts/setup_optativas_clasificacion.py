#!/usr/bin/env python3
"""Create skeleton TeX files for optativas and sync propuesta / JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUROS = ROOT / "Cursos"
CATALOG = Path(__file__).resolve().parent / "optativas_catalog.json"
PROGRAMAS = ROOT / "propuesta-elementos-programas.tex"

DRIVER = """% !TeX program = pdflatex
% Compilar desde la raíz del proyecto: latexmk Cursos/{driver}.tex
\\documentclass[11pt]{{report}}
\\makeatletter
\\def\\input@path{{{{../}}{{./Cursos/}}{{./}}}}
\\makeatother
\\input{{preamble-body.tex}}

\\begin{{document}}
\\input{{{cuerpo}.tex}}
\\end{{document}}
"""

CUERPO = """%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% {full_title} %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\newpage
\\subsection*{{{full_title}}}
\\addcontentsline{{toc}}{{subsection}}{{{full_title}}}

\\hypertarget{{{hypertarget}}}{{}}
\\begin{{refsection}}
\\begin{{table}}[H]
\\centering{{
\\begin{{tabular}}{{|ll|}}
\\hline
\\textbf{{Año:}} IV  & \\textbf{{Requisitos:}} Por determinar \\\\ 
\\textbf{{Ciclo:}} Optativa  & \\textbf{{Correquisitos:}} Ninguno \\\\ 
\\textbf{{Tipo de curso:}} Teórico & \\textbf{{Horas presenciales por semana:}} Por determinar \\\\ 
\\textbf{{Créditos:}} 5 & \\textbf{{Horas de trabajo independiente por semana:}} Por determinar \\\\ \\hline
\\end{{tabular}}
}}
\\end{{table}}

\\subsubsection*{{Descripción del curso}}

\\textit{{Programa pendiente de elaboración.}}

\\subsubsection*{{Objetivos}}

\\textit{{Pendiente de elaboración.}}

\\subsubsection*{{Contenidos}}

\\textit{{Pendiente de elaboración.}}

\\subsubsection*{{Metodología}}

\\textit{{Pendiente de elaboración.}}

\\end{{refsection}}
"""


def full_title(entry: dict) -> str:
    return f"{entry['code']} {entry['title']}"


def hypertarget(code: str) -> str:
    return code.replace("-", "")


def load_catalog() -> tuple[list[dict], list[dict]]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return data["nucleo"], data["tematicos"]


def ensure_skeleton(entry: dict) -> bool:
    cuerpo_path = CUROS / f"{entry['stem']}.tex"
    driver_stem = entry["stem"].removesuffix("-cuerpo")
    driver_path = CUROS / f"{driver_stem}.tex"
    created = False
    if not cuerpo_path.exists():
        cuerpo_path.write_text(
            CUERPO.format(
                full_title=full_title(entry),
                hypertarget=hypertarget(entry["code"]),
            ),
            encoding="utf-8",
        )
        print(f"  + cuerpo {cuerpo_path.name}")
        created = True
    if not driver_path.exists():
        driver_path.write_text(
            DRIVER.format(driver=driver_stem, cuerpo=entry["stem"]),
            encoding="utf-8",
        )
        print(f"  + driver {driver_path.name}")
        created = True
    return created


def tex_inputs(entries: list[dict]) -> str:
    lines = [f"\\input{{Cursos/{e['stem']}}}" for e in entries]
    return "\n".join(lines) + "\n"


def update_programas_tex(nucleo: list[dict], tematicos: list[dict]) -> None:
    tex = PROGRAMAS.read_text(encoding="utf-8")

    tercer_nucleo = [e for e in nucleo if e["code"] == "MA-0725"]
    cuarto_nucleo = [e for e in nucleo if e["code"] != "MA-0725"]

    old_tercer = (
        "\\subsubsection{Cursos optativos}\n"
        "\\input{Cursos/MA0725-analisis-real-ii-cuerpo}"
    )
    new_tercer = (
        "\\subsubsection{Cursos optativos de núcleo}\n"
        + tex_inputs(tercer_nucleo).rstrip()
    )
    if old_tercer not in tex:
        raise RuntimeError("No se encontró optativa MA-0725 en tercer año")
    tex = tex.replace(old_tercer, new_tercer, 1)

    old_block = re.search(
        r"\\subsubsection\{Cursos optativos\}\s*\n"
        r"(?:\\input\{Cursos/[^}]+\}\s*\n)+",
        tex,
    )
    if not old_block:
        raise RuntimeError("No se encontró bloque de optativas de cuarto año")
    new_block = (
        "\\subsubsection{Cursos optativos de núcleo}\n"
        + tex_inputs(cuarto_nucleo)
        + "\\subsubsection{Cursos optativos temáticos}\n"
        + tex_inputs(tematicos)
    )
    tex = tex[: old_block.start()] + new_block + tex[old_block.end() :]
    PROGRAMAS.write_text(tex, encoding="utf-8")
    print(f"Updated {PROGRAMAS.name}")


def sync_json(nucleo: list[dict], tematicos: list[dict]) -> None:
    titles_n = [full_title(e) for e in nucleo]
    titles_t = [full_title(e) for e in tematicos]
    path = ROOT / "optativas.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {}
    for name in ("pura", "aplicada"):
        data[name] = {
            "Optativas de núcleo": titles_n,
            "Optativas temáticas": titles_t,
        }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {path.name}")


def main() -> int:
    nucleo, tematicos = load_catalog()
    print("Creating missing skeleton files…")
    n_created = sum(ensure_skeleton(e) for e in nucleo + tematicos)
    print(f"Skeletons created: {n_created}")
    update_programas_tex(nucleo, tematicos)
    sync_json(nucleo, tematicos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

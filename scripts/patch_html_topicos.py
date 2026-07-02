#!/usr/bin/env python3
"""Patch malla-aplicada.html with new Tópicos courses."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COURSES = [
    ("MA-0791 Tópicos de Probabilidad", "MA0791-topicos-probabilidad.pdf", "topicos-probabilidad"),
    ("MA-0792 Tópicos de Ecuaciones diferenciales", "MA0792-topicos-ecuaciones-diferenciales.pdf", "topicos-ecuaciones-diferenciales"),
    ("MA-0793 Tópicos de Geometría", "MA0793-topicos-geometria.pdf", "topicos-geometria"),
    ("MA-0794 Tópicos de Modelación", "MA0794-topicos-modelacion.pdf", "topicos-modelacion"),
    ("MA-0795 Tópicos de Computación científica", "MA0795-topicos-computacion-cientifica.pdf", "topicos-computacion-cientifica"),
    ("MA-0796 Tópicos de Álgebra", "MA0796-topicos-algebra.pdf", "topicos-algebra"),
    ("MA-0797 Tópicos de Matemática discreta", "MA0797-topicos-matematica-discreta.pdf", "topicos-matematica-discreta"),
    ("MA-0798 Tópicos de Análisis de datos", "MA0798-topicos-analisis-datos.pdf", "topicos-analisis-datos"),
    ("MA-0799 Tópicos de Aprendizaje automático", "MA0799-topicos-aprendizaje-automatico.pdf", "topicos-aprendizaje-automatico"),
]


def main() -> None:
    path = ROOT / "malla-aplicada.html"
    text = path.read_text(encoding="utf-8")
    if '"MA-0791 Tópicos de Probabilidad"' in text:
        print("malla-aplicada.html already has new Tópicos")
        return
    pdf = "\n".join(f'        "{t}": "{p}",' for t, p, _ in COURSES)
    ids = "\n".join(f'        "{t}": "curso-{s}-aplicada",' for t, _, s in COURSES)
    text = text.replace(
        '"MA-0790 Tópicos de análisis": "MA0790-topicos-analisis.pdf",',
        '"MA-0790 Tópicos de análisis": "MA0790-topicos-analisis.pdf",\n' + pdf,
        1,
    )
    text = text.replace(
        '"MA-0790 Tópicos de análisis": "curso-topicos-analisis-aplicada",',
        '"MA-0790 Tópicos de análisis": "curso-topicos-analisis-aplicada",\n' + ids,
        1,
    )
    path.write_text(text, encoding="utf-8")
    print("Patched malla-aplicada.html")


if __name__ == "__main__":
    main()

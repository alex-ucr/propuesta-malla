#!/usr/bin/env python3
"""One-shot text sync after splitting siglas pura vs aplicada (práctica / seminarios)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    ("MA-0881 Práctica profesional en matemática aplicada", "MA-0883 Práctica profesional en matemática aplicada"),
    ("MA-0881 Seminario de estudios dirigidos en matemática pura I", "MA-0982 Seminario de estudios dirigidos en matemática pura I"),
    ("MA-0881 Seminario de estudios dirigidos en matemática aplicada I", "MA-0984 Seminario de estudios dirigidos en matemática aplicada I"),
    ("MA-1081 Seminario de estudios dirigidos en matemática aplicada II", "MA-1082 Seminario de estudios dirigidos en matemática aplicada II"),
    ("MA1081-practica-profesional-aplicada", "MA0883-practica-profesional-aplicada"),
    ("MA1081-seminario-estudios-dirigidos-pura-i", "MA0982-seminario-estudios-dirigidos-pura-i"),
    ("MA1081-seminario-estudios-dirigidos-aplicada-i", "MA0984-seminario-estudios-dirigidos-aplicada-i"),
    ("MA1081-seminario-estudios-dirigidos-aplicada", "MA1082-seminario-estudios-dirigidos-aplicada"),
    ("\\hyperlink{MA1081Aplicada}", "\\hyperlink{MA0883}"),
    ("\\hyperlink{MA1081SEDPura}", "\\hyperlink{MA0982}"),
    ("\\hyperlink{MA1081SEDAplicada}", "\\hyperlink{MA0984}"),
    ("\\hyperlink{MA1081Aplicada}", "\\hyperlink{MA1082}"),
    ("\\hypertarget{MA1081Aplicada}", "\\hypertarget{MA0883}"),
    ("\\hypertarget{MA1081SEDPura}", "\\hypertarget{MA0982}"),
    ("\\hypertarget{MA1081SEDAplicada}", "\\hypertarget{MA0984}"),
    ("\\hypertarget{MA1081Aplicada}", "\\hypertarget{MA1082}"),
    ("\\MallaSigla[MA1081Aplicada]{MA1081}", "\\MallaSigla[MA0883]{MA0883}"),
    ("\\MallaSigla[MA1081SEDPura]{MA1081}", "\\MallaSigla[MA0982]{MA0982}"),
    ("\\MallaSigla[MA1081SEDAplicada]{MA1081}", "\\MallaSigla[MA0984]{MA0984}"),
    ("\\MallaSigla[MA1081Aplicada]{MA1081}", "\\MallaSigla[MA1082]{MA1082}"),
    ("inputcurso{Cursos/MA1081-practica-profesional-aplicada-cuerpo}", "inputcurso{Cursos/MA0883-practica-profesional-aplicada-cuerpo}"),
    ("inputcurso{Cursos/MA1081-seminario-estudios-dirigidos-pura-i-cuerpo}", "inputcurso{Cursos/MA0982-seminario-estudios-dirigidos-pura-i-cuerpo}"),
    ("inputcurso{Cursos/MA1081-seminario-estudios-dirigidos-aplicada-i-cuerpo}", "inputcurso{Cursos/MA0984-seminario-estudios-dirigidos-aplicada-i-cuerpo}"),
    ("inputcurso{Cursos/MA1081-seminario-estudios-dirigidos-aplicada-cuerpo}", "inputcurso{Cursos/MA1082-seminario-estudios-dirigidos-aplicada-cuerpo}"),
    ("MA1081 Práctica profesional en matemática aplicada", "MA0883 Práctica profesional en matemática aplicada"),
    ("MA1081 Seminario de estudios dirigidos en matemática pura I", "MA0982 Seminario de estudios dirigidos en matemática pura I"),
    ("MA1081 Seminario de estudios dirigidos en matemática aplicada I", "MA0984 Seminario de estudios dirigidos en matemática aplicada I"),
    ("MA1081 Seminario de estudios dirigidos en matemática aplicada II", "MA1082 Seminario de estudios dirigidos en matemática aplicada II"),
]

GLOBS = ("*.tex", "*.json", "*.html", "*.py", "*.md")


def main() -> None:
    changed: list[str] = []
    for pattern in GLOBS:
        for path in ROOT.rglob(pattern):
            if "node_modules" in path.parts or ".git" in path.parts:
                continue
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8")
            new = text
            for old, rep in REPLACEMENTS:
                new = new.replace(old, rep)
            if new != text:
                path.write_text(new, encoding="utf-8")
                changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    for p in sorted(changed)[:40]:
        print(f"  {p}")
    if len(changed) > 40:
        print(f"  ... and {len(changed) - 40} more")


if __name__ == "__main__":
    main()

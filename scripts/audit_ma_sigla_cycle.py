#!/usr/bin/env python3
"""Report MA cursos whose 4-digit sigla prefix != Ciclo I–X in *-cuerpo.tex."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUROS = ROOT / "Cursos"

ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
}


def audit_file(path: Path) -> tuple[str, int, int] | None:
    text = path.read_text(encoding="utf-8")
    m_ciclo = re.search(r"\\textbf\{Ciclo:\}\s*([IVX]+)", text)
    m_sigla = re.search(r"\\subsection\*\{MA-(\d{4})", text)
    if not m_ciclo or not m_sigla:
        return None
    ciclo_name = m_ciclo.group(1)
    if ciclo_name not in ROMAN:
        return None
    digits = m_sigla.group(1)
    prefix = int(digits[:2])
    ciclo = ROMAN[ciclo_name]
    if prefix != ciclo:
        return (f"MA-{digits}", ciclo, prefix)
    return None


def main() -> int:
    bad: list[str] = []
    for path in sorted(CUROS.glob("*-cuerpo.tex")):
        row = audit_file(path)
        if row:
            sigla, ciclo, prefix = row
            bad.append(f"{path.name}: {sigla} tiene prefijo {prefix:02d} pero Ciclo {ciclo}")
    if bad:
        print("Violaciones:", len(bad))
        for line in bad:
            print(" ", line)
        return 1
    print("OK: todos los cuerpos con Ciclo I–X cumplen la regla.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

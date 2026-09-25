#!/usr/bin/env python3
"""Regenerate MA-0525 cuerpo from Documentos/Programa Combinatoria.tex (via maintained cuerpo)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUERPO = ROOT / "Cursos" / "MA0525-combinatoria-cuerpo.tex"
SRC = Path(
    r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos\Programa Combinatoria.tex"
)


def main() -> None:
    if not SRC.is_file():
        sys.exit(f"Fuente no encontrada: {SRC}")
    if not CUERPO.is_file():
        sys.exit(f"Falta {CUERPO}; incorpore el programa manualmente.")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "extract_contenidos.py")],
        check=True,
        cwd=ROOT,
    )
    print(f"OK: contenidos actualizados; cuerpo en {CUERPO.name}")


if __name__ == "__main__":
    main()

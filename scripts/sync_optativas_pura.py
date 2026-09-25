#!/usr/bin/env python3
"""Sync optativas.json from propuesta-lista-cursos.tex (OPT-001 / OPT-002 / OPT-003)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Implementation lives in sync_optativas_from_lista.py (same repo).
sys.path.insert(0, str(ROOT / "scripts"))
from sync_optativas_from_lista import main  # noqa: E402

if __name__ == "__main__":
    main()

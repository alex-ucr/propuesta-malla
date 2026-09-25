#!/usr/bin/env python3
"""Parse 210401-3 Pura/Aplicada xlsx files and dump structured data."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

DOCS = Path(r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos")
OUT = Path(__file__).resolve().parents[1] / "scripts" / "210401_parsed.json"

SKIP_SIGLAS = {
    "NIVEL Y SIGLA",
    "PRIMER AÑO",
    "SEGUNDO AÑO",
    "TERCER AÑO",
    "CUARTO AÑO",
    "QUINTO AÑO",
    "SEXTO AÑO",
}


def fmt(v) -> str:
    if pd.isna(v) or v in ("-", "---", "nan"):
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip()


def parse_xlsx(path: Path, emphasis: str) -> dict:
    df = pd.read_excel(path, sheet_name=0, header=None)
    courses: list[dict] = []
    subtotals: list[dict] = []
    current_cycle: str | None = None
    cycle_num: int | None = None

    for _, row in df.iterrows():
        sigla_raw = row[0]
        sigla = "" if pd.isna(sigla_raw) else str(sigla_raw).strip()

        if re.search(r"\b([IVX]+|\d+)\s+CICLO\b", sigla, re.I):
            current_cycle = sigla
            m = re.search(r"\b([IVX]+|\d+)\s+CICLO", sigla, re.I)
            if m:
                token = m.group(1).upper()
                roman = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
                cycle_num = roman.get(token, int(token) if token.isdigit() else None)
            continue

        if pd.isna(row[0]) and fmt(row[7]) == "SUBTOTAL":
            subtotals.append(
                {
                    "cycle_label": current_cycle,
                    "cycle": cycle_num,
                    "credits": fmt(row[8]),
                }
            )
            continue

        if not sigla or sigla.startswith("ESTRUCTURA") or sigla in SKIP_SIGLAS:
            continue
        if "CICLO" in sigla.upper() and not sigla.startswith(("MA", "CA", "LM", "EG", "EF", "RP", "SR", "OPT")):
            continue

        courses.append(
            {
                "cycle_label": current_cycle,
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

    return {"emphasis": emphasis, "courses": courses, "subtotals": subtotals}


def main() -> None:
    data = {
        "pura": parse_xlsx(DOCS / "210401-3 Pura.xlsx", "pura"),
        "aplicada": parse_xlsx(DOCS / "210401-3 Aplicada.xlsx", "aplicada"),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    for key in ("pura", "aplicada"):
        d = data[key]
        print(f"\n=== {key.upper()} ===")
        for s in d["subtotals"]:
            print(f"  ciclo {s['cycle']}: {s['credits']} cr")
        print(f"  total courses: {len(d['courses'])}")


if __name__ == "__main__":
    main()

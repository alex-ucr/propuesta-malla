#!/usr/bin/env python3
"""Import course bodies from Documentos/Cursos-TN-GA.tex into Cursos/*-cuerpo.tex."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(
    r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos\Cursos-TN-GA.tex"
)
CUROS = ROOT / "Cursos"

COURSES = (
    {
        "marker": r"\\subsection\*\{MA-07XX Teoría de Números Algebraicos\}",
        "comment": "MA-0506 Teoría algebraica de números",
        "title": r"MA-0506 Teoría algebraica de números",
        "toc_title": r"MA-0506 Teoría algebraica de números",
        "hypertarget": "MA0506",
        "out": "MA0506-teoria-algebraica-numeros-cuerpo.tex",
    },
    {
        "marker": r"\\subsection\*\{MA-07XX Teoría Analítica de Números\}",
        "comment": "MA-0609 Teoría analítica de números",
        "title": r"MA-0609 Teoría analítica de números",
        "toc_title": r"MA-0609 Teoría analítica de números",
        "hypertarget": "MA0609",
        "out": "MA0609-teoria-analitica-numeros-cuerpo.tex",
    },
    {
        "marker": r"\\subsection\*\{MA-0709 Geometría Algebraica\}",
        "comment": "MA-0709 Geometría algebraica I",
        "title": r"MA-0709 Geometría algebraica I",
        "toc_title": r"MA-0709 Geometría algebraica I",
        "hypertarget": "MA0709",
        "out": "MA0709-geometria-algebraica-i-cuerpo.tex",
    },
)


def _extract_refsection(tex: str, marker: str) -> str:
    m = re.search(marker, tex)
    if not m:
        raise ValueError(f"No se encontró marcador: {marker}")
    rest = tex[m.end() :]
    m2 = re.search(r"\\begin\{refsection\}(.*?)\\end\{refsection\}", rest, re.DOTALL)
    if not m2:
        raise ValueError(f"No refsection tras {marker}")
    return m2.group(1).strip()


def _normalize_body(body: str) -> str:
    body = body.replace('M"obius', r'M\"obius')
    body = re.sub(
        r"\\printbibliography\[heading=subbibliography\]",
        r"\\printcursosbibliography",
        body,
    )
    body = body.replace("Presencial}\\ \\hline", "Presencial}\\\\ \\hline")
    if "\\textbf{Virtualidad:" not in body:
        body = re.sub(
            r"(\\textbf\{Créditos:\}[^\n]+)\s*\n(\\hline)",
            r"\1 \\\\ \n\\textbf{Virtualidad:} P  &  \\\\ \n\2",
            body,
            count=1,
        )
    return body


def _wrap_cuerpo(meta: dict, body: str) -> str:
    return f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% {meta['comment']} %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\newpage
\\subsection*{{{meta['title']}}}
\\addcontentsline{{toc}}{{subsection}}{{{meta['toc_title']}}}

\\hypertarget{{{meta['hypertarget']}}}{{}}
\\begin{{refsection}}
{body}
\\end{{refsection}}
"""


def main() -> None:
    tex = SRC.read_text(encoding="utf-8")
    for cfg in COURSES:
        body = _normalize_body(_extract_refsection(tex, cfg["marker"]))
        out = CUROS / cfg["out"]
        out.write_text(_wrap_cuerpo(cfg, body), encoding="utf-8")
        print(f"Wrote {out.name} ({len(body)} chars body)")


if __name__ == "__main__":
    main()

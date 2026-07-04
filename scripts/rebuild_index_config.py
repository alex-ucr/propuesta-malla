#!/usr/bin/env python3
"""Rebuild CONFIG block in index.html from pura.json / aplicada.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CATALOG = Path(__file__).resolve().parent / "optativas_catalog.json"

PDF_OVERRIDES = {
    "MA-0625 Análisis Real I": "MA0625-analisis-real-i-individual.pdf",
    "MA-0702 Análisis Complejo": "MA0702-analisis-complejo-individual.pdf",
    "MA-0705 Análisis Real I": "MA0705-analisis-real-i-individual.pdf",
    "MA-0725 Análisis Real II": "MA0725-analisis-real-ii-individual.pdf",
}

PDF = {
    "MA-0151 Fundamentos de álgebra, trigonometría y geometría analítica": "MA0151-fundamentos.pdf",
    "MA-0152 Matemática Exploratoria": "MA0152-matematica-exploratoria.pdf",
    "MA-0251 Introducción al Cálculo en una variable": "MA0251-calculo-una-variable.pdf",
    "MA-0252 Introducción a las Demostraciones": "MA0252-intro-demostraciones.pdf",
    "MA-0261 Algebra Lineal I": "MA0261-algebra-lineal-i.pdf",
    "MA-0341 Matemática Computacional I": "MA0341-matematica-computacional-i.pdf",
    "MA-0351 Introducción al Cálculo en varias variables": "MA0351-calculo-varias-variables.pdf",
    "MA-0361 Algebra Lineal I": "MA0361-algebra-lineal-i.pdf",
    "MA-0361 Algebra Lineal II": "MA0361-algebra-lineal-ii.pdf",
    "MA-0451 Principios de análisis en una variable": "MA0451-principios-analisis-i.pdf",
    "MA-0461 Algebra Lineal II": "MA0461-algebra-lineal-ii.pdf",
    "MA-0471 Introducción a la Geometría Diferencial": "MA0471-geometria.pdf",
    "MA-0496 Teoría de Números": "MA0496-teoria-numeros.pdf",
    "MA-0515 Ecuaciones Diferenciales": "MA0515-ecuaciones-diferenciales.pdf",
    "MA-0541 Matemática Computacional II": "MA0641-matematica-computacional-ii.pdf",
    "MA-0551 Principios de análisis en varias variables": "MA0551-principios-analisis-ii.pdf",
    "MA-0561 Algebra Abstracta I": "MA0561-algebra-abstracta-i.pdf",
    "MA-0615 Ecuaciones Diferenciales": "MA0615-ecuaciones-diferenciales.pdf",
    "MA-0625 Análisis Real I": "MA0625-analisis-real-i-individual.pdf",
    "MA-0635 Introducción a la Topología": "MA0635-topologia.pdf",
    "MA-0641 Matemática Computacional II": "MA0641-matematica-computacional-ii.pdf",
    "MA-0661 Algebra Abstracta II": "MA0661-algebra-abstracta-ii.pdf",
    "MA-0701 Seminario de Matemática": "MA0701-seminario-matematica.pdf",
    "MA-0702 Análisis Complejo": "MA0702-analisis-complejo-individual.pdf",
    "MA-0705 Análisis Real I": "MA0705-analisis-real-i-individual.pdf",
    "MA-0780 Comunicación en las ciencias": "MA0780-comunicacion-ciencias.pdf",
    "MA-0725 Análisis Real II": "MA0725-analisis-real-ii-individual.pdf",
    "MA-0840 Probabilidad": "MA0840-probabilidad.pdf",
    "MA-0918 Procesos estocásticos": "MA0918-procesos-estocasticos.pdf",
    "MA-0703 Integración": "MA0703-integracion.pdf",
    "MA-0790 Tópicos de análisis": "MA0790-topicos-analisis.pdf",
    "MA-0791 Tópicos de Probabilidad": "MA0791-topicos-probabilidad.pdf",
    "MA-0792 Tópicos de Ecuaciones diferenciales": "MA0792-topicos-ecuaciones-diferenciales.pdf",
    "MA-0793 Tópicos de Geometría": "MA0793-topicos-geometria.pdf",
    "MA-0794 Tópicos de Modelación": "MA0794-topicos-modelacion.pdf",
    "MA-0795 Tópicos de Computación científica": "MA0795-topicos-computacion-cientifica.pdf",
    "MA-0796 Tópicos de Álgebra": "MA0796-topicos-algebra.pdf",
    "MA-0797 Tópicos de Matemática discreta": "MA0797-topicos-matematica-discreta.pdf",
    "MA-0798 Tópicos de Análisis de datos": "MA0798-topicos-analisis-datos.pdf",
    "MA-0799 Tópicos de Aprendizaje automático": "MA0799-topicos-aprendizaje-automatico.pdf",
    "MA-0830 Tópicos de Teoría de Números": "MA0830-topicos-teoria-numeros.pdf",
    "MA-0831 Tópicos de Lógica": "MA0831-topicos-logica.pdf",
    "MA-0832 Tópicos en Topología": "MA0832-topicos-topologia.pdf",
    "MA-0711 Lógica": "MA0711-logica.pdf",
    "MA-0820 Teoría de modelos": "MA0820-teoria-modelos.pdf",
    "MA-0404 Herramientas de ciencia de datos I": "MA0404-herramientas-ciencia-datos-i.pdf",
    "MA-0503 Estadística I": "MA0503-estadistica-i.pdf",
    "MA-0711 Análisis de Datos I": "MA0711-analisis-datos-i.pdf",
    "MA-0421 Probabilidad": "MA0421-probabilidad.pdf",
    "MA-0647 Modelación Matemática": "MA0647-modelacion-matematica.pdf",
}

ID = {
    "MA-0151 Fundamentos de álgebra, trigonometría y geometría analítica": "curso-fundamentos-algebra",
    "MA-0152 Matemática Exploratoria": "curso-matematica-exploratoria",
    "MA-0251 Introducción al Cálculo en una variable": "curso-calculo-una-variable",
    "MA-0252 Introducción a las Demostraciones": "curso-intro-demostraciones",
    "MA-0261 Algebra Lineal I": "curso-algebra-lineal-i",
    "MA-0341 Matemática Computacional I": "curso-mat-computacional-i",
    "MA-0351 Introducción al Cálculo en varias variables": "curso-calculo-varias-variables",
    "MA-0361 Algebra Lineal I": "curso-algebra-lineal-i",
    "MA-0361 Algebra Lineal II": "curso-algebra-lineal-ii",
    "MA-0451 Principios de análisis en una variable": "curso-principios-analisis-una-variable",
    "MA-0461 Algebra Lineal II": "curso-algebra-lineal-ii",
    "MA-0471 Introducción a la Geometría Diferencial": "curso-geometria-diferencial",
    "MA-0496 Teoría de Números": "curso-teoria-numeros",
    "MA-0515 Ecuaciones Diferenciales": "curso-ecuaciones-diferenciales",
    "MA-0541 Matemática Computacional II": "curso-mat-computacional-ii",
    "MA-0551 Principios de análisis en varias variables": "curso-principios-analisis-varias-variables",
    "MA-0561 Algebra Abstracta I": "curso-algebra-abstracta-i",
    "MA-0615 Ecuaciones Diferenciales": "curso-ecuaciones-diferenciales",
    "MA-0625 Análisis Real I": "curso-analisis-real-i",
    "MA-0635 Introducción a la Topología": "curso-topologia",
    "MA-0641 Matemática Computacional II": "curso-mat-computacional-ii",
    "MA-0661 Algebra Abstracta II": "curso-algebra-abstracta-ii",
    "MA-0701 Seminario de Matemática": "curso-seminario-matematica",
    "MA-0702 Análisis Complejo": "curso-analisis-complejo",
    "MA-0705 Análisis Real I": "curso-analisis-real-i",
    "MA-0780 Comunicación en las ciencias": "curso-comunicacion-ciencias",
    "MA-0725 Análisis Real II": "curso-analisis-real-ii",
    "MA-0840 Probabilidad": "curso-probabilidad",
    "MA-0918 Procesos estocásticos": "curso-procesos-estocasticos",
    "MA-0703 Integración": "curso-integracion",
    "MA-0790 Tópicos de análisis": "curso-topicos-analisis",
    "MA-0791 Tópicos de Probabilidad": "curso-topicos-probabilidad",
    "MA-0792 Tópicos de Ecuaciones diferenciales": "curso-topicos-ecuaciones-diferenciales",
    "MA-0793 Tópicos de Geometría": "curso-topicos-geometria",
    "MA-0794 Tópicos de Modelación": "curso-topicos-modelacion",
    "MA-0795 Tópicos de Computación científica": "curso-topicos-computacion-cientifica",
    "MA-0796 Tópicos de Álgebra": "curso-topicos-algebra",
    "MA-0797 Tópicos de Matemática discreta": "curso-topicos-matematica-discreta",
    "MA-0798 Tópicos de Análisis de datos": "curso-topicos-analisis-datos",
    "MA-0799 Tópicos de Aprendizaje automático": "curso-topicos-aprendizaje-automatico",
    "MA-0830 Tópicos de Teoría de Números": "curso-topicos-teoria-numeros",
    "MA-0831 Tópicos de Lógica": "curso-topicos-logica",
    "MA-0832 Tópicos en Topología": "curso-topicos-topologia",
    "MA-0711 Lógica": "curso-logica",
    "MA-0820 Teoría de modelos": "curso-teoria-modelos",
    "MA-0404 Herramientas de ciencia de datos I": "curso-ma-0404-herramientas-ciencia-datos-i",
    "MA-0503 Estadística I": "curso-ma-0503-estadistica-i",
    "MA-0711 Análisis de Datos I": "curso-ma-0711-analisis-datos-i",
    "MA-0647 Modelación Matemática": "curso-modelacion-matematica",
    "MA-0421 Probabilidad": "curso-ma-0421-probabilidad",
}


def enrich_from_catalog(pdf: dict[str, str], ids: dict[str, str]) -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    for group in ("nucleo", "tematicos"):
        for entry in data[group]:
            title = f"{entry['code']} {entry['title']}"
            stem = entry["stem"].removesuffix("-cuerpo")
            pdf.setdefault(title, PDF_OVERRIDES.get(title, f"{stem}.pdf"))
            code = entry["code"]
            slug = stem.lower().replace("_", "-")
            if code.startswith("CA-"):
                ids.setdefault(title, f"curso-ca-{code[3:]}-{slug.split('-', 1)[-1]}")
            else:
                ids.setdefault(title, f"curso-{slug}")


enrich_from_catalog(PDF, ID)

# Posiciones relativas: left = origin.left + dx, top = origin.top + dy.
# Valores en % del contenedor. (dx, dy) o (dx, dy, w, h) si el tamaño difiere.
HOTSPOT_ORIGIN_PUR = {"left": 14, "top": 11, "w": 14, "h": 8}
HOTSPOT_ORIGIN_APL = {"left": 14, "top": 11, "w": 14, "h": 8}

HOTSPOT_PUR = {
    "MA-0151 Fundamentos de álgebra, trigonometría y geometría analítica": (36, 0),
    "MA-0152 Matemática Exploratoria": (0, 0),
    "MA-0251 Introducción al Cálculo en una variable": (36, 11),
    "MA-0252 Introducción a las Demostraciones": (0, 11),
    "MA-0361 Algebra Lineal I": (54, 23),
    "MA-0341 Matemática Computacional I": (0, 23),
    "MA-0351 Introducción al Cálculo en varias variables": (36, 23),
    "MA-0461 Algebra Lineal II": (54, 34.5),
    "MA-0451 Principios de análisis en una variable": (36, 34.5),
    "MA-0471 Introducción a la Geometría Diferencial": (0, 34.5),
    "MA-0496 Teoría de Números": (18, 34.5),
    "MA-0561 Algebra Abstracta I": (54, 46),
    "MA-0551 Principios de análisis en varias variables": (36, 46),
    "MA-0515 Ecuaciones Diferenciales": (18, 46),
    "MA-0661 Algebra Abstracta II": (54, 57.5),
    "MA-0635 Introducción a la Topología": (36, 57.5),
    "MA-0641 Matemática Computacional II": (18, 57.5),
    "MA-0705 Análisis Real I": (54, 67.5),
    "MA-0702 Análisis Complejo": (36, 67.5),
    "MA-0780 Comunicación en las ciencias": (54, 69),
    "MA-0701 Seminario de Matemática": (72, 69),
    "MA-0725 Análisis Real II": (18, 69),
    "MA-0840 Probabilidad": (0, 69),
    "MA-0918 Procesos estocásticos": (18, 78),
    "MA-0703 Integración": (36, 78),
    "MA-0790 Tópicos de análisis": (54, 78),
    "MA-0711 Lógica": (0, 86),
    "MA-0820 Teoría de modelos": (18, 86),
    "MA-0647 Modelación Matemática": (36, 86),
}

HOTSPOT_APL = {
    "MA-0151 Fundamentos de álgebra, trigonometría y geometría analítica": (36, 0),
    "MA-0152 Matemática Exploratoria": (0, 0),
    "MA-0251 Introducción al Cálculo en una variable": (36, 11),
    "MA-0252 Introducción a las Demostraciones": (0, 11),
    "MA-0361 Algebra Lineal I": (54, 23),
    "MA-0341 Matemática Computacional I": (0, 23),
    "MA-0351 Introducción al Cálculo en varias variables": (36, 23),
    "MA-0461 Algebra Lineal II": (54, 34.5),
    "MA-0451 Principios de análisis en una variable": (36, 34.5),
    "MA-0421 Probabilidad": (54, 34.5),
    "MA-0404 Herramientas de ciencia de datos I": (0, 34.5),
    "MA-0551 Principios de análisis en varias variables": (36, 46),
    "MA-0615 Ecuaciones Diferenciales": (18, 46),
    "MA-0503 Estadística I": (0, 46),
    "MA-0541 Matemática Computacional II": (0, 57.5),
    "MA-0625 Análisis Real I": (18, 57.5),
    "MA-0635 Introducción a la Topología": (36, 57.5),
    "MA-0702 Análisis Complejo": (18, 69),
    "MA-0711 Análisis de Datos I": (0, 69),
    "MA-0780 Comunicación en las ciencias": (54, 69),
    "MA-0701 Seminario de Matemática": (72, 69),
    "MA-0725 Análisis Real II": (18, 77),
    "MA-0840 Probabilidad": (0, 77),
    "MA-0918 Procesos estocásticos": (36, 77),
    "MA-0703 Integración": (54, 77),
    "MA-0790 Tópicos de análisis": (0, 85),
    "MA-0711 Lógica": (18, 85),
    "MA-0820 Teoría de modelos": (36, 85),
    "MA-0647 Modelación Matemática": (54, 85),
}

ID_APL_SUFFIX = {
    "MA-0725 Análisis Real II": "curso-analisis-real-ii-aplicada",
    "MA-0840 Probabilidad": "curso-probabilidad-aplicada",
    "MA-0918 Procesos estocásticos": "curso-procesos-estocasticos-aplicada",
    "MA-0703 Integración": "curso-integracion-aplicada",
    "MA-0790 Tópicos de análisis": "curso-topicos-analisis-aplicada",
    "MA-0791 Tópicos de Probabilidad": "curso-topicos-probabilidad-aplicada",
    "MA-0792 Tópicos de Ecuaciones diferenciales": "curso-topicos-ecuaciones-diferenciales-aplicada",
    "MA-0793 Tópicos de Geometría": "curso-topicos-geometria-aplicada",
    "MA-0794 Tópicos de Modelación": "curso-topicos-modelacion-aplicada",
    "MA-0795 Tópicos de Computación científica": "curso-topicos-computacion-cientifica-aplicada",
    "MA-0796 Tópicos de Álgebra": "curso-topicos-algebra-aplicada",
    "MA-0797 Tópicos de Matemática discreta": "curso-topicos-matematica-discreta-aplicada",
    "MA-0798 Tópicos de Análisis de datos": "curso-topicos-analisis-datos-aplicada",
    "MA-0799 Tópicos de Aprendizaje automático": "curso-topicos-aprendizaje-automatico-aplicada",
    "MA-0830 Tópicos de Teoría de Números": "curso-topicos-teoria-numeros-aplicada",
    "MA-0831 Tópicos de Lógica": "curso-topicos-logica-aplicada",
    "MA-0832 Tópicos en Topología": "curso-topicos-topologia-aplicada",
    "MA-0711 Lógica": "curso-logica-aplicada",
    "MA-0820 Teoría de modelos": "curso-teoria-modelos-aplicada",
}


def load_titles(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for key in (
        "I Ciclo", "II Ciclo", "III Ciclo", "IV Ciclo",
        "V Ciclo", "VI Ciclo", "VII Ciclo",
        "Optativas de núcleo", "Optativas temáticas",
        "Optativas",
    ):
        out.extend(data.get(key, []))
    return out


def js_map(d: dict[str, str], titles: list[str], indent: str) -> str:
    lines = []
    for t in titles:
        if t not in d:
            continue
        v = d[t]
        if len(t) > 42:
            lines.append(f'{indent}"{t}":\n{indent}  "{v}",')
        else:
            lines.append(f'{indent}"{t}": "{v}",')
    return "\n".join(lines)


def js_origin(origin: dict, indent: str) -> str:
    return (
        f'{indent}left: {origin["left"]}, top: {origin["top"]}, '
        f'w: {origin["w"]}, h: {origin["h"]},'
    )


def js_hotspot(d: dict[str, tuple], titles: list[str], indent: str) -> str:
    lines = []
    for t in titles:
        if t not in d:
            continue
        vals = d[t]
        dx, dy = vals[0], vals[1]
        if len(vals) >= 4:
            body = f"dx: {dx}, dy: {dy}, w: {vals[2]}, h: {vals[3]}"
        else:
            body = f"dx: {dx}, dy: {dy}"
        if len(t) > 42:
            lines.append(f'{indent}"{t}": {{\n{indent}  {body},\n{indent}}},')
        else:
            lines.append(f'{indent}"{t}": {{ {body} }},')
    return "\n".join(lines)


def build_config() -> str:
    pura_t = load_titles(ROOT / "pura.json")
    apl_t = load_titles(ROOT / "aplicada.json")
    apl_id = {**ID, **ID_APL_SUFFIX}
    return f"""      const CONFIG = {{
        pura: {{
          mallaFile: "pura.json",
          image: "propuesta_pura.png",
          imageAlt: "Diagrama de la propuesta de malla curricular (énfasis en matemática pura)",
          enfasis: "Énfasis en matemática pura",
          PDF_POR_TITULO: {{
{js_map(PDF, pura_t, "            ")}
          }},
          ID_POR_TITULO: {{
{js_map(ID, pura_t, "            ")}
          }},
          HOTSPOT_ORIGIN: {{
{js_origin(HOTSPOT_ORIGIN_PUR, "            ")}
          }},
          HOTSPOT_POR_TITULO: {{
{js_hotspot(HOTSPOT_PUR, pura_t, "            ")}
          }},
        }},
        aplicada: {{
          mallaFile: "aplicada.json",
          image: "propuesta_aplicada.png",
          imageAlt: "Diagrama de la propuesta de malla curricular (énfasis en matemática aplicada)",
          enfasis: "Énfasis en matemática aplicada",
          PDF_POR_TITULO: {{
{js_map(PDF, apl_t, "            ")}
          }},
          ID_POR_TITULO: {{
{js_map(apl_id, apl_t, "            ")}
          }},
          HOTSPOT_ORIGIN: {{
{js_origin(HOTSPOT_ORIGIN_APL, "            ")}
          }},
          HOTSPOT_POR_TITULO: {{
{js_hotspot(HOTSPOT_APL, apl_t, "            ")}
          }},
        }},
      }};"""


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    start = html.index("const CONFIG = {")
    end = html.index("const STORAGE_KEY =")
    html = html[:start] + build_config() + "\n\n      " + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print(f"Updated {INDEX.name}")


if __name__ == "__main__":
    main()

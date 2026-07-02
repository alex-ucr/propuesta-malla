#!/usr/bin/env python3
"""Generate Tópicos de … course files from the MA-0790 template."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUROS = ROOT / "Cursos"

# (code, slug, title, requisito, area_emphasis, area_genitive, area_adjective)
COURSES = [
    (
        "0791",
        "topicos-probabilidad",
        "Tópicos de Probabilidad",
        "MA-0840 Probabilidad",
        "Probabilidad",
        "la probabilidad",
        "probabilísticos",
    ),
    (
        "0792",
        "topicos-ecuaciones-diferenciales",
        "Tópicos de Ecuaciones diferenciales",
        "MA-0515 Ecuaciones Diferenciales",
        "Ecuaciones diferenciales",
        "las ecuaciones diferenciales",
        "diferenciales",
    ),
    (
        "0793",
        "topicos-geometria",
        "Tópicos de Geometría",
        "MA-0471 Introducción a la Geometría Diferencial",
        "Geometría",
        "la geometría",
        "geométricos",
    ),
    (
        "0794",
        "topicos-modelacion",
        "Tópicos de Modelación",
        "MA-0515 Ecuaciones Diferenciales",
        "Modelación matemática",
        "la modelación matemática",
        "de modelación",
    ),
    (
        "0795",
        "topicos-computacion-cientifica",
        "Tópicos de Computación científica",
        "MA-0641 Matemática Computacional II",
        "Computación científica",
        "la computación científica",
        "computacionales",
    ),
    (
        "0796",
        "topicos-algebra",
        "Tópicos de Álgebra",
        "MA-0561 Algebra Abstracta I",
        "Álgebra",
        "el álgebra",
        "algebraicos",
    ),
    (
        "0797",
        "topicos-matematica-discreta",
        "Tópicos de Matemática discreta",
        "MA-0496 Teoría de Números",
        "Matemática discreta",
        "la matemática discreta",
        "discretos",
    ),
    (
        "0798",
        "topicos-analisis-datos",
        "Tópicos de Análisis de datos",
        "MA-0641 Matemática Computacional II",
        "Análisis de datos",
        "el análisis de datos",
        "de análisis de datos",
    ),
    (
        "0799",
        "topicos-aprendizaje-automatico",
        "Tópicos de Aprendizaje automático",
        "MA-0641 Matemática Computacional II",
        "Aprendizaje automático",
        "el aprendizaje automático",
        "de aprendizaje automático",
    ),
    (
        "0830",
        "topicos-teoria-numeros",
        "Tópicos de Teoría de Números",
        "MA-0496 Teoría de Números",
        "Teoría de números",
        "la teoría de números",
        "de teoría de números",
    ),
    (
        "0831",
        "topicos-logica",
        "Tópicos de Lógica",
        "MA-0711 Lógica",
        "Lógica",
        "la lógica",
        "lógicos",
    ),
    (
        "0832",
        "topicos-topologia",
        "Tópicos en Topología",
        "MA-0635 Introducción a la Topología",
        "Topología",
        "la topología",
        "topológicos",
    ),
]

DRIVER = """% !TeX program = pdflatex
% Compilar desde la raíz del proyecto: latexmk Cursos/{stem}.tex
% Luego: biber {stem} y pdflatex de nuevo (×2), si aplica.
\\documentclass[11pt]{{report}}
\\makeatletter
\\def\\input@path{{{{../}}{{./Cursos/}}{{./}}}}
\\makeatother
\\input{{preamble-body.tex}}

\\begin{{document}}
\\input{{{stem}-cuerpo.tex}}
\\end{{document}}
"""


def cuerpo(code: str, title: str, requisito: str, area: str, area_gen: str, area_adj: str) -> str:
    sigla = f"MA-{code}"
    hy = f"MA{code}"
    return f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%% {sigla} {title} %%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\newpage
\\subsection*{{{sigla} {title}}}
\\addcontentsline{{toc}}{{subsection}}{{{sigla} {title}}}

\\hypertarget{{{hy}}}{{}}
\\begin{{refsection}}
\\begin{{table}}[H]
\\centering{{
\\begin{{tabular}}{{|ll|}}
\\hline
\\textbf{{Año:}} IV  & \\textbf{{Requisitos:}} {requisito} \\\\ 
\\textbf{{Ciclo:}} Optativa  & \\textbf{{Correquisitos:}} Ninguno \\\\ 
\\textbf{{Tipo de curso:}} Teórico & \\textbf{{Horas presenciales por semana:}} 4 \\\\ 
\\textbf{{Créditos:}} 4 & \\textbf{{Horas de trabajo independiente por semana:}} 8 \\\\ \\hline
\\end{{tabular}}
}}
\\end{{table}}

\\subsubsection*{{Descripción del curso}}

Este curso optativo ofrece un espacio formativo para profundizar en temas de \\emph{{{area}}} que no se desarrollan de manera sistemática en otros cursos de la carrera. Cada curso ofrecido bajo esta sigla puede orientarse hacia líneas distintas dentro de {area_gen}---por ejemplo, pero no restringido a, aspectos clásicos o contemporáneos del área---según la especialidad de la persona docente y las necesidades formativas del estudiantado.

La naturaleza abierta del curso permite responder a avances recientes de la disciplina, a demandas del estudiantado avanzado o a líneas de investigación activas en la Escuela de Matemática, siempre dentro del marco general de {area_gen}. Se espera que la persona estudiante consolide su capacidad de lectura de textos especializados, demostración o aplicación de resultados y comunicación matemática en un contexto de mayor autonomía intelectual.

\\subsubsection*{{Objetivos}}

\\textbf{{General:}} Profundizar en un tema de {area_gen}, definido para cada oferta del curso, mediante el estudio guiado de resultados, problemas y, cuando corresponda, aplicaciones.

\\textbf{{Específicos:}} Al finalizar el curso se espera que la persona estudiante sea capaz de:

\\begin{{enumerate}}
\\item Comprender y utilizar los conceptos centrales del bloque temático abordado en el curso correspondiente.
\\item Demostrar o aplicar resultados {area_adj} con el nivel de rigor esperado en cursos avanzados de la carrera.
\\item Consultar y sintetizar bibliografía especializada relacionada con el tema del curso.
\\item Resolver problemas o desarrollar un trabajo integrador vinculado con el contenido del curso.
\\item Comunicar ideas, argumentos y resultados de forma oral y escrita.
\\end{{enumerate}}

\\subsubsection*{{Contenidos}}

Los contenidos no se fijan de manera permanente en el plan de estudios: son \\textbf{{abiertos por oferta}}, siempre que pertenezcan al ámbito de \\emph{{{area}}}. Al inicio del ciclo lectivo, la persona docente debe comunicar por escrito al estudiantado:

\\begin{{itemize}}
\\item el bloque temático general que se desarrollará;
\\item los objetivos específicos de esa oferta;
\\item la bibliografía de referencia;
\\item el cronograma de actividades y criterios de evaluación.
\\end{{itemize}}

El curso incluirá estudio teórico, resolución de problemas y, según criterio docente, un proyecto o trabajo final integrador coherente con el tema elegido.

\\subsubsection*{{Metodología}}

\\noindent \\textbf{{Lineamientos metodológicos:}} La persona docente a cargo de este curso debe respetar las siguientes pautas:

\\begin{{enumerate}}
    \\item Definir y publicar al inicio del curso el programa concreto de la oferta, dentro del marco general de {area_gen}.
    \\item Combinar \\textbf{{clases magistrales}} o \\textbf{{seminarios}} con trabajo independiente y, cuando proceda, sesiones de ejercicios o presentaciones del estudiantado.
    \\item Promover la lectura activa de fuentes especializadas y la discusión crítica de resultados.
    \\item Incluir evaluación formativa continua acorde con el tema y la modalidad de la oferta.
    \\item Cuando las autoridades sanitarias o institucionales impongan restricciones, adaptar las actividades según normativa vigente.
\\end{{enumerate}}

\\textbf{{Sugerencias metodológicas:}} Adicionalmente, se tienen las siguientes recomendaciones para la persona docente a cargo de este curso:

\\begin{{enumerate}}
    \\item Coordinar con la jefatura del departamento la coherencia de la oferta con otros cursos de {area_gen} de la malla.
    \\item Explicitar los prerrequisitos conceptuales particulares de la oferta, más allá del requisito formal del curso.
    \\item Fomentar la participación en coloquios, seminarios o actividades de divulgación del departamento cuando el tema lo permita.
    \\item Documentar la oferta (programa, bibliografía y evaluación) para apoyar futuras reiteraciones del curso.
\\end{{enumerate}}

\\end{{refsection}}
"""


def main() -> None:
    for code, slug, title, req, area, area_gen, area_adj in COURSES:
        stem = f"MA{code}-{slug}"
        cuerpo_path = CUROS / f"{stem}-cuerpo.tex"
        driver_path = CUROS / f"{stem}.tex"
        cuerpo_path.write_text(
            cuerpo(code, title, req, area, area_gen, area_adj),
            encoding="utf-8",
        )
        driver_path.write_text(DRIVER.format(stem=stem), encoding="utf-8")
        print(f"Wrote {cuerpo_path.name}, {driver_path.name}")


if __name__ == "__main__":
    main()

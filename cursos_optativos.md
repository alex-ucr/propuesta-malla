# Cursos optativos — Malla con énfasis en matemática pura

Este documento resume los cursos optativos de matemática incluidos en la propuesta curricular (`pura.json`) y su ubicación en el repositorio.

## Convenciones

| Elemento | Ubicación |
|----------|-----------|
| Programa del curso (cuerpo) | `Cursos/<sigla>-<nombre>-cuerpo.tex` |
| Driver PDF individual | `Cursos/<sigla>-<nombre>.tex` |
| Documento unificado | `propuesta-elementos-programas.tex` |
| Malla interactiva | `pura.json`, `index.html` |
| Contenidos para el modal web | `contenidos_por_curso.json` (generado con `scripts/extract_contenidos.py`) |

Compilar un driver desde la raíz del proyecto:

```bash
pdflatex Cursos/MA0790-topicos-analisis.tex
# Si el curso usa bibliografía por curso:
biber MA0790-topicos-analisis
pdflatex Cursos/MA0790-topicos-analisis.tex
```

O compilar todos los drivers:

```bash
python scripts/compile_cursos_drivers.py
```

## Listado de optativas en matemática

| Sigla | Nombre | Requisito principal | Notas |
|-------|--------|---------------------|-------|
| MA-0725 | Análisis Real II | Por determinar en programa | Análisis real intermedio |
| MA-0840 | Probabilidad | MA-0705 Análisis Real I | Teoría de la medida aplicada a probabilidad |
| MA-0918 | Procesos estocásticos | MA-0840 Probabilidad | Cálculo estocástico, movimiento browniano |
| MA-0703 | Integración | MA-0725 Análisis Real II | Medida abstracta (optativa) |
| MA-0790 | Tópicos de análisis | MA-0551 Principios de análisis en varias variables | **Contenidos abiertos por oferta** (ver abajo) |
| MA-0711 | Lógica | MA-0451; MA-0461 | Fundamentos de lógica matemática |
| MA-0820 | Teoría de modelos | MA-0711 Lógica | Teoría de modelos; aplicaciones al álgebra |

## MA-0790 Tópicos de análisis

Curso de **temas abiertos** dentro del Análisis matemático. El plan de estudios no enumera capítulos fijos: cada vez que se ofrece, la persona docente define el bloque temático (siempre en análisis), la bibliografía, el cronograma y la evaluación, y lo comunica al estudiantado al inicio del ciclo.

**Propósito:** ampliar la formación en análisis más allá de los cursos obligatorios, incorporando temas actuales o de interés especializado sin modificar la malla cada semestre.

**Archivos:**

- `Cursos/MA0790-topicos-analisis.tex`
- `Cursos/MA0790-topicos-analisis-cuerpo.tex`

## MA-0711 Lógica

Optativa de **lógica matemática**: ordinales y cardinales, cálculo de predicados de primer orden, completitud, compacidad e introducción a teoría de modelos.

**Archivos:** `Cursos/MA0711-logica.tex`, `Cursos/MA0711-logica-cuerpo.tex`

## MA-0820 Teoría de modelos

Optativa avanzada en **teoría de modelos** (requiere MA-0711): eliminación de cuantificadores, aplicaciones al álgebra y geometría algebraica, tipos y compacidad.

**Archivos:** `Cursos/MA0820-teoria-modelos.tex`, `Cursos/MA0820-teoria-modelos-cuerpo.tex`

## Cursos optativos de otra disciplina

(Pendiente de documentar según el plan vigente y la propuesta de reestructuración.)

## Cursos optativos complementarios

Ver también `Cursos_optativos.xlsx` (extraído del plan 1992) para referencia histórica de optativas en economía, física, química y computación.

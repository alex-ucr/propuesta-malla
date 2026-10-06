# Cursos optativos — Propuesta curricular

Las optativas se organizan en **núcleo** (programas fijos) y **temáticos** (incluye cursos «Tópicos de…» con contenidos abiertos por oferta).

Fuente de verdad: `scripts/optativas_catalog.json`, `propuesta-elementos-programas.tex`, `pura.json` / `aplicada.json`.

## Convenciones

| Elemento | Ubicación |
|----------|-----------|
| Programa del curso (cuerpo) | `Cursos/<sigla>-<nombre>-cuerpo.tex` |
| Driver PDF individual | `Cursos/<sigla>-<nombre>.tex` |
| Documento unificado | `propuesta-elementos-programas.tex` |
| Malla interactiva | `index.html`, `pura.json`, `aplicada.json` |
| Contenidos para el modal web | `contenidos_por_curso.json` |

## Optativas de núcleo (21)

| Sigla | Nombre |
|-------|--------|
| MA-0788 | Análisis Real II |
| MA-0717 | Geometría Diferencial |
| MA-0920 | Ecuaciones en Derivadas Parciales Numéricas |
| MA-0806 | Análisis Funcional |
| MA-0783 | Integración |
| MA-0525 | Combinatoria |
| MA-0528 | Sistemas Dinámicos |
| CA-0411 | Análisis de Datos I |
| MA-0815 | Análisis Armónico |
| MA-0876 | Teoría Algebraica de Números |
| MA-0858 | Teoría de Conjuntos |
| MA-0719 | Geometría Algebraica |
| MA-0781 | Lógica |
| MA-0756 | Ecuaciones Diferenciales Parciales |
| MA-0889 | Álgebra Conmutativa |
| MA-0804 | Topología Algebraica |
| MA-0827 | Estadística Matemática |
| MA-0824 | Teoría de Modelos |
| MA-0841 | Probabilidad |
| MA-0849 | Teoría de Módulos |
| MA-0734 | Optimización |

## Optativas temáticas (27)

| Sigla | Nombre |
|-------|--------|
| CA-0721 | Probabilidad |
| MA-0647 | Modelación Matemática |
| MA-0928 | Procesos Estocásticos |
| MA-0917 | Estadística II |
| CA-0512 | Modelos lineales |
| CA-0612 | Series de Tiempo |
| MA-0406 | Introducción a la Optimización |
| MA-0477 | Ecuaciones Diferenciales Parciales Aplicadas |
| CA-0203 | Herramientas de Ciencia de Datos I |
| CA-0304 | Herramientas de Ciencia de Datos II |
| MA-0759 | Tópicos de Matemática Financiera |
| MA-0790 | Tópicos de Análisis |
| MA-0791 | Tópicos de Probabilidad |
| MA-0792 | Tópicos de Ecuaciones Diferenciales |
| MA-0793 | Tópicos de Geometría |
| MA-0794 | Tópicos de Modelación |
| MA-0795 | Tópicos de Computación Científica |
| MA-0796 | Tópicos de Álgebra |
| MA-0797 | Tópicos de Matemática Discreta |
| MA-0798 | Tópicos de Análisis de Datos |
| MA-0799 | Tópicos de Aprendizaje Automático |
| MA-0809 | Teoría Analítica de Números |
| MA-0830 | Tópicos de Teoría de Números |
| MA-0831 | Tópicos de Lógica |
| MA-0832 | Tópicos en Topología |
| MA-0833 | Tópicos de Estadística |
| CA-0412 | Análisis de Datos II |

Los cursos marcados como *pendiente de elaboración* tienen cascarón en `Cursos/` (`Programa pendiente de elaboración`).

## Scripts

```bash
python scripts/setup_optativas_clasificacion.py   # cascarones + tex + json
python scripts/sync_optativas_pura.py             # verificar sincronía
python scripts/rebuild_index_config.py            # actualizar index.html
python scripts/extract_contenidos.py              # regenerar contenidos JSON
```

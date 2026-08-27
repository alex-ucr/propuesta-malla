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
| MA-0725 | Análisis Real II |
| MA-0707 | Geometría Diferencial |
| MA-0920 | Ecuaciones en derivadas parciales numéricas |
| MA-0806 | Análisis funcional |
| MA-0703 | Integración |
| MA-0525 | Combinatoria |
| MA-0528 | Sistemas dinámicos |
| CA-0411 | Análisis de Datos I |
| MA-0815 | Análisis armónico |
| MA-0506 | Teoría algebraica de números |
| MA-0512 | Teoría de conjuntos |
| MA-0709 | Geometría algebraica I |
| MA-0711 | Lógica |
| MA-0755 | Ecuaciones diferenciales parciales |
| MA-0889 | Álgebra conmutativa |
| MA-0804 | Topología algebraica |
| MA-0817 | Estadística matemática I |
| MA-0820 | Teoría de modelos |
| MA-0840 | Probabilidad |
| MA-0860 | Teoría de módulos |
| MA-0714 | Optimización |

## Optativas temáticas (24)

| Sigla | Nombre |
|-------|--------|
| CA-0721 | Probabilidad |
| MA-0647 | Modelación Matemática |
| MA-0918 | Procesos estocásticos |
| MA-0917 | Estadística II |
| CA-0512 | Modelos lineales |
| CA-0612 | Series de tiempo |
| MA-0406 | Introducción a la optimización |
| CA-0203 | Herramientas de ciencia de datos I |
| CA-0304 | Herramientas de ciencia de datos II |
| MA-0790 | Tópicos de análisis |
| MA-0791 | Tópicos de Probabilidad |
| MA-0792 | Tópicos de Ecuaciones diferenciales |
| MA-0793 | Tópicos de Geometría |
| MA-0794 | Tópicos de Modelación |
| MA-0795 | Tópicos de Computación científica |
| MA-0796 | Tópicos de Álgebra |
| MA-0797 | Tópicos de Matemática discreta |
| MA-0798 | Tópicos de Análisis de datos |
| MA-0799 | Tópicos de Aprendizaje automático |
| MA-0609 | Teoría analítica de números |
| MA-0830 | Tópicos de Teoría de Números |
| MA-0831 | Tópicos de Lógica |
| MA-0832 | Tópicos en Topología |
| CA-0412 | Análisis de datos II |

Los cursos marcados como *pendiente de elaboración* tienen cascarón en `Cursos/` (`Programa pendiente de elaboración`).

## Scripts

```bash
python scripts/setup_optativas_clasificacion.py   # cascarones + tex + json
python scripts/sync_optativas_pura.py             # verificar sincronía
python scripts/rebuild_index_config.py            # actualizar index.html
python scripts/extract_contenidos.py              # regenerar contenidos JSON
```

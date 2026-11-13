#!/usr/bin/env python3
"""
Generar las tablas del resumen ejecutivo (OPES-CONARE) a partir de las fuentes del proyecto.

Salidas (se incluyen desde resumen-ejecutivo.tex):
  resumen-ejecutivo-cursos.tex         apartado 8: listado de cursos (nombre, créditos, ciclo)
  resumen-ejecutivo-descripciones.tex  apartado 9: nombre, objetivo general y temática resumida
  resumen-ejecutivo-docentes.tex       apartado 10: correspondencia curso-docente

Fuentes: malla-curricular-tablas.tex, propuesta-lista-cursos.tex, Cursos/*-cuerpo.tex,
propuesta-gestion-plan.tex (tabla de profesores por curso) y Documentos/optativas_otras_carreras.xlsx.
Uso: python scripts/generate_resumen_ejecutivo.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_optativas_otra_disciplina_tex import load_rows  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CURSOS = ROOT / "Cursos"
SMALL = {"de", "del", "la", "las", "el", "los", "y", "e", "en", "a", "al", "o", "u", "para", "con", "por"}
ROMAN = re.compile(r"^[IVX]+$")


# ----------------------------------------------------------------------------- utilidades
def read(p: Path) -> str:
    return p.read_bytes().decode("utf-8")


def write(name: str, text: str) -> None:
    (ROOT / name).write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    print("escrito", name)


def strip_comments(t: str) -> str:
    return "\n".join(x for x in t.splitlines() if not x.lstrip().startswith("%"))


def title_case(s: str) -> str:
    words = s.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if ROMAN.match(w):
            out.append(w)
        elif i and lw in SMALL:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return " ".join(out)


def sigla(code: str) -> str:
    m = re.match(r"^([A-Z]{2})-?(\d{4})$", code)
    return f"{m.group(1)}-{m.group(2)}" if m else code


def brace_group(s: str, i: int) -> tuple[str, int]:
    """s[i] == '{'; devuelve (contenido, índice tras la llave de cierre)."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
    return s[i + 1 :], len(s)


_ACC = {("'", b): a for b, a in zip("aeiouAEIOU", "áéíóúÁÉÍÓÚ")}
_ACC.update({("~", "n"): "ñ", ("~", "N"): "Ñ"})


def clean(s: str) -> str:
    s = unwrap(re.sub(r"(?<!\\)%[^\n]*", "", s))
    s = re.sub(r"\\([~'])\{?([A-Za-z])\}?", lambda m: _ACC.get((m.group(1), m.group(2)), m.group(2)), s)
    s = s.replace("{,}", ",")
    s = re.sub(r"\\(?:cite|parencite|textcite)\*?(?:\[[^\]]*\])*\{[^}]*\}", "", s)
    s = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", s)
    s = s.replace(r"\newline", " ").replace("~", " ")
    s = re.sub(r"\\\\", " ", s)
    s = re.sub(r"\s*\(\s*\d+(?:[.,]\d+)?\s*(?:a\s*\d+\s*)?semanas?[^)]*\)", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    return s.strip(" :;,")


def esc(s: str) -> str:
    return s.translate(str.maketrans({"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_"}))


# ----------------------------------------------------------------------------- nombres y créditos
def course_names() -> dict[str, str]:
    """sigla -> nombre canónico según propuesta-lista-cursos.tex."""
    names: dict[str, str] = {}
    t = strip_comments(read(ROOT / "propuesta-lista-cursos.tex"))
    for m in re.finditer(r"\\item\s*(?:\\hyperlink\{[^}]*\})?\{((?:MA|CA)-\d{4})\s+([^}]*)\}", t):
        names.setdefault(m.group(1).replace("-", ""), m.group(2).strip())
    return names


def cuerpo_for(code: str) -> Path | None:
    hits = sorted(CURSOS.glob(f"{code}-*-cuerpo.tex"))
    hits = [h for h in hits if "propuesta" not in h.name]
    return hits[0] if hits else None


def credits_of(code: str) -> str | None:
    f = cuerpo_for(code)
    if not f:
        return None
    t = read(f).replace("% ", "")
    m = re.search(r"Créditos:\}\s*(\d+)", t)
    return m.group(1) if m else None


NAMES = course_names()


def name_of(code: str, fallback: str = "") -> str:
    return NAMES.get(code) or fallback


# ----------------------------------------------------------------------------- apartado 8
BLOCKS = [
    ("Bloque común (ciclos I a III)", "Total créditos bloque común"),
    ("Énfasis en matemática pura (ciclos IV a VIII)", "Total créditos bachillerato pura"),
    ("Énfasis en matemática aplicada (ciclos IV a VIII)", "Total créditos bachillerato aplicada"),
    ("Énfasis en matemática pura (licenciatura, ciclos IX y X)", "Total créditos licenciatura pura"),
    ("Énfasis en matemática aplicada (licenciatura, ciclos IX y X)", "Total créditos licenciatura aplicada"),
]


def parse_malla() -> list[dict]:
    t = strip_comments(read(ROOT / "malla-curricular-tablas.tex"))
    blocks: list[dict] = []
    cur = None
    for line in t.splitlines():
        m = re.match(r"\\MallaSubsection\{(.*)\}", line)
        if m:
            cur = {"title": m.group(1), "rows": [], "totals": {}, "final": None}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\\MallaCicloTotal\{(\d+)\}\{(\d+)\}", line)
        if m:
            cur["rows"].append(("total", int(m.group(1)), int(m.group(2))))
            continue
        m = re.match(r"\\MallaTotalFinal\{(.*?)\}\{(\d+)\}", line)
        if m:
            cur["final"] = (m.group(1), int(m.group(2)))
            continue
        if re.match(r"^\d+ & ", line):
            cells = [c.strip() for c in line.rstrip("\\ ").split("&")]
            cells[-1] = cells[-1].rstrip("\\ ").strip()
            ciclo = int(cells[0])
            raw = cells[1]
            m2 = re.match(r"\\MallaSigla(?:\[[^\]]*\])?\{([A-Z]{2}\d{4})\}", raw)
            code = m2.group(1) if m2 else raw
            nm = cells[2]
            if m2 and code in NAMES:
                nm = NAMES[code]
            elif nm.isupper():
                nm = title_case(nm)
            cred = cells[7] if len(cells) > 7 and cells[7] else "0"
            cur["rows"].append(("curso", ciclo, sigla(code), nm, cred))
    return blocks


def longtable_open(cols: str, caption: str, label: str, header: str, ncols: int) -> list[str]:
    head = [r"\hline", r"\rowcolor{Azul-UCR}", header + r" \\ \hline"]
    return (
        [r"\begingroup", r"\small", r"\arrayrulecolor{Azul-UCR!80}%", r"\renewcommand{\arraystretch}{1.2}%",
         r"\rowcolors{2}{white}{Celeste-UCR!12}%",
         r"\begin{longtable}{" + cols + "}",
         rf"\caption{{{caption}}}\label{{{label}}}\\"]
        + head + [r"\endfirsthead"] + head + [r"\endhead", r"\hline", r"\endfoot"]
    )


def hdr(*cells: str) -> str:
    return " & ".join(rf"\textcolor{{white}}{{\textbf{{{c}}}}}" for c in cells)


def build_cursos() -> str:
    out = ["% Generado por scripts/generate_resumen_ejecutivo.py. No editar a mano.", ""]
    out.append(r"\subsection*{Cursos de la estructura curricular}")
    out.append("")
    labels = ["res:malla-comun", "res:malla-pura", "res:malla-aplicada", "res:lic-pura", "res:lic-aplicada"]
    n_total = 0
    for blk, label in zip(parse_malla(), labels):
        cap = blk["title"].replace("matemática", "Matemática").replace("énfasis", "énfasis")
        cols = r"|c|l|>{\raggedright\arraybackslash}p{8.6cm}|c|"
        out += longtable_open(cols, cap, label, hdr("Ciclo", "Sigla", "Nombre del curso", "Créditos"), 4)
        for r in blk["rows"]:
            if r[0] == "total":
                out.append(rf"\rowcolor{{Verde-UCR!28}}\multicolumn{{4}}{{|l|}}{{\textit{{Créditos del ciclo {r[1]}: {r[2]}}}}} \\ \hline")
            else:
                n_total += 1
                out.append(rf"{r[1]} & {r[2]} & {esc(r[3])} & {r[4]} \\ \hline")
        if blk["final"]:
            lab, n = blk["final"]
            out.append(rf"\rowcolor{{Amarillo-UCR!45}}\multicolumn{{4}}{{|r|}}{{\textbf{{{lab}: {n}}}}} \\ \hline")
        out += [r"\end{longtable}", r"\endgroup", ""]

    # optativas de matemática (desde propuesta-lista-cursos)
    t = strip_comments(read(ROOT / "propuesta-lista-cursos.tex"))
    out.append(r"\subsection*{Cursos optativos de Matemática}")
    out.append("")
    sections = re.split(r"\\subsubsection\*\{", t)
    wanted = [("OPT-001", "Optativas de núcleo en Matemática Pura (OPT-001)", "res:opt001"),
              ("OPT-002", "Optativas de núcleo en Matemática Aplicada (OPT-002)", "res:opt002"),
              ("OPT-003", "Optativas generales en Matemática (OPT-003)", "res:opt003")]
    for key, cap, label in wanted:
        sec = next((s for s in sections if key in s.split("}", 1)[0]), None)
        if sec is None:
            continue
        items = re.findall(r"\\item\s*(?:\\hyperlink\{[^}]*\})?\{((?:MA|CA)-\d{4})\s+([^}]*)\}", sec)
        out += longtable_open(r"|l|>{\raggedright\arraybackslash}p{9.4cm}|c|", cap, label, hdr("Sigla", "Nombre del curso", "Créditos"), 3)
        for code, nm in items:
            cr = credits_of(code.replace("-", "")) or "---"
            out.append(rf"{code} & {esc(nm.strip())} & {cr} \\ \hline")
        out += [r"\end{longtable}", r"\endgroup", ""]
    out.append(r"{\footnotesize Los créditos de los cursos de Ciencias Actuariales (CA) se rigen por el plan de estudios de la carrera que los administra (---: no registrado en esta propuesta).\par}")
    out.append("")

    # optativas de otra disciplina (Excel)
    rows = load_rows()
    out.append(r"\subsection*{Cursos optativos de otra disciplina (OPT-)}")
    out.append("")
    out += longtable_open(r"|l|>{\raggedright\arraybackslash}p{6cm}|c|>{\raggedright\arraybackslash}p{4.2cm}|",
                          "Cursos optativos de otra disciplina", "res:opt-otra",
                          hdr("Sigla", "Nombre del curso", "Créditos", "Unidad académica"), 4)
    for r in rows:
        out.append(rf"{sigla(str(r['Sigla']).strip())} & {esc(str(r['Nombre']).strip())} & {r['Créditos']} & "
                   rf"{esc(str(r['Escuela que ofrece el curso']).replace('Escuela de ', '').replace('Escuela ', '').strip())} \\ \hline")
    out += [r"\end{longtable}", r"\endgroup", ""]
    print("cursos en malla:", n_total, "| optativas otra disciplina:", len(rows))
    return "\n".join(out)


# ----------------------------------------------------------------------------- apartado 9
def top_items(cont: str) -> list[str]:
    toks = list(re.finditer(r"\\begin\{(?:enumerate|itemize)\}|\\end\{(?:enumerate|itemize)\}|\\item\b", cont))
    depth, items = 0, []
    for k, m in enumerate(toks):
        tok = m.group(0)
        if tok.startswith(r"\begin"):
            depth += 1
        elif tok.startswith(r"\end"):
            depth -= 1
        elif depth == 1:
            nxt = toks[k + 1].start() if k + 1 < len(toks) else len(cont)
            items.append(cont[m.end() : nxt].strip())
    return items


def unwrap(s: str) -> str:
    """Quita \\textbf{..}, \\textit{..} y \\emph{..} conservando el contenido (con llaves anidadas)."""
    pat = re.compile(r"\\(?:textbf|textit|emph)\{")
    while True:
        m = pat.search(s)
        if not m:
            return s
        g, end = brace_group(s, m.end() - 1)
        s = s[: m.start()] + g + s[end:]


def item_title(it: str) -> str:
    it = it.lstrip()
    head = unwrap(re.split(r"\\begin\{(?:enumerate|itemize)\}", it, maxsplit=1)[0])
    first = re.split(r"(?<=[a-záéíóúñ\)])\.\s|:\s*\n|:\s|\n\s*\n", head, maxsplit=1)[0]
    return clean(first).rstrip(".")


def describe(f: Path) -> dict | None:
    t = strip_comments(read(f))
    m = re.search(r"\\subsection\*\{((?:MA|CA)-\d{4})\s+([^}]*)\}", t)
    if not m:
        return None
    code = m.group(1)
    g = re.search(r"\\textbf\{(?:Objetivo )?[Gg]eneral:\}\s*(.*?)(?=\\\\|\n\s*\n|\\textbf\{)", t, re.S)
    obj = clean(g.group(1)) if g else ""
    c = re.search(r"\\subsubsection\*\{Contenidos\}(.*?)(?=\\subsubsection\*\{|\\printcursosbibliography|\Z)", t, re.S)
    cont = c.group(1) if c else ""
    if r"abiertos por oferta" in cont or "no se fijan de manera permanente" in cont:
        para = re.split(r"\n\s*\n", cont.strip())[0]
        sent = clean(re.split(r"(?<=[a-záéíóúñ\)])\.\s", para, maxsplit=1)[0]).rstrip(".") + "."
        tema = sent
    else:
        tit = [item_title(i) for i in top_items(cont)]
        tit = [x for x in tit if x]
        tema = "; ".join(tit) + "." if tit else ""
    return {"code": code, "name": name_of(code.replace("-", ""), m.group(2).strip()), "cred": credits_of(code.replace("-", "")) or "---",
            "obj": obj, "tema": tema}


def build_descripciones() -> str:
    t = strip_comments(read(ROOT / "propuesta-lista-cursos.tex"))
    codes: list[str] = []
    for m in re.finditer(r"\\item\s*(?:\\hyperlink\{[^}]*\})?\{((?:MA|CA)-\d{4})\s+[^}]*\}", t):
        c = m.group(1).replace("-", "")
        if c not in codes:
            codes.append(c)
    out = ["% Generado por scripts/generate_resumen_ejecutivo.py. No editar a mano.", ""]
    out += longtable_open(
        r"|>{\raggedright\arraybackslash}p{3.3cm}|>{\raggedright\arraybackslash}p{5.5cm}|>{\raggedright\arraybackslash}p{6.9cm}|",
        "Descripción de los cursos propios de la carrera", "res:descripciones",
        hdr("Curso (créditos)", "Objetivo general", "Temática resumida"), 3)
    n, skipped = 0, []
    for c in codes:
        f = cuerpo_for(c)
        d = describe(f) if f else None
        if not d or not d["obj"]:
            skipped.append(c)
            continue
        n += 1
        out.append(rf"\textbf{{{d['code']}}}\newline {d['name']} ({d['cred']}) & {d['obj']} & {d['tema']} \\ \hline")
    out += [r"\end{longtable}", r"\endgroup", ""]
    print("descripciones:", n, "| sin programa:", skipped)
    return "\n".join(out)


# ----------------------------------------------------------------------------- apartado 10
def parse_docentes() -> list[dict]:
    """Cursos de la tabla de profesores por curso de propuesta-gestion-plan.tex, en orden de aparición."""
    t = read(ROOT / "propuesta-gestion-plan.tex")
    m = re.search(r"Código / Curso.*?\\endhead\r?\n(.*?)\\caption\{[^}]*\}\r?\n\\label\{tabla:cursos-docentes\}", t, re.S)
    body = m.group(1).replace("\r\n", "\n")
    cursos: list[dict] = []
    cur = None
    for line in body.splitlines():
        ls = line.strip()
        if not ls or ls.startswith("%") or ls.startswith(("\\hline", "\\rowcolor", "\\multicolumn")):
            continue
        cells = [c.strip() for c in ls.rstrip("\\ ").split("&")]
        first = cells[0]
        mc = re.match(r"\\textbf\{([^}]*)\}(.*)", first)
        if mc:
            cur = {"code": mc.group(1), "name": "", "docentes": [], "existente": False}
            cursos.append(cur)
            rest = mc.group(2)
            mn = re.search(r"\\textit\{(.*)\}", rest)
            if mn:
                cur["name"] = mn.group(1)
        elif cur is not None and not cur["name"]:
            mn = re.match(r"\\textit\{(.*)\}", first)
            if mn:
                cur["name"] = mn.group(1)
        if cur is None or len(cells) < 2:
            continue
        who = cells[1]
        if "Curso ya existente" in who:
            cur["existente"] = True
        elif who:
            cur["docentes"].append(who)
    return cursos


def build_docentes() -> str:
    cursos = parse_docentes()
    grupos = [
        ("Escuela de Matemática, Departamento de Matemática", lambda c: not c["existente"]),
        ("Escuela de Matemática, Departamento de Ciencias Actuariales", lambda c: c["existente"] and c["code"].startswith("CA")),
        ("Escuela de Matemática, otros cursos ya existentes", lambda c: c["existente"] and not c["code"].startswith("CA")),
    ]
    col = (r"|>{\raggedright\arraybackslash}p{6.9cm}|>{\raggedright\arraybackslash}p{9.8cm}|")
    header = r"\textcolor{white}{\textbf{Nombre del curso}} & \textcolor{white}{\textbf{Persona(s) docente(s) a cargo}}"
    out = ["% Generado por scripts/generate_resumen_ejecutivo.py. No editar a mano.", "",
           r"\begingroup", r"\small", r"\arrayrulecolor{Azul-UCR!80}%", r"\renewcommand{\arraystretch}{1.2}%",
           r"\begin{longtable}{" + col + "}",
           r"\caption{Listado de las actividades de formación (cursos) y personal docente a cargo}\label{res:docentes}\\",
           r"\hline", r"\rowcolor{Azul-UCR}", header + r" \\ \hline", r"\endfirsthead",
           r"\hline", r"\rowcolor{Azul-UCR}", header + r" \\ \hline", r"\endhead", r"\hline", r"\endfoot"]
    n = 0
    for titulo, pred in grupos:
        sel = [c for c in cursos if pred(c)]
        if not sel:
            continue
        out.append(rf"\rowcolor{{Celeste-UCR!35}}\multicolumn{{2}}{{|l|}}{{\textbf{{{esc(titulo)}}}}} \\ \hline")
        for c in sel:
            code = c["code"]
            nm = name_of(code.replace("-", ""), c["name"]) or c["name"]
            if c["existente"]:
                quien = r"\textit{Curso ya existente, a cargo del personal docente que actualmente lo imparte.}"
            else:
                quien = "; ".join(esc(x) for x in c["docentes"]) or r"\textit{Por asignar}"
            out.append(rf"\textbf{{{esc(code)}}} {esc(nm)} & {quien} \\ \hline")
            n += 1
    out += [r"\end{longtable}", r"\endgroup", ""]
    print("cursos en tabla docentes:", n)
    return "\n".join(out)


def main() -> None:
    write("resumen-ejecutivo-cursos.tex", build_cursos())
    write("resumen-ejecutivo-descripciones.tex", build_descripciones())
    write("resumen-ejecutivo-docentes.tex", build_docentes())


if __name__ == "__main__":
    main()

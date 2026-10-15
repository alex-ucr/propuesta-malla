"""Genera las filas de los cuadros de «Situación de la población estudiantil».

Lee las salidas del SIIAGC (copias locales de los .xlsx de OneDrive) y escribe un
fragmento LaTeX por cuadro (T1.tex ... T12.tex) en el directorio de salida, más un
resumen de cifras clave en la consola. Solo se usan datos agregados.

    python scripts/generate_poblacion_estudiantil.py PUNTAJES.xlsx DURACION.xlsx \
        PERMANENCIA.xlsx ESTADO.xlsx [OUTDIR]
"""
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd


def _r(x, q):
    return str(Decimal(repr(float(x))).quantize(Decimal(q), ROUND_HALF_UP)).replace(".", ",")


def f1(x):
    return _r(x, "0.1")


def f2(x):
    return _r(x, "0.01")


def pct(a, b):
    return f1(100 * a / b) if b else "---"


def group_row(title, ncols):
    return (f"\\rowcolor{{Celeste-UCR!35}}\\multicolumn{{{ncols}}}{{|l|}}"
            f"{{\\cellcolor{{Celeste-UCR!35}}\\textbf{{{title}}}}} \\\\ \\hline")


def admision(path):
    p = pd.read_excel(path, header=1).iloc[:, :8]
    p.columns = ["anio", "modal", "corte", "cupo", "cupo_disp", "sol", "acep", "noacep"]
    p = p[pd.to_numeric(p.anio, errors="coerce").notna()].copy()
    p["anio"] = p.anio.astype(int)
    p["cupo_disp"] = p.cupo_disp.fillna(p.cupo)
    for c in ["corte", "cupo", "cupo_disp", "sol", "acep"]:
        p[c] = pd.to_numeric(p[c])
    return p


def graduados(path):
    d = pd.read_excel(path, header=1)
    d.columns = ["carne", "a1", "a2", "nom", "sexo", "correo", "ing_ucr", "ing_car", "grad",
                 "ciclo", "jur", "grado", "dur_ef", "dur", "honor", "excl", "adic", "modal",
                 "cod", "tit"]
    d = d.dropna(subset=["grad"]).copy()
    d["grad"] = d.grad.astype(int)
    d["ing_car"] = d.ing_car.astype(int)
    # La columna trae «Sí» con un carácter dañado; basta distinguir «NO».
    d["excl"] = d.excl.where(d.excl == "NO", "SI")
    return d


def ciclo(s):
    """«II-2025» -> ordinal cronológico; None si no hay ciclo."""
    s = str(s)
    if "-" not in s or s.startswith("-"):
        return None
    c, y = s.split("-")
    return int(y) * 3 + {"I": 0, "II": 1, "III": 2}[c]


def permanencia(path):
    xl = pd.ExcelFile(path)
    frames = []
    for sh in xl.sheet_names:
        raw = pd.read_excel(xl, sh, header=None, dtype=str)
        h = raw.index[raw.iloc[:, 0].astype(str).str.startswith("Carn")][0]
        df = raw.iloc[h + 1:].copy()
        df.columns = ["carne", "a1", "a2", "nom", "modal", "consol", "ing", "nivel7", "ult_ucr",
                      "ult_car", "excl_pre", "excl_bach", "excl_lic", "g_pre", "g_bach", "g_lic",
                      "disc"]
        df["cohorte"] = int(sh)
        frames.append(df)
    p = pd.concat(frames, ignore_index=True)
    p = p[p.modal != "Visitante"].copy()
    uc, uu = p.ult_car.map(ciclo), p.ult_ucr.map(ciclo)
    corte = ciclo(f"I-{int(max(filter(None, uc))) // 3 - 1}")
    p["grad"] = p.g_bach.ne("--")
    p["activa"] = ~p.grad & (uc >= corte)
    p["otra_ucr"] = ~p.grad & ~p.activa & (uu >= corte)
    p["fuera"] = ~p.grad & ~p.activa & ~p.otra_ucr
    p["anios_aband"] = p.ult_car.str.extract(r"-(\d{4})$")[0].astype(float) - p.cohorte
    return p, corte


def estado(path):
    e = pd.read_excel(path, header=1)
    e.columns = ["carne", "a1", "a2", "nom", "correo", "sexo", "edad", "disc", "nac", "idprov",
                 "prov", "idcan", "can", "iddis", "dis", "idcol", "col", "idtipo", "tipocol",
                 "tipoing", "aprob", "reprob", "aprob_otras", "nivel", "ing", "estado"]
    return e


MODALIDADES = [
    ("Primer Ingreso", "Primer ingreso"),
    ("Primer Ingreso (Diferida.)", "Primer ingreso (diferido)"),
    ("Admisión", "Traslado por nota de admisión"),
    ("Rendimiento Académico", "Rendimiento académico"),
    ("Excelencia Académica", "Excelencia académica"),
]


MODALIDADES_PERM = [
    ("Prueba de aptitud académica (Primer ingreso)", "Primer ingreso"),
    ("Prueba de aptitud académica (Traslado)", "Traslado por nota de admisión"),
    ("Excelencia académica", "Excelencia académica"),
    ("Rendimiento académico", "Rendimiento académico"),
]

ESTADOS = [
    ("ACTIVO MATRICULADO", "Activa con matrícula"),
    ("ACTIVO SIN MATRÍCULA", "Activa sin matrícula"),
    ("INACTIVO GRADUADO DE BACHILLERATO", "Inactiva, graduada de bachillerato"),
    ("INACTIVO", "Inactiva (sin graduarse)"),
    ("NO HA CONSOLIDADO SU INGRESO A LA UCR", "No ha consolidado su ingreso a la UCR"),
]


def cuadros_permanencia(p):
    out = {}
    c = p[p.consol == "SI"]
    rows = []

    def fila(lab, s, nocons):
        n = len(s)
        ab = int(s.otra_ucr.sum() + s.fuera.sum())
        return (f"{lab} & {nocons} & {n} & {int(s.grad.sum())} & {int(s.activa.sum())} & "
                f"{int(s.otra_ucr.sum())} & {int(s.fuera.sum())} & {pct(s.grad.sum(), n)} & "
                f"{pct(ab, n)} \\\\ \\hline")

    for y, s in c.groupby("cohorte"):
        rows.append(fila(y, s, int((p[p.cohorte == y].consol != "SI").sum())))
    rows.append(fila("\\textbf{Total}", c, int((p.consol != "SI").sum())))
    out["T7"] = rows

    def nivel(s):
        v = s.nivel7
        al_dia = int((v == "7").sum())
        return (f"{len(s)} & {al_dia} & {int(v.isin(['4', '5', '6']).sum())} & "
                f"{int(v.isin(['1', '2', '3']).sum())} & {int((v == 'NO MATRICULÓ').sum())} & "
                f"{pct(al_dia, len(s))}")

    rows = [f"{y} & {nivel(s)} \\\\ \\hline" for y, s in c.groupby("cohorte")]
    rows.append(f"\\textbf{{Total}} & {nivel(c)} \\\\ \\hline")
    out["T8"] = rows

    rows = []
    for key, lab in MODALIDADES_PERM + [(None, "\\textbf{Total}")]:
        s = c if key is None else c[c.modal == key]
        n = len(s)
        ab = s.otra_ucr.sum() + s.fuera.sum()
        rows.append(f"{lab} & {n} & {int(s.grad.sum())} & {pct(s.grad.sum(), n)} & "
                    f"{int(s.activa.sum())} & {pct(s.activa.sum(), n)} & {int(ab)} & "
                    f"{pct(ab, n)} \\\\ \\hline")
    out["T9"] = rows

    ab = c[c.otra_ucr | c.fuera]
    yrs = ab.anios_aband.clip(lower=0)
    tramos = [("En el mismo año de ingreso", yrs == 0), ("Al segundo año", yrs == 1),
              ("Al tercer año", yrs == 2), ("Al cuarto año", yrs == 3),
              ("Al quinto año o después", yrs >= 4),
              ("Sin matrícula en cursos de la carrera", yrs.isna())]
    rows, acc, n = [], 0, len(ab)
    for lab, m in tramos:
        k = int(m.sum())
        if not k:
            continue
        acc += k
        rows.append(f"{lab} & {k} & {pct(k, n)} & {pct(acc, n)} \\\\ \\hline")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{n}}} & \\textbf{{100,0}} & \\\\ \\hline")
    out["T10"] = rows
    return out


def cuadros_estado(e):
    out = {}
    n = len(e)
    rows = []
    for key, lab in ESTADOS:
        s = e[e.estado == key]
        rows.append(f"{lab} & {(s.sexo == 'FEMENINO').sum()} & {(s.sexo == 'MASCULINO').sum()} & "
                    f"{len(s)} & {pct(len(s), n)} \\\\ \\hline")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{(e.sexo == 'FEMENINO').sum()}}} & "
                f"\\textbf{{{(e.sexo == 'MASCULINO').sum()}}} & \\textbf{{{n}}} & "
                f"\\textbf{{100,0}} \\\\ \\hline")
    out["T11"] = rows

    a = e[e.estado.str.startswith("ACTIVO")]
    na = len(a)
    mat = a.estado == "ACTIVO MATRICULADO"
    reg = ["SAN JOSÉ", "ALAJUELA", "CARTAGO", "HEREDIA"]
    grupos = [
        ("Año de ingreso a la carrera", [
            ("2015 o antes", a.ing <= 2015), ("2016 a 2020", a.ing.between(2016, 2020)),
            ("2021 a 2023", a.ing.between(2021, 2023)), ("2024 a 2026", a.ing >= 2024)]),
        ("Sexo", [("Mujeres", a.sexo == "FEMENINO"), ("Hombres", a.sexo == "MASCULINO")]),
        ("Tipo de ingreso", [("Primer ingreso", a.tipoing == "Primer ingreso"),
                             ("Traslado", a.tipoing == "Traslado")]),
        ("Tipo de colegio de procedencia", [
            ("Público", a.tipocol == "PUBLICO"), ("Privado", a.tipocol == "PRIVADO"),
            ("Subvencionado", a.tipocol == "SUBVENCIONADO"),
            ("Otro (educación abierta o del exterior)",
             ~a.tipocol.isin(["PUBLICO", "PRIVADO", "SUBVENCIONADO"]))]),
        ("Provincia de procedencia", [
            ("San José", a.prov == "SAN JOSÉ"),
            ("Alajuela, Cartago o Heredia", a.prov.isin(reg[1:])),
            ("Guanacaste, Puntarenas o Limón", ~a.prov.isin(reg))]),
        ("Condición de discapacidad", [("Sí", a.disc == "SI"), ("No", a.disc == "NO")]),
        ("Veces que ha reprobado cursos de la carrera", [
            ("Ninguna", a.reprob == 0), ("1 o 2", a.reprob.between(1, 2)),
            ("3 a 5", a.reprob.between(3, 5)), ("6 a 10", a.reprob.between(6, 10)),
            ("Más de 10", a.reprob > 10)]),
    ]
    rows = []
    for title, cats in grupos:
        rows.append(group_row(title, 5))
        for lab, m in cats:
            rows.append(f"{lab} & {int((m & mat).sum())} & {int((m & ~mat).sum())} & "
                        f"{int(m.sum())} & {pct(m.sum(), na)} \\\\ \\hline")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{int(mat.sum())}}} & "
                f"\\textbf{{{int((~mat).sum())}}} & \\textbf{{{na}}} & \\textbf{{100,0}} \\\\ \\hline")
    out["T12"] = rows
    return out


def resumen_permanencia(p, corte, e):
    c = p[p.consol == "SI"]
    print("corte de actividad:", corte, "| cohortes", c.cohorte.min(), "-", c.cohorte.max())
    print("admitidas:", len(p), "no consolidaron:", int((p.consol != "SI").sum()), "consolidaron:", len(c))
    ab = c.otra_ucr | c.fuera
    print("graduadas:", int(c.grad.sum()), "activas:", int(c.activa.sum()), "otra UCR:",
          int(c.otra_ucr.sum()), "fuera:", int(c.fuera.sum()), "abandono %", pct(ab.sum(), len(c)))
    s = c[c.cohorte <= 2019]
    print("cohortes <=2019: n", len(s), "grad %", pct(s.grad.sum(), len(s)), "aband %",
          pct((s.otra_ucr | s.fuera).sum(), len(s)))
    y = c[ab].anios_aband.clip(lower=0)
    print("abandono en año 0-1:", int((y <= 1).sum()), "de", int(ab.sum()), pct((y <= 1).sum(), ab.sum()))
    print("al día en 7º ciclo:", int((c.nivel7 == "7").sum()), "no matriculó:",
          int((c.nivel7 == "NO MATRICULÓ").sum()))
    a = e[e.estado.str.startswith("ACTIVO")]
    print("estado: total", len(e), "activas", len(a), "matriculadas", int((a.estado == "ACTIVO MATRICULADO").sum()),
          "ingreso<=2020", int((a.ing <= 2020).sum()), "mujeres activas", int((a.sexo == "FEMENINO").sum()))
    print("mediana reprobaciones activas", a.reprob.median(), "mediana aprobados", a.aprob.median())


def main(puntajes, duracion, perm_path, estado_path, outdir):
    p, d = admision(puntajes), graduados(duracion)
    g = p.groupby("anio").agg(cupo=("cupo", "sum"), disp=("cupo_disp", "sum"),
                              sol=("sol", "sum"), acep=("acep", "sum"))
    pi = p[p.modal == "Primer Ingreso"].set_index("anio")
    out = {}

    # El cupo disponible no se suma entre modalidades: los cupos no ocupados en una se
    # reasignan a otras, y el total contaría el mismo cupo varias veces.
    out["T1"] = [
        f"{y} & {int(r.cupo)} & {int(r.sol)} & {int(r.acep)} & "
        f"{pct(r.acep, r.sol)} & {pct(r.acep, r.cupo)} & {f2(pi.loc[y, 'corte'])} \\\\ \\hline"
        for y, r in g.sort_index(ascending=False).iterrows()
    ]

    rows = []
    last = int(p.anio.max())
    for y in range(last, last - 5, -1):
        sub = p[p.anio == y].set_index("modal")
        rows.append(group_row(y, 7))
        for key, lab in MODALIDADES:
            r = sub.loc[key]
            corte = "---" if r.corte == 0 else f2(r.corte)
            rows.append(f"{lab} & {corte} & {int(r.cupo)} & {int(r.cupo_disp)} & {int(r.sol)} & "
                        f"{int(r.acep)} & {pct(r.acep, r.sol)} \\\\ \\hline")
    out["T2"] = rows

    n = len(d)
    stats = lambda s: (f"{len(s)} & {(s.sexo == 'FEMENINO').sum()} & {(s.honor == 'SI').sum()} & "
                       f"{f1(s.dur.mean())} & {f1(s.dur.median())} & {f1(s.dur.min())} & "
                       f"{f1(s.dur.max())}")
    rows = [f"{y} & {stats(s)} \\\\ \\hline" for y, s in d.groupby("grad")]
    total = " & ".join(f"\\textbf{{{c.strip()}}}" for c in stats(d).split("&"))
    rows.append(f"\\textbf{{Total}} & {total} \\\\ \\hline")
    out["T3"] = rows

    bins = [(0, 4, "4,0 o menos (duración del plan)"), (4, 5, "4,5 a 5,0"),
            (5, 6, "5,5 a 6,0"), (6, 8, "6,5 a 8,0"), (8, 99, "Más de 8,0")]
    rows, acc = [], 0
    for lo, hi, lab in bins:
        k = int(((d.dur > lo) & (d.dur <= hi)).sum())
        acc += k
        rows.append(f"{lab} & {k} & {pct(k, n)} & {pct(acc, n)} \\\\ \\hline")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{n}}} & \\textbf{{100,0}} & \\\\ \\hline")
    out["T4"] = rows

    grupos = [
        ("Sexo", "sexo", [("FEMENINO", "Mujeres"), ("MASCULINO", "Hombres")]),
        ("Modalidad de ingreso", "modal", [
            ("Prueba de aptitud académica (Primer ingreso)", "Primer ingreso"),
            ("Prueba de aptitud académica (Traslado)", "Traslado por nota de admisión"),
            ("Excelencia académica", "Excelencia académica"),
            ("Rendimiento académico", "Rendimiento académico")]),
        ("Estudiante exclusivo de la carrera", "excl", [("SI", "Sí"), ("NO", "No")]),
        ("Graduación de honor", "honor", [("SI", "Sí"), ("NO", "No")]),
    ]
    rows = []
    for title, col, mapping in grupos:
        rows.append(group_row(title, 6))
        for key, lab in mapping:
            s = d[d[col] == key]
            rows.append(f"{lab} & {len(s)} & {pct(len(s), n)} & {f1(s.dur.mean())} & "
                        f"{f1(s.dur.median())} & {pct((s.dur <= 4).sum(), len(s))} \\\\ \\hline")
    out["T5"] = rows

    rows = []
    for y in range(int(d.ing_car.min()), int(d.ing_car.max()) + 1):
        s = d[d.ing_car == y]
        a = int(g.loc[y].acep)
        rows.append(f"{y} & {a} & {len(s)} & {pct(len(s), a)} & {(s.dur <= 4).sum()} & "
                    f"{f1(s.dur.mean()) if len(s) else '---'} \\\\ \\hline")
    out["T6"] = rows

    pm, corte = permanencia(perm_path)
    e = estado(estado_path)
    out.update(cuadros_permanencia(pm))
    out.update(cuadros_estado(e))

    outdir.mkdir(parents=True, exist_ok=True)
    for k, v in out.items():
        (outdir / f"{k}.tex").write_text("\n".join(v) + "\n", encoding="utf-8")

    print("graduados:", n, "| mujeres:", (d.sexo == "FEMENINO").sum(),
          "| honor:", (d.honor == "SI").sum(), "| en 4 años o menos:", (d.dur <= 4).sum())
    print("duración real media/mediana:", f1(d.dur.mean()), f1(d.dur.median()))
    for a, b in [(2014, 2018), (2022, 2026)]:
        s = d[d.grad.between(a, b)]
        print(f"graduados {a}-{b}: {len(s)}, duración media {f1(s.dur.mean())}")
    for a, b in [(2002, 2006), (2012, 2016), (2022, 2026)]:
        s = g.loc[a:b]
        print(f"admisión {a}-{b}: cupo original {f1(s.cupo.mean())}, solicitudes {f1(s.sol.mean())}, "
              f"aceptadas {f1(s.acep.mean())} (promedio anual)")
    c = d[d.ing_car.between(2012, 2018)]
    print("cohortes 2012-2018: aceptadas", int(g.loc[2012:2018].acep.sum()), "graduadas", len(c))
    resumen_permanencia(pm, corte, e)


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:5]),
         Path(sys.argv[5]) if len(sys.argv) > 5 else Path("poblacion-estudiantil-tablas"))

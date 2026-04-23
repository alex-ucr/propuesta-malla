#!/usr/bin/env python3
"""
Extract the \"Contenidos\" subsubsection from each *cuerpo*.tex in Cursos and
write a JSON object mapping course titles to HTML (for use with innerHTML).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

TITLE_RE = re.compile(
    r"\\(?:paragraph|subsection)\*\{([^}]+)\}",
    re.MULTILINE,
)
CONTENIDOS_RE = re.compile(
    r"\\subsubsection\*\{\s*Contenidos\s*\}\s*"
    r"(.*?)(?=\\subsubsection\*\{)",
    re.DOTALL,
)
_CMD_ENV = re.compile(r"\\(begin|end)\{(enumerate|itemize)\}", re.DOTALL)
_ITEM = re.compile(r"\\item\s*")


def _bslash_escaped(s: str, j: int) -> bool:
    n = 0
    k = j - 1
    while k >= 0 and s[k] == "\\":
        n += 1
        k -= 1
    return n % 2 == 1


def _read_brace_group(s: str, i: int) -> tuple[str, int] | None:
    if i >= len(s) or s[i] != "{":
        return None
    depth = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == "{" and not _bslash_escaped(s, j):
            depth += 1
        elif c == "}" and not _bslash_escaped(s, j):
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
    return None


def _strip_tex_comments(s: str) -> str:
    out: list[str] = []
    for line in s.splitlines(keepends=True):
        i = 0
        while i < len(line):
            if line[i] == "%" and not _bslash_escaped(line, i):
                line = line[:i]
                if not line.endswith("\n"):
                    line += "\n"
                break
            i += 1
        out.append(line)
    return "".join(out)


def _env_depth_before(s: str, pos: int) -> int:
    d = 0
    for m in _CMD_ENV.finditer(s[:pos]):
        d += 1 if m.group(1) == "begin" else -1
    return d


def _split_top_level_items(body: str) -> list[str]:
    top = [m for m in _ITEM.finditer(body) if _env_depth_before(body, m.start()) == 0]
    if not top:
        t = body.strip()
        return [t] if t else []
    out: list[str] = []
    for k, m in enumerate(top):
        a, b = m.end(), top[k + 1].start() if k + 1 < len(top) else len(body)
        t = body[a:b].strip()
        if t:
            out.append(t)
    return out


def _read_list_env(s: str, i: int) -> tuple[str, str, int] | None:
    m0 = re.match(r"\\begin\{(enumerate|itemize)\}", s[i:])
    if not m0:
        return None
    name = m0.group(1)
    a = i + m0.end()
    stack: list[str] = [name]
    pos, body_start = a, a
    while stack:
        mm = _CMD_ENV.search(s, pos)
        if not mm:
            return None
        g1, g2 = mm.group(1), mm.group(2)
        rel = mm.start()
        if g1 == "begin":
            stack.append(g2)
        else:
            if not stack or stack[-1] != g2:
                return None
            stack.pop()
        nxt = mm.end()
        if not stack:
            return name, s[body_start:rel], nxt
        pos = nxt
    return None


def _apply_tex_accents(s: str) -> str:
    comb = "\u0301"
    s = re.sub(
        r"\\'([aeiou])", lambda m: m.group(1) + comb, s, flags=re.IGNORECASE
    )
    s = re.sub(
        r"\\`([aeiou])", lambda m: m.group(1) + "\u0300", s, flags=re.IGNORECASE
    )
    s = re.sub(
        r"\\^([aeiou])", lambda m: m.group(1) + "\u0302", s, flags=re.IGNORECASE
    )
    s = re.sub(
        r'\\"([aeiou])', lambda m: m.group(1) + "\u0308", s, flags=re.IGNORECASE
    )
    s = re.sub(r"\\~n", "ñ", s, flags=re.IGNORECASE)
    s = re.sub(r"\\'\\i", "í", s)
    s = s.replace("---", "—")
    return s


_MATH_P: list[tuple[str, str]] = [
    (r"\\mathbb\{R\}", "ℝ"),
    (r"\\mathbb\{Z\}", "ℤ"),
    (r"\\mathbb\{N\}", "ℕ"),
    (r"\\mathbb\{Q\}", "ℚ"),
    (r"\\mathbb\{C\}", "ℂ"),
    (r"\\mathbb\{F\}_p", "𝔽ₚ"),
    (r"\\mathbb\{F\}_(\w+)", r"𝔽\1"),
    (r"\\R(?![a-zA-Z])", "ℝ"),
    (r"\\C(?![a-zA-Z])", "ℂ"),
    (r"\\Q(?![a-zA-Z])", "ℚ"),
    (r"\\Z(?![a-zA-Z])", "ℤ"),
    (r"\\N(?![a-zA-Z])", "ℕ"),
    (r"\\ell\b", "ℓ"),
    (r"\\infty\b", "∞"),
    (r"\\times\b", "×"),
    (r"\\pm\b", "±"),
    (r"\\cdot\b", "·"),
    (r"\\sigma\b", "σ"),
    (r"\\pi\b", "π"),
    (r"\\varphi\b", "φ"),
    (r"\\varepsilon\b", "ε"),
    (r"\\delta\b", "δ"),
    (r"\\sen\b", "sen"),
    (r"\\S\b", "§"),
    (r"\\cdots\b", "⋯"),
    (r"\\ldots\b", "…"),
    (r"\\bmod\b", " mod "),
    (r"\\text\{([^}]+)\}", r"\1"),
    (r"\\operatorname\*?\{([^}]+)\}", r"\1"),
    (r"\\pmod\{([^}]+)\}", r" (mod \1)"),
]
_SUP = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _math_to_plain(s: str) -> str:
    t = s.strip()
    for a, b in _MATH_P:
        t = re.sub(a, b, t, flags=re.IGNORECASE)
    t = t.replace("\\\\", " ")
    t = re.sub(
        r"\^\{([^{}]*)\}", lambda m: m.group(1).translate(_SUP) if m.group(1) else "⁺", t
    )
    t = re.sub(
        r"\_\{([^{}]*)\}", lambda m: m.group(1).translate(_SUB) if m.group(1) else "₊", t
    )
    t = re.sub(
        r"\^([0-9+\-=()n])", lambda m: m.group(1).translate(_SUP) if m.group(1) else "", t
    )
    t = re.sub(r"\_([0-9])", lambda m: m.group(1).translate(_SUB) if m.group(1) else "", t)
    t = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", t)
    t = re.sub(r"\\left\(", "(", t)
    t = re.sub(r"\\right\)", ")", t)
    t = re.sub(r"\\left\|", "|", t)
    t = re.sub(r"\\right\|", "|", t)
    t = t.replace(r"\{", "{").replace(r"\}", "}")
    return t


def _inline_latex_to_html(s: str) -> str:
    if not s:
        return ""
    out: list[str] = []
    last = 0
    for m in re.finditer(
        r"(?<!\\)\$((?:\\.|[^$\\])*?)(?<!\\)\$", s, flags=re.DOTALL
    ):
        out.append(_plain_latex_to_html(s[last : m.start()]))
        out.append(
            f'<span class="math" lang="la">{escape(_math_to_plain(m.group(1)))}</span>'
        )
        last = m.end()
    out.append(_plain_latex_to_html(s[last:]))
    return "".join(out)


def _plain_latex_to_html(s: str) -> str:
    s = _apply_tex_accents(s)
    out: list[str] = []
    i, n = 0, len(s)
    while i < n:
        b = s.find(r"\textbf{", i)
        t0 = s.find(r"\texttt{", i)
        u0 = s.find(r"\url{", i)
        c0 = s.find(r"\cite", i)
        opts: list[tuple[int, str]] = []
        for pos, k in (b, "b"), (c0, "c"), (t0, "t"), (u0, "u"):
            if pos >= 0:
                opts.append((pos, k))
        if not opts:
            out.append(escape(s[i:]))
            break
        pos, kind = min(opts, key=lambda t: t[0])
        if pos > i:
            out.append(escape(s[i:pos]))
        if kind == "c":
            m = re.match(
                r"\\cite(?:(?:\s*\[[^\]]+\])+)?\s*\{([^}]+)\}",
                s[pos:],
            ) or re.match(
                r"\\cite\s*\{([^}]+)\}", s[pos:]
            )
            if m:
                key = m.group(1).strip()
                out.append(
                    f'<span class="cite" title="cita">[{escape(key)}]</span>'
                )
                i = pos + m.end()
            else:
                out.append(escape(s[pos]))
                i = pos + 1
            continue
        lp = s.find("{", pos)
        g = _read_brace_group(s, lp) if lp >= 0 else None
        if g is None:
            out.append(escape(s[pos]))
            i = pos + 1
            continue
        body, nxt = g
        if kind == "b":
            out.append(f"<strong>{_inline_latex_to_html(body)}</strong>")
        elif kind == "t":
            out.append(f"<code>{escape(body)}</code>")
        else:
            u = body
            out.append(
                f'<a href="{escape(u, quote=True)}" rel="nofollow noopener">{escape(u)}</a>'
            )
        i = nxt
    return "".join(out)


def _list_to_html(kind: str, body: str) -> str:
    tag = "ol" if kind == "enumerate" else "ul"
    items = _split_top_level_items(body)
    if not items:
        return f"<{tag}></{tag}>"
    parts = []
    for it in items:
        s = re.sub(
            r"%\s*[^\n]*$", "", it, flags=re.M
        ).strip()  # trailing % comments on same line
        s = s.replace("%Fin del enumerate de Contenidos", "").strip()
        parts.append(f"<li>{_parse_latex_mixed(s)}</li>")
    return f"<{tag}>" + "\n".join(parts) + f"</{tag}>"


def _parse_latex_mixed(s: str) -> str:
    s = s.strip()
    if s.startswith("%") and s.split("\n", 1)[0].strip().startswith("%"):
        # Drop one leading % block (e.g. MA-0615 long comment)
        s = s.split("\n", 1)[-1] if "\n" in s else ""
        s = s.strip()
    out: list[str] = []
    p = 0
    n = len(s)
    while p < n:
        m = re.search(r"\\begin\{(enumerate|itemize)\}", s[p:])
        if not m:
            out.append(_inline_latex_to_html(s[p:]))
            break
        mstart = p + m.start()
        if mstart > p:
            out.append(_inline_latex_to_html(s[p:mstart]))
        ev = _read_list_env(s, mstart)
        if ev is None:
            out.append(escape(s[mstart]))
            p = mstart + 1
            continue
        ekind, ebody, npos = ev
        out.append(_list_to_html(ekind, ebody))
        p = npos
    return "".join(out)


def latex_contenidos_to_html(tex: str) -> str:
    s = _strip_tex_comments(tex).strip()
    s = re.sub(r"^%[^\n]*\n", "", s)
    s = s.replace(r"\%Fin del enumerate de Contenidos", "")
    s = s.replace("%Fin del enumerate de Contenidos", "")
    s = s.strip()
    return f'<div class="contenidos-bloque">{_parse_latex_mixed(s)}</div>'


# --- Extraction (unchanged) ---


def extract_course_title(src: str) -> str | None:
    m = TITLE_RE.search(src)
    if not m:
        return None
    return m.group(1).strip()


def extract_contenidos_block(src: str) -> str | None:
    m = CONTENIDOS_RE.search(src)
    if not m:
        return None
    return m.group(1).strip()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--cursos",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Cursos",
        help="Folder containing *cuerpo*.tex (default: ../Cursos next to this repo root)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "contenidos_por_curso.json",
        help="Output JSON path (values are HTML strings)",
    )
    args = p.parse_args()
    cursos: Path = args.cursos
    if not cursos.is_dir():
        print(f"Not a directory: {cursos}", file=sys.stderr)
        return 1

    files = sorted(
        cursos.glob("*.tex"),
        key=lambda x: x.name,
    )
    cuerpos = [f for f in files if "cuerpo" in f.name.lower()]

    result: dict[str, str] = {}
    skipped: list[tuple[str, str]] = []

    for path in cuerpos:
        text = path.read_text(encoding="utf-8")
        title = extract_course_title(text)
        if not title:
            skipped.append((path.name, "no course title (\\paragraph* or \\subsection*)"))
            continue
        block = extract_contenidos_block(text)
        if block is None:
            skipped.append((path.name, "no \\subsubsection*{Contenidos} block"))
            continue
        if title in result:
            key = f"{title} [{path.stem}]"
        else:
            key = title
        result[key] = latex_contenidos_to_html(block)

    for name, reason in sorted(skipped, key=lambda x: x[0].lower()):
        print(f"Warning: {name}: {reason}", file=sys.stderr)

    out = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(result)} courses to {out}", file=sys.stderr)
    if skipped:
        return 0 if result else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

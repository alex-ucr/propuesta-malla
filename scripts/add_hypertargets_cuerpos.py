#!/usr/bin/env python3
"""Insert \\hypertarget{SIGLA}{} after addcontentsline in *cuerpo*.tex (MA0151 style)."""
from __future__ import annotations

import re
from pathlib import Path

CUROS = Path(__file__).resolve().parent.parent / "Cursos"
TITLE_PATS = (
    r"\\paragraph\*\{([^}]+)\}",
    r"\\subsection\*\{([^}]+)\}",
    r"\\subsubsection\*\{([^}]+)\}",
)
ADDCONTENT = re.compile(
    r"(\\addcontentsline\{toc\}\{subsection\}\{[^}]+\}\s*\n)",
    re.MULTILINE,
)


def anchor_from_title(title: str) -> str | None:
    m = re.search(r"\b(MA|CA)-(\d{4})\b", title, re.IGNORECASE)
    if m:
        return m.group(1).upper() + m.group(2)
    m = re.search(r"\b(MA|CA)-0xxx\b", title, re.IGNORECASE)
    if m:
        return m.group(1).upper() + "0xxx"
    return None


def first_title(text: str) -> str | None:
    for pat in TITLE_PATS:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    return None


def main() -> int:
    seen: set[Path] = set()
    updated = 0
    for fp in sorted(CUROS.glob("*cuerpo*.tex")):
        rp = fp.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        text = fp.read_text(encoding="utf-8")
        if re.search(r"\\hypertarget\{", text):
            continue
        title = first_title(text)
        if not title:
            print(f"skip (no title): {fp.name}")
            continue
        anchor = anchor_from_title(title)
        if not anchor:
            print(f"skip (no anchor): {fp.name} -> {title!r}")
            continue
        line = f"\\hypertarget{{{anchor}}}{{}}\n"
        if ADDCONTENT.search(text):

            def _after_add(m: re.Match[str]) -> str:
                return m.group(1) + line

            new_text, n = ADDCONTENT.subn(_after_add, text, count=1)
        else:
            # Insert after first title command line
            inserted = False
            new_text = text
            for pat in TITLE_PATS:
                m = re.search(pat, new_text)
                if not m:
                    continue
                end = m.end()
                # include trailing newline after closing brace
                if end < len(new_text) and new_text[end] == "\n":
                    end += 1
                new_text = (
                    new_text[:end]
                    + line
                    + f"\\addcontentsline{{toc}}{{subsection}}{{{title}}}\n"
                    + new_text[end:]
                )
                inserted = True
                break
            if not inserted:
                print(f"skip (no insert point): {fp.name}")
                continue
            n = 1
        if n:
            fp.write_text(new_text, encoding="utf-8")
            updated += 1
            print(f"{fp.name} -> {anchor}")
    print(f"Updated {updated} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

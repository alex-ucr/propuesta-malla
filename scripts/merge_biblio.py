#!/usr/bin/env python3
"""Merge entries from Documentos/Biblio.bib into propuesta-malla/Biblio.bib."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "Biblio.bib"
EXTRA = Path(
    r"C:\Users\josea\OneDrive - Universidad de Costa Rica\Revisión curricular\Documentos\Biblio.bib"
)


def _split_entries(text: str) -> list[tuple[str, str]]:
    """Return list of (key, full_entry_text)."""
    parts = re.split(r"(?=@[a-zA-Z]+\s*\{)", text.lstrip())
    out: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part.startswith("@"):
            continue
        m = re.match(r"@[a-zA-Z]+\s*\{\s*([^,\s]+)\s*,", part)
        if not m:
            continue
        out.append((m.group(1), part))
    return out


def main() -> None:
    main_text = MAIN.read_text(encoding="utf-8")
    extra_text = EXTRA.read_text(encoding="utf-8")
    main_keys = {k for k, _ in _split_entries(main_text)}
    to_add: list[str] = []
    for key, entry in _split_entries(extra_text):
        if key in main_keys:
            continue
        to_add.append(entry)
        main_keys.add(key)
    if not to_add:
        print("No new bib entries to merge.")
        return
    merged = main_text.rstrip() + "\n\n% --- merged from Documentos/Biblio.bib ---\n\n"
    merged += "\n\n".join(to_add) + "\n"
    MAIN.write_text(merged, encoding="utf-8")
    print(f"Added {len(to_add)} entries to {MAIN.name}")


if __name__ == "__main__":
    main()

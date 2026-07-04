"""Extract plain text from CA*.pdf next to propuesta-malla (../Cursos/)."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Install pypdf: pip install pypdf", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
# PDFs junto a los .tex en propuesta-malla/Cursos/
PDF_DIR = ROOT / "Cursos"


def main() -> None:
    specs = [
        ("MA0404", ("MA0404.pdf",)),
        ("MA0503", ("MA0503.pdf",)),
        ("MA0421", ("MA0421.pdf", "ma0421.pdf")),
        ("MA0711", ("MA0711.pdf",)),
    ]
    for stem, names in specs:
        pdf = next((PDF_DIR / n for n in names if (PDF_DIR / n).is_file()), None)
        out = ROOT / "scripts" / f"_extract_{stem}.txt"
        if pdf is None:
            print(f"Missing PDF for {stem} in {PDF_DIR}", file=sys.stderr)
            continue
        reader = PdfReader(str(pdf))
        parts: list[str] = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            parts.append(f"\n\n===== PAGE {i + 1} =====\n\n")
            parts.append(t)
        text = "".join(parts)
        out.write_text(text, encoding="utf-8")
        print(f"Wrote {out} from {pdf.name} ({len(text)} chars)")


if __name__ == "__main__":
    main()

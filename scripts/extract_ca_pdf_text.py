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
        ("CA0204", ("CA0204.pdf",)),
        ("CA0303", ("CA0303.pdf",)),
        ("CA0721", ("CA0721.pdf", "ca0721.pdf")),
        ("CA0411", ("CA0411.pdf",)),
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

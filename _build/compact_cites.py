#!/usr/bin/env python3
"""Reduce la densidad de citas: dentro de un párrafo, deja la última aparición
de cada cita idéntica. No toca listas, tablas, títulos ni bloques de código.

Uso: python3 compact_cites.py archivo.md [archivo2.md ...]
"""
import re
import sys
from pathlib import Path

CITE = re.compile(r"\s*\[((?:Purves|Zeise|Kelly|Altman|Gross|apuntes|Kandel)[^\[\]\n]{0,90})\]")


def compact_paragraph(text: str) -> str:
    hits = list(CITE.finditer(text))
    if len(hits) < 2:
        return text
    seen = {}
    for m in hits:
        seen.setdefault(m.group(1), []).append(m)
    drop = []
    for matches in seen.values():
        drop.extend(matches[:-1])
    if not drop:
        return text
    out = text
    for m in sorted(drop, key=lambda x: x.start(), reverse=True):
        out = out[: m.start()] + out[m.end():]
    return out


def process(md: str) -> tuple[str, int, int]:
    blocks = re.split(r"(\n\s*\n)", md)
    before = len(CITE.findall(md))
    for i in range(0, len(blocks), 2):
        block = blocks[i]
        stripped = block.lstrip()
        if not stripped or stripped[0] in "|#-*>```":
            continue
        blocks[i] = compact_paragraph(block)
    out = "".join(blocks)
    return out, before, len(CITE.findall(out))


def main() -> int:
    for name in sys.argv[1:]:
        path = Path(name)
        md = path.read_text(encoding="utf-8")
        out, before, after = process(md)
        path.write_text(out, encoding="utf-8")
        print(f"{path.name}: {before} -> {after} citas")
    return 0


if __name__ == "__main__":
    sys.exit(main())

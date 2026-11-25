#!/usr/bin/env python3
"""QA del sitio: HTML, anclas, enlaces, citas, em dash y paridad con el Markdown."""
import json
import re
import sys
from pathlib import Path

from lxml import html

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build"
PAGES = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))["pages"]
EMDASH = "\u2014"
errors = []
warnings = []


def load_figures(page_id: str) -> list:
    path = BUILD / "figures" / f"{page_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("figures", [])
    return []


CREDITS = ROOT / "creditos.html"
CREDITS_IDS = set()
if CREDITS.exists():
    _cdoc = html.fromstring(CREDITS.read_text(encoding="utf-8"))
    CREDITS_IDS = {e.get("id") for e in _cdoc.xpath("//*[@id]")}


def check_page(page: dict) -> None:
    path = ROOT / page["file"]
    if not path.exists():
        errors.append(f"{page['file']}: no existe")
        return
    raw = path.read_text(encoding="utf-8")
    doc = html.fromstring(raw)

    ids = [e.get("id") for e in doc.xpath("//*[@id]")]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errors.append(f"{page['file']}: ids duplicados {sorted(dup)}")

    toc = [a.get("href")[1:] for a in doc.xpath('//ul[contains(@class,"toc")]//a[starts-with(@href,"#")]')]
    missing = [t for t in toc if t not in ids]
    if missing:
        errors.append(f"{page['file']}: anclas del TOC sin destino {missing}")
    if not toc:
        errors.append(f"{page['file']}: TOC vacío")

    for href in doc.xpath("//a/@href"):
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (path.parent / href.split("#")[0]).resolve()
        if not target.exists():
            errors.append(f"{page['file']}: enlace roto {href}")

    figs_expected = load_figures(page["id"])
    fig_nodes = doc.xpath('//figure[contains(@class,"fig")]')
    if len(fig_nodes) != len(figs_expected):
        errors.append(f"{page['file']}: figuras HTML {len(fig_nodes)} vs JSON {len(figs_expected)}")
    seen = set()
    for node in fig_nodes:
        fid = node.get("id") or ""
        if not fid:
            errors.append(f"{page['file']}: figura sin id")
        elif fid in seen:
            errors.append(f"{page['file']}: figura repetida {fid}")
        seen.add(fid)
        if not node.xpath("./figcaption"):
            errors.append(f"{page['file']}: figura {fid} sin leyenda")
        if not node.xpath("./figcaption//span[contains(@class,'fig-source')]"):
            errors.append(f"{page['file']}: figura {fid} sin fuente")
        imgs = node.xpath("./a[contains(@class,'fig-open')]/img")
        if not imgs:
            errors.append(f"{page['file']}: figura {fid} sin imagen")
        elif not (imgs[0].get("alt") or "").strip():
            errors.append(f"{page['file']}: figura {fid} sin alt")
        for a in node.xpath("./figcaption//a[contains(@href,'creditos.html#')]"):
            frag = a.get("href").split("#", 1)[1]
            if frag not in CREDITS_IDS:
                errors.append(f"{page['file']}: crédito sin ancla {frag}")

    for img in doc.xpath("//img"):
        src = img.get("src") or ""
        if not src or src.startswith("data:"):
            continue
        if not (path.parent / src).resolve().exists():
            errors.append(f"{page['file']}: imagen rota {src}")

    if not doc.xpath('//footer//a[contains(@href,"creditos.html")]'):
        errors.append(f"{page['file']}: footer sin enlace a créditos")
    if EMDASH in raw:
        errors.append(f"{page['file']}: contiene em dash")
    if "%%" in raw:
        errors.append(f"{page['file']}: placeholder sin reemplazar")
    if not doc.xpath('//section[@id="alcance"]'):
        errors.append(f"{page['file']}: falta el bloque de alcance")

    md = (ROOT / page["source"]).resolve().read_text(encoding="utf-8")
    md_h2 = len(re.findall(r"^## ", md, re.M))
    html_h2 = len(doc.xpath("//main//h2"))
    if page["kind"] != "manual":
        for required in ("Lo esencial en 60 segundos", "Puntos de examen", "Límites del material"):
            if required.lower() not in md.lower():
                errors.append(f"{page['file']}: falta la sección {required}")

    expected_cites = len(re.findall(r"\[(?:Purves|Zeise|Kelly|Altman|Gross|apuntes|Kandel)", md))
    cites = len(doc.xpath('//span[contains(@class,"cite")]'))
    if page["kind"] != "manual":
        if expected_cites < 30:
            errors.append(f"{page['file']}: solo {expected_cites} citas en el Markdown")
        if abs(cites - expected_cites) > 3:
            warnings.append(f"{page['file']}: citas HTML {cites} vs MD {expected_cites}")

    words = len(re.findall(r"\w+", md))
    target = page.get("target") or 0
    if target and not (0.82 * target <= words <= 1.18 * target):
        warnings.append(f"{page['file']}: {words} palabras vs objetivo {target}")

    print(
        f"{page['id']:<10} h2={html_h2:<3} md_h2={md_h2:<3} palabras={words:<5} "
        f"citas={cites:<4} tablas={len(doc.xpath('//table')):<3} img={len(doc.xpath('//img'))}"
    )


def check_indexes() -> None:
    for rel in ["index.html", "manual.html", "creditos.html"]:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: no existe")
            continue
        raw = path.read_text(encoding="utf-8")
        doc = html.fromstring(raw)
        if EMDASH in raw:
            errors.append(f"{rel}: contiene em dash")
        for href in doc.xpath("//a/@href"):
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (path.parent / href.split("#")[0]).resolve().exists():
                errors.append(f"{rel}: enlace roto {href}")
        if not doc.xpath("//h1"):
            errors.append(f"{rel}: sin h1")
        print(f"{rel:<16} enlaces={len(doc.xpath('//a'))}")

    idx = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
    linked = {a.get("href") for a in idx.xpath('//div[contains(@class,"guide-grid")]//a')}
    for page in PAGES:
        if Path(page["file"]).name not in linked:
            errors.append(f"index.html: no enlaza {page['file']}")


def main() -> int:
    for page in PAGES:
        check_page(page)
    check_indexes()
    expected = sum(len(load_figures(p["id"])) for p in PAGES)
    if CREDITS.exists():
        rows = html.fromstring(CREDITS.read_text(encoding="utf-8")).xpath("//tr[@id]")
        if len(rows) != expected:
            errors.append(f"creditos.html: filas {len(rows)} vs figuras {expected}")
    print()
    for w in warnings:
        print("AVISO:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"\n{len(errors)} errores")
        return 1
    print(f"OK: {len(PAGES) + 2} páginas sin errores")
    return 0


if __name__ == "__main__":
    sys.exit(main())

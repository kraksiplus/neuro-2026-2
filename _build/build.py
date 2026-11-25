#!/usr/bin/env python3
"""Genera el sitio de Neurociencias (Certamen 1) desde los capítulos en Markdown.

Uso:
    python build.py                # todas las páginas, índice y créditos
    python build.py --page c1-04   # una página
    python build.py --indexes      # índice y créditos
"""
import argparse
import html
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build"
SITE = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
PAGES = SITE["pages"]
CSS = (BUILD / "theme.css").read_text(encoding="utf-8")
JS = (BUILD / "theme.js").read_text(encoding="utf-8")
TPL = (BUILD / "template.html").read_text(encoding="utf-8")

EMDASH = "\u2014"
SOURCES = ("Purves", "Zeise", "Kelly", "Altman", "Gross", "apuntes", "Kandel")
CITE_RE = re.compile(r"\[((?:" + "|".join(SOURCES) + r")(?:[^\[\]\n]{1,90}))\]")


def clean(text: str) -> str:
    """Sin em dash: celdas vacías pasan a "No aplica" y el resto a coma."""
    text = re.sub(r"(?<=\|)\s*(?:\*\*)?[\u2014\u2013](?:\*\*)?\s*(?=\|)", " No aplica ", text)
    text = text.replace(EMDASH, ", ")
    text = re.sub(r",\s*,+", ",", text)
    text = re.sub(r"\(\s*,\s*", "(", text)
    text = re.sub(r",\s*\)", ")", text)
    text = re.sub(r",\s*([.;:!?])", r"\1", text)
    return text


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:64] or "seccion"


def pandoc(md: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none"],
        input=md, capture_output=True, text=True, check=True,
    )
    return proc.stdout


def citations(md: str) -> str:
    return CITE_RE.sub(lambda m: f'<span class="cite">{m.group(1)}</span>', md)


def inline(md: str) -> str:
    out = pandoc(citations(clean(md))).strip()
    return re.sub(r"^<p>|</p>$", "", out)


def text_of(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def load_figures(page_id: str) -> dict:
    path = BUILD / "figures" / f"{page_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"figures": []}


def figure_anchor(number: str) -> str:
    return "fig-" + number.replace(".", "-")


def find_anchor_html(fragment: str, anchor: str) -> int | None:
    """Posición en el HTML de un texto que puede estar partido por etiquetas."""
    chars, positions, i = [], [], 0
    while i < len(fragment):
        if fragment[i] == "<":
            j = fragment.find(">", i)
            if j == -1:
                break
            i = j + 1
            continue
        chars.append(fragment[i])
        positions.append(i)
        i += 1
    start = "".join(chars).find(anchor)
    return positions[start] if start != -1 else None


def figure_html(fig: dict) -> str:
    num = fig["number"]
    fid = figure_anchor(num)
    img = "assets/fig/" + fig["image"]
    caption_html = inline(fig["caption"])
    source = fig.get("source", "")
    alt = html.escape(f"Figura {num}. {text_of(caption_html)}", quote=True)
    data_caption = html.escape(f"Figura {num}. {text_of(caption_html)}", quote=True)
    return f"""<figure class="fig" id="{fid}">
  <a class="fig-open" href="{img}" data-caption="{data_caption}" data-alt="{alt}">
    <img src="{img}" width="{fig.get('width', 1000)}" height="{fig.get('height', 700)}" loading="lazy" decoding="async" alt="{alt}">
  </a>
  <figcaption>
    <strong>Figura {num}.</strong> {caption_html}
    <span class="fig-source">{source} <a href="creditos.html#{fid}">Ver créditos</a></span>
  </figcaption>
</figure>"""


def insert_figure(section: str, fig: dict) -> tuple[str, bool]:
    block = figure_html(fig)
    anchor = (fig.get("after_text") or "").strip()
    if not anchor:
        return section.replace("</section>", block + "\n</section>"), True
    start = find_anchor_html(section, anchor)
    if start is None:
        return section.replace("</section>", block + "\n</section>"), False

    li_open = section.rfind("<li", 0, start)
    p_close = section.find("</p>", start)
    if li_open != -1 and section.find("</li>", li_open, start) == -1:
        closes = [c for c in (section.find("</ul>", start), section.find("</ol>", start)) if c != -1]
        if closes:
            pos = min(closes) + 5
        elif p_close != -1:
            pos = p_close + len("</p>")
        else:
            pos = len(section)
    elif p_close != -1:
        pos = p_close + len("</p>")
    else:
        pos = section.find("</section>", start)
        if pos == -1:
            pos = len(section)
    return section[:pos] + "\n" + block + section[pos:], True


def atlas_html(figures: list) -> str:
    if not figures:
        return ""
    items = []
    for fig in figures:
        fid = figure_anchor(fig["number"])
        img = "assets/fig/" + fig["image"]
        items.append(
            f'<a class="fig-thumb" href="#{fid}" aria-label="Figura {fig["number"]}">'
            f'<img src="{img}" loading="lazy" decoding="async" alt="Figura {fig["number"]}">'
            f'<span>Figura {fig["number"]}</span></a>'
        )
    return (
        '<section id="atlas" class="card">\n'
        '<div class="section-kicker"><span class="n">★</span> Atlas</div>\n'
        "<h2>Figuras de la guía</h2>\n"
        '<p class="small">Toca una miniatura para volver a la figura en su sección.</p>\n'
        f'<div class="fig-grid">{"".join(items)}</div>\n'
        "</section>"
    )


def table_wrap(fragment: str, label: str) -> str:
    def repl(match):
        return (
            f'<div class="table-wrap" role="region" aria-label="Tabla: {html.escape(label)}" '
            f'tabindex="0">{match.group(0)}</div>'
        )
    return re.sub(r"<table>.*?</table>", repl, fragment, flags=re.S)


def section_title(fragment: str) -> str:
    m = re.search(r"<h2[^>]*>(.*?)</h2>", fragment, re.S)
    return text_of(m.group(1)) if m else ""


def process_section(fragment: str, idx: int) -> tuple[str, str]:
    title = section_title(fragment)
    sid = f"sec-{idx:02d}-{slug(title)}"
    fragment = re.sub(r"<h2[^>]*>", "<h2>", fragment, count=1)
    fragment = table_wrap(fragment, title)
    fragment = re.sub(r"<th([^>]*)>\s*</th>", r"<th\1>Característica</th>", fragment)
    fragment = re.sub(r"<p>(Fuente:)", r'<p class="small table-source">\1', fragment)

    low = title.lower()
    if low.startswith("puntos de examen"):
        fragment = fragment.replace("<ul>", '<ul class="exam-list">', 1)
    if low.startswith("límites"):
        m = re.search(r"</h2>\s*(.*?)\s*$", fragment, re.S)
        inner = m.group(1) if m else ""
        fragment = re.sub(
            r"</h2>\s*.*$",
            '</h2>\n<div class="warnbox"><span class="box-title">Límites del material</span>'
            + inner + "</div>",
            fragment, flags=re.S,
        )
    kicker = f'<div class="section-kicker"><span class="n">{idx:02d}</span> Tema</div>'
    return f'<section id="{sid}" class="card">\n{kicker}\n{fragment}\n</section>', title


def alcance_html(page: dict) -> str:
    if page["kind"] == "manual":
        box = page["alcance"]
        note = (
            "El manual se apoya en las ocho guías y en el material de clases; usa rangos de "
            "páginas y bloques en vez de una cita por oración."
        )
    else:
        box = page["alcance"]
        note = (
            "Las citas remiten a la fuente y a su página o sección, por ejemplo "
            "<em>Zeise p. 108</em>, <em>Purves p. 78</em> o <em>apuntes, bloque III</em>."
        )
    excluye = page.get("excluye", "")
    extra = f'<p class="small"><strong>Fuera de alcance:</strong> {excluye}</p>' if excluye else ""
    return (
        '<section id="alcance" class="card">'
        '<div class="section-kicker"><span class="n">00</span> Alcance y método</div>'
        "<h2>Qué cubre esta guía</h2>"
        f'<div class="keybox"><span class="box-title">Alcance</span>{box}</div>'
        f'<p class="small">{note}</p>{extra}'
        "</section>"
    )


def essentials_html(fragment: str) -> str:
    body = re.sub(r"<h2[^>]*>.*?</h2>", "", fragment, count=1, flags=re.S).strip()
    body = re.sub(r"^<ul>", '<ul>', body)
    return (
        '<section id="esencial" class="card">'
        '<div class="section-kicker"><span class="n">★</span> Repaso rápido</div>'
        "<h2>Lo esencial en 60 segundos</h2>"
        f'<div class="keybox"><span class="box-title">Si solo te llevas estas ideas</span>{body}</div>'
        "</section>"
    )


def build_body(page: dict) -> tuple[str, dict]:
    src = (ROOT / page["source"]).resolve()
    md = clean(src.read_text(encoding="utf-8"))
    words = len(re.findall(r"\w+", md))
    body = pandoc(citations(md))
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)

    parts = re.split(r"(?=<h2\b)", body)
    head = parts[0].strip()
    raw = [p for p in parts[1:] if p.strip()]

    essential_frag = ""
    sections, titles = [], []
    for frag in raw:
        title = section_title(frag)
        if title.lower().startswith("lo esencial"):
            essential_frag = essentials_html(frag)
            continue
        idx = len(sections) + 1
        wrapped, title = process_section(frag, idx)
        sections.append(wrapped)
        titles.append(title)

    fig_data = load_figures(page["id"])
    figures = fig_data.get("figures", [])

    def section_rank(title: str, wanted: str) -> tuple[int, int]:
        tl, wl = title.lower(), wanted.lower()
        if tl == wl:
            return (0, len(tl))
        if tl.startswith(wl):
            return (1, len(tl))
        if wl in tl:
            return (2, len(tl))
        return (9, len(tl))

    inserted = []
    for fig in figures:
        wanted = fig.get("section", "")
        ranked = [(section_rank(t, wanted), i) for i, t in enumerate(titles)]
        ranked.sort()
        target = ranked[0][1] if ranked and ranked[0][0][0] < 9 else None
        if target is None:
            print(f"AVISO {page['id']}: figura {fig['number']} sin sección")
            continue
        sections[target], ok = insert_figure(sections[target], fig)
        if not ok:
            print(f"AVISO {page['id']}: figura {fig['number']} sin ancla, al final de la sección")
        inserted.append(fig)

    joined = "".join(sections)
    body_html = alcance_html(page) + essential_frag + joined + atlas_html(inserted)
    stats = {
        "words": words,
        "cites": len(re.findall(r'<span class="cite">', body_html)),
        "tables": len(re.findall(r"<table>", body_html)),
        "rows": len(re.findall(r"<tr", body_html)),
        "sections": len(sections),
        "titles": titles,
        "figures": inserted,
        "essentials": bool(essential_frag),
    }
    return head + body_html, stats


def hero_html(page: dict, stats: dict) -> str:
    figs = len(stats["figures"])
    if page["kind"] == "manual":
        h1 = page["title"]
        lede = page.get("lede", "")
        meta = [
            ("Guías", "8"), ("Temas", str(stats["sections"])),
            ("Filas de tabla", str(stats["rows"])), ("Citas", str(stats["cites"])),
            ("Fuentes", page["fuentes"]),
        ]
    else:
        h1 = f"{page['num']:02d}. {page['title']}"
        lede = (
            f"Guía {page['num']:02d} de {page['of']:02d}. "
            f"{stats['words']:,} palabras, {stats['cites']} citas y {stats['rows']} filas de tabla."
        ).replace(",", ".")
        if figs:
            lede += f" {figs} figuras seleccionadas."
        meta = [
            ("Guía", f"{page['num']:02d} de {page['of']:02d}"),
            ("Fuentes", page["fuentes"]),
            ("Citas", str(stats["cites"])),
            ("Tablas", str(stats["rows"])),
            ("Palabras", f"{stats['words']:,}".replace(",", ".")),
        ]
        if figs:
            meta.insert(3, ("Figuras", str(figs)))
    meta_html = "".join(
        f"<div><span>{html.escape(k)}</span><strong>{html.escape(v)}</strong></div>" for k, v in meta
    )
    return f"""<header class="hero">
  <div class="hero-inner">
    <p class="eyebrow">{html.escape(SITE['eyebrow'])}</p>
    <h1>{html.escape(h1)}</h1>
    <p class="lede">{html.escape(lede)}</p>
    <div class="meta-grid">{meta_html}</div>
    <div class="hero-actions">
      <button class="btn primary" id="printBtn" type="button">Imprimir / guardar PDF</button>
      <button class="btn" id="themeBtn" type="button" aria-pressed="false">Modo oscuro</button>
      <a class="btn" href="#alcance">Empezar por el alcance</a>
    </div>
  </div>
</header>"""


def toc_html(stats: dict) -> str:
    items = ['<li><a href="#alcance">Alcance y método</a></li>']
    if stats.get("essentials"):
        items.insert(0, '<li><a href="#esencial">Lo esencial en 60 segundos</a></li>')
    for i, title in enumerate(stats["titles"]):
        sid = f"sec-{i + 1:02d}-{slug(title)}"
        items.append(f'<li><a href="#{sid}">{html.escape(title)}</a></li>')
    if stats.get("figures"):
        items.append('<li><a href="#atlas">Figuras de la guía</a></li>')
    return "\n".join("        " + x for x in items)


def nav_html(page: dict) -> str:
    chapters = sorted([p for p in PAGES if p["kind"] == "chapter"], key=lambda p: p["num"])
    links = ['<a href="index.html" title="Índice del certamen">Índice</a>']
    for other in chapters:
        if other["id"] == page["id"] or abs(other["num"] - page["num"]) != 1:
            continue
        links.append(
            f'<a href="{Path(other["file"]).name}" title="{html.escape(other["title"])}">'
            f'{other["num"]:02d}</a>'
        )
    if page["kind"] == "chapter":
        links.append('<a href="manual.html" title="Manual del Certamen 1">Manual</a>')
    return "\n        ".join(links)


def build_page(page: dict) -> Path:
    body, stats = build_body(page)
    title = f"{page['title']} · Neurociencias UBB"
    desc = f"{page['title']}. Guía de estudio del Certamen 1 de Neurociencias, con citas por fuente."
    out = TPL
    for key, val in {
        "%%TITLE%%": html.escape(title),
        "%%DESC%%": html.escape(desc),
        "%%CSS%%": CSS,
        "%%HERO%%": hero_html(page, stats),
        "%%TOC%%": toc_html(stats),
        "%%NAV%%": nav_html(page),
        "%%BODY%%": body,
        "%%JS%%": JS,
        "%%CREDITS%%": "creditos.html",
    }.items():
        out = out.replace(key, val)
    if EMDASH in out:
        raise SystemExit(f"Em dash detectado en {page['file']}")
    dest = ROOT / page["file"]
    dest.write_text(out, encoding="utf-8")
    page["_stats"] = stats
    print(f"{page['id']}: {page['file']} ({stats['cites']} citas, {stats['rows']} filas)")
    return dest


def card(page: dict) -> str:
    n = "M" if page["kind"] == "manual" else f"{page['num']:02d}"
    topics = page.get("topics") or []
    topic_html = ", ".join(html.escape(t) for t in topics[:5]) or "Guía del certamen."
    badges = [page["fuentes"]] if page.get("fuentes") else []
    if page["kind"] == "manual":
        badges = ["mapa del certamen", "cifras", "pares que se confunden"]
    return f"""    <a href="{Path(page['file']).name}">
      <span class="gn">{n}</span>
      <h3>{html.escape(page['title'])}</h3>
      <p>{topic_html}</p>
      <div class="badges">{''.join(f'<span>{html.escape(b)}</span>' for b in badges)}</div>
    </a>"""


def index_page() -> str:
    chapters = sorted([p for p in PAGES if p["kind"] == "chapter"], key=lambda p: p["num"])
    manual = next((p for p in PAGES if p["kind"] == "manual"), None)
    order = ([manual] if manual else []) + chapters
    cards = "\n".join(card(p) for p in order)

    total_cites = sum(p.get("_stats", {}).get("cites", 0) for p in PAGES)
    total_rows = sum(p.get("_stats", {}).get("rows", 0) for p in PAGES)
    total_figs = sum(len(load_figures(p["id"]).get("figures", [])) for p in chapters)
    total_words = sum(p.get("_stats", {}).get("words", 0) for p in PAGES)

    def miles(n: int) -> str:
        return f"{n:,}".replace(",", ".")

    rows = "".join(
        f"<tr><td>{p['num']:02d}</td>"
        f"<td><a href=\"{Path(p['file']).name}\">{html.escape(p['title'])}</a></td>"
        f"<td>{html.escape(p.get('fuentes', ''))}</td>"
        f"<td>{p.get('_stats', {}).get('cites', 0)}</td>"
        f"<td>{p.get('_stats', {}).get('rows', 0)}</td>"
        f"<td>{miles(p.get('_stats', {}).get('words', 0))}</td></tr>"
        for p in chapters
    )

    hero = f"""<header class="hero">
  <div class="hero-inner">
    <p class="eyebrow">{html.escape(SITE['eyebrow'])}</p>
    <h1>{SITE['title']}</h1>
    <p class="lede">{SITE['lede']}</p>
    <div class="meta-grid">
      <div><span>Guías</span><strong>{len(chapters)} + manual</strong></div>
      <div><span>Palabras</span><strong>{miles(total_words)}</strong></div>
      <div><span>Citas</span><strong>{miles(total_cites)}</strong></div>
      <div><span>Filas de tabla</span><strong>{miles(total_rows)}</strong></div>
      <div><span>Figuras</span><strong>{total_figs}</strong></div>
      <div><span>Ramo</span><strong>Neurociencias · UBB 2026-2</strong></div>
    </div>
    <div class="hero-actions">
      <button class="btn primary" id="printBtn" type="button">Imprimir / guardar PDF</button>
      <button class="btn" id="themeBtn" type="button" aria-pressed="false">Modo oscuro</button>
      <a class="btn" href="manual.html">Ir al manual</a>
    </div>
  </div>
</header>"""

    body = f"""<section id="guias" class="card">
  <div class="section-kicker"><span class="n">01</span> Material</div>
  <h2>Guías del certamen</h2>
  <div class="guide-grid">
{cards}
  </div>
</section>

<section id="orden" class="card">
  <div class="section-kicker"><span class="n">02</span> Método</div>
  <h2>Orden de estudio sugerido</h2>
  <ol>
    <li><strong>Manual del Certamen 1:</strong> el mapa, las cifras y los pares que se confunden.</li>
    <li><strong>Las ocho guías en orden:</strong> nace, se construye, emite señal, se comunica, madura, falla, y el cierre con Cajal.</li>
    <li><strong>Puntos de examen:</strong> al final de cada guía, para repasar sin releer.</li>
  </ol>
  <div class="keybox"><span class="box-title">Cómo citar</span>
    Cada afirmación lleva la fuente al lado: <span class="cite">Purves p. 78</span>,
    <span class="cite">Zeise p. 108</span>, <span class="cite">apuntes, bloque III</span>,
    <span class="cite">Kelly §7</span>. Si el material no lo dice, no está en la guía.
  </div>
</section>

<section id="cobertura" class="card">
  <div class="section-kicker"><span class="n">03</span> Verificación</div>
  <h2>Cobertura</h2>
  <div class="table-wrap" role="region" aria-label="Cobertura por guía" tabindex="0">
    <table>
      <thead><tr><th>#</th><th>Guía</th><th>Fuentes</th><th>Citas</th><th>Filas</th><th>Palabras</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>

<section id="fuentes" class="card">
  <div class="section-kicker"><span class="n">04</span> Fuentes</div>
  <h2>Notas de fuente</h2>
  <ul>
    <li>Purves, <em>Neurociencia</em>, edición en español: capítulos 3, 4, 22 y 23.</li>
    <li>Zeise (ed.), <em>Neurociencia para la psicología y otras áreas</em>: capítulos 2, 4 y 7.</li>
    <li>Apuntes de clase de Neurociencias Aplicadas a la Medicina (56 páginas) y seminario de Cajal.</li>
    <li>Gross, <em>Joseph Altman and adult neurogenesis</em>; Kelly et al., <em>Sci. Adv.</em> 2026; viñetas clínicas de Kandel.</li>
    <li>No se publican los PDF originales ni el OCR crudo; solo el HTML de estudio.</li>
    <li>Material docente, no una recomendación clínica.</li>
  </ul>
</section>"""
    toc = """<li><a href="#guias">Guías del certamen</a></li>
        <li><a href="#orden">Orden de estudio</a></li>
        <li><a href="#cobertura">Cobertura</a></li>
        <li><a href="#fuentes">Fuentes</a></li>"""
    out = TPL
    for key, val in {
        "%%TITLE%%": f"Certamen 1 · Neurociencias UBB",
        "%%DESC%%": SITE["lede"],
        "%%CSS%%": CSS,
        "%%HERO%%": hero,
        "%%TOC%%": toc,
        "%%NAV%%": '<a href="manual.html">Manual</a>',
        "%%BODY%%": body,
        "%%JS%%": JS,
        "%%CREDITS%%": "creditos.html",
    }.items():
        out = out.replace(key, val)
    if EMDASH in out:
        raise SystemExit("Em dash detectado en el índice")
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print("índice: index.html")
    return out


def credits_page() -> None:
    items = []
    for page in PAGES:
        for fig in load_figures(page["id"]).get("figures", []):
            items.append((page, fig))
    rows = "".join(
        f'<tr id="{figure_anchor(fig["number"])}"><td><a href="{page["file"]}#{figure_anchor(fig["number"])}">'
        f'Figura {html.escape(fig["number"])}</a></td><td>{html.escape(page["title"])}</td>'
        f'<td>{fig.get("source", "")}</td></tr>'
        for page, fig in items
    ) or '<tr><td colspan="3">Sin figuras registradas.</td></tr>'
    hero = f"""<header class="hero">
  <div class="hero-inner">
    <p class="eyebrow">{html.escape(SITE['eyebrow'])}</p>
    <h1>Créditos de las figuras</h1>
    <p class="lede">Cada figura de las guías, con su fuente y su página. La titularidad corresponde a los autores y editoriales de las obras citadas.</p>
    <div class="meta-grid">
      <div><span>Figuras</span><strong>{len(items)}</strong></div>
      <div><span>Fuentes</span><strong>Purves · apuntes de clase · artículos</strong></div>
      <div><span>Uso</span><strong>Educativo, sin fines comerciales</strong></div>
    </div>
    <div class="hero-actions">
      <a class="btn primary" href="index.html">Volver al índice</a>
      <button class="btn" id="themeBtn" type="button" aria-pressed="false">Modo oscuro</button>
    </div>
  </div>
</header>"""
    body = f"""<section id="aviso" class="card">
  <div class="section-kicker"><span class="n">01</span> Aviso</div>
  <h2>Fuente y titularidad</h2>
  <div class="warnbox"><span class="box-title">Obras citadas</span>
    Las figuras provienen de las obras indicadas en cada leyenda: Purves, <em>Neurociencia</em>
    (Editorial Médica Panamericana), los apuntes de clase del ramo y los artículos del curso.
    La titularidad corresponde a sus autores y editoriales. Se reproducen con fines
    exclusivamente educativos y sin fines comerciales, citando la figura y la página.
    Los PDF originales y el OCR crudo no se distribuyen.
  </div>
  <p class="small">Si eres titular de derechos y deseas la retirada de una figura, abre un
    <a href="https://github.com/kraksiplus/neuro-2026-2/issues">issue en el repositorio</a>.
    El sitio puede regenerarse sin imágenes sin romper el texto.</p>
</section>

<section id="listado" class="card">
  <div class="section-kicker"><span class="n">02</span> Listado</div>
  <h2>Todas las figuras</h2>
  <div class="table-wrap" role="region" aria-label="Listado de figuras y fuentes" tabindex="0">
    <table>
      <thead><tr><th>Figura</th><th>Guía</th><th>Fuente</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>"""
    toc = """<li><a href="#aviso">Aviso</a></li>
        <li><a href="#listado">Listado</a></li>"""
    out = TPL
    for key, val in {
        "%%TITLE%%": "Créditos de las figuras · Neurociencias UBB",
        "%%DESC%%": "Fuente, página y titularidad de cada figura usada en las guías de Neurociencias.",
        "%%CSS%%": CSS,
        "%%HERO%%": hero,
        "%%TOC%%": toc,
        "%%NAV%%": '<a href="index.html">Índice</a>',
        "%%BODY%%": body,
        "%%JS%%": JS,
        "%%CREDITS%%": "creditos.html",
    }.items():
        out = out.replace(key, val)
    (ROOT / "creditos.html").write_text(out, encoding="utf-8")
    print(f"créditos: creditos.html ({len(items)} figuras)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page")
    ap.add_argument("--indexes", action="store_true")
    args = ap.parse_args()
    if args.page:
        page = next(p for p in PAGES if p["id"] == args.page)
        build_page(page)
        credits_page()
        return
    if not args.indexes:
        for page in PAGES:
            build_page(page)
    index_page()
    credits_page()


if __name__ == "__main__":
    main()

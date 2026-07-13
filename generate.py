#!/usr/bin/env python3
"""
Statische sitegenerator voor Total Tuning

Werkwijze:
  1. Artikelen staan als .md-bestanden in content/articles/ met een frontmatter-kop.
  2. Losse pagina's (privacy, cookies, disclaimer) staan in content/pages/.
  3. Templates staan in templates/ (Jinja2).
  4. Statische bestanden (css, robots, favicon, _headers, _redirects) staan in static/.

Bouwen:
  python generate.py

De volledige website verschijnt daarna in de map public/, klaar om te
deployen naar Cloudflare Pages.
"""

import os
import re
import shutil
from datetime import datetime, date

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

# --------------------------------------------------------------------------- #
# Configuratie
# --------------------------------------------------------------------------- #

SITE = {
    "name": "Total Tuning",
    "domain": "totaltuning.nl",
    "base_url": "https://totaltuning.nl",
    "email": "info@totaltuning.nl",
    "tagline": "Magazine over carstyling en cartuning",
    "description": (
        "Onafhankelijk magazine over carstyling en cartuning. Uitleg, "
        "achtergrond en praktische kennis over het aanpassen van auto's."
    ),
    "year": 2026,
}

NAV = [
    {"label": "Home", "url": "/"},
    {"label": "Over", "url": "/over/"},
    {"label": "Nieuws", "url": "/nieuws/"},
    {"label": "Partners", "url": "/partners/"},
    {"label": "Contact", "url": "/contact/"},
]

FOOTER_LEGAL = [
    {"label": "Privacybeleid", "url": "/privacybeleid/"},
    {"label": "Cookiebeleid", "url": "/cookiebeleid/"},
    {"label": "Disclaimer", "url": "/disclaimer/"},
]

# Volgorde waarin onderwerpen op de site getoond worden.
CATEGORIES = ["Exterieur", "Onderstel", "Verlichting", "Uitlaat", "Interieur"]

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

MONTHS_NL = [
    "", "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]


# --------------------------------------------------------------------------- #
# Hulpfuncties
# --------------------------------------------------------------------------- #

def parse_frontmatter(text):
    """Splitst een eenvoudige '---'-frontmatter van de markdown-body."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, parts[2].lstrip("\n")


def md_to_html(body):
    return markdown.markdown(
        body,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def nl_date(d):
    return f"{d.day} {MONTHS_NL[d.month]} {d.year}"


def load_articles():
    articles = []
    src = os.path.join(ROOT, "content", "articles")
    for name in os.listdir(src):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(src, name), encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_frontmatter(raw)
        d = datetime.strptime(meta["date"], "%Y-%m-%d").date()
        articles.append({
            "title": meta["title"],
            "slug": meta["slug"],
            "category": meta.get("category", ""),
            "excerpt": meta.get("excerpt", ""),
            "read_minutes": meta.get("read_minutes", ""),
            "date": d,
            "date_iso": d.isoformat(),
            "date_nl": nl_date(d),
            "url": f"/nieuws/{meta['slug']}/",
            "html": md_to_html(body),
        })
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def load_pages():
    pages = {}
    src = os.path.join(ROOT, "content", "pages")
    for name in os.listdir(src):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(src, name), encoding="utf-8") as f:
            raw = f.read()
        meta, body = parse_frontmatter(raw)
        pages[meta["slug"]] = {
            "title": meta["title"],
            "slug": meta["slug"],
            "description": meta.get("description", ""),
            "url": f"/{meta['slug']}/",
            "html": md_to_html(body),
        }
    return pages


def write(path, html):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" \
        else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


# --------------------------------------------------------------------------- #
# Bouwen
# --------------------------------------------------------------------------- #

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    env = Environment(
        loader=FileSystemLoader(os.path.join(ROOT, "templates")),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(site=SITE, nav=NAV, footer_legal=FOOTER_LEGAL,
                        categories=CATEGORIES, now_year=date.today().year)

    articles = load_articles()
    pages = load_pages()

    # Homepage
    write("/", env.get_template("home.html").render(
        page_title=None,
        meta_description=SITE["description"],
        canonical="/",
        latest=articles[:4],
    ))

    # Over
    write("/over/", env.get_template("over.html").render(
        page_title="Over " + SITE["name"],
        meta_description=(
            "Over Total Tuning: een onafhankelijk magazine over "
            "carstyling en cartuning."),
        canonical="/over/",
    ))

    # Nieuws index, gegroepeerd per categorie
    groups = build_groups(articles)
    write("/nieuws/", env.get_template("nieuws.html").render(
        page_title="Nieuws",
        meta_description=(
            "Alle artikelen over carstyling en cartuning: exterieur, "
            "onderstel, verlichting, uitlaat en interieur."),
        canonical="/nieuws/",
        groups=groups,
    ))

    # Artikelen
    art_tpl = env.get_template("artikel.html")
    for i, art in enumerate(articles):
        related = [a for a in articles if a["slug"] != art["slug"]][:3]
        write(art["url"], art_tpl.render(
            page_title=art["title"],
            meta_description=art["excerpt"],
            canonical=art["url"],
            article=art,
            related=related,
        ))

    # Partners
    write("/partners/", env.get_template("partners.html").render(
        page_title="Partners",
        meta_description=(
            "Linkpartnerschappen met Total Tuning. Voor automotive-, "
            "styling- en tuningwebsites die passen bij het magazine."),
        canonical="/partners/",
    ))

    # Contact
    write("/contact/", env.get_template("contact.html").render(
        page_title="Contact",
        meta_description=(
            "Neem contact op met Total Tuning via "
            + SITE["email"] + "."),
        canonical="/contact/",
    ))

    # Losse pagina's (privacy, cookies, disclaimer)
    page_tpl = env.get_template("pagina.html")
    for slug, page in pages.items():
        write(page["url"], page_tpl.render(
            page_title=page["title"],
            meta_description=page["description"],
            canonical=page["url"],
            page=page,
        ))

    # 404
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(env.get_template("404.html").render(
            page_title="Pagina niet gevonden",
            meta_description="",
            canonical=None,
        ))

    # Statische bestanden kopieren
    static_src = os.path.join(ROOT, "static")
    for rootdir, _dirs, files in os.walk(static_src):
        for fn in files:
            srcfile = os.path.join(rootdir, fn)
            rel = os.path.relpath(srcfile, static_src)
            dst = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(srcfile, dst)

    # Sitemap
    build_sitemap(articles, pages)

    print(f"Klaar. {len(articles)} artikelen en {len(pages)} losse pagina's "
          f"gegenereerd in {OUT}/")


def build_groups(articles):
    """Groepeert artikelen per categorie. Categorieen buiten de vaste lijst
    (zoals 'Algemeen') komen bovenaan, daarna de vaste onderwerpvolgorde."""
    present = []
    for a in articles:
        if a["category"] not in present:
            present.append(a["category"])
    extra = [c for c in present if c not in CATEGORIES]
    order = extra + [c for c in CATEGORIES if c in present]
    groups = []
    for cat in order:
        items = [a for a in articles if a["category"] == cat]
        if items:
            groups.append({"name": cat, "slug": cat.lower(), "articles": items})
    return groups


def build_sitemap(articles, pages):
    urls = ["/", "/over/", "/nieuws/", "/partners/", "/contact/"]
    urls += [a["url"] for a in articles]
    urls += [p["url"] for p in pages.values()]
    today = date.today().isoformat()
    items = "\n".join(
        f"  <url><loc>{SITE['base_url']}{u}</loc>"
        f"<lastmod>{today}</lastmod></url>" for u in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n</urlset>\n"
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


if __name__ == "__main__":
    build()

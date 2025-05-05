#!/usr/bin/env python3
"""
bbc_religions_scraper.py
────────────────────────
Scrapes the archived BBC Religions site and produces a Markdown‑to‑HTML file
structured like:

Table of Contents
- religion A
- religion B
<hr>
- Religion A
  - sub‑heading 1 (link)
  - sub‑heading 2 (link)
…
"""

from collections import defaultdict
import pathlib
import sys
from urllib.parse import urljoin

import requests
from lxml import html
import re

BASE_URL   = "https://www.bbc.co.uk/religion/religions"
HOME_XPATH = '//*[@id="prg-wrapper-featured"]/div[2]/div[2]/div/div/ul[1]/li/h3/a'
ACC_TITLES = '//*[@id="prg-wrapper-featured"]/div[4]'
ACC_LINKS  = '//*[@id="prg-wrapper-featured"]/div[4]/div[1]/div/div/ul/li/a'
ACCORDION_XPATH  = '//*[@id="prg-wrapper-featured"]//div[contains(@class,"accordion")]'
PROMO_TEXT_XPATH = ('//*[@id="prg-wrapper-featured"]'
                    '//div[contains(@class,"top_promo")]//div[@class="content"]/p')
MODAL_HTML = """
<div id="link-modal" class="modal" aria-hidden="true">
  <div class="modal-content" role="dialog" aria-modal="true">
    <button id="modal-close" aria-label="Close modal">×</button>
    <iframe id="modal-frame" src="" loading="lazy"></iframe>
  </div>
</div>"""

FOOTER_HTML = """
<footer>
  <p>© 2025 <a href="https://www.linkedin.com/in/joshuamaxweiner/" target="_blank" rel="noopener">Joshua Weiner</a>.  
  This page is an academic archival project &mdash; all original article content and images remain © BBC.</p>
</footer>"""

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (compatible; BBC-Scraper/1.0)"

def _fix_text(txt: str) -> str:
    """
    Try to reverse 'UTF‑8 bytes decoded as Latin‑1' mojibake, e.g.
    'CandomblÃ©' -> 'Candomblé'.  If it fails, return txt unchanged.
    """
    try:
        return txt.encode('latin1').decode('utf8')
    except UnicodeEncodeError:
        return txt

def fetch(url: str) -> html.HtmlElement:
    """Download *url* and return an lxml tree, forcing UTF‑8 decoding."""
    resp = requests.get(url, timeout=20, headers={
        "User-Agent": "Mozilla/5.0 (compatible; BBC-Scraper/1.0)"})
    resp.raise_for_status()
    parser = html.HTMLParser(encoding="utf-8", recover=True)
    return html.fromstring(resp.content, parser=parser)

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def get_religions() -> list[dict]:
    """Extract (title, url) pairs for each religion on the home page."""
    root = fetch(BASE_URL)
    items = []
    for a in root.xpath(HOME_XPATH.replace("[1]", "")):          # strip the hard‑coded index
        title = a.text_content().strip()
        link  = urljoin(BASE_URL, a.get("href"))
        items.append({"title": title, "url": link, "subs": []})
    return items

def get_subsections(rel: dict) -> None:
    """
    Populate rel["promo"]  -> summary text (str)
              rel["subs"]  -> list[(h2_heading, link_text, absolute_href)]
    """
    doc = fetch(rel["url"])

    # Grab the promo blurb
    promo_paras = [p.text_content().strip() for p in doc.xpath(PROMO_TEXT_XPATH)]
    rel["promo"] = "  ".join(promo_paras)      # join with double‑space for Markdown
    rel["subs"] = []
    for acc in doc.xpath(ACCORDION_XPATH):
        # Accordion heading
        h2_nodes = acc.xpath('./h2')
        if not h2_nodes:
            continue                              # skip malformed blocks
        heading = h2_nodes[0].text_content().strip()

        # Out-links inside this accordion
        for a in acc.xpath('.//div[contains(@class,"accordion_content")]//a'):
            link_text = a.text_content().strip()
            href      = urljoin(rel["url"], a.get('href'))
            rel["subs"].append((heading, link_text, href))

def build_markdown(rels: list[dict]) -> str:
    md = ["Table of Contents"]
    md.extend(f"- {rel['title']}" for rel in rels)
    md.append("<hr>")

    for rel in rels:
        md.append(f"- {rel['title']}")
        if rel.get("promo"):
            md.append(f"  - *{rel['promo']}*")   # italics for the promo summary

        # group by accordion heading
        last_h = None
        for heading, link_txt, href in rel["subs"]:
            if heading != last_h:
                md.append(f"  - **{heading}**")
                last_h = heading
            md.append(f"    - {link_txt} ({href})")
        md.append("")          # blank line for readability
    return "\n".join(md)


def markdown_to_html(md: str) -> str:
    """Convert Markdown to simple HTML without external deps if possible."""
    try:
        import markdown  # optional
        return markdown.markdown(md)
    except ModuleNotFoundError:
        # very dumb fallback: wrap in <pre>
        return f"<html><body><pre>\n{md}\n</pre></body></html>"

def build_html(rels: list[dict]) -> str:
    # -------------- Table‑of‑Contents ------------------
    toc_items = "\n".join(
        f'        <li><a href="#{slugify(rel["title"])}">{rel["title"]}</a></li>'
        for rel in rels
    )
    toc_html = f"""
    <nav id="toc">
      <h2>Table of Contents</h2>
      <ul>
{toc_items}
      </ul>
    </nav>"""

    # -------------- Main content -----------------------
    sections = []
    for rel in rels:
        sec_id = slugify(rel["title"])
        promo  = f'<p class="promo">{rel.get("promo","")}</p>' if rel.get("promo") else ""
        groups: dict[str, list[tuple[str,str]]] = defaultdict(list)
        for heading, link_txt, href in rel["subs"]:
            groups[heading].append((link_txt, href))

        accordion_blocks = []
        for heading, links in groups.items():
            li_html = "\n".join(
                f'          <li><a href="#" data-url="{href}" class="modal-link">{txt}</a></li>'
                for txt, href in links
            )
            accordion_blocks.append(f"""
                <details>
                    <summary>{heading}</summary>
                    <ul class="links">{li_html}</ul>
                </details>
            """)

            section_html = f"""
                <section id="{sec_id}">
                <h2>{rel["title"]}</h2>
                {promo}
                {''.join(accordion_blocks)}
                </section>
            """
        sections.append(section_html)

    return f"""<!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="utf-8">
            <title>BBC Religions Overview</title>
            <link rel="stylesheet" href="./src/static/main.css">
            </head>
            <body>
            <header><h1>BBC Religions: Overview & Teaching Links</h1></header>
            {toc_html}
            <main>
            {''.join(sections)}
            </main>
            {FOOTER_HTML}
            {MODAL_HTML}
            <script src="./src/static/modal.js"></script>
            </body>
            </html>
            """

def main(out_path: str = "bbc_religions.html") -> None:
    religions = get_religions()
    for rel in religions:
        get_subsections(rel)

    html_out = build_html(religions)
    pathlib.Path(out_path).write_text(html_out, encoding="utf-8")
    print(f"Finished. Open '{out_path}'.")

if __name__ == "__main__":
    main(*sys.argv[1:]) 

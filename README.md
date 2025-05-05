# BBC Religions Archive Viewer

An interactive, **self‑hosted classroom reference** that gathers the legacy “BBC Religions” site (archived by the BBC in 2014) into a single, clean, modern webpage with:

* a sticky header & responsive **table of contents**  
* per‑religion *promo* summaries  
* collapsible accordions for every topic (*Beliefs*, *History*, …)  
* **in‑page modals** that preview each BBC article without leaving the site  
* smooth scrolling, Material‑style palette, and basic a11y

> **Academic use only** — this project is a not‑for‑profit archival tool for teaching comparative‑religion. All articles, images, and trademarks remain © BBC.

---

## Why?

The original BBC Religions microsite is no longer actively maintained; its JavaScript is broken and the navigation is painful for students.  
This project repackages the public‐domain HTML into a single, searchable hand‑out so learners can jump straight to the content.

---

## What’s inside

| Folder | Purpose |
|--------|---------|
| `src/generator.py` | Scraper that pulls the archive, fixes encoding issues, and emits `bbc_religions.html`. |
| `src/static/main.css` | Material‑inspired stylesheet. |
| _generated_ `bbc_religions.html` | One‑page, offline‑friendly viewer. |
| `README.md` | This file. |

---

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt      # requests, lxml
python src/generator.py              # creates bbc_religions.html
open bbc_religions.html              # or double‑click in Finder / Explorer
```

No build tools, databases, or servers are required.
You can host the resulting HTML/CSS file on GitHub Pages or any static host.

## Features

- Robust UTF‑8 fixer — resolves mojibake like CandomblÃ© → Candomblé
- Modal preview — links open in an iframe overlay; if the BBC blocks embedding the code gracefully opens a new tab.
- Progressive enhancement — all content remains accessible as plain links if JavaScript is disabled.
- Mobile‑friendly breakpoints & smooth‑scroll.
- Minimal footprint: one HTML file + one CSS file + ~80 kB JS (inline).

## Credits

Original articles & images © BBC. Retrieved from https://www.bbc.co.uk/religion/religion.
Project concept, scraper & UI © 2025 Joshua Weiner.
Icons: Material Symbols (Apache 2.0).

## License

The code in this repo is released under the MIT License — see LICENSE.
The embedded BBC content is used under fair‑dealing for educational purposes and must not be redistributed commercially.

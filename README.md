# Nūr's website: the sources

## TL;DR

- This branch (`source`) holds what builds https://getnurapp.com. The `main` branch holds the built files that GitHub Pages serves; never edit `main` by hand.
- **The page** is one file, `demos/option-d/index.html`, plus its `assets/`. It runs as the demo (with `#/` addresses) and as the built site (real paths).
- **Build:** `python demos/blog_build.py`, then `python demos/docs_build.py`, then `python demos/site_build.py`. The result is written to `site/`, which is not kept here.
- **Publish:** `powershell -File demos/publish_site.ps1 -Message "…"` mirrors `site/` into a clone of `main` and pushes it. Then `python demos/indexnow_ping.py` tells Bing what changed.
- Made in Nūr issue #257 (AGMTechnology/nur). The lane's build notes, with every decision and Ahmed's words, are in nur-docs once /lead has moved them.

## What is where

| Path | What |
|---|---|
| `demos/option-d/index.html` | The whole site: markup, styles, script. `ARTICLES` and `DOCS` are written into it by the two builders below. |
| `demos/option-d/assets/` | Pictures, the store badges, the app's sounds, the icon. |
| `blog/<id>.json` | The eight articles, FR and EN: slug, titles, description, excerpt, body (HTML). |
| `demos/blog_build.py` | Checks the articles (lengths, dashes, banned words, forbidden markup) and writes `ARTICLES` into the page. |
| `pages/about.json`, `pages/legal.json`, `pages/privacy-site.json` | À propos, the mentions légales, and the website's section of the privacy policy. |
| `pages/legal-src/` | The privacy policy and the terms (Markdown, FR and EN), the site's own copy. |
| `demos/docs_build.py` | Turns those into `DOCS` in the page. |
| `demos/site_build.py` | Builds `site/`: one HTML file per page and language, with its head (title, description, canonical, hreflang, Open Graph, JSON-LD). Also writes `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `CNAME`, `404.html`, `.nojekyll` and the IndexNow key file, and serves fonts and libraries from `/assets/vendor/`. Settings at its top: `ORIGIN`, `GO_LIVE`. |
| `demos/vendor/`, `demos/vendor_fetch.py` | Amiri and Nunito (SIL OFL), gsap, ScrollTrigger, lenis, three, downloaded once so no request leaves the site before the cookie banner is answered. |
| `demos/indexnow_ping.py` | The IndexNow ping (all pages, or the paths given). |
| `demos/en_guard.py` | Checks an English rewrite of an article against its copy taken before. |
| `demos/probes/` | Browser and crawler checks (Playwright). On Ahmed's machine they run through `tools\heavy\heavy.ps1`, one at a time. |

## Settings inside the page

- `STORE = { ios: '', android: '' }`: the store listings' addresses. While empty, the badges read « Bientôt disponible ».
- `GA_ID`: Google Analytics, loaded only after « Accepter » and only on the built site.

## Paths

`publish_site.ps1` and a few probes name paths on Ahmed's machine (the lane's notes folder, the clone at `C:\Users\ahmed\Desktop\nur-site`). Change them if the sources move.

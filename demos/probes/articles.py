"""v74 probe: the eight articles. For each, in French then English: its hash, page title, description, H1, the words
on the page, the related cards, errors; on English pages, any visible French. Then a link inside an article to another
one, the old #/blog/commencer address, the language switch on an article, and the blog's cards and chips in both
languages (frames). Takes `<demo folder> <port> <out dir> [WxH]`."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = map(int, (sys.argv[4] if len(sys.argv) > 4 else "1440x900").split("x"))
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
SCAN = r"""(() => { const out = new Set(), FR = /[éèêàâçùûôîœ«»]|\b(le|la|les|des|du|une|et|ton|ta|tes|pour|avec|dans|sur|est|pas|qui|que|tu|leçon|lettre|verset|sourate|histoire|écoute|appli)\b/i;
  const vis = e => { for (let x = e; x && x.nodeType === 1; x = x.parentElement) { const c = getComputedStyle(x); if (c.display === 'none' || c.visibility === 'hidden') return false; } return true; };
  const w = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) { const t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (t.length > 1 && FR.test(t) && n.parentElement && !n.parentElement.closest('[lang="ar"]') && vis(n.parentElement)) out.add(t.slice(0, 80)); }
  return [...out].slice(0, 8); })()"""
PAGE = """(() => ({ hash: location.hash, title: document.title, desc: (document.querySelector('meta[name=description]') || {}).content, lang: document.documentElement.lang,
  h1: document.querySelector('#h-article').textContent, crumb: document.querySelector('.crumbs ol').innerText.replace(/\\s+/g, ' '),
  words: document.querySelector('#prose').innerText.split(/\\s+/).length, h2: document.querySelectorAll('#prose h2').length,
  img: !!document.querySelector('#art-img img, #art-img .typo'), related: [...document.querySelectorAll('#related .card h3')].map(x => x.textContent.slice(0, 28)),
  parts: [...document.querySelectorAll('#prose .ex, #prose .appcard, #prose .vcard, #prose .tbl')].map(x => x.className.split(' ')[0]), sx: document.documentElement.scrollWidth - innerWidth }))()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
    logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
    page.goto(f"http://127.0.0.1:{port}/index.html#/blog", wait_until="networkidle"); time.sleep(1.5)
    slugs = page.evaluate("ARTICLES_SLUGS = null, [...document.querySelectorAll('[data-slug]')].map(a => a.dataset.slug)")
    arts = page.evaluate("(() => { const s = document.querySelector('script:not([src])'); return null; })()")
    pairs = page.evaluate("""(() => { const t = [...document.scripts].map(s => s.textContent).find(x => x.includes('/*ARTICLES*/'));
      const j = t.slice(t.indexOf('/*ARTICLES*/') + 12, t.indexOf('/*/ARTICLES*/')); return JSON.parse(j).map(a => [a.id, a.fr.slug, a.en.slug]); })()""")
    print("articles:", json.dumps(pairs, ensure_ascii=False))
    page.screenshot(path=f"{out}/blog-fr.png", full_page=True)
    for i, (aid, fr, en) in enumerate(pairs):
        for lang, slug in (("fr", fr), ("en", en)):
            hsh = ("#/en" if lang == "en" else "#") + "/blog/" + slug
            page.goto(f"http://127.0.0.1:{port}/index.html{hsh}", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(1.4)
            st = page.evaluate(PAGE)
            print(aid, lang, json.dumps(st, ensure_ascii=False))
            if lang == "en": print("   french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
            if i in (0, 2, 5) or aid in ("lire-le-coran-debutant",): page.screenshot(path=f"{out}/art-{aid}-{lang}.png", full_page=True)
    # a link inside an article to another one
    page.goto(f"http://127.0.0.1:{port}/index.html#/blog/{pairs[0][1]}", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(1.4)
    link = page.query_selector("#prose [data-art]")
    if link:
        target = link.get_attribute("data-art"); link.click(); time.sleep(2.6)
        print("in-article link →", target, page.evaluate("[location.hash, document.querySelector('#h-article').textContent]"))
    # the old address, and the language switch on an article
    page.goto(f"http://127.0.0.1:{port}/index.html#/blog/commencer", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(1.4)
    print("old address:", page.evaluate("[location.hash, document.querySelector('#h-article').textContent]"))
    page.click(".hdr [data-lang=en]"); page.wait_for_load_state("networkidle"); time.sleep(2.2)
    print("switch on article → EN:", page.evaluate("[location.hash, document.documentElement.lang, document.querySelector('#h-article').textContent]"))
    page.goto(f"http://127.0.0.1:{port}/index.html#/en/blog", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(1.4)
    print("EN blog chips:", page.evaluate("[...document.querySelectorAll('#chips .chip')].map(c => c.textContent)"), "french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
    page.screenshot(path=f"{out}/blog-en.png", full_page=True)
    print("errors:", logs[:6]); b.close()
httpd.shutdown()

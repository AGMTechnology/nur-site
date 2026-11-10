"""v71 probe: the plain blog. At each size: a full-page frame of #/blog, the newest three's boxes (the lead and the two
beside it: their heights, so dead space shows), the chips, a chip pressed (the grid's articles), the article's
breadcrumb back to a filtered blog, and home → « Blog » through the green veil. Takes `<demo folder> <port> <out> [WxH,…]`."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sizes = [tuple(map(int, s.split("x"))) for s in (sys.argv[4] if len(sys.argv) > 4 else "1440x900").split(",")]
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
M = """(() => { const r = e => { const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top + scrollY), Math.round(b.width), Math.round(b.height)]; };
  const card = e => ({ box: r(e), thumb: r(e.querySelector('.thumb')), body: r(e.querySelector('.card-b')), title: e.querySelector('h3').textContent.slice(0, 40),
    bodyContent: (() => { const b = e.querySelector('.card-b'), kids = [...b.children].filter(k => getComputedStyle(k).display !== 'none'); const t = kids[0].getBoundingClientRect().top, bo = kids[kids.length - 1].getBoundingClientRect().bottom; return Math.round(bo - t); })() });
  return { lead: card(document.querySelector('.card--lead')), side: [...document.querySelectorAll('.card--row')].map(card),
    chips: [...document.querySelectorAll('#chips .chip')].map(c => c.textContent + (c.getAttribute('aria-pressed') === 'true' ? '*' : '')),
    grid: [...document.querySelectorAll('#all-grid .card h3')].map(h => h.textContent.slice(0, 30)), h1: document.querySelector('#h-blog').getBoundingClientRect().height | 0,
    sx: document.documentElement.scrollWidth - innerWidth }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html#/blog", wait_until="networkidle"); time.sleep(2.2)
        print(w, "blog", json.dumps(page.evaluate(M), ensure_ascii=False))
        page.screenshot(path=f"{out}/b{w}-blog.png", full_page=True)
        page.click("#chips .chip[data-cat-k=lire]"); time.sleep(.6)
        print(w, "chip lire", json.dumps(page.evaluate("[[...document.querySelectorAll('#chips .chip')].map(c => c.textContent + (c.getAttribute('aria-pressed') === 'true' ? '*' : '')), [...document.querySelectorAll('#all-grid .card h3')].map(h => h.textContent.slice(0, 30))]"), ensure_ascii=False))
        # the article, then its breadcrumb back to the blog, filtered
        page.click(".card--lead"); time.sleep(2.4)
        print(w, "article", page.evaluate("[document.body.dataset.route, document.title]"))
        page.click(".crumbs a[data-cat]"); time.sleep(2.4)
        print(w, "crumb", json.dumps(page.evaluate("[document.body.dataset.route, [...document.querySelectorAll('#chips .chip')].map(c => c.textContent + (c.getAttribute('aria-pressed') === 'true' ? '*' : '')), [...document.querySelectorAll('#all-grid .card h3')].map(h => h.textContent.slice(0, 30))]"), ensure_ascii=False))
        # home, then « Blog » in the header (or the menu): the green veil, mid-way
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
        if not page.evaluate("!![...document.querySelectorAll('[data-link=blog]')].find(a => a.offsetParent)"): page.click("#menu-btn"); time.sleep(.6)
        page.evaluate("[...document.querySelectorAll('[data-link=blog]')].find(a => a.offsetParent).click()"); time.sleep(.45)
        page.screenshot(path=f"{out}/b{w}-veil.png"); time.sleep(2.2)
        print(w, "home→blog", page.evaluate("[document.body.dataset.route, document.title]"))
        print(w, "errors:", logs[:4]); page.close()
    b.close()
httpd.shutdown()

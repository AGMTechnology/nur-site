"""v72 probe: the article page in one column. At each size: the gaps from the header to the breadcrumb, the breadcrumb to
the title, the title to the meta and the picture (the dead space Ahmed saw over the title), the column's width, a
full-page frame, a sound tile pressed, the related cards, errors. Takes `<demo folder> <port> <out dir> [WxH,…]`."""
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
M = """(() => { const b = s => document.querySelector(s).getBoundingClientRect();
  const hd = b('#hdr'), cr = b('.crumbs ol'), h1 = b('#h-article'), mt = b('.art-meta'), im = b('.art-img'), pr = b('#prose');
  return { hdrBottom: Math.round(hd.bottom), headerToCrumbs: Math.round(cr.top - hd.bottom), crumbsToTitle: Math.round(h1.top - cr.bottom),
    title: [Math.round(h1.left), Math.round(h1.top), Math.round(h1.width), Math.round(h1.height)], titleToMeta: Math.round(mt.top - h1.bottom),
    metaToPicture: Math.round(im.top - mt.bottom), picture: [Math.round(im.width), Math.round(im.height)], pictureToText: Math.round(pr.top - im.bottom),
    column: [Math.round(pr.left), Math.round(pr.width)], firstScreenShows: Math.round(innerHeight - im.top) > 0 ? 'picture top at ' + Math.round(im.top) : 'no picture',
    related: document.querySelectorAll('#related .card').length, sx: document.documentElement.scrollWidth - innerWidth }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html#/blog", wait_until="networkidle"); time.sleep(2)
        page.click(".card--lead"); time.sleep(2.6)
        print(w, "article", json.dumps(page.evaluate(M), ensure_ascii=False))
        page.screenshot(path=f"{out}/a{w}-top.png")
        page.screenshot(path=f"{out}/a{w}-full.png", full_page=True)
        page.evaluate("document.querySelector('[data-sound=l-ba]').click()"); time.sleep(.4)
        print(w, "sound tile", page.evaluate("[document.querySelector('[data-sound=l-ba]').classList.contains('is-playing'), document.querySelector('.player') ? getComputedStyle(document.querySelector('.player')).visibility : null]"))
        print(w, "errors:", logs[:4]); page.close()
    b.close()
httpd.shutdown()

"""v75 probe: the built site against the validated demo. Serves both (the demo with its # addresses, the site with real
paths), shoots the same pages at the same size in each and compares them pixel by pixel (share of pixels that differ);
then, on the site: a card opens its article at a real path, back returns to the blog, a link inside an article, the
language switch on an article, and no page errors. Takes `<demo folder> <site folder> <port> <out dir> [WxH]`."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
demo, site, port, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
w, h = map(int, (sys.argv[5] if len(sys.argv) > 5 else "1440x900").split("x"))
os.makedirs(out, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
for d, pt in ((demo, port), (site, port + 1)):
    s = S(("127.0.0.1", pt), functools.partial(Q, directory=d)); threading.Thread(target=s.serve_forever, daemon=True).start()
D, T = f"http://127.0.0.1:{port}/index.html", f"http://127.0.0.1:{port + 1}"
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
PAIRS = [("home-fr", D + "#/", T + "/"), ("blog-fr", D + "#/blog", T + "/blog/"), ("article-fr", D + "#/blog/juz-amma-liste-des-sourates", T + "/blog/juz-amma-liste-des-sourates/"),
         ("home-en", D + "#/en/", T + "/en/"), ("blog-en", D + "#/en/blog", T + "/en/blog/"), ("article-en", D + "#/en/blog/story-of-prophet-yusuf", T + "/en/blog/story-of-prophet-yusuf/")]
def diff(a, b):
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if A.size != B.size: return f"sizes differ {A.size} {B.size}"
    d = ImageChops.difference(A, B).convert("L").point(lambda v: 255 if v > 24 else 0)
    return f"{100 * sum(1 for v in d.getdata() if v) / (A.size[0] * A.size[1]):.2f}% of pixels differ"
with sync_playwright() as p:
    b = p.chromium.launch()
    logs = []
    for name, du, tu in PAIRS:
        shots = []
        for tag, u in (("demo", du), ("site", tu)):
            pg = b.new_page(viewport={"width": w, "height": h}); pg.add_init_script(INIT); pg.on("pageerror", lambda e, t=tag: logs.append(f"{t}: {str(e)[:150]}"))
            pg.goto(u, wait_until="networkidle"); pg.reload(wait_until="networkidle"); time.sleep(3.2)
            pg.evaluate("document.querySelectorAll('.orbit, .orbit--front').forEach(e => e.style.visibility = 'hidden')")   # (the orbit turns with time)
            f = f"{out}/{name}-{tag}.png"; pg.screenshot(path=f); shots.append(f)
            if tag == "site": print(name, "site:", pg.evaluate("[location.pathname, document.documentElement.lang, document.title, document.body.dataset.route]"))
            pg.close()
        print(name, "demo vs site:", diff(*shots))
    pg = b.new_page(viewport={"width": w, "height": h}); pg.add_init_script(INIT); pg.on("pageerror", lambda e: logs.append("nav: " + str(e)[:150]))
    pg.goto(T + "/blog/", wait_until="networkidle"); time.sleep(2)
    pg.click(".card--lead"); time.sleep(2.8)
    print("card →", pg.evaluate("[location.pathname, document.querySelector('#h-article').textContent, document.title]"))
    l = pg.query_selector("#prose [data-art]")
    if l: print("   in-article link href:", l.get_attribute("href")); l.click(); time.sleep(2.8); print("   in-article link →", pg.evaluate("[location.pathname, document.querySelector('#h-article').textContent]"))
    pg.go_back(); time.sleep(2.6); print("back →", pg.evaluate("[location.pathname, document.body.dataset.route, document.querySelector('#h-article').textContent]"))
    pg.go_back(); time.sleep(2.6); print("back →", pg.evaluate("[location.pathname, document.body.dataset.route]"))
    pg.goto(T + "/blog/histoire-prophete-youssouf/", wait_until="networkidle"); time.sleep(2)
    pg.click(".hdr [data-lang=en]"); pg.wait_for_load_state("networkidle"); time.sleep(2.2)
    print("switch on article →", pg.evaluate("[location.pathname, document.documentElement.lang, document.querySelector('#h-article').textContent]"))
    pg.click(".hdr [data-link=home], .hdr .logo"); time.sleep(2.8)
    print("logo →", pg.evaluate("[location.pathname, document.body.dataset.route]"))
    print("errors:", logs[:6]); b.close()

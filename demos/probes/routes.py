"""v69 probe: the routes after the old page went. Home (and a load on an old section's hash, #lecon), the blog index and
the article: page errors, what is visible on each, whether the footer shows, the page's height on home (it must end at
the first node), and a frame of each. Takes `<demo folder> <port> <out dir> [WxH,…]`."""
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
M = """(() => { const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const n = document.querySelector('#hero-node').getBoundingClientRect();
  return { route: document.body.dataset.route, title: document.title, h1: (document.querySelector('[data-page]:not([hidden]) h1') || {}).textContent,
    foot: vis(document.querySelector('body > .foot')), gated: document.body.classList.contains('gated'),
    docH: document.documentElement.scrollHeight, vh: innerHeight, nodeTopAtMax: null,
    sections: [...document.querySelectorAll('[data-page="home"] section')].map(s => s.className).join(' | '),
    sx: document.documentElement.scrollWidth - innerWidth }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in sizes:
        for name, hash_ in (("home", ""), ("old-hash", "#lecon"), ("blog", "#/blog"), ("article", "#/blog/commencer")):
            page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
            logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200])); page.on("console", lambda m: logs.append("console " + m.text[:160]) if m.type == "error" else None)
            page.goto(f"http://127.0.0.1:{port}/index.html{hash_}", wait_until="networkidle"); time.sleep(2.4)
            st = page.evaluate(M)
            if st["route"] == "home":   # at the furthest scroll, the node sits mid-screen
                page.evaluate("window.scrollTo(0, 1e6)"); time.sleep(1.2)
                st["nodeMidAtMax"] = page.evaluate("(() => { const r = document.querySelector('#hero-node').getBoundingClientRect(); return Math.round(r.top + r.height / 2); })()")
                page.evaluate("window.scrollTo(0, 0)"); time.sleep(.6)
            print(w, h, name, json.dumps(st, ensure_ascii=False))
            page.screenshot(path=f"{out}/r{w}-{name}.png", full_page=(name in ("blog", "article")))
            print(w, h, name, "errors:", [l for l in logs if "favicon" not in l][:4]); page.close()
    b.close()
httpd.shutdown()

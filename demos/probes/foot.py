"""v67 probe: the first screen's foot (the scroll hint and the legal links) across sizes. At each size: a frame of the first
screen, the foot's and the badges' boxes, how many rows the links take, each link's height, the demo chip's box, then
the hint after a small scroll and again back at the top. Takes `<demo folder> <port> <out dir> [WxH,…]`."""
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
M = """(() => { const r = e => { if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; };
  const foot = document.querySelector('.hero-foot'), links = [...document.querySelectorAll('.hero-legal a')];
  return { shown: getComputedStyle(foot).display !== 'none', foot: r(foot), hint: r(document.querySelector('.scroll-hint')),
    hintOpacity: getComputedStyle(document.querySelector('.scroll-hint')).opacity, legal: r(document.querySelector('.hero-legal')),
    rows: new Set(links.map(a => Math.round(a.getBoundingClientRect().top))).size, linkH: links.map(a => Math.round(a.getBoundingClientRect().height)),
    badges: r(document.querySelector('.hero-copy .stores')), copy: r(document.querySelector('.hero-copy')), chip: r(document.querySelector('.demo-tag')),
    nav: [...document.querySelectorAll('.hdr .nav a')].map(a => a.textContent), cta: getComputedStyle(document.querySelector('.hdr-cta')).color,
    hdr: r(document.querySelector('.hdr-in')), vh: innerHeight, sx: document.documentElement.scrollWidth - innerWidth }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2.6)
        print(w, h, "top", json.dumps(page.evaluate(M))); page.screenshot(path=f"{out}/f{w}x{h}.png")
        page.mouse.move(w * .3, h * .5); page.mouse.wheel(0, 120); time.sleep(1.2)
        print(w, h, "scrolled", page.evaluate("[Math.round(scrollY), getComputedStyle(document.querySelector('.scroll-hint')).opacity]"))
        page.mouse.wheel(0, -400); time.sleep(1.4)
        print(w, h, "back", page.evaluate("[Math.round(scrollY), getComputedStyle(document.querySelector('.scroll-hint')).opacity]"))
        # the header's « Télécharger » from further down: back to the top
        page.mouse.wheel(0, 300); time.sleep(1.2); y0 = page.evaluate("Math.round(scrollY)")
        page.evaluate("[...document.querySelectorAll('[data-go=telecharger]')].find(a => a.offsetParent).click()"); time.sleep(2.2)
        print(w, h, "cta", y0, "->", page.evaluate("Math.round(scrollY)"))
        print(w, h, "errors:", logs[:3]); page.close()
    b.close()
httpd.shutdown()

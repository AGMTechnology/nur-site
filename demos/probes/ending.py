"""v65 probe: the ending, finely. The run to its end (End), back up to just before the flash, then forward a tenth of a
screen at a time to the end, a frame each; then a trace of alif with the mouse; then back to the start."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sizes = [tuple(map(int, s.split("x"))) for s in (sys.argv[4] if len(sys.argv) > 4 else "1440x900,390x844").split(",")]
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
Q = """(() => { const s = __press.state(); let o = 0; for (const [id, len] of s.segs) { if (id === 'sky') return { q: (s.v - o) / innerHeight, v: s.v }; o += len; } return null; })()"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
        for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
        time.sleep(2)
        bb = page.query_selector("#hero-node").bounding_box()
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
        time.sleep(11.5)
        for _ in range(14): page.keyboard.press("End"); time.sleep(1.2)
        q = page.evaluate(Q); print(w, "at the end", q)
        page.mouse.wheel(0, -(q["q"] - 9.6) * h); time.sleep(2.5); print(w, "back to", page.evaluate(Q))
        i = 0
        while True:
            page.mouse.wheel(0, h * .1); time.sleep(.7); q = page.evaluate(Q)
            page.screenshot(path=f"{out}/n{w}-{i:02d}.png"); i += 1
            if q["q"] >= 12.39 or i > 40: break
        time.sleep(1.5); page.screenshot(path=f"{out}/n{w}-end.png")
        # trace alif: down its stroke with the mouse
        r = page.evaluate("(() => { const r = document.querySelector('.fin .alif').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        x0 = r[0] + r[2] * .5; page.mouse.move(x0, r[1] + r[3] * .12); page.mouse.down()
        for k in range(1, 21): page.mouse.move(x0 + (k % 3 - 1), r[1] + r[3] * (.12 + .8 * k / 20)); time.sleep(.03)
        page.mouse.up(); time.sleep(.6)
        print(w, "traced:", page.evaluate("document.querySelector('.fin-trace').textContent"))
        page.screenshot(path=f"{out}/n{w}-traced.png")
        for _ in range(300): page.mouse.wheel(0, -250); time.sleep(.02)
        time.sleep(3)
        print(w, "back at the start", page.evaluate("[__press.active(), !!document.querySelector('.fin')]"))
        print(w, "errors:", logs[:3]); page.close()
    b.close()
httpd.shutdown()

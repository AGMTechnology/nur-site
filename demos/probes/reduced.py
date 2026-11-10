"""v55, reduced motion: the run on past the scene into the proofs and the closing call by wheel, then back. No errors."""
import sys, threading, functools, http.server, socketserver, time, json
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
S = """(() => { const s = __press.state(); let o = 0, aft = null; for (const [id, len] of s.segs) { if (id === 'sky') aft = [o, len]; o += len; }
  return { v: Math.round(s.v), max: Math.round(s.max), segs: s.segs.map(x => x[0]).join(','), u: aft ? Math.round(s.v - aft[0]) : null, len: aft ? aft[1] : null,
    sceneOn: document.body.classList.contains('scene-on') }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for w, h in ((1440, 900), (390, 844)):
        page = b.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce"); page.add_init_script(INIT)
        errs = []; page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(1.5)
        for y in range(0, 7000, 120): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.02)
        time.sleep(1.2)
        page.click("#hero-node"); time.sleep(3.6)
        page.mouse.move(w * .9, h / 2)
        for i in range(120):
            page.mouse.wheel(0, 300); time.sleep(.08)
            st = page.evaluate(S)
            if st["u"] is not None and st["u"] > h * .4: break
        time.sleep(.5); print(w, "into the sky", json.dumps(page.evaluate(S))); page.screenshot(path=f"{out}/r{w}-1.png")
        page.keyboard.press("End"); time.sleep(.8); print(w, "End", json.dumps(page.evaluate(S))); page.screenshot(path=f"{out}/r{w}-2.png")
        for _ in range(200): page.mouse.wheel(0, -400); time.sleep(.02)
        time.sleep(1.5); print(w, "back", page.evaluate("[__press.active(), !!document.querySelector('.sky-stars')]"))
        print(w, "errors:", errs[:3]); page.close()
    b.close()
httpd.shutdown()

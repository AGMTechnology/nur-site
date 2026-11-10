"""v70 probe: #266's words in place. The hero; the run's first and second stops (features 1 and 2); the road's eight
words (each one's one-line width and the scale it gets, the desktop fit check); Bilal's scene (feature 3); the words in
stars. A frame at each. Takes `<demo folder> <port> <out dir> [WxH,…]`."""
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
SEG = """(() => { const s = __press.state(); let o = 0, r = {}; for (const [id, len] of s.segs) { r[id] = [o, len]; o += len; } return { v: s.v, want: s.want, segs: r, H: innerHeight }; })()"""
WORDS = """(() => [...document.querySelectorAll('.vword')].map(e => { const m = /scale\\(([\\d.]+)/.exec(e.style.transform) || [];
  const t = getComputedStyle(e).transform; let sc = null; if (t && t !== 'none') { const v = t.match(/matrix3d\\(([^)]+)\\)/); if (v) { const a = v[1].split(',').map(Number); sc = Math.hypot(a[0], a[1], a[2]); } }
  return [e.textContent.replace(/\\u00a0/g, ' '), e.offsetWidth, sc && +sc.toFixed(2)]; }))()"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2.6)
        page.screenshot(path=f"{out}/c{w}-0-hero.png")
        print(w, "hero", page.evaluate("(() => { const r = e => { const b = document.querySelector(e).getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; }; return { title: document.title, meta: (document.querySelector('meta[name=description]') || {}).content, lead: r('.hero-copy .lead'), badges: r('.hero-copy .stores'), foot: getComputedStyle(document.querySelector('.hero-foot')).display !== 'none' ? r('.hero-foot') : null }; })()"))
        for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
        time.sleep(2)
        bb = page.query_selector("#hero-node").bounding_box()
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
        time.sleep(12)
        page.screenshot(path=f"{out}/c{w}-1-stop1.png"); print(w, "stop1", page.evaluate("[...document.querySelectorAll('.feat')].map(f => f.innerText.replace(/\\n+/g, ' | '))"))
        page.keyboard.press("End"); time.sleep(7)
        page.screenshot(path=f"{out}/c{w}-2-stop2.png"); print(w, "stop2", page.evaluate("[...document.querySelectorAll('.feat')].map(f => f.innerText.replace(/\\n+/g, ' | '))"))
        # on to the road: End lays the flight out; then back to its start and along it by the wheel
        for _ in range(4):
            st = page.evaluate(SEG)
            if 'voy' in st["segs"]: break
            page.keyboard.press("End"); time.sleep(3)
        st = page.evaluate(SEG); print(w, "segs", json.dumps(st["segs"]))
        vo = st["segs"].get("voy")
        if vo:
            page.mouse.wheel(0, -(st["want"] - (vo[0] + 220))); time.sleep(4)
            print(w, "road words (text, one-line width, scale)", json.dumps(page.evaluate(WORDS), ensure_ascii=False))
            for k in range(14):
                page.mouse.wheel(0, 150); time.sleep(.9)
                if k % 2: page.screenshot(path=f"{out}/c{w}-3-road-{k:02d}.png")
            st = page.evaluate(SEG); page.mouse.wheel(0, (vo[0] + vo[1]) - st["want"] + 2); time.sleep(5)
            page.screenshot(path=f"{out}/c{w}-4-scene.png"); print(w, "scene", page.evaluate("(document.querySelector('.story-hero') || {}).innerText"))
            for _ in range(6):
                st = page.evaluate(SEG)
                if 'sky' in st["segs"]: break
                page.keyboard.press("End"); time.sleep(2)
            st = page.evaluate(SEG); sk = st["segs"].get("sky")
            if sk:
                page.mouse.wheel(0, sk[0] + 8.95 * h - st["want"]); time.sleep(6)
                page.screenshot(path=f"{out}/c{w}-5-stars.png"); print(w, "stars at", round((page.evaluate(SEG)["v"] - sk[0]) / h, 2))
        print(w, "errors:", logs[:4]); page.close()
    b.close()
httpd.shutdown()

"""v56 probe: the run to Bilal's scene, then on: the lift to the night (the words coming apart where they stand), the
flight into the stars (slow, then a fast burst for the streaks), back up into the scene (the words whole again), back to
the start. Frames at each step; WebGL through SwiftShader."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sizes = [tuple(map(int, s.split("x"))) for s in (sys.argv[4] if len(sys.argv) > 4 else "1440x900,390x844").split(",")]
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8", ".js": "text/javascript"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
S = """(() => { const s = __press.state(); let o = 0, seg = null; for (const [id, len] of s.segs) { if (id === 'sky') seg = [o, len]; o += len; }
  const l = document.querySelector('.story-hero .lc'), h = document.querySelector('.story-hero'), f = document.querySelector('.scene-full');
  return { v: Math.round(s.v), u: seg ? Math.round(s.v - seg[0]) : null, len: seg ? seg[1] : null, sky: __press.sky(),
    letter0: l ? [l.style.transform.slice(0, 60), l.style.opacity] : null, heroVis: h ? h.style.visibility : null, fullT: f ? f.style.translate : null,
    sceneOn: document.body.classList.contains('scene-on'), sx: document.documentElement.scrollWidth - innerWidth }; })()"""
ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append("pageerror " + str(e)[:200])); page.on("console", lambda m: logs.append(f"{m.type} {m.text[:160]}") if m.type in ("error", "warning") else None)
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
        for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
        time.sleep(2)
        bb = page.query_selector("#hero-node").bounding_box()
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .9, h * .5)
        time.sleep(11.5)
        for _ in range(30): page.mouse.wheel(0, 100); time.sleep(.06)
        time.sleep(1.2)
        VO = "(() => { let o = 0; for (const [id, len] of __press.state().segs) { if (id === 'voy') return [o, len]; o += len; } return null; })()"
        n = 0
        for it in range(600):
            st = page.evaluate(S); vo = page.evaluate(VO)
            if st["u"] is not None and st["u"] >= -30: break
            if vo and st["v"] >= vo[0] + 150 and it % 3 == 0:   # along the road: a frame every few small steps
                page.screenshot(path=f"{out}/v{w}-{n:02d}.png"); n += 1
            gap = (-st["u"]) if st["u"] is not None else 400
            page.mouse.wheel(0, 70 if vo and st["v"] >= vo[0] else max(20, min(150, gap * .5))); time.sleep(.12)
        time.sleep(3.0)
        st = page.evaluate(S); print(w, "at the scene", json.dumps(st)); page.screenshot(path=f"{out}/s{w}-00.png")
        # the lift and the pause, a tenth of a screen at a time
        for i in range(1, 18):
            page.mouse.wheel(0, h * .1); time.sleep(.9); st = page.evaluate(S)
            print(w, f"lift {i}", json.dumps({k: st[k] for k in ("u", "sky", "letter0", "heroVis", "fullT")}))
            page.screenshot(path=f"{out}/s{w}-{i:02d}.png")
        # the rest of the way, a third of a screen at a time, to the end
        i = 18
        while True:
            for _ in range(3): page.mouse.wheel(0, h * .1); time.sleep(.12)
            time.sleep(.8); st = page.evaluate(S); print(w, f"way {i}", json.dumps({k: st[k] for k in ("u", "sky")}))
            page.screenshot(path=f"{out}/s{w}-{i:02d}.png"); i += 1
            if st["u"] >= st["len"] - 2 or i > 60: break
        time.sleep(1.5); page.screenshot(path=f"{out}/s{w}-end.png")
        # a fast burst back and forth for the streaks
        for _ in range(5): page.mouse.wheel(0, -h * .4); time.sleep(.03)
        time.sleep(.25); st = page.evaluate(S); print(w, "fast", json.dumps({k: st[k] for k in ("u", "sky")})); page.screenshot(path=f"{out}/s{w}-fast.png")
        # back up into the scene: the words whole again
        for _ in range(80):
            page.mouse.wheel(0, -h * .15); time.sleep(.1); st = page.evaluate(S)
            if st["u"] is not None and st["u"] <= -60: break
        time.sleep(1.5); st = page.evaluate(S); print(w, "back in the scene", json.dumps(st)); page.screenshot(path=f"{out}/s{w}-back.png")
        for _ in range(260): page.mouse.wheel(0, -200); time.sleep(.02)
        time.sleep(3)
        print(w, "back at the start", page.evaluate("[__press.active(), !!document.querySelector('.sky-night'), !!document.querySelector('.sky-stars'), document.querySelector('#start-badge').textContent]"))
        print(w, "logs:", [l for l in logs if 'preload' not in l][:6]); page.close()
    b.close()
httpd.shutdown()

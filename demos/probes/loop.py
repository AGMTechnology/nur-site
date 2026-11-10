"""v66 probe: the loop. The run to the sky (End), the last stretch into the book a frame at a time, the flash at its
height, then the landing: frames as the light falls on the hero, the page held while the hand still scrolls, then free.
Then a second run to the end (state left behind by the first would show there). At the last size only: the header's
« Télécharger » during the run (the quick loop). Takes `<demo folder> <port> <out dir> [WxH,…]`."""
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
Q = """(() => { if (!__press.active()) return null; const s = __press.state(); let o = 0;
  for (const [id, len] of s.segs) { if (id === 'sky') return { q: +((s.v - o) / innerHeight).toFixed(3), want: +((s.want - o) / innerHeight).toFixed(3) }; o += len; } return { q: null }; })()"""
P = """(() => { const f = [...document.querySelectorAll('.sky-flash')].map(e => [e.style.visibility, (+e.style.opacity || 0).toFixed(2)]);
  const w = document.querySelector('.hero-title .w');
  return { run: __press.active(), y: Math.round(scrollY), flash: f, w0: w ? [getComputedStyle(w).opacity.slice(0, 4), w.style.transform.slice(0, 40)] : null,
    sceneOn: document.body.classList.contains('scene-on'), sky: !!document.querySelector('.sky-night'), stars: !!document.querySelector('.sky-stars'),
    badge: document.querySelector('#start-badge').textContent, sx: document.documentElement.scrollWidth - innerWidth }; })()"""

SAMPLER = """(() => { window.__smp = []; const t0 = performance.now(); const f = () => {
  const fl = [...document.querySelectorAll('.sky-flash')].map(e => +getComputedStyle(e).opacity).reduce((a, b) => Math.max(a, b), 0);
  const w = document.querySelector('.hero-title .w');
  __smp.push([Math.round(performance.now() - t0), +fl.toFixed(2), Math.round(scrollY), __press.active() ? 1 : 0, w ? +(+getComputedStyle(w).opacity).toFixed(2) : -1]);
  if (performance.now() - t0 < 14000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""

def landing(smp):
    """from the sampled frames: when the run ended, and the light's fall after it"""
    end = next((i for i, x in enumerate(smp) if x[3] == 0), None)
    if end is None: return "no landing"
    t = smp[end][0]; rows = [x for x in smp[end:] if x[0] - t <= 2600]
    pick = [rows[0]] + [next((x for x in rows if x[0] - t >= d), rows[-1]) for d in (100, 300, 500, 700, 900, 1100, 1300, 1800, 2500)]
    gaps = [b[0] - a[0] for a, b in zip(smp[max(0, end - 3):end + 4], smp[max(0, end - 3) + 1:end + 4])]
    return {"frames_around_landing_ms": gaps, "t+ms, flash, scrollY, run, word": [[x[0] - t] + x[1:] for x in pick],
            "max_scrollY_first_2.6s": max(x[2] for x in rows)}

def to_node(page, w, h):
    for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
    time.sleep(2)
    bb = page.query_selector("#hero-node").bounding_box()
    page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
    time.sleep(11.5)

def to_sky(page):
    for _ in range(20):
        page.keyboard.press("End")
        for _ in range(6):
            time.sleep(.2); q = page.evaluate(Q)
            if q and q["q"] is not None: return q
    return page.evaluate(Q)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for si, (w, h) in enumerate(sizes):
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
        page.screenshot(path=f"{out}/l{w}-0-hero-first.png")
        for run in (1, 2):
            to_node(page, w, h)
            q = to_sky(page); print(w, run, "sky laid out", q)
            # (an End press may already have sent it on: hold it before the words)
            if q and q["want"] > 9.0: page.mouse.wheel(0, -(q["want"] - 8.9) * h); time.sleep(2.5)
            q = page.evaluate(Q)
            if q and q["q"] < 8.9: page.mouse.wheel(0, (8.9 - q["q"]) * h); time.sleep(4)
            print(w, run, "before the words", page.evaluate(Q)); page.evaluate(SAMPLER)
            i = 0
            while True:   # the last stretch: a fifth of a screen at a time
                page.mouse.wheel(0, h * .2); time.sleep(.8); q = page.evaluate(Q)
                if run == 1 and i >= 3: page.screenshot(path=f"{out}/l{w}-1-way-{i:02d}.png")
                i += 1
                if not q or i > 12: break
            t0 = time.time(); print(w, run, "landing", round(time.time() - t0, 2), json.dumps(page.evaluate(P)))
            # the hand still on the wheel: the page holds
            for k in range(6):
                page.mouse.wheel(0, 120); time.sleep(.2)
                st = page.evaluate(P); print(w, run, "fall", round(time.time() - t0, 2), json.dumps(st))
                if run == 1 and k in (0, 2): page.screenshot(path=f"{out}/l{w}-2-fall-{k}.png")
            time.sleep(2.2); st = page.evaluate(P); print(w, run, "settled", json.dumps(st))
            print(w, run, "sampled", json.dumps(landing(page.evaluate("__smp"))))
            page.screenshot(path=f"{out}/l{w}-3-settled-run{run}.png")
            page.mouse.wheel(0, 400); time.sleep(1.5); print(w, run, "free", json.dumps(page.evaluate(P)))
            if run == 1: page.screenshot(path=f"{out}/l{w}-4-free.png")
        if si == len(sizes) - 1:   # the header's « Télécharger » during the run
            to_node(page, w, h); page.keyboard.press("End"); time.sleep(1.5)
            print(w, "quick: in the run", page.evaluate(Q))
            page.evaluate("document.querySelector('.hdr-cta').click()"); t0 = time.time()
            for k in range(5):
                time.sleep(.3); st = page.evaluate(P); print(w, "quick", round(time.time() - t0, 2), json.dumps(st))
                page.screenshot(path=f"{out}/l{w}-5-quick-{k}.png")
            time.sleep(2.5); print(w, "quick settled", json.dumps(page.evaluate(P))); page.screenshot(path=f"{out}/l{w}-5-quick-end.png")
        print(w, "errors:", logs[:4]); page.close()
    b.close()
httpd.shutdown()

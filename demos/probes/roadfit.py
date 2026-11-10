"""v70 probe: do the road's words collide, or run off the screen while they can be read? For each variant of the
desktop rows (patched into the served page, the file on disk untouched), the run goes to the road and on along it in
small steps; at each step, the revealed letters of each word give its box on the screen; pairs of boxes that overlap
(as a share of the smaller), and boxes cut by the screen's edge, are counted.
Takes `<demo folder> <port> <WxH> [en] <variant>…`, a variant being 'name=-220,80,-70,190' ('base' leaves the page as it is)."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, size = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = map(int, size.split('x'))
HASHV = '#/en/' if 'en' in sys.argv[4:] else ''   # (v76) the word 'en' runs the English road (Git Bash rewrites a '/en/' argument as a path)
variants = [v.split('=') for v in sys.argv[4:] if v != 'en']
BASE = "dy = (phone ? [-300, -40, -170, 90] : [-220, 80, -70, 190])[lv]"
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
src = open(os.path.join(folder, 'index.html'), encoding='utf-8').read()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
SEG = """(() => { const s = __press.state(); let o = 0, r = {}; for (const [id, len] of s.segs) { r[id] = [o, len]; o += len; } return { v: s.v, want: s.want, segs: r }; })()"""
BOXES = """(() => [...document.querySelectorAll('.vword')].map(e => {
  let l = 1e9, t = 1e9, r = -1e9, b = -1e9, n = 0;
  e.querySelectorAll('span').forEach(s => { if ((+s.style.opacity || 0) < .5) return; const q = s.getBoundingClientRect(); if (!q.width) return; n++; l = Math.min(l, q.left); t = Math.min(t, q.top); r = Math.max(r, q.right); b = Math.max(b, q.bottom); });
  const op = +getComputedStyle(e).opacity, vis = getComputedStyle(e).visibility !== 'hidden';
  const all = [...e.querySelectorAll('span')].every(s => (+s.style.opacity || 0) >= .99) ? 1 : 0;
  return n && op > .05 && vis ? [e.textContent.replace(/\\u00a0/g, ' ').slice(0, 22), Math.round(l), Math.round(t), Math.round(r), Math.round(b), all] : null; }).filter(Boolean))()"""
def run(b, name, rows):
    page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
    if rows and rows.startswith('src:'): html = open(os.path.join(folder, rows[4:]), encoding='utf-8').read()   # another version, as it is
    elif rows is None: html = src
    else: assert src.count(BASE) == 1, 'the rows line moved: update BASE'; html = src.replace(BASE, f"dy = (phone ? [-300, -40, -170, 90] : [{rows}])[lv]")
    page.route("**/index.html", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html))
    logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:160]))
    page.goto(f"http://127.0.0.1:{port}/index.html" + HASHV, wait_until="networkidle"); time.sleep(2.4)
    print("   loaded:", page.evaluate("[location.hash, document.documentElement.lang]"), repr(HASHV))
    for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
    time.sleep(2)
    bb = page.query_selector("#hero-node").bounding_box()
    page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
    time.sleep(12)
    for _ in range(5):
        if 'voy' in page.evaluate(SEG)["segs"]: break
        page.keyboard.press("End"); time.sleep(3)
    st = page.evaluate(SEG); vo = st["segs"]["voy"]
    page.mouse.wheel(0, -(st["want"] - vo[0])); time.sleep(4)
    worst, hits, cut, steps, many, offv = 0, [], [], 0, [], []   # (v78) many: words readable at once; offv: cut by the top or bottom
    while page.evaluate(SEG)["v"] < vo[0] + vo[1] - 400 and steps < 70:
        page.mouse.wheel(0, 50); time.sleep(.5); steps += 1
        # a word is « being read » when its whole box is on the screen and it is no taller than a third of it; only such
        # words are compared; a word cut by the edge counts only while it is still being written
        allb = page.evaluate(BOXES); many.append(len([a for a in allb if a[5] >= 1]))
        offv += [(steps, a[0], a[1], a[2], a[3], a[4]) for a in allb if (a[1] < 0 or a[3] > w or a[2] < 56 or a[4] > h) and a[5] >= 1]
        for a in allb:
            if (a[1] < 0 or a[3] > w) and a[5] < 1: cut.append((steps, a[0], a[1], a[3]))
        bx = [a for a in allb if a[1] >= 0 and a[3] <= w and a[2] >= 0 and a[4] <= h and a[4] - a[2] <= h / 3]
        for i in range(len(bx)):
            a = bx[i]
            for j in range(i + 1, len(bx)):
                c = bx[j]
                ix = max(0, min(a[3], c[3]) - max(a[1], c[1])); iy = max(0, min(a[4], c[4]) - max(a[2], c[2]))
                if ix * iy <= 0: continue
                sm = min((a[3] - a[1]) * (a[4] - a[2]), (c[3] - c[1]) * (c[4] - c[2])) or 1
                f = ix * iy / sm; worst = max(worst, f)
                if f > .05: hits.append((steps, a[0], c[0], round(f, 2)))
        if steps % 6 == 0: page.screenshot(path=os.path.join(OUT, f"fit-{name}-{steps:02d}.png"))
    print(name, rows, f"steps {steps}, worst overlap {worst:.2f}, frames over 5%: {len(set(x[0] for x in hits))}, whole words on screen at once: max {max(many or [0])}, per step {many}")
    print("   whole words cut by an edge or under the header (step, word, l, t, r, b):", offv[:8], f"({len(offv)} in all)")
    for x in hits[:12]: print("   overlap", x)
    print("   cut by the edge (step, word, left, right):", cut[:10], f"({len(cut)} in all)")
    print("   errors:", logs[:3]); page.close()
OUT = os.environ.get('OUT', '.'); os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for name, rows in variants: run(b, name, None if rows == 'base' else rows)
    b.close()
httpd.shutdown()

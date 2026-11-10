"""v62 probe: what appears around the badge's impact. Press, then a frame every ~100 ms from 1.2 s to 4.2 s, with the
count of visible cards (rain, descent field) at each, so a pop-in shows as a jump."""
import sys, threading, functools, http.server, socketserver, time, json, os
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = map(int, (sys.argv[4] if len(sys.argv) > 4 else '1440x900').split('x'))
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
S = """(() => { const vis = el => { if (!el) return false; const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    let o = 1, e = el; while (e && e !== document.body) { const c = getComputedStyle(e); if (c.visibility === 'hidden' || c.display === 'none') return false; o *= +c.opacity; e = e.parentElement; }
    return o > .05 && r.right > 0 && r.bottom > 0 && r.left < innerWidth && r.top < innerHeight && r.width > 4; };
  const all = [...document.querySelectorAll('.orb')];
  const groups = {};
  all.forEach(o => { const k = o.closest('.rain') ? 'rain' : o.closest('.vgroup') ? 'voy' : o.closest('.descent') ? 'descent' : o.closest('.orbit, .orbit--front, #orbit-front') ? 'orbit' : o.closest('.flood') ? 'flood' : 'other';
    groups[k] = groups[k] || [0, 0]; groups[k][0]++; if (vis(o)) groups[k][1]++; });
  return { t: Math.round((__press.state().t || 0) * 100) / 100, word: document.querySelector('#start-badge').textContent, groups }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
    page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
    for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
    time.sleep(2)
    bb = page.query_selector("#hero-node").bounding_box()
    page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
    t0 = time.time(); i = 0; prev = None
    while time.time() - t0 < 7.0:
        st = page.evaluate(S); el = time.time() - t0
        if el > 3.9:
            page.screenshot(path=f"{out}/i{i:03d}.png"); i += 1
            key = json.dumps(st['groups'])
            if key != prev: print(f"{el:5.2f}s t={st['t']} {st['word']!r} {key}"); prev = key
    b.close()
httpd.shutdown()

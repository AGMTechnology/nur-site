"""v62 probe: how long each review card is readable. Reach the sky, then sweep the line's progress f from 0 to 1 by
setting the sky's wanted state directly (two frames each), and project each card's corners with the live camera.
Readable = the card fully drawn (opacity ≥ .95), wholly on screen, and at least 34 % of the screen wide (22 % on
phones is too small: 42 %). Prints, per card, the readable stretch in px of scroll (the way spans 4.5 screens)."""
import sys, threading, functools, http.server, socketserver, time, json
from playwright.sync_api import sync_playwright
folder, port = sys.argv[1], int(sys.argv[2])
sizes = [tuple(map(int, s.split("x"))) for s in (sys.argv[3] if len(sys.argv) > 3 else "1440x900,390x844").split(",")]
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
SWEEP = """async (minW) => {
  const S = __press.skyRaw(), g = S.gl, T = g.T, W = innerWidth, H = innerHeight, out = g.cards.map(() => []);
  const raf = () => new Promise(r => requestAnimationFrame(r));
  for (let f = 0; f <= 1.0001; f += 0.0025) {
    S.want = Object.assign({}, S.want, { f, pitch: 0, alpha: 1, morph: 1, birth: 1, plug: 0, settle: 0 });
    await raf(); await raf();
    g.cards.forEach((c, k) => {
      const m = c.mesh; m.updateMatrixWorld();
      const hw = m.geometry.parameters.width / 2, hh = m.geometry.parameters.height / 2;
      const pts = [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]].map(([x, y]) => new T.Vector3(x, y, 0).applyMatrix4(m.matrixWorld).project(g.cam));
      const inFront = pts.every(p => p.z < 1);
      const xs = pts.map(p => (p.x + 1) / 2 * W), ys = pts.map(p => (1 - p.y) / 2 * H);
      const l = Math.min(...xs), r = Math.max(...xs), t = Math.min(...ys), b = Math.max(...ys);
      const ok = inFront && m.visible && m.material.opacity >= .95 && l >= 0 && r <= W && t >= 0 && b <= H && (r - l) >= minW * W;
      if (ok) out[k].push(+f.toFixed(4));
    });
  }
  return out.map(a => a.length ? [a[0], a[a.length - 1], a.length] : null);
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for w, h in sizes:
        page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle"); time.sleep(2)
        for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
        time.sleep(2)
        bb = page.query_selector("#hero-node").bounding_box()
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .9, h * .5)
        time.sleep(11.5)
        page.keyboard.press("End"); time.sleep(4)
        for _ in range(12): page.keyboard.press("End"); time.sleep(1.2)
        ok = page.evaluate("!!(__press.skyRaw() && __press.skyRaw().gl && __press.skyRaw().active)")
        if not ok: print(w, "sky not reached"); page.close(); continue
        res = page.evaluate(SWEEP, .34 if w >= 600 else .42)
        px = h * 5.5
        for k, r in enumerate(res):
            print(w, f"card {k + 1}", "never readable" if not r else f"f {r[0]:.3f}–{r[1]:.3f}  ≈ {round((r[1] - r[0]) * px)} px of scroll")
        page.close()
    b.close()
httpd.shutdown()

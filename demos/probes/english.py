"""v73 probe: the English site. Home, the blog and the article under #/en, then the run (the two stops, the road, the
scene, the stars): on each, the page's language, its title, a frame, and every visible text node or label that still
looks French. Then the FR | EN switch both ways. Takes `<demo folder> <port> <out dir> [WxH]`."""
import sys, threading, functools, http.server, socketserver, time, json, os, re
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = map(int, (sys.argv[4] if len(sys.argv) > 4 else "1440x900").split("x"))
os.makedirs(out, exist_ok=True)
class Utf8(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class Srv(socketserver.TCPServer): allow_reuse_address = True
httpd = Srv(("127.0.0.1", port), functools.partial(Utf8, directory=folder)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
# visible text nodes and labels; French is guessed from French-only letters and common French words
SCAN = r"""(() => { const out = new Set(), FR = /[éèêàâçùûôîœ«»]|\b(le|la|les|des|du|une|et|ton|ta|tes|pour|avec|dans|sur|est|pas|qui|que|tu|ta|ton|leçon|lettre|verset|sourate|histoire|écoute|appli)\b/i;
  const vis = e => { for (let x = e; x && x.nodeType === 1; x = x.parentElement) { const c = getComputedStyle(x); if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return false; } return true; };
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) { const t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (t.length > 1 && FR.test(t) && n.parentElement && !n.parentElement.closest('script,style,[lang="ar"]') && vis(n.parentElement)) out.add(t.slice(0, 90)); }
  document.querySelectorAll('[aria-label],[alt]').forEach(e => ['aria-label', 'alt'].forEach(a => { const v = e.getAttribute(a); if (v && FR.test(v) && vis(e)) out.add('@' + a + ': ' + v.slice(0, 80)); }));
  return [...out]; })()"""
STATE = "({ lang: document.documentElement.lang, title: document.title, hash: location.hash, route: document.body.dataset.route })"
SEG = """(() => { const s = __press.state(); let o = 0, r = {}; for (const [id, len] of s.segs) { r[id] = [o, len]; o += len; } return { v: s.v, want: s.want, segs: r }; })()"""
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": w, "height": h}); page.add_init_script(INIT)
    logs = []; page.on("pageerror", lambda e: logs.append(str(e)[:200]))
    for name, hsh in (("home", "#/en/"), ("blog", "#/en/blog"), ("article", "#/en/blog/commencer")):
        page.goto(f"http://127.0.0.1:{port}/index.html{hsh}", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(2.4)
        print(name, json.dumps(page.evaluate(STATE), ensure_ascii=False))
        print(name, "french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
        page.screenshot(path=f"{out}/en-{name}.png", full_page=(name != "home"))
    # the switch, from the English blog to French and back
    page.goto(f"http://127.0.0.1:{port}/index.html#/en/blog", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(2)
    page.click(".hdr [data-lang=fr]"); page.wait_for_load_state("networkidle"); time.sleep(2.4)
    print("switch → FR", json.dumps(page.evaluate(STATE), ensure_ascii=False), page.evaluate("document.querySelector('#h-blog').textContent"))
    page.click(".hdr [data-lang=en]"); page.wait_for_load_state("networkidle"); time.sleep(2.4)
    print("switch → EN", json.dumps(page.evaluate(STATE), ensure_ascii=False), page.evaluate("document.querySelector('#h-blog').textContent"))
    # the run, in English
    page.goto(f"http://127.0.0.1:{port}/index.html#/en/", wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(2.4)
    for y in range(0, 6000, 90): page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.03)
    time.sleep(2)
    bb = page.query_selector("#hero-node").bounding_box()
    page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up(); page.mouse.move(w * .97, h * .5)
    time.sleep(12); page.screenshot(path=f"{out}/en-run-stop1.png")
    print("stop1 french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
    page.keyboard.press("End"); time.sleep(7); page.screenshot(path=f"{out}/en-run-stop2.png")
    print("stop2 french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
    for _ in range(4):
        if 'voy' in page.evaluate(SEG)["segs"]: break
        page.keyboard.press("End"); time.sleep(3)
    st = page.evaluate(SEG); vo = st["segs"]["voy"]
    page.mouse.wheel(0, -(st["want"] - (vo[0] + 220))); time.sleep(4)
    print("road words:", json.dumps(page.evaluate("[...document.querySelectorAll('.vword')].map(e => e.textContent.replace(/\\u00a0/g, ' '))"), ensure_ascii=False))
    for k in range(8): page.mouse.wheel(0, 150); time.sleep(.9)
    page.screenshot(path=f"{out}/en-run-road.png")
    st = page.evaluate(SEG); page.mouse.wheel(0, (vo[0] + vo[1]) - st["want"] + 2); time.sleep(5)
    page.screenshot(path=f"{out}/en-run-scene.png")
    print("scene:", page.evaluate("(document.querySelector('.story-hero') || {}).innerText"))
    print("scene french left:", json.dumps(page.evaluate(SCAN), ensure_ascii=False))
    for _ in range(6):
        st = page.evaluate(SEG)
        if 'sky' in st["segs"]: break
        page.keyboard.press("End"); time.sleep(2)
    st = page.evaluate(SEG); sk = st["segs"].get("sky")
    if sk: page.mouse.wheel(0, sk[0] + 8.95 * h - st["want"]); time.sleep(6); page.screenshot(path=f"{out}/en-run-stars.png")
    print("errors:", logs[:5]); b.close()
httpd.shutdown()

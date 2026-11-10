"""v81 probe: the phone menu. Opens it (French), shoots it, lists its rows and links with their heights; the language row
switches to the English page; opens it there and shoots it. Takes `<demo folder> <port> <out dir> [WxH]`."""
import sys, threading, functools, http.server, socketserver, time, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
folder, port, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = map(int, (sys.argv[4] if len(sys.argv) > 4 else '390x844').split('x'))
os.makedirs(out, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
srv = S(("127.0.0.1", port), functools.partial(Q, directory=folder)); threading.Thread(target=srv.serve_forever, daemon=True).start()
errors = []
LIST = "[...document.querySelectorAll('#menu .menu-row, #menu .menu-legal a, #menu .menu-legal button')].map(a => a.textContent.trim() + (a.getAttribute('href') ? ' → ' + a.getAttribute('href') : '') + ' [' + Math.round(a.getBoundingClientRect().height) + 'px]')"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx.add_init_script("try { localStorage.setItem('nur-consent', JSON.stringify({ ok: false, t: Date.now() })); } catch (e) {}")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)[:200]))
    pg.goto(f"http://127.0.0.1:{port}/index.html#/", wait_until="networkidle"); time.sleep(2.2)
    pg.click('#menu-btn'); time.sleep(1); pg.screenshot(path=f"{out}/menu-fr.png"); print('fr:', pg.evaluate(LIST))
    pg.click('#menu-lang'); pg.wait_for_load_state("networkidle"); time.sleep(2.4)
    print('after the language row:', pg.evaluate("[location.hash, document.documentElement.lang]"))
    pg.click('#menu-btn'); time.sleep(1); pg.screenshot(path=f"{out}/menu-en.png"); print('en:', pg.evaluate(LIST))
    print('errors:', errors[:4]); b.close()
srv.shutdown()

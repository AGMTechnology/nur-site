"""v82 probe: Google Analytics waits for consent. On the built site, in a fresh browser: no request leaves the site
before an answer; « Refuser » sends none either; « Accepter » loads gtag.js with the property's ID; reopening and
refusing switches GA off (ga-disable) and removes its cookies. Takes `<site folder> <port>`."""
import sys, threading, functools, http.server, socketserver, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
folder, port = sys.argv[1], int(sys.argv[2])
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
srv = S(("127.0.0.1", port), functools.partial(Q, directory=folder)); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{port}"; out = []; errors = []
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 1280, "height": 800})
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)[:160]))
    pg.on("request", lambda r: out.append(r.url.split('?')[0][:80] + ('?' + r.url.split('?')[1][:30] if '?' in r.url else '')) if not r.url.startswith(B) and not r.url.startswith('data:') else None)
    pg.goto(B + "/", wait_until="networkidle"); time.sleep(2)
    print('before any answer, outside requests:', out); n0 = len(out)
    pg.click('.consent [data-c=no]'); pg.goto(B + "/blog/", wait_until="networkidle"); time.sleep(1.5)
    print('after Refuser, outside requests:', out[n0:]); n1 = len(out)
    pg.evaluate("localStorage.removeItem('nur-consent')"); pg.reload(wait_until="networkidle"); time.sleep(1.5)
    pg.click('.consent [data-c=yes]'); time.sleep(4)
    print('after Accepter:', sorted(set(out[n1:]))[:6], '| gtag:', pg.evaluate("typeof window.gtag"))
    pg.click('.foot [data-consent]'); time.sleep(.5)
    with pg.expect_navigation(timeout=10000): pg.click('.consent [data-c=no]')
    time.sleep(1.5)
    print('after reopening and Refuser:', pg.evaluate("[localStorage.getItem('nur-consent'), document.cookie.split(';').filter(c => /_ga/.test(c)).length]"))
    print('errors:', errors[:4]); b.close()
srv.shutdown()

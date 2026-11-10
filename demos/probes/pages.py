"""v80 probe: the five pieces. In a fresh browser (nothing stored): the cookie banner shows; « Refuser » closes it and is
kept (a reload shows no banner); « Gérer les cookies » opens it again; « Accepter » is kept and loads nothing while
GA_ID is empty. The hero's badges carry « Bientôt disponible » and a tap says so. À propos opens from the bottom line,
with the badges; a link inside goes to the privacy policy; the switch on it lands on the English page; the legal
notice shows its placeholders; no demo tag; no page errors. On a phone: the banner, the menu's legal line, a page.
Takes `<demo or site folder> <port> <out dir> <WxH>`."""
import sys, threading, functools, http.server, socketserver, time, json, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
folder, port, out, size = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
w, h = map(int, size.split('x')); phone = w < 1024
os.makedirs(out, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
srv = S(("127.0.0.1", port), functools.partial(Q, directory=folder)); threading.Thread(target=srv.serve_forever, daemon=True).start()
SITE = os.path.exists(os.path.join(folder, 'blog', 'index.html'))
B = f"http://127.0.0.1:{port}" + ('' if SITE else '/index.html')
at = lambda p: B + (p if SITE else '#' + p.rstrip('/').replace('#', '') if p != '/' else '#/')
errors = []
def state(pg): return pg.evaluate("""[location.pathname + location.hash, document.body.dataset.route, (document.querySelector('#h-doc')||{}).textContent, document.title,
  !!document.querySelector('.consent'), localStorage.getItem('nur-consent'), typeof window.gtag, !!document.getElementById('demo-tag')]""")
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if phone else 1, is_mobile=phone, has_touch=phone)
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)[:200]))
    pg.goto(at('/'), wait_until="networkidle"); time.sleep(2.5)
    print('first visit:', state(pg)); pg.screenshot(path=f"{out}/1-banner.png")
    pg.click('.consent [data-c=no]'); time.sleep(.4); print('refused:', state(pg))
    pg.reload(wait_until="networkidle"); time.sleep(2); print('reloaded:', state(pg))
    print('soon pill:', pg.evaluate("[...document.querySelectorAll('.hero-copy .soon')].map(e => e.textContent)"), '| links:', pg.evaluate("[...document.querySelectorAll('.hero-copy .store-link')].map(a => [a.getAttribute('aria-disabled'), a.getAttribute('aria-label')])"))
    pg.click('.hero-copy .store-link', force=True); time.sleep(.5); print('badge tap toast:', pg.evaluate("document.getElementById('toast').textContent"), '|', state(pg)[0])
    if phone:
        pg.click('#menu-btn'); time.sleep(1); pg.screenshot(path=f"{out}/2-menu.png")
        print('menu legal:', pg.evaluate("[...document.querySelectorAll('.menu-legal a, .menu-legal button')].map(a => a.textContent + ' → ' + (a.getAttribute('href') || 'button'))"))
        pg.click('.menu-legal [data-consent]'); time.sleep(.6)
    else:
        print('home line:', pg.evaluate("[...document.querySelectorAll('.hero-foot .hero-legal a, .hero-foot .hero-legal button')].map(a => a.textContent + ' → ' + (a.getAttribute('href') || 'button'))"))
        pg.click('.hero-foot [data-consent]'); time.sleep(.6)
    print('reopened:', state(pg)); pg.screenshot(path=f"{out}/3-reopened.png")
    pg.click('.consent [data-c=yes]'); time.sleep(.4); print('accepted:', state(pg))
    pg.goto(at('/a-propos/'), wait_until="networkidle"); time.sleep(2.2)
    print('about:', state(pg), '| stores in page:', pg.evaluate("[...document.querySelectorAll('#doc-prose .soon')].length"), '| FAQ h2:', pg.evaluate("document.querySelectorAll('#doc-prose h2').length"))
    pg.screenshot(path=f"{out}/4-about.png", full_page=False)
    pg.click('#doc-prose a[data-doc=privacy]'); time.sleep(2.6)
    print('privacy:', state(pg), '| english link:', pg.evaluate("(document.querySelector('#doc-prose a[data-doc-lang=en]')||{}).href"), '| tables:', pg.evaluate("document.querySelectorAll('#doc-prose table').length"))
    pg.screenshot(path=f"{out}/5-privacy.png")
    pg.click('.hdr [data-lang=en]' if not phone else '.foot [data-lang=en]'); pg.wait_for_load_state("networkidle"); time.sleep(2.4)
    print('switch → EN:', state(pg))
    pg.goto(at('/mentions-legales/'), wait_until="networkidle"); time.sleep(2.2)
    print('legal notice:', state(pg)[1:4], '| placeholders:', pg.evaluate("[...document.querySelectorAll('#doc-prose mark.todo')].map(m => m.textContent)"))
    pg.screenshot(path=f"{out}/6-legal.png")
    print('errors:', errors[:5]); b.close()
srv.shutdown()

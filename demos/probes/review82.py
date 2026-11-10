"""v82 probe: the code review's fixes, on the built site at a phone's size. The article app box's « Sur l'App Store… »
line has no pill; the phone menu's rows touch their dividers; « Gérer les cookies » from the menu puts the focus in the
banner and a choice gives it back; the Juz ʿAmma table keeps its roles and its headers for screen readers; with the
banner up, the player rises above it. Takes `<site folder> <port> <out dir> [WxH]`."""
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
B = f"http://127.0.0.1:{port}"; errors = []; outside = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx.add_init_script("try { localStorage.setItem('nur-consent', JSON.stringify({ ok: false, t: Date.now() })); } catch (e) {}")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)[:200]))
    pg.on("request", lambda r: outside.append(r.url[:90]) if not r.url.startswith(B) and not r.url.startswith('data:') else None)
    pg.goto(B + "/blog/lire-le-coran-debutant/", wait_until="networkidle"); time.sleep(2)
    print('app box line:', pg.evaluate("(() => { const e = document.querySelector('.appcard .soon'); if (!e) return null; const c = getComputedStyle(e); return [e.textContent, c.backgroundColor, c.boxShadow.slice(0, 20), c.color]; })()"))
    pg.click('#menu-btn'); time.sleep(.9)
    print('menu rows:', pg.evaluate("(() => { const r = [...document.querySelectorAll('#menu .menu-row')].map(e => e.getBoundingClientRect()); return [Math.round(r[0].bottom), Math.round(r[1].top), getComputedStyle(document.querySelector('#menu ul')).rowGap]; })()"))
    pg.click('#menu [data-consent]'); time.sleep(.5)
    print('focus after « Gérer les cookies »:', pg.evaluate("[document.activeElement.textContent, !!document.activeElement.closest('.consent'), document.body.firstElementChild.className]"))
    pg.evaluate("document.querySelector('.consent [data-c=no]').click()"); time.sleep(.4)
    print('focus after the choice:', pg.evaluate("[document.activeElement.tagName, document.activeElement.id || document.activeElement.className]"))
    pg.goto(B + "/blog/juz-amma-liste-des-sourates/", wait_until="networkidle"); time.sleep(2)
    print('table:', pg.evaluate("(() => { const t = document.querySelector('#prose table'); const th = t.querySelector('thead'); return [t.getAttribute('role'), t.querySelector('tr').getAttribute('role'), t.querySelector('td').getAttribute('role'), getComputedStyle(th).display, th.getBoundingClientRect().width]; })()"))
    pg.evaluate("localStorage.removeItem('nur-consent')"); pg.reload(wait_until="networkidle"); time.sleep(2)
    pg.evaluate("document.querySelector('[data-sound]') && document.querySelector('[data-sound]').click()")
    pg.goto(B + "/blog/lire-le-coran-debutant/", wait_until="networkidle"); time.sleep(2)
    pg.evaluate("localStorage.removeItem('nur-consent')"); pg.reload(wait_until="networkidle"); time.sleep(2)
    pg.evaluate("document.querySelector('#prose [data-sound], #prose .lsn-tile, #prose button.w') && (document.querySelector('#prose [data-sound]') || document.querySelector('#prose button.w')).click()"); time.sleep(1.2)
    print('player vs banner:', pg.evaluate("(() => { const pl = document.getElementById('player'), c = document.querySelector('.consent'); return [pl.hidden, Math.round(pl.getBoundingClientRect().bottom), c ? Math.round(c.getBoundingClientRect().top) : null]; })()"))
    pg.screenshot(path=f"{out}/player-banner.png")
    print('requests outside the site:', sorted(set(outside))[:6])
    print('errors:', errors[:4]); b.close()
srv.shutdown()

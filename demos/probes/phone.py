"""v77 probe: the phone audit (Ahmed, 2026-11-09: "Walk the website in phone format and audit the problems"). An emulated
phone (touch, mobile viewport, 2x pixels) walks the site as a visitor would: the hero, the home scrolled to its node,
the menu, the run from the node's tap to its end, the blog, every article. At each screen it shoots a frame and
measures, on what is on the screen:
  cut        text running past the screen's left or right edge
  overlap    two pieces of text from different elements covering each other (more than 15 % of the smaller)
  small      text under 12 px (body under 16 px is listed under 'body' when a run of 40+ characters)
  target     a link or button under 44 x 44 px (a link inside a sentence is left out: WCAG's inline exception)
  hscroll    the page wider than the screen
  clipped    text cut by an ancestor that hides its overflow
Decorative text (inside aria-hidden, e.g. the app screens drawn in the hero) is listed apart, under 'decor'.
Takes `<demo folder> <port> <out dir> <WxH> <lang fr|en> <parts: hero,menu,run,blog,articles>`."""
import sys, threading, functools, http.server, socketserver, time, json, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
folder, port, out, size, lang = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
parts = sys.argv[6].split(',') if len(sys.argv) > 6 else ['hero', 'menu', 'run', 'blog', 'articles']
w, h = map(int, size.split('x'))
os.makedirs(out, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".html": "text/html; charset=utf-8"}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
srv = S(("127.0.0.1", port), functools.partial(Q, directory=folder)); threading.Thread(target=srv.serve_forever, daemon=True).start()
# the built site (site_build.py: real paths and its <meta name=viewport>) or the demo (# addresses, no viewport tag)
SITE = os.path.exists(os.path.join(folder, 'blog', 'index.html'))
PFX = ('/en' if lang == 'en' else '') if SITE else ('#/en' if lang == 'en' else '#')
URL = f"http://127.0.0.1:{port}" + ('' if SITE else '/index.html')
def at(r, slug=''): return PFX + ({'home': '/', 'blog': '/blog/', 'art': f'/blog/{slug}/'} if SITE else {'home': '/', 'blog': '/blog', 'art': f'/blog/{slug}'})[r]
INIT = "document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='[hidden]{display:none!important}';document.head.prepend(s);});"
AUDIT = r"""(() => {
  const W = innerWidth, H = innerHeight, o = { cut: [], overlap: [], small: [], body: [], target: [], clipped: [], decor: [], hscroll: 0 };
  const sw = document.documentElement.scrollWidth; if (sw > W + 1) o.hscroll = sw;
  const seen = e => { for (let p = e; p && p !== document.documentElement; p = p.parentElement) { const c = getComputedStyle(p);
    if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity < .06) return false; } return true; };
  const T = [], tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = tw.nextNode());) {
    const v = n.nodeValue.replace(/\s+/g, ' ').trim(); if (!v) continue;
    const e = n.parentElement; if (!e || e.closest('script, style, noscript')) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const R = [...r.getClientRects()].filter(q => q.width > .5 && q.height > .5); if (!R.length) continue;
    const b = { l: Math.min(...R.map(q => q.left)), t: Math.min(...R.map(q => q.top)), r: Math.max(...R.map(q => q.right)), b: Math.max(...R.map(q => q.bottom)) };
    if (b.b <= 0 || b.t >= H) continue;
    if (!seen(e)) continue;
    const cs = getComputedStyle(e), fs = parseFloat(cs.fontSize), decor = !!e.closest('[aria-hidden="true"]');
    const t = v.slice(0, 48);
    if (decor) { if (fs < 12) o.decor.push([t, fs]); continue; }
    T.push({ txt: t, e, ...b });
    if (fs < 12) o.small.push([t, fs]); else if (v.length >= 40 && fs < 16) o.body.push([t, fs]);
    if (b.l < -1 || b.r > W + 1) o.cut.push([t, Math.round(b.l), Math.round(b.r)]);
    for (let p = e; p && p !== document.body; p = p.parentElement) {
      const c = getComputedStyle(p); if (c.overflow === 'visible' && c.overflowX === 'visible' && c.overflowY === 'visible') continue;
      if (c.overflowX === 'auto' || c.overflowX === 'scroll') break;
      const q = p.getBoundingClientRect();
      if (b.l < q.left - 1 || b.r > q.right + 1 || b.t < q.top - 1 || b.b > q.bottom + 1) { o.clipped.push([t, p.className.toString().slice(0, 30) || p.tagName]); break; }
    }
  }
  for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
    const a = T[i], c = T[j]; if (a.e === c.e || a.e.contains(c.e) || c.e.contains(a.e)) continue;
    const ix = Math.min(a.r, c.r) - Math.max(a.l, c.l), iy = Math.min(a.b, c.b) - Math.max(a.t, c.t); if (ix <= 1 || iy <= 1) continue;
    const sm = Math.min((a.r - a.l) * (a.b - a.t), (c.r - c.l) * (c.b - c.t)) || 1;
    if (ix * iy / sm > .15) o.overlap.push([a.txt, c.txt, +(ix * iy / sm).toFixed(2)]);
  }
  document.querySelectorAll('a[href], button, [role="button"], input, select, summary, [tabindex="0"]').forEach(e => {
    if (!seen(e) || e.closest('[aria-hidden="true"]')) return; const q = e.getBoundingClientRect();
    if (!q.width || q.bottom <= 0 || q.top >= H) return;
    if (e.tagName === 'A' && e.closest('p, li, td') && !e.closest('nav, .crumbs, .chips')) return;
    if (q.width < 43.5 || q.height < 43.5) o.target.push([(e.getAttribute('aria-label') || e.textContent || e.tagName).replace(/\s+/g, ' ').trim().slice(0, 34), Math.round(q.width), Math.round(q.height)]);
  });
  return o; })()"""
SEG = """(() => { if (!window.__press || !__press.active()) return null; const s = __press.state(); let o = 0, r = {};
  for (const [id, len] of s.segs) { r[id] = [o, len]; o += len; } return { v: s.v, total: o, segs: r }; })()"""
report = {}
def shot(page, name, audit=True, pic=True):
    if pic: page.screenshot(path=f"{out}/{name}.png")
    if audit:
        a = page.evaluate(AUDIT); a = {k: v for k, v in a.items() if v}
        report[name] = a
        if a: print(name, json.dumps(a, ensure_ascii=False)[:900])
def fresh(b, hash_):
    page = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page.add_init_script(INIT); page.on("pageerror", lambda e: errors.append(str(e)[:200]))
    page.goto(URL + hash_, wait_until="networkidle"); page.reload(wait_until="networkidle"); time.sleep(2.6)
    print('   layout width', page.evaluate('innerWidth'), 'at', hash_)
    return page
def walk(page, tag, step=.8, limit=40):
    y, k = 0, 0
    while k < limit:
        shot(page, f"{tag}-{k:02d}")
        H = page.evaluate("document.documentElement.scrollHeight"); y += int(h * step)
        if y >= H - h + int(h * step): break
        page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.9); k += 1
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    if 'hero' in parts or 'menu' in parts or 'run' in parts:
        page = fresh(b, at('home'))
        shot(page, 'a-hero')
        if 'menu' in parts:
            page.click('#menu-btn'); time.sleep(1.2); shot(page, 'b-menu'); page.click('#menu-btn'); time.sleep(1)
        if 'hero' in parts or 'run' in parts:
            for k, y in enumerate(range(int(h * .5), 6000, int(h * .5))):   # the home, down to its node
                page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.6)
                shot(page, f"c-home-{k:02d}")
                if page.evaluate("scrollY + innerHeight >= document.documentElement.scrollHeight - 2"): break
        if 'run' in parts:
            bb = page.query_selector("#hero-node").bounding_box()
            page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); time.sleep(.1); page.mouse.up()
            for k in range(6): time.sleep(2); shot(page, f"d-intro-{k}")
            k, last = 0, -1
            while k < 160:
                page.mouse.wheel(0, h * .45); time.sleep(.7)
                s = page.evaluate(SEG)
                if not s: shot(page, f"e-run-{k:03d}-after"); break
                if k % 2 == 0: shot(page, f"e-run-{k:03d}-" + next((i for i, (o, l) in s['segs'].items() if o <= s['v'] < o + l), 'end'))
                k += 1
            time.sleep(4); shot(page, 'f-after-loop')
        page.close()
    if 'arrive' in parts:   # (v78) the start button's entrance, frame by frame
        page = fresh(b, at('home'))
        y = page.evaluate("document.getElementById('start').getBoundingClientRect().top + scrollY - innerHeight * .74")
        page.evaluate(f"window.scrollTo(0, {y})")
        for k in range(10): time.sleep(.15); shot(page, f"i-arrive-{k}", audit=False)
        time.sleep(1.2); shot(page, 'i-arrive-end')
        page.close()
    if 'push' in parts:   # (v79) entering the phone, a few px at a time: scroll, whether the page's node has taken over, the phone's transform, the badge
        page = fresh(b, at('home'))
        end = page.evaluate("document.documentElement.scrollHeight - innerHeight")
        for k, y in enumerate(range(0, int(end) + 61, 60)):
            page.evaluate(f"window.scrollTo(0, {y})"); time.sleep(.4)
            st = page.evaluate("[Math.round(scrollY), document.getElementById('journey').classList.contains('landed'), getComputedStyle(document.getElementById('orbit-anchor')).transform.slice(0, 48), document.getElementById('start-badge').className, getComputedStyle(document.getElementById('phone-dock')).position]")
            print('   push', k, st)
            if k % 2 == 0: shot(page, f"j-push-{k:02d}", audit=False)
        time.sleep(1.2); shot(page, 'j-push-end')
        page.close()
    if 'blog' in parts:
        page = fresh(b, at('blog')); walk(page, 'g-blog'); page.close()
    if 'articles' in parts:
        page = fresh(b, at('blog'))
        slugs = page.evaluate("[...document.querySelectorAll('[data-link=article][data-slug]')].map(a => a.dataset.slug).filter((v, i, s) => s.indexOf(v) === i)")
        page.close()
        for i, sl in enumerate(slugs):
            page = fresh(b, at('art', sl)); walk(page, f"h-art{i}-{sl[:14]}"); page.close()
    b.close()
json.dump({'size': size, 'lang': lang, 'errors': errors, 'screens': report}, open(f"{out}/report.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('screens', len(report), 'with findings', sum(1 for v in report.values() if v), '| page errors', errors[:4])
srv.shutdown()

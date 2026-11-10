"""v75 probe: the site as a crawler or an AI assistant sees it, with no JavaScript. Serves nur-257/site, reads
robots.txt, sitemap.xml and llms.txt, then fetches every page in the sitemap as plain HTML and checks: status, <title>,
description, canonical (its own address), hreflang (fr, en, x-default), JSON-LD (parses; its types), the H1, the words
readable without the script, internal links that lead nowhere, and French left on English pages.
No browser. Takes `<site folder> <port>`."""
import sys, threading, functools, http.server, socketserver, urllib.request, re, json, html
sys.stdout.reconfigure(encoding='utf-8')
folder, port = sys.argv[1], int(sys.argv[2])
class Q(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml'}
    def log_message(self, *a): pass
class S(socketserver.TCPServer): allow_reuse_address = True
srv = S(('127.0.0.1', port), functools.partial(Q, directory=folder)); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{port}'
ORIGIN = 'https://getnurapp.com'
get = lambda p: urllib.request.urlopen(BASE + p, timeout=20)
def text(p): r = get(p); return r.status, r.read().decode('utf-8')

st, robots = text('/robots.txt'); print('robots.txt', st, '| agents:', re.findall(r'User-agent: (\S+)', robots), '| sitemap line:', 'Sitemap:' in robots)
st, sm = text('/sitemap.xml'); locs = re.findall(r'<loc>([^<]+)</loc>', sm); print('sitemap.xml', st, len(locs), 'urls, alternates:', sm.count('xhtml:link'))
st, llms = text('/llms.txt'); print('llms.txt', st, len(llms.split()), 'words,', llms.count('](' + ORIGIN), 'links')
st, full = text('/llms-full.txt'); print('llms-full.txt', st, len(full.split()), 'words')
FR = re.compile(r'[éèêàâçùûôîœ«»]|\b(le|la|les|des|du|une|et|ton|ta|tes|pour|avec|dans|sur|est|pas|qui|que|tu)\b', re.I)
dead, seen = set(), set()
for u in locs:
    p = u.replace(ORIGIN, '')
    st, h = text(p)
    head = h[:h.index('</head>')]
    title = re.search(r'<title>(.*?)</title>', head).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', head).group(1)
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', head).group(1)
    hl = re.findall(r'hreflang="([^"]+)"', head)
    types = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S):
        g = json.loads(m.group(1)); types += [x['@type'] for x in g.get('@graph', [g])]
    body = h[h.index('<body>'):]
    vis = re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<svg\b.*?</svg>', ' ', body, flags=re.S)
    # what a crawler reads as this page's own content: the shown page only (data-page without hidden)
    shown = re.search(r'<div class="page" data-page="(\w+)">(.*?)(?=<div class="page" data-page=|</main>)', vis, flags=re.S)
    words = html.unescape(re.sub(r'<[^>]+>', ' ', shown.group(2))).split() if shown else []
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', shown.group(2), flags=re.S) if shown else None
    h1t = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else None
    for href in re.findall(r'href="(/[^"#]*)"', vis):
        if href in seen: continue
        seen.add(href)
        try: get(href if not href.endswith('/') else href + 'index.html')
        except Exception: dead.add(href)
    fr_left = []
    if p.startswith('/en/') and shown:
        for t in re.findall(r'>([^<>]+)<', shown.group(2)):
            t = html.unescape(t).strip()
            if len(t) > 2 and FR.search(t) and not re.search(r'[؀-ۿ]', t): fr_left.append(t[:60])
    print(f'{p}\n   {st} | {title} ({len(title)}) | desc {len(desc)} | canonical ok: {canon == u} | hreflang {hl} | JSON-LD {types}\n   shown: {shown.group(1) if shown else None} | H1: {h1t} | words without JS: {len(words)}' + (f' | French left: {fr_left[:4]}' if fr_left else ''))
print('dead internal links:', sorted(dead) or 'none')
srv.shutdown()

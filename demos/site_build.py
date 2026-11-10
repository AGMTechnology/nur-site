"""Build Nūr's website as static files that search engines and AI assistants can read (v75, Ahmed 2026-11-09).
One HTML file per page at a real address, its words already in the HTML, French and English:
  /  /blog/  /blog/<slug>/   and   /en/  /en/blog/  /en/blog/<slug>/
plus robots.txt, sitemap.xml, llms.txt, llms-full.txt and the assets. Every page is the validated demo itself
(option-d/index.html) in its static mode (<html data-static="1">): it looks and moves the same; the build only fills in
what the script would draw (the blog's cards, an article's text), translates the static words for /en/, and adds the
head a crawler reads (title, description, canonical, hreflang, Open Graph, JSON-LD).
Usage: python site_build.py   →   nur-257/site/"""
import html, io, json, os, re, shutil, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'option-d', 'index.html')
OUT = os.path.join(HERE, '..', 'site')
ORIGIN = 'https://getnurapp.com'   # Ahmed, 2026-11-09: the main domain; getnurapp.fr redirects here
TODAY = datetime.date.today().isoformat()
GO_LIVE = '2026-11-10'   # (v82) the day the site goes live, 'YYYY-MM-DD': every article's datePublished (Ahmed validated all eight, 2026-11-10)

src = io.open(SRC, encoding='utf-8').read()
cut = src.index('<svg width="0" height="0"')
head_src = src[:cut]
head_src = head_src[head_src.index('<script>'):]          # drop the demo's own <title> and description
body_src = src[cut:]

def between(s, a, b):
    i = s.index(a) + len(a); return s[i:s.index(b, i)]
EN_TEXT = json.loads(between(src, 'const EN_TEXT = ', ';\n'))
EN_HTML = json.loads(between(src, 'const EN_HTML = ', ';\n'))
ARTICLES = json.loads(between(src, '/*ARTICLES*/', '/*/ARTICLES*/'))
DOCS = json.loads(between(src, '/*DOCS*/', '/*/DOCS*/'))   # (v80) À propos and the legal pages (docs_build.py)
CATS = {'tout': ('Tout', 'All'), 'lire': ('Lire', 'Read'), 'memoriser': ('Mémoriser', 'Memorise'), 'histoires': ('Histoires', 'Stories'), 'manieres': ('Bonnes manières', 'Good manners')}
DEF = {'fr': 'Nūr t’apprend l’islam à partir du Coran : le lire, le mémoriser, écouter ses histoires et pratiquer les bonnes manières au quotidien.',
       'en': 'Nūr teaches you Islam through the Quran: read it, memorise it, listen to its stories, and put good manners into practice every day.'}
HOME_TITLE = {'fr': 'Lire le Coran et mémoriser les sourates avec Nūr', 'en': 'Read the Quran and Memorise Surahs with Nūr'}
BLOG_TITLE = {'fr': 'Le blog · Nūr', 'en': 'The blog · Nūr'}
BLOG_DESC = {'fr': 'Des articles pour lire, mémoriser et comprendre le Coran.', 'en': 'Articles to help you read, memorise and understand the Quran.'}
TEAM = {'fr': 'L’équipe Nūr', 'en': 'The Nūr team'}
MIN = {'fr': 'min de lecture', 'en': 'min read'}
L = lambda lang, fr, en: fr if lang == 'fr' else en
esc = lambda t: html.escape(t, quote=True)
fold = lambda t: re.sub(r'[\s  ]+', ' ', t).strip()

def path(lang, route, slug=None):
    p = '/en' if lang == 'en' else ''
    return p + ('/' if route == 'home' else '/blog/' if route == 'blog' else f'/{slug}/' if route == 'doc' else f'/blog/{slug}/')

def doclinks(s, lang):
    """(v80) every link to one of the site's own pages gets its real address (in its data-doc-lang, else the page's)"""
    ds = {d['id']: d for d in DOCS}
    def one(m):
        attrs = re.sub(r'\s*href="[^"]*"', '', m.group(1))
        d = ds.get(re.search(r'data-doc="(\w+)"', attrs).group(1)); lg = (re.search(r'data-doc-lang="(\w+)"', attrs) or [None, lang])[1]
        return f'<a href="{path(lg, "doc", d[lg]["slug"])}"{attrs}>' if d else m.group(0)
    return re.sub(r'<a\b((?:(?!>)[^>])*\bdata-doc="\w+"[^>]*)>', one, s)

def outside_scripts(s, fn):
    """apply fn to the markup only, never inside <script> or <style>"""
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', s, flags=re.S)
    return ''.join(x if (x.startswith('<script') or x.startswith('<style')) else fn(x) for x in parts)

def to_english(s):
    def text(m):
        raw = m.group(1); k = fold(html.unescape(raw))
        if k in EN_TEXT:
            lead = re.match(r'^\s*', raw).group(0); trail = re.search(r'\s*$', raw).group(0)
            return '>' + lead + esc(EN_TEXT[k]).replace('&#x27;', '’') + trail + '<'
        return m.group(0)
    def attr(m):
        k = fold(html.unescape(m.group(2)))
        return f'{m.group(1)}="{esc(EN_TEXT[k])}"' if k in EN_TEXT else m.group(0)
    s = re.sub(r'>([^<>]+)<', text, s)
    s = re.sub(r'\b(aria-label|alt)="([^"]*)"', attr, s)
    s = re.sub(r'(<h1 class="display hero-title" id="h-home" tabindex="-1">).*?(</h1>)', lambda m: m.group(1) + EN_HTML['#h-home'] + m.group(2), s, flags=re.S)
    s = s.replace('assets/badges/app-store-fr.svg" width="152"', 'assets/badges/app-store-en.svg" width="144"')
    s = s.replace('assets/badges/google-play-fr.png" width="162"', 'assets/badges/google-play-en.png" width="161"')
    return s

def card(a, lang, kind=None):
    T = a[lang]; c = L(lang, *CATS[a['cat']])
    if a.get('img'):
        thumb = f'<span class="thumb"><img src="/assets/img/{a["img"]}.webp" alt="{esc(a["alt"][lang])}" width="600" height="1067" loading="lazy" style="object-position:{a.get("pos", "50% 40%")}"></span>'
    else:
        thumb = f'<span class="thumb{" thumb--gold" if a.get("gold") else ""}"><span class="typo" lang="ar" dir="rtl" aria-hidden="true">{a["typo"]}</span></span>'
    return (f'<a class="card{" card--" + kind if kind else ""}" href="{path(lang, "article", T["slug"])}" data-link="article" data-slug="{T["slug"]}">{thumb}'
            f'<span class="card-b"><span class="kicker">{c}</span><h3>{T["title"]}</h3><span class="card-ex">{T["ex"]}</span><span class="meta"><span>{a["min"]} {MIN[lang]}</span></span></span></a>')

def fill(s, open_tag, inner):
    """put inner into the element that opens with open_tag (its first closing tag of the same name ends it)"""
    i = s.index(open_tag) + len(open_tag); name = re.match(r'<(\w+)', open_tag).group(1)
    j = s.index(f'</{name}>', i)
    return s[:i] + inner + s[j:]

def plain(h):
    return fold(html.unescape(re.sub(r'<[^>]+>', ' ', h)))

def faq(body):
    """the article's question headings and the words that answer them (FAQPage), when there are two or more"""
    out = []
    for m in re.finditer(r'<h2>(.*?)</h2>(.*?)(?=<h2>|$)', body, flags=re.S):
        q = plain(m.group(1))
        if not q.endswith('?'): continue
        ans = plain(re.sub(r'<!--.*?-->|<table.*?</table>', ' ', m.group(2), flags=re.S))
        if len(ans) > 600: ans = ans[:600].rsplit('. ', 1)[0] + '.'
        if ans: out.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': ans}})
    return out if len(out) >= 2 else []

ORG = {'@type': 'Organization', '@id': ORIGIN + '/#org', 'name': 'Nūr', 'url': ORIGIN + '/', 'logo': ORIGIN + '/assets/nur-icon.webp'}
PUB = {'@type': 'Person', '@id': ORIGIN + '/#publisher', 'name': 'Ahmed Agoummadane', 'url': ORIGIN + '/mentions-legales/'}   # (v82) the publisher, Ahmed as a person (2026-11-10)
SITE = {'@type': 'WebSite', '@id': ORIGIN + '/#site', 'name': 'Nūr', 'url': ORIGIN + '/', 'inLanguage': ['fr', 'en'], 'publisher': {'@id': ORIGIN + '/#publisher'}}

def page(lang, route, a=None):
    me = path(lang, route, a[lang]['slug'] if a else None)
    alt = {lg: path(lg, route, a[lg]['slug'] if a else None) for lg in ('fr', 'en')}
    if route == 'home': title, desc, img, kind = HOME_TITLE[lang], DEF[lang], '/assets/img/kawthar-p2.webp', 'website'
    elif route == 'blog': title, desc, img, kind = BLOG_TITLE[lang], BLOG_DESC[lang], '/assets/img/kawthar-p2.webp', 'website'
    elif route == 'doc': title, desc, img, kind = a[lang]['metaTitle'], a[lang]['metaDesc'], '/assets/nur-icon.webp', 'website'
    else: title, desc, img, kind = a[lang]['metaTitle'], a[lang]['metaDesc'], ('/assets/img/' + a['img'] + '.webp' if a.get('img') else '/assets/nur-icon.webp'), 'article'
    graph = [ORG, PUB, SITE]
    if route == 'home':
        graph.append({'@type': 'MobileApplication', 'name': 'Nūr', 'url': ORIGIN + me, 'description': DEF[lang], 'operatingSystem': 'iOS, Android',
                      'applicationCategory': 'EducationalApplication', 'inLanguage': ['fr', 'en'], 'image': ORIGIN + '/assets/nur-icon.webp', 'publisher': {'@id': ORIGIN + '/#publisher'}})
    elif route == 'blog':
        graph.append({'@type': 'Blog', 'name': BLOG_TITLE[lang], 'url': ORIGIN + me, 'description': BLOG_DESC[lang], 'inLanguage': lang, 'publisher': {'@id': ORIGIN + '/#publisher'},
                      'blogPost': [{'@type': 'BlogPosting', 'headline': plain(x[lang]['title']), 'url': ORIGIN + path(lang, 'article', x[lang]['slug'])} for x in ARTICLES]})
    elif route == 'doc':   # (v80) À propos: an AboutPage with its questions (FAQPage); the legal pages: WebPage
        T = a[lang]
        graph.append({'@type': 'AboutPage' if a['id'] == 'about' else 'WebPage', 'name': T['title'], 'url': ORIGIN + me, 'description': T['metaDesc'],
                      'inLanguage': lang, 'isPartOf': {'@id': ORIGIN + '/#site'}, 'publisher': {'@id': ORIGIN + '/#publisher'}})
        q = faq(T['body']) if a['id'] == 'about' else []
        if q: graph.append({'@type': 'FAQPage', 'mainEntity': q})
    else:
        T = a[lang]; words = len(plain(T['body']).split())
        graph.append({'@type': 'BlogPosting', 'headline': plain(T['title']), 'description': T['metaDesc'], 'inLanguage': lang, 'url': ORIGIN + me,
                      'mainEntityOfPage': ORIGIN + me, 'image': ORIGIN + img, 'wordCount': words, **({'datePublished': GO_LIVE, 'dateModified': GO_LIVE} if GO_LIVE else {}), 'articleSection': L(lang, *CATS[a['cat']]),
                      'author': {'@type': 'Organization', 'name': TEAM[lang], 'url': ORIGIN + '/'}, 'publisher': {'@id': ORIGIN + '/#publisher'},
                      'isPartOf': {'@type': 'Blog', 'name': BLOG_TITLE[lang], 'url': ORIGIN + path(lang, 'blog')}})
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Blog', 'item': ORIGIN + path(lang, 'blog')},
            {'@type': 'ListItem', 'position': 2, 'name': plain(T['title']), 'item': ORIGIN + me}]})
        q = faq(T['body'])
        if q: graph.append({'@type': 'FAQPage', 'mainEntity': q})
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/')
    head = (f'<!doctype html>\n<html lang="{lang}" data-static="1">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<title>{esc(title)}</title>\n<meta name="description" content="{esc(desc)}">\n'
            f'<link rel="canonical" href="{ORIGIN}{me}">\n'
            f'<link rel="alternate" hreflang="fr" href="{ORIGIN}{alt["fr"]}">\n<link rel="alternate" hreflang="en" href="{ORIGIN}{alt["en"]}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{alt["fr"]}">\n'
            f'<meta property="og:type" content="{kind}">\n<meta property="og:site_name" content="Nūr">\n<meta property="og:title" content="{esc(title)}">\n'
            f'<meta property="og:description" content="{esc(desc)}">\n<meta property="og:url" content="{ORIGIN}{me}">\n<meta property="og:image" content="{ORIGIN}{img}">\n'
            f'<meta property="og:locale" content="{L(lang, "fr_FR", "en_GB")}">\n<meta property="og:locale:alternate" content="{L(lang, "en_GB", "fr_FR")}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<link rel="icon" href="/assets/nur-icon.webp">\n'
            f'<link rel="sitemap" type="application/xml" href="/sitemap.xml">\n'
            f'<script type="application/ld+json">{ld}</script>\n')
    body = body_src
    if lang == 'en': body = outside_scripts(body, to_english)
    # real links for crawlers (the script still catches every click and keeps the green veil)
    body = outside_scripts(body, lambda s: s.replace('href="#/blog"', f'href="{path(lang, "blog")}"').replace('href="#/"', f'href="{path(lang, "home")}"'))
    # which page shows (the script's swap() does the same on load)
    body = body.replace('<div class="page" data-page="home">', '<div class="page" data-page="home"' + (' hidden' if route != 'home' else '') + '>')
    body = body.replace('<div class="page" data-page="blog" hidden>', '<div class="page" data-page="blog"' + (' hidden' if route != 'blog' else '') + '>')
    body = body.replace('<div class="page" data-page="article" hidden>', '<div class="page" data-page="article"' + (' hidden' if route != 'article' else '') + '>')
    body = body.replace('<div class="page" data-page="doc" hidden>', '<div class="page" data-page="doc"' + (' hidden' if route != 'doc' else '') + '>')
    if route == 'doc':   # (v80) the page, as the script draws it
        T = a[lang]
        body = fill(body, '<h1 class="display" id="h-doc" tabindex="-1">', esc(T['title']))
        body = fill(body, '<p class="art-meta" id="doc-meta">', f'<span>{esc(T["meta"])}</span>' if T.get('meta') else '')
        stores = re.search(r'<div class="stores" id="telecharger"[^>]*>(.*?)</div>', body, flags=re.S).group(1)
        prose = T['body'].replace('<table', '<div class="tbl"><table').replace('</table>', '</table></div>').replace('<!--BADGES-->', f'<div class="stores doc-stores">{stores}</div>')
        body = fill(body, '<article class="prose" id="doc-prose" data-rise>', prose)
    body = outside_scripts(body, lambda x: doclinks(x, lang))
    if route == 'blog':   # the cards, as the script draws them
        lead, *side = ARTICLES[:3]
        body = fill(body, '<div class="new-grid" id="new-grid">', card(lead, lang, 'lead') + '<div class="new-side">' + ''.join(card(x, lang, 'row') for x in side) + '</div>')
        chips = [k for k in CATS if k == 'tout' or any(x['cat'] == k for x in ARTICLES)]
        body = fill(body, '<div class="chips" id="chips" role="group" aria-label="' + L(lang, 'Catégories', 'Categories') + '">',
                    ''.join(f'<button class="chip" type="button" data-cat-k="{k}" aria-pressed="{str(k == "tout").lower()}">{L(lang, *CATS[k])}</button>' for k in chips))
        body = fill(body, '<div class="grid" id="all-grid" aria-live="polite">', ''.join(card(x, lang) for x in ARTICLES[3:]))
    if route == 'article':   # the article, as the script draws it
        T = a[lang]; c = L(lang, *CATS[a['cat']])
        body = fill(body, '<nav class="crumbs" aria-label="' + L(lang, 'Fil d’Ariane', 'Breadcrumb') + '" data-rise>\n    <ol>',
                    f'<li><a href="{path(lang, "blog")}" data-link="blog">Blog</a></li><li class="sep" aria-hidden="true">›</li><li><a href="{path(lang, "blog")}" data-link="blog" data-cat="{a["cat"]}">{c}</a></li>')
        body = fill(body, '<h1 class="display" id="h-article" tabindex="-1">', T['title'])
        body = fill(body, '<p class="art-meta" id="art-meta">', f'<span>{a["min"]} {MIN[lang]}</span><span>{TEAM[lang]}</span>')
        fig = (f'<img src="/assets/img/{a["img"]}.webp" alt="{esc(a["alt"][lang])}" width="800" height="1422" style="object-position:{a.get("pos", "50% 40%")}">' if a.get('img')
               else f'<span class="thumb{" thumb--gold" if a.get("gold") else ""}"><span class="typo" lang="ar" dir="rtl" aria-hidden="true">{a["typo"]}</span></span>')
        body = fill(body, '<figure class="art-img" id="art-img">', fig)
        prose = T['body'].replace('<table', '<div class="tbl"><table').replace('</table>', '</table></div>')
        ids = {x['id']: x[lang]['slug'] for x in ARTICLES}   # links between articles: their real address
        prose = re.sub(r'href="#/blog/([^"]+)" data-art="([^"]+)"', lambda m: f'href="{path(lang, "article", ids.get(m.group(2), m.group(2)))}" data-art="{m.group(2)}"', prose)
        body = fill(body, '<article class="prose" id="prose" data-rise>', prose)
        rest = [x for x in ARTICLES if x['id'] != a['id']]
        rel = ([x for x in rest if x['cat'] == a['cat']] + [x for x in rest if x['cat'] != a['cat']])[:3]
        body = fill(body, '<div class="grid" id="related">', ''.join(card(x, lang) for x in rel))
    doc = head + head_src + '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    doc = self_host(doc)
    # every asset from the site's root, whatever the page's depth
    doc = re.sub(r'(?<=["\'`(])assets/', '/assets/', doc)
    f = os.path.join(OUT, me.strip('/').replace('/', os.sep), 'index.html')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    io.open(f, 'w', encoding='utf-8', newline='\n').write(doc)
    return me, alt

VENDOR = {'https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js': '/assets/vendor/js/gsap.min.js',
          'https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js': '/assets/vendor/js/ScrollTrigger.min.js',
          'https://cdn.jsdelivr.net/npm/lenis@1.3.27/dist/lenis.min.js': '/assets/vendor/js/lenis.min.js',
          'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js': '/assets/vendor/js/three.module.min.js',
          'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Nunito:wght@600;700;800;900&display=swap': '/assets/vendor/fonts/fonts.css'}
def self_host(doc):
    """(v82, code review) the libraries and fonts from the site itself (vendor_fetch.py): nothing leaves for a third party
    before the cookie banner is answered, and no CDN can change what runs"""
    for a, b in VENDOR.items():
        assert a in doc or a.startswith('https://fonts'), a; doc = doc.replace(a, b)
    doc = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n?', '', doc)
    left = re.findall(r'https://(?:cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com)[^"\'\s)]*', doc)
    assert not left, left
    return doc

def md(h):
    """an article body as Markdown, for llms-full.txt"""
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    def table(m):
        rows = re.findall(r'<tr>(.*?)</tr>', m.group(0), flags=re.S)
        cells = [[plain(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, flags=re.S)] for r in rows]
        if not cells: return ''
        out = ['| ' + ' | '.join(cells[0]) + ' |', '|' + '---|' * len(cells[0])] + ['| ' + ' | '.join(r) + ' |' for r in cells[1:]]
        return '\n\n' + '\n'.join(out) + '\n\n'
    h = re.sub(r'<table.*?</table>', table, h, flags=re.S)
    h = re.sub(r'<h2>(.*?)</h2>', lambda m: '\n\n## ' + plain(m.group(1)) + '\n\n', h, flags=re.S)
    h = re.sub(r'<li>(.*?)</li>', lambda m: '\n- ' + plain(m.group(1)), h, flags=re.S)
    h = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n\n> ' + plain(m.group(1)) + '\n\n', h, flags=re.S)
    h = re.sub(r'<a [^>]*data-art="([^"]+)"[^>]*>(.*?)</a>', lambda m: m.group(2), h, flags=re.S)
    h = re.sub(r'<strong>(.*?)</strong>', r'**\1**', h, flags=re.S)
    h = re.sub(r'</p>', '\n\n', h); h = re.sub(r'<[^>]+>', '', h)
    return re.sub(r'\n{3,}', '\n\n', html.unescape(h)).strip()

# ---- build
if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
urls = []
for lang in ('fr', 'en'):
    urls.append(page(lang, 'home')); urls.append(page(lang, 'blog'))
    for a in ARTICLES: urls.append(page(lang, 'article', a))
    for d in DOCS: urls.append(page(lang, 'doc', d))
shutil.copytree(os.path.join(HERE, 'option-d', 'assets'), os.path.join(OUT, 'assets'))
shutil.copytree(os.path.join(HERE, 'vendor'), os.path.join(OUT, 'assets', 'vendor'))   # (v82) vendor_fetch.py
# (v82, code review) GitHub Pages: the custom domain survives every build, and an unknown address gets the home page
io.open(os.path.join(OUT, 'CNAME'), 'w', encoding='utf-8', newline='\n').write(ORIGIN.split('//', 1)[1] + '\n')
shutil.copyfile(os.path.join(OUT, 'index.html'), os.path.join(OUT, '404.html'))
io.open(os.path.join(OUT, '.nojekyll'), 'w').write('')   # (v82) GitHub Pages serves the files as they are, no Jekyll pass
INDEXNOW = '99f35bf5a1b32fd5ce7c79ebb44ab429'   # (v82) IndexNow (Bing and others): the key file at the root proves the site is ours; indexnow_ping.py uses it
io.open(os.path.join(OUT, INDEXNOW + '.txt'), 'w', encoding='utf-8').write(INDEXNOW)

io.open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(f"""# Nūr's website: every page is public. Search engines and AI assistants are welcome to read it.
User-agent: *
Allow: /

# AI assistants and their crawlers, named so the intent is explicit
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: GPTBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: ClaudeBot
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: Applebot-Extended
Allow: /

Sitemap: {ORIGIN}/sitemap.xml
""")
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for me, alt in urls:
    sm.append(f'  <url><loc>{ORIGIN}{me}</loc><lastmod>{TODAY}</lastmod>'
              f'<xhtml:link rel="alternate" hreflang="fr" href="{ORIGIN}{alt["fr"]}"/><xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}{alt["en"]}"/>'
              f'<xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}{alt["fr"]}"/></url>')
sm.append('</urlset>')
io.open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sm) + '\n')

# llms.txt: what Nūr is, in plain words, with every page (the facts are WHAT-NUR-IS.md's and legal-claims.md's)
arts_en = '\n'.join(f'- [{plain(a["en"]["title"])}]({ORIGIN}{path("en", "article", a["en"]["slug"])}): {a["en"]["metaDesc"]}' for a in ARTICLES)
arts_fr = '\n'.join(f'- [{plain(a["fr"]["title"])}]({ORIGIN}{path("fr", "article", a["fr"]["slug"])}): {a["fr"]["metaDesc"]}' for a in ARTICLES)
docs_lines = '\n'.join(f'- [{d[lg]["title"]} ({"English" if lg == "en" else "French"})]({ORIGIN}{path(lg, "doc", d[lg]["slug"])}): {d[lg]["metaDesc"]}' for d in DOCS for lg in ('en', 'fr'))
io.open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write(f"""# Nūr

> {DEF['en']}

Nūr is a mobile app for iOS and Android, in French and English. Its French line: « {DEF['fr']} »

## What Nūr teaches
- **Reading the Quran**, starting from the first Arabic letter: the letters, joined letters, the vowel marks, then the page of the Quran itself. At the end of the reading part, a learner reads al-Fātiḥah and al-Ikhlāṣ from the page, unaided.
- **Memorising the Quran**, surah by surah: al-Fātiḥah, then Juzʾ ʿAmma, then on through the Quran. Each passage is heard recited by Shaykh Maḥmūd Khalīl al-Ḥuṣarī, read along, read alone, then recited from memory; the app listens and shows which word to say again. A spaced revision brings back what the learner knows.
- **Stories** of the prophets and companions, and the stories behind surahs, told aloud on illustrated pages, from the Quran and reports graded authentic.
- **Good manners**: everyday situations and the words of the sunnah (for example, what to say when someone sneezes).

## Who it is for
Adults and teenagers (the store audience is 13+): someone who cannot read an Arabic letter yet, someone who reads and wants to memorise, and someone who wants the stories and manners. A household can share one account with several learners.

## What Nūr does not teach (at launch)
The Arabic language (vocabulary and grammar), tajwīd, fiqh (rulings) and creed. Nūr makes no claim of review by scholars.

## Price
A subscription: yearly with a 7-day free trial, or monthly with no trial. The price is shown on the App Store and Google Play, for each country.

## Who makes Nūr
Ahmed, as a private individual. The legal notice gives the details.

## Privacy
When the app listens to a recitation, it does so on the phone; recordings never leave it. Nūr shows no advertising and carries no advertising tracker.

## Pages
- [Home (French)]({ORIGIN}/): Moins de scroll. Plus de Coran.
- [Home (English)]({ORIGIN}/en/): Less scrolling. More Quran.
- [Blog (French)]({ORIGIN}/blog/)
- [Blog (English)]({ORIGIN}/en/blog/)
{docs_lines}

## Articles (English)
{arts_en}

## Articles (French)
{arts_fr}

## Optional
- [Every article in full, as Markdown]({ORIGIN}/llms-full.txt)
""")
full = ['# Nūr: the About page and the blog, in full', '', f'> {DEF["en"]}', '']
about = next(d for d in DOCS if d['id'] == 'about')
for lang in ('en', 'fr'):
    full += ['', '---', '', f'# {about[lang]["title"]}', '', f'URL: {ORIGIN}{path(lang, "doc", about[lang]["slug"])}', f'Language: {lang}', '', md(about[lang]['body'])]
for lang in ('en', 'fr'):
    for a in ARTICLES:
        T = a[lang]
        full += ['', '---', '', f'# {plain(T["title"])}', '', f'URL: {ORIGIN}{path(lang, "article", T["slug"])}', f'Language: {lang}', '', md(T['body'])]
io.open(os.path.join(OUT, 'llms-full.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(full) + '\n')

print('pages:', len(urls))
for me, _ in urls: print('  ', me)
tot = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
print('site size:', round(tot / 1e6, 1), 'MB →', os.path.abspath(OUT))

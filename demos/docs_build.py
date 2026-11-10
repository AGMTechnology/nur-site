"""v80 (Ahmed, 2026-11-10: "Bypass Figma, these are simple feature to implement, go do the five pieces"): the site's
own pages besides the blog, in French and English, written into option-d/index.html between /*DOCS*/ markers:
  about    À propos / About            nur-257/pages/about.json
  legal    Mentions légales / Legal notice    nur-257/pages/legal.json
  privacy  Politique de confidentialité / Privacy Policy   the published Markdown (nur-docs content/fr/legal-pages),
           plus the website's own section (nur-257/pages/privacy-site.json)
  terms    Conditions d'utilisation / Terms of Service   the published Markdown
The legal Markdown is turned into HTML here (headings, paragraphs, lists, tables, bold, italics, links). Its front
matter, title, tagline and closing navigation line are left out; its « last updated » line becomes the page's meta.
Links between the documents become data-doc links (the page sets their address). Usage: python docs_build.py"""
import html, io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, 'option-d', 'index.html')
PAGES = os.path.join(HERE, '..', 'pages')
LEGAL = os.path.join(PAGES, 'legal-src')   # (v82) the site's own copy of the legal texts (the site is their home since decision 3;
                                           # copied from nur-docs content/fr/legal-pages at t/257 16c8595, publisher Ahmed)
DOCLINK = {'privacy-policy': ('privacy', 'en'), '../privacy-policy': ('privacy', 'en'), 'politique-de-confidentialite': ('privacy', 'fr'),
           'fr/politique-de-confidentialite': ('privacy', 'fr'), 'terms-of-service': ('terms', 'en'), '../terms-of-service': ('terms', 'en'),
           'conditions-d-utilisation': ('terms', 'fr'), 'fr/conditions-d-utilisation': ('terms', 'fr')}

def inline(t):
    t = html.escape(t, quote=False)
    def link(m):
        txt, url = m.group(1), m.group(2)
        if url in DOCLINK: d, l = DOCLINK[url]; return f'<a data-doc="{d}" data-doc-lang="{l}">{txt}</a>'
        if url.startswith(('mailto:', 'http')): return f'<a href="{html.escape(url, quote=True)}"' + ('' if url.startswith('mailto:') else ' rel="noopener"') + f'>{txt}</a>'
        return f'<a data-link="home">{txt}</a>'
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def md(path):
    src = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    if src.startswith('---\n'): src = src[src.index('\n---\n', 4) + 5:]
    lines, out, title, meta, i = src.split('\n'), [], '', '', 0
    para = []
    def flush():
        nonlocal para
        if para:
            t = ' '.join(x.strip() for x in para)
            only_links = re.fullmatch(r'(\s*\[[^\]]+\]\([^)]+\)\s*·?\s*)+', t)
            if not only_links: out.append(f'<p>{inline(t)}</p>')
            para = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('# '): flush(); title = ln[2:].strip(); i += 1; continue
        if ln.startswith('### '): flush(); out.append(f'<h3>{inline(ln[4:].strip())}</h3>'); i += 1; continue
        if ln.startswith('## '): flush(); out.append(f'<h2>{inline(ln[3:].strip())}</h2>'); i += 1; continue
        if ln.strip() == '---': flush(); i += 1; continue
        if ln.startswith('|'):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i += 1
            cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
            head, body = cells[0], [r for r in cells[2:]]
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table>')
            continue
        if ln.startswith('- '):
            flush(); items = []
            while i < len(lines) and lines[i].startswith('- '):
                item = lines[i][2:]; i += 1
                while i < len(lines) and lines[i].startswith('  ') and lines[i].strip(): item += ' ' + lines[i].strip(); i += 1
                items.append(item)
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); continue
        if not ln.strip(): flush(); i += 1; continue
        # the lines right under the title: the tagline (left out) and the « last updated » line (the page's meta)
        if not out and not para and re.match(r'^\*\*?[^*]+\*\*?$', ln.strip()):
            t = ln.strip().strip('*')
            if re.search(r'mise à jour|updated', t, re.I): meta = t
            i += 1; continue
        para.append(ln); i += 1
    flush()
    return title, meta, ''.join(out)

docs = []
for f in ('about', 'legal'):
    docs.append(json.load(io.open(os.path.join(PAGES, f + '.json'), encoding='utf-8')))
site = json.load(io.open(os.path.join(PAGES, 'privacy-site.json'), encoding='utf-8'))
SRC = {'privacy': {'fr': ('fr/politique-de-confidentialite.md', 'confidentialite'), 'en': ('en/privacy-policy.md', 'privacy')},
       'terms': {'fr': ('fr/conditions-d-utilisation.md', 'conditions'), 'en': ('en/terms-of-service.md', 'terms')}}
DESC = {'privacy': {'fr': 'Nūr fonctionne sans compte, tes enregistrements ne quittent pas ton téléphone et tu peux tout effacer. Ce que Nūr traite, en détail, et tes droits.',
                    'en': 'Nūr works without an account, your recordings never leave your phone, and you can delete everything. What Nūr handles, in detail, and your rights.'},
        'terms': {'fr': 'Les conditions d’utilisation de l’appli Nūr : le compte, l’abonnement, tes enregistrements, et ce que chacun s’engage à faire.',
                  'en': 'The terms of use of the Nūr app: the account, the subscription, your recordings, and what each side agrees to do.'}}
for d in ('privacy', 'terms'):
    e = {'id': d}
    for lang in ('fr', 'en'):
        path, slug = SRC[d][lang]
        title, meta, body = md(os.path.join(LEGAL, path))
        if d == 'privacy': body += site[lang]
        e[lang] = {'slug': slug, 'title': title, 'metaTitle': f'{title} · Nūr', 'metaDesc': DESC[d][lang], 'meta': meta, 'body': body}
    docs.append(e)
for e in docs:
    for lang in ('fr', 'en'):
        L = e[lang]; L.setdefault('meta', '')
        n = len(re.sub(r'<[^>]+>', ' ', L['body']).split())
        print(f"{e['id']:8} {lang} /{L['slug']}  {n} words  title « {L['title']} »  meta « {L['meta']} »  desc {len(L['metaDesc'])}")
        bad = re.search(r'<script|<iframe|<object|<embed|style=|\son\w+\s*=|javascript:', L['body'] + L['title'] + L.get('meta', ''), re.I)
        if bad: sys.exit(f"{e['id']} {lang}: forbidden markup « {bad.group(0)} »: nothing written")   # (v82) the build fails
s = io.open(PAGE, encoding='utf-8').read()
a, b = s.index('/*DOCS*/') + len('/*DOCS*/'), s.index('/*/DOCS*/')
data = json.dumps(docs, ensure_ascii=False).replace('<!--', '\\u003c!--').replace('</', '<\\/')
s = s[:a] + data + s[b:]
io.open(PAGE, 'w', encoding='utf-8', newline='').write(s)
print('written:', len(docs), 'pages')

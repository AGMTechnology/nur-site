"""Write the blog's articles into the demo (v74). Reads nur-257/blog/<id>.json (one per article, French and English),
adds each one's picture or letter cover, checks what a machine can check of PLAYBOOK-MARKETING-WORDS §7, and writes
`const ARTICLES = /*ARTICLES*/[...]/*/ARTICLES*/` into option-d/index.html. Usage: python blog_build.py [--check]"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.join(HERE, '..', 'blog')
PAGE = os.path.join(HERE, 'option-d', 'index.html')

# newest first: the research's rank (SEO-BLOG-KEYWORDS-257 §4); the first three lead the blog
ORDER = ['apprendre-sourate', 'juz-amma', 'alphabet-arabe', 'lire-le-coran-debutant', 'memoriser-sans-oublier', 'sourate-al-fil', 'prophete-youssouf', 'eternuer-islam']
# pictures: Nūr's own art only (the app's story pages and situation scenes); a letter cover where none fits.
# Arabic covers are copied from the app's data (quran-text.json 78:1, surah-meta.json 105)
LOOK = {
  'apprendre-sourate': {'img': 'kawthar-p2', 'pos': '50% 50%', 'alt': {'fr': 'Des hommes assis ensemble sous un toit de palmes, à l’ombre.', 'en': 'Men sitting together in the shade of a palm-leaf roof.'}},
  'juz-amma': {'typo': 'عَمَّ يَتَسَآءَلُونَ', 'gold': True},
  'alphabet-arabe': {'typo': 'ا ب ت ث'},
  'lire-le-coran-debutant': {'img': 'salam-p7', 'pos': '50% 38%', 'aliases': ['commencer'],
    'alt': {'fr': 'Un homme, vu de dos sur une colline, regarde des chemins qui serpentent entre des collines vertes.', 'en': 'A man seen from behind on a hill looks at paths winding between green hills.'}},
  'memoriser-sans-oublier': {'img': 'nas-p6', 'pos': '50% 46%', 'alt': {'fr': 'Une femme au foulard jaune, calme, dans une pièce le soir.', 'en': 'A calm woman in a yellow headscarf, in a room in the evening.'}},
  'sourate-al-fil': {'typo': 'سُوْرَةُ الْفِيْلِ', 'gold': True},
  'prophete-youssouf': {'img': 'yusuf-p2', 'pos': '50% 22%', 'alt': {'fr': 'Un père assis avec ses fils devant des tentes, et un jeune garçon près de lui.', 'en': 'A father sitting with his sons by the tents, a young boy beside him.'}},
  'eternuer-islam': {'img': 'sit-salam', 'pos': '50% 50%', 'alt': {'fr': 'Une famille réunie dans un salon, autour d’un thé.', 'en': 'A family gathered in a living room over tea.'}},
}
CATS = {'lire', 'memoriser', 'histoires', 'manieres'}
BANNED = [r'\bmeilleur', r'\bbest\b', r'découvr', r'\bpour enfants\b', r'\bfor kids\b', r'\btélécharge', r'\bdownload now\b', r'\bn°\s*1\b', r'#1\b']
FLAG = [r'tajw[iī]d', r'\bprière\b', r'\bprayer\b', r'ṣalāh|salat\b', r'apprendre l.arabe', r'learn arabic', r'bienfaits', r'Zulaykha', r'Binyām', r'Abrah']

def text_of(html): return re.sub(r'<[^>]+>', ' ', html)

def check(a):
    out = []
    for k in ('id', 'cat', 'min', 'fr', 'en'):
        if k not in a: out.append(f'missing {k}')
    if a.get('cat') not in CATS: out.append(f"cat '{a.get('cat')}' is not one of {sorted(CATS)}")
    for lang in ('fr', 'en'):
        L = a.get(lang, {})
        for k in ('slug', 'title', 'metaTitle', 'metaDesc', 'ex', 'body'):
            if not L.get(k): out.append(f'{lang}: missing {k}')
        mt, md, ex = len(L.get('metaTitle', '')), len(L.get('metaDesc', '')), len(L.get('ex', ''))
        if not 30 <= mt <= 62: out.append(f'{lang}: page title {mt} characters')
        if not 110 <= md <= 165: out.append(f'{lang}: description {md} characters')
        if ex > 125: out.append(f'{lang}: card excerpt {ex} characters')
        body = L.get('body', '')
        if re.search(r'<script|<img|<iframe|<object|<embed|style=|\son\w+\s*=|javascript:', body + L.get('title', '') + L.get('ex', '') + L.get('metaDesc', ''), re.I): out.append(f'{lang}: FORBIDDEN markup')
        if not body.lstrip().startswith('<p class="art-lead">'): out.append(f'{lang}: body does not open on the lead')
        t = text_of(' '.join([L.get('title', ''), L.get('metaDesc', ''), L.get('ex', ''), body]))
        for d in re.finditer(r'.{0,20}[—–].{0,20}', t):
            if not re.search(r'\d\s*[—–]\s*\d', d.group(0)): out.append(f'{lang}: dash « {d.group(0).strip()} »')
        for b in BANNED:
            for m in re.finditer(b, t, re.I): out.append(f"{lang}: banned « {t[max(0, m.start() - 30):m.end() + 30].strip()} »")
        for f in FLAG:
            for m in re.finditer(f, t, re.I): out.append(f"{lang}: to read « {t[max(0, m.start() - 40):m.end() + 40].strip()} »")
        for m in re.finditer(r'data-art="([^"]+)"', body):
            if m.group(1) not in ORDER: out.append(f'{lang}: link to unknown article {m.group(1)}')
        words = len(text_of(body).split())
        out.append(f'(info) {lang}: {words} words, title {mt}, description {md}')
    return out

arts, notes = [], {}
for i in ORDER:
    f = os.path.join(BLOG, i + '.json')
    if not os.path.exists(f): print('MISSING', i); continue
    a = json.load(io.open(f, encoding='utf-8'))
    a.pop('notes', None); a.pop('imgIdea', None); src = a.pop('sources', [])
    a.update(LOOK.get(i, {}))
    issues = check(a)
    print(f'== {i} ({a.get("cat")}, {a.get("min")} min, {len(src)} sources)')
    for x in issues: print('   ', x)
    arts.append(a)
if any('FORBIDDEN' in x for a in arts for x in check(a)): sys.exit('forbidden markup in an article: nothing written')   # (v82) the build fails
if '--check' in sys.argv: sys.exit(0)
s = io.open(PAGE, encoding='utf-8').read()
a0, a1 = s.index('/*ARTICLES*/') + len('/*ARTICLES*/'), s.index('/*/ARTICLES*/')
# (inside a <script>: no « </ » and no « <!-- » in the raw text; the escapes read back the same in JavaScript)
s = s[:a0] + json.dumps(arts, ensure_ascii=False).replace('<!--', '\\u003c!--').replace('</', '<\\/') + s[a1:]
io.open(PAGE, 'w', encoding='utf-8', newline='').write(s)
print('written:', len(arts), 'articles')

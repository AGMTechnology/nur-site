"""v76 guard for the English rewrite (Ahmed, 2026-11-09: "everything ... go"). Compares an article's JSON with its copy
taken before the rewrite (blog/_before-en/<id>.json) and fails on anything the rewrite must not touch: the French, the
slug, the titles, the sources and notes; in the English body, every tag and marker (same tags, same order, same
attributes), the verse meanings (<span class="sens">), the quoted words (“…”), every Arabic run, every number, the
question headings (still questions). Also prints the word count change (±12 % allowed) and the contractions.
Usage: python en_guard.py <id> [<id> …]   (all articles when none is given)"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.join(HERE, '..', 'blog')
AR = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿][؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿\s]*')
text = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()
def parts(b):
    return {
        'tags and markers': re.findall(r'<[^>]+>', b),
        'verse meanings': re.findall(r'<span class="sens"[^>]*>.*?</span>', b, flags=re.S),
        'quoted words': re.findall(r'“[^”]*”', b),
        'Arabic': [a.strip() for a in AR.findall(b) if a.strip()],
        'numbers': sorted(re.findall(r'\d+', text(b))),
        'question headings': [h.strip().endswith('?') for h in re.findall(r'<h2[^>]*>(.*?)</h2>', b, flags=re.S)],
    }
ids = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(BLOG) if f.endswith('.json'))
bad = 0
for i in ids:
    old = json.load(io.open(os.path.join(BLOG, '_before-en', i + '.json'), encoding='utf-8'))
    new = json.load(io.open(os.path.join(BLOG, i + '.json'), encoding='utf-8'))
    out = []
    for k in old:
        if k != 'en' and old[k] != new.get(k): out.append(f'{k} changed')
    for k in ('slug', 'title', 'metaTitle'):
        if old['en'][k] != new['en'][k]: out.append(f'en.{k} changed')
    P, Q = parts(old['en']['body']), parts(new['en']['body'])
    for k in P:
        if P[k] != Q[k]:
            a = [x for x in P[k] if x not in Q[k]][:3]; b = [x for x in Q[k] if x not in P[k]][:3]
            out.append(f'{k} differ: before {a} | after {b}' if (a or b) else f'{k} differ (order or count)')
    w0, w1 = len(text(old['en']['body']).split()), len(text(new['en']['body']).split())
    if abs(w1 - w0) > 0.12 * w0: out.append(f'word count {w0} -> {w1} (more than 12 %)')
    c0 = len(re.findall(r"\b\w+['’](?:t|ve|re|m|ll|d|s)\b", text(old['en']['body'])))
    c1 = len(re.findall(r"\b\w+['’](?:t|ve|re|m|ll|d|s)\b", text(new['en']['body'])))
    print(f'{i}: {"OK" if not out else "FAIL"} | words {w0} -> {w1} | contractions {c0} -> {c1} | description {len(new["en"]["metaDesc"])} | excerpt {len(new["en"]["ex"])}')
    for o in out: print('   ', o)
    bad += bool(out)
sys.exit(1 if bad else 0)

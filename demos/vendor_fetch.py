"""v82 (code review, finding 3): the built site serves its own copies of the libraries and fonts, so no request leaves
for a third party before the visitor has answered the cookie banner (Google Fonts, jsDelivr), and nothing runs from a
CDN that could change under it. Downloads once into demos/vendor/: the four scripts the page loads from jsDelivr, and
Google Fonts' CSS for Amiri and Nunito (woff2, every subset) with its font files, the CSS rewritten to
/assets/vendor/fonts/. site_build.py copies vendor/ to /assets/vendor/ and points the page at it. The demo artifact keeps
the CDN (claude.ai serves it in a frame). Usage: python vendor_fetch.py"""
import os, re, sys, urllib.request, hashlib
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(HERE, 'vendor')
JS = ['https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js', 'https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js',
      'https://cdn.jsdelivr.net/npm/lenis@1.3.27/dist/lenis.min.js', 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js']
FONTS = 'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Nunito:wght@600;700;800;900&display=swap'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
os.makedirs(os.path.join(V, 'js'), exist_ok=True); os.makedirs(os.path.join(V, 'fonts'), exist_ok=True)
for u in JS:
    b = get(u); open(os.path.join(V, 'js', u.rsplit('/', 1)[1]), 'wb').write(b); print(len(b), u.rsplit('/', 1)[1])
css = get(FONTS).decode('utf-8'); n = 0
def font(m):
    global n
    u = m.group(1); name = hashlib.sha1(u.encode()).hexdigest()[:12] + '.woff2'
    open(os.path.join(V, 'fonts', name), 'wb').write(get(u)); n += 1
    return f'url(/assets/vendor/fonts/{name})'
css = re.sub(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', font, css)
open(os.path.join(V, 'fonts', 'fonts.css'), 'w', encoding='utf-8').write('/* Amiri and Nunito, from Google Fonts (SIL Open Font License 1.1), served by the site itself */\n' + css)
print(n, 'font files, fonts.css', len(css), 'bytes')

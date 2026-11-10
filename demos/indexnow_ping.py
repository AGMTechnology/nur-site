"""v82 (decision 4: an IndexNow ping when the site or an article is published): tells Bing (and every IndexNow engine)
which addresses are new or changed. Reads the key from site_build.py and the addresses from the built sitemap; the key
file must already be live at https://getnurapp.com/<key>.txt. Usage: python indexnow_ping.py [path …] (all pages when
none is given, e.g. /blog/<slug>/ and /en/blog/<slug>/ for a new article)"""
import json, os, re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'site_build.py'), encoding='utf-8').read()
key = re.search(r"^INDEXNOW = '([0-9a-f]+)'", src, re.M).group(1)
origin = re.search(r"^ORIGIN = '([^']+)'", src, re.M).group(1)
host = origin.split('//', 1)[1]
urls = [origin + p for p in sys.argv[1:]] or re.findall(r'<loc>([^<]+)</loc>', open(os.path.join(HERE, '..', 'site', 'sitemap.xml'), encoding='utf-8').read())
body = json.dumps({'host': host, 'key': key, 'keyLocation': f'{origin}/{key}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    r = urllib.request.urlopen(req, timeout=30); print('IndexNow:', r.status, len(urls), 'addresses')
except urllib.error.HTTPError as e:
    print('IndexNow:', e.code, e.read()[:200]); sys.exit(1)

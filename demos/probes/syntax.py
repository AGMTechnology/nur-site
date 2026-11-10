"""Extract demo D's inline script and let node check its syntax."""
import re, subprocess
from pathlib import Path
s = Path(r'C:\Users\ahmed\tools\lanes\notes\nur-257\demos\option-d\index.html').read_text(encoding='utf-8')
scripts = re.findall(r'<script>(.*?)</script>', s, flags=re.S)
out = Path(__file__).with_name('_inline.js')
out.write_text(max(scripts, key=len), encoding='utf-8')
r = subprocess.run(['node', '--check', str(out)], capture_output=True, text=True, encoding='utf-8')
print(r.returncode, r.stderr[:1500])

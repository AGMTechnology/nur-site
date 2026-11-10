"""Contact sheets: sheets.py <frames dir> <cols> <rows> <cell width>; each frame labelled with its file name."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
d = Path(__file__).resolve().parent / sys.argv[1]
cols, rows, cw = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
fs = sorted(p for p in d.glob('*.png') if not p.name.startswith('sheet'))
im0 = Image.open(fs[0]); ch = round(cw * im0.height / im0.width)
n = cols * rows
for k in range(0, len(fs), n):
    sh = Image.new('RGB', (cols * cw + (cols + 1) * 6, rows * ch + (rows + 1) * 6), (40, 40, 40))
    for i, f in enumerate(fs[k:k + n]):
        t = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
        x, y = 6 + (i % cols) * (cw + 6), 6 + (i // cols) * (ch + 6)
        sh.paste(t, (x, y)); dr = ImageDraw.Draw(sh); dr.rectangle([x, y, x + 64, y + 16], fill=(0, 0, 0)); dr.text((x + 4, y + 3), f.stem, fill=(255, 255, 0))
    sh.save(d / f'sheet{k // n:02d}.png')
print(len(fs), 'frames,', (len(fs) + n - 1) // n, 'sheets')

import math, numpy as np
from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy()
R.paste_c(im, R.earth(820), W / 2, H + 420)
# shower of faint streaks + one hero meteor
rg = np.random.default_rng(5)
for i in range(14):
    a = rg.uniform(0.5, 2.6); dist = rg.uniform(200, 700)
    hx = R.RAD[0] + math.cos(a) * dist; hy = 700 + math.sin(a) * dist * 0.8
    R.streak(im, hx, hy, a, rg.uniform(120, 260), 4, 0.6, head=False)
R.streak(im, 400, 1180, math.atan2(560, -560), 700, 22, 1.0, col=(255, 225, 180), head=False)
R.grain(im, 400, 1180, 70, 1.0, hot=1.0)
yy = np.arange(H); g = np.clip(1 - (yy - 560) / 220, 0, 1)
mask = Image.fromarray(np.repeat((g * 200).astype(np.uint8)[:, None], W, 1), 'L'); im.paste((0, 0, 0), (0, 0), mask)
d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(185, 'A GRAIN OF SAND', 106, WHITE)
t(370, '71 KM/S', 250, GOLD)
t(560, 'WHAT HAPPENS?', 120, CYAN)
R.pill(d, W / 2, 1780, 'LEONIDS · PEAK ≈ NOV 17', 58, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

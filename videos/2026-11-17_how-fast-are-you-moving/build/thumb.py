from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy()
R.streaks(im, 0.3, 0.8)
R.paste_c(im, R.glow(560, (90, 140, 255), 1.6), 540, 1950, 0.7)
R.paste_c(im, R.earth_rot(520, 0.4), 540, 2020, 1.0)
R.paste_c(im, R.glow(500, (255, 170, 60), 1.5), 540, 1000, 0.5)
R.gauge(im, 540, 1000, 330, 0.97, '1.3M', 'km/h', 1.0)
d = ImageDraw.Draw(im, 'RGBA')
import numpy as np
gr = np.zeros((600, W, 4), np.uint8); gr[..., 3] = (np.linspace(200, 0, 600)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gr, 'RGBA'), (0, 0)); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(220, "YOU'RE NOT", 150, WHITE)
t(390, 'SITTING STILL', 135, GOLD)
R.pill(d, W / 2, 1450, 'RIGHT NOW', 60, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (1370, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0))
for i, f in enumerate(('f0.jpg', 'f1.jpg')): c.paste(Image.open(f).resize((270, 480)), (840 + (i % 2) * 270 - 0, 0 if i == 0 else 480)) if False else None
c.paste(Image.open('f0.jpg').resize((270,480)), (560, 480)); c.paste(Image.open('f1.jpg').resize((270,480)), (840, 480))
c.save('thumbcheck.jpg')

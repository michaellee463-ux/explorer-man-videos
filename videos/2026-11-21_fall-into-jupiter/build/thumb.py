from PIL import Image, ImageDraw
import numpy as np, math
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED
im = R.BG.copy()
R.paste_c(im, R.glow(1300, (255, 200, 140), 2.2), 540, 2150, 0.4)
R.paste_c(im, R.jscaled(1000), 540, 2150, 1.0)
R.streaks(im, 0.4, 0.6)
R.paste_c(im, R.astro(150), 540, 930, 1.0)
gr = np.zeros((760, W, 4), np.uint8); gr[..., 3] = (np.linspace(225, 0, 760)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gr, 'RGBA'), (0, 0)); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(230, 'THERE IS', 150, WHITE)
t(420, 'NO GROUND', 156, GOLD)
gb = np.zeros((520, W, 4), np.uint8); gb[..., 3] = (np.linspace(0, 200, 520)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gb, 'RGBA'), (0, H - 520)); d = ImageDraw.Draw(im, 'RGBA')
t(1640, 'NEVER HIT BOTTOM', 96, RED)
R.pill(d, W / 2, 1830, 'WHAT IF...? #6', 60, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

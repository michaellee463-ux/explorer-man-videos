from PIL import Image, ImageDraw
import numpy as np
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED, CYAN
im = R.BG.copy()
R.to_scale(im, 0, 540, 990, 1.12, 1.0, moons=1.0, moonpos=(870, 1480))
gr = np.zeros((760, W, 4), np.uint8); gr[..., 3] = (np.linspace(230, 0, 760)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gr, 'RGBA'), (0, 0)); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(220, '6 MOONS', 200, GOLD)
t(420, 'WIDE', 190, WHITE)
gb = np.zeros((560, W, 4), np.uint8); gb[..., 3] = (np.linspace(0, 220, 560)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gb, 'RGBA'), (0, H - 560)); d = ImageDraw.Draw(im, 'RGBA')
t(1640, "IN YOUR SKY", 130, CYAN)
R.pill(d, W / 2, 1810, 'ANDROMEDA', 60, (40, 90, 210))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

from PIL import Image, ImageDraw
import numpy as np
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED
im = R.BG.copy()
R.paste_c(im, R.EGLOW, 540, 2300, 0.5)
R.paste_c(im, R.BIGEARTH, 540, 2400, 1.0)
R.timer_ring(ImageDraw.Draw(im, 'RGBA'), 540, 960, 380, 0.8, RED, 1.0, 30)
R.paste_c(im, R.spun(R.person(230, 0.5), 15), 540, 980, 1.0)
gr = np.zeros((760, W, 4), np.uint8); gr[..., 3] = (np.linspace(225, 0, 760)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gr, 'RGBA'), (0, 0)); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(230, 'NO SUIT', 190, WHITE)
t(430, 'IN SPACE?', 170, GOLD)
gb = np.zeros((560, W, 4), np.uint8); gb[..., 3] = (np.linspace(0, 210, 560)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gb, 'RGBA'), (0, H - 560)); d = ImageDraw.Draw(im, 'RGBA')
t(1610, 'UNDER 15 SEC', 120, RED)
R.pill(d, W / 2, 1810, 'YOU VS... #4', 60, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

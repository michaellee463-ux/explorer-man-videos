import numpy as np
from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
G = 1800; m = 1150 / R.H_SHIP
d.rectangle((0, G, W, H), fill=(10, 10, 16, 255))
R.paste_b(im, R.starship_sprite(R.H_SHIP * m), 330, G)
R.paste_b(im, R.liberty_sprite(R.H_LIB * m), 760, G)
yy = np.arange(H); g = np.clip(1 - (yy - 520) / 200, 0, 1)
mask = Image.fromarray(np.repeat((g * 215).astype(np.uint8)[:, None], W, 1), 'L'); im.paste((0, 0, 0), (0, 0), mask)
d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(170, 'THE TALLEST', 136, WHITE)
t(340, 'ROCKET', 220, GOLD)
t(510, 'EVER BUILT', 136, WHITE)
R.pill(d, W / 2, 1862, '124 M vs 93 M · TO SCALE', 54, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

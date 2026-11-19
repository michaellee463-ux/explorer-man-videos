from PIL import Image, ImageDraw
import numpy as np
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy()
R.radial_streaks(im, 0.6, 540, 1250, 0.7)
R.paste_c(im, R.glow(560, (90, 140, 255), 1.7), 330, 1250, 0.7)
R.paste_c(im, R.earth_rot(300, 0.4), 330, 1250, 1.0)
R.paste_c(im, R.glow(200, (255, 210, 140), 1.8), 860, 1250, 0.5)
R.paste_c(im, R.sand_grain(70), 860, 1250, 1.0)
d = ImageDraw.Draw(im, 'RGBA')
d.text((680, 1250), '=', font=F(BLACK, 200), fill=(255, 255, 255), anchor='mm', stroke_width=12, stroke_fill=(5, 8, 16))
gr = np.zeros((760, W, 4), np.uint8); gr[..., 3] = (np.linspace(215, 0, 760)[:, None]).astype(np.uint8)
im.alpha_composite(Image.fromarray(gr, 'RGBA'), (0, 0)); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(250, 'SHRINK EARTH', 124, WHITE)
t(420, 'TO SAND...', 160, GOLD)
R.atom_icon(d, 540, 1720, 80, 0.7)
t(1560, 'YOU = ATOM-SIZED', 100, CYAN)
R.pill(d, W / 2, 1860, 'SCALE MODEL', 56, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

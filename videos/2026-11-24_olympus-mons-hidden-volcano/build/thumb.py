from PIL import Image, ImageDraw
import numpy as np
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED, CYAN
im = R.hook_scene(0, zoom=1.2, labels=0.0)
d = ImageDraw.Draw(im, 'RGBA')
R.grad(im, True, 760, 235); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(230, '2.5×', 260, GOLD)
t(440, 'EVEREST', 190, WHITE)
R.grad(im, False, 620, 230); d = ImageDraw.Draw(im, 'RGBA')
t(1590, 'YOU MIGHT', 120, CYAN)
t(1730, 'NOT NOTICE', 130, WHITE)
R.pill(d, W / 2, 1870, 'OLYMPUS MONS · MARS', 44, (190, 70, 30))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

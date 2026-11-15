import numpy as np
from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy()
R.crowd_stream(im, 2.0, W / 2, 1080, 1.0)
R.darkband(im, 1.0)
R.draw_cube(im, W / 2, 1080, 300, 1.0, g=1.0)
d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(250, 'ALL 8 BILLION', 130, WHITE)
t(420, 'OF US', 190, GOLD)
t(1560, 'IN ONE', 150, WHITE)
t(1720, 'SUGAR CUBE', 150, CYAN)
R.pill(d, W / 2, 1880 - 20, 'YOU VS. #3', 50, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED
im = R.SKY.copy()
R.pair(im, W / 2, 980, 330, 2.6, 1.0)
d = ImageDraw.Draw(im, 'RGBA'); R.ground(d)
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(260, 'NOT', 150, WHITE)
t(430, 'TOUCHING', 190, GOLD)
t(1330, '368 MILLION', 130, WHITE)
t(1470, 'MILES APART', 120, RED)
R.label(d, W / 2 + 330, 1200, 'JUPITER', 60, (255, 244, 215), 1.0)
R.label(d, W / 2 - 330, 720, 'MARS', 60, (255, 140, 60), 1.0)
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

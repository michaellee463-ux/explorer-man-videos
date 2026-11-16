from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
im = R.BG.copy()
R.paste_c(im, R.glow(700, (120, 180, 255), 1.6), 330, 1000, 0.6)
R.paste_c(im, R.earth(260), 330, 1000, 1.0)
d = ImageDraw.Draw(im, 'RGBA')
d.polygon([(610, 960), (690, 1000), (610, 1040)], fill=(255, 255, 255, 240)); d.line((520, 1000, 640, 1000), fill=(255, 255, 255, 240), width=18)
R.draw_bh(im, 860, 1000, 85, 1.0)
d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(270, 'CRUSH EARTH', 140, WHITE)
t(430, 'TO A MARBLE', 140, GOLD)
t(1560, 'IT BECOMES A', 120, WHITE)
t(1710, 'BLACK HOLE', 160, (255, 110, 60))
R.pill(d, W / 2, 1860, 'WHAT IF #5', 50, (210, 30, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

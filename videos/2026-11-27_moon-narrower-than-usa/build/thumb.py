from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN
cam = (R.UCX, R.UCY - 250, 0.215)
im = R.BG.copy(); im.alpha_composite(R.USMAP.view(*cam, W, H))
cx, cy = R.scr((R.UCX, R.UCY - 60), cam)
R.draw_body(im, 'Moon', cx, cy, cam[2]); R.us_outline(im, cam, 0.4)
d = ImageDraw.Draw(im, 'RGBA')
R.grad(im, True, 700, 235); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(220, "IT DOESN'T", 150, WHITE)
t(390, 'REACH', 190, GOLD)
R.grad(im, False, 640, 235); d = ImageDraw.Draw(im, 'RGBA')
t(1560, 'COAST TO', 150, WHITE)
t(1720, 'COAST', 170, GOLD)
R.pill(d, W / 2, 1860, 'THE MOON · TO SCALE', 44, (30, 110, 170))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

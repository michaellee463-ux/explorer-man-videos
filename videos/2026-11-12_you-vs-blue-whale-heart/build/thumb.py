import numpy as np
from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, CYAN, PURPLE
im = R.bg_image(0.2, 0)
whale, wcy = R.whale_sprite(1500)
R.paste_c(im, whale, W / 2 + 120, 1540, rot=8)
hs = R.heart_sprite(900)
R.paste_c(im, hs, W / 2 + 30, 1060, scale=0.95)
# dark gradient behind text (top)
yy = np.arange(H)
g = np.clip(1 - (yy - 680) / 360, 0, 1) ** 1.2
mask = Image.fromarray(np.repeat((g * 200).astype(np.uint8)[:, None], W, 1), 'L')
im.paste((0, 0, 0), (0, 0), mask)
d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col):
    d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(250, 'A 180 KG HEART', 112, WHITE)
t(420, '2 BEATS', 220, CYAN)
t(580, 'A MINUTE', 130, GOLD)
t(690, 'ON A DEEP DIVE', 64, WHITE)
R.pill(d, W / 2, 1820, 'YOU vs', 64, PURPLE, (20, 10, 40))
out = im.convert('RGB')
out.save('../thumbnail.jpg', quality=92)
out.resize((270, 480), Image.LANCZOS).save('thumb_small.png')

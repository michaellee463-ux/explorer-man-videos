from PIL import Image, ImageDraw
import render as R
from render import W, H, F, BLACK, WHITE, GOLD, RED, CYAN
im = R.BG.copy()
R.paste_c(im, R.galaxy_sprite(520), W / 2, 980, 0.7)
R.clock(im, W / 2, 1000, 380, 11, 59.5, alpha=1.0, glowc=RED)
R.paste_c(im, R.emoji('🦖', 360), 230, 1420)
R.paste_c(im, R.emoji('🧍', 330), W - 190, 1430)
R.grad(im, True, 760, 235); d = ImageDraw.Draw(im, 'RGBA')
def t(y, s, size, col): d.text((W / 2, y), s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=max(8, size // 11), stroke_fill=(5, 8, 16))
t(200, 'WE SHOW UP', 140, WHITE)
t(390, 'AT WHAT', 190, WHITE)
t(590, 'TIME?!', 200, GOLD)
R.grad(im, False, 520, 230); d = ImageDraw.Draw(im, 'RGBA')
t(1700, 'UNIVERSE = 1 YEAR', 96, CYAN)
R.pill(d, W / 2, 1830, '13.8 BILLION YEARS', 48, (190, 40, 40))
out = im.convert('RGB'); out.save('../thumbnail.jpg', quality=92)
a = out.resize((540, 960)); b = out.resize((270, 480), Image.LANCZOS)
c = Image.new('RGB', (830, 960), (40, 40, 40)); c.paste(a, (0, 0)); c.paste(b, (560, 0)); c.save('thumbcheck.jpg')

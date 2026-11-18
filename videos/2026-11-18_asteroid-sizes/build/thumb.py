import numpy as np
from PIL import Image, ImageDraw
from render import make_globe, make_asteroid, glow, BG, F, BLACK, POP_B, GOLD, WHITE, RED, W, H
from PIL import ImageFilter
def rocky(R):
    a = make_asteroid(R, 51)
    arr = np.array(a).astype(np.float32)
    al = arr[..., 3:4] / 255
    g = np.random.default_rng(4)
    n = Image.fromarray((g.random((a.height // 6 + 1, a.width // 6 + 1)) * 255).astype(np.uint8)).resize(a.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(4))
    n2 = Image.fromarray((g.random((a.height // 2 + 1, a.width // 2 + 1)) * 255).astype(np.uint8)).resize(a.size, Image.BICUBIC)
    lum = arr[..., :3].mean(-1, keepdims=True)
    lum = np.array(a.filter(ImageFilter.GaussianBlur(10))).astype(np.float32)[..., :3].mean(-1, keepdims=True)
    tex = 0.75 + 0.45 * np.array(n, np.float32)[..., None] / 255 + 0.15 * np.array(n2, np.float32)[..., None] / 255
    col = lum * tex * np.array([1.0, 0.92, 0.82])
    return Image.fromarray(np.concatenate([np.clip(col, 0, 255), arr[..., 3:4]], -1).astype(np.uint8), 'RGBA')
im = BG.copy()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
g = np.exp(-(((xx - 1300) / 700) ** 2 + ((yy - 470) / 600) ** 2) * 2.0)[..., None] * np.array([0.5, 0.25, 0.06])
base = np.array(im)[..., :3].astype(np.int32) + (g * 255).astype(np.int32)
im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
e = make_globe(150, 0.8); im.alpha_composite(e, (1640 - 152, 830 - 152))
# fiery trail
d = ImageDraw.Draw(im, 'RGBA')
for i in range(70):
    q = i / 70
    x0, y0 = 1250 + q * 700, 470 - q * 520
    r = 330 * (1 - q) + 30
    d.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), fill=(255, 140 + int(80 * q), 60, int(14 * (1 - q) ** 1.5)))
gl = glow(520, (255, 170, 90)); im.alpha_composite(gl, (1250 - 520, 470 - 520))
a = rocky(330); im.alpha_composite(a, (1250 - a.width // 2, 470 - a.height // 2))
m = np.clip(1 - (xx[0] - 520) / 520, 0, 1) ** 1.3
im.paste((0, 0, 0), (0, 0), Image.fromarray(np.repeat((m * 220).astype(np.uint8)[None, :], H, 0), 'L'))
d = ImageDraw.Draw(im, 'RGBA')
def t(xy, s, size, col, st):
    d.text(xy, s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=st, stroke_fill=(8, 8, 14))
t((500, 270), 'HOW BIG', 190, WHITE, 16)
t((500, 470), 'IS TOO', 190, WHITE, 16)
t((500, 680), 'BIG?', 230, GOLD, 18)
f = F(POP_B, 58); s = 'EVERY SIZE COMPARED'; w = f.getlength(s) + 90
d.rounded_rectangle((500 - w / 2, 860, 500 + w / 2, 970), 55, fill=(215, 30, 40, 255))
d.text((500, 915), s, font=f, fill=WHITE, anchor='mm')
out = im.convert('RGB'); out.save('thumb_full.jpg', quality=92)
out.resize((1280, 720), Image.LANCZOS).save('../thumbnail.jpg', quality=92)
out.resize((320, 180), Image.LANCZOS).save('thumb_small.png')

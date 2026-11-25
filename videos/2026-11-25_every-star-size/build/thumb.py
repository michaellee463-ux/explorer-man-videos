import numpy as np
from PIL import Image, ImageDraw
from render import BG, F, BLACK, POP_B, GOLD, WHITE, W, H, draw_star, star_sprite, STARS, IDX, glow_sprite, paste_scaled
im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
i = IDX['VY']; rs = 13.0; R = 1420 * rs
edge = 1060; draw_star(im, d, star_sprite(i), STARS[i][2], edge + R, H * 0.5, R)
from render import noise
cx_ = edge + R; dist = np.hypot(np.mgrid[0:H, 0:W][1] - cx_, np.mgrid[0:H, 0:W][0] - H * 0.5) - R
inside = (dist < 0)
nz = noise(1024, 9, ((6, 0.6), (14, 0.35), (36, 0.2)))
nz = np.asarray(Image.fromarray(((nz - nz.min()) / np.ptp(nz) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
arr = np.asarray(im).astype(np.float32)
lit = (0.55 + 0.9 * nz) * (0.75 + 0.25 * np.clip(-dist / 400, 0, 1))
col = np.array([255, 95, 45], np.float32)
arr[..., :3] = np.where(inside[..., None], np.clip(col[None, None] * lit[..., None] + (np.clip(lit - 1.05, 0, 1) * 200)[..., None], 0, 255), arr[..., :3])
halo = np.exp(-np.clip(dist, 0, None) / 40) * (dist >= 0)
arr[..., :3] += (halo[..., None] * np.array([255, 110, 60]) * 0.6)
im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(im, 'RGBA')
sx, sy = 905, 640
paste_scaled(im, glow_sprite((255, 220, 150)), sx, sy, 70)
draw_star(im, d, star_sprite(0), STARS[0][2], sx, sy, rs)
d = ImageDraw.Draw(im, 'RGBA')
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
m = np.clip(1 - (xx[0] - 560) / 380, 0, 1) ** 1.3
im.paste((0, 0, 0), (0, 0), Image.fromarray(np.repeat((m * 200).astype(np.uint8)[None, :], H, 0), 'L'))
d = ImageDraw.Draw(im, 'RGBA')
def t(xy, s, size, col, st):
    d.text(xy, s, font=F(BLACK, size), fill=col, anchor='mm', stroke_width=st, stroke_fill=(8, 8, 14))
t((440, 250), 'OUR SUN', 170, WHITE, 16)
t((440, 440), 'IS THIS', 170, WHITE, 16)
t((440, 650), 'DOT', 230, GOLD, 18)
# arrow from DOT to the Sun
d.line((640, 650, sx - 40, sy), fill=(255, 205, 90, 255), width=16)
d.polygon([(sx - 22, sy), (sx - 70, sy - 30), (sx - 70, sy + 30)], fill=(255, 205, 90, 255))
f = F(POP_B, 58); s = 'EVERY STAR SIZE COMPARED'; w = f.getlength(s) + 90
d.rounded_rectangle((470 - w / 2, 880, 470 + w / 2, 990), 55, fill=(215, 30, 40, 255))
d.text((470, 935), s, font=f, fill=WHITE, anchor='mm')
t((1500, 120), 'VY CANIS MAJORIS', 64, WHITE, 8)
d.text((1880, 1040), 'to scale', font=F(POP_B, 30), fill=(230, 230, 230, 200), anchor='rm')
out = im.convert('RGB'); out.save('thumb_full.jpg', quality=92)
out.resize((1280, 720), Image.LANCZOS).save('../thumbnail.jpg', quality=92)
out.resize((320, 180), Image.LANCZOS).save('thumb_small.png')

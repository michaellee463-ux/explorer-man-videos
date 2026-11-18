import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from script import SCENES

W, H, FPS = 1920, 1080, 30
LEAD, END = 0.0, 0.25
POP_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
POP_M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
WHITE = (255, 255, 255); GOLD = (255, 205, 90); CYAN = (90, 215, 255); RED = (255, 80, 70)
GREEN = (110, 235, 140); GREY = (170, 178, 195); ORANGE = (255, 150, 60)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return min(max((t - a) / (b - a), 0), 1)
def pop(t, a, d=0.35): return ease(ramp(t, a, a + d))

# ---------------------------------------------------------------- background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
bg = np.zeros((H, W, 3), np.float32); bg[:] = np.array([0.03, 0.035, 0.07])
r2 = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2
bg *= (1.3 - 1.2 * r2)[..., None]
for _ in range(1100):
    x, y = rng.integers(0, W), rng.integers(0, H); bg[y, x] += rng.uniform(0.05, 0.4)
BG = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

def text(d, xy, s, size, col=WHITE, font=BLACK, anchor='mm', stroke=None, alpha=1.0):
    if alpha <= 0.01: return
    if stroke is None: stroke = max(3, size // 12)
    d.text(xy, s, font=F(font, size), fill=tuple(col) + (int(255 * alpha),), anchor=anchor,
           stroke_width=stroke, stroke_fill=(5, 8, 15, int(255 * alpha)))

def pill(d, xy, s, size, bgc, fg=(15, 15, 25), alpha=1.0):
    if alpha <= 0.01: return
    f = F(POP_B, size); w = f.getlength(s) + size * 1.2; h = size * 1.6
    x, y = xy
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), h / 2, fill=tuple(bgc) + (int(240 * alpha),))
    d.text((x, y), s, font=f, fill=tuple(fg) + (int(255 * alpha),), anchor='mm')

def note(d, s, a=1.0):
    text(d, (W - 60, 128), s, 26, GREY, POP_M, anchor='rm', stroke=2, alpha=a)

def wrap(s, font, maxw):
    words = s.split(); lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if font.getlength(t) > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    if cur: lines.append(cur)
    return lines

def caption(s):
    # spoken words -> readable caption
    rep = [("twenty twenty-nine", "2029"), ("twenty thirteen", "2013"), ("twenty twenty-two", "2022"), ("nineteen oh eight", "1908"),
           ("April thirteenth", "April 13"), ("February fifteenth", "February 15"), ("June thirtieth", "June 30"),
           ("thirty-two thousand kilometers", "32,000 km"), ("thirty-six thousand kilometers", "36,000 km"),
           ("three hundred and forty meters", "340 meters"), ("a hundred and sixty meters", "160 meters"), ("a hundred and forty meters", "140 meters"),
           ("a hundred and eighty meters", "180 meters"), ("five hundred kilotons", "500 kilotons"),
           ("fifteen hundred", "1,500"), ("eighty million", "80 million"), ("two thousand square kilometers", "2,000 square kilometers"),
           ("fifty thousand years", "50,000 years"), ("sixty-six million", "66 million"), ("ninety percent", "90%"),
           ("a hundred and fifty to a hundred and eighty kilometers", "150 to 180 kilometers"), ("ten to fifteen kilometers", "10 to 15 kilometers"),
           ("thirty-two minutes", "32 minutes"), ("nineteen kilometers", "19 kilometers"), ("thirty kilometers", "30 kilometers"),
           ("five to ten kilometers", "5 to 10 kilometers"), ("fifty to a hundred meters", "50 to 100 meters"), ("Fifty to a hundred", "50 to 100"),
           ("fifty meters", "50 meters"), ("Twenty meters", "20 meters"), ("twenty meters", "20 meters"), ("One point two kilometers", "1.2 kilometers"),
           ("one kilometer", "1 kilometer"), ("One kilometer", "1 kilometer"), ("ten kilometers", "10 kilometers"), ("fifteen megatons", "15 megatons"),
           ("a thousand times", "1,000 times"), ("eleven football", "11 football"), ("a hundred years", "100 years"), ("Friday the thirteenth", "Friday the 13th")]
    for a, b in rep: s = s.replace(a, b)
    return s

def draw_caption(d, s):
    if not s: return
    f = F(POP_M, 40)
    lines = wrap(s, f, 1560)[-2:] if len(wrap(s, f, 1560)) <= 2 else wrap(s, f, 1560)
    y0 = H - 62 - (len(lines) - 1) * 52
    for i, ln in enumerate(lines):
        bw = f.getlength(ln) + 40
        d.rounded_rectangle((W / 2 - bw / 2, y0 + i * 52 - 27, W / 2 + bw / 2, y0 + i * 52 + 27), 12, fill=(0, 0, 0, 120))
        d.text((W / 2, y0 + i * 52), ln, font=f, fill=(255, 255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))

# ---------------------------------------------------------------- sprites
def make_asteroid(R, seed=1, iron=False):
    S = int(2 * R * 1.35 + 8); c = S / 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    ang = np.arctan2(y - c, x - c); rr = np.hypot(x - c, y - c)
    g = np.random.default_rng(seed); ph = g.uniform(0, 6.3, 6)
    rad = R * (1 + 0.13 * np.sin(2 * ang + ph[0]) + 0.08 * np.sin(3 * ang + ph[1]) + 0.05 * np.sin(5 * ang + ph[2]) + 0.025 * np.sin(9 * ang + ph[3]))
    inside = rr < rad
    nx = (x - c) / rad; ny = (y - c) / rad
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    light = np.clip(0.18 + 0.95 * (-0.55 * nx - 0.45 * ny + 0.7 * nz), 0.05, 1.15)
    base = np.array([0.55, 0.52, 0.5]) if iron else np.array([0.5, 0.44, 0.38])
    tex = (0.12 * np.sin(x * 0.35 / max(R / 40, 1) + np.sin(y * 0.21 / max(R / 40, 1)) * 3) * np.sin(y * 0.29 / max(R / 40, 1))
           + 0.06 * np.sin((x + y) * 0.9 / max(R / 40, 1)))
    col = base[None, None, :] * (light * (1 + tex))[..., None]
    for _ in range(14):
        cx_, cy_ = g.uniform(-0.6, 0.6, 2) * R + c; cr = g.uniform(0.06, 0.2) * R
        dd = np.hypot(x - cx_, y - cy_) / cr
        m = dd < 1
        col[m] *= (0.72 + 0.28 * dd[m] + 0.25 * np.clip((x[m] - cx_) / cr, -1, 1) * -0.6)[..., None] * 1.0
    a = np.clip(rad - rr + 0.5, 0, 1)
    rgba = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    return Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')

def make_globe(R, lon0=0.0):
    S = int(2 * R + 4); c = S / 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    nx = (x - c) / R; ny = (y - c) / R; rr2 = nx ** 2 + ny ** 2; inside = rr2 <= 1
    nz = np.sqrt(np.clip(1 - rr2, 0, 1))
    lat = np.arcsin(np.clip(-ny, -1, 1)); lon = np.arctan2(nx, nz) + lon0
    n = (np.sin(lon * 2 + 1.3) * np.cos(lat * 3) + 0.6 * np.sin(lon * 5 + lat * 4 + 0.5) + 0.35 * np.sin(lon * 11 - lat * 7))
    land = n > 0.55; ice = np.abs(lat) > 1.25
    col = np.zeros((S, S, 3), np.float32); col[:] = np.array([0.05, 0.22, 0.5])
    col[land] = np.array([0.25, 0.43, 0.2]); col[land & (n > 1.1)] = np.array([0.52, 0.42, 0.28]); col[ice] = np.array([0.88, 0.92, 0.96])
    cl = np.sin(lon * 4 + 3 * np.sin(lat * 6)) * np.sin(lat * 9 + lon * 1.5) + 0.5 * np.sin(lon * 13 + lat * 11)
    cm = np.clip((cl - 0.7) / 0.6, 0, 1)[..., None] * 0.5; col = col * (1 - cm) + cm * 0.92
    light = np.clip(0.2 + 0.9 * (-0.5 * nx - 0.3 * ny + 0.8 * nz), 0.06, 1.1); col *= light[..., None]
    rim = np.clip((np.sqrt(rr2) - 0.93) / 0.07, 0, 1) * inside; col += rim[..., None] * np.array([0.15, 0.3, 0.6])
    a = np.clip((1 - np.sqrt(rr2)) * R + 0.5, 0, 1)
    return Image.fromarray((np.concatenate([np.clip(col, 0, 1), a[..., None]], -1) * 255).astype(np.uint8), 'RGBA')

def glow(R, col, power=2.0):
    S = int(R * 2); c = S / 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    a = np.clip(1 - np.hypot(x - c, y - c) / R, 0, 1) ** power
    im = np.zeros((S, S, 4), np.float32); im[..., :3] = np.array(col) / 255; im[..., 3] = a
    return Image.fromarray((im * 255).astype(np.uint8), 'RGBA')

C = {}
def sprite(key, fn):
    if key not in C: C[key] = fn()
    return C[key]

def paste_c(im, sp, cx, cy, rot=0):
    if rot: sp = sp.rotate(rot, resample=Image.BILINEAR)
    im.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))

def add_glow(im, cx, cy, R, col, a):
    if a <= 0.01: return
    g = sprite(('glow', R, col), lambda: glow(R, col))
    if a < 1:
        g = g.copy(); al = np.array(g)[..., 3].astype(np.float32) * a; g.putalpha(Image.fromarray(al.astype(np.uint8)))
    paste_c(im, g, cx, cy)

def flash(im, a):
    if a <= 0.01: return
    ov = Image.new('RGBA', (W, H), (255, 245, 220, int(255 * min(a, 1))))
    im.alpha_composite(ov)

# ---------------------------------------------------------------- scene framework
class Scene:
    def __init__(self, key, chapter, sents, lead):
        self.key, self.chapter, self.sents = key, chapter, sents
        t = lead; self.marks = []
        for s in sents:
            self.marks.append((t, t + s['dur'], caption(s['text'])))
            t += s['dur'] + s['pause']
        self.dur = t + END
    def s(self, i): return self.marks[i][0]
    def e(self, i): return self.marks[i][1]
    def cap_at(self, t):
        cur = None
        for a, b, s in self.marks:
            if t >= a - 0.05: cur = (a, b, s)
        if cur and t <= cur[1] + 0.6: return cur[2]
        return None

def satellite(d, x, y, a=1.0):
    c = (200, 210, 230, int(255 * a))
    d.rectangle((x - 5, y - 5, x + 5, y + 5), fill=c)
    d.rectangle((x - 22, y - 3, x - 8, y + 3), fill=(70, 120, 220, int(255 * a)))
    d.rectangle((x + 8, y - 3, x + 22, y + 3), fill=(70, 120, 220, int(255 * a)))

def orbit_diagram(im, d, t, cx, cy, Rpx, show_ast, ast_p, labels=True, la=1.0, big=False):
    """Earth + geosynchronous ring + Apophis path, distances to scale (Earth radius Rpx)."""
    R_E = 6371.0
    geo = (R_E + 35786) / R_E * Rpx
    ap = (R_E + 32000) / R_E * Rpx
    paste_c(im, sprite(('globe', Rpx), lambda: make_globe(Rpx, 0.8)), cx, cy)
    for k in range(0, 360, 3):  # dashed ring
        a0 = math.radians(k + t * 2)
        d.arc((cx - geo, cy - geo, cx + geo, cy + geo), k + t * 2, k + t * 2 + 1.6, fill=(120, 190, 255, 170), width=3)
    for k in range(6):
        a0 = math.radians(k * 60 + t * 4 + 15)
        satellite(d, cx + geo * math.cos(a0), cy + geo * math.sin(a0))
    if show_ast:
        # straight-line path, closest approach `ap` from centre, at angle -35deg (upper right)
        th = math.radians(-12 if big else -35); nx_, ny_ = math.cos(th), math.sin(th); tx, ty = -ny_, nx_
        px, py = cx + ap * nx_, cy + ap * ny_
        s_ = (ast_p - 0.5) * 2600
        ax_, ay_ = px + tx * s_, py + ty * s_
        # trail
        for i in range(40):
            ss = s_ - i * 14
            qx, qy = px + tx * ss, py + ty * ss
            d.ellipse((qx - 9 + i * 0.2, qy - 9 + i * 0.2, qx + 9 - i * 0.2, qy + 9 - i * 0.2), fill=(255, 190, 120, int(140 * (1 - i / 40))))
        rA = 46 if big else 30
        add_glow(im, ax_, ay_, rA * 3, (255, 190, 120), 0.55)
        paste_c(im, sprite(('ast', rA, 3), lambda: make_asteroid(rA, 3)), ax_, ay_, rot=-t * 40)
        if big: text(d, (ax_, ay_ + rA + 40), 'APOPHIS', 40, GOLD)
        text(d, (cx + geo * math.cos(math.radians(14)) + 30, cy + geo * math.sin(math.radians(14))), 'satellites', 30, CYAN, POP_B, anchor='lm')
        if labels:
            d.line((cx, cy, px, py), fill=(255, 205, 90, int(200 * la)), width=3)
    return geo, ap

# ---------------------------------------------------------------- scenes
def sc_hook(sc, t, im, d):
    s = sc.s
    Rpx = 115; cx, cy = 230, 560
    p = 0.47 + 0.08 * t / sc.dur
    orbit_diagram(im, d, t, cx, cy, Rpx, True, p, labels=False, big=True)
    # headline visible from frame 0
    a2 = 1 - pop(t, s(2) - 0.2)
    text(d, (1450, 200), 'CLOSER THAN', 100, WHITE, alpha=a2)
    text(d, (1450, 315), 'OUR SATELLITES', 100, GOLD, alpha=a2)
    pill(d, (1450, 440), 'FRIDAY, APRIL 13, 2029', 44, RED, WHITE, alpha=a2)
    text(d, (1450, 545), 'as tall as the Eiffel Tower', 42, GREY, POP_B, alpha=a2 * pop(t, 0.6))
    a1 = pop(t, s(1)) * a2
    pill(d, (1450, 650), 'NASA: IT WILL MISS', 44, GREEN, alpha=a1)
    note(d, 'distances to scale · asteroid enlarged', a2)
    # question
    a3 = pop(t, s(2))
    text(d, (1300, 230), 'HOW BIG DOES IT', 100, WHITE, alpha=a3)
    text(d, (1300, 345), 'HAVE TO BE', 100, WHITE, alpha=a3)
    text(d, (1300, 470), 'TO END THE WORLD?', 112, RED, alpha=a3)
    a4 = pop(t, s(3))
    labs = ['sand', '20 m', '50–100 m', '340 m', '1 km', '10 km']
    for i, l in enumerate(labs):
        ai = pop(t, s(3) + 0.25 * i)
        x = 760 + i * 180; r = 8 + i * 13
        paste_c(im, sprite(('ast', r, 10 + i), lambda: make_asteroid(r, 10 + i)), x, 720) if ai > 0.5 else None
        text(d, (x, 830), l, 38, GOLD, alpha=ai)
    if a4 > 0: text(d, (1200, 900), 'sizes not to scale', 26, GREY, POP_M, stroke=2, alpha=a4)

def sky_ground(im, d, col=(14, 18, 30)):
    d.rectangle((0, 900, W, H), fill=col + (255,))

def skyline(d, y0, seed=2, col=(18, 22, 34), lit=True, shake=0.0):
    g = np.random.default_rng(seed); x = 0
    while x < W:
        w_ = g.integers(50, 130); h_ = g.integers(80, 320)
        d.rectangle((x, y0 - h_, x + w_ - 6, y0), fill=col + (255,))
        if lit:
            for wy in range(int(y0 - h_ + 14), int(y0 - 10), 26):
                for wx in range(int(x + 10), int(x + w_ - 16), 22):
                    if g.random() < 0.5:
                        d.rectangle((wx, wy, wx + 9, wy + 12), fill=(255, 215, 130, 200))
        x += w_

def sc_sand(sc, t, im, d):
    s = sc.s
    d.rectangle((0, 880, W, H), fill=(10, 14, 22, 255))
    g = np.random.default_rng(5)
    for k in range(14):
        t0 = g.uniform(-0.5, sc.dur); x0 = g.uniform(300, 1900); y0 = g.uniform(60, 400); L = g.uniform(250, 520)
        p = (t - t0) / 0.7
        if 0 < p < 1:
            dx, dy = -0.85, 0.53
            hx, hy = x0 + dx * L * p, y0 + dy * L * p
            for i in range(30):
                q = i / 30; a = (1 - q) * math.sin(math.pi * p)
                d.line((hx - dx * L * 0.35 * q, hy - dy * L * 0.35 * q, hx - dx * L * 0.35 * (q + 1 / 30), hy - dy * L * 0.35 * (q + 1 / 30)),
                       fill=(200, 230, 255, int(255 * a)), width=max(1, int(5 * (1 - q))))
    a = pop(t, 0.1)
    text(d, (W / 2, 520), 'MOST SHOOTING STARS', 96, WHITE, alpha=a)
    text(d, (W / 2, 640), '= DUST & SAND GRAINS', 96, GOLD, alpha=a)
    a = pop(t, s(1))
    pill(d, (W / 2, 780), 'burn up high above you', 42, CYAN, alpha=a)
    a = pop(t, s(2))
    pill(d, (W / 2, 330), 'HARMLESS', 50, GREEN, alpha=a)

def sc_chel(sc, t, im, d):
    s = sc.s
    tb = s(3) + 0.3  # explosion time
    tsh = s(5) + 0.2  # shock wave
    shake = 6 * math.exp(-max(0, t - tsh) * 4) * math.sin(t * 60) if t > tsh else 0
    skyline(d, 900 + shake, 4)
    d.rectangle((0, 900, W, H), fill=(12, 15, 24, 255))
    # fireball path from upper right to explosion point
    ex, ey = 760, 300
    if t < tb:
        p = ease(ramp(t, 0.0, tb))
        sx, sy = 1900 - (1900 - ex) * p, -40 + (ey + 40) * p
        for i in range(60):
            q = i / 60
            d.line((sx + q * 900 * 0.45, sy - q * 340 * 0.45, sx + (q + 1 / 60) * 900 * 0.45, sy - (q + 1 / 60) * 340 * 0.45),
                   fill=(255, 220, 160, int(230 * (1 - q))), width=max(2, int(18 * (1 - q))))
        add_glow(im, sx, sy, 90, (255, 230, 170), 0.9)
        paste_c(im, sprite(('ast', 16, 21), lambda: make_asteroid(16, 21)), sx, sy, rot=t * 90)
    else:
        k = t - tb
        flash(im, 0.95 * math.exp(-k * 3.5))
        add_glow(im, ex, ey, int(160 + 60 * min(k, 1)), (255, 200, 120), max(0, 1 - k * 0.25))
        # smoke trail
        for i in range(80):
            q = i / 80
            d.line((ex + q * 1100, ey - q * 420, ex + (q + 1 / 80) * 1100, ey - (q + 1 / 80) * 420), fill=(210, 205, 200, int(120 * (1 - q) * min(1, k))), width=int(14 + 30 * q))
    if t > tsh:
        k = t - tsh; r = k * 900
        d.ellipse((ex - r, ey - r * 0.75, ex + r, ey + r * 0.75), outline=(255, 255, 255, int(200 * max(0, 1 - k / 1.6))), width=6)
    # cards (left/right panels)
    pill(d, (330, 140), '20 METERS', 52, GOLD, alpha=pop(t, s(0)))
    pill(d, (330, 240), 'FEB 15, 2013 · RUSSIA', 36, WHITE, alpha=pop(t, s(1)))
    pill(d, (1560, 140), '≈ 19 KM/S', 52, CYAN, alpha=pop(t, s(1) + 3.5))
    a = pop(t, s(2)) * (1 - pop(t, s(3)))
    text(d, (W / 2, 520), 'NO TELESCOPE SAW IT COMING', 80, RED, alpha=a)
    a = pop(t, s(3)) * (1 - pop(t, s(4) - 0.2))
    text(d, (W / 2, 520), 'EXPLODED ≈ 30 KM UP', 92, WHITE, alpha=a)
    text(d, (W / 2, 630), 'briefly brighter than the Sun', 48, GOLD, POP_B, alpha=a)
    a = pop(t, s(4)) * (1 - pop(t, s(5) - 0.2))
    text(d, (W / 2, 500), '≈ 500 KILOTONS', 110, GOLD, alpha=a)
    text(d, (W / 2, 620), '≈ 30× HIROSHIMA', 80, WHITE, alpha=a)
    a = pop(t, s(5) + 2.5)
    text(d, (W / 2, 520), '≈ 1,500 PEOPLE HURT', 100, RED, alpha=a * (1 - pop(t, s(6))))
    text(d, (W / 2, 630), 'mostly by flying glass', 48, WHITE, POP_B, alpha=a * (1 - pop(t, s(6))))
    a = pop(t, s(6))
    text(d, (W / 2, 560), 'AND THAT WAS A SMALL ONE', 96, GOLD, alpha=a)

TREES = None
def sc_tung(sc, t, im, d):
    global TREES
    s = sc.s
    tb = s(1) + 2.6
    cx, cy = W / 2, 560
    if TREES is None:
        g = np.random.default_rng(9); TREES = []
        for _ in range(900):
            ang = g.uniform(0, 2 * math.pi); r = math.sqrt(g.uniform(0.0, 1)) * 860
            x = cx + r * math.cos(ang); y = cy + r * math.sin(ang) * 0.42 + 200
            if 380 < y < 1010: TREES.append((x, y, ang, r, g.uniform(26, 44)))
        TREES.sort(key=lambda z: z[1])
    d.rectangle((0, 380, W, H), fill=(22, 30, 22, 255))
    k = t - tb
    for x, y, ang, r, h_ in TREES:
        fall = ease(ramp(k, r / 1400, r / 1400 + 0.35)) if k > 0 else 0
        dx = math.cos(ang); dy = math.sin(ang) * 0.42
        tipx = x + dx * h_ * fall * 1.1; tipy = y - h_ * (1 - fall) + dy * h_ * fall
        c = (40, 70, 40) if fall < 0.5 else (90, 75, 50)
        d.line((x, y, tipx, tipy), fill=c + (255,), width=4)
    if k > 0:
        flash(im, 0.9 * math.exp(-k * 3))
        add_glow(im, cx, 180, 200, (255, 210, 140), max(0, 1 - k * 0.3))
    elif t > s(1):
        p = ease(ramp(t, s(1), tb)); sx, sy = 1800 - (1800 - cx) * p, -40 + 220 * p
        add_glow(im, sx, sy, 70, (255, 230, 170), 0.9)
        paste_c(im, sprite(('ast', 22, 31), lambda: make_asteroid(22, 31)), sx, sy, rot=t * 80)
    fo = 1 - pop(t, s(2) - 0.3)
    pill(d, (330, 120), '50–100 METERS', 50, GOLD, alpha=pop(t, s(0)) * fo)
    pill(d, (330, 215), 'JUNE 30, 1908 · SIBERIA', 36, WHITE, alpha=pop(t, s(1)) * fo)
    pill(d, (1560, 215), 'EXPLODED 5–10 KM UP', 40, CYAN, alpha=pop(t, s(1) + 3) * fo)
    a = pop(t, s(2)) * (1 - pop(t, s(4) - 0.2))
    text(d, (W / 2, 260), '≈ 80 MILLION TREES', 104, WHITE, alpha=a)
    text(d, (W / 2, 370), 'flattened across ≈ 2,000 km²', 54, GOLD, POP_B, alpha=a)
    a = pop(t, s(3)) * (1 - pop(t, s(4) - 0.2))
    pill(d, (W / 2, 480), 'UP TO 15 MEGATONS · UP TO 1,000× HIROSHIMA', 40, ORANGE, alpha=a)
    a = pop(t, s(4) + 1.2)
    text(d, (W / 2, 300), 'NO CLEAR CRATER', 110, RED, alpha=a)
    a = pop(t, s(5))
    text(d, (W / 2, 430), 'rock blows apart in the air...', 54, WHITE, POP_B, alpha=a)
    text(d, (W / 2, 520), 'but IRON?', 80, GOLD, alpha=pop(t, s(5) + 3.2))

def sc_crater(sc, t, im, d):
    s = sc.s
    # cross-section to scale: 1.2 km wide, 180 m deep, rock ~50 m
    x0, x1 = 260, 1660; mpp = 1200 / (x1 - x0)  # m per px
    gy = 560; depth = 180 / mpp
    d.rectangle((0, gy, W, H), fill=(120, 80, 50, 255))
    d.rectangle((0, gy, W, gy + 18), fill=(170, 120, 75, 255))
    pr = ease(ramp(t, s(1) - 0.4, s(1) + 0.4))
    tb = s(1) - 0.4
    if t < tb:
        p = ease(ramp(t, 0.3, tb)); sx, sy = 1700 - (1700 - (x0 + x1) / 2) * p, -80 + (gy + 80) * p
        add_glow(im, sx, sy, 60, (255, 230, 170), 0.8)
        r = 25 / mpp
        paste_c(im, sprite(('ast', int(r), 41, 'i'), lambda: make_asteroid(int(r), 41, True)), sx, sy, rot=t * 70)
    if pr > 0:
        pts = []
        for i in range(81):
            u = i / 80 * 2 - 1
            x = (x0 + x1) / 2 + u * (x1 - x0) / 2
            y = gy + depth * (1 - u * u) * pr
            pts.append((x, y))
        d.polygon(pts, fill=(14, 18, 30, 255))
        d.line(pts, fill=(200, 150, 100, 255), width=4)
        if t - tb < 0.6: flash(im, 0.8 * math.exp(-(t - tb) * 6))
    a = pop(t, s(0))
    pill(d, (360, 120), 'IRON · ≈ 50 METERS', 46, GOLD, alpha=a)
    pill(d, (360, 215), '≈ 50,000 YEARS AGO · ARIZONA', 34, WHITE, alpha=a)
    a = pop(t, s(1) + 0.6)
    if a > 0:
        d.line((x0, gy - 40, x1, gy - 40), fill=(255, 205, 90, int(255 * a)), width=4)
        d.line((x0, gy - 55, x0, gy - 25), fill=(255, 205, 90, int(255 * a)), width=4)
        d.line((x1, gy - 55, x1, gy - 25), fill=(255, 205, 90, int(255 * a)), width=4)
        text(d, ((x0 + x1) / 2, gy - 100), '1.2 KM WIDE', 80, GOLD, alpha=a)
        text(d, (x1 + 130, gy + depth / 2), '≈ 180 m', 44, WHITE, alpha=pop(t, s(1) + 2.5))
        d.line((x1 + 30, gy, x1 + 30, gy + depth), fill=(255, 255, 255, int(255 * pop(t, s(1) + 2.5))), width=3)
    a = pop(t, s(2))
    if a > 0:
        fw = 120 * 0.9144 / mpp
        n = int(1200 / (120 * 0.9144))
        for i in range(n + 1):
            frac = min(1, 1200 / (120 * 0.9144) - i)
            xa = x0 + i * fw; xb = xa + fw * frac
            if frac <= 0: break
            d.rectangle((xa + 1, 600, xb - 1, 640), fill=(60, 150, 70, int(255 * a)), outline=(255, 255, 255, int(255 * a)))
        text(d, ((x0 + x1) / 2, 870), '≈ 11 FOOTBALL FIELDS ACROSS', 60, WHITE, alpha=a)
        rr = 25 / mpp
        paste_c(im, sprite(('ast', int(rr), 41, 'i'), lambda: make_asteroid(int(rr), 41, True)), x0 + fw / 2, 700)
        text(d, (x0 + fw / 2 + 50, 700), 'the rock', 30, GOLD, POP_B, anchor='lm', alpha=a)
    note(d, 'drawn to scale', pop(t, s(1)))
    a = pop(t, s(3))
    text(d, (W / 2, 330), 'STILL NOT THE SCARIEST SIZE', 84, RED, alpha=a)

def eiffel(d, x, base, h, col=(170, 160, 150, 255)):
    w = h * 0.38
    pts = [(x - w / 2, base), (x - w * 0.12, base - h * 0.55), (x - 3, base - h), (x + 3, base - h), (x + w * 0.12, base - h * 0.55), (x + w / 2, base)]
    d.polygon(pts, fill=col)
    d.polygon([(x - w * 0.3, base), (x, base - h * 0.25), (x + w * 0.3, base)], fill=(10, 12, 20, 255))
    d.line((x - w * 0.28, base - h * 0.28, x + w * 0.28, base - h * 0.28), fill=col, width=6)
    d.line((x - w * 0.16, base - h * 0.55, x + w * 0.16, base - h * 0.55), fill=col, width=5)

def sc_apophis(sc, t, im, d):
    s = sc.s
    a_cmp = 1 - pop(t, s(1) - 0.2)
    if a_cmp > 0.01:
        base = 900; mpp = 330 / 640  # Eiffel 330 m tall -> 640 px
        d.rectangle((0, base, W, H), fill=(20, 24, 34, 255))
        eiffel(d, 650, base, 330 / mpp)
        r = 170 / mpp
        paste_c(im, sprite(('ast', int(r), 51), lambda: make_asteroid(int(r), 51)), 1250, base - r - 6)
        text(d, (650, 200), 'EIFFEL TOWER ≈ 330 m', 48, WHITE, alpha=pop(t, 0.3))
        text(d, (1250, 200), 'APOPHIS ≈ 340 m', 60, GOLD, alpha=pop(t, 0.1))
        note(d, 'to scale')
    if t > s(1) - 0.2:
        Rpx = 120; cx, cy = 300, 560
        p = 0.44 + 0.12 * ramp(t, s(1), sc.dur)
        geo, ap = orbit_diagram(im, d, t, cx, cy, Rpx, True, p, labels=True, la=pop(t, s(1)), big=True)
        a = pop(t, s(1))
        text(d, (1480, 210), 'APOPHIS: ≈ 32,000 km', 72, GOLD, alpha=a)
        text(d, (1480, 290), 'above Earth\'s surface', 44, WHITE, POP_B, alpha=a)
        a = pop(t, s(2))
        text(d, (1480, 380), 'SATELLITES: ≈ 36,000 km', 60, CYAN, alpha=a)
        a = pop(t, s(3))
        pill(d, (1480, 490), 'VISIBLE WITHOUT A TELESCOPE', 40, WHITE, alpha=a)
        text(d, (1480, 555), 'from places like Europe & Africa', 36, GREY, POP_B, alpha=a)
        a = pop(t, s(4))
        pill(d, (1480, 650), '≈ ONCE EVERY FEW THOUSAND YEARS', 40, GOLD, alpha=a)
        a = pop(t, s(5))
        pill(d, (1480, 760), 'NASA: NO RISK FOR 100+ YEARS', 46, GREEN, alpha=a)
        note(d, 'distances to scale · asteroid enlarged', pop(t, s(1)))

def sc_global(sc, t, im, d):
    s = sc.s
    # 1 km vs 340 m vs 20 m to scale, on a ground line
    base = 760; mpp = 1000 / 520
    d.rectangle((0, base, W, H), fill=(20, 24, 34, 255))
    r1 = 500 / mpp; ra = 170 / mpp; rc = 10 / mpp
    a = pop(t, 0.1)
    paste_c(im, sprite(('ast', int(r1), 61), lambda: make_asteroid(int(r1), 61)), 1180, base - r1 - 4)
    paste_c(im, sprite(('ast', int(ra), 51), lambda: make_asteroid(int(ra), 51)), 640, base - ra - 4)
    paste_c(im, sprite(('ast', max(3, int(rc)), 21), lambda: make_asteroid(max(3, int(rc)), 21)), 380, base - rc - 4)
    text(d, (1180, 120), '1 KM', 100, RED, alpha=a)
    text(d, (640, 430), '340 m', 48, GOLD, alpha=a)
    text(d, (380, 690), '20 m', 36, WHITE, alpha=a)
    note(d, 'to scale')
    a = pop(t, s(1))
    pill(d, (1180, 840), 'NASA: COULD HAVE GLOBAL EFFECTS', 44, RED, WHITE, alpha=a * (1 - pop(t, s(2))))
    a = pop(t, s(2))
    pill(d, (W / 2, 840), '> 90% OF THESE ALREADY FOUND', 46, GREEN, alpha=a * (1 - pop(t, s(3))))
    a = pop(t, s(3))
    pill(d, (W / 2, 840), 'NO KNOWN ASTEROID OVER 140 m: SIGNIFICANT RISK IN NEXT 100 YEARS', 32, GREEN, alpha=a)

def everest(d, x, base, h, w):
    pts = [(x - w / 2, base), (x - w * 0.18, base - h * 0.62), (x - w * 0.06, base - h * 0.8), (x, base - h), (x + w * 0.1, base - h * 0.78),
           (x + w * 0.22, base - h * 0.7), (x + w / 2, base)]
    d.polygon(pts, fill=(110, 115, 130, 255))
    d.polygon([(x - w * 0.08, base - h * 0.78), (x, base - h), (x + w * 0.1, base - h * 0.78), (x + w * 0.02, base - h * 0.72)], fill=(240, 245, 255, 255))

def sc_chix(sc, t, im, d):
    s = sc.s
    base = 940; mpp = 15000 / 760  # 15 km -> 760 px
    a_side = 1 - pop(t, s(3) - 0.2)
    if a_side > 0.01:
        d.rectangle((0, base, W, H), fill=(20, 24, 34, 255))
        everest(d, 560, base, 8849 / mpp, 900)
        r10 = 5000 / mpp
        paste_c(im, sprite(('ast', int(r10), 71), lambda: make_asteroid(int(r10), 71)), 1320, base - r10 * 1.16 - 4, rot=90)
        r15 = 7500 / mpp
        if t > s(1):
            for k in range(0, 360, 6):
                d.arc((1320 - r15, base - 2 * r15 - 4, 1320 + r15, base - 4), k, k + 3, fill=(255, 205, 90, 200), width=3)
        text(d, (560, base - 8849 / mpp - 50), 'EVEREST 8.8 km', 46, WHITE, alpha=pop(t, s(2)))
        text(d, (1320, 120), '10–15 KM WIDE', 84, RED, alpha=pop(t, s(1)))
        pill(d, (300, 120), '≈ 66 MILLION YEARS AGO', 36, GOLD, alpha=pop(t, s(1)))
        note(d, 'to scale', pop(t, s(1)))
        if t < s(1):
            text(d, (W / 2, 520), 'THE BIG ONE', 150, RED, alpha=pop(t, 0.0))
    if t > s(3) - 0.2:
        Rg = 330; cx, cy = 620, 560
        paste_c(im, sprite(('globe', Rg, 2.2), lambda: make_globe(Rg, 2.2)), cx, cy)
        k = t - (s(3) - 0.2)
        ix, iy = cx - 40, cy - 60
        add_glow(im, ix, iy, int(60 + 140 * min(k / 2, 1)), (255, 150, 60), min(1, k * 2))
        flash(im, 0.7 * math.exp(-k * 5))
        a = pop(t, s(3))
        text(d, (1420, 200), 'CRATER', 70, WHITE, alpha=a)
        text(d, (1420, 300), '≈ 150–180 KM', 96, GOLD, alpha=a)
        a = pop(t, s(4))
        text(d, (1420, 450), 'BILLIONS ×', 80, ORANGE, alpha=a)
        text(d, (1420, 540), 'HIROSHIMA', 80, ORANGE, alpha=a)
        a = pop(t, s(5))
        text(d, (1420, 700), '≈ 3 IN 4 SPECIES', 72, RED, alpha=a)
        text(d, (1420, 790), 'GONE', 90, RED, alpha=a)
        text(d, (1420, 880), '(birds made it)', 40, WHITE, POP_B, alpha=pop(t, s(5) + 3.5))

def sc_dart(sc, t, im, d):
    s = sc.s
    cx, cy = 900, 560
    paste_c(im, sprite(('ast', 150, 81), lambda: make_asteroid(150, 81)), cx, cy, rot=t * 6)
    tb = s(1) + 3.2
    orbit_r = 360
    per = 6.0 if t < tb else 5.6
    ang = t / per * 2 * math.pi
    for k in range(0, 360, 4):
        d.arc((cx - orbit_r, cy - orbit_r * 0.35, cx + orbit_r, cy + orbit_r * 0.35), k, k + 2, fill=(150, 190, 255, 140), width=2)
    mx, my = cx + orbit_r * math.cos(ang), cy + orbit_r * 0.35 * math.sin(ang)
    paste_c(im, sprite(('ast', 34, 82), lambda: make_asteroid(34, 82)), mx, my, rot=t * 20)
    if s(1) < t < tb:
        p = ease(ramp(t, s(1), tb))
        sx, sy = 1900 + (mx - 1900) * p, 120 + (my - 120) * p
        d.rectangle((sx - 10, sy - 6, sx + 10, sy + 6), fill=(230, 230, 240, 255))
        d.rectangle((sx - 30, sy - 2, sx + 30, sy + 2), fill=(80, 130, 220, 255))
    if t >= tb:
        k = t - tb
        add_glow(im, mx, my, int(80 + 60 * min(k, 1)), (255, 230, 170), max(0, 1 - k * 0.6))
        flash(im, 0.6 * math.exp(-k * 6))
    pill(d, (300, 120), 'NASA DART · 2022', 44, GOLD, alpha=pop(t, s(1)))
    text(d, (mx, my + 62), '≈ 160 m', 36, WHITE, alpha=pop(t, s(1) + 2))
    a = pop(t, s(2))
    text(d, (1480, 320), 'ORBIT: 11 h 55 min → 11 h 23 min', 50, WHITE, alpha=a)
    text(d, (1480, 420), '− 32 MINUTES', 100, GREEN, alpha=a)
    a = pop(t, s(3))
    pill(d, (W / 2, 200), 'FIRST TIME HUMANS MOVED A NATURAL SPACE OBJECT ON PURPOSE', 36, GREEN, alpha=a)
    note(d, 'not to scale')

def sc_outro(sc, t, im, d):
    s = sc.s
    rows = [('20 m', 'shatters a city\'s windows', WHITE), ('50–100 m', 'flattens a forest', GOLD), ('1 km', 'global effects', ORANGE), ('10 km', 'ends an age', RED)]
    a_l = 1 - pop(t, s(2) - 0.2)
    text(d, (W / 2, 120), 'THE WHOLE LADDER', 80, WHITE, alpha=pop(t, 0.1) * a_l)
    for i, (sz, eff, col) in enumerate(rows):
        a = pop(t, s(1) + i * 1.6) * a_l
        y = 300 + i * 160; r = 14 + i * 22
        if a > 0.3:
            paste_c(im, sprite(('ast', r, 90 + i), lambda: make_asteroid(r, 90 + i)), 420, y)
        text(d, (700, y), sz, 70, col, anchor='lm', alpha=a)
        text(d, (1120, y), eff, 56, WHITE, POP_B, anchor='lm', alpha=a)
    note(d, 'sizes not to scale', pop(t, s(1)) * a_l)
    a = pop(t, s(2))
    text(d, (W / 2, 300), 'WHICH SIZE SCARES', 110, WHITE, alpha=a)
    text(d, (W / 2, 430), 'YOU THE MOST?', 120, GOLD, alpha=a)
    text(d, (W / 2, 550), '20 m · 50 m · 340 m · 1 km · 10 km 👇'.replace(' 👇', ''), 52, CYAN, alpha=a)
    a = pop(t, s(3))
    pill(d, (W / 2, 690), 'SEND THIS TO YOUR APOPHIS-WATCHING BUDDY · APRIL 13, 2029', 36, RED, WHITE, alpha=a)
    a = pop(t, s(4))
    if a > 0:
        f = F(BLACK, 54); w = f.getlength('SUBSCRIBE') + 90
        d.rounded_rectangle((W / 2 - w / 2, 790, W / 2 + w / 2, 880), 45, fill=(220, 30, 40, int(255 * a)))
        text(d, (W / 2, 835), 'SUBSCRIBE', 54, WHITE, alpha=a, stroke=0)
        text(d, (W / 2, 925), 'Explorer Man', 40, GOLD, POP_B, alpha=a)

FUN = dict(hook=sc_hook, sand=sc_sand, chel=sc_chel, tung=sc_tung, crater=sc_crater, apophis=sc_apophis,
           glob=None, chix=sc_chix, dart=sc_dart, outro=sc_outro)
FUN['global'] = sc_global

def chapter_pill(d, label, a):
    if a <= 0.01: return
    f = F(POP_B, 30); w = f.getlength(label) + 50
    d.rounded_rectangle((W - 60 - w, 40, W - 60, 94), 27, fill=(255, 255, 255, int(40 * a)), outline=(255, 205, 90, int(200 * a)), width=2)
    d.text((W - 60 - w / 2, 67), label, font=f, fill=(255, 205, 90, int(255 * a)), anchor='mm')

def build_scenes():
    idx = json.load(open('aud/index.json'))
    out = []
    for i, (key, ch, _) in enumerate(SCENES):
        ss = [x for x in idx if x['scene'] == key]
        out.append(Scene(key, ch, ss, 0.0 if i == 0 else 0.15))
    return out

def frame(sc, t):
    im = BG.copy()
    d = ImageDraw.Draw(im, 'RGBA')
    FUN[sc.key](sc, t, im, d)
    d = ImageDraw.Draw(im, 'RGBA')
    if sc.key not in ('hook',):
        chapter_pill(d, sc.chapter, pop(t, 0.0, 0.2) * (1 - pop(t, 3.5, 0.5)))
    draw_caption(d, sc.cap_at(t))
    return im.convert('RGB')

if __name__ == '__main__':
    scenes = build_scenes()
    mode = sys.argv[1]
    if mode == 'still':
        name, tt = sys.argv[2], float(sys.argv[3])
        sc = [x for x in scenes if x.key == name][0]
        frame(sc, tt).save(f'still_{name}_{tt}.jpg', quality=88)
    elif mode == 'scene':
        name = sys.argv[2]
        sc = [x for x in scenes if x.key == name][0]
        os.makedirs('scenes', exist_ok=True)
        n = int(round(sc.dur * FPS)); tmp = f'scenes/{name}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(frame(sc, i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'scenes/{name}.mp4')
        print(name, n, rc)
    elif mode == 'timing':
        t = 0
        for sc in scenes:
            print(f'{int(t // 60)}:{int(t % 60):02d} {sc.chapter} ({sc.dur:.1f}s)'); t += sc.dur
        print('total', t)

import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
START, END = 0.15, 1.0
POP_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
POP_M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]
WHITE = (255, 255, 255); GOLD = (255, 205, 90); CYAN = (90, 215, 255); RED = (255, 85, 85); GREY = (175, 185, 205)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return min(max((t - a) / (b - a), 0), 1)

AUD = json.load(open('aud.json')); LINES = json.load(open('lines.json'))
T0 = []; _t = START
for a in AUD:
    T0.append(_t); _t += a['dur'] + a['pause']
TOTAL = _t + END
KEYS = [l['key'] for l in LINES]
def st(k): return T0[KEYS.index(k)]
def en(k): i = KEYS.index(k); return T0[i] + AUD[i]['dur']
def nx(k):
    i = KEYS.index(k); return T0[i + 1] if i + 1 < len(T0) else TOTAL

# ---------------------------------------------------------------- background: deep space
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
k = (yy / H)[..., None]
sky = np.array([0.01, 0.015, 0.05]) * (1 - k) + np.array([0.03, 0.03, 0.09]) * k
neb = np.exp(-(((xx - 300) / 500) ** 2 + ((yy - 700) / 380) ** 2))[..., None] * np.array([0.10, 0.04, 0.14])
neb += np.exp(-(((xx - 850) / 420) ** 2 + ((yy - 1300) / 300) ** 2))[..., None] * np.array([0.02, 0.07, 0.12])
BGA = np.clip(sky + neb, 0, 1)
for _ in range(1100):
    x, y = rng.integers(0, W), rng.integers(0, H)
    BGA[y, x] += rng.uniform(0.15, 0.8)
for _ in range(60):
    x, y = rng.integers(1, W - 1), rng.integers(1, H - 1)
    BGA[y - 1:y + 2, x - 1:x + 2] += rng.uniform(0.2, 0.5)
BG = Image.fromarray((np.clip(BGA, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

# night sky over land (for shower scenes)
skyn = np.array([0.02, 0.03, 0.09]) * (1 - k) + np.array([0.07, 0.08, 0.17]) * k
NA = np.clip(skyn, 0, 1).copy()
for _ in range(900):
    x, y = rng.integers(0, W), rng.integers(0, 1500)
    NA[y, x] += rng.uniform(0.15, 0.7)
NIGHT = Image.fromarray((np.clip(NA, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
_d = ImageDraw.Draw(NIGHT)
pts = [(0, 1560)]
for i in range(0, W + 60, 60):
    pts.append((i, 1560 - 60 * math.sin(i / 170) - 35 * math.sin(i / 53 + 1) - 40))
pts += [(W, H), (0, H)]
_d.polygon(pts, fill=(6, 7, 12, 255))
# a few pine trees
for tx_, th_ in ((90, 150), (160, 110), (880, 170), (960, 130), (1030, 150)):
    base = 1560 - 60 * math.sin(tx_ / 170) - 35 * math.sin(tx_ / 53 + 1) - 40
    _d.polygon([(tx_, base - th_), (tx_ - th_ * 0.28, base + 5), (tx_ + th_ * 0.28, base + 5)], fill=(4, 5, 9, 255))
LAND_Y = 1520

def text(d, xy, s, size, col=WHITE, font=BLACK, anchor='mm', stroke=None, alpha=1.0):
    if alpha <= 0.004: return
    if stroke is None: stroke = max(4, size // 11)
    f = F(font, size)
    if alpha >= 0.999:
        d.text(xy, s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 6, 16, 255)); return
    x0, y0, x1, y1 = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
    x0, y0 = max(0, int(x0) - 2), max(0, int(y0) - 2)
    lay = Image.new('RGBA', (int(x1) - x0 + 4, int(y1) - y0 + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0] - x0, xy[1] - y0), s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 6, 16, 255))
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
    d._image.alpha_composite(lay, (x0, y0))

def pop(t, a, dur=0.25):
    """scale-pop factor for text entrance"""
    p = ramp(t, a, a + dur); return ease(p)

def ptext(d, xy, s, size, col, t, a, b, font=BLACK, stroke=None):
    """text visible from a to b with a pop-in (size grows from 80%)"""
    al = xf(t, a, b, 0.18, 0.2)
    if al <= 0: return
    sc = 0.8 + 0.2 * pop(t, a, 0.22)
    text(d, xy, s, max(8, int(size * sc)), col, font, stroke=stroke, alpha=al)

def pill(d, cx, cy, s, size, bg, fg=WHITE, alpha=1.0):
    if alpha <= 0.004: return
    f = F(BLACK, size); w = f.getlength(s) + size * 1.4; h = size * 1.7
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=tuple(bg) + (int(255 * alpha),))
    text(d, (cx, cy), s, size, fg, BLACK, stroke=0, alpha=alpha)

def fade(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a))); return im

def paste_c(im, spr, cx, cy, alpha=1.0):
    if alpha <= 0.004: return
    im.alpha_composite(fade(spr, alpha), (int(cx - spr.width / 2), int(cy - spr.height / 2)))

def xf(t, a, b, fi=0.25, fo=0.25):
    return ease(ramp(t, a, a + fi)) * (1 - ease(ramp(t, b - fo, b)))

CACHE = {}
def sp(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]

# ---------------------------------------------------------------- sprites
def sphere(R, base, seed=0, land=None, atmo=None, rough=0.0):
    SS = 2; r = R * SS; n = int(2 * r + 8 * SS)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
    u = (x - c) / r; v = (y - c) / r; rr = u * u + v * v
    inside = rr <= 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    L = np.array([-0.55, -0.45, 0.70]); L /= np.linalg.norm(L)
    lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
    col = np.ones((n, n, 3), np.float32) * np.array(base)
    rg = np.random.default_rng(seed)
    if land is not None or rough > 0:
        g = rg.random((24, 24)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        g2 = rg.random((70, 70)).astype(np.float32)
        g2 = np.array(Image.fromarray((g2 * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        nn = 0.7 * g + 0.3 * g2
        if land is not None:
            m = nn > 0.6
            col[m] = np.array(land) * (0.8 + 0.4 * nn[m, None])
            cl = (g2 > 0.74)
            col[cl] = col[cl] * 0.55 + 0.45
        if rough > 0:
            col *= (1 - rough + rough * 1.6 * nn[..., None])
    col = col * (0.06 + 0.94 * lam[..., None])
    a = inside.astype(np.float32)
    rgb = col
    if atmo is not None:
        edge = np.clip(1 - np.abs(np.sqrt(rr) - 1) / 0.06, 0, 1) * (np.sqrt(rr) < 1.06)
        rgb = np.where(inside[..., None], rgb + np.array(atmo) * (1 - z[..., None]) ** 2 * 0.8 * lam[..., None] ** 0.3, np.array(atmo) * np.ones_like(rgb))
        a = np.maximum(a, edge * 0.7 * (np.sqrt(rr) >= 1))
    arr = np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)

def earth(R): return sp(('earth', R), lambda: sphere(R, (0.10, 0.30, 0.75), 3, land=(0.25, 0.55, 0.25), atmo=(0.4, 0.7, 1.0)))
def moonsp(R): return sp(('moon', R), lambda: sphere(R, (0.72, 0.72, 0.70), 5, rough=0.5))

def glow(R, col, power=2.0):
    def mk():
        n = int(R * 2); y, x = np.mgrid[0:n, 0:n].astype(np.float32)
        r = np.sqrt((x - n / 2) ** 2 + (y - n / 2) ** 2) / (n / 2)
        a = np.clip(1 - r, 0, 1) ** power
        arr = np.zeros((n, n, 4), np.float32); arr[..., :3] = np.array(col) / 255; arr[..., 3] = a
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('glow', R, col, power), mk)

def streak(im, x0, y0, ang, length, width, alpha, col=(255, 240, 210), head=True):
    """meteor streak: head at (x0,y0), tail going back along -ang direction"""
    if alpha <= 0.01 or length < 2: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    dx, dy = math.cos(ang), math.sin(ang)
    N = 18
    for i in range(N):
        f0, f1 = i / N, (i + 1) / N
        a = (1 - f0) ** 1.6
        d.line((x0 - dx * length * f0, y0 - dy * length * f0, x0 - dx * length * f1, y0 - dy * length * f1),
               fill=(col[0], col[1], int(col[2] * (0.8 + 0.2 * a)), int(255 * alpha * a)), width=max(1, int(width * (1 - 0.7 * f0))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(width * 0.35)))
    im.alpha_composite(lay)
    if head:
        paste_c(im, glow(width * 5, (255, 235, 200), 1.6), x0, y0, alpha)

def grain(im, cx, cy, r, alpha=1.0, hot=0.0):
    """a sand grain: irregular tan blob, optional hot glow"""
    def mk():
        n = 64; img = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        rg = np.random.default_rng(11); pts = []
        for i in range(14):
            a = 2 * math.pi * i / 14; rr_ = 24 * (0.8 + 0.3 * rg.random())
            pts.append((32 + rr_ * math.cos(a), 32 + rr_ * math.sin(a)))
        d.polygon(pts, fill=(205, 170, 115, 255))
        d.ellipse((18, 16, 34, 30), fill=(240, 215, 165, 255))
        return img.filter(ImageFilter.GaussianBlur(1.2))
    g = sp('grain', mk); s = max(2, int(r * 2 * 64 / 52))
    if hot > 0: paste_c(im, glow(r * 7, (255, 170, 80), 1.5), cx, cy, alpha * hot)
    paste_c(im, g.resize((s, s), Image.LANCZOS), cx, cy, alpha)

def bar(d, x0, y, wmax, frac, col, alpha, h=80):
    if alpha <= 0.004: return
    d.rounded_rectangle((x0, y, x0 + wmax, y + h), 16, outline=(120, 128, 150, int(255 * alpha)), width=3)
    if frac > 0.01: d.rounded_rectangle((x0, y, x0 + wmax * frac, y + h), 16, fill=tuple(col) + (int(255 * alpha),))

def car_icon(d, x, y, s, col, alpha):
    a = int(255 * alpha); c = tuple(col) + (a,)
    d.rounded_rectangle((x, y + 0.35 * s, x + 2.2 * s, y + 0.8 * s), 0.12 * s, fill=c)
    d.polygon([(x + 0.45 * s, y + 0.36 * s), (x + 0.75 * s, y), (x + 1.55 * s, y), (x + 1.85 * s, y + 0.36 * s)], fill=c)
    for wx in (0.5, 1.7):
        d.ellipse((x + (wx - 0.22) * s, y + 0.6 * s, x + (wx + 0.22) * s, y + 1.04 * s), fill=(20, 20, 26, a), outline=c, width=4)

# storm meteors (deterministic list): (t_start, x, y, angle, length)
RAD = (W * 0.62, 260)   # radiant (in Leo), on screen
def storm_list(t0, t1, rate, seed):
    r = np.random.default_rng(seed); out = []; t = t0
    while t < t1:
        t += r.exponential(1 / rate)
        a = r.uniform(0, 2 * math.pi); d0 = r.uniform(60, 500)
        out.append((t, a, d0, r.uniform(120, 380), r.uniform(0.45, 1.0)))
    return out
STORM = None

def draw_storm(im, t, t0, t1, rate, seed, alpha=1.0, wmul=1.0):
    key = ('storm', t0, t1, rate, seed)
    L = sp(key, lambda: storm_list(t0, t1, rate, seed))
    for ts, a, d0, ln, br in L:
        age = t - ts
        if age < 0 or age > 0.45: continue
        p = age / 0.45
        dist = d0 + ln * (0.3 + p)
        hx = RAD[0] + math.cos(a) * dist; hy = RAD[1] + math.sin(a) * dist
        if hy > LAND_Y + 40: continue
        streak(im, hx, hy, a, ln * min(1, age / 0.12) * 0.9, 5 * wmul, alpha * br * (1 - p) ** 0.7, head=False)

# ---------------------------------------------------------------- frame
def frame(t):
    keys = KEYS
    # pick background: night for storm..end except reveal
    im = BG.copy()
    night_a = max(xf(t, st('storm') - 0.2, st('reveal') + 0.05, 0.3, 0.3), xf(t, st('star') - 0.2, TOTAL + 1, 0.3, 0.01) * (1 - ease(ramp(t, st('loop') - 0.1, st('loop') + 0.4))))
    if night_a > 0: im.alpha_composite(fade(NIGHT, night_a))
    d = ImageDraw.Draw(im, 'RGBA')

    # ============ hook + loop: grain hurtling towards Earth
    for k0, k1, isloop in (('hook', 'again', False), ('loop', None, True)):
        a0 = st(k0); a1 = nx(k0) if k1 else TOTAL + 1
        a_h = xf(t, a0 - (0.2 if isloop else 0), a1, 0.3 if isloop else 0.01, 0.25)
        if a_h <= 0: continue
        er = 760; ex, ey = W / 2, H + 380
        paste_c(im, earth(er), ex, ey, a_h)
        if isloop:
            p = ramp(t, a0, a1 - 0.2)
        else:
            p = ramp(t, a0, a1 + (en('loop') - st('loop')) * 0)   # same motion as loop
        # grain travels diagonally down from top-right towards Earth's limb
        p2 = ((t - a0) / 6.0) % 1.0
        gx = 900 - 520 * p2; gy = 560 + 520 * p2
        streak(im, gx, gy, math.atan2(520, -520), 340, 9, a_h * 0.9, col=(255, 210, 160), head=False)
        grain(im, gx, gy, 40 + 6 * math.sin(t * 9), a_h, hot=0.7)
        d = ImageDraw.Draw(im, 'RGBA')
        if not isloop:
            ptext(d, (W / 2, 230), 'A GRAIN OF SAND', 104, WHITE, t, a0, a1)
            ptext(d, (W / 2, 370), 'HITS EARTH AT', 84, WHITE, t, a0 + 0.9, a1)
            ptext(d, (W / 2, 540), '71 KM/S', 200, GOLD, t, a0 + 2.6, a1)
            ptext(d, (W / 2, 700), 'WHAT HAPPENS?', 96, CYAN, t, a0 + 3.9, a1)
        else:
            ptext(d, (W / 2, 230), 'MOST LEONIDS', 110, WHITE, t, a0, a1)
            ptext(d, (W / 2, 370), '= GRAINS OF SAND', 96, GOLD, t, a0 + 2.2, a1)
            ptext(d, (W / 2, 540), '71 KM/S', 200, GOLD, t, a0 + 4.2, a1)

    # ============ again: several faint meteors, THIS WEEK
    a_g = xf(t, st('again'), nx('again'))
    if a_g > 0:
        er = 760; paste_c(im, earth(er), W / 2, H + 380 + 120 * ease(ramp(t, st('again'), nx('again'))), a_g)
        for i, (ox, oy) in enumerate(((800, 500), (980, 820), (650, 380), (1000, 300))):
            q = ((t - st('again')) * 0.9 + i * 0.27) % 1.0
            streak(im, ox - 420 * q, oy + 420 * q, math.atan2(1, -1), 200, 5, a_g * (1 - q), col=(255, 220, 180))
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 330), 'THIS WEEK', 140, WHITE, t, st('again'), nx('again'))
        ptext(d, (W / 2, 480), 'AGAIN & AGAIN', 104, GOLD, t, st('again') + 1.2, nx('again'))

    # ============ speed: speedometer
    a_s = xf(t, st('speed'), nx('speed'))
    if a_s > 0:
        p = ease(ramp(t, st('speed') + 0.1, st('speed') + 1.6))
        cx, cy, R = W / 2, 1050, 380
        d.arc((cx - R, cy - R, cx + R, cy + R), 150, 390, fill=(70, 80, 110, int(255 * a_s)), width=40)
        d.arc((cx - R, cy - R, cx + R, cy + R), 150, 150 + 240 * p * 71 / 80, fill=GOLD + (int(255 * a_s),), width=40)
        ang = math.radians(150 + 240 * p * 71 / 80)
        d.line((cx, cy, cx + (R - 70) * math.cos(ang), cy + (R - 70) * math.sin(ang)), fill=(255, 90, 80, int(255 * a_s)), width=14)
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(230, 230, 240, int(255 * a_s)))
        for i in range(0, 81, 10):
            aa = math.radians(150 + 240 * i / 80)
            text(d, (cx + (R + 70) * math.cos(aa), cy + (R + 70) * math.sin(aa)), str(i), 40, GREY, POP_B, stroke=3, alpha=a_s)
        text(d, (cx, cy + 190), f'{int(round(71 * p))}', 170, GOLD, alpha=a_s)
        text(d, (cx, cy + 300), 'km per SECOND', 54, WHITE, POP_B, alpha=a_s)
        ptext(d, (W / 2, 240), '71 KILOMETERS', 116, WHITE, t, st('speed'), nx('speed'))
        ptext(d, (W / 2, 380), 'EVERY SECOND', 116, GOLD, t, st('speed') + 1.3, nx('speed'))
        ptext(d, (W / 2, 1610), '= 255,600 km/h', 76, CYAN, t, st('speed') + 1.9, nx('speed'))

    # ============ nyla
    a_n = xf(t, st('nyla'), nx('nyla'))
    if a_n > 0:
        y = 950; xa, xb = 860, 220
        d.line((xb, y, xa, y), fill=(90, 100, 140, int(255 * a_n)), width=10)
        p = ease(ramp(t, st('nyla') + 0.5, st('nyla') + 1.8))
        xg = xa + (xb - xa) * p
        d.line((xg, y, xa, y), fill=GOLD + (int(255 * a_n),), width=10)
        for x_, lab in ((xa, 'NEW YORK'), (xb, 'LOS ANGELES')):
            d.ellipse((x_ - 22, y - 22, x_ + 22, y + 22), fill=(255, 90, 80, int(255 * a_n)))
            text(d, (x_, y + 80), lab, 46, WHITE, alpha=a_n)
        streak(im, xg, y, 0 + math.pi, 220 * (1 - p * 0.3), 7, a_n * (1 if p < 1 else 0.0), col=(255, 220, 170))
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, y - 90), '≈ 3,940 km', 64, GREY, POP_B, alpha=a_n)
        ptext(d, (W / 2, 260), 'NEW YORK → L.A.', 100, WHITE, t, st('nyla'), nx('nyla'))
        ptext(d, (W / 2, 420), 'IN UNDER', 92, WHITE, t, st('nyla') + 1.4, nx('nyla'))
        ptext(d, (W / 2, 560), '1 MINUTE', 150, GOLD, t, st('nyla') + 1.6, nx('nyla'))
        ptext(d, (W / 2, 1300), '(about 55 seconds)', 54, CYAN, t, st('nyla') + 1.9, nx('nyla'), font=POP_B)

    # ============ moon (to scale): Earth dia 12,742 km, distance 384,400 km
    a_m = xf(t, st('moon'), nx('moon'))
    if a_m > 0:
        x0 = 90; x1 = 990; s = (x1 - x0) / 384400
        er = 12742 / 2 * s; mr = 3474.8 / 2 * s
        y = 1000
        paste_c(im, earth(max(4, int(er))), x0, y, a_m)
        paste_c(im, moonsp(max(3, int(mr))), x1, y, a_m)
        d = ImageDraw.Draw(im, 'RGBA')
        for xq in range(int(x0 + er + 10), int(x1 - mr - 10), 26):
            d.line((xq, y, xq + 12, y), fill=(120, 130, 170, int(200 * a_m)), width=3)
        p = ease(ramp(t, st('moon') + 0.4, en('moon') + 0.2))
        gx = x0 + er + (x1 - mr - x0 - er) * p
        streak(im, gx, y, 0, 160, 6, a_m * (1 if p < 1 else 0), col=(255, 220, 170))
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (x0, y + 70), 'EARTH', 42, WHITE, alpha=a_m)
        text(d, (x1 - 10, y + 70), 'MOON', 42, WHITE, alpha=a_m)
        text(d, (W / 2, y + 160), '384,400 km · drawn to scale', 40, GREY, POP_M, stroke=3, alpha=a_m)
        ptext(d, (W / 2, 280), 'TO THE MOON IN', 92, WHITE, t, st('moon'), nx('moon'))
        ptext(d, (W / 2, 440), '~1.5 HOURS', 150, GOLD, t, st('moon') + 1.8, nx('moon'))
        hrs = 1.5 * p
        text(d, (W / 2, 1400), f'{int(hrs)}:{int((hrs % 1) * 60):02d} h', 90, CYAN, alpha=a_m)

    # ============ comet orbit
    a_c = xf(t, st('comet'), nx('comet'))
    a_tr = xf(t, st('trail'), nx('trail'))
    a_o = max(a_c, a_tr)
    if a_o > 0:
        cx, cy = 360, 1150
        paste_c(im, glow(170, (255, 210, 120), 1.4), cx, cy, a_o)
        d = ImageDraw.Draw(im, 'RGBA')
        d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(255, 235, 170, int(255 * a_o)))
        # comet ellipse: perihelion near Sun (left), aphelion far right/off-screen; tilted
        A, ecc = 870, 0.7; B = 330
        foc = A * ecc
        tilt = math.radians(-22)
        def orb(th):
            x_ = foc + A * math.cos(th) * -1 + 0; y_ = B * math.sin(th)
            # place so that perihelion (th=0 -> x=foc-A) is near Sun
            xr = x_ * math.cos(tilt) - y_ * math.sin(tilt); yr = x_ * math.sin(tilt) + y_ * math.cos(tilt)
            return cx - xr * -1 - 0, cy + yr
        P = [orb(2 * math.pi * i / 240) for i in range(241)]
        d.line(P, fill=(120, 140, 190, int(150 * a_o)), width=3)
        # debris dots along orbit (grow in trail scene)
        rg = np.random.default_rng(2)
        nd = int(60 + 260 * a_tr)
        for i in range(nd):
            th = rg.uniform(-1.3, 1.3); px, py = orb(th)
            px += rg.normal(0, 9); py += rg.normal(0, 9)
            d.ellipse((px - 2.5, py - 2.5, px + 2.5, py + 2.5), fill=(230, 200, 150, int(200 * a_o)))
        # comet moving along orbit
        th = 0.9 - 1.8 * ramp(t, st('comet'), nx('trail'))
        px, py = orb(th)
        tx_, ty_ = px - cx, py - cy; ln = math.hypot(tx_, ty_)
        ang_tail = math.atan2(ty_, tx_)
        streak(im, px + math.cos(ang_tail) * 0, py, ang_tail + math.pi, 150, 14, a_c * 0.9, col=(170, 220, 255), head=False)
        paste_c(im, glow(40, (200, 235, 255), 1.3), px, py, a_o)
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (cx, cy + 90), 'SUN', 40, GOLD, alpha=a_o)
        # Earth's orbit (trail scene) crossing debris
        if a_tr > 0:
            ER = 260
            d.ellipse((cx - ER, cy - ER, cx + ER, cy + ER), outline=(90, 200, 255, int(200 * a_tr)), width=4)
            ea = math.radians(140 + 30 * ramp(t, st('trail'), nx('trail')))
            exx, eyy = cx + ER * math.cos(ea), cy + ER * math.sin(ea)
            paste_c(im, earth(22), exx, eyy, a_tr)
            d = ImageDraw.Draw(im, 'RGBA')
            text(d, (exx, eyy + 60), 'EARTH', 40, CYAN, alpha=a_tr)
            ptext(d, (W / 2, 250), 'EVERY NOVEMBER', 104, WHITE, t, st('trail'), nx('trail'))
            ptext(d, (W / 2, 380), 'EARTH PLOWS THROUGH', 70, WHITE, t, st('trail') + 0.8, nx('trail'))
            ptext(d, (W / 2, 470), 'THE DEBRIS TRAIL', 70, GOLD, t, st('trail') + 0.8, nx('trail'))
            ptext(d, (W / 2, 1650), 'LEONID', 140, GOLD, t, st('trail') + 3.6, nx('trail'))
            ptext(d, (W / 2, 1790), 'METEOR SHOWER', 96, WHITE, t, st('trail') + 3.6, nx('trail'))
            text(d, (W / 2, 1880), 'illustration · not to scale', 34, GREY, POP_M, stroke=3, alpha=a_tr)
        if a_c > 0:
            ptext(d, (W / 2, 250), 'COMET', 110, WHITE, t, st('comet'), nx('comet'))
            ptext(d, (W / 2, 380), 'TEMPEL-TUTTLE', 112, CYAN, t, st('comet') + 0.4, nx('comet'))
            ptext(d, (W / 2, 1660), 'ONE ORBIT =', 80, WHITE, t, st('comet') + 3.4, nx('comet'))
            ptext(d, (W / 2, 1790), '33 YEARS', 130, GOLD, t, st('comet') + 3.4, nx('comet'))
            text(d, (W / 2, 1880), 'illustration · not to scale', 34, GREY, POP_M, stroke=3, alpha=a_c)

    # ============ energy: pea vs car
    a_e = xf(t, st('energy'), nx('energy'))
    if a_e > 0:
        e0 = st('energy')
        ptext(d, (W / 2, 240), "TINY ≠ WEAK", 130, WHITE, t, e0, e0 + 2.2)
        # pea sized grain
        a1 = xf(t, e0 + 2.0, nx('energy'))
        grain(im, 230, 640, 60, a1, hot=0.5); d = ImageDraw.Draw(im, 'RGBA')
        text(d, (230, 760), 'PEA-SIZED', 52, GOLD, alpha=a1)
        text(d, (230, 820), '≈ 10 mm · 0.5 g', 42, WHITE, POP_B, alpha=a1)
        text(d, (230, 870), 'at 71 km/s', 42, WHITE, POP_B, alpha=a1)
        car_icon(d, 620, 580, 170, (200, 210, 230), a1)
        text(d, (810, 800), 'CAR', 52, WHITE, alpha=a1)
        text(d, (810, 860), '1.5 t at 100 km/h', 42, WHITE, POP_B, alpha=a1)
        g = ease(ramp(t, e0 + 4.5, e0 + 6.0))
        text(d, (100, 1040), 'PEA-SIZED LEONID', 50, GOLD, anchor='lm', alpha=a1)
        bar(d, 100, 1090, 880, g * 1.0, GOLD, a1)
        text(d, (100, 1220), '≈ 1.26 megajoules', 46, GOLD, POP_B, anchor='lm', alpha=a1)
        text(d, (100, 1340), 'CAR AT HIGHWAY SPEED', 50, WHITE, anchor='lm', alpha=a1)
        bar(d, 100, 1390, 880, g * 0.58 / 1.26, (200, 210, 230), a1)
        text(d, (100, 1520), '≈ 0.58 megajoules', 46, GREY, POP_B, anchor='lm', alpha=a1)
        text(d, (W / 2, 1600), 'energy of motion · bars to scale', 36, GREY, POP_M, stroke=3, alpha=a1)
        ptext(d, (W / 2, 1740), '≈ 2× THE ENERGY', 110, GOLD, t, e0 + 6.2, nx('energy'))
        ptext(d, (W / 2, 260), 'HALF A GRAM', 120, WHITE, t, e0 + 2.3, nx('energy'))

    # ============ tease
    a_t = xf(t, st('tease'), nx('tease'), 0.15, 0.2)
    if a_t > 0:
        sc = 0.85 + 0.15 * ease(ramp(t, st('tease'), st('tease') + 0.3))
        text(d, (W / 2, 780), "BUT THAT'S NOT", int(100 * sc), WHITE, alpha=a_t)
        text(d, (W / 2, 930), 'THE CRAZY PART', int(120 * sc), GOLD, alpha=a_t)

    # ============ storm 1966
    a_st = xf(t, st('storm') - 0.1, nx('storm'))
    if a_st > 0:
        s0 = st('storm')
        rate = 6 + 34 * ease(ramp(t, s0 + 0.5, s0 + 3.2))
        draw_storm(im, t, s0 - 0.5, nx('storm'), 40, 9, min(1, a_st * ease(ramp(t, s0 + 0.3, s0 + 3.0)) + 0.25 * a_st), 1.5)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 250), '1966', 170, GOLD, t, s0, nx('storm'))
        ptext(d, (W / 2, 420), 'UP TO 40 METEORS', 88, WHITE, t, s0 + 1.8, nx('storm'))
        ptext(d, (W / 2, 560), 'EVERY SECOND', 120, GOLD, t, s0 + 3.4, nx('storm'))
        text(d, (W / 2, 1700), 'as reported by observers · illustration', 36, GREY, POP_M, stroke=3, alpha=a_st)
        n_ = int(40 * 60 * ease(ramp(t, s0 + 3.4, nx('storm'))))
        ptext(d, (W / 2, 1810), '= 2,400 PER MINUTE', 70, CYAN, t, s0 + 3.6, nx('storm'))

    # ============ reveal: altitude ruler, grain vaporizes ~100 km up
    a_r = xf(t, st('reveal') - 0.05, nx('reveal'), 0.3, 0.3)
    if a_r > 0:
        r0 = st('reveal')
        gy0, gy1 = 1700, 560          # 0 km at y=1700, 120 km at y=300
        kmy = lambda km: gy0 - (gy0 - gy1) * km / 120
        # atmosphere gradient
        lay = np.zeros((H, W, 4), np.uint8)
        ys = np.arange(H); dens = np.clip((ys - gy1) / (gy0 - gy1), 0, 1) ** 2.2
        lay[..., 2] = 255; lay[..., 1] = 170; lay[..., 0] = 90
        lay[..., 3] = (dens * 110 * a_r).astype(np.uint8)[:, None]
        im.alpha_composite(Image.fromarray(lay, 'RGBA'))
        d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, gy0, W, H), fill=(14, 22, 18, int(255 * a_r)))
        d.line((0, gy0, W, gy0), fill=(90, 120, 90, int(255 * a_r)), width=4)
        rx = 120
        d.line((rx, gy0, rx, gy1), fill=(200, 210, 230, int(255 * a_r)), width=4)
        for km in range(0, 121, 20):
            y = kmy(km); d.line((rx - 16, y, rx + 16, y), fill=(200, 210, 230, int(255 * a_r)), width=4)
            text(d, (rx + 30, y), f'{km} km', 38, GREY, POP_B, anchor='lm', stroke=3, alpha=a_r)
        # Everest for scale (8.8 km)
        ev = kmy(8.8)
        d.polygon([(560, gy0), (700, ev), (760, ev + 18), (860, gy0)], fill=(80, 90, 100, int(255 * a_r)))
        text(d, (900, ev - 10), 'Everest 8.8 km', 34, GREY, POP_B, anchor='lm', stroke=3, alpha=a_r) if False else None
        text(d, (710, ev - 40), 'Mt Everest', 36, GREY, POP_B, stroke=3, alpha=a_r)
        # grain path: from top-right toward lower-left; ignites at ~100 km
        tig = r0 + 3.6
        p = ramp(t, r0 + 0.5, tig)
        ang = math.atan2(0.75, -1)
        sx0, sy0 = 1080, kmy(140)
        yig = kmy(100)
        xig = sx0 - (sy0 - yig) * 0  # computed below
        dxdy = -1 / 0.75
        x_at = lambda y: sx0 + (y - sy0) * dxdy
        if t < tig:
            yy_ = sy0 + (yig - sy0) * p
            grain(im, x_at(yy_), yy_, 14, a_r, hot=0.2 * p)
        else:
            q = ease(ramp(t, tig, tig + 1.2))
            yh = yig + (kmy(80) - yig) * q
            ln = (yh - yig) / 0.6 + 40
            streak(im, x_at(yh), yh, ang, ln * 1.25, 16 * (1 - 0.5 * q), a_r * (1 - 0.6 * ramp(t, tig + 1.2, tig + 2.5)) * (1 - ramp(t, tig + 4.0, tig + 5.5)), col=(255, 235, 200))
            paste_c(im, glow(260, (190, 255, 210), 1.6), x_at(yh), yh, a_r * 0.8 * (1 - ramp(t, tig + 1.2, tig + 4.0)))
        d = ImageDraw.Draw(im, 'RGBA')
        d.line((rx + 16, yig, W - 40, yig), fill=(255, 205, 90, int(150 * a_r)), width=3)
        ptext(d, (W / 2 + 60, 200), 'IT NEVER', 100, WHITE, t, r0 + 1.4, tig - 0.1)
        ptext(d, (W / 2 + 60, 200), '~100 KM UP...', 100, GOLD, t, tig - 0.1, nx('reveal'))
        ptext(d, (W / 2 + 60, 330), 'REACHES THE GROUND', 66, WHITE, t, r0 + 1.4, tig - 0.1)
        ptext(d, (W / 2 + 110, 1250), 'IT VAPORIZES', 100, CYAN, t, tig + 3.0, nx('reveal'))
        text(d, (W / 2 + 60, 1820), 'altitude to scale · grain size exaggerated', 34, GREY, POP_M, stroke=3, alpha=a_r)

    # ============ star: one bright shooting star over landscape
    a_sh = xf(t, st('star') - 0.1, nx('star'))
    if a_sh > 0:
        q = ramp(t, st('star'), st('star') + 1.0)
        hx, hy = 900 - 600 * q, 420 + 330 * q
        streak(im, hx, hy, math.atan2(330, -600), 380 * min(1, q * 3), 10, a_sh * (1 - ramp(t, st('star') + 1.0, st('star') + 1.5)), col=(255, 245, 225))
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 1050), "THAT'S A", 110, WHITE, t, st('star') + 0.2, nx('star'))
        ptext(d, (W / 2, 1200), 'SHOOTING STAR', 130, GOLD, t, st('star') + 0.4, nx('star'))

    # ============ watch: peak date
    a_w = xf(t, st('watch'), nx('watch'))
    if a_w > 0:
        draw_storm(im, t, st('watch') - 0.5, nx('watch'), 1.6, 21, a_w * 0.9, 0.9)
        d = ImageDraw.Draw(im, 'RGBA')
        pill(d, W / 2, 210, 'LEONIDS 2026', 60, (200, 40, 50), alpha=a_w)
        ptext(d, (W / 2, 400), 'PEAK ≈ NOV 17', 128, GOLD, t, st('watch') + 0.3, nx('watch'))
        ptext(d, (W / 2, 580), 'LOOK UP', 120, WHITE, t, st('watch') + 2.6, nx('watch'))
        ptext(d, (W / 2, 710), 'AFTER MIDNIGHT', 104, CYAN, t, st('watch') + 2.9, nx('watch'))
        ptext(d, (W / 2, 830), 'once the Moon has set', 54, WHITE, t, st('watch') + 3.6, nx('watch'), font=POP_B)

    out = im.convert('RGB')
    f = min(ramp(t, 0, 0.06), 1 - ramp(t, TOTAL - 0.12, TOTAL))
    if f < 1: out = Image.blend(Image.new('RGB', (W, H)), out, f)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{float(tt):05.2f}.jpg', quality=88)
    elif mode == 'timing':
        for k_ in KEYS: print(k_, round(st(k_), 2), round(en(k_), 2))
        print('TOTAL', TOTAL)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3]); n = int(round(TOTAL * FPS))
        b = min(b, n); tmp = f'part_{a:05d}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'part_{a:05d}.mp4')
        print('rendered', a, b, rc)

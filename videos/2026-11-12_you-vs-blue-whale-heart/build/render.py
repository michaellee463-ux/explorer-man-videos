import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
GAP, END = 0.28, 0.5
POP_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
POP_M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
_fc = {}
def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]
WHITE = (255, 255, 255); GOLD = (255, 205, 90); CYAN = (90, 215, 255); RED = (255, 85, 85)
GREY = (170, 180, 200); PURPLE = (190, 150, 255)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return min(max((t - a) / (b - a), 0), 1)

# ---------------------------------------------------------------- timeline
AUD = json.load(open('aud.json'))
LINES = json.load(open('lines.json'))
T0 = []; t = 0.15
for a in AUD:
    T0.append(t); t += a['dur'] + GAP
TOTAL = t - GAP + END
KEYS = [l['key'] for l in LINES]
def st(key): return T0[KEYS.index(key)]
def en(key): i = KEYS.index(key); return T0[i] + AUD[i]['dur']

# ---------------------------------------------------------------- background (deep ocean)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(5)
def make_bg(top, bot):
    k = (yy / H)[..., None]
    bg = np.array(top) * (1 - k) + np.array(bot) * k
    bg *= (1.15 - 0.5 * (((xx - W / 2) / W) ** 2))[..., None]
    return bg.astype(np.float32)
BG_OCEAN = make_bg((0.03, 0.10, 0.20), (0.005, 0.015, 0.04))
BG_DARK = make_bg((0.02, 0.03, 0.07), (0.005, 0.008, 0.02))
# light rays
rays = np.zeros((H, W), np.float32)
for i in range(7):
    x0 = rng.uniform(-200, W + 200); ang = rng.uniform(-0.25, 0.25); wdt = rng.uniform(40, 120)
    d = np.abs((xx - x0) - (yy) * math.tan(ang)) / wdt
    rays += np.exp(-d ** 2) * rng.uniform(0.02, 0.05)
rays *= np.clip(1 - yy / (H * 0.8), 0, 1)
BG_OCEAN += rays[..., None] * np.array([0.5, 0.8, 1.0])
PART = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), rng.uniform(0.15, 0.5), rng.uniform(5, 20)) for _ in range(140)]

def bg_image(mix_dark, t):
    bg = BG_OCEAN * (1 - mix_dark) + BG_DARK * mix_dark
    im = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    for x, y, r, a, v in PART:
        yv = (y - v * t) % H
        d.ellipse((x - r, yv - r, x + r, yv + r), fill=(200, 230, 255, int(255 * a * (1 - 0.5 * mix_dark))))
    return im

# ---------------------------------------------------------------- text helpers
def text(d, xy, s, size, col=WHITE, font=BLACK, anchor='mm', stroke=None, alpha=1.0):
    if alpha <= 0: return
    if stroke is None: stroke = max(3, size // 12)
    f = F(font, size)
    if alpha >= 0.999:
        d.text(xy, s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 8, 18, 255)); return
    x0, y0, x1, y1 = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
    x0, y0 = int(x0) - 2, int(y0) - 2
    lay = Image.new('RGBA', (int(x1) - x0 + 4, int(y1) - y0 + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0] - x0, xy[1] - y0), s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 8, 18, 255))
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
    d._image.alpha_composite(lay, (max(0, x0), max(0, y0))) if x0 >= 0 and y0 >= 0 else d._image.alpha_composite(lay.crop((max(0, -x0), max(0, -y0), lay.width, lay.height)), (max(0, x0), max(0, y0)))

def pill(d, cx, cy, s, size, bg, fg=WHITE, alpha=1.0):
    if alpha <= 0: return
    f = F(BLACK, size); w = f.getlength(s) + size * 1.4; h = size * 1.6
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=tuple(bg) + (int(255 * alpha),))
    text(d, (cx, cy), s, size, fg, BLACK, stroke=0, alpha=alpha)

def headline(d, lines, y, alpha, gap=1.08):
    cur = y
    for s, size, col in lines:
        text(d, (W / 2, cur + size / 2), s, size, col, alpha=alpha)
        cur += size * gap

# ---------------------------------------------------------------- whale sprite (side view, head at left)
def whale_sprite(L):
    SS = 2; Lw = int(L * SS); Hh = int(L * 0.30 * SS)
    cy = Hh * 0.45
    y, x = np.mgrid[0:Hh, 0:Lw].astype(np.float32)
    u = x / Lw
    # half-thickness profiles (fractions of length)
    body = np.where(u < 0.86, np.clip(np.sin(np.pi * np.clip(u / 0.86, 0, 1)), 0, 1) ** 0.55, 0)
    top = 0.068 * body * (1 - 0.25 * np.clip((u - 0.55) / 0.3, 0, 1))
    bot = 0.080 * body * (1 + 0.15 * np.exp(-((u - 0.2) / 0.12) ** 2))
    stock = (u >= 0.80) & (u < 0.95)
    sk = np.clip((u - 0.80) / 0.15, 0, 1)
    top = np.where(stock, np.maximum(top, 0.03 * (1 - sk) + 0.008 * sk), top)
    bot = np.where(stock, np.maximum(bot, 0.03 * (1 - sk) + 0.008 * sk), bot)
    dy = (y - cy) / Lw
    m = (dy > -top) & (dy < bot) & (u < 0.95)
    # flukes (slight 3/4 view)
    fu = (u - 0.93) / 0.07
    fc = np.clip(fu, 0, 1)
    fl = (fu >= 0) & (fu <= 1) & (dy > -0.006 - 0.018 * fc ** 1.5) & (dy < 0.006 + 0.004 * fc) & ~((fc > 0.75) & (dy > -0.006 - 0.02 * (fc - 0.75) / 0.25 + 0.0) & (dy < 0.0) & (fc > 0.85 + 0.0))
    m |= fl
    # dorsal fin
    df = (u > 0.74) & (u < 0.79) & (dy < -top) & (dy > -top - 0.012 * np.clip((u - 0.74) / 0.04, 0, 1) * np.clip((0.79 - u) / 0.012, 0, 1))
    m |= df
    # pectoral fin
    pu = (u - 0.27) / 0.09
    pf = (pu > 0) & (pu < 1) & (dy > 0.02 + pu * 0.035) & (dy < 0.035 + pu * 0.05 - 0.012 * pu ** 2)
    m |= pf
    # shading
    rel = np.clip((dy + top) / (top + bot + 1e-6), 0, 1)
    base = np.array([0.42, 0.52, 0.62])
    belly = np.array([0.62, 0.68, 0.72])
    col = base * (1 - rel[..., None] ** 2) + belly * rel[..., None] ** 2
    shade = 0.55 + 0.6 * np.clip(np.cos(np.pi * (rel - 0.3)), 0, 1) ** 0.8
    col = col * np.clip(shade, 0.35, 1.2)[..., None]
    nrng = np.random.default_rng(3)
    nz = nrng.random((Hh // 8 + 2, Lw // 8 + 2)).astype(np.float32)
    nz = np.array(Image.fromarray((nz * 255).astype(np.uint8)).resize((Lw, Hh), Image.BICUBIC), np.float32) / 255
    col *= (0.88 + 0.22 * nz)[..., None]
    # ventral grooves on throat
    gz = (u > 0.03) & (u < 0.45) & (rel > 0.62)
    col[gz] *= (0.9 + 0.1 * np.sin(dy[gz] * Lw * 0.9))[..., None]
    # eye
    ex, ey = 0.13 * Lw, cy + 0.008 * Lw
    eye = (x - ex) ** 2 + (y - ey) ** 2 < (0.0045 * Lw) ** 2
    col[eye] = np.array([0.05, 0.05, 0.07])
    # mouth line
    ml = (u > 0.0) & (u < 0.15) & (np.abs(dy - (0.012 + 0.01 * u / 0.15)) < 0.0012)
    col[ml] *= 0.5
    a = m.astype(np.float32)
    rgba = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    return im.resize((Lw // SS, Hh // SS), Image.LANCZOS), cy / SS

# ---------------------------------------------------------------- person (simple 3D-ish figure)
def person_sprite(h, shirt=(60, 120, 230)):
    SS = 4; Hs = int(h * SS); Ws = int(h * 0.42 * SS)
    im = Image.new('RGBA', (Ws, Hs), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = Hs / 100; cx = Ws / 2
    skin = (225, 175, 135, 255); pants = (35, 55, 110, 255); hair = (50, 35, 25, 255)
    d.ellipse((cx - 6.5 * u, 0, cx + 6.5 * u, 14 * u), fill=skin)
    d.chord((cx - 6.8 * u, -0.5 * u, cx + 6.8 * u, 10 * u), 180, 360, fill=hair)
    d.rounded_rectangle((cx - 3 * u, 12 * u, cx + 3 * u, 17 * u), u, fill=skin)
    d.rounded_rectangle((cx - 11 * u, 16 * u, cx + 11 * u, 52 * u), 4 * u, fill=shirt + (255,))
    d.rounded_rectangle((cx - 15.5 * u, 17 * u, cx - 10 * u, 50 * u), 2.5 * u, fill=shirt + (255,))
    d.rounded_rectangle((cx + 10 * u, 17 * u, cx + 15.5 * u, 50 * u), 2.5 * u, fill=shirt + (255,))
    d.ellipse((cx - 15.5 * u, 48 * u, cx - 10 * u, 55 * u), fill=skin)
    d.ellipse((cx + 10 * u, 48 * u, cx + 15.5 * u, 55 * u), fill=skin)
    d.rounded_rectangle((cx - 10.5 * u, 50 * u, cx - 0.5 * u, 97 * u), 2.5 * u, fill=pants)
    d.rounded_rectangle((cx + 0.5 * u, 50 * u, cx + 10.5 * u, 97 * u), 2.5 * u, fill=pants)
    d.rounded_rectangle((cx - 11.5 * u, 95 * u, cx - 0.5 * u, 100 * u), 2 * u, fill=(240, 240, 240, 255))
    d.rounded_rectangle((cx + 0.5 * u, 95 * u, cx + 11.5 * u, 100 * u), 2 * u, fill=(240, 240, 240, 255))
    # simple shading: darken right side
    arr = np.array(im, np.float32)
    k = np.linspace(1.12, 0.78, arr.shape[1])[None, :, None]
    arr[..., :3] = np.clip(arr[..., :3] * k, 0, 255)
    im = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    return im.resize((Ws // SS, Hs // SS), Image.LANCZOS)

# ---------------------------------------------------------------- heart (stylised anatomical)
def heart_sprite(size, glow=True):
    SS = 2; S = int(size * SS); pad = int(S * 0.3); N = S + 2 * pad
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    X = (x - N / 2) / (S / 2.2); Y = -(y - N / 2 - S * 0.05) / (S / 2.2)
    # classic implicit heart, tilted
    a = 0.22; c, s = math.cos(a), math.sin(a)
    Xr = c * X - s * Y; Yr = s * X + c * Y
    f = (Xr ** 2 + Yr ** 2 - 1) ** 3 - Xr ** 2 * Yr ** 3
    m = f < 0
    # aorta / vessels
    def tube(x0, y0, x1, y1, r):
        px, py = x1 - x0, y1 - y0; L2 = px * px + py * py
        tt = np.clip(((X - x0) * px + (Y - y0) * py) / L2, 0, 1)
        return (X - x0 - tt * px) ** 2 + (Y - y0 - tt * py) ** 2 < r * r
    ves = tube(-0.15, 0.7, -0.08, 1.35, 0.15) | tube(-0.08, 1.35, 0.35, 1.42, 0.12) | tube(0.3, 0.8, 0.48, 1.22, 0.11) | tube(-0.5, 0.75, -0.62, 1.12, 0.09)
    allm = m | ves
    # shading: light from upper-left
    r = np.sqrt(np.clip(1 - (X + 0.35) ** 2 * 0.35 - (Y - 0.3) ** 2 * 0.35, 0, 1))
    base = np.where(ves[..., None], np.array([0.50, 0.10, 0.20]), np.array([0.72, 0.10, 0.12]))
    col = base * (0.45 + 0.75 * r)[..., None]
    spec = np.exp(-(((X + 0.45) / 0.25) ** 2 + ((Y - 0.35) / 0.18) ** 2)) * 0.45
    col += spec[..., None]
    # surface vessels (coronary)
    cv = np.abs(Y + 0.35 * np.sin(X * 3) - 0.05 + 0.4 * X) < 0.025
    col[cv & m] *= 0.7
    al = allm.astype(np.float32)
    rgba = np.concatenate([np.clip(col, 0, 1), al[..., None]], -1)
    im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(0.8))
    if glow:
        g = Image.new('RGBA', im.size, (255, 60, 70, 0))
        ga = im.getchannel('A').filter(ImageFilter.GaussianBlur(S * 0.06)).point(lambda v: int(v * 0.55))
        g.putalpha(ga)
        g.alpha_composite(im); im = g
    return im.resize((N // SS, N // SS), Image.LANCZOS)

CACHE = {}
def sprite(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]

def paste_c(im, sp, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0 or scale <= 0: return
    if scale != 1.0:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BILINEAR)
    if rot: sp = sp.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        sp = sp.copy(); sp.putalpha(sp.getchannel('A').point(lambda v: int(v * alpha)))
    im.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))

def beat(t, period, t0=0):
    """heartbeat pulse 0..1"""
    p = ((t - t0) % period)
    return math.exp(-((p - 0.08) / 0.07) ** 2) + 0.5 * math.exp(-((p - 0.32) / 0.07) ** 2)

# ---------------------------------------------------------------- the frame
WL = 980
def frame(t):
    dark = ease(ramp(t, st('dive') - 0.3, st('dive') + 0.8))
    im = bg_image(dark, t)
    d = ImageDraw.Draw(im, 'RGBA')
    whale, wcy = sprite('whale', lambda: whale_sprite(WL))
    # series badge (always top)
    pill(d, W / 2, 150, 'YOU vs', 44, PURPLE, (20, 10, 40), alpha=1 - ease(ramp(t, TOTAL - 1.8, TOTAL - 1.4)))

    # ---- hook
    a_h = 1 - ease(ramp(t, st('size') - 0.2, st('size') + 0.2))
    if a_h > 0:
        headline(d, [('YOU vs THE', 92, WHITE), ('BIGGEST', 128, CYAN), ('ANIMAL EVER', 104, WHITE)], 250, a_h)
        text(d, (W / 2, 640), 'the largest animal known to have ever lived', 34, GREY, POP_M, stroke=3, alpha=a_h)
        sx = 1 + 0.06 * t
        paste_c(im, whale, W / 2 + 40 - 30 * t, 1150, scale=sx * 1.05, alpha=a_h)
        per = sprite('per300', lambda: person_sprite(300))
        paste_c(im, per, 170, 1610, alpha=a_h * ease(ramp(t, 0.3, 0.8)))
        text(d, (170, 1800), 'YOU', 50, WHITE, alpha=a_h * ease(ramp(t, 0.3, 0.8)))
        text(d, (W / 2 + 120, 1420), 'BLUE WHALE', 54, CYAN, alpha=a_h * ease(ramp(t, 0.8, 1.3)))
        text(d, (W / 2 + 120, 1480), 'not to scale', 30, GREY, POP_M, alpha=a_h * ease(ramp(t, 0.8, 1.3)))

    # ---- size (to scale)
    s0 = st('size'); a_s = ease(ramp(t, s0 - 0.1, s0 + 0.4)) * (1 - ease(ramp(t, st('yourheart') - 0.2, st('yourheart') + 0.2)))
    if a_s > 0:
        y = 1000
        paste_c(im, whale, W / 2, y + (whale.height / 2 - wcy), alpha=a_s)
        # person to scale: 1.7 m vs 33 m whale length
        ph = WL * 1.7 / 33.0
        per = sprite('per_s', lambda: person_sprite(ph, (255, 205, 90)))
        px = W / 2 - WL / 2 - 10
        paste_c(im, per, px - per.width / 2 + 0, y + 70 - ph / 2, alpha=a_s)
        text(d, (px - 5, y + 70 - ph - 26), 'YOU', 34, GOLD, alpha=a_s)
        # ruler
        ry = y + 170
        d.line((W / 2 - WL / 2, ry, W / 2 + WL / 2, ry), fill=(255, 255, 255, int(220 * a_s)), width=4)
        for xx_ in (W / 2 - WL / 2, W / 2 + WL / 2):
            d.line((xx_, ry - 16, xx_, ry + 16), fill=(255, 255, 255, int(220 * a_s)), width=4)
        a1 = a_s * ease(ramp(t, s0 + 0.9, s0 + 1.4))
        text(d, (W / 2, 330), 'UP TO', 70, WHITE, alpha=a1)
        text(d, (W / 2, 450), '≈33 METERS', 130, CYAN, alpha=a1)
        text(d, (W / 2, ry + 60), '≈33 m', 56, WHITE, alpha=a1)
        a2 = a_s * ease(ramp(t, s0 + 3.4, s0 + 3.9))
        text(d, (W / 2, 1390), 'UP TO', 64, WHITE, alpha=a2)
        text(d, (W / 2, 1510), '150 TONNES', 130, GOLD, alpha=a2)
        text(d, (W / 2, 1640), 'whale & person drawn to scale', 36, GREY, POP_M, stroke=3, alpha=a_s)

    # ---- your heart
    y0 = st('yourheart'); a_y = ease(ramp(t, y0 - 0.1, y0 + 0.4)) * (1 - ease(ramp(t, st('whaleheart') - 0.2, st('whaleheart') + 0.3)))
    hs = sprite('heart', lambda: heart_sprite(700))
    if a_y > 0:
        text(d, (W / 2, 330), 'YOUR HEART', 110, WHITE, alpha=a_y)
        b = beat(t, 0.8)
        paste_c(im, hs, W / 2, 1000, scale=0.42 * (1 + 0.05 * b), alpha=a_y)
        a1 = a_y * ease(ramp(t, y0 + 0.4, y0 + 0.9))
        text(d, (W / 2, 1380), '≈ THE SIZE OF', 70, WHITE, alpha=a1)
        text(d, (W / 2, 1480), 'YOUR FIST', 110, GOLD, alpha=a1)
        a2 = a_y * ease(ramp(t, y0 + 2.0, y0 + 2.5))
        text(d, (W / 2, 1640), 'UNDER HALF A KILO', 76, CYAN, alpha=a2)
        text(d, (W / 2, 1725), '≈200–425 g', 46, GREY, POP_B, stroke=3, alpha=a2)

    # ---- whale heart
    w0 = st('whaleheart'); a_w = ease(ramp(t, w0 - 0.1, w0 + 0.4)) * (1 - ease(ramp(t, st('tease') - 0.3, st('tease') + 0.05)))
    if a_w > 0:
        g = ease(ramp(t, w0 + 0.3, w0 + 2.0))
        paste_c(im, hs, W / 2 + 70, 1000, scale=0.42 + 0.62 * g, alpha=a_w)
        text(d, (W / 2, 300), "A BLUE WHALE'S", 76, WHITE, alpha=a_w)
        text(d, (W / 2, 400), 'HEART', 120, RED, alpha=a_w)
        paste_c(im, hs, 150, 1290, scale=0.13, alpha=a_w * g)
        text(d, (150, 1395), 'yours', 36, WHITE, POP_B, stroke=3, alpha=a_w * g)
        a1 = a_w * ease(ramp(t, w0 + 1.4, w0 + 1.9))
        text(d, (W / 2, 1510), '≈180 KG', 150, GOLD, alpha=a1)
        a2 = a_w * ease(ramp(t, w0 + 3.4, w0 + 3.9))
        text(d, (W / 2, 1660), 'MORE THAN 400×', 92, WHITE, alpha=a2)
        text(d, (W / 2, 1750), 'HEAVIER THAN YOURS', 60, CYAN, alpha=a2)
        text(d, (W / 2, 1830), 'illustration, not to scale', 30, GREY, POP_M, stroke=3, alpha=a_w)

    # ---- tease + dive + reveal: heart monitor
    t0 = st('tease'); a_m = ease(ramp(t, t0 + 0.1, t0 + 0.5)) * (1 - ease(ramp(t, st('outro') - 0.4, st('outro') - 0.05)))
    if a_m > 0:
        at = a_m * (1 - ease(ramp(t, st('dive') - 0.2, st('dive') + 0.2)))
        headline(d, [('BUT THE', 90, WHITE), ('WILDEST', 140, GOLD), ('PART…', 110, WHITE)], 290, at)
        # whale diving in background
        dv = ease(ramp(t, t0, st('dive') + 2.5))
        wsmall = sprite('whale_sm', lambda: whale.resize((int(whale.width * 0.7), int(whale.height * 0.7)), Image.LANCZOS))
        paste_c(im, wsmall, W / 2 + 200 - 300 * dv, 900 + 260 * dv, rot=-18 * dv, alpha=at * 0.95 + (a_m - at) * 0.35)
        a_d = a_m * ease(ramp(t, st('dive') + 0.2, st('dive') + 0.6))
        if a_d > 0:
            text(d, (W / 2, 300), 'ON A DEEP DIVE', 78, WHITE, alpha=a_d * (1 - ease(ramp(t, st('reveal') - 0.2, st('reveal') + 0.2))))
            # whale heart monitor (top) and your heart (bottom)
            rows = [(720, CYAN, 'BLUE WHALE', 30.0, st('dive') + 0.8), (1300, GOLD, 'YOU (resting)', 60 / 80, st('dive') + 0.3)]
            for (ry, col, lab, period, ts) in rows:
                if lab.startswith('YOU') and t < st('reveal') - 0.3: continue
                aa = a_d if not lab.startswith('YOU') else a_m * ease(ramp(t, st('reveal') - 0.3, st('reveal') + 0.2))
                d.rounded_rectangle((60, ry - 170, W - 60, ry + 170), 30, fill=(0, 0, 0, int(140 * aa)), outline=tuple(col) + (int(200 * aa),), width=3)
                text(d, (100, ry - 130), lab, 44, col, anchor='lm', alpha=aa)
                # ECG trace scrolling: trace of last 5 s across width
                pts = []
                win = 5.0 if not lab.startswith('YOU') else 5.0
                for i in range(0, 841, 3):
                    tt = t - win + win * i / 840
                    v = 0
                    if tt > ts:
                        p = (tt - ts) % period
                        v = 1.0 * math.exp(-((p - 0.05) / 0.018) ** 2) - 0.35 * math.exp(-((p - 0.09) / 0.02) ** 2) + 0.18 * math.exp(-((p - 0.3) / 0.06) ** 2)
                    pts.append((120 + i, ry + 40 - 110 * v))
                d.line(pts, fill=tuple(col) + (int(255 * aa),), width=5, joint='curve')
                hb = 0
                if t > ts: hb = beat(t, period, ts)
                paste_c(im, hs, W - 170, ry - 110, scale=0.11 * (1 + 0.15 * hb), alpha=aa)
            a_b = a_d * ease(ramp(t, st('dive') + 1.6, st('dive') + 2.1))
            text(d, (W / 2, 1000), '2 BEATS / MINUTE', 100, CYAN, alpha=a_b * (1 - ease(ramp(t, st('reveal') - 0.2, st('reveal') + 0.2))))
            text(d, (W / 2, 1090), 'one beat every 30 seconds', 46, WHITE, POP_B, stroke=3, alpha=a_b * (1 - ease(ramp(t, st('reveal') - 0.2, st('reveal') + 0.2))))
            r0 = st('reveal'); a_r = a_m * ease(ramp(t, r0 + 0.2, r0 + 0.6))
            if a_r > 0:
                text(d, (W / 2, 290), '1 WHALE BEAT =', 96, WHITE, alpha=a_r)
                text(d, (W / 2, 520), '(at its slowest)', 50, WHITE, POP_B, stroke=4, alpha=a_r)
                text(d, (W / 2, 410), '30–50 OF YOURS', 112, GOLD, alpha=a_r)
                text(d, (W / 2, 1620), 'your heart at rest: 60–100 beats/min', 46, WHITE, POP_B, stroke=3, alpha=a_r)
                text(d, (W / 2, 1700), "whale on a deep dive: as low as 2 beats/min", 40, CYAN, POP_B, stroke=3, alpha=a_r)
                text(d, (W / 2, 1000), '…still waiting for its next beat', 46, CYAN, POP_B, stroke=3, alpha=a_r)

    # ---- outro
    o0 = st('outro'); a_o = ease(ramp(t, o0, o0 + 0.3))
    if a_o > 0:
        headline(d, [('FOLLOW', 130, WHITE), ('FOR MORE', 130, GOLD)], 640, a_o)
        pill(d, W / 2, 1050, 'YOU vs', 70, PURPLE, (20, 10, 40), alpha=a_o)
    out = im.convert('RGB')
    fade = min(ramp(t, 0, 0.12), 1 - ramp(t, TOTAL - 0.15, TOTAL))
    if fade < 1: out = Image.blend(Image.new('RGB', (W, H)), out, fade)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]:
            frame(float(tt)).save(f'still_{float(tt):.2f}.jpg', quality=88)
    elif mode == 'timing':
        for k in KEYS: print(k, round(st(k), 2), round(en(k), 2))
        print('TOTAL', TOTAL)
    elif mode == 'render':
        n = int(round(TOTAL * FPS)); tmp = 'video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, 'video.mp4')
        print('rendered', n, rc)

import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from script import SCENES, caption

W, H, FPS = 1920, 1080, 30
GAP, END = 0.35, 0.9
POP_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
POP_M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
WHITE = (255, 255, 255); GOLD = (255, 205, 90); CYAN = (90, 215, 255); RED = (255, 90, 80); PINK = (255, 120, 140)
GREY = (170, 178, 195)

R_E = 6370.0
D_MANTLE = 2900.0; D_OUTER = 5100.0
KOLA = 12.262

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return min(max((t - a) / (b - a), 0), 1)

# ---------------------------------------------------------------- background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(11)
bg = np.zeros((H, W, 3), np.float32)
r2 = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2
bg[:] = np.array([0.035, 0.045, 0.085])
bg *= (1.25 - 1.2 * r2)[..., None]
for _ in range(900):
    x, y = rng.integers(0, W), rng.integers(0, H)
    bg[y, x] += rng.uniform(0.05, 0.35)
BG = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8))

def text(d, xy, s, size, col=WHITE, font=POP_B, anchor='mm', stroke=0, alpha=1.0):
    if alpha <= 0: return
    c = tuple(col) + (int(255 * alpha),)
    d.text(xy, s, font=F(font, size), fill=c, anchor=anchor,
           stroke_width=stroke, stroke_fill=(5, 8, 15, int(255 * alpha)))

def wrap(s, font, maxw):
    words = s.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if font.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def draw_caption(im, s, alpha):
    if not s or alpha <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    f = F(POP_M, 38)
    lines = wrap(s, f, 1500)
    y0 = H - 70 - (len(lines) - 1) * 50
    for i, ln in enumerate(lines):
        text(d, (W / 2, y0 + i * 50), ln, 38, WHITE, POP_M, stroke=3, alpha=alpha)

def chapter_pill(im, label, a):
    if a <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    f = F(POP_B, 34); w = f.getlength(label) + 60
    d.rounded_rectangle((60, 50, 60 + w, 112), 31, fill=(255, 205, 90, int(235 * a)))
    text(d, (60 + w / 2, 81), label, 34, (20, 20, 30), POP_B, alpha=a)

# ---------------------------------------------------------------- Earth cross-section
def layer_color(rn):
    """rn = r/R (0 centre .. 1 surface) -> rgb float"""
    out = np.zeros(rn.shape + (3,), np.float32)
    inner = 1 - D_OUTER / R_E; mant = 1 - D_MANTLE / R_E
    crust = 1 - 35 / R_E
    # inner core: white-yellow hot
    m = rn < inner
    k = (rn / inner)[m]
    out[m] = np.stack([1.0 - 0.0 * k, 0.95 - 0.15 * k, 0.70 - 0.35 * k], -1)
    m = (rn >= inner) & (rn < mant)
    k = ((rn - inner) / (mant - inner))[m]
    out[m] = np.stack([1.0 - 0.05 * k, 0.62 - 0.22 * k, 0.12 + 0.0 * k], -1)
    m = (rn >= mant) & (rn < crust)
    k = ((rn - mant) / (crust - mant))[m]
    out[m] = np.stack([0.80 - 0.25 * k, 0.25 - 0.08 * k, 0.08 + 0.02 * k], -1)
    m = rn >= crust
    out[m] = np.array([0.45, 0.33, 0.24])
    return out

def disc_layers(R, glow_layer=None, dim=0.0, swirl_t=None):
    """Return RGBA image (2R+40 square) of a cross-section, true radii."""
    S = int(2 * R + 40); c = S / 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(x - c, y - c); rn = rr / R
    col = layer_color(rn)
    # subtle texture
    ang = np.arctan2(y - c, x - c)
    tex = 0.06 * np.sin(rn * 60 + 3 * np.sin(ang * 5)) + 0.04 * np.sin(ang * 23 + rn * 17)
    col *= (1 + tex)[..., None]
    inner = 1 - D_OUTER / R_E; mant = 1 - D_MANTLE / R_E
    if swirl_t is not None:
        m = (rn >= inner) & (rn < mant)
        sw = 0.5 + 0.5 * np.sin(ang * 6 + rn * 25 - swirl_t * 2.2 + 2 * np.sin(ang * 3 + swirl_t * 0.7))
        col[m] *= (0.8 + 0.35 * sw[m])[..., None]
    if glow_layer is not None and dim > 0:
        sel = {'crust': rn >= 1 - 35 / R_E - 1.5 / R, 'mantle': (rn >= mant) & (rn < 1),
               'outer': (rn >= inner) & (rn < mant), 'inner': rn < inner}[glow_layer]
        col[~sel] *= (1 - 0.7 * dim)
    # limb shading + edge AA
    col *= (1 - 0.18 * rn ** 6)[..., None]
    a = np.clip(R - rr + 0.5, 0, 1)
    rgba = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
    # boundary lines
    d = ImageDraw.Draw(im)
    for rf in (inner, mant):
        rp = rf * R
        d.ellipse((c - rp, c - rp, c + rp, c + rp), outline=(20, 10, 5, 110), width=2)
    d.ellipse((c - R, c - R, c + R, c + R), outline=(150, 200, 255, 160), width=3)
    return im

def paste_c(im, sp, cx, cy):
    im.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))

# ---------------------------------------------------------------- globe (intro)
def make_globe(R, lon0, cut=0.0):
    S = int(2 * R + 4); c = S / 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    nx = (x - c) / R; ny = (y - c) / R
    rr2 = nx ** 2 + ny ** 2
    inside = rr2 <= 1
    nz = np.sqrt(np.clip(1 - rr2, 0, 1))
    lat = np.arcsin(np.clip(-ny, -1, 1)); lon = np.arctan2(nx, nz) + lon0
    n = (np.sin(lon * 2 + 1.3) * np.cos(lat * 3) + 0.6 * np.sin(lon * 5 + lat * 4 + 0.5)
         + 0.35 * np.sin(lon * 11 - lat * 7) + 0.2 * np.sin(lon * 23 + lat * 19))
    land = n > 0.55
    ice = np.abs(lat) > 1.25
    col = np.zeros((S, S, 3), np.float32)
    col[:] = np.array([0.05, 0.22, 0.48])
    col[land] = np.array([0.24, 0.42, 0.18]) * (0.85 + 0.15 * np.sin(n * 9))[land][..., None]
    col[land & (n > 1.1)] = np.array([0.52, 0.42, 0.28])
    col[ice] = np.array([0.88, 0.92, 0.96])
    cl = (np.sin(lon * 4 + 3 * np.sin(lat * 6)) * np.sin(lat * 9 + lon * 1.5)
          + 0.5 * np.sin(lon * 13 + lat * 11 + 2 * np.sin(lon * 3)) + 0.25 * np.sin(lon * 29 - lat * 23))
    cm = np.clip((cl - 0.75) / 0.6, 0, 1)[..., None] * 0.45; col = col * (1 - cm) + cm * 0.92
    light = np.clip(0.25 + 0.85 * (-0.45 * nx - 0.35 * ny + 0.82 * nz), 0.08, 1.1)
    col *= light[..., None]
    rim = np.clip((np.sqrt(rr2) - 0.92) / 0.08, 0, 1) * inside
    col += rim[..., None] * np.array([0.15, 0.3, 0.6])
    if cut > 0:
        # wedge: upper-right quadrant, angle from -90 to -90+90*cut (screen coords)
        ang = np.degrees(np.arctan2(-(y - c), x - c))  # 0 = right, 90 = up
        wedge = inside & (ang >= 0) & (ang <= 90 * cut + 0.001)
        rn = np.sqrt(rr2)
        lc = layer_color(rn)
        lc *= (1 + 0.05 * np.sin(rn * 60))[..., None]
        col[wedge] = lc[wedge]
    a = np.clip((1 - np.sqrt(rr2)) * R + 0.5, 0, 1)
    rgba = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    return Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')

# ---------------------------------------------------------------- scenes
class Scene:
    def __init__(self, key, chapter, sents):
        self.key, self.chapter, self.sents = key, chapter, sents
        t = 0.25; self.marks = []
        for s in sents:
            self.marks.append((t, t + s['dur'], caption(s['text'])))
            t += s['dur'] + GAP
        self.dur = t - GAP + END
    def sent_t(self, i): return self.marks[i][0]
    def cap_at(self, t):
        for a, b, s in self.marks:
            if a - 0.05 <= t <= b + GAP: return s
        return None

CACHE = {}

def sc_intro(sc, t, im, d):
    R = 360
    i3 = sc.sent_t(2)
    cut = ease(ramp(t, i3, i3 + 1.5))
    zoom = 1 + 0.06 * t / sc.dur
    g = make_globe(int(R * zoom), t * 0.06, cut)
    paste_c(im, g, W * 0.62, H * 0.47)
    cx, cy = W * 0.62, H * 0.47
    a = ease(ramp(t, 0.6, 1.4))
    if a > 0:
        rr = R * zoom
        d.line((cx, cy - rr, cx, cy - rr + (rr) * ease(ramp(t, 0.6, 2.2))), fill=(255, 205, 90, int(255 * a)), width=6)
        d.ellipse((cx - 9, cy - rr - 9, cx + 9, cy - rr + 9), fill=(255, 255, 255, int(255 * a)))
        if t > 2.0: d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 205, 90, 255))
        text(d, (W * 0.24, H * 0.36), 'ABOUT', 54, WHITE, BLACK, stroke=6, alpha=a)
        text(d, (W * 0.24, H * 0.47), '6,370 KM', 120, GOLD, BLACK, stroke=10, alpha=a)
        text(d, (W * 0.24, H * 0.58), 'TO THE CENTER', 54, WHITE, BLACK, stroke=6, alpha=a)
    a2 = ease(ramp(t, sc.sent_t(1), sc.sent_t(1) + 0.6)) * (1 - ease(ramp(t, i3, i3 + 0.6)))
    text(d, (W * 0.24, H * 0.70), 'Visited by: nobody', 40, PINK, POP_B, stroke=3, alpha=a2)

def strata_panel(x0, y0, w, h, km_per_px, top_km=0):
    key = ('strata', x0, y0, w, h, km_per_px)
    if key not in CACHE:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        depth = y * km_per_px
        base = np.array([0.42, 0.31, 0.22])
        v = 0.85 + 0.08 * np.sin(depth * 2.1 + 0.4 * np.sin(x / 90)) + 0.05 * np.sin(depth * 7.3 + x / 37)
        dark = np.clip(1 - depth / (h * km_per_px) * 0.45, 0.5, 1)
        col = base * (v * dark)[..., None]
        CACHE[key] = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    return CACHE[key]

def sc_kola(sc, t, im, d):
    # vertical panel: 0..14 km over 760 px
    x0, y0, w, h = 980, 210, 760, 680
    kmpp = 14.0 / h
    im.alpha_composite(strata_panel(x0, y0, w, h, kmpp), (x0, y0))
    d.rectangle((x0, y0 - 40, x0 + w, y0), fill=(70, 120, 190, 255))
    d.rectangle((x0, y0 - 6, x0 + w, y0), fill=(80, 140, 70, 255))
    # depth scale
    for km in range(0, 15, 2):
        yy_ = y0 + km / kmpp
        d.line((x0 - 20, yy_, x0, yy_), fill=(220, 220, 230, 255), width=3)
        text(d, (x0 - 30, yy_), f'{km} km', 30, GREY, POP_B, anchor='rm')
    # rig
    rx = x0 + w * 0.5
    d.polygon([(rx - 40, y0 - 6), (rx + 40, y0 - 6), (rx + 8, y0 - 150), (rx - 8, y0 - 150)], outline=(230, 230, 240, 255), width=4)
    for k in range(1, 5):
        yk = y0 - 6 - k * 30; hw = 40 - k * 7.5
        d.line((rx - hw, yk, rx + hw, yk), fill=(230, 230, 240, 255), width=3)
    t0 = sc.sent_t(0) + 0.5; t1 = sc.sent_t(2) + 3.0
    p = ease(ramp(t, t0, t1))
    depth = KOLA * p
    yd = y0 + depth / kmpp
    d.rectangle((rx - 3, y0, rx + 3, yd), fill=(255, 205, 90, 255))
    if p > 0:
        d.ellipse((rx - 9, yd - 9, rx + 9, yd + 9), fill=(255, 255, 255, 255))
    al = ease(ramp(t, t0 - 0.5, t0))
    text(d, (480, 330), 'KOLA SUPERDEEP', 58, WHITE, BLACK, stroke=6)
    text(d, (480, 400), 'BOREHOLE', 58, WHITE, BLACK, stroke=6)
    yl = '1970' if p <= 0 else ('1970 – 1989' if p < 1 else '1989')
    text(d, (480, 520), yl, 96 if p < 1 and p > 0 else 110, CYAN, BLACK, stroke=8, alpha=al)
    if p > 0 and p < 1:
        text(d, (480, 610), 'drilling…', 44, GREY, POP_B, stroke=3, alpha=al)
    ad = ease(ramp(t, t1, t1 + 0.4))
    text(d, (480, 660), '12,262 m', 110, GOLD, BLACK, stroke=8, alpha=ad)
    if p >= 1:
        a = ease(ramp(t, t1, t1 + 0.5))
        text(d, (rx + 30, yd), '12,262 m', 40, GOLD, POP_B, anchor='lm', stroke=4, alpha=a)
    a = ease(ramp(t, sc.sent_t(3), sc.sent_t(3) + 0.5))
    text(d, (480, 780), 'DEEPEST HOLE EVER DRILLED', 40, PINK, POP_B, stroke=4, alpha=a)
    a = ease(ramp(t, sc.sent_t(4) + 1.6, sc.sent_t(4) + 2.2))
    text(d, (480, 850), '…but the center is 6,370 km down', 36, WHITE, POP_M, stroke=3, alpha=a)

def sc_scale(sc, t, im, d):
    R = 380; cx, cy = 560, 510
    if 'disc380' not in CACHE: CACHE['disc380'] = disc_layers(R)
    paste_c(im, CACHE['disc380'], cx, cy)
    # Kola to scale: 12.262/6370*400 = 0.77 px -> mark position with ring
    kpx = KOLA / R_E * R
    d.line((cx, cy - R, cx, cy - R + kpx), fill=(255, 60, 60, 255), width=3)
    a = ease(ramp(t, 0.5, 1.2))
    d.ellipse((cx - 22, cy - R - 22, cx + 22, cy - R + 22), outline=(255, 90, 80, int(255 * a)), width=4)
    d.line((cx + 22, cy - R, 1080, 190), fill=(255, 90, 80, int(255 * a)), width=3)
    text(d, (1100, 170), 'Kola, drawn to scale', 36, PINK, POP_B, anchor='lm', stroke=3, alpha=a)
    text(d, (1100, 215), '(it\'s less than one pixel)', 30, GREY, POP_M, anchor='lm', stroke=2, alpha=a)
    a = ease(ramp(t, sc.sent_t(0) + 2.5, sc.sent_t(0) + 3.2))
    text(d, (1420, 400), '12 km ÷ 6,370 km', 52, WHITE, POP_B, stroke=4, alpha=a)
    text(d, (1420, 500), '≈ 0.19%', 120, GOLD, BLACK, stroke=9, alpha=a)
    a = ease(ramp(t, sc.sent_t(1), sc.sent_t(1) + 0.6))
    text(d, (1420, 650), 'Globe 1 m wide: hole ≈ 1 mm deep', 40, CYAN, POP_B, stroke=3, alpha=a)
    a = ease(ramp(t, sc.sent_t(2), sc.sent_t(2) + 0.6))
    text(d, (1420, 760), '99.8% NEVER REACHED', 66, PINK, BLACK, stroke=6, alpha=a)

def sc_crust(sc, t, im, d):
    kmpp = 50.0 / 720  # 50 km over 720 px, same scale both columns
    y0 = 210
    cols = [(560, 'UNDER THE OCEANS', 5.5, (5, 6)), (1300, 'UNDER THE CONTINENTS', 35, (30, 40))]
    gp = ease(ramp(t, sc.sent_t(1) - 0.3, sc.sent_t(1) + 0.6))
    gc = ease(ramp(t, sc.sent_t(2) - 0.3, sc.sent_t(2) + 0.6))
    for i, (x, lab, mid, (lo, hi)) in enumerate(cols):
        w = 420; x0 = x - w / 2
        a = gp if i == 0 else gc
        if a <= 0: continue
        A = int(255 * a)
        # mantle below
        d.rectangle((x0, y0, x0 + w, y0 + 720), fill=(150, 50, 25, A))
        # crust min part solid, uncertain range hatched lighter
        d.rectangle((x0, y0, x0 + w, y0 + lo / kmpp), fill=(115, 85, 62, A))
        d.rectangle((x0, y0 + lo / kmpp, x0 + w, y0 + hi / kmpp), fill=(132, 92, 60, A))
        for yy_ in np.arange(y0 + lo / kmpp, y0 + hi / kmpp, 12):
            d.line((x0, yy_, x0 + w, yy_), fill=(115, 85, 62, A), width=4)
        top = (40, 90, 170, A) if i == 0 else (70, 130, 60, A)
        d.rectangle((x0, y0 - 18, x0 + w, y0), fill=top)
        text(d, (x, y0 - 50), lab, 34, WHITE, POP_B, stroke=3, alpha=a)
        text(d, (x0 + w + 20, y0 + mid / kmpp), f'crust ≈{lo}–{hi} km', 32, GOLD, POP_B, anchor='lm', stroke=3, alpha=a)
        text(d, (x, y0 + 680), 'MANTLE', 34, (255, 200, 170), POP_B, stroke=3, alpha=a)
    # scale bar
    a = max(gp, 0)
    for km in range(0, 51, 10):
        yy_ = y0 + km / kmpp
        d.line((150, yy_, 175, yy_), fill=(220, 220, 230, int(255 * a)), width=3)
        text(d, (140, yy_), f'{km} km', 28, GREY, POP_B, anchor='rm', alpha=a)
    # Kola in the continent column
    ak = ease(ramp(t, sc.sent_t(3), sc.sent_t(3) + 0.4))
    if ak > 0:
        p = ease(ramp(t, sc.sent_t(3), sc.sent_t(3) + 1.8))
        yd = y0 + KOLA * p / kmpp
        d.rectangle((1300 - 3, y0, 1300 + 3, yd), fill=(255, 205, 90, 255))
        d.ellipse((1300 - 8, yd - 8, 1300 + 8, yd + 8), fill=(255, 255, 255, 255))
        text(d, (1300 - 20, yd), 'Kola 12.3 km', 32, GOLD, POP_B, anchor='rm', stroke=4, alpha=ak)
    a0 = ease(ramp(t, sc.sent_t(0), sc.sent_t(0) + 0.6)) * (1 - gp)
    text(d, (W / 2, 470), 'LAYER 1', 60, GOLD, BLACK, stroke=6, alpha=a0)
    text(d, (W / 2, 560), 'THE CRUST', 110, WHITE, BLACK, stroke=9, alpha=a0)
    text(d, (W / 2, 660), 'Earth\'s thin outer skin', 40, GREY, POP_M, stroke=3, alpha=a0)
    text(d, (W / 2, 1000 - 60), 'drawn to scale: 50 km', 26, GREY, POP_M, alpha=gp * 0.9)

def layer_scene(sc, t, im, d, layer, notes, swirl=False, field=False):
    R = 405; cx, cy = 640, 515
    dim = ease(ramp(t, 0.3, 1.2))
    if swirl:
        img = disc_layers(R, layer, dim, swirl_t=t)
    else:
        k = ('L', layer, round(dim, 2))
        if k not in CACHE: CACHE[k] = disc_layers(R, layer, dim)
        img = CACHE[k]
    if field:
        fa = ease(ramp(t, sc.sent_t(2) + 1.5, sc.sent_t(2) + 3.0))
        if fa > 0:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            for L in (1.3, 1.6, 1.95):
                for side in (-1, 1):
                    pts = [(cx + side * L * math.sin(th) ** 3 * R, cy - L * math.sin(th) ** 2 * math.cos(th) * R)
                           for th in np.linspace(0.02, math.pi - 0.02, 200) if L * math.sin(th) ** 2 >= 1.0]
                    if len(pts) > 1: dl.line(pts, fill=(120, 200, 255, int(190 * fa)), width=3)
            m = np.clip((1150 - xx[0]) / 120, 0, 1)
            mask = Image.fromarray(np.repeat((m * 255).astype(np.uint8)[None, :], H, 0), 'L')
            a = lay.getchannel('A'); a = Image.fromarray((np.array(a, np.float32) * np.array(mask, np.float32) / 255).astype(np.uint8))
            lay.putalpha(a); im.alpha_composite(lay)
    paste_c(im, img, cx, cy)
    for n in notes:
        st, txt, size, col, font, y = n
        a = ease(ramp(t, st, st + 0.6))
        text(d, (1450, y), txt, size, col, font, stroke=max(3, size // 14), alpha=a)
    return R, cx, cy

def depth_arrow(d, cx, cy, R, depth_km, a, label):
    if a <= 0: return
    y1 = cy - R + R * depth_km / R_E * ease(a)
    x = cx + 6
    d.line((x, cy - R, x, y1), fill=(255, 255, 255, int(255 * a)), width=4)
    d.polygon([(x - 10, y1 - 14), (x + 10, y1 - 14), (x, y1)], fill=(255, 255, 255, int(255 * a)))
    if a >= 0.99 and label:
        text(d, (x - 20, (cy - R + y1) / 2), label, 32, WHITE, POP_B, anchor='rm', stroke=4)

def sc_mantle(sc, t, im, d):
    s = sc.sent_t
    R, cx, cy = layer_scene(sc, t, im, d, 'mantle', [
        (0.3, 'LAYER 2', 56, GOLD, BLACK, 300),
        (0.3, 'THE MANTLE', 96, WHITE, BLACK, 390),
        (s(0) + 2.5, 'hot rock to ≈2,900 km', 46, (255, 190, 150), POP_B, 520),
        (s(1), 'almost halfway down', 46, CYAN, POP_B, 600),
        (s(2) + 1.5, '> 80% OF EARTH\'S VOLUME', 56, GOLD, BLACK, 730)])
    depth_arrow(d, cx, cy, R, D_MANTLE, ramp(t, s(0) + 2.0, s(0) + 3.5), '2,900 km')

def sc_outer(sc, t, im, d):
    s = sc.sent_t
    R, cx, cy = layer_scene(sc, t, im, d, 'outer', [
        (0.3, 'LAYER 3', 56, GOLD, BLACK, 300),
        (0.3, 'THE OUTER CORE', 90, WHITE, BLACK, 390),
        (s(1), 'liquid iron & nickel', 46, (255, 200, 120), POP_B, 520),
        (s(1) + 2.0, '≈2,200 km thick', 46, CYAN, POP_B, 600),
        (s(2) + 2.0, 'swirling liquid metal makes', 44, WHITE, POP_B, 720),
        (s(2) + 2.6, 'EARTH\'S MAGNETIC FIELD', 52, CYAN, BLACK, 790)], swirl=True, field=True)
    depth_arrow(d, cx, cy, R, D_MANTLE, ramp(t, s(0), s(0) + 1.5), '2,900 km')

def sc_inner(sc, t, im, d):
    s = sc.sent_t
    R, cx, cy = layer_scene(sc, t, im, d, 'inner', [
        (0.3, 'LAYER 4', 56, GOLD, BLACK, 250),
        (0.3, 'THE INNER CORE', 90, WHITE, BLACK, 340),
        (s(0) + 3.0, 'radius > 1,200 km', 44, (255, 220, 150), POP_B, 460),
        (s(1), '≈5,000–6,000 °C', 74, RED, BLACK, 570),
        (s(1) + 2.5, '≈ as hot as the Sun\'s surface', 40, WHITE, POP_B, 650),
        (s(3), 'PRESSURE > 3,000,000×', 58, GOLD, BLACK, 760),
        (s(3) + 1.0, 'sea-level air pressure', 38, GREY, POP_B, 825),
        (s(4) + 0.5, 'squeezed SOLID', 56, CYAN, BLACK, 920)])
    depth_arrow(d, cx, cy, R, D_OUTER, ramp(t, s(0), s(0) + 2.0), '5,100 km')

def sc_fall(sc, t, im, d):
    s = sc.sent_t
    R = 380; cx, cy = 640, 500
    if 'disc380' not in CACHE: CACHE['disc380'] = disc_layers(R)
    paste_c(im, CACHE['disc380'], cx, cy)
    ta = ease(ramp(t, s(1), s(1) + 1.0))
    if ta > 0:
        d.rectangle((cx - 9, cy - R * ta, cx + 9, cy + R * ta), fill=(15, 15, 22, 255), outline=(220, 220, 230, 200), width=2)
    # fall animation during sentences 1..4: simple back-and-forth illustration, one pass
    f0, f1 = s(1) + 3.5, s(4) + 2.5
    p = ramp(t, f0, f1)
    if t >= f0:
        y = cy - R * math.cos(math.pi * p)
        d.ellipse((cx - 16, y - 16, cx + 16, y + 16), fill=(255, 255, 255, 255), outline=(255, 205, 90, 255), width=4)
        mins = 38 * p
        text(d, (1450, 300), f'{int(mins):02d}:{int((mins % 1) * 60):02d}', 120, WHITE, BLACK, stroke=8)
        text(d, (1450, 380), 'minutes (sped up)', 32, GREY, POP_M)
    text(d, (cx + 40, cy - R + 10), 'jump in', 30, WHITE, POP_B, anchor='lm', stroke=3, alpha=ta)
    text(d, (cx + 40, cy + R - 10), 'other side', 30, WHITE, POP_B, anchor='lm', stroke=3, alpha=ta)
    a = ease(ramp(t, s(2), s(2) + 0.6))
    text(d, (1450, 520), 'Same density everywhere:', 38, GREY, POP_B, stroke=3, alpha=a)
    text(d, (1450, 585), '≈ 42 min', 70, WHITE, BLACK, stroke=6, alpha=a)
    a = ease(ramp(t, s(3) + 2.0, s(3) + 2.6))
    text(d, (1450, 700), 'Real, measured Earth:', 38, GREY, POP_B, stroke=3, alpha=a)
    text(d, (1450, 775), '≈ 38 min', 96, GOLD, BLACK, stroke=8, alpha=a)
    text(d, (1450, 900), '(no air, no heat — a thought experiment)', 28, GREY, POP_M, alpha=ease(ramp(t, s(1), s(1) + 0.6)))

def sc_walk(sc, t, im, d):
    s = sc.sent_t
    y = 620; x0, x1 = 220, 1700
    d.line((x0, y, x1, y), fill=(200, 200, 215, 255), width=6)
    d.ellipse((x1 - 22, y - 22, x1 + 22, y + 22), fill=(255, 235, 170, 255))
    text(d, (x1, y + 60), 'CENTER', 32, GOLD, POP_B)
    text(d, (x0, y + 60), 'SURFACE', 32, WHITE, POP_B)
    p = ease(ramp(t, 0.5, sc.dur - 0.5)) * 0.18
    wx = x0 + (x1 - x0) * p
    ph = math.sin(t * 7)
    # stick figure walker
    hy = y - 150
    d.ellipse((wx - 18, hy - 18, wx + 18, hy + 18), fill=(255, 255, 255, 255))
    d.line((wx, hy + 18, wx, y - 60), fill=(255, 255, 255, 255), width=8)
    d.line((wx, y - 60, wx + 28 * ph, y - 4), fill=(255, 255, 255, 255), width=8)
    d.line((wx, y - 60, wx - 28 * ph, y - 4), fill=(255, 255, 255, 255), width=8)
    d.line((wx, hy + 45, wx - 26 * ph, hy + 95), fill=(255, 255, 255, 255), width=7)
    d.line((wx, hy + 45, wx + 26 * ph, hy + 95), fill=(255, 255, 255, 255), width=7)
    a = ease(ramp(t, s(1), s(1) + 0.6))
    text(d, (W / 2, 210), '6,370 km ÷ 5 km/h', 64, WHITE, BLACK, stroke=6, alpha=a)
    a = ease(ramp(t, s(1) + 3.0, s(1) + 3.6))
    text(d, (W / 2, 330), '≈ 53 DAYS', 120, GOLD, BLACK, stroke=9, alpha=a)
    text(d, (W / 2, 820), 'nonstop · no sleep · just to the center', 38, GREY, POP_B, stroke=3, alpha=a)

def sc_outro(sc, t, im, d):
    s = sc.sent_t
    R = 380; cx, cy = 560, 510
    if 'disc380' not in CACHE: CACHE['disc380'] = disc_layers(R)
    paste_c(im, CACHE['disc380'], cx, cy)
    d.ellipse((cx - 22, cy - R - 22, cx + 22, cy - R + 22), outline=(255, 90, 80, 255), width=4)
    a = ease(ramp(t, s(1), s(1) + 0.6))
    text(d, (1420, 300), '19 YEARS OF DRILLING', 50, WHITE, BLACK, stroke=5, alpha=a)
    text(d, (1420, 400), '≈ 0.19%', 120, GOLD, BLACK, stroke=9, alpha=a)
    a = ease(ramp(t, s(2), s(2) + 0.6))
    text(d, (1420, 540), 'The other 99.8%:', 46, WHITE, POP_B, stroke=4, alpha=a)
    text(d, (1420, 610), 'never seen by anyone', 46, PINK, POP_B, stroke=4, alpha=a)
    a = ease(ramp(t, s(3), s(3) + 0.6))
    if a > 0:
        f = F(BLACK, 54); w = f.getlength('SUBSCRIBE') + 90
        d.rounded_rectangle((1420 - w / 2, 720, 1420 + w / 2, 810), 45, fill=(220, 30, 40, int(255 * a)))
        text(d, (1420, 765), 'SUBSCRIBE', 54, WHITE, BLACK, alpha=a)
        text(d, (1420, 860), 'Explorer Man', 40, GOLD, POP_B, alpha=a)

FUN = dict(intro=sc_intro, kola=sc_kola, scale=sc_scale, crust=sc_crust, mantle=sc_mantle,
           outer=sc_outer, inner=sc_inner, fall=sc_fall, walk=sc_walk, outro=sc_outro)

def build_scenes():
    idx = json.load(open('aud/index.json'))
    out = []
    for key, ch, sents in SCENES:
        ss = [x for x in idx if x['scene'] == key]
        out.append(Scene(key, ch, ss))
    return out

def frame(sc, t):
    im = BG.copy().convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    FUN[sc.key](sc, t, im, d)
    fade = min(ramp(t, 0, 0.35), 1 - ramp(t, sc.dur - 0.3, sc.dur))
    chapter_pill(im, sc.chapter, ease(ramp(t, 0.2, 0.6)) * (1 - ease(ramp(t, 3.5, 4.0))) if sc.key != 'intro' else 0)
    draw_caption(im, sc.cap_at(t), 1.0)
    im = im.convert('RGB')
    if fade < 1:
        im = Image.blend(Image.new('RGB', (W, H)), im, fade)
    return im

if __name__ == '__main__':
    scenes = build_scenes()
    mode = sys.argv[1]
    if mode == 'still':
        name, tt = sys.argv[2], float(sys.argv[3])
        sc = [s for s in scenes if s.key == name][0]
        frame(sc, tt).save(f'still_{name}_{tt}.jpg', quality=90)
    elif mode == 'scene':
        name = sys.argv[2]
        sc = [s for s in scenes if s.key == name][0]
        os.makedirs('scenes', exist_ok=True)
        n = int(round(sc.dur * FPS))
        tmp = f'scenes/{name}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                              '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(n):
            p.stdin.write(frame(sc, i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'scenes/{name}.mp4')
        print(name, n, rc)
    elif mode == 'timing':
        t = 0
        for sc in scenes:
            print(f'{int(t//60)}:{int(t%60):02d} {sc.chapter}  ({sc.dur:.1f}s)'); t += sc.dur
        print('total', t)

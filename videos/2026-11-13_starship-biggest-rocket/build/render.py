import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
START, END = 0.15, 1.2
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

# real figures (facts.md)
H_SHIP, H_SAT, H_LIB = 124.4, 110.6, 93.0

# ---------------------------------------------------------------- background: dusk sky + ground
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(4)
k = (yy / H)[..., None]
sky = np.array([0.015, 0.025, 0.07]) * (1 - k) + np.array([0.10, 0.07, 0.16]) * k
glow = np.exp(-((yy - 1700) / 260) ** 2)[..., None] * np.array([0.42, 0.20, 0.10])
BGA = np.clip(sky + glow, 0, 1)
for _ in range(700):
    x, y = rng.integers(0, W), rng.integers(0, 1300)
    BGA[y, x] += rng.uniform(0.1, 0.6) * (1 - y / 1400)
BG = Image.fromarray((np.clip(BGA, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
GROUND_Y = 1640

def text(d, xy, s, size, col=WHITE, font=BLACK, anchor='mm', stroke=None, alpha=1.0):
    if alpha <= 0.004: return
    if stroke is None: stroke = max(3, size // 12)
    f = F(font, size)
    if alpha >= 0.999:
        d.text(xy, s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 6, 16, 255)); return
    x0, y0, x1, y1 = d.textbbox(xy, s, font=f, anchor=anchor, stroke_width=stroke)
    x0, y0 = max(0, int(x0) - 2), max(0, int(y0) - 2)
    lay = Image.new('RGBA', (int(x1) - x0 + 4, int(y1) - y0 + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0] - x0, xy[1] - y0), s, font=f, fill=tuple(col) + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(4, 6, 16, 255))
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
    d._image.alpha_composite(lay, (x0, y0))

def pill(d, cx, cy, s, size, bg, fg=WHITE, alpha=1.0):
    if alpha <= 0.004: return
    f = F(BLACK, size); w = f.getlength(s) + size * 1.4; h = size * 1.7
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=tuple(bg) + (int(255 * alpha),))
    text(d, (cx, cy), s, size, fg, BLACK, stroke=0, alpha=alpha)

def fade(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a))); return im

def paste_b(im, sp, cx, base_y, alpha=1.0):
    """paste sprite with bottom-centre at (cx, base_y)"""
    if alpha <= 0.004: return
    im.alpha_composite(fade(sp, alpha), (int(cx - sp.width / 2), int(base_y - sp.height)))

def paste_c(im, sp, cx, cy, alpha=1.0):
    if alpha <= 0.004: return
    im.alpha_composite(fade(sp, alpha), (int(cx - sp.width / 2), int(cy - sp.height / 2)))

# ---------------------------------------------------------------- sprites
def cyl_shade(wpx, base, spec=0.5):
    """horizontal metallic shading profile, shape (wpx,3)"""
    u = np.linspace(-1, 1, wpx)
    lam = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    sh = 0.35 + 0.65 * np.clip(lam * 0.6 + 0.5 * (-u * 0.7 + 0.3), 0, 1)
    hl = spec * np.exp(-((u + 0.45) / 0.16) ** 2)
    return np.clip(np.array(base)[None, :] * sh[:, None] + hl[:, None], 0, 1)

def starship_sprite(hpx, part='stack'):
    """Starship V3 stack; hpx = pixel height of full 124.4 m stack. part: stack | booster | ship"""
    SS = 3; m = hpx * SS / H_SHIP           # px per metre
    bw = 9.0 * m; Wd = int(bw * 2.6); Hh = int(hpx * SS) + 4
    arr = np.zeros((Hh, Wd, 4), np.float32); cx = Wd / 2
    y, x = np.mgrid[0:Hh, 0:Wd].astype(np.float32)
    hm = (Hh - y) / m                         # height above ground in metres
    BOOST = 72.3
    half = np.full_like(hm, bw / 2)
    nose0 = H_SHIP - 16.0
    nk = np.clip((hm - nose0) / 16.0, 0, 1)
    half = np.where(hm > nose0, bw / 2 * np.sqrt(np.clip(1 - nk ** 1.9, 0, 1)), half)
    u = (x - cx) / np.maximum(half, 1e-3)
    inside = (np.abs(u) <= 1) & (hm >= 0) & (hm <= H_SHIP)
    lam = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    sh = 0.35 + 0.65 * np.clip(lam * 0.6 + 0.5 * (-u * 0.7 + 0.3), 0, 1)
    hl = 0.45 * np.exp(-((u + 0.45) / 0.16) ** 2)
    steel = np.array([0.74, 0.76, 0.80])
    col = steel[None, None, :] * sh[..., None] + hl[..., None]
    # weld rings
    ring = (np.abs((hm % 3.6) - 1.8) > 1.74)
    col[ring] *= 0.86
    # ship heat-shield tiles (dark) on the right/windward side
    ship = hm > BOOST
    tiles = ship & (u > -0.05)
    tcol = np.array([0.07, 0.07, 0.085])[None, None, :] * (0.7 + 0.6 * lam[..., None]) + 0.10 * np.exp(-((u - 0.35) / 0.2) ** 2)[..., None]
    col = np.where(tiles[..., None], tcol, col)
    # hot-stage ring (vented interstage)
    hs = (hm > BOOST - 1.8) & (hm <= BOOST)
    col[hs] *= 0.45
    vent = hs & ((x.astype(int) // max(2, int(0.45 * m))) % 2 == 0)
    col[vent] *= 0.4
    # frost band near booster LOX
    arr[..., :3] = np.clip(col, 0, 1); arr[..., 3] = inside
    # flaps (ship): forward + aft, grid fins (booster)
    def quad(pts, c):
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(im)
        d.polygon([(cx + px * m, Hh - py * m) for px, py in pts], fill=c); return np.array(im, np.float32) / 255
    for sgn in (-1, 1):
        dark = (22, 22, 26, 255) if sgn > 0 else (150, 154, 162, 255)
        arr = quad([(sgn * 4.4, BOOST + 1.5), (sgn * 8.3, BOOST + 1.0), (sgn * 8.3, BOOST + 9.0), (sgn * 4.4, BOOST + 14.5)], dark)      # aft flap
        arr = quad([(sgn * 4.0, H_SHIP - 15.5), (sgn * 6.6, H_SHIP - 16.5), (sgn * 6.3, H_SHIP - 11.0), (sgn * 3.2, H_SHIP - 7.5)], dark)  # forward flap
        arr = quad([(sgn * 4.4, BOOST - 3.2), (sgn * 7.6, BOOST - 3.2), (sgn * 7.6, BOOST - 5.0), (sgn * 4.4, BOOST - 5.0)], (95, 98, 106, 255))  # grid fin
    # engine skirt shadow
    sk = (hm < 2.0) & (np.abs(x - cx) <= bw / 2)
    arr[sk, :3] *= 0.5
    if part == 'booster':
        arr[(hm > BOOST)[...]] = 0
    elif part == 'ship':
        arr[(hm <= BOOST)[...]] = 0
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA')
    im = im.resize((Wd // SS, Hh // SS), Image.LANCZOS)
    if part == 'booster': im = im.crop((0, int(im.height * (1 - 72.3 / H_SHIP)) - 1, im.width, im.height))
    if part == 'ship': im = im.crop((0, 0, im.width, int(im.height * (1 - 72.3 / H_SHIP)) + 1))
    return im

def saturn_sprite(hpx):
    """Saturn V, hpx = pixel height of 110.6 m"""
    SS = 3; m = hpx * SS / H_SAT
    Wd = int(10.1 * m * 2.2); Hh = int(hpx * SS) + 4; cx = Wd / 2
    y, x = np.mgrid[0:Hh, 0:Wd].astype(np.float32); hm = (Hh - y) / m
    # radius profile (m): S-IC/S-II 10.1 dia to 66 m; taper to 6.6 at 71; S-IVB to 88; taper to 3.9 at 93 (SLA->CSM); CSM to 101; LES tower to 110.6
    r = np.select([hm < 66, hm < 71, hm < 86, hm < 92, hm < 99, hm < 101.5, hm <= H_SAT],
                  [5.05, 5.05 - (hm - 66) / 5 * 1.75, 3.3, 3.3 - (hm - 86) / 6 * 1.35, 1.95, 1.95 * (1 - (hm - 99) / 2.5) + 0.3, 0.3], 0)
    half = r * m
    u = (x - cx) / np.maximum(half, 1e-3)
    inside = (np.abs(u) <= 1) & (hm >= 0) & (hm <= H_SAT)
    lam = np.sqrt(np.clip(1 - u ** 2, 0, 1))
    sh = 0.4 + 0.6 * np.clip(lam * 0.6 + 0.5 * (-u * 0.7 + 0.3), 0, 1)
    col = np.ones((Hh, Wd, 3), np.float32) * 0.93
    # black roll-pattern bands
    blk = ((hm < 8) & (np.abs(u) > 0.45)) | ((hm > 34) & (hm < 42) & ((u > 0.1) | (u < -0.6))) | ((hm > 62) & (hm < 66)) | ((hm > 71) & (hm < 73)) | ((hm > 84) & (hm < 86) & (u > 0)) | (hm > 101.5)
    col[blk] = 0.10
    col *= sh[..., None]
    arr = np.concatenate([col, inside[..., None].astype(np.float32)], -1)
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA'); d = ImageDraw.Draw(im)
    for sgn in (-1, 1):  # fins + engine fairings
        d.polygon([(cx + sgn * 5.05 * m, Hh - 7 * m), (cx + sgn * 8.3 * m, Hh - 0.3 * m), (cx + sgn * 5.05 * m, Hh - 0.3 * m)], fill=(60, 60, 66, 255))
    return im.resize((Wd // SS, Hh // SS), Image.LANCZOS)

def liberty_sprite(hpx):
    """Statue of Liberty silhouette (ground to torch 93 m): pedestal+base 46.9 m, statue 46.1 m"""
    SS = 3; m = hpx * SS / H_LIB
    Wd = int(48 * m); Hh = int(hpx * SS) + 4; cx = Wd / 2
    im = Image.new('RGBA', (Wd, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda px, py: (cx + px * m, Hh - py * m)
    stone = (150, 140, 125, 255); stone2 = (120, 112, 100, 255); cu = (95, 170, 150, 255); cu2 = (70, 135, 120, 255)
    # star fort base + pedestal
    d.polygon([P(-21, 0), P(21, 0), P(19, 10), P(-19, 10)], fill=stone2)
    d.polygon([P(-11, 10), P(11, 10), P(9.5, 20), P(-9.5, 20)], fill=stone)
    d.polygon([P(-8, 20), P(8, 20), P(6.5, 44), P(-6.5, 44)], fill=stone)
    d.rectangle([P(-8.5, 46.9), P(8.5, 43.5)], fill=stone2)
    for xx_ in (-4, 0, 4): d.rectangle([P(xx_ - 0.8, 38), P(xx_ + 0.8, 26)], fill=stone2)
    # robed body
    d.polygon([P(-7, 46.9), P(7, 46.9), P(5.2, 62), P(4.2, 74), P(-3.6, 74), P(-5.6, 62)], fill=cu)
    d.polygon([P(0.5, 46.9), P(7, 46.9), P(5.2, 62), P(4.2, 74), P(1.5, 74)], fill=cu2)
    # left arm with tablet
    d.polygon([P(-3.6, 72), P(-7.2, 66), P(-6.2, 61), P(-3.2, 64)], fill=cu2)
    d.polygon([P(-8.2, 67.5), P(-5.4, 68.5), P(-4.6, 61.5), P(-7.4, 60.5)], fill=cu)
    # head + crown
    d.ellipse([P(-2.0, 80.6), P(2.2, 75.2)], fill=cu)
    d.rectangle([P(-1.2, 76), P(1.4, 73.5)], fill=cu)
    for ang in (-70, -45, -20, 5, 30, 55, 80):
        a = math.radians(90 - ang * 0.9)
        d.polygon([P(0.1 + 1.6 * math.cos(a) - 0.35, 79.6 + 1.2 * math.sin(a)), P(0.1 + 1.6 * math.cos(a) + 0.35, 79.6 + 1.2 * math.sin(a)), P(0.1 + 4.6 * math.cos(a), 79.6 + 4.2 * math.sin(a))], fill=cu)
    # raised right arm + torch (tip at 93 m)
    d.polygon([P(2.2, 73.5), P(4.4, 72), P(7.6, 86.5), P(6.0, 87.2)], fill=cu)
    d.polygon([P(5.4, 87), P(8.4, 87), P(7.8, 88.6), P(6.0, 88.6)], fill=cu2)
    d.polygon([P(6.0, 88.6), P(7.8, 88.6), P(7.5, 91.4), P(6.9, 93.0), P(6.2, 91.0)], fill=(255, 200, 80, 255))
    arr = np.array(im, np.float32)
    kx = np.linspace(1.12, 0.8, arr.shape[1])[None, :, None]
    arr[..., :3] = np.clip(arr[..., :3] * kx, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA').resize((Wd // SS, Hh // SS), Image.LANCZOS)

def flame_sprite(w, h, seed, hot=1.0):
    r = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (x - w / 2) / (w / 2); v = y / h
    wid = (0.55 + 0.45 * v) * (1 - 0.25 * v)
    core = np.exp(-(u / (wid * 0.45)) ** 2) * (1 - v) ** 0.7
    outer = np.exp(-(u / (wid * 0.9)) ** 2) * (1 - v) ** 1.4
    n = r.random((h // 12 + 2, w // 12 + 2)).astype(np.float32)
    n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    outer *= 0.7 + 0.6 * n
    rgb = np.stack([np.clip(outer * 1.4 + core, 0, 1), np.clip(outer * 0.75 + core * 0.95, 0, 1), np.clip(outer * 0.45 + core * 1.1, 0, 1)], -1)
    a = np.clip(outer * 1.3 + core, 0, 1) * hot
    return Image.fromarray((np.concatenate([rgb, a[..., None]], -1) * 255).astype(np.uint8), 'RGBA')

CACHE = {}
def sp(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]

def ground(im, d, alpha=1.0, y=GROUND_Y):
    d.rectangle((0, y, W, H), fill=(10, 10, 16, int(255 * alpha)))
    d.line((0, y, W, y), fill=(70, 60, 70, int(255 * alpha)), width=3)

_bm = np.clip(1 - (np.arange(H) - 430) / 130, 0, 1)
BAND = Image.fromarray(np.repeat((_bm * 255).astype(np.uint8)[:, None], W, 1), 'L')
def band(im, alpha):
    lay = Image.fromarray((np.clip(BGA, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    lay.putalpha(BAND.point(lambda v: int(v * alpha)))
    im.alpha_composite(lay)

def ruler(d, x, y_top, y_bot, label, col, alpha, side=1):
    if alpha <= 0.004: return
    c = tuple(col) + (int(255 * alpha),)
    d.line((x, y_top, x, y_bot), fill=c, width=4)
    for yy_ in (y_top, y_bot): d.line((x - 14, yy_, x + 14, yy_), fill=c, width=4)

# engine layout: 33 Raptors = 3 centre + 10 middle + 20 outer
def engine_view(d, cx, cy, R, t, t_on, alpha):
    if alpha <= 0.004: return
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(38, 40, 48, int(255 * alpha)), outline=(190, 195, 205, int(255 * alpha)), width=6)
    rings = [(3, 0.13, 30), (10, 0.42, 0), (20, 0.80, 9)]
    idx = 0; er = R * 0.095
    for n, rr, off in rings:
        for i in range(n):
            a = math.radians(off + 360 * i / n)
            ex, ey = cx + R * rr * math.cos(a), cy + R * rr * math.sin(a)
            on = ease(ramp(t, t_on + idx * 0.035, t_on + idx * 0.035 + 0.25))
            d.ellipse((ex - er, ey - er, ex + er, ey + er), fill=(18, 18, 22, int(255 * alpha)), outline=(120, 124, 135, int(255 * alpha)), width=3)
            if on > 0:
                fl = 0.85 + 0.15 * math.sin(t * 40 + idx)
                g = er * (1.2 + 0.15 * fl)
                d.ellipse((ex - g, ey - g, ex + g, ey + g), fill=(255, 140, 40, int(90 * on * alpha)))
                d.ellipse((ex - er * 0.85, ey - er * 0.85, ex + er * 0.85, ey + er * 0.85), fill=(255, 190, 90, int(255 * on * alpha)))
                d.ellipse((ex - er * 0.45, ey - er * 0.45, ex + er * 0.45, ey + er * 0.45), fill=(255, 250, 235, int(255 * on * alpha)))
            idx += 1

def tower(im, d, x, base_y, m, arm_y, arm_open, alpha=1.0, arm2_y=None, arm2_open=1.0):
    """launch tower (146 m) with chopstick arms at height arm_y (m). arms extend to the left."""
    if alpha <= 0.004: return
    a = int(255 * alpha); tw = 11 * m; th = 146 * m
    d.rectangle((x, base_y - th, x + tw, base_y), fill=(34, 36, 44, a), outline=(110, 115, 128, a), width=3)
    n = 16
    for i in range(n):
        y0 = base_y - th * i / n; y1 = base_y - th * (i + 1) / n
        d.line((x, y0, x + tw, y1), fill=(90, 95, 108, a), width=2)
        d.line((x + tw, y0, x, y1), fill=(90, 95, 108, a), width=2)
    d.rectangle((x + tw * 0.3, base_y - th - 8 * m, x + tw * 0.7, base_y - th), fill=(60, 62, 72, a))
    for ay, op in ((arm_y, arm_open), (arm2_y, arm2_open)):
        if ay is None: continue
        y = base_y - ay * m; L = 34 * m
        d.rectangle((x - 3 * m, y - 5 * m, x + 2, y + 5 * m), fill=(70, 74, 86, a))
        # two arms seen from the side: draw as a pair, spread vertically a touch to read as "chopsticks"
        gap = (2.0 + 5.0 * op) * m
        for sgn in (-1, 1):
            yy_ = y + sgn * gap * 0.35
            d.polygon([(x - 3 * m, yy_ - 1.6 * m), (x - L, yy_ - 0.9 * m), (x - L, yy_ + 0.9 * m), (x - 3 * m, yy_ + 1.6 * m)], fill=(200, 204, 214, a) if sgn < 0 else (140, 144, 156, a))

def bar(d, x0, y, wmax, frac, col, alpha, h=70):
    if alpha <= 0.004: return
    d.rounded_rectangle((x0, y, x0 + wmax, y + h), 14, outline=(120, 128, 150, int(255 * alpha)), width=2)
    if frac > 0.01: d.rounded_rectangle((x0, y, x0 + wmax * frac, y + h), 14, fill=tuple(col) + (int(255 * alpha),))

# ---------------------------------------------------------------- frame
M1 = 1180 / H_SHIP          # px per metre in the height scenes (shared scale => drawn to scale)
def xf(t, a, b, fi=0.3, fo=0.3):
    """visible between a and b with fades"""
    return ease(ramp(t, a, a + fi)) * (1 - ease(ramp(t, b - fo, b)))

def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    ship_full = sp('ship', lambda: starship_sprite(H_SHIP * M1))
    # ============ height scenes: hook .. saturn
    a_hs = 1 - ease(ramp(t, st('engines') - 0.35, st('engines') - 0.05))
    if a_hs > 0:
        ground(im, d, a_hs)
        # starship x position: centre during hook/height, slides left for comparisons
        sl = ease(ramp(t, st('liberty') - 0.3, st('liberty') + 0.4))
        sx = W / 2 - 230 * sl
        rise = ease(ramp(t, 0.0, 0.9))
        paste_b(im, ship_full, sx, GROUND_Y + (1 - rise) * 500, a_hs)
        # hook text
        a = xf(t, 0.05, st('height') - 0.05, 0.25, 0.25)
        text(d, (W / 2, 200), 'THE TALLEST,', 84, WHITE, alpha=a)
        text(d, (W / 2, 300), 'MOST POWERFUL', 100, GOLD, alpha=a)
        text(d, (W / 2, 400), 'ROCKET EVER BUILT', 76, WHITE, alpha=a)
        # height
        a = xf(t, st('height'), st('liberty') - 0.05) * a_hs
        text(d, (W / 2, 180), 'STARSHIP', 110, WHITE, alpha=a)
        text(d, (W / 2 + 330, 900), '124 m', 120, CYAN, alpha=a)
        text(d, (W / 2 + 330, 990), '408 feet', 54, WHITE, POP_B, alpha=a)
        gr = ease(ramp(t, st('height') + 0.2, st('height') + 1.6))
        if a > 0:
            rx = W / 2 + 120; yb = GROUND_Y; yt = GROUND_Y - H_SHIP * M1 * gr
            ruler(d, rx, yt, yb, '', CYAN, a)
        # liberty
        lib = sp('lib', lambda: liberty_sprite(H_LIB * M1))
        a_l = xf(t, st('liberty'), st('saturn') - 0.05) * a_hs
        paste_b(im, lib, W / 2 + 250, GROUND_Y, a_l)
        text(d, (W / 2, 170), 'TALLER THAN THE', 70, WHITE, alpha=a_l)
        text(d, (W / 2, 265), 'STATUE OF LIBERTY', 86, GOLD, alpha=a_l)
        text(d, (W / 2 + 250, GROUND_Y + 60), '93 m', 64, GOLD, alpha=a_l)
        text(d, (sx, GROUND_Y + 60), '124 m', 64, CYAN, alpha=max(a_l, xf(t, st('saturn'), st('engines') - 0.05)) * a_hs)
        a_d = a_l * ease(ramp(t, st('liberty') + 3.2, st('liberty') + 3.6))
        if a_d > 0:
            y_l = GROUND_Y - H_LIB * M1; y_s = GROUND_Y - H_SHIP * M1
            for xq in range(int(sx + 60), int(W / 2 + 420), 26):
                d.line((xq, y_l, xq + 13, y_l), fill=(255, 205, 90, int(230 * a_d)), width=3)
                d.line((xq, y_s, xq + 13, y_s), fill=(90, 215, 255, int(230 * a_d)), width=3)
            ruler(d, W / 2 + 400, y_s, y_l, '', WHITE, a_d)
            text(d, (W / 2 + 250, (y_l + y_s) / 2), '+31 m', 76, WHITE, alpha=a_d)
        # saturn
        sat = sp('sat', lambda: saturn_sprite(H_SAT * M1))
        a_s = xf(t, st('saturn'), st('engines') - 0.05) * a_hs
        paste_b(im, sat, W / 2 + 250, GROUND_Y, a_s)
        text(d, (W / 2, 170), 'TALLER THAN THE', 70, WHITE, alpha=a_s)
        text(d, (W / 2, 265), 'SATURN V', 110, GOLD, alpha=a_s)
        text(d, (W / 2, 350), 'the Apollo Moon rocket', 44, WHITE, POP_B, alpha=a_s)
        text(d, (W / 2 + 250, GROUND_Y + 60), '111 m', 64, GOLD, alpha=a_s)
        a_sc = max(a_l, a_s)
        text(d, (W / 2, GROUND_Y + 150), 'drawn to scale', 38, GREY, POP_M, stroke=3, alpha=a_sc)

    # ============ engines + thrust
    e0 = st('engines'); a_e = xf(t, e0, st('tease') - 0.05)
    if a_e > 0:
        a1 = a_e * (1 - ease(ramp(t, st('twice') - 0.3, st('twice'))))
        text(d, (W / 2, 190), '33 ENGINES', 130, GOLD, alpha=a1)
        text(d, (W / 2, 300), 'fire together at liftoff', 48, WHITE, POP_B, alpha=a1)
        engine_view(d, W / 2, 870, 400, t, e0 + 1.0, a1)
        text(d, (W / 2, 1330), 'booster seen from below (illustration)', 34, GREY, POP_M, stroke=3, alpha=a1)
        a2 = a1 * ease(ramp(t, e0 + 3.6, e0 + 4.0))
        text(d, (W / 2, 1480), 'MORE THAN', 64, WHITE, alpha=a2)
        text(d, (W / 2, 1590), '18 MILLION LB', 124, CYAN, alpha=a2)
        text(d, (W / 2, 1700), 'OF THRUST', 70, WHITE, alpha=a2)
        # twice
        a3 = a_e * ease(ramp(t, st('twice'), st('twice') + 0.3))
        text(d, (W / 2, 200), 'MORE THAN', 84, WHITE, alpha=a3)
        text(d, (W / 2, 330), '2× SATURN V', 140, GOLD, alpha=a3)
        g = ease(ramp(t, st('twice') + 0.3, st('twice') + 1.5))
        bw = 880; x0 = 100
        text(d, (x0, 620), 'SATURN V', 54, WHITE, anchor='lm', alpha=a3)
        bar(d, x0, 670, bw, g * 7.7 / 18.2, WHITE, a3)
        text(d, (x0, 800), '≈7.7 million lb', 50, GREY, POP_B, anchor='lm', alpha=a3)
        text(d, (x0, 980), 'STARSHIP', 54, CYAN, anchor='lm', alpha=a3)
        bar(d, x0, 1030, bw, g * 1.0, CYAN, a3)
        text(d, (x0, 1160), '>18 million lb', 50, CYAN, POP_B, anchor='lm', alpha=a3)
        text(d, (W / 2, 1400), 'liftoff thrust · bars to scale', 38, GREY, POP_M, stroke=3, alpha=a3)

    # ============ tease
    a_t = xf(t, st('tease'), st('catch') - 0.05, 0.2, 0.25)
    text(d, (W / 2, 760), "BUT HERE'S THE", 96, WHITE, alpha=a_t)
    text(d, (W / 2, 900), 'CRAZY PART', 150, GOLD, alpha=a_t)

    # ============ catch (booster) and both (plan)
    c0 = st('catch'); a_c = xf(t, c0, st('outro') - 0.1, 0.3, 0.3)
    if a_c > 0:
        MC = 8.2  # px per metre
        ground(im, d, a_c)
        tx = 700
        boost = sp('boost', lambda: starship_sprite(H_SHIP * MC, 'booster'))
        shp = sp('shp', lambda: starship_sprite(H_SHIP * MC, 'ship'))
        in_both = t >= st('both') - 0.2
        if not in_both:
            # booster descends beside tower and is caught at ~c0+6.2
            tc = c0 + 6.4
            p = ease(ramp(t, c0 + 0.3, tc))
            arm_h = 96.0
            by_final = GROUND_Y - (arm_h - 66) * MC        # booster base y when hanging: top (72 m) sits ~6 m above arms
            by = by_final - (1 - p) ** 1.6 * 1500
            bx = tx - 20 * MC + (1 - p) * -160
            close = ease(ramp(t, tc - 0.5, tc))
            tower(im, d, tx, GROUND_Y, MC, arm_h, 1 - close, a_c)
            if p < 1:
                fl = flame_sprite(int(11 * MC), int((34 + 6 * math.sin(t * 31)) * MC * (1 - 0.6 * ease(ramp(t, tc - 0.6, tc)))) + 2, int(t * 30) % 7)
                im.alpha_composite(fade(fl, a_c), (int(bx - fl.width / 2), int(by - 4)))
            paste_b(im, boost, bx, by, a_c)
            band(im, a_c); d = ImageDraw.Draw(im, 'RGBA')
            a1 = a_c * (1 - ease(ramp(t, c0 + 3.0, c0 + 3.3)))
            text(d, (W / 2, 200), 'THE BOOSTER', 96, WHITE, alpha=a1)
            text(d, (W / 2, 320), "DOESN'T LAND", 116, GOLD, alpha=a1)
            a2 = a_c * ease(ramp(t, c0 + 3.4, c0 + 3.8))
            text(d, (W / 2, 200), 'THE TOWER', 96, WHITE, alpha=a2)
            text(d, (W / 2, 320), 'CATCHES IT', 126, CYAN, alpha=a2)
            a3 = a_c * ease(ramp(t, tc, tc + 0.3))
            text(d, (300, 1010), 'CAUGHT', 84, GOLD, alpha=a3)
            text(d, (300, 1090), 'first done Oct 2024', 38, WHITE, POP_B, stroke=3, alpha=a3)
        else:
            b0 = st('both')
            arm_hi = 84.0
            tower(im, d, tx, GROUND_Y, MC, arm_hi, 1 - ease(ramp(t, b0 + 4.2, b0 + 4.8)), a_c)
            bx = tx - 20 * MC
            p = ease(ramp(t, b0 + 0.4, b0 + 4.8))
            ship_base_final = GROUND_Y - (arm_hi - 44) * MC
            sy = ship_base_final - (1 - p) ** 1.6 * 1000
            if p < 1:
                fl = flame_sprite(int(9 * MC), int((22 + 4 * math.sin(t * 29)) * MC) + 2, int(t * 30) % 7)
                im.alpha_composite(fade(fl, a_c), (int(bx - fl.width / 2), int(sy - 4)))
            paste_b(im, shp, bx, sy, a_c)
            band(im, a_c); d = ImageDraw.Draw(im, 'RGBA')
            text(d, (W / 2, 190), 'FLIGHT 15: THE PLAN', 70, WHITE, alpha=a_c)
            text(d, (W / 2, 310), 'CATCH BOTH STAGES', 88, GOLD, alpha=a_c)
            text(d, (W / 2, 410), 'for the first time', 50, WHITE, POP_B, alpha=a_c)
            text(d, (250, 640), '1. BOOSTER', 56, WHITE, alpha=a_c)
            text(d, (250, 720), '2. SHIP', 56, CYAN, alpha=a_c)
            text(d, (W / 2, GROUND_Y + 110), 'illustration of the plan', 36, GREY, POP_M, stroke=3, alpha=a_c)

    # ============ outro
    a_o = ease(ramp(t, st('outro'), st('outro') + 0.3))
    if a_o > 0:
        text(d, (W / 2, 760), 'FOLLOW', 150, WHITE, alpha=a_o)
        text(d, (W / 2, 920), 'FOR MORE', 150, GOLD, alpha=a_o)
        text(d, (W / 2, 1060), 'Explorer Man', 60, CYAN, POP_B, alpha=a_o)
    out = im.convert('RGB')
    f = min(ramp(t, 0, 0.12), 1 - ramp(t, TOTAL - 0.2, TOTAL))
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
        n = int(round(TOTAL * FPS)); tmp = 'video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, 'video.mp4')
        print('rendered', n, rc)

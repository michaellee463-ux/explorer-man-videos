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


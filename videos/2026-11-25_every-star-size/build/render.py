import json, math, sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from script import SCENES

W, H, FPS = 1920, 1080, 30
END = 0.25
POP_B = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
POP_M = '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
_fc = {}
def F(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]
WHITE = (255, 255, 255); GOLD = (255, 205, 90); CYAN = (90, 215, 255); RED = (255, 80, 70)
GREY = (170, 178, 195); ORANGE = (255, 150, 60)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return min(max((t - a) / (b - a), 0), 1)
def pop(t, a, d=0.35): return ease(ramp(t, a, a + d))

# ---------------------------------------------------------------- background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
bg = np.zeros((H, W, 3), np.float32); bg[:] = np.array([0.02, 0.025, 0.055])
r2 = ((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2
bg *= (1.3 - 1.2 * r2)[..., None]
for _ in range(1400):
    x, y = rng.integers(0, W), rng.integers(0, H); bg[y, x] += rng.uniform(0.05, 0.45)
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
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), h / 2, fill=tuple(bgc) + (int(235 * alpha),))
    d.text((x, y), s, font=f, fill=tuple(fg) + (int(255 * alpha),), anchor='mm')

def wrap(s, font, maxw):
    words = s.split(); lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if font.getlength(t) > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    if cur: lines.append(cur)
    return lines

CAP = [("eight hundred years", "800 years"), ("a hundred and nine", "109"), ("one point three million", "1.3 million"),
       ("fifteen seconds", "15 seconds"), ("seven months", "7 months"), ("eight point six light-years", "8.6 light-years"),
       ("one point seven", "1.7"), ("twenty-five", "25"), ("fifteen thousand", "15,000"), ("five billion", "5 billion"),
       ("sixty-five", "65"), ("forty-four", "44"), ("five thousand", "5,000"), ("eight hundred and sixty", "860"),
       ("seventy-five", "75"), ("eighteen minutes", "18 minutes"), ("seven hundred and fifty", "750"), ("seven hundred", "700"),
       ("three hours", "3 hours"), ("five hundred and fifty", "550"), ("a hundred thousand", "100,000"),
       ("one thousand four hundred and twenty", "1,420"), ("three billion", "3 billion"), ("six hours", "6 hours"),
       ("Stephenson two eighteen", "Stephenson 2-18"), ("fifteen hundred to two thousand", "1,500 to 2,000"),
       ("a hundred and sixty thousand", "160,000"), ("two hundred", "200"), ("thirty-five to forty", "35 to 40")]
def caption(s):
    for a, b in CAP: s = s.replace(a, b)
    return s

def draw_caption(d, s):
    if not s: return
    f = F(POP_M, 40)
    lines = wrap(s, f, 1560)
    y0 = H - 50 - (len(lines) - 1) * 52
    for i, ln in enumerate(lines):
        bw = f.getlength(ln) + 40
        d.rounded_rectangle((W / 2 - bw / 2, y0 + i * 52 - 27, W / 2 + bw / 2, y0 + i * 52 + 27), 12, fill=(0, 0, 0, 140))
        d.text((W / 2, y0 + i * 52), ln, font=f, fill=(255, 255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, 255))

# ---------------------------------------------------------------- stars
STARS = [  # name, radius in solar radii (facts.md), colour, sprite style, label
    ('Sun', 1.0, (255, 214, 140), 'sun', 'SUN'),
    ('Sirius', 1.7, (205, 222, 255), 'hot', 'SIRIUS'),
    ('Arcturus', 25.0, (255, 165, 85), 'giant', 'ARCTURUS'),
    ('Aldebaran', 44.0, (255, 140, 70), 'giant', 'ALDEBARAN'),
    ('Rigel', 75.0, (160, 195, 255), 'hot', 'RIGEL'),
    ('Antares', 700.0, (255, 95, 55), 'super', 'ANTARES'),
    ('Betelgeuse', 750.0, (255, 115, 60), 'super', 'BETELGEUSE'),
    ('VY', 1420.0, (235, 80, 50), 'super', 'VY CANIS MAJORIS'),
]
IDX = {s[0]: i for i, s in enumerate(STARS)}
# world layout (solar radii): bottom-aligned on y=0, left to right
XC = []; xr = 0.0
for i, (n, R, *_r) in enumerate(STARS):
    gap = 0.0 if i == 0 else max(0.35 * R, 0.8)
    if n == 'Betelgeuse': gap = 0.08 * R
    XC.append(xr + gap + R); xr = XC[-1] + R

def noise(S, seed, octaves=((6, 0.5), (14, 0.3), (34, 0.2))):
    g = np.random.default_rng(seed); out = np.zeros((S, S), np.float32)
    for n, a in octaves:
        small = g.standard_normal((n, n)).astype(np.float32)
        im = Image.fromarray(((small - small.min()) / (np.ptp(small) + 1e-6) * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
        out += a * (np.asarray(im, np.float32) / 255 - 0.5)
    return out

def make_star(col, style, S=1024, seed=1):
    c = S / 2; R = S / 2 - 2
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(x - c, y - c) / R
    mu = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    if style == 'super':
        nz = noise(S, seed, ((4, 0.6), (9, 0.35), (22, 0.15)))
        limb = 0.35 + 0.65 * mu ** 0.7; amp = 0.55
    elif style == 'giant':
        nz = noise(S, seed, ((8, 0.5), (20, 0.35), (50, 0.15)))
        limb = 0.4 + 0.6 * mu ** 0.6; amp = 0.35
    elif style == 'hot':
        nz = noise(S, seed, ((10, 0.4), (40, 0.4), (90, 0.2)))
        limb = 0.55 + 0.45 * mu ** 0.5; amp = 0.12
    else:
        nz = noise(S, seed, ((12, 0.3), (60, 0.4), (140, 0.3)))
        limb = 0.45 + 0.55 * mu ** 0.6; amp = 0.22
    base = np.array(col, np.float32) / 255
    bright = limb * (1 + amp * nz * 2)
    rgb = base[None, None] * bright[..., None]
    rgb = rgb + (np.clip(bright - 0.85, 0, 1) * 0.6)[..., None]  # hot white centre
    a = np.clip((1 - rr) * R / 1.5, 0, 1)
    rgba = np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)
    return Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')

SPR = {}
def star_sprite(i):
    if i not in SPR:
        n, R, col, style, _ = STARS[i]
        SPR[i] = make_star(col, style, 2048 if n in ('VY', 'Antares', 'Betelgeuse') else 1024, seed=i + 3)
    return SPR[i]
R136 = dict(col=(175, 205, 255))
def r136_sprite():
    if 'r136' not in SPR: SPR['r136'] = make_star(R136['col'], 'hot', 1024, seed=40)
    return SPR['r136']

def glow_sprite(col, S=512):
    key = ('glow', col)
    if key not in SPR:
        c = S / 2; y, x = np.mgrid[0:S, 0:S].astype(np.float32)
        rr = np.hypot(x - c, y - c) / c
        a = np.clip(1 - rr, 0, 1) ** 2.2 * 0.55
        im = np.zeros((S, S, 4), np.float32); im[..., :3] = np.array(col) / 255; im[..., 3] = a
        SPR[key] = Image.fromarray((im * 255).astype(np.uint8), 'RGBA')
    return SPR[key]

def paste_scaled(im, sp, cx, cy, r):
    """paste a square sprite so it covers a circle of radius r (px) centred at cx, cy; crops to screen."""
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    vx0, vy0, vx1, vy1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    if vx1 - vx0 < 1 or vy1 - vy0 < 1: return
    k = sp.width / (2 * r)
    box = ((vx0 - x0) * k, (vy0 - y0) * k, (vx1 - x0) * k, (vy1 - y0) * k)
    ix0, iy0 = int(math.floor(vx0)), int(math.floor(vy0))
    w_, h_ = int(math.ceil(vx1)) - ix0, int(math.ceil(vy1)) - iy0
    if w_ < 1 or h_ < 1: return
    piece = sp.resize((w_, h_), Image.BILINEAR, box=box)
    im.alpha_composite(piece, (ix0, iy0))

def draw_star(im, d, sp, col, cx, cy, r, glow=True):
    if r < 2.0:
        g = glow_sprite(col); paste_scaled(im, g, cx, cy, 9)
        rr = max(r, 1.6)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tuple(min(255, c + 40) for c in col) + (255,))
        return
    if glow: paste_scaled(im, glow_sprite(col), cx, cy, r * 1.35 + 8)
    paste_scaled(im, sp, cx, cy, r)

def earth_dot(d, x, y, r):
    r = max(r, 2.2)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(70, 140, 255, 255))

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

BASE = H * 0.80     # screen y of the ladder baseline
FOCUS_X = W * 0.64  # screen x of the focused star's centre
FILL = 0.33         # focused star radius as fraction of H

def cam_for(k):
    return (FILL * H / STARS[k][1], XC[k])

def lerp_cam(c0, c1, u):
    s = math.exp(math.log(c0[0]) * (1 - u) + math.log(c1[0]) * u)
    return (s, c0[1] * (1 - u) + c1[1] * u)

def draw_ladder(im, d, cam, labels=True, upto=None, la=1.0, sun_arrow=True, hide=()):
    s, xw0 = cam
    n = len(STARS) if upto is None else upto + 1
    for i in range(n):
        if STARS[i][0] in hide: continue
        name, R, col, style, lab = STARS[i]
        cx = FOCUS_X + (XC[i] - xw0) * s; r = R * s; cy = BASE - r
        if cx + r < -50 or cx - r > W + 50: continue
        draw_star(im, d, star_sprite(i), col, cx, cy, r)
    d = ImageDraw.Draw(im, 'RGBA')
    if labels and la > 0.01:
        for i in range(n):
            if STARS[i][0] in hide: continue
            name, R, col, style, lab = STARS[i]
            cx = FOCUS_X + (XC[i] - xw0) * s; r = R * s
            if cx < -50 or cx > W + 50: continue
            if r >= 40 or (r >= 22 and i == n - 1):
                text(d, (cx, BASE + 34), lab, 30 if r < 120 else 38, col, POP_B, alpha=la, stroke=3)
    if sun_arrow:
        cx = FOCUS_X + (XC[0] - xw0) * s; r = STARS[0][1] * s
        if r < 22 and -20 < cx < W + 20:
            d.line((cx, BASE - 2 * r - 14, cx, BASE - 2 * r - 90), fill=(255, 214, 140, int(230 * la)), width=4)
            d.polygon([(cx, BASE - 2 * r - 8), (cx - 10, BASE - 2 * r - 26), (cx + 10, BASE - 2 * r - 26)], fill=(255, 214, 140, int(230 * la)))
            text(d, (cx, BASE - 2 * r - 115), 'SUN', 34, (255, 214, 140), POP_B, alpha=la, stroke=3)
    return d

def headline(d, t, a, name, sub, col):
    al = pop(t, a, 0.3)
    if al <= 0: return
    text(d, (70, 105), name, 78, col, BLACK, anchor='lm', alpha=al)
    if sub: pill(d, (70 + F(POP_B, 38).getlength(sub) / 2 + 23, 190), sub, 38, GOLD, alpha=al)

def callout(d, t, a, s, y=300, col=WHITE, size=54, x=70, anchor='lm', dur=None):
    al = pop(t, a, 0.3) * (1 - pop(t, dur, 0.3) if dur else 1)
    text(d, (x, y), s, size, col, BLACK, anchor=anchor, alpha=al)

def ladder_scene(k, info, extra=None):
    """generic rung: zoom out from star k-1 to star k, then show callouts."""
    def fn(sc, t, im, d):
        u = ease(ramp(t, 0.0, 1.8))
        cam = lerp_cam(cam_for(k - 1), cam_for(k), u)
        d = draw_ladder(im, d, cam, la=ramp(t, 1.4, 1.8))
        name, sub, col = info['head']
        headline(d, t, 0.9, name, sub, col)
        for i, (s, y, c) in enumerate(info.get('calls', [])):
            if s: callout(d, t, sc.s(i), s, y, c)
        if extra: extra(sc, t, im, d, cam)
    return fn

# ---------------------------------------------------------------- scenes
def sc_hook(sc, t, im, d):
    # The Sun as a dot beside the limb of VY Canis Majoris (to scale: radius ratio 1420)
    rs = 9.0 * (1 + 0.04 * t / sc.dur)
    sx, sy = W * 0.20, H * 0.56
    edge = W * 0.43 - 18 * t / sc.dur
    R = 1420 * rs; cx = edge + R; cy = H * 0.50
    i = IDX['VY']
    draw_star(im, d, star_sprite(i), STARS[i][2], cx, cy, R)
    draw_star(im, d, star_sprite(0), STARS[0][2], sx, sy, rs)
    d = ImageDraw.Draw(im, 'RGBA')
    # arrow to the Sun
    d.line((sx, sy - 30, sx, sy - 120), fill=(255, 214, 140, 255), width=6)
    d.polygon([(sx, sy - 18), (sx - 14, sy - 42), (sx + 14, sy - 42)], fill=(255, 214, 140, 255))
    text(d, (sx, sy - 175), 'THE SUN', 70, (255, 214, 140))
    text(d, (sx, sy + 70), 'IS THIS DOT', 50, WHITE, POP_B)
    text(d, (W * 0.71, 150), 'THIS STAR IS', 64, WHITE)
    text(d, (W * 0.71, 250), '1,420× WIDER', 104, GOLD)
    text(d, (W * 0.71, 345), 'VY CANIS MAJORIS', 46, WHITE, POP_B)
    a = pop(t, sc.s(1) + 1.2)
    pill(d, (W * 0.71, 470), 'JET AROUND IT: ~800 YEARS', 40, CYAN, alpha=a)
    a = pop(t, sc.s(2))
    text(d, (W * 0.71, 590), 'MIGHT NOT EVEN BE', 52, WHITE, alpha=a)
    text(d, (W * 0.71, 660), 'THE BIGGEST', 66, RED, alpha=a)
    note_a = 1.0
    text(d, (W - 40, H - 140), 'Sizes to scale', 24, GREY, POP_M, anchor='rm', stroke=2, alpha=note_a)

def sc_sun(sc, t, im, d):
    s, xw0 = cam_for(0)
    xw0 = XC[0] - 0.9 / s * 0
    cx, r = W * 0.64, FILL * H; cy = BASE - r
    zoom = ease(ramp(t, 0, 1.6))
    r_now = r * (0.25 + 0.75 * zoom)
    draw_star(im, d, star_sprite(0), STARS[0][2], cx, BASE - r_now, r_now)
    d = ImageDraw.Draw(im, 'RGBA')
    re_ = r_now / 109.2
    ex = cx - r_now - 70; ey = BASE - re_
    earth_dot(d, ex, ey, re_)
    text(d, (ex, ey - 46), 'EARTH', 30, CYAN, POP_B, stroke=3)
    text(d, (cx, BASE + 34), 'SUN', 38, STARS[0][2], POP_B, stroke=3)
    headline(d, t, 0.2, 'THE SUN', 'OUR STAR', STARS[0][2])
    a = pop(t, sc.s(1))
    if a > 0:
        # a row of Earths across the Sun's diameter (109, to scale)
        n = int(109 * ease(ramp(t, sc.s(1), sc.s(1) + 2.0)))
        for j in range(n):
            x = cx - r + re_ + j * 2 * re_
            d.ellipse((x - re_, cy - re_, x + re_, cy + re_), fill=(70, 140, 255, 230))
    callout(d, t, sc.s(1), '109 EARTHS WIDE', 290, CYAN)
    callout(d, t, sc.s(1) + 2.6, '~1.3 MILLION EARTHS FIT INSIDE', 365, WHITE, 46)
    callout(d, t, sc.s(2), 'LIGHT AROUND IT: ~15 s', 450, GOLD, 44)
    callout(d, t, sc.s(2) + 1.6, 'JET AROUND IT: ~7 MONTHS', 515, GOLD, 44)

def tag(d, t, a, s, col=GOLD, y=270, dur=None):
    al = pop(t, a, 0.3) * ((1 - pop(t, dur, 0.3)) if dur else 1)
    if al > 0: pill(d, (70 + F(POP_B, 40).getlength(s) / 2 + 24, y), s, 40, col, alpha=al)

def sc_sirius(sc, t, im, d):
    k = 1
    u = ease(ramp(t, 0.0, 1.6))
    cam = (FILL * H / 1.7, XC[0] * (1 - u) + XC[1] * u)
    cam = (cam[0], cam[1] - (XC[1] - XC[0]) * 0.5 * u)
    d = draw_ladder(im, d, cam, la=1)
    headline(d, t, 0.3, 'SIRIUS', 'BRIGHTEST STAR IN THE NIGHT SKY', STARS[1][2])
    callout(d, t, sc.s(0) + 2.2, '~8.6 LIGHT-YEARS AWAY', 290, WHITE, 46)
    callout(d, t, sc.s(1), '~1.7× WIDER THAN THE SUN', 365, GOLD, 50)

def ex_arcturus(sc, t, im, d, cam):
    callout(d, t, sc.s(1), '~25× WIDER THAN THE SUN', 290, GOLD, 50)
    callout(d, t, sc.s(2), '15,000+ SUNS FIT INSIDE', 365, WHITE, 46)
    callout(d, t, sc.s(3), 'OUR SUN: A RED GIANT IN ~5 BILLION YEARS', 440, CYAN, 36)

def ex_aldebaran(sc, t, im, d, cam):
    callout(d, t, sc.s(0) + 2.0, '~65 LIGHT-YEARS AWAY', 290, WHITE, 44)
    callout(d, t, sc.s(1), '~44× WIDER THAN THE SUN', 360, GOLD, 50)
    callout(d, t, sc.s(2) + 1.2, '~4,800 EARTHS ACROSS', 435, CYAN, 46)

def ex_rigel(sc, t, im, d, cam):
    callout(d, t, sc.s(0) + 2.4, '~860 LIGHT-YEARS AWAY', 290, WHITE, 44)
    callout(d, t, sc.s(1), '~75× WIDER THAN THE SUN', 360, GOLD, 50)
    callout(d, t, sc.s(2), 'LIGHT AROUND IT: ~18 MIN', 435, CYAN, 44)
    a = pop(t, sc.s(3) + 1.0)
    text(d, (W / 2, 560), '...BUT THE NEXT ONE BREAKS THE SCALE', 56, RED, alpha=a)

def sc_antares(sc, t, im, d):
    # slower, dramatic zoom out from Rigel: Antares slides in from the right
    u = ease(ramp(t, 0.2, 3.6))
    cam = lerp_cam(cam_for(4), cam_for(5), u)
    shake = 6 * math.sin(t * 60) * (ramp(t, 3.3, 3.5) - ramp(t, 3.7, 4.2))
    cam = (cam[0], cam[1] + shake / cam[0])
    d = draw_ladder(im, d, cam, upto=5, la=1)
    headline(d, t, 0.3, 'ANTARES', 'HEART OF THE SCORPION', STARS[5][2])
    callout(d, t, sc.s(1), '~700× WIDER THAN THE SUN', 290, GOLD, 56)
    a = pop(t, sc.s(2))
    if a > 0:
        s, xw0 = cam; sx = FOCUS_X + (XC[0] - xw0) * s
        d.ellipse((sx - 22, BASE - 34, sx + 22, BASE + 10), outline=(255, 214, 140, int(255 * a)), width=4)
        callout(d, t, sc.s(2), 'THE SUN: BARELY 1 PIXEL', 365, (255, 214, 140), 44)
    callout(d, t, sc.s(3), 'LIGHT AROUND IT: ~3 HOURS', 440, CYAN, 44)

def sc_betel(sc, t, im, d):
    u = ease(ramp(t, 0.0, 1.8))
    c0 = cam_for(5); c1 = cam_for(6); c1 = (c1[0] * 0.82, (XC[5] + XC[6]) / 2 + 120)
    cam = lerp_cam(c0, c1, u)
    d = draw_ladder(im, d, cam, upto=6, la=1)
    headline(d, t, 0.3, 'BETELGEUSE', "ORION'S SHOULDER · ~550 LIGHT-YEARS", STARS[6][2])
    callout(d, t, sc.s(1), '~750× WIDER THAN THE SUN', 290, GOLD, 52)
    a = pop(t, sc.s(2) + 1.0) * (1 - pop(t, sc.s(3), 0.3))
    if a > 0:
        d.rounded_rectangle((W / 2 - 560, 360, W / 2 + 560, 520), 30, fill=(10, 14, 28, int(215 * a)), outline=(90, 215, 255, int(255 * a)), width=4)
        text(d, (W / 2, 410), 'ON AVERAGE, ITS GAS IS', 46, WHITE, alpha=a)
        text(d, (W / 2, 475), 'THOUSANDS OF TIMES THINNER THAN AIR', 52, CYAN, alpha=a)
    a = pop(t, sc.s(3))
    if a > 0:
        d.rounded_rectangle((W / 2 - 420, 360, W / 2 + 420, 520), 30, fill=(10, 14, 28, int(215 * a)), outline=(255, 80, 70, int(255 * a)), width=4)
        text(d, (W / 2, 410), 'FUTURE SUPERNOVA', 64, RED, alpha=a)
        text(d, (W / 2, 480), 'probably not for ~100,000 years', 40, WHITE, POP_B, alpha=a)

ORB = [('EARTH', 1.0, (90, 160, 255)), ('MARS', 1.524, (230, 120, 80)), ('JUPITER', 5.203, (230, 200, 160)), ('SATURN', 9.537, (230, 210, 140))]
def solar_overlay(im, d, t, a, cx, cy):
    """VY CMa (6.6 AU radius) placed where the Sun is, orbits to scale."""
    pxau = 0.44 * H / 9.537
    i = IDX['VY']
    if a <= 0.01: return d
    ov = Image.new('RGBA', (W, H), (2, 3, 8, int(255 * a)))
    im.alpha_composite(ov)
    grow = ease(ramp(t, 0, 1.2))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay, 'RGBA')
    r = 6.60 * pxau * (0.02 + 0.98 * grow)
    draw_star(lay, dl, star_sprite(i), STARS[i][2], cx, cy, r)
    dl = ImageDraw.Draw(lay, 'RGBA')
    for name, au, col in ORB:
        R = au * pxau
        for k in range(0, 360, 4):
            dl.arc((cx - R, cy - R, cx + R, cy + R), k, k + 2.2, fill=col + (230,), width=3)
        ang = {'EARTH': 2.5, 'MARS': -0.6}.get(name, -0.6)
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        dl.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col + (255,))
    lay.putalpha(Image.fromarray((np.asarray(lay)[..., 3].astype(np.float32) * a).astype(np.uint8)))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im, 'RGBA')
    for name, au, col in ORB:
        R = au * pxau
        ang = {'EARTH': 2.5, 'MARS': -0.6}.get(name, -0.6)
        px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
        if name == 'EARTH': text(d, (px - 14, py + 22), name, 26, col, POP_B, anchor='rm', alpha=a, stroke=3)
        else: text(d, (px + 14, py - 22), name, 26, col, POP_B, anchor='lm', alpha=a, stroke=3)
    text(d, (W - 60, H - 150), 'Orbits and star to scale', 24, GREY, POP_M, anchor='rm', stroke=2, alpha=a)
    return d

def sc_vy(sc, t, im, d):
    u = ease(ramp(t, 0.1, 2.4))
    cam = lerp_cam((cam_for(6)[0] * 0.82, (XC[5] + XC[6]) / 2 + 120), cam_for(7), u)
    d = draw_ladder(im, d, cam, la=1)
    headline(d, t, 0.3, 'VY CANIS MAJORIS', '~3,900 LIGHT-YEARS AWAY', STARS[7][2])
    callout(d, t, sc.s(1), '~1,420× WIDER THAN THE SUN', 290, GOLD, 56)
    a = pop(t, sc.s(2) - 0.2, 0.5) * (1 - pop(t, sc.s(4) - 0.3, 0.5))
    if a > 0:
        d = solar_overlay(im, d, t - sc.s(2) + 0.2, a, W * 0.58, H * 0.47)
        text(d, (70, 140), 'IN THE SUN\'S PLACE', 60, WHITE, BLACK, anchor='lm', alpha=a)
        text(d, (70, 215), 'REACHES PAST JUPITER', 56, RED, BLACK, anchor='lm', alpha=a)
        callout(d, t, sc.s(3), '~3 BILLION SUNS FIT INSIDE', 300, GOLD, 46)
    a = pop(t, sc.s(4))
    if a > 0:
        callout(d, t, sc.s(4), 'LIGHT AROUND IT: ~6 HOURS', 365, CYAN, 44)
        callout(d, t, sc.s(4) + 2.6, 'JET AROUND IT: ~800 YEARS', 435, CYAN, 44)

GHOST = (XC[7] + 1420 + 0.12 * 2000 + 2000)
def sc_biggest(sc, t, im, d):
    u = ease(ramp(t, 0.0, 2.2))
    c1 = (0.40 * H / 2000, (XC[7] + GHOST) / 2 + 300)
    cam = lerp_cam(cam_for(7), c1, u)
    d = draw_ladder(im, d, cam, la=1)
    s, xw0 = cam
    a = pop(t, sc.s(2))
    if a > 0:
        cx = FOCUS_X + (GHOST - xw0) * s
        for R, col in ((2000, (255, 120, 90)), (1500, (255, 190, 120))):
            r = R * s; cy = BASE - 2000 * s
            for k in range(0, 360, 6):
                d.arc((cx - r, cy - r, cx + r, cy + r), k + t * 3, k + t * 3 + 3, fill=col + (int(230 * a),), width=4)
        text(d, (cx, BASE - 2000 * s - 10), '?', 160, WHITE, alpha=a)
        text(d, (cx, BASE + 34), '~1,500–2,000× ?', 34, (255, 190, 120), POP_B, alpha=a, stroke=3)
    headline(d, t, 0.3, 'THE BIGGEST?', 'NOBODY KNOWS FOR SURE', WHITE)
    callout(d, t, sc.s(1), 'NO HARD SURFACE · VERY FAR AWAY', 290, CYAN, 42)
    callout(d, t, sc.s(2) + 1.5, 'e.g. STEPHENSON 2-18', 355, WHITE, 42)
    callout(d, t, sc.s(3), 'RECORD SIZES: UNCERTAIN', 420, RED, 46)
    text(d, (W - 40, H - 140), 'Dashed rings: range of estimates', 24, GREY, POP_M, anchor='rm', stroke=2)

def sc_heavy(sc, t, im, d):
    # Aldebaran (44) vs R136a1 (~35-40, drawn at 37.5) vs the Sun, to scale
    s = 0.22 * H / 44.0
    xa, xr_, xs = W * 0.36, W * 0.74, W * 0.555
    a0 = pop(t, 0.0, 0.5)
    ia = IDX['Aldebaran']
    draw_star(im, d, star_sprite(ia), STARS[ia][2], xa, BASE - 44 * s, 44 * s)
    a = pop(t, sc.s(1))
    if a > 0:
        rr = 37.5 * s * (0.3 + 0.7 * a)
        draw_star(im, d, r136_sprite(), R136['col'], xr_, BASE - rr, rr)
    draw_star(im, d, star_sprite(0), STARS[0][2], xs, BASE - s, s)
    d = ImageDraw.Draw(im, 'RGBA')
    text(d, (xa, BASE + 34), 'ALDEBARAN ~44×', 34, STARS[ia][2], POP_B, stroke=3)
    text(d, (xs, BASE + 34), 'SUN', 30, STARS[0][2], POP_B, stroke=3)
    if a > 0: text(d, (xr_, BASE + 34), 'R136a1 ~35–40×', 34, R136['col'], POP_B, stroke=3, alpha=a)
    headline(d, t, 0.2, 'BIGGEST ≠ HEAVIEST', None, WHITE)
    callout(d, t, sc.s(1), 'MOST MASSIVE STAR KNOWN: R136a1', 185, R136['col'], 46)
    callout(d, t, sc.s(1) + 3.0, 'TARANTULA NEBULA · ~160,000 LIGHT-YEARS', 240, WHITE, 36)
    callout(d, t, sc.s(2), '~200 SUNS OF MASS, OR MORE', 295, GOLD, 46)
    callout(d, t, sc.s(3), 'BUT ONLY ~35–40× WIDER', 350, CYAN, 46)
    text(d, (W - 40, H - 140), 'Sizes to scale', 24, GREY, POP_M, anchor='rm', stroke=2)

def sc_outro(sc, t, im, d):
    c0 = (0.40 * H / 2000, (XC[7] + GHOST) / 2 + 300)
    c1 = (0.30 * H / 1420, XC[7] - 900)
    u = ease(ramp(t, 0.0, 2.0))
    cam = lerp_cam(c0, c1, u)
    d = draw_ladder(im, d, cam, la=1)
    s, xw0 = cam
    # list of rung names appearing as spoken
    names = ['SUN 1×', 'SIRIUS 1.7×', 'ARCTURUS ~25×', 'ALDEBARAN ~44×', 'RIGEL ~75×', 'ANTARES ~700×', 'BETELGEUSE ~750×', 'VY CMa ~1,420×']
    st, en = sc.s(0), sc.e(0)
    for j, nm in enumerate(names):
        a = pop(t, st + 0.6 + j * (en - st - 0.8) / 8)
        text(d, (70, 120 + j * 52), nm, 40, STARS[j][2], POP_B, anchor='lm', alpha=a, stroke=3)
    a = pop(t, sc.s(1))
    if a > 0:
        sx = FOCUS_X + (XC[0] - xw0) * s
        d.ellipse((sx - 26, BASE - 40, sx + 26, BASE + 12), outline=(255, 214, 140, int(255 * a)), width=5)
    a = pop(t, sc.s(2))
    pill(d, (W * 0.62, 150), 'WHICH STAR BLEW YOUR MIND? 👇', 44, GOLD, alpha=a) if False else pill(d, (W * 0.64, 150), 'WHICH STAR BLEW YOUR MIND? COMMENT!', 42, GOLD, alpha=a)
    a = pop(t, sc.s(3))
    pill(d, (W * 0.64, 240), 'SEND THIS TO SOMEONE WHO THINKS THE SUN IS BIG', 34, RED, WHITE, alpha=a)
    a = pop(t, sc.s(4))
    if a > 0:
        f = F(BLACK, 54); w = f.getlength('SUBSCRIBE') + 90
        d.rounded_rectangle((W * 0.64 - w / 2, 300, W * 0.64 + w / 2, 390), 45, fill=(220, 30, 40, int(255 * a)))
        text(d, (W * 0.64, 345), 'SUBSCRIBE', 54, WHITE, alpha=a, stroke=0)
        text(d, (W * 0.64, 430), 'Explorer Man', 40, GOLD, POP_B, alpha=a)

FUN = dict(hook=sc_hook, sun=sc_sun, sirius=sc_sirius,
           arcturus=ladder_scene(2, dict(head=('ARCTURUS', 'BRIGHTEST IN THE NORTHERN SKY', STARS[2][2])), ex_arcturus),
           aldebaran=ladder_scene(3, dict(head=('ALDEBARAN', 'EYE OF TAURUS THE BULL', STARS[3][2])), ex_aldebaran),
           rigel=ladder_scene(4, dict(head=('RIGEL', "BLUE SUPERGIANT · ORION'S FOOT", STARS[4][2])), ex_rigel),
           antares=sc_antares, betel=sc_betel, vy=sc_vy, biggest=sc_biggest, heavy=sc_heavy, outro=sc_outro)

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
    if sc.key != 'hook':
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

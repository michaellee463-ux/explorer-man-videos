from base import *

ORANGE = (255, 150, 60)
MPH = 1.609344

def label(d, x, y, s, size, col, a=1.0):
    text(d, (x, y), s, size, col, POP_B, stroke=max(3, size // 12), alpha=a)

# ---------------------------------------------------------------- speed streaks (mid-action motion)
SR_ = np.random.default_rng(11)
STREAKS = [(SR_.uniform(-200, W + 600), SR_.uniform(0, H), SR_.uniform(0.6, 1.4), SR_.uniform(0.3, 1.0)) for _ in range(90)]
def streaks(im, t, k, a=1.0):
    """k = intensity 0..1; lines fly from upper right to lower left"""
    if a <= 0.01 or k <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    sp_ = 900 + 2600 * k; L = 40 + 360 * k
    for x0, y0, s, b in STREAKS:
        p = (y0 + t * sp_ * s) % (H + 600) - 300
        x = x0 - (p - y0) * 0.35
        x = (x + 300) % (W + 600) - 300
        dx, dy = -0.35, 1.0; n = math.hypot(dx, dy)
        l = L * s
        d.line((x, p, x - dx / n * l, p - dy / n * l), fill=(170, 210, 255, int(115 * b * a * min(1, k * 1.5))), width=2 + int(2 * k))

# ---------------------------------------------------------------- rotating Earth
_rg = np.random.default_rng(3)
_g = _rg.random((18, 36)).astype(np.float32)
_g = np.array(Image.fromarray((_g * 255).astype(np.uint8)).resize((1440, 720), Image.BICUBIC), np.float32) / 255
_g2 = _rg.random((60, 120)).astype(np.float32)
_g2 = np.array(Image.fromarray((_g2 * 255).astype(np.uint8)).resize((1440, 720), Image.BICUBIC), np.float32) / 255
EMAP_N = 0.7 * _g + 0.3 * _g2
def earth_rot(R, lon):
    n = 2 * R + 6; y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
    u = (x - c) / R; v = (y - c) / R; rr = u * u + v * v; inside = rr <= 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    # tilt 0; lat = asin(v), lon = atan2(u, z)
    lat = np.arcsin(np.clip(v, -1, 1)); lo = np.arctan2(u, z) + lon
    ix = ((lo / (2 * np.pi)) % 1 * 1439).astype(int); iy = ((lat / np.pi + 0.5) * 719).astype(int)
    nn = EMAP_N[iy, ix]; nn2 = _g2[iy, ix]
    col = np.ones((n, n, 3), np.float32) * np.array([0.10, 0.30, 0.75])
    m = nn > 0.6; col[m] = np.array([0.25, 0.55, 0.25]) * (0.8 + 0.4 * nn[m, None])
    polar = np.abs(lat) > 1.25; col[polar] = 0.9
    cl = nn2 > 0.72; col[cl] = col[cl] * 0.5 + 0.5
    L = np.array([-0.5, -0.4, 0.77]); L /= np.linalg.norm(L)
    lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
    col = col * (0.08 + 0.92 * lam[..., None]) + np.array([0.4, 0.7, 1.0]) * (1 - z[..., None]) ** 3 * 0.5
    a = inside.astype(np.float32)
    arr = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')

# ---------------------------------------------------------------- gauge
def gauge(im, cx, cy, R, frac, txt, sub, a=1.0, txtcol=GOLD):
    if a <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA')
    d.ellipse((cx - R - 18, cy - R - 18, cx + R + 18, cy + R + 18), fill=(10, 14, 30, int(220 * a)), outline=(90, 110, 160, int(255 * a)), width=6)
    a0, a1 = 135, 405
    d.arc((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=(60, 70, 100, int(255 * a)), width=26)
    af = a0 + (a1 - a0) * min(max(frac, 0), 1)
    if af > a0 + 1:
        d.arc((cx - R, cy - R, cx + R, cy + R), a0, af, fill=(255, 120 + int(80 * (1 - frac)), 60, int(255 * a)), width=26)
    for i in range(11):
        an = math.radians(a0 + (a1 - a0) * i / 10)
        r1, r2 = R - 40, R - 70 if i % 5 == 0 else R - 55
        d.line((cx + r1 * math.cos(an), cy + r1 * math.sin(an), cx + r2 * math.cos(an), cy + r2 * math.sin(an)), fill=(200, 210, 230, int(220 * a)), width=5)
    an = math.radians(af)
    d.line((cx, cy, cx + (R - 60) * math.cos(an), cy + (R - 60) * math.sin(an)), fill=(255, 70, 60, int(255 * a)), width=12)
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(230, 230, 240, int(255 * a)))
    text(d, (cx, cy + R * 0.45), txt, int(R * 0.30), txtcol, BLACK, alpha=a)
    text(d, (cx, cy + R * 0.75), sub, int(R * 0.14), WHITE, POP_B, alpha=a)

# ---------------------------------------------------------------- galaxy sprite
def galaxy_sprite(R):
    def mk():
        n = 2 * R; img = np.zeros((n, n, 3), np.float32); c = n / 2
        rg = np.random.default_rng(5)
        N = 220000
        arm = rg.integers(0, 4, N); rr = rg.power(0.9, N) * 0.98
        th = arm * (np.pi / 2) + np.log(rr * 12 + 1) * 2.1 + rg.normal(0, 0.28, N) * (1.1 - rr * 0.5)
        x = c + rr * R * np.cos(th); y = c + rr * R * np.sin(th) * 0.9
        ok = (x >= 0) & (x < n) & (y >= 0) & (y < n)
        xi, yi = x[ok].astype(int), y[ok].astype(int)
        colr = np.where(rg.random(ok.sum())[:, None] < 0.5, np.array([0.55, 0.7, 1.0]), np.array([1.0, 0.9, 0.75]))
        np.add.at(img, (yi, xi), colr * 0.5)
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32); dd = np.sqrt((xx - c) ** 2 + ((yy - c) / 0.9) ** 2) / R
        img += np.exp(-(dd / 0.13) ** 2)[..., None] * np.array([1.0, 0.85, 0.6]) * 1.2
        img += np.exp(-(dd / 0.5) ** 2)[..., None] * np.array([0.25, 0.22, 0.35]) * 0.5
        pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
        a = np.clip(np.array(pil, np.float32).max(-1) / 255 * 1.6, 0, 1)
        arr = np.dstack([np.array(pil), (a * 255).astype(np.uint8)])
        return Image.fromarray(arr, 'RGBA')
    return sp(('gal', R), mk)

# ---------------------------------------------------------------- CMB sprite
def cmb_sprite(w, h):
    def mk():
        rg = np.random.default_rng(9)
        g = rg.random((24, 48)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        g2 = rg.random((60, 120)).astype(np.float32)
        g2 = np.array(Image.fromarray((g2 * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
        nn = 0.6 * g + 0.4 * g2
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        u = (xx - w / 2) / (w / 2); v = (yy - h / 2) / (h / 2)
        inside = u * u + v * v <= 1
        dip = 0.5 + 0.35 * u
        val = np.clip(0.55 * dip + 0.45 * nn, 0, 1)
        lo = np.array([0.05, 0.15, 0.6]); mid = np.array([0.9, 0.85, 0.5]); hi = np.array([0.85, 0.15, 0.05])
        col = np.where(val[..., None] < 0.5, lo + (mid - lo) * (val[..., None] / 0.5), mid + (hi - mid) * ((val[..., None] - 0.5) / 0.5))
        arr = np.concatenate([col, inside[..., None].astype(np.float32)], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('cmb', w, h), mk)

def arrow(d, x0, y0, x1, y1, col, wdt=14, a=1.0):
    d.line((x0, y0, x1, y1), fill=col + (int(255 * a),), width=wdt)
    an = math.atan2(y1 - y0, x1 - x0); s = wdt * 2.6
    p = [(x1 + s * math.cos(an), y1 + s * math.sin(an)), (x1 + s * math.cos(an + 2.4), y1 + s * math.sin(an + 2.4)), (x1 + s * math.cos(an - 2.4), y1 + s * math.sin(an - 2.4))]
    d.polygon(p, fill=col + (int(255 * a),))

def plane(d, cx, cy, s, col, a=1.0):
    c = col + (int(255 * a),)
    d.rounded_rectangle((cx - 1.0 * s, cy - 0.12 * s, cx + 1.0 * s, cy + 0.12 * s), int(0.12 * s), fill=c)
    d.polygon([(cx - 0.1 * s, cy), (cx + 0.25 * s, cy), (cx - 0.25 * s, cy + 0.7 * s), (cx - 0.45 * s, cy + 0.7 * s)], fill=c)
    d.polygon([(cx - 0.1 * s, cy), (cx + 0.25 * s, cy), (cx - 0.25 * s, cy - 0.7 * s), (cx - 0.45 * s, cy - 0.7 * s)], fill=c)
    d.polygon([(cx - 0.8 * s, cy), (cx - 0.65 * s, cy), (cx - 0.9 * s, cy - 0.35 * s), (cx - 1.0 * s, cy - 0.35 * s)], fill=c)

def fmt(n): return f'{n:,.0f}'

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy()
    # streak intensity by scene
    kmap = [('hook', 0.55), ('spin', 0.25), ('jet', 0.25), ('orbit', 0.45), ('moon', 0.45), ('tease', 0.8), ('galaxy', 0.65), ('lap', 0.3), ('why', 0.0), ('setup', 0.2), ('reveal', 1.0), ('share', 0.7), ('comment', 0.55)]
    kk = 0
    for key, v in kmap:
        if t >= st(key) - 0.2: kk = v
    streaks(im, t, kk)

    # ============ HOOK
    a = xf(t, -1, nx('hook') + 0.1, 0.01, 0.25)
    if a > 0:
        paste_c(im, glow(560, (90, 140, 255), 1.6), 540, 1980, 0.7 * a)
        paste_c(im, earth_rot(520, t * 0.6), 540, 2050, a)
        jitter = 0.04 * math.sin(t * 37) + 0.03 * math.sin(t * 23)
        frac = 0.82 + jitter
        gauge(im, 540, 1000, 320, frac, '???', 'km/h', a)
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 250), 'HOW FAST ARE YOU', 92, WHITE, alpha=a)
        text(d, (W / 2, 370), 'MOVING RIGHT NOW?', 92, GOLD, alpha=a)
        pa = ease(ramp(t, st('hook') + 2.2, st('hook') + 2.45)) * a
        pill(d, W / 2, 1460, 'WHILE SITTING STILL', 58, (210, 40, 50), alpha=pa)

    # ============ SPIN
    a = xf(t, st('spin') - 0.1, nx('spin') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('spin')
        paste_c(im, glow(520, (90, 140, 255), 1.6), 540, 1080, 0.6 * a)
        paste_c(im, earth_rot(400, t * 1.1), 540, 1080, a)
        d = ImageDraw.Draw(im, 'RGBA')
        ea = ease(ramp(t, s0 + 1.6, s0 + 2.1)) * a
        d.arc((140, 1050, 940, 1110), 0, 180, fill=(255, 205, 90, int(255 * ea)), width=8)
        arrow(d, 540, 1135, 760, 1124, GOLD, 12, ea)
        label(d, 540, 1200, 'EQUATOR', 44, GOLD, ea)
        ptext(d, (W / 2, 290), 'EARTH SPINS', 110, WHITE, t, s0, nx('spin') + 0.1)
        ptext(d, (W / 2, 1640), '1,670 km/h', 150, GOLD, t, s0 + 2.6, nx('spin') + 0.1)
        ptext(d, (W / 2, 1780), '≈ 1,040 mph', 76, WHITE, t, s0 + 2.8, nx('spin') + 0.1)

    # ============ JET
    a = xf(t, st('jet') - 0.1, nx('jet') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('jet'); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 330), 'ALMOST 2×', 160, GOLD, t, s0, nx('jet') + 0.1)
        ptext(d, (W / 2, 480), 'A JET AIRLINER', 100, WHITE, t, s0 + 0.15, nx('jet') + 0.1)
        full = 860; x0 = 110
        g1 = ease(ramp(t, s0 + 0.3, s0 + 1.1)); g2 = ease(ramp(t, s0 + 0.6, s0 + 1.6))
        plane(d, x0 + 90, 760, 80, (220, 230, 245), a)
        label(d, x0, 870, 'JET  ~900 km/h', 52, WHITE, a) if False else text(d, (x0, 880), 'JET AIRLINER  ~900 km/h', 54, WHITE, POP_B, anchor='lm', alpha=a)
        d.rounded_rectangle((x0, 930, x0 + max(20, full * 900 / 1670 * g1), 1010), 20, fill=(150, 170, 210, int(255 * a)))
        text(d, (x0, 1130), "EARTH'S SPIN  1,670 km/h", 54, GOLD, POP_B, anchor='lm', alpha=a)
        d.rounded_rectangle((x0, 1180, x0 + max(20, full * g2), 1260), 20, fill=(255, 190, 70, int(255 * a)))
        label(d, W / 2, 1320, 'bars to scale', 36, GREY, a * 0.8)
        fa = ease(ramp(t, s0 + 2.6, s0 + 2.9))
        ptext(d, (W / 2, 1560), 'YOU FEEL:', 90, WHITE, t, s0 + 2.6, nx('jet') + 0.1)
        ptext(d, (W / 2, 1700), 'NOTHING', 150, RED, t, s0 + 2.9, nx('jet') + 0.1)

    # ============ ORBIT
    a = xf(t, st('orbit') - 0.1, nx('orbit') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('orbit'); cx, cy, Ro = 540, 1050, 390
        paste_c(im, glow(330, (255, 190, 80), 1.4), cx, cy, a)
        paste_c(im, sp(('sun', 110), lambda: sphere(110, (1.0, 0.75, 0.25), 2, rough=0.15)), cx, cy, a)
        d = ImageDraw.Draw(im, 'RGBA')
        d.ellipse((cx - Ro, cy - Ro * 0.42, cx + Ro, cy + Ro * 0.42), outline=(120, 160, 230, int(160 * a)), width=3)
        th = -1.2 + (t - s0) * 1.4
        for k in range(28):
            tk = th - k * 0.03
            px, py = cx + Ro * math.cos(tk), cy + Ro * 0.42 * math.sin(tk)
            d.ellipse((px - 10, py - 10, px + 10, py + 10), fill=(120, 190, 255, int(200 * a * (1 - k / 28))))
        px, py = cx + Ro * math.cos(th), cy + Ro * 0.42 * math.sin(th)
        paste_c(im, earth(34), px, py, a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 290), 'AROUND THE SUN', 100, WHITE, t, s0, nx('orbit') + 0.1)
        ptext(d, (W / 2, 1520), '107,000 km/h', 140, GOLD, t, s0 + 2.0, nx('orbit') + 0.1)
        ptext(d, (W / 2, 1660), '≈ 67,000 mph', 76, WHITE, t, s0 + 2.2, nx('orbit') + 0.1)
        label(d, W / 2, 1850, 'not to scale', 36, GREY, a * 0.8)

    # ============ MOON
    a = xf(t, st('moon') - 0.1, nx('moon') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('moon'); d = ImageDraw.Draw(im, 'RGBA')
        paste_c(im, earth(90), 170, 1000, a); paste_c(im, moonsp(26), 930, 1000, a)
        d = ImageDraw.Draw(im, 'RGBA')
        g = ease(ramp(t, s0 + 0.3, s0 + 2.4))
        for x in range(270, 900, 34):
            d.line((x, 1000, x + 16, 1000), fill=(200, 210, 230, int(160 * a)), width=4)
        bx = 270 + (895 - 270) * g
        d.ellipse((bx - 16, 984, bx + 16, 1016), fill=(255, 205, 90, int(255 * a)))
        label(d, 170, 1130, 'EARTH', 46, WHITE, a); label(d, 930, 1080, 'MOON', 46, WHITE, a)
        ptext(d, (W / 2, 330), 'TO THE MOON IN', 100, WHITE, t, s0, nx('moon') + 0.1)
        ptext(d, (W / 2, 1450), 'UNDER 4 HOURS', 130, GOLD, t, s0 + 1.6, nx('moon') + 0.1)
        label(d, W / 2, 1580, '384,400 km at 107,000 km/h ≈ 3.6 h', 46, WHITE, ease(ramp(t, s0 + 1.9, s0 + 2.2)) * a)
        label(d, W / 2, 1850, 'not to scale', 36, GREY, a * 0.8)

    # ============ TEASE
    a = xf(t, st('tease') - 0.05, nx('tease') + 0.1, 0.1, 0.2)
    if a > 0:
        s0 = st('tease'); d = ImageDraw.Draw(im, 'RGBA')
        sh = 12 * math.sin(t * 60) * (1 - ramp(t, s0, s0 + 0.6))
        ptext(d, (W / 2 + sh, 820), "THAT'S NOT", 150, WHITE, t, s0, nx('tease') + 0.1)
        ptext(d, (W / 2 - sh, 1000), 'EVEN CLOSE', 160, RED, t, s0 + 0.5, nx('tease') + 0.1)

    # ============ GALAXY + LAP
    a = xf(t, st('galaxy') - 0.1, nx('lap') + 0.1, 0.25, 0.2)
    if a > 0:
        s0 = st('galaxy'); cx, cy = 540, 1050
        dim = 1 - 0.55 * ease(ramp(t, st('lap') + 0.2, st('lap') + 0.8))
        zoom = 1.0 + 0.08 * ramp(t, s0, nx('lap'))
        gs = galaxy_sprite(470)
        rot = gs.rotate(-(t - s0) * 6, resample=Image.BILINEAR)
        if zoom != 1: rot = rot.resize((int(rot.width * zoom), int(rot.height * zoom)), Image.BILINEAR)
        paste_c(im, rot, cx, cy, a * dim)
        ang = math.radians(-(t - s0) * 6) + 0.6; rs = 0.56 * 470 * zoom
        sx, sy = cx + rs * math.cos(ang), cy + rs * 0.9 * math.sin(ang)
        d = ImageDraw.Draw(im, 'RGBA')
        ya = ease(ramp(t, s0 + 0.8, s0 + 1.2)) * a * dim
        d.ellipse((sx - 26, sy - 26, sx + 26, sy + 26), outline=(255, 220, 90, int(255 * ya)), width=6)
        d.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(255, 240, 160, int(255 * ya)))
        label(d, sx, sy - 60, 'YOU ARE HERE', 44, GOLD, ya)
        ptext(d, (W / 2, 290), 'AROUND THE', 96, WHITE, t, s0, st('lap'))
        ptext(d, (W / 2, 410), 'MILKY WAY', 120, CYAN, t, s0 + 0.15, st('lap'))
        ptext(d, (W / 2, 1620), '828,000 km/h', 140, GOLD, t, s0 + 3.6, st('lap'))
        ptext(d, (W / 2, 1760), '≈ 514,000 mph', 76, WHITE, t, s0 + 3.8, st('lap'))
        # LAP timeline
        l0 = st('lap')
        ptext(d, (W / 2, 300), 'ONE LAP:', 110, WHITE, t, l0, nx('lap') + 0.1)
        ptext(d, (W / 2, 430), '200+ MILLION YEARS', 92, GOLD, t, l0 + 0.4, nx('lap') + 0.1)
        ba = ease(ramp(t, l0 + 2.6, l0 + 3.0)) * a
        if ba > 0:
            x0, full = 110, 860
            g1 = ease(ramp(t, l0 + 2.6, l0 + 3.3)); g2 = ease(ramp(t, l0 + 3.4, l0 + 4.2))
            text(d, (x0, 1350), 'ONE LAP  ~225 million years', 52, GOLD, POP_B, anchor='lm', alpha=ba)
            d.rounded_rectangle((x0, 1400, x0 + max(20, full * g1), 1480), 20, fill=(255, 190, 70, int(255 * ba)))
            text(d, (x0, 1580), 'ALL THE DINOSAURS  164 million', 52, (140, 230, 140), POP_B, anchor='lm', alpha=ba * ease(ramp(t, l0 + 3.4, l0 + 3.7)))
            d.rounded_rectangle((x0, 1630, x0 + max(20, full * 164 / 225 * g2), 1710), 20, fill=(90, 200, 110, int(255 * ba * ease(ramp(t, l0 + 3.4, l0 + 3.7)))))
            label(d, W / 2, 1780, '230 to 66 million years ago  ·  bars to scale', 36, GREY, ba * 0.85)

    # ============ WHY (steady speed: airliner window, still cup)
    a = xf(t, st('why') - 0.1, nx('why') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('why'); d = ImageDraw.Draw(im, 'RGBA')
        wx0, wy0, wx1, wy1 = 260, 640, 820, 1240
        d.rounded_rectangle((wx0 - 30, wy0 - 30, wx1 + 30, wy1 + 30), 200, fill=(200, 205, 215, int(255 * a)))
        win = Image.new('RGBA', (wx1 - wx0, wy1 - wy0), (0, 0, 0, 0)); wd = ImageDraw.Draw(win)
        for yy_ in range(0, wy1 - wy0, 6):
            k_ = yy_ / (wy1 - wy0); wd.line((0, yy_, wx1 - wx0, yy_), fill=(int(70 + 90 * k_), int(130 + 80 * k_), int(220 + 20 * k_), 255), width=6)
        rgc = np.random.default_rng(4)
        for i in range(9):
            y_ = rgc.uniform(80, 560); w_ = rgc.uniform(160, 320); sp_ = rgc.uniform(500, 800)
            x_ = (rgc.uniform(0, 900) - (t - s0) * sp_) % 1100 - 250
            wd.ellipse((x_, y_, x_ + w_, y_ + w_ * 0.35), fill=(255, 255, 255, 220))
        m = Image.new('L', win.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, win.width - 1, win.height - 1), 180, fill=int(255 * a))
        win.putalpha(m); im.alpha_composite(win, (wx0, wy0))
        d = ImageDraw.Draw(im, 'RGBA')
        # cup on tray, perfectly still
        d.rectangle((180, 1380, 900, 1410), fill=(120, 110, 100, int(255 * a)))
        d.polygon([(470, 1250), (610, 1250), (595, 1380), (485, 1380)], fill=(245, 245, 245, int(255 * a)))
        d.arc((585, 1270, 650, 1340), 270, 90, fill=(245, 245, 245, int(255 * a)), width=12)
        d.ellipse((474, 1240, 606, 1262), fill=(110, 70, 40, int(255 * a)))
        ptext(d, (W / 2, 300), "WHY DON'T", 110, WHITE, t, s0, nx('why') + 0.1)
        ptext(d, (W / 2, 430), 'YOU FEEL IT?', 110, GOLD, t, s0 + 0.2, nx('why') + 0.1)
        ptext(d, (W / 2, 1560), 'STEADY SPEED', 120, CYAN, t, s0 + 2.2, nx('why') + 0.1)
        ptext(d, (W / 2, 1690), '= YOU FEEL NOTHING', 82, WHITE, t, s0 + 2.5, nx('why') + 0.1)

    # ============ SETUP (directions, then CMB)
    a = xf(t, st('setup') - 0.1, nx('setup') + 0.15, 0.2, 0.2)
    if a > 0:
        s0 = st('setup'); dur = AUD[KEYS.index('setup')]['dur']; sw = s0 + dur * 0.43
        a1 = a * (1 - ease(ramp(t, sw - 0.2, sw + 0.1)))
        d = ImageDraw.Draw(im, 'RGBA')
        if a1 > 0:
            cx, cy = 540, 1050
            arrow(d, cx, cy, cx + 260, cy - 120, (90, 200, 255), 16, a1 * ease(ramp(t, s0 + 0.2, s0 + 0.5)))
            label(d, cx + 300, cy - 190, 'SPIN', 50, (90, 200, 255), a1 * ease(ramp(t, s0 + 0.2, s0 + 0.5)))
            arrow(d, cx, cy, cx - 280, cy - 260, (255, 205, 90), 16, a1 * ease(ramp(t, s0 + 0.5, s0 + 0.8)))
            label(d, cx - 290, cy - 340, 'ORBIT', 50, GOLD, a1 * ease(ramp(t, s0 + 0.5, s0 + 0.8)))
            arrow(d, cx, cy, cx - 60, cy + 360, (140, 230, 140), 16, a1 * ease(ramp(t, s0 + 0.8, s0 + 1.1)))
            label(d, cx - 70, cy + 440, 'GALAXY', 50, (140, 230, 140), a1 * ease(ramp(t, s0 + 0.8, s0 + 1.1)))
            d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(255, 255, 255, int(255 * a1)))
            ptext(d, (W / 2, 300), "THEY DON'T", 110, WHITE, t, s0, sw)
            ptext(d, (W / 2, 430), 'JUST ADD UP', 110, RED, t, s0 + 0.3, sw)
        a2 = a * ease(ramp(t, sw - 0.1, sw + 0.3))
        if a2 > 0:
            paste_c(im, cmb_sprite(940, 470), 540, 1050, a2)
            d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 330), "THE BIG BANG'S", 100, WHITE, t, sw, nx('setup') + 0.2)
            ptext(d, (W / 2, 460), 'AFTERGLOW', 130, ORANGE, t, sw + 0.2, nx('setup') + 0.2)
            label(d, W / 2, 1400, 'the light that fills the whole universe', 50, WHITE, a2 * ease(ramp(t, sw + 1.4, sw + 1.8)))
            label(d, W / 2, 1470, '(cosmic microwave background)', 40, GREY, a2 * ease(ramp(t, sw + 1.4, sw + 1.8)))

    # ============ REVEAL
    a = xf(t, st('reveal') - 0.1, nx('reveal') + 0.1, 0.15, 0.2)
    if a > 0:
        s0 = st('reveal'); hit = s0 + 1.55
        g = ease(ramp(t, s0, hit))
        paste_c(im, glow(700, (255, 170, 60), 1.5), 540, 980, a * 0.6 * ease(ramp(t, hit - 0.2, hit + 0.3)))
        val = 1_331_352 * g
        frac = 0.05 + 0.93 * g + (0.015 * math.sin(t * 40) if t > hit else 0)
        gauge(im, 540, 980, 360, frac, f'{val/1e6:.1f}M' if t < hit else '1.3M', 'km/h', a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 260), "YOU'RE MOVING", 104, WHITE, t, s0, nx('reveal') + 0.1)
        ptext(d, (W / 2, 1530), '1.3 MILLION km/h', 116, GOLD, t, hit, nx('reveal') + 0.1)
        ptext(d, (W / 2, 1670), '≈ 830,000 mph', 80, WHITE, t, hit + 0.25, nx('reveal') + 0.1)
        ptext(d, (W / 2, 1780), '(about 370 km every second)', 54, CYAN, t, hit + 0.5, nx('reveal') + 0.1)
        fl = (1 - ramp(t, hit, hit + 0.35)) * (t >= hit)
        if fl > 0: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(170 * fl))))

    # ============ SHARE: live distance counter
    a = xf(t, st('share') - 0.1, nx('share') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('share')
        paste_c(im, glow(480, (90, 140, 255), 1.6), 540, 1050, 0.5 * a)
        paste_c(im, earth_rot(250, t * 0.8), 540, 1050, a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 260), 'SINCE THIS VIDEO', 96, WHITE, t, s0, nx('share') + 0.1)
        ptext(d, (W / 2, 380), "STARTED YOU'VE GONE", 84, WHITE, t, s0 + 0.1, nx('share') + 0.1)
        ptext(d, (W / 2, 560), f'{fmt(369.82 * t)} km', 140, GOLD, t, s0 + 0.2, nx('share') + 0.1)
        label(d, W / 2, 680, 'live count · 370 km per second', 40, GREY, a * 0.85)
        sa = ease(ramp(t, s0 + 3.3, s0 + 3.6)) * a
        if sa > 0:
            d.rounded_rectangle((70, 1400, 1010, 1760), 40, fill=(200, 30, 45, int(235 * sa)))
            text(d, (W / 2, 1480), 'SEND THIS TO SOMEONE', 70, WHITE, alpha=sa)
            text(d, (W / 2, 1580), "WHO THINKS THEY'RE", 70, WHITE, alpha=sa)
            text(d, (W / 2, 1680), 'SITTING STILL', 84, GOLD, alpha=sa)

    # ============ COMMENT (loops back to the opening gauge)
    a = xf(t, st('comment') - 0.1, TOTAL + 1, 0.2, 0.01)
    if a > 0:
        s0 = st('comment')
        paste_c(im, glow(560, (90, 140, 255), 1.6), 540, 1980, 0.7 * a)
        paste_c(im, earth_rot(520, t * 0.6), 540, 2050, a)
        gauge(im, 540, 1000, 320, 0.82 + 0.04 * math.sin(t * 37), '???', 'km/h', a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 250), 'WHAT WAS', 110, WHITE, t, s0, TOTAL + 1)
        ptext(d, (W / 2, 380), 'YOUR GUESS?', 110, GOLD, t, s0 + 0.15, TOTAL + 1)
        pa = ease(ramp(t, s0 + 1.5, s0 + 1.8)) * a
        pill(d, 300, 1460, 'TOO LOW', 60, (30, 120, 200), alpha=pa)
        pill(d, 770, 1460, 'WAY TOO LOW', 60, (200, 50, 50), alpha=pa)
        text(d, (W / 2, 1610), 'COMMENT ↓', 80, GOLD, alpha=pa)
    return im.convert('RGB')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{float(tt):05.2f}.jpg', quality=88)
    elif mode == 'times':
        for k in KEYS: print(k, round(st(k), 2), round(nx(k), 2))
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

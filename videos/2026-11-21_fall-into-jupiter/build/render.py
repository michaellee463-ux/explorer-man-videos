from base import *

ORANGE = (255, 150, 60); SILVER = (190, 215, 255); HOT = (255, 240, 200)
def label(d, x, y, s, size, col, a=1.0):
    text(d, (x, y), s, size, col, POP_B, stroke=max(3, size // 12), alpha=a)


def dim(im, k):
    if k <= 0: return
    im.alpha_composite(Image.new('RGBA', im.size, (0, 0, 0, int(255 * min(1, k)))))
_TG = {}
def topgrad(im, h=620, a=200):
    if (h, a) not in _TG:
        g = np.zeros((h, W, 4), np.uint8); g[..., 3] = np.linspace(a, 0, h)[:, None].astype(np.uint8); _TG[(h, a)] = Image.fromarray(g, 'RGBA')
    im.alpha_composite(_TG[(h, a)], (0, 0))

def noise(shape, cells, seed):
    g = np.random.default_rng(seed).random(cells).astype(np.float32)
    return np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC), np.float32) / 255

# ---------------------------------------------------------------- Jupiter texture (equirectangular)
TW, TH = 2048, 1024
def jup_tex():
    y, x = np.mgrid[0:TH, 0:TW].astype(np.float32)
    lat = (y / TH - 0.5) * np.pi
    n1 = noise((TH, TW), (16, 64), 1); n2 = noise((TH, TW), (60, 240), 2); n3 = noise((TH, TW), (160, 640), 3)
    warp = (n1 - 0.5) * 0.10 + (n2 - 0.5) * 0.035
    l = lat + warp
    # belts (dark) and zones (light)
    band = 0.5 + 0.5 * np.sin(l * 11.0 + 0.8) * np.cos(l * 3.1)
    zone = np.array([0.93, 0.86, 0.74]); belt = np.array([0.66, 0.43, 0.28]); cream = np.array([0.98, 0.95, 0.88])
    col = zone * (1 - band[..., None]) + belt * band[..., None]
    col = col * (0.88 + 0.22 * n3[..., None])
    eq = np.exp(-(lat / 0.12) ** 2)[..., None]; col = col * (1 - 0.5 * eq) + cream * 0.5 * eq
    pole = np.clip((np.abs(lat) - 1.05) / 0.4, 0, 1)[..., None]; col = col * (1 - 0.55 * pole) + np.array([0.55, 0.5, 0.48]) * 0.55 * pole
    # Great Red Spot
    gx, gy = TW * 0.62, TH * (0.5 + 22 / 180)
    d = ((x - gx) / 95) ** 2 + ((y - gy) / 48) ** 2
    spot = np.clip(1.15 - d, 0, 1)[..., None] ** 0.8
    swirl = 0.85 + 0.15 * np.sin(np.sqrt(d) * 14 + np.arctan2(y - gy, x - gx) * 2)[..., None]
    col = col * (1 - spot) + np.array([0.80, 0.36, 0.22]) * swirl * spot
    ring = np.exp(-((np.sqrt(d) - 1.12) / 0.12) ** 2)[..., None]; col = col * (1 - 0.35 * ring) + 0.35 * ring * cream
    return np.clip(col, 0, 1).astype(np.float32)
TEX = jup_tex()

def jupiter(R, lon=0.0):
    def mk():
        RR = int(R); n = 2 * RR + 4; y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        u = (x - c) / RR; v = (y - c) / RR; rr = u * u + v * v; inside = rr <= 1
        z = np.sqrt(np.clip(1 - rr, 0, 1))
        lat = np.arcsin(np.clip(v, -1, 1)); lo = np.arctan2(u, z) + lon
        ix = ((lo / (2 * np.pi)) % 1 * (TW - 1)).astype(int); iy = ((lat / np.pi + 0.5) * (TH - 1)).astype(int)
        col = TEX[iy, ix]
        L = np.array([-0.45, -0.35, 0.82]); L /= np.linalg.norm(L)
        lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
        col = col * (0.05 + 0.95 * lam[..., None] ** 0.9) + np.array([0.9, 0.8, 0.6]) * (1 - z[..., None]) ** 4 * 0.12
        edge = np.clip((1 - np.sqrt(rr)) * RR / 1.5, 0, 1)
        arr = np.concatenate([np.clip(col, 0, 1), (edge * inside)[..., None]], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('jup', int(R), round(lon, 3)), mk)

JBIG = jupiter(1000, 0.3)
def jscaled(R):
    R = max(4, int(R))
    if R >= 1000: return JBIG.resize((2 * R + 4, 2 * R + 4), Image.BILINEAR)
    if R not in _JS:
        if len(_JS) > 6: _JS.pop(next(iter(_JS)))
        _JS[R] = JBIG.resize((2 * R + 4, 2 * R + 4), Image.LANCZOS)
    return _JS[R]
_JS = {}

def earth_s(R): return sp(('es', int(R) if R > 60 else int(R)), lambda: sphere(int(R), (0.10, 0.30, 0.75), 3, land=(0.25, 0.55, 0.25), atmo=(0.4, 0.7, 1.0)))

# ---------------------------------------------------------------- astronaut (simple silhouette, spread-eagle fall)
def astro(s):
    def mk():
        n = int(s * 3); im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        c = n / 2; w = s * 0.16
        body = (235, 238, 245, 255); dark = (60, 70, 90, 255)
        for (ax, ay) in ((-0.9, -0.55), (0.9, -0.55), (-0.55, 0.95), (0.55, 0.95)):
            d.line((c, c + (0.15 if ay > 0 else -0.15) * s, c + ax * s, c + ay * s), fill=body, width=int(w * 1.6))
            d.ellipse((c + ax * s - w, c + ay * s - w, c + ax * s + w, c + ay * s + w), fill=body)
        d.rounded_rectangle((c - s * 0.28, c - s * 0.45, c + s * 0.28, c + s * 0.4), int(s * 0.18), fill=body)
        d.rounded_rectangle((c - s * 0.2, c - s * 0.32, c + s * 0.2, c + s * 0.1), int(s * 0.08), fill=(200, 205, 215, 255))
        d.ellipse((c - s * 0.26, c - s * 0.92, c + s * 0.26, c - s * 0.4), fill=body)
        d.ellipse((c - s * 0.18, c - s * 0.8, c + s * 0.18, c - s * 0.52), fill=(255, 190, 80, 255))
        d.ellipse((c - s * 0.12, c - s * 0.76, c - s * 0.02, c - s * 0.66), fill=(255, 245, 220, 255))
        return im
    return sp(('astro', int(s)), mk)

def probe(s):
    def mk():
        n = int(s * 3); im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = n / 2
        d.polygon([(c - s, c - s * 0.15), (c + s, c - s * 0.15), (c + s * 0.45, c + s * 0.55), (c - s * 0.45, c + s * 0.55)], fill=(120, 90, 70, 255))
        d.ellipse((c - s, c - s * 0.42, c + s, c + s * 0.12), fill=(170, 130, 95, 255))
        return im
    return sp(('probe', int(s)), mk)

def streaks(im, t, k, col=(255, 230, 200), up=True, a=1.0):
    if k <= 0 or a <= 0: return
    d = ImageDraw.Draw(im, 'RGBA'); rg = np.random.default_rng(5)
    for i in range(70):
        x = rg.uniform(0, W); ph = rg.uniform(0, 1); sp_ = rg.uniform(0.8, 1.8)
        y = ((ph + t * sp_ * 1.6) % 1) * (H + 600) - 300
        y = H - y if up else y
        l = 80 + 380 * k * sp_
        d.line((x, y, x, y + l), fill=col + (int(110 * k * a),), width=2 + int(3 * k))

# ---------------------------------------------------------------- cloud dive strip
def cloud_strip():
    h = 7000; y, x = np.mgrid[0:h, 0:W].astype(np.float32)
    n1 = noise((h, W), (70, 12), 21); n2 = noise((h, W), (260, 40), 22)
    depth = y / h
    top = np.array([0.95, 0.88, 0.75]); mid = np.array([0.80, 0.52, 0.30]); low = np.array([0.30, 0.14, 0.08])
    base = np.where(depth[..., None] < 0.5, top * (1 - depth[..., None] * 2) + mid * depth[..., None] * 2, mid * (2 - depth[..., None] * 2) + low * (depth[..., None] * 2 - 1))
    puff = np.clip((n1 * 0.7 + n2 * 0.3 - 0.35) * 2.2, 0, 1)
    layers = 0.5 + 0.5 * np.sin(y / 340 + n1 * 3)
    col = base * (0.55 + 0.45 * puff[..., None]) * (0.8 + 0.25 * layers[..., None])
    return Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8), 'RGB').convert('RGBA')
CLOUDS = cloud_strip()

def gauge(d, y, label_s, val_s, col, a=1.0):
    """pressure / temperature readout panel"""
    if a <= 0.01: return
    d.rounded_rectangle((90, y - 95, W - 90, y + 95), 40, fill=(6, 8, 18, int(190 * a)), outline=col + (int(255 * a),), width=5)
    text(d, (W / 2, y - 45), label_s, 46, GREY, POP_B, stroke=0, alpha=a)
    text(d, (W / 2, y + 28), val_s, 92, col, BLACK, alpha=a)

def fmtn(v): return f'{v:,.0f}'

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')

    # ============ HOOK / SIZE / SPEED / MPH: falling toward Jupiter from space
    a_sp = 1 - ease(ramp(t, st('probe') - 0.2, st('probe') + 0.25))
    if a_sp > 0:
        if t < st('size'):                       # hook: huge Jupiter below, you falling at it
            JR = 900 + 60 * t; jy = 1080 + JR - 70 * t
        elif t < st('speed'):                    # size: pull back to show whole planet + 11 Earths
            p = ease(ramp(t, st('size'), st('size') + 0.9)); JR = (1133 * (1 - p) + 470 * p); jy = (1941 * (1 - p) + 1180 * p)
        else:                                    # speed + mph: plunge toward it again
            p = ease(ramp(t, st('speed'), st('probe'))); JR = 470 + 1100 * p ** 1.6; jy = 1180 + (JR - 470) * 0.85
        if JR < 900: paste_c(im, glow(int(JR * 1.25) // 40 * 40, (255, 200, 140), 2.2), 540, jy, 0.35 * a_sp)
        paste_c(im, jscaled(JR), 540, jy, a_sp)
        d = ImageDraw.Draw(im, 'RGBA')
        # 11 Earths across the diameter, drawn to scale (Earth radius = Jupiter radius / 11.21)
        ea = xf(t, st('size') + 0.6, st('speed') + 0.3, 0.3, 0.3)
        if ea > 0:
            er = JR / 11.21
            for i in range(11):
                cx = 540 - JR + er + i * 2 * er * (2 * JR - 2 * er) / (2 * er * 10) if False else 540 - JR + er * (1 + 2 * i) * (11.21 / 11)
                k = ease(ramp(t, st('size') + 0.6 + i * 0.07, st('size') + 0.9 + i * 0.07))
                paste_c(im, earth_s(max(3, er)), cx, jy, ea * k)
            d.line((540 - JR, jy + JR + 40, 540 + JR, jy + JR + 40), fill=(255, 255, 255, int(200 * ea)), width=5)
        topgrad(im, 760, 215); d = ImageDraw.Draw(im, 'RGBA')
        # you, falling
        aa = xf(t, -1, st('probe'), 0.01, 0.3) * (1 - xf(t, st('size') + 0.2, st('speed'), 0.3, 0.3))
        if aa > 0:
            s = 105 + 15 * math.sin(t * 2)
            paste_c(im, astro(s), 540 + 40 * math.sin(t * 1.3), 900 + 20 * math.sin(t * 1.7), aa)
        sk = 0.55 if t < st('size') else ramp(t, st('speed'), st('mph')) * 0.9 + 0.1 * (t > st('speed'))
        if t < st('size') or t > st('speed'): streaks(im, t, sk, a=a_sp)
        d = ImageDraw.Draw(im, 'RGBA')
        # texts
        ptext(d, (W / 2, 210), 'WHAT IF YOU FELL', 98, WHITE, t, -1, st('size'))
        ptext(d, (W / 2, 350), 'INTO JUPITER?', 128, GOLD, t, -1, st('size'))
        pa = ease(ramp(t, 1.6, 1.85)) * xf(t, -1, st('size'), 0.01, 0.2)
        pill(d, W / 2, 520, 'THERE IS NO GROUND', 60, (205, 30, 40), alpha=pa)
        ptext(d, (W / 2, 230), '11 EARTHS WIDE', 120, WHITE, t, st('size') + 0.1, st('speed'))
        ptext(d, (W / 2, 380), 'HYDROGEN + HELIUM', 76, CYAN, t, st('size') + 1.8, st('speed'))
        if st('speed') <= t < st('probe'):
            v = 60 * ease(ramp(t, st('speed') + 0.3, st('speed') + 4.2))
            ptext(d, (W / 2, 190), 'YOUR SPEED', 70, GREY, t, st('speed'), st('probe'))
            if t < st('mph'):
                ptext(d, (W / 2, 330), f'{v:.0f} km/s', 170, GOLD, t, st('speed') + 0.2, st('mph'))
            else:
                ptext(d, (W / 2, 330), '130,000+ MPH', 140, GOLD, t, st('mph'), st('probe'))
                # Earth with an orbit dot: one lap in 11 minutes
                oa = xf(t, st('mph') + 2.3, st('probe'), 0.3, 0.2)
                if oa > 0:
                    paste_c(im, earth_s(110), 540, 700, oa); d = ImageDraw.Draw(im, 'RGBA')
                    ang = (t - st('mph') - 2.3) * 2.6
                    d.ellipse((540 - 160, 700 - 160, 540 + 160, 700 + 160), outline=(255, 205, 90, int(150 * oa)), width=4)
                    x, y = 540 + 160 * math.cos(ang), 700 + 160 * math.sin(ang)
                    d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 230, 150, int(255 * oa)))
                    text(d, (W / 2, 925), 'AROUND EARTH IN 11 MIN', 74, WHITE, POP_B, alpha=oa)

    # ============ PROBE: fireball entry
    a = xf(t, st('probe') - 0.2, st('weight') + 0.2, 0.35, 0.35)
    if a > 0:
        ty = (t - st('probe')) * 900
        cs = CLOUDS.crop((0, int(ty) % 2000, W, int(ty) % 2000 + H)); im.alpha_composite(fade(cs, a))
        d = ImageDraw.Draw(im, 'RGBA')
        # orange plasma
        paste_c(im, glow(520, (255, 140, 40), 1.4), 540, 1150, 0.9 * a)
        paste_c(im, glow(300, (255, 245, 200), 1.6), 540, 1150, a)
        d = ImageDraw.Draw(im, 'RGBA')
        for i in range(14):
            ang = math.pi / 2 + (i - 6.5) * 0.09 + 0.03 * math.sin(t * 9 + i)
            l = 700 + 160 * math.sin(t * 11 + i * 1.7)
            d.line((540, 1150, 540 - math.cos(ang) * l, 1150 - math.sin(ang) * l), fill=(255, 190 - i * 5, 90, int(140 * a)), width=26)
        paste_c(im, probe(110), 540 + 8 * math.sin(t * 30), 1170, a)
        streaks(im, t, 1.0, (255, 220, 170), up=False, a=a)
        topgrad(im, 760, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'NASA GALILEO PROBE, 1995', 66, WHITE, t, st('probe') + 1.5, st('weight'))
        ptext(d, (W / 2, 340), '106,000 MPH', 160, GOLD, t, st('probe') + 3.0, st('weight'))
        ptext(d, (W / 2, 1660), 'MORE THAN 200 G', 112, RED, t, st('probe') + 5.8, st('weight'))
        if t < st('probe') + 1.5:
            ptext(d, (W / 2, 300), 'FIREBALL', 170, ORANGE, t, st('probe') - 0.1, st('probe') + 1.6)

    # ============ WEIGHT: falling through clouds, storm bigger than Earth
    a = xf(t, st('weight') - 0.1, st('tease') + 0.6, 0.35, 0.4)
    if a > 0:
        ty = 2200 + (t - st('weight')) * 360
        im.alpha_composite(fade(CLOUDS.crop((0, int(ty), W, int(ty) + H)), a)); d = ImageDraw.Draw(im, 'RGBA')
        # storm (oval vortex) rising past, with Earth to scale beside it (storm wider than Earth)
        sy = 1900 - (t - st('weight')) * 260
        ox, oy, rx, ry = 560, sy, 330, 175
        for k in range(10, 0, -1):
            f = k / 10
            d.ellipse((ox - rx * f, oy - ry * f, ox + rx * f, oy + ry * f), fill=(int(150 + 60 * (1 - f)), int(55 + 30 * (1 - f)), 40, int(200 * a)))
        for k in range(5):
            ang0 = t * 1.5 + k * 1.25
            pts = [(ox + rx * 0.85 * (j / 40) * math.cos(ang0 + j * 0.18), oy + ry * 0.85 * (j / 40) * math.sin(ang0 + j * 0.18)) for j in range(41)]
            d.line(pts, fill=(255, 210, 170, int(120 * a)), width=6)
        ea = ease(ramp(t, st('weight') + 2.3, st('weight') + 2.7)) * a
        er = 230  # Earth drawn smaller than the storm (storm ~1.3 Earths wide, i.e. "bigger than Earth")
        paste_c(im, earth_s(er), 270, oy - 380, ea)
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (270, oy - 380 + er + 50), 'EARTH', 56, WHITE, POP_B, alpha=ea)
        topgrad(im, 700, 210); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'YOU WEIGH', 90, WHITE, t, st('weight') + 0.9, st('tease'))
        ptext(d, (W / 2, 340), 'MORE THAN 2×', 128, GOLD, t, st('weight') + 1.1, st('tease'))
        ptext(d, (W / 2, 1700), 'STORMS BIGGER THAN EARTH', 72, WHITE, t, st('weight') + 2.6, st('tease') + 0.4)

    # ============ TEASE
    a = xf(t, st('tease') - 0.05, st('silent') + 0.2, 0.15, 0.3)
    if a > 0:
        dim(im, 0.6 * a); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 820), "BUT THE CLOUDS", 112, WHITE, t, st('tease'), st('silent') + 0.1)
        ptext(d, (W / 2, 980), "AREN'T THE", 112, WHITE, t, st('tease') + 0.2, st('silent') + 0.1)
        ptext(d, (W / 2, 1160), 'SCARY PART...', 128, RED, t, st('tease') + 0.45, st('silent') + 0.1)

    # ============ SILENT: Galileo on parachute, pressure gauge 1x -> 23x, signal lost
    a = xf(t, st('silent') - 0.05, st('metal') + 0.2, 0.3, 0.35)
    if a > 0:
        ty = 4300 + (t - st('silent')) * 160
        im.alpha_composite(fade(CLOUDS.crop((0, int(ty), W, int(ty) + H)), a)); dim(im, 0.25 * a); d = ImageDraw.Draw(im, 'RGBA')
        px, py = 540 + 30 * math.sin(t), 1000
        d.arc((px - 170, py - 470, px + 170, py - 170), 180, 360, fill=(255, 255, 255, int(230 * a)), width=14)
        d.chord((px - 170, py - 470, px + 170, py - 170), 180, 360, fill=(240, 240, 245, int(200 * a)))
        for dx in (-165, -60, 60, 165):
            d.line((px + dx, py - 320, px, py - 40), fill=(230, 230, 230, int(200 * a)), width=4)
        paste_c(im, probe(90), px, py, a); d = ImageDraw.Draw(im, 'RGBA')
        lost = ramp(t, st('silent') + 5.6, st('silent') + 5.8)
        # radio waves (stop when signal is lost)
        if lost < 1:
            for k in range(3):
                r = ((t * 1.2 + k / 3) % 1) * 260 + 60
                d.arc((px - r, py - 120 - r, px + r, py - 120 + r), 230, 310, fill=(120, 230, 255, int(220 * a * (1 - (r - 60) / 260))), width=8)
        tt = ramp(t, st('silent') + 0.2, st('silent') + 3.6)
        topgrad(im, 700, 215); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 190), 'DATA SENT FOR', 70, WHITE, t, st('silent') + 0.1, st('metal'))
        mins = int(round(58 * ease(tt)))
        ptext(d, (W / 2, 330), f'{mins} MINUTES', 150, CYAN, t, st('silent') + 0.2, st('metal'))
        pv = 1 + 22 * ease(ramp(t, st('silent') + 3.0, st('silent') + 5.4))
        gauge(d, 1450, "PRESSURE (× EARTH'S AIR)", f'{pv:.0f}×', ORANGE, a * ease(ramp(t, st('silent') + 2.8, st('silent') + 3.1)))
        if lost > 0:
            pill(d, W / 2, 1700, 'SIGNAL LOST', 76, (205, 30, 40), alpha=a * lost)

    # ============ METAL: liquid metallic hydrogen ocean
    a = xf(t, st('metal') - 0.1, st('core') + 0.2, 0.35, 0.35)
    if a > 0:
        dim(im, a * 0.95); d = ImageDraw.Draw(im, 'RGBA')
        k = ease(ramp(t, st('metal'), st('metal') + 3.0))
        sy = 1500 - 500 * k
        # metallic sheen: many shimmering horizontal strokes
        for j in range(60):
            yy = sy + j * j * 0.45
            if yy > H: break
            w = 0.5 + 0.5 * math.sin(t * 2.2 + j * 0.7)
            c = (int(120 + 110 * w), int(140 + 100 * w), int(170 + 85 * w))
            d.rectangle((0, yy, W, yy + 4 + j * 0.9), fill=c + (int(235 * a),))
            for q in range(4):
                xx = (q * 290 + t * 80 * (1 + j % 3) + j * 37) % (W + 200) - 100
                d.ellipse((xx - 60, yy - 3, xx + 60, yy + 6 + j * 0.5), fill=(255, 255, 255, int(120 * a * w)))
        paste_c(im, glow(700, (150, 190, 255), 1.6), 540, sy, 0.35 * a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 210), "PRESSURE", 80, WHITE, t, st('metal') + 0.2, st('core'))
        ptext(d, (W / 2, 350), 'MILLIONS ×', 160, ORANGE, t, st('metal') + 1.2, st('core'))
        ptext(d, (W / 2, 560), 'HYDROGEN TURNS TO', 70, WHITE, t, st('metal') + 2.9, st('core'))
        ptext(d, (W / 2, 670), 'LIQUID METAL', 128, SILVER, t, st('metal') + 3.4, st('core'))
        ptext(d, (W / 2, 1780), 'THOUSANDS OF KM DEEP', 74, WHITE, t, st('metal') + 5.6, st('core'))

    # ============ CORE: temperature bars, proportional (core ~20,000 C vs Sun surface 5,500 C)
    a = xf(t, st('core') - 0.1, st('reveal') + 0.2, 0.35, 0.35)
    if a > 0:
        dim(im, a * 0.95)
        paste_c(im, glow(560, (255, 230, 170), 1.4), 540, 1180, a * (0.6 + 0.1 * math.sin(t * 8)))
        paste_c(im, glow(250, (255, 255, 240), 1.2), 540, 1180, a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), "JUPITER'S CORE", 92, WHITE, t, st('core'), st('reveal'))
        g = ease(ramp(t, st('core') + 1.0, st('core') + 2.6))
        ptext(d, (W / 2, 340), f'~{fmtn(20000 * g)} °C', 140, HOT, t, st('core') + 1.0, st('reveal'))
        ba = a * ease(ramp(t, st('core') + 2.6, st('core') + 3.0))
        if ba > 0:
            base_y = 1800; full = 900 * ease(ramp(t, st('core') + 2.6, st('core') + 3.4))
            for x0, val, col, lab in ((250, 20000, (255, 240, 200), 'CORE'), (830, 5500, (255, 170, 60), "SUN'S SURFACE")):
                h = full * val / 20000
                d.rounded_rectangle((x0 - 85, base_y - h, x0 + 85, base_y), 30, fill=col + (int(240 * ba),))
                text(d, (x0, base_y - h - 60), f'{fmtn(val)} °C', 58, col, BLACK, alpha=ba)
                text(d, (x0, base_y + 60), lab, 52, WHITE, POP_B, alpha=ba)

    # ============ REVEAL: cutaway, you never hit the bottom
    a = xf(t, st('reveal') - 0.1, st('share') + 0.3, 0.35, 0.35)
    if a > 0:
        JR = 430; cx, cy = 540, 1150
        paste_c(im, jscaled(JR), cx, cy, a); d = ImageDraw.Draw(im, 'RGBA')
        # cut-away wedge (layers drawn schematically, not to an exact depth)
        for rf, col in ((1.0, (215, 160, 110)), (0.72, (150, 170, 210)), (0.12, (255, 245, 210))):
            r = JR * rf; d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, 0, fill=col + (int(255 * a),))
        text(d, (cx + 320, cy - 470), 'GAS', 44, WHITE, POP_B, alpha=a)
        text(d, (cx + 350, cy + 50), 'LIQUID METAL', 40, SILVER, POP_B, alpha=a)
        # your path: a dot sinking toward the core that fades out
        p = ramp(t, st('reveal') + 0.5, st('reveal') + 4.0)
        r = JR * (1.15 - 0.9 * p); ang = -math.pi / 4
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        da = a * (1 - ease(ramp(p, 0.55, 0.95)))
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(120, 230, 255, int(255 * da)))
        topgrad(im, 700, 215); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 210), 'YOU NEVER', 110, WHITE, t, st('reveal'), st('share'))
        ptext(d, (W / 2, 360), 'HIT THE BOTTOM', 120, GOLD, t, st('reveal') + 0.3, st('share'))
        for i, w in enumerate(('CRUSHED', 'MELTED', 'VAPORIZED')):
            ptext(d, (W / 2, 1680 + i * 0), w, 112, RED, t, st('reveal') + 2.6 + i * 0.55, st('reveal') + 3.15 + i * 0.55 if i < 2 else st('share'))

    # ============ SHARE + COMMENT (+ loop back to the opening)
    a = xf(t, st('share') - 0.1, TOTAL + 1, 0.3, 0.01)
    if a > 0:
        lp = ramp(t, TOTAL - 0.8, TOTAL)
        JR = 520 + (900 - 520) * ease(lp); jy = 1350 + (1080 + 900 - 1350) * ease(lp)
        paste_c(im, glow(int(JR * 1.25) // 40 * 40, (255, 200, 140), 2.2), 540, jy, 0.35 * a)
        paste_c(im, jscaled(JR), 540, jy, a)
        topgrad(im, 900, 220); d = ImageDraw.Draw(im, 'RGBA')
        ca = 1 - ease(lp)
        ptext(d, (W / 2, 200), 'SEND THIS TO SOMEONE', 78, WHITE, t, st('share'), st('comment'))
        ptext(d, (W / 2, 320), 'WHO THINKS YOU COULD', 78, WHITE, t, st('share') + 0.2, st('comment'))
        ptext(d, (W / 2, 460), 'LAND ON JUPITER', 118, GOLD, t, st('share') + 0.5, st('comment'))
        if t >= st('comment'):
            text(d, (W / 2, 250), 'WOULD YOU', 120, WHITE, BLACK, alpha=ca)
            text(d, (W / 2, 400), 'TAKE THE JUMP?', 120, GOLD, BLACK, alpha=ca)
            pa = ease(ramp(t, st('comment') + 0.7, st('comment') + 1.0)) * ca
            pill(d, 330, 640, 'YES', 80, (30, 150, 70), alpha=pa)
            pill(d, 750, 640, 'NO', 80, (205, 30, 40), alpha=pa)
            text(d, (W / 2, 800), 'COMMENT ↓', 80, GOLD, BLACK, alpha=pa)
        if lp > 0:
            paste_c(im, astro(105), 540, 900, ease(lp))
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

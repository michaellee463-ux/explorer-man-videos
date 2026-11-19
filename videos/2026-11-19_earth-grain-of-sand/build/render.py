from base import *

ORANGE = (255, 150, 60); SAND = (222, 184, 125); GREEN = (140, 230, 140)

def label(d, x, y, s, size, col, a=1.0):
    text(d, (x, y), s, size, col, POP_B, stroke=max(3, size // 12), alpha=a)

# ---------------------------------------------------------------- sprites
def sand_grain(R, seed=4):
    def mk():
        SS = 2; r = R * SS; n = int(2.6 * r)
        y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        ang = np.arctan2(y - c, x - c); rad = np.hypot(x - c, y - c) / r
        rg = np.random.default_rng(seed)
        edge = 1 + sum(rg.uniform(0.03, 0.09) * np.cos(k * ang + rg.uniform(0, 6.3)) for k in (2, 3, 5, 7))
        inside = rad <= edge
        u = (x - c) / (r * edge); v = (y - c) / (r * edge); z = np.sqrt(np.clip(1 - u * u - v * v, 0, 1))
        L = np.array([-0.55, -0.5, 0.67]); L /= np.linalg.norm(L)
        lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
        g = rg.random((40, 40)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        g2 = rg.random((n // 3, n // 3)).astype(np.float32)
        g2 = np.array(Image.fromarray((g2 * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR), np.float32) / 255
        col = np.array(SAND, np.float32) / 255 * (0.75 + 0.35 * g[..., None]) * (0.85 + 0.25 * g2[..., None])
        spec = np.clip(lam, 0, 1) ** 18 * 0.35
        col = col * (0.12 + 0.88 * lam[..., None]) + spec[..., None]
        arr = np.concatenate([np.clip(col, 0, 1), inside[..., None].astype(np.float32)], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)
    return sp(('sand', R, seed), mk)

_rg = np.random.default_rng(3)
_g = _rg.random((18, 36)).astype(np.float32)
def _wrap(g, cols):
    g = np.concatenate([g, g[:, :1]], 1)
    big = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((int(1440 * g.shape[1] / cols), 720), Image.BICUBIC), np.float32) / 255
    return big[:, :1440]
_g = _wrap(_g, 36)
_g2 = _wrap(_rg.random((60, 120)).astype(np.float32), 120)
EMAP_N = 0.7 * _g + 0.3 * _g2
def earth_rot(R, lon):
    R = max(2, int(R)); n = 2 * R + 6; y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
    u = (x - c) / R; v = (y - c) / R; rr = u * u + v * v; inside = rr <= 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
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
    arr = np.concatenate([np.clip(col, 0, 1), inside[..., None].astype(np.float32)], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')

def sun_sp(R):
    def mk():
        n = int(2 * R + 4); y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        rr = np.hypot(x - c, y - c) / R; inside = rr <= 1
        rg = np.random.default_rng(9)
        g = rg.random((60, 60)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        limb = np.sqrt(np.clip(1 - rr ** 2, 0, 1)) ** 0.5
        col = np.stack([np.ones_like(rr), 0.62 + 0.25 * limb, 0.18 + 0.3 * limb], -1) * (0.55 + 0.45 * limb[..., None]) * (0.9 + 0.15 * g[..., None])
        arr = np.concatenate([np.clip(col, 0, 1), inside[..., None].astype(np.float32)], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('sun', R), mk)

def jupiter_sp(R):
    def mk():
        n = int(2 * R + 4); y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        u = (x - c) / R; v = (y - c) / R; rr = u * u + v * v; inside = rr <= 1
        z = np.sqrt(np.clip(1 - rr, 0, 1))
        band = 0.5 + 0.5 * np.sin(v * 13 + 0.6 * np.sin(u * 4))
        col = np.array([0.85, 0.72, 0.55]) * (1 - band[..., None]) + np.array([0.62, 0.42, 0.28]) * band[..., None]
        L = np.array([-0.5, -0.4, 0.77]); L /= np.linalg.norm(L)
        lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
        col = col * (0.08 + 0.92 * lam[..., None])
        arr = np.concatenate([np.clip(col, 0, 1), inside[..., None].astype(np.float32)], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('jup', R), mk)

def neptune_sp(R): return sp(('nep', R), lambda: sphere(R, (0.25, 0.42, 0.95), 8, atmo=(0.5, 0.7, 1.0)))

def galaxy_sp(R):
    def mk():
        n = int(2 * R); y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        X = (x - c) / R; Y = (y - c) / R / 0.62
        r = np.hypot(X, Y) + 1e-6; th = np.arctan2(Y, X)
        arms = np.cos(2 * (th - 2.6 * np.log(r)))
        rg = np.random.default_rng(2)
        g = rg.random((90, 90)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        disk = np.exp(-r * 3.0) * (0.55 + 0.45 * np.clip(arms, 0, 1) ** 2) * (0.7 + 0.5 * g)
        bulge = np.exp(-(r / 0.13) ** 2)
        I = np.clip(disk * 2.2 + bulge, 0, 1) * (r < 1)
        col = np.stack([0.75 + 0.25 * bulge, 0.78 + 0.1 * bulge, 1.0 - 0.35 * bulge], -1)
        arr = np.concatenate([col * I[..., None] ** 0.6, (I ** 0.8)[..., None]], -1)
        stars = rg.random((n, n)) > 0.9965
        arr[stars & (r < 1), 3] = np.maximum(arr[stars & (r < 1), 3], 0.9); arr[stars & (r < 1), :3] = 1
        return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA')
    return sp(('gal', R), mk)

def atom_icon(d, cx, cy, s, t, a=1.0):
    if a <= 0.01: return
    al = int(255 * a)
    for k in range(3):
        ang = k * math.pi / 3 + t * 0.4
        pts = []
        for j in range(60):
            p = j / 59 * 2 * math.pi
            ex, ey = s * math.cos(p), s * 0.36 * math.sin(p)
            pts.append((cx + ex * math.cos(ang) - ey * math.sin(ang), cy + ex * math.sin(ang) + ey * math.cos(ang)))
        d.line(pts, fill=(120, 210, 255, al), width=max(2, int(s / 22)))
        p = t * 3 + k * 2
        ex, ey = s * math.cos(p), s * 0.36 * math.sin(p)
        ex2, ey2 = cx + ex * math.cos(ang) - ey * math.sin(ang), cy + ex * math.sin(ang) + ey * math.cos(ang)
        rr = s / 11; d.ellipse((ex2 - rr, ey2 - rr, ex2 + rr, ey2 + rr), fill=(200, 240, 255, al))
    rr = s / 6; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 120, 90, al))

SR_ = np.random.default_rng(11)
STREAKS = [(SR_.uniform(0, 2 * math.pi), SR_.uniform(0, 1), SR_.uniform(0.5, 1.4)) for _ in range(110)]
def radial_streaks(im, t, cx, cy, k, a=1.0):
    """streaks rushing outward (camera pulling back fast)"""
    if a <= 0.01 or k <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    for ang, ph, s in STREAKS:
        p = (ph + t * 0.9 * s) % 1
        r0 = 120 + p * 1300; l = 30 + 260 * p * k
        x0, y0 = cx + math.cos(ang) * r0, cy + math.sin(ang) * r0
        x1, y1 = cx + math.cos(ang) * (r0 + l), cy + math.sin(ang) * (r0 + l)
        d.line((x0, y0, x1, y1), fill=(170, 210, 255, int(120 * a * k * p)), width=2 + int(2 * p))

def dim(im, k):
    if k <= 0: return
    im.alpha_composite(Image.new('RGBA', im.size, (0, 0, 0, int(255 * k))))

TOPGR = None
def topgrad(im, h=620, a=200):
    global TOPGR
    if TOPGR is None:
        g = np.zeros((h, W, 4), np.uint8); g[..., 3] = np.linspace(a, 0, h)[:, None].astype(np.uint8); TOPGR = Image.fromarray(g, 'RGBA')
    im.alpha_composite(TOPGR, (0, 0))

def counter(d, cy, val, unit, col, a=1.0, size=200):
    text(d, (W / 2, cy), val, size, col, BLACK, alpha=a)
    text(d, (W / 2, cy + size * 0.78), unit, int(size * 0.36), WHITE, BLACK, alpha=a)

def fmt_m(m):
    if m < 1000: return f'{m:.0f} m'
    return (f'{m / 1000:.1f} km' if m < 1950 else f'{m / 1000:.0f} km') if m < 10000 else f'{m / 1000:,.0f} km'

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy()
    # ============ HOOK: Earth shrinking into a grain of sand (mid-action at frame 0)
    a = xf(t, -1, nx('hook') + 0.15, 0.01, 0.25)
    if a > 0:
        s0, s1 = 0.0, nx('hook')
        p = ease(ramp(t, 0, 2.6))
        R = 620 * (0.06 / 1.0) ** p * 1.0 + 0 if False else 620 * math.exp(math.log(46 / 620) * p)
        cx, cy = 540, 1060
        radial_streaks(im, t, cx, cy, 1 - p * 0.7, a)
        paste_c(im, glow(int(R * 1.5) + 4, (90, 140, 255), 1.8), cx, cy, 0.6 * a * (1 - ramp(t, 1.8, 2.6)))
        ge = ramp(t, 1.9, 2.7)
        paste_c(im, earth_rot(R, t * 0.5), cx, cy, a * (1 - ge))
        if ge > 0:
            paste_c(im, sand_grain(46), cx, cy, a * ge)
            d = ImageDraw.Draw(im, 'RGBA'); ba = a * ease(ramp(t, 2.5, 2.9))
            y = cy + 80; d.line((cx - 46, y, cx + 46, y), fill=(255, 255, 255, int(255 * ba)), width=5)
            for xx_ in (cx - 46, cx + 46): d.line((xx_, y - 14, xx_, y + 14), fill=(255, 255, 255, int(255 * ba)), width=5)
            label(d, cx, y + 50, '1 mm', 54, WHITE, ba)
        topgrad(im)
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 230), 'EARTH =', 120, WHITE)
        text(d, (W / 2, 370), '1 GRAIN OF SAND', 112, GOLD)
        # "you = an atom" panel (on screen from frame 0, grows when spoken)
        k = 0.85 + 0.15 * ease(ramp(t, 2.9, 3.3))
        atom_icon(d, 540, 1560, 120 * k, t, a)
        text(d, (W / 2, 1745), 'YOU = THE SIZE', int(84 * k), WHITE, alpha=a)
        text(d, (W / 2, 1840), 'OF AN ATOM', int(84 * k), CYAN, alpha=a)

    # ============ ISS: a hair's width above the grain
    a = xf(t, st('iss') - 0.1, nx('iss') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('iss'); cx, cy = 470, 1150; R = 520
        zoom = 1 + 0.05 * ramp(t, s0, nx('iss'))
        R = int(R * zoom)
        paste_c(im, glow(int(R * 1.25), (90, 140, 255), 2.2), cx, cy, 0.5 * a)
        paste_c(im, earth_rot(R, 0.8 + t * 0.15), cx, cy, a)
        d = ImageDraw.Draw(im, 'RGBA')
        gap = R * 2 * 0.0314  # 0.031 mm on a 1 mm grain
        ra = ease(ramp(t, s0 + 0.2, s0 + 0.8)) * a
        d.arc((cx - R - gap, cy - R - gap, cx + R + gap, cy + R + gap), 200, 340, fill=(90, 230, 255, int(255 * ra)), width=4)
        ang = math.radians(200 + 140 * ramp(t, s0 + 0.3, nx('iss')))
        ix, iy = cx + (R + gap) * math.cos(ang), cy + (R + gap) * math.sin(ang)
        d.rectangle((ix - 9, iy - 4, ix + 9, iy + 4), fill=(255, 255, 255, int(255 * ra)))
        # hair strand to the same scale (0.07 mm typical) at the right edge
        hw = R * 2 * 0.07; hx = 990
        ha = ease(ramp(t, s0 + 0.9, s0 + 1.3)) * a
        pts = [(hx + 10 * math.sin(yy_ / 140), yy_) for yy_ in range(520, 1900, 20)]
        d.line(pts, fill=(95, 70, 45, int(255 * ha)), width=int(hw))
        label(d, hx - 130, 1850, 'a human hair', 40, WHITE, ha)
        topgrad(im)
        ptext(d, (W / 2, 230), 'SPACE STATION', 106, WHITE, t, s0, nx('iss') + 0.3)
        ptext(d, (W / 2, 360), '0.03 mm UP', 120, CYAN, t, s0 + 0.15, nx('iss') + 0.3)
        label(d, W / 2, 470, '(drawn to scale)', 40, GREY, a)

    # ============ MOON + HUMANS: ruler, everything to scale
    a = xf(t, st('moon') - 0.1, nx('humans') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('moon'); sh = st('humans')
        x0, x1, y = 130, 1000, 1150; pxcm = (x1 - x0) / 3.5
        d = ImageDraw.Draw(im, 'RGBA'); al = int(255 * a)
        d.rounded_rectangle((x0 - 30, y + 40, x1 + 30, y + 190), 14, fill=(230, 210, 150, int(225 * a)))
        for i_ in range(36):
            xx_ = x0 + i_ * pxcm / 10; L_ = 60 if i_ % 10 == 0 else (40 if i_ % 5 == 0 else 24)
            d.line((xx_, y + 40, xx_, y + 40 + L_), fill=(40, 30, 20, al), width=3)
            if i_ % 10 == 0: text(d, (xx_, y + 140), f'{i_ // 10} cm', 38, (40, 30, 20), POP_B, stroke=0, alpha=a)
        ex = x0 + 0.05 * pxcm; er = 0.05 * pxcm
        paste_c(im, earth_rot(er, 0.5), ex, y - er - 2, a)
        mx = x0 + 3.013 * pxcm; mr = max(2, 0.0136 * pxcm)
        d = ImageDraw.Draw(im, 'RGBA')
        ma = ease(ramp(t, s0 + 0.2, s0 + 0.6)) * a
        paste_c(im, glow(40, (220, 220, 220), 2.0), mx, y - 6, 0.6 * ma)
        d.ellipse((mx - mr, y - 6 - mr, mx + mr, y - 6 + mr), fill=(225, 225, 220, int(255 * ma)))
        # magnified callouts
        for (px, py, lab, kind, aa) in ((ex + 120, 820, 'EARTH', 'e', a), (mx - 60, 820, 'MOON', 'm', ma)):
            if aa <= 0: continue
            d.line((px, py + 95, ex if kind == 'e' else mx, y - 20), fill=(255, 255, 255, int(150 * aa)), width=3)
            d.ellipse((px - 95, py - 95, px + 95, py + 95), outline=(255, 255, 255, int(200 * aa)), width=4, fill=(5, 8, 20, int(200 * aa)))
            if kind == 'e': paste_c(im, earth_rot(80, 0.5 + t * 0.3), px, py, aa)
            else: paste_c(im, moonsp(22), px, py, aa)
            d = ImageDraw.Draw(im, 'RGBA')
            label(d, px, py - 125, lab, 44, WHITE, aa)
        label(d, W / 2, 1420, 'sizes and distance to scale; circles magnified', 36, GREY, a)
        topgrad(im); d = ImageDraw.Draw(im, 'RGBA')
        if t < sh:
            ptext(d, (W / 2, 230), 'THE MOON', 120, WHITE, t, s0, sh + 0.1)
            ptext(d, (W / 2, 370), '3 cm AWAY', 130, GOLD, t, s0 + 0.15, sh + 0.1)
        else:
            ha = ease(ramp(t, sh + 0.2, sh + 1.4)) * a
            hx = x0 + 3.19 * pxcm
            d.line((ex, y - 30, ex + (hx - ex) * ha, y - 30), fill=(255, 205, 90, int(255 * a)), width=8)
            if ha > 0.98:
                d.polygon([(hx, y - 30), (hx - 26, y - 46), (hx - 26, y - 14)], fill=(255, 205, 90, al))
            la = ease(ramp(t, sh + 1.4, sh + 1.8)) * a
            label(d, W / 2, 1520, 'Farthest any human has gone:', 46, WHITE, la)
            label(d, W / 2, 1585, 'Artemis II, April 2026 (406,000+ km)', 46, GOLD, la)
            ca = ease(ramp(t, sh + 3.0, sh + 3.4)) * a
            text(d, (W / 2, 1760), '3.2 cm', 170, GOLD, alpha=ca)
            ptext(d, (W / 2, 230), 'EVERY ASTRONAUT', 98, WHITE, t, sh, nx('humans') + 0.3)
            ptext(d, (W / 2, 370), 'EVER: UNDER 3.2 cm', 100, GOLD, t, sh + 0.15, nx('humans') + 0.3)

    # ============ SUN / JUPITER / NEPTUNE / VOYAGER: distance counter, sizes to scale
    a = xf(t, st('sun') - 0.1, nx('voyager') + 0.1, 0.2, 0.2)
    if a > 0:
        ks = ['sun', 'jupiter', 'neptune', 'voyager']; dist = [11.73, 61.0, 352.4, 2031]
        ci = max(i for i, k_ in enumerate(ks) if st(k_) <= t + 0.05) if t >= st('sun') - 0.05 else 0
        # rolling counter from previous to current value
        prev = 0 if ci == 0 else dist[ci - 1]
        pr = ease(ramp(t, st(ks[ci]) + 0.1, st(ks[ci]) + 1.0))
        val = math.exp(math.log(max(prev, 0.5)) + (math.log(dist[ci]) - math.log(max(prev, 0.5))) * pr)
        PX = 5.0  # px per model mm (Sun 109 mm -> 545 px): sizes to scale
        d = ImageDraw.Draw(im, 'RGBA')
        k = ks[ci]; s0 = st(k)
        sa = ease(ramp(t, s0, s0 + 0.35)) * a
        if k == 'sun':
            paste_c(im, glow(560, (255, 170, 60), 1.6), 540, 1030, 0.7 * sa)
            paste_c(im, sun_sp(int(109.1 * PX / 2)), 540, 1030, sa)
            paste_c(im, earth_rot(3, 0), 540 + 380, 1030, sa)
            d = ImageDraw.Draw(im, 'RGBA')
            d.line((540 + 380, 1010, 540 + 380, 930), fill=(255, 255, 255, int(220 * sa)), width=3)
            label(d, 540 + 380, 900, 'Earth', 40, WHITE, sa)
            ptext(d, (W / 2, 230), 'THE SUN =', 112, WHITE, t, s0, nx(k) + 0.1)
            ptext(d, (W / 2, 360), 'A GRAPEFRUIT', 122, ORANGE, t, s0 + 0.15, nx(k) + 0.1)
        elif k == 'jupiter':
            paste_c(im, jupiter_sp(int(11.21 * PX * 4 / 2)), 540, 1030, sa)
            paste_c(im, earth_rot(int(1 * PX * 4 / 2), 0.4), 820, 1030, sa)
            d = ImageDraw.Draw(im, 'RGBA')
            label(d, 820, 960, 'Earth', 40, WHITE, sa)
            label(d, 540, 1220, 'magnified 4x vs. the Sun scene', 34, GREY, sa)
            ptext(d, (W / 2, 230), 'JUPITER', 120, WHITE, t, s0, nx(k) + 0.1)
            ptext(d, (W / 2, 360), '1 cm WIDE', 128, GOLD, t, s0 + 0.15, nx(k) + 0.1)
        elif k == 'neptune':
            paste_c(im, neptune_sp(int(3.88 * PX * 8 / 2)), 540, 1030, sa)
            paste_c(im, earth_rot(int(1 * PX * 8 / 2), 0.9), 760, 1030, sa)
            d = ImageDraw.Draw(im, 'RGBA')
            label(d, 760, 960, 'Earth', 40, WHITE, sa)
            label(d, 540, 1220, 'magnified 8x vs. the Sun scene', 34, GREY, sa)
            ptext(d, (W / 2, 230), 'NEPTUNE', 120, WHITE, t, s0, nx(k) + 0.1)
            ptext(d, (W / 2, 360), 'THE LAST PLANET', 104, CYAN, t, s0 + 0.15, nx(k) + 0.1)
        else:
            # Voyager probe icon flying with a trail
            vx = 540 + 40 * math.sin(t); vy = 1030
            for j in range(30):
                d.ellipse((vx - 200 - j * 18 - 3, vy + j * 6 - 3, vx - 200 - j * 18 + 3, vy + j * 6 + 3), fill=(180, 210, 255, int(150 * sa * (1 - j / 30))))
            d.ellipse((vx - 70, vy - 70, vx + 70, vy + 70), outline=(230, 230, 240, int(255 * sa)), width=10)
            d.line((vx, vy, vx, vy + 160), fill=(200, 200, 210, int(255 * sa)), width=8)
            d.rectangle((vx - 40, vy + 150, vx + 40, vy + 200), fill=(210, 190, 120, int(255 * sa)))
            d.line((vx + 40, vy + 175, vx + 230, vy + 175), fill=(200, 200, 210, int(255 * sa)), width=5)
            ptext(d, (W / 2, 230), 'VOYAGER 1', 120, WHITE, t, s0, nx(k) + 0.1)
            ptext(d, (W / 2, 360), 'AFTER 49 YEARS', 110, GOLD, t, s0 + 0.15, nx(k) + 0.1)
        text(d, (W / 2, 1450), 'DISTANCE FROM THE SUN', 52, GREY, POP_B, stroke=3, alpha=a)
        counter(d, 1600, fmt_m(val) if not (ci == 0 and pr > 0.95) else '12 m', '', GOLD, a, 210)

    # ============ TEASE
    a = xf(t, st('tease') - 0.05, nx('tease') + 0.05, 0.08, 0.15)
    if a > 0:
        s0 = st('tease'); d = ImageDraw.Draw(im, 'RGBA')
        sc = 1 + 0.08 * ramp(t, s0, nx('tease'))
        text(d, (W / 2, 840), "BUT THAT'S", int(140 * sc), WHITE, alpha=a)
        text(d, (W / 2, 1000), 'NOT THE', int(140 * sc), WHITE, alpha=a)
        text(d, (W / 2, 1170), 'CRAZY PART', int(150 * sc), RED, alpha=a)

    # ============ NEAREST STAR + VOYAGER TIME
    a = xf(t, st('star') - 0.1, nx('voy2') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('star'); s2 = st('voy2'); d = ImageDraw.Draw(im, 'RGBA')
        ax, ay, bx, by = 170, 1150, 910, 1080
        la = ease(ramp(t, s0 + 0.3, s0 + 1.6))
        n = 40
        for j in range(n):
            if j / n > la: break
            if j % 2: continue
            p0, p1 = j / n, (j + 1) / n
            d.line((ax + (bx - ax) * p0, ay + (by - ay) * p0 - 120 * math.sin(math.pi * p0), ax + (bx - ax) * p1, ay + (by - ay) * p1 - 120 * math.sin(math.pi * p1)), fill=(255, 205, 90, int(255 * a)), width=7)
        paste_c(im, sand_grain(14), ax, ay, a)
        paste_c(im, glow(70, (255, 120, 90), 1.5), bx, by, a * ease(ramp(t, s0 + 1.4, s0 + 1.8)))
        d = ImageDraw.Draw(im, 'RGBA')
        label(d, ax + 10, ay + 70, 'NEW YORK', 46, WHITE, a)
        label(d, ax + 10, ay + 120, '(our grain)', 36, GREY, a)
        label(d, bx - 30, by + 70, 'SALT LAKE CITY', 46, WHITE, a * ease(ramp(t, s0 + 1.4, s0 + 1.8)))
        label(d, bx - 30, by + 120, '(nearest star)', 36, GREY, a * ease(ramp(t, s0 + 1.4, s0 + 1.8)))
        if t < s2:
            ptext(d, (W / 2, 230), 'NEAREST STAR', 116, WHITE, t, s0, s2 + 0.1)
            ptext(d, (W / 2, 370), '3,150 km AWAY', 120, GOLD, t, s0 + 0.15, s2 + 0.1)
        else:
            ptext(d, (W / 2, 230), "AT VOYAGER'S SPEED", 92, WHITE, t, s2, nx('voy2') + 0.3)
            yrs = int(75000 * ease(ramp(t, s2 + 0.1, s2 + 2.0)))
            text(d, (W / 2, 1530), f'{yrs:,}', 200, GOLD, alpha=a)
            text(d, (W / 2, 1690), 'YEARS', 90, WHITE, alpha=a)
        label(d, W / 2, 1830, 'model scale: Earth = 1 mm', 36, GREY, a)

    # ============ SHARE
    a = xf(t, st('share') - 0.1, nx('share') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('share'); d = ImageDraw.Draw(im, 'RGBA')
        ax, ay, bx, by = 170, 1150, 910, 1080
        for j in range(0, 40, 2):
            p0, p1 = j / 40, (j + 1) / 40
            d.line((ax + (bx - ax) * p0, ay + (by - ay) * p0 - 120 * math.sin(math.pi * p0), ax + (bx - ax) * p1, ay + (by - ay) * p1 - 120 * math.sin(math.pi * p1)), fill=(255, 205, 90, int(120 * a)), width=5)
        paste_c(im, sand_grain(14), ax, ay, a); paste_c(im, glow(70, (255, 120, 90), 1.5), bx, by, a)
        d = ImageDraw.Draw(im, 'RGBA')
        label(d, W / 2, 940, '3,150 km of almost nothing', 50, GREY, a)
        ptext(d, (W / 2, 330), 'SEND THIS TO', 110, WHITE, t, s0, nx('share') + 0.3)
        ptext(d, (W / 2, 470), 'SOMEONE WHO THINKS', 86, WHITE, t, s0 + 0.15, nx('share') + 0.3)
        ptext(d, (W / 2, 610), 'SPACE IS CROWDED', 104, GOLD, t, s0 + 0.3, nx('share') + 0.3)
        pill(d, W / 2, 1500, 'SHARE ➤', 70, (30, 120, 200), alpha=a * ease(ramp(t, s0 + 0.8, s0 + 1.1)))

    # ============ GALAXY setup + reveal
    a = xf(t, st('setup') - 0.1, nx('reveal') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('setup'); sr = st('reveal')
        g = ease(ramp(t, s0, sr + 0.3))
        rot = t * 0.03
        gs = galaxy_sp(470)
        gsr = gs.rotate(math.degrees(rot), resample=Image.BICUBIC)
        k = 0.7 + 0.3 * g
        gsr = gsr.resize((int(gsr.width * k), int(gsr.height * k)))
        paste_c(im, gsr, 540, 960, a)
        d = ImageDraw.Draw(im, 'RGBA')
        if t < sr:
            ptext(d, (W / 2, 230), 'OUR WHOLE GALAXY', 100, WHITE, t, s0, sr + 0.1)
            ptext(d, (W / 2, 360), 'AT THIS SCALE?', 116, CYAN, t, s0 + 0.15, sr + 0.1)
        else:
            dim(im, 0.35 * a * ease(ramp(t, sr + 1.6, sr + 2.0)))
            d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 230), '74 MILLION km', 118, GOLD, t, sr, nx('reveal') + 0.3)
            ba = ease(ramp(t, sr + 2.2, sr + 2.7)) * a
            if ba > 0:
                x0, x1, y = 110, 970, 1520
                d.line((x0, y, x1, y), fill=(255, 255, 255, int(160 * ba)), width=4)
                gx = x0 + (x1 - x0) * 0.496 * ease(ramp(t, sr + 2.4, sr + 3.6))
                d.line((x0, y, gx, y), fill=(140, 200, 255, int(255 * ba)), width=18)
                paste_c(im, earth_rot(16, 0.3), x0, y, ba)
                paste_c(im, glow(70, (255, 170, 60), 1.5), x1, y, ba); paste_c(im, sun_sp(22), x1, y, ba)
                d = ImageDraw.Draw(im, 'RGBA')
                label(d, x0 + 30, y + 70, 'real Earth', 42, WHITE, ba)
                label(d, x1 - 30, y + 70, 'real Sun', 42, ORANGE, ba)
                label(d, (x0 + x1) / 2, y - 80, 'our model galaxy', 46, (140, 200, 255), ba)
                ptext(d, (W / 2, 1760), 'HALFWAY TO THE SUN', 96, GOLD, t, sr + 3.3, nx('reveal') + 0.3)

    # ============ COMMENT + loop back to the shrinking Earth
    a = xf(t, st('comment') - 0.1, TOTAL + 1, 0.2, 0.01)
    if a > 0:
        s0 = st('comment'); d = ImageDraw.Draw(im, 'RGBA')
        atom_icon(d, 290, 1050, 120, t, a)
        paste_c(im, galaxy_sp(150), 790, 1050, a)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 260), 'WHICH ONE', 116, WHITE, t, s0, TOTAL + 1)
        ptext(d, (W / 2, 400), 'BROKE YOUR BRAIN?', 96, GOLD, t, s0 + 0.15, TOTAL + 1)
        pa = ease(ramp(t, s0 + 1.2, s0 + 1.5)) * a
        pill(d, 290, 1290, 'THE ATOM', 62, (30, 120, 200), alpha=pa)
        pill(d, 790, 1290, 'THE GALAXY', 62, (120, 60, 200), alpha=pa)
        text(d, (W / 2, 1460), 'COMMENT ↓', 84, GOLD, alpha=pa)
        # loop: big Earth rushes back in during the last 0.8 s
        la = ramp(t, TOTAL - 0.8, TOTAL)
        if la > 0:
            R = int(46 + (620 - 46) * ease(la))
            paste_c(im, earth_rot(R, t * 0.5), 540, 1060, ease(la))
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

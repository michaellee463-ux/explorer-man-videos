from base import *

ORANGE = (255, 150, 60); GREEN = (60, 210, 110); BLUE = (120, 170, 255)
MOON_PX = 150                     # full Moon width in the to-scale shots
GAL_PX = 6 * MOON_PX              # Andromeda long axis = 6 Moons (3.0 x 1.0 deg vs 0.5 deg)
TILT = -32

def dim(im, k):
    if k <= 0: return
    im.alpha_composite(Image.new('RGBA', im.size, (0, 0, 0, int(255 * min(1, k)))))
_G = {}
def grad(im, top=True, h=640, a=210):
    k = (top, h, a)
    if k not in _G:
        g = np.zeros((h, W, 4), np.uint8); col = np.linspace(a, 0, h) if top else np.linspace(0, a, h)
        g[..., 3] = col[:, None].astype(np.uint8); _G[k] = Image.fromarray(g, 'RGBA')
    im.alpha_composite(_G[k], (0, 0 if top else H - h))

# ---------------------------------------------------------------- Andromeda sprite (inclined spiral, dust lanes)
def make_andromeda(L, core_only=False):
    SS = 1; n = int(L * 1.6)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
    u = (x - c) / (L / 2) * 0.68; v = (y - c) / (L / 2) / 0.30 * 0.68
    r = np.sqrt(u * u + v * v)
    rg = np.random.default_rng(11)
    def noise(g, s):
        a = rg.random((g, g)).astype(np.float32)
        return np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
    nz = 0.6 * noise(40, 0) + 0.4 * noise(140, 0)
    core = np.exp(-r / 0.035) * 1.6 + np.exp(-r / 0.11) * 0.9
    disk = np.exp(-r / 0.34) * (0.7 + 0.7 * nz)
    halo = np.exp(-r / 0.55) * 0.12
    # spiral-ish ring structure (Andromeda's ring at ~10 kpc) and dust lanes on the near side
    ang = np.arctan2(v, u)
    arms = 0.5 + 0.5 * np.cos(2 * (ang - 4.2 * np.log(r + 0.05)))
    ring = np.exp(-((r - 0.62) / 0.07) ** 2) * 0.35 * (0.5 + nz)
    disk = disk * (0.6 + 0.6 * arms) + ring
    dust = (np.exp(-((r - 0.42) / 0.035) ** 2) + 0.8 * np.exp(-((r - 0.58) / 0.03) ** 2) + 0.6 * np.exp(-((r - 0.74) / 0.03) ** 2))
    dust *= np.clip((v + 0.15) / 0.4, 0, 1) * (0.55 + 0.45 * nz)
    lum = core + disk * (1 - 0.75 * np.clip(dust, 0, 1)) + halo
    if core_only:
        lum = core * 0.9 + disk * 0.08
    warm = np.array([1.0, 0.86, 0.62]); cool = np.array([0.62, 0.74, 1.0])
    mixw = np.clip(np.exp(-r / 0.25), 0, 1)[..., None]
    col = (warm * mixw + cool * (1 - mixw)) * lum[..., None]
    # pink star-forming knots + resolved stars in the disk
    for _ in range(int(L * 0.25)):
        rr = rg.uniform(0.35, 0.95); th = rg.uniform(0, 2 * np.pi)
        px = int(c + rr * np.cos(th) * L / 2); py = int(c + rr * np.sin(th) * 0.30 * L / 2)
        if 0 < px < n - 2 and 0 < py < n - 2 and not core_only:
            col[py:py + 2, px:px + 2] += np.array([0.5, 0.35, 0.5]) if rg.random() < 0.3 else np.array([0.45, 0.5, 0.65])
    a = np.clip(lum * 1.8, 0, 1)
    rgb = np.clip(col / (1 + col * 0.6) * 1.35, 0, 1)
    arr = np.concatenate([rgb, a[..., None]], -1)
    im = Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(max(1, L / 900)))
    im = im.rotate(TILT, resample=Image.BICUBIC, expand=True)
    return im

ANDRO = make_andromeda(1800)          # master sprite: galaxy long axis = 1800 px
ANDRO_CORE = make_andromeda(1800, True)
A_SCALE = 1800                        # long-axis px in the master
def andro(L, core=False):
    key = ('a', int(L), core)
    if key not in CACHE:
        if len(CACHE) > 6: CACHE.clear()
        src = ANDRO_CORE if core else ANDRO; f = L / A_SCALE
        CACHE[key] = src.resize((max(2, int(src.width * f)), max(2, int(src.height * f))), Image.BILINEAR)
    return CACHE[key]

def make_milkyway(R):
    n = int(R * 2.3); y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
    u = (x - c) / R; v = (y - c) / R / 0.55; r = np.sqrt(u * u + v * v); ang = np.arctan2(v, u)
    rg = np.random.default_rng(5)
    a0 = rg.random((60, 60)).astype(np.float32)
    nz = np.array(Image.fromarray((a0 * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
    arms = (0.5 + 0.5 * np.cos(2 * (ang - 3.0 * np.log(r + 0.05)))) ** 3
    lum = np.exp(-r / 0.08) * 1.4 + np.exp(-r / 0.35) * (0.25 + 0.9 * arms) * (0.6 + 0.6 * nz)
    warm = np.array([1.0, 0.88, 0.66]); cool = np.array([0.6, 0.75, 1.0]); m = np.exp(-r / 0.2)[..., None]
    col = (warm * m + cool * (1 - m)) * lum[..., None]
    arr = np.concatenate([np.clip(col / (1 + col * 0.6) * 1.35, 0, 1), np.clip(lum * 1.4, 0, 1)[..., None]], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').rotate(15, resample=Image.BICUBIC, expand=True)
MW = make_milkyway(300)

from PIL import ImageEnhance
MOON = moonsp(MOON_PX // 2)
_a = MOON.getchannel('A'); MOON = ImageEnhance.Brightness(MOON.convert('RGB')).enhance(1.35).convert('RGBA'); MOON.putalpha(_a)
def moon(px):
    return sp(('moonr', int(px)), lambda: MOON.resize((int(MOON.width * px / MOON_PX), int(MOON.height * px / MOON_PX)), Image.LANCZOS))

# night-sky background with twinkle layer
rng2 = np.random.default_rng(21)
TW = [(int(rng2.integers(0, W)), int(rng2.integers(0, H)), rng2.uniform(0, 6.28), rng2.uniform(1.5, 3.5)) for _ in range(90)]
def twinkle(d, t, a=1.0, ox=0, oy=0):
    for (x, y, ph, s) in TW:
        k = 0.5 + 0.5 * math.sin(t * 3 + ph)
        al = int(220 * k * a)
        if al > 8: d.ellipse((x + ox - s, y + oy - s, x + ox + s, y + oy + s), fill=(255, 255, 255, al))

# horizon silhouette for the naked-eye scene
def horizon():
    im = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rg = np.random.default_rng(4)
    pts = [(0, 520)]
    for x in range(0, W + 40, 40): pts.append((x, 250 + 40 * math.sin(x / 170) + rg.uniform(-12, 12)))
    pts.append((W, 520)); d.polygon(pts, fill=(4, 6, 10, 255))
    for x in (130, 220, 860, 960):
        h = rg.uniform(150, 230)
        for k in range(6):
            w = 60 - k * 9; yb = 260 - k * h / 7
            d.polygon([(x - w, yb), (x + w, yb), (x, yb - h / 4)], fill=(4, 6, 10, 255))
    return im
HOR = horizon()

def to_scale(im, t, cx, cy, s=1.0, a=1.0, moons=0.0, moonpos=None, core=False):
    """Andromeda at 6 Moon widths, with a real full Moon beside it (same scale factor s)."""
    g = andro(GAL_PX * s, core)
    paste_c(im, g, cx, cy, a)
    m = moon(MOON_PX * s)
    if moonpos is not None: paste_c(im, m, moonpos[0], moonpos[1], a)
    if moons > 0:
        d = ImageDraw.Draw(im, 'RGBA'); ang = math.radians(TILT); L = GAL_PX * s; R = MOON_PX * s / 2
        for i in range(6):
            p = ease(ramp(moons, i / 6, (i + 1) / 6))
            if p <= 0: continue
            off = -L / 2 + R + i * 2 * R
            x = cx + off * math.cos(ang); y = cy - off * math.sin(ang)
            d.ellipse((x - R, y - R, x + R, y + R), outline=(255, 230, 160, int(230 * p * a)), width=max(3, int(5 * s)))
            text(d, (x, y - R - 34 * s), str(i + 1), int(44 * s), GOLD, BLACK, alpha=p * a)

def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')
    twinkle(d, t)

    # ============ HOOK: Andromeda to scale with the Moon, moons counting along it (mid-action from frame 0)
    a = xf(t, -1, nx('hook') + 0.2, 0.01, 0.35)
    if a > 0:
        s = 1.05 + 0.04 * t
        to_scale(im, t, 540, 980, s, a, moons=ramp(t, 0.0, 2.6) * 1.0 + 0.17, moonpos=(870, 1470))
        grad(im, True, 700, 220); d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 210), 'A GALAXY 6× WIDER', 96, WHITE, BLACK, alpha=a)
        text(d, (W / 2, 330), 'THAN THE MOON', 110, GOLD, BLACK, alpha=a)
        grad(im, False, 560, 210); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 1640), "WHY CAN'T", 120, WHITE, t, max(0, st('hook') + 2.6), nx('hook') + 0.2)
        ptext(d, (W / 2, 1790), 'YOU SEE IT?', 130, RED, t, max(0, st('hook') + 2.9), nx('hook') + 0.2)
        if t < 2.6:
            text(d, (W / 2, 1700), 'IN YOUR SKY', 110, CYAN, BLACK, alpha=1 - ease(ramp(t, 2.3, 2.6)))

    # ============ NAME + STARS: zoom into the galaxy
    a = xf(t, st('name') - 0.2, nx('stars') + 0.2, 0.3, 0.3)
    if a > 0:
        z = ease(ramp(t, st('name') - 0.2, nx('stars')))
        paste_c(im, andro(1500 + 700 * z), 540 - 60 * z, 1000, a)
        if t >= st('stars'):   # sparkles = stars
            rg = np.random.default_rng(int(t * 10))
            for _ in range(40):
                x = rg.uniform(100, 980); y = 1000 + rg.uniform(-380, 380); r_ = rg.uniform(2, 5)
                d.ellipse((x - r_, y - r_, x + r_, y + r_), fill=(255, 255, 255, int(200 * a)))
        grad(im, True, 640, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 220), 'ANDROMEDA', 140, WHITE, t, st('name') + 0.1, st('stars'))
        ptext(d, (W / 2, 370), 'OUR CLOSEST BIG', 76, CYAN, t, st('name') + 0.6, st('stars'))
        ptext(d, (W / 2, 460), 'NEIGHBOR GALAXY', 76, CYAN, t, st('name') + 0.9, st('stars'))
        if t >= st('stars'):
            p = ease(ramp(t, st('stars'), st('stars') + 1.2))
            v = int(1e12 * p)
            text(d, (W / 2, 250), f'{v:,}', 84 if v >= 1e11 else 90, GOLD, BLACK, alpha=a)
            ptext(d, (W / 2, 390), '~1 TRILLION STARS', 92, WHITE, t, st('stars') + 0.6, nx('stars') + 0.2)

    # ============ DIST + LIGHT: Andromeda far away, light travelling to us
    a = xf(t, st('dist') - 0.2, nx('light') + 0.2, 0.3, 0.3)
    if a > 0:
        paste_c(im, andro(560), 540, 700, a)
        paste_c(im, MW, 540, 1500, a * 0.95)
        text(d, (540, 1760), 'YOU ARE HERE', 50, GREY, POP_B, stroke=4, alpha=a)
        for yy in range(860, 1340, 34):
            d.line((540, yy, 540, yy + 16), fill=(255, 255, 255, int(150 * a)), width=5)
        grad(im, True, 520, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), '2.5 MILLION', 130, GOLD, t, st('dist') + 0.1, st('light'))
        ptext(d, (W / 2, 340), 'LIGHT-YEARS AWAY', 92, WHITE, t, st('dist') + 0.5, st('light'))
        if t >= st('light'):
            p = ramp(t, st('light') + 0.3, st('light') + 4.0)
            yph = 860 + 480 * p
            paste_c(im, glow(70, (255, 240, 200), 1.6), 540, yph, a); d = ImageDraw.Draw(im, 'RGBA')
            yrs = 2_500_000 * (1 - p)
            text(d, (W / 2, 190), 'THIS LIGHT LEFT', 92, WHITE, BLACK, alpha=a)
            text(d, (W / 2, 320), f'{2_500_000:,} YEARS AGO', 82, GOLD, BLACK, alpha=a)
            # timeline bar
            ba = a * ease(ramp(t, st('light') + 3.6, st('light') + 4.0))
            if ba > 0:
                d.rounded_rectangle((90, 440, 990, 480), 20, fill=(255, 255, 255, int(70 * ba)))
                xs = 90 + 900 * (1 - 300_000 / 2_500_000)
                d.rounded_rectangle((xs, 440, 990, 480), 20, fill=GREEN + (int(255 * ba),))
                text(d, (130, 530), 'LIGHT LEFT', 40, GREY, POP_B, anchor='lm', stroke=3, alpha=ba)
                text(d, (990, 530), 'HUMANS LIKE US', 40, GREEN, POP_B, anchor='rm', stroke=3, alpha=ba)
                text(d, (990, 580), '~300,000 YRS', 40, GREEN, POP_B, anchor='rm', stroke=3, alpha=ba)

    # ============ SPEED: coming toward us
    a = xf(t, st('speed') - 0.2, nx('speed') + 0.1, 0.3, 0.2)
    if a > 0:
        p = ramp(t, st('speed') - 0.2, nx('speed'))
        Lg = 600 + 900 * ease(p)
        rg = np.random.default_rng(3)
        for _ in range(60):   # speed streaks radiating out
            th = rg.uniform(0, 6.28); r0 = rg.uniform(200, 700) + ((t * 900) % 600)
            x0 = 540 + r0 * math.cos(th); y0 = 1000 + r0 * math.sin(th)
            d.line((x0, y0, x0 + 60 * math.cos(th), y0 + 60 * math.sin(th)), fill=(200, 220, 255, int(120 * a)), width=3)
        paste_c(im, andro(Lg), 540, 1000, a)
        grad(im, True, 560, 220); grad(im, False, 520, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'COMING AT US', 110, WHITE, t, st('speed') + 0.1, nx('speed'))
        ptext(d, (W / 2, 350), '250,000 MPH', 130, RED, t, st('speed') + 1.6, nx('speed'))
        t1 = st('speed') + 3.9
        if t >= t1:
            miles = 69.4 * (t - t1)
            text(d, (W / 2, 1640), '70 MILES CLOSER', 96, GOLD, BLACK, alpha=a)
            text(d, (W / 2, 1770), 'EVERY SECOND', 90, WHITE, BLACK, alpha=a)

    # ============ TEASE
    a = xf(t, st('tease') - 0.1, nx('tease') + 0.1, 0.12, 0.15)
    if a > 0:
        paste_c(im, andro(1500), 540, 1000, a * 0.5)
        dim(im, 0.35 * a); d = ImageDraw.Draw(im, 'RGBA')
        jx = 8 * math.sin(t * 60) * (1 - ramp(t, st('tease'), st('tease') + 0.4))
        ptext(d, (W / 2 + jx, 860), "BUT THAT'S NOT", 116, WHITE, t, st('tease'), nx('tease') + 0.1)
        ptext(d, (W / 2 + jx, 1020), 'THE CRAZY PART', 116, GOLD, t, st('tease') + 0.25, nx('tease') + 0.1)

    # ============ CRASH: two galaxies on course
    a = xf(t, st('crash') - 0.1, nx('crash') + 0.2, 0.25, 0.3)
    if a > 0:
        p = ease(ramp(t, st('crash'), nx('crash')))
        paste_c(im, MW, 360 + 90 * p, 1250 - 120 * p, a)
        paste_c(im, andro(820), 760 - 110 * p, 760 + 110 * p, a)
        grad(im, True, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 210), 'A CRASH INTO', 104, WHITE, t, st('crash') + 0.2, nx('crash') + 0.2)
        ptext(d, (W / 2, 350), 'OUR MILKY WAY?', 110, ORANGE, t, st('crash') + 1.4, nx('crash') + 0.2)
        grad(im, False, 400, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 1730), 'IN A FEW BILLION YEARS', 72, GREY, t, st('crash') + 2.8, nx('crash') + 0.2)

    # ============ COIN: 2025 study, 50/50 in 10 billion years
    a = xf(t, st('coin') - 0.1, nx('coin') + 0.2, 0.25, 0.3)
    if a > 0:
        paste_c(im, MW, 330, 1550, a * 0.55); paste_c(im, andro(560), 800, 1500, a * 0.55)
        d = ImageDraw.Draw(im, 'RGBA')
        ct = t - (st('coin') + 4.0)
        sq = abs(math.cos(ct * 9)) if 0 < ct < 1.6 else 1.0
        hy = -380 * math.sin(math.pi * ct / 1.6) if 0 < ct < 1.6 else 0
        R_ = 190
        cy = 960 + hy
        d.ellipse((540 - R_, cy - R_ * sq, 540 + R_, cy + R_ * sq), fill=(225, 175, 60, int(255 * a)), outline=(150, 110, 30, int(255 * a)), width=12)
        if sq > 0.5: text(d, (540, cy), '50/50', int(110 * sq), WHITE, BLACK, alpha=a)
        ptext(d, (W / 2, 210), '2025 STUDY', 116, WHITE, t, st('coin') + 0.6, nx('coin') + 0.2)
        ptext(d, (W / 2, 340), 'HUBBLE + GAIA', 80, CYAN, t, st('coin') + 2.0, nx('coin') + 0.2)
        ptext(d, (W / 2, 1300), "IT'S A COIN FLIP", 104, GOLD, t, st('coin') + 4.6, nx('coin') + 0.2)
        ptext(d, (W / 2, 1440), 'IN THE NEXT', 70, WHITE, t, st('coin') + 6.4, nx('coin') + 0.2)
        ptext(d, (W / 2, 1540), '10 BILLION YEARS', 92, WHITE, t, st('coin') + 6.8, nx('coin') + 0.2)

    # ============ MISS: stars pass each other
    a = xf(t, st('miss') - 0.1, nx('miss') + 0.2, 0.25, 0.3)
    if a > 0:
        p = ramp(t, st('miss'), nx('miss'))
        rg = np.random.default_rng(8)
        for i in range(36):
            y = rg.uniform(560, 1500); x = rg.uniform(-200, 1280)
            x1 = (x + 700 * p) % 1300 - 100; x2 = (x - 700 * p) % 1300 - 100
            d.ellipse((x1 - 9, y - 9, x1 + 9, y + 9), fill=(255, 220, 160, int(255 * a)))
            d.ellipse((x2 - 9, y + 30 - 9, x2 + 9, y + 30 + 9), fill=(150, 190, 255, int(255 * a)))
        grad(im, True, 520, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 210), 'EVEN IF THEY MERGE', 86, WHITE, t, st('miss') + 0.1, nx('miss') + 0.2)
        ptext(d, (W / 2, 1700), 'STARS ALMOST', 104, GOLD, t, st('miss') + 1.8, nx('miss') + 0.2)
        ptext(d, (W / 2, 1830), 'NEVER HIT', 110, GOLD, t, st('miss') + 2.2, nx('miss') + 0.2)

    # ============ ANSWER: what your eyes see (core smudge ~1 Moon wide), then REVEAL: full galaxy, 6 Moons
    a = xf(t, st('answer') - 0.1, nx('reveal') + 0.2, 0.25, 0.3)
    if a > 0:
        sky = Image.new('RGBA', (W, H), (8, 12, 34, int(200 * a))); im.alpha_composite(sky); d = ImageDraw.Draw(im, 'RGBA')
        twinkle(d, t, a)
        s = 1.0; cx, cy = 520, 860; mp = (870, 1330)
        rp = ease(ramp(t, st('reveal') + 2.2, st('reveal') + 3.4))     # bloom at "there it is"
        if rp < 1:
            g = andro(GAL_PX * s, True); paste_c(im, g, cx, cy, a * (1 - rp) * 0.85)
        if rp > 0:
            paste_c(im, andro(GAL_PX * s), cx, cy, a * rp)
        paste_c(im, moon(MOON_PX * s), mp[0], mp[1], a)
        d = ImageDraw.Draw(im, 'RGBA')
        if t < st('reveal') + 2.2 and t > st('answer') + 6.0:
            R = MOON_PX * s / 2; ka = a * ease(ramp(t, st('answer') + 6.0, st('answer') + 6.4))
            for k in range(0, 360, 20):
                d.arc((cx - R, cy - R, cx + R, cy + R), k, k + 10, fill=(255, 230, 160, int(230 * ka)), width=5)
        if rp > 0:
            to_scale(im, t, cx, cy, s, 0.0001, moons=ramp(t, st('reveal') + 2.6, st('reveal') + 4.0))
            d = ImageDraw.Draw(im, 'RGBA')
            # draw the moon outlines with full alpha (to_scale draws with alpha a)
            ang = math.radians(TILT); L = GAL_PX * s; R = MOON_PX * s / 2
            mo = ramp(t, st('reveal') + 2.6, st('reveal') + 4.0)
            for i in range(6):
                pp = ease(ramp(mo, i / 6, (i + 1) / 6))
                if pp <= 0: continue
                off = -L / 2 + R + i * 2 * R; x = cx + off * math.cos(ang); y = cy - off * math.sin(ang)
                d.ellipse((x - R, y - R, x + R, y + R), outline=(255, 230, 160, int(230 * pp * a)), width=5)
                text(d, (x, y - R - 34), str(i + 1), 44, GOLD, BLACK, alpha=pp * a)
        im.alpha_composite(HOR, (0, H - 520)); d = ImageDraw.Draw(im, 'RGBA')
        grad(im, True, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'WHAT YOUR', 110, WHITE, t, st('answer') + 1.4, st('reveal'))
        ptext(d, (W / 2, 330), 'EYES SEE', 120, CYAN, t, st('answer') + 1.8, st('reveal'))
        ptext(d, (W / 2, 1520), 'TOO FAINT', 120, RED, t, st('answer') + 2.4, st('answer') + 6.0)
        ptext(d, (W / 2, 1520), '≈ 1 MOON WIDE', 100, GOLD, t, st('answer') + 6.4, st('reveal') + 2.2)
        ptext(d, (W / 2, 210), 'LONG EXPOSURE', 108, WHITE, t, st('reveal') + 0.1, nx('reveal') + 0.2)
        ptext(d, (W / 2, 340), 'PHOTO', 110, CYAN, t, st('reveal') + 0.5, st('reveal') + 2.2)
        ptext(d, (W / 2, 1520), '6 FULL MOONS', 130, GOLD, t, st('reveal') + 3.0, nx('reveal') + 0.2)
        ptext(d, (W / 2, 1660), 'WIDE', 130, WHITE, t, st('reveal') + 3.4, nx('reveal') + 0.2)

    # ============ FAR
    a = xf(t, st('far') - 0.1, nx('far') + 0.2, 0.25, 0.3)
    if a > 0:
        paste_c(im, andro(1300 + 150 * ramp(t, st('far'), nx('far'))), 540, 1000, a)
        grad(im, True, 600, 220); grad(im, False, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'ONE OF THE FARTHEST', 82, WHITE, t, st('far') + 0.1, nx('far') + 0.2)
        ptext(d, (W / 2, 320), 'THINGS YOU CAN SEE', 82, WHITE, t, st('far') + 0.6, nx('far') + 0.2)
        ptext(d, (W / 2, 1680), 'WITH YOUR OWN EYES', 86, GOLD, t, st('far') + 2.4, nx('far') + 0.2)

    # ============ SHARE + COMMENT, loops back into the opening composition
    a = xf(t, st('share') - 0.1, TOTAL + 1, 0.3, 0.01)
    if a > 0:
        s = 1.05 + 0.04 * (t - st('share')) * 0.3
        to_scale(im, t, 540, 980, 1.05, a, moonpos=(870, 1470))
        lp = ramp(t, TOTAL - 0.7, TOTAL); ca = 1 - ease(lp)
        grad(im, True, 700, 225); grad(im, False, 600, 215); d = ImageDraw.Draw(im, 'RGBA')
        if t < st('comment'):
            ptext(d, (W / 2, 200), 'SEND THIS TO SOMEONE', 76, WHITE, t, st('share'), st('comment'))
            ptext(d, (W / 2, 320), "WHO'S NEVER SEEN", 92, WHITE, t, st('share') + 0.3, st('comment'))
            ptext(d, (W / 2, 450), 'ANOTHER GALAXY', 104, GOLD, t, st('share') + 0.7, st('comment'))
        else:
            text(d, (W / 2, 220), 'HAVE YOU EVER', 110, WHITE, BLACK, alpha=ca)
            text(d, (W / 2, 360), 'SEEN IT?', 130, GOLD, BLACK, alpha=ca)
            pa = ease(ramp(t, st('comment') + 0.9, st('comment') + 1.2)) * ca
            pill(d, 330, 1600, 'YES', 80, (30, 150, 70), alpha=pa)
            pill(d, 750, 1600, 'NO', 80, (205, 30, 40), alpha=pa)
            text(d, (W / 2, 1760), 'COMMENT ↓', 80, GOLD, BLACK, alpha=pa)
        if lp > 0:
            la = ease(lp)
            text(d, (W / 2, 210), 'A GALAXY 6× WIDER', 96, WHITE, BLACK, alpha=la)
            text(d, (W / 2, 330), 'THAN THE MOON', 110, GOLD, BLACK, alpha=la)
            text(d, (W / 2, 1700), 'IN YOUR SKY', 110, CYAN, BLACK, alpha=la)
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

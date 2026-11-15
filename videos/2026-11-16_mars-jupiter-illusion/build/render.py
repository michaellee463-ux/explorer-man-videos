from base import *

ORANGE = (255, 140, 60)
MARSC = (255, 120, 60)
JUPC = (255, 244, 215)

# ---------------------------------------------------------------- dawn sky (looking south, an hour before sunrise)
k2 = (yy / H)[..., None]
top = np.array([0.012, 0.018, 0.06]); mid = np.array([0.04, 0.07, 0.17]); low = np.array([0.30, 0.20, 0.22])
skyA = np.where(k2 < 0.6, top * (1 - k2 / 0.6) + mid * (k2 / 0.6), mid * (1 - (k2 - 0.6) / 0.4) + low * ((k2 - 0.6) / 0.4))
# warm glow on the left (east) near the horizon
skyA = skyA + np.exp(-(((xx + 150) / 700) ** 2 + ((yy - 1750) / 380) ** 2))[..., None] * np.array([0.45, 0.22, 0.06])
rs = np.random.default_rng(11)
for _ in range(500):
    x, y = rs.integers(0, W), rs.integers(0, 1300)
    skyA[y, x] += rs.uniform(0.1, 0.5) * (1 - y / 1500)
SKY = Image.fromarray((np.clip(skyA, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

def ground(d, a=255):
    """trees + rooftops silhouette along the bottom"""
    c = (6, 8, 16, a)
    d.rectangle((0, 1700, W, H), fill=c)
    rg = np.random.default_rng(3)
    x = -20
    while x < W + 40:
        w_ = rg.integers(60, 140); h_ = rg.integers(50, 170)
        if rg.random() < 0.35:   # house with roof
            d.rectangle((x, 1700 - h_ * 0.6, x + w_, 1710), fill=c)
            d.polygon([(x - 10, 1700 - h_ * 0.6), (x + w_ / 2, 1700 - h_), (x + w_ + 10, 1700 - h_ * 0.6)], fill=c)
        else:                    # tree
            d.ellipse((x, 1700 - h_, x + w_, 1700 - h_ * 0.25), fill=c)
            d.rectangle((x + w_ / 2 - 6, 1700 - h_ * 0.4, x + w_ / 2 + 6, 1710), fill=c)
        x += w_ * 0.8

def starpt(R, col, spikes=True):
    def mk():
        n = int(R * 2); img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
        y, x = np.mgrid[0:n, 0:n].astype(np.float32); r = np.sqrt((x - n / 2) ** 2 + (y - n / 2) ** 2) / (n / 2)
        a = np.clip(1 - r, 0, 1) ** 3.0 + 0.9 * np.exp(-(r / 0.06) ** 2)
        if spikes:
            a += 0.35 * np.exp(-(np.abs(x - n / 2) / 2.5) ** 2) * np.clip(1 - r, 0, 1) ** 2
            a += 0.35 * np.exp(-(np.abs(y - n / 2) / 2.5) ** 2) * np.clip(1 - r, 0, 1) ** 2
        arr = np.zeros((n, n, 4), np.float32); arr[..., :3] = np.array(col) / 255
        core = np.exp(-(r / 0.08) ** 2)[..., None]
        arr[..., :3] = arr[..., :3] * (1 - core) + core
        arr[..., 3] = np.clip(a, 0, 1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('star', R, col, spikes), mk)

def pair(im, cx, cy, sepx, s=1.0, alpha=1.0, jb=1.0, tw=0.0):
    """Jupiter (bright, white) lower right, Mars (orange, fainter) upper left: 1.2 deg apart"""
    jx, jy = cx + sepx * 0.42, cy + sepx * 0.30
    mx, my = cx - sepx * 0.58, cy - sepx * 0.42
    paste_c(im, starpt(int(90 * s * jb), JUPC), jx, jy, alpha)
    paste_c(im, starpt(int(46 * s), MARSC, spikes=False), mx, my, alpha * (0.9 + 0.1 * math.sin(tw * 9)))
    return (jx, jy), (mx, my)

def jupiter_sprite(R):
    def mk():
        SS = 2; r = R * SS; n = int(2 * r + 8)
        y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2
        u = (x - c) / r; v = (y - c) / r; rr = u * u + v * v; inside = rr <= 1
        z = np.sqrt(np.clip(1 - rr, 0, 1))
        L = np.array([-0.5, -0.35, 0.79]); L /= np.linalg.norm(L)
        lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
        lat = v
        bands = 0.5 + 0.5 * np.sin(lat * 19 + 0.6 * np.sin(u * 3 + lat * 7))
        c1 = np.array([0.93, 0.86, 0.74]); c2 = np.array([0.72, 0.52, 0.36])
        col = c1 * bands[..., None] + c2 * (1 - bands[..., None])
        spot = np.exp(-(((u - 0.25) / 0.16) ** 2 + ((v - 0.33) / 0.08) ** 2))[..., None]
        col = col * (1 - spot) + np.array([0.80, 0.38, 0.25]) * spot
        col = col * (0.08 + 0.92 * lam[..., None])
        arr = np.concatenate([np.clip(col, 0, 1), inside[..., None].astype(np.float32)], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)
    return sp(('jup', R), mk)

def marsball(R): return sp(('mars', R), lambda: sphere(R, (0.78, 0.36, 0.18), 8, rough=0.35))

def hand(d, cx, tipy, a):
    """silhouette: pinky raised at arm's length, tip at (cx, tipy)"""
    c = (12, 10, 14, int(255 * a)); rim = (255, 170, 120, int(140 * a))
    fw = 86
    d.rounded_rectangle((cx - fw / 2, tipy, cx + fw / 2, tipy + 420), fw // 2, fill=c, outline=rim, width=3)
    d.rounded_rectangle((cx - 40, tipy + 300, cx + 260, tipy + 700), 70, fill=c, outline=rim, width=3)
    if tipy + 650 < H + 60: d.rounded_rectangle((cx + 120, tipy + 650, cx + 320, H + 60), 60, fill=c)

def label(d, x, y, s, size, col, alpha, anchor='mm'):
    text(d, (x, y), s, size, col, POP_B, anchor=anchor, stroke=4, alpha=alpha)

def lightpulse(im, x, y, col, a):
    paste_c(im, glow(70, col, 1.4), x, y, a); paste_c(im, glow(22, (255, 255, 255), 1.2), x, y, a)

# ---------------------------------------------------------------- side view geometry (distances to scale)
EX, MX, JX, SY = 90, 90 + 800 * 195.0 / 786.9, 890, 1080
def sideview(im, t, a, show_m=1.0, show_j=1.0):
    d = ImageDraw.Draw(im, 'RGBA')
    for x in range(EX + 40, JX - 50, 26):
        d.line((x, SY, x + 12, SY), fill=(200, 210, 230, int(110 * a)), width=3)
    paste_c(im, earth(46), EX, SY, a)
    paste_c(im, glow(110, (255, 120, 60), 1.8), MX, SY, a * show_m * 0.5)
    paste_c(im, marsball(24), MX, SY, a * show_m)
    paste_c(im, glow(200, (255, 230, 190), 1.8), JX, SY, a * show_j * 0.4)
    paste_c(im, jupiter_sprite(70), JX, SY, a * show_j)
    d = ImageDraw.Draw(im, 'RGBA')
    label(d, EX, SY + 88, 'EARTH', 38, CYAN, a)
    label(d, MX, SY + 88, 'MARS', 38, ORANGE, a * show_m)
    label(d, JX - 20, SY + 120, 'JUPITER', 38, GOLD, a * show_j)
    text(d, (W / 2, 720), 'distances to scale · planet sizes not', 30, GREY, POP_M, stroke=3, alpha=a * 0.9)

def bar(d, x0, x1, y, col, a, h=10):
    if x1 > x0 and a > 0: d.rounded_rectangle((x0, y - h / 2, x1, y + h / 2), h // 2, fill=col + (int(255 * a),))

# ---------------------------------------------------------------- frame
def frame(t):
    sky_keys = ('hook', 'where', 'which', 'pinky')
    im = SKY.copy() if (t < st('illusion') or st('reveal') <= t < st('size') or t >= st('bright')) else BG.copy()
    d = ImageDraw.Draw(im, 'RGBA')

    # ============ HOOK: the pair, already glowing, huge text in frame 1
    a = xf(t, -1, st('where') + 0.1, 0.01, 0.25)
    if a > 0:
        z = 1.0 + 0.08 * t
        pair(im, W / 2, 1020, 210 * z, 1.6 * z, a, tw=t)
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 330), 'TWO PLANETS', 120, WHITE, alpha=a)
        text(d, (W / 2, 480), 'ALMOST', 110, WHITE, alpha=a)
        text(d, (W / 2, 640), 'TOUCHING', 160, GOLD, alpha=a)
        label(d, W / 2 + 240, 1260, 'JUPITER', 50, JUPC, a * ease(ramp(t, 0.6, 1.0)))
        label(d, W / 2 - 270, 800, 'MARS', 50, ORANGE, a * ease(ramp(t, 0.6, 1.0)))
        ground(d, int(255 * a))

    # ============ WHERE: before sunrise, high in the south
    a = xf(t, st('where'), st('which') + 0.1, 0.25, 0.25)
    if a > 0:
        s0 = st('where')
        pair(im, W / 2 + 40, 560, 60, 0.75, a, tw=t)
        d = ImageDraw.Draw(im, 'RGBA'); ground(d, int(255 * a))
        ar = ease(ramp(t, s0 + 1.0, s0 + 2.2))
        d.line((W / 2, 1600, W / 2, 1600 - 900 * ar), fill=(255, 255, 255, int(200 * a)), width=8)
        if ar > 0.95: d.polygon([(W / 2 - 26, 720), (W / 2 + 26, 720), (W / 2, 680)], fill=(255, 255, 255, int(200 * a)))
        pill(d, W / 2, 1790, 'SOUTH', 64, (30, 90, 170), alpha=a)
        ptext(d, (W / 2, 220), 'BEFORE SUNRISE', 104, WHITE, t, s0, st('which') + 0.1)
        ptext(d, (W / 2, 350), 'THIS WEEK', 104, GOLD, t, s0 + 0.5, st('which') + 0.1)
        ptext(d, (W / 2 + 230, 1230), 'LOOK HIGH', 74, WHITE, t, s0 + 2.0, st('which') + 0.1)

    # ============ WHICH: Jupiter bright, Mars orange
    a = xf(t, st('which'), st('pinky') + 0.1, 0.25, 0.2)
    if a > 0:
        s0 = st('which'); z = 1 + 0.05 * (t - s0)
        (jx, jy), (mx, my) = pair(im, W / 2, 1000, 260 * z, 1.8 * z, a, jb=1.0 + 0.15 * math.sin(t * 5), tw=t)
        d = ImageDraw.Draw(im, 'RGBA')
        aj = ease(ramp(t, s0, s0 + 0.3)) * a; am = ease(ramp(t, s0 + 1.8, s0 + 2.1)) * a
        d.line((jx + 40, jy + 40, jx + 120, jy + 260), fill=JUPC + (int(220 * aj),), width=5)
        text(d, (jx + 120, jy + 320), 'JUPITER', 100, GOLD, alpha=aj)
        d.line((mx - 30, my - 30, mx - 90, my - 220), fill=MARSC + (int(220 * am),), width=5)
        text(d, (mx - 70, my - 290), 'MARS', 110, ORANGE, alpha=am)
        ptext(d, (W / 2, 300), 'BRIGHT ONE UP HIGH', 66, WHITE, t, s0, s0 + 1.9)
        ptext(d, (W / 2, 300), 'ORANGE DOT NEXT TO IT', 66, WHITE, t, s0 + 1.9, st('pinky') + 0.1)
        ground(d, int(255 * a))

    # ============ PINKY: barely more than a pinky's width (1.2 deg)
    a = xf(t, st('pinky'), st('illusion') + 0.05, 0.2, 0.2)
    if a > 0:
        s0 = st('pinky')
        pair(im, W / 2, 760, 84, 1.0, a, tw=t)   # 84 px gap scale: pinky 86 px ~ 1 deg; gap 1.23*84 = 103 px ~ 1.2 deg
        d = ImageDraw.Draw(im, 'RGBA')
        up = ease(ramp(t, s0, s0 + 0.6))
        hand(d, W / 2 + 120, 780 + 900 * (1 - up), a)
        ptext(d, (W / 2, 260), 'BARELY MORE THAN', 90, WHITE, t, s0, st('illusion') + 0.05)
        ptext(d, (W / 2, 400), 'A PINKY APART', 130, GOLD, t, s0 + 0.5, st('illusion') + 0.05)
        text(d, (W / 2, 520), '(about 1° at arm\'s length)', 48, GREY, POP_M, stroke=4, alpha=a * ease(ramp(t, s0 + 1.0, s0 + 1.4)))

    # ============ ILLUSION -> side view with distances (to scale)
    a = xf(t, st('illusion'), st('reveal') + 0.1, 0.2, 0.25)
    if a > 0:
        s0 = st('illusion')
        sm = 1.0; sj = 1.0
        sideview(im, t, a * ease(ramp(t, s0 + 0.5, s0 + 1.2)), sm, sj)
        d = ImageDraw.Draw(im, 'RGBA')
        if t < st('marsd'):
            ptext(d, (W / 2, 420), "IT'S AN", 120, WHITE, t, s0, st('marsd'))
            ptext(d, (W / 2, 570), 'ILLUSION', 170, RED, t, s0 + 0.15, st('marsd'))
            ptext(d, (W / 2, 1450), 'NOT CLOSE AT ALL', 80, WHITE, t, s0 + 1.1, st('marsd'))
        # distance bars
        m0 = st('marsd'); j0 = st('jupd'); g0 = st('gap')
        if t >= m0 and t < st('tease'):
            pm = ease(ramp(t, m0, m0 + 0.9))
            bar(d, EX, EX + (MX - EX) * pm, SY - 110, CYAN, a)
            if t < j0:
                ptext(d, (W / 2, 380), '121 MILLION', 140, CYAN, t, m0 + 0.2, j0)
                ptext(d, (W / 2, 520), 'MILES TO MARS', 90, WHITE, t, m0 + 0.4, j0)
                text(d, (W / 2, 620), '(195 million km)', 48, GREY, POP_M, stroke=4, alpha=a * ease(ramp(t, m0 + 0.6, m0 + 1)))
            if t >= j0:
                pj = ease(ramp(t, j0, j0 + 1.2))
                bar(d, EX, EX + (JX - EX) * pj, SY - 150, GOLD, a)
                if t < g0:
                    ptext(d, (W / 2, 360), '4× FARTHER', 150, GOLD, t, j0 + 0.1, g0)
                    ptext(d, (W / 2, 520), '489 MILLION MILES', 84, WHITE, t, j0 + 1.6, g0)
                    text(d, (W / 2, 610), '(787 million km)', 48, GREY, POP_M, stroke=4, alpha=a * ease(ramp(t, j0 + 1.8, j0 + 2.2)))
            if t >= g0:
                pg = ease(ramp(t, g0 + 0.3, g0 + 1.2))
                bk = (255, 90, 90, int(255 * a))
                y_ = SY + 190
                d.line((MX, y_, MX + (JX - MX) * pg, y_), fill=bk, width=8)
                d.line((MX, y_ - 24, MX, y_ + 24), fill=bk, width=8)
                if pg > 0.98: d.line((JX, y_ - 24, JX, y_ + 24), fill=bk, width=8)
                ptext(d, (W / 2, 360), 'THE GAP:', 110, WHITE, t, g0, st('tease'))
                ptext(d, (W / 2, 510), '368 MILLION MILES', 96, RED, t, g0 + 1.2, st('tease'))
                # 4 x Earth-Sun units (to the same scale as the gap)
                ua = ease(ramp(t, g0 + 4.0, g0 + 4.5)) * a
                if ua > 0:
                    unit = (JX - MX) / 3.96
                    for k_ in range(4):
                        x0 = MX + unit * k_ * ease(ramp(t, g0 + 4.0 + 0.3 * k_, g0 + 4.3 + 0.3 * k_))
                        paste_c(im, glow(30, (255, 220, 120), 1.2), x0 + unit, y_ + 110, ua)
                        paste_c(im, earth(9), x0, y_ + 110, ua)
                        d = ImageDraw.Draw(im, 'RGBA')
                        d.line((x0 + 12, y_ + 110, x0 + unit - 14, y_ + 110), fill=(255, 220, 120, int(200 * ua)), width=4)
                    text(d, (W / 2, 1470), '≈ 4× EARTH → SUN', 76, GOLD, alpha=ua)
        # tease: shake + flash text
        if st('tease') <= t < st('light'):
            ptext(d, (W / 2, 470), "HERE'S THE", 120, WHITE, t, st('tease'), st('light'))
            ptext(d, (W / 2, 620), 'CRAZY PART', 150, RED, t, st('tease') + 0.2, st('light'))
        # light travel
        for key, x_, mins, col in (('light', MX, 11, ORANGE), ('light2', JX, 44, GOLD)):
            if st(key) <= t < nx(key):
                s1 = st(key); p = ramp(t, s1 + 0.4, nx(key) - 0.4)
                lx = x_ + (EX - x_) * p
                lightpulse(im, lx, SY, col, a)
                d = ImageDraw.Draw(im, 'RGBA')
                d.line((lx, SY, x_, SY), fill=col + (int(120 * a),), width=6)
                ptext(d, (W / 2, 360), 'LIGHT FROM ' + ('MARS' if key == 'light' else 'JUPITER'), 84, WHITE, t, s1, nx(key))
                ptext(d, (W / 2, 520), f'{mins} MIN AGO', 160, col, t, s1 + 0.9, nx(key))
                text(d, (W / 2, 1450), f'{int(mins * p):d} min', 80, WHITE, POP_B, stroke=5, alpha=a)

    # ============ REVEAL: two moments in time, side by side
    a = xf(t, st('reveal') - 0.05, st('size') + 0.1, 0.12, 0.25)
    if a > 0:
        s0 = st('reveal')
        flash = 1 - ease(ramp(t, s0, s0 + 0.25))
        (jx, jy), (mx, my) = pair(im, W / 2, 1000, 300, 2.0, a, tw=t)
        d = ImageDraw.Draw(im, 'RGBA')
        pill(d, mx - 30, my - 170, '11 MIN AGO', 56, (190, 80, 30), alpha=a * ease(ramp(t, s0 + 0.3, s0 + 0.6)))
        pill(d, jx + 10, jy + 200, '44 MIN AGO', 56, (150, 120, 40), alpha=a * ease(ramp(t, s0 + 0.6, s0 + 0.9)))
        ptext(d, (W / 2, 290), '2 MOMENTS', 140, WHITE, t, s0 + 0.1, st('size') + 0.1)
        ptext(d, (W / 2, 430), 'IN TIME', 120, GOLD, t, s0 + 0.4, st('size') + 0.1)
        ptext(d, (W / 2, 1400), 'SIDE BY SIDE', 110, WHITE, t, s0 + 2.0, st('size') + 0.1)
        ground(d, int(255 * a))
        if flash > 0: im.alpha_composite(Image.new('RGBA', (W, H), (255, 240, 220, int(150 * flash * a))))

    # ============ SIZE: 21x wider, ~8,800 Mars inside
    a = xf(t, st('size'), st('bright') + 0.1, 0.2, 0.25)
    if a > 0:
        s0 = st('size'); RJ = 370
        paste_c(im, glow(int(RJ * 2.7), (255, 220, 170), 2.2), W / 2, 1060, a * 0.5)
        paste_c(im, jupiter_sprite(RJ), W / 2, 1060, a)
        mr = RJ / 21.05
        d = ImageDraw.Draw(im, 'RGBA')
        sz_end = s0 + 3.3
        if t < sz_end:
            mx_ = W / 2 + RJ + 40 * (1 - ease(ramp(t, s0, s0 + 0.5)))
            paste_c(im, marsball(int(mr)), W / 2 - RJ - 60, 1060, a)
            d = ImageDraw.Draw(im, 'RGBA')
            label(d, W / 2 - RJ - 60, 1060 + 50, 'MARS', 34, ORANGE, a)
            ptext(d, (W / 2, 330), '21× WIDER', 150, GOLD, t, s0 + 0.8, sz_end + 0.2)
            ptext(d, (W / 2, 470), 'THAN MARS', 100, WHITE, t, s0 + 1.1, sz_end + 0.2)
        else:
            # fill Jupiter's disk with Mars-sized dots (a real count would be ~8,800 by volume; the 2D fill is illustrative)
            p = ease(ramp(t, sz_end, nx('size') - 1.6))
            rows = int((2 * RJ) / (2 * mr)); n_ = 0
            for i in range(rows + 1):
                yv = 1060 - RJ + i * 2 * mr + mr
                half = math.sqrt(max(0, RJ ** 2 - (yv - 1060) ** 2))
                cols = int(2 * half / (2 * mr))
                for j in range(cols):
                    if (i * 37 + j * 11) % 100 / 100 > p: continue
                    xv = W / 2 - half + j * 2 * mr + mr
                    d.ellipse((xv - mr * 0.9, yv - mr * 0.9, xv + mr * 0.9, yv + mr * 0.9), fill=(220, 100, 50, int(230 * a)))
            cnt = int(8800 * p)
            ptext(d, (W / 2, 300), f'≈ {cnt:,}', 170, ORANGE, t, sz_end, nx('size') + 0.1)
            ptext(d, (W / 2, 450), 'MARS FIT INSIDE', 100, WHITE, t, sz_end + 0.2, nx('size') + 0.1)
            text(d, (W / 2, 1450), 'by volume', 44, GREY, POP_M, stroke=4, alpha=a)

    # ============ BRIGHT: farther, still brighter
    a = xf(t, st('bright'), st('share') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('bright')
        pair(im, W / 2, 1000, 260, 1.8, a, jb=1.0 + 0.35 * ease(ramp(t, s0 + 1.5, s0 + 2.2)), tw=t)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 300), '4× FARTHER', 130, WHITE, t, s0, st('share') + 0.1)
        ptext(d, (W / 2, 450), '…STILL', 110, WHITE, t, s0 + 1.4, st('share') + 0.1)
        ptext(d, (W / 2, 1380), '≈ 12× BRIGHTER', 120, GOLD, t, s0 + 2.0, st('share') + 0.1)
        ground(d, int(255 * a))

    # ============ SHARE
    a = xf(t, st('share'), st('comment') + 0.1, 0.2, 0.2)
    if a > 0:
        s0 = st('share')
        pair(im, W / 2, 1150, 150, 1.25, a, tw=t)
        d = ImageDraw.Draw(im, 'RGBA'); ground(d, int(255 * a))
        ptext(d, (W / 2, 330), 'SEND THIS TO', 120, WHITE, t, s0, st('comment') + 0.1)
        ptext(d, (W / 2, 470), "SOMEONE WHO'S UP", 96, WHITE, t, s0 + 0.4, st('comment') + 0.1)
        ptext(d, (W / 2, 610), 'BEFORE SUNRISE', 120, GOLD, t, s0 + 0.8, st('comment') + 0.1)

    # ============ COMMENT (ends on the opening image so the loop is seamless)
    a = xf(t, st('comment'), TOTAL + 1, 0.2, 0.01)
    if a > 0:
        s0 = st('comment'); z = 1.0 + 0.08 * max(0, t - (TOTAL - 1.5))
        pair(im, W / 2, 1020, 210, 1.6, a, tw=t)
        d = ImageDraw.Draw(im, 'RGBA'); ground(d, int(255 * a))
        ptext(d, (W / 2, 330), 'GOING OUT', 130, WHITE, t, s0, TOTAL + 1)
        ptext(d, (W / 2, 480), 'TO LOOK?', 130, GOLD, t, s0 + 0.3, TOTAL + 1)
        pa = ease(ramp(t, s0 + 1.6, s0 + 1.9)) * a
        pill(d, 330, 1330, 'YES', 90, (40, 150, 70), alpha=pa)
        pill(d, 750, 1330, 'NO', 90, (190, 60, 50), alpha=pa)
        text(d, (W / 2, 1470), 'COMMENT ↓', 70, WHITE, alpha=pa)

    return im.convert('RGB')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{float(tt):05.2f}.jpg', quality=88)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3]); n = int(round(TOTAL * FPS))
        b = min(b, n); tmp = f'part_{a:05d}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'part_{a:05d}.mp4')
        print('rendered', a, b, rc)

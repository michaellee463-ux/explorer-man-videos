from base import *

ORANGE = (255, 150, 60)
rng2 = np.random.default_rng(21)

# ---------------------------------------------------------------- sprites
def cube_sprite(s):
    """isometric sugar cube, edge s px: three faces with crystalline sparkle texture"""
    def mk():
        n = int(s * 2.2); img = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        cx, cy = n / 2, n / 2
        c30, s30 = math.cos(math.pi / 6) * s, math.sin(math.pi / 6) * s
        top = [(cx, cy - s), (cx + c30, cy - s + s30), (cx, cy - s + 2 * s30), (cx - c30, cy - s + s30)]
        left = [(cx - c30, cy - s + s30), (cx, cy - s + 2 * s30), (cx, cy + 2 * s30 - s + s), (cx - c30, cy + s30 - s + s)]
        right = [(cx + c30, cy - s + s30), (cx, cy - s + 2 * s30), (cx, cy + 2 * s30 - s + s), (cx + c30, cy + s30 - s + s)]
        d.polygon(top, fill=(252, 250, 244, 255)); d.polygon(left, fill=(222, 220, 214, 255)); d.polygon(right, fill=(194, 192, 188, 255))
        arr = np.array(img).astype(np.float32)
        a = arr[..., 3] > 0
        rg = np.random.default_rng(4)
        noise = rg.random(arr.shape[:2]) * 26 - 13
        arr[..., :3][a] += noise[a][:, None]
        sparkle = (rg.random(arr.shape[:2]) > 0.992) & a
        arr[..., :3][sparkle] = 255
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
        d = ImageDraw.Draw(img)
        for poly in (top, left, right):
            d.line(poly + [poly[0]], fill=(255, 255, 255, 140), width=max(1, int(s / 60)))
        return img
    return sp(('cube', s), mk)

def draw_cube(im, cx, cy, s, alpha=1.0, glowc=(255, 230, 170), g=0.6):
    if alpha <= 0.004: return
    if g > 0: paste_c(im, glow(int(s * 2.2), glowc, 1.8), cx, cy, alpha * g)
    paste_c(im, cube_sprite(max(4, int(s))), cx, cy, alpha)

def person(d, x, y, h, col, a=255):
    """simple human silhouette, feet at (x,y), height h"""
    hr = h * 0.11
    d.ellipse((x - hr, y - h, x + hr, y - h + 2 * hr), fill=col + (a,))
    bw = h * 0.17
    d.rounded_rectangle((x - bw, y - h + 2.2 * hr, x + bw, y - h * 0.42), int(bw * 0.6), fill=col + (a,))
    lw = h * 0.07
    d.rectangle((x - bw * 0.85, y - h * 0.46, x - bw * 0.85 + 2 * lw, y), fill=col + (a,))
    d.rectangle((x + bw * 0.85 - 2 * lw, y - h * 0.46, x + bw * 0.85, y), fill=col + (a,))

def person_sprite(h, col):
    def mk():
        img = Image.new('RGBA', (int(h * 0.6) + 4, int(h) + 4), (0, 0, 0, 0))
        person(ImageDraw.Draw(img), img.width / 2, h + 2, h, col); return img
    return sp(('person', h, col), mk)

STREAM = [(rng2.uniform(0, 2 * math.pi), rng2.uniform(0, 1), rng2.uniform(0.6, 1.4), rng2.integers(0, 3)) for _ in range(260)]
PCOLS = [(255, 205, 90), (90, 215, 255), (255, 255, 255)]
def crowd_stream(im, t, cx, cy, alpha, R0=900, speed=0.35):
    """tiny people spiralling into the point (cx,cy)"""
    if alpha <= 0.01: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for ang, ph, sc, ci in STREAM:
        p = (ph + t * speed * sc) % 1.0           # 0 = far, 1 = absorbed
        r = R0 * (1 - p) ** 1.3 + 30
        a = ang + 2.2 * p
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 1.15
        h = 10 + 46 * (1 - p) * sc
        person(d, x, y + h / 2, h, PCOLS[ci], int(230 * min(1, p * 6) * min(1, (1 - p) * 8)))
    im.alpha_composite(fade(lay, alpha))

def esb_icon(d, x, y, h, col, a=255):
    """Empire State Building silhouette, base centre (x,y)"""
    w = h * 0.36; c = col + (a,)
    d.rectangle((x - w / 2, y - h * 0.55, x + w / 2, y), fill=c)
    d.rectangle((x - w * 0.36, y - h * 0.72, x + w * 0.36, y - h * 0.55), fill=c)
    d.rectangle((x - w * 0.24, y - h * 0.84, x + w * 0.24, y - h * 0.72), fill=c)
    d.rectangle((x - w * 0.13, y - h * 0.93, x + w * 0.13, y - h * 0.84), fill=c)
    d.line((x, y - h * 0.93, x, y - h), fill=c, width=max(1, int(h * 0.03)))

def nstar(R):
    def mk():
        s = sphere(R, (0.75, 0.85, 1.0), 9, rough=0.15)
        return s
    return sp(('ns', R), mk)

def skyline(d, x0, x1, ybase, hmax, col, a):
    rg = np.random.default_rng(3); x = x0
    while x < x1:
        w = rg.uniform(26, 60); h = rg.uniform(0.25, 1) * hmax
        d.rectangle((x, ybase - h, min(x1, x + w), ybase), fill=col + (a,))
        if rg.random() > 0.6: d.line((x + w / 2, ybase - h, x + w / 2, ybase - h - 25), fill=col + (a,), width=3)
        x += w + rg.uniform(2, 10)

def atom(im, t, cx, cy, R, alpha, zoom_nuc=0.0):
    """electron cloud + 3 orbits + nucleus"""
    if alpha <= 0.01: return
    paste_c(im, glow(int(R * 1.15), (70, 140, 255), 1.4), cx, cy, alpha * 0.55)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(3):
        ang = k * math.pi / 3 + 0.3
        pts = []
        for i in range(73):
            q = 2 * math.pi * i / 72
            ex, ey = R * math.cos(q), R * 0.32 * math.sin(q)
            pts.append((cx + ex * math.cos(ang) - ey * math.sin(ang), cy + ex * math.sin(ang) + ey * math.cos(ang)))
        d.line(pts, fill=(120, 190, 255, int(150 * alpha)), width=4)
        q = t * (2.4 + k * 0.7) + k * 2
        ex, ey = R * math.cos(q), R * 0.32 * math.sin(q)
        px, py = cx + ex * math.cos(ang) - ey * math.sin(ang), cy + ex * math.sin(ang) + ey * math.cos(ang)
        d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=(140, 220, 255, int(255 * alpha)))
    im.alpha_composite(lay)
    paste_c(im, glow(60, (255, 190, 90), 1.5), cx, cy, alpha)
    d = ImageDraw.Draw(im, 'RGBA')
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(255, 200, 100, int(255 * alpha)))

def stadium(im, cx, cy, Rw, alpha):
    if alpha <= 0.01: return
    d = ImageDraw.Draw(im, 'RGBA'); a = int(255 * alpha)
    d.ellipse((cx - Rw, cy - Rw * 0.72, cx + Rw, cy + Rw * 0.72), fill=(70, 74, 88, a))
    for k in range(9):
        f = 1 - k * 0.035
        d.ellipse((cx - Rw * f, cy - Rw * 0.72 * f, cx + Rw * f, cy + Rw * 0.72 * f), outline=(100 + k * 6, 104 + k * 6, 120 + k * 6, a), width=5)
    fw, fh = Rw * 0.58, Rw * 0.36
    d.rounded_rectangle((cx - fw, cy - fh, cx + fw, cy + fh), 40, fill=(40, 125, 60, a))
    for i in range(-5, 6):
        d.rectangle((cx + i * fw / 5.5 - fw / 11, cy - fh, cx + i * fw / 5.5, cy + fh), fill=(48, 140, 68, a)) if i % 2 == 0 else None
    d.rounded_rectangle((cx - fw, cy - fh, cx + fw, cy + fh), 40, outline=(230, 240, 230, a), width=4)
    d.line((cx, cy - fh, cx, cy + fh), fill=(230, 240, 230, a), width=4)
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), outline=(230, 240, 230, a), width=4)

def pea(im, cx, cy, r, alpha):
    if alpha <= 0.01: return
    s = sp(('pea', r), lambda: sphere(r, (0.35, 0.75, 0.25), 2, rough=0.1))
    paste_c(im, s, cx, cy, alpha)

_ys = np.arange(H, dtype=np.float32)
_band = np.clip(1 - np.abs(_ys - 380) / 260, 0, 1) ** 0.7 + np.clip(1 - np.abs(_ys - 1610) / 220, 0, 1) ** 0.7
BAND = Image.fromarray(np.repeat((np.clip(_band, 0, 1) * 200).astype(np.uint8)[:, None], W, 1), 'L')
def darkband(im, a):
    if a > 0.01: im.paste((2, 3, 10), (0, 0), BAND.point(lambda v: int(v * a)))

def label(d, x, y, s, size, col, alpha, anchor='mm'):
    text(d, (x, y), s, size, col, POP_B, anchor=anchor, stroke=4, alpha=alpha)

def counter(d, xy, n, size, col, alpha):
    text(d, xy, f'{int(n):,}', size, col, BLACK, alpha=alpha)

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy()
    # gentle drift on the starfield: shift with time for constant motion
    im = im.transform(im.size, Image.AFFINE, (1, 0, (t * 6) % 40, 0, 1, (t * 3) % 40), resample=Image.NEAREST) if False else im
    d = ImageDraw.Draw(im, 'RGBA')

    # ============ hook: people streaming into a sugar cube; claim already on screen at frame 0
    a_h = xf(t, -1, nx('setup') - 0.1, 0.01, 0.35) * (1 if t < st('setup') else 1)
    if t < st('setup') + 0.1:
        a = 1 - ease(ramp(t, st('setup') - 0.15, st('setup') + 0.1))
        sc = 1 + 0.06 * t
        crowd_stream(im, t + 2.0, W / 2, 1060, a)
        darkband(im, a)
        draw_cube(im, W / 2, 1060, 210 * sc, a, g=0.7 + 0.2 * math.sin(t * 6))
        d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 300), 'ALL 8 BILLION', 132, WHITE, alpha=a)
        text(d, (W / 2, 450), 'HUMANS', 150, GOLD, alpha=a)
        text(d, (W / 2, 1530), 'FIT IN THIS', 150, WHITE, alpha=a)
        text(d, (W / 2, 1690), 'ONE SUGAR CUBE', 96, CYAN, alpha=a * ease(ramp(t, 1.6, 1.9)))

    # ============ setup: crowd + counter
    a_s = xf(t, st('setup') - 0.1, nx('setup') + 0.15, 0.25, 0.3)
    if a_s > 0:
        s0 = st('setup')
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        rg = np.random.default_rng(8)
        for row in range(14):
            y = 760 + row * 62; hh = 34 + row * 7
            for i in range(26):
                x = (i * 46 + row * 23 + t * 30 * (1 if row % 2 else -1)) % (W + 80) - 40
                person(dl, x + rg.uniform(-8, 8), y + hh, hh, PCOLS[(i + row) % 3], int(200 * a_s))
        im.alpha_composite(lay)
        d = ImageDraw.Draw(im, 'RGBA')
        counter(d, (W / 2, 330), 8_000_000_000 * ease(ramp(t, s0, s0 + 2.2)), 120, GOLD, a_s)
        ptext(d, (W / 2, 470), 'PEOPLE', 110, WHITE, t, s0 + 0.2, nx('setup') + 0.15)
        ptext(d, (W / 2, 1700), 'IMPOSSIBLE?', 140, CYAN, t, s0 + 2.6, nx('setup') + 0.15)

    # ============ atoms: zoom from a person into an atom
    a_a = xf(t, st('atoms') - 0.1, nx('atoms') + 0.1, 0.25, 0.3)
    if a_a > 0:
        s0 = st('atoms'); z = ease(ramp(t, s0, s0 + 1.8))
        if z < 1:
            ph = int(900 * (1 + 6 * z))
            spr = person_sprite(900, (90, 215, 255)).resize((int(ph * 0.6) + 4, ph + 4))
            paste_c(im, spr, W / 2 + 120 * z, 1060 + 800 * z, a_a * (1 - z))
        atom(im, t, W / 2, 1060, 380, a_a * ease(ramp(t, s0 + 0.9, s0 + 1.8)))
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 300), "YOU'RE MADE OF", 90, WHITE, t, s0 + 0.1, nx('atoms') + 0.1)
        ptext(d, (W / 2, 430), 'ATOMS', 170, GOLD, t, s0 + 0.4, nx('atoms') + 0.1)
        ptext(d, (W / 2, 1620), 'ALMOST ALL', 110, WHITE, t, s0 + 2.4, nx('atoms') + 0.1)
        ptext(d, (W / 2, 1760), 'EMPTY SPACE', 130, CYAN, t, s0 + 2.8, nx('atoms') + 0.1)
        label(d, W / 2 + 230, 1060 - 250, 'electrons', 44, CYAN, a_a * ease(ramp(t, s0 + 4.0, s0 + 4.4)))

    # ============ stadium: atom = stadium, nucleus = pea (magnified inset)
    a_st = xf(t, st('stadium') - 0.1, nx('stadium') + 0.1, 0.25, 0.3)
    if a_st > 0:
        s0 = st('stadium')
        stadium(im, W / 2, 1000, 470 * (0.92 + 0.08 * ease(ramp(t, s0, s0 + 3))), a_st)
        d = ImageDraw.Draw(im, 'RGBA')
        ap = ease(ramp(t, s0 + 2.0, s0 + 2.5)) * a_st
        if ap > 0:
            d.ellipse((W / 2 - 4, 1000 - 4, W / 2 + 4, 1000 + 4), fill=(140, 230, 90, int(255 * ap)))
            d.line((W / 2, 1000, 820, 1420), fill=(255, 255, 255, int(200 * ap)), width=4)
            d.ellipse((820 - 150, 1420 - 150, 820 + 150, 1420 + 150), fill=(14, 18, 34, int(240 * ap)), outline=(255, 255, 255, int(230 * ap)), width=6)
            pea(im, 820, 1420, 70, ap)
            d = ImageDraw.Draw(im, 'RGBA')
            label(d, 820, 1610, 'NUCLEUS = A PEA', 50, GOLD, ap)
            label(d, 820, 1665, '(magnified)', 38, GREY, ap)
        ptext(d, (W / 2, 290), 'IF AN ATOM WERE', 92, WHITE, t, s0, nx('stadium') + 0.1)
        ptext(d, (W / 2, 420), 'A STADIUM...', 140, GOLD, t, s0 + 0.5, nx('stadium') + 0.1)

    # ============ mass: the pea holds > 99.9% of the mass
    a_m = xf(t, st('mass') - 0.1, nx('mass') + 0.1, 0.25, 0.3)
    if a_m > 0:
        s0 = st('mass')
        paste_c(im, glow(520, (140, 255, 120), 1.6), W / 2, 1050, a_m * (0.5 + 0.2 * math.sin(t * 5)))
        pea(im, W / 2, 1050, int(160 * (0.85 + 0.15 * ease(ramp(t, s0, s0 + 1)))), a_m)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 340), 'THAT TINY PEA HOLDS', 80, WHITE, t, s0 + 0.2, nx('mass') + 0.1)
        ptext(d, (W / 2, 560), '>99.9%', 260, GOLD, t, s0 + 1.6, nx('mass') + 0.1)
        ptext(d, (W / 2, 1600), "OF THE ATOM'S MASS", 92, CYAN, t, s0 + 3.0, nx('mass') + 0.1)

    # ============ squeeze: person collapses into a dot
    a_q = xf(t, st('squeeze') - 0.1, nx('speck') + 0.1, 0.25, 0.3)
    if a_q > 0:
        s0 = st('squeeze'); q = ease(ramp(t, s0 + 0.6, en('squeeze') + 0.2))
        if q < 0.98:
            ph = int(1000 * (1 - q) + 6)
            spr = person_sprite(1000, (90, 215, 255)).resize((max(2, int(ph * 0.6) + 4), ph + 4))
            paste_c(im, spr, W / 2, 1000, a_q * (1 - q))
            # particles rushing inward
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            for k in range(70):
                an = k * 2.399; r = (700 * (1 - ((t * 0.9 + k * 0.037) % 1)))
                x, y = W / 2 + r * math.cos(an), 1000 + r * math.sin(an)
                dl.line((x, y, x - 30 * math.cos(an), y - 30 * math.sin(an)), fill=(200, 230, 255, int(160 * a_q)), width=3)
            im.alpha_composite(lay)
        d = ImageDraw.Draw(im, 'RGBA')
        if t < st('speck'):
            ptext(d, (W / 2, 300), 'SQUEEZE OUT', 120, WHITE, t, s0 + 0.1, st('speck'))
            ptext(d, (W / 2, 440), 'ALL THE SPACE', 120, CYAN, t, s0 + 0.4, st('speck'))
        # speck vs hair (proportional: hair ~70 um, speck ~8 um)
        sk = st('speck'); ah = ease(ramp(t, sk - 0.2, sk + 0.3)) * a_q
        if ah > 0:
            hx, hw = 360, 420
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            for i in range(hw):
                c = 0.55 + 0.45 * math.sin(math.pi * i / hw)
                dl.line((hx - hw / 2 + i, 600, hx - hw / 2 + i + 60, 1500), fill=(int(120 * c), int(80 * c), int(45 * c), int(255 * ah)), width=1)
            im.alpha_composite(lay)
            d = ImageDraw.Draw(im, 'RGBA')
            paste_c(im, glow(120, (180, 230, 255), 1.5), 820, 1050, ah)
            d.ellipse((820 - 24, 1050 - 24, 820 + 24, 1050 + 24), fill=(220, 240, 255, int(255 * ah)))
            label(d, 390, 1560, 'a human hair', 48, GREY, ah)
            label(d, 820, 1140, 'YOU', 60, GOLD, ah)
            ptext(d, (W / 2, 300), 'YOU → A SPECK', 116, WHITE, t, sk, nx('speck') + 0.1)
            ptext(d, (W / 2, 430), 'THINNER THAN A HAIR', 84, CYAN, t, sk + 0.4, nx('speck') + 0.1)
            label(d, W / 2, 1720, 'magnified · widths to scale', 38, GREY, ah)

    # ============ tease
    a_t = xf(t, st('tease') - 0.05, nx('tease'), 0.12, 0.2)
    if a_t > 0:
        s0 = st('tease')
        sh = 6 * math.sin(t * 60) * (1 - ramp(t, s0, s0 + 0.4))
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2 + sh, 840), "BUT THAT'S", 130, WHITE, t, s0, nx('tease'))
        ptext(d, (W / 2 - sh, 1000), 'NOT THE', 130, WHITE, t, s0 + 0.25, nx('tease'))
        ptext(d, (W / 2 + sh, 1180), 'CRAZY PART', 150, RED, t, s0 + 0.55, nx('tease'))

    # ============ all: Earth, everyone pulled in
    a_e = xf(t, st('all') - 0.05, nx('all') + 0.15, 0.2, 0.3)
    if a_e > 0:
        s0 = st('all')
        paste_c(im, earth(380), W / 2, 1050, a_e)
        crowd_stream(im, t * 1.6, W / 2, 1050, a_e, R0=520, speed=0.5)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 300), 'NOW DO IT TO', 104, WHITE, t, s0, nx('all') + 0.15)
        ptext(d, (W / 2, 440), 'ALL 8 BILLION', 130, GOLD, t, s0 + 0.3, nx('all') + 0.15)

    # ============ reveal: the cube, with a 1 cm scale bar
    a_r = xf(t, st('reveal') - 0.1, nx('lift') + 0.1, 0.2, 0.3)
    if a_r > 0:
        s0 = st('reveal'); g = ease(ramp(t, s0, s0 + 0.5))
        flash = 1 - ramp(t, s0, s0 + 0.5)
        cy0 = 1030
        size = 330 * (0.3 + 0.7 * g) * (1 + 0.015 * math.sin(t * 3))
        if t < st('weight'):
            draw_cube(im, W / 2, cy0, size, a_r, g=0.9)
            d = ImageDraw.Draw(im, 'RGBA')
            # scale bar: cube edge ~ 1.2 cm
            if g > 0.99:
                ab = ease(ramp(t, s0 + 1.0, s0 + 1.5)) * a_r
                d.line((W / 2 - 290, cy0 + 380, W / 2 + 290, cy0 + 380), fill=(255, 255, 255, int(220 * ab)), width=5)
                label(d, W / 2, cy0 + 440, '≈ 1.2 cm wide', 64, WHITE, ab)
            ptext(d, (W / 2, 300), 'EVERY ONE OF US', 104, WHITE, t, s0 + 0.2, st('weight'))
            ptext(d, (W / 2, 1640), 'A SUGAR CUBE', 150, GOLD, t, s0 + 3.2, st('weight'))
        if flash > 0:
            im.alpha_composite(Image.new('RGBA', (W, H), (255, 245, 220, int(170 * flash * a_r))))
        # weight: cube top, ESB grid below
        if t >= st('weight') - 0.05:
            w0 = st('weight'); m = ease(ramp(t, w0, w0 + 0.5))
            draw_cube(im, W / 2, 1030 - 520 * m, size * (1 - 0.45 * m), a_r, g=0.9)
            d = ImageDraw.Draw(im, 'RGBA')
            if t < st('lift'):
                ptext(d, (W / 2, 820), 'WEIGHT ≈', 92, WHITE, t, w0 + 0.3, st('lift'))
                ptext(d, (W / 2, 960), '400 MILLION', 140, GOLD, t, w0 + 0.6, st('lift'))
                ptext(d, (W / 2, 1090), 'TONNES', 120, GOLD, t, w0 + 0.9, st('lift'))
                # >1,000 Empire State Buildings: 40 x 26 = 1,040 icons
                nshow = int(1040 * ease(ramp(t, w0 + 2.6, w0 + 5.0)))
                for i in range(nshow):
                    cx_ = 70 + (i % 40) * 24.0; cy_ = 1240 + (i // 40) * 24.0
                    esb_icon(d, cx_, cy_ + 20, 22, (190, 200, 220), int(255 * a_r))
                if nshow > 0:
                    label(d, W / 2, 1880 + 10, 'Empire State Buildings', 40, WHITE, a_r) if False else None
                    text(d, (W / 2, 1210), '> 1,000 EMPIRE STATE BUILDINGS', 54, CYAN, POP_B, stroke=4, alpha=a_r * ease(ramp(t, w0 + 2.6, w0 + 3.0)))
            else:
                l0 = st('lift')
                cr = ease(ramp(t, l0, l0 + 0.3))
                d.line((0, 1500, W, 1500), fill=(120, 110, 100, int(255 * a_r)), width=6)
                for k in range(7):
                    an = math.pi * (0.15 + 0.7 * k / 6)
                    d.line((W / 2, 1500, W / 2 + 260 * cr * math.cos(an), 1500 + 160 * cr * math.sin(an)), fill=(200, 190, 170, int(255 * a_r)), width=5)
                ptext(d, (W / 2, 900), "YOU COULDN'T", 130, WHITE, t, l0, nx('lift') + 0.1)
                ptext(d, (W / 2, 1060), 'LIFT IT', 170, RED, t, l0 + 0.2, nx('lift') + 0.1)

    # ============ neutron star: Sun's mass, city-sized
    a_n = xf(t, st('neutron') - 0.1, nx('ncube') + 0.1, 0.25, 0.3)
    if a_n > 0:
        s0 = st('neutron')
        R_ = int(300 * (0.9 + 0.1 * ease(ramp(t, s0, s0 + 4))))
        paste_c(im, glow(int(R_ * 2.6), (140, 190, 255), 1.6), W / 2, 980, a_n * (0.75 + 0.15 * math.sin(t * 7)))
        paste_c(im, nstar(R_), W / 2, 980, a_n)
        d = ImageDraw.Draw(im, 'RGBA')
        if t < st('ncube'):
            ab = ease(ramp(t, s0 + 4.0, s0 + 4.6)) * a_n
            skyline(d, W / 2 - 300, W / 2 + 300, 1560, 150, (150, 160, 190), int(255 * ab))
            d.line((W / 2 - 300, 1600, W / 2 + 300, 1600), fill=(255, 255, 255, int(220 * ab)), width=5)
            label(d, W / 2, 1650, 'a city ≈ 20 km', 54, WHITE, ab)
            ptext(d, (W / 2, 290), 'NATURE DOES THIS', 104, WHITE, t, s0 + 0.1, st('ncube'))
            ptext(d, (W / 2, 420), 'NEUTRON STAR', 128, CYAN, t, s0 + 1.2, st('ncube'))
            ptext(d, (W / 2, 1790), "A SUN'S MASS · CITY-SIZED", 64, GOLD, t, s0 + 2.6, st('ncube'))
        else:
            c0 = st('ncube'); m = ease(ramp(t, c0, c0 + 0.5))
            draw_cube(im, W / 2, 1520, 170 * m + 4, a_n * m, glowc=(150, 200, 255), g=0.9)
            d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 290), 'ONE SUGAR CUBE OF IT', 88, WHITE, t, c0 + 0.1, nx('ncube') + 0.1)
            ptext(d, (W / 2, 430), '≈ 1 BILLION', 140, GOLD, t, c0 + 1.4, nx('ncube') + 0.1)
            ptext(d, (W / 2, 560), 'TONNES', 120, GOLD, t, c0 + 1.6, nx('ncube') + 0.1)

    # ============ share
    a_sh = xf(t, st('share') - 0.1, nx('share') + 0.1, 0.2, 0.25)
    if a_sh > 0:
        s0 = st('share')
        draw_cube(im, W / 2, 1300, 200, a_sh, g=0.6)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 480), 'SEND THIS TO', 120, WHITE, t, s0, nx('share') + 0.1)
        ptext(d, (W / 2, 620), 'SOMEONE WHO THINKS', 84, WHITE, t, s0 + 0.4, nx('share') + 0.1)
        ptext(d, (W / 2, 770), "THEY'RE SOLID", 140, GOLD, t, s0 + 0.9, nx('share') + 0.1)

    # ============ comment + loop back to the opening image
    a_c = xf(t, st('comment') - 0.1, TOTAL + 1, 0.2, 0.01)
    if a_c > 0:
        s0 = st('comment')
        crowd_stream(im, t + 2.0, W / 2, 1060, a_c * ease(ramp(t, s0 + 1.5, s0 + 2.5)))
        darkband(im, a_c)
        draw_cube(im, W / 2, 1060, 210, a_c, g=0.7)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 330), 'WHICH BLOWS', 120, WHITE, t, s0, TOTAL + 1)
        ptext(d, (W / 2, 470), 'YOUR MIND?', 120, WHITE, t, s0 + 0.2, TOTAL + 1)
        pa = ease(ramp(t, s0 + 1.5, s0 + 1.8)) * a_c
        pill(d, 250, 1520, 'SIZE', 80, (30, 120, 200), alpha=pa)
        text(d, (462, 1520), 'or', 70, WHITE, POP_B, stroke=4, alpha=pa)
        pill(d, 735, 1520, 'WEIGHT', 80, (200, 60, 50), alpha=pa)
        text(d, (W / 2, 1700), 'COMMENT ↓', 80, GOLD, alpha=pa)

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

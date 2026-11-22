from base import *

ORANGE = (255, 150, 60); ICE = (150, 220, 255); GREEN = (60, 210, 110); PINK = (240, 120, 140)
def dim(im, k):
    if k <= 0: return
    im.alpha_composite(Image.new('RGBA', im.size, (0, 0, 0, int(255 * min(1, k)))))
_TG = {}
def topgrad(im, h=620, a=200):
    if (h, a) not in _TG:
        g = np.zeros((h, W, 4), np.uint8); g[..., 3] = np.linspace(a, 0, h)[:, None].astype(np.uint8); _TG[(h, a)] = Image.fromarray(g, 'RGBA')
    im.alpha_composite(_TG[(h, a)], (0, 0))
_BG2 = {}
def botgrad(im, h=520, a=200):
    if (h, a) not in _BG2:
        g = np.zeros((h, W, 4), np.uint8); g[..., 3] = np.linspace(0, a, h)[:, None].astype(np.uint8); _BG2[(h, a)] = Image.fromarray(g, 'RGBA')
    im.alpha_composite(_BG2[(h, a)], (0, H - h))

BIGEARTH = sphere(700, (0.10, 0.30, 0.75), 3, land=(0.25, 0.55, 0.25), atmo=(0.4, 0.7, 1.0)).resize((2900, 2900), Image.BICUBIC)
EGLOW = glow(1600, (110, 170, 255), 2.4)

# ---------------------------------------------------------------- person without a suit (t-shirt), puff = swelling
def person(s, puff=0.0):
    def mk():
        n = int(s * 3); im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        c = n / 2; w = s * 0.13 * (1 + 0.35 * puff)
        skin = (238, 190, 150, 255); shirt = (40, 120, 220, 255); pants = (40, 45, 70, 255)
        for (ax, ay, col) in ((-0.95, -0.6, skin), (0.95, -0.5, skin)):
            d.line((c, c - 0.25 * s, c + ax * s, c + ay * s), fill=shirt, width=int(w * 1.7))
            d.ellipse((c + ax * s - w, c + ay * s - w, c + ax * s + w, c + ay * s + w), fill=skin)
        for (ax, ay) in ((-0.5, 1.0), (0.55, 0.95)):
            d.line((c, c + 0.25 * s, c + ax * s, c + ay * s), fill=pants, width=int(w * 2.0))
            d.ellipse((c + ax * s - w * 1.1, c + ay * s - w * 0.8, c + ax * s + w * 1.3, c + ay * s + w * 0.8), fill=(30, 30, 35, 255))
        bw = 0.30 * (1 + 0.25 * puff)
        d.rounded_rectangle((c - s * bw, c - s * 0.45, c + s * bw, c + s * 0.38), int(s * 0.16), fill=shirt)
        hr = 0.22 * (1 + 0.22 * puff)
        d.ellipse((c - s * hr, c - s * (0.67 + hr), c + s * hr, c - s * (0.67 - hr)), fill=skin)
        d.chord((c - s * hr, c - s * (0.67 + hr), c + s * hr, c - s * (0.67 - hr)), 180, 360, fill=(70, 45, 30, 255))
        for ex in (-0.08, 0.08):
            d.ellipse((c + (ex - 0.03) * s, c - 0.66 * s, c + (ex + 0.03) * s, c - 0.6 * s), fill=(30, 30, 40, 255))
        d.ellipse((c - 0.06 * s, c - 0.56 * s, c + 0.06 * s, c - 0.49 * s), fill=(120, 40, 50, 255))
        return im
    return sp(('person', int(s), round(puff, 2)), mk)

def spun(spr, ang):
    return spr.rotate(ang, resample=Image.BILINEAR, expand=False)

def astro(s):
    def mk():
        n = int(s * 3); im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        c = n / 2; w = s * 0.16; body = (235, 238, 245, 255)
        for (ax, ay) in ((-0.7, 0.2), (0.7, 0.2), (-0.3, 1.0), (0.3, 1.0)):
            d.line((c, c + (0.15 if ay > 0.5 else -0.15) * s, c + ax * s, c + ay * s), fill=body, width=int(w * 1.6))
            d.ellipse((c + ax * s - w, c + ay * s - w, c + ax * s + w, c + ay * s + w), fill=body)
        d.rounded_rectangle((c - s * 0.28, c - s * 0.45, c + s * 0.28, c + s * 0.45), int(s * 0.18), fill=body)
        d.ellipse((c - s * 0.26, c - s * 0.92, c + s * 0.26, c - s * 0.4), fill=body)
        d.ellipse((c - s * 0.18, c - s * 0.8, c + s * 0.18, c - s * 0.52), fill=(255, 190, 80, 255))
        return im
    return sp(('astro', int(s)), mk)

def timer_ring(d, cx, cy, r, frac, col, a=1.0, width=22):
    if a <= 0.01: return
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, int(60 * a)), width=width)
    if frac > 0:
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frac, fill=col + (int(255 * a),), width=width)

def bubbles(d, cx, cy, wid, t, n, a, col=(220, 240, 255), seed=3, rise=260, size=(8, 26)):
    rg = np.random.default_rng(seed)
    for i in range(n):
        x0 = cx + rg.uniform(-wid / 2, wid / 2); ph = rg.uniform(0, 1); spd = rg.uniform(0.6, 1.4); r = rg.uniform(*size)
        p = (ph + t * spd * 0.9) % 1
        y = cy - p * rise; x = x0 + 10 * math.sin(t * 4 + i)
        al = a * (1 - p) * 0.95
        d.ellipse((x - r, y - r, x + r, y + r), outline=col + (int(255 * al),), width=4)
        d.ellipse((x - r * 0.45, y - r * 0.6, x - r * 0.1, y - r * 0.25), fill=(255, 255, 255, int(200 * al)))

def hook_scene(im, t, a=1.0, puff=0.0, py=930):
    """person tumbling above Earth's limb"""
    paste_c(im, EGLOW, 540, 2420, 0.45 * a)
    paste_c(im, BIGEARTH, 540, 2550 - 8 * math.sin(t * 0.4), a)
    s = 170
    paste_c(im, spun(person(s, puff), 12 * math.sin(t * 0.9) + t * 9), 540 + 30 * math.sin(t * 0.7), py + 18 * math.sin(t * 1.1), a)

def stamp(d, cx, cy, s, size, col, t, a0, ang=-8):
    al = ease(ramp(t, a0, a0 + 0.15))
    if al <= 0: return
    sc = 1.6 - 0.6 * ease(ramp(t, a0, a0 + 0.18))
    f = F(BLACK, int(size * sc)); w = f.getlength(s) + 60; h = size * sc * 1.5
    lay = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((20, 20, 20 + w, 20 + h), 26, outline=col + (255,), width=14)
    ld.text((20 + w / 2, 20 + h / 2), s, font=f, fill=col + (255,), anchor='mm')
    lay = lay.rotate(ang, expand=True, resample=Image.BILINEAR)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * al)))
    d._image.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im, 'RGBA')

    # ============ HOOK / MYTH / SKIN: you, no suit, above Earth
    a = xf(t, -1, st('armstrong') + 0.25, 0.01, 0.35)
    if a > 0:
        puff = 0.9 * ease(ramp(t, st('skin') + 1.6, st('skin') + 3.2))
        hook_scene(im, t, a, puff); d = ImageDraw.Draw(im, 'RGBA')
        topgrad(im, 760, 215); d = ImageDraw.Draw(im, 'RGBA')
        if t < st('myth'):
            frac = 1 - 0.25 * ramp(t, 0, st('myth'))
            timer_ring(d, 540, 930, 330, frac, RED, a)
            ptext(d, (W / 2, 200), 'NO SPACESUIT?', 104, WHITE, t, -1, st('myth') + 0.05)
            ptext(d, (W / 2, 350), 'UNDER 15 SECONDS', 100, GOLD, t, -1, st('myth') + 0.05)
            pill(d, W / 2, 1520, 'THEN YOU BLACK OUT', 62, (205, 30, 40), alpha=a * ease(ramp(t, 1.4, 1.7)))
        elif t < st('skin'):
            ptext(d, (W / 2, 220), 'YOU EXPLODE?', 130, WHITE, t, st('myth'), st('skin'))
            stamp(d, 540, 1450, 'MYTH', 150, (235, 40, 50), t, st('myth') + 0.9)
        else:
            ptext(d, (W / 2, 200), 'STRETCHY,', 120, WHITE, t, st('skin') + 0.05, st('skin') + 1.5)
            ptext(d, (W / 2, 350), 'STRONG SKIN', 120, CYAN, t, st('skin') + 0.3, st('skin') + 1.5)
            ptext(d, (W / 2, 200), 'YOU SWELL UP...', 110, WHITE, t, st('skin') + 1.5, st('armstrong'))
            ptext(d, (W / 2, 350), 'BUT HOLD TOGETHER', 88, GREEN, t, st('skin') + 2.9, st('armstrong'))

    # ============ ARMSTRONG + ISS: altitude ladder, drawn to scale
    a = xf(t, st('armstrong') - 0.05, st('saliva') + 0.25, 0.35, 0.35)
    if a > 0:
        # sky gradient
        g0 = 1750
        z = ease(ramp(t, st('iss') - 0.2, st('iss') + 1.6))
        pxkm = 57 * (1 - z) + 3.9 * z          # pixels per km
        sky = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sky)
        for y in range(0, H, 8):
            h_km = (g0 - y) / pxkm
            k = min(1, max(0, h_km / 40)) ** 0.5
            col = (int(70 * (1 - k) + 3 * k), int(130 * (1 - k) + 4 * k), int(210 * (1 - k) + 14 * k))
            sd.rectangle((0, y, W, y + 8), fill=col + (255,))
        im.alpha_composite(fade(sky, a)); d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((0, g0, W, H), fill=(40, 70, 40, int(255 * a)))
        # Everest (8.849 km) to scale
        eh = 8.849 * pxkm
        d.polygon([(180, g0), (430, g0 - eh), (520, g0 - eh * 0.82), (760, g0)], fill=(120, 115, 125, int(255 * a)))
        d.polygon([(430, g0 - eh), (380, g0 - eh * 0.8), (470, g0 - eh * 0.86), (520, g0 - eh * 0.82)], fill=(245, 245, 250, int(255 * a)))
        text(d, (870, g0 - eh * 0.5 if z < 0.5 else g0 - 60), 'EVEREST 8.8 KM' if z < 0.5 else 'EVEREST', 50, WHITE, POP_B, alpha=a)
        # Armstrong limit (19.2 km)
        ay = g0 - 19.2 * pxkm
        d.line((0, ay, W, ay), fill=(255, 205, 90, int(255 * a)), width=7)
        bubbles(d, 540, ay - 10, W, t, 26, a * ease(ramp(t, st('armstrong') + 5.0, st('armstrong') + 5.5)), rise=180, size=(6, 18))
        if z < 0.5:
            text(d, (W / 2, ay - 60), '~19 KM: WATER BOILS AT 37 °C', 58, GOLD, BLACK, alpha=a * ease(ramp(t, st('armstrong') + 2.0, st('armstrong') + 2.4)))
        else:
            text(d, (760, ay - 45), '19 KM', 50, GOLD, BLACK, alpha=a)
        # ISS at 400 km
        if z > 0:
            iy = g0 - 400 * pxkm
            if iy > -100:
                ia = a * ease(ramp(t, st('iss') + 1.2, st('iss') + 1.6))
                d.rectangle((540 - 120, iy - 8, 540 + 120, iy + 8), fill=(220, 220, 230, int(255 * ia)))
                for dx in (-120, 90):
                    d.rectangle((540 + dx, iy - 40, 540 + dx + 30, iy + 40), fill=(60, 90, 170, int(255 * ia)))
                d.rectangle((520, iy - 20, 560, iy + 20), fill=(240, 240, 245, int(255 * ia)))
                text(d, (W / 2, iy + 90), 'SPACE STATION ~400 KM', 62, WHITE, BLACK, alpha=ia)
        topgrad(im, 520, 150 if z < 0.5 else 0); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'ABOVE ~19 KM', 110, WHITE, t, st('armstrong') + 0.2, st('armstrong') + 3.0)
        ptext(d, (W / 2, 200), '2× HIGHER THAN EVEREST', 70, WHITE, t, st('armstrong') + 3.0, st('iss'))
        ptext(d, (W / 2, 330), 'WATER BOILS AT 37 °C', 84, GOLD, t, st('armstrong') + 5.0, st('iss'))
        ptext(d, (W / 2, 560), '20× HIGHER', 150, CYAN, t, st('iss') + 1.8, st('saliva'))

    # ============ SALIVA: tongue close-up, boiling
    a = xf(t, st('saliva') - 0.1, st('lungs') + 0.2, 0.3, 0.3)
    if a > 0:
        dim(im, a * 0.85); d = ImageDraw.Draw(im, 'RGBA')
        k = 0.96 + 0.04 * ease(ramp(t, st('saliva'), st('lungs')))
        cx, cy = 540, 1150
        d.ellipse((cx - 420 * k, cy - 280 * k, cx + 420 * k, cy + 300 * k), fill=(70, 15, 25, int(255 * a)))
        d.ellipse((cx - 330 * k, cy - 120 * k, cx + 330 * k, cy + 260 * k), fill=(225, 105, 120, int(255 * a)))
        d.line((cx, cy - 60, cx, cy + 200), fill=(190, 80, 95, int(255 * a)), width=8)
        boil = ease(ramp(t, st('saliva') + 1.6, st('saliva') + 2.2))
        bubbles(d, cx, cy + 120, 520, t, 40, a * boil, seed=9, rise=420, size=(10, 34))
        topgrad(im, 600, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 230), 'THE SALIVA', 110, WHITE, t, st('saliva') + 0.1, st('lungs'))
        ptext(d, (W / 2, 380), 'ON YOUR TONGUE', 100, WHITE, t, st('saliva') + 0.4, st('lungs'))
        ptext(d, (W / 2, 1650), 'BOILS', 190, ORANGE, t, st('saliva') + 1.6, st('lungs'))

    # ============ LUNGS
    a = xf(t, st('lungs') - 0.1, st('tease') + 0.2, 0.3, 0.3)
    if a > 0:
        dim(im, a * 0.9); d = ImageDraw.Draw(im, 'RGBA')
        ex = ease(ramp(t, st('lungs') + 2.6, st('lungs') + 4.2))
        sc = 1 + 0.35 * ex + 0.03 * math.sin(t * 6)
        for sx in (-1, 1):
            cx = 540 + sx * 190 * sc; cy = 1150
            d.ellipse((cx - 160 * sc, cy - 300 * sc, cx + 160 * sc, cy + 300 * sc), fill=(235, 120, 130, int(240 * a)))
            for j in range(5):
                d.line((540, 870, cx + sx * (j - 2) * 30 * sc, cy + (j - 2) * 80 * sc), fill=(170, 60, 75, int(200 * a)), width=8)
            if ex > 0.6:
                rk = (ex - 0.6) / 0.4
                d.line((cx - 40 * sx, cy - 120, cx + 30 * sx, cy - 30, cx - 20 * sx, cy + 60, cx + 50 * sx, cy + 140), fill=(255, 255, 255, int(255 * a * rk)), width=10)
        d.rectangle((520, 650, 560, 880), fill=(220, 160, 165, int(255 * a)))
        topgrad(im, 600, 210); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 220), "DON'T HOLD", 130, WHITE, t, st('lungs') + 0.4, st('tease'))
        ptext(d, (W / 2, 380), 'YOUR BREATH', 130, RED, t, st('lungs') + 0.7, st('tease'))
        ptext(d, (W / 2, 1700), 'AIR EXPANDS → LUNGS RIP', 70, WHITE, t, st('lungs') + 2.6, st('tease'))

    # ============ TEASE
    a = xf(t, st('tease') - 0.05, st('blackout') + 0.2, 0.15, 0.3)
    if a > 0:
        dim(im, 0.92 * a); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 860), "BUT THAT'S", 130, WHITE, t, st('tease'), st('blackout') + 0.1)
        ptext(d, (W / 2, 1040), 'NOT THE', 130, WHITE, t, st('tease') + 0.2, st('blackout') + 0.1)
        ptext(d, (W / 2, 1230), 'SCARIEST PART...', 112, RED, t, st('tease') + 0.45, st('blackout') + 0.1)

    # ============ BLACKOUT: oxygen countdown, vision fades
    a = xf(t, st('blackout') - 0.1, st('cold') + 0.2, 0.3, 0.3)
    if a > 0:
        hook_scene(im, t, a, 0.9); d = ImageDraw.Draw(im, 'RGBA')
        p = ramp(t, st('blackout') + 0.3, en('blackout'))
        secs = 15 * (1 - p)
        timer_ring(d, 540, 930, 330, 1 - p, RED, a)
        topgrad(im, 600, 210); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'NO OXYGEN', 110, WHITE, t, st('blackout') + 0.1, st('cold'))
        if p < 1:
            ptext(d, (W / 2, 1500), f'{secs:.0f}', 200, GOLD, t, st('blackout') + 0.3, st('cold'))
        # vignette closing in
        v = ease(ramp(p, 0.55, 1.0))
        if v > 0:
            vg = sp('vig', lambda: Image.fromarray((np.clip(np.sqrt(((xx - 540) / 540) ** 2 + ((yy - 960) / 960) ** 2), 0, 1) * 255).astype(np.uint8), 'L'))
            blk = Image.new('RGBA', (W, H), (0, 0, 0, 255)); blk.putalpha(vg.point(lambda q: int(min(255, q * 1.6 * v + 160 * v))))
            im.alpha_composite(blk); d = ImageDraw.Draw(im, 'RGBA')
        if p >= 0.95:
            pill(d, W / 2, 1500, 'BLACKOUT', 96, (205, 30, 40), alpha=a)

    # ============ COLD
    a = xf(t, st('cold') - 0.1, st('leblanc') + 0.2, 0.3, 0.3)
    if a > 0:
        hook_scene(im, t, a, 0.9, py=1050); dim(im, 0.35 * a); d = ImageDraw.Draw(im, 'RGBA')
        topgrad(im, 760, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'DEEP SPACE', 96, WHITE, t, st('cold') + 1.5, en('cold') - 3.2)
        ptext(d, (W / 2, 350), 'ABOUT −270 °C', 118, ICE, t, st('cold') + 1.8, en('cold') - 3.2)
        stamp(d, 540, 1600, 'NO INSTANT FREEZE', 82, ICE, t, st('cold') + 0.2, ang=5)
        ptext(d, (W / 2, 260), 'NO AIR =', 110, WHITE, t, en('cold') - 3.1, st('leblanc'))
        ptext(d, (W / 2, 410), 'HEAT LEAVES SLOWLY', 84, GOLD, t, en('cold') - 2.8, st('leblanc'))

    # ============ LEBLANC: NASA vacuum chamber, 1966
    a = xf(t, st('leblanc') - 0.1, st('reveal') + 0.2, 0.3, 0.3)
    if a > 0:
        dim(im, a); d = ImageDraw.Draw(im, 'RGBA')
        cx, cy = 540, 1150
        d.rounded_rectangle((90, 620, 990, 1720), 120, fill=(95, 102, 115, int(255 * a)), outline=(160, 170, 185, int(255 * a)), width=16)
        for yy_ in (700, 1640):
            d.line((90, yy_, 990, yy_), fill=(70, 75, 88, int(255 * a)), width=10)
        d.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), fill=(20, 25, 40, int(255 * a)), outline=(200, 205, 215, int(255 * a)), width=24)
        for k_ in range(12):
            an = k_ * math.pi / 6; d.ellipse((cx + 360 * math.cos(an) - 16, cy + 360 * math.sin(an) - 16, cx + 360 * math.cos(an) + 16, cy + 360 * math.sin(an) + 16), fill=(180, 185, 195, int(255 * a)))
        pop_t = st('leblanc') + 4.2
        paste_c(im, astro(120), cx - 20, cy + 40, a); d = ImageDraw.Draw(im, 'RGBA')
        hx = cx + 60; hy = cy - 30
        if t < pop_t:
            d.line((hx, hy, cx + 300, cy + 200), fill=(40, 40, 45, int(255 * a)), width=18)
        else:
            q = ease(ramp(t, pop_t, pop_t + 0.4))
            ex_, ey_ = cx + 300 - 120 * q, cy + 200 + 40 * q
            d.line((ex_, ey_, cx + 300, cy + 200), fill=(40, 40, 45, int(255 * a)), width=18)
            for i in range(8):
                r = 30 + 160 * ((t - pop_t) * 1.4 + i / 8) % 1 * 1.0
                d.ellipse((hx - r, hy - r, hx + r, hy + r), outline=(255, 255, 255, int(120 * a * (1 - r / 190))), width=5)
            if t > en('leblanc') - 3.2:
                bubbles(d, cx - 20, cy - 30, 120, t, 14, a, seed=4, rise=160, size=(6, 16))
        topgrad(im, 560, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'NASA, 1966', 120, WHITE, t, st('leblanc') + 0.1, st('reveal'))
        ptext(d, (W / 2, 350), 'VACUUM CHAMBER', 96, CYAN, t, st('leblanc') + 1.4, st('reveal'))
        ptext(d, (W / 2, 1830), 'AIR HOSE POPS OFF', 76, RED, t, pop_t, en('leblanc') - 3.3)
        ptext(d, (W / 2, 1830), 'LAST MEMORY: SALIVA BUBBLING', 58, ORANGE, t, en('leblanc') - 3.2, st('reveal'))

    # ============ REVEAL: 87 seconds, he survived
    a = xf(t, st('reveal') - 0.1, st('rule') + 0.2, 0.25, 0.3)
    if a > 0:
        dim(im, a); d = ImageDraw.Draw(im, 'RGBA')
        p = ease(ramp(t, st('reveal') + 0.2, st('reveal') + 2.2))
        timer_ring(d, 540, 900, 360, p * 87 / 90, GOLD, a, 30)
        text(d, (540, 870), f'{87 * p:.0f}', 260, GOLD, BLACK, alpha=a)
        text(d, (540, 1030), 'SECONDS', 70, WHITE, POP_B, alpha=a)
        ptext(d, (W / 2, 260), 'TO GET THE AIR BACK', 80, WHITE, t, st('reveal') + 0.1, st('rule'))
        ptext(d, (W / 2, 1480), 'HE WOKE UP', 120, WHITE, t, st('reveal') + 3.0, st('rule'))
        ptext(d, (W / 2, 1640), 'NO LASTING HARM', 110, GREEN, t, st('reveal') + 4.0, st('rule'))

    # ============ RULE: ~90 seconds
    a = xf(t, st('rule') - 0.1, st('share') + 0.2, 0.25, 0.3)
    if a > 0:
        dim(im, a); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 330), 'BACK TO AIR', 120, WHITE, t, st('rule') + 0.2, st('share'))
        ptext(d, (W / 2, 490), 'IN ~90 SECONDS?', 100, GOLD, t, st('rule') + 0.9, st('share'))
        p = ease(ramp(t, st('rule') + 0.9, st('rule') + 2.6))
        ba = a * ease(ramp(t, st('rule') + 0.8, st('rule') + 1.0))
        d.rounded_rectangle((110, 1000, 970, 1110), 55, outline=(255, 255, 255, int(200 * ba)), width=8)
        if p > 0: d.rounded_rectangle((122, 1012, 122 + (958 - 122) * p, 1098), 45, fill=GREEN + (int(255 * ba),))
        text(d, (140, 1180), '0 s', 52, GREY, POP_B, stroke=0, alpha=ba); text(d, (930, 1180), '90 s', 52, GREY, POP_B, stroke=0, alpha=ba)
        ptext(d, (W / 2, 1500), 'YOU COULD SURVIVE', 92, GREEN, t, st('rule') + 2.3, st('share'))

    # ============ SHARE + COMMENT, loops back to the opening
    a = xf(t, st('share') - 0.1, TOTAL + 1, 0.3, 0.01)
    if a > 0:
        lp = ramp(t, TOTAL - 0.8, TOTAL)
        hook_scene(im, t, a, 0.9 * (1 - ease(lp))); d = ImageDraw.Draw(im, 'RGBA')
        topgrad(im, 900, 225); d = ImageDraw.Draw(im, 'RGBA')
        ca = 1 - ease(lp)
        ptext(d, (W / 2, 200), 'SEND THIS TO SOMEONE', 78, WHITE, t, st('share'), st('comment'))
        ptext(d, (W / 2, 320), "WHO THINKS YOU'D", 86, WHITE, t, st('share') + 0.2, st('comment'))
        ptext(d, (W / 2, 470), "EXPLODE IN SPACE", 100, GOLD, t, st('share') + 0.5, st('comment'))
        if t >= st('comment'):
            text(d, (W / 2, 230), 'DID YOU THINK', 112, WHITE, BLACK, alpha=ca)
            text(d, (W / 2, 380), "YOU'D EXPLODE?", 108, GOLD, BLACK, alpha=ca)
            pa = ease(ramp(t, st('comment') + 0.7, st('comment') + 1.0)) * ca
            pill(d, 330, 1560, 'YES', 80, (30, 150, 70), alpha=pa)
            pill(d, 750, 1560, 'NO', 80, (205, 30, 40), alpha=pa)
            text(d, (W / 2, 1720), 'COMMENT ↓', 80, GOLD, BLACK, alpha=pa)
        if lp > 0:
            la = ease(lp)
            timer_ring(d, 540, 930, 330, 1.0, RED, la)
            text(d, (W / 2, 200), 'NO SPACESUIT?', 104, WHITE, BLACK, alpha=la)
            text(d, (W / 2, 350), 'UNDER 15 SECONDS', 100, GOLD, BLACK, alpha=la)
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

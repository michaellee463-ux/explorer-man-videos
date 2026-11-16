from base import *

ORANGE = (255, 150, 60)
AU_PX = None

# ---------------------------------------------------------------- sprites
def bh_sprite(R):
    """black hole: black shadow, bright photon ring, orange lensed glow. R = event-horizon radius in px"""
    def mk():
        n = int(R * 5.2) + 8; c = n / 2
        y, x = np.mgrid[0:n, 0:n].astype(np.float32)
        r = np.sqrt((x - c) ** 2 + (y - c) ** 2) / max(R, 1)
        ang = np.arctan2(y - c, x - c)
        arr = np.zeros((n, n, 4), np.float32)
        # warm halo
        halo = np.exp(-((r - 1.35) / 0.55) ** 2) * (r > 1.0) + 0.35 * np.exp(-((r - 1.0) / 1.4) ** 2) * (r > 1.0)
        bright = 0.75 + 0.25 * np.cos(ang - 2.4)  # doppler-ish asymmetry
        halo *= bright
        ring = np.exp(-((r - 1.12) / 0.045) ** 2) * (0.8 + 0.2 * np.cos(ang - 2.4))
        col = np.array([1.0, 0.55, 0.18])[None, None] * halo[..., None] + np.array([1.0, 0.93, 0.75])[None, None] * ring[..., None] * 1.3
        a = np.clip(halo * 0.95 + ring, 0, 1)
        inside = r < 1.06
        col[inside] = 0; a[inside] = 1.0
        arr[..., :3] = np.clip(col, 0, 1); arr[..., 3] = a
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('bh', int(R)), mk)

def disk_sprite(R):
    """flattened accretion disk drawn as a tilted ellipse band (back half and front half)"""
    def mk():
        n = int(R * 5.2) + 8; c = n / 2
        y, x = np.mgrid[0:n, 0:n].astype(np.float32)
        u = (x - c) / R; v = (y - c) / (R * 0.28)
        rr = np.sqrt(u * u + v * v)
        band = np.exp(-((rr - 1.9) / 0.55) ** 2) * (rr > 1.15)
        streak = 0.8 + 0.2 * np.sin(rr * 14)
        col = np.zeros((n, n, 4), np.float32)
        col[..., 0] = 1.0; col[..., 1] = 0.62 + 0.25 * band; col[..., 2] = 0.25 + 0.3 * band
        col[..., 3] = np.clip(band * streak * 1.1, 0, 1)
        front = col.copy(); back = col.copy()
        front[y < c, 3] = 0; back[y >= c, 3] = 0
        f = lambda A: Image.fromarray((A * 255).astype(np.uint8), 'RGBA')
        return f(back), f(front)
    return sp(('disk', int(R)), mk)

def draw_bh(im, cx, cy, R, alpha=1.0, disk=True, rot=0.0):
    if alpha <= 0.004 or R < 1: return
    R = int(R)
    if disk:
        b, f = disk_sprite(R)
        paste_c(im, b, cx, cy, alpha)
    paste_c(im, bh_sprite(R), cx, cy, alpha)
    if disk:
        paste_c(im, f, cx, cy, alpha)

def sunsp(R):
    def mk():
        n = int(R * 2.6); c = n / 2
        y, x = np.mgrid[0:n, 0:n].astype(np.float32)
        r = np.sqrt((x - c) ** 2 + (y - c) ** 2) / R
        rg = np.random.default_rng(2)
        g = rg.random((40, 40)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
        limb = np.sqrt(np.clip(1 - r * r, 0, 1)) ** 0.45
        base = np.stack([np.ones_like(r), 0.72 + 0.18 * g, 0.25 + 0.2 * g], -1) * (0.55 + 0.45 * limb)[..., None]
        a = (r <= 1).astype(np.float32)
        cor = np.clip(1 - (r - 1) / 0.3, 0, 1) ** 2 * (r > 1)
        rgb = np.where((r <= 1)[..., None], base, np.array([1.0, 0.75, 0.3]))
        a = np.maximum(a, cor * 0.7)
        arr = np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA')
    return sp(('sun', int(R)), mk)

def darkband(im, y0, y1, a=0.6):
    if a <= 0: return
    d = ImageDraw.Draw(im, 'RGBA')
    for k in range(30):
        aa = int(255 * a * (1 - k / 30) * 0.6)
        d.rectangle((0, y0 - k * 4, W, y0 - k * 4 + 4), fill=(0, 0, 0, aa)) if False else None
    ov = Image.new('RGBA', (W, y1 - y0), (0, 0, 0, int(255 * a)))
    im.alpha_composite(ov, (0, y0))

def label(d, x, y, s, size, col, a):
    text(d, (x, y), s, size, col, POP_B, stroke=max(3, size // 12), alpha=a)

def walker(d, x, y, h, a):
    col = (235, 240, 255, int(255 * a)); hr = h * 0.12
    d.ellipse((x - hr, y - h, x + hr, y - h + 2 * hr), fill=col)
    w = max(2, int(h * 0.09))
    d.line((x, y - h + 2 * hr, x, y - h * 0.45), fill=col, width=w)
    d.line((x, y - h * 0.45, x - h * 0.18, y), fill=col, width=w); d.line((x, y - h * 0.45, x + h * 0.15, y), fill=col, width=w)
    d.line((x, y - h * 0.72, x - h * 0.17, y - h * 0.5), fill=col, width=w); d.line((x, y - h * 0.72, x + h * 0.17, y - h * 0.55), fill=col, width=w)

# ---------------------------------------------------------------- frame
def frame(t):
    im = BG.copy()
    # slow drift of the starfield for constant motion
    d = ImageDraw.Draw(im, 'RGBA')

    # ============ HOOK + MASS: Earth already collapsing (frame 0 mid-action) -> marble black hole
    e_mass = nx('mass')
    a_e = xf(t, -1, e_mass + 0.1, 0.01, 0.3)
    if a_e > 0:
        # Earth shrinks from 430 px (already 15% crushed at t=0) to vanish at ~1.6 s, black hole marble appears
        k = ease(ramp(t, 0.0, 1.7))
        Re = 430 * (1 - k) ** 1.4
        cy = 1000
        if Re > 6:
            paste_c(im, glow(int(Re * 2.8 + 60), (120, 180, 255), 1.6), W / 2, cy, a_e * 0.6)
            paste_c(im, earth(max(4, int(Re))), W / 2, cy, a_e)
            # crush streaks converging inward
            d = ImageDraw.Draw(im, 'RGBA')
            for j in range(18):
                an = j * math.pi / 9 + 0.3
                r1 = Re + 60 + 140 * ((t * 2.5 + j * 0.37) % 1)
                r2 = r1 + 90
                d.line((W / 2 + r1 * math.cos(an), cy + r1 * math.sin(an), W / 2 + r2 * math.cos(an), cy + r2 * math.sin(an)), fill=(170, 210, 255, int(200 * a_e * (1 - k))), width=6)
        ab = ease(ramp(t, 1.1, 1.8)) * a_e
        if ab > 0:
            Rb = 120 * (0.85 + 0.15 * ease(ramp(t, 1.4, 2.6)))
            draw_bh(im, W / 2, cy, Rb, ab)
        d = ImageDraw.Draw(im, 'RGBA')
        # frame-0 text: fully visible immediately
        text(d, (W / 2, 250), 'CRUSH EARTH', 128, WHITE, alpha=a_e if t < st('mass') else a_e * (1 - ease(ramp(t, st('mass'), st('mass') + 0.2))))
        text(d, (W / 2, 390), 'TO A MARBLE', 128, GOLD, alpha=a_e if t < st('mass') else a_e * (1 - ease(ramp(t, st('mass'), st('mass') + 0.2))))
        if t < st('mass'):
            text(d, (W / 2, 1600), '= BLACK HOLE', 132, (255, 120, 70), alpha=a_e)
        # mass beat
        if t >= st('mass') - 0.05:
            s0 = st('mass')
            ptext(d, (W / 2, 280), '6 SEXTILLION', 120, WHITE, t, s0 + 0.05, e_mass + 0.1)
            ptext(d, (W / 2, 410), 'TONNES', 120, GOLD, t, s0 + 0.35, e_mass + 0.1)
            ab2 = ease(ramp(t, s0 + 2.0, s0 + 2.4)) * a_e
            if ab2 > 0:
                # ruler under the marble: 1.8 cm
                d.line((W / 2 - 132, 1250, W / 2 + 132, 1250), fill=(255, 255, 255, int(230 * ab2)), width=6)
                for xx_ in (W / 2 - 132, W / 2 + 132):
                    d.line((xx_, 1225, xx_, 1275), fill=(255, 255, 255, int(230 * ab2)), width=6)
                label(d, W / 2, 1330, '≈ 1.8 cm', 92, WHITE, ab2)
            ptext(d, (W / 2, 1600), 'LESS THAN 2 cm WIDE', 84, CYAN, t, s0 + 2.6, e_mass + 0.1)

    # ============ ESCAPE + LIGHT
    a_x = xf(t, st('escape') - 0.1, nx('light') + 0.1, 0.25, 0.3)
    if a_x > 0:
        s0 = st('escape'); cy = 1080
        if t < st('light'):
            paste_c(im, glow(420, (120, 180, 255), 1.6), W / 2, cy + 120, a_x * 0.6)
            paste_c(im, earth(160), W / 2, cy + 120, a_x)
        else:
            draw_bh(im, W / 2, cy + 120, 110, a_x * ease(ramp(t, st('light') - 0.1, st('light') + 0.3)))
        d = ImageDraw.Draw(im, 'RGBA')
        if t < st('light'):
            # rocket climbing out of normal Earth (icon)
            p = ramp(t, s0, s0 + 3.5)
            rx, ry = W / 2 - 300, 1450 - 600 * ease(p)
            d.polygon([(rx, ry - 150), (rx - 50, ry - 40), (rx - 50, ry + 40), (rx + 50, ry + 40), (rx + 50, ry - 40)], fill=(240, 240, 250, int(255 * a_x)))
            d.ellipse((rx - 30, ry + 40, rx + 30, ry + 140 + 30 * math.sin(t * 30)), fill=(255, 170, 60, int(220 * a_x)))
            label(d, rx, ry + 200, 'rocket', 44, WHITE, a_x)
            ptext(d, (W / 2, 300), 'TO ESCAPE EARTH', 100, WHITE, t, s0, st('light'))
            ptext(d, (W / 2, 440), '11 km/s', 150, CYAN, t, s0 + 0.9, st('light'))
        else:
            l0 = st('light')
            # light rays leaving then bending back
            for j in range(10):
                an = j * math.pi / 5 + t * 0.4
                ph = ((t - l0) * 1.2 + j * 0.13) % 1
                r1 = 150 + 90 * math.sin(ph * math.pi)
                x1 = W / 2 + 150 * math.cos(an); y1 = cy + 120 + 150 * math.sin(an)
                x2 = W / 2 + r1 * 1.6 * math.cos(an); y2 = cy + 120 + r1 * 1.6 * math.sin(an)
                d.line((x1, y1, x2, y2), fill=(255, 245, 190, int(220 * a_x * math.sin(ph * math.pi))), width=7)
            ptext(d, (W / 2, 300), 'NOT EVEN LIGHT', 116, WHITE, t, l0, nx('light') + 0.1)
            ptext(d, (W / 2, 430), 'GETS OUT', 116, (255, 120, 70), t, l0 + 0.4, nx('light') + 0.1)
            ptext(d, (W / 2, 1640), '300,000 km/s', 120, GOLD, t, l0 + 2.4, nx('light') + 0.1)
            ptext(d, (W / 2, 1770), "ISN'T FAST ENOUGH", 70, WHITE, t, l0 + 2.8, nx('light') + 0.1)

    # ============ WEIRD + MOON: Moon keeps orbiting
    a_m = xf(t, st('weird') - 0.1, nx('moon') + 0.1, 0.25, 0.3)
    if a_m > 0:
        s0 = st('weird'); cx, cy = W / 2, 1060; orb = 380
        d = ImageDraw.Draw(im, 'RGBA')
        d.ellipse((cx - orb, cy - orb * 0.42, cx + orb, cy + orb * 0.42), outline=(180, 200, 255, int(140 * a_m)), width=4)
        ang = (t - s0) * 1.1 + 2.0
        mx, my = cx + orb * math.cos(ang), cy + orb * 0.42 * math.sin(ang)
        behind = math.sin(ang) < 0
        if behind: paste_c(im, moonsp(52), mx, my, a_m)
        draw_bh(im, cx, cy, 70, a_m)
        if not behind: paste_c(im, moonsp(52), mx, my, a_m)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 300), 'THE MOON', 130, WHITE, t, s0 + 0.9, nx('moon') + 0.1)
        ptext(d, (W / 2, 440), "WOULDN'T NOTICE", 110, GOLD, t, s0 + 1.3, nx('moon') + 0.1)
        if t >= st('moon'):
            m0 = st('moon')
            ptext(d, (W / 2, 1520), 'SAME MASS = SAME PULL', 76, CYAN, t, m0, nx('moon') + 0.1)
            ptext(d, (W / 2, 1650), 'ORBIT: STILL 27 DAYS', 76, WHITE, t, m0 + 2.2, nx('moon') + 0.1)
        label(d, W / 2, 1830, 'not to scale', 40, GREY, a_m * 0.8)

    # ============ SHARE: myth vs fact
    a_s = xf(t, st('share') - 0.1, nx('share') + 0.1, 0.2, 0.3)
    if a_s > 0:
        s0 = st('share'); cy = 1060
        # particles orbiting calmly (not sucked in)
        d = ImageDraw.Draw(im, 'RGBA')
        for j in range(26):
            rr_ = 200 + (j * 37) % 220; an = j * 2.4 + (t - s0) * (1.5 * 200 / rr_)
            px, py = W / 2 + rr_ * math.cos(an), cy + rr_ * 0.45 * math.sin(an)
            d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(200, 220, 255, int(220 * a_s)))
        draw_bh(im, W / 2, cy, 95, a_s)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 270), 'MYTH:', 90, (255, 90, 90), t, s0, nx('share') + 0.1)
        ptext(d, (W / 2, 400), 'THEY SUCK', 120, WHITE, t, s0 + 0.3, nx('share') + 0.1)
        ptext(d, (W / 2, 530), 'EVERYTHING IN', 110, WHITE, t, s0 + 0.5, nx('share') + 0.1)
        # strike-through on "they don't"
        sk = ease(ramp(t, s0 + 2.6, s0 + 3.0)) * a_s
        if sk > 0:
            d.line((150, 470, 150 + 780 * sk, 470), fill=(255, 60, 60, int(255 * a_s)), width=16)
        ptext(d, (W / 2, 1520), 'FACT: SAME MASS,', 84, CYAN, t, s0 + 3.3, nx('share') + 0.1)
        ptext(d, (W / 2, 1630), 'SAME PULL', 110, CYAN, t, s0 + 3.6, nx('share') + 0.1)
        ptext(d, (W / 2, 1790), 'send this to someone who thinks they do', 46, GOLD, t, s0 + 4.5, nx('share') + 0.1, font=POP_B, stroke=4)

    # ============ SUN -> 6 km
    a_u = xf(t, st('sun') - 0.1, nx('sun') + 0.1, 0.2, 0.3)
    if a_u > 0:
        s0 = st('sun'); cy = 1000
        k = ease(ramp(t, s0 + 0.2, s0 + 1.8))
        Rs_ = 460 * (1 - k) ** 1.3
        if Rs_ > 5:
            paste_c(im, glow(int(Rs_ * 3 + 80), (255, 170, 60), 1.5), W / 2, cy, a_u * 0.7)
            paste_c(im, sunsp(max(4, int(Rs_))), W / 2, cy, a_u)
        ab = ease(ramp(t, s0 + 1.4, s0 + 2.0)) * a_u
        if ab > 0:
            draw_bh(im, W / 2, cy, 120, ab)
            d = ImageDraw.Draw(im, 'RGBA')
            # 6 km bar with a walker
            d.line((W / 2 - 300, 1330, W / 2 + 300, 1330), fill=(255, 255, 255, int(230 * ab)), width=6)
            for xx_ in (W / 2 - 300, W / 2 + 300):
                d.line((xx_, 1305, xx_, 1355), fill=(255, 255, 255, int(230 * ab)), width=6)
            wp = ramp(t, s0 + 4.0, nx('sun'))
            walker(d, W / 2 - 290 + 580 * wp, 1320, 80, ab)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 280), 'CRUSH THE SUN', 116, WHITE, t, s0, nx('sun') + 0.1)
        ptext(d, (W / 2, 420), '≈ 6 km WIDE', 140, GOLD, t, s0 + 1.6, nx('sun') + 0.1)
        ptext(d, (W / 2, 1450), '≈ 1 HOUR WALK', 96, CYAN, t, s0 + 4.0, nx('sun') + 0.1)
        label(d, W / 2, 1830, "(the real Earth and Sun can't collapse like this)", 36, GREY, a_u * 0.85)

    # ============ TEASE: zoom-out burst
    a_t = xf(t, st('tease') - 0.05, nx('tease') + 0.15, 0.15, 0.25)
    if a_t > 0:
        s0 = st('tease'); g = ease(ramp(t, s0, nx('tease') + 0.15))
        draw_bh(im, W / 2, 1050, 60 + 260 * g, a_t)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 330), 'REAL ONES GET', 112, WHITE, t, s0, nx('tease') + 0.15)
        ptext(d, (W / 2, 470), 'WAY BIGGER', 140, (255, 120, 70), t, s0 + 0.3, nx('tease') + 0.15)

    # ============ SGR A*: inside Mercury's orbit (to scale: Rs/Mercury = 0.219)
    a_g = xf(t, st('sgr') - 0.1, nx('sgr') + 0.1, 0.2, 0.3)
    if a_g > 0:
        s0 = st('sgr'); cx, cy = W / 2, 1060
        merc_px = 420; rbh = merc_px * 0.219 / 1.06  # sprite's black disk = 1.06 R
        d = ImageDraw.Draw(im, 'RGBA')
        ao = ease(ramp(t, st('sgr') + 3.6, st('sgr') + 4.4)) * a_g
        if ao > 0:
            d.ellipse((cx - merc_px, cy - merc_px, cx + merc_px, cy + merc_px), outline=(170, 190, 220, int(230 * ao)), width=5)
            an = (t - s0) * 0.9
            mx, my = cx + merc_px * math.cos(an), cy + merc_px * math.sin(an)
            d.ellipse((mx - 16, my - 16, mx + 16, my + 16), fill=(190, 180, 170, int(255 * ao)))
            label(d, mx, my - 50, 'Mercury', 44, WHITE, ao)
        draw_bh(im, cx, cy, rbh, a_g, disk=False)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 270), 'OUR GALAXY’S CENTER', 84, WHITE, t, s0, nx('sgr') + 0.1)
        ptext(d, (W / 2, 400), '4 MILLION SUNS', 120, GOLD, t, s0 + 1.3, nx('sgr') + 0.1)
        ptext(d, (W / 2, 1600), "FITS INSIDE", 96, WHITE, t, s0 + 4.0, nx('sgr') + 0.1)
        ptext(d, (W / 2, 1720), "MERCURY'S ORBIT", 96, CYAN, t, s0 + 4.3, nx('sgr') + 0.1)
        label(d, W / 2, 1850, 'event horizon and orbit to scale', 38, GREY, a_g * 0.8)

    # ============ M87 + REVEAL: swallows the solar system (to scale: Rs = 128 AU, Neptune 30.07 AU)
    a_r = xf(t, st('m87') - 0.1, nx('reveal') + 0.1, 0.2, 0.3)
    if a_r > 0:
        s0 = st('m87'); r0 = st('reveal'); cx, cy = W / 2, 1060
        rbh_full = 470; au = rbh_full / 128.3
        if t < r0:
            # M87* shown big with its disk
            draw_bh(im, cx, cy, 200 + 20 * ease(ramp(t, s0, r0)), a_r)
            d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 280), 'M87*', 150, (255, 120, 70), t, s0, r0 + 0.05)
            ptext(d, (W / 2, 1600), '6.5 BILLION', 130, GOLD, t, s0 + 1.6, r0 + 0.05)
            ptext(d, (W / 2, 1730), 'SUNS', 110, WHITE, t, s0 + 1.9, r0 + 0.05)
        else:
            g = ease(ramp(t, r0 + 1.6, r0 + 3.4))
            d = ImageDraw.Draw(im, 'RGBA')
            # orbits to scale
            orbits = [(30.07, 'Neptune', (120, 160, 255)), (19.19, 'Uranus', (150, 220, 230)), (9.54, 'Saturn', (230, 200, 140)), (5.20, 'Jupiter', (230, 170, 120))]
            rbh = rbh_full * g
            if g > 0:
                paste_c(im, glow(int(rbh * 2.5 + 40), (255, 140, 50), 2.2), cx, cy, a_r * 0.45)
                paste_c(im, bh_sprite(max(2, int(rbh / 1.06))), cx, cy, a_r)
            d = ImageDraw.Draw(im, 'RGBA')
            for k_, (a_au, nm, col) in enumerate(orbits):
                R_ = a_au * au
                swallowed = rbh > R_
                oa = a_r * (0.55 if swallowed else 1.0)
                d.ellipse((cx - R_, cy - R_, cx + R_, cy + R_), outline=col + (int(200 * oa),), width=3)
                an = (t - r0) * (0.6 / math.sqrt(a_au)) + k_ * 1.3
                px, py = cx + R_ * math.cos(an), cy + R_ * math.sin(an)
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col + (int(255 * oa),))
            ss = ease(ramp(t, r0, r0 + 0.5)) * a_r * (1 - g)
            paste_c(im, glow(26, (255, 220, 120), 1.2), cx, cy, ss)
            label(d, cx, cy - 30.07 * au - 34, 'Neptune', 40, (150, 180, 255), a_r * ease(ramp(t, r0, r0 + 0.5)))
            ae = ease(ramp(t, r0 + 3.4, r0 + 3.8)) * a_r
            if ae > 0:
                label(d, cx, cy + rbh_full - 40, 'event horizon', 44, (255, 200, 140), ae)
            d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 330), 'OUR SOLAR SYSTEM', 100, WHITE, t, r0, r0 + 1.45)
            ptext(d, (W / 2, 1600), 'TO SCALE', 100, CYAN, t, r0 + 0.2, r0 + 1.45)
            ptext(d, (W / 2, 260), 'SWALLOWS', 120, WHITE, t, r0 + 1.4, nx('reveal') + 0.1)
            ptext(d, (W / 2, 390), 'EVERY PLANET', 120, (255, 120, 70), t, r0 + 1.7, nx('reveal') + 0.1)
            ptext(d, (W / 2, 1640), '≈ 4× NEPTUNE’S DISTANCE', 74, GOLD, t, r0 + 3.4, nx('reveal') + 0.1)
            ptext(d, (W / 2, 1760), 'LIGHT: 1.5 DAYS TO CROSS', 74, CYAN, t, r0 + 6.4, nx('reveal') + 0.1)
            label(d, W / 2, 1870, 'event horizon and orbits to scale', 38, GREY, a_r * 0.8)

    # ============ COMMENT: marble vs monster, loops to the opening marble
    a_c = xf(t, st('comment') - 0.1, TOTAL + 1, 0.2, 0.01)
    if a_c > 0:
        s0 = st('comment')
        draw_bh(im, 300, 1050, 60, a_c)
        draw_bh(im, 760, 1050, 170, a_c)
        d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 300), 'WHICH WOULD YOU', 104, WHITE, t, s0, TOTAL + 1)
        ptext(d, (W / 2, 430), 'FALL INTO?', 130, GOLD, t, s0 + 0.2, TOTAL + 1)
        pa = ease(ramp(t, s0 + 1.6, s0 + 1.9)) * a_c
        pill(d, 300, 1420, 'MARBLE', 70, (30, 120, 200), alpha=pa)
        pill(d, 760, 1420, 'MONSTER', 70, (200, 60, 50), alpha=pa)
        text(d, (W / 2, 1640), 'COMMENT ↓', 84, GOLD, alpha=pa)
        label(d, W / 2, 1850, 'not to scale', 40, GREY, a_c * 0.8)

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

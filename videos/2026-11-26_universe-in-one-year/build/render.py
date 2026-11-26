import sys, os, math, subprocess, datetime as dt
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import *

ORANGE = (255, 150, 60); GREEN = (110, 230, 120); PINK = (255, 120, 200)
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
YS = 365 * 86400.0

def emoji(ch, size):
    def mk():
        f = ImageFont.truetype(EMO, 109)
        im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
        im = im.crop(im.getbbox())
        s = size / max(im.size)
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return sp(('emo', ch, size), mk)
from PIL import ImageFont

def grad(im, top=True, h=600, a=215):
    g = np.zeros((h, W, 4), np.uint8)
    g[..., 3] = (np.linspace(a, 0, h) if top else np.linspace(0, a, h))[:, None].astype(np.uint8)
    im.alpha_composite(Image.fromarray(g, 'RGBA'), (0, 0 if top else H - h))

# ------------------------------------------------ calendar position (seconds into the cosmic year) by time
def D(day, h=0, m=0, s=0): return day * 86400 + h * 3600 + m * 60 + s
def doy(mon, day): return (dt.date(2026, mon, day) - dt.date(2026, 1, 1)).days
def kf():
    return [
        (0.0, D(40)), (st('bang') - 0.25, D(330)), (st('bang'), 0), (st('scale'), 0), (nx('scale') - 0.2, D(1)),
        (st('galaxy') + 0.6, D(7, 9, 54)), (st('empty'), D(7, 9, 54)), (st('empty') + 3.6, D(doy(8, 31))),
        (st('sun') + 0.5, D(doy(9, 2))), (st('life') + 0.6, D(doy(9, 30), 8)), (st('tease') + 0.3, D(doy(9, 30), 8)),
        (st('tease') + 2.0, D(doy(12, 1))), (st('animals') + 0.5, D(doy(12, 17), 17, 39)), (st('dinos'), D(doy(12, 17), 17, 39)),
        (st('dinos') + 0.6, D(doy(12, 25), 21, 52)), (st('rock'), D(doy(12, 25), 21, 52)), (st('rock') + 0.8, D(doy(12, 30), 6, 4)),
        (st('eleven'), D(doy(12, 30), 6, 4)), (st('eleven') + 0.8, D(364, 23)), (st('reveal') + 0.3, D(364, 23)),
        (st('reveal') + 2.6, D(364, 23, 48, 33)), (st('pyr'), D(364, 23, 48, 33)), (st('pyr') + 1.0, D(364, 23, 59, 49.5)),
        (st('you'), D(364, 23, 59, 49.5)), (st('you') + 2.5, D(364, 23, 59, 59.82)), (st('share'), D(364, 23, 59, 59.82)),
        (st('share') + 1.0, YS - 0.001), (99, YS - 0.001)]
KF = None
def cal(t):
    global KF
    if KF is None: KF = kf()
    for (a, x), (b, y) in zip(KF, KF[1:]):
        if a <= t <= b:
            p = ease((t - a) / max(b - a, 1e-6)); return x + (y - x) * p
    return KF[-1][1]

MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
def stamp(sec, mode):
    d = dt.datetime(2026, 1, 1) + dt.timedelta(seconds=min(sec, YS - 0.001))
    if mode == 0: return f'{MON[d.month-1]} {d.day}', ''
    if mode == 1:
        h = d.hour % 12 or 12
        return f'{MON[d.month-1]} {d.day}', f'{h}:{d.minute:02d} {"AM" if d.hour < 12 else "PM"}'
    h = d.hour % 12 or 12
    return f'DEC 31', f'{h}:{d.minute:02d}:{d.second:02d} PM'

# timeline window (start, end in cosmic seconds) — zooms year -> December -> Dec 31 -> last minute
def window(t):
    W0 = (0, YS); W1 = (D(doy(12, 1)), YS); W2 = (D(364), YS); W3 = (YS - 60, YS)
    seq = [(st('tease') + 1.0, W0), (st('tease') + 2.4, W1), (st('eleven') + 0.1, W1), (st('eleven') + 1.0, W2),
           (st('pyr') - 0.2, W2), (st('pyr') + 0.6, W3)]
    if t <= seq[0][0]: return W0
    for (a, x), (b, y) in zip(seq, seq[1:]):
        if a <= t <= b:
            p = ease((t - a) / (b - a))
            lw = math.log(x[1] - x[0]) * (1 - p) + math.log(y[1] - y[0]) * p
            w = math.exp(lw); return (YS - w, YS)
    return W3

def hud(im, t, alpha=1.0):
    if alpha <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, 'RGBA')
    sec = cal(t); a0, a1 = window(t); wd = a1 - a0
    x0, x1, y = 90, W - 90, 1730
    d.rounded_rectangle((x0 - 30, y - 300, x1 + 30, y + 120), 36, fill=(8, 10, 24, 200), outline=(90, 110, 170, 160), width=3)
    d.rounded_rectangle((x0, y - 14, x1, y + 14), 14, fill=(40, 46, 80, 255))
    fx = min(max((sec - a0) / wd, 0), 1)
    d.rounded_rectangle((x0, y - 14, x0 + max(28, (x1 - x0) * fx), y + 14), 14, fill=GOLD + (255,))
    # ticks + labels
    if wd > 200 * 86400: ticks = [(D(doy(m + 1, 1)), MON[m][0]) for m in range(12)]; step_lab = 1
    elif wd > 3 * 86400: ticks = [(D(doy(12, k)), str(k)) for k in range(1, 32)]; step_lab = 5
    elif wd > 600: ticks = [(D(364, h), (f'{h%12 or 12}{"A" if h<12 else "P"}')) for h in range(0, 24)]; step_lab = 3
    else: ticks = [(YS - 60 + s, f':{s:02d}') for s in range(0, 60, 5)]; step_lab = 2
    for i, (ts, lab) in enumerate(ticks):
        if ts < a0 - 1 or ts > a1: continue
        xx_ = x0 + (x1 - x0) * (ts - a0) / wd
        d.line((xx_, y - 26, xx_, y - 16), fill=(170, 180, 210, 220), width=3)
        if i % step_lab == 0 and abs(xx_ - x1) > 30:
            text(d, (xx_ + (20 if step_lab == 1 else 0), y + 52), lab, 34, GREY, POP_B, stroke=3)
    mx = x0 + (x1 - x0) * fx
    d.ellipse((mx - 22, y - 22, mx + 22, y + 22), fill=WHITE + (255,), outline=GOLD + (255,), width=6)
    mode = 0 if wd > 3 * 86400 and not (sec > D(364)) else (1 if wd > 600 else 2)
    if sec > D(364) and mode == 0: mode = 1
    a, b = stamp(sec, mode)
    text(d, (W / 2, y - 220), 'COSMIC CALENDAR' + ('  ·  DEC 31' if mode == 2 else ''), 34, CYAN, POP_B, stroke=3)
    if mode == 0: text(d, (W / 2, y - 120), a, 120, WHITE)
    elif mode == 1: text(d, (W / 2, y - 120), f'{a} · {b}', 96, WHITE)
    else: text(d, (W / 2, y - 120), b, 110, WHITE)
    im.alpha_composite(fade(lay, alpha))

# ------------------------------------------------ visuals
def galaxy_sprite(R):
    def mk():
        n = 2 * R; y, x = (np.mgrid[0:n, 0:n].astype(np.float32) - R) / R
        y = y / 0.55
        r = np.sqrt(x * x + y * y) + 1e-6; th = np.arctan2(y, x)
        arm = 0.5 + 0.5 * np.cos(2 * (th - 3.2 * np.log(r + 0.05)))
        rg = np.random.default_rng(4); nz = rg.random((n, n)).astype(np.float32)
        I = np.exp(-r * 1.7) * (0.45 + 1.1 * arm ** 3) + 1.6 * np.exp(-(r / 0.13) ** 2)
        I = I * (0.75 + 0.5 * nz) * (r < 1.1)
        col = np.stack([I * 1.0, I * 0.85, I * 1.05], -1)
        col += (nz[..., None] > 0.9965) * np.exp(-r)[..., None] * 0.8
        a = np.clip(I * 2.2, 0, 1)
        arr = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
        return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(1.2))
    return sp(('gal', R), mk)

def sun_sprite(R): return sp(('sun', R), lambda: sphere(R, (1.0, 0.72, 0.25), 2, rough=0.25))

def clock(im, cx, cy, R, hh, mm, ss=None, alpha=1.0, glowc=GOLD):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, 'RGBA')
    paste_c(lay, glow(int(R * 1.6), glowc, 2.2), cx, cy, 0.5)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(14, 16, 34, 255), outline=(235, 238, 250, 255), width=12)
    for k in range(60):
        a = k / 60 * 2 * math.pi; r1 = R * (0.84 if k % 5 == 0 else 0.9)
        d.line((cx + math.sin(a) * r1, cy - math.cos(a) * r1, cx + math.sin(a) * R * 0.95, cy - math.cos(a) * R * 0.95),
               fill=(220, 225, 240, 255), width=8 if k % 5 == 0 else 3)
    for k in range(1, 13):
        a = k / 12 * 2 * math.pi
        text(d, (cx + math.sin(a) * R * 0.68, cy - math.cos(a) * R * 0.68), str(k), int(R * 0.17), WHITE, POP_B, stroke=0)
    def hand(frac, L, wd, col):
        a = frac * 2 * math.pi
        d.line((cx, cy, cx + math.sin(a) * L, cy - math.cos(a) * L), fill=col + (255,), width=wd)
    hand(((hh % 12) + mm / 60) / 12, R * 0.48, 22, WHITE)
    hand(mm / 60, R * 0.74, 14, GOLD)
    if ss is not None: hand(ss / 60, R * 0.82, 5, RED)
    d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=GOLD + (255,))
    im.alpha_composite(fade(lay, alpha))

def burst(im, t, t0, alpha):
    p = ramp(t, t0, t0 + 1.2)
    R = int(200 + 700 * ease(p))
    paste_c(im, glow(R, (255, 240, 210), 1.4), W / 2, 820, alpha * (1 - 0.5 * p))
    paste_c(im, glow(int(R * 0.45), (255, 255, 255), 1.0), W / 2, 820, alpha)

def pyramid(d, cx, by, s, col):
    d.polygon([(cx - s, by), (cx, by - s * 0.95), (cx + s, by)], fill=col)
    d.polygon([(cx, by - s * 0.95), (cx + s, by), (cx + s * 0.3, by)], fill=tuple(int(c * 0.7) for c in col[:3]) + (255,))

def frame(t):
    im = BG.copy()
    # slow star drift
    d = ImageDraw.Draw(im, 'RGBA')

    def scene(k0, k1, pre=0.12, post=0.22):
        return xf(t, st(k0) - pre, nx(k1) + post, 0.22, 0.22)

    # ============ HOOK (frame 0 = question + key number on screen, clock racing)
    a = xf(t, -1, nx('hook') + 0.1, 0.01, 0.25)
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        paste_c(lay, galaxy_sprite(420), W / 2, 860, 0.55)
        spin = t * 900
        clock(lay, W / 2, 860, 330, (spin / 60) % 12, spin % 60, alpha=1.0, glowc=CYAN)
        grad(lay, True, 560, 230); ld = ImageDraw.Draw(lay, 'RGBA')
        text(ld, (W / 2, 120), '13.8 BILLION YEARS', 92, GOLD)
        text(ld, (W / 2, 230), 'SQUEEZED INTO 1 YEAR', 76, WHITE)
        text(ld, (W / 2, 365), 'WHAT TIME', 120, WHITE)
        text(ld, (W / 2, 490), 'DO WE SHOW UP?', 104, CYAN)
        im.alpha_composite(fade(lay, a))

    # ============ BANG
    a = scene('bang', 'bang', 0.05)
    if a > 0:
        burst(im, t, st('bang') - 0.1, a); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 260), 'JAN 1 · MIDNIGHT', 96, WHITE, t, st('bang'), nx('bang') + 0.2)
        ptext(d, (W / 2, 390), 'THE BIG BANG', 120, GOLD, t, st('bang') + 0.9, nx('bang') + 0.2)

    # ============ SCALE
    a = scene('scale', 'scale')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        paste_c(lay, glow(500, (255, 200, 150), 2.5), W / 2, 820, 0.35)
        s0 = st('scale')
        ptext(ld, (W / 2, 420), '1 DAY', 150, WHITE, t, s0, 99)
        ptext(ld, (W / 2, 570), '≈ 38 MILLION YEARS', 84, GOLD, t, s0 + 0.5, 99)
        ptext(ld, (W / 2, 860), '1 SECOND', 150, WHITE, t, s0 + 3.2, 99)
        ptext(ld, (W / 2, 1010), '≈ 440 YEARS', 96, CYAN, t, s0 + 3.7, 99)
        im.alpha_composite(fade(lay, a))

    # ============ GALAXY
    a = scene('galaxy', 'galaxy')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        g = galaxy_sprite(460).rotate(-(t - st('galaxy')) * 6, Image.BICUBIC)
        sc = 0.7 + 0.3 * ease(ramp(t, st('galaxy'), nx('galaxy')))
        g = g.resize((int(g.width * sc), int(g.height * sc)), Image.BILINEAR)
        paste_c(lay, g, W / 2, 900)
        ld = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 520, 200); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 170), 'JAN 8', 140, GOLD, t, st('galaxy'), 99)
        ptext(ld, (W / 2, 310), 'GALAXIES ALREADY EXIST', 76, WHITE, t, st('galaxy') + 0.6, 99)
        ptext(ld, (W / 2, 1290), 'WEBB SAW ONE FROM 280 MILLION', 44, CYAN, t, st('galaxy') + 2.4, 99, POP_B)
        ptext(ld, (W / 2, 1350), 'YEARS AFTER THE BIG BANG', 44, CYAN, t, st('galaxy') + 2.4, 99, POP_B)
        im.alpha_composite(fade(lay, a))

    # ============ EMPTY months
    a = scene('empty', 'empty')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        dd = dt.datetime(2026, 1, 1) + dt.timedelta(seconds=cal(t))
        mname = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER'][min(dd.month - 1, 8)]
        text(ld, (W / 2, 700), mname, 140, WHITE)
        ptext(ld, (W / 2, 330), 'STILL NO SUN', 120, ORANGE, t, st('empty') + 2.6, 99)
        ptext(ld, (W / 2, 450), 'NO EARTH. NO US.', 70, GREY, t, st('empty') + 3.2, 99)
        im.alpha_composite(fade(lay, a))

    # ============ SUN + EARTH
    a = scene('sun', 'sun')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        p = ease(ramp(t, st('sun'), st('sun') + 1.0))
        paste_c(lay, glow(520, (255, 190, 90), 2.0), W / 2 - 80, 850, 0.8 * p)
        s = sun_sprite(300); sc = 0.3 + 0.7 * p
        paste_c(lay, s.resize((int(s.width * sc), int(s.height * sc))), W / 2 - 80, 850)
        paste_c(lay, earth(60), W / 2 + 330, 1150, ease(ramp(t, st('sun') + 0.8, st('sun') + 1.3)))
        ld = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 520, 200); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 170), 'EARLY SEPTEMBER', 104, GOLD, t, st('sun'), 99)
        ptext(ld, (W / 2, 300), 'OUR SUN & EARTH FORM', 76, WHITE, t, st('sun') + 0.5, 99)
        im.alpha_composite(fade(lay, a))

    # ============ LIFE
    a = scene('life', 'life')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        paste_c(lay, earth(330), W / 2, 880)
        rg = np.random.default_rng(5)
        for k in range(9):
            ang = k / 9 * 2 * math.pi + 0.3; rr = 420 + 40 * math.sin(k * 1.7)
            ea = ease(ramp(t, st('life') + 0.3 + k * 0.12, st('life') + 0.6 + k * 0.12))
            bob = 12 * math.sin(t * 3 + k)
            paste_c(lay, emoji('🦠', 110 + (k % 3) * 20), W / 2 + math.cos(ang) * rr, 880 + math.sin(ang) * rr * 0.9 + bob, ea)
        ld = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 460, 210); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 160), 'LATE SEPTEMBER', 104, GREEN, t, st('life') + 0.3, 99)
        ptext(ld, (W / 2, 285), 'FIRST LIFE: MICROBES', 76, WHITE, t, st('life') + 0.8, 99)
        im.alpha_composite(fade(lay, a))

    # ============ TEASE
    a = scene('tease', 'tease')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        paste_c(lay, glow(520, (255, 60, 60), 2.0), W / 2, 760, 0.5 * ease(ramp(t, st('tease') + 1.0, st('tease') + 1.6)))
        ptext(ld, (W / 2, 560), 'BUT THE CRAZIEST PART…', 76, WHITE, t, st('tease'), 99)
        sc = 1 + 0.08 * math.sin(max(0, t - st('tease') - 1.2) * 9) * math.exp(-max(0, t - st('tease') - 1.2) * 2)
        ptext(ld, (W / 2, 760), 'IS DECEMBER', int(150 * sc), RED, t, st('tease') + 1.1, 99)
        im.alpha_composite(fade(lay, a))

    # ============ ANIMALS (Cambrian)
    a = scene('animals', 'animals')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        k_ = np.linspace(0, 1, H)[:, None]
        ocean = np.zeros((H, W, 4), np.uint8); ocean[..., 2] = (110 - 80 * k_).astype(np.uint8); ocean[..., 1] = (60 - 45 * k_).astype(np.uint8)
        ocean[..., 3] = 210
        lay.alpha_composite(Image.fromarray(ocean, 'RGBA'))
        es = ['🦐', '🐚', '🪼', '🦐', '🪼', '🐚', '🦐']
        for k, e in enumerate(es):
            ea = ease(ramp(t, st('animals') + 0.4 + k * 0.18, st('animals') + 0.7 + k * 0.18))
            x = 150 + (k * 137) % 800 + 30 * math.sin(t * 1.3 + k); y = 620 + (k * 211) % 620 + 20 * math.cos(t * 1.7 + k)
            paste_c(lay, emoji(e, 150 + (k % 3) * 30), x, y, ea)
        ld = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 520, 220); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 170), 'DEC 17', 140, GOLD, t, st('animals'), 99)
        ptext(ld, (W / 2, 310), 'ANIMALS EXPLODE', 92, WHITE, t, st('animals') + 0.5, 99)
        ptext(ld, (W / 2, 410), 'ACROSS THE OCEANS', 64, CYAN, t, st('animals') + 0.9, 99)
        im.alpha_composite(fade(lay, a))

    # ============ DINOS
    a = scene('dinos', 'dinos')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        p = ease(ramp(t, st('dinos'), st('dinos') + 0.4))
        paste_c(lay, glow(480, (60, 200, 90), 2.2), W / 2, 900, 0.4)
        paste_c(lay, emoji('🦖', 470), W / 2 - 170 + 200 * (1 - p), 920, p)
        paste_c(lay, emoji('🦕', 380), W / 2 + 230, 960, ease(ramp(t, st('dinos') + 0.3, st('dinos') + 0.6)))
        paste_c(lay, emoji('🎄', 170), 160, 640, ease(ramp(t, st('dinos') + 1.0, st('dinos') + 1.3)))
        paste_c(lay, emoji('🎄', 140), W - 150, 620, ease(ramp(t, st('dinos') + 1.1, st('dinos') + 1.4)))
        grad(lay, True, 520, 220); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 170), 'DEC 25', 150, RED, t, st('dinos'), 99)
        ptext(ld, (W / 2, 315), 'DINOSAURS ON', 92, WHITE, t, st('dinos') + 0.5, 99)
        ptext(ld, (W / 2, 425), 'CHRISTMAS DAY', 92, GREEN, t, st('dinos') + 1.0, 99)
        im.alpha_composite(fade(lay, a))

    # ============ ASTEROID
    a = scene('rock', 'rock')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        hit = st('rock') + 1.4
        p = ramp(t, st('rock'), hit)
        if t < hit + 0.15:
            paste_c(lay, emoji('🦖', 300), W / 2 + 120, 1080)
            r = emoji('☄️', 330)
            paste_c(lay, r, 120 + (W / 2 + 60 - 120) * p, 480 + (1000 - 480) * p)
        else:
            q = ramp(t, hit, hit + 1.2)
            paste_c(lay, glow(int(250 + 500 * q), (255, 150, 60), 1.4), W / 2 + 100, 1040, 1 - 0.5 * q)
            paste_c(lay, emoji('💥', int(300 + 200 * q)), W / 2 + 100, 1040, 1 - 0.3 * q)
        grad(lay, True, 520, 220); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 170), 'DEC 30', 140, ORANGE, t, st('rock'), 99)
        ptext(ld, (W / 2, 305), 'THE ASTEROID HITS', 88, WHITE, t, st('rock') + 0.6, 99)
        ptext(ld, (W / 2, 410), 'DINOSAURS GONE', 70, RED, t, hit + 0.2, 99)
        im.alpha_composite(fade(lay, a))

    # ============ ELEVEN PM + REVEAL (clock)
    a = xf(t, st('eleven') - 0.12, nx('reveal') + 0.22, 0.22, 0.22)
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        sec = cal(t); tod = sec - D(364) if sec > D(364) else 23 * 3600
        hh = tod / 3600; mm = (tod % 3600) / 60
        rev = t >= st('reveal') + 2.6
        clock(lay, W / 2, 880, 330, int(hh), mm, alpha=1.0, glowc=GOLD if rev else CYAN)
        grad(lay, True, 520, 220); ld = ImageDraw.Draw(lay, 'RGBA')
        if t < st('reveal'):
            ptext(ld, (W / 2, 160), "NEW YEAR'S EVE", 104, WHITE, t, st('eleven'), st('reveal') + 0.1)
            ptext(ld, (W / 2, 290), 'STILL NOBODY LIKE US', 76, RED, t, st('eleven') + 1.6, st('reveal') + 0.1)
        else:
            ptext(ld, (W / 2, 160), 'OUR SPECIES ARRIVES', 80, WHITE, t, st('reveal'), 99)
            if rev:
                sc = 1 + 0.12 * math.exp(-(t - st('reveal') - 2.6) * 4)
                text(ld, (W / 2, 330), '11:48 PM', int(190 * sc), GOLD)
                paste_c(lay, emoji('🧍', 260), W / 2 + 300, 1150, ease(ramp(t, st('reveal') + 2.7, st('reveal') + 3.0)))
                ptext(ld, (W / 2, 1290), '(ABOUT 300,000 YEARS AGO)', 46, GREY, t, st('reveal') + 3.0, 99, POP_B)
        im.alpha_composite(fade(lay, a))

    # ============ PYRAMIDS
    a = scene('pyr', 'pyr')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        paste_c(lay, glow(520, (255, 190, 100), 2.0), W / 2, 1000, 0.5)
        ld.rectangle((0, 1180, W, 1360), fill=(150, 110, 60, 255))
        pyramid(ld, W / 2 - 40, 1190, 300, (220, 175, 105, 255))
        pyramid(ld, W / 2 + 300, 1190, 170, (205, 160, 95, 255))
        pyramid(ld, W / 2 - 360, 1190, 120, (200, 155, 90, 255))
        grad(lay, True, 520, 220); ld = ImageDraw.Draw(lay, 'RGBA')
        ptext(ld, (W / 2, 160), 'THE PYRAMIDS', 110, GOLD, t, st('pyr'), 99)
        ptext(ld, (W / 2, 290), '~10 SECONDS TO MIDNIGHT', 72, WHITE, t, st('pyr') + 0.9, 99)
        im.alpha_composite(fade(lay, a))

    # ============ YOUR LIFE
    a = scene('you', 'you')
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        paste_c(lay, glow(560, (90, 215, 255), 2.2), W / 2, 820, 0.45)
        ptext(ld, (W / 2, 170), 'YOUR WHOLE LIFE', 104, WHITE, t, st('you'), 99)
        ptext(ld, (W / 2, 290), '(80 YEARS)', 64, GREY, t, st('you') + 0.3, 99)
        ptext(ld, (W / 2, 640), 'LESS THAN', 100, WHITE, t, st('you') + 1.8, 99)
        sc = 1 + 0.12 * math.exp(-max(0, t - st('you') - 2.4) * 4)
        ptext(ld, (W / 2, 820), '1/5 SECOND', int(170 * sc), CYAN, t, st('you') + 2.4, 99)
        paste_c(lay, emoji('👁️', 220), W / 2, 1110, ease(ramp(t, st('you') + 4.6, st('you') + 4.9)))
        ptext(ld, (W / 2, 1290), 'ABOUT ONE BLINK', 64, GOLD, t, st('you') + 4.6, 99)
        im.alpha_composite(fade(lay, a))

    # ============ SHARE + COMMENT (loops into the opening)
    a = xf(t, st('share') - 0.12, TOTAL + 1, 0.22, 0.01)
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay, 'RGBA')
        lp = ramp(t, TOTAL - 0.7, TOTAL); ca = 1 - ease(lp)
        if t < st('comment'):
            ptext(ld, (W / 2, 170), 'SEND THIS TO SOMEONE', 76, WHITE, t, st('share'), st('comment'))
            ptext(ld, (W / 2, 290), 'WHO THINKS DINOSAURS', 80, WHITE, t, st('share') + 0.4, st('comment'))
            ptext(ld, (W / 2, 400), 'LIVED AGES AGO', 96, GOLD, t, st('share') + 0.8, st('comment'))
            paste_c(lay, emoji('🦖', 380), W / 2, 870, xf(t, st('share') + 0.3, st('comment'), 0.3, 0.2))
            ptext(ld, (W / 2, 1200), '= LAST WEEK 📅'.replace(' 📅', ''), 110, RED, t, st('share') + 3.2, st('comment'))
        else:
            text(ld, (W / 2, 220), 'WHICH SHOCKED', 110, WHITE, alpha=ca)
            text(ld, (W / 2, 345), 'YOU MORE?', 130, GOLD, alpha=ca)
            pa = ease(ramp(t, st('comment') + 1.2, st('comment') + 1.5)) * ca
            pb = ease(ramp(t, st('comment') + 3.0, st('comment') + 3.3)) * ca
            paste_c(lay, emoji('🦖', 260), W / 2 - 250, 760, pa); pill(ld, W / 2 - 250, 1000, 'CHRISTMAS', 52, (30, 150, 70), alpha=pa)
            paste_c(lay, emoji('🧍', 260), W / 2 + 250, 760, pb); pill(ld, W / 2 + 250, 1000, '11:48 PM', 52, (200, 140, 20), alpha=pb)
        if lp > 0:
            lay2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            spin = t * 900
            clock(lay2, W / 2, 860, 330, (spin / 60) % 12, spin % 60, alpha=1.0, glowc=CYAN)
            l2 = ImageDraw.Draw(lay2, 'RGBA')
            text(l2, (W / 2, 120), '13.8 BILLION YEARS', 92, GOLD)
            text(l2, (W / 2, 230), 'SQUEEZED INTO 1 YEAR', 76, WHITE)
            lay.alpha_composite(fade(lay2, ease(lp)))
        im.alpha_composite(fade(lay, a))

    # HUD calendar (hidden on hook's first frames? no: it is part of the hook image)
    hud(im, t, 1.0)
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

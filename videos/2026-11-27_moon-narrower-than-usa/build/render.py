import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import *
import world as Wd

ORANGE = (255, 150, 60); GREEN = (90, 220, 150)
D = Wd.D

def blend(im, fn):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(ov)); im.alpha_composite(ov)
def pill(d, cx, cy, s, size, bg, fg=WHITE, alpha=1.0):
    if alpha <= 0.004: return
    f = F(BLACK, size); w = f.getlength(s) + size * 1.4; h = size * 1.7
    blend(d._image, lambda o: o.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=tuple(bg) + (int(255 * alpha),)))
    text(d, (cx, cy), s, size, fg, BLACK, stroke=0, alpha=alpha)
def grad(im, top=True, h=600, a=215):
    g = np.zeros((h, W, 4), np.uint8)
    g[..., 3] = (np.linspace(a, 0, h) if top else np.linspace(0, a, h))[:, None].astype(np.uint8)
    im.alpha_composite(Image.fromarray(g, 'RGBA'), (0, 0 if top else H - h))
def lerp(a, b, p): return a + (b - a) * p

# ------------------------------------------------------------------ maps
US = Wd.LOWER48
NEIGH = [Wd.country('Canada'), Wd.country('Mexico')]
USMAP = Wd.MapCanvas(Wd.US_P, -3600, 3600, -5200, 5200, 0.55,
                     [(NEIGH, (36, 48, 62, 255), (75, 92, 112, 255), 2), (US, (40, 112, 84, 255), (110, 190, 150, 120), 2)])
US_RINGS = [Wd.US_P(r) for f in US for r in Wd.rings(f['geometry'])]
_allx = np.concatenate([r[:, 0] for r in US_RINGS]); _ally = np.concatenate([r[:, 1] for r in US_RINGS])
UCX, UCY = (_allx.min() + _allx.max()) / 2, (_ally.min() + _ally.max()) / 2
US_WKM = _allx.max() - _allx.min()
OUTER = [r for r in US_RINGS if len(r) > 40]
A = Wd.US_P([(-122.998791, 37.988616)])[0]; B = Wd.US_P([(-67.014015, 44.867749)])[0]  # 4,648 km great-circle (compute.py)
TX = [Wd.US_P(r) for f in US if f['properties']['name'] == 'Texas' for r in Wd.rings(f['geometry'])]
TXC = np.concatenate(TX).mean(0)
AUS = Wd.country('Australia'); AUS_P = Wd.proj('aeqd', -25.5, 134.0)
AUSMAP = Wd.MapCanvas(AUS_P, -3200, 3200, -5200, 5200, 0.55, [([AUS], (40, 112, 84, 255), (150, 220, 180, 200), 3)])
RUS = Wd.country('Russia'); RUS_P = Wd.proj('laea', 62, 97)
AFR = None

def scr(p, cam):
    cx, cy, s = cam
    return (W / 2 + (p[0] - cx) * s, H / 2 - (p[1] - cy) * s)

SPR = {}
def body(name, px):
    k = (name, int(px))
    if k not in SPR:
        big = ('big', name)
        if big not in SPR: SPR[big] = Wd.sphere_img(name, 1250, lon0=math.radians(-98) if name == 'Earth' else 0.0)
        SPR[k] = SPR[big].resize((max(2, int(px * SPR[big].width / 1250)),) * 2, Image.LANCZOS)
    return SPR[k]
def skin(name, px):
    k = ('skin', name, int(px))
    if k not in SPR:
        big = ('skinbig', name)
        if big not in SPR: SPR[big] = Wd.flat_skin(name, 1100)
        SPR[k] = SPR[big].resize((max(2, int(px * SPR[big].width / 1100)),) * 2, Image.LANCZOS)
    return SPR[k]
SIL = Wd.silhouette(US, Wd.US_P, 0.4, fill=(70, 200, 140, 255))
RUSSIL = Wd.silhouette([RUS], RUS_P, 0.4, fill=(220, 70, 70, 255))
def sil(which, wpx, alpha=1.0):
    im, wk, hk = which
    k = (id(which), int(wpx))
    if k not in SPR: SPR[k] = im.resize((int(wpx), int(wpx * im.height / im.width)), Image.LANCZOS)
    return fade(SPR[k], alpha)

def us_outline(im, cam, alpha=0.5, col=(255, 255, 255), width=3):
    if alpha <= 0: return
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for r in OUTER:
        q = [scr(p, cam) for p in r]
        d.line(q + [q[0]], fill=col + (int(255 * alpha),), width=width)
    im.alpha_composite(ov)

def draw_body(im, name, cx, cy, s, alpha=1.0, shadow=True):
    px = D[name] * s
    spr = body(name, px)
    if shadow:
        g = glow(int(px * 0.62) + 4, (0, 0, 0), 1.2)
        paste_c(im, g, cx + px * 0.04, cy + px * 0.05, 0.55 * alpha)
    paste_c(im, spr, cx, cy, alpha)

def measure(d, p0, p1, col, label, size=44, off=-40, alpha=1.0, prog=1.0):
    if alpha <= 0: return
    x0, y0 = p0; x1, y1 = p1
    x1 = x0 + (x1 - x0) * prog; y1 = y0 + (y1 - y0) * prog
    c = tuple(col) + (int(255 * alpha),)
    d.line([(x0, y0), (x1, y1)], fill=(0, 0, 0, int(200 * alpha)), width=14)
    d.line([(x0, y0), (x1, y1)], fill=c, width=8)
    ang = math.atan2(y1 - y0, x1 - x0); nx_, ny_ = -math.sin(ang), math.cos(ang)
    for (x, y) in ((x0, y0), (x1, y1)):
        d.line([(x - nx_ * 22, y - ny_ * 22), (x + nx_ * 22, y + ny_ * 22)], fill=c, width=8)
    if prog > 0.6 and label:
        text(d, ((x0 + x1) / 2 + nx_ * off, (y0 + y1) / 2 + ny_ * off), label, size, col, BLACK, alpha=alpha * ease(ramp(prog, 0.6, 1)))

# ------------------------------------------------------------------ cameras
HOOKCAM = (UCX, UCY - 250, 0.215)
def hook_cam(t): return (UCX, UCY - 250, 0.212 + 0.004 * math.sin(t * 0.6))

def map_scene(t):
    """US map scenes: returns frame"""
    # camera by beat
    k_ce0, k_ce1 = st('ceres'), nx('ceres')
    k_pl, k_me = st('pluto'), st('mercury')
    cam = hook_cam(t)
    if t >= st('map') - 0.2 and t < st('aus'):
        p = ease(ramp(t, st('map'), st('map') + 1.2)); cam = (UCX, lerp(UCY - 250, UCY - 80, p), lerp(0.213, 0.2, p))
    if k_ce0 - 0.1 <= t < k_pl:
        p = ease(ramp(t, k_ce0, k_ce0 + 1.3)); cam = (lerp(UCX, TXC[0], p), lerp(UCY - 250, TXC[1] + 80, p), lerp(0.2, 0.62, p) + 0.02 * ramp(t, k_ce0 + 1.3, k_ce1))
    if k_pl <= t < k_me:
        p = ease(ramp(t, k_pl, k_pl + 0.8)); cam = (lerp(TXC[0], UCX, p), lerp(TXC[1] + 80, UCY - 200, p), lerp(0.64, 0.205, p))
    if k_me <= t < st('ganymede'):
        p = ease(ramp(t, k_me, k_me + 0.9)); cam = (UCX, UCY - 200, lerp(0.205, 0.168, p) - 0.004 * ramp(t, k_me + 0.9, nx('mercury')))
    im = USMAP.view(cam[0], cam[1], cam[2], W, H)
    return im, cam

def frame(t):
    im = BG.copy()
    d = ImageDraw.Draw(im, 'RGBA')
    # ============ MAP SCENES (hook, map, tease, share, comment use the Moon on the US)
    in_map = (t < st('aus')) or (st('ceres') <= t < st('ganymede')) or (t >= st('tease') and t < st('peel')) or t >= st('share')
    if in_map:
        mim, cam = map_scene(t)
        im.alpha_composite(mim); d = ImageDraw.Draw(im, 'RGBA')
        s = cam[2]
        if t < st('aus') or (st('tease') <= t < st('peel')) or t >= st('share'):
            # Moon on the USA
            mc = (UCX, UCY - 60)
            if st('map') <= t < st('aus'):
                p = ease(ramp(t, st('map') + 0.6, st('map') + 2.0))
                u = (B - A) / np.linalg.norm(B - A); R = D['Moon'] / 2
                tgt = A + u * R
                mc = (lerp(UCX, tgt[0], p), lerp(UCY - 60, tgt[1], p))
            cx, cy = scr(mc, cam)
            draw_body(im, 'Moon', cx, cy, s)
            us_outline(im, cam, 0.35)
            d = ImageDraw.Draw(im, 'RGBA')
            if st('map') <= t < st('aus'):
                pa = scr(A, cam); pb = scr(B, cam)
                u = (B - A) / np.linalg.norm(B - A)
                m0 = scr(A, cam); m1 = scr(A + u * D['Moon'], cam)
                off = np.array([-(pb[1] - pa[1]), pb[0] - pa[0]]); off = off / np.linalg.norm(off)
                q0 = (pa[0] + off[0] * 0, pa[1] + 0); q1 = pb
                measure(d, (pa[0], pa[1] + 0), (pb[0], pb[1]), GOLD, '', prog=ease(ramp(t, st('map') + 7.1, st('map') + 8.0)))
                pr = ease(ramp(t, st('map') + 4.0, st('map') + 4.8))
                measure(d, (m0[0] - off[0] * 0, m0[1] - 0), (m1[0], m1[1]), CYAN, '', prog=pr)
                al = ease(ramp(t, st('map') + 4.2, st('map') + 4.6))
                text(d, (W / 2, 1330), 'MOON  3,475 KM', 86, CYAN, BLACK, alpha=al)
                text(d, (W / 2, 1450), 'USA  4,500+ KM', 86, GOLD, BLACK, alpha=ease(ramp(t, st('map') + 7.2, st('map') + 7.6)))
                pill(d, W / 2, 1580, 'COAST TO COAST', 40, (150, 110, 20), alpha=ease(ramp(t, st('map') + 7.5, st('map') + 7.9)))
            grad(im, True, 640, 225); d = ImageDraw.Draw(im, 'RGBA')
            if t < st('map'):
                text(d, (W / 2, 210), 'THE MOON IS', 104, WHITE, BLACK)
                text(d, (W / 2, 360), 'NARROWER', 168, GOLD, BLACK)
                text(d, (W / 2, 510), 'THAN THE USA', 116, WHITE, BLACK)
                grad(im, False, 420, 200); d = ImageDraw.Draw(im, 'RGBA')
                text(d, (W / 2, 1560), 'MOON 3,475 KM', 82, CYAN, BLACK)
                text(d, (W / 2, 1670), 'USA 4,500+ KM', 82, GOLD, BLACK)
                pill(d, W / 2, 1800, 'DRAWN TO SCALE', 44, (30, 110, 170))
            elif t < st('aus'):
                ptext(d, (W / 2, 200), 'DROP IT ON A MAP', 96, WHITE, t, st('map'), st('aus'))
                ptext(d, (W / 2, 330), "IT DOESN'T REACH", 92, GOLD, t, st('map') + 1.4, st('aus'))
                ptext(d, (W / 2, 450), 'COAST TO COAST', 92, GOLD, t, st('map') + 1.8, st('aus'))
            elif t < st('peel'):
                sh = 10 * math.sin(t * 60) * (1 - ramp(t, st('tease') + 3.0, st('tease') + 3.4)) * (t > st('tease') + 3.0)
                ptext(d, (W / 2 + sh, 230), 'NARROWER…', 130, WHITE, t, st('tease') + 2.3, st('peel') + 0.2)
                ptext(d, (W / 2 + sh, 400), 'BUT NOT SMALLER', 112, RED, t, st('tease') + 3.0, st('peel') + 0.2)
                if t < st('tease') + 2.3:
                    text(d, (W / 2, 230), "HERE'S THE TWIST", 104, GOLD, BLACK)
            else:
                lp = ramp(t, TOTAL - 0.7, TOTAL); ca = 1 - ease(lp)
                if t < st('comment'):
                    ptext(d, (W / 2, 180), 'SEND THIS TO SOMEONE', 76, WHITE, t, st('share'), st('comment'))
                    ptext(d, (W / 2, 300), 'WHO THINKS THE MOON', 86, WHITE, t, st('share') + 0.3, st('comment'))
                    ptext(d, (W / 2, 430), 'IS TINY', 130, GOLD, t, st('share') + 0.7, st('comment'))
                else:
                    text(d, (W / 2, 190), 'MOON WIDER', 120, WHITE, BLACK, alpha=ca)
                    text(d, (W / 2, 330), 'THAN THE USA?', 110, GOLD, BLACK, alpha=ca)
                    pa_ = ease(ramp(t, st('comment') + 0.6, st('comment') + 0.9)) * ca
                    pill(d, 330, 1720, 'YES', 80, (30, 150, 70), alpha=pa_)
                    pill(d, 750, 1720, 'NO', 80, (205, 30, 40), alpha=pa_)
                if lp > 0:
                    text(d, (W / 2, 210), 'THE MOON IS', 104, WHITE, BLACK, alpha=ease(lp))
                    text(d, (W / 2, 360), 'NARROWER', 168, GOLD, BLACK, alpha=ease(lp))
                    text(d, (W / 2, 510), 'THAN THE USA', 116, WHITE, BLACK, alpha=ease(lp))
        elif t < st('pluto'):
            # ============ CERES on TEXAS
            p = ease(ramp(t, st('ceres') + 2.5, st('ceres') + 3.3))
            tc = (TXC[0], TXC[1] + lerp(2500, 0, p))
            cx, cy = scr(tc, cam)
            draw_body(im, 'Ceres', cx, cy, s, alpha=0.93)
            ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            for r in TX:
                q = [scr(pp, cam) for pp in r]
                od.line(q + [q[0]], fill=GOLD + (255,), width=7)
            im.alpha_composite(ov)
            grad(im, True, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 190), 'CERES', 150, WHITE, t, st('ceres'), nx('ceres') + 0.2)
            ptext(d, (W / 2, 330), 'BIGGEST IN THE ASTEROID BELT', 56, GREY, t, st('ceres') + 0.4, nx('ceres') + 0.2)
            grad(im, False, 520, 220); d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 1600), '≈ SAME AREA', 120, GOLD, t, st('ceres') + 4.1, nx('ceres') + 0.2)
            ptext(d, (W / 2, 1730), 'AS TEXAS', 110, WHITE, t, st('ceres') + 4.4, nx('ceres') + 0.2)
        elif t < st('mercury'):
            # ============ PLUTO on the USA
            u = (B - A) / np.linalg.norm(B - A)
            pc = A + u * D['Pluto'] / 2
            p = ease(ramp(t, st('pluto') + 0.2, st('pluto') + 1.0))
            pc = (pc[0], pc[1] + lerp(3000, 0, p))
            cx, cy = scr(pc, cam)
            draw_body(im, 'Pluto', cx, cy, s)
            us_outline(im, cam, 0.35); d = ImageDraw.Draw(im, 'RGBA')
            pa = scr(A, cam); pb = scr(B, cam); pm = scr(A + u * D['Pluto'], cam)
            measure(d, pa, pb, GOLD, '', prog=ease(ramp(t, st('pluto') + 1.0, st('pluto') + 1.8)))
            measure(d, pa, pm, ORANGE, '', prog=ease(ramp(t, st('pluto') + 1.4, st('pluto') + 2.0)))
            grad(im, True, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 200), 'PLUTO', 150, ORANGE, t, st('pluto'), nx('pluto') + 0.2)
            ptext(d, (W / 2, 350), '≈ HALF AS WIDE', 104, WHITE, t, st('pluto') + 1.0, nx('pluto') + 0.2)
            ptext(d, (W / 2, 1400), '2,377 KM', 96, ORANGE, t, st('pluto') + 1.6, nx('pluto') + 0.2)
        else:
            # ============ MERCURY over the USA
            p = ease(ramp(t, st('mercury') + 0.2, st('mercury') + 1.1))
            mc = (UCX, UCY - 60 + lerp(-4000, 0, p))
            cx, cy = scr(mc, cam)
            draw_body(im, 'Mercury', cx, cy, s)
            us_outline(im, cam, lerp(0, 0.75, ramp(t, st('mercury') + 1.1, st('mercury') + 1.6)), (120, 255, 180), 4)
            grad(im, True, 600, 225); d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 190), 'MERCURY', 140, WHITE, t, st('mercury'), nx('mercury') + 0.2)
            ptext(d, (W / 2, 320), 'A WHOLE PLANET', 80, GREY, t, st('mercury') + 0.6, nx('mercury') + 0.2)
            grad(im, False, 520, 220); d = ImageDraw.Draw(im, 'RGBA')
            ptext(d, (W / 2, 1600), 'JUST A LITTLE', 100, WHITE, t, st('mercury') + 1.6, nx('mercury') + 0.2)
            ptext(d, (W / 2, 1730), 'WIDER THAN THE USA', 86, GREEN, t, st('mercury') + 2.0, nx('mercury') + 0.2)
        return im.convert('RGB')

    # ============ AUSTRALIA
    if st('aus') <= t < st('ceres'):
        p = ramp(t, st('aus'), nx('aus'))
        s = 0.235 + 0.01 * p; cam = (0, -250, s)
        im.alpha_composite(AUSMAP.view(cam[0], cam[1], s, W, H)); d = ImageDraw.Draw(im, 'RGBA')
        q = ease(ramp(t, st('aus'), st('aus') + 0.5))
        cx, cy = scr((lerp(-1200, 0, q), 0), cam)
        draw_body(im, 'Moon', cx, cy, s)
        grad(im, True, 560, 220); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 200), 'EVEN AUSTRALIA', 110, WHITE, t, st('aus') - 0.3, nx('aus') + 0.2)
        ptext(d, (W / 2, 340), 'IS WIDER', 120, GOLD, t, st('aus') + 0.6, nx('aus') + 0.2)
        grad(im, False, 420, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 1700), 'AUSTRALIA ≈ 4,000 KM', 76, GREEN, t, st('aus') + 0.9, nx('aus') + 0.2)
        return im.convert('RGB')

    # ============ GANYMEDE vs MERCURY (space)
    if st('ganymede') <= t < st('mars'):
        s = 0.096 * (1 + 0.03 * ramp(t, st('ganymede'), nx('ganymede')))
        p = ease(ramp(t, st('ganymede'), st('ganymede') + 0.7))
        gm, gg = D['Mercury'] * s, D['Ganymede'] * s
        xm = 30 + gm / 2; xg = W - 30 - gg / 2
        draw_body(im, 'Mercury', lerp(W / 2, xm, p), 900, s)
        draw_body(im, 'Ganymede', lerp(W + gg, xg, p), 900, s)
        d = ImageDraw.Draw(im, 'RGBA')
        sl = sil(SIL, US_WKM * s, ease(ramp(t, st('ganymede') + 1.6, st('ganymede') + 2.1)))
        paste_c(im, sl, W / 2, 1440, 1.0)
        text(d, (W / 2, 1440 + sl.height / 2 + 50), 'USA (same scale)', 50, GREEN, BLACK, alpha=ease(ramp(t, st('ganymede') + 1.8, st('ganymede') + 2.2)))
        ptext(d, (xm, 900 + gg / 2 + 50), 'MERCURY 4,879 KM', 48, GREY, t, st('ganymede') + 0.6, nx('ganymede') + 0.2)
        ptext(d, (xg, 900 + gg / 2 + 50), 'GANYMEDE 5,268 KM', 48, CYAN, t, st('ganymede') + 0.9, nx('ganymede') + 0.2)
        grad(im, True, 520, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 190), 'A MOON OF JUPITER', 88, WHITE, t, st('ganymede'), nx('ganymede') + 0.2)
        ptext(d, (W / 2, 320), 'BIGGER THAN MERCURY', 88, CYAN, t, st('ganymede') + 1.3, nx('ganymede') + 0.2)
        return im.convert('RGB')

    # ============ MARS / EARTH with rows of USA silhouettes
    if st('mars') <= t < st('tease'):
        is_e = t >= st('earth'); k0 = st('earth') if is_e else st('mars'); k1 = nx('earth') if is_e else nx('mars')
        name = 'Earth' if is_e else 'Mars'
        s = (0.068 if is_e else 0.12) * (1 + 0.04 * ramp(t, k0, k1))
        cy = 960; px = D[name] * s
        draw_body(im, name, W / 2, cy, s * ease(0.4 + 0.6 * ramp(t, k0, k0 + 0.4)))
        d = ImageDraw.Draw(im, 'RGBA')
        uw = US_WKM * s; n = D[name] / US_WKM
        x = W / 2 - px / 2; i = 0
        row = Image.new('RGBA', im.size, (0, 0, 0, 0))
        while x < W / 2 + px / 2 - 2:
            a = ease(ramp(t, k0 + 0.8 + 0.45 * i, k0 + 1.1 + 0.45 * i))
            if a > 0:
                sl = sil(SIL, uw, 0.88 * a)
                row.alpha_composite(sl, (int(x), int(cy - sl.height / 2)))
            x += uw; i += 1
        # clip to the planet's width
        mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).rectangle((W / 2 - px / 2, 0, W / 2 + px / 2, H), fill=255)
        row.putalpha(Image.fromarray(np.minimum(np.array(row.getchannel('A')), np.array(mask))))
        im.alpha_composite(row); d = ImageDraw.Draw(im, 'RGBA')
        measure(d, (W / 2 - px / 2, cy + px / 2 + 70), (W / 2 + px / 2, cy + px / 2 + 70), CYAN if is_e else ORANGE, '', prog=ease(ramp(t, k0 + 0.3, k0 + 0.9)))
        grad(im, True, 520, 200); d = ImageDraw.Draw(im, 'RGBA')
        if is_e:
            ptext(d, (W / 2, 190), 'EARTH', 150, CYAN, t, k0, k1 + 0.2)
            ptext(d, (W / 2, 1640), '< 3 USA ACROSS', 108, WHITE, t, k0 + 1.9, k1 + 0.2)
        else:
            ptext(d, (W / 2, 190), 'MARS', 150, ORANGE, t, k0, k1 + 0.2)
            ptext(d, (W / 2, 1640), '≈ 1.5 USA WIDE', 108, WHITE, t, k0 + 1.3, k1 + 0.2)
        return im.convert('RGB')

    # ============ PEEL the Moon
    if st('peel') <= t < st('russia'):
        k0 = st('peel'); s = 0.088
        mpx = D['Moon'] * s
        p = ease(ramp(t, k0 + 0.3, k0 + 2.4))
        mcy = lerp(960, 520, p); mpx_ = lerp(D['Moon'] * 0.2, mpx, p)
        draw_body(im, 'Moon', W / 2, mcy, mpx_ / D['Moon'])
        sk = 2 * mpx * ease(ramp(t, k0 + 1.4, k0 + 3.0))
        if sk > 4:
            spr = skin('Moon', sk)
            spr = spr.rotate(-90 * (1 - ramp(t, k0 + 1.4, k0 + 3.0)), resample=Image.BICUBIC)
            paste_c(im, spr, W / 2, 1020, 1.0)
        d = ImageDraw.Draw(im, 'RGBA')
        # width arrows: "twice as wide"
        tw = st('peel') + 8.1
        a2 = ease(ramp(t, tw, tw + 0.5))
        if a2 > 0:
            measure(d, (W / 2 - mpx / 2, mcy - mpx / 2 - 30), (W / 2 + mpx / 2, mcy - mpx / 2 - 30), CYAN, '', alpha=a2)
            measure(d, (W / 2 - mpx, 1020 + mpx + 30), (W / 2 + mpx, 1020 + mpx + 30), GOLD, '', alpha=a2)
            text(d, (W / 2 + mpx / 2 + 140, mcy), '1×', 90, CYAN, BLACK, alpha=a2)
            text(d, (W / 2, 1020 + mpx + 110), '2× AS WIDE', 90, GOLD, BLACK, alpha=a2)
        # area bars
        ab = ease(ramp(t, k0 + 2.9, k0 + 3.3)) * (1 - ease(ramp(t, tw - 0.2, tw + 0.2)))
        if ab > 0:
            box = Image.new('RGBA', im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(box, 'RGBA')
            bd.rounded_rectangle((40, 1360, W - 40, 1880), 30, fill=(5, 8, 20, 225))
            X0, XW = 90, 900; moon_a = 37.93
            def bar(y, frac, col, lab, val):
                bd.rounded_rectangle((X0, y, X0 + XW * frac, y + 70), 14, fill=col + (255,))
                text(bd, (X0, y - 34), lab, 40, WHITE, BLACK, anchor='lm', stroke=4)
                text(bd, (X0 + XW, y - 34), val, 40, GREY, BLACK, anchor='rm', stroke=4)
            bar(1430, 1.0, (190, 190, 185), "MOON'S SURFACE", '37.9 M KM²')
            nUS = ramp(t, k0 + 3.1, k0 + 5.0) * 3.86
            seg = XW * 9.83 / moon_a
            for i in range(4):
                fr = min(max(nUS - i, 0), 1)
                if fr * seg > 10:
                    x0 = X0 + seg * i
                    bd.rounded_rectangle((x0 + 3, 1590, x0 + seg * fr - 3, 1660), 12, fill=(60, 190, 130, 255))
                    if fr == 1: text(bd, (x0 + seg / 2, 1625), f'USA {i + 1}', 34, WHITE, BLACK, stroke=3)
            text(bd, (X0, 1556), 'ALMOST 4 × USA', 40, GREEN, BLACK, anchor='lm', stroke=4)
            text(bd, (X0 + XW, 1556), f'{nUS:.1f} ×', 40, GREY, BLACK, anchor='rm', stroke=4)
            af = ease(ramp(t, st('peel') + 5.6, st('peel') + 6.3))
            if af > 0:
                bd.rounded_rectangle((X0, 1760, X0 + XW * 30.37 / moon_a * af, 1830), 14, fill=ORANGE + (255,))
                text(bd, (X0, 1726), 'ALL OF AFRICA', 40, ORANGE, BLACK, anchor='lm', stroke=4)
                text(bd, (X0 + XW, 1726), '30.4 M KM²', 40, GREY, BLACK, anchor='rm', stroke=4)
            box.putalpha(box.getchannel('A').point(lambda v: int(v * ab)))
            im.alpha_composite(box)
        grad(im, True, 300, 200); d = ImageDraw.Draw(im, 'RGBA')
        ptext(d, (W / 2, 150), 'PEEL IT. LAY IT FLAT.', 92, WHITE, t, k0, st('russia') + 0.2)
        return im.convert('RGB')

    # ============ PLUTO's surface vs RUSSIA
    if st('russia') <= t < st('share'):
        k0 = st('russia'); s = 0.11
        ppx = D['Pluto'] * s
        draw_body(im, 'Pluto', 190, 470, s)
        sk = 2 * ppx * ease(ramp(t, k0 + 0.3, k0 + 1.5))
        if sk > 4: paste_c(im, skin('Pluto', sk), 640, 700, 1.0)
        d = ImageDraw.Draw(im, 'RGBA')
        ra = ease(ramp(t, k0 + 1.6, k0 + 2.3))
        rs = sil(RUSSIL, RUSSIL[1] * s, ra)
        paste_c(im, rs, W / 2, 1330, 1.0)
        ptext(d, (640, 700 + ppx + 50), "PLUTO'S WHOLE SURFACE · 17.7 M KM²", 38, ORANGE, t, k0 + 1.0, st('share') + 0.2)
        ptext(d, (W / 2, 1330 + rs.height / 2 + 50), 'RUSSIA · 17.1 M KM²', 46, RED, t, k0 + 2.0, st('share') + 0.2)
        grad(im, True, 330, 200); d = ImageDraw.Draw(im, 'RGBA')
        if t < st('world'):
            ptext(d, (W / 2, 160), "PLUTO'S SURFACE", 96, WHITE, t, k0, st('world'))
            ptext(d, (W / 2, 270), '≈ RUSSIA', 100, RED, t, k0 + 1.8, st('world'))
        else:
            ptext(d, (W / 2, 160), 'A WHOLE WORLD', 104, WHITE, t, st('world'), st('share') + 0.2)
            ptext(d, (W / 2, 275), '≈ ONE COUNTRY', 100, GOLD, t, st('world') + 0.9, st('share') + 0.2)
        return im.convert('RGB')
    return im.convert('RGB')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{float(tt):05.2f}.jpg', quality=88)
    elif mode == 'times':
        for k in KEYS: print(k, round(st(k), 2), round(nx(k), 2))
        print('TOTAL', TOTAL, 'US width km (proj bbox)', round(US_WKM))
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3]); n = int(round(TOTAL * FPS))
        b = min(b, n); tmp = f'part_{a:05d}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'part_{a:05d}.mp4')
        print('rendered', a, b, rc)

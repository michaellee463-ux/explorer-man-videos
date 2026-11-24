import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import *

ORANGE = (255, 140, 60)

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

def noise2(n, m, cells, seed):
    rg = np.random.default_rng(seed)
    g = rg.random((cells, int(cells * m / n) + 1)).astype(np.float32)
    return np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((m, n), Image.BICUBIC), np.float32) / 255

# ------------------------------------------------------------- Olympus Mons height model (km)
R_SHIELD, R_EDGE = 285.0, 300.0
def prof_h(r):
    r = np.abs(np.asarray(r, np.float64))
    h = np.where(r < R_SHIELD, 6 + 16 * (1 - (r / R_SHIELD) ** 1.5), 6 * np.clip((R_EDGE - r) / (R_EDGE - R_SHIELD), 0, 1))
    h -= 3.0 * np.clip((40 - r) / 14, 0, 1) ** 0.7  # caldera ~80 km wide, ~3 km deep
    return h

def everest_h(x):  # x km from peak
    x = np.abs(np.asarray(x, np.float64))
    return np.clip(8.85 * (1 - (x / 15) ** 0.8), 0, None)

# ------------------------------------------------------------- Mars sky / ground
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def sky_img(top, bot, h0=0, h1=H):
    k = np.clip((yy - h0) / (h1 - h0), 0, 1)[..., None]
    a = np.array(top) * (1 - k) + np.array(bot) * k
    return a

def make_hook():
    """heights to scale, vertical exaggeration ~13x; Everest in front of Olympus Mons"""
    S = 1.12; w, h = int(W * S), int(H * S)
    gy = int(1520 * S); vs = 40.0 * S; hs = 3.1 * S
    k = np.linspace(0, 1, h)[:, None, None]
    sky = np.array([0.03, 0.02, 0.05]) * (1 - k) ** 1.2 + np.array([0.62, 0.36, 0.22]) * (1 - (1 - k) ** 1.2)
    arr = np.repeat(sky, w, 1)
    rg = np.random.default_rng(3)
    for _ in range(500):
        x, y = rg.integers(0, w), rg.integers(0, int(h * 0.35))
        arr[y, x] += rg.uniform(0.2, 0.7) * (1 - y / (h * 0.35))
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    # dome
    cx = int(720 * S)
    xs = np.arange(w); r = (xs - cx) / hs
    top = gy - prof_h(r) * vs
    mask = Image.new('L', (w, h), 0); md = ImageDraw.Draw(mask)
    md.polygon([(0, h)] + [(int(x), float(y)) for x, y in zip(xs, top)] + [(w, h)], fill=255)
    n = noise2(h, w, 60, 5); n2 = noise2(h, w, 220, 6)
    base = np.array([0.66, 0.34, 0.18])
    shade = (0.55 + 0.35 * ((xs - cx) < 0)[None, :] * 0.0)
    rel = np.clip((yy_s := np.arange(h)[:, None] - top[None, :]) / (gy - top[None, :] + 1), 0, 1)
    tone = 0.70 + 0.22 * np.clip((cx - xs[None, :]) / (900 * S), -1, 1) + 0.18 * (1 - rel)
    col = base[None, None, :] * (tone * (0.8 + 0.25 * n + 0.15 * n2))[..., None]
    domeim = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).convert('RGBA'); domeim.putalpha(mask)
    im.alpha_composite(domeim.filter(ImageFilter.GaussianBlur(0.6)))
    # Everest (same scales)
    ex = int(210 * S); xs2 = np.arange(ex - 60 * S, ex + 60 * S); r2 = (xs2 - ex) / hs
    top2 = gy - everest_h(r2) * vs
    d = ImageDraw.Draw(im)
    pts = [(float(x), float(y)) for x, y in zip(xs2, top2)]
    d.polygon([(xs2[0], gy)] + pts + [(xs2[-1], gy)], fill=(70, 76, 92, 255))
    d.polygon([(xs2[0], gy)] + [(float(x), float(y)) for x, y in zip(xs2, top2) if x <= ex] + [(ex, gy)], fill=(110, 118, 138, 255))
    snow = [(float(x), float(y)) for x, y in zip(xs2, top2) if y < gy - 5.6 * vs]
    if snow: d.polygon(snow, fill=(240, 244, 252, 255))
    # ground
    d.rectangle((0, gy, w, h), fill=(52, 26, 16, 255))
    for i in range(0, w, 3):
        d.line((i, gy, i + rg.integers(-30, 30), h), fill=(60 + rg.integers(0, 25), 30, 18, 60))
    return im, S, gy, vs

HOOK, HS, HGY, HVS = make_hook()

def hook_scene(t, zoom=0.0, labels=1.0):
    S = HS; z = 1 + 0.07 * zoom
    w, h = int(W * S / z), int(H * S / z)
    x0 = int((W * S - w) * 0.45); y0 = int((H * S - h) * 0.8)
    im = HOOK.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)
    if labels > 0:
        d = ImageDraw.Draw(im, 'RGBA')
        def ly(km): return ((HGY - km * HVS) - y0) * H / h
        for km, s, col, x in ((8.85, 'EVEREST 8.8 KM', WHITE, 60), (22.0, 'OLYMPUS MONS ≈ 22 KM', GOLD, 420)):
            y = ly(km)
            blend(im, lambda o: [o.line((xx_, y, xx_ + 18, y), fill=tuple(col) + (int(200 * labels),), width=4) for xx_ in range(0, W, 34)])
            text(d, (x, y - 42), s, 46, col, BLACK, anchor='lm', alpha=labels)
        text(d, (W / 2, H - 60), 'heights to scale · height exaggerated ×13', 30, GREY, POP_M, stroke=3, alpha=labels)
    return im

# ------------------------------------------------------------- shaded relief map (top-down)
KMPX = 0.6                  # km per pixel (wide map)
MAPN = 3000
KMPX2, MAPN2 = 0.08, 2400   # summit map
def make_relief(n=MAPN, kmpx=KMPX, seed=11):
    y, x = (np.mgrid[0:n, 0:n].astype(np.float32) - n / 2) * kmpx
    r = np.sqrt(x * x + y * y); ang = np.arctan2(y, x)
    wob = 1 + 0.035 * np.sin(3 * ang + 0.5) + 0.02 * np.sin(7 * ang + 1.3)
    rr = r / wob
    h = prof_h(rr).astype(np.float32)
    # complex caldera: several nested collapse pits (overall ~60 x 80 km)
    h = h + 3.0 * np.clip((40 - rr) / 14, 0, 1) ** 0.7   # remove simple caldera
    for (cx, cy, rad, dep) in ((-8, -4, 32, 2.2), (14, 10, 22, 2.8), (-18, 14, 14, 3.0), (6, -18, 12, 2.5), (20, -6, 10, 3.0)):
        rc = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        h = np.minimum(h, np.where(rc < rad, 22 - dep + 0.15 * (rc / rad) ** 4, 99))
        h = h - 0.6 * np.exp(-((rc - rad) / 1.2) ** 2) * (rc > rad - 2) * 0
    # radial lava-flow texture
    nr = noise2(n, n, max(20, int(n * kmpx / 6)), seed)
    rad_tex = (np.sin(ang * 140 + nr * 9) * 0.5 + 0.5) * np.clip((rr - 45) / 40, 0, 1) * (rr < R_SHIELD)
    h = h + 0.05 * (kmpx / 0.6) * rad_tex + 0.10 * (kmpx / 0.6) ** 0.3 * noise2(n, n, max(12, int(n * kmpx / 8)), seed + 1) * (rr < R_EDGE)
    # aureole: lobate rough terrain outside
    au = noise2(n, n, max(8, int(n * kmpx / 40)), seed + 2) * noise2(n, n, max(20, int(n * kmpx / 12)), seed + 3)
    lobe = np.clip(1 - (rr - R_EDGE) / (350 + 250 * (0.5 + 0.5 * np.sin(2 * ang + 2.2))), 0, 1) * (rr >= R_EDGE)
    h = h + lobe * (0.6 + 1.2 * au) + 0.12 * noise2(n, n, max(30, int(n * kmpx / 4)), seed + 4)
    # hillshade
    gy_, gx_ = np.gradient(h, kmpx)
    L = np.array([-0.6, -0.6, 0.53]); L /= np.linalg.norm(L)
    ex = 18.0 * (kmpx / 0.6) ** 0.6
    nx_, ny_, nz_ = -gx_ * ex, -gy_ * ex, np.ones_like(h)
    nn = np.sqrt(nx_ ** 2 + ny_ ** 2 + nz_ ** 2)
    sh = np.clip((nx_ * L[0] + ny_ * L[1] + nz_ * L[2]) / nn, 0, 1)
    hk = np.clip(h / 22, 0, 1)[..., None]
    low = np.array([0.55, 0.27, 0.14]); hi = np.array([0.86, 0.62, 0.42])
    col = low * (1 - hk) + hi * hk
    col = col * (0.25 + 0.95 * sh[..., None])
    return Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

if os.path.exists('relief.png'): REL = Image.open('relief.png').convert('RGBA')
else:
    REL = make_relief(); REL.save('relief.png')
if os.path.exists('relief2.png'): REL2 = Image.open('relief2.png').convert('RGBA')
else:
    REL2 = make_relief(MAPN2, KMPX2, 11); REL2.save('relief2.png')

def relief_view(cx_km, cy_km, km_per_screen_w):
    """view of the relief map centred at (cx,cy) km, showing km_per_screen_w across the screen width"""
    half = MAPN2 * KMPX2 / 2; hw = km_per_screen_w / 2; hh = hw * H / W
    if abs(cx_km) + hw <= half and abs(cy_km) + hh <= half: src, kp, n = REL2, KMPX2, MAPN2
    else: src, kp, n = REL, KMPX, MAPN
    pxw = km_per_screen_w / kp; pxh = pxw * H / W
    cxp = n / 2 + cx_km / kp; cyp = n / 2 + cy_km / kp
    box = (cxp - pxw / 2, cyp - pxh / 2, cxp + pxw / 2, cyp + pxh / 2)
    return src.transform((W, H), Image.EXTENT, box, Image.BILINEAR, fillcolor=(40, 20, 12, 255))

def km2px(km, km_per_screen_w): return km * W / km_per_screen_w

# Arizona outline (lon, lat) -> km, approximate state border
AZ = [(-114.05, 37.0), (-109.05, 37.0), (-109.05, 31.33), (-111.07, 31.33), (-114.81, 32.49), (-114.72, 32.72), (-114.53, 33.03),
      (-114.70, 33.41), (-114.52, 33.69), (-114.53, 34.0), (-114.13, 34.27), (-114.43, 34.80), (-114.63, 35.12), (-114.57, 35.53),
      (-114.75, 36.09), (-114.05, 36.19)]
def az_km():
    lat0 = 34.2; lon0 = -111.7; c = math.cos(math.radians(lat0))
    pts = [((lo - lon0) * 111.32 * c, -(la - lat0) * 110.57) for lo, la in AZ]
    # area check via shoelace
    a = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
    mx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2; my = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    return [(x - mx, y - my) for x, y in pts], a
AZP, AZ_AREA = az_km()

# ------------------------------------------------------------- Mars globe
def mars_globe(R):
    def mk():
        s = sphere(R, (0.74, 0.36, 0.19), 9, rough=0.55)
        d = ImageDraw.Draw(s, 'RGBA')
        return s
    return sp(('mars', R), mk)

# ------------------------------------------------------------- first-person Mars surface
def make_surface():
    hy = 820
    k = np.clip(yy / hy, 0, 1)[..., None]
    sky = np.array([0.42, 0.27, 0.20]) * (1 - k) + np.array([0.86, 0.66, 0.48]) * k
    arr = sky.copy()
    g = yy > hy
    z = 260.0 / np.maximum(yy - hy, 1)                       # depth
    u = (xx - W / 2) * z / 300
    n1 = noise2(H, W, 50, 21); n2 = noise2(H, W, 200, 22)
    tex = 0.5 * np.sin(u * 3 + z * 2.1) * 0 + n1 * 0.5 + n2 * 0.5
    fade_ = np.clip(1 - z / 20, 0, 1)[..., None]
    ground = np.array([0.62, 0.34, 0.19]) * (0.75 + 0.35 * tex[..., None])
    hazec = np.array([0.80, 0.58, 0.42])
    ground = ground * fade_ + hazec * (1 - fade_)
    arr[g] = ground[g]
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA'); rg = np.random.default_rng(8)
    for _ in range(260):
        y = hy + (H - hy) * rg.random() ** 2.2 + 2
        s = (y - hy) / (H - hy)
        x = rg.uniform(-50, W + 50); rw = rg.uniform(4, 40) * s * 3 + 1; rh = rw * rg.uniform(0.35, 0.6)
        d.ellipse((x - rw, y - rh, x + rw, y + rh * 0.4), fill=(40, 20, 12, 200))
        d.ellipse((x - rw * 0.9, y - rh * 1.1, x + rw * 0.7, y), fill=(120, 66, 38, 255))
    return im, hy
SURF, SURF_HY = make_surface()

def astronaut(d, x, y, s, a=1.0):
    c = (235, 238, 245, int(255 * a)); dk = (60, 70, 90, int(255 * a))
    d.ellipse((x - 28 * s, y - 250 * s, x + 28 * s, y - 194 * s), fill=c)
    d.ellipse((x - 16 * s, y - 236 * s, x + 18 * s, y - 210 * s), fill=(200, 150, 60, int(255 * a)))
    d.rounded_rectangle((x - 40 * s, y - 196 * s, x + 40 * s, y - 90 * s), 18 * s, fill=c)
    d.rounded_rectangle((x - 56 * s, y - 190 * s, x - 34 * s, y - 100 * s), 10 * s, fill=c)
    d.rounded_rectangle((x + 34 * s, y - 190 * s, x + 56 * s, y - 100 * s), 10 * s, fill=c)
    d.rounded_rectangle((x - 36 * s, y - 95 * s, x - 6 * s, y), 10 * s, fill=c)
    d.rounded_rectangle((x + 6 * s, y - 95 * s, x + 36 * s, y), 10 * s, fill=c)
    d.rectangle((x - 30 * s, y - 180 * s, x + 30 * s, y - 150 * s), fill=dk)

def jet(d, x, y, s, col=(235, 240, 250, 255)):
    d.polygon([(x - 60 * s, y), (x + 60 * s, y - 6 * s), (x + 70 * s, y), (x + 60 * s, y + 6 * s)], fill=col)
    d.polygon([(x - 5 * s, y), (x + 20 * s, y), (x - 15 * s, y + 40 * s), (x - 30 * s, y + 40 * s)], fill=col)
    d.polygon([(x - 5 * s, y), (x + 20 * s, y), (x - 15 * s, y - 40 * s), (x - 30 * s, y - 40 * s)], fill=col)
    d.polygon([(x - 60 * s, y), (x - 45 * s, y), (x - 58 * s, y - 22 * s), (x - 66 * s, y - 22 * s)], fill=col)

# ------------------------------------------------------------- profile drawing (generic)
def draw_profile(im, cx, gy, hs, vs, col=(178, 92, 48), everest_x=None, alpha=1.0):
    d = ImageDraw.Draw(im, 'RGBA')
    xs = np.arange(-20, W + 20, 2); r = (xs - cx) / hs
    top = gy - prof_h(r) * vs
    d.polygon([(xs[0], gy)] + [(float(x), float(y)) for x, y in zip(xs, top)] + [(xs[-1], gy)], fill=tuple(col) + (int(255 * alpha),))
    if everest_x is not None:
        xs2 = np.arange(everest_x - 16 * hs, everest_x + 16 * hs + 1, 1); t2 = gy - everest_h((xs2 - everest_x) / hs) * vs
        d.polygon([(xs2[0], gy)] + [(float(x), float(y)) for x, y in zip(xs2, t2)] + [(xs2[-1], gy)], fill=(200, 210, 230, int(255 * alpha)))

# ------------------------------------------------------------- plate tectonics diagram
def plate_scene(im0, t, t0, moving):
    rgb = im0.convert('RGB'); _plate(rgb, t, t0, moving); im0.paste(rgb.convert('RGBA'), (0, 0))

def _plate(im, t, t0, moving):
    d = ImageDraw.Draw(im, 'RGBA')
    top_y, plate_y, mantle_y = 900, 1180, 1300
    if moving:
        d.rectangle((0, 560, W, plate_y), fill=(20, 60, 130, 255))       # ocean
        for i in range(8): d.line((0, 600 + i * 70, W, 600 + i * 70), fill=(40, 90, 170, 120), width=2)
    d.rectangle((0, plate_y, W, mantle_y), fill=(110, 70, 45, 255))     # plate / crust
    for y in range(mantle_y, H, 6):
        k = (y - mantle_y) / (H - mantle_y)
        d.line((0, y, W, y), fill=(int(150 + 60 * k), int(50 + 20 * k), 25, 255))
    hx = 640
    pulse = 0.85 + 0.15 * math.sin(t * 6)
    for k in range(10):
        w_ = 70 - k * 4
        d.ellipse((hx - w_, H - 80 - k * 55 - w_, hx + w_, H - 80 - k * 55 + w_), fill=(255, int(120 + k * 10), 40, int(120 * pulse)))
    d.polygon([(hx - 30, mantle_y + 10), (hx + 30, mantle_y + 10), (hx + 70, H), (hx - 70, H)], fill=(255, 150, 50, 150))
    el = max(0.0, t - t0)
    if moving:
        speed = 70.0; period = 1.3
        n_ = int(el / period) + 1
        for i in range(n_):
            born = i * period; age = el - born
            x = hx - age * speed
            if x < -150: continue
            g = min(1.0, age / 0.9)
            hh = (170 * g) * max(0.25, 1 - age / 12)
            ww = 90 + 0.5 * hh
            d.polygon([(x - ww, plate_y), (x + ww, plate_y), (x + 18, plate_y - hh), (x - 18, plate_y - hh)], fill=(90, 70, 55, 255))
            if age < 1.5:
                d.ellipse((x - 14, plate_y - hh - 14, x + 14, plate_y - hh + 8), fill=(255, 120, 40, int(220 * (1 - age / 1.5))))
        d.line((hx + 200, plate_y + 60, hx - 60, plate_y + 60), fill=(255, 255, 255, 230), width=8)
        d.polygon([(hx - 90, plate_y + 60), (hx - 50, plate_y + 40), (hx - 50, plate_y + 80)], fill=(255, 255, 255, 230))
    else:
        g = ease(ramp(el, 0.2, 4.6))
        hh = 140 + 560 * g; ww = 260 + 900 * g
        xs = np.linspace(hx - ww, hx + ww, 200)
        ys = plate_y - hh * (1 - (np.abs(xs - hx) / ww) ** 1.5)
        d.polygon([(float(x), float(y)) for x, y in zip(xs, ys)] + [(hx + ww, plate_y), (hx - ww, plate_y)], fill=(176, 92, 48, 255))
        for k in range(5):
            f = (el * 0.5 + k / 5) % 1.0
            yk = plate_y - hh * f
            d.ellipse((hx - 18, yk - 18, hx + 18, yk + 18), fill=(255, 130, 40, int(200 * (1 - f))))
        d.rectangle((hx - 40, plate_y - 4, hx + 40, plate_y + 120), fill=(255, 110, 40, 140))

# ------------------------------------------------------------- frame
def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255))

    # ============ HOOK (t=0 already fully composed, no fade-in)
    if t < nx('hook') + 0.3:
        im = hook_scene(t, zoom=t / 7.0)
        d = ImageDraw.Draw(im, 'RGBA'); grad(im, True, 560, 200); d = ImageDraw.Draw(im, 'RGBA')
        text(d, (W / 2, 190), '2.5× EVEREST', 136, GOLD, BLACK)
        ptext(d, (W / 2, 350), "…YOU MIGHT NOT", 92, WHITE, t, st('hook') + 3.6, 99)
        ptext(d, (W / 2, 460), "EVEN NOTICE IT", 92, CYAN, t, st('hook') + 3.9, 99)
        a_out = ramp(t, nx('hook') - 0.1, nx('hook') + 0.3)
        if a_out > 0: im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * a_out))))

    # ============ NAME: Mars globe zoom
    a = xf(t, st('name') - 0.1, nx('name') + 0.3, 0.25, 0.3)
    if a > 0:
        lay = BG.copy(); p = ramp(t, st('name'), nx('name'))
        R = int(380 + 160 * ease(p))
        g = mars_globe(R)
        cx, cy = 540 + 120 * ease(p), 1050 + 60 * ease(p)
        paste_c(lay, g, cx, cy)
        d = ImageDraw.Draw(lay, 'RGBA')
        ox, oy = cx - 0.42 * R, cy - 0.22 * R
        rr = 26 + 10 * math.sin(t * 5)
        d.ellipse((ox - 22, oy - 22, ox + 22, oy + 22), fill=(230, 170, 110, 255))
        d.ellipse((ox - 8, oy - 8, ox + 8, oy + 8), fill=(120, 60, 30, 255))
        d.ellipse((ox - rr - 20, oy - rr - 20, ox + rr + 20, oy + rr + 20), outline=GOLD + (255,), width=7)
        grad(lay, True, 620, 220); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 200), 'OLYMPUS MONS', 128, GOLD, t, st('name') + 0.1, 99)
        ptext(d, (W / 2, 330), 'ON MARS', 100, WHITE, t, st('name') + 0.7, 99)
        grad(lay, False, 520, 220); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 1600), 'BIGGEST VOLCANO', 100, WHITE, t, st('name') + 1.8, 99)
        ptext(d, (W / 2, 1720), 'IN THE SOLAR SYSTEM', 80, ORANGE, t, st('name') + 2.2, 99)
        im.alpha_composite(fade(lay, a))

    # ============ HEIGHT: altitude ruler, Everest, jets, summit
    a = xf(t, st('height') - 0.1, nx('height') + 0.3, 0.25, 0.3)
    if a > 0:
        lay = Image.fromarray((np.clip(sky_img((0.02, 0.02, 0.05), (0.55, 0.32, 0.2)), 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        gy = 1640; vs = 48.0; p = ease(ramp(t, st('height') + 0.1, st('height') + 2.6))
        draw_profile(lay, 760, gy, 1.8, vs * p, col=(190, 98, 52), everest_x=230)
        d = ImageDraw.Draw(lay, 'RGBA'); d.rectangle((0, gy, W, H), fill=(50, 25, 15, 255))
        for km in range(0, 25, 5):
            y = gy - km * vs
            d.line((40, y, 80, y), fill=(255, 255, 255, 200), width=4)
            text(d, (95, y), f'{km} KM', 34, GREY, POP_B, anchor='lm', stroke=3)
        d.line((60, gy, 60, gy - 24 * vs), fill=(255, 255, 255, 120), width=3)
        hk = 22 * p
        if p > 0.02: text(d, (760, gy - hk * vs - 60), f'{hk:4.1f} KM', 78, GOLD, BLACK)
        ja = ease(ramp(t, st('height') + 3.0, st('height') + 3.5))
        if ja > 0:
            jy = gy - 10.7 * vs; jx = -150 + (W + 300) * ramp(t, st('height') + 2.9, nx('height') + 1.0)
            jet(d, jx, jy, 1.2)
            blend(lay, lambda o: [o.line((xx_, jy, xx_ + 18, jy), fill=(140, 220, 255, int(200 * ja)), width=3) for xx_ in range(0, W, 34)])
            text(d, (W - 40, jy - 50), 'PASSENGER JETS ≈ 11 KM', 44, CYAN, BLACK, anchor='rm', alpha=ja)
        text(d, (330, gy - 8.85 * vs + 40), 'EVEREST', 40, WHITE, BLACK, alpha=ease(ramp(t, st('height') + 0.6, st('height') + 1.0)))
        grad(lay, True, 420, 200); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 170), '2× AS HIGH', 130, GOLD, t, st('height') + 3.4, 99)
        ptext(d, (W / 2, 300), 'AS JETS FLY', 96, WHITE, t, st('height') + 3.7, 99)
        im.alpha_composite(fade(lay, a))

    # ============ WIDE: top-down relief, 600 km + Arizona
    a = xf(t, st('wide') - 0.1, nx('wide') + 0.3, 0.25, 0.3)
    if a > 0:
        p = ease(ramp(t, st('wide'), st('wide') + 2.2))
        kw = 260 + (820 - 260) * p
        lay = relief_view(0, 40, kw)
        d = ImageDraw.Draw(lay, 'RGBA'); cyc = H / 2 - km2px(40, kw)
        aw = ease(ramp(t, st('wide') + 1.8, st('wide') + 2.4))
        if aw > 0:
            x0, x1 = W / 2 - km2px(300, kw), W / 2 + km2px(300, kw); yb = cyc + km2px(300, kw) + 60
            blend(lay, lambda o: [o.line(l, fill=(255, 255, 255, int(255 * aw)), width=8) for l in ((x0, yb, x1, yb), (x0, yb - 30, x0, yb + 30), (x1, yb - 30, x1, yb + 30))])
            text(d, (W / 2, yb + 70), '≈ 600 KM WIDE', 84, GOLD, BLACK, alpha=aw)
        aa = ease(ramp(t, st('wide') + 3.3, st('wide') + 3.8))
        if aa > 0:
            pts = [(W / 2 + km2px(x, kw), cyc + km2px(y, kw)) for x, y in AZP]
            blend(lay, lambda o: (o.polygon(pts, fill=(90, 160, 255, int(70 * aa))), o.line(pts + [pts[0]], fill=(120, 200, 255, int(255 * aa)), width=7)))
        grad(lay, True, 520, 215); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 190), 'THE REAL SHOCK:', 92, WHITE, t, st('wide') + 0.1, 99)
        ptext(d, (W / 2, 320), 'ITS WIDTH', 128, ORANGE, t, st('wide') + 0.5, st('wide') + 3.4)
        ptext(d, (W / 2, 320), '≈ SIZE OF ARIZONA', 100, CYAN, t, st('wide') + 3.4, 99)
        im.alpha_composite(fade(lay, a))

    # ============ SCALE: squash vertical exaggeration down to true scale
    a = xf(t, st('scale') - 0.1, nx('scale') + 0.3, 0.25, 0.3)
    if a > 0:
        lay = Image.fromarray((np.clip(sky_img((0.02, 0.02, 0.05), (0.40, 0.22, 0.15), 0, 1300), 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        hs = 1000 / 600.0
        p = ease(ramp(t, st('scale') + 0.4, st('scale') + 2.6))
        ex = 13 * (1 - p) + 1 * p
        gy = 1150
        draw_profile(lay, 540, gy, hs, hs * ex, everest_x=None)
        d = ImageDraw.Draw(lay, 'RGBA'); d.rectangle((0, gy, W, H), fill=(50, 25, 15, 255))
        # Everest to the same true scale
        xs2 = np.arange(40 - 16 * hs, 40 + 16 * hs + 1, 0.5)
        if p > 0.95:
            pe = ease(ramp(t, st('scale') + 2.8, st('scale') + 3.2))
            for km_x in np.arange(-15, 15.01, 0.25):
                pass
            ehs = hs; xsE = np.arange(940 - 16 * ehs, 940 + 16 * ehs + 1, 0.5)
            tE = gy - everest_h((xsE - 940) / ehs) * ehs
            d.polygon([(xsE[0], gy)] + [(float(x), float(y)) for x, y in zip(xsE, tE)] + [(xsE[-1], gy)], fill=(220, 228, 245, int(255 * pe)))
            text(d, (940, gy - 70), 'EVEREST', 38, WHITE, BLACK, alpha=pe)
        lab = 'HEIGHT ×%d' % round(ex) if ex > 1.05 else 'TRUE SCALE'
        pill(d, W / 2, gy + 140, lab, 54, (200, 60, 40) if ex > 1.05 else (30, 140, 70))
        grad(lay, True, 520, 210); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 190), 'OVER 20×', 150, GOLD, t, st('scale') + 2.4, 99)
        ptext(d, (W / 2, 340), 'WIDER THAN TALL', 92, WHITE, t, st('scale') + 2.8, 99)
        grad(lay, False, 420, 200); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 1640), 'A GIANT, GENTLE DOME', 80, CYAN, t, en('scale') - 1.6, 99)
        im.alpha_composite(fade(lay, a))

    # ============ CLIFF + CRATER: zooms into the relief
    a = xf(t, st('cliff') - 0.1, nx('crater') + 0.3, 0.25, 0.3)
    if a > 0:
        if t < st('crater'):
            p = ease(ramp(t, st('cliff') - 0.1, nx('cliff')))
            cxk, cyk = -60 - 160 * p, 0 + 160 * p; kw = 700 - 380 * p
        else:
            p = ease(ramp(t, st('crater') - 0.2, st('crater') + 2.2))
            cxk, cyk = -220 * (1 - p), 160 * (1 - p); kw = 320 - 215 * p
        lay = relief_view(cxk, cyk, kw)
        d = ImageDraw.Draw(lay, 'RGBA')
        grad(lay, True, 520, 215); d = ImageDraw.Draw(lay, 'RGBA')
        if t < st('crater'):
            ptext(d, (W / 2, 190), 'A WALL OF CLIFFS', 104, WHITE, t, st('cliff'), nx('cliff') + 0.1)
            ptext(d, (W / 2, 320), 'KILOMETERS HIGH', 104, ORANGE, t, st('cliff') + 0.5, nx('cliff') + 0.1)
        else:
            ca = ease(ramp(t, st('crater') + 1.6, st('crater') + 2.2))
            if ca > 0:
                ccx, ccy = W / 2 + km2px(-4 - cxk, kw), H / 2 + km2px(1 - cyk, kw); rr = km2px(40, kw)
                blend(lay, lambda o: o.ellipse((ccx - rr, ccy - rr * 0.85, ccx + rr, ccy + rr * 0.85), outline=GOLD + (int(255 * ca),), width=8))
            ptext(d, (W / 2, 190), 'CRATER ≈ 80 KM WIDE', 92, GOLD, t, st('crater') + 1.6, 99)
            ptext(d, (W / 2, 320), '≈ 3 KM DEEP', 110, WHITE, t, st('crater') + 3.0, 99)
        im.alpha_composite(fade(lay, a))

    # ============ TEASE
    a = xf(t, st('tease') - 0.1, nx('tease') + 0.2, 0.15, 0.2)
    if a > 0:
        sh = 14 * math.exp(-(t - st('tease')) * 6) * math.sin(t * 80) if t > st('tease') else 0
        lay = relief_view(10 + sh, 0, 900)
        lay.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 120)))
        d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 820), "BUT THAT'S NOT", 110, WHITE, t, st('tease'), 99)
        ptext(d, (W / 2, 960), 'THE CRAZIEST', 130, RED, t, st('tease') + 0.3, 99)
        ptext(d, (W / 2, 1100), 'PART', 130, RED, t, st('tease') + 0.5, 99)
        im.alpha_composite(fade(lay, a))

    # ============ EARTH: plates drift over a hotspot -> chain
    a = xf(t, st('earth') - 0.1, nx('earth') + 0.25, 0.25, 0.25)
    if a > 0:
        lay = Image.fromarray((np.clip(sky_img((0.05, 0.10, 0.22), (0.35, 0.55, 0.80), 0, 560), 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        plate_scene(lay, t, st('earth') + 1.0, True)
        d = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 520, 200); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 180), 'EARTH', 130, CYAN, t, st('earth'), 99)
        ptext(d, (W / 2, 320), 'GROUND DRIFTS', 96, WHITE, t, st('earth') + 1.6, 99)
        ptext(d, (W / 2, 430), 'OVER A HOT SPOT', 80, ORANGE, t, st('earth') + 2.2, 99)
        ptext(d, (W / 2, 1440), '→ A CHAIN: HAWAII', 82, WHITE, t, st('earth') + 3.8, 99)
        im.alpha_composite(fade(lay, a))

    # ============ MARS: fixed crust -> one giant
    a = xf(t, st('mars') - 0.1, nx('mars') + 0.25, 0.25, 0.25)
    if a > 0:
        lay = Image.fromarray((np.clip(sky_img((0.05, 0.03, 0.06), (0.70, 0.45, 0.30), 0, 1180), 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        plate_scene(lay, t, st('mars'), False)
        d = ImageDraw.Draw(lay, 'RGBA'); grad(lay, True, 520, 200); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 180), 'MARS', 130, ORANGE, t, st('mars'), 99)
        ptext(d, (W / 2, 320), 'CRUST STAYS PUT', 96, WHITE, t, st('mars') + 0.7, 99)
        ptext(d, (W / 2, 430), 'LAVA PILES UP', 86, GOLD, t, st('mars') + 2.0, 99)
        ptext(d, (W / 2, 1460), '+ WEAKER GRAVITY', 86, CYAN, t, st('mars') + 4.0, 99)
        im.alpha_composite(fade(lay, a))

    # ============ REVEAL: first-person near the summit
    a = xf(t, st('reveal') - 0.1, nx('reveal') + 0.3, 0.3, 0.3)
    if a > 0:
        p = ramp(t, st('reveal'), nx('reveal'))
        z = 1.0 + 0.06 * p
        w_, h_ = int(W / z), int(H / z)
        lay = SURF.crop(((W - w_) // 2, (H - h_) // 2, (W - w_) // 2 + w_, (H - h_) // 2 + h_)).resize((W, H), Image.BILINEAR)
        d = ImageDraw.Draw(lay, 'RGBA')
        astronaut(d, 250, 1800, 1.5)
        hyz = (SURF_HY - (H - h_) // 2) * z
        ha = ease(ramp(t, st('reveal') + 4.0, st('reveal') + 4.5))
        if ha > 0:
            blend(lay, lambda o: [o.line((xx_, hyz, xx_ + 22, hyz), fill=(255, 255, 255, int(230 * ha)), width=5) for xx_ in range(0, W, 40)])
            text(d, (W / 2, hyz - 60), 'HORIZON ≈ 3 KM AWAY', 70, WHITE, BLACK, alpha=ha)
        grad(lay, True, 520, 190); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 180), 'NEAR THE TOP', 110, GOLD, t, st('reveal') + 0.1, 99)
        ptext(d, (W / 2, 310), 'JUST A GENTLE SLOPE', 80, WHITE, t, st('reveal') + 1.6, 99)
        # inset: how small 3 km is against the 600 km dome (true scale)
        ia = ease(ramp(t, st('reveal') + 5.2, st('reveal') + 5.7))
        if ia > 0:
            box = Image.new('RGBA', (980, 300), (10, 8, 14, 215)); bd = ImageDraw.Draw(box, 'RGBA')
            hs = 900 / 600.0; gy = 230
            xs = np.arange(40, 941, 1); top = gy - prof_h((xs - 490) / hs) * hs * 4
            bd.polygon([(40, gy)] + [(float(x), float(y)) for x, y in zip(xs, top)] + [(940, gy)], fill=(178, 92, 48, 255))
            px = 490 + 70 * hs; py = gy - prof_h(70) * hs * 4
            rr = 3 * hs
            bd.ellipse((px - 14, py - 14, px + 14, py + 14), outline=CYAN + (255,), width=4)
            text(bd, (px, py - 50), 'YOU SEE ~3 KM', 34, CYAN, BLACK)
            text(bd, (490, 268), '600 KM WIDE  (height ×4)', 30, GREY, POP_B, stroke=3)
            box.putalpha(box.getchannel('A').point(lambda v: int(v * ia)))
            lay.alpha_composite(box, (50, 930))
        im.alpha_composite(fade(lay, a))

    # ============ NEVER: pull back to the whole volcano
    a = xf(t, st('never') - 0.1, nx('never') + 0.25, 0.3, 0.25)
    if a > 0:
        p = ease(ramp(t, st('never'), nx('never')))
        lay = relief_view(-60 * (1 - p), 30 * (1 - p), 100 + 920 * p)
        d = ImageDraw.Draw(lay, 'RGBA')
        dk = ease(ramp(t, st('never') + 0.3, st('never') + 0.8))
        grad(lay, True, 560, 220); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 180), 'BIGGEST VOLCANO', 104, WHITE, t, st('never') + 0.2, 99)
        ptext(d, (W / 2, 300), 'IN THE SOLAR SYSTEM', 78, ORANGE, t, st('never') + 0.6, 99)
        grad(lay, False, 520, 220); d = ImageDraw.Draw(lay, 'RGBA')
        ptext(d, (W / 2, 1620), '…AND YOU MIGHT', 92, WHITE, t, st('never') + 2.4, 99)
        ptext(d, (W / 2, 1740), 'NOT EVEN KNOW', 100, CYAN, t, st('never') + 2.8, 99)
        im.alpha_composite(fade(lay, a))

    # ============ SHARE + COMMENT, loops into the opening
    a = xf(t, st('share') - 0.1, TOTAL + 1, 0.3, 0.01)
    if a > 0:
        lay = hook_scene(t, zoom=0.0, labels=0.0)
        lp = ramp(t, TOTAL - 0.7, TOTAL); ca = 1 - ease(lp)
        grad(lay, True, 640, 220); d = ImageDraw.Draw(lay, 'RGBA')
        if t < st('comment'):
            ptext(d, (W / 2, 180), 'SEND THIS TO SOMEONE', 76, WHITE, t, st('share'), st('comment'))
            ptext(d, (W / 2, 300), 'WHO THINKS EVEREST', 90, WHITE, t, st('share') + 0.3, st('comment'))
            ptext(d, (W / 2, 420), 'IS THE TALLEST', 110, GOLD, t, st('share') + 0.7, st('comment'))
        else:
            text(d, (W / 2, 200), 'WOULD YOU', 120, WHITE, BLACK, alpha=ca)
            text(d, (W / 2, 340), 'CLIMB IT?', 140, GOLD, BLACK, alpha=ca)
            pa = ease(ramp(t, st('comment') + 0.5, st('comment') + 0.8)) * ca
            pill(d, 330, 600, 'YES', 80, (30, 150, 70), alpha=pa)
            pill(d, 750, 600, 'NO', 80, (205, 30, 40), alpha=pa)
        if lp > 0:
            text(d, (W / 2, 190), '2.5× EVEREST', 136, GOLD, BLACK, alpha=ease(lp))
        im.alpha_composite(fade(lay, a))
    return im.convert('RGB')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for tt in sys.argv[2:]: frame(float(tt)).save(f'still_{float(tt):05.2f}.jpg', quality=88)
    elif mode == 'times':
        for k in KEYS: print(k, round(st(k), 2), round(nx(k), 2))
        print('TOTAL', TOTAL, 'AZ area km2', round(AZ_AREA))
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3]); n = int(round(TOTAL * FPS))
        b = min(b, n); tmp = f'part_{a:05d}.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); rc = p.wait()
        if rc == 0: os.rename(tmp, f'part_{a:05d}.mp4')
        print('rendered', a, b, rc)

# textures, spheres and maps for the Moon-vs-USA Short (all sizes from NASA diameters / Natural Earth outlines)
import json, math, os, pickle
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pyproj import Transformer

D = dict(Moon=3474.8, Ceres=939.4, Pluto=2376.6, Mercury=4879.4, Ganymede=5268.2, Mars=6779.0, Earth=12742.0)
HERE = os.path.dirname(os.path.abspath(__file__))
ST = json.load(open(os.path.join(HERE, 'states.geojson')))
CO = json.load(open(os.path.join(HERE, 'countries.geojson')))

def rings(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]

def proj(kind, lat, lon):
    t = Transformer.from_crs('EPSG:4326', f'+proj={kind} +lat_0={lat} +lon_0={lon} +units=km', always_xy=True)
    return lambda ring: np.array(t.transform([p[0] for p in ring], [p[1] for p in ring])).T

LOWER48 = [f for f in ST['features'] if f['properties'].get('iso_a2') == 'US' and f['properties']['name'] not in ('Alaska', 'Hawaii')]
def country(name): return [f for f in CO['features'] if f['properties']['NAME'] == name][0]
US_P = proj('aeqd', 39.5, -98.5)

# ------------------------------------------------------------------ noise
def vnoise(h, w, cells, seed):
    rg = np.random.default_rng(seed)
    g = rg.random((cells, cells * 2 + 1)).astype(np.float32)
    g[:, -1] = g[:, 0]
    return np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
def fbm(h, w, seed, octs=((6, .5), (14, .25), (34, .15), (80, .1))):
    v = sum(a * vnoise(h, w, c, seed + i) for i, (c, a) in enumerate(octs))
    k = np.cos((0.5 - (np.arange(h) + 0.5) / h) * np.pi)[:, None] ** 0.6
    return 0.5 + (v - 0.5) * k

TH, TW = 768, 1536
LAT = (0.5 - (np.arange(TH) + 0.5) / TH)[:, None] * np.pi
LON = ((np.arange(TW) + 0.5) / TW * 2 - 1)[None, :] * np.pi

def craters(tex, n, seed, rmin=0.006, rmax=0.08, depth=0.25, rays=0):
    rg = np.random.default_rng(seed)
    X = np.cos(LAT) * np.cos(LON); Y = np.cos(LAT) * np.sin(LON); Z = np.sin(LAT) * np.ones_like(LON)
    for i in range(n):
        r = rmin * (rmax / rmin) ** (rg.random() ** 2.2)
        la = np.arcsin(rg.uniform(-1, 1)); lo = rg.uniform(-np.pi, np.pi)
        cx, cy, cz = math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)
        dot = X * cx + Y * cy + Z * cz
        m = dot > math.cos(r * 1.6)
        if not m.any(): continue
        ang = np.arccos(np.clip(dot[m], -1, 1)) / r
        floor = np.where(ang < 0.85, -depth * (1 - (ang / 0.85) ** 2) * 0.6, 0)
        rim = depth * 0.35 * np.exp(-((ang - 0.97) / 0.10) ** 2)
        tex[m] *= (1 + floor + rim)[:, None]
        if i < rays:
            ray = np.exp(-((ang - 1) / 3.5) ** 2) * 0
    return tex

def tex_moon():
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.66, 0.65, 0.63])
    n = fbm(TH, TW, 11); t *= (0.78 + 0.4 * n)[..., None]
    # maria mostly on the near side (lon ~ 0), dark basaltic plains
    mare = np.zeros((TH, TW), np.float32); rg = np.random.default_rng(4)
    for la, lo, r in [(0.55, -0.25, 0.32), (0.3, 0.3, 0.2), (0.15, 0.55, 0.16), (-0.15, 0.6, 0.14), (-0.3, -0.05, 0.18), (0.05, -0.75, 0.36), (0.6, 0.2, 0.14), (-0.45, -0.45, 0.12), (0.25, 0.9, 0.1)]:
        dd = np.arccos(np.clip(np.sin(LAT) * math.sin(la) + np.cos(LAT) * math.cos(la) * np.cos(LON - lo), -1, 1))
        mare = np.maximum(mare, np.clip(1 - dd / r, 0, 1) ** 0.5)
    mare *= np.clip(0.6 + 0.8 * (fbm(TH, TW, 21) - 0.5), 0, 1) > 0.3
    mare = np.array(Image.fromarray((mare * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    t = t * (1 - 0.42 * mare[..., None])
    t = craters(t, 420, 7, depth=0.22)
    # Tycho-like bright ray crater
    dd = np.arccos(np.clip(np.sin(LAT) * math.sin(-0.75) + np.cos(LAT) * math.cos(-0.75) * np.cos(LON + 0.2), -1, 1))
    t += (0.25 * np.exp(-(dd / 0.03) ** 2) + 0.06 * np.exp(-(dd / 0.35) ** 2) * (vnoise(TH, TW, 90, 3) > 0.6))[..., None]
    return np.clip(t, 0, 1)

def tex_mercury():
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.60, 0.56, 0.52])
    t *= (0.7 + 0.5 * fbm(TH, TW, 31))[..., None]
    t = craters(t, 700, 9, depth=0.3)
    return np.clip(t, 0, 1)

def tex_ceres():
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.40, 0.39, 0.38])
    t *= (0.75 + 0.45 * fbm(TH, TW, 41))[..., None]
    t = craters(t, 380, 13, rmax=0.12, depth=0.35)
    dd = np.arccos(np.clip(np.sin(LAT) * math.sin(0.35) + np.cos(LAT) * math.cos(0.35) * np.cos(LON - 0.2), -1, 1))
    t += 0.55 * np.exp(-(dd / 0.018) ** 2)[..., None]  # Occator's bright spot
    return np.clip(t, 0, 1)

def tex_pluto():
    n = fbm(TH, TW, 51)
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.78, 0.62, 0.46]) * (0.8 + 0.35 * n)[..., None]
    band = np.clip(1 - np.abs(LAT + 0.12) / 0.28, 0, 1) * (vnoise(TH, TW, 12, 5) > 0.42)
    band = np.array(Image.fromarray((band * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    t = t * (1 - band[..., None]) + np.array([0.33, 0.17, 0.11]) * band[..., None]
    # Tombaugh Regio "heart": two lobes, facing the viewer at lon 0
    x = LON / 0.5; y = (LAT - 0.18) / 0.5
    heart = ((x ** 2 + y ** 2 - 0.35) ** 3 - x ** 2 * y ** 3 * 1.0) < 0
    heart = np.array(Image.fromarray((heart * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32) / 255
    t = t * (1 - 0.9 * heart[..., None]) + 0.9 * heart[..., None] * np.array([0.96, 0.93, 0.88])
    return np.clip(t, 0, 1)

def tex_ganymede():
    n = fbm(TH, TW, 61); g = fbm(TH, TW, 62, ((4, .6), (10, .3), (30, .1)))
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.42, 0.37, 0.32]) * (0.8 + 0.4 * n)[..., None]
    light = np.clip((g - 0.48) * 6, 0, 1)[..., None]
    grooves = 0.9 + 0.1 * np.sin((LAT * 60 + LON * 25) + 8 * vnoise(TH, TW, 20, 7))[..., None]
    t = t * (1 - light) + light * np.array([0.68, 0.65, 0.6]) * grooves
    t = craters(t, 250, 17, depth=0.25)
    for la, lo in ((0.4, 0.5), (-0.3, -0.6), (0.1, -0.1)):
        dd = np.arccos(np.clip(np.sin(LAT) * math.sin(la) + np.cos(LAT) * math.cos(la) * np.cos(LON - lo), -1, 1))
        t += (0.35 * np.exp(-(dd / 0.05) ** 2))[..., None]
    return np.clip(t, 0, 1)

def tex_mars():
    n = fbm(TH, TW, 71); g = fbm(TH, TW, 72, ((5, .6), (12, .3), (40, .1)))
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.78, 0.42, 0.24]) * (0.85 + 0.3 * n)[..., None]
    dark = np.clip((g - 0.5) * 5, 0, 1) * np.clip(1 - np.abs(LAT + 0.1) / 0.9, 0, 1)
    t = t * (1 - 0.45 * dark[..., None])
    cap = np.clip((np.abs(LAT) - 1.25) * 8, 0, 1)
    t = t * (1 - cap[..., None]) + cap[..., None] * 0.93
    vm = np.exp(-((LAT + 0.15) / 0.06) ** 2) * np.exp(-((LON + 0.3) / 0.45) ** 4)
    t *= (1 - 0.35 * vm)[..., None]
    return np.clip(t, 0, 1)

def tex_earth():
    img = Image.new('L', (TW, TH), 0); d = ImageDraw.Draw(img)
    for f in CO['features']:
        for r in rings(f['geometry']):
            d.polygon([((p[0] + 180) / 360 * TW, (90 - p[1]) / 180 * TH) for p in r], fill=255)
    land = np.array(img.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255
    n = fbm(TH, TW, 81)
    lat = np.abs(LAT) * np.ones_like(LON)
    desert = np.exp(-((lat - 0.42) / 0.12) ** 2) * (n > 0.45)
    lc = np.array([0.22, 0.42, 0.20]) * (1 - desert[..., None]) + np.array([0.72, 0.6, 0.42]) * desert[..., None]
    lc = lc * (0.8 + 0.3 * n[..., None])
    ice = np.clip((lat - 1.15) * 6, 0, 1)[..., None]
    oc = np.array([0.03, 0.14, 0.38]) * (0.85 + 0.25 * n[..., None])
    t = oc * (1 - land[..., None]) + lc * land[..., None]
    t = t * (1 - ice) + ice * 0.95
    cl = np.clip((fbm(TH, TW, 82, ((8, .5), (20, .3), (60, .2))) - 0.52) * 3.2, 0, 0.85)[..., None]
    return np.clip(t * (1 - cl) + cl * 0.97, 0, 1)

TEX = dict(Moon=tex_moon, Mercury=tex_mercury, Ceres=tex_ceres, Pluto=tex_pluto, Ganymede=tex_ganymede, Mars=tex_mars, Earth=tex_earth)
ATMO = dict(Earth=(0.45, 0.7, 1.0), Mars=(0.9, 0.55, 0.4))
_TC = {}
def texture(name):
    if name not in _TC:
        p = os.path.join(HERE, f'tex_{name}.npy')
        if os.path.exists(p): _TC[name] = np.load(p)
        else: _TC[name] = TEX[name](); np.save(p, _TC[name])
    return _TC[name]

def sample(tex, lat, lon):
    yi = np.clip(((0.5 - lat / np.pi) * TH).astype(int), 0, TH - 1)
    xi = (((lon / (2 * np.pi)) + 0.5) % 1.0 * TW).astype(int) % TW
    return tex[yi, xi]

def sphere_img(name, px, lon0=0.0, light=(-0.6, -0.45, 0.66)):
    """orthographic render, px = diameter in pixels"""
    SS = 2; n = int(px * SS) + 4
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2; r = px * SS / 2
    u = (x - c) / r; v = (y - c) / r; rr = u * u + v * v; inside = rr <= 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    tilt = 0.25
    yy_ = -v * math.cos(tilt) + z * math.sin(tilt); zz = z * math.cos(tilt) + v * math.sin(tilt)
    lat = np.arcsin(np.clip(yy_, -1, 1)); lon = np.arctan2(u, zz) + lon0
    col = sample(texture(name), lat, lon)
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    lam = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)
    shade = (0.05 + 0.95 * lam ** 0.9) * (0.75 + 0.25 * z)
    rgb = col * shade[..., None]
    a = inside.astype(np.float32)
    if name in ATMO:
        R = np.sqrt(rr); at = np.array(ATMO[name])
        rim = np.clip(1 - np.abs(R - 1) / 0.035, 0, 1)
        rgb = rgb + at * ((1 - z) ** 3 * 0.5 * (0.2 + lam))[..., None] * inside[..., None]
        a = np.maximum(a, rim * 0.6 * (R > 1))
        rgb = np.where(inside[..., None], rgb, at)
    # anti-aliased edge
    edge = np.clip((1 - np.sqrt(rr)) * r, 0, 1)
    a = np.maximum(a * edge, a * 0) if name not in ATMO else a
    arr = np.concatenate([np.clip(rgb, 0, 1), a[..., None]], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)

def flat_skin(name, px):
    """Lambert azimuthal equal-area map of the WHOLE sphere: a disk of radius 2R (px = disk diameter)"""
    SS = 2; n = int(px * SS) + 4
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = n / 2; Rd = px * SS / 2
    X = (x - c) / Rd * 2; Y = -(y - c) / Rd * 2  # units of sphere radius, disk radius 2
    rho = np.sqrt(X * X + Y * Y); inside = rho <= 2
    cc = 2 * np.arcsin(np.clip(rho / 2, 0, 1))
    lat = np.arcsin(np.clip(np.where(rho > 0, Y * np.sin(cc) / np.maximum(rho, 1e-6), 0), -1, 1))
    lon = np.arctan2(X * np.sin(cc), rho * np.cos(cc))
    col = sample(texture(name), lat, lon) * 0.92
    a = inside.astype(np.float32) * np.clip((2 - rho) * Rd / 2, 0, 1)
    arr = np.concatenate([np.clip(col, 0, 1), a[..., None]], -1)
    return Image.fromarray((arr * 255).astype(np.uint8), 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)

# ------------------------------------------------------------------ maps
class MapCanvas:
    """pre-rendered map in projected km at K px/km; view() crops & scales"""
    def __init__(self, P, x0, x1, y0, y1, K, layers):
        self.P, self.x0, self.y1, self.K = P, x0, y1, K
        w, h = int((x1 - x0) * K), int((y1 - y0) * K)
        g = np.zeros((h, w, 3), np.float32)
        yy = np.linspace(0, 1, h)[:, None, None]
        g[:] = np.array([6, 16, 38]) / 255 * (1 - yy) + np.array([10, 26, 56]) / 255 * yy
        im = Image.fromarray((g * 255).astype(np.uint8)).convert('RGBA')
        d = ImageDraw.Draw(im, 'RGBA')
        for gx in range(int(x0 // 500) * 500, int(x1), 500):
            d.line([self.px((gx, y0)), self.px((gx, y1))], fill=(70, 110, 170, 40), width=2)
        for gy in range(int(y0 // 500) * 500, int(y1), 500):
            d.line([self.px((x0, gy)), self.px((x1, gy))], fill=(70, 110, 170, 40), width=2)
        for feats, fill, line, lw in layers:
            for f in feats:
                for r in rings(f['geometry']):
                    pts = P(r)
                    if np.abs(pts).max() > 2e4: continue
                    q = [self.px(p) for p in pts]
                    if len(q) > 2: d.polygon(q, fill=fill)
            for f in feats:
                for r in rings(f['geometry']):
                    pts = P(r)
                    if np.abs(pts).max() > 2e4: continue
                    q = [self.px(p) for p in pts]
                    if len(q) > 2 and line: d.line(q + [q[0]], fill=line, width=lw)
        self.im = im
    def px(self, p): return ((p[0] - self.x0) * self.K, (self.y1 - p[1]) * self.K)
    def view(self, cx, cy, s, W, H):
        """screen centre at (cx,cy) km, s px/km"""
        wk, hk = W / s, H / s
        box = ((cx - wk / 2 - self.x0) * self.K, (self.y1 - cy - hk / 2) * self.K, (cx + wk / 2 - self.x0) * self.K, (self.y1 - cy + hk / 2) * self.K)
        return self.im.transform((W, H), Image.EXTENT, box, Image.BILINEAR)

def silhouette(feats, P, K, fill=(255, 255, 255, 255)):
    allp = [P(r) for f in feats for r in rings(f['geometry'])]
    xs = np.concatenate([a[:, 0] for a in allp]); ys = np.concatenate([a[:, 1] for a in allp])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    im = Image.new('RGBA', (int((x1 - x0) * K) + 4, int((y1 - y0) * K) + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for a in allp:
        q = [((p[0] - x0) * K + 2, (y1 - p[1]) * K + 2) for p in a]
        if len(q) > 2: d.polygon(q, fill=fill)
    return im, (x1 - x0), (y1 - y0)

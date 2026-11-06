"""Vertical 1080x1920 cover thumbnails for every Explorer Man Short."""
import math, json, sys, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import put_text, WHITE, AMBER, CYAN, W, H
import planets as PL

OUT = "final/thumbs"
os.makedirs(OUT, exist_ok=True)
GOLD = (255, 205, 90)
RED = (255, 80, 70)
yy, xx = np.mgrid[0:H, 0:W]
rng = np.random.default_rng(7)


def space(tint=(0.02, 0.025, 0.06)):
    cv = np.zeros((H, W, 3), np.float32)
    cv[:] = (np.array(tint) * (1.3 - 0.7 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2))[..., None]).astype(np.float32)
    for _ in range(1500):
        x, y = rng.integers(0, W), rng.integers(0, H)
        cv[y, x] = rng.uniform(0.3, 0.95)
    return cv


def img(cv):
    return Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8), "RGB")


def darken_band(im, y0, y1, strength=170):
    g = np.zeros((H, W), np.float32)
    ramp = 120
    for y in range(max(0, y0 - ramp), min(H, y1 + ramp)):
        if y < y0:
            v = (y - (y0 - ramp)) / ramp
        elif y > y1:
            v = 1 - (y - y1) / ramp
        else:
            v = 1
        g[y] = v
    im.paste((0, 0, 0), (0, 0), Image.fromarray((g * strength).astype(np.uint8), "L"))


def text_block(im, lines, y, gap=1.08):
    """lines: (text, size, color)"""
    cur = y
    for txt, size, col in lines:
        put_text(im, txt, W // 2, cur + size // 2, size, "Black", col, 1.0, stroke=max(8, size // 11))
        cur += int(size * gap)


def badge(im, txt, y, col=(210, 30, 40)):
    d = ImageDraw.Draw(im, "RGBA")
    from common import text_width
    w = text_width(txt, 64) + 80
    d.rounded_rectangle((W / 2 - w / 2, y - 52, W / 2 + w / 2, y + 52), 30, fill=col + (255,))
    put_text(im, txt, W // 2, y, 64, "Black", WHITE, 1.0)


def paste_sprite(im, path, cx, cy, width, rot=0, glow=None):
    sp = Image.open(path).convert("RGBA")
    k = width / sp.width
    sp = sp.resize((int(sp.width * k), int(sp.height * k)), Image.LANCZOS)
    if rot:
        sp = sp.rotate(rot, expand=True, resample=Image.BICUBIC)
    if glow:
        g = sp.getchannel("A").filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.8))
        im.paste(glow, (int(cx - sp.width / 2), int(cy - sp.height / 2)), g)
    im.paste(sp.convert("RGB"), (int(cx - sp.width / 2), int(cy - sp.height / 2)), sp.getchannel("A"))


def save(im, name):
    im.save(f"{OUT}/{name}.jpg", quality=92)


# ---------------------------------------------------------------- What if: Earth stops forever
def t_spin():
    cv = space()
    e0, o0 = PL.T("earth").copy(), PL.T("ocean").copy()
    PL.TEX["earth"] = np.load("tex/earth_dry.npy"); PL.TEX["ocean"] = np.load("tex/ocean_dry.npy")
    L0 = PL.LIGHT.copy(); H0 = PL.HALF.copy()
    L = np.array([0.95, -0.15, 0.27], np.float32); L /= np.linalg.norm(L)
    Hh = L + np.array([0, 0, 1], np.float32); Hh /= np.linalg.norm(Hh)
    PL.LIGHT[:] = L; PL.HALF[:] = Hh
    cv = cv + (np.exp(-(((xx - 1150) ** 2 + (yy - 1080) ** 2) / (2 * 300 ** 2)))[..., None] * np.array([1.0, 0.75, 0.4]) * 0.9).astype(np.float32)
    PL.planet(cv, 540, 1080, 470, "earth", rot=math.radians(-15), a=1.0)
    PL.LIGHT[:] = L0; PL.HALF[:] = H0; PL.TEX["earth"] = e0; PL.TEX["ocean"] = o0
    im = img(cv)
    darken_band(im, 230, 640)
    text_block(im, [("WHAT IF EARTH", 104, WHITE), ("STOPPED", 150, GOLD), ("SPINNING?", 150, GOLD)], 250)
    badge(im, "FOREVER", 1640)
    save(im, "whatif_spin")


# ---------------------------------------------------------------- What if: Moon at ISS height
def t_moon():
    import whatif as WI  # ground_sky lives there (needs WI env)
    cv = WI.ground_sky().copy()
    PL.planet(cv, 540, 1500 - 1490 * 0.42 + 120, 1150, "moon", rot=0.2, a=1.0)
    im = img(cv)
    darken_band(im, 230, 700)
    text_block(im, [("THE MOON", 150, WHITE), ("JUST 400 KM", 120, GOLD), ("AWAY?", 120, GOLD)], 260)
    badge(im, "WHAT IF…", 1640)
    save(im, "whatif_moon")


# ---------------------------------------------------------------- What if: Mariana Trench
def t_trench():
    cv = np.zeros((H, W, 3), np.float32)
    g = np.clip(yy / H, 0, 1)[..., None]
    cv[:] = np.array([0.02, 0.07, 0.16]) * (1 - g) + np.array([0.0, 0.01, 0.03]) * g
    for _ in range(500):
        x, y = rng.integers(0, W), rng.integers(0, H)
        r = rng.uniform(1, 3)
        cv[max(0, int(y - r)):int(y + r), max(0, int(x - r)):int(x + r)] += 0.15
    im = img(cv)
    d = ImageDraw.Draw(im, "RGBA")
    # lure glow
    meta = json.load(open("tex/sp_meta.json"))
    paste_sprite(im, "tex/sp_angler.png", 540, 1180, 820)
    k = 820 / 440
    lx, ly = 540 - 410 + meta["lure"][0] * k, 1180 - Image.open("tex/sp_angler.png").height * k / 2 + meta["lure"][1] * k
    glow = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    for r, c in ((260, (0, 40, 35)), (140, (20, 110, 95)), (60, (90, 230, 200)), (22, (220, 255, 245))):
        gd.ellipse((lx - r, ly - r, lx + r, ly + r), fill=c)
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    im = Image.fromarray(np.clip(np.asarray(im, np.int32) + np.asarray(glow, np.int32), 0, 255).astype(np.uint8))
    darken_band(im, 230, 700)
    text_block(im, [("10,935 M", 150, CYAN), ("DOWN", 150, WHITE), ("8 TONS PER INCH²", 84, GOLD)], 250)
    badge(im, "WHAT IF YOU FELL?", 1640)
    save(im, "whatif_trench")


# ---------------------------------------------------------------- What if: Betelgeuse
def t_betel():
    cv = space()
    PL.star(cv, 540, 1650, 880, "betelgeuse", rot=0.3, a=1.0)
    im = img(cv)
    d = ImageDraw.Draw(im, "RGBA")
    # the Sun to scale
    sx, sy = 120, 718
    for r, al in ((16, 50), (8, 130), (3, 255)):
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=GOLD + (al,))
    darken_band(im, 240, 640, 120)
    text_block(im, [("IT WOULD EAT", 116, WHITE), ("THE WHOLE", 140, RED), ("SOLAR SYSTEM", 124, RED)], 270)
    put_text(im, "← the Sun (to scale)", sx + 30, sy + 4, 40, "Black", GOLD, 1.0, anchor="lm", stroke=5) if False else None
    put_text(im, "← the Sun, to scale", sx + 34, sy, 42, "Black", GOLD, 1.0, anchor="lm", stroke=5)
    badge(im, "BETELGEUSE", 1700)
    save(im, "whatif_betel")


# ---------------------------------------------------------------- Billion seconds
def t_billion():
    cv = np.zeros((H, W, 3), np.float32)
    g = np.clip(yy / H, 0, 1)[..., None]
    cv[:] = np.array([0.06, 0.08, 0.17]) * (1 - g) + np.array([0.02, 0.03, 0.07]) * g
    im = img(cv)
    paste_sprite(im, "tex/sp_watch.png", 540, 1180, 820, glow=(255, 200, 110))
    paste_sprite(im, "tex/sp_watch_glass.png", 540, 1180, 820)
    darken_band(im, 230, 640, 120)
    text_block(im, [("1 BILLION", 160, GOLD), ("SECONDS", 150, WHITE), ("= HOW LONG?", 100, CYAN)], 250)
    save(im, "billion_seconds")


# ---------------------------------------------------------------- Ocean depth
def t_ocean():
    cv = np.zeros((H, W, 3), np.float32)
    g = np.clip(yy / H, 0, 1)[..., None]
    cv[:] = np.array([0.12, 0.45, 0.65]) * (1 - g) ** 2 + np.array([0.0, 0.01, 0.04])
    im = img(cv)
    d = ImageDraw.Draw(im, "RGBA")
    for k in range(6):  # light rays
        x = 120 + k * 170
        d.polygon([(x, 0), (x + 60, 0), (x + 200, 900), (x + 90, 900)], fill=(255, 255, 255, 14))
    paste_sprite(im, "tex/sp_titanic.png", 540, 1300, 1000)
    # depth scale on the left
    for q, (lab, y) in enumerate((("0 m", 720), ("3,800 m", 1300), ("10,935 m", 1800))):
        d.line((70, y, 120, y), fill=(255, 255, 255, 200), width=4)
        put_text(im, lab, 135, y, 40, "Black", WHITE, 1.0, anchor="lm", stroke=5)
    d.line((95, 720, 95, 1800), fill=(255, 255, 255, 120), width=3)
    darken_band(im, 230, 620, 110)
    text_block(im, [("HOW DEEP IS", 120, WHITE), ("THE OCEAN?", 150, CYAN)], 270)
    save(im, "ocean_depth")


# ---------------------------------------------------------------- Sun scale
def t_sun():
    cv = space()
    PL.star(cv, 540, 1650, 1000, "sun", rot=0.4, a=1.0)
    PL.planet(cv, 540, 560 + 330, 9.2, "earth", rot=math.radians(-60), a=1.0)
    im = img(cv)
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((540 - 40, 890 - 40, 540 + 40, 890 + 40), outline=(255, 255, 255, 230), width=4)
    put_text(im, "Earth", 600, 890, 54, "Black", CYAN, 1.0, anchor="lm", stroke=6)
    darken_band(im, 230, 640, 120)
    text_block(im, [("HOW BIG IS", 130, WHITE), ("THE SUN?", 170, GOLD)], 260)
    badge(im, "TO SCALE", 1150, (40, 60, 120))
    save(im, "sun_scale")


# ---------------------------------------------------------------- Human -> Planck
def t_planck():
    cv = space((0.03, 0.02, 0.06))
    im = img(cv)
    paste_sprite(im, "tex/z_human2.png", 300, 1180, 420, glow=(120, 160, 255))
    paste_sprite(im, "tex/z_proton.png", 790, 1150, 520)
    d = ImageDraw.Draw(im, "RGBA")
    put_text(im, "vs", 560, 1180, 110, "Black", GOLD, 1.0, stroke=10)
    darken_band(im, 230, 700, 120)
    text_block(im, [("YOU vs THE", 120, WHITE), ("SMALLEST", 160, (200, 180, 255)), ("THING", 160, (200, 180, 255))], 250)
    badge(im, "10⁻³⁵ m", 1700, (90, 60, 170))
    save(im, "human_to_planck")


if __name__ == "__main__":
    os.environ["WI"] = "moon"
    for f in (t_spin, t_moon, t_trench, t_betel, t_billion, t_ocean, t_sun, t_planck):
        f()
        print("ok", f.__name__)
    names = ["whatif_spin", "whatif_moon", "whatif_trench", "whatif_betel", "billion_seconds", "ocean_depth", "sun_scale", "human_to_planck"]
    ims = [Image.open(f"{OUT}/{n}.jpg").resize((270, 480)) for n in names]
    sheet = Image.new("RGB", (270 * 8 + 70, 480), (255, 255, 255))
    for i, t in enumerate(ims):
        sheet.paste(t, (i * 280, 0))
    sheet.save("/tmp/claude-0/-home-claude/ea0570c9-5ff9-58c1-b0bc-351cad26040b/scratchpad/thumb_sheet.png")

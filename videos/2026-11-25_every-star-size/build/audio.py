import numpy as np, soundfile as sf
from render import build_scenes, FPS
SR = 24000
scenes = build_scenes()
parts = []; starts = []; T = 0.0
for sc in scenes:
    n = int(round(sc.dur * FPS)); L = int(round(n / FPS * SR))
    buf = np.zeros(L, np.float32)
    for (a, b, _), s in zip(sc.marks, sc.sents):
        w, sr = sf.read(s['file'], dtype='float32'); assert sr == SR
        i = int(a * SR); buf[i:i + len(w)] += w[:max(0, L - i)]
    parts.append(buf); starts.append(T); T += n / FPS
v = np.concatenate(parts); L = len(v); t = np.arange(L) / SR
v = v / np.abs(v).max() * 0.9
S = {sc.key: (st, sc) for st, sc in zip(starts, scenes)}
def at(key, i, off=0.0):
    st, sc = S[key]; return st + sc.s(i) + off
rng = np.random.default_rng(3)
pad = np.zeros(L)
for f, amp in ((55, 1), (82.4, 0.7), (110, 0.45), (164.8, 0.25)):
    pad += amp * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.05 * t))
pad *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 19) ** 2
pad = pad / np.abs(pad).max() * 0.035 * np.clip(t / 0.3, 0, 1) * np.clip((t[-1] - t) / 2, 0, 1)
fx = np.zeros(L)
def whoosh(t0, dur=0.55, amp=0.08):
    n = int(dur * SR); i = int(max(0, t0 - dur * 0.6) * SR); x = rng.standard_normal(n)
    out = np.zeros(n); seg = n // 8
    for k in range(8):
        win = int(40 - 4.5 * k); ker = np.ones(win) / win
        out[k * seg:(k + 1) * seg] = np.convolve(x, ker, 'same')[k * seg:(k + 1) * seg]
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    e = min(L, i + n); fx[i:e] += (out * env * amp * 4)[:e - i]
def impact(t0, amp=0.35, f0=60, dec=4.0):
    n = int(1.4 * SR); i = int(t0 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f0 * tt - 15 * tt ** 2)) * np.exp(-tt * dec)
    s += 0.35 * rng.standard_normal(n) * np.exp(-tt * 12)
    e = min(L, i + n); fx[i:e] += (s * amp)[:e - i]
def rumble(t0, dur, amp=0.12):
    n = int(dur * SR); i = int(t0 * SR); x = np.convolve(rng.standard_normal(n), np.ones(200) / 200, 'same')
    env = np.clip(np.arange(n) / (0.2 * SR), 0, 1) * np.exp(-np.arange(n) / SR * 1.5)
    e = min(L, i + n); fx[i:e] += (x / np.abs(x).max() * env * amp)[:e - i]
impact(0.0, 0.3, 50)
for st in starts[1:]: whoosh(st)
impact(at('antares', 0, 3.4), 0.6, 38, 2.5); rumble(at('antares', 0, 3.4), 3.0, 0.15)
impact(at('vy', 1), 0.55, 40, 2.5); rumble(at('vy', 1), 3.0, 0.15)
impact(at('betel', 3), 0.4, 45); rumble(at('betel', 3), 2.0)
for k, i in (('rigel', 3), ('biggest', 2), ('heavy', 3), ('outro', 1), ('hook', 1), ('sun', 1)): impact(at(k, i), 0.2, 70)
kick = np.zeros(L); beat = 60 / 96; tb = at('vy', 0)
while tb < T - 1:
    n = int(0.35 * SR); i = int(tb * SR); tt = np.arange(n) / SR
    k_ = np.sin(2 * np.pi * 55 * tt * (1 + 0.8 * np.exp(-tt * 30))) * np.exp(-tt * 9)
    e = min(L, i + n); kick[i:e] += (k_ * 0.06)[:e - i]; tb += beat
mix = v + pad + fx + kick
sf.write('mix.wav', np.clip(mix / max(1, np.abs(mix).max() / 0.98), -1, 1).astype(np.float32), SR)
print('ok', T)

import json, numpy as np, soundfile as sf
import render as R
SR = 24000
L = int(R.TOTAL * SR); v = np.zeros(L, np.float32)
for a, t0 in zip(R.AUD, R.T0):
    w, sr = sf.read(a['file'], dtype='float32'); assert sr == SR
    i = int(t0 * SR); v[i:i + len(w)] += w[:max(0, L - i)]
v = v / np.abs(v).max() * 0.9
t = np.arange(L) / SR
pad = np.zeros(L)
for f, amp in ((55, 1), (82.4, 0.6), (110, 0.45), (164.8, 0.25)):
    pad += amp * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t))
pad *= 0.6 + 0.4 * np.sin(2 * np.pi * t / 9) ** 2
pad = pad / np.abs(pad).max() * 0.05 * np.clip(t / 1.0, 0, 1) * np.clip((t[-1] - t) / 0.8, 0, 1)
def thump(at, amp):
    out = np.zeros(L)
    for dt, a in ((0.0, 1.0), (0.24, 0.6)):
        i = int((at + dt) * SR); n = int(0.18 * SR); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * (48 - 60 * tt) * tt) * np.exp(-tt / 0.05) * a
        out[i:i + n] += s[:max(0, L - i)]
    return out * amp
hb = thump(R.st('dive') + 0.8, 0.35)
mix = v + pad + hb
sf.write('mix.wav', np.clip(mix, -1, 1).astype(np.float32), SR)
print(L / SR)

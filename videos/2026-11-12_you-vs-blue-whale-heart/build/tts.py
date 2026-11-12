import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro('/home/claude/tts/kokoro-v1.0.onnx', '/home/claude/tts/voices-v1.0.bin')
S = json.load(open('lines.json'))
out = []
for i, s in enumerate(S):
    a, sr = k.create(s['say'], voice='am_michael', speed=1.07, lang='en-us')
    # trim silence
    nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-240):nz[-1]+1200]
    f = f'aud_{i}.wav'; sf.write(f, a, sr)
    out.append(dict(i=i, file=f, dur=len(a)/sr, sr=sr)); print(i, round(len(a)/sr, 2), s['say'])
json.dump(out, open('aud.json', 'w'))
print('total', sum(o['dur'] for o in out))

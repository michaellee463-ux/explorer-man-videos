import json, numpy as np, soundfile as sf
from render import build_scenes, FPS
SR=24000
scenes=build_scenes()
parts=[]
for sc in scenes:
    n=int(round(sc.dur*FPS)); L=int(round(n/FPS*SR))
    buf=np.zeros(L,np.float32)
    for (a,b,_),s in zip(sc.marks,sc.sents):
        w,sr=sf.read(s['file'],dtype='float32'); assert sr==SR
        i=int(a*SR); buf[i:i+len(w)]+=w[:max(0,L-i)]
    parts.append(buf)
v=np.concatenate(parts)
t=np.arange(len(v))/SR
# soft ambient pad: slowly drifting low chord
pad=np.zeros_like(v)
for f,amp in ((55,1),(82.4,0.7),(110,0.5),(164.8,0.3)):
    pad+=amp*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*0.05*t))
pad*=0.5+0.5*np.sin(2*np.pi*t/23)**2
pad=pad/np.abs(pad).max()*0.035
fade=np.clip(t/3,0,1)*np.clip((t[-1]-t)/3,0,1)
mix=v/np.abs(v).max()*0.9+pad*fade
sf.write('mix.wav',np.clip(mix,-1,1),SR)
print(len(v)/SR)

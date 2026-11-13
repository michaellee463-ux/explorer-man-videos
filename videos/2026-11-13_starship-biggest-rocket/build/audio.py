import numpy as np, soundfile as sf
import render as R
SR=24000; L=int(R.TOTAL*SR); v=np.zeros(L,np.float32)
for a,t0 in zip(R.AUD,R.T0):
    w,sr=sf.read(a['file'],dtype='float32'); assert sr==SR
    i=int(t0*SR); v[i:i+len(w)]+=w[:max(0,L-i)]
v=v/np.abs(v).max()*0.9
t=np.arange(L)/SR; pad=np.zeros(L)
for f,amp in ((55,1),(82.4,0.6),(110,0.45),(164.8,0.25)):
    pad+=amp*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*0.07*t))
pad*=0.6+0.4*np.sin(2*np.pi*t/9)**2
pad=pad/np.abs(pad).max()*0.045*np.clip(t/1.0,0,1)*np.clip((t[-1]-t)/0.8,0,1)
# low engine rumble under the engines + catch scenes
rng=np.random.default_rng(1); n=rng.standard_normal(L)
k=np.exp(-np.arange(400)/60.0); n=np.convolve(n,k/k.sum(),'same')
def env(a,b): return np.clip((t-a)/0.6,0,1)*np.clip((b-t)/0.8,0,1)
rum=n/np.abs(n).max()*0.10*(env(R.st('engines')+1.0,R.st('tease'))+0.7*env(R.st('catch')+0.3,R.st('catch')+6.6)+0.6*env(R.st('both')+0.4,R.st('both')+5.0))
sf.write('mix.wav',np.clip(v+pad+rum,-1,1).astype(np.float32),SR)

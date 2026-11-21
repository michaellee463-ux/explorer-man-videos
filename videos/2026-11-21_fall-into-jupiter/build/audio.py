import numpy as np, soundfile as sf
import render as R
SR=24000; L=int(R.TOTAL*SR); v=np.zeros(L,np.float32)
for a,t0 in zip(R.AUD,R.T0):
    w,sr=sf.read(a['file'],dtype='float32'); assert sr==SR
    i=int(t0*SR); v[i:i+len(w)]+=w[:max(0,L-i)]
v=v/np.abs(v).max()*0.9
t=np.arange(L)/SR; rng=np.random.default_rng(1)
pad=np.zeros(L)
for f,amp in ((49,1),(73.4,0.6),(98,0.45),(146.8,0.25)):
    pad+=amp*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*0.07*t))
pad*=0.6+0.4*np.sin(2*np.pi*t/8)**2
pad=pad/np.abs(pad).max()*0.04*np.clip(t/0.3,0,1)*np.clip((t[-1]-t)/0.6,0,1)
fx=np.zeros(L)
def whoosh(t0,dur=0.5,amp=0.09):
    n=int(dur*SR); i=int(max(0,t0-dur*0.6)*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=n//8
    for k in range(8):
        win=int(40-4.5*k); out[k*seg:(k+1)*seg]=np.convolve(x,np.ones(win)/win,'same')[k*seg:(k+1)*seg]
    env=np.sin(np.linspace(0,np.pi,n))**2; e=min(L,i+n); fx[i:e]+=(out*env*amp*4)[:e-i]
def impact(t0,amp=0.35,f0=70):
    n=int(0.9*SR); i=int(t0*SR); tt=np.arange(n)/SR
    s=np.sin(2*np.pi*(f0*tt-20*tt**2))*np.exp(-tt*5)+0.3*rng.standard_normal(n)*np.exp(-tt*30)
    e=min(L,i+n); fx[i:e]+=(s*amp)[:e-i]
# whoosh at start (mid-action pull-back) and each beat
whoosh(0.3,1.2,0.12)
for k in R.KEYS[1:]: whoosh(R.st(k))
impact(0.0,0.4); impact(1.6,0.3,90); impact(R.st('tease'),0.45,50); impact(R.st('probe'),0.35,60)
impact(R.st('core'),0.3); impact(R.st('comment'),0.25); impact(R.st('silent')+5.6,0.3,40); impact(R.st('metal')+1.2,0.3)
drop=R.st('reveal')
impact(drop,0.6,45); whoosh(drop,0.9,0.14)
beat=60/100; kick=np.zeros(L); tb=R.st('size')
while tb<R.TOTAL-0.5:
    if not (R.st('tease')<tb<R.st('metal')):
        n=int(0.35*SR); i=int(tb*SR); tt=np.arange(n)/SR
        k_=np.sin(2*np.pi*(55*tt+60*tt*np.exp(-tt*25)))*np.exp(-tt*9)
        e=min(L,i+n); kick[i:e]+=(k_*(0.10 if tb<drop else 0.15))[:e-i]
    tb+=beat
mix=v+pad+fx+kick
sf.write('mix.wav',np.clip(mix/max(1,np.abs(mix).max()/0.98),-1,1).astype(np.float32),SR)
print('ok',R.TOTAL)

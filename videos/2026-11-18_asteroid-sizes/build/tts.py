import json, sys, os, soundfile as sf
os.environ['KOKORO_DIR']='/root/kokoro'
sys.path.insert(0,'/home/claude/explorer-man-videos/tools')
from voice import say, phonemes
from script import SCENES
os.makedirs('aud',exist_ok=True)
only=set(sys.argv[1:])
idx=json.load(open('aud/index.json')) if os.path.exists('aud/index.json') else []
old={(x['scene'],x['k']):x for x in idx}
out=[]; ph=[]
for key,ch,lines in SCENES:
    for k,(text,pause) in enumerate(lines):
        p=phonemes(text); ph.append(f"[{key}.{k}] {text}\n    {p}")
        f=f'aud/{key}_{k}.wav'
        if only and key not in only and (key,k) in old and old[(key,k)]['text']==text:
            out.append(old[(key,k)]); continue
        w,sr=say(text,'am_puck',speed=1.0); w=w[:len(w)-1800]
        sf.write(f,w,sr); out.append(dict(scene=key,k=k,file=f,text=text,dur=len(w)/sr,pause=pause))
json.dump(out,open('aud/index.json','w'),indent=0)
open('../phonemes.txt','w').write('\n'.join(ph)+'\n')
print(open('../phonemes.txt').read())
print('speech',sum(o['dur'] for o in out),'total',sum(o['dur']+o['pause'] for o in out))

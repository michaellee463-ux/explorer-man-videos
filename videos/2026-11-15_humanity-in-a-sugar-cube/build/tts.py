import json, sys, os, soundfile as sf
os.environ['KOKORO_DIR']='/root/kokoro'
sys.path.insert(0,'/home/claude/explorer-man-videos/tools')
from voice import say, phonemes
S=json.load(open('lines.json')); out=[]; ph=[]
for i,s in enumerate(S):
    p=phonemes(s['say']); ph.append(f"{s['say']}\n    {p}")
    w,sr=say(s['say'],'am_puck',speed=1.0)
    w=w[:len(w)-1800]  # voice.py leaves 0.1s tail; keep 0.025s
    sf.write(f'aud_{i}.wav',w,sr); out.append(dict(i=i,file=f'aud_{i}.wav',dur=len(w)/sr,pause=s['pause']))
json.dump(out,open('aud.json','w')); open('../phonemes.txt','w').write('\n'.join(ph)+'\n')
print(open('../phonemes.txt').read()); print('speech',sum(o['dur'] for o in out),'total',sum(o['dur']+o['pause'] for o in out))

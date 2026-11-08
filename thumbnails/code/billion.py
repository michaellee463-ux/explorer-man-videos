import sys; sys.path.insert(0,'/home/claude/build')
import numpy as np
from PIL import Image, ImageFilter
from lib import put_text, pill, grad_band, GOLD, WHITE, CYAN, RED
src=Image.open('/home/claude/explorer-man-videos/thumbnails/shorts/billion_seconds.jpg').convert("RGB")
W,H=src.size
watch=src.crop((120,700,960,1680))
# background: dark navy gradient like original + stars
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
bg=np.zeros((H,W,3),np.float32)+np.array([0.02,0.025,0.06])
bg+=np.exp(-(((xx-540)/600)**2+((yy-1450)/500)**2))[...,None]*np.array([0.16,0.10,0.02])
rng=np.random.default_rng(2)
for _ in range(700):
    x,y=rng.integers(0,W),rng.integers(0,H); bg[y,x]+=rng.uniform(0.2,0.7)
im=Image.fromarray((np.clip(bg,0,1)*255).astype(np.uint8)).convert("RGBA")
# stopwatch lower, slightly smaller; soft-mask its rectangular edges
w2=watch.resize((int(watch.width*0.82),int(watch.height*0.82)),Image.LANCZOS)
m=Image.new("L",w2.size,0)
from PIL import ImageDraw
ImageDraw.Draw(m).ellipse((20,int(w2.height*0.22),w2.width-20,w2.height-10),fill=255)
ImageDraw.Draw(m).rounded_rectangle((w2.width*0.425,int(w2.height*0.02),w2.width*0.575,w2.height*0.4),20,fill=255)
m=m.filter(ImageFilter.GaussianBlur(6))
im.paste(w2,((W-w2.width)//2,H-w2.height-40),m)
grad_band(im,180,1100,170,120)
put_text(im,"1 MILLION SECONDS",W//2,250,92,WHITE,stroke=10)
put_text(im,"= 11.6 DAYS",W//2,385,130,CYAN,stroke=13)
put_text(im,"1 BILLION SECONDS",W//2,620,92,GOLD,stroke=10)
put_text(im,"= ???",W//2,830,250,RED,stroke=20)
im=im.convert("RGB"); im.save("billion_seconds_v2.jpg",quality=92); im.resize((270,480),Image.LANCZOS).save("billion_small.png")

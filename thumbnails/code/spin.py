import sys; sys.path.insert(0,'/home/claude/build')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import put_text, pill, GOLD, WHITE, RED
src=Image.open('/home/claude/explorer-man-videos/thumbnails/shorts/whatif_spin.jpg').convert("RGB")
W,H=src.size
a=np.asarray(src,np.float32)/255
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rng=np.random.default_rng(4)
space=np.zeros_like(a)+np.array([0.012,0.014,0.03])
for _ in range(900):
    x,y=rng.integers(0,W),rng.integers(0,H); space[y,x]=rng.uniform(0.2,0.8)
# Earth disk (from source): center ~ (540,1100), r ~ 470 ; keep disk + glow, replace rest of top & bottom
d=np.sqrt((xx-540)**2+(yy-1105)**2)
keep=np.clip((485-d)/12,0,1)[...,None]
# also keep sun glow on right side
glow=np.clip((xx-900)/180,0,1)*np.clip(1-np.abs(yy-1100)/600,0,1)
keep=np.maximum(keep,glow[...,None])
keep=keep*np.clip((yy-668)/60,0,1)[...,None]
out=a*keep+space*(1-keep)
im=Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)).convert("RGBA")
# wind streaks sweeping across the Earth (the atmosphere keeps moving)
lay=Image.new("RGBA",(W,H),(0,0,0,0)); dr=ImageDraw.Draw(lay)
for i in range(11):
    y0=rng.uniform(760,1460); x0=rng.uniform(-200,500); L=rng.uniform(380,800); bend=rng.uniform(-40,40)
    pts=[(x0+t*L, y0+bend*np.sin(t*np.pi)) for t in np.linspace(0,1,24)]
    dr.line(pts,fill=(235,245,255,int(rng.uniform(70,140))),width=int(rng.uniform(4,9)))
lay=lay.filter(ImageFilter.GaussianBlur(2.5))
im.alpha_composite(lay)
put_text(im,"EARTH STOPS",W//2,300,140,WHITE,stroke=14)
put_text(im,"SPINNING…",W//2,450,140,WHITE,stroke=14)
put_text(im,"1,040 MPH",W//2,1650,175,GOLD,stroke=17)
put_text(im,"WINDS",W//2,1810,130,WHITE,stroke=13)
pill(im,"WHAT IF…?",W//2,140,56,(210,30,40))
im=im.convert("RGB"); im.save("whatif_spin_v2.jpg",quality=92); im.resize((270,480),Image.LANCZOS).save("spin_small.png")

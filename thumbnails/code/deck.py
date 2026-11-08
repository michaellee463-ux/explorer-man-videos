import sys; sys.path.insert(0,'/home/claude/build')
import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import lib
from lib import put_text, GOLD, WHITE, text_w
W,H=1920,1080
rng=np.random.default_rng(3)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
bg=np.zeros((H,W,3),np.float32)
r=((xx-1350)/900)**2+((yy-560)/700)**2
bg+=np.exp(-r*1.6)[...,None]*np.array([0.20,0.13,0.03])
bg+=np.array([0.01,0.012,0.03])
for _ in range(1800):
    x,y=rng.integers(0,W),rng.integers(0,H); bg[y,x]+=rng.uniform(0.2,0.8)
im=Image.fromarray((np.clip(bg,0,1)*255).astype(np.uint8)).convert("RGBA")
SUIT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',10)
def card(rank,suit,red):
    cw,ch=420,600
    c=Image.new("RGBA",(cw+80,ch+80),(0,0,0,0)); d=ImageDraw.Draw(c)
    d.rounded_rectangle((40,40,40+cw,40+ch),36,fill=(250,248,242,255),outline=(200,195,185,255),width=3)
    col=(205,25,35,255) if red else (20,20,26,255)
    fr=ImageFont.truetype(lib.FONT,96); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',80)
    d.text((95,105),rank,font=fr,fill=col,anchor="mm"); d.text((95,190),suit,font=fs,fill=col,anchor="mm")
    big=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',300)
    d.text((40+cw/2,40+ch/2+30),suit,font=big,fill=col,anchor="mm")
    c2=c.rotate(180); c.alpha_composite(Image.new("RGBA",c.size,(0,0,0,0)))
    # bottom-right index
    d.text((40+cw-55,40+ch-65),rank,font=fr,fill=col,anchor="mm")
    return c
cards=[("10","♠",0),("J","♦",1),("Q","♣",0),("K","♥",1),("A","♠",0)]
cx,cy=1520,1180
for i,(rk,st,red) in enumerate(cards):
    ang=(i-2)*13
    c=card(rk,st,red).rotate(-ang,expand=True,resample=Image.BICUBIC)
    # pivot: rotate around bottom center, approximate offset
    a=math.radians(ang); L=520
    px=cx+L*math.sin(a); py=cy-L*math.cos(a)
    sh=Image.new("RGBA",c.size,(0,0,0,0)); sh.putalpha(c.getchannel("A").point(lambda v:int(v*0.6)))
    sh=sh.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(sh,(int(px-c.width/2+14),int(py-c.height/2+20)))
    im.alpha_composite(c,(int(px-c.width/2),int(py-c.height/2)))
# left gradient for text
g=np.clip(1-(xx[0]-200)/900,0,1)**1.2
m=Image.fromarray(np.repeat((g*200).astype(np.uint8)[None,:],H,0),"L")
im.paste((0,0,0),(0,0),m)
put_text(im,"1 DECK OF CARDS",560,270,104,WHITE,stroke=12)
put_text(im,"≈8×10",450,510,250,GOLD,stroke=20)
put_text(im,"67",905,400,130,GOLD,stroke=13)
put_text(im,"WAYS TO",560,740,150,WHITE,stroke=15)
put_text(im,"SHUFFLE IT",560,895,150,WHITE,stroke=15)
im=im.convert("RGB"); im.resize((1280,720),Image.LANCZOS).save("deck_thumbnail_v3.jpg",quality=92)
im.resize((320,180),Image.LANCZOS).save("deck_small.png")

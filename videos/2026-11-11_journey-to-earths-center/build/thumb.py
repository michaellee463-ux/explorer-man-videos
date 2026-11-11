import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
from render import make_globe, BG, F, BLACK, POP_B, GOLD, WHITE, W, H, layer_color
im=BG.copy().convert('RGBA')
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
glow=np.exp(-(((xx-1330)/620)**2+((yy-560)/620)**2)*2.2)[...,None]*np.array([0.45,0.22,0.05])
g=Image.fromarray((np.clip(glow,0,1)*255).astype(np.uint8)).convert('RGBA')
im=Image.fromarray(np.clip(np.array(im,np.int32)[...,:3]+np.array(g)[...,:3],0,255).astype(np.uint8)).convert('RGBA')
R=470
gl=make_globe(R,1.0,1.0)
im.alpha_composite(gl,(int(1330-gl.width/2),int(560-gl.height/2)))
d=ImageDraw.Draw(im,'RGBA')
cx,cy=1330,560
# center glow dot

# left gradient for text
m=np.clip(1-(xx[0]-560)/520,0,1)**1.3
mask=Image.fromarray(np.repeat((m*215).astype(np.uint8)[None,:],H,0),'L')
im.paste((0,0,0),(0,0),mask)
d=ImageDraw.Draw(im,'RGBA')
def t(xy,s,size,col,stroke):
    d.text(xy,s,font=F(BLACK,size),fill=col,anchor='mm',stroke_width=stroke,stroke_fill=(8,8,14))
t((520,290),'DEEPEST HOLE',112,WHITE,12)
t((520,500),'0.19%',250,GOLD,18)
t((520,720),'OF THE WAY',112,WHITE,12)
# badge
f=F(POP_B,54); s='6,370 KM TO THE CENTER'; w=f.getlength(s)+80
d.rounded_rectangle((520-w/2,850,520+w/2,950),50,fill=(210,30,40,255))
d.text((520,900),s,font=f,fill=WHITE,anchor='mm')
out=im.convert('RGB')
out.save('thumb_full.jpg',quality=92)
out.resize((1280,720),Image.LANCZOS).save('thumbnail.jpg',quality=92)
out.resize((320,180),Image.LANCZOS).save('thumb_small.png')

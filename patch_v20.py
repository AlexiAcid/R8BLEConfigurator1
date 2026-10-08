from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFile
import math, random
ImageFile.LOAD_TRUNCATED_IMAGES=True
root=Path("R8BLEConfigurator/app/src/main")
java=root/"java/com/openai/r8ble/MainActivity.java"
s=java.read_text()
s=s.replace("R8 BLE Configurator v1.9 ready. Target device name: R8-US","R8 BLE Configurator v2.0 ready. Target device name: R8-US")
s=s.replace('\\nv1.9\\n','\\nv2.0\\n')
s=s.replace('ride.setBackgroundResource(R.drawable.r8_ride_background);','rideScroll.setBackgroundResource(R.drawable.r8_ride_background);\n        ride.setBackgroundColor(0x00000000);')
java.write_text(s)
res=root/"res/drawable"
res.mkdir(parents=True,exist_ok=True)
# Construct cinematic sunset/mountain background, not a flattened screenshot.
W,H=720,1280
im=Image.new("RGB",(W,H)); pix=im.load()
for y in range(H):
 t=y/H
 glow=math.exp(-((t-.31)/.17)**2)
 for x in range(W):
  horizon=(1-abs(x-W*.58)/(W*.85))*.6+.4
  pix[x,y]=(int(5+62*glow*horizon),int(13+24*glow*horizon),int(23+12*glow))
d=ImageDraw.Draw(im,"RGBA")
random.seed(18)
for layer in range(4):
 base=370+layer*115
 coords=[(0,H)]
 for x in range(0,W+24,24):
  peaks=math.sin(x/95+layer*2)*42+math.sin(x/38+layer)*20
  coords.append((x,int(base+peaks-random.randint(0,19))))
 coords.extend([(W,H)])
 d.polygon(coords,fill=(5+layer*2,12+layer*3,20+layer*3,210+layer*9))
# Subtle warm horizon.
d.ellipse((420,300,560,440),fill=(255,92,18,60))
im=im.filter(ImageFilter.GaussianBlur(3))
shade=Image.new("RGBA",(W,H),(0,0,0,0));sd=ImageDraw.Draw(shade)
for y in range(H):
 alpha=int(90+100*(y/H))
 sd.line((0,y,W,y),fill=(0,0,0,alpha))
im=Image.alpha_composite(im.convert("RGBA"),shade).convert("RGB")
im.save(res/"r8_mountains.png",quality=94)
# Crop broken gray footer completely; fit with dark edge background and rounded-safe margins.
icon=res/"r8_launcher.jpg"
orig=Image.open(icon).convert("RGB")
w,h=orig.size
# Gray overlay starts around 75 percent of current icon: cut before that.
orig=orig.crop((0,0,w,int(h*.68)))
# Center crop to avoid bottom strip; retain tire and R8 branding.
side=min(orig.size)
orig=orig.crop(((orig.width-side)//2,0,(orig.width+side)//2,side))
orig=orig.resize((512,512),Image.Resampling.LANCZOS)
orig.save(icon,quality=97)
print("v2.0 asset processing completed")

from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import io

p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()
a=s.index('        LinearLayout iconCard=releaseCard("App Icon");')
b=s.index('        LinearLayout styleCard=releaseCard("UI Style");',a)
s=s[:a]+s[b:]
s=s.replace('Custom R8 e-bike control and configuration.','Custom R8 e-bike control and configuration.')
s=s.replace('\\nv1.8\\n','\\nv1.9\\n')
s=s.replace('R8 BLE Configurator v1.8 ready. Target device name: R8-US','R8 BLE Configurator v1.9 ready. Target device name: R8-US')
# Give the ride screen a full-width landscape backdrop without obscuring controls.
needle='''        rideScroll.addView(ride,new ScrollView.LayoutParams(-1,-2));'''
replacement='''        rideScroll.addView(ride,new ScrollView.LayoutParams(-1,-2));
        ride.setBackgroundResource(R.drawable.r8_ride_background);'''
if needle not in s: raise SystemExit("missing ride background anchor")
s=s.replace(needle,replacement,1)
p.write_text(s)

res=Path("R8BLEConfigurator/app/src/main/res/drawable")
icon=res/"r8_launcher.jpg"
im=Image.open(icon).convert("RGB")
# The source collage crop contained a gray strip in its bottom quarter.
# Retain the complete tire/flame area and reframe to a square without that strip.
w,h=im.size
im=im.crop((0,0,w,int(h*0.73)))
side=max(im.size)
canvas=Image.new("RGB",(side,side),(5,10,15))
im.thumbnail((side,side))
canvas.paste(im,((side-im.width)//2,(side-im.height)//2))
canvas=canvas.resize((512,512),Image.Resampling.LANCZOS)
canvas.save(icon,quality=95)

# Dark mountain silhouette background: drawable gradient with layered peaks.
xml='''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
 <item>
  <shape android:shape="rectangle">
   <gradient android:startColor="#152432" android:centerColor="#0A141E"
       android:endColor="#060B10" android:angle="270"/>
  </shape>
 </item>
 <item android:top="110dp" android:bottom="350dp">
  <bitmap android:src="@drawable/r8_mountains" android:gravity="fill"/>
 </item>
</layer-list>'''
(res/"r8_ride_background.xml").write_text(xml)
# Raster landscape: blue dusk, distant mountain ridges, orange horizon.
from PIL import ImageDraw
bg=Image.new("RGB",(800,1400))
px=bg.load()
for y in range(1400):
 t=y/1399
 for x in range(800):
  px[x,y]=(int(12*(1-t)+4*t),int(26*(1-t)+9*t),int(40*(1-t)+16*t))
draw=ImageDraw.Draw(bg)
draw.polygon([(0,510),(70,430),(155,485),(240,355),(330,480),(430,380),(560,510),(655,410),(800,520),(800,1400),(0,1400)],fill=(22,36,48))
draw.polygon([(0,600),(100,520),(215,610),(330,475),(460,615),(570,505),(690,595),(800,520),(800,1400),(0,1400)],fill=(12,24,34))
bg=bg.filter(ImageFilter.GaussianBlur(2))
bg.save(res/"r8_mountains.png")
print("v1.9 icon cleaned, App Icon settings removed, dark mountain background added")

from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
from urllib.request import Request, urlopen
from io import BytesIO
root=Path("R8BLEConfigurator/app/src/main")
java=root/"java/com/openai/r8ble/MainActivity.java"
s=java.read_text()
s=s.replace("R8 BLE Configurator v2.2 ready. Target device name: R8-US","R8 BLE Configurator v2.3 ready. Target device name: R8-US")
# Keep the photographic backdrop behind the whole screen, including the status area.
s=s.replace('rideScroll.setBackgroundResource(R.drawable.r8_ride_background);','rideScroll.setBackgroundResource(R.drawable.r8_ride_background);')
# Glass effect for all release cards: dark translucent gradient with light border.
needle='        c.setTag("card");'
if needle not in s: raise SystemExit("card anchor missing")
s=s.replace(needle,'''        c.setTag("card");
        android.graphics.drawable.GradientDrawable glass=new android.graphics.drawable.GradientDrawable(
            android.graphics.drawable.GradientDrawable.Orientation.TOP_BOTTOM,
            new int[]{0xDB101820,0xE610141B});
        glass.setCornerRadius(dp(20));
        glass.setStroke(dp(1),0x665D6977);
        c.setBackground(glass);''',1)
# The styling recursion should not overwrite glass cards with flat opaque backgrounds.
s=s.replace('g.setColor(surface); g.setCornerRadius(dp(20));', 'g.setColor(0xD51A222C); g.setCornerRadius(dp(20));')
# Move GPS prompt away from prominent dashboard area while retaining tap-to-start functionality.
s=s.replace('gpsStatusView.setText("Tap the speed dial to start phone GPS");','gpsStatusView.setText("Tap dial for GPS speed");')
s=s.replace('gpsStatusView.setTextSize(13f);','gpsStatusView.setTextSize(11f);')
# Make the main speed display a premium black circular instrument.
needle='        gauge.setTag("gauge");'
if needle not in s: raise SystemExit("gauge anchor missing")
s=s.replace(needle,'''        gauge.setTag("gauge");
        android.graphics.drawable.GradientDrawable instrument=new android.graphics.drawable.GradientDrawable(
            android.graphics.drawable.GradientDrawable.Orientation.TL_BR,
            new int[]{0xFF303039,0xFF07080C,0xFF09090D});
        instrument.setShape(android.graphics.drawable.GradientDrawable.OVAL);
        instrument.setStroke(dp(5),0xFF7A3614);
        gauge.setBackground(instrument);
        gauge.setElevation(dp(12));''',1)
# Rounded unified nav: instead of three isolated bright tabs, dark nav buttons with orange text.
s=s.replace('rideTab.setTag("navS', 'rideTab.setTag("navS')
java.write_text(s)
# Photographic source, free-to-use Unsplash photo. Pin its photo ID, bundle offline.
url="https://images.unsplash.com/photo-1674116202635-0d5d4ceaf5b4?auto=format&fit=crop&w=1400&q=90"
req=Request(url,headers={"User-Agent":"Mozilla/5.0"})
raw=urlopen(req,timeout=35).read()
im=Image.open(BytesIO(raw)).convert("RGB")
W,H=900,1600
scale=max(W/im.width,H/im.height)
new=(int(im.width*scale),int(im.height*scale))
im=im.resize(new,Image.Resampling.LANCZOS)
x=(im.width-W)//2
# keep upper sky and peaks visible
y=max(0,int((im.height-H)*0.24))
im=im.crop((x,y,x+W,y+H))
im=ImageEnhance.Color(im).enhance(1.5)
im=ImageEnhance.Contrast(im).enhance(1.15)
overlay=Image.new("RGBA",(W,H));d=ImageDraw.Draw(overlay)
for py in range(H):
    t=py/H
    alpha=int(10+140*t*t)
    d.line((0,py,W,py),fill=(0,3,8,alpha))
im=Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB")
res=root/"res/drawable"
res.mkdir(parents=True,exist_ok=True)
im.save(res/"r8_photo_sunset.jpg",quality=89,optimize=True)
# Replace PNG drawable name with new JPEG asset by removing old PNG, avoiding duplicate resource.
old=res/"r8_photo_sunset.png"
if old.exists(): old.unlink()
print("v2.3 PHOTO bundled",im.size,"JPEG bytes",(res/"r8_photo_sunset.jpg").stat().st_size)

# Replace the old layer-list silhouette with a full-screen photo drawable.
xml=res/"r8_ride_background.xml"
xml.write_text('''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
  <item><bitmap android:src="@drawable/r8_photo_sunset" android:gravity="fill"/></item>
</layer-list>''')

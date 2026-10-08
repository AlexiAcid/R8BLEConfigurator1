from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()
s=s.replace("R8 BLE Configurator v2.0 ready. Target device name: R8-US","R8 BLE Configurator v2.1 ready. Target device name: R8-US")
s=s.replace('\\nv2.0\\n','\\nv2.1\\n')
# Use the same mountain artwork across all tabs and leave content transparent.
s=s.replace('rideScroll.setBackgroundResource(R.drawable.r8_ride_background);','''rideScroll.setBackgroundResource(R.drawable.r8_ride_background);
        advancedScroll.setBackgroundResource(R.drawable.r8_ride_background);
        appearanceScroll.setBackgroundResource(R.drawable.r8_ride_background);
        advanced.setBackgroundColor(0x00000000);
        appearance.setBackgroundColor(0x00000000);''')
# Segmented instrument dial, matching the orange illuminated reference.
old='g.setStroke(dp(10), accent);'
if old not in s: raise SystemExit("gauge stroke anchor missing")
s=s.replace(old,'g.setStroke(dp(10), accent, dp(13), dp(3));',1)
# Avoid representing an unconfirmed physical light change as success.
s=s.replace('lightSwitch.setOnCheckedChangeListener((b,checked)->setRideLight(checked));','''lightSwitch.setOnCheckedChangeListener((b,checked)->{
            setRideLight(checked);
            android.widget.Toast.makeText(this,
                "Light command sent — verify actual headlight",android.widget.Toast.LENGTH_SHORT).show();
        });''')
p.write_text(s)
print("v2.1 consistent landscape on three pages, segmented dial and honest light feedback")

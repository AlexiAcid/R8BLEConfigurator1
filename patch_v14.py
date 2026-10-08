from pathlib import Path

p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v14 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.3 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.4 ready. Target device name: R8-US");',
    "version")

# R8 field test: APP_LIGHT boolean is inverted on this controller.
rep('''        byte[] frame = officialFrame(new byte[]{0x33, 0x02, 0x01, (byte)(on ? 1 : 0)});
        writeOfficialFf62(frame, on ? "RIDE LIGHT ON" : "RIDE LIGHT OFF");''',
'''        // R8 field-tested semantics are inverted versus the generic APP_LIGHT boolean:
        // payload 0 activates the bike light; payload 1 deactivates it.
        byte[] frame = officialFrame(new byte[]{0x33, 0x02, 0x01, (byte)(on ? 0 : 1)});
        writeOfficialFf62(frame, on ? "RIDE LIGHT ON" : "RIDE LIGHT OFF");''',
    "R8 light semantics")

# Remove misleading prerequisite language now that 62 SET is ACKed and range query returns max=62.
rep('''        profileHint.setText("62 mode is available only when the controller reports a maximum of 62. Use Refresh Bike after changing P5 on the bike.");''',
'''        profileHint.setText("Quick speed presets. The bike confirms changes over BLE; Refresh Bike reads the current controller range.");''',
    "speed preset hint")

# Cleaner, more app-like copy.
rep('''        rideTitle.setText("R8 Ride");''',
'''        rideTitle.setText("R8 Control");''',
    "ride title")
rep('''        TextView rideNote = new TextView(this);
        rideNote.setText("Ride controls use verified R8 commands. GPS speed is measured by your phone. Change settings only while stopped.");''',
'''        TextView rideNote = new TextView(this);
        rideNote.setText("Connected controls for your R8  •  GPS speed uses your phone");''',
    "ride note")

# Friendly labels on the main screen only; Advanced remains unchanged.
rep('''        Button full62 = button("FULL SPEED 62");
        Button street32 = button("STREET 32");''',
'''        Button full62 = button("62 KM/H");
        Button street32 = button("32 KM/H");''',
    "speed labels")
rep('''        Button lightOnRide = button("LIGHT ON");
        Button lightOffRide = button("LIGHT OFF");''',
'''        Button lightOnRide = button("LIGHT  ON");
        Button lightOffRide = button("LIGHT  OFF");''',
    "light labels")
rep('''        Button queryRangeRide = button("QUERY RANGE");
        Button applyCap = button("APPLY CAP");''',
'''        Button queryRangeRide = button("REFRESH RANGE");
        Button applyCap = button("SET SPEED");''',
    "cap labels")

p.write_text(s)
print("Applied v1.4 R8 light fix and Ride-screen polish")

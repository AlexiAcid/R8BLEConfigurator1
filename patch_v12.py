from pathlib import Path

p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v12 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.1 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.2 ready. Target device name: R8-US");',
    "version")

rep('''        LinearLayout capRow = row();
        Button queryRangeRide = button("QUERY RANGE");
        Button applyCap = button("APPLY CAP");
        capRow.addView(queryRangeRide, weight());
        capRow.addView(applyCap, weight());
        root.addView(capRow);

        LinearLayout utilityRow = row();''',
'''        LinearLayout capRow = row();
        Button queryRangeRide = button("QUERY RANGE");
        Button applyCap = button("APPLY CAP");
        capRow.addView(queryRangeRide, weight());
        capRow.addView(applyCap, weight());
        root.addView(capRow);

        LinearLayout speedPresetRow = row();
        Button full62 = button("FULL SPEED 62");
        Button street32 = button("STREET 32");
        speedPresetRow.addView(full62, weight());
        speedPresetRow.addView(street32, weight());
        root.addView(speedPresetRow);

        TextView profileHint = new TextView(this);
        profileHint.setText("FULL SPEED 62 only works when the bike reports hidden maximum >= 62. Your latest physical secret-menu test successfully changed that maximum between 32 and 62.");
        root.addView(profileHint);

        LinearLayout lightRow = row();
        Button lightOnRide = button("LIGHT ON");
        Button lightOffRide = button("LIGHT OFF");
        lightRow.addView(lightOnRide, weight());
        lightRow.addView(lightOffRide, weight());
        root.addView(lightRow);

        LinearLayout utilityRow = row();''',
    "ride presets")

rep('''        applyCap.setOnClickListener(v -> applyRideSpeedCap());
        toggleUnits.setOnClickListener(v -> toggleRideUnits());''',
'''        applyCap.setOnClickListener(v -> applyRideSpeedCap());
        full62.setOnClickListener(v -> setRideSpeedPreset(62));
        street32.setOnClickListener(v -> setRideSpeedPreset(32));
        lightOnRide.setOnClickListener(v -> setRideLight(true));
        lightOffRide.setOnClickListener(v -> setRideLight(false));
        toggleUnits.setOnClickListener(v -> toggleRideUnits());''',
    "preset listeners")

rep('''        String txt = "R8 LIVE  •  Gear: " + gearRaw + "  •  Display unit: " + displayUnit''',
'''        String profile = speedLimitMaxRaw >= 62 ? "FULL (62)" :
                (speedLimitMaxRaw > 0 ? "LIMITED (" + speedLimitMaxRaw + ")" : "unknown");
        String txt = "R8 LIVE  •  Gear: " + gearRaw + "  •  Display unit: " + displayUnit''',
    "profile var")

rep('''            String ride = "Bike: Gear " + gearRaw
                    + "  •  Battery " + socLike + "%"
                    + "  •  " + voltage
                    + "\nController cap: " + cap
                    + "  •  Range: " + range
                    + "\nLight " + (light ? "ON" : "OFF")''',
'''            String ride = "Bike: Gear " + gearRaw
                    + "  •  Battery " + socLike + "%"
                    + "  •  " + voltage
                    + "\nProfile: " + profile
                    + "  •  Controller cap: " + cap
                    + "  •  Range: " + range
                    + "\nLight " + (light ? "ON" : "OFF")''',
    "ride profile status")

rep('''    private void toggleRideUnits() {''',
'''    private void setRideSpeedPreset(int value) {
        if (!stationaryForSetting()) return;
        if (speedLimitMaxRaw < 0) {
            toast("Query the controller range first.");
            sendOfficialSpeedQuery();
            return;
        }
        if (value > speedLimitMaxRaw) {
            toast("Bike currently reports hidden max " + speedLimitMaxRaw
                    + " km/h. Set the secret-menu value to 62 first, then Refresh Bike.");
            return;
        }
        if (value < speedLimitMinRaw) {
            toast("Requested speed is below the controller minimum.");
            return;
        }
        byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, (byte)value});
        writeOfficialFf62(frame, "RIDE SPEED PRESET " + value + " KM/H");
        main.postDelayed(this::sendOfficialSpeedQuery, 500);
        toast("Requested " + value + " km/h.");
    }

    private void setRideLight(boolean on) {
        if (gatt == null) {
            toast("Connect to R8-US first.");
            return;
        }
        // Official isinwheel APP_LIGHT command: 0x33 / param 0x02 / one-byte boolean payload.
        byte[] frame = officialFrame(new byte[]{0x33, 0x02, 0x01, (byte)(on ? 1 : 0)});
        writeOfficialFf62(frame, on ? "RIDE LIGHT ON" : "RIDE LIGHT OFF");
    }

    private void toggleRideUnits() {''',
    "preset methods")

p.write_text(s)
print("Applied v1.2 full-speed presets, hidden-profile display and ride light controls")

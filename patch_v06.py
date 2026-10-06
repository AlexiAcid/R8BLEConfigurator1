from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v06 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.5 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.6 ready. Target device name: R8-US");',
    "version")

rep('''    private int currentLikeRaw;''',
'''    private int currentLikeRaw;
    private int gearRaw = -1;
    private boolean mphUnits;
    private boolean dualDrive;
    private int electricModeRaw = -1;
    private int currentSpeedLimitRaw = -1;
    private int speedLimitMinRaw = -1;
    private int speedLimitMaxRaw = -1;''',
    "state")

rep('''        Button querySpeed = button("QUERY SPEED LIMIT");
        Button set56 = button("SET LIMIT 56 KM/H");''',
'''        Button querySpeed = button("QUERY SPEED LIMIT");
        Button set56 = button("SET REPORTED MAX");''',
    "speed button label")

rep('''        root.addView(speedRow);
''',
'''        root.addView(speedRow);

        LinearLayout driveRow = row();
        Button singleDrive = button("SINGLE-WHEEL DRIVE");
        Button dualDriveBtn = button("DUAL-WHEEL DRIVE");
        driveRow.addView(singleDrive, weight());
        driveRow.addView(dualDriveBtn, weight());
        root.addView(driveRow);

        TextView driveNote = new TextView(this);
        driveNote.setText("Official R8/isinwheel command 0x3B. Current drive mode is decoded live from the bike. Only select dual-wheel drive if this bike physically has both front and rear motor hubs.");
        root.addView(driveNote);
''',
    "drive UI")

rep('''        set56.setOnClickListener(v -> confirmOfficialSpeed56());
''',
'''        set56.setOnClickListener(v -> confirmOfficialReportedMax());
        singleDrive.setOnClickListener(v -> confirmOfficialDrive(false));
        dualDriveBtn.setOnClickListener(v -> confirmOfficialDrive(true));
''',
    "listeners")

rep('''            int type = rxStream.get(2) & 0xFF;
            int len = type == 0x20 ? 27 : type == 0x21 ? 25 : -1;''',
'''            int type = rxStream.get(2) & 0xFF;
            int len = type == 0x20 ? 27
                    : type == 0x21 ? 25
                    : type == 0x62 ? 11
                    : (type == 0x36 || type == 0x3B) ? 9
                    : -1;''',
    "frame lengths")

old_decode='''        if (type == 0x20 && f.length == 27) {
            latestStatus20 = Arrays.copyOf(f, f.length);
            latestStatusAt = System.currentTimeMillis();
            boolean light = (f[5] & 0x10) != 0;
            boolean brake = (f[6] & 0x08) != 0;
            int socLike = f[8] & 0xFF;
            int counterLike = f[15] & 0xFF;
            updateDecoder(light, brake, socLike, counterLike);
        } else if (type == 0x21 && f.length == 25) {
            motorRaw = le16(f,5);
            batteryCentivolts = le16(f,7);
            currentLikeRaw = le16(f,9);
            if (latestStatus20 != null) {
                boolean light = (latestStatus20[5] & 0x10) != 0;
                boolean brake = (latestStatus20[6] & 0x08) != 0;
                updateDecoder(light, brake, latestStatus20[8] & 0xFF, latestStatus20[15] & 0xFF);
            }
        }
'''
new_decode='''        if (type == 0x20 && f.length == 27) {
            latestStatus20 = Arrays.copyOf(f, f.length);
            latestStatusAt = System.currentTimeMillis();
            boolean light = (f[5] & 0x10) != 0;
            boolean brake = (f[6] & 0x08) != 0;
            int socLike = f[8] & 0xFF;

            // isinwheel club 1.1.4 YFDMeter1 status parser:
            // byte 15 packs speedMode, unit, single/dual drive and electric/riding mode.
            int packed = f[15] & 0xFF;
            gearRaw = packed & 0x07;
            mphUnits = (packed & 0x08) != 0;
            dualDrive = (packed & 0x10) != 0;
            electricModeRaw = (packed >> 5) & 0x03;

            // Official parser exposes this byte as the current highest-gear speed limit.
            currentSpeedLimitRaw = f[12] & 0xFF;
            updateDecoder(light, brake, socLike, packed);
        } else if (type == 0x21 && f.length == 25) {
            motorRaw = le16(f,5);
            batteryCentivolts = le16(f,7);
            currentLikeRaw = le16(f,9);
            if (latestStatus20 != null) {
                boolean light = (latestStatus20[5] & 0x10) != 0;
                boolean brake = (latestStatus20[6] & 0x08) != 0;
                updateDecoder(light, brake, latestStatus20[8] & 0xFF, latestStatus20[15] & 0xFF);
            }
        } else if (type == 0x62 && f.length == 11) {
            speedLimitMinRaw = f[5] & 0xFF;
            speedLimitMaxRaw = f[6] & 0xFF;
            append("R8 SPEED LIMIT RANGE response: min=" + speedLimitMinRaw + " max=" + speedLimitMaxRaw);
            if (latestStatus20 != null) {
                updateDecoder((latestStatus20[5] & 0x10) != 0,
                        (latestStatus20[6] & 0x08) != 0,
                        latestStatus20[8] & 0xFF, latestStatus20[15] & 0xFF);
            }
        } else if (type == 0x36 && f.length == 9) {
            append("R8 SPEED LIMIT SET ACK status=" + (f[4] & 0xFF));
            main.postDelayed(this::sendOfficialSpeedQuery, 500);
        } else if (type == 0x3B && f.length == 9) {
            append("R8 DRIVE-MODE SET ACK status=" + (f[4] & 0xFF));
            toast("Drive-mode command acknowledged; watch LIVE Drive status.");
        }
'''
rep(old_decode,new_decode,"decoder")

old_update=r'''    private void updateDecoder(boolean light, boolean brake, int socLike, int counterLike) {
        String voltage = batteryCentivolts > 0 ? String.format(Locale.US, "%.2f V", batteryCentivolts / 100.0) : "—";
        String txt = "R8 LIVE  •  Light: " + (light ? "ON" : "OFF")
                + "  •  Brake: " + (brake ? "ON" : "OFF")
                + "\nBattery-like: " + socLike + "%  •  Voltage: " + voltage
                + "\nMotor-speed raw: " + motorRaw + "  •  Current/power raw: " + currentLikeRaw
                + "  •  Counter: " + counterLike;
        if (decodedView != null) decodedView.setText(txt);
    }
'''
new_update=r'''    private void updateDecoder(boolean light, boolean brake, int socLike, int packed) {
        String voltage = batteryCentivolts > 0 ? String.format(Locale.US, "%.2f V", batteryCentivolts / 100.0) : "—";
        String unit = mphUnits ? "mph" : "km/h";
        String cap = currentSpeedLimitRaw >= 0 ? currentSpeedLimitRaw + " " + unit : "—";
        String converted = "";
        if (currentSpeedLimitRaw >= 0 && mphUnits) {
            converted = String.format(Locale.US, " (~%.1f km/h)", currentSpeedLimitRaw * 1.609344);
        } else if (currentSpeedLimitRaw >= 0 && !mphUnits) {
            converted = String.format(Locale.US, " (~%.1f mph)", currentSpeedLimitRaw / 1.609344);
        }
        String range = speedLimitMinRaw >= 0 && speedLimitMaxRaw >= 0
                ? speedLimitMinRaw + "–" + speedLimitMaxRaw + " " + unit : "not queried";
        String txt = "R8 LIVE  •  Gear: " + gearRaw + "  •  Units: " + unit
                + "\nDrive: " + (dualDrive ? "DUAL-WHEEL" : "SINGLE-WHEEL")
                + "  •  Electric/riding raw: " + electricModeRaw
                + "\nSpeed cap: " + cap + converted + "  •  Allowed: " + range
                + "\nLight: " + (light ? "ON" : "OFF") + "  •  Brake: " + (brake ? "ON" : "OFF")
                + "\nBattery: " + socLike + "%  •  Voltage: " + voltage
                + "\nMotor raw: " + motorRaw + "  •  Current/power raw: " + currentLikeRaw
                + String.format(Locale.US, "\nPacked settings byte: 0x%02X", packed & 0xFF);
        if (decodedView != null) decodedView.setText(txt);
    }
'''
rep(old_update,new_update,"live decoder")

# Replace misleading raw-56 routine with the queried maximum.
start='''    private void confirmOfficialSpeed56() {
        if (latestStatus20 == null || System.currentTimeMillis() - latestStatusAt > 3000) {
            toast("Wait for fresh R8 telemetry first.");
            return;
        }
        if ((latestStatus20[6] & 0x08) != 0) {
            toast("Release the brake before changing the speed limit.");
            return;
        }
        if (motorRaw != 0 || currentLikeRaw != 0) {
            toast("Stop the wheel/motor before changing the speed limit.");
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Set R8 speed limit to 56 km/h")
                .setMessage("This uses the exact speed-limit command format recovered from isinwheel club 1.1.4 (command 0x36, parameter 0x02). Keep the bike stationary. Use only where this speed is legal and appropriate.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Set 56 km/h", (d,w) -> sendOfficialSpeed56())
                .show();
    }

    private void sendOfficialSpeed56() {
        // isinwheel club 1.1.4: speedLimit(speed) -> d(0x36, 0x02, [speed], TRUE)
        // TRUE causes d() to insert payload-length byte 0x01.
        byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, 0x38});
        writeOfficialFf62(frame, "SET SPEED LIMIT 56 KM/H");
    }

'''
replacement='''    private boolean stationaryForSetting() {
        if (latestStatus20 == null || System.currentTimeMillis() - latestStatusAt > 3000) {
            toast("Wait for fresh R8 telemetry first."); return false;
        }
        if ((latestStatus20[6] & 0x08) != 0) {
            toast("Release the brake before changing this setting."); return false;
        }
        if (motorRaw != 0 || currentLikeRaw != 0) {
            toast("Stop the wheel/motor before changing this setting."); return false;
        }
        return true;
    }

    private void confirmOfficialReportedMax() {
        if (!stationaryForSetting()) return;
        if (speedLimitMaxRaw < 0) {
            toast("Query the speed limit first."); return;
        }
        final int max = speedLimitMaxRaw;
        final String unit = mphUnits ? "mph" : "km/h";
        new AlertDialog.Builder(this)
                .setTitle("Set reported maximum")
                .setMessage("Set the normal highest-gear speed limit to the controller-reported maximum of "
                        + max + " " + unit + "?")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Set " + max + " " + unit, (d,w) -> {
                    byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, (byte)max});
                    writeOfficialFf62(frame, "SET SPEED LIMIT " + max + " " + unit);
                }).show();
    }

    private void confirmOfficialDrive(boolean dual) {
        if (!stationaryForSetting()) return;
        if (dual == dualDrive) {
            toast("Bike already reports " + (dual ? "DUAL-WHEEL" : "SINGLE-WHEEL") + " drive.");
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle(dual ? "Enable dual-wheel drive" : "Enable single-wheel drive")
                .setMessage(dual
                        ? "The bike currently reports SINGLE-WHEEL drive. This sends the official APP_DRIVE command with value 1. Only continue if the bike physically has both front and rear motor hubs."
                        : "This sends the official APP_DRIVE command with value 0 to select single-wheel drive.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton(dual ? "Enable Dual" : "Enable Single",
                        (d,w) -> sendOfficialDrive(dual))
                .show();
    }

    private void sendOfficialDrive(boolean dual) {
        // isinwheel club 1.1.4 setDrive(): command 0x3B, param 0x02,
        // one-byte payload: 0=single-wheel, 1=dual-wheel.
        byte[] frame = officialFrame(new byte[]{0x3B, 0x02, 0x01, (byte)(dual ? 1 : 0)});
        writeOfficialFf62(frame, dual ? "SET DUAL-WHEEL DRIVE" : "SET SINGLE-WHEEL DRIVE");
    }

'''
rep(start,replacement,"replace 56 setter")

# Auto-query after telemetry subscription has had time to settle.
rep('''            append("Auto-subscribing R8 FF61 telemetry channel…");
            subscribeSelected();
''',
'''            append("Auto-subscribing R8 FF61 telemetry channel…");
            subscribeSelected();
            main.postDelayed(this::sendOfficialSpeedQuery, 1200);
''',
    "auto query")

rep('''        motorRaw = batteryCentivolts = currentLikeRaw = 0;
''',
'''        motorRaw = batteryCentivolts = currentLikeRaw = 0;
        gearRaw = electricModeRaw = currentSpeedLimitRaw = -1;
        speedLimitMinRaw = speedLimitMaxRaw = -1;
        mphUnits = false;
        dualDrive = false;
''',
    "reset state")

p.write_text(s)
print("Applied v0.6 verified unit/drive decoding and official single/dual controls")

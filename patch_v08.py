from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v08 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.7 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.8 ready. Target device name: R8-US");',
    "version")

rep('''    private int speedLimitMaxRaw = -1;''',
'''    private int speedLimitMaxRaw = -1;
    private String protocolVersion = "—";
    private String meterVersion = "—";
    private String controllerVersion = "—";
    private int countryCode = -1;
    private int meterSupplierCode = -1;
    private int controllerSupplierCode = -1;
    private String meterCrc = "not queried";
    private String controllerCrc = "not queried";''',
    "diagnostic state")

rep('''        Button set56 = button("SET REPORTED MAX");''',
'''        Button set56 = button("SET ALLOWED MAX");''',
    "speed button correction")

# Insert diagnostic query controls immediately after the speed row, before gear UI.
rep('''        root.addView(speedRow);

        TextView gearTitle = new TextView(this);''',
'''        root.addView(speedRow);

        TextView restrictionNote = new TextView(this);
        restrictionNote.setText("IMPORTANT: speed-limit raw values are km/h internally. The MPH/KM/H bit only controls display conversion. A range of 17–33 therefore means the current profile only permits up to 33 km/h (~20.5 mph).");
        root.addView(restrictionNote);

        LinearLayout crcRow = row();
        Button queryControllerCrc = button("QUERY CONTROLLER CRC");
        Button queryMeterCrc = button("QUERY METER CRC");
        crcRow.addView(queryControllerCrc, weight());
        crcRow.addView(queryMeterCrc, weight());
        root.addView(crcRow);

        TextView crcNote = new TextView(this);
        crcNote.setText("Official diagnostics from isinwheel Club 1.1.4 (0x66). These are read-only queries and help fingerprint the restricted controller/display firmware.");
        root.addView(crcNote);

        TextView gearTitle = new TextView(this);''',
    "diagnostic UI")

rep('''        gear5.setOnClickListener(v -> confirmOfficialGear(5));''',
'''        gear5.setOnClickListener(v -> confirmOfficialGear(5));
        queryControllerCrc.setOnClickListener(v -> sendOfficialCrcQuery(1));
        queryMeterCrc.setOnClickListener(v -> sendOfficialCrcQuery(2));''',
    "diagnostic listeners")

# Dynamic 0x66 response length: total frame = 9 + payload-length byte at index 4.
rep('''            int len = type == 0x20 ? 27
                    : type == 0x21 ? 25
                    : type == 0x62 ? 11
                    : (type == 0x35 || type == 0x36 || type == 0x3B) ? 9
                    : -1;''',
'''            int len = type == 0x20 ? 27
                    : type == 0x21 ? 25
                    : type == 0x62 ? 11
                    : (type == 0x35 || type == 0x36 || type == 0x3B) ? 9
                    : -1;
            if (type == 0x66) {
                if (rxStream.size() < 5) return;
                len = 9 + (rxStream.get(4) & 0xFF);
            }''',
    "0x66 dynamic framing")

# Populate official version/country/supplier fields in 0x20.
rep('''            // Official parser exposes this byte as the current highest-gear speed limit.
            currentSpeedLimitRaw = f[12] & 0xFF;
            updateDecoder(light, brake, socLike, packed);''',
'''            // Official parser exposes this byte as the current highest-gear speed limit.
            // Speed values remain KM/H internally even when the display unit is MPH.
            currentSpeedLimitRaw = f[12] & 0xFF;

            // isinwheel Club 1.1.4 YFDMeter1 parser:
            // 17 protocol version, 18 meter version, 19 controller version,
            // 20 country, 21 meter supplier, 22 controller supplier.
            protocolVersion = decodePackedVersion(f[17] & 0xFF);
            meterVersion = decodePackedVersion(f[18] & 0xFF);
            controllerVersion = decodePackedVersion(f[19] & 0xFF);
            countryCode = f[20] & 0xFF;
            meterSupplierCode = f[21] & 0xFF;
            controllerSupplierCode = f[22] & 0xFF;
            updateDecoder(light, brake, socLike, packed);''',
    "status diagnostics")

# Parse 0x66 before 0x35 ACK branch.
rep('''        } else if (type == 0x35 && f.length == 9) {''',
'''        } else if (type == 0x66 && f.length >= 10) {
            int payloadLen = f[4] & 0xFF;
            int selector = f[5] & 0xFF;
            int dataLen = Math.max(0, Math.min(payloadLen - 1, f.length - 10));
            byte[] crcBytes = dataLen > 0 ? Arrays.copyOfRange(f, 6, 6 + dataLen) : new byte[0];
            String crcHex = hex(crcBytes);
            // Official MainViewModel mapping: selector 1 -> controller CRC; selector 2 -> meter CRC.
            if (selector == 1) controllerCrc = crcHex;
            else if (selector == 2) meterCrc = crcHex;
            append("R8 CRC response selector=" + selector + " data=" + crcHex);
            if (latestStatus20 != null) {
                updateDecoder((latestStatus20[5] & 0x10) != 0,
                        (latestStatus20[6] & 0x08) != 0,
                        latestStatus20[8] & 0xFF, latestStatus20[15] & 0xFF);
            }
        } else if (type == 0x35 && f.length == 9) {''',
    "0x66 decoder")

old_update=r'''    private void updateDecoder(boolean light, boolean brake, int socLike, int packed) {
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
new_update=r'''    private void updateDecoder(boolean light, boolean brake, int socLike, int packed) {
        String voltage = batteryCentivolts > 0 ? String.format(Locale.US, "%.2f V", batteryCentivolts / 100.0) : "—";
        String displayUnit = mphUnits ? "MPH" : "KM/H";
        String cap = currentSpeedLimitRaw >= 0
                ? String.format(Locale.US, "%d km/h (~%.1f mph)", currentSpeedLimitRaw, currentSpeedLimitRaw / 1.609344)
                : "—";
        String range = speedLimitMinRaw >= 0 && speedLimitMaxRaw >= 0
                ? String.format(Locale.US, "%d–%d km/h (~%.1f–%.1f mph)",
                    speedLimitMinRaw, speedLimitMaxRaw,
                    speedLimitMinRaw / 1.609344, speedLimitMaxRaw / 1.609344)
                : "not queried";
        String profile = speedLimitMaxRaw >= 0 && speedLimitMaxRaw <= 33
                ? "RESTRICTED-RANGE DETECTED"
                : "range not classified";
        String country = countryName(countryCode);
        String txt = "R8 LIVE  •  Gear: " + gearRaw + "  •  Display unit: " + displayUnit
                + "\nDrive: " + (dualDrive ? "DUAL-WHEEL" : "SINGLE-WHEEL")
                + "  •  Riding mode raw: " + electricModeRaw
                + "\nSpeed cap: " + cap
                + "\nAllowed range: " + range + "  •  " + profile
                + "\nProtocol: " + protocolVersion + "  •  Meter FW: " + meterVersion
                + "  •  Controller FW: " + controllerVersion
                + "\nCountry: " + country + " (" + countryCode + ")"
                + "  •  Meter supplier: " + supplierName(meterSupplierCode) + " (" + meterSupplierCode + ")"
                + "  •  Controller supplier: " + supplierName(controllerSupplierCode) + " (" + controllerSupplierCode + ")"
                + "\nController CRC: " + controllerCrc + "  •  Meter CRC: " + meterCrc
                + "\nLight: " + (light ? "ON" : "OFF") + "  •  Brake: " + (brake ? "ON" : "OFF")
                + "\nBattery: " + socLike + "%  •  Voltage: " + voltage
                + "\nMotor raw: " + motorRaw + "  •  Current/power raw: " + currentLikeRaw
                + String.format(Locale.US, "\nPacked settings byte: 0x%02X", packed & 0xFF);
        if (decodedView != null) decodedView.setText(txt);
    }

    private String decodePackedVersion(int raw) {
        int major = (raw >> 5) & 0x07;
        int minor = raw & 0x1F;
        return String.format(Locale.US, "%d.%02d", major, minor);
    }

    private String countryName(int code) {
        switch (code) {
            case 0: return "00";
            case 1: return "US";
            case 2: return "EU";
            case 3: return "DE";
            case 4: return "ES";
            case 5: return "BR";
            case 6: return "RU";
            default: return "unknown";
        }
    }

    private String supplierName(int code) {
        switch (code) {
            case 1: return "DX";
            case 2: return "HY";
            case 3: return "BSW";
            case 4: return "KCQ";
            case 5: return "XFY";
            case 6: return "ZQ";
            case 7: return "JX";
            default: return "raw";
        }
    }
'''
rep(old_update,new_update,"correct units and diagnostics")

# Correct the dialog: raw speed is km/h, not display units.
rep('''        final int max = speedLimitMaxRaw;
        final String unit = mphUnits ? "mph" : "km/h";
        new AlertDialog.Builder(this)
                .setTitle("Set reported maximum")
                .setMessage("Set the normal highest-gear speed limit to the controller-reported maximum of "
                        + max + " " + unit + "?")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Set " + max + " " + unit, (d,w) -> {
                    byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, (byte)max});
                    writeOfficialFf62(frame, "SET SPEED LIMIT " + max + " " + unit);
                }).show();''',
'''        final int max = speedLimitMaxRaw;
        new AlertDialog.Builder(this)
                .setTitle("Set allowed maximum")
                .setMessage("Set the normal highest-gear speed limit to the controller-reported maximum of "
                        + max + " km/h? This does NOT expand the controller's allowed range.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Set " + max + " km/h", (d,w) -> {
                    byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, (byte)max});
                    writeOfficialFf62(frame, "SET SPEED LIMIT " + max + " KM/H");
                }).show();''',
    "correct speed dialog")

# Add official CRC query sender before gear setter.
rep('''    private void confirmOfficialGear(int gear) {''',
'''    private void sendOfficialCrcQuery(int selector) {
        if (selector != 1 && selector != 2) return;
        // isinwheel Club 1.1.4 s4/a.t(int):
        // d(APP_QUERY_PRO/CRC=0x66, param=0x01, [selector], TRUE)
        // MainViewModel maps 1=controller CRC, 2=meter CRC.
        byte[] frame = officialFrame(new byte[]{0x66, 0x01, 0x01, (byte)selector});
        writeOfficialFf62(frame, selector == 1 ? "QUERY CONTROLLER CRC" : "QUERY METER CRC");
    }

    private void confirmOfficialGear(int gear) {''',
    "CRC sender")

# Auto-query CRC after normal speed-range query has settled.
rep('''            main.postDelayed(this::sendOfficialSpeedQuery, 1200);''',
'''            main.postDelayed(this::sendOfficialSpeedQuery, 1200);
            main.postDelayed(() -> sendOfficialCrcQuery(1), 1900);
            main.postDelayed(() -> sendOfficialCrcQuery(2), 2500);''',
    "auto CRC query")

rep('''        mphUnits = false;
        dualDrive = false;''',
'''        mphUnits = false;
        dualDrive = false;
        protocolVersion = meterVersion = controllerVersion = "—";
        countryCode = meterSupplierCode = controllerSupplierCode = -1;
        meterCrc = controllerCrc = "not queried";''',
    "reset diagnostics")

p.write_text(s)
print("Applied v0.8 corrected KM/H speed interpretation and firmware diagnostics")

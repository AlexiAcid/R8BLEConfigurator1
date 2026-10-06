from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v05 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.4 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.5 ready. Target device name: R8-US");',
    "version")

anchor='''        TextView exp = new TextView(this);
        exp.setText("Experimental v0.4: same known light-state frame, but sends it to FF62 using ATT WRITE WITH RESPONSE so we get a real GATT acknowledgement. Keep the bike stationary.");
        root.addView(exp);
'''
insert='''        TextView exp = new TextView(this);
        exp.setText("Official protocol controls recovered from isinwheel club 1.1.4. Speed query uses command 0x62; speed-limit write uses command 0x36. Keep the bike stationary before changing the limit.");
        root.addView(exp);

        LinearLayout speedRow = row();
        Button querySpeed = button("QUERY SPEED LIMIT");
        Button set56 = button("SET LIMIT 56 KM/H");
        speedRow.addView(querySpeed, weight());
        speedRow.addView(set56, weight());
        root.addView(speedRow);
'''
rep(anchor,insert,"speed controls UI")

rep('''        lightOn.setOnClickListener(v -> confirmLightExperiment(true));
        lightOff.setOnClickListener(v -> confirmLightExperiment(false));
''',
'''        lightOn.setOnClickListener(v -> confirmLightExperiment(true));
        lightOff.setOnClickListener(v -> confirmLightExperiment(false));
        querySpeed.setOnClickListener(v -> sendOfficialSpeedQuery());
        set56.setOnClickListener(v -> confirmOfficialSpeed56());
''',
"speed listeners")

helpers=r'''
    private byte[] officialFrame(byte[] body) {
        int crc = crc16Modbus(body, 0, body.length);
        byte[] out = new byte[body.length + 6];
        out[0] = 0x1A;
        out[1] = (byte)0xA1;
        System.arraycopy(body, 0, out, 2, body.length);
        out[out.length - 4] = (byte)(crc & 0xFF);
        out[out.length - 3] = (byte)((crc >>> 8) & 0xFF);
        out[out.length - 2] = 0x1F;
        out[out.length - 1] = (byte)0xF1;
        return out;
    }

    private void writeOfficialFf62(byte[] out, String label) {
        if (gatt == null) { toast("Connect to R8-US first."); return; }
        BluetoothGattCharacteristic tx = findCharacteristic(R8_TX);
        if (tx == null) { toast("FF62 transmit characteristic not found."); return; }
        append("OFFICIAL " + label + " -> FF62 hex=" + hex(out));
        try {
            if (Build.VERSION.SDK_INT >= 33) {
                int r = gatt.writeCharacteristic(tx, out, BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                append("OFFICIAL FF62 write queue result=" + r);
            } else {
                tx.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                tx.setValue(out);
                append("OFFICIAL FF62 write queued=" + gatt.writeCharacteristic(tx));
            }
        } catch (SecurityException e) { append("Official FF62 write permission error: " + e); }
    }

    private void sendOfficialSpeedQuery() {
        // isinwheel club 1.1.4: querySpeedLimit() -> e(0x62, 0x01, FALSE)
        // e() builds body [command, parameter, 0x00].
        byte[] frame = officialFrame(new byte[]{0x62, 0x01, 0x00});
        writeOfficialFf62(frame, "QUERY SPEED LIMIT");
        toast("Speed-limit query sent. Watch FF61 / export the log.");
    }

    private void confirmOfficialSpeed56() {
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
rep('    private void confirmLightExperiment(boolean on) {\n',helpers+'    private void confirmLightExperiment(boolean on) {\n',"official helpers")

p.write_text(s)
print("Applied v0.5 official isinwheel speed-limit protocol patch")

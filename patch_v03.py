from pathlib import Path

p = Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s = p.read_text()

def need(old, new, label):
    global s
    if old not in s:
        raise SystemExit("patch_v03 missing anchor: " + label)
    s = s.replace(old, new, 1)

need("import android.app.Activity;\n",
     "import android.app.Activity;\nimport android.app.AlertDialog;\n",
     "AlertDialog import")

need("import java.util.ArrayList;\n",
     "import java.util.ArrayList;\nimport java.util.Arrays;\n",
     "Arrays import")

need(
    'private static final UUID CCCD = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");',
    'private static final UUID CCCD = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");\n'
    '    private static final UUID R8_RX = UUID.fromString("0000ff61-0000-1000-8000-00805f9b34fb");\n'
    '    private static final UUID R8_TX = UUID.fromString("0000ff62-0000-1000-8000-00805f9b34fb");',
    "R8 UUID constants"
)

need(
    "    private final List<BluetoothGattCharacteristic> characteristics = new ArrayList<>();",
    "    private final List<BluetoothGattCharacteristic> characteristics = new ArrayList<>();\n"
    "    private final List<Byte> rxStream = new ArrayList<>();\n"
    "    private byte[] latestStatus20;\n"
    "    private long latestStatusAt;\n"
    "    private int motorRaw;\n"
    "    private int batteryCentivolts;\n"
    "    private int currentLikeRaw;",
    "decoder state"
)

need(
    "    private TextView logView;",
    "    private TextView logView;\n    private TextView decodedView;",
    "decoded view"
)

need(
    'append("R8 BLE Configurator v0.2 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.3 ready. Target device name: R8-US");',
    "version"
)

need(
'''        selectedCharView = new TextView(this);
        selectedCharView.setText("Selected characteristic: none");
        root.addView(selectedCharView);
''',
'''        selectedCharView = new TextView(this);
        selectedCharView.setText("Selected characteristic: none");
        root.addView(selectedCharView);

        decodedView = new TextView(this);
        decodedView.setText("R8 decoder: waiting for FF61 telemetry…");
        decodedView.setTextSize(16f);
        decodedView.setPadding(0, dp(8), 0, dp(8));
        root.addView(decodedView);

        LinearLayout lightRow = row();
        Button lightOn = button("TEST LIGHT ON (FF62)");
        Button lightOff = button("TEST LIGHT OFF (FF62)");
        lightRow.addView(lightOn, weight());
        lightRow.addView(lightOff, weight());
        root.addView(lightRow);

        TextView exp = new TextView(this);
        exp.setText("Experimental: uses the latest valid 0x20 status frame from the bike, changes only light bit 0x10, recalculates CRC-16/MODBUS, then writes it to FF62. Keep the bike stationary for this test.");
        root.addView(exp);
''',
"decoder UI"
)

need(
'''        export.setOnClickListener(v -> exportLog());
''',
'''        export.setOnClickListener(v -> exportLog());
        lightOn.setOnClickListener(v -> confirmLightExperiment(true));
        lightOff.setOnClickListener(v -> confirmLightExperiment(false));
''',
"light listeners"
)

need(
'''        @Override
        public void onCharacteristicChanged(BluetoothGatt g, BluetoothGattCharacteristic c, byte[] value) {
            main.post(() -> append("NOTIFY " + c.getUuid() + " hex=" + hex(value) + " ascii=" + ascii(value)));
        }

        @SuppressWarnings("deprecation")
        @Override
        public void onCharacteristicChanged(BluetoothGatt g, BluetoothGattCharacteristic c) {
            if (Build.VERSION.SDK_INT < 33) {
                byte[] v = c.getValue();
                main.post(() -> append("NOTIFY " + c.getUuid() + " hex=" + hex(v) + " ascii=" + ascii(v)));
            }
        }
''',
'''        @Override
        public void onCharacteristicChanged(BluetoothGatt g, BluetoothGattCharacteristic c, byte[] value) {
            byte[] copy = value == null ? new byte[0] : Arrays.copyOf(value, value.length);
            main.post(() -> handleNotification(c, copy));
        }

        @SuppressWarnings("deprecation")
        @Override
        public void onCharacteristicChanged(BluetoothGatt g, BluetoothGattCharacteristic c) {
            if (Build.VERSION.SDK_INT < 33) {
                byte[] v = c.getValue();
                byte[] copy = v == null ? new byte[0] : Arrays.copyOf(v, v.length);
                main.post(() -> handleNotification(c, copy));
            }
        }
''',
"notification handler"
)

need(
'''        append("Loaded " + characteristics.size() + " characteristics. Candidates with WRITE/NOTIFY are sorted to the top and marked ★.");
        append("Swipe inside the characteristic box to scroll. Start with READ/NOTIFY; do not write unknown bytes.");
    }
''',
'''        append("Loaded " + characteristics.size() + " characteristics. Candidates with WRITE/NOTIFY are sorted to the top and marked ★.");
        append("Swipe inside the characteristic box to scroll. Start with READ/NOTIFY; do not write unknown bytes.");
        BluetoothGattCharacteristic rx = findCharacteristic(R8_RX);
        if (rx != null) {
            selectedCharacteristic = rx;
            selectedCharView.setText("Selected characteristic: " + rx.getUuid());
            append("Auto-subscribing R8 FF61 telemetry channel…");
            subscribeSelected();
        }
    }
''',
"auto subscribe"
)

helpers = r'''
    private BluetoothGattCharacteristic findCharacteristic(UUID uuid) {
        for (BluetoothGattCharacteristic c : characteristics) if (uuid.equals(c.getUuid())) return c;
        return null;
    }

    private void handleNotification(BluetoothGattCharacteristic c, byte[] value) {
        append("NOTIFY " + c.getUuid() + " hex=" + hex(value) + " ascii=" + ascii(value));
        if (!R8_RX.equals(c.getUuid()) || value == null || value.length == 0) return;
        for (byte b : value) rxStream.add(b);
        parseR8Stream();
    }

    private void parseR8Stream() {
        while (true) {
            while (rxStream.size() >= 2 && !((rxStream.get(0) & 0xFF) == 0x1A && (rxStream.get(1) & 0xFF) == 0xA1)) rxStream.remove(0);
            if (rxStream.size() < 3) return;
            int type = rxStream.get(2) & 0xFF;
            int len = type == 0x20 ? 27 : type == 0x21 ? 25 : -1;
            if (len < 0) { rxStream.remove(0); continue; }
            if (rxStream.size() < len) return;
            byte[] frame = new byte[len];
            for (int i=0;i<len;i++) frame[i] = rxStream.get(i);
            if ((frame[len-2] & 0xFF) != 0x1F || (frame[len-1] & 0xFF) != 0xF1) { rxStream.remove(0); continue; }
            int stored = (frame[len-4] & 0xFF) | ((frame[len-3] & 0xFF) << 8);
            int calc = crc16Modbus(frame, 2, len-4);
            if (stored != calc) { append("R8 frame CRC mismatch type=0x" + Integer.toHexString(type)); rxStream.remove(0); continue; }
            for (int i=0;i<len;i++) rxStream.remove(0);
            decodeR8Frame(frame);
        }
    }

    private void decodeR8Frame(byte[] f) {
        int type = f[2] & 0xFF;
        if (type == 0x20 && f.length == 27) {
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
    }

    private void updateDecoder(boolean light, boolean brake, int socLike, int counterLike) {
        String voltage = batteryCentivolts > 0 ? String.format(Locale.US, "%.2f V", batteryCentivolts / 100.0) : "—";
        String txt = "R8 LIVE  •  Light: " + (light ? "ON" : "OFF")
                + "  •  Brake: " + (brake ? "ON" : "OFF")
                + "\nBattery-like: " + socLike + "%  •  Voltage: " + voltage
                + "\nMotor-speed raw: " + motorRaw + "  •  Current/power raw: " + currentLikeRaw
                + "  •  Counter: " + counterLike;
        if (decodedView != null) decodedView.setText(txt);
    }

    private static int le16(byte[] b, int i) { return (b[i] & 0xFF) | ((b[i+1] & 0xFF) << 8); }

    private static int crc16Modbus(byte[] data, int start, int endExclusive) {
        int crc = 0xFFFF;
        for (int i=start; i<endExclusive; i++) {
            crc ^= data[i] & 0xFF;
            for (int j=0;j<8;j++) crc = (crc & 1) != 0 ? (crc >>> 1) ^ 0xA001 : (crc >>> 1);
        }
        return crc & 0xFFFF;
    }

    private void confirmLightExperiment(boolean on) {
        new AlertDialog.Builder(this)
                .setTitle("Experimental R8 light command")
                .setMessage("Keep the bike stationary. This clones the latest valid status packet, changes only the light bit, recalculates its CRC, and sends it to FF62. Continue?")
                .setNegativeButton("Cancel", null)
                .setPositiveButton(on ? "Test Light ON" : "Test Light OFF", (d,w) -> sendLightExperiment(on))
                .show();
    }

    private void sendLightExperiment(boolean on) {
        if (gatt == null) { toast("Connect to R8-US first."); return; }
        if (latestStatus20 == null || System.currentTimeMillis() - latestStatusAt > 3000) { toast("No recent valid 0x20 status frame. Wait for live telemetry first."); return; }
        if ((latestStatus20[6] & 0x08) != 0) { toast("Release the brake before this experiment."); return; }
        if (motorRaw != 0 || currentLikeRaw != 0) { toast("Wait until the wheel/motor is fully stopped."); return; }
        BluetoothGattCharacteristic tx = findCharacteristic(R8_TX);
        if (tx == null) { toast("FF62 transmit characteristic not found."); return; }
        byte[] out = Arrays.copyOf(latestStatus20, latestStatus20.length);
        if (on) out[5] = (byte)((out[5] & 0xFF) | 0x10); else out[5] = (byte)((out[5] & 0xFF) & ~0x10);
        int crc = crc16Modbus(out, 2, out.length - 4);
        out[out.length-4] = (byte)(crc & 0xFF);
        out[out.length-3] = (byte)((crc >>> 8) & 0xFF);
        append("EXPERIMENT LIGHT " + (on ? "ON" : "OFF") + " -> FF62 hex=" + hex(out));
        try {
            if (Build.VERSION.SDK_INT >= 33) {
                int r = gatt.writeCharacteristic(tx, out, BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                append("FF62 experimental write queue result=" + r);
            } else {
                tx.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                tx.setValue(out);
                append("FF62 experimental write queued=" + gatt.writeCharacteristic(tx));
            }
        } catch (SecurityException e) { append("Experimental write permission error: " + e); }
    }

'''

need("    private void readSelected() {\n", helpers + "    private void readSelected() {\n", "decoder helpers")

need(
'''        selectedCharacteristic = null;
        characteristics.clear();
''',
'''        selectedCharacteristic = null;
        characteristics.clear();
        rxStream.clear();
        latestStatus20 = null;
        latestStatusAt = 0;
        motorRaw = batteryCentivolts = currentLikeRaw = 0;
''',
"disconnect state"
)

p.write_text(s)
print("Applied R8 v0.3 protocol decoder/light experiment patch")

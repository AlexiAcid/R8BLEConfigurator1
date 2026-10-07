from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v10 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.9 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.0 ready. Target device name: R8-US");',
    "version")

rep('''    private String controllerCrc = "not queried";''',
'''    private String controllerCrc = "not queried";

    // Passive physical-button trace. This never sends controller-setting commands.
    // It watches FF61 plus the alternate custom notification channel and
    // round-robin reads the non-standard readable characteristics.
    private boolean buttonTraceActive = false;
    private boolean traceReadPending = false;
    private int traceReadIndex = 0;
    private long traceStartedAt = 0;
    private final List<BluetoothGattCharacteristic> traceReadTargets = new ArrayList<>();
    private final Map<String,String> traceLastReadHex = new LinkedHashMap<>();''',
    "trace state")

# Add the physical-button trace UI before normal gear controls.
rep('''        TextView identityNote = new TextView(this);
        identityNote.setText("Read-only official queries: 0x60 asks the bike for its current-user/device profile state. 0x61 reads the device serial response. The SN query can place the bike serial in the exported log, so use it only if you want that fingerprint included.");
        root.addView(identityNote);

        TextView gearTitle = new TextView(this);''',
'''        TextView identityNote = new TextView(this);
        identityNote.setText("Read-only official queries: 0x60 asks the bike for its current-user/device profile state. 0x61 reads the device serial response. The SN query can place the bike serial in the exported log, so use it only if you want that fingerprint included.");
        root.addView(identityNote);

        TextView traceTitle = new TextView(this);
        traceTitle.setText("PHYSICAL BUTTON / P05 TRACE");
        traceTitle.setTextSize(17f);
        root.addView(traceTitle);

        LinearLayout traceRow = row();
        Button startTrace = button("START BUTTON TRACE");
        Button stopTrace = button("STOP TRACE");
        traceRow.addView(startTrace, weight());
        traceRow.addView(stopTrace, weight());
        root.addView(traceRow);

        LinearLayout markerRow = row();
        Button markPlus = button("MARK + / LEFT");
        Button markMinus = button("MARK - / RIGHT");
        Button markPower = button("MARK POWER");
        markerRow.addView(markPlus, weight());
        markerRow.addView(markMinus, weight());
        markerRow.addView(markPower, weight());
        root.addView(markerRow);

        TextView traceNote = new TextView(this);
        traceNote.setText("Passive diagnostic mode: records every FF61 packet, subscribes to the alternate custom notify channel FF02, and repeatedly reads FF21, FF22, FF00, FF02 and FF03 when present. It does not alter bike settings. Use the MARK buttons immediately before/after a physical button action if convenient.");
        root.addView(traceNote);

        TextView gearTitle = new TextView(this);''',
    "trace UI")

rep('''        querySn.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("Read device serial?")
                .setMessage("This is read-only, but the returned bike serial may be written into the exported diagnostic log.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Query SN", (d,w) -> sendOfficialSimpleQuery(0x61, "QUERY DEVICE SN"))
                .show());''',
'''        querySn.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("Read device serial?")
                .setMessage("This is read-only, but the returned bike serial may be written into the exported diagnostic log.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Query SN", (d,w) -> sendOfficialSimpleQuery(0x61, "QUERY DEVICE SN"))
                .show());
        startTrace.setOnClickListener(v -> startButtonTrace());
        stopTrace.setOnClickListener(v -> stopButtonTrace());
        markPlus.setOnClickListener(v -> traceMarker("PHYSICAL + / LEFT"));
        markMinus.setOnClickListener(v -> traceMarker("PHYSICAL - / RIGHT"));
        markPower.setOnClickListener(v -> traceMarker("PHYSICAL POWER"));''',
    "trace listeners")

# Route read callbacks through one handler so polling is properly serialized.
rep('''        @Override
        public void onCharacteristicRead(BluetoothGatt g, BluetoothGattCharacteristic c, byte[] value, int statusCode) {
            main.post(() -> append("READ " + c.getUuid() + " status=" + statusCode + " hex=" + hex(value) + " ascii=" + ascii(value)));
        }

        @SuppressWarnings("deprecation")
        @Override
        public void onCharacteristicRead(BluetoothGatt g, BluetoothGattCharacteristic c, int statusCode) {
            if (Build.VERSION.SDK_INT < 33) {
                byte[] v = c.getValue();
                main.post(() -> append("READ " + c.getUuid() + " status=" + statusCode + " hex=" + hex(v) + " ascii=" + ascii(v)));
            }
        }''',
'''        @Override
        public void onCharacteristicRead(BluetoothGatt g, BluetoothGattCharacteristic c, byte[] value, int statusCode) {
            byte[] copy = value == null ? new byte[0] : Arrays.copyOf(value, value.length);
            main.post(() -> handleReadResult(c, copy, statusCode));
        }

        @SuppressWarnings("deprecation")
        @Override
        public void onCharacteristicRead(BluetoothGatt g, BluetoothGattCharacteristic c, int statusCode) {
            if (Build.VERSION.SDK_INT < 33) {
                byte[] v = c.getValue();
                byte[] copy = v == null ? new byte[0] : Arrays.copyOf(v, v.length);
                main.post(() -> handleReadResult(c, copy, statusCode));
            }
        }''',
    "serialized read callbacks")

# Stop trace cleanly if BLE disconnects.
rep('''            } else if (newState == android.bluetooth.BluetoothProfile.STATE_DISCONNECTED) {
                main.post(() -> status.setText("Disconnected"));
            }''',
'''            } else if (newState == android.bluetooth.BluetoothProfile.STATE_DISCONNECTED) {
                main.post(() -> {
                    status.setText("Disconnected");
                    if (buttonTraceActive) stopButtonTrace();
                });
            }''',
    "disconnect trace stop")

# Add passive trace methods before readSelected().
rep('''    private void readSelected() {''',
'''    private void traceMarker(String label) {
        if (!buttonTraceActive) {
            toast("Start Button Trace first.");
            return;
        }
        long elapsed = System.currentTimeMillis() - traceStartedAt;
        append("========== TRACE MARK " + label + "  t=" + elapsed + "ms ==========");
    }

    private boolean isStandardGattService(BluetoothGattCharacteristic c) {
        if (c == null || c.getService() == null) return false;
        String u = c.getService().getUuid().toString().toLowerCase(Locale.US);
        return u.equals("00001800-0000-1000-8000-00805f9b34fb")
                || u.equals("00001801-0000-1000-8000-00805f9b34fb");
    }

    private void startButtonTrace() {
        if (gatt == null) {
            toast("Connect to R8-US first.");
            return;
        }
        if (buttonTraceActive) {
            toast("Button trace is already running.");
            return;
        }

        buttonTraceActive = true;
        traceReadPending = false;
        traceReadIndex = 0;
        traceStartedAt = System.currentTimeMillis();
        traceReadTargets.clear();
        traceLastReadHex.clear();

        for (BluetoothGattCharacteristic c : characteristics) {
            if ((c.getProperties() & BluetoothGattCharacteristic.PROPERTY_READ) != 0
                    && !isStandardGattService(c)) {
                traceReadTargets.add(c);
            }
        }

        append("========== BUTTON TRACE START ==========");
        append("TRACE targets: " + traceReadTargets.size()
                + " non-standard readable characteristic(s). FF61 raw notifications remain captured continuously.");
        append("TRACE instructions: leave 1-2 seconds between physical button actions. Use MARK buttons if useful.");

        enableAlternateTraceNotify();

        // Give any CCCD write time to finish before the first read.
        main.postDelayed(this::traceReadNext, 700);
    }

    private void stopButtonTrace() {
        if (!buttonTraceActive) return;
        long elapsed = System.currentTimeMillis() - traceStartedAt;
        buttonTraceActive = false;
        traceReadPending = false;
        append("========== BUTTON TRACE STOP  duration=" + elapsed + "ms ==========");
        append("TRACE captured " + traceLastReadHex.size() + " readable characteristic baseline(s)/changes plus raw notifications.");
        toast("Button trace stopped. Export the log and send it to me.");
    }

    private void enableAlternateTraceNotify() {
        if (gatt == null) return;
        for (BluetoothGattCharacteristic c : characteristics) {
            String u = c.getUuid().toString().toLowerCase(Locale.US);
            if (!u.endsWith("ff02") || (c.getProperties() &
                    (BluetoothGattCharacteristic.PROPERTY_NOTIFY | BluetoothGattCharacteristic.PROPERTY_INDICATE)) == 0) {
                continue;
            }
            try {
                boolean local = gatt.setCharacteristicNotification(c, true);
                append("TRACE alternate notify local=" + local + " uuid=" + c.getUuid());
                BluetoothGattDescriptor cccd = c.getDescriptor(CCCD);
                if (cccd == null) {
                    append("TRACE alternate notify has no CCCD: " + c.getUuid());
                    return;
                }
                byte[] enable = (c.getProperties() & BluetoothGattCharacteristic.PROPERTY_INDICATE) != 0
                        ? BluetoothGattDescriptor.ENABLE_INDICATION_VALUE
                        : BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE;
                if (Build.VERSION.SDK_INT >= 33) {
                    int r = gatt.writeDescriptor(cccd, enable);
                    append("TRACE alternate CCCD write result=" + r);
                } else {
                    //noinspection deprecation
                    cccd.setValue(enable);
                    //noinspection deprecation
                    append("TRACE alternate CCCD write queued=" + gatt.writeDescriptor(cccd));
                }
            } catch (SecurityException e) {
                append("TRACE alternate notify permission error: " + e);
            }
            return;
        }
        append("TRACE alternate FF02 notification characteristic not found.");
    }

    private void traceReadNext() {
        if (!buttonTraceActive || gatt == null || traceReadPending) return;
        if (traceReadTargets.isEmpty()) {
            main.postDelayed(this::traceReadNext, 500);
            return;
        }

        BluetoothGattCharacteristic c = traceReadTargets.get(traceReadIndex % traceReadTargets.size());
        traceReadIndex = (traceReadIndex + 1) % traceReadTargets.size();
        try {
            traceReadPending = true;
            boolean ok = gatt.readCharacteristic(c);
            if (!ok) {
                traceReadPending = false;
                append("TRACE read queue rejected uuid=" + c.getUuid());
                main.postDelayed(this::traceReadNext, 180);
            }
        } catch (SecurityException e) {
            traceReadPending = false;
            append("TRACE read permission error: " + e);
            main.postDelayed(this::traceReadNext, 250);
        }
    }

    private void handleReadResult(BluetoothGattCharacteristic c, byte[] value, int statusCode) {
        append("READ " + c.getUuid() + " status=" + statusCode + " hex=" + hex(value) + " ascii=" + ascii(value));

        if (buttonTraceActive) {
            String key = c.getUuid().toString();
            String now = hex(value);
            String old = traceLastReadHex.put(key, now);
            long elapsed = System.currentTimeMillis() - traceStartedAt;
            if (old == null) {
                append("TRACE BASELINE t=" + elapsed + "ms uuid=" + key + " hex=" + now);
            } else if (!old.equals(now)) {
                append("TRACE CHANGE t=" + elapsed + "ms uuid=" + key + " old=" + old + " new=" + now);
            }
            traceReadPending = false;
            main.postDelayed(this::traceReadNext, 120);
        }
    }

    private void readSelected() {''',
    "trace methods")

# Ensure disconnect/reset clears trace state.
rep('''        selectedCharacteristic = null;
        characteristics.clear();
        rxStream.clear();''',
'''        buttonTraceActive = false;
        traceReadPending = false;
        traceReadTargets.clear();
        traceLastReadHex.clear();
        selectedCharacteristic = null;
        characteristics.clear();
        rxStream.clear();''',
    "trace reset")

p.write_text(s)
print("Applied v1.0 passive physical-button/P05 trace")

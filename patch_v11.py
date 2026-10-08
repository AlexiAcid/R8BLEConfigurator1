from pathlib import Path

java = Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s = java.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v11 missing anchor: " + label)
    s = s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.0 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.1 ready. Target device name: R8-US");',
    "version")

rep('''import android.content.pm.PackageManager;
import android.net.Uri;''',
'''import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.Uri;''',
    "location imports")

rep('''import android.widget.ScrollView;
import android.widget.TextView;''',
'''import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;''',
    "seekbar import")

rep('''    private static final int REQ_EXPORT = 1002;''',
'''    private static final int REQ_EXPORT = 1002;
    private static final int REQ_GPS = 1003;''',
    "gps request code")

rep('''    private TextView decodedView;''',
'''    private TextView decodedView;
    private TextView rideStateView;
    private TextView gpsSpeedView;
    private TextView gpsStatusView;
    private SeekBar speedCapSeek;
    private TextView speedCapValueView;
    private LocationManager locationManager;
    private Location lastGpsLocation;
    private boolean gpsRunning = false;
    private boolean autoConnectRequested = false;''',
    "ride fields")

rep('''        scroll.addView(root);

        TextView title = new TextView(this);''',
'''        scroll.addView(root);

        // v1.1 Ride Dashboard: large, simple controls first; all reverse-engineering tools remain below.
        LinearLayout tabs = row();
        Button tabRide = button("RIDE DASHBOARD");
        Button tabTools = button("ADVANCED TOOLS");
        tabs.addView(tabRide, weight());
        tabs.addView(tabTools, weight());
        root.addView(tabs);

        TextView rideTitle = new TextView(this);
        rideTitle.setText("R8 RIDE DASHBOARD");
        rideTitle.setTextSize(24f);
        rideTitle.setPadding(0, dp(10), 0, dp(4));
        root.addView(rideTitle);

        status = new TextView(this);
        status.setText("Disconnected");
        status.setTextSize(17f);
        root.addView(status);

        gpsSpeedView = new TextView(this);
        gpsSpeedView.setText("GPS  —.- km/h");
        gpsSpeedView.setTextSize(44f);
        gpsSpeedView.setPadding(0, dp(12), 0, dp(4));
        root.addView(gpsSpeedView);

        gpsStatusView = new TextView(this);
        gpsStatusView.setText("Phone GPS speedometer stopped.");
        root.addView(gpsStatusView);

        LinearLayout gpsRow = row();
        Button gpsStart = button("START GPS SPEED");
        Button gpsStop = button("STOP GPS");
        gpsRow.addView(gpsStart, weight());
        gpsRow.addView(gpsStop, weight());
        root.addView(gpsRow);

        LinearLayout connectRow = row();
        Button autoConnect = button("AUTO CONNECT R8-US");
        Button quickQuery = button("REFRESH BIKE");
        connectRow.addView(autoConnect, weight());
        connectRow.addView(quickQuery, weight());
        root.addView(connectRow);

        rideStateView = new TextView(this);
        rideStateView.setText("Bike data: connect to R8-US.");
        rideStateView.setTextSize(16f);
        rideStateView.setPadding(0, dp(8), 0, dp(8));
        root.addView(rideStateView);

        TextView gearQuickTitle = label("Assist / electric gear");
        root.addView(gearQuickTitle);

        LinearLayout quickGearRow1 = row();
        Button quickGear1 = button("GEAR 1");
        Button quickGear2 = button("GEAR 2");
        Button quickGear3 = button("GEAR 3");
        quickGearRow1.addView(quickGear1, weight());
        quickGearRow1.addView(quickGear2, weight());
        quickGearRow1.addView(quickGear3, weight());
        root.addView(quickGearRow1);

        LinearLayout quickGearRow2 = row();
        Button quickGear4 = button("GEAR 4");
        Button quickGear5 = button("GEAR 5");
        quickGearRow2.addView(quickGear4, weight());
        quickGearRow2.addView(quickGear5, weight());
        root.addView(quickGearRow2);

        TextView speedTitle = label("Normal controller speed cap");
        root.addView(speedTitle);
        speedCapValueView = new TextView(this);
        speedCapValueView.setText("Cap: query bike first");
        root.addView(speedCapValueView);
        speedCapSeek = new SeekBar(this);
        speedCapSeek.setMax(16);
        speedCapSeek.setProgress(16);
        root.addView(speedCapSeek);

        LinearLayout capRow = row();
        Button queryRangeRide = button("QUERY RANGE");
        Button applyCap = button("APPLY CAP");
        capRow.addView(queryRangeRide, weight());
        capRow.addView(applyCap, weight());
        root.addView(capRow);

        LinearLayout utilityRow = row();
        Button toggleUnits = button("TOGGLE MPH / KM/H");
        Button singleMotor = button("SINGLE MOTOR MODE");
        utilityRow.addView(toggleUnits, weight());
        utilityRow.addView(singleMotor, weight());
        root.addView(utilityRow);

        TextView rideNote = new TextView(this);
        rideNote.setText("Ride controls use only commands already recovered from the official isinwheel app. Pull over before using phone controls. GPS speed comes from the phone, not the bike display.");
        rideNote.setPadding(0, dp(6), 0, dp(16));
        root.addView(rideNote);

        TextView advancedAnchor = new TextView(this);
        advancedAnchor.setText("ADVANCED / DIAGNOSTIC TOOLS");
        advancedAnchor.setTextSize(20f);
        advancedAnchor.setPadding(0, dp(18), 0, dp(4));
        root.addView(advancedAnchor);

        tabRide.setOnClickListener(v -> scroll.post(() -> scroll.smoothScrollTo(0, 0)));
        tabTools.setOnClickListener(v -> scroll.post(() -> scroll.smoothScrollTo(0, advancedAnchor.getTop())));
        gpsStart.setOnClickListener(v -> startGpsSpeedometer());
        gpsStop.setOnClickListener(v -> stopGpsSpeedometer());
        autoConnect.setOnClickListener(v -> autoConnectR8());
        quickQuery.setOnClickListener(v -> {
            sendOfficialSpeedQuery();
            toast("Bike refresh sent.");
        });
        quickGear1.setOnClickListener(v -> sendRideGear(1));
        quickGear2.setOnClickListener(v -> sendRideGear(2));
        quickGear3.setOnClickListener(v -> sendRideGear(3));
        quickGear4.setOnClickListener(v -> sendRideGear(4));
        quickGear5.setOnClickListener(v -> sendRideGear(5));
        queryRangeRide.setOnClickListener(v -> sendOfficialSpeedQuery());
        applyCap.setOnClickListener(v -> applyRideSpeedCap());
        toggleUnits.setOnClickListener(v -> toggleRideUnits());
        singleMotor.setOnClickListener(v -> confirmOfficialDrive(false));
        speedCapSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                int min = speedLimitMinRaw >= 0 ? speedLimitMinRaw : 17;
                int value = min + progress;
                if (speedLimitMaxRaw >= min) value = Math.min(value, speedLimitMaxRaw);
                if (speedCapValueView != null)
                    speedCapValueView.setText("Cap: " + value + " km/h  (~" + String.format(Locale.US, "%.1f", value / 1.609344) + " mph)");
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        TextView title = new TextView(this);''',
    "ride dashboard")

# The connection status now lives in the Ride Dashboard, so don't create a second status field below.
rep('''        status = new TextView(this);
        status.setText("Disconnected");
        status.setTextSize(16f);
        root.addView(status);
''',
'''        TextView advancedStatus = new TextView(this);
        advancedStatus.setText("Connection status is shown in the Ride Dashboard above.");
        root.addView(advancedStatus);
''',
    "advanced status")

# Auto-connect as soon as a matching advertisement is seen.
rep('''            if (!devices.containsKey(addr)) {
                devices.put(addr, d);
                final String n = name;
                final int rssi = result.getRssi();
                main.post(() -> deviceAdapter.add((n.equalsIgnoreCase("R8-US") ? "★ TARGET " : "") + n + " RSSI " + rssi + " [" + addr + "]"));
            }
''',
'''            if (!devices.containsKey(addr)) {
                devices.put(addr, d);
                final String n = name;
                final int rssi = result.getRssi();
                main.post(() -> deviceAdapter.add((n.equalsIgnoreCase("R8-US") ? "★ TARGET " : "") + n + " RSSI " + rssi + " [" + addr + "]"));
            }
            if (autoConnectRequested && name.equalsIgnoreCase("R8-US")) {
                autoConnectRequested = false;
                try { if (scanner != null) scanner.stopScan(this); } catch (Exception ignored) {}
                main.post(() -> connect(d));
            }
''',
    "auto connect callback")

# Keep Ride Dashboard live in parallel with the detailed decoder.
rep('''        if (decodedView != null) decodedView.setText(txt);
    }
''',
'''        if (decodedView != null) decodedView.setText(txt);
        if (rideStateView != null) {
            String ride = "Bike: Gear " + gearRaw
                    + "  •  Battery " + socLike + "%"
                    + "  •  " + voltage
                    + "\nController cap: " + cap
                    + "  •  Range: " + range
                    + "\nLight " + (light ? "ON" : "OFF")
                    + "  •  Brake " + (brake ? "ON" : "OFF")
                    + "  •  " + (dualDrive ? "DUAL" : "SINGLE") + " motor mode";
            rideStateView.setText(ride);
        }
    }
''',
    "ride live state")

# Synchronize the Ride speed-cap slider to the actual queried range.
rep('''            speedLimitMinRaw = f[5] & 0xFF;
            speedLimitMaxRaw = f[6] & 0xFF;
            append("R8 SPEED LIMIT RANGE response: min=" + speedLimitMinRaw + " max=" + speedLimitMaxRaw);''',
'''            speedLimitMinRaw = f[5] & 0xFF;
            speedLimitMaxRaw = f[6] & 0xFF;
            append("R8 SPEED LIMIT RANGE response: min=" + speedLimitMinRaw + " max=" + speedLimitMaxRaw);
            if (speedCapSeek != null) {
                int span = Math.max(0, speedLimitMaxRaw - speedLimitMinRaw);
                speedCapSeek.setMax(span);
                int cur = currentSpeedLimitRaw >= speedLimitMinRaw ? currentSpeedLimitRaw : speedLimitMaxRaw;
                speedCapSeek.setProgress(Math.max(0, Math.min(span, cur - speedLimitMinRaw)));
            }''',
    "sync speed slider")

# Add ride/GPS helpers before the trace marker helpers.
rep('''    private void traceMarker(String label) {''',
'''    private void autoConnectR8() {
        if (!hasBlePermission()) {
            ensurePermissions();
            toast("Grant Bluetooth permission, then tap Auto Connect again.");
            return;
        }
        if (gatt != null) {
            toast("Already connected.");
            return;
        }
        autoConnectRequested = true;
        toast("Searching for R8-US…");
        startScan();
    }

    private void sendRideGear(int gear) {
        if (gatt == null) {
            toast("Connect to R8-US first.");
            return;
        }
        if (gear < 1 || gear > 5) return;
        // Exact official APP_ELECTRIC_GEAR command recovered from isinwheel Club.
        byte[] frame = officialFrame(new byte[]{0x35, 0x02, 0x02, (byte)gear, 0x00});
        writeOfficialFf62(frame, "RIDE SET ELECTRIC GEAR " + gear);
    }

    private void applyRideSpeedCap() {
        if (!stationaryForSetting()) return;
        if (speedLimitMinRaw < 0 || speedLimitMaxRaw < 0) {
            toast("Query the controller range first.");
            return;
        }
        int value = speedLimitMinRaw + speedCapSeek.getProgress();
        value = Math.max(speedLimitMinRaw, Math.min(speedLimitMaxRaw, value));
        byte[] frame = officialFrame(new byte[]{0x36, 0x02, 0x01, (byte)value});
        writeOfficialFf62(frame, "RIDE SET SPEED CAP " + value + " KM/H");
        final int chosen = value;
        main.postDelayed(this::sendOfficialSpeedQuery, 500);
        toast("Requested " + chosen + " km/h cap.");
    }

    private void toggleRideUnits() {
        if (gatt == null) {
            toast("Connect to R8-US first.");
            return;
        }
        // Official APP_UNIT command 0x3C. The status bit uses 1 for MPH and 0 for KM/H.
        int raw = mphUnits ? 0 : 1;
        byte[] frame = officialFrame(new byte[]{0x3C, 0x02, 0x01, (byte)raw});
        writeOfficialFf62(frame, raw == 1 ? "SET DISPLAY UNIT MPH" : "SET DISPLAY UNIT KM/H");
    }

    private void startGpsSpeedometer() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, REQ_GPS);
            return;
        }
        if (locationManager == null)
            locationManager = (LocationManager)getSystemService(Context.LOCATION_SERVICE);
        if (locationManager == null) {
            toast("Location service unavailable.");
            return;
        }
        try {
            gpsRunning = true;
            gpsStatusView.setText("GPS speedometer running…");
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 500L, 0f, gpsListener);
            Location last = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (last != null) onGpsLocation(last);
        } catch (SecurityException e) {
            gpsRunning = false;
            gpsStatusView.setText("GPS permission unavailable.");
        }
    }

    private void stopGpsSpeedometer() {
        gpsRunning = false;
        if (locationManager != null) {
            try { locationManager.removeUpdates(gpsListener); } catch (SecurityException ignored) {}
        }
        if (gpsStatusView != null) gpsStatusView.setText("Phone GPS speedometer stopped.");
    }

    private final LocationListener gpsListener = new LocationListener() {
        @Override public void onLocationChanged(Location location) { onGpsLocation(location); }
        @Override public void onProviderEnabled(String provider) {
            if (gpsStatusView != null) gpsStatusView.setText("GPS available; waiting for speed…");
        }
        @Override public void onProviderDisabled(String provider) {
            if (gpsStatusView != null) gpsStatusView.setText("Phone GPS is disabled.");
        }
    };

    private void onGpsLocation(Location location) {
        if (location == null || gpsSpeedView == null) return;
        float metersPerSecond = 0f;
        if (location.hasSpeed()) {
            metersPerSecond = Math.max(0f, location.getSpeed());
        } else if (lastGpsLocation != null) {
            long dt = location.getTime() - lastGpsLocation.getTime();
            if (dt > 250) {
                metersPerSecond = lastGpsLocation.distanceTo(location) / (dt / 1000f);
            }
        }
        lastGpsLocation = location;
        double kmh = metersPerSecond * 3.6;
        double mph = kmh / 1.609344;
        gpsSpeedView.setText(String.format(Locale.US, "GPS  %.1f km/h  •  %.1f mph", kmh, mph));
        if (gpsStatusView != null) {
            String acc = location.hasAccuracy() ? String.format(Locale.US, " ±%.0f m", location.getAccuracy()) : "";
            gpsStatusView.setText("Phone GPS" + acc);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQ_GPS && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startGpsSpeedometer();
        }
    }

    private void traceMarker(String label) {''',
    "ride helpers")

# Stop GPS cleanly with the Activity.
rep('''    protected void onDestroy() {
        disconnectGatt();
        super.onDestroy();
    }''',
'''    protected void onDestroy() {
        stopGpsSpeedometer();
        disconnectGatt();
        super.onDestroy();
    }''',
    "destroy gps")

java.write_text(s)

manifest = Path("R8BLEConfigurator/app/src/main/AndroidManifest.xml")
m = manifest.read_text()
if 'android.permission.ACCESS_FINE_LOCATION" android:maxSdkVersion="30"' in m:
    m = m.replace('android.permission.ACCESS_FINE_LOCATION" android:maxSdkVersion="30"',
                  'android.permission.ACCESS_FINE_LOCATION"')
elif 'android.permission.ACCESS_FINE_LOCATION"' not in m:
    m = m.replace('<uses-feature android:name="android.hardware.bluetooth_le" android:required="true" />',
                  '<uses-feature android:name="android.hardware.bluetooth_le" android:required="true" />\n    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />')
if 'android.hardware.location.gps' not in m:
    m = m.replace('<uses-feature android:name="android.hardware.bluetooth_le" android:required="true" />',
                  '<uses-feature android:name="android.hardware.bluetooth_le" android:required="true" />\n    <uses-feature android:name="android.hardware.location.gps" android:required="false" />')
manifest.write_text(m)

print("Applied v1.1 ride dashboard + phone GPS speedometer")

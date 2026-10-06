from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v07 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.6 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.7 ready. Target device name: R8-US");',
    "version")

# Insert direct gear controls after speed controls.
anchor='''        root.addView(speedRow);

        LinearLayout driveRow = row();
'''
insert='''        root.addView(speedRow);

        TextView gearTitle = new TextView(this);
        gearTitle.setText("OFFICIAL ELECTRIC GEAR (0x35) — live current gear is shown above");
        root.addView(gearTitle);

        LinearLayout gearRow1 = row();
        Button gear1 = button("GEAR 1");
        Button gear2 = button("GEAR 2");
        Button gear3 = button("GEAR 3");
        gearRow1.addView(gear1, weight());
        gearRow1.addView(gear2, weight());
        gearRow1.addView(gear3, weight());
        root.addView(gearRow1);

        LinearLayout gearRow2 = row();
        Button gear4 = button("GEAR 4");
        Button gear5 = button("GEAR 5 / MAX");
        gearRow2.addView(gear4, weight());
        gearRow2.addView(gear5, weight());
        root.addView(gearRow2);

        TextView gearNote = new TextView(this);
        gearNote.setText("Recovered from isinwheel club 1.1.4: APP_ELECTRIC_GEAR = 0x35. The official app sends payload [gear, 0]. Test Gear 5 with the bike stationary first.");
        root.addView(gearNote);

        LinearLayout driveRow = row();
'''
rep(anchor,insert,"gear UI")

# Disable dual-drive button for this user's known single-motor R8.
rep('''        Button dualDriveBtn = button("DUAL-WHEEL DRIVE");
        driveRow.addView(singleDrive, weight());
        driveRow.addView(dualDriveBtn, weight());
''',
'''        Button dualDriveBtn = button("DUAL DRIVE (NOT FOR THIS BIKE)");
        dualDriveBtn.setEnabled(false);
        driveRow.addView(singleDrive, weight());
        driveRow.addView(dualDriveBtn, weight());
''',
    "disable dual")

# Add listeners.
rep('''        singleDrive.setOnClickListener(v -> confirmOfficialDrive(false));
        dualDriveBtn.setOnClickListener(v -> confirmOfficialDrive(true));
''',
'''        singleDrive.setOnClickListener(v -> confirmOfficialDrive(false));
        dualDriveBtn.setOnClickListener(v -> confirmOfficialDrive(true));
        gear1.setOnClickListener(v -> confirmOfficialGear(1));
        gear2.setOnClickListener(v -> confirmOfficialGear(2));
        gear3.setOnClickListener(v -> confirmOfficialGear(3));
        gear4.setOnClickListener(v -> confirmOfficialGear(4));
        gear5.setOnClickListener(v -> confirmOfficialGear(5));
''',
    "gear listeners")

# Teach stream parser the official 0x35 ACK packet.
rep(''': (type == 0x36 || type == 0x3B) ? 9
                    : -1;''',
''': (type == 0x35 || type == 0x36 || type == 0x3B) ? 9
                    : -1;''',
    "gear ack frame length")

# Decode 0x35 ACK.
rep('''        } else if (type == 0x36 && f.length == 9) {
            append("R8 SPEED LIMIT SET ACK status=" + (f[4] & 0xFF));
            main.postDelayed(this::sendOfficialSpeedQuery, 500);
        } else if (type == 0x3B && f.length == 9) {
''',
'''        } else if (type == 0x35 && f.length == 9) {
            append("R8 ELECTRIC-GEAR SET ACK status=" + (f[4] & 0xFF));
            toast("Gear command acknowledged. LIVE Gear should update.");
        } else if (type == 0x36 && f.length == 9) {
            append("R8 SPEED LIMIT SET ACK status=" + (f[4] & 0xFF));
            main.postDelayed(this::sendOfficialSpeedQuery, 500);
        } else if (type == 0x3B && f.length == 9) {
''',
    "gear ack decoder")

# Insert verified official gear sender before drive-mode methods.
anchor2='''    private void confirmOfficialDrive(boolean dual) {
'''
helpers='''    private void confirmOfficialGear(int gear) {
        if (!stationaryForSetting()) return;
        if (gear < 1 || gear > 5) {
            toast("Gear must be 1–5.");
            return;
        }
        new AlertDialog.Builder(this)
                .setTitle("Set electric gear " + gear)
                .setMessage("Send the official isinwheel electric-gear command for Gear " + gear
                        + "? The bike is currently reporting Gear " + gearRaw + ". Keep it stationary for the setting change.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Set Gear " + gear, (d,w) -> sendOfficialGear(gear))
                .show();
    }

    private void sendOfficialGear(int gear) {
        // isinwheel club 1.1.4, s4/a.j(int data1, int gearsMode):
        // d(APP_ELECTRIC_GEAR=0x35, PARAM=0x02, [data1, gearsMode], TRUE)
        // Both stock UI call sites pass gearsMode=0.
        byte[] frame = officialFrame(new byte[]{0x35, 0x02, 0x02, (byte)gear, 0x00});
        writeOfficialFf62(frame, "SET ELECTRIC GEAR " + gear + " (mode 0)");
    }

'''
rep(anchor2,helpers+anchor2,"gear helpers")

p.write_text(s)
print("Applied v0.7 verified electric-gear controls")

from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v09 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v0.8 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.9 ready. Target device name: R8-US");',
    "version")

# Add safe read-only profile/SN query controls beside the existing CRC diagnostics.
rep('''        TextView crcNote = new TextView(this);
        crcNote.setText("Official diagnostics from isinwheel Club 1.1.4 (0x66). These are read-only queries and help fingerprint the restricted controller/display firmware.");
        root.addView(crcNote);

        TextView gearTitle = new TextView(this);''',
'''        TextView crcNote = new TextView(this);
        crcNote.setText("Official diagnostics from isinwheel Club 1.1.4 (0x66). This R8 has not replied to the CRC query so far; buttons are retained for manual checks.");
        root.addView(crcNote);

        LinearLayout identityRow = row();
        Button queryProfile = button("QUERY DEVICE PROFILE");
        Button querySn = button("QUERY DEVICE SN");
        identityRow.addView(queryProfile, weight());
        identityRow.addView(querySn, weight());
        root.addView(identityRow);

        TextView identityNote = new TextView(this);
        identityNote.setText("Read-only official queries: 0x60 asks the bike for its current-user/device profile state. 0x61 reads the device serial response. The SN query can place the bike serial in the exported log, so use it only if you want that fingerprint included.");
        root.addView(identityNote);

        TextView gearTitle = new TextView(this);''',
    "identity UI")

rep('''        queryControllerCrc.setOnClickListener(v -> sendOfficialCrcQuery(1));
        queryMeterCrc.setOnClickListener(v -> sendOfficialCrcQuery(2));''',
'''        queryControllerCrc.setOnClickListener(v -> sendOfficialCrcQuery(1));
        queryMeterCrc.setOnClickListener(v -> sendOfficialCrcQuery(2));
        queryProfile.setOnClickListener(v -> sendOfficialSimpleQuery(0x60, "QUERY DEVICE PROFILE"));
        querySn.setOnClickListener(v -> new AlertDialog.Builder(this)
                .setTitle("Read device serial?")
                .setMessage("This is read-only, but the returned bike serial may be written into the exported diagnostic log.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Query SN", (d,w) -> sendOfficialSimpleQuery(0x61, "QUERY DEVICE SN"))
                .show());''',
    "identity listeners")

# General dynamic framing for variable-length query replies.
rep('''            if (type == 0x66) {
                if (rxStream.size() < 5) return;
                len = 9 + (rxStream.get(4) & 0xFF);
            }''',
'''            if (type == 0x60 || type == 0x61 || type == 0x66) {
                if (rxStream.size() < 5) return;
                len = 9 + (rxStream.get(4) & 0xFF);
            }''',
    "variable query framing")

# Decode read-only 0x60/0x61 replies before CRC.
rep('''        } else if (type == 0x66 && f.length >= 10) {''',
'''        } else if ((type == 0x60 || type == 0x61) && f.length >= 9) {
            int payloadLen = f[4] & 0xFF;
            int dataLen = Math.max(0, Math.min(payloadLen, f.length - 9));
            byte[] payload = dataLen > 0 ? Arrays.copyOfRange(f, 5, 5 + dataLen) : new byte[0];
            String payloadHex = hex(payload);
            if (type == 0x60) {
                append("R8 DEVICE PROFILE response raw=" + payloadHex);
            } else {
                StringBuilder printable = new StringBuilder();
                for (byte b : payload) {
                    int c = b & 0xFF;
                    printable.append(c >= 32 && c <= 126 ? (char)c : '.');
                }
                append("R8 DEVICE SN response raw=" + payloadHex + " printable=" + printable);
            }
        } else if (type == 0x66 && f.length >= 10) {''',
    "identity response decoder")

# Add official simple query helper before CRC query sender.
rep('''    private void sendOfficialCrcQuery(int selector) {''',
'''    private void sendOfficialSimpleQuery(int command, String label) {
        // isinwheel Club query format: e(command, param=0x01, FALSE)
        // body = [command, 0x01, payloadLength=0].
        byte[] frame = officialFrame(new byte[]{(byte)command, 0x01, 0x00});
        writeOfficialFf62(frame, label);
    }

    private void sendOfficialCrcQuery(int selector) {''',
    "simple query sender")

# Stop automatically spamming CRC queries because this controller did not answer them.
rep('''            main.postDelayed(this::sendOfficialSpeedQuery, 1200);
            main.postDelayed(() -> sendOfficialCrcQuery(1), 1900);
            main.postDelayed(() -> sendOfficialCrcQuery(2), 2500);''',
'''            main.postDelayed(this::sendOfficialSpeedQuery, 1200);''',
    "remove automatic CRC")

p.write_text(s)
print("Applied v0.9 read-only device profile and SN diagnostics")

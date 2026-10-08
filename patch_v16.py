from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit("patch_v16 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.5 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.6 ready. Target device name: R8-US");',"version")

# Concept defaults: dark cinematic + orange accent.
rep('''        darkMode = prefs.getBoolean("dark", false);''',
    '''        darkMode = prefs.getBoolean("dark", true);''',"dark default")

# Dashboard typography/card hierarchy.
rep('''        status.setTextSize(17f);''','''        status.setTextSize(16f);
        status.setPadding(dp(12),dp(10),dp(12),dp(10));''',"status card")
rep('''        gpsSpeedView.setTextSize(44f);''','''        gpsSpeedView.setTextSize(58f);
        gpsSpeedView.setGravity(android.view.Gravity.CENTER);
        gpsSpeedView.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);''',"speed hero")
rep('''        rideStateView.setTextSize(16f);''','''        rideStateView.setTextSize(17f);
        rideStateView.setGravity(android.view.Gravity.CENTER);''',"ride state")
rep('''        TextView gearQuickTitle = label("Assist / electric gear");''',
    '''        TextView gearQuickTitle = label("ASSIST LEVEL");''',"assist title")
rep('''        TextView speedTitle = label("Normal controller speed cap");''',
    '''        TextView speedTitle = label("SPEED CONTROL");''',"speed title")
rep('''        Button full62 = button("62 KM/H");
        Button street32 = button("32 KM/H");''',
    '''        Button full62 = button("FULL SPEED  •  62 km/h");
        Button street32 = button("STREET MODE  •  32 km/h");''',"mode cards")
rep('''        Button lightOnRide = button("LIGHT  ON");
        Button lightOffRide = button("LIGHT  OFF");''',
    '''        Button lightOnRide = button("☀  LIGHT ON");
        Button lightOffRide = button("☾  LIGHT OFF");''',"light cards")
rep('''        Button toggleUnits = button("TOGGLE MPH / KM/H");''',
    '''        Button toggleUnits = button("UNITS  •  MPH / KM/H");''',"units")

# Advanced concept hierarchy.
rep('''        advancedAnchor.setText("Advanced & Diagnostics");''',
    '''        advancedAnchor.setText("Advanced");''',"advanced title")
rep('''        advancedIntro.setText("Bluetooth, controller information, telemetry and support tools.");''',
    '''        advancedIntro.setText("Bluetooth  •  Live Data  •  Controller  •  Diagnostics  •  Appearance");''',"advanced intro")

# Stronger cinematic theming and selected-tab accent.
rep('''        int bg = darkMode ? 0xFF0B1015 : 0xFFF4F6F8;
        int surface = darkMode ? 0xFF161D24 : 0xFFFFFFFF;''',
    '''        int bg = darkMode ? 0xFF070C11 : 0xFFF2F4F6;
        int surface = darkMode ? 0xFF121A21 : 0xFFFFFFFF;''',"palette")
rep('''            g.setColor(surface); g.setCornerRadius(dp(12)); g.setStroke(dp(1), accent);''',
    '''            g.setColor(surface); g.setCornerRadius(dp(16)); g.setStroke(dp(1), accent);
            b.setMinHeight(dp(52));''',"buttons")

# Make labels read like section headers.
rep('''    private void styleTree(View view, int surface, int text, int muted, int accent) {''',
'''    private void styleTree(View view, int surface, int text, int muted, int accent) {''',"style anchor")

p.write_text(s)
print("Applied v1.6 concept-dashboard UI")

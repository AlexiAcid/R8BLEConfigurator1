from pathlib import Path

p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v13 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.2 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.3 ready. Target device name: R8-US");',
    "version")

rep('''        tabRide.setOnClickListener(v -> scroll.post(() -> scroll.smoothScrollTo(0, 0)));
        tabTools.setOnClickListener(v -> scroll.post(() -> scroll.smoothScrollTo(0, advancedAnchor.getTop())));''',
'''        // v1.3: these are true mutually-exclusive app sections, not scroll shortcuts.
        // The Ride screen cannot be scrolled into diagnostics accidentally.
        final int firstRideChild = root.indexOfChild(rideTitle);
        final int firstAdvancedChild = root.indexOfChild(advancedAnchor);
        tabRide.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, false, tabRide, tabTools));
        tabTools.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, true, tabRide, tabTools));
        root.post(() -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, false, tabRide, tabTools));''',
    "real tabs")

rep('''    private void autoConnectR8() {''',
'''    private void showAppSection(LinearLayout root, ScrollView scroll,
                                int firstRideChild, int firstAdvancedChild,
                                boolean advanced, Button tabRide, Button tabTools) {
        if (firstRideChild < 0 || firstAdvancedChild < 0) return;
        for (int i = firstRideChild; i < root.getChildCount(); i++) {
            View child = root.getChildAt(i);
            boolean isAdvancedChild = i >= firstAdvancedChild;
            child.setVisibility(isAdvancedChild == advanced ? View.VISIBLE : View.GONE);
        }
        // The two navigation buttons stay visible at all times.
        tabRide.setEnabled(advanced);
        tabTools.setEnabled(!advanced);
        tabRide.setText(advanced ? "RIDE" : "● RIDE");
        tabTools.setText(advanced ? "● ADVANCED" : "ADVANCED");
        scroll.post(() -> scroll.scrollTo(0, 0));
    }

    private void autoConnectR8() {''',
    "tab helper")

# Cleaner release-facing copy while keeping protocol details in Advanced/logs.
rep('''        rideTitle.setText("R8 RIDE DASHBOARD");''',
    '''        rideTitle.setText("R8 Ride");''',
    "ride title")
rep('''        Button tabRide = button("RIDE DASHBOARD");
        Button tabTools = button("ADVANCED TOOLS");''',
    '''        Button tabRide = button("● RIDE");
        Button tabTools = button("ADVANCED");''',
    "tab labels")
rep('''        TextView advancedAnchor = new TextView(this);
        advancedAnchor.setText("ADVANCED / DIAGNOSTIC TOOLS");''',
    '''        TextView advancedAnchor = new TextView(this);
        advancedAnchor.setText("Advanced & Diagnostics");''',
    "advanced title")
rep('''        TextView profileHint = new TextView(this);
        profileHint.setText("FULL SPEED 62 only works when the bike reports hidden maximum >= 62. Your latest physical secret-menu test successfully changed that maximum between 32 and 62.");''',
    '''        TextView profileHint = new TextView(this);
        profileHint.setText("62 mode is available only when the controller reports a maximum of 62. Use Refresh Bike after changing P5 on the bike.");''',
    "profile hint")
rep('''        TextView rideNote = new TextView(this);
        rideNote.setText("Ride controls use only commands already recovered from the official isinwheel app. Pull over before using phone controls. GPS speed comes from the phone, not the bike display.");''',
    '''        TextView rideNote = new TextView(this);
        rideNote.setText("Ride controls use verified R8 commands. GPS speed is measured by your phone. Change settings only while stopped.");''',
    "ride note")

p.write_text(s)
print("Applied v1.3 polished mutually-exclusive Ride / Advanced tabs")

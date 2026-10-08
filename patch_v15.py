from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit("patch_v15 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.4 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.5 ready. Target device name: R8-US");',"version")

# Theme state + persistent preferences.
rep('''    private boolean autoConnectRequested = false;''',
'''    private boolean autoConnectRequested = false;
    private LinearLayout appRoot;
    private boolean darkMode = false;
    private int accentIndex = 0;
    private static final int[] ACCENTS = new int[]{0xFFFF7A1A,0xFF2979FF,0xFF00BFA5,0xFF7C4DFF,0xFFE53935};''',"theme fields")

rep('''        scroll.addView(root);''',
'''        scroll.addView(root);
        appRoot = root;
        android.content.SharedPreferences prefs = getSharedPreferences("r8_ui", MODE_PRIVATE);
        darkMode = prefs.getBoolean("dark", false);
        accentIndex = Math.max(0, Math.min(ACCENTS.length - 1, prefs.getInt("accent", 0)));''',"prefs")

# Hide obsolete reverse-engineering trace controls from the public Advanced UI.
rep('''        root.addView(traceTitle);''','''        traceTitle.setVisibility(View.GONE);
        root.addView(traceTitle);''',"hide trace title")
rep('''        root.addView(traceRow);''','''        traceRow.setVisibility(View.GONE);
        root.addView(traceRow);''',"hide trace row")
rep('''        root.addView(markerRow);''','''        markerRow.setVisibility(View.GONE);
        root.addView(markerRow);''',"hide marker row")
rep('''        root.addView(traceNote);''','''        traceNote.setVisibility(View.GONE);
        root.addView(traceNote);''',"hide trace note")

# Add Appearance at the top of Advanced.
rep('''        advancedAnchor.setPadding(0, dp(18), 0, dp(4));
        root.addView(advancedAnchor);''',
'''        advancedAnchor.setPadding(0, dp(18), 0, dp(4));
        root.addView(advancedAnchor);

        TextView appearanceTitle = label("Appearance");
        root.addView(appearanceTitle);
        LinearLayout appearanceRow = row();
        Button themeToggle = button(darkMode ? "LIGHT MODE" : "DARK MODE");
        Button accentButton = button("ACCENT COLOR");
        appearanceRow.addView(themeToggle, weight());
        appearanceRow.addView(accentButton, weight());
        root.addView(appearanceRow);

        TextView advancedIntro = new TextView(this);
        advancedIntro.setText("Bluetooth, controller information, telemetry and support tools.");
        advancedIntro.setPadding(0, dp(2), 0, dp(12));
        root.addView(advancedIntro);

        themeToggle.setOnClickListener(v -> {
            darkMode = !darkMode;
            getSharedPreferences("r8_ui", MODE_PRIVATE).edit().putBoolean("dark", darkMode).apply();
            themeToggle.setText(darkMode ? "LIGHT MODE" : "DARK MODE");
            applyAppTheme();
        });
        accentButton.setOnClickListener(v -> {
            accentIndex = (accentIndex + 1) % ACCENTS.length;
            getSharedPreferences("r8_ui", MODE_PRIVATE).edit().putInt("accent", accentIndex).apply();
            applyAppTheme();
        });''',"appearance")

# Apply theme after full UI exists.
rep('''        setContentView(scroll);''','''        setContentView(scroll);
        root.post(this::applyAppTheme);''',"apply theme")

# Add theme renderer before app-section helper.
rep('''    private void showAppSection(LinearLayout root, ScrollView scroll,''',
'''    private void applyAppTheme() {
        if (appRoot == null) return;
        int bg = darkMode ? 0xFF0B1015 : 0xFFF4F6F8;
        int surface = darkMode ? 0xFF161D24 : 0xFFFFFFFF;
        int text = darkMode ? 0xFFF3F6F8 : 0xFF17212B;
        int muted = darkMode ? 0xFFB0BEC5 : 0xFF52606D;
        int accent = ACCENTS[accentIndex];
        appRoot.setBackgroundColor(bg);
        styleTree(appRoot, surface, text, muted, accent);
        if (getWindow() != null) {
            getWindow().setStatusBarColor(darkMode ? 0xFF070B0F : 0xFFE8ECEF);
            getWindow().setNavigationBarColor(bg);
        }
    }

    private void styleTree(View view, int surface, int text, int muted, int accent) {
        if (view instanceof Button) {
            Button b=(Button)view;
            b.setTextColor(text);
            android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable();
            g.setColor(surface); g.setCornerRadius(dp(12)); g.setStroke(dp(1), accent);
            b.setBackground(g);
            b.setAllCaps(false);
            b.setPadding(dp(12),dp(10),dp(12),dp(10));
        } else if (view instanceof TextView) {
            ((TextView)view).setTextColor(text);
        }
        if (view instanceof android.view.ViewGroup) {
            android.view.ViewGroup vg=(android.view.ViewGroup)view;
            for(int i=0;i<vg.getChildCount();i++) styleTree(vg.getChildAt(i),surface,text,muted,accent);
        }
    }

    private void showAppSection(LinearLayout root, ScrollView scroll,''',"theme renderer")

p.write_text(s)
print("Applied v1.5 Advanced cleanup and persistent themes")

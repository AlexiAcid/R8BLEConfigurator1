from pathlib import Path

p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v18 missing anchor: "+label)
    s=s.replace(old,new,1)

rep('append("R8 BLE Configurator v1.7 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v1.8 ready. Target device name: R8-US");',
    "version")

rep('''    private int accentIndex = 0;
    private static final int[] ACCENTS = new int[]{0xFFFF7A1A,0xFF2979FF,0xFF00BFA5,0xFF7C4DFF,0xFFE53935};''',
'''    private int accentIndex = 0;
    private int uiStyle = 0; // 0 modern, 1 classic, 2 minimal
    private static final int[] ACCENTS = new int[]{0xFFFF7A1A,0xFF2979FF,0xFF00C853,0xFF7C4DFF,0xFFFF3D45};''',
    "ui style state")

rep('''        accentIndex = Math.max(0, Math.min(ACCENTS.length - 1, prefs.getInt("accent", 0)));''',
'''        accentIndex = Math.max(0, Math.min(ACCENTS.length - 1, prefs.getInt("accent", 0)));
        uiStyle = Math.max(0, Math.min(2, prefs.getInt("ui_style", 0)));''',
    "load ui style")

# The v1.8 shell completely replaces the visible legacy root.
rep('''        setContentView(scroll);
        root.post(this::applyAppTheme);''',
'''        setContentView(buildReleaseUi());
        appRoot.post(this::applyAppTheme);''',
    "replace visible UI")

# Compact live summary for the dashboard card.
rep('''            String ride = "Bike: Gear " + gearRaw
                    + "  •  Battery " + socLike + "%"
                    + "  •  " + voltage
                    + "\\nProfile: " + speedProfile
                    + "  •  Controller cap: " + cap
                    + "  •  Range: " + range
                    + "\\nLight " + (light ? "ON" : "OFF")''',
'''            String ride = "▰  " + socLike + "%   •   Gear " + gearRaw
                    + "   •   " + voltage
                    + "\\n" + speedProfile + "   •   Cap " + cap
                    + "   •   Light " + (light ? "ON" : "OFF")''',
    "compact ride summary")

# Make the GPS display match the reference gauge rather than a sentence.
rep('''        gpsSpeedView.setText(String.format(Locale.US, "GPS  %.1f km/h  •  %.1f mph", kmh, mph));''',
'''        gpsSpeedView.setText(String.format(Locale.US, "%.1f\\n%s",
                mphUnits ? mph : kmh, mphUnits ? "mph" : "km/h"));''',
    "gauge speed format")

# Replace the generic outlined-button theme with the reference's dark cards and filled accents.
old_style='''    private void styleTree(View view, int surface, int text, int muted, int accent) {
        if (view instanceof Button) {
            Button b=(Button)view;
            b.setTextColor(text);
            android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable();
            g.setColor(surface); g.setCornerRadius(dp(16)); g.setStroke(dp(1), accent);
            b.setMinHeight(dp(52));
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
'''
new_style='''    private void styleTree(View view, int surface, int text, int muted, int accent) {
        Object rawTag = view.getTag();
        String tag = rawTag == null ? "" : String.valueOf(rawTag);
        int border = darkMode ? 0xFF2A343D : 0xFFD5DCE2;
        float radius = uiStyle == 1 ? dp(9) : (uiStyle == 2 ? dp(2) : dp(16));

        if (view instanceof android.widget.Switch) {
            ((android.widget.Switch)view).setTextColor(text);
        } else if (view instanceof Button) {
            Button b=(Button)view;
            android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable();
            g.setCornerRadius(radius);
            if ("primary".equals(tag) || "navSelected".equals(tag)) {
                g.setColor(accent);
                g.setStroke(0, accent);
                b.setTextColor(0xFF071018);
            } else if (tag.startsWith("accentPicker:")) {
                int idx;
                try { idx=Integer.parseInt(tag.substring(tag.indexOf(':')+1)); } catch(Exception e) { idx=0; }
                int c=ACCENTS[Math.max(0,Math.min(ACCENTS.length-1,idx))];
                g.setColor(surface);
                g.setStroke(dp(idx==accentIndex?3:1), c);
                g.setShape(android.graphics.drawable.GradientDrawable.OVAL);
                b.setTextColor(c);
            } else if ("nav".equals(tag)) {
                g.setColor(darkMode ? 0xFF0B1117 : 0xFFF8FAFB);
                g.setStroke(0, border);
                b.setTextColor(muted);
            } else {
                g.setColor(surface);
                g.setStroke(uiStyle==2 ? 0 : dp(1), border);
                b.setTextColor(text);
            }
            b.setMinHeight(dp(50));
            b.setBackground(g);
            b.setAllCaps(false);
            b.setPadding(dp(12),dp(10),dp(12),dp(10));
        } else if (view instanceof TextView) {
            TextView tv=(TextView)view;
            if ("muted".equals(tag)) tv.setTextColor(muted);
            else if ("accentText".equals(tag)) tv.setTextColor(accent);
            else tv.setTextColor(text);
        } else if (view instanceof LinearLayout && "card".equals(tag)) {
            android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable();
            g.setColor(surface);
            g.setCornerRadius(radius);
            g.setStroke(uiStyle==2 ? 0 : dp(1), border);
            view.setBackground(g);
        } else if (view instanceof android.widget.FrameLayout && "gauge".equals(tag)) {
            android.graphics.drawable.GradientDrawable g=new android.graphics.drawable.GradientDrawable();
            g.setShape(android.graphics.drawable.GradientDrawable.OVAL);
            g.setColor(darkMode ? 0xFF070B0E : 0xFFFFFFFF);
            g.setStroke(dp(10), accent);
            view.setBackground(g);
        }
        if (view instanceof android.view.ViewGroup) {
            android.view.ViewGroup vg=(android.view.ViewGroup)view;
            for(int i=0;i<vg.getChildCount();i++) styleTree(vg.getChildAt(i),surface,text,muted,accent);
        }
    }
'''
if old_style not in s:
    raise SystemExit("patch_v18 missing anchor: styleTree")
s=s.replace(old_style,new_style,1)

# New release shell: independent pages + fixed bottom nav.
anchor='''    private void showAppSection(LinearLayout root, ScrollView scroll,'''
if anchor not in s:
    raise SystemExit("patch_v18 missing anchor: shell insertion")
release='''    private View buildReleaseUi() {
        final int pad=dp(18);
        final LinearLayout shell=new LinearLayout(this);
        shell.setOrientation(LinearLayout.VERTICAL);
        shell.setPadding(0,0,0,0);
        appRoot=shell;

        final android.widget.FrameLayout host=new android.widget.FrameLayout(this);
        shell.addView(host,new LinearLayout.LayoutParams(-1,0,1f));

        final ScrollView rideScroll=new ScrollView(this);
        final ScrollView advancedScroll=new ScrollView(this);
        final ScrollView appearanceScroll=new ScrollView(this);
        rideScroll.setFillViewport(true);
        advancedScroll.setFillViewport(true);
        appearanceScroll.setFillViewport(true);

        final LinearLayout ride=new LinearLayout(this);
        final LinearLayout advanced=new LinearLayout(this);
        final LinearLayout appearance=new LinearLayout(this);
        for(LinearLayout page:new LinearLayout[]{ride,advanced,appearance}) {
            page.setOrientation(LinearLayout.VERTICAL);
            page.setPadding(pad,dp(14),pad,dp(28));
        }
        rideScroll.addView(ride,new ScrollView.LayoutParams(-1,-2));
        advancedScroll.addView(advanced,new ScrollView.LayoutParams(-1,-2));
        appearanceScroll.addView(appearance,new ScrollView.LayoutParams(-1,-2));
        host.addView(rideScroll,new android.widget.FrameLayout.LayoutParams(-1,-1));
        host.addView(advancedScroll,new android.widget.FrameLayout.LayoutParams(-1,-1));
        host.addView(appearanceScroll,new android.widget.FrameLayout.LayoutParams(-1,-1));

        // ----- RIDE -----
        LinearLayout connection=row();
        Button bt=button("◈");
        bt.setTextSize(22f);
        status=new TextView(this);
        status.setText("Disconnected\\nR8-US");
        status.setTextSize(17f);
        status.setPadding(dp(12),dp(4),dp(8),dp(4));
        Button gear=button("⚙");
        gear.setTextSize(20f);
        connection.addView(bt,new LinearLayout.LayoutParams(dp(56),dp(56)));
        connection.addView(status,new LinearLayout.LayoutParams(0,dp(56),1f));
        connection.addView(gear,new LinearLayout.LayoutParams(dp(56),dp(56)));
        ride.addView(connection);
        bt.setOnClickListener(v->autoConnectR8());

        TextView speedLabel=new TextView(this);
        speedLabel.setText("SPEED");
        speedLabel.setTextSize(13f);
        speedLabel.setGravity(android.view.Gravity.CENTER);
        speedLabel.setTag("muted");
        speedLabel.setPadding(0,dp(12),0,dp(5));
        ride.addView(speedLabel);

        android.widget.FrameLayout gauge=new android.widget.FrameLayout(this);
        gauge.setTag("gauge");
        LinearLayout.LayoutParams gaugeLp=new LinearLayout.LayoutParams(dp(252),dp(252));
        gaugeLp.gravity=android.view.Gravity.CENTER_HORIZONTAL;
        gaugeLp.setMargins(0,0,0,dp(10));
        gpsSpeedView=new TextView(this);
        gpsSpeedView.setText("—.-\\nkm/h");
        gpsSpeedView.setTextSize(48f);
        gpsSpeedView.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        gpsSpeedView.setGravity(android.view.Gravity.CENTER);
        gauge.addView(gpsSpeedView,new android.widget.FrameLayout.LayoutParams(-1,-1));
        ride.addView(gauge,gaugeLp);
        gauge.setOnClickListener(v->startGpsSpeedometer());

        gpsStatusView=new TextView(this);
        gpsStatusView.setText("Tap the speed dial to start phone GPS");
        gpsStatusView.setGravity(android.view.Gravity.CENTER);
        gpsStatusView.setTextSize(13f);
        gpsStatusView.setTag("muted");
        ride.addView(gpsStatusView);

        rideStateView=new TextView(this);
        rideStateView.setText("▰  --%   •   Waiting for bike data");
        rideStateView.setGravity(android.view.Gravity.CENTER);
        rideStateView.setTextSize(16f);
        rideStateView.setPadding(0,dp(10),0,dp(14));
        ride.addView(rideStateView);

        LinearLayout assist=releaseCard("ASSIST LEVEL");
        LinearLayout gearRow=new LinearLayout(this);
        gearRow.setOrientation(LinearLayout.HORIZONTAL);
        Button[] gears=new Button[5];
        for(int i=0;i<5;i++) {
            final int level=i+1;
            gears[i]=button(String.valueOf(level));
            gears[i].setTextSize(18f);
            final int index=i;
            gears[i].setOnClickListener(v->{
                sendRideGear(level);
                for(int k=0;k<gears.length;k++) gears[k].setTag(k==index?"primary":"");
                applyAppTheme();
            });
            gearRow.addView(gears[i],releaseWeight());
        }
        assist.addView(gearRow);
        ride.addView(assist,releaseCardParams());

        LinearLayout modes=row();
        Button street=button("STREET MODE\\n32 km/h");
        Button full=button("FULL SPEED\\n62 km/h");
        street.setTextSize(16f); full.setTextSize(16f);
        modes.addView(street,releaseWeight());
        modes.addView(full,releaseWeight());
        ride.addView(modes);
        street.setOnClickListener(v->{
            setRideSpeedPreset(32);
            street.setTag("primary"); full.setTag("");
            applyAppTheme();
        });
        full.setOnClickListener(v->{
            setRideSpeedPreset(62);
            full.setTag("primary"); street.setTag("");
            applyAppTheme();
        });

        LinearLayout lightCard=releaseCard("");
        LinearLayout lightRow=new LinearLayout(this);
        lightRow.setOrientation(LinearLayout.HORIZONTAL);
        TextView lightText=new TextView(this);
        lightText.setText("☀   Bike Light");
        lightText.setTextSize(17f);
        lightText.setGravity(android.view.Gravity.CENTER_VERTICAL);
        android.widget.Switch lightSwitch=new android.widget.Switch(this);
        lightSwitch.setText("");
        lightRow.addView(lightText,new LinearLayout.LayoutParams(0,dp(58),1f));
        lightRow.addView(lightSwitch,new LinearLayout.LayoutParams(dp(82),dp(58)));
        lightCard.addView(lightRow);
        ride.addView(lightCard,releaseCardParams());
        lightSwitch.setOnCheckedChangeListener((b,checked)->setRideLight(checked));

        LinearLayout unitsCard=releaseCard("");
        LinearLayout units=row();
        TextView unitLabel=new TextView(this);
        unitLabel.setText("◴   Units");
        unitLabel.setTextSize(17f);
        unitLabel.setGravity(android.view.Gravity.CENTER_VERTICAL);
        Button mph=button("MPH");
        Button kmh=button("KM/H");
        units.addView(unitLabel,new LinearLayout.LayoutParams(0,dp(54),1f));
        units.addView(mph,new LinearLayout.LayoutParams(dp(78),dp(54)));
        units.addView(kmh,new LinearLayout.LayoutParams(dp(78),dp(54)));
        unitsCard.addView(units);
        ride.addView(unitsCard,releaseCardParams());
        mph.setTag(mphUnits?"primary":"");
        kmh.setTag(!mphUnits?"primary":"");
        mph.setOnClickListener(v->{
            if(!mphUnits) toggleRideUnits();
            mph.setTag("primary"); kmh.setTag(""); applyAppTheme();
        });
        kmh.setOnClickListener(v->{
            if(mphUnits) toggleRideUnits();
            kmh.setTag("primary"); mph.setTag(""); applyAppTheme();
        });

        // ----- ADVANCED -----
        TextView advTitle=releaseHeading("Advanced",26f);
        advanced.addView(advTitle);

        TextView advStatus=new TextView(this);
        advStatus.setText("Disconnected\\nR8-US");
        advStatus.setTextSize(15f);
        advStatus.setPadding(0,0,0,dp(12));
        advanced.addView(advStatus);

        Button bluetoothCard=button("◈   Bluetooth\\nScan, connect, device info");
        Button liveCard=button("▥   Live Data\\nView real-time telemetry");
        Button speedCard=button("◉   Speed Settings\\nStreet / Full speed / Custom");
        Button systemCard=button("▣   System Info\\nController & battery details");
        Button diagnosticCard=button("⌁   Diagnostics\\nRead data & GATT details");
        Button exportCard=button("▤   Export Logs\\nSave logs for support");
        for(Button b:new Button[]{bluetoothCard,liveCard,speedCard,systemCard,diagnosticCard,exportCard}) {
            b.setGravity(android.view.Gravity.LEFT|android.view.Gravity.CENTER_VERTICAL);
            b.setTextSize(16f);
            LinearLayout.LayoutParams lp=releaseCardParams();
            lp.height=dp(76);
            advanced.addView(b,lp);
        }

        LinearLayout bluetoothPanel=releaseCard("");
        bluetoothPanel.setVisibility(View.GONE);
        LinearLayout connButtons=row();
        Button scan=button("Scan R8-US");
        Button disconnect=button("Disconnect");
        connButtons.addView(scan,releaseWeight());
        connButtons.addView(disconnect,releaseWeight());
        bluetoothPanel.addView(connButtons);
        ListView releaseDeviceList=new ListView(this);
        releaseDeviceList.setAdapter(deviceAdapter);
        releaseDeviceList.setNestedScrollingEnabled(true);
        bluetoothPanel.addView(releaseDeviceList,new LinearLayout.LayoutParams(-1,dp(180)));
        advanced.addView(bluetoothPanel,releaseCardParams());
        scan.setOnClickListener(v->startScan());
        disconnect.setOnClickListener(v->disconnectGatt());
        releaseDeviceList.setOnItemClickListener((parent,view,pos,id)->{
            Object item=deviceAdapter.getItem(pos);
            if(item==null) return;
            String line=String.valueOf(item);
            int a=line.lastIndexOf('['), b=line.lastIndexOf(']');
            if(a>=0 && b>a) {
                android.bluetooth.BluetoothDevice d=devices.get(line.substring(a+1,b));
                if(d!=null) connect(d);
            }
        });

        LinearLayout livePanel=releaseCard("");
        livePanel.setVisibility(View.GONE);
        decodedView=new TextView(this);
        decodedView.setText("Connect to the R8 to view telemetry.");
        decodedView.setTextSize(14f);
        decodedView.setPadding(dp(8),dp(8),dp(8),dp(8));
        livePanel.addView(decodedView);
        advanced.addView(livePanel,releaseCardParams());

        LinearLayout speedPanel=releaseCard("");
        speedPanel.setVisibility(View.GONE);
        speedCapValueView=new TextView(this);
        speedCapValueView.setText("Custom speed: query bike first");
        speedPanel.addView(speedCapValueView);
        speedCapSeek=new SeekBar(this);
        speedCapSeek.setMax(16);
        speedCapSeek.setProgress(16);
        speedPanel.addView(speedCapSeek);
        LinearLayout customButtons=row();
        Button refreshRange=button("Refresh Range");
        Button applyCustom=button("Set Custom");
        customButtons.addView(refreshRange,releaseWeight());
        customButtons.addView(applyCustom,releaseWeight());
        speedPanel.addView(customButtons);
        LinearLayout driveButtons=row();
        Button single=button("Single Motor");
        Button dual=button("Dual Motor");
        driveButtons.addView(single,releaseWeight());
        driveButtons.addView(dual,releaseWeight());
        speedPanel.addView(driveButtons);
        advanced.addView(speedPanel,releaseCardParams());
        refreshRange.setOnClickListener(v->sendOfficialSpeedQuery());
        applyCustom.setOnClickListener(v->applyRideSpeedCap());
        single.setOnClickListener(v->confirmOfficialDrive(false));
        dual.setOnClickListener(v->confirmOfficialDrive(true));
        speedCapSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar,int progress,boolean fromUser) {
                int min=speedLimitMinRaw>=0?speedLimitMinRaw:16;
                int value=min+progress;
                if(speedLimitMaxRaw>=min) value=Math.min(value,speedLimitMaxRaw);
                if(speedCapValueView!=null) speedCapValueView.setText("Custom speed  •  "+value+" km/h");
            }
            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {}
        });

        LinearLayout systemPanel=releaseCard("");
        systemPanel.setVisibility(View.GONE);
        LinearLayout sys1=row();
        Button profile=button("Device Profile");
        Button sn=button("Device SN");
        sys1.addView(profile,releaseWeight());
        sys1.addView(sn,releaseWeight());
        systemPanel.addView(sys1);
        LinearLayout sys2=row();
        Button controllerCrc=button("Controller CRC");
        Button meterCrc=button("Meter CRC");
        sys2.addView(controllerCrc,releaseWeight());
        sys2.addView(meterCrc,releaseWeight());
        systemPanel.addView(sys2);
        advanced.addView(systemPanel,releaseCardParams());
        profile.setOnClickListener(v->sendOfficialSimpleQuery(0x60,"QUERY DEVICE PROFILE"));
        sn.setOnClickListener(v->sendOfficialSimpleQuery(0x61,"QUERY DEVICE SN"));
        controllerCrc.setOnClickListener(v->sendOfficialCrcQuery(1));
        meterCrc.setOnClickListener(v->sendOfficialCrcQuery(2));

        LinearLayout diagnosticPanel=releaseCard("");
        diagnosticPanel.setVisibility(View.GONE);
        LinearLayout diagButtons=row();
        Button mtu=button("Request MTU 247");
        Button query=button("Query Speed Range");
        diagButtons.addView(mtu,releaseWeight());
        diagButtons.addView(query,releaseWeight());
        diagnosticPanel.addView(diagButtons);
        ListView releaseGattList=new ListView(this);
        releaseGattList.setAdapter(charAdapter);
        releaseGattList.setNestedScrollingEnabled(true);
        diagnosticPanel.addView(releaseGattList,new LinearLayout.LayoutParams(-1,dp(210)));
        advanced.addView(diagnosticPanel,releaseCardParams());
        mtu.setOnClickListener(v->{
            if(gatt==null) toast("Connect to R8-US first.");
            else try { gatt.requestMtu(247); } catch(SecurityException e) { toast("Bluetooth permission required."); }
        });
        query.setOnClickListener(v->sendOfficialSpeedQuery());

        bluetoothCard.setOnClickListener(v->toggleReleasePanel(bluetoothPanel));
        liveCard.setOnClickListener(v->toggleReleasePanel(livePanel));
        speedCard.setOnClickListener(v->toggleReleasePanel(speedPanel));
        systemCard.setOnClickListener(v->toggleReleasePanel(systemPanel));
        diagnosticCard.setOnClickListener(v->toggleReleasePanel(diagnosticPanel));
        exportCard.setOnClickListener(v->exportLog());

        // ----- APPEARANCE -----
        appearance.addView(releaseHeading("Appearance",26f));

        LinearLayout darkCard=releaseCard("");
        android.widget.Switch darkSwitch=new android.widget.Switch(this);
        darkSwitch.setText("☾   Dark Mode");
        darkSwitch.setTextSize(17f);
        darkSwitch.setChecked(darkMode);
        darkCard.addView(darkSwitch,new LinearLayout.LayoutParams(-1,dp(62)));
        appearance.addView(darkCard,releaseCardParams());
        darkSwitch.setOnCheckedChangeListener((b,checked)->{
            darkMode=checked;
            getSharedPreferences("r8_ui",MODE_PRIVATE).edit().putBoolean("dark",darkMode).apply();
            applyAppTheme();
        });

        LinearLayout colorCard=releaseCard("Theme Color");
        LinearLayout colors=row();
        for(int i=0;i<ACCENTS.length;i++) {
            final int idx=i;
            Button color=button("●");
            color.setTextSize(28f);
            color.setTag("accentPicker:"+i);
            color.setOnClickListener(v->{
                accentIndex=idx;
                getSharedPreferences("r8_ui",MODE_PRIVATE).edit().putInt("accent",idx).apply();
                applyAppTheme();
            });
            colors.addView(color,releaseWeight());
        }
        colorCard.addView(colors);
        appearance.addView(colorCard,releaseCardParams());

        LinearLayout iconCard=releaseCard("App Icon");
        android.widget.ImageView icon=new android.widget.ImageView(this);
        icon.setImageResource(R.drawable.r8_launcher);
        icon.setScaleType(android.widget.ImageView.ScaleType.CENTER_CROP);
        LinearLayout.LayoutParams iconLp=new LinearLayout.LayoutParams(dp(104),dp(104));
        iconLp.gravity=android.view.Gravity.CENTER_HORIZONTAL;
        iconCard.addView(icon,iconLp);
        TextView iconNote=new TextView(this);
        iconNote.setText("Fiery R8 wheel");
        iconNote.setGravity(android.view.Gravity.CENTER);
        iconNote.setTag("muted");
        iconCard.addView(iconNote);
        appearance.addView(iconCard,releaseCardParams());

        LinearLayout styleCard=releaseCard("UI Style");
        LinearLayout styles=row();
        Button modern=button("Modern");
        Button classic=button("Classic");
        Button minimal=button("Minimal");
        styles.addView(modern,releaseWeight());
        styles.addView(classic,releaseWeight());
        styles.addView(minimal,releaseWeight());
        styleCard.addView(styles);
        appearance.addView(styleCard,releaseCardParams());
        Button[] styleButtons=new Button[]{modern,classic,minimal};
        for(int i=0;i<styleButtons.length;i++) styleButtons[i].setTag(i==uiStyle?"primary":"");
        modern.setOnClickListener(v->selectUiStyle(0,styleButtons));
        classic.setOnClickListener(v->selectUiStyle(1,styleButtons));
        minimal.setOnClickListener(v->selectUiStyle(2,styleButtons));

        LinearLayout about=releaseCard("About");
        TextView aboutText=new TextView(this);
        aboutText.setText("R8 BLE Configurator\\nv1.8\\n\\nCustom R8 e-bike control and configuration.");
        aboutText.setTextSize(15f);
        aboutText.setPadding(0,dp(5),0,dp(5));
        about.addView(aboutText);
        appearance.addView(about,releaseCardParams());

        // ----- FIXED BOTTOM NAV -----
        LinearLayout bottom=new LinearLayout(this);
        bottom.setOrientation(LinearLayout.HORIZONTAL);
        bottom.setPadding(dp(8),dp(6),dp(8),dp(8));
        Button rideTab=button("⌁\\nRide");
        Button advancedTab=button("⚙\\nAdvanced");
        Button appearanceTab=button("◉\\nAppearance");
        rideTab.setTag("navSelected");
        advancedTab.setTag("nav");
        appearanceTab.setTag("nav");
        bottom.addView(rideTab,releaseWeight());
        bottom.addView(advancedTab,releaseWeight());
        bottom.addView(appearanceTab,releaseWeight());
        shell.addView(bottom,new LinearLayout.LayoutParams(-1,dp(76)));

        View[] pages=new View[]{rideScroll,advancedScroll,appearanceScroll};
        Button[] tabs=new Button[]{rideTab,advancedTab,appearanceTab};
        rideTab.setOnClickListener(v->showReleasePage(pages,tabs,0));
        advancedTab.setOnClickListener(v->{
            advStatus.setText(status==null?"Disconnected":String.valueOf(status.getText()));
            showReleasePage(pages,tabs,1);
        });
        appearanceTab.setOnClickListener(v->showReleasePage(pages,tabs,2));
        gear.setOnClickListener(v->showReleasePage(pages,tabs,1));

        showReleasePage(pages,tabs,0);
        return shell;
    }

    private TextView releaseHeading(String text,float size) {
        TextView t=new TextView(this);
        t.setText(text);
        t.setTextSize(size);
        t.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        t.setPadding(0,dp(6),0,dp(14));
        return t;
    }

    private LinearLayout releaseCard(String title) {
        LinearLayout c=new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setPadding(dp(14),dp(12),dp(14),dp(12));
        c.setTag("card");
        if(title!=null && !title.isEmpty()) {
            TextView h=new TextView(this);
            h.setText(title);
            h.setTextSize(15f);
            h.setTag("muted");
            h.setPadding(0,0,0,dp(9));
            c.addView(h);
        }
        return c;
    }

    private LinearLayout.LayoutParams releaseCardParams() {
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);
        lp.setMargins(0,dp(6),0,dp(6));
        return lp;
    }

    private LinearLayout.LayoutParams releaseWeight() {
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-1,1f);
        lp.setMargins(dp(3),dp(3),dp(3),dp(3));
        return lp;
    }

    private void toggleReleasePanel(View panel) {
        panel.setVisibility(panel.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE);
    }

    private void showReleasePage(View[] pages,Button[] tabs,int index) {
        for(int i=0;i<pages.length;i++) {
            pages[i].setVisibility(i==index?View.VISIBLE:View.GONE);
            tabs[i].setTag(i==index?"navSelected":"nav");
        }
        applyAppTheme();
    }

    private void selectUiStyle(int style,Button[] buttons) {
        uiStyle=style;
        getSharedPreferences("r8_ui",MODE_PRIVATE).edit().putInt("ui_style",style).apply();
        for(int i=0;i<buttons.length;i++) buttons[i].setTag(i==style?"primary":"");
        applyAppTheme();
    }

'''
s=s.replace(anchor,release+anchor,1)

p.write_text(s)
print("Applied v1.8 real release shell with fixed Ride / Advanced / Appearance pages")

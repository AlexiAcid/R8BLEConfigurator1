from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()
s=s.replace("R8 BLE Configurator v2.1 ready. Target device name: R8-US","R8 BLE Configurator v2.2 ready. Target device name: R8-US")
# Field to retain live battery UI.
needle="    private View buildReleaseUi() {"
if needle not in s: raise SystemExit("missing buildReleaseUi")
s=s.replace(needle,"    private TextView dashboardBatteryPercent;\n    private android.widget.ProgressBar dashboardBatteryBar;\n\n"+needle,1)
# Replace plain text battery summary with a real icon/bar plus live percentage inside dial.
needle="        ride.addView(speedLabel);"
if needle not in s: raise SystemExit("speed label anchor missing")
s=s.replace(needle,"        // Label belongs inside the gauge, as in the reference design.",1)
needle="        gauge.addView(gpsSpeedView,new android.widget.FrameLayout.LayoutParams(-1,-1));"
if needle not in s: raise SystemExit("gauge child anchor missing")
replacement='''        gauge.addView(gpsSpeedView,new android.widget.FrameLayout.LayoutParams(-1,-1));
        android.widget.FrameLayout.LayoutParams speedLabelLp=new android.widget.FrameLayout.LayoutParams(-1,dp(36),android.view.Gravity.TOP);
        speedLabelLp.topMargin=dp(34);
        gauge.addView(speedLabel,speedLabelLp);
        LinearLayout batteryRow=new LinearLayout(this);
        batteryRow.setGravity(android.view.Gravity.CENTER);
        batteryRow.setOrientation(LinearLayout.HORIZONTAL);
        android.widget.FrameLayout batteryHousing=new android.widget.FrameLayout(this);
        android.graphics.drawable.GradientDrawable batteryOutline=new android.graphics.drawable.GradientDrawable();
        batteryOutline.setColor(0xFF07110B);
        batteryOutline.setCornerRadius(dp(4));
        batteryOutline.setStroke(dp(2),0xFF00F030);
        batteryHousing.setBackground(batteryOutline);
        dashboardBatteryBar=new android.widget.ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);
        dashboardBatteryBar.setMax(100);
        dashboardBatteryBar.setProgress(0);
        dashboardBatteryBar.setProgressTintList(android.content.res.ColorStateList.valueOf(0xFF00F030));
        dashboardBatteryBar.setProgressBackgroundTintList(android.content.res.ColorStateList.valueOf(0xFF14251B));
        android.widget.FrameLayout.LayoutParams fillLp=new android.widget.FrameLayout.LayoutParams(-1,dp(18));
        fillLp.setMargins(dp(4),dp(4),dp(4),dp(4));
        batteryHousing.addView(dashboardBatteryBar,fillLp);
        batteryRow.addView(batteryHousing,new LinearLayout.LayoutParams(dp(55),dp(27)));
        dashboardBatteryPercent=new TextView(this);
        dashboardBatteryPercent.setText("--%");
        dashboardBatteryPercent.setTextColor(0xFFFFFFFF);
        dashboardBatteryPercent.setTextSize(21f);
        dashboardBatteryPercent.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        dashboardBatteryPercent.setPadding(dp(12),0,0,0);
        batteryRow.addView(dashboardBatteryPercent);
        android.widget.FrameLayout.LayoutParams batteryLp=new android.widget.FrameLayout.LayoutParams(-1,dp(38),android.view.Gravity.BOTTOM);
        batteryLp.bottomMargin=dp(26);
        gauge.addView(batteryRow,batteryLp);'''
s=s.replace(needle,replacement,1)
# Update percentage only when live bike telemetry is decoded.
needle='            String ride = "▰  " + socLike + "%"'
if needle not in s: raise SystemExit("live telemetry anchor missing")
s=s.replace(needle,'''            if(dashboardBatteryPercent!=null) {
                dashboardBatteryPercent.setText(socLike + "%");
                try {
                    int batteryLevel=Math.max(0,Math.min(100,Integer.parseInt(String.valueOf(socLike).trim())));
                    dashboardBatteryBar.setProgress(batteryLevel);
                    dashboardBatteryBar.setProgressTintList(android.content.res.ColorStateList.valueOf(
                        batteryLevel<=20 ? 0xFFFF4030 : batteryLevel<=40 ? 0xFFFFAA00 : 0xFF00F030));
                } catch(Exception ignored) {}
            }
            String ride = "▰  " + socLike + "%"''',1)
# Make the gauge more compact to fit the ride controls.
s=s.replace('new LinearLayout.LayoutParams(dp(252),dp(252))','new LinearLayout.LayoutParams(dp(280),dp(280))',1)
p.write_text(s)
print("v2.2 live gauge battery meter and percentage installed")

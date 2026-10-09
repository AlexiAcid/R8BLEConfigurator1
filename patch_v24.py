from pathlib import Path
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()
s=s.replace("R8 BLE Configurator v2.3 ready. Target device name: R8-US","R8 BLE Configurator v2.4 ready. Target device name: R8-US")
needle='        LinearLayout unitsCard=releaseCard("");'
if needle not in s: raise SystemExit("units anchor missing")
block='''        // Cruise: do not send a speculative BLE throttle or cruise opcode.
        // P5 on this specific bike is confirmed by the owner to be the 32/62 speed profile.
        LinearLayout cruiseCard=releaseCard("");
        LinearLayout cruiseRow=new LinearLayout(this);
        cruiseRow.setOrientation(LinearLayout.HORIZONTAL);
        cruiseRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
        TextView cruiseLabel=new TextView(this);
        cruiseLabel.setText("◉   Cruise Control\\nController command not verified");
        cruiseLabel.setTextSize(15f);
        cruiseLabel.setGravity(android.view.Gravity.CENTER_VERTICAL);
        Button cruiseInfo=button("SETUP");
        cruiseRow.addView(cruiseLabel,new LinearLayout.LayoutParams(0,dp(64),1f));
        cruiseRow.addView(cruiseInfo,new LinearLayout.LayoutParams(dp(100),dp(58)));
        cruiseCard.addView(cruiseRow);
        ride.addView(cruiseCard,releaseCardParams());
        cruiseInfo.setOnClickListener(v->new android.app.AlertDialog.Builder(this)
            .setTitle("R8 Cruise Control")
            .setMessage("Cruise control has not yet been verified over R8-US Bluetooth. This button does not activate or change motor output.\\n\\nYour bike's P5 setting controls the 32/62 km/h profile, not cruise.\\n\\nAn older R8/R8S manual describes holding the minus button while accelerating to enter cruise, then braking to exit. That procedure is not confirmed for your exact R8 controller.\\n\\nFor an actual app toggle we need a verified R8-specific BLE command and confirmation that braking reliably cancels cruise.")
            .setPositiveButton("OK",(d,w)->{})
            .show());

'''
s=s.replace(needle,block+needle,1)
p.write_text(s)
print("v2.4 main Ride cruise information card inserted; no unsafe BLE opcode")

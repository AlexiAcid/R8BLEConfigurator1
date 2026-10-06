from pathlib import Path

p = Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s = p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("patch_v04 missing anchor: " + label)
    s=s.replace(old,new,1)

rep('Button lightOn = button("TEST LIGHT ON (FF62)");',
    'Button lightOn = button("TEST LIGHT ON (FF62 ACK)");',
    "light on label")
rep('Button lightOff = button("TEST LIGHT OFF (FF62)");',
    'Button lightOff = button("TEST LIGHT OFF (FF62 ACK)");',
    "light off label")
rep('Experimental: uses the latest valid 0x20 status frame from the bike, changes only light bit 0x10, recalculates CRC-16/MODBUS, then writes it to FF62. Keep the bike stationary for this test.',
    'Experimental v0.4: same known light-state frame, but sends it to FF62 using ATT WRITE WITH RESPONSE so we get a real GATT acknowledgement. Keep the bike stationary.',
    "experiment text")
rep('append("R8 BLE Configurator v0.3 ready. Target device name: R8-US");',
    'append("R8 BLE Configurator v0.4 ready. Target device name: R8-US");',
    "version")

rep('int r = gatt.writeCharacteristic(tx, out, BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);\n                append("FF62 experimental write queue result=" + r);',
    'int r = gatt.writeCharacteristic(tx, out, BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT);\n                append("FF62 WRITE-WITH-RESPONSE queue result=" + r);',
    "api33 write type")
rep('tx.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);\n                tx.setValue(out);\n                append("FF62 experimental write queued=" + gatt.writeCharacteristic(tx));',
    'tx.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT);\n                tx.setValue(out);\n                append("FF62 WRITE-WITH-RESPONSE queued=" + gatt.writeCharacteristic(tx));',
    "legacy write type")

p.write_text(s)
print("Applied v0.4 FF62 write-with-response diagnostic patch")

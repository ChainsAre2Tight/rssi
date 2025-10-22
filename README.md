## MAC esp32:
- **ESP32_01** ```00:4B:12:2F:C0:44```
- **ESP32_02** ```00:4B:12:2F:7C:B0```
- **ESP32_03** ```-```
- **ESP32_04** ```-```
- **ESP32_05** ```-```

## Cхема данных

```
PACKETS:
id              device      tsf     rssi    channel type    subtype seq     src_mac dst_mac bssid   ssid
INTEGER         TEXT        TEXT    INTEGER INTEGER INTEGER INTEGER INTEGER TEXT    TEXT    TEXT    TEXT
PRIMARY KEY     NOT NULL    
AUTOINCREMENT
```